# Changelog

Todos los cambios importantes de este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto sigue [Versionado Semántico](https://semver.org/lang/es/).

## [Unreleased]

### Agregado
- Paquete instalable `vivero_seedbank` (`pip install -e .`) con `pyproject.toml`, versión 0.1.0a1.
- Herramienta de consola `seedbank` con los comandos `import`, `list`, `sembrar`, `germinacion` e `informe`, ayuda en español y opción `--db` / variable `SEEDBANK_DB` (#6).
- Guardado y carga del banco en SQLite (`seedbank.db` por defecto), solo con la biblioteca estándar (#5).
- Validaciones de datos con mensajes en español: viabilidad 0–1, gramos ≥ 0, año de cosecha entre 1900 y el año próximo, celdas > 0, germinadas ≤ celdas, ids repetidos (con reemplazo explícito) (#2).
- CSV: columna opcional `origin`, viabilidad como `0.85`, `85%` o `0,85`, separador `,` o `;`, archivos de Excel con BOM, errores con número de fila e importación todo-o-nada (#4, #1).
- Informe de germinación por lote (germinación real vs. viabilidad declarada).
- Suite de tests con pytest (#3) y CI en GitHub Actions para Python 3.10–3.13 (#7).
- README bilingüe (español / inglés) con instalación, ejemplo de uso, formato del CSV y hoja de ruta.
- CSV de ejemplo en `examples/lotes_ejemplo.csv`.
- Guías de comunidad: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`.
- Plantillas de issues y de pull requests en `.github/`.

### Cambiado
- `src/lots.py` pasa a `src/vivero_seedbank/lots.py`. Se importa con `from vivero_seedbank import SeedBank, Lot, Tray`.
- `load_lots_csv` ahora devuelve la cantidad de lotes cargados y, si faltan columnas o hay datos inválidos, lanza `ValidationError` (subclase de `ValueError`) en lugar de `KeyError`/`ValueError` genéricos.
- Buscar un lote o bandeja inexistente lanza `NotFoundError` (subclase de `KeyError`, compatible con el comportamiento anterior).
- Agregar un lote con un id existente ya no lo reemplaza en silencio: hay que usar `replace=True` / `--reemplazar`.

## [0.1.0-alpha] - 2026-09-25

Primera versión pública, en etapa alfa.

### Agregado
- `Lot`: lote de semillas (id, especie, año de cosecha, viabilidad 0–1, gramos, origen opcional).
- `Tray`: bandeja de siembra (id, lote, fecha de siembra, celdas, germinadas).
- `SeedBank`: almacenamiento en memoria de lotes y bandejas, con `add_lot`, `sow`, `germ_rate` y `load_lots_csv`.
- Importación de lotes desde CSV (columnas `id`, `species`, `harvest_year`, `viability`, `grams`; salta filas sin id).
- Nota de hardware sugerido en `docs/HARDWARE_ANDROID.md`.
- Licencia MIT y `LEEME_LICENCIA.md`.
