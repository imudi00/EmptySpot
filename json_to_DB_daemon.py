#메인 코드를 통해 변화되는 JSON파일을 DB로 전송하는 코드
import os, json, argparse, time, hashlib
from datetime import datetime
from supabase import create_client
from postgrest.exceptions import APIError

# ---------- 설정 가능한 기본값 ----------
DEFAULT_POLL_SEC = 1.0
DEFAULT_SETTLE_SEC = 0.05

# ---------- 유틸 ----------
def load_snapshot(path: str) -> dict[str, dict]:
    """yolo_result.txt(JSON)을 읽어 좌석 딕셔너리로 변환"""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    seats: dict[str, dict] = {}
    for seat_id, vals in raw.items():
        if seat_id.startswith("_"):
            continue  # _people_count 같은 메타는 무시
        occ_str, start_str, end_str = vals
        seats[seat_id] = {
            "occupied": (occ_str == "1" or occ_str is True),
            "start": (start_str or None),  # DB가 timestamp(타임존 없음)라면 KST 문자열 그대로 보냄
            "end":   (end_str or None),
        }
    return seats

def connect_supabase(url_arg: str | None, key_arg: str | None, verbose=True):
    url = (url_arg or os.getenv("SUPABASE_URL") or "").strip().rstrip("/")
    key = (key_arg or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
    if not url or not key:
        raise SystemExit(
            "[ERR] SUPABASE_URL 또는 SUPABASE_SERVICE_ROLE_KEY 가 비어 있습니다.\n"
            "  - PowerShell(현재 세션):\n"
            '      $env:SUPABASE_URL="https://<your>.supabase.co"\n'
            '      $env:SUPABASE_SERVICE_ROLE_KEY="<eyJ...>"\n'
            "  - 또는 실행 인자로 --url 과 --key 를 넘겨주세요."
        )
    if verbose:
        masked = (key[:6] + "..." + key[-4:]) if len(key) > 12 else "***"
        print(f"[INFO] SUPABASE_URL = {url}")
        print(f"[INFO] SERVICE_ROLE_KEY = {masked}")
    return create_client(url, key)

def _update_with_bool_or_int(sb, table: str, location_id: int, seat_id: str, payload: dict, occupied_key="occupied"):
    """occupied가 boolean이라 실패하면 smallint(1/0)로 폴백하여 UPDATE"""
    try:
        sb.table(table).update(payload).eq("location_id", location_id).eq("seat_id", seat_id).execute()
    except APIError as e:
        msg = str(e)
        if "smallint" in msg or '22P02' in msg:
            p2 = dict(payload)
            if occupied_key in p2 and isinstance(p2[occupied_key], bool):
                p2[occupied_key] = 1 if p2[occupied_key] else 0
            sb.table(table).update(p2).eq("location_id", location_id).eq("seat_id", seat_id).execute()
        else:
            raise

# ---------- 메인 루프 ----------
def daemon_loop(snapshot_path: str, table: str, location_id: int, sb, poll: float, settle: float, verbose=True):
    last_occ: dict[str, bool] = {}         # 마지막으로 보낸 occupied
    last_end_sent: dict[str, str | None] = {}  # 마지막으로 보낸 end시간(중복 방지)

    last_mtime: float | None = None
    last_hash: str | None = None

    print(f"[RUN] Watching: {snapshot_path} (poll={poll}s)")

    while True:
        try:
            if not os.path.exists(snapshot_path):
                time.sleep(poll)
                continue

            mtime = os.path.getmtime(snapshot_path)
            if last_mtime is not None and mtime == last_mtime:
                time.sleep(poll)
                continue

            time.sleep(settle)  # 파일 쓰기 안정화 대기

            with open(snapshot_path, "rb") as f:
                data_bytes = f.read()
            cur_hash = hashlib.sha256(data_bytes).hexdigest()
            if cur_hash == last_hash:
                last_mtime = mtime
                time.sleep(poll)
                continue

            snapshot = json.loads(data_bytes.decode("utf-8"))
            seats = {}
            for sid, vals in snapshot.items():
                if sid.startswith("_"):
                    continue
                occ, s, e = vals
                seats[sid] = {
                    "occupied": (occ == "1" or occ is True),
                    "start": (s or None),
                    "end":   (e or None),
                }

            # 1) occupied 변화 즉시 UPDATE
            for sid, v in seats.items():
                new_occ = bool(v["occupied"])
                prev_occ = last_occ.get(sid)
                if prev_occ is None or prev_occ != new_occ:
                    if verbose: print(f"[UPDATE] {sid}: occupied {prev_occ} -> {new_occ}")
                    _update_with_bool_or_int(sb, table, location_id, sid, {"occupied": new_occ})
                    last_occ[sid] = new_occ

            # 2) end가 생긴 좌석은 start/end를 한 번에 UPDATE (OFF 확정)
            for sid, v in seats.items():
                end_str = v["end"]
                if not end_str:
                    continue
                if last_end_sent.get(sid) == end_str:
                    continue  # 같은 종료시각 재전송 방지

                payload = {
                    "occupied": False,        # OFF 확정
                    "start_time": v["start"], # DB가 timestamp면 그대로(타임존 없음)
                    "end_time":   v["end"],
                }
                if verbose:
                    print(f"[UPDATE] {sid}: start_time={payload['start_time']}, end_time={payload['end_time']}")
                _update_with_bool_or_int(sb, table, location_id, sid, payload)

                last_end_sent[sid] = end_str
                last_occ[sid] = False

            last_mtime = mtime
            last_hash = cur_hash
            time.sleep(poll)

        except KeyboardInterrupt:
            print("\n[STOP] Ctrl+C")
            break
        except Exception as e:
            print(f"[WARN] loop error: {e}")
            time.sleep(max(poll, 2.0))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", default="yolo_snapshot.json", help="스냅샷 JSON 파일 경로 (기본: yolo_snapshot.json)")
    ap.add_argument("-t", "--table", default="seat_log", help="Supabase 테이블명 (기본: seat_log)")
    ap.add_argument("--location-id", type=int, default=1, help="seat_log.location_id 값 (기본: 1)")
    ap.add_argument("--url", help="(옵션) SUPABASE_URL 인자")
    ap.add_argument("--key", help="(옵션) SUPABASE_SERVICE_ROLE_KEY 인자")
    ap.add_argument("--poll", type=float, default=DEFAULT_POLL_SEC, help=f"파일 폴링 주기 초 (기본: {DEFAULT_POLL_SEC})")
    ap.add_argument("--settle", type=float, default=DEFAULT_SETTLE_SEC, help=f"파일 쓰기 안정화 대기 초 (기본: {DEFAULT_SETTLE_SEC})")
    ap.add_argument("--quiet", action="store_true", help="로그 최소화")
    args = ap.parse_args()

    sb = connect_supabase(args.url, args.key, verbose=(not args.quiet))
    daemon_loop(args.file, args.table, args.location_id, sb, poll=args.poll, settle=args.settle, verbose=(not args.quiet))

if __name__ == "__main__":
    main()
