# Reporte — Data Model: Star Schema

## Objetivo

Diseñar un modelo dimensional que preserve la granularidad de ventas y permita analizar KPIs mediante joins con dimensiones sin duplicar los importes.

## Granularidad y modelo

- **Grano de `fact_sales`:** una fila por `order_id`.
- **Hecho:** cantidad, precio unitario, descuento, ingresos netos, costo y margen estimado.
- **Dimensiones:** fecha, cliente, canal, categoría, geografía de transacción, método de pago y dispositivo.
- **Integridad:** claves primarias en dimensiones, claves foráneas en el hecho, restricciones de cantidad/descuento/importes y chequeo de claves foráneas en el pipeline.

No se crea `dim_product` relacionada con ventas porque `sales.csv` no contiene `product_id`. Unir por categoría al nivel de producto multiplicaría los importes y produciría resultados incorrectos.

## KPIs del dataset sintético

| KPI | Resultado |
|---|---:|
| Filas de hechos / pedidos | 3.500 |
| Clientes únicos | 877 |
| Categorías | 6 |
| Canales | 7 |
| Unidades vendidas | 10.602 |
| Ingresos netos | 608.810,14 |
| Costo estimado | 364.075,27 |
| Margen bruto estimado | 244.734,87 |
| Tasa de margen estimada | 40,20% |

## Insights

1. El total de ingresos del hecho coincide con la fuente: 608.810,14. Las pruebas automatizadas validan esta conciliación y que el número de pedidos distintos sea 3.500.
2. Infantil es la categoría de mayor ingreso (105.711,81; 17,36%), seguida de OTC (104.438,16; 17,16%) y Perfumería (103.784,47; 17,05%).
3. Paid Social registra 95.217,15, apenas por encima de Email con 94.856,04. La diferencia no prueba una ventaja de rentabilidad.
4. La tasa de margen estimada es 40,20%; no incluye gastos operativos ni de marketing.

## Recomendaciones

- Agregar `product_id` a cada venta para conectar la dimensión de producto y analizar unidades/productos vendidos.
- Si un pedido puede tener varios productos, separar `fact_orders` y `fact_order_items` para no confundir pedido con línea de producto.
- Añadir una tabla de cliente con atributos estables y definir la gestión de cambios de dimensiones si se incorporan datos reales.
- Validar medidas en Power BI contra los totales SQL para detectar duplicación por joins.

## Limitaciones

Los datos son sintéticos y no representan una empresa real. El costo es estimado y el margen no equivale a beneficio neto. La geografía describe la ubicación asociada al pedido, no una ubicación permanente del cliente.
