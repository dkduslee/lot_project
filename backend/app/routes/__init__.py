from .store import bp as store_bp
from .live import bp as live_bp
from .debug import bp as debug_bp
from .notify import register_ws


def register_routes(app, sock):
    app.register_blueprint(store_bp)
    app.register_blueprint(live_bp)
    app.register_blueprint(debug_bp)
    register_ws(sock)  # WebSocket 라우트 등록
