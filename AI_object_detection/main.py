#실제 서비스 구동 시 사용하는 메인 코드
import time, threading, queue
from datetime import datetime
import torch, cv2, numpy as np
import json   

# ───────────── 설정 ─────────────
# DISPLAY_SIZE   = (640, 360)
DISPLAY_SIZE=(1280, 720)
INFER_INTERVAL = 1.0           # 1 초마다 추론
MODEL_INPUT    = 640           # YOLOv5 입력 해상도
ON_DELAY_SEC   = 10.0          # 10 초 연속 감지 → 점유 ON
OFF_DELAY_SEC  = 5.0           # 5 초 연속 미감지 → 점유 OFF
LOG_PATH       = "occupancy_log.csv"         # 세션별 착‧퇴석 기록/#필요시 사용
# SNAPSHOT_PATH  = "yolo_result.txt"           # 실시간 상태 + 전체 사람 수
SNAPSHOT_PATH  = "yolo_snapshot.json"

# “사람”으로 셀 클래스 이름 목록 
PERSON_CLASSES = {"person", "ChairFull", "StandingPerson", "WalkingPerson"}

# ────────── 모델 로드 ──────────
model = torch.hub.load(
    'C:/Users/User/Desktop/VisionProject/yolov5',
    'custom',
    path='4th.pt',
    source='local'
)
if torch.cuda.is_available():
    model.to('cuda').half()
model.eval()

# ──────── 카메라 스레드 ────────
rtsp_url = "rtsp://<(tapo카메라아이디>:<비밀번호>@<ip>/stream1"
cap = cv2.VideoCapture(rtsp_url)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

frame_q = queue.Queue(maxsize=1)
def reader():
    while True:
        ret, f = cap.read()
        if not ret:
            break
        if frame_q.full():
            try:
                frame_q.get_nowait()
            except queue.Empty:
                pass
        frame_q.put(f)
threading.Thread(target=reader, daemon=True).start()

# ────────── ROI 정의 ──────────
polygons = {
    # ───── Left 열 ─────
    "left_1": [(3, 645), (138, 660), (54, 795), (6, 774)],
    "left_2": [(111, 516), (231, 531), (153, 636), (30, 615)],
    "left_3": [(210, 393), (333, 408), (267, 495), (141, 495)],
    "left_4": [(285, 324), (405, 330), (342, 396), (225, 381)],
    "left_5": [(354, 264), (456, 270), (414, 318), (303, 309)],
    "left_6": [(414, 210), (504, 213), (465, 261), (372, 252)],
    "left_7": [(483, 165), (567, 171), (519, 207), (441, 201)],
    "left_8": [(510, 141), (594, 141), (573, 165), (489, 156)],
    "left_9": [(555, 108), (624, 120), (603, 135), (528, 126)],
    "left_10": [(591, 84), (648, 87), (633, 108), (573, 96)],

    # ───── Center-Left 열 ─────
    "center_left_1": [(726, 669), (948, 666), (936, 915), (684, 891)],
    "center_left_2": [(756, 549), (939, 549), (939, 645), (729, 651)],
    "center_left_3": [(777, 456), (933, 456), (936, 537), (762, 537)],
    "center_left_4": [(798, 387), (942, 384), (933, 441), (786, 444)],
    "center_left_5": [(816, 321), (948, 321), (939, 375), (807, 375)],
    "center_left_6": [(837, 255), (948, 261), (945, 309), (828, 309)],
    "center_left_7": [(855, 192), (954, 186), (951, 243), (843, 243)],

    # ───── Center-Right 열 ─────
    "center_right_1": [(963, 666), (1185, 669), (1236, 897), (975, 906)],
    "center_right_2": [(963, 558), (1158, 561), (1182, 648), (972, 651)],
    "center_right_3": [(963, 465), (1131, 471), (1158, 549), (969, 543)],
    "center_right_4": [(969, 390), (1119, 396), (1131, 450), (972, 447)],
    "center_right_5": [(972, 327), (1104, 336), (1116, 384), (975, 372)],
    "center_right_6": [(963, 258), (1089, 267), (1104, 321), (978, 318)],
    "center_right_7": [(975, 186), (1074, 189), (1086, 252), (966, 246)],

    # ───── Right 열 ─────
    "right_1": [(1833, 666), (1911, 654), (1917, 786), (1899, 789)],
    "right_2": [(1755, 555), (1851, 546), (1914, 630), (1824, 657)],
    "right_3": [(1629, 402), (1716, 408), (1779, 471), (1689, 471)],
    "right_4": [(1572, 342), (1659, 330), (1707, 384), (1614, 396)],
    "right_5": [(1500, 282), (1587, 273), (1629, 318), (1545, 327)],
    "right_6": [(1437, 225), (1527, 219), (1587, 261), (1479, 282)],
}

