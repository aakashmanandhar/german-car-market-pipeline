import os
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import quote_plus
from pymongo import MongoClient
from google.cloud import bigquery
from google.oauth2 import service_account

load_dotenv()

mongo_user = quote_plus(os.environ["MONGO_USERNAME"])
mongo_pass = quote_plus(os.environ["MONGO_PASSWORD"])
mongo_client = MongoClient(f"mongodb+srv://{mongo_user}:{mongo_pass}@german-car-market.ixetgbe.mongodb.net/")
mongo_db = mongo_client["german_car_market"]

credentials = service_account.Credentials.from_service_account_file(
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
)
bq_client = bigquery.Client(
    credentials=credentials,
    project=os.environ["GCP_PROJECT_ID"]
)

collections_to_extract = ["customer_reviews", "dealer_notes", "market_events"]

# Clear existing Bronze tables before reloading — same idempotency pattern
# as the PostgreSQL extraction script.
for name in collections_to_extract:
    bq_client.query(
        f"TRUNCATE TABLE `{os.environ['GCP_PROJECT_ID']}.bronze_mongo_dev.{name}`"
    ).result()
print("Cleared existing Bronze tables before reloading.")


def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


for collection_name in collections_to_extract:
    documents = list(mongo_db[collection_name].find())

    # Convert MongoDB's ObjectId (_id) into a plain string — BigQuery has no
    # concept of Mongo's native ObjectId type, so this must become JSON-safe text.
    rows_to_insert = []
    for doc in documents:
        doc["_id"] = str(doc["_id"])
        rows_to_insert.append(doc)

    table_id = f"{os.environ['GCP_PROJECT_ID']}.bronze_mongo_dev.{collection_name}"

    total_loaded = 0
    for batch in chunk_list(rows_to_insert, 5000):
        errors = bq_client.insert_rows_json(table_id, batch)
        if errors == []:
            total_loaded += len(batch)
        else:
            print(f"Errors loading a batch into {collection_name}: {errors}")

    print(f"Loaded {total_loaded} rows into {collection_name}.")

mongo_client.close()