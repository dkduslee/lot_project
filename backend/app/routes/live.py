from flask import Blueprint, jsonify

from ..services import seat_service, sensor_service

bp = Blueprint("live", __name__)


# 최신 좌석 및 온습도 정보 리턴
@bp.get("/get/live")
def get_live():
    temp, hum = sensor_service.latest()
    seat_list = seat_service.get_seat_matrix()
    return jsonify({
        "temp": temp,
        "hum": hum,
        "seatList": seat_list,
    }), 200
