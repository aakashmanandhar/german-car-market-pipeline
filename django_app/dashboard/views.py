import re
from google.cloud import bigquery
from google import genai
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .bigquery_client import get_bigquery_client

PROJECT_ID = "german-car-pipeline"

genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="europe-west3")

STAR_SCHEMA_DESCRIPTION = """
fact_purchases: purchase_id, customer_id, vehicle_id, store_id, financing_id, channel_id, purchase_date, price, mileage_at_purchase, new_or_used, discount_applied, trade_in_value, net_price
dim_customer: customer_id, first_name, last_name, birth_date, gender, occupation, income_bracket, marital_status, city, region_name
dim_vehicle: vehicle_id, model_year, fuel_type, engine_size_liters, transmission_type, emissions_class, model_name, body_type, segment, brand_name, brand_country, brand_tier
dim_store: store_id, store_name, region_id, region_name, city, store_type
dim_financing: financing_id, type_name
dim_channel: channel_id, channel_name
dim_date: full_date, year, quarter, month, month_name, day_of_week, day_name, is_weekend
"""

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

@api_view(['GET'])
def fuel_type_trend(request):
    client = get_bigquery_client()
    where_clause = region_filter_clause(request)
    query = f"""
        SELECT
            EXTRACT(YEAR FROM f.purchase_date) AS year,
            v.fuel_type,
            COUNT(*) AS purchase_count
        FROM `{PROJECT_ID}.gold_dev.fact_purchases` f
        JOIN `{PROJECT_ID}.gold_dev.dim_vehicle` v ON f.vehicle_id = v.vehicle_id
        JOIN `{PROJECT_ID}.gold_dev.dim_store` s ON f.store_id = s.store_id
        {where_clause}
        GROUP BY year, fuel_type
        ORDER BY year, fuel_type
    """
    results = client.query(query).result()
    return Response([dict(row) for row in results])


@api_view(['GET'])
def price_trend(request):
    client = get_bigquery_client()
    where_clause = region_filter_clause(request)
    query = f"""
        SELECT
            EXTRACT(YEAR FROM f.purchase_date) AS year,
            ROUND(AVG(f.net_price), 2) AS avg_net_price
        FROM `{PROJECT_ID}.gold_dev.fact_purchases` f
        JOIN `{PROJECT_ID}.gold_dev.dim_store` s ON f.store_id = s.store_id
        {where_clause}
        GROUP BY year
        ORDER BY year
    """
    results = client.query(query).result()
    return Response([dict(row) for row in results])


@api_view(['GET'])
def new_vs_used(request):
    client = get_bigquery_client()
    where_clause = region_filter_clause(request)
    query = f"""
        SELECT
            f.new_or_used,
            COUNT(*) AS purchase_count
        FROM `{PROJECT_ID}.gold_dev.fact_purchases` f
        JOIN `{PROJECT_ID}.gold_dev.dim_store` s ON f.store_id = s.store_id
        {where_clause}
        GROUP BY new_or_used
    """
    results = client.query(query).result()
    return Response([dict(row) for row in results])

@api_view(['GET'])
def fuel_type_trend(request):
    client = get_bigquery_client()
    where_clause = region_filter_clause(request)
    query = f"""
        SELECT
            EXTRACT(YEAR FROM f.purchase_date) AS year,
            v.fuel_type,
            COUNT(*) AS purchase_count
        FROM `{PROJECT_ID}.gold_dev.fact_purchases` f
        JOIN `{PROJECT_ID}.gold_dev.dim_vehicle` v ON f.vehicle_id = v.vehicle_id
        JOIN `{PROJECT_ID}.gold_dev.dim_store` s ON f.store_id = s.store_id
        {where_clause}
        GROUP BY year, fuel_type
        ORDER BY year, fuel_type
    """
    results = client.query(query).result()
    return Response([dict(row) for row in results])


@api_view(['GET'])
def price_trend(request):
    client = get_bigquery_client()
    where_clause = region_filter_clause(request)
    query = f"""
        SELECT
            EXTRACT(YEAR FROM f.purchase_date) AS year,
            ROUND(AVG(f.net_price), 2) AS avg_net_price
        FROM `{PROJECT_ID}.gold_dev.fact_purchases` f
        JOIN `{PROJECT_ID}.gold_dev.dim_store` s ON f.store_id = s.store_id
        {where_clause}
        GROUP BY year
        ORDER BY year
    """
    results = client.query(query).result()
    return Response([dict(row) for row in results])


