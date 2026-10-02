"""Prueba corta de expected_germinated.

La corro desde la raiz con:
    python -m unittest tests/test_expected_germinated.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from lots import expected_germinated


class TestExpected(unittest.TestCase):
    def test_72_celdas_085(self):
        # 72 * 0.85 = 61.2, redondea a 61. No es un conteo real.
        self.assertEqual(expected_germinated(72, 0.85), 61)

    def test_cero_celdas(self):
        self.assertEqual(expected_germinated(0, 0.85), 0)

    def test_celdas_negativas(self):
        with self.assertRaises(ValueError):
            expected_germinated(-1, 0.5)

    def test_viabilidad_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            expected_germinated(10, 1.2)


if __name__ == "__main__":
    unittest.main()
