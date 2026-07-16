{{ config(materialized='table') }}

select * from {{ ref('silver_vehicles') }}