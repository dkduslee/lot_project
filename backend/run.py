from app import create_app

app = create_app()

# 서버 시작
if __name__ == "__main__":
    cfg = app.config
    app.run(
        host=cfg["HOST"],
        port=cfg["PORT"],
        debug=cfg["DEBUG"],
        threaded=True,
        use_reloader=False,
    )
