{{ config(materialized='table') }}

select
    customer_id,
    first_name,
    last_name,
    birth_date,
    gender,
    coalesce(occupation, 'Unknown') as occupation,
    coalesce(income_bracket, 'Unknown') as income_bracket,
    marital_status,
    region_id,

    case
        when city in ('Munich', 'München', 'Muenchen') then 'Munich'
        when city in ('Cologne', 'Köln', 'Koeln') then 'Cologne'
        when city in ('Nuremberg', 'Nürnberg', 'Nuernberg') then 'Nuremberg'
        else city
    end as city

from {{ source('bronze_postgres', 'customers') }}