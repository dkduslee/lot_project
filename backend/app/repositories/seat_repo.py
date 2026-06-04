# 모든 좌석 데이터 가져오기
def fetch_all(conn):
    return conn.execute(
        "SELECT row, col, occupied, last_changed_at, last_seen_at FROM seats"
    ).fetchall()


# 해당 좌석 사용 중으로 바꾸기
def set_occupied(conn, row, col, occupied, ts):
    conn.execute(
        """UPDATE seats
           SET occupied = ?, last_changed_at = ?, last_seen_at = ?
           WHERE row = ? AND col = ?""",
        (1 if occupied else 0, ts, ts, row, col),
    )


# 마지막 상태 갱신 시각 갱신
def touch_seen(conn, row, col, ts):
    conn.execute(
        "UPDATE seats SET last_seen_at = ? WHERE row = ? AND col = ?",
        (ts, row, col),
    )


# 자동 반납 대상 조회
def fetch_stale_occupied(conn, before_ts):
    return conn.execute(
        """SELECT row, col FROM seats
           WHERE occupied = 1 AND last_seen_at < ?""",
        (before_ts,),
    ).fetchall()


# 좌석 상태 변경 기록
def add_event(conn, row, col, event_type, ts):
    conn.execute(
        """INSERT INTO seat_events (row, col, event_type, created_at)
           VALUES (?, ?, ?, ?)""",
        (row, col, event_type, ts),
    )
