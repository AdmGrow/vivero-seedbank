# Vivero Seedbank — Banco de semillas abierto

**Estado: alfa / etapa temprana — buscamos colaboradores**

[![tests](https://github.com/AdmGrow/vivero-seedbank/actions/workflows/tests.yml/badge.svg)](https://github.com/AdmGrow/vivero-seedbank/actions/workflows/tests.yml) ![Licencia: MIT](https://img.shields.io/badge/licencia-MIT-green) ![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue) ![Estado: alfa](https://img.shields.io/badge/estado-alfa-orange)

[Español](#español) · [English](#english)

---

## Español

### Qué es

Vivero Seedbank es un proyecto de software libre para registrar **lotes de semillas**, su **viabilidad** y las **bandejas de siembra** que se hacen a partir de ellos, y comparar la germinación real con la viabilidad declarada de cada lote.

Funciona como **herramienta de consola** (`seedbank`) y como **librería de Python**. Los datos se guardan en un archivo **SQLite** local. No necesita internet ni dependencias externas.

### Para quién podría servir

Algunos usos posibles (no son usuarios actuales, son ejemplos de a quién apunta el proyecto):

- Huertas comunitarias
- Escuelas con huerta
- Viveros chicos
- Bancos de semillas nativas

### Qué hace hoy

- **Lotes**: id, especie, año de cosecha, viabilidad (0 a 1), gramos y origen (opcional).
- **Bandejas**: lote de origen, fecha de siembra, celdas y cuántas germinaron.
- **Validaciones** con mensajes claros en español: viabilidad entre 0 y 1, gramos no negativos, año de cosecha entre 1900 y el año próximo, celdas mayores que 0, germinadas no mayores que las celdas, ids repetidos.
- **Importación desde CSV** (compatible con Excel): separador `,` o `;`, viabilidad como `0.85` o `85%`, errores con número de fila. Si una fila está mal, no se importa nada.
- **Guardado en SQLite** (archivo `seedbank.db` por defecto).
- **Informe de germinación por lote**: germinación real vs. viabilidad declarada.

### Instalación

Requisitos: **Python 3.10 o superior**. No hay dependencias externas.

```bash
git clone https://github.com/AdmGrow/vivero-seedbank.git
cd vivero-seedbank
python -m venv .venv
source .venv/bin/activate      # en Windows: .venv\Scripts\activate
pip install -e .
```

Esto instala el comando `seedbank`. También se puede usar `python -m vivero_seedbank`.

### Uso de la consola

Con el CSV de ejemplo [`examples/lotes_ejemplo.csv`](examples/lotes_ejemplo.csv):

```bash
seedbank import examples/lotes_ejemplo.csv                 # importar lotes
seedbank list                                              # ver lotes y bandejas
seedbank sembrar EJ-002 --celdas 72 --fecha 2026-09-01     # registrar una bandeja (id automático: B001)
seedbank germinacion B001 --germinadas 60                  # anotar cuántas germinaron
seedbank informe                                           # resumen por lote
```

Salida real del informe:

```text
Informe de germinación por lote:
Lote    Especie                        Viab. declarada  Bandejas  Celdas  Germinadas  Germinación  Diferencia
------  -----------------------------  ---------------  --------  ------  ----------  -----------  ----------
EJ-001  Cebolla (Allium cepa)          85.0 %           0         0       0           —            —
EJ-002  Tomate (Solanum lycopersicum)  92.0 %           1         72      60          83.3 %       -8.7 pts
...
Total: 60 de 72 celdas germinaron (83.3 %).
```

Opciones útiles:

| Opción | Para qué |
|---|---|
| `--db RUTA` | Usar otro archivo de datos (por defecto `seedbank.db` en la carpeta actual). También con la variable `SEEDBANK_DB`. |
| `import ... --reemplazar` | Actualizar lotes que ya existen con el mismo id. |
| `sembrar ... --id ID` | Elegir el id de la bandeja en vez de B001, B002... |
| `sembrar ... --fecha AAAA-MM-DD` | Fecha de siembra (por defecto, hoy). |
| `seedbank COMANDO --help` | Ayuda de cada comando. |

> El archivo `seedbank.db` es tuyo: no lo subas al repositorio (ya está en `.gitignore`).

### Uso como librería

```python
from datetime import date
from vivero_seedbank import SeedBank, Tray

banco = SeedBank()
banco.load_lots_csv("examples/lotes_ejemplo.csv")
banco.sow(Tray(id="B1", lot_id="EJ-002", sown=date(2026, 9, 1), cells=72, germinated=60))
print(f"{banco.germ_rate('B1'):.0%}")  # 83%
banco.save_sqlite("seedbank.db")
```

### Formato del CSV

La primera fila tiene que tener estos nombres de columna (no importan mayúsculas):

| Columna        | Qué es                         | Ejemplo                        |
|----------------|--------------------------------|--------------------------------|
| `id`           | Código único del lote          | `EJ-001`                       |
| `species`      | Especie o variedad             | `Cebolla (Allium cepa)`        |
| `harvest_year` | Año de cosecha (número entero) | `2025`                         |
| `viability`    | Viabilidad                     | `0.85` o `85%`                 |
| `grams`        | Cantidad en gramos             | `40`                           |
| `origin`       | Origen (opcional)              | `Intercambio huerta escolar`   |

Notas: el separador puede ser `,` o `;` (Excel en español suele usar `;`, y ahí se acepta coma decimal: `0,85`). Guardá el archivo como **CSV UTF-8**. Las filas sin `id` se saltan. Los datos del archivo de ejemplo son inventados.

### Tests

```bash
pip install -e ".[dev]"
python -m pytest
```

Los tests corren automáticamente en GitHub Actions con Python 3.10, 3.11, 3.12 y 3.13.

### Hoja de ruta

1. ~~Tests automáticos~~, ~~validaciones~~, ~~persistencia SQLite~~, ~~herramienta de consola~~ (0.1.0a1).
2. Exportar informes a CSV.
3. Control de stock: descontar gramos al sembrar.
4. Etiquetas con código QR por lote (ver [`docs/HARDWARE_ANDROID.md`](docs/HARDWARE_ANDROID.md)).
5. Más adelante, interfaz web.

Ver también [`CHANGELOG.md`](CHANGELOG.md).

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

Vivero Seedbank is an open-source tool to record **seed lots**, their **viability**, and the **sowing trays** made from them, and to compare real germination with each lot's declared viability. It ships a **command-line tool** (`seedbank`) and a **Python library**, storing data in a local **SQLite** file. No internet or external dependencies required.

### Who it could serve

Possible uses (examples, not current users): community gardens, school gardens, small nurseries, native seed banks.

### Features

- Lots (id, species, harvest year, viability 0–1, grams, optional origin) and trays (lot, sowing date, cells, germinated).
- Validation with clear (Spanish) error messages: viability 0–1, non-negative grams, harvest year 1900..next year, cells > 0, germinated ≤ cells, duplicate ids.
- CSV import (Excel-friendly): `,` or `;` delimiter, viability as `0.85` or `85%`, row-numbered errors, all-or-nothing.
- SQLite persistence (`seedbank.db` by default) and a per-lot germination report.

### Install

Requires **Python 3.10+**.

```bash
git clone https://github.com/AdmGrow/vivero-seedbank.git
cd vivero-seedbank
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

### Usage

```bash
seedbank import examples/lotes_ejemplo.csv
seedbank list
seedbank sembrar EJ-002 --celdas 72 --fecha 2026-09-01   # "sembrar" = sow a tray
seedbank germinacion B001 --germinadas 60                # record germinated cells
seedbank informe                                         # per-lot germination report
```

Use `--db PATH` (or `SEEDBANK_DB`) to choose the data file. CSV columns: `id`, `species`, `harvest_year`, `viability`, `grams`, optional `origin`. Run the tests with `pip install -e ".[dev]"` and `python -m pytest`.

### Roadmap

Done in 0.1.0a1: tests, validation, SQLite, CLI. Next: CSV report export → stock tracking (grams used when sowing) → QR labels → web UI later.

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
