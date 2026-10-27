PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_device;
DROP TABLE IF EXISTS dim_payment_method;
DROP TABLE IF EXISTS dim_geography;
DROP TABLE IF EXISTS dim_category;
DROP TABLE IF EXISTS dim_channel;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date TEXT NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    month_name TEXT NOT NULL,
    weekday_name TEXT NOT NULL
);

CREATE TABLE dim_customer (
    customer_key INTEGER PRIMARY KEY,
    customer_id TEXT NOT NULL UNIQUE
);

CREATE TABLE dim_channel (
    channel_key INTEGER PRIMARY KEY,
    channel TEXT NOT NULL UNIQUE
);

CREATE TABLE dim_category (
    category_key INTEGER PRIMARY KEY,
    category TEXT NOT NULL UNIQUE
);

CREATE TABLE dim_geography (
    geography_key INTEGER PRIMARY KEY,
    country TEXT NOT NULL,
    city TEXT NOT NULL,
    UNIQUE (country, city)
);

CREATE TABLE dim_payment_method (
    payment_method_key INTEGER PRIMARY KEY,
    payment_method TEXT NOT NULL UNIQUE
);

CREATE TABLE dim_device (
    device_key INTEGER PRIMARY KEY,
    device TEXT NOT NULL UNIQUE
);

CREATE TABLE fact_sales (
    order_id TEXT PRIMARY KEY,
    date_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    channel_key INTEGER NOT NULL,
    category_key INTEGER NOT NULL,
    geography_key INTEGER NOT NULL,
    payment_method_key INTEGER NOT NULL,
    device_key INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    discount_rate REAL NOT NULL CHECK (discount_rate BETWEEN 0 AND 0.20),
    net_revenue REAL NOT NULL CHECK (net_revenue >= 0),
    cost REAL NOT NULL CHECK (cost >= 0),
    gross_margin REAL NOT NULL,
    CHECK (
        ABS(net_revenue - ROUND(quantity * unit_price * (1 - discount_rate), 2)) <= 0.011
    ),
    CHECK (ABS(gross_margin - (net_revenue - cost)) <= 0.011),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (channel_key) REFERENCES dim_channel(channel_key),
    FOREIGN KEY (category_key) REFERENCES dim_category(category_key),
    FOREIGN KEY (geography_key) REFERENCES dim_geography(geography_key),
    FOREIGN KEY (payment_method_key) REFERENCES dim_payment_method(payment_method_key),
    FOREIGN KEY (device_key) REFERENCES dim_device(device_key)
);

CREATE INDEX idx_fact_sales_date ON fact_sales(date_key);
CREATE INDEX idx_fact_sales_customer ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_category ON fact_sales(category_key);
CREATE INDEX idx_fact_sales_channel ON fact_sales(channel_key);
