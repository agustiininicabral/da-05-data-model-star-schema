# Data Dictionary

## sales_3500.csv
- order_id (text): identificador único de pedido
- customer_id (text): identificador de cliente
- order_date (date): fecha de compra
- category (category): categoría del producto
- channel (category): canal de adquisición/venta
- country (category): país
- city (text): ciudad
- quantity (int): unidades
- unit_price (decimal): precio unitario
- discount_rate (decimal): descuento aplicado (0-0.20)
- net_revenue (decimal): ingresos netos (qty*price*(1-discount))
- cost (decimal): costo estimado
- payment_method (category): método de pago
- device (category): dispositivo

## products_500.csv
- product_id (text)
- product_name (text)
- category (category)
- brand (category)
- active (Yes/No): producto activo
