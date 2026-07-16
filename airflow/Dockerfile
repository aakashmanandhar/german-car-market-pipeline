FROM apache/airflow:2.9.3-python3.12

USER airflow

RUN pip install --no-cache-dir \
    psycopg2-binary==2.9.12 \
    python-dotenv==1.2.2 \
    google-cloud-bigquery==3.42.2 \
    pymongo==4.17.0 \
    requests==2.32.3 \
    faker==40.31.0 \
    dbt-bigquery==1.11.3