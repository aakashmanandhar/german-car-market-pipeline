from rest_framework.decorators import api_view
from rest_framework.response import Response
from .bigquery_client import get_bigquery_client

PROJECT_ID = "german-car-pipeline"


@api_view(['GET'])
def brand_market_share(request):
    client = get_bigquery_client()
    query = f"""
        SELECT
            v.brand_name,
            EXTRACT(YEAR FROM f.purchase_date) AS year,
            COUNT(*) AS purchase_count
        FROM `{PROJECT_ID}.gold_dev.fact_purchases` f
        JOIN `{PROJECT_ID}.gold_dev.dim_vehicle` v ON f.vehicle_id = v.vehicle_id
        GROUP BY brand_name, year
        ORDER BY year, brand_name
    """
    results = client.query(query).result()
    data = [dict(row) for row in results]
    return Response(data)