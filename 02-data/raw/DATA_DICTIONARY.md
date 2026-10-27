# Data Dictionary

## sales.csv — 3.500 pedidos
- `order_id` (text): identificador único de pedido y grano de la tabla de hechos.
- `customer_id` (text): identificador de cliente.
- `order_date` (date): fecha del pedido.
- `category` (category): categoría de la venta.
- `channel` (category): canal atribuido.
- `country` (category): país de la transacción.
- `city` (text): ciudad de la transacción.
- `quantity` (integer): unidades vendidas.
- `unit_price` (decimal): precio unitario.
- `discount_rate` (decimal): descuento entre 0 y 0,20.
- `net_revenue` (decimal): ingresos netos.
- `cost` (decimal): costo estimado.
- `payment_method` (category): método de pago.
- `device` (category): dispositivo.

## products.csv — 500 productos
- `product_id` (text): identificador único del producto.
- `product_name` (text): nombre.
- `category` (category): categoría del catálogo.
- `brand` (category): marca ficticia.
- `active` (Yes/No): estado del producto.

## Modelado

La tabla de ventas no contiene `product_id`; no se debe relacionar directamente el catálogo con el hecho por categoría a nivel de fila. El modelo actual usa `dim_category` y conserva el catálogo como fuente de referencia.
