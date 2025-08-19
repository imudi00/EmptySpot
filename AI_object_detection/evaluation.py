#녹화된 영상을 이용하여 테스트/평가 하는 코드
import time, threading, queue
from datetime import datetime, timedelta
import torch, cv2, numpy as np
import json
from typing import Optional, Tuple, Set, Dict, List

# ───────────────── 설정 ─────────────────
DISPLAY_SIZE = (1280, 720)     # 보기용 리사이즈(좌표계와 무관)
INFER_INTERVAL = 1.0           # 추론 주기(초). 매 프레임 추론하려면 0.0
MODEL_INPUT = 640              # YOLOv5 입력 해상도

ON_DELAY_SEC  = 10.0           # 연속 감지 → 점유 ON
OFF_DELAY_SEC = 5.0            # 연속 미감지 → 점유 OFF

LOG_PATH      = "occupancy_log.csv"     # 세션(착석~이탈) 기록
SNAPSHOT_PATH = "yolo_snapshot.json"    # 현재 스냅샷 + 전체 사람 수

PERSON_CLASSES = {"person", "ChairFull", "StandingPerson", "WalkingPerson"}

# 입력 소스 선택
SOURCE     = "file"  # "file" 또는 "rtsp"
VIDEO_FILE = r"testvideo.mp4"
RTSP_URL   = "rtsp://<아이디>:<비밀번호>@<ip>/stream1"

SHOW_WINDOW = True

# ROI를 처음 찍었던 '기준' 프레임 크기 (가로, 세로)
ROI_BASE_SIZE = (1920, 1080)  # ← 원래 ROI 좌표를 찍던 해상도로

# 회전 옵션
MANUAL_ROTATE_DEG = 0                 # 0/90/180/270 (0이면 자동 규칙 적용 가능)
AUTO_ROTATE_TO_LANDSCAPE = True       # 세로 영상이면 90도 회전

# 내부 전역(실행 중 결정)
ACTIVE_POLYGONS: Optional[Dict[str, List[Tuple[int,int]]]] = None
FRAME_ROTATE_DEG = 0                  # 실제 적용된 회전 각도(초기 0)

# ───────────────── 모델 로드 ─────────────────
model = torch.hub.load(
    'C:/Users/User/Desktop/AI_object_detection/yolov5',  # ← 환경에 맞춰 경로/weights 수정
    'custom',
    path='4th.pt', #pt 파일 설정
    source='local'
)
if torch.cuda.is_available():
    model.to('cuda').half()
model.eval()

# ────────── ROI 정의 ────────── #extract_roi.py 파일을 통해 환경에 맞게 ROI추출
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
    # "center_right_6": [(963, 258), (1089, 267), (1104, 321), (978, 318)],
    # "center_right_7": [(975, 186), (1074, 189), (1086, 252), (966, 246)],
    "center_right_6": [(972, 237), (1077, 237), (1095, 291), (981, 294)],
    "center_right_7": [(966, 177), (1059, 177), (1071, 219), (975, 222)],

    # ───── Right 열 ─────
    "right_1": [(1833, 666), (1911, 654), (1917, 786), (1899, 789)],
    "right_2": [(1755, 555), (1851, 546), (1914, 630), (1824, 657)],
    "right_3": [(1629, 402), (1716, 408), (1779, 471), (1689, 471)],
    "right_4": [(1572, 342), (1659, 330), (1707, 384), (1614, 396)],
    "right_5": [(1500, 282), (1587, 273), (1629, 318), (1545, 327)],
    "right_6": [(1437, 225), (1527, 219), (1587, 261), (1479, 282)],
}

# ───────────────── 상태 구조 ─────────────────
def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

run_anchor = datetime.now()  # 파일 모드용: 실행 시작 시각을 기준으로 가짜 실제 시각 생성
def ts_from_video(t_sec: float) -> str:
    return (run_anchor + timedelta(seconds=float(t_sec))).strftime("%Y-%m-%d %H:%M:%S")

states = {
    roi: {
        "occupied":   False,
        "accum_on":   0.0,
        "accum_off":  0.0,
        "last_ts":    time.time(),  # RTSP 경과시간 계산용
        "first_hit":  None,         # 최초 감지 시각(문자열)
        "last_seen":  None,         # 마지막 감지 시각(문자열)
        "start_time": None,         # 확정된 착석 시각(문자열)
        "end_time":   None          # 확정된 이탈 시각(문자열)
    } for roi in polygons
}

# ───────────────── 유틸 ─────────────────
def rotate_frame(frame: np.ndarray, deg: int) -> np.ndarray:
    if deg == 90:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif deg == 180:
        return cv2.rotate(frame, cv2.ROTATE_180)
    elif deg == 270:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return frame

