{{ config(materialized='table') }}

with deduped as (
    select
        *,
        row_number() over (
            partition by customer_id, vehicle_id, purchase_date, price
            order by purchase_id
        ) as row_num
    from {{ source('bronze_postgres', 'purchases') }}
),

cleaned as (
    select
        purchase_id,
        customer_id,
        vehicle_id,
        store_id,
        financing_id,
        channel_id,
        purchase_date,

        -- Fix the deliberate decimal-shift price typo: if price looks
        -- suspiciously low for a car (under 1000), assume it's off by a
        -- factor of 10 and correct it.
        case
            when price < 1000 then price * 10
            else price
        end as price,

        mileage_at_purchase,
        new_or_used,

        -- Deliberate messiness: a small number of discounts came in negative,
        -- which is a real-world data-entry error, not a valid business case.
        case
            when discount_applied < 0 then 0
            else discount_applied
        end as discount_applied,

        trade_in_value

    from deduped
    where row_num = 1  -- drops the deliberate duplicate transactions
)

select * from cleaned