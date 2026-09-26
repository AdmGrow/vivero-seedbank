"""Modelo de datos de Vivero Seedbank: lotes de semillas, bandejas de siembra y banco.

Todas las validaciones lanzan :class:`ValidationError` (subclase de ``ValueError``)
con un mensaje claro en español. Buscar un lote o una bandeja que no existe lanza
:class:`NotFoundError` (subclase de ``KeyError``).
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date

MIN_HARVEST_YEAR = 1900

REQUIRED_CSV_COLUMNS = ("id", "species", "harvest_year", "viability", "grams")
OPTIONAL_CSV_COLUMNS = ("origin",)


class ValidationError(ValueError):
    """Dato inválido (mensaje en español)."""


class NotFoundError(KeyError):
    """Lote o bandeja inexistente (mensaje en español)."""

    def __str__(self) -> str:  # KeyError agrega comillas; mostramos el mensaje tal cual
        return str(self.args[0]) if self.args else ""


def max_harvest_year() -> int:
    """Año de cosecha máximo aceptado: el año actual + 1."""
    return date.today().year + 1


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


@dataclass
class Lot:
    """Lote de semillas."""

    id: str
    species: str
    harvest_year: int
    viability: float  # 0 a 1
    grams: float
    origin: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValidationError("El lote necesita un id (no puede estar vacío).")
        self.id = self.id.strip()
        name = f"Lote {self.id}"
        if not isinstance(self.species, str) or not self.species.strip():
            raise ValidationError(f"{name}: la especie no puede estar vacía.")
        self.species = self.species.strip()
        top = max_harvest_year()
        if not _is_int(self.harvest_year) or not MIN_HARVEST_YEAR <= self.harvest_year <= top:
            raise ValidationError(
                f"{name}: año de cosecha inválido ({self.harvest_year!r}). "
                f"Tiene que ser un año entero entre {MIN_HARVEST_YEAR} y {top}."
            )
        if not _is_number(self.viability) or not 0 <= self.viability <= 1:
            raise ValidationError(
                f"{name}: viabilidad inválida ({self.viability!r}). "
                "Tiene que ser un número entre 0 y 1 (por ejemplo 0.85)."
            )
        self.viability = float(self.viability)
        if not _is_number(self.grams) or self.grams < 0:
            raise ValidationError(
                f"{name}: los gramos no pueden ser negativos ni estar vacíos (valor: {self.grams!r})."
            )
        self.grams = float(self.grams)
        self.origin = (self.origin or "").strip() if isinstance(self.origin, str) else ""


@dataclass
class Tray:
    """Bandeja de siembra hecha a partir de un lote."""

    id: str
    lot_id: str
    sown: date
    cells: int
    germinated: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValidationError("La bandeja necesita un id (no puede estar vacío).")
        self.id = self.id.strip()
        name = f"Bandeja {self.id}"
        if not isinstance(self.lot_id, str) or not self.lot_id.strip():
            raise ValidationError(f"{name}: falta el id del lote.")
        self.lot_id = self.lot_id.strip()
        if not isinstance(self.sown, date):
            raise ValidationError(f"{name}: la fecha de siembra tiene que ser una fecha (date).")
        if not _is_int(self.cells) or self.cells <= 0:
            raise ValidationError(
                f"{name}: la cantidad de celdas tiene que ser un entero mayor que 0 (valor: {self.cells!r})."
            )
        _check_germinated(self.id, self.germinated, self.cells)


def _check_germinated(tray_id: str, germinated: object, cells: int) -> None:
    if not _is_int(germinated) or germinated < 0:
        raise ValidationError(
            f"Bandeja {tray_id}: las germinadas tienen que ser un entero mayor o igual a 0 "
            f"(valor: {germinated!r})."
        )
    if germinated > cells:
        raise ValidationError(
            f"Bandeja {tray_id}: no puede haber más germinadas ({germinated}) que celdas ({cells})."
        )


@dataclass(frozen=True)
class LotSummary:
    """Resumen de germinación de un lote (ver :meth:`SeedBank.lot_report`)."""

    lot: Lot
    trays: int
    cells: int
    germinated: int

    @property
    def germ_rate(self) -> float | None:
        """Germinadas / celdas de todas sus bandejas, o ``None`` si no tiene bandejas."""
        return self.germinated / self.cells if self.cells else None


class SeedBank:
    """Banco de semillas: guarda lotes y bandejas en memoria.

    Para guardarlo en disco ver :meth:`save_sqlite` y :meth:`load_sqlite`.
    """

    def __init__(self) -> None:
        self.lots: dict[str, Lot] = {}
        self.trays: dict[str, Tray] = {}

    # --- lotes ---------------------------------------------------------------

    def add_lot(self, lot: Lot, replace: bool = False) -> None:
        """Agrega un lote. Si el id ya existe lanza ValidationError, salvo ``replace=True``."""
        if not isinstance(lot, Lot):
            raise ValidationError("add_lot espera un objeto Lot.")
        if lot.id in self.lots and not replace:
            raise ValidationError(
                f"Ya existe un lote con id '{lot.id}'. "
                "Usá otro id o reemplazalo explícitamente (replace=True / --reemplazar)."
            )
        self.lots[lot.id] = lot

    def get_lot(self, lot_id: str) -> Lot:
        try:
            return self.lots[lot_id]
        except KeyError:
            raise NotFoundError(f"No existe el lote '{lot_id}'.") from None

    # --- bandejas ------------------------------------------------------------

    def sow(self, tray: Tray) -> None:
        """Registra una bandeja. El lote tiene que existir y el id de bandeja no puede repetirse."""
        if not isinstance(tray, Tray):
            raise ValidationError("sow espera un objeto Tray.")
        if tray.lot_id not in self.lots:
            raise NotFoundError(f"No existe el lote '{tray.lot_id}' (bandeja {tray.id}).")
        if tray.id in self.trays:
            raise ValidationError(f"Ya existe una bandeja con id '{tray.id}'.")
        self.trays[tray.id] = tray

    def get_tray(self, tray_id: str) -> Tray:
        try:
            return self.trays[tray_id]
        except KeyError:
            raise NotFoundError(f"No existe la bandeja '{tray_id}'.") from None

    def next_tray_id(self) -> str:
        """Próximo id libre con el formato B001, B002, ..."""
        n = len(self.trays) + 1
        while f"B{n:03d}" in self.trays:
            n += 1
        return f"B{n:03d}"

    def record_germination(self, tray_id: str, germinated: int) -> Tray:
        """Actualiza cuántas celdas germinaron en una bandeja (validado)."""
        tray = self.get_tray(tray_id)
        _check_germinated(tray.id, germinated, tray.cells)
        tray.germinated = germinated
        return tray

    def germ_rate(self, tray_id: str) -> float:
        """Porcentaje de germinación de una bandeja, de 0 a 1 (germinadas / celdas)."""
        t = self.get_tray(tray_id)
        return t.germinated / t.cells if t.cells else 0.0

    def lot_report(self) -> list[LotSummary]:
        """Resumen de germinación por lote, ordenado por id de lote."""
        report = []
        for lot_id in sorted(self.lots):
            trays = [t for t in self.trays.values() if t.lot_id == lot_id]
            report.append(
                LotSummary(
                    lot=self.lots[lot_id],
                    trays=len(trays),
                    cells=sum(t.cells for t in trays),
                    germinated=sum(t.germinated for t in trays),
                )
            )
        return report

    # --- CSV -----------------------------------------------------------------

    def load_lots_csv(self, path: str, replace: bool = False) -> int:
        """Carga lotes desde un CSV y devuelve cuántos se cargaron.

        Columnas requeridas: id, species, harvest_year, viability, grams.
        Columna opcional: origin. Separador ``,`` o ``;`` (se detecta solo).
        La viabilidad acepta ``0.85``, ``85%`` o ``0,85``. Las filas sin id se saltan.

        Es todo o nada: si una fila es inválida se lanza ValidationError con el
        número de fila y no se agrega ningún lote del archivo.
        """
        lots = read_lots_csv(path)
        if not replace:
            for lot in lots:
                if lot.id in self.lots:
                    raise ValidationError(
                        f"El lote '{lot.id}' ya existe en el banco. "
                        "Usá --reemplazar (replace=True) para actualizarlo."
                    )
        for lot in lots:
            self.add_lot(lot, replace=replace)
        return len(lots)

    # --- SQLite --------------------------------------------------------------

    def save_sqlite(self, path: str = "seedbank.db") -> None:
        """Guarda el banco completo en un archivo SQLite."""
        from .storage import save_bank

        save_bank(self, path)

    @classmethod
    def load_sqlite(cls, path: str = "seedbank.db") -> "SeedBank":
        """Carga un banco desde un archivo SQLite (vacío si el archivo no existe)."""
        from .storage import load_bank

        return load_bank(path)


# --- lectura de CSV -----------------------------------------------------------


def parse_viability(raw: str) -> float:
    """Convierte ``"0.85"``, ``"0,85"``, ``"85%"`` o ``"85 %"`` en 0.85."""
    text = (raw or "").strip().replace(",", ".")
    if not text:
        raise ValueError("vacía")
    if text.endswith("%"):
        return float(text[:-1].strip()) / 100
    return float(text)


def _parse_number(raw: str) -> float:
    text = (raw or "").strip().replace(",", ".")
    if not text:
        raise ValueError("vacío")
    return float(text)


def _detect_delimiter(first_line: str) -> str:
    return ";" if first_line.count(";") > first_line.count(",") else ","


def read_lots_csv(path: str) -> list[Lot]:
    """Lee y valida todos los lotes de un CSV (sin agregarlos a ningún banco)."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        first_line = f.readline()
        f.seek(0)
        reader = csv.DictReader(f, delimiter=_detect_delimiter(first_line))
        if not reader.fieldnames:
            raise ValidationError(f"El archivo {path} está vacío o no tiene encabezado.")
        reader.fieldnames = [(name or "").strip().lower() for name in reader.fieldnames]
        missing = [c for c in REQUIRED_CSV_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValidationError(
                f"Faltan columnas en el CSV: {', '.join(missing)}. "
                f"Columnas requeridas: {', '.join(REQUIRED_CSV_COLUMNS)} "
                f"(opcional: {', '.join(OPTIONAL_CSV_COLUMNS)})."
            )

        lots: list[Lot] = []
        seen: dict[str, int] = {}
        for row in reader:
            line = reader.line_num
            lot_id = (row.get("id") or "").strip()
            if not lot_id:
                continue
            where = f"Fila {line} (lote {lot_id})"
            if lot_id in seen:
                raise ValidationError(f"{where}: id repetido, ya aparece en la fila {seen[lot_id]}.")
            raw_year = (row.get("harvest_year") or "").strip()
            try:
                year = int(raw_year)
            except ValueError:
                raise ValidationError(
                    f"{where}: año de cosecha inválido '{raw_year}'. Usá un año entero, por ejemplo 2025."
                ) from None
            raw_viab = row.get("viability") or ""
            try:
                viability = parse_viability(raw_viab)
            except ValueError:
                raise ValidationError(
                    f"{where}: viabilidad inválida '{raw_viab.strip()}'. "
                    "Usá un número entre 0 y 1 (ej. 0.85) o un porcentaje (ej. 85%)."
                ) from None
            raw_grams = row.get("grams") or ""
            try:
                grams = _parse_number(raw_grams)
            except ValueError:
                raise ValidationError(
                    f"{where}: gramos inválidos '{raw_grams.strip()}'. Usá un número, por ejemplo 12.5."
                ) from None
            try:
                lot = Lot(
                    id=lot_id,
                    species=row.get("species") or "",
                    harvest_year=year,
                    viability=viability,
                    grams=grams,
                    origin=row.get("origin") or "",
                )
            except ValidationError as e:
                raise ValidationError(f"Fila {line}: {e}") from None
            seen[lot_id] = line
            lots.append(lot)
    return lots
