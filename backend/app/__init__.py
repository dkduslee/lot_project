import os
from flask import Flask

from .config import load_config
from .db import init_db
from .extensions import sock
from .routes import register_routes
from .services.checkout_worker import start_checkout_worker


def create_app():
    # 플라스크 초기화 및 콘피그 로드
    app = Flask(__name__)
    load_config(app)

    # 필수 폴더 생성
    os.makedirs(os.path.dirname(app.config["DB_PATH"]) or ".", exist_ok=True)
    os.makedirs(app.config["FRAMES_DIR"], exist_ok=True)

    sock.init_app(app)
    init_db(app)  # db 초기화
    register_routes(app, sock)
    start_checkout_worker(app)  # 자동 반납 워커 시작

    return app
