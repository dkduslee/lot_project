import os
from flask import Blueprint, current_app, send_file, jsonify, render_template

bp = Blueprint("debug", __name__)


# 최신 프레임 파일 바로 리턴
@bp.get("/debug/frame")
def debug_frame():
    frames_dir = current_app.config["FRAMES_DIR"]
    latest_path = os.path.join(frames_dir, "latest.png")

    if not os.path.exists(latest_path):
        return jsonify({"error": "프레임 파일이 없음"}), 404

    return send_file(latest_path, mimetype="image/png", max_age=0)


@bp.get("/debug/live")
def debug_live():
    return render_template("live_debug.html")