import threading
import time

from ..db import new_connection
from ..repositories import seat_repo
from ..ws.hub import hub

_thread = None


def start_checkout_worker(app):
    global _thread
    if _thread is not None and _thread.is_alive():
        return

    threshold = app.config["AUTO_CHECKOUT_SECONDS"]
    interval = app.config["CHECK_INTERVAL_SECONDS"]

    # 지정된 주기마다 돌면서 빈 좌석 검사
    def loop():
        conn = new_connection(app)
        try:
            while True:
                time.sleep(interval)
                try:
                    _check_unusable_seat(conn, threshold)
                except Exception as e:
                    # 에러 로그를 남기고 다음 주기에 다시 시도
                    print(f"Worker Error: {e}")
        finally:
            conn.close()

    _thread = threading.Thread(target=loop, name="checkout-worker", daemon=True)
    _thread.start()


# 실제로 일정 시간 이상 비어있는 좌석을 찾는다
def _check_unusable_seat(conn, threshold):
    now = time.time()
    stale = seat_repo.fetch_stale_occupied(conn, now - threshold)
    changes = []
    for r in stale:
        seat_repo.set_occupied(conn, r["row"], r["col"], False, now)
        seat_repo.add_event(conn, r["row"], r["col"], "AUTO_CHECKOUT", now)
        changes.append({"x": r["row"], "y": r["col"], "newStatus": False})

    if changes:
        conn.commit()
        hub.broadcast({"latestSeat": changes})
