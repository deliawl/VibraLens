"""
VibraLens · Query helper
Semua fungsi query SQLite untuk dipakai di app.py
"""
import json
from datetime import datetime, timezone
from database import get_db


# ============================================================
# NODES
# ============================================================
def get_all_nodes():
    """Ambil SEMUA node (termasuk nonaktif) — untuk katalog."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM node_latest ORDER BY id").fetchall()
    conn.close()
    return [_row_to_node(r) for r in rows]


def get_active_nodes():
    """Ambil hanya node aktif — untuk peta & dashboard."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM node_latest WHERE aktif = 1 ORDER BY id"
    ).fetchall()
    conn.close()
    return [_row_to_node(r) for r in rows]


def get_node(node_id):
    """Ambil 1 node by ID."""
    conn = get_db()
    r = conn.execute("SELECT * FROM node_latest WHERE id = ?", (node_id,)).fetchone()
    conn.close()
    return _row_to_node(r) if r else None


def _row_to_node(r):
    """Convert row → dict lengkap dengan metadata ter-parse."""
    meta = json.loads(r["metadata_json"]) if r["metadata_json"] else {}

    umur = None
    if r["last_reading_at"]:
        try:
            ts = datetime.fromisoformat(r["last_reading_at"])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            umur = int((datetime.now(timezone.utc) - ts).total_seconds())
        except Exception:
            umur = None

    status = r["status"] or "offline"
    if umur is not None and umur > 3600:
        status = "offline"

    return {
        "id": r["id"],
        "kode": r["kode"],
        "nama": r["nama"],
        "aktif": bool(r["aktif"]),
        "instrumen": meta.get("instrumen", {}),
        "sensor_tambahan": meta.get("sensor_tambahan", []),
        "data": meta.get("data", {}),
        "katalog": meta.get("katalog", {}),
        "lokasi": {
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "elevasi": r["elevasi"],
            "deskripsi": r["deskripsi"],
            "kawasan": r["kawasan"],
        },
        "hvsr": {
            "f0": r["f0"],
            "a0": r["a0"],
            "kg": r["kg"],
            "zona": r["zona"],
        },
        "rt": {
            "pgv": r["pgv"],
            "pga": r["pga"],
            "freq_dom": r["freq_dom"],
            "status": status,
            "umur_detik": umur,
        },
        "env": get_env_latest(r["id"]),
    }


