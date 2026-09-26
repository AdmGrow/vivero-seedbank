import os
import subprocess
import sys
from datetime import date

import pytest

from vivero_seedbank.cli import main


@pytest.fixture
def db(tmp_path):
    return str(tmp_path / "seedbank.db")


def run(capsys, *args):
    code = main(list(args))
    out, err = capsys.readouterr()
    return code, out, err


def test_flujo_completo(capsys, db, example_csv):
    code, out, _ = run(capsys, "--db", db, "import", str(example_csv))
    assert code == 0 and "Importados 5 lotes" in out

    code, out, _ = run(capsys, "--db", db, "list")
    assert code == 0
    for lot_id in ("EJ-001", "EJ-002", "EJ-003", "EJ-004", "EJ-005"):
        assert lot_id in out

    code, out, _ = run(capsys, "--db", db, "sembrar", "EJ-002", "--celdas", "72", "--fecha", "2026-09-01")
    assert code == 0 and "Bandeja B001" in out and "2026-09-01" in out

    code, out, _ = run(capsys, "--db", db, "germinacion", "B001", "--germinadas", "60")
    assert code == 0 and "60 de 72" in out and "83.3 %" in out

    code, out, _ = run(capsys, "--db", db, "informe")
    assert code == 0
    line = next(ln for ln in out.splitlines() if ln.startswith("EJ-002"))
    assert "83.3 %" in line and "92.0 %" in line and "-8.7 pts" in line
    assert "Total: 60 de 72" in out


def test_db_despues_del_subcomando(capsys, db, example_csv):
    assert run(capsys, "import", str(example_csv), "--db", db)[0] == 0
    code, out, _ = run(capsys, "list", "--db", db)
    assert code == 0 and "EJ-005" in out


def test_variable_de_entorno(capsys, db, example_csv, monkeypatch):
    monkeypatch.setenv("SEEDBANK_DB", db)
    assert run(capsys, "import", str(example_csv))[0] == 0
    assert "EJ-001" in run(capsys, "--db", db, "list")[1]


def test_fecha_por_defecto_hoy(capsys, db, example_csv):
    run(capsys, "--db", db, "import", str(example_csv))
    code, out, _ = run(capsys, "--db", db, "sembrar", "EJ-001", "--celdas", "10", "--id", "MI-BANDEJA")
    assert code == 0 and "MI-BANDEJA" in out and date.today().isoformat() in out


def test_banco_vacio(capsys, db):
    assert "vacío" in run(capsys, "--db", db, "list")[1]
    assert "vacío" in run(capsys, "--db", db, "informe")[1]


@pytest.mark.parametrize(
    "args,fragment",
    [
        (["sembrar", "NOPE", "--celdas", "5"], "No existe el lote 'NOPE'"),
        (["sembrar", "EJ-001", "--celdas", "0"], "celdas"),
        (["germinacion", "B999", "--germinadas", "1"], "No existe la bandeja 'B999'"),
        (["import", "no-existe.csv"], "no se encontró el archivo"),
    ],
)
def test_errores_claros_sin_traceback(capsys, db, example_csv, args, fragment):
    run(capsys, "--db", db, "import", str(example_csv))
    code, _, err = run(capsys, "--db", db, *args)
    assert code == 1
    assert fragment in err
    assert "Traceback" not in err


def test_germinadas_mayor_que_celdas(capsys, db, example_csv):
    run(capsys, "--db", db, "import", str(example_csv))
    run(capsys, "--db", db, "sembrar", "EJ-002", "--celdas", "72")
    code, _, err = run(capsys, "--db", db, "germinacion", "B001", "--germinadas", "99")
    assert code == 1 and "más germinadas (99) que celdas (72)" in err


def test_import_duplicado_y_reemplazo(capsys, db, example_csv):
    run(capsys, "--db", db, "import", str(example_csv))
    code, _, err = run(capsys, "--db", db, "import", str(example_csv))
    assert code == 1 and "ya existe" in err and "--reemplazar" in err
    assert run(capsys, "--db", db, "import", str(example_csv), "--reemplazar")[0] == 0


def test_error_no_guarda_cambios(capsys, db, example_csv, write_csv):
    run(capsys, "--db", db, "import", str(example_csv))
    bad = write_csv("id,species,harvest_year,viability,grams\nN1,Poroto,2025,0.9,10\nN2,Haba,2025,mucha,5\n")
    code, _, err = run(capsys, "--db", db, "import", str(bad))
    assert code == 1 and "Fila 3" in err
    assert "N1" not in run(capsys, "--db", db, "list")[1]


def test_fecha_invalida_es_error_de_argumentos(capsys, db, example_csv):
    run(capsys, "--db", db, "import", str(example_csv))
    with pytest.raises(SystemExit) as e:
        main(["--db", db, "sembrar", "EJ-001", "--celdas", "5", "--fecha", "01/09/2026"])
    assert e.value.code == 2
    assert "AAAA-MM-DD" in capsys.readouterr().err


def test_ayuda_en_espanol(capsys):
    with pytest.raises(SystemExit) as e:
        main(["--help"])
    assert e.value.code == 0
    out = capsys.readouterr().out
    assert out.startswith("uso: seedbank")
    for cmd in ("import", "list", "sembrar", "germinacion", "informe"):
        assert cmd in out


def test_python_m(tmp_path, example_csv):
    db = str(tmp_path / "x.db")
    result = subprocess.run(
        [sys.executable, "-m", "vivero_seedbank", "--db", db, "import", str(example_csv)],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(example_csv.parent.parent / "src")},
    )
    assert result.returncode == 0, result.stderr
    assert "Importados 5 lotes" in result.stdout
