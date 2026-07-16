{{ config(materialized='table') }}

select * from {{ ref('silver_stores') }}