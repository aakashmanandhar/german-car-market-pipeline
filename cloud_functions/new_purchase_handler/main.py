import base64
import json
import os
from google.cloud import bigquery

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "german-car-pipeline")
TABLE_ID = f"{PROJECT_ID}.bronze_postgres_dev.purchases"

bq_client = bigquery.Client(project=PROJECT_ID)


def handle_new_purchase(event, context):
    """
    Triggered by a message on the new-purchase Pub/Sub topic.
    Appends exactly one new purchase row to Bronze — does NOT truncate,
    since this represents one real-time event, not a full historical reload.
    """
    message_data = base64.b64decode(event["data"]).decode("utf-8")
    purchase = json.loads(message_data)

    errors = bq_client.insert_rows_json(TABLE_ID, [purchase])

    if errors == []:
        print(f"Successfully streamed purchase_id {purchase.get('purchase_id')} into Bronze.")
    else:
        print(f"Errors inserting purchase: {errors}")