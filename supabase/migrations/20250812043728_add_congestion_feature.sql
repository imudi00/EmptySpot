
-- 1) 혼잡도 스냅샷 기록 함수
create or replace function public.fn_snapshot_congestion()
returns trigger
language plpgsql
security definer
as $$
declare
  v_capacity int;
  v_current  int;
  v_congestion float4;
  v_ts timestamp;
begin
  -- 스냅샷 시각: end_time 우선, 없으면 start_time, 그것도 없으면 now()
  v_ts := coalesce(NEW.end_time, NEW.start_time, now());

  -- 해당 장소의 좌석수
  select capacity into v_capacity
  from public.location
  where id = NEW.location_id;

  -- 방어: 좌석수가 없거나 0이면 스냅샷 생략
  if v_capacity is null or v_capacity = 0 then
    return NEW;
  end if;

  -- 현재 점유 좌석 수 (요구사항 그대로: occupied=1 인 행의 개수)
  -- ※ “현재 진행 중만” 세고 싶으면 AND (end_time is null OR end_time > v_ts) 조건 추가 가능
  select count(*) into v_current
  from public.seat_log
  where location_id = NEW.location_id
    and occupied = 1;

  v_congestion := least(1.0, v_current::float / v_capacity::float);

  insert into public.congestion_snapshot(
    location_id, current_people, congestion,
    date, hour, day_week, "timestamp"
  )
  values (
    NEW.location_id,
    v_current,
    v_congestion,
    v_ts::date,
    extract(hour from v_ts)::int,
    extract(isodow from v_ts)::int, -- 월=1 … 일=7
    v_ts
  );

  return NEW;
end;
$$;

-- 2) seat_log에 변경이 생길 때마다 스냅샷 남기기
drop trigger if exists trg_seat_log_snapshot on public.seat_log;

create trigger trg_seat_log_snapshot
after insert or update of occupied, start_time, end_time
on public.seat_log
for each row
execute function public.fn_snapshot_congestion();

-- 3) 각 location의 가장 최신 스냅샷
create or replace view public.latest_congestion as
select distinct on (cs.location_id)
  cs.location_id,
  cs.current_people,
  cs.congestion,
  cs.date,
  cs.hour,
  cs.day_week,
  cs."timestamp"
from public.congestion_snapshot cs
order by cs.location_id, cs."timestamp" desc;

-- 4) 장소 정보까지 합친 뷰 (API에서 바로 쓰기 좋게)
create or replace view public.v_location_congestion as
select
  l.id as location_id,
  l.name,
  l.building,
  l.campus,
  l.capacity,
  l.max_group,
  lc.current_people,
  lc.congestion,
  lc.date,
  lc.hour,
  lc.day_week,
  lc."timestamp"
from public.location l
left join public.latest_congestion lc
  on lc.location_id = l.id;

--인덱싱. 속도 높히기 위
create index if not exists idx_seat_log_loc_occ on public.seat_log (location_id, occupied); 
create index if not exists idx_congestion_snapshot_loc_ts on public.congestion_snapshot (location_id, "timestamp" desc);
