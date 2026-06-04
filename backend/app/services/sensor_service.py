import time
from ..db import get_db
from ..repositories import sensor_repo
from ..ws.hub import hub


# 센서값 저장
def save_reading(temp, hum):
    conn = get_db()
    sensor_repo.insert(conn, temp, hum, time.time())
    conn.commit()

    # 센서값 변경 시 웹소켓으로 알림
    hub.broadcast({
        "latestSensor": {
            "temp": temp,
            "hum": hum
        }
    })


def latest():
    conn = get_db()
    row = sensor_repo.latest(conn)
    if row is None:
        return None, None
    return row["temp"], row["hum"]