-- SQL Starter (PostgreSQL/SQL Server friendly)
-- 1) Top categorías por ingresos
SELECT category, SUM(net_revenue) AS revenue
FROM sales
GROUP BY category
ORDER BY revenue DESC;

-- 2) Margen por canal
SELECT channel,
       SUM(net_revenue) AS revenue,
       SUM(net_revenue - cost) AS gross_margin
FROM sales
GROUP BY channel
ORDER BY gross_margin DESC;

-- 3) Clientes más valiosos (LTV proxy)
SELECT customer_id,
       SUM(net_revenue) AS ltv_proxy,
       COUNT(*) AS orders
FROM sales
GROUP BY customer_id
ORDER BY ltv_proxy DESC
LIMIT 20;
