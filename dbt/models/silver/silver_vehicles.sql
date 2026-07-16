{{ config(materialized='table') }}

select
    v.vehicle_id,
    v.model_year,
    v.fuel_type,
    v.engine_size_liters,
    v.transmission_type,
    v.emissions_class,
    m.model_name,
    m.body_type,
    m.segment,
    b.brand_name,
    b.country_of_origin as brand_country,
    b.brand_tier

from {{ source('bronze_api', 'vehicles') }} v
left join {{ source('bronze_api', 'models') }} m on v.model_id = m.model_id
left join {{ source('bronze_api', 'brands') }} b on m.brand_id = b.brand_id