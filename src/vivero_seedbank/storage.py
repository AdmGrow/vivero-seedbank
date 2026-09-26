"""Persistencia del banco en SQLite (solo biblioteca estándar).

El archivo por defecto es ``seedbank.db``. ``save_bank`` reemplaza el contenido
del archivo por el estado actual del banco, dentro de una transacción.
"""
from __future__ import annotations

import os
import sqlite3
from datetime import date

from .lots import Lot, SeedBank, Tray, ValidationError

DEFAULT_DB = "seedbank.db"
SCHEMA_VERSION = 1

_SCHEMA = """
CREATE TABLE IF NOT EXISTS lots (
    id           TEXT PRIMARY KEY,
    species      TEXT NOT NULL,
    harvest_year INTEGER NOT NULL,
    viability    REAL NOT NULL CHECK (viability BETWEEN 0 AND 1),
    grams        REAL NOT NULL CHECK (grams >= 0),
    origin       TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS trays (
    id         TEXT PRIMARY KEY,
    lot_id     TEXT NOT NULL REFERENCES lots(id),
    sown       TEXT NOT NULL,
    cells      INTEGER NOT NULL CHECK (cells > 0),
    germinated INTEGER NOT NULL DEFAULT 0 CHECK (germinated >= 0 AND germinated <= cells)
);
"""


def _connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version > SCHEMA_VERSION:
        raise ValidationError(
            f"La base de datos usa un formato más nuevo (versión {version}) que esta versión "
            f"del programa (versión {SCHEMA_VERSION}). Actualizá vivero-seedbank."
        )
    conn.executescript(_SCHEMA)
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")


def save_bank(bank: SeedBank, path: str = DEFAULT_DB) -> None:
    """Guarda todos los lotes y bandejas del banco en ``path``."""
    conn = _connect(path)
    try:
        _ensure_schema(conn)
        with conn:  # transacción: o se guarda todo o nada
            conn.execute("DELETE FROM trays")
            conn.execute("DELETE FROM lots")
            conn.executemany(
                "INSERT INTO lots (id, species, harvest_year, viability, grams, origin) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (lot.id, lot.species, lot.harvest_year, lot.viability, lot.grams, lot.origin)
                    for lot in bank.lots.values()
                ],
            )
            conn.executemany(
                "INSERT INTO trays (id, lot_id, sown, cells, germinated) VALUES (?, ?, ?, ?, ?)",
                [
                    (t.id, t.lot_id, t.sown.isoformat(), t.cells, t.germinated)
                    for t in bank.trays.values()
                ],
            )
    finally:
        conn.close()


def load_bank(path: str = DEFAULT_DB) -> SeedBank:
    """Carga un banco desde ``path``. Si el archivo no existe devuelve un banco vacío."""
    bank = SeedBank()
    if not os.path.exists(path):
        return bank
    conn = _connect(path)
    try:
        _ensure_schema(conn)
        for row in conn.execute(
            "SELECT id, species, harvest_year, viability, grams, origin FROM lots ORDER BY id"
        ):
            bank.add_lot(Lot(*row))
        for tray_id, lot_id, sown, cells, germinated in conn.execute(
            "SELECT id, lot_id, sown, cells, germinated FROM trays ORDER BY id"
        ):
            bank.sow(Tray(tray_id, lot_id, date.fromisoformat(sown), cells, germinated))
    finally:
        conn.close()
    return bank
