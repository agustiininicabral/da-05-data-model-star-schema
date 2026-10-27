-- SQL examples for the retail star schema (SQLite).
-- QUERY: Q01 Monthly revenue and margin
SELECT d.year, d.month, d.month_name,
       ROUND(SUM(f.net_revenue), 2) AS revenue,
       ROUND(SUM(f.gross_margin), 2) AS gross_margin
FROM fact_sales AS f
INNER JOIN dim_date AS d ON d.date_key = f.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- QUERY: Q02 Revenue by channel
SELECT c.channel,
       COUNT(*) AS orders,
       ROUND(SUM(f.net_revenue), 2) AS revenue,
       ROUND(SUM(f.gross_margin), 2) AS gross_margin
FROM fact_sales AS f
INNER JOIN dim_channel AS c ON c.channel_key = f.channel_key
GROUP BY c.channel
ORDER BY revenue DESC;

-- QUERY: Q03 Revenue by category
SELECT c.category,
       COUNT(*) AS orders,
       ROUND(SUM(f.net_revenue), 2) AS revenue,
       ROUND(SUM(f.gross_margin), 2) AS gross_margin
FROM fact_sales AS f
INNER JOIN dim_category AS c ON c.category_key = f.category_key
GROUP BY c.category
ORDER BY revenue DESC;

-- QUERY: Q04 Top geographies by revenue
SELECT g.country, g.city,
       COUNT(*) AS orders,
       ROUND(SUM(f.net_revenue), 2) AS revenue
FROM fact_sales AS f
INNER JOIN dim_geography AS g ON g.geography_key = f.geography_key
GROUP BY g.country, g.city
ORDER BY revenue DESC
LIMIT 10;

-- QUERY: Q05 Top customers by revenue
SELECT c.customer_id,
       COUNT(*) AS orders,
       ROUND(SUM(f.net_revenue), 2) AS revenue
FROM fact_sales AS f
INNER JOIN dim_customer AS c ON c.customer_key = f.customer_key
GROUP BY c.customer_id
ORDER BY revenue DESC
LIMIT 20;

-- QUERY: Q06 Revenue by payment method and device
SELECT p.payment_method, d.device,
       COUNT(*) AS orders,
       ROUND(SUM(f.net_revenue), 2) AS revenue
FROM fact_sales AS f
INNER JOIN dim_payment_method AS p
    ON p.payment_method_key = f.payment_method_key
INNER JOIN dim_device AS d ON d.device_key = f.device_key
GROUP BY p.payment_method, d.device
ORDER BY revenue DESC;

-- QUERY: Q07 Monthly cumulative revenue
WITH monthly AS (
    SELECT d.year, d.month,
           printf('%04d-%02d', d.year, d.month) AS year_month,
           SUM(f.net_revenue) AS revenue
    FROM fact_sales AS f
    INNER JOIN dim_date AS d ON d.date_key = f.date_key
    GROUP BY d.year, d.month
)
SELECT year_month,
       ROUND(revenue, 2) AS revenue,
       ROUND(SUM(revenue) OVER (
           ORDER BY year_month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ), 2) AS cumulative_revenue
FROM monthly
ORDER BY year_month;

-- QUERY: Q08 Fact table grain and revenue reconciliation
SELECT COUNT(*) AS fact_rows,
       COUNT(DISTINCT order_id) AS distinct_orders,
       ROUND(SUM(net_revenue), 2) AS revenue,
       ROUND(SUM(gross_margin), 2) AS gross_margin
FROM fact_sales;
