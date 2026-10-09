"""Prueba corta de parse_viability. Correr: python tests/test_parse_viability.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from lots import parse_viability

assert parse_viability("0.85") == 0.85
assert parse_viability("85%") == 0.85
assert parse_viability("85,5%") == 0.855
print("ok")
