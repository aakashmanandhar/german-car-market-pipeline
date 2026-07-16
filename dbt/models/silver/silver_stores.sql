{{ config(materialized='table') }}

select
    s.store_id,
    s.store_name,
    s.region_id,
    r.region_name,
    s.city,
    s.store_type
from {{ source('bronze_postgres', 'stores') }} s
left join {{ source('bronze_postgres', 'regions') }} r on s.region_id = r.region_id