import os
from dotenv import load_dotenv

# 프로젝트 루트 경로 가져온다
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _as_bool(v, default=False):
    if v is None:
        return default
    return str(v).strip().lower() in ("1", "true", "yes", "on")


def _resolve(path):
    return path if os.path.isabs(path) else os.path.join(BASE_DIR, path)


# .env 파일 내용 로드
def load_config(app):
    load_dotenv(os.path.join(BASE_DIR, ".env"))

    app.config["HOST"] = os.getenv("HOST", "0.0.0.0")
    app.config["PORT"] = int(os.getenv("PORT", "5000"))
    app.config["DEBUG"] = _as_bool(os.getenv("DEBUG"), True)

    app.config["SEAT_ROWS"] = int(os.getenv("SEAT_ROWS", "2"))
    app.config["SEAT_COLS"] = int(os.getenv("SEAT_COLS", "4"))

    app.config["AUTO_CHECKOUT_SECONDS"] = float(os.getenv("AUTO_CHECKOUT_SECONDS", "10"))
    app.config["CHECK_INTERVAL_SECONDS"] = float(os.getenv("CHECK_INTERVAL_SECONDS", "2"))

    app.config["DB_PATH"] = _resolve(os.getenv("DB_PATH", "data/app.db"))
    app.config["FRAMES_DIR"] = _resolve(os.getenv("FRAMES_DIR", "frames"))
