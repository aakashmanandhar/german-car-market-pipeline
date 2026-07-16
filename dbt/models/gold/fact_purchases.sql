{{ config(materialized='table') }}

select
    purchase_id,
    customer_id,
    vehicle_id,
    store_id,
    financing_id,
    channel_id,
    purchase_date,
    price,
    mileage_at_purchase,
    new_or_used,
    discount_applied,
    trade_in_value,
    (price - discount_applied - trade_in_value) as net_price
from {{ ref('silver_purchases') }}