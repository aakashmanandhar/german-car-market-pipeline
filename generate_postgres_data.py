import psycopg2
import os
import random
from datetime import date
from dotenv import load_dotenv
from faker import Faker

load_dotenv()

fake = Faker('de_DE')

pg_conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="german_car_market",
    user="postgres",
    password=os.environ["DB_PASSWORD"]
)
pg_cur = pg_conn.cursor()

# Development safeguard: clear existing data before regenerating.
pg_cur.execute("TRUNCATE TABLE regions, financing_types, sales_channels, brands, models, vehicles, customers, stores, purchases RESTART IDENTITY CASCADE;")
pg_conn.commit()

# --- Regions ---
regions = [
    "Bavaria", "North Rhine-Westphalia", "Baden-Württemberg", "Lower Saxony",
    "Hesse", "Saxony", "Rhineland-Palatinate", "Berlin", "Schleswig-Holstein",
    "Brandenburg", "Saxony-Anhalt", "Thuringia", "Hamburg", "Mecklenburg-Vorpommern",
    "Saarland", "Bremen"
]
region_ids = {}
for name in regions:
    pg_cur.execute("INSERT INTO regions (region_name) VALUES (%s) RETURNING region_id", (name,))
    region_ids[name] = pg_cur.fetchone()[0]

# --- Financing types ---
financing_types = ["Cash", "Loan", "Lease"]
financing_ids = {}
for name in financing_types:
    pg_cur.execute("INSERT INTO financing_types (type_name) VALUES (%s) RETURNING financing_id", (name,))
    financing_ids[name] = pg_cur.fetchone()[0]

# --- Sales channels ---
sales_channels = ["In-person", "Phone", "Online"]
channel_ids = {}
for name in sales_channels:
    pg_cur.execute("INSERT INTO sales_channels (channel_name) VALUES (%s) RETURNING channel_id", (name,))
    channel_ids[name] = pg_cur.fetchone()[0]

pg_conn.commit()
print(f"Inserted {len(region_ids)} regions, {len(financing_ids)} financing types, {len(channel_ids)} sales channels.")

# --- Brands ---
brands_data = [
    ("Volkswagen", "Germany", "mainstream"), ("BMW", "Germany", "premium"),
    ("Mercedes-Benz", "Germany", "premium"), ("Audi", "Germany", "premium"),
    ("Opel", "Germany", "mainstream"), ("Porsche", "Germany", "luxury"),
    ("Toyota", "Japan", "mainstream"), ("Renault", "France", "mainstream"),
    ("Skoda", "Czech Republic", "mainstream"), ("Fiat", "Italy", "mainstream"),
]
brand_ids = {}
for name, origin, tier in brands_data:
    pg_cur.execute(
        "INSERT INTO brands (brand_name, country_of_origin, brand_tier) VALUES (%s, %s, %s) RETURNING brand_id",
        (name, origin, tier)
    )
    brand_ids[name] = pg_cur.fetchone()[0]

pg_conn.commit()
print(f"Inserted {len(brand_ids)} brands.")

# --- Models ---
models_data = [
    ("Volkswagen", "Golf", "hatchback", "compact"), ("Volkswagen", "Passat", "sedan", "mid-size"),
    ("Volkswagen", "Tiguan", "SUV", "compact"), ("BMW", "3 Series", "sedan", "mid-size"),
    ("BMW", "X5", "SUV", "luxury"), ("Mercedes-Benz", "C-Class", "sedan", "mid-size"),
    ("Mercedes-Benz", "GLE", "SUV", "luxury"), ("Audi", "A4", "sedan", "mid-size"),
    ("Audi", "Q5", "SUV", "compact"), ("Opel", "Corsa", "hatchback", "economy"),
    ("Opel", "Astra", "hatchback", "compact"), ("Porsche", "911", "coupe", "luxury"),
    ("Toyota", "Corolla", "sedan", "compact"), ("Toyota", "RAV4", "SUV", "compact"),
    ("Renault", "Clio", "hatchback", "economy"), ("Skoda", "Octavia", "estate", "mid-size"),
    ("Fiat", "500", "hatchback", "economy"),
]
model_ids = {}
for brand_name, model_name, body_type, segment in models_data:
    pg_cur.execute(
        "INSERT INTO models (brand_id, model_name, body_type, segment) VALUES (%s, %s, %s, %s) RETURNING model_id",
        (brand_ids[brand_name], model_name, body_type, segment)
    )
    model_ids[(brand_name, model_name)] = pg_cur.fetchone()[0]

pg_conn.commit()
print(f"Inserted {len(model_ids)} models.")

# --- Vehicles ---
def pick_fuel_type(year):
    if year < 2010:
        return random.choices(["petrol", "diesel"], weights=[55, 45])[0]
    elif year < 2015:
        return random.choices(["petrol", "diesel"], weights=[50, 50])[0]
    elif year < 2020:
        return random.choices(["petrol", "diesel", "hybrid", "electric"], weights=[45, 35, 15, 5])[0]
    else:
        return random.choices(["petrol", "diesel", "hybrid", "electric"], weights=[30, 15, 25, 30])[0]

def pick_emissions_class(year):
    if year < 1992:
        return None
    elif year < 1996:
        return "Euro 1"
    elif year < 2000:
        return "Euro 2"
    elif year < 2005:
        return "Euro 3"
    elif year < 2009:
        return "Euro 4"
    elif year < 2014:
        return "Euro 5"
    else:
        return "Euro 6"

def pick_transmission(year):
    auto_share = min(10 + (year - 1990) * 1.5, 70)
    return random.choices(["manual", "automatic"], weights=[100 - auto_share, auto_share])[0]

