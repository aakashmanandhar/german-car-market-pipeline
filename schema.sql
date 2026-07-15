CREATE TABLE regions (
    region_id   SERIAL PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL,
    country     VARCHAR(50) NOT NULL DEFAULT 'Germany'
);

CREATE TABLE financing_types (
    financing_id SERIAL PRIMARY KEY,
    type_name    VARCHAR(30) NOT NULL
);

CREATE TABLE sales_channels (
    channel_id   SERIAL PRIMARY KEY,
    channel_name VARCHAR(30) NOT NULL
);

CREATE TABLE customers (
    customer_id     SERIAL PRIMARY KEY,
    first_name      VARCHAR(50),
    last_name       VARCHAR(50),
    birth_date      DATE,
    gender          VARCHAR(10),
    occupation      VARCHAR(50),
    income_bracket  VARCHAR(20),
    marital_status  VARCHAR(20),
    region_id       INTEGER REFERENCES regions(region_id),
    city            VARCHAR(50)
);

CREATE TABLE stores (
    store_id    SERIAL PRIMARY KEY,
    store_name  VARCHAR(100),
    region_id   INTEGER REFERENCES regions(region_id),
    city        VARCHAR(50),
    store_type  VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS brands (
    brand_id           SERIAL PRIMARY KEY,
    brand_name         VARCHAR(50) NOT NULL,
    country_of_origin  VARCHAR(50),
    brand_tier         VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS brands (
    brand_id           SERIAL PRIMARY KEY,
    brand_name         VARCHAR(50) NOT NULL,
    country_of_origin  VARCHAR(50),
    brand_tier         VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS models (
    model_id    SERIAL PRIMARY KEY,
    brand_id    INTEGER REFERENCES brands(brand_id),
    model_name  VARCHAR(50) NOT NULL,
    body_type   VARCHAR(30),
    segment     VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id         SERIAL PRIMARY KEY,
    model_id           INTEGER REFERENCES models(model_id),
    model_year         INTEGER NOT NULL,
    fuel_type          VARCHAR(20),
    engine_size_liters NUMERIC(3,1),
    transmission_type  VARCHAR(20),
    emissions_class    VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS purchases (
    purchase_id         SERIAL PRIMARY KEY,
    customer_id         INTEGER REFERENCES customers(customer_id),
    vehicle_id          INTEGER REFERENCES vehicles(vehicle_id),
    store_id            INTEGER REFERENCES stores(store_id),
    financing_id         INTEGER REFERENCES financing_types(financing_id),
    channel_id          INTEGER REFERENCES sales_channels(channel_id),
    purchase_date       DATE NOT NULL,
    price               NUMERIC(10,2),
    mileage_at_purchase INTEGER DEFAULT 0,
    new_or_used         VARCHAR(10),
    discount_applied    NUMERIC(10,2) DEFAULT 0,
    trade_in_value      NUMERIC(10,2) DEFAULT 0
);

SELECT COUNT(*) FROM information_schema.table_constraints 
WHERE constraint_type = 'FOREIGN KEY';