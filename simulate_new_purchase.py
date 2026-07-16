import json
import os
from datetime import date
from dotenv import load_dotenv
import psycopg2
from google.cloud import pubsub_v1
from google.oauth2 import service_account

load_dotenv()

# --- Step 1: Insert into the REAL PostgreSQL database first ---
# This makes Postgres the single source of truth. The next batch extraction
# run will naturally pick this row up too, with no conflict, since both
# paths now agree on the same underlying data.
pg_conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="german_car_market",
    user="postgres",
    password=os.environ["DB_PASSWORD"]
)
pg_cur = pg_conn.cursor()

new_purchase_values = {
    "customer_id": 42,
    "vehicle_id": 15,
    "store_id": 3,
    "financing_id": 1,
    "channel_id": 3,
    "purchase_date": date.today(),
    "price": 34500.00,
    "mileage_at_purchase": 0,
    "new_or_used": "New",
    "discount_applied": 500.00,
    "trade_in_value": 0.0
}

pg_cur.execute(
    """INSERT INTO purchases (customer_id, vehicle_id, store_id, financing_id, channel_id,
       purchase_date, price, mileage_at_purchase, new_or_used, discount_applied, trade_in_value)
       VALUES (%(customer_id)s, %(vehicle_id)s, %(store_id)s, %(financing_id)s, %(channel_id)s,
       %(purchase_date)s, %(price)s, %(mileage_at_purchase)s, %(new_or_used)s,
       %(discount_applied)s, %(trade_in_value)s)
       RETURNING purchase_id""",
    new_purchase_values
)
real_purchase_id = pg_cur.fetchone()[0]
pg_conn.commit()
pg_cur.close()
pg_conn.close()

print(f"Inserted purchase_id {real_purchase_id} into real PostgreSQL.")

# --- Step 2: Stream that SAME real purchase to Bronze via Pub/Sub ---
# This gets it into BigQuery immediately, without waiting for the next
# batch run, while Postgres remains the authoritative record.
credentials = service_account.Credentials.from_service_account_file(
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
)
publisher = pubsub_v1.PublisherClient(credentials=credentials)
topic_path = publisher.topic_path(os.environ["GCP_PROJECT_ID"], "new-purchase-dev")

streaming_payload = {"purchase_id": real_purchase_id, **new_purchase_values}
streaming_payload["purchase_date"] = streaming_payload["purchase_date"].isoformat()

message_data = json.dumps(streaming_payload).encode("utf-8")
future = publisher.publish(topic_path, message_data)
message_id = future.result()

print(f"Published message {message_id} for purchase_id {real_purchase_id} to Pub/Sub.")