"""
VibraLens · NASA POWER API client
Fetch data lingkungan dari satelit, cache di SQLite.

Sumber: https://power.larc.nasa.gov/
Data:  suhu (T2M), kelembaban (RH2M), hujan (PRECTOTCORR), tekanan (PS)
"""
import requests
from datetime import datetime, timezone, timedelta
from database import get_db

NASA_BASE = "https://power.larc.nasa.gov/api/temporal/hourly/point"

# Parameter NASA POWER:
#   T2M          → Temperature at 2 Meters (°C)
#   RH2M         → Relative Humidity at 2 Meters (%)
#   PRECTOTCORR  → Precipitation Corrected (mm/day)
#   PS           → Surface Pressure (kPa)
PARAMS = "T2M,RH2M,PRECTOTCORR,PS"

# Cache valid selama 1 jam
CACHE_HOURS = 1


def fetch_from_nasa(lat, lon, start_date, end_date):
    """Ambil data dari NASA POWER API."""
    params = {
        "parameters": PARAMS,
        "community": "RE",           # Renewable Energy
        "longitude": lon,
        "latitude": lat,
        "start": start_date,         # format YYYYMMDD
        "end": end_date,
        "format": "JSON",
    }

    try:
        r = requests.get(NASA_BASE, params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        print(f"[NASA] Timeout untuk ({lat}, {lon})")
    except requests.exceptions.RequestException as e:
        print(f"[NASA] Error: {e}")
    except Exception as e:
        print(f"[NASA] Unexpected error: {e}")
    return None


def parse_nasa_response(data):
    """Parse response NASA POWER → dict sederhana."""
    if not data or "properties" not in data:
        return None

    try:
        params = data["properties"]["parameter"]
        t2m = params.get("T2M", {})
        rh2m = params.get("RH2M", {})
        rain = params.get("PRECTOTCORR", {})
        ps = params.get("PS", {})

        if not t2m:
            return None

        # Ambil key terakhir (data terbaru)
        last_key = sorted(t2m.keys())[-1]

        def clean(v):
            """NASA kadang return -999 untuk no data."""
            if v is None or v == -999 or v == -999.0:
                return None
            return round(float(v), 2)

        return {
            "timestamp": datetime.strptime(last_key, "%Y%m%d%H").replace(tzinfo=timezone.utc).isoformat(),
            "suhu":        clean(t2m.get(last_key)),
            "kelembaban":  clean(rh2m.get(last_key)),
            "curah_hujan": clean(rain.get(last_key)),
            "tekanan":     clean(ps.get(last_key)),
            "sumber":      "NASA POWER",
            "parameter":   PARAMS,
        }
    except Exception as e:
        print(f"[NASA] Parse error: {e}")
        return None


def is_cache_valid(node_id, max_age_hours=CACHE_HOURS):
    """Cek apakah data cached masih fresh."""
    conn = get_db()
    row = conn.execute("""
        SELECT timestamp FROM env_data
        WHERE node_id = ?
        ORDER BY timestamp DESC LIMIT 1
    """, (node_id,)).fetchone()
    conn.close()

    if not row or not row["timestamp"]:
        return False

    try:
        ts = datetime.fromisoformat(row["timestamp"])
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        age_hours = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
        return age_hours < max_age_hours
    except Exception:
        return False


def save_env_data(node_id, env):
    """Simpan data lingkungan ke DB."""
    if not env:
        return False

    conn = get_db()
    conn.execute("""
        INSERT INTO env_data
          (node_id, timestamp, suhu, kelembaban, curah_hujan, tekanan, sumber, parameter)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        node_id,
        env["timestamp"],
        env["suhu"],
        env["kelembaban"],
        env["curah_hujan"],
        env["tekanan"],
        env["sumber"],
        env["parameter"],
    ))
    conn.commit()
    conn.close()
    return True


def get_env_for_node(node_id, lat, lon, force=False):
    """
    Ambil data lingkungan untuk 1 node.
    - Cek cache dulu (kecuali force=True)
    - Kalau cache expired → fetch baru dari NASA
    - Kalau fetch gagal → pakai cache lama (fallback)
    """
    # Cek cache
    if not force and is_cache_valid(node_id):
        conn = get_db()
        row = conn.execute("""
            SELECT timestamp, suhu, kelembaban, curah_hujan, tekanan, sumber
            FROM env_data
            WHERE node_id = ?
            ORDER BY timestamp DESC LIMIT 1
        """, (node_id,)).fetchone()
        conn.close()
        if row:
            return dict(row)

    # Fetch baru dari NASA
    # NASA POWER data ada delay ~2 hari, jadi minta H-3 sampai H-1
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=3)).strftime("%Y%m%d")
    end = (now - timedelta(days=1)).strftime("%Y%m%d")

    print(f"[NASA] Fetch untuk node {node_id} ({lat}, {lon})...")
    raw = fetch_from_nasa(lat, lon, start, end)
    parsed = parse_nasa_response(raw)

    if parsed:
        save_env_data(node_id, parsed)
        return parsed

    # Fallback: pakai cache lama kalau ada
    print(f"[NASA] Fallback ke cache lama untuk node {node_id}")
    conn = get_db()
    row = conn.execute("""
        SELECT timestamp, suhu, kelembaban, curah_hujan, tekanan, sumber
        FROM env_data
        WHERE node_id = ?
        ORDER BY timestamp DESC LIMIT 1
    """, (node_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_env_latest(node_id):
    """Ambil data lingkungan terbaru (dari cache saja)."""
    conn = get_db()
    row = conn.execute("""
        SELECT timestamp, suhu, kelembaban, curah_hujan, tekanan, sumber
        FROM env_data
        WHERE node_id = ?
        ORDER BY timestamp DESC LIMIT 1
    """, (node_id,)).fetchone()
    conn.close()
    return dict(row) if row else None