create or replace function public.fn_rollup_congestion_hourly()
returns trigger
language plpgsql
as $$
begin
  -- (location_id, date, hour) 버킷에 누적
  insert into public.congestion_hourly as h (
    location_id, date, hour,
    samples, sum_congestion, sum_people, updated_at
  )
  values (
    NEW.location_id, NEW.date, NEW.hour,
    1,
    coalesce(NEW.congestion, 0),
    coalesce(NEW.current_people, 0),
    now()
  )
  on conflict (location_id, date, hour)
  do update set
    samples        = h.samples + 1,
    sum_congestion = h.sum_congestion + coalesce(EXCLUDED.sum_congestion, 0),
    sum_people     = h.sum_people + coalesce(EXCLUDED.sum_people, 0),
    updated_at     = now();

  return NEW;
end;
$$;

drop trigger if exists trg_snapshot_to_hourly on public.congestion_snapshot;

create trigger trg_snapshot_to_hourly
after insert on public.congestion_snapshot
for each row
execute function public.fn_rollup_congestion_hourly();

insert into public.congestion_hourly (
  location_id, date, hour, samples, sum_congestion, sum_people, updated_at
)
select
  location_id,
  date,
  hour,
  count(*)                         as samples,
  sum(coalesce(congestion,0))      as sum_congestion,
  sum(coalesce(current_people,0))  as sum_people,
  now()                            as updated_at
from public.congestion_snapshot
group by location_id, date, hour
on conflict (location_id, date, hour) do nothing;

create or replace view public.v_hourly_avg_28d as
select
  location_id,
  hour,
  round( avg( (sum_congestion::numeric) / nullif(samples, 0)::numeric ), 3 ) as avg_congestion,
  round( avg( (sum_people::numeric)     / nullif(samples, 0)::numeric ), 1 ) as avg_people
from public.congestion_hourly
where date >= (current_date - interval '28 days')::date
group by location_id, hour
order by location_id, hour;
