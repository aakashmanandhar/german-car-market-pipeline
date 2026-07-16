{{ config(materialized='table') }}

select
    _id as review_id,
    purchase_id,
    review_text,
    rating,
    parse_date('%Y-%m-%d', review_date) as review_date
from {{ source('bronze_mongo', 'customer_reviews') }}