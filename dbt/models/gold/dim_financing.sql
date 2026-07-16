{{ config(materialized='table') }}

select * from {{ ref('silver_financing_types') }}