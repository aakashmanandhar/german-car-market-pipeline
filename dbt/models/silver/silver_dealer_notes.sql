{{ config(materialized='table') }}

select
    _id as note_id,
    purchase_id,
    note_text,
    staff_member,
    parse_date('%Y-%m-%d', note_date) as note_date
from {{ source('bronze_mongo', 'dealer_notes') }}