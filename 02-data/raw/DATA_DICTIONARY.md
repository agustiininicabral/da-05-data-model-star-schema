# Data Dictionary

## sales.csv — 3.500 registros

Una fila representa un pedido.

- `order_id` (text): identificador único del pedido.
- `customer_id` (text): identificador del cliente.
- `order_date` (date): fecha de compra en formato ISO.
- `category` (category): categoría informada en la venta.
- `channel` (category): canal atribuido.
- `country` (category): país.
- `city` (text): ciudad.
- `quantity` (int): unidades vendidas.
- `unit_price` (decimal): precio unitario.
- `discount_rate` (decimal): descuento entre 0 y 0,20.
- `net_revenue` (decimal): ingresos netos.
- `cost` (decimal): costo estimado.
- `payment_method` (category): método de pago.
- `device` (category): dispositivo.

## products.csv — 500 registros

- `product_id` (text): identificador único del producto.
- `product_name` (text): nombre del producto.
- `category` (category): categoría de catálogo.
- `brand` (category): marca ficticia.
- `active` (Yes/No): estado del producto.

## Relaciones y limitaciones

- `order_id` es la clave natural del pedido en la fuente.
- `sales.csv` no contiene `product_id`, por lo que no se puede crear una relación válida venta-producto a nivel de SKU.
- Las ventas y el catálogo se pueden comparar por categoría, pero no atribuir cada pedido a un producto concreto.
- Todos los importes son sintéticos.
