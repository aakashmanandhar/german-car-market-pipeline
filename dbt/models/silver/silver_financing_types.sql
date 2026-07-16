{{ config(materialized='table') }}

select financing_id, type_name
from {{ source('bronze_postgres', 'financing_types') }}