def decide_rotation_and_scale_once(frame: np.ndarray):
    """
    첫 프레임에서 1) 회전 각 결정 2) 회전 적용 3) ROI 스케일 산출을 한 번만 수행
    """
    global FRAME_ROTATE_DEG, ACTIVE_POLYGONS
    # 1) 회전 각도 결정
    if MANUAL_ROTATE_DEG in (90, 180, 270):
        FRAME_ROTATE_DEG = MANUAL_ROTATE_DEG
    else:
        # 자동: 세로 -> 가로로
        h, w = frame.shape[:2]
        FRAME_ROTATE_DEG = 90 if (AUTO_ROTATE_TO_LANDSCAPE and h > w) else 0

    # 2) 회전 적용
    rotated = rotate_frame(frame, FRAME_ROTATE_DEG)

    # 3) ROI 스케일 계산
    fh, fw = rotated.shape[:2]
    bw, bh = ROI_BASE_SIZE
    sx = fw / float(bw)
    sy = fh / float(bh)
    ACTIVE_POLYGONS = {
        name: [(int(round(x * sx)), int(round(y * sy))) for (x, y) in pts]
        for name, pts in polygons.items()
    }
    print(f"[INFO] first frame after-rotation size = {fw}x{fh}, "
          f"rotation={FRAME_ROTATE_DEG}deg, scale sx={sx:.4f}, sy={sy:.4f}")
    return rotated

def current_polygons():
    return ACTIVE_POLYGONS if ACTIVE_POLYGONS is not None else polygons

def pick_roi_name(cx: float, cy: float, cls_name: str) -> Optional[str]:
    polys = current_polygons()
    if cls_name == "ChairFull":
        best, dmin = None, float('inf')
        for name, pts in polys.items():
            for px, py in pts:
                d = (cx - px) ** 2 + (cy - py) ** 2
                if d < dmin:
                    best, dmin = name, d
        return best
    else:
        for name, pts in polys.items():
            if cv2.pointPolygonTest(np.array(pts, np.int32),
                                    (int(cx), int(cy)), False) >= 0:
                return name
    return None

