# Changelog

Todos los cambios importantes de este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto sigue [Versionado Semántico](https://semver.org/lang/es/).

## [Unreleased]

### Agregado
- README bilingüe (español / inglés) con instalación, ejemplo de uso, formato del CSV y hoja de ruta.
- CSV de ejemplo en `examples/lotes_ejemplo.csv`.
- Guías de comunidad: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`.
- Plantillas de issues y de pull requests en `.github/`.

### Cambiado
- Docstrings de `src/lots.py` redactados de forma neutral (sin cambios de lógica).

## [0.1.0-alpha] - 2026-09-25

Primera versión pública, en etapa alfa.

### Agregado
- `Lot`: lote de semillas (id, especie, año de cosecha, viabilidad 0–1, gramos, origen opcional).
- `Tray`: bandeja de siembra (id, lote, fecha de siembra, celdas, germinadas).
- `SeedBank`: almacenamiento en memoria de lotes y bandejas, con `add_lot`, `sow`, `germ_rate` y `load_lots_csv`.
- Importación de lotes desde CSV (columnas `id`, `species`, `harvest_year`, `viability`, `grams`; salta filas sin id).
- Nota de hardware sugerido en `docs/HARDWARE_ANDROID.md`.
- Licencia MIT y `LEEME_LICENCIA.md`.
