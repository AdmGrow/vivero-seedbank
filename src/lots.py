"""Lotes de semillas. Lo fui armando con videos de huerta.
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
        Simple, para principiantes. Si falta alguna columna, se rompe.
        """
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lot = Lot(
                    id=row["id"],
                    species=row["species"],
                    harvest_year=int(row["harvest_year"]),
                    viability=float(row["viability"]),
                    grams=float(row["grams"]),
                )
                self.add_lot(lot)
