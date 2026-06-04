-- 좌석 현재 상태
CREATE TABLE IF NOT EXISTS seats (
    row             INTEGER NOT NULL,
    col             INTEGER NOT NULL,
    occupied        INTEGER NOT NULL DEFAULT 0,   -- 0=EMPTY, 1=OCCUPIED
    last_changed_at REAL    NOT NULL,
    last_seen_at    REAL    NOT NULL,
    PRIMARY KEY (row, col)
);

-- 좌석 상태 변경 이력
CREATE TABLE IF NOT EXISTS seat_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    row         INTEGER NOT NULL,
    col         INTEGER NOT NULL,
    event_type  TEXT    NOT NULL,                 -- 'OCCUPIED' | 'AUTO_CHECKOUT'
    created_at  REAL    NOT NULL
);

-- 온습도
CREATE TABLE IF NOT EXISTS sensor_readings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    temp        REAL    NOT NULL,
    hum         REAL    NOT NULL,
    created_at  REAL    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sensor_created ON sensor_readings (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_created ON seat_events (created_at DESC);
