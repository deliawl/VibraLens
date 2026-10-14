"""
VibraLens · Seeder
Isi database dengan 6 node + readings + HVSR + events + env_data.
"""
import json
import math
import random
import sqlite3
from datetime import datetime, timedelta, timezone

from database import get_db, init_db


# ============================================================
# NODES — metadata lengkap
# ============================================================
NODES_SEED = [
    {
        "id": "A", "kode": "VBL-GP-A01", "nama": "Rektorat Unpad",
        "instrumen": {
            "model": "Geophone SM-24", "manufaktur": "Sensor Nederland",
            "serial_number": "SN-2024-A01", "tipe_sensor": "Geophone 3-komponen",
            "jumlah_kanal": 3, "satuan": "mm/s", "sampling_rate": 100,
            "frekuensi_kerja": "1–100 Hz", "tanggal_instalasi": "2024-08-15",
            "status": "aktif", "kalibrasi_terakhir": "2025-06-10",
        },
        "sensor_tambahan": [],
        "lokasi": {"latitude": -6.9238, "longitude": 107.7698, "elevasi": 725,
                   "deskripsi": "Atap Gedung Rektorat Lt. 3", "kawasan": "Unpad Jatinangor"},
        "data": {"format": "miniSEED + JSON", "stream_endpoint": "/api/nodes/A/stream",
                 "interval_kirim": 10, "buffer_window": 1800,
                 "resolusi_bit": 24, "enkripsi": "TLS 1.3"},
        "katalog": {"kode_katalog": "VBL.2024.GP.A",
                    "pemilik": "Prodi Geofisika, Universitas Padjadjaran",
                    "penanggung_jawab": "Delia Wulandari", "kontak": "deliawulandari348@gmail.com",
                    "lisensi": "CC BY-NC 4.0", "versi": "1.0",
                    "tgl_dibuat": "2024-08-20", "bahasa": "id, en"},
        "hvsr": {"f0": 4.2, "a0": 3.8, "kg": 3.44, "zona": "sedang"},
    },
    {
        "id": "B", "kode": "VBL-GP-B01", "nama": "Fakultas Teknik",
        "instrumen": {
            "model": "Geophone SM-24", "manufaktur": "Sensor Nederland",
            "serial_number": "SN-2024-B01", "tipe_sensor": "Geophone 3-komponen",
            "jumlah_kanal": 3, "satuan": "mm/s", "sampling_rate": 100,
            "frekuensi_kerja": "1–100 Hz", "tanggal_instalasi": "2024-08-15",
            "status": "aktif", "kalibrasi_terakhir": "2025-06-10",
        },
        "sensor_tambahan": [],
        "lokasi": {"latitude": -6.9187, "longitude": 107.7740, "elevasi": 742,
                   "deskripsi": "Atap Gedung FTTM Lt. 2", "kawasan": "Unpad Jatinangor"},
        "data": {"format": "miniSEED + JSON", "stream_endpoint": "/api/nodes/B/stream",
                 "interval_kirim": 10, "buffer_window": 1800,
                 "resolusi_bit": 24, "enkripsi": "TLS 1.3"},
        "katalog": {"kode_katalog": "VBL.2024.GP.B",
                    "pemilik": "Prodi Geofisika, Universitas Padjadjaran",
                    "penanggung_jawab": "Delia Wulandari", "kontak": "deliawulandari348@gmail.com",
                    "lisensi": "CC BY-NC 4.0", "versi": "1.0",
                    "tgl_dibuat": "2024-08-20", "bahasa": "id, en"},
        "hvsr": {"f0": 3.8, "a0": 4.1, "kg": 4.42, "zona": "sedang"},
    },
    {
        "id": "C", "kode": "VBL-GP-C01", "nama": "Gerbang Utama",
        "instrumen": {
            "model": "Geophone SM-24", "manufaktur": "Sensor Nederland",
            "serial_number": "SN-2024-C01", "tipe_sensor": "Geophone 3-komponen",
            "jumlah_kanal": 3, "satuan": "mm/s", "sampling_rate": 100,
            "frekuensi_kerja": "1–100 Hz", "tanggal_instalasi": "2024-09-01",
            "status": "aktif", "kalibrasi_terakhir": "2025-06-10",
        },
        "sensor_tambahan": [],
        "lokasi": {"latitude": -6.9285, "longitude": 107.7672, "elevasi": 720,
                   "deskripsi": "Pos Satpam Gerbang Utama", "kawasan": "Unpad Jatinangor"},
        "data": {"format": "miniSEED + JSON", "stream_endpoint": "/api/nodes/C/stream",
                 "interval_kirim": 10, "buffer_window": 1800,
                 "resolusi_bit": 24, "enkripsi": "TLS 1.3"},
        "katalog": {"kode_katalog": "VBL.2024.GP.C",
                    "pemilik": "Prodi Geofisika, Universitas Padjadjaran",
                    "penanggung_jawab": "Delia Wulandari", "kontak": "deliawulandari348@gmail.com",
                    "lisensi": "CC BY-NC 4.0", "versi": "1.0",
                    "tgl_dibuat": "2024-09-05", "bahasa": "id, en"},
        "hvsr": {"f0": 2.1, "a0": 5.6, "kg": 14.93, "zona": "rawan"},
    },
    {
        "id": "D", "kode": "VBL-GP-D01", "nama": "Fakultas MIPA",
        "instrumen": {
            "model": "Geophone SM-24", "manufaktur": "Sensor Nederland",
            "serial_number": "SN-2024-D01", "tipe_sensor": "Geophone 3-komponen",
            "jumlah_kanal": 3, "satuan": "mm/s", "sampling_rate": 100,
            "frekuensi_kerja": "1–100 Hz", "tanggal_instalasi": "2024-09-01",
            "status": "aktif", "kalibrasi_terakhir": "2025-06-10",
        },
        "sensor_tambahan": [],
        "lokasi": {"latitude": -6.9210, "longitude": 107.7735, "elevasi": 730,
                   "deskripsi": "Atap Gedung FMIPA Lt. 4", "kawasan": "Unpad Jatinangor"},
        "data": {"format": "miniSEED + JSON", "stream_endpoint": "/api/nodes/D/stream",
                 "interval_kirim": 10, "buffer_window": 1800,
                 "resolusi_bit": 24, "enkripsi": "TLS 1.3"},
        "katalog": {"kode_katalog": "VBL.2024.GP.D",
                    "pemilik": "Prodi Geofisika, Universitas Padjadjaran",
                    "penanggung_jawab": "Delia Wulandari", "kontak": "deliawulandari348@gmail.com",
                    "lisensi": "CC BY-NC 4.0", "versi": "1.0",
                    "tgl_dibuat": "2024-09-05", "bahasa": "id, en"},
        "hvsr": {"f0": 5.1, "a0": 3.2, "kg": 2.01, "zona": "aman"},
    },
    {
        "id": "E", "kode": "VBL-GP-E01", "nama": "Asrama Mahasiswa",
        "instrumen": {
            "model": "Geophone SM-24", "manufaktur": "Sensor Nederland",
            "serial_number": "SN-2024-E01", "tipe_sensor": "Geophone 3-komponen",
            "jumlah_kanal": 3, "satuan": "mm/s", "sampling_rate": 100,
            "frekuensi_kerja": "1–100 Hz", "tanggal_instalasi": "2024-10-10",
            "status": "aktif", "kalibrasi_terakhir": "2025-06-10",
        },
        "sensor_tambahan": [],
        "lokasi": {"latitude": -6.9265, "longitude": 107.7755, "elevasi": 715,
                   "deskripsi": "Atap Asrama Putri Blok C", "kawasan": "Unpad Jatinangor"},
        "data": {"format": "miniSEED + JSON", "stream_endpoint": "/api/nodes/E/stream",
                 "interval_kirim": 10, "buffer_window": 1800,
                 "resolusi_bit": 24, "enkripsi": "TLS 1.3"},
        "katalog": {"kode_katalog": "VBL.2024.GP.E",
                    "pemilik": "Prodi Geofisika, Universitas Padjadjaran",
                    "penanggung_jawab": "Delia Wulandari", "kontak": "deliawulandari348@gmail.com",
                    "lisensi": "CC BY-NC 4.0", "versi": "1.0",
                    "tgl_dibuat": "2024-10-15", "bahasa": "id, en"},
        "hvsr": {"f0": 1.8, "a0": 6.4, "kg": 22.76, "zona": "rawan"},
    },
    {
        "id": "F", "kode": "VBL-GP-F01", "nama": "Perpustakaan Pusat",
        "instrumen": {
            "model": "Geophone SM-24", "manufaktur": "Sensor Nederland",
            "serial_number": "SN-2024-F01", "tipe_sensor": "Geophone 3-komponen",
            "jumlah_kanal": 3, "satuan": "mm/s", "sampling_rate": 100,
            "frekuensi_kerja": "1–100 Hz", "tanggal_instalasi": "2024-10-10",
            "status": "nonaktif", "kalibrasi_terakhir": "2025-06-10",
        },
        "sensor_tambahan": [],
        "lokasi": {"latitude": -6.9203, "longitude": 107.7663, "elevasi": 728,
                   "deskripsi": "Atap Gedung Perpustakaan Lt. 5", "kawasan": "Unpad Jatinangor"},
        "data": {"format": "miniSEED + JSON", "stream_endpoint": "/api/nodes/F/stream",
                 "interval_kirim": 10, "buffer_window": 1800,
                 "resolusi_bit": 24, "enkripsi": "TLS 1.3"},
        "katalog": {"kode_katalog": "VBL.2024.GP.F",
                    "pemilik": "Prodi Geofisika, Universitas Padjadjaran",
                    "penanggung_jawab": "Delia Wulandari", "kontak": "deliawulandari348@gmail.com",
                    "lisensi": "CC BY-NC 4.0", "versi": "1.0",
                    "tgl_dibuat": "2024-10-15", "bahasa": "id, en"},
        "hvsr": {"f0": 4.5, "a0": 3.5, "kg": 2.72, "zona": "aman"},
    },
]


