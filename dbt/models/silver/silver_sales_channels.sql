{{ config(materialized='table') }}

select channel_id, channel_name
from {{ source('bronze_postgres', 'sales_channels') }}