import json
import os
import random
from datetime import date
from dotenv import load_dotenv
from google.cloud import pubsub_v1
from google.oauth2 import service_account

load_dotenv()

credentials = service_account.Credentials.from_service_account_file(
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
)
publisher = pubsub_v1.PublisherClient(credentials=credentials)
topic_path = publisher.topic_path(os.environ["GCP_PROJECT_ID"], "new-purchase-dev")

# A single simulated real-time purchase — using real, existing IDs so this
# integrates correctly with actual customers/vehicles/stores already in Bronze.
new_purchase = {
    "purchase_id": random.randint(900000, 999999),  # high range, avoids colliding with real IDs
    "customer_id": 42,
    "vehicle_id": 15,
    "store_id": 3,
    "financing_id": 1,
    "channel_id": 3,
    "purchase_date": date.today().isoformat(),
    "price": 34500.00,
    "mileage_at_purchase": 0,
    "new_or_used": "New",
    "discount_applied": 500.00,
    "trade_in_value": 0.0
}

message_data = json.dumps(new_purchase).encode("utf-8")
future = publisher.publish(topic_path, message_data)
message_id = future.result()

print(f"Published message {message_id} with purchase_id {new_purchase['purchase_id']}")