import psycopg2
import os
import random
from datetime import timedelta
from dotenv import load_dotenv
from urllib.parse import quote_plus
from pymongo import MongoClient
from faker import Faker

load_dotenv()

fake = Faker('de_DE')

# Read-only connection — just fetching real purchases already created by generate_postgres_data.py
pg_conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="german_car_market",
    user="postgres",
    password=os.environ["DB_PASSWORD"]
)
pg_cur = pg_conn.cursor()

mongo_user = quote_plus(os.environ['MONGO_USERNAME'])
mongo_pass = quote_plus(os.environ['MONGO_PASSWORD'])
mongo_client = MongoClient(f"mongodb+srv://{mongo_user}:{mongo_pass}@german-car-market.ixetgbe.mongodb.net/")
mongo_db = mongo_client["german_car_market"]

# Development safeguard: clear existing Mongo data before regenerating.
mongo_db["customer_reviews"].delete_many({})
mongo_db["dealer_notes"].delete_many({})
mongo_db["market_events"].delete_many({})

pg_cur.execute("SELECT purchase_id, purchase_date FROM purchases")
all_purchases = pg_cur.fetchall()

# --- Customer reviews ---
review_templates_positive = [
    "Great car, exactly as described. Very happy with the purchase.",
    "Smooth buying experience, the dealer was helpful and professional.",
    "Love the fuel efficiency, would buy from this dealer again.",
    "Sehr zufrieden mit dem Auto und dem Service.",
    "Excellent condition for a used vehicle, no complaints.",
]
review_templates_negative = [
    "Paperwork took way longer than expected, frustrating experience.",
    "Car had some issues shortly after purchase, disappointed.",
    "Sales staff seemed rushed and didn't answer all my questions.",
    "Nicht so gut, Lieferung war verspätet.",
    "Overpriced for the condition it was actually in.",
]
review_templates_neutral = ["Good car.", "It's fine.", "As expected.", "Okay experience overall."]

customer_reviews_docs = []
for purchase_id, purchase_date in all_purchases:
    if random.random() < 0.25:
        sentiment = random.choices(["positive", "negative", "neutral"], weights=[55, 20, 25])[0]
        if sentiment == "positive":
            text = random.choice(review_templates_positive)
            rating = random.choice([4, 5])
        elif sentiment == "negative":
            text = random.choice(review_templates_negative)
            rating = random.choice([1, 2])
        else:
            text = random.choice(review_templates_neutral)
            rating = 3

        if random.random() < 0.10:
            rating = None

        review_date = purchase_date + timedelta(days=random.randint(1, 45))
        customer_reviews_docs.append({
            "purchase_id": purchase_id,
            "review_text": text,
            "rating": rating,
            "review_date": review_date.isoformat()
        })

mongo_db["customer_reviews"].insert_many(customer_reviews_docs)
print(f"Inserted {len(customer_reviews_docs)} customer reviews into MongoDB.")

# --- Dealer notes ---
note_templates = [
    "Customer negotiated {amount} EUR off the listed price after trade-in discussion.",
    "Financing approved same day, customer opted for {financing} plan.",
    "Delivery delayed by 3 days due to registration paperwork.",
    "Customer requested additional inspection before finalizing purchase.",
    "Straightforward sale, no negotiation, customer paid asking price.",
]

dealer_notes_docs = []
for purchase_id, purchase_date in all_purchases:
    if random.random() < 0.15:
        template = random.choice(note_templates)
        text = template.format(amount=random.randint(200, 2000), financing=random.choice(["Loan", "Lease"]))
        note_date = purchase_date + timedelta(days=random.randint(0, 5))
        dealer_notes_docs.append({
            "purchase_id": purchase_id,
            "note_text": text,
            "staff_member": fake.name(),
            "note_date": note_date.isoformat()
        })

mongo_db["dealer_notes"].insert_many(dealer_notes_docs)
print(f"Inserted {len(dealer_notes_docs)} dealer notes into MongoDB.")

# --- Market events ---
market_events_docs = [
    {"event_date": "2008-09-15", "event_title": "Global financial crisis",
     "event_description": "Lehman Brothers collapse triggers a global financial crisis, sharply reducing car sales and financing availability through 2009-2010."},
    {"event_date": "2015-09-18", "event_title": "Dieselgate scandal breaks",
     "event_description": "Volkswagen's emissions cheating scandal becomes public, severely damaging diesel's reputation and accelerating the shift toward petrol, hybrid, and electric vehicles in Germany."},
    {"event_date": "2020-03-01", "event_title": "COVID-19 disrupts the automotive market",
     "event_description": "Pandemic lockdowns halt production and dealership sales for months, followed by a sharp rebound and supply chain shortages affecting new vehicle availability into 2022."},
    {"event_date": "2023-01-01", "event_title": "German EV subsidies reduced",
     "event_description": "The German government scales back electric vehicle purchase subsidies, slightly slowing the growth rate of EV adoption compared to 2020-2022."},
]

mongo_db["market_events"].insert_many(market_events_docs)
print(f"Inserted {len(market_events_docs)} market events into MongoDB.")

pg_cur.close()
pg_conn.close()