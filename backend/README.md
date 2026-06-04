## 실행하기

```bash
# backend 폴더 안으로 이동

# 최초 1회 가상환경 생성 및 설정 셋팅
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # 필요한 패키지 설치 (최초 1회)
cp .env.example .env  # 설정 파일 생성


# 서버 시작
python run.py
```

## 엔드포인트

| 메서드 | 경로 | 설명                   |
|---|---|----------------------|
| POST | `/store/live` | 주기적으로 좌석 상태 전송받는 곳   |
| POST | `/store/temphum` | 온습도 데이터 전송 받는 곳      |
| GET  | `/get/live` | 프론트용 온습도 + 좌석 상태 조회  |
| GET  | `/debug/frame` | 최신 프레임 이미지 확인        |
| WS   | `/ws/notify` | 프론트용 좌석 변동 정보 실시간 알림 |


## 각 엔드포인트별 요청/응답 형식

### 1. POST `/store/live`

카메라/센서에서 인식한 현재 좌석 상태를 서버로 전송한다.

**참고**

`true`는 해당 좌석이 사용 중임을 의미한다. 주기적으로 사용 중이라는 데이터를 보내지 않으면 `.env` 파일에서 설정된 시간(기본 10초) 이후에 자동으로 빈자리(반납) 처리되므로 주의가 필요하다.

**요청 (Request)**
```json
{
  "seatList": [
    [true, false, false, true],
    [true, false, true, false]
  ]
}
```

**응답 (Response)**

상태가 실제로 변경된 좌석의 좌표(x=행, y=열)와 변경된 상태 배열을 반환한다. 변경된 사항이 없으면 빈 배열을 반환한다.
```json
{
  "ok": true,
  "changes": [
    {
      "x": 0,
      "y": 1,
      "newStatus": true
    }
  ]
}
```

---

### 2. POST `/store/temphum`

측정된 온습도 데이터를 받아 저장한다

**요청 (Request)**
```json
{
  "temp": 12.3,
  "hum": 45.6
}
```

값은 숫자로 줘야한다

**응답 (Response)**
```json
{
  "ok": true
}
```

---

### 3. GET `/get/live`

현재 서버에 저장된 최신 온습도 정보와 전체 좌석의 실시간 상태를 조회한다.

프론트 측에선 이 요청은 페이지 로드시 최초 1회만 진행하고, 이후에는 웹소켓으로 수신하는 알림에 따라 변경점만 표시해주는게 나을듯 하다

**응답 (Response)**
```json
{
  "temp": 12.3,
  "hum": 45.6,
  "seatList": [
    [true, false, false, true],
    [true, false, true, false]
  ]
}

```

---

### 4. WS `/ws/notify` (웹소켓)
좌석 상태에 변동이 생기거나, 자동 반납 처리로 인해 빈자리가 발생했을 때 접속 중인 전체 클라이언트에게 서버가 실시간으로 알림을 전송한다.

**응답 (Response - 서버에서 클라이언트로 브로드캐스트)**
* `newStatus`가 `true`면 해당 좌석이 누군가 사용을 시작 했다는 것을, `false`면 사용 종료(또는 자동 반납) 했다는 것을 뜻한다.

**주의사항**
* 웹소켓의 응답은 서로 다른 형식의 두가지 응답을 반환할 수 있다. 하나는 좌석 정보와 관련된것, 하나는 센서값과 관련된것이다.
* 프론트는 웹소켓을 통해 도착한 응답이 어떤것인지 확인하기 위해 응답에 키 `latestSeat` 혹은 `latestSensor` 중 어떤것이 존재하는지 확인 후 따로 처리해줘야한다
```json
{
  "latestSeat": [
    {
      "x": 0,
      "y": 1,
      "newStatus": true
    },
    {
      "x": 1,
      "y": 2,
      "newStatus": false
    }
  ]
}
```

```json
{
  "latestSensor": {
    "temp": 12.3,
    "hum": 45.6
  }
}
```

---

### 5. GET `/debug/frame`
디버깅용으로, 서버의 `frames` 폴더에 저장된 가장 최근 프레임 이미지를 확인한다.

**응답 (Response)**
* 최신 프레임 파일이 단순 이미지로 응답된다