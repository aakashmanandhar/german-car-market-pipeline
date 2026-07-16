{{ config(materialized='table') }}

select region_id, region_name, country
from {{ source('bronze_postgres', 'regions') }}