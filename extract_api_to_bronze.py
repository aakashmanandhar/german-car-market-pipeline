import os
import requests
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account

load_dotenv()

API_BASE_URL = "http://localhost:5001/api/v1"
API_USER = os.environ["CATALOG_API_USER"]
API_PASS = os.environ["CATALOG_API_PASS"]

credentials = service_account.Credentials.from_service_account_file(
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
)
bq_client = bigquery.Client(
    credentials=credentials,
    project=os.environ["GCP_PROJECT_ID"]
)

endpoints_to_extract = ["brands", "models", "vehicles"]

# Clear existing Bronze tables before reloading — same idempotency pattern
# as the other two extraction scripts.
for name in endpoints_to_extract:
    bq_client.query(
        f"TRUNCATE TABLE `{os.environ['GCP_PROJECT_ID']}.bronze_api_dev.{name}`"
    ).result()
print("Cleared existing Bronze tables before reloading.")


def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


for endpoint in endpoints_to_extract:
    response = requests.get(
        f"{API_BASE_URL}/{endpoint}",
        auth=(API_USER, API_PASS),
        timeout=30
    )
    response.raise_for_status()  # raises an error immediately if the API call failed

    rows_to_insert = response.json()["data"]

    table_id = f"{os.environ['GCP_PROJECT_ID']}.bronze_api_dev.{endpoint}"

    total_loaded = 0
    for batch in chunk_list(rows_to_insert, 5000):
        errors = bq_client.insert_rows_json(table_id, batch)
        if errors == []:
            total_loaded += len(batch)
        else:
            print(f"Errors loading a batch into {endpoint}: {errors}")

    print(f"Loaded {total_loaded} rows into {endpoint}.")