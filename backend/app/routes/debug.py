import os
import glob
from flask import Blueprint, current_app, send_file, jsonify, render_template

bp = Blueprint("debug", __name__)


# 최신 프레임 파일 찾아서 리턴
@bp.get("/debug/frame")
def debug_frame():
    frames_dir = current_app.config["FRAMES_DIR"]
    candidates = glob.glob(os.path.join(frames_dir, "*.png")) + glob.glob(os.path.join(frames_dir, "*.jpg"))
    if not candidates:
        return jsonify({"error": "프레임 파일이 없음"}), 404

    latest = max(candidates, key=os.path.getmtime)
    return send_file(latest, mimetype="image/png", max_age=0)


@bp.get("/debug/live")
def debug_live():
    return render_template("live_debug.html")