import time

from ..db import get_db
from ..repositories import seat_repo
from ..ws.hub import hub


# DB에서 전체 좌석 정보 가져와 2차원 배열로 만들어 반환
def get_seat_matrix():
    conn = get_db()
    rows = seat_repo.fetch_all(conn)
    if not rows:
        return []
    max_r = max(r["row"] for r in rows)
    max_c = max(r["col"] for r in rows)
    matrix = [[False] * (max_c + 1) for _ in range(max_r + 1)]
    for r in rows:
        matrix[r["row"]][r["col"]] = bool(r["occupied"])
    return matrix


# 좌석 상태 갱신
def update_from_seatlist(seat_list):
    conn = get_db()
    now = time.time()
    current = {(r["row"], r["col"]): r for r in seat_repo.fetch_all(conn)}
    changes = []

    for r, line in enumerate(seat_list):
        for c, detected in enumerate(line):
            cur = current.get((r, c))
            if cur is None:
                continue
            was_occupied = bool(cur["occupied"])

            if detected and not was_occupied:
                seat_repo.set_occupied(conn, r, c, True, now)
                seat_repo.add_event(conn, r, c, "OCCUPIED", now)
                changes.append({"x": r, "y": c, "newStatus": True})
            elif detected and was_occupied:
                seat_repo.touch_seen(conn, r, c, now)
            elif not detected and was_occupied:
                pass

    conn.commit()

    # 변경 있으면 웹소켓으로 알림 전송
    if changes:
        hub.broadcast({"latestSeat": changes})
    return changes
