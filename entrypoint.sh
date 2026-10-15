#!/bin/sh
set -e

DB_FILE="${DB_DIR:-/app/data}/vibralens.db"

echo "================================================"
echo "  VIBRALENS · Starting"
echo "================================================"
echo "  Time:    $(date)"
echo "  DB file: $DB_FILE"

mkdir -p "$(dirname "$DB_FILE")"

if [ ! -L /app/vibralens.db ]; then
    ln -sf "$DB_FILE" /app/vibralens.db
    echo "  Symlink /app/vibralens.db → $DB_FILE"
fi

if [ ! -f "$DB_FILE" ] || [ ! -s "$DB_FILE" ]; then
    echo "  Database belum ada → jalankan seeder..."
    python seed.py --force
else
    echo "  Database sudah ada → skip seeding."
fi

echo "================================================"
echo "  Menjalankan: $@"
echo "================================================"

exec "$@"