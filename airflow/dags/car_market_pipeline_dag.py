from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_DIR = "/opt/airflow/dbt"

with DAG(
    dag_id="german_car_market_pipeline",
    description="PostgreSQL + MongoDB + API -> Bronze -> dbt Silver -> dbt Gold, daily",
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["car-market", "postgres", "mongo", "api", "gcp", "star-schema"],
) as dag:

    extract_postgres = BashOperator(
        task_id="extract_postgres_to_bronze",
        bash_command="python /opt/airflow/extract_postgres_to_bronze.py",
    )

    extract_mongo = BashOperator(
        task_id="extract_mongo_to_bronze",
        bash_command="python /opt/airflow/extract_mongo_to_bronze.py",
    )

    extract_api = BashOperator(
        task_id="extract_api_to_bronze",
        bash_command="python /opt/airflow/extract_api_to_bronze.py",
    )

    dbt_run_silver = BashOperator(
        task_id="dbt_run_silver",
        bash_command=f"cd {DBT_DIR} && dbt run --select silver.*",
    )

    dbt_run_gold = BashOperator(
        task_id="dbt_run_gold",
        bash_command=f"cd {DBT_DIR} && dbt run --select gold.*",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && dbt test",
    )

    [extract_postgres, extract_mongo, extract_api] >> dbt_run_silver >> dbt_run_gold >> dbt_test