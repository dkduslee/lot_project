# 온습도 값 추가
def insert(conn, temp, hum, ts):
    conn.execute(
        "INSERT INTO sensor_readings (temp, hum, created_at) VALUES (?, ?, ?)",
        (temp, hum, ts),
    )


# 온습도값 가져오기
def latest(conn):
    return conn.execute(
        "SELECT temp, hum, created_at FROM sensor_readings ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