@api_view(['GET'])
def new_vs_used(request):
    client = get_bigquery_client()
    where_clause = region_filter_clause(request)
    query = f"""
        SELECT
            f.new_or_used,
            COUNT(*) AS purchase_count
        FROM `{PROJECT_ID}.gold_dev.fact_purchases` f
        JOIN `{PROJECT_ID}.gold_dev.dim_store` s ON f.store_id = s.store_id
        {where_clause}
        GROUP BY new_or_used
    """
    results = client.query(query).result()
    return Response([dict(row) for row in results])

def classify_question(question):
    prompt = f"""Classify this question about a German car sales database as either "SQL" or "RAG".
SQL = asking for a specific number, count, average, or fact from structured data.
RAG = asking to understand/explain why something happened, or about reviews, opinions, or context.

Question: "{question}"

Respond with exactly one word: SQL or RAG"""
    response = genai_client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return "SQL" if "SQL" in response.text.strip().upper() else "RAG"


def is_safe_select(sql):
    """Only ever allow read-only SELECT queries — a real safety boundary,
    since this SQL is generated by an LLM and run against real data."""
    normalized = sql.strip().upper()
    if not normalized.startswith("SELECT"):
        return False
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER", "CREATE", "MERGE"]
    return not any(word in normalized for word in forbidden)


def handle_sql_question(question):
    client = get_bigquery_client()

    sql_prompt = f"""You are a BigQuery SQL expert. Given this star schema (all tables live in `{PROJECT_ID}.gold_dev`):
{STAR_SCHEMA_DESCRIPTION}

Write ONE BigQuery SQL SELECT query, fully qualifying every table as `{PROJECT_ID}.gold_dev.tablename`, to answer this question. Return ONLY the raw SQL, no explanation, no markdown formatting, no backticks around the whole thing.

Question: "{question}" """

    response = genai_client.models.generate_content(model="gemini-2.5-flash", contents=sql_prompt)
    sql = re.sub(r'^```sql\s*|\s*```$', '', response.text.strip(), flags=re.MULTILINE).strip()

    if not is_safe_select(sql):
        return "I could only generate an unsafe query for that question, so I won't run it.", sql

    try:
        rows = [dict(row) for row in client.query(sql).result()][:20]
    except Exception as e:
        return f"I generated a query but it failed to run: {e}", sql

    phrase_prompt = f"""Question: "{question}"
Query result (JSON rows): {rows}

Answer in one or two plain, natural sentences, using the real numbers from this result."""
    final = genai_client.models.generate_content(model="gemini-2.5-flash", contents=phrase_prompt)
    return final.text.strip(), sql


def handle_rag_question(question):
    client = get_bigquery_client()

    search_query = f"""
        SELECT base.content, base.source_table, distance
        FROM VECTOR_SEARCH(
            TABLE `{PROJECT_ID}.gold_dev.embedded_documents`,
            'embedding',
            (
                SELECT ml_generate_embedding_result AS embedding
                FROM ML.GENERATE_EMBEDDING(
                    MODEL `{PROJECT_ID}.gold_dev.embedding_model`,
                    (SELECT @question AS content)
                )
            ),
            top_k => 5
        )
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("question", "STRING", question)]
    )
    results = list(client.query(search_query, job_config=job_config).result())
    retrieved = [{"content": r["content"], "source": r["source_table"]} for r in results]

    context = "\n".join(f"- ({r['source']}) {r['content']}" for r in retrieved)
    answer_prompt = f"""Context from real customer reviews, dealer notes, and market events:
{context}

Question: "{question}"

Answer in 2-3 plain sentences, based only on the context above."""
    response = genai_client.models.generate_content(model="gemini-2.5-flash", contents=answer_prompt)
    return response.text.strip(), retrieved


@api_view(['POST'])
def ask(request):
    question = request.data.get('question', '').strip()
    if not question:
        return Response({"error": "No question provided"}, status=400)

    route = classify_question(question)

    if route == "SQL":
        answer, sources = handle_sql_question(question)
        tag = "Text-to-SQL"
    else:
        answer, sources = handle_rag_question(question)
        tag = "RAG"

    return Response({"answer": answer, "tag": tag, "sources": sources})