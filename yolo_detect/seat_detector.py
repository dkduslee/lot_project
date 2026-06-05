from ultralytics import YOLO
import cv2
import time
import requests

# =========================
# 설정
# =========================

SERVER_URL = "http://semaphore.kro.kr:5000/store/live"

AUTO_RETURN_TIME = 10  # 초
TARGET_FPS = 2  # 카메라 fps
FRAME_INTERVAL = 1.0 / TARGET_FPS
model = YOLO("yolov8n.pt")
DISPLAY_SCALE = 0.8  # 디버깅 화면 스케일

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

seat_status = {
    "Seat1": "EMPTY",
    "Seat2": "EMPTY",
    "Seat3": "EMPTY",
    "Seat4": "EMPTY"
}

empty_start_time = {
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
    # 자동 반납 처리
    # =========================

    for seat_name in SEATS:

        if current_status[seat_name] == "OCCUPIED":

            seat_status[seat_name] = "OCCUPIED"
            empty_start_time[seat_name] = None

        else:

            if empty_start_time[seat_name] is None:
                empty_start_time[seat_name] = time.time()

            empty_duration = time.time() - empty_start_time[seat_name]

            if empty_duration >= AUTO_RETURN_TIME:
                seat_status[seat_name] = "AUTO RETURN"
            else:
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
    # 화면 표시
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
    display_w = int(w * DISPLAY_SCALE)
    display_h = int(h * DISPLAY_SCALE)
    resized_frame = cv2.resize(annotated, (display_w, display_h))
    cv2.imshow("Seat Detector", resized_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
