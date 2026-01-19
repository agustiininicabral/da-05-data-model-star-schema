# Data Model: Star Schema

## Objetivo
Diseño de modelo estrella, tablas dimensión/hechos y claves.

## Contexto
Proyecto de portfolio Data Analytics con dataset ficticio de ventas (3.500 filas) y catálogo de productos. El foco es reproducibilidad y storytelling.

## Alcance
- Preparación de datos
- Análisis exploratorio
- KPIs e insights
- Reporte final

## Fuera de alcance
- Modelos predictivos complejos
- Machine Learning en producción
- Infraestructura cloud

## Herramientas
- Excel / Power Query (pasos documentados)
- SQL (scripts)
- Power BI (notas y layout)
- Markdown para documentación

## Entregables
- Dataset (raw + processed)
- Data Dictionary
- SQL scripts
- Reporte final con insights
- Evidencia (capturas/exports)

## Cómo reproducir
1) Copiar datasets desde `_shared_datasets/` a `02-data/raw/`.
2) Ejecutar SQL en `03-work/sql/` (o adaptar a tu motor).
3) Documentar transformaciones en `02-data/processed/`.
4) Completar `05-results/report.md` con KPIs e insights.

## Evidencia
- Ver carpeta `04-evidence/` (capturas, exports, logs).

## Resultados
- Ver `05-results/report.md`.

## Próximos pasos
- Publicar dashboard (Power BI) con capturas en `04-evidence/`
- Agregar README con link a demo / pbix
- Crear data model estrella en repo 05 y reutilizar