# ============================================================
# Helper
# ============================================================
def hitung_status(pgv, umur_detik=None):
    if pgv is None:
        return "offline"
    if umur_detik is not None and umur_detik > 60:
        return "offline"
    if pgv > 1.0:
        return "alert"
    if pgv > 0.5:
        return "warn"
    return "ok"


def generate_readings(node_id, hours=24, interval_seconds=300):
    """Generate dummy readings untuk 1 node."""
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=hours)

    base_pgv = {
        "A": 0.40, "B": 0.30, "C": 0.85, "D": 0.25, "E": 1.40, "F": None,
    }.get(node_id, 0.35)

    readings = []
    t = start
    while t <= now:
        if base_pgv is None:
            pgv = None
            status = "offline"
        else:
            pgv = max(0.02, base_pgv + random.gauss(0, 0.08))
            status = hitung_status(pgv)

        readings.append({
            "node_id": node_id,
            "timestamp": t.isoformat(),
            "pgv": pgv,
            "pga": (pgv / 1000 * 9.81) if pgv else None,
            "freq_dom": round(random.uniform(1.5, 6.5), 2),
            "rms": round(pgv * 0.7, 3) if pgv else None,
            "kanal_1": round(pgv * random.uniform(.9, 1.1), 3) if pgv else None,
            "kanal_2": round(pgv * random.uniform(.9, 1.1), 3) if pgv else None,
            "kanal_3": round(pgv * random.uniform(.9, 1.1), 3) if pgv else None,
            "curah_hujan": round(random.uniform(0, 8), 2),
            "kelembaban": round(random.uniform(55, 92), 1),
            "suhu": round(random.uniform(18, 28), 1),
            "tekanan": round(random.uniform(1005, 1015), 1),
            "status": status,
        })
        t += timedelta(seconds=interval_seconds)

    return readings


