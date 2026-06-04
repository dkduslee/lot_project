from ..ws.hub import hub


# 알림용 웹소켓 연결
def register_ws(sock):
    @sock.route("/ws/notify")
    def notify(ws):
        hub.register(ws)
        try:
            while True:
                msg = ws.receive()
                if msg is None:
                    break
        finally:
            hub.unregister(ws)