def annotate(frame: np.ndarray, results) -> np.ndarray:
    img = frame.copy()
    for name, pts in current_polygons().items():
        color = (0, 0, 255) if states[name]["occupied"] else (0, 255, 0)
        cv2.polylines(img, [np.array(pts, np.int32)], True, color, 2)
    for *box, _, cls in results.xyxy[0]:
        x1, y1, x2, y2 = map(int, box)
        cls_name = model.names[int(cls)] if hasattr(model, "names") else model.module.names[int(cls)]
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(img, cls_name, (x1, max(0, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    return img

def read_frame_and_dt(cap: cv2.VideoCapture, fps: float, prev_pos_msec: Optional[float]) -> Tuple[Optional[np.ndarray], Optional[float], Optional[float]]:
    ret, frame = cap.read()
    if not ret:
        return None, None, None
    cur_pos_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
    if cur_pos_msec and prev_pos_msec is not None and cur_pos_msec > 0:
        dt = max(0.0, (cur_pos_msec - prev_pos_msec) / 1000.0)
    elif fps and fps > 0:
        dt = 1.0 / float(fps)
    else:
        dt = 1.0 / 30.0
    return frame, dt, cur_pos_msec

def update_states_with_hits(hits: Set[str], dt: float, video_clock_sec: float):
    now_ts_str = ts_from_video(video_clock_sec)
    for name, st in states.items():
        if name in hits:
            if st["accum_on"] == 0:
                st["first_hit"] = now_ts_str
            st["accum_on"]  += dt
            st["accum_off"]  = 0.0
            st["last_seen"]  = now_ts_str
        else:
            if st["accum_off"] == 0:
                st["last_seen"] = now_ts_str
            st["accum_off"] += dt
            st["accum_on"]   = 0.0

        if (not st["occupied"]) and (st["accum_on"] >= ON_DELAY_SEC):
            st["occupied"]   = True
            st["start_time"] = st["first_hit"]
            st["end_time"]   = None
        elif st["occupied"] and (st["accum_off"] >= OFF_DELAY_SEC):
            st["occupied"] = False
            st["end_time"]  = st["last_seen"]
            with open(LOG_PATH, "a", encoding="utf-8") as log:
                log.write(f"{name},{st['start_time']},{st['end_time']}\n")

def write_snapshot(people_count: int):
    snapshot = {
        k: [
            "1" if st["occupied"] else "0",
            st["start_time"] or "",
            st["end_time"]   or ""
        ] for k, st in states.items()
    }
    snapshot["_people_count"] = str(people_count)
    with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False)

def flush_open_sessions_on_end():
    for name, st in states.items():
        if st["occupied"]:
            st["occupied"] = False
            if not st["end_time"]:
                st["end_time"] = st["last_seen"] or now_str()
            with open(LOG_PATH, "a", encoding="utf-8") as log:
                log.write(f"{name},{st['start_time']},{st['end_time']}\n")

# ───────────────── 실행(라이브) ─────────────────
def run_rtsp():
    cap = cv2.VideoCapture(RTSP_URL)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    frame_q: "queue.Queue[np.ndarray]" = queue.Queue(maxsize=1)

    def reader():
        while True:
            ret, f = cap.read()
            if not ret:
                break
            if frame_q.full():
                try: frame_q.get_nowait()
                except queue.Empty: pass
            frame_q.put(f)

    threading.Thread(target=reader, daemon=True).start()

    last_infer_t = time.time() - INFER_INTERVAL
    last_annot   = None
    did_init = False

    with torch.no_grad():
        while True:
            try:
                frame = frame_q.get(timeout=1)
            except queue.Empty:
                print("⚠️  캡처 실패")
                break

            # 첫 프레임에서 회전/스케일 1회 결정
            if not did_init:
                frame = decide_rotation_and_scale_once(frame)
                did_init = True
            else:
                frame = rotate_frame(frame, FRAME_ROTATE_DEG)

            now_t = time.time()
            if INFER_INTERVAL == 0.0 or (now_t - last_infer_t >= INFER_INTERVAL):
                results = model(frame, size=MODEL_INPUT)
                hits: Set[str] = set()
                people_count = 0

                for *box, conf, cls in results.xyxy[0]:
                    x1, y1, x2, y2 = map(int, box)
                    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                    cls_name = model.names[int(cls)] if hasattr(model, "names") else model.module.names[int(cls)]
                    if cls_name in PERSON_CLASSES:
                        people_count += 1
                    roi = pick_roi_name(cx, cy, cls_name)
                    if roi: hits.add(roi)

                # 경과시간 기반 상태 갱신
                for name, st in states.items():
                    elapsed = now_t - st["last_ts"]
                    if name in hits:
                        if st["accum_on"] == 0:
                            st["first_hit"] = now_str()
                        st["accum_on"] += elapsed
                        st["accum_off"] = 0.0
                        st["last_seen"] = now_str()
                    else:
                        if st["accum_off"] == 0:
                            st["last_seen"] = now_str()
                        st["accum_off"] += elapsed
                        st["accum_on"] = 0.0
                    st["last_ts"] = now_t

                    if (not st["occupied"]) and (st["accum_on"] >= ON_DELAY_SEC):
                        st["occupied"] = True
                        st["start_time"] = st["first_hit"]
                        st["end_time"]   = None
                    elif st["occupied"] and (st["accum_off"] >= OFF_DELAY_SEC):
                        st["occupied"] = False
                        st["end_time"]  = st["last_seen"]
                        with open(LOG_PATH, "a", encoding="utf-8") as log:
                            log.write(f"{name},{st['start_time']},{st['end_time']}\n")

                write_snapshot(people_count)
                last_annot   = annotate(frame, results)
                last_infer_t = now_t

            if SHOW_WINDOW:
                show = last_annot if last_annot is not None else frame
                cv2.imshow("YOLOv5 Occupancy (RTSP)", cv2.resize(show, DISPLAY_SIZE))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    cap.release()
    if SHOW_WINDOW:
        cv2.destroyAllWindows()
    flush_open_sessions_on_end()

# ───────────────── 실행(파일) ─────────────────
def run_file():
    cap = cv2.VideoCapture(VIDEO_FILE)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video file: {VIDEO_FILE}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    pos_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
    video_clock = 0.0
    since_last_infer = 0.0  # 0.0이면 첫 프레임에서 바로 추론
    last_annot = None
    did_init = False

    with torch.no_grad():
        while True:
            frame, dt, pos_msec = read_frame_and_dt(cap, fps, pos_msec)
            if frame is None:
                break  # EOF

            if not did_init:
                frame = decide_rotation_and_scale_once(frame)
                did_init = True
            else:
                frame = rotate_frame(frame, FRAME_ROTATE_DEG)

            # 비디오 시계 진행
            dt = dt or (1.0 / fps if fps > 0 else 1.0 / 30.0)
            video_clock += dt
            since_last_infer += dt

            if INFER_INTERVAL == 0.0 or (since_last_infer >= INFER_INTERVAL):
                results = model(frame, size=MODEL_INPUT)
                hits: Set[str] = set()
                people_count = 0

                for *box, conf, cls in results.xyxy[0]:
                    x1, y1, x2, y2 = map(int, box)
                    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                    cls_name = model.names[int(cls)] if hasattr(model, "names") else model.module.names[int(cls)]
                    if cls_name in PERSON_CLASSES:
                        people_count += 1
                    roi = pick_roi_name(cx, cy, cls_name)
                    if roi: hits.add(roi)

                # dt(누적 간격)로 상태 갱신
                update_states_with_hits(hits, dt=since_last_infer, video_clock_sec=video_clock)
                write_snapshot(people_count)
                last_annot = annotate(frame, results)

                since_last_infer = 0.0

            if SHOW_WINDOW:
                show = last_annot if last_annot is not None else frame
                cv2.imshow("YOLOv5 Occupancy (File)", cv2.resize(show, DISPLAY_SIZE))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    cap.release()
    if SHOW_WINDOW:
        cv2.destroyAllWindows()
    flush_open_sessions_on_end()

# ───────────────── 엔트리 ─────────────────
if __name__ == "__main__":
    if SOURCE.lower() == "rtsp":
        print("[INFO] Running in RTSP (live) mode.")
        run_rtsp()
    else:
        print("[INFO] Running in FILE (offline evaluation) mode.")
        run_file()
