{{ config(materialized='table') }}

with date_spine as (
    select date_add(date '1990-01-01', interval n day) as full_date
    from unnest(generate_array(0, date_diff(date '2026-12-31', date '1990-01-01', day))) as n
)

select
    full_date,
    extract(year from full_date) as year,
    extract(quarter from full_date) as quarter,
    extract(month from full_date) as month,
    format_date('%B', full_date) as month_name,
    extract(dayofweek from full_date) as day_of_week,
    format_date('%A', full_date) as day_name,
    case when extract(dayofweek from full_date) in (1, 7) then true else false end as is_weekend
from date_spine