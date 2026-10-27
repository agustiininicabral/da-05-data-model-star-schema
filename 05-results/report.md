# Reporte — Data Model: Star Schema

## Objetivo

Diseñar un modelo dimensional que permita filtrar y agregar ventas por fecha, cliente, categoría, canal, geografía, método de pago y dispositivo, manteniendo el grano de la fuente y la consistencia de las métricas.

## Modelo lógico

```text
dim_date ─────────────┐
dim_customer ─────────┤
dim_category ─────────┤
dim_channel ──────────┤
dim_geography ────────┼── fact_sales
dim_payment_method ───┤
dim_device ───────────┘
```

Cada dimensión tiene una clave sustituta y la tabla de hechos guarda las claves foráneas junto con las medidas. `fact_sales` contiene una fila por `order_id`.

## Métricas verificadas

| KPI | Resultado |
|---|---:|
| Filas de ventas fuente | 3.500 |
| Filas en fact_sales | 3.500 |
| Clientes únicos | 877 |
| Productos de catálogo | 500 |
| Fechas de calendario | 731 |
| Ingresos netos | 608.810,14 |
| Costo estimado | 364.075,27 |
| Margen bruto estimado | 244.734,87 |
| Margen sobre ingresos | 40,20% |

## Decisiones de modelado

1. **Grano explícito:** una fila representa un pedido. `order_id` se mantiene único en la tabla de hechos.
2. **Claves sustitutas:** las dimensiones utilizan claves enteras, separando las relaciones analíticas de los identificadores de origen.
3. **Calendario continuo:** `dim_date` incluye cada día entre la fecha mínima y máxima, incluso si no hubo pedidos ese día.
4. **Geografía compuesta:** la dimensión se identifica por país y ciudad, porque una ciudad puede repetirse entre países.
5. **Producto fuera del hecho:** las ventas no contienen `product_id`. El catálogo no puede conectarse de forma válida a nivel de SKU; se conserva como referencia y se valida la cobertura de categorías.
6. **Medidas auditables:** ingresos y costos se comparan con los CSV fuente para evitar duplicación o pérdida de registros durante la transformación.

## Hallazgos de negocio del dataset sintético

- Infantil es la categoría con mayores ingresos (105.711,81; 17,36%), seguida por OTC (104.438,16) y Perfumería (103.784,47).
- Paid Social registra 95.217,15 en ingresos, seguido de cerca por Email con 94.856,04.
- El margen bruto estimado es 40,20%, pero no incluye gastos operativos ni costos de adquisición.
- Los ingresos están casi equilibrados entre 2024 (304.482,45) y 2025 (304.327,69), con una variación aproximada de -0,05%.

## Calidad y reproducibilidad

El script reconstruye el modelo en SQLite en memoria y verifica automáticamente:

- Igualdad entre filas de ventas y hechos.
- Unicidad del pedido en el hecho.
- Paridad de ingresos y costos.
- Integridad de claves foráneas.
- Cobertura de categorías de ventas en el catálogo.
- Cardinalidad esperada de calendario y dimensiones principales.

## Recomendaciones

- Añadir `product_id` al origen de ventas o una tabla de líneas de pedido para permitir análisis por producto.
- Si un pedido puede incluir varios productos, cambiar el grano de la tabla de hechos a una fila por línea de pedido y mantener una dimensión de pedido si hace falta.
- Definir moneda, devoluciones, impuestos y política de reconocimiento de ingresos antes de usar el modelo con datos reales.
- Añadir tests para nuevas columnas, valores nulos y cambios de esquema.

## Limitaciones

- Los datos son ficticios y no representan una empresa real.
- El catálogo no tiene relación por producto con las ventas; solo se valida la cobertura por categoría.
- El costo es estimado y el margen no equivale a beneficio neto.
- La base SQLite es temporal para demostración y pruebas; no es un servicio de producción.
