PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_device;
DROP TABLE IF EXISTS dim_payment_method;
DROP TABLE IF EXISTS dim_geography;
DROP TABLE IF EXISTS dim_channel;
DROP TABLE IF EXISTS dim_category;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date TEXT NOT NULL UNIQUE,
    year_num INTEGER NOT NULL,
    quarter_num INTEGER NOT NULL,
    month_num INTEGER NOT NULL,
    year_month TEXT NOT NULL
);

CREATE TABLE dim_customer (
    customer_key INTEGER PRIMARY KEY,
    customer_id TEXT NOT NULL UNIQUE
);

CREATE TABLE dim_category (
    category_key INTEGER PRIMARY KEY,
    category TEXT NOT NULL UNIQUE
);

CREATE TABLE dim_channel (
    channel_key INTEGER PRIMARY KEY,
    channel TEXT NOT NULL UNIQUE
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
    sales_key INTEGER PRIMARY KEY,
    order_id TEXT NOT NULL UNIQUE,
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    customer_key INTEGER NOT NULL REFERENCES dim_customer(customer_key),
    category_key INTEGER NOT NULL REFERENCES dim_category(category_key),
    channel_key INTEGER NOT NULL REFERENCES dim_channel(channel_key),
    geography_key INTEGER NOT NULL REFERENCES dim_geography(geography_key),
    payment_method_key INTEGER NOT NULL REFERENCES dim_payment_method(payment_method_key),
    device_key INTEGER NOT NULL REFERENCES dim_device(device_key),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    discount_rate REAL NOT NULL CHECK (discount_rate >= 0 AND discount_rate <= 0.20),
    net_revenue REAL NOT NULL CHECK (net_revenue >= 0),
    cost REAL NOT NULL CHECK (cost >= 0)
);

WITH RECURSIVE calendar(full_date) AS (
    SELECT MIN(order_date) FROM sales
    UNION ALL
    SELECT date(full_date, '+1 day')
    FROM calendar
    WHERE full_date < (SELECT MAX(order_date) FROM sales)
)
INSERT INTO dim_date (date_key, full_date, year_num, quarter_num, month_num, year_month)
SELECT CAST(strftime('%Y%m%d', full_date) AS INTEGER),
       full_date,
       CAST(strftime('%Y', full_date) AS INTEGER),
       ((CAST(strftime('%m', full_date) AS INTEGER) - 1) / 3) + 1,
       CAST(strftime('%m', full_date) AS INTEGER),
       strftime('%Y-%m', full_date)
FROM calendar;

INSERT INTO dim_customer (customer_id)
SELECT DISTINCT customer_id FROM sales ORDER BY customer_id;

INSERT INTO dim_category (category)
SELECT DISTINCT category FROM sales ORDER BY category;

INSERT INTO dim_channel (channel)
SELECT DISTINCT channel FROM sales ORDER BY channel;

INSERT INTO dim_geography (country, city)
SELECT DISTINCT country, city FROM sales ORDER BY country, city;

INSERT INTO dim_payment_method (payment_method)
SELECT DISTINCT payment_method FROM sales ORDER BY payment_method;

INSERT INTO dim_device (device)
SELECT DISTINCT device FROM sales ORDER BY device;

INSERT INTO fact_sales (
    order_id, date_key, customer_key, category_key, channel_key,
    geography_key, payment_method_key, device_key, quantity, unit_price,
    discount_rate, net_revenue, cost
)
SELECT s.order_id,
       d.date_key,
       c.customer_key,
       ca.category_key,
       ch.channel_key,
       g.geography_key,
       pm.payment_method_key,
       dv.device_key,
       CAST(s.quantity AS INTEGER),
       CAST(s.unit_price AS REAL),
       CAST(s.discount_rate AS REAL),
       CAST(s.net_revenue AS REAL),
       CAST(s.cost AS REAL)
FROM sales AS s
JOIN dim_date AS d ON d.full_date = s.order_date
JOIN dim_customer AS c ON c.customer_id = s.customer_id
JOIN dim_category AS ca ON ca.category = s.category
JOIN dim_channel AS ch ON ch.channel = s.channel
JOIN dim_geography AS g ON g.country = s.country AND g.city = s.city
JOIN dim_payment_method AS pm ON pm.payment_method = s.payment_method
JOIN dim_device AS dv ON dv.device = s.device;
