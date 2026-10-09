"""Modelo de datos de Vivero Seedbank: lotes de semillas, bandejas de siembra y banco.

Etapa alfa: los datos se guardan solo en memoria.
"""
from dataclasses import dataclass
from datetime import date
import csv

@dataclass
class Lot:
    id: str
    species: str
    harvest_year: int
    viability: float   # 0 a 1
    grams: float
    origin: str = ""

@dataclass
class Tray:
    id: str
    lot_id: str
    sown: date
    cells: int
    germinated: int = 0

class SeedBank:
    def __init__(self):
        self.lots: dict[str, Lot] = {}
        self.trays: dict[str, Tray] = {}

    def add_lot(self, lot: Lot):
        if not 0 <= lot.viability <= 1:
            raise ValueError("viability")
        self.lots[lot.id] = lot

    def sow(self, tray: Tray):
        if tray.lot_id not in self.lots:
            raise KeyError("unknown lot")
        self.trays[tray.id] = tray

    def germ_rate(self, tray_id: str) -> float:
        t = self.trays[tray_id]
        return t.germinated / t.cells if t.cells else 0.0

    def load_lots_csv(self, path: str):
        """Carga lotes desde un csv con columnas: id,species,harvest_year,viability,grams

        origin es opcional. viability acepta 0.85 o 85%.
        Salta filas sin id. Si falta una columna requerida, lanza KeyError.
        """
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get("id") or not str(row["id"]).strip():
                    continue
                lot = Lot(
                    id=row["id"].strip(),
                    species=row["species"].strip(),
                    harvest_year=int(row["harvest_year"]),
                    viability=parse_viability(row["viability"]),
                    grams=float(row["grams"]),
                    origin=(row.get("origin") or "").strip(),
                )
                self.add_lot(lot)


def parse_viability(raw) -> float:
    """Acepta 0.85 o 85%. Devuelve un float entre 0 y 1."""
    text = str(raw).strip().replace(",", ".")
    if text.endswith("%"):
        value = float(text[:-1]) / 100.0
    else:
        value = float(text)
    if not 0 <= value <= 1:
        raise ValueError("viability")
    return value


def expected_germinated(cells: int, viability: float) -> int:
    """Plantulas que espero si siembro `cells` con esa viabilidad (0 a 1).

    Redondeo al entero mas cercano. No reemplaza un conteo real en la bandeja.
    """
    if cells < 0:
        raise ValueError("cells")
    if not 0 <= viability <= 1:
        raise ValueError("viability")
    return round(cells * viability)
