{{ config(materialized='table') }}

select
    c.customer_id,
    c.first_name,
    c.last_name,
    c.birth_date,
    c.gender,
    c.occupation,
    c.income_bracket,
    c.marital_status,
    c.city,
    r.region_name
from {{ ref('silver_customers') }} c
left join {{ ref('silver_regions') }} r on c.region_id = r.region_id