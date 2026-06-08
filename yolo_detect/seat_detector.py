from ultralytics import YOLO
import cv2
import time
import requests
import os
import datetime

# =========================
# 설정
# =========================

#SERVER_URL = "http://semaphore.kro.kr:5000/store/live"
SERVER_URL = "http://127.0.0.1:5000/store/live"

OCCUPY_THRESHOLD_TIME = 3.0  # 점유 인식 대기 시간 (초)
TARGET_FPS = 5  # 카메라 fps
FRAME_INTERVAL = 1.0 / TARGET_FPS
model = YOLO("yolov8n.pt")
DISPLAY_SCALE = 0.8  # 디버깅 화면 스케일

# 서버의 frames 폴더 경로 지정 및 폴더 생성
FRAMES_SAVE_DIR = "/home/pi/lot_project/backend/frames"
os.makedirs(FRAMES_SAVE_DIR, exist_ok=True)

# 브라우저에 고정으로 서빙될 파일 경로
LATEST_FRAME_PATH = os.path.join(FRAMES_SAVE_DIR, "latest.png")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

seat_status = {
    "Seat1": "EMPTY",
    "Seat2": "EMPTY",
    "Seat3": "EMPTY",
    "Seat4": "EMPTY"
}

# 연속 탐지 시작 시간을 기록
occupy_start_time = {
    "Seat1": None,
    "Seat2": None,
    "Seat3": None,
    "Seat4": None
}

last_send_time = 0
last_process_time = 0

# =========================
# 메인 루프
# =========================

while True:

    ret, frame = cap.read()

    if not ret:
        print("카메라 읽기 실패")
        break

    now = time.time()

    if now - last_process_time < FRAME_INTERVAL:
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        continue

    last_process_time = now

    h, w = frame.shape[:2]

    # 화면 세로 4분할
    SEATS = {
        "Seat1": (0, 0, w // 4, h),
        "Seat2": (w // 4, 0, w // 2, h),
        "Seat3": (w // 2, 0, 3 * w // 4, h),
        "Seat4": (3 * w // 4, 0, w, h)
    }

    current_status = {
        "Seat1": "EMPTY",
        "Seat2": "EMPTY",
        "Seat3": "EMPTY",
        "Seat4": "EMPTY"
    }

    results = model(frame, verbose=False)

    annotated = frame.copy()

    # =========================
    # 사람 탐지
    # =========================

    for result in results:

        for box in result.boxes:

            cls = int(box.cls[0])

            # person 클래스만 사용
            if cls != 0:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            cv2.rectangle(
                annotated,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            cv2.circle(
                annotated,
                (center_x, center_y),
                5,
                (0, 0, 255),
                -1
            )

            for seat_name, (sx1, sy1, sx2, sy2) in SEATS.items():

                if sx1 <= center_x <= sx2 and sy1 <= center_y <= sy2:
                    current_status[seat_name] = "OCCUPIED"

    # =========================
    # 점유 상태 지연 업데이트 처리
    # =========================

    for seat_name in SEATS:

        if current_status[seat_name] == "OCCUPIED":

            # 처음 사람을 인식한 경우 시간 기록
            if occupy_start_time[seat_name] is None:
                occupy_start_time[seat_name] = time.time()

            # 지속 시간 계산
            occupy_duration = time.time() - occupy_start_time[seat_name]

            # 5초 이상 지속되었을 때만 실제 상태를 OCCUPIED로 변경
            if occupy_duration >= OCCUPY_THRESHOLD_TIME:
                seat_status[seat_name] = "OCCUPIED"

        else:
            # 사람이 인식되지 않으면 시작 시간 초기화 및 EMPTY 상태로 변경
            occupy_start_time[seat_name] = None
            seat_status[seat_name] = "EMPTY"

    # =========================
    # 서버 전송
    # 5초마다 전송
    # =========================

    now = time.time()

    if now - last_send_time >= 5:

        seat_list = [[
            seat_status["Seat1"] == "OCCUPIED",
            seat_status["Seat2"] == "OCCUPIED",
            seat_status["Seat3"] == "OCCUPIED",
            seat_status["Seat4"] == "OCCUPIED"
        ]]

        try:

            response = requests.post(
                SERVER_URL,
                json={"seatList": seat_list},
                timeout=3
            )

            print("전송 성공 :", seat_list)

        except Exception as e:

            print("전송 실패 :", e)

        last_send_time = now

    # =========================
    # 화면 표시 및 파일 이중 저장
    # =========================

    for seat_name, (sx1, sy1, sx2, sy2) in SEATS.items():
        cv2.rectangle(
            annotated,
            (sx1, sy1),
            (sx2, sy2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            annotated,
            f"{seat_name}: {seat_status[seat_name]}",
            (sx1 + 10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    # 날짜와 밀리초가 포함된 파일명 생성 (예: 20260608_131536_123.png)
    now_dt = datetime.datetime.now()
    timestamp_str = now_dt.strftime("%Y%m%d_%H%M%S_%f")[:19]
    history_filename = f"frame_{timestamp_str}.png"
    history_path = os.path.join(FRAMES_SAVE_DIR, history_filename)

    try:
        pass
        # 1. 기록 보관용 파일 저장
        cv2.imwrite(history_path, annotated)
        # 2. 웹 브라우저 제공용 덮어쓰기 저장
        cv2.imwrite(LATEST_FRAME_PATH, annotated)
    except Exception as e:
        print("프레임 파일 저장 실패:", e)

    display_w = int(w * DISPLAY_SCALE)
    display_h = int(h * DISPLAY_SCALE)
    resized_frame = cv2.resize(annotated, (display_w, display_h))
    cv2.imshow("Seat Detector", resized_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
