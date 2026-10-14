-- ============================================================
-- VIBRALENS · SCHEMA SQLITE
-- ============================================================

PRAGMA foreign_keys = ON;

-- ============================================================
-- 1. NODES — metadata lengkap (jarang berubah)
-- ============================================================
CREATE TABLE IF NOT EXISTS nodes (
  id              TEXT PRIMARY KEY,
  kode            TEXT UNIQUE NOT NULL,
  nama            TEXT NOT NULL,

  latitude        REAL NOT NULL,
  longitude       REAL NOT NULL,
  elevasi         INTEGER,
  deskripsi       TEXT,
  kawasan         TEXT,

  -- Metadata nested (instrumen, sensor_tambahan, katalog) → JSON
  metadata_json   TEXT NOT NULL,

  aktif           INTEGER DEFAULT 1,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_nodes_kode ON nodes(kode);

-- ============================================================
-- 2. READINGS — time-series data sensor
-- ============================================================
CREATE TABLE IF NOT EXISTS readings (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  node_id         TEXT NOT NULL,
  timestamp       DATETIME NOT NULL,

  -- Getaran
  pgv             REAL,        -- mm/s
  pga             REAL,        -- m/s²
  freq_dom        REAL,        -- Hz
  rms             REAL,

  kanal_1         REAL,        -- mm/s
  kanal_2         REAL,
  kanal_3         REAL,

  -- Lingkungan
  curah_hujan     REAL,        -- mm
  kelembaban      REAL,        -- %
  suhu            REAL,        -- °C
  tekanan         REAL,        -- hPa

  status          TEXT,        -- 'ok','warn','alert','offline'

  FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_readings_node_time
  ON readings(node_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_readings_time
  ON readings(timestamp DESC);

-- ============================================================
-- 3. HVSR_RESULTS — hasil olahan HVSR per window
-- ============================================================
CREATE TABLE IF NOT EXISTS hvsr_results (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  node_id          TEXT NOT NULL,
  window_start     DATETIME NOT NULL,
  window_end       DATETIME NOT NULL,

  f0               REAL,       -- Hz
  a0               REAL,       -- amplifikasi
  kg               REAL,       -- A0²/f0
  zona             TEXT,       -- 'aman','sedang','rawan'

  frekuensi_json   TEXT,       -- JSON array
  amplifikasi_json TEXT,       -- JSON array

  FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_hvsr_node_time
  ON hvsr_results(node_id, window_start DESC);

-- ============================================================
-- 4. EVENTS — log alert/offline/online
-- ============================================================
CREATE TABLE IF NOT EXISTS events (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  node_id         TEXT NOT NULL,
  timestamp       DATETIME NOT NULL,
  tipe            TEXT NOT NULL,   -- 'alert','warn','offline','online'
  pesan           TEXT,
  nilai           REAL,

  FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_events_time ON events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_node ON events(node_id, timestamp DESC);

-- ============================================================
-- 5. VIEW — data terbaru per node (untuk dashboard)
-- ============================================================
DROP VIEW IF EXISTS node_latest;
CREATE VIEW node_latest AS
SELECT
  n.id,
  n.kode,
  n.nama,
  n.latitude,
  n.longitude,
  n.elevasi,
  n.deskripsi,
  n.kawasan,
  n.metadata_json,
  n.aktif,
  r.pgv,
  r.pga,
  r.freq_dom,
  r.rms,
  r.kanal_1, r.kanal_2, r.kanal_3,
  r.curah_hujan, r.kelembaban, r.suhu, r.tekanan,
  r.status,
  r.timestamp            AS last_reading_at,
  h.f0, h.a0, h.kg, h.zona,
  h.window_start         AS hvsr_window_start
FROM nodes n
LEFT JOIN readings r ON r.id = (
  SELECT id FROM readings WHERE node_id = n.id ORDER BY timestamp DESC LIMIT 1
)
LEFT JOIN hvsr_results h ON h.id = (
  SELECT id FROM hvsr_results WHERE node_id = n.id ORDER BY window_start DESC LIMIT 1
);

-- ============================================================
-- 6. ENV_DATA — data lingkungan dari satelit (NASA POWER)
-- ============================================================
CREATE TABLE IF NOT EXISTS env_data (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  node_id       TEXT NOT NULL,
  timestamp     DATETIME NOT NULL,

  suhu          REAL,        -- °C
  kelembaban    REAL,        -- %
  curah_hujan   REAL,        -- mm
  tekanan       REAL,        -- kPa

  sumber        TEXT DEFAULT 'NASA POWER',
  parameter     TEXT,        -- parameter NASA yang dipakai

  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_env_node_time
  ON env_data(node_id, timestamp DESC);