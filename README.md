# Vivero Seedbank — Banco de semillas abierto

**Estado: alfa / etapa temprana — buscamos colaboradores**

![Licencia: MIT](https://img.shields.io/badge/licencia-MIT-green) ![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue) ![Estado: alfa](https://img.shields.io/badge/estado-alfa-orange)

[Español](#español) · [English](#english)

---

## Español

### Qué es

Vivero Seedbank es un proyecto de software libre para registrar **lotes de semillas**, su **viabilidad** y las **bandejas de siembra** que se hacen a partir de ellos. La idea es ofrecer una herramienta simple y abierta para llevar el inventario de un banco de semillas o de un vivero.

Hoy es una **librería mínima en Python**: todavía no tiene interfaz de línea de comandos, ni web, ni guarda los datos en disco.

### Para quién podría servir

Algunos usos posibles (no son usuarios actuales, son ejemplos de a quién apunta el proyecto):

- Huertas comunitarias
- Escuelas con huerta
- Viveros chicos
- Bancos de semillas nativas

### Qué hace hoy

Todo está en [`src/lots.py`](src/lots.py):

- **`Lot`** — un lote de semillas: `id`, `species` (especie), `harvest_year` (año de cosecha), `viability` (viabilidad, de 0 a 1), `grams` (gramos) y `origin` (origen, opcional).
- **`Tray`** — una bandeja de siembra: `id`, `lot_id` (lote de origen), `sown` (fecha de siembra), `cells` (celdas) y `germinated` (celdas germinadas).
- **`SeedBank`** — el banco, que guarda lotes y bandejas **en memoria**:
  - `add_lot(lot)` agrega un lote (rechaza viabilidad fuera de 0–1).
  - `sow(tray)` registra una bandeja (el lote tiene que existir).
  - `germ_rate(tray_id)` calcula el porcentaje de germinación de una bandeja (germinadas / celdas).
  - `load_lots_csv(path)` importa lotes desde un archivo CSV.

### Instalación

Requisitos: **Python 3.10 o superior**. No hay dependencias externas.

```bash
git clone https://github.com/AdmGrow/vivero-seedbank.git
cd vivero-seedbank
```

### Ejemplo de uso

Desde la carpeta del repositorio, con el CSV de ejemplo [`examples/lotes_ejemplo.csv`](examples/lotes_ejemplo.csv):

```python
import sys
from datetime import date

sys.path.insert(0, "src")
from lots import SeedBank, Tray

banco = SeedBank()
banco.load_lots_csv("examples/lotes_ejemplo.csv")
print(list(banco.lots))  # ['EJ-001', 'EJ-002', 'EJ-003', 'EJ-004', 'EJ-005']

# Sembrar una bandeja de 72 celdas con el lote de tomate
banco.sow(Tray(id="B1", lot_id="EJ-002", sown=date(2026, 9, 1), cells=72, germinated=60))
print(f"{banco.germ_rate('B1'):.0%}")  # 83%
```

### Formato del CSV

La primera fila tiene que tener estos nombres de columna exactos:

| Columna        | Qué es                         | Ejemplo                        |
|----------------|--------------------------------|--------------------------------|
| `id`           | Código único del lote          | `EJ-001`                       |
| `species`      | Especie o variedad             | `Cebolla (Allium cepa)`        |
| `harvest_year` | Año de cosecha (número entero) | `2025`                         |
| `viability`    | Viabilidad de 0 a 1            | `0.85` (no `85%`)              |
| `grams`        | Cantidad en gramos             | `40`                           |

Notas: las filas sin `id` se saltan. La columna `origin` todavía no se lee desde el CSV. Los datos del archivo de ejemplo son inventados.

### Hoja de ruta

1. Tests automáticos.
2. Validaciones (germinadas no mayores que celdas, gramos no negativos, años posibles, ids repetidos, mensajes claros).
3. Persistencia de datos (SQLite o CSV).
4. Herramienta de línea de comandos (CLI).
5. Más adelante, interfaz web.

Ver también [`CHANGELOG.md`](CHANGELOG.md) y [`docs/HARDWARE_ANDROID.md`](docs/HARDWARE_ANDROID.md).

### Cómo participar

- Foro de discusión: <https://github.com/AdmGrow/vivero-seedbank/discussions>
- Reportar errores o proponer ideas: [issues](https://github.com/AdmGrow/vivero-seedbank/issues)
- Guía para contribuir: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Código de conducta: [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
- Seguridad: [`SECURITY.md`](SECURITY.md)

### Enlaces

- Blog: <https://vepa0.blogspot.com>
- Canal de YouTube "Vivero Experimental": <https://www.youtube.com/channel/UCTlQIttTgJ_8TjH45dZSjfg>

### Licencia

MIT — ver [`LICENSE`](LICENSE) y [`LEEME_LICENCIA.md`](LEEME_LICENCIA.md). Se entrega sin garantía.

### Autor

Lucas Baigorria / Vivero Experimental

---

## English

**Status: alpha / early stage — contributors welcome**

### What it is

Vivero Seedbank is an open-source project to record **seed lots**, their **viability**, and the **sowing trays** made from them. Today it is a **minimal Python library**: no CLI, no web UI, and data is kept in memory only.

### Who it could serve

Possible uses (examples, not current users): community gardens, school gardens, small nurseries, native seed banks.

### Current features

In [`src/lots.py`](src/lots.py):

- **`Lot`** — seed lot: `id`, `species`, `harvest_year`, `viability` (0–1), `grams`, optional `origin`.
- **`Tray`** — sowing tray: `id`, `lot_id`, `sown` (date), `cells`, `germinated`.
- **`SeedBank`** — in-memory store with `add_lot`, `sow`, `germ_rate` (germinated / cells) and `load_lots_csv`.

### Install

Requires **Python 3.10+**, no external dependencies.

```bash
git clone https://github.com/AdmGrow/vivero-seedbank.git
cd vivero-seedbank
```

### Usage

See the Spanish example above; it works as-is with [`examples/lotes_ejemplo.csv`](examples/lotes_ejemplo.csv). CSV columns (exact header names): `id`, `species`, `harvest_year`, `viability` (0–1, e.g. `0.85`), `grams`. Rows without `id` are skipped; `origin` is not read from CSV yet.

### Roadmap

Tests → validation → persistence (SQLite/CSV) → CLI → web UI later.

### Get involved

- Forum: <https://github.com/AdmGrow/vivero-seedbank/discussions>
- [Issues](https://github.com/AdmGrow/vivero-seedbank/issues) · [`CONTRIBUTING.md`](CONTRIBUTING.md) · [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) · [`SECURITY.md`](SECURITY.md)

### Links

- Blog: <https://vepa0.blogspot.com>
- YouTube channel "Vivero Experimental": <https://www.youtube.com/channel/UCTlQIttTgJ_8TjH45dZSjfg>

### License

MIT — see [`LICENSE`](LICENSE). Provided without warranty.

### Author

Lucas Baigorria / Vivero Experimental
