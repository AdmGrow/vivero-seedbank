"""Herramienta de consola ``seedbank``.

Ejemplos::

    seedbank import examples/lotes_ejemplo.csv
    seedbank list
    seedbank sembrar EJ-002 --celdas 72 --fecha 2026-09-01
    seedbank germinacion B001 --germinadas 60
    seedbank informe

El archivo de datos por defecto es ``seedbank.db`` en la carpeta actual; se puede
cambiar con ``--db RUTA`` o con la variable de entorno ``SEEDBANK_DB``.
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from datetime import date

from . import __version__
from .lots import NotFoundError, SeedBank, Tray, ValidationError
from .storage import DEFAULT_DB, load_bank, save_bank


class _SpanishHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = "uso: "
        return super().add_usage(usage, actions, groups, prefix)


class _SpanishArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("formatter_class", _SpanishHelpFormatter)
        kwargs["add_help"] = False
        super().__init__(*args, **kwargs)
        self._positionals.title = "argumentos"
        self._optionals.title = "opciones"
        self.add_argument("-h", "--help", action="help", help="mostrar esta ayuda y salir")

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: error: {message}\n")


def _int(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{text}' no es un número entero") from None
    return value


def _iso_date(text: str) -> date:
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"fecha inválida '{text}'; usá el formato AAAA-MM-DD, por ejemplo 2026-09-01"
        ) from None


def _table(headers: list[str], rows: list[list[str]]) -> str:
    widths = [len(h) for h in headers]
    for row in rows:
        widths = [max(w, len(c)) for w, c in zip(widths, row)]
    def fmt(cells: list[str]) -> str:
        return "  ".join(c.ljust(w) for c, w in zip(cells, widths)).rstrip()

    return "\n".join([fmt(headers), fmt(["-" * w for w in widths]), *(fmt(r) for r in rows)])


def _pct(value: float | None) -> str:
    return "—" if value is None else f"{value * 100:.1f} %"


def _grams(value: float) -> str:
    return f"{value:g}"


# --- comandos -----------------------------------------------------------------


def cmd_import(args, bank: SeedBank) -> bool:
    n = bank.load_lots_csv(args.csv, replace=args.reemplazar)
    print(f"Importados {n} lotes desde {args.csv}. Total en el banco: {len(bank.lots)} lotes.")
    return True


def cmd_list(args, bank: SeedBank) -> bool:
    if not bank.lots:
        print("El banco está vacío. Importá lotes con: seedbank import archivo.csv")
        return False
    rows = [
        [lot.id, lot.species, str(lot.harvest_year), _pct(lot.viability), _grams(lot.grams), lot.origin or "—"]
        for lot in sorted(bank.lots.values(), key=lambda lot: lot.id)
    ]
    print(f"Lotes ({len(rows)}):")
    print(_table(["ID", "Especie", "Año", "Viabilidad", "Gramos", "Origen"], rows))
    if bank.trays:
        trays = sorted(bank.trays.values(), key=lambda t: t.id)
        print(f"\nBandejas ({len(trays)}):")
        print(
            _table(
                ["ID", "Lote", "Siembra", "Celdas", "Germinadas", "Germinación"],
                [
                    [t.id, t.lot_id, t.sown.isoformat(), str(t.cells), str(t.germinated), _pct(bank.germ_rate(t.id))]
                    for t in trays
                ],
            )
        )
    return False


def cmd_sembrar(args, bank: SeedBank) -> bool:
    bank.get_lot(args.lot_id)  # error claro si no existe
    tray_id = args.id or bank.next_tray_id()
    tray = Tray(tray_id, args.lot_id, args.fecha or date.today(), args.celdas, args.germinadas)
    bank.sow(tray)
    print(
        f"Bandeja {tray.id} sembrada con el lote {tray.lot_id}: "
        f"{tray.cells} celdas, fecha {tray.sown.isoformat()}."
    )
    return True


def cmd_germinacion(args, bank: SeedBank) -> bool:
    tray = bank.record_germination(args.tray_id, args.germinadas)
    print(
        f"Bandeja {tray.id} (lote {tray.lot_id}): {tray.germinated} de {tray.cells} celdas "
        f"germinaron ({_pct(bank.germ_rate(tray.id))})."
    )
    return True


def cmd_informe(args, bank: SeedBank) -> bool:
    report = bank.lot_report()
    if not report:
        print("El banco está vacío. Importá lotes con: seedbank import archivo.csv")
        return False
    rows = []
    for s in report:
        diff = "—" if s.germ_rate is None else f"{(s.germ_rate - s.lot.viability) * 100:+.1f} pts"
        rows.append(
            [
                s.lot.id,
                s.lot.species,
                _pct(s.lot.viability),
                str(s.trays),
                str(s.cells),
                str(s.germinated),
                _pct(s.germ_rate),
                diff,
            ]
        )
    print("Informe de germinación por lote:")
    print(
        _table(
            ["Lote", "Especie", "Viab. declarada", "Bandejas", "Celdas", "Germinadas", "Germinación", "Diferencia"],
            rows,
        )
    )
    total_cells = sum(s.cells for s in report)
    total_germ = sum(s.germinated for s in report)
    if total_cells:
        print(f"\nTotal: {total_germ} de {total_cells} celdas germinaron ({_pct(total_germ / total_cells)}).")
    return False


# --- parser -------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    db_default = os.environ.get("SEEDBANK_DB", DEFAULT_DB)
    # --db también se acepta después del subcomando (sin pisar el valor global)
    db_parent = argparse.ArgumentParser(add_help=False)
    db_parent.add_argument("--db", default=argparse.SUPPRESS, metavar="RUTA", help="archivo SQLite de datos")

    parser = _SpanishArgumentParser(
        prog="seedbank",
        description=(
            "Banco de semillas abierto: registrá lotes, viabilidad y bandejas de germinación.\n"
            f"Los datos se guardan en un archivo SQLite (por defecto: {DEFAULT_DB})."
        ),
    )
    parser.add_argument(
        "--db",
        default=db_default,
        metavar="RUTA",
        help=f"archivo SQLite de datos (por defecto: {db_default}; también con la variable SEEDBANK_DB)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}", help="mostrar la versión")

    sub = parser.add_subparsers(dest="command", title="comandos", metavar="COMANDO")
    sub.required = True

    p = sub.add_parser(
        "import", parents=[db_parent], help="importar lotes desde un archivo CSV",
        description="Importa lotes desde un CSV con columnas id, species, harvest_year, viability, grams\n"
        "(y opcionalmente origin). Separador , o ;. La viabilidad puede ser 0.85 o 85%.\n"
        "Si una fila es inválida no se importa nada y se indica el número de fila.",
    )
    p.add_argument("csv", help="ruta del archivo CSV")
    p.add_argument("--reemplazar", action="store_true", help="reemplazar lotes que ya existen con el mismo id")
    p.set_defaults(func=cmd_import)

    p = sub.add_parser("list", parents=[db_parent], help="listar lotes y bandejas",
                       description="Muestra los lotes y las bandejas registradas.")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("sembrar", parents=[db_parent], help="registrar una bandeja sembrada con un lote",
                       description="Registra una bandeja de siembra hecha con un lote existente.")
    p.add_argument("lot_id", help="id del lote que se siembra (por ejemplo EJ-002)")
    p.add_argument("--celdas", type=_int, required=True, help="cantidad de celdas de la bandeja")
    p.add_argument("--fecha", type=_iso_date, help="fecha de siembra AAAA-MM-DD (por defecto: hoy)")
    p.add_argument("--id", help="id de la bandeja (por defecto se genera: B001, B002, ...)")
    p.add_argument("--germinadas", type=_int, default=0, help="celdas ya germinadas (por defecto: 0)")
    p.set_defaults(func=cmd_sembrar)

    p = sub.add_parser("germinacion", parents=[db_parent], help="anotar cuántas celdas germinaron en una bandeja",
                       description="Actualiza la cantidad de celdas germinadas de una bandeja y muestra el porcentaje.")
    p.add_argument("tray_id", help="id de la bandeja (por ejemplo B001)")
    p.add_argument("--germinadas", type=_int, required=True, help="cantidad de celdas germinadas")
    p.set_defaults(func=cmd_germinacion)

    p = sub.add_parser("informe", parents=[db_parent], help="resumen de germinación por lote",
                       description="Resumen por lote: bandejas, celdas, germinadas, germinación real "
                       "y diferencia con la viabilidad declarada.")
    p.set_defaults(func=cmd_informe)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        bank = load_bank(args.db)
        changed = args.func(args, bank)
        if changed:
            save_bank(bank, args.db)
    except (ValidationError, NotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"Error: no se encontró el archivo {e.filename}", file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        print("Error: el archivo no está en UTF-8. Guardalo como 'CSV UTF-8' e intentá de nuevo.", file=sys.stderr)
        return 1
    except sqlite3.Error as e:
        print(f"Error en la base de datos {args.db}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
