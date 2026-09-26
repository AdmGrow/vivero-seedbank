import sqlite3
from datetime import date

import pytest

from vivero_seedbank import Lot, SeedBank, Tray, ValidationError
from vivero_seedbank.storage import load_bank, save_bank


def sample_bank(example_csv):
    bank = SeedBank()
    bank.load_lots_csv(str(example_csv))
    bank.add_lot(Lot("L-ORIG", "Maíz", 2024, 0.6, 50, origin="Intercambio"))
    bank.sow(Tray("B001", "EJ-002", date(2026, 9, 1), 72, 60))
    bank.sow(Tray("B002", "EJ-001", date(2026, 9, 3), 50))
    return bank


def test_ida_y_vuelta(tmp_path, example_csv):
    db = tmp_path / "banco.db"
    bank = sample_bank(example_csv)
    save_bank(bank, str(db))
    loaded = load_bank(str(db))
    assert loaded.lots == bank.lots
    assert loaded.trays == bank.trays
    assert loaded.trays["B001"].sown == date(2026, 9, 1)
    assert loaded.lots["L-ORIG"].origin == "Intercambio"


def test_metodos_del_banco(tmp_path, example_csv):
    db = str(tmp_path / "banco.db")
    bank = sample_bank(example_csv)
    bank.save_sqlite(db)
    assert SeedBank.load_sqlite(db).lots == bank.lots


def test_guardar_dos_veces_no_duplica(tmp_path, example_csv):
    db = str(tmp_path / "banco.db")
    bank = sample_bank(example_csv)
    save_bank(bank, db)
    save_bank(bank, db)
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM lots").fetchone()[0] == 6
        assert conn.execute("SELECT COUNT(*) FROM trays").fetchone()[0] == 2


def test_guardar_refleja_cambios(tmp_path, example_csv):
    db = str(tmp_path / "banco.db")
    bank = sample_bank(example_csv)
    save_bank(bank, db)
    bank.record_germination("B002", 40)
    save_bank(bank, db)
    assert load_bank(db).trays["B002"].germinated == 40


def test_archivo_inexistente_da_banco_vacio(tmp_path):
    db = tmp_path / "no-existe.db"
    bank = load_bank(str(db))
    assert bank.lots == {} and bank.trays == {}
    assert not db.exists()


def test_ids_con_comillas_no_rompen_sql(tmp_path):
    db = str(tmp_path / "banco.db")
    bank = SeedBank()
    bank.add_lot(Lot("L'1\"; DROP TABLE lots;--", "Tomate", 2025, 0.9, 1))
    save_bank(bank, db)
    assert list(load_bank(db).lots) == ["L'1\"; DROP TABLE lots;--"]


def test_datos_invalidos_en_la_base_se_detectan(tmp_path, example_csv):
    db = str(tmp_path / "banco.db")
    save_bank(sample_bank(example_csv), db)
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE lots SET harvest_year = 1500 WHERE id = 'EJ-001'")
    with pytest.raises(ValidationError, match="año de cosecha"):
        load_bank(db)


def test_version_de_esquema_mas_nueva(tmp_path):
    db = str(tmp_path / "banco.db")
    save_bank(SeedBank(), db)
    with sqlite3.connect(db) as conn:
        conn.execute("PRAGMA user_version = 99")
    with pytest.raises(ValidationError, match="más nuevo"):
        load_bank(db)
