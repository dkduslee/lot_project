import os
import sqlite3
import time
from flask import current_app, g

from app.config import BASE_DIR

# 기본 스케마 파일 경로
SCHEMA_FILE = os.path.join(BASE_DIR, "schema.sql")


# db 연결
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DB_PATH"],
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False,
            timeout=5.0
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL;")
    return g.db


# db 닫기
def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# 커넥션 추가
def new_connection(app):
    conn = sqlite3.connect(
        app.config["DB_PATH"],
        detect_types=sqlite3.PARSE_DECLTYPES,
        check_same_thread=False,
        timeout=5.0
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


# db 초기화
def init_db(app):
    app.teardown_appcontext(close_db)

    conn = new_connection(app)
    try:
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

        rows = app.config["SEAT_ROWS"]
        cols = app.config["SEAT_COLS"]
        now = time.time()
        
        # 콘피그에서 설정한 행열 개수만큼으로 테이블에 값 초기화
        for r in range(rows):
            for c in range(cols):
                conn.execute(
                    """INSERT OR IGNORE INTO seats
                       (row, col, occupied, last_changed_at, last_seen_at)
                       VALUES (?, ?, 0, ?, ?)""",
                    (r, c, now, now),
                )
        conn.commit()
    finally:
        conn.close()
