{{ config(materialized='table') }}

select
    _id as event_id,
    parse_date('%Y-%m-%d', event_date) as event_date,
    event_title,
    event_description
from {{ source('bronze_mongo', 'market_events') }}