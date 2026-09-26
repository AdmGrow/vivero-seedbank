from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def example_csv() -> Path:
    return ROOT / "examples" / "lotes_ejemplo.csv"


@pytest.fixture
def write_csv(tmp_path):
    def _write(text: str, name: str = "lotes.csv", encoding: str = "utf-8") -> Path:
        path = tmp_path / name
        path.write_text(text, encoding=encoding)
        return path

    return _write