# ──── ROI별 상태(타이머 + 시각) ────
def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

states = {
    roi: {
        "occupied":   False,
        "accum_on":   0.0,
        "accum_off":  0.0,
        "last_ts":    time.time(),
        "first_hit":  None,   # 착석 최초 감지
        "last_seen":  None,   # 마지막 감지
        "start_time": None,   # 확정된 착석 시각
        "end_time":   None    # 확정된 이탈 시각
    } for roi in polygons
}

# ────────── 보조 함수 ──────────
def pick_roi_name(cx, cy, cls_name):
    if cls_name == "ChairFull":                 # 사람(착석) 클래스
        best, dmin = None, float('inf')
        for name, pts in polygons.items():
            for px, py in pts:
                d = (cx - px) ** 2 + (cy - py) ** 2
                if d < dmin:
                    best, dmin = name, d
        return best
    else:                                       # 사물
        for name, pts in polygons.items():
            if cv2.pointPolygonTest(np.array(pts, np.int32),
                                    (int(cx), int(cy)), False) >= 0:
                return name
    return None

def annotate(frame, results):
    img = frame.copy()
    for name, pts in polygons.items():
        color = (0, 0, 255) if states[name]["occupied"] else (0, 255, 0)
        cv2.polylines(img, [np.array(pts, np.int32)], True, color, 2)
    for *box, _, cls in results.xyxy[0]:
        x1, y1, x2, y2 = map(int, box)
        cls_name = model.names[int(cls)] if hasattr(model, "names") else model.module.names[int(cls)]
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(img, cls_name, (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    return img

# ─────────── 메인 루프 ───────────
last_infer_t = time.time() - INFER_INTERVAL
last_annot   = None

with torch.no_grad():
    while True:
        # ① 프레임 받기
        try:
            frame = frame_q.get(timeout=1)
        except queue.Empty:
            print("⚠️  캡처 실패"); break

        # ② 추론 (1 초 간격)
        if time.time() - last_infer_t >= INFER_INTERVAL:
            results = model(frame, size=MODEL_INPUT)
            now = time.time()

            # ―― 이번 프레임에서 감지된 ROI / 사람 수 ――
            hits = set()
            people_count = 0

            for *box, conf, cls in results.xyxy[0]:
                x1, y1, x2, y2 = map(int, box)
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                cls_name = model.names[int(cls)] if hasattr(model, "names") else model.module.names[int(cls)]

                # 전체 사람 수 카운트
                if cls_name in PERSON_CLASSES:
                    people_count += 1

                # ROI 매핑(착석만)
                roi = pick_roi_name(cx, cy, cls_name)
                if roi:
                    hits.add(roi)

            # ③ 타이머·시각 업데이트
            for name, st in states.items():
                elapsed = now - st["last_ts"]

                if name in hits:                      # 감지 O
                    if st["accum_on"] == 0:           # 처음 들어온 프레임
                        st["first_hit"] = now_str()
                    st["accum_on"]  += elapsed
                    st["accum_off"]  = 0.0
                    st["last_seen"]  = now_str()
                else:                                 # 감지 X
                    if st["accum_off"] == 0:
                        st["last_seen"] = now_str()   # 마지막 보인 시각
                    st["accum_off"] += elapsed
                    st["accum_on"]   = 0.0
                st["last_ts"] = now

                # ④ 상태 전환
                if (not st["occupied"]) and (st["accum_on"] >= ON_DELAY_SEC):
                    st["occupied"]   = True
                    st["start_time"] = st["first_hit"]  # 실제 착석 시각
                    st["end_time"]   = None
                elif st["occupied"] and (st["accum_off"] >= OFF_DELAY_SEC):
                    st["occupied"] = False
                    st["end_time"]  = st["last_seen"]   # 실제 이탈 시각

                    # ▶︎ 파일에 세션 기록 (append)
                    with open(LOG_PATH, "a", encoding="utf-8") as log:
                        log.write(f"{name},{st['start_time']},{st['end_time']}\n")

            # ⑤ 스냅샷 저장(JSON, 덮어쓰기)
            snapshot = {
                k: [
                    "1" if st["occupied"] else "0",
                    st["start_time"] or "",
                    st["end_time"]   or ""
                ] for k, st in states.items()
            }
            snapshot["_people_count"] = str(people_count)   # ← 추가 필드
            with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, ensure_ascii=False)

            last_annot   = annotate(frame, results)
            last_infer_t = now

        # ⑥ 화면 표시
        show = last_annot if last_annot is not None else frame
        cv2.imshow("YOLOv5 Occupancy Demo", cv2.resize(show, DISPLAY_SIZE))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
