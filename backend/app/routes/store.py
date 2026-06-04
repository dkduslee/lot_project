from flask import Blueprint, request, jsonify, current_app

from ..services import seat_service, sensor_service

bp = Blueprint("store", __name__)


@bp.post("/store/live")
def store_live():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "body가 JSON이 아님"}), 400

    if "seatList" in data:
        seat_list = data["seatList"]
        rows = current_app.config["SEAT_ROWS"]
        cols = current_app.config["SEAT_COLS"]
        if (not isinstance(seat_list, list) or len(seat_list) != rows
                or any(not isinstance(r, list) or len(r) != cols for r in seat_list)):
            return jsonify({"error": f"seatList 사이즈가 서버 설정과 일치하지 않음 - .env파일 수정 필요 / 현재: {rows}x{cols}"}), 400

        changes = seat_service.update_from_seatlist(seat_list)
        return jsonify({"ok": True, "changes": changes}), 200

    if "positions" in data:
        if not isinstance(data["positions"], list):
            return jsonify({"error": "positions는 list 타입이어야함"}), 400
        return jsonify({"ok": True}), 200

    return jsonify({"error": "필수 키 누락"}), 400


@bp.post("/store/temphum")
def store_temphum():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "temp" not in data or "hum" not in data:
        return jsonify({"error": "필수 키 누락"}), 400
    try:
        temp = float(data["temp"])
        hum = float(data["hum"])
    except (TypeError, ValueError):
        return jsonify({"error": "입력 값이 숫자형이 아님"}), 400

    sensor_service.save_reading(temp, hum)
    return jsonify({"ok": True}), 200
