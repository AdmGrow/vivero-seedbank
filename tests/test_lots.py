from datetime import  date
from src.lots import SeedBank, Lot, Tray, expected_germinated
import pytest
import csv

@pytest.fixture
def lots_maker():
    def _make_lot(
            id="EJ-001", species="Tomato",
            harvest_year=2025, viability=0.85,
            grams=40
    ):
        return Lot(
            id=id, species=species, harvest_year=harvest_year
            , viability=viability, grams=grams
        )
    return _make_lot


@pytest.fixture
def trey_maker():
    def _make_trey(
            id="A1", id_lot="EJ-001", sown=date(year=2025, month=10, day=8),
            cells=43, germinated=32
    ):
        return Tray(
            id=id, lot_id=id_lot, sown=sown,
            cells=cells, germinated=germinated
        )
    return _make_trey


@pytest.mark.parametrize(
    "lot_id, viability",
    [
        ("EJ-002", 0.56),
        ("EJ-003", 0),
        ("EJ-004",  1),
        ("EJ-005", 0.17),
    ]
)
def test_add_good_lot(lot_id, viability, lots_maker):

    lot = lots_maker(id=lot_id, viability=viability)

    bank = SeedBank()


    bank.add_lot(lot)

    assert lot.id in bank.lots
    assert bank.lots[lot.id] == lot


@pytest.mark.parametrize(
    "lot_id, viability",
    [
        ("EJ-001",  -0.01),
        ("EJ-002",  -0.98),
        ("EJ-003",  1.17),
        ("EJ-004", 2.23),
        ("EJ-005", 1.01),
    ]
)
def test_add_bad_lot(lot_id, viability, lots_maker):
    lot = lots_maker(id=lot_id, viability=viability)

    bank = SeedBank()

    with pytest.raises(ValueError, match="viability"):
        bank.add_lot(lot)

    assert bank.lots == {}

@pytest.mark.parametrize(
    "lot_id, trey_di, cells, germinated",

    [
        ("EJ-001", "A1", 34, 13),
        ("EJ-002", "A2", 25, 11),
        ("EJ-003", "A3" , 31, 9),
        ("EJ-004", "A4", 22, 5),
    ]
)
def test_sow(lots_maker, trey_maker, lot_id, trey_di, cells, germinated):

    lot = lots_maker(id=lot_id)
    print(lot)

    trey = trey_maker(id=trey_di, id_lot=lot_id, cells=cells, germinated=germinated)

    bank = SeedBank()

    bank.add_lot(lot)

    assert trey.lot_id in bank.lots

@pytest.mark.parametrize(
    "lot_id, trey_di, unknowing_id, cells, germinated",

    [
        ("EJ-001", "A1", "EJ-005" , 34, 13),
        ("EJ-002",  "A2", "EJ-006", 25, 11),
        ("EJ-003", "A3" , "EJ-007", 31, 9),
        ("EJ-004", "A4", "EJ-008", 22, 5),
    ]
)
def test_error_sow(lots_maker, trey_maker, lot_id, trey_di, unknowing_id, cells, germinated):

    lot = lots_maker(id=lot_id)
    print(lot)

    trey = trey_maker(id=trey_di, id_lot=unknowing_id, cells=cells, germinated=germinated)
    print(trey)

    bank = SeedBank()

    bank.add_lot(lot)

    with pytest.raises(KeyError, match="unknown lot"):
        bank.sow(trey)

@pytest.mark.parametrize(
    "lot_id, trey_di, cells, germinated, expected",

    [
        ("EJ-001", "A1",34, 13, 0.38235294117647056),
        ("EJ-002", "A2",25, 11 ,0.44),
        ("EJ-003", "A3" , 31, 9, 0.2903225806451613),
        ("EJ-004",  "A4", 22, 5, 0.22727272727272727),
    ]
)
def test_good_germ_rate(lots_maker, trey_maker, lot_id, trey_di, cells, germinated, expected):

    lot = lots_maker(id=lot_id)

    trey = trey_maker(id=trey_di, id_lot=lot_id, cells=cells, germinated=germinated)

    bank = SeedBank()

    bank.add_lot(lot)

    bank.sow(trey)

    result = bank.germ_rate(trey_di)

    assert result == expected

@pytest.mark.parametrize(
    "lot_id, trey_di, cells, germinated, expected",

    [
        ("EJ-001", "A1",10, 0,0.0),
        ("EJ-002", "A2",0,  0,0.0),

    ]
)
def test_bad_germ_rate(lots_maker, trey_maker, lot_id, trey_di, cells, germinated, expected):

    lot = lots_maker(id=lot_id)

    trey = trey_maker(id=trey_di, id_lot=lot_id, cells=cells, germinated=germinated)

    bank = SeedBank()

    bank.add_lot(lot)

    bank.sow(trey)

    result = bank.germ_rate(trey_di)

    assert result == expected


def test_good_load_csv(tmp_path, lots_maker):

    csv_path = tmp_path / "test_file.csv"
    lot = lots_maker()

    fieldnames = ["id", "species", "harvest_year", "viability", "grams"]

    check_file = {
        "id": lot.id,
        "species": lot.species,
        "harvest_year": lot.harvest_year,
        "viability": lot.viability,
        "grams": lot.grams,
    }



    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(check_file)


    bank = SeedBank()


    bank.load_lots_csv(csv_path)

    assert lot.id in bank.lots
    assert bank.lots[lot.id] == lot


def test_bad_load_cvs(tmp_path, lots_maker):

    csv_path = tmp_path / "test_file.csv"
    lot = lots_maker()

    fieldnames = ["species", "harvest_year", "viability", "grams"]

    check_file = {
        "species": lot.species,
        "harvest_year": lot.harvest_year,
        "viability": lot.viability,
        "grams": lot.grams,
    }

    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(check_file)

    bank = SeedBank()

    bank.load_lots_csv(csv_path)

    assert bank.lots == {}
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
