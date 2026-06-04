from app import create_app
from flask import Flask, render_template

app = create_app()

@app.route('/')
def index():
    return render_template('interface.html')

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
