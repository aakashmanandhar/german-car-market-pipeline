from rest_framework.decorators import api_view
from rest_framework.response import Response
from .bigquery_client import get_bigquery_client

PROJECT_ID = "german-car-pipeline"


def region_filter_clause(request):
    """Returns a SQL WHERE clause fragment filtering by region, if one was requested."""
    region = request.GET.get('region')
    if region:
        # Basic escaping — safe here since region names come from a fixed,
        # known dropdown list, not free-text user input.
        safe_region = region.replace("'", "")
        return f"WHERE s.region_name = '{safe_region}'"
    return ""


@api_view(['GET'])
def brand_market_share(request):
    client = get_bigquery_client()
    where_clause = region_filter_clause(request)
    query = f"""
        SELECT
            v.brand_name,
            EXTRACT(YEAR FROM f.purchase_date) AS year,
            COUNT(*) AS purchase_count
        FROM `{PROJECT_ID}.gold_dev.fact_purchases` f
        JOIN `{PROJECT_ID}.gold_dev.dim_vehicle` v ON f.vehicle_id = v.vehicle_id
        JOIN `{PROJECT_ID}.gold_dev.dim_store` s ON f.store_id = s.store_id
        {where_clause}
        GROUP BY brand_name, year
        ORDER BY year, brand_name
    """
    results = client.query(query).result()
    return Response([dict(row) for row in results])


@api_view(['GET'])
def kpi_summary(request):
    client = get_bigquery_client()
    where_clause = region_filter_clause(request)
    query = f"""
        SELECT
            ROUND(SUM(f.price), 2) AS total_revenue,
            ROUND(AVG(f.net_price), 2) AS avg_net_price,
            COUNT(*) AS total_purchases,
            ROUND(
                COUNTIF(v.fuel_type IN ('electric', 'hybrid')) / COUNT(*) * 100, 1
            ) AS ev_hybrid_share_pct
        FROM `{PROJECT_ID}.gold_dev.fact_purchases` f
        JOIN `{PROJECT_ID}.gold_dev.dim_vehicle` v ON f.vehicle_id = v.vehicle_id
        JOIN `{PROJECT_ID}.gold_dev.dim_store` s ON f.store_id = s.store_id
        {where_clause}
    """
    results = client.query(query).result()
    data = [dict(row) for row in results]
    return Response(data[0])


@api_view(['GET'])
def revenue_by_region(request):
    client = get_bigquery_client()
    query = f"""
        SELECT
            s.region_name,
            ROUND(SUM(f.net_price), 2) AS total_revenue,
            COUNT(*) AS purchase_count
        FROM `{PROJECT_ID}.gold_dev.fact_purchases` f
        JOIN `{PROJECT_ID}.gold_dev.dim_store` s ON f.store_id = s.store_id
        GROUP BY region_name
        ORDER BY total_revenue DESC
    """
    results = client.query(query).result()
    return Response([dict(row) for row in results])


@api_view(['GET'])
def revenue_by_financing(request):
    client = get_bigquery_client()
    where_clause = region_filter_clause(request)
    query = f"""
        SELECT
            fin.type_name,
            ROUND(SUM(f.net_price), 2) AS total_revenue,
            COUNT(*) AS purchase_count
        FROM `{PROJECT_ID}.gold_dev.fact_purchases` f
        JOIN `{PROJECT_ID}.gold_dev.dim_financing` fin ON f.financing_id = fin.financing_id
        JOIN `{PROJECT_ID}.gold_dev.dim_store` s ON f.store_id = s.store_id
        {where_clause}
        GROUP BY type_name
        ORDER BY total_revenue DESC
    """
    results = client.query(query).result()
    return Response([dict(row) for row in results])


@api_view(['GET'])
def channel_shift(request):
    client = get_bigquery_client()
    where_clause = region_filter_clause(request)
    query = f"""
        SELECT
            CASE WHEN EXTRACT(YEAR FROM f.purchase_date) < 2015 THEN 'Before 2015' ELSE '2015+' END AS period,
            c.channel_name,
            COUNT(*) AS purchase_count
        FROM `{PROJECT_ID}.gold_dev.fact_purchases` f
        JOIN `{PROJECT_ID}.gold_dev.dim_channel` c ON f.channel_id = c.channel_id
        JOIN `{PROJECT_ID}.gold_dev.dim_store` s ON f.store_id = s.store_id
        {where_clause}
        GROUP BY period, channel_name
        ORDER BY period, channel_name
    """
    results = client.query(query).result()
    return Response([dict(row) for row in results])