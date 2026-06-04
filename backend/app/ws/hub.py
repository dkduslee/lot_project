import json
import threading


# 알림용 웹소켓 관리
class WSHub:
    def __init__(self):
        self._clients = set()
        self._lock = threading.Lock()

    def register(self, ws):
        with self._lock:
            self._clients.add(ws)

    def unregister(self, ws):
        with self._lock:
            self._clients.discard(ws)

    # 주어진 객체 json 문자열 형태로 만들어서 소켓으로 뿌린다
    def broadcast(self, payload):
        msg = json.dumps(payload)
        with self._lock:
            targets = list(self._clients)
        dead = []
        for ws in targets:
            try:
                ws.send(msg)
            except Exception:
                dead.append(ws)
        if dead:
            with self._lock:
                for ws in dead:
                    self._clients.discard(ws)


hub = WSHub()
