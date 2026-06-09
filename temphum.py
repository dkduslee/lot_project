import time
import requests
import board
import busio
from adafruit_htu21d import HTU21D

SERVER_URL = "http://localhost:5000/store/temphum"
SEND_INTERVAL = 5  # 데이터 전송 주기 (초)
i2c = busio.I2C(board.SCL, board.SDA)
sensor = HTU21D(i2c)


def getTemperature(sensor):
    return float(sensor.temperature)


def getHumidity(sensor):
    return float(sensor.relative_humidity)


while True:
    try:
        temp_val = getTemperature(sensor)
        hum_val = getHumidity(sensor)

        payload = {
            "temp": round(temp_val, 2),
            "hum": round(hum_val, 2)
        }

        response = requests.post(SERVER_URL, json=payload, timeout=3)

        if response.status_code != 200:
            print(f"전송 실패: 응답 코드 {response.status_code}")

    except requests.exceptions.RequestException as req_e:
        print("요청 오류")
    except Exception as e:
        print(f"기타 오류")

    time.sleep(SEND_INTERVAL)