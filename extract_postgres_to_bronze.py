import psycopg2
import os
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account

load_dotenv()

pg_conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="german_car_market",
    user="postgres",
    password=os.environ["DB_PASSWORD"]
)
pg_cur = pg_conn.cursor()

credentials = service_account.Credentials.from_service_account_file(
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
)
bq_client = bigquery.Client(
    credentials=credentials,
    project=os.environ["GCP_PROJECT_ID"]
)

# Tables to extract, in dependency order (matches Bronze table names exactly)
tables_to_extract = [
    "regions", "financing_types", "sales_channels",
    "customers", "stores", "purchases"
]

# Clear existing Bronze tables before reloading, so re-running this script
# doesn't duplicate data on top of a previous run.
for table_name in tables_to_extract:
    bq_client.query(
        f"TRUNCATE TABLE `{os.environ['GCP_PROJECT_ID']}.bronze_postgres_dev.{table_name}`"
    ).result()
print("Cleared existing Bronze tables before reloading.")


def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


for table_name in tables_to_extract:
    pg_cur.execute(f"SELECT * FROM {table_name}")
    columns = [desc[0] for desc in pg_cur.description]
    rows = pg_cur.fetchall()

    rows_to_insert = [dict(zip(columns, row)) for row in rows]

    for row in rows_to_insert:
        for key, value in row.items():
            if hasattr(value, "isoformat"):
                row[key] = value.isoformat()
            elif hasattr(value, "__float__") and not isinstance(value, (int, float)):
                row[key] = float(value)

    table_id = f"{os.environ['GCP_PROJECT_ID']}.bronze_postgres_dev.{table_name}"

    total_loaded = 0
    for batch in chunk_list(rows_to_insert, 5000):
        errors = bq_client.insert_rows_json(table_id, batch)
        if errors == []:
            total_loaded += len(batch)
        else:
            print(f"Errors loading a batch into {table_name}: {errors}")

    print(f"Loaded {total_loaded} rows into {table_name}.")

pg_cur.close()
pg_conn.close()