vehicle_ids = []
for (brand_name, model_name), m_id in model_ids.items():
    for year in range(1990, 2027):
        if random.random() < 0.4:
            continue
        fuel_type = pick_fuel_type(year)
        emissions = pick_emissions_class(year)
        transmission = pick_transmission(year)
        engine_size = round(random.uniform(1.0, 4.0), 1)
        pg_cur.execute(
            """INSERT INTO vehicles (model_id, model_year, fuel_type, engine_size_liters, transmission_type, emissions_class)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING vehicle_id""",
            (m_id, year, fuel_type, engine_size, transmission, emissions)
        )
        vehicle_ids.append(pg_cur.fetchone()[0])

pg_conn.commit()
print(f"Inserted {len(vehicle_ids)} vehicle configurations.")

# --- Customers ---
occupations = ["Engineer", "Teacher", "Nurse", "Sales Manager", "Software Developer",
               "Doctor", "Accountant", "Electrician", "Retired", "Business Owner"]
income_brackets = ["<30k", "30k-50k", "50k-80k", "80k-120k", "120k+"]
marital_statuses = ["Single", "Married", "Divorced", "Widowed"]
region_names = list(region_ids.keys())

city_variants = {
    "Munich": ["Munich", "München", "Muenchen"],
    "Cologne": ["Cologne", "Köln", "Koeln"],
    "Nuremberg": ["Nuremberg", "Nürnberg", "Nuernberg"],
}

def pick_city():
    if random.random() < 0.2:
        base_city = random.choice(list(city_variants.keys()))
        return random.choice(city_variants[base_city])
    return fake.city()

customer_ids = []
for _ in range(8000):
    gender = random.choice(["Male", "Female"])
    first_name = fake.first_name_male() if gender == "Male" else fake.first_name_female()
    last_name = fake.last_name()
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=85)
    region_name = random.choice(region_names)
    income = None if random.random() < 0.10 else random.choice(income_brackets)
    occupation = None if random.random() < 0.08 else random.choice(occupations)

    pg_cur.execute(
        """INSERT INTO customers (first_name, last_name, birth_date, gender, occupation, income_bracket, marital_status, region_id, city)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING customer_id""",
        (first_name, last_name, birth_date, gender, occupation,
         income, random.choice(marital_statuses), region_ids[region_name], pick_city())
    )
    customer_ids.append(pg_cur.fetchone()[0])

pg_conn.commit()
print(f"Inserted {len(customer_ids)} customers.")

# --- Stores ---
store_types = ["Dealership", "Franchise", "Certified Pre-Owned Center"]
store_ids = []
for region_name in region_names:
    for _ in range(random.randint(2, 4)):
        pg_cur.execute(
            "INSERT INTO stores (store_name, region_id, city, store_type) VALUES (%s, %s, %s, %s) RETURNING store_id",
            (f"{fake.company()} Auto", region_ids[region_name], fake.city(), random.choice(store_types))
        )
        store_ids.append(pg_cur.fetchone()[0])

pg_conn.commit()
print(f"Inserted {len(store_ids)} stores.")

# --- Purchases ---
financing_names = list(financing_ids.keys())

def price_for_year(base_price, year):
    inflation_factor = 1 + ((year - 1990) / 36) * 1.0
    return round(base_price * inflation_factor, 2)

def pick_channel(year):
    if year < 2015:
        return random.choices(["In-person", "Phone"], weights=[85, 15])[0]
    else:
        return random.choices(["In-person", "Phone", "Online"], weights=[55, 10, 35])[0]

def insert_purchase(customer_id, vehicle_id, store_id, financing_id, channel_id,
                     purchase_date, price, mileage, new_or_used, discount, trade_in):
    pg_cur.execute(
        """INSERT INTO purchases (customer_id, vehicle_id, store_id, financing_id, channel_id,
           purchase_date, price, mileage_at_purchase, new_or_used, discount_applied, trade_in_value)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (customer_id, vehicle_id, store_id, financing_id, channel_id,
         purchase_date, price, mileage, new_or_used, discount, trade_in)
    )

purchase_count = 0
for _ in range(50000):
    vehicle_id = random.choice(vehicle_ids)
    pg_cur.execute("SELECT model_year FROM vehicles WHERE vehicle_id = %s", (vehicle_id,))
    year = pg_cur.fetchone()[0]

    purchase_date = date(year, random.randint(1, 12), random.randint(1, 28))
    base_price = random.uniform(15000, 45000)
    price = price_for_year(base_price, year)
    if random.random() < 0.02:
        price = round(price / 10, 2)

    customer_id = random.choice(customer_ids)
    store_id = random.choice(store_ids)
    financing_id = financing_ids[random.choice(financing_names)]
    channel_id = channel_ids[pick_channel(year)]
    new_or_used = random.choices(["New", "Used"], weights=[60, 40])[0]

    if new_or_used == "Used" and random.random() < 0.03:
        mileage = None
    else:
        mileage = 0 if new_or_used == "New" else random.randint(5000, 150000)

    discount = round(random.uniform(0, price * 0.1), 2)
    trade_in = round(random.uniform(0, 8000), 2) if random.random() < 0.4 else 0
    if random.random() < 0.01:
        discount = -abs(discount) if discount > 0 else -50.0

    insert_purchase(customer_id, vehicle_id, store_id, financing_id, channel_id,
                     purchase_date, price, mileage, new_or_used, discount, trade_in)
    purchase_count += 1

    if random.random() < 0.04:
        insert_purchase(customer_id, vehicle_id, store_id, financing_id, channel_id,
                         purchase_date, price, mileage, new_or_used, discount, trade_in)
        purchase_count += 1

pg_conn.commit()
print(f"Inserted {purchase_count} purchases (including deliberate duplicates).")

pg_cur.close()
pg_conn.close()