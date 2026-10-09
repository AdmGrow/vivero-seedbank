"""CSV con origin y viabilidad 85%. Correr: python tests/test_load_origin.py"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from lots import SeedBank

csv_text = (
    "id,species,harvest_year,viability,grams,origin\n"
    "L1,Lechuga,2024,85%,8,huerta norte\n"
    "L2,Tomate,2025,0.9,3,\n"
)
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
    f.write(csv_text)
    path = f.name

bank = SeedBank()
bank.load_lots_csv(path)
assert bank.lots["L1"].viability == 0.85
assert bank.lots["L1"].origin == "huerta norte"
assert bank.lots["L2"].origin == ""
print("ok")
