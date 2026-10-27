# Data Model: Star Schema

Modelo dimensional para análisis de ventas con una tabla de hechos y siete dimensiones, construido en SQLite a partir de los CSV sintéticos del repositorio.

![Star schema CI](https://github.com/agustiininicabral/da-05-data-model-star-schema/actions/workflows/ci.yml/badge.svg)

## Dataset y granularidad

- `02-data/raw/sales.csv`: 3.500 pedidos; cada fila es un pedido único.
- `02-data/raw/products.csv`: catálogo de 500 productos.
- `02-data/raw/DATA_DICTIONARY.md`: columnas y limitaciones.

Los datos son ficticios. El archivo de ventas no incluye `product_id`; por eso no se crea una dimensión de producto conectada a la tabla de hechos. El catálogo se conserva como referencia independiente hasta que exista una clave de producto en ventas.

## Instalación (Windows PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

## Construir el modelo y ejecutar consultas

```powershell
python scripts/build_star_schema.py
python scripts/run_queries.py
```

El generador valida IDs, fechas, cantidades, descuentos, importes y coherencia de ingresos netos antes de construir la base. El archivo generado es `data/warehouse.db`, excluido de Git.

## Modelo

```text
                    dim_date
                       |
dim_customer -- fact_sales -- dim_channel
                       |
dim_category -- fact_sales -- dim_geography
                       |
             dim_payment_method
                       |
                   dim_device
```

- `fact_sales`: una fila por `order_id`, con cantidad, precio, descuento, ingreso neto, costo y margen.
- Dimensiones: fecha, cliente, canal, categoría, geografía de la transacción, método de pago y dispositivo.
- Claves: surrogate keys enteras para dimensiones y claves foráneas en la tabla de hechos.
- Restricciones: IDs únicos, claves foráneas, cantidad positiva, descuento entre 0 y 20%, ingresos coherentes con la fórmula y margen consistente con ingresos menos costo.

## Consultas incluidas

Las consultas en `03-work/sql/02_star_schema_queries.sql` cubren ingresos mensuales, margen por canal, ingresos por categoría, top geográfico, top clientes, mix de pago/dispositivo, acumulado mensual y conciliación del grano de la tabla de hechos.

## Pruebas y calidad

```powershell
python -m pip check
ruff format --check scripts tests
ruff check scripts tests
python -m pytest -q
```

Las pruebas validan el recuento de dimensiones/hechos, claves foráneas, reconciliación de ingresos y ejecución de las ocho consultas. GitHub Actions publica la base SQLite generada como artefacto temporal.

## Limitaciones

- Dataset sintético; importes en unidades monetarias no asociadas a una moneda real.
- No hay `product_id` en ventas, por lo que el catálogo no puede conectarse de forma segura al hecho a nivel de producto.
- `dim_customer` solo contiene el identificador, porque el dataset no ofrece atributos de cliente estables.
- El margen es una aproximación y no equivale a beneficio neto.

## Licencia

MIT.