# ============================================================
# READINGS
# ============================================================
def get_readings(node_id, hours=24, limit=500):
    """Ambil readings N jam terakhir untuk 1 node."""
    conn = get_db()
    rows = conn.execute("""
        SELECT timestamp, pgv, pga, freq_dom, rms, status
        FROM readings
        WHERE node_id = ?
          AND timestamp >= datetime('now', ?)
        ORDER BY timestamp ASC
        LIMIT ?
    """, (node_id, f"-{hours} hours", limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pgv_series(hours=24, limit=24):
    """PGV agregat (max per bucket) — untuk chart ringkasan."""
    conn = get_db()
    rows = conn.execute("""
        SELECT pgv FROM readings
        WHERE timestamp >= datetime('now', ?)
          AND pgv IS NOT NULL
        ORDER BY timestamp ASC
    """, (f"-{hours} hours",)).fetchall()
    conn.close()

    values = [r["pgv"] for r in rows]
    if not values:
        return [0.0] * limit

    if len(values) <= limit:
        return values

    bucket_size = len(values) // limit
    result = []
    for i in range(limit):
        chunk = values[i * bucket_size:(i + 1) * bucket_size]
        if chunk:
            result.append(max(chunk))
    return result


# ============================================================
# HVSR
# ============================================================
def get_latest_hvsr(node_id):
    """HVSR terbaru untuk 1 node."""
    conn = get_db()
    r = conn.execute("""
        SELECT * FROM hvsr_results
        WHERE node_id = ?
        ORDER BY window_start DESC LIMIT 1
    """, (node_id,)).fetchone()
    conn.close()
    if not r:
        return None
    return {
        "f0": r["f0"],
        "a0": r["a0"],
        "kg": r["kg"],
        "zona": r["zona"],
        "frekuensi": json.loads(r["frekuensi_json"] or "[]"),
        "amplifikasi": json.loads(r["amplifikasi_json"] or "[]"),
    }


def get_hvsr_summary():
    """Rata-rata f0, a0, kg dari semua node."""
    conn = get_db()
    r = conn.execute("""
        SELECT
          AVG(f0) AS f0_avg,
          AVG(a0) AS a0_avg,
          AVG(kg) AS kg_avg
        FROM hvsr_results
        WHERE (node_id, window_start) IN (
          SELECT node_id, MAX(window_start) FROM hvsr_results GROUP BY node_id
        )
    """).fetchone()
    conn.close()
    return {
        "f0_rata": round(r["f0_avg"] or 0, 2),
        "a0_rata": round(r["a0_avg"] or 0, 2),
        "kg_rata": round(r["kg_avg"] or 0, 2),
    }


def get_hvsr_curve_rata():
    """Kurva HVSR rata-rata dari semua node."""
    conn = get_db()
    rows = conn.execute("""
        SELECT frekuensi_json, amplifikasi_json
        FROM hvsr_results
        WHERE (node_id, window_start) IN (
          SELECT node_id, MAX(window_start) FROM hvsr_results GROUP BY node_id
        )
    """).fetchall()
    conn.close()

    if not rows:
        return {"frekuensi": [], "amplifikasi": [], "f0_peak": 0, "a0_peak": 0}

    all_freqs = json.loads(rows[0]["frekuensi_json"])
    all_amps = [[] for _ in all_freqs]

    for r in rows:
        amps = json.loads(r["amplifikasi_json"])
        for i, a in enumerate(amps):
            if i < len(all_amps):
                all_amps[i].append(a)

    avg_amps = [round(sum(x) / len(x), 3) if x else 0 for x in all_amps]
    max_a = max(avg_amps) if avg_amps else 0
    idx_max = avg_amps.index(max_a) if avg_amps else 0
    f0_peak = all_freqs[idx_max] if all_freqs else 0

    return {
        "frekuensi": all_freqs,
        "amplifikasi": avg_amps,
        "f0_peak": f0_peak,
        "a0_peak": max_a,
    }


def get_hvsr_per_node():
    """HVSR summary per node (untuk tabel)."""
    conn = get_db()
    rows = conn.execute("""
        SELECT n.id, h.f0, h.a0, h.kg, h.zona
        FROM nodes n
        LEFT JOIN hvsr_results h ON h.id = (
          SELECT id FROM hvsr_results WHERE node_id = n.id
          ORDER BY window_start DESC LIMIT 1
        )
        WHERE n.aktif = 1
        ORDER BY n.id
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# EVENTS
# ============================================================
def get_events(node_id=None, limit=50):
    """Log event (alert/offline/online)."""
    conn = get_db()
    if node_id:
        rows = conn.execute("""
            SELECT * FROM events WHERE node_id = ?
            ORDER BY timestamp DESC LIMIT ?
        """, (node_id, limit)).fetchall()
    else:
        rows = conn.execute("""
            SELECT * FROM events ORDER BY timestamp DESC LIMIT ?
        """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# ENV DATA (dari satelit NASA POWER)
# ============================================================
def get_env_latest(node_id):
    """Ambil data lingkungan terbaru untuk 1 node."""
    conn = get_db()
    try:
        r = conn.execute("""
            SELECT timestamp, suhu, kelembaban, curah_hujan, tekanan, sumber
            FROM env_data
            WHERE node_id = ?
            ORDER BY timestamp DESC LIMIT 1
        """, (node_id,)).fetchone()
    except Exception:
        r = None
    conn.close()
    return dict(r) if r else None


def get_env_history(node_id, days=7):
    """Histori data lingkungan N hari terakhir."""
    conn = get_db()
    rows = conn.execute("""
        SELECT timestamp, suhu, kelembaban, curah_hujan, tekanan
        FROM env_data
        WHERE node_id = ?
          AND timestamp >= datetime('now', ?)
        ORDER BY timestamp ASC
    """, (node_id, f"-{days} days")).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ============================================================
# EVENTS (extended)
# ============================================================
def get_events_extended(node_id=None, tipe=None, limit=200):
    """Events dengan filter opsional (node + tipe)."""
    conn = get_db()
    sql = """
        SELECT e.*, n.nama AS node_nama, n.kode AS node_kode
        FROM events e
        LEFT JOIN nodes n ON e.node_id = n.id
        WHERE 1=1
    """
    params = []
    if node_id:
        sql += " AND e.node_id = ?"
        params.append(node_id)
    if tipe:
        sql += " AND e.tipe = ?"
        params.append(tipe)
    sql += " ORDER BY e.timestamp DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    conn.close()

    result = []
    for r in rows:
        d = dict(r)
        # Parse umur
        try:
            ts = datetime.fromisoformat(d["timestamp"])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            d["umur_detik"] = int((datetime.now(timezone.utc) - ts).total_seconds())
        except Exception:
            d["umur_detik"] = None
        result.append(d)
    return result


def get_event_summary():
    """Hitung jumlah event per tipe."""
    conn = get_db()
    rows = conn.execute("""
        SELECT tipe, COUNT(*) AS c FROM events GROUP BY tipe
    """).fetchall()
    conn.close()
    base = {"alert": 0, "warn": 0, "offline": 0, "online": 0}
    for r in rows:
        base[r["tipe"]] = r["c"]
    return base


# ============================================================
# READINGS (extended)
# ============================================================
def get_readings_filtered(node_id=None, date_from=None, date_to=None, limit=1000):
    """Readings dengan filter node + range tanggal."""
    conn = get_db()
    sql = "SELECT * FROM readings WHERE 1=1"
    params = []
    if node_id:
        sql += " AND node_id = ?"
        params.append(node_id)
    if date_from:
        sql += " AND timestamp >= ?"
        params.append(date_from)
    if date_to:
        sql += " AND timestamp <= ?"
        params.append(date_to)
    sql += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# SYSTEM INFO (pengaturan)
# ============================================================
def get_system_info():
    """Info sistem: versi, ukuran DB, jumlah record."""
    from database import DB_PATH

    conn = get_db()
    counts = {}
    for table in ["nodes", "readings", "hvsr_results", "events", "env_data"]:
        try:
            counts[table] = conn.execute(
                f"SELECT COUNT(*) AS c FROM {table}"
            ).fetchone()["c"]
        except Exception:
            counts[table] = 0
    conn.close()

    db_size = DB_PATH.stat().st_size if DB_PATH.exists() else 0

    return {
        "version": "1.0.0",
        "build": "2026.10",
        "db_path": str(DB_PATH),
        "db_size_kb": round(db_size / 1024, 1),
        "counts": counts,
        "thresholds": {
            "warn": 0.5,
            "alert": 1.0,
            "offline_seconds": 60,
        },
        "server_time": datetime.now(timezone.utc).isoformat(),
    }

# ============================================================
# STATS
# ============================================================
def get_sistem_stats():
    """Statistik ringkasan untuk beranda."""
    conn = get_db()

    total = conn.execute(
        "SELECT COUNT(*) AS c FROM nodes WHERE aktif = 1"
    ).fetchone()["c"]

    online = conn.execute("""
        SELECT COUNT(DISTINCT node_id) AS c
        FROM readings
        WHERE timestamp >= datetime('now', '-60 seconds')
    """).fetchone()["c"]

    pgv_max = conn.execute("""
        SELECT MAX(pgv) AS m FROM readings
        WHERE timestamp >= datetime('now', '-24 hours')
    """).fetchone()["m"] or 0

    last = conn.execute("SELECT MAX(timestamp) AS t FROM readings").fetchone()["t"]
    conn.close()

    umur = 0
    if last:
        try:
            ts = datetime.fromisoformat(last)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            umur = int((datetime.now(timezone.utc) - ts).total_seconds())
        except Exception:
            umur = 0

    hvsr = get_hvsr_summary()

    return {
        "total_node": total,
        "node_online": online,
        "pgv_max": round(pgv_max, 2),
        "update_detik": umur,
        "uptime_persen": 99.9,
        "f0_rata": hvsr["f0_rata"],
        "a0_rata": hvsr["a0_rata"],
        "kg_rata": hvsr["kg_rata"],
    }


# ============================================================
# WAVEFORM & ANALYSIS
# ============================================================
def get_waveform_for_node(node_id, duration=1800, fs=100):
    """
    Ambil waveform untuk analisis HVSR.

    SAAT INI: generate sintetis (dummy) — untuk demo.
    NANTI:    tinggal ganti sumber (dari DB, miniSEED, atau stream sensor).

    Kontrak fungsi:
        Return dict {z, n, e, fs, duration} — pipeline processing
        berikutnya nggak peduli sumber datanya dari mana.
    """
    from analysis.synth import generate_waveform

    node = get_node(node_id)
    if not node:
        return None

    f0_target = node["hvsr"]["f0"] or 4.0
    a0_target = node["hvsr"]["a0"] or 3.0

    waveform = generate_waveform(
        f0=f0_target,
        a0=a0_target,
        duration=duration,
        fs=fs,
    )
    waveform["node_id"] = node_id
    waveform["source"] = "synthetic"
    return waveform


def run_hvsr_analysis(node_id, duration=1800):
    """
    Pipeline lengkap:
        ambil waveform → preprocess → PSD → HVSR → interpretasi AI.

    Returns
    -------
    dict siap tampil di UI, atau None kalau node nggak ketemu.
    """
    from analysis.hvsr import compute_hvsr
    from analysis.interpretasi import interpret_hvsr
    import time as _time

    t_start = _time.time()

    node = get_node(node_id)
    if not node:
        return None

    # Step 1 — Ambil waveform
    wf = get_waveform_for_node(node_id, duration=duration)
    if not wf:
        return None

    # Step 2 — Hitung HVSR
    hvsr_result = compute_hvsr(
        wf["z"], wf["n"], wf["e"],
        fs=wf["fs"],
        f_min=0.5, f_max=20.0,
    )

    # Step 3 — Interpretasi AI (rule-based)
    interpretation = interpret_hvsr(
        hvsr_result["f0"],
        hvsr_result["a0"],
        hvsr_result["kg"],
        node_info=node,
    )

    t_end = _time.time()

    return {
        "node": {
            "id": node["id"],
            "kode": node["kode"],
            "nama": node["nama"],
            "lokasi": node["lokasi"],
        },
        "processing": {
            "duration_sec": duration,
            "fs_hz": wf["fs"],
            "samples": len(wf["z"]),
            "source": wf["source"],
            "processing_time_ms": round((t_end - t_start) * 1000, 1),
        },
        "hvsr": {
            "frekuensi": hvsr_result["frekuensi"],
            "hvsr": hvsr_result["hvsr"],
            "f0": hvsr_result["f0"],
            "a0": hvsr_result["a0"],
            "kg": hvsr_result["kg"],
            "zona": hvsr_result["zona"],
        },
        "target": {
            "f0": node["hvsr"]["f0"],
            "a0": node["hvsr"]["a0"],
            "kg": node["hvsr"]["kg"],
            "zona": node["hvsr"]["zona"],
        },
        "interpretation": interpretation,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }