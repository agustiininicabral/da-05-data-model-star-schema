# Data Model: Star Schema

Modelo dimensional reproducible para analizar ventas sintéticas con una tabla de hechos y dimensiones conformadas.

![Star schema CI](https://github.com/agustiininicabral/da-05-data-model-star-schema/actions/workflows/ci.yml/badge.svg)

## Modelo

La tabla `fact_sales` mantiene el grano de **una fila por pedido** y contiene claves foráneas a siete dimensiones:

- `dim_date`: calendario continuo con fecha, año, trimestre y mes.
- `dim_customer`: cliente.
- `dim_category`: categoría informada en la venta.
- `dim_channel`: canal atribuido.
- `dim_geography`: combinación país/ciudad.
- `dim_payment_method`: método de pago.
- `dim_device`: dispositivo.

El catálogo de 500 productos se conserva como fuente de referencia, pero no se crea una dimensión de producto relacionada con la tabla de hechos: `sales.csv` no incluye `product_id`. Inventar esa relación produciría atribuciones falsas.

## Dataset

- `02-data/raw/sales.csv`: 3.500 pedidos entre 2024-01-01 y 2025-12-31.
- `02-data/raw/products.csv`: 500 productos.
- `02-data/raw/DATA_DICTIONARY.md`: columnas y limitaciones.

Los datos e importes son sintéticos, no representan una empresa ni una moneda real.

## Ejecutar en Windows PowerShell

Requiere Python 3.12. Desde la raíz del repositorio:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python scripts/build_star_schema.py
python -m pytest -q
ruff format --check scripts tests
ruff check scripts tests
```

El script carga los CSV a una base SQLite temporal en memoria, construye dimensiones y hechos a partir de `03-work/sql/01_core_queries.sql`, y verifica que las métricas y el grano coincidan con la fuente. No crea una base persistente ni modifica los CSV originales.

GitHub Actions ejecuta las mismas pruebas y validaciones en cada push y pull request.

## Validaciones automáticas

- 3.500 filas de ventas y 3.500 filas en `fact_sales`.
- Un `order_id` distinto por fila de hechos.
- Ingresos y costos iguales a los de la fuente.
- Integridad de claves foráneas.
- Sin categorías de ventas ausentes en el catálogo.
- Dimensión calendario completa para el rango de fechas.

## Resultados

Ver [05-results/report.md](05-results/report.md) para los KPIs, el diagrama lógico, decisiones de granularidad y limitaciones.

## Estructura

- `01-requirements/`: alcance e hipótesis.
- `02-data/raw/`: fuentes originales y diccionario.
- `03-work/sql/01_core_queries.sql`: DDL, dimensiones y carga de hechos.
- `scripts/build_star_schema.py`: construcción y validación.
- `tests/test_star_schema.py`: pruebas de grano, métricas e integridad.
- `05-results/report.md`: resultados y recomendaciones.

## Licencia

MIT.