def generate_hvsr_curve(f0, a0):
    """Bikin kurva HVSR sintetis dengan puncak di f0."""
    freqs = [0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7, 1.9, 2.1, 2.3,
             2.5, 2.7, 2.9, 3.1, 3.3, 3.5, 3.7, 3.9, 4.1, 4.3,
             4.5, 4.7, 5.0, 5.5, 6.0, 6.5, 7.0, 8.0, 9.0, 10.0]
    amps = []
    for f in freqs:
        g = a0 * (1 / (1 + ((f - f0) / 0.8) ** 2))
        amps.append(round(max(1.0, g + random.uniform(-0.15, 0.15)), 3))
    return freqs, amps


def generate_env_data(node_id, days=7):
    """Generate dummy data lingkungan (simulasi NASA POWER) untuk 7 hari."""
    now = datetime.now(timezone.utc)
    data = []

    for h in range(days * 24):
        t = now - timedelta(hours=h)

        # Pola harian: suhu tinggi siang, rendah malam
        hour = t.hour
        suhu_base = 25 + 4 * math.sin((hour - 6) * math.pi / 12)
        suhu = round(suhu_base + random.uniform(-1.5, 1.5), 2)

        # Kelembaban berkebalikan dengan suhu
        kelembaban = round(85 - (suhu - 20) * 1.5 + random.uniform(-5, 5), 1)
        kelembaban = max(40, min(95, kelembaban))

        # Hujan random
        if random.random() < 0.1:
            curah_hujan = round(random.uniform(0.5, 8), 2)
        else:
            curah_hujan = 0

        # Tekanan ~101 kPa
        tekanan = round(101 + random.uniform(-0.8, 0.8), 2)

        data.append({
            "node_id": node_id,
            "timestamp": t.isoformat(),
            "suhu": suhu,
            "kelembaban": kelembaban,
            "curah_hujan": curah_hujan,
            "tekanan": tekanan,
            "sumber": "NASA POWER",
            "parameter": "T2M,RH2M,PRECTOTCORR,PS",
        })

    return data


