"""Prueba corta de expected_germinated.

La corro desde la raiz con:
    python -m unittest tests/test_expected_germinated.py
"""
import sys
import unittest
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from src.lots import expected_germinated


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



@pytest.mark.parametrize(
    "cells, viability, expect",
    [
        (0, 0.0, 0),
        (0, 0.75, 0),
        (0, 1.0, 0),
        (10, 0.0, 0),
        (10, 1.0, 10),
        (100, 0.85, 85),
        (40, 0.75, 30),
        (10, 0.34, 3),  # 3.4 → 3
        (10, 0.36, 4),  # 3.6 → 4
        (1, 0.5, 0),  # 0.5 → 0
        (3, 0.5, 2),  # 1.5 → 2
        (5, 0.5, 2),  # 2.5 → 2
        (7, 0.5, 4),
    ]
)
def test_expected_germinated(cells, viability, expect):

    result = expected_germinated(cells, viability)

    assert result == expect



@pytest.mark.parametrize(
    "cells, viability, message",
    [
        (-1, 0.5, "cells"),
        (-10, 0.0, "cells"),
        (-100, 1.0, "cells"),

        (10, -0.01, "viability"),
        (10, -1.0, "viability"),
        (10, 1.01, "viability"),
        (10, 2.0, "viability"),

        (0, -0.1, "viability"),
        (0, 1.1, "viability"),

        (-1, -0.1, "cells"),
        (-1, 1.1, "cells"),
    ]
)
def test_exception_in_expected_germinated(cells, viability, message):

    with pytest.raises(ValueError, match=message):
        expected_germinated(cells, viability)




if __name__ == "__main__":
    unittest.main()
