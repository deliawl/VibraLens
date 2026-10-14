"""
VibraLens · Database helper
"""
import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "vibralens.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_db():
    """Buka koneksi SQLite (row_factory = sqlite3.Row → dict-like)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(force=False):
    """Inisialisasi skema DB. force=True → hapus file lama & buat ulang."""
    if force and DB_PATH.exists():
        DB_PATH.unlink()
        print(f"[DB] Hapus file lama: {DB_PATH.name}")

    if not DB_PATH.exists():
        print(f"[DB] Membuat database baru: {DB_PATH.name}")

    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"[DB] Skema berhasil dimuat dari {SCHEMA_PATH.name}")


if __name__ == "__main__":
    init_db(force=True)