# ============================================================
# Seed
# ============================================================
def seed_all(force=False):
    init_db(force=force)
    conn = get_db()
    cur = conn.cursor()

    # Bersihkan data lama
    cur.executescript("""
        DELETE FROM env_data;
        DELETE FROM events;
        DELETE FROM hvsr_results;
        DELETE FROM readings;
        DELETE FROM nodes;
    """)

    now = datetime.now(timezone.utc)

    # ============ Insert nodes ============
    print(f"[SEED] Insert {len(NODES_SEED)} node...")
    for n in NODES_SEED:
        metadata = {
            "instrumen": n["instrumen"],
            "sensor_tambahan": n["sensor_tambahan"],
            "data": n["data"],
            "katalog": n["katalog"],
        }
        cur.execute("""
            INSERT INTO nodes (id, kode, nama, latitude, longitude, elevasi,
                               deskripsi, kawasan, metadata_json, aktif)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            n["id"], n["kode"], n["nama"],
            n["lokasi"]["latitude"], n["lokasi"]["longitude"], n["lokasi"]["elevasi"],
            n["lokasi"]["deskripsi"], n["lokasi"]["kawasan"],
            json.dumps(metadata, ensure_ascii=False),
            0 if n["instrumen"]["status"] == "nonaktif" else 1,
        ))

    # ============ Insert readings ============
    print("[SEED] Generate readings (24 jam, interval 5 menit)...")
    total = 0
    for n in NODES_SEED:
        readings = generate_readings(n["id"], hours=24, interval_seconds=300)
        cur.executemany("""
            INSERT INTO readings
              (node_id, timestamp, pgv, pga, freq_dom, rms,
               kanal_1, kanal_2, kanal_3,
               curah_hujan, kelembaban, suhu, tekanan, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (r["node_id"], r["timestamp"], r["pgv"], r["pga"], r["freq_dom"],
             r["rms"], r["kanal_1"], r["kanal_2"], r["kanal_3"],
             r["curah_hujan"], r["kelembaban"], r["suhu"], r["tekanan"], r["status"])
            for r in readings
        ])
        total += len(readings)
    print(f"       → {total} readings total")

    # ============ Insert HVSR ============
    print("[SEED] Generate HVSR results...")
    for n in NODES_SEED:
        hvsr = n["hvsr"]
        freqs, amps = generate_hvsr_curve(hvsr["f0"], hvsr["a0"])
        window_end = now
        window_start = now - timedelta(minutes=30)
        cur.execute("""
            INSERT INTO hvsr_results
              (node_id, window_start, window_end, f0, a0, kg, zona,
               frekuensi_json, amplifikasi_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            n["id"], window_start.isoformat(), window_end.isoformat(),
            hvsr["f0"], hvsr["a0"], hvsr["kg"], hvsr["zona"],
            json.dumps(freqs), json.dumps(amps),
        ))

    # ============ Insert events ============
    print("[SEED] Generate event log...")
    events = [
        ("E", now - timedelta(hours=2), "alert", "PGV melebihi 1.0 mm/s", 1.42),
        ("C", now - timedelta(hours=5), "warn", "PGV melebihi 0.5 mm/s", 0.88),
        ("F", now - timedelta(hours=12), "offline", "Tidak ada data >60 detik", None),
        ("F", now - timedelta(hours=10), "online", "Node kembali online", None),
    ]
    cur.executemany("""
        INSERT INTO events (node_id, timestamp, tipe, pesan, nilai)
        VALUES (?, ?, ?, ?, ?)
    """, [(n, t.isoformat(), tp, p, v) for n, t, tp, p, v in events])

    # ============ Insert ENV_DATA (simulasi NASA POWER) ============
    print("[SEED] Generate data lingkungan (7 hari)...")
    env_total = 0
    for n in NODES_SEED:
        env_rows = generate_env_data(n["id"], days=7)
        cur.executemany("""
            INSERT INTO env_data
              (node_id, timestamp, suhu, kelembaban, curah_hujan, tekanan, sumber, parameter)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (e["node_id"], e["timestamp"], e["suhu"], e["kelembaban"],
             e["curah_hujan"], e["tekanan"], e["sumber"], e["parameter"])
            for e in env_rows
        ])
        env_total += len(env_rows)
    print(f"       → {env_total} record env_data")

    conn.commit()
    conn.close()
    print(f"\n✅ Seed selesai.")
    print(f"   Database: vibralens.db")


if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv or "-f" in sys.argv
    seed_all(force=force)