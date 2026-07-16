{{ config(materialized='table') }}

select * from {{ ref('silver_sales_channels') }}