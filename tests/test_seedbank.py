from datetime import  date
from src.lots import SeedBank, Lot, Tray, expected_germinated
import pytest
import csv
from pathlib import Path

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
def tray_maker():
    def _make_tray(
            id="A1", id_lot="EJ-001", sown=date(year=2025, month=10, day=8),
            cells=43, germinated=32
    ):
        return Tray(
            id=id, lot_id=id_lot, sown=sown,
            cells=cells, germinated=germinated
        )
    return _make_tray


@pytest.mark.parametrize(
    "lot_id, viability",
    [
        (" EJ-002 ",0.56),
        ("EJ-003 ", 0),
        (" EJ-004", 1),
        ("EJ-005",  0.17),
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
    "lot_id, tray_di, cells, germinated",

    [
        ("EJ-001", "A1", 34, 13),
        ("EJ-002", "A2", 25, 11),
        ("EJ-003", "A3" , 31, 9),
        ("EJ-004", "A4", 22, 5),
    ]
)
def test_sow(lots_maker, tray_maker, lot_id, tray_di, cells, germinated):

    lot = lots_maker(id=lot_id)
    print(lot)

    trey = tray_maker(id=tray_di, id_lot=lot_id, cells=cells, germinated=germinated)

    bank = SeedBank()

    bank.add_lot(lot)

    bank.sow(trey)

    assert trey.lot_id in bank.lots
    assert trey.id in bank.trays

@pytest.mark.parametrize(
    "lot_id, tray_di, unknowing_id, cells, germinated",

    [
        ("EJ-001", "A1", "EJ-005" , 34, 13),
        ("EJ-002",  "A2", "EJ-006", 25, 11),
        ("EJ-003", "A3" , "EJ-007", 31, 9),
        ("EJ-004", "A4", "EJ-008", 22, 5),
    ]
)
def test_error_sow(lots_maker, tray_maker, lot_id, tray_di, unknowing_id, cells, germinated):

    lot = lots_maker(id=lot_id)


    tray = tray_maker(id=tray_di, id_lot=unknowing_id, cells=cells, germinated=germinated)


    bank = SeedBank()

    bank.add_lot(lot)

    with pytest.raises(KeyError, match="unknown lot"):
        bank.sow(tray)

@pytest.mark.parametrize(
    "lot_id, tray_di, cells, germinated, expected",

    [
        ("EJ-001", "A1",34, 13, 0.38235294117647056),
        ("EJ-002", "A2",25, 11 ,0.44),
        ("EJ-003", "A3" , 72, 60, 0.8333333333333334),
        ("EJ-004",  "A4", 22, 5, 0.22727272727272727),
    ]
)
def test_good_germ_rate(lots_maker, tray_maker, lot_id, tray_di, cells, germinated, expected):

    lot = lots_maker(id=lot_id)

    tray = tray_maker(id=tray_di, id_lot=lot_id, cells=cells, germinated=germinated)

    bank = SeedBank()

    bank.add_lot(lot)

    bank.sow(tray)

    result = bank.germ_rate(tray_di)

    assert result == pytest.approx(expected)

@pytest.mark.parametrize(
    "lot_id, tray_di, cells, germinated, expected",

    [
        ("EJ-001", "A1",10, 0,0.0),
        ("EJ-002", "A2",0,  0,0.0),

    ]
)
def test_bad_germ_rate(lots_maker, tray_maker, lot_id, tray_di, cells, germinated, expected):

    lot = lots_maker(id=lot_id)

    tray = tray_maker(id=tray_di, id_lot=lot_id, cells=cells, germinated=germinated)

    bank = SeedBank()

    bank.add_lot(lot)

    bank.sow(tray)

    result = bank.germ_rate(tray_di)

    assert result == expected


def test_good_load_csv(tmp_path, lots_maker):

    csv_path = tmp_path / "test_file.csv"
    lot = lots_maker()

    fieldnames = ["id", "species", "harvest_year", "viability", "grams"]

    check_file = {
        "id": f" {lot.id}",
        "species": f" {lot.species} ",
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

@pytest.mark.parametrize(
    "check_file, fieldnames",
    [

        (
                {
                    "id": "", "species": None, "harvest_year": None, "viability": None, "grams": None
                },
                [
                    "id", "species", "harvest_year", "viability", "grams"
                ]
        ),
        (
                {
                    "id": " ", "species": None, "harvest_year": None, "viability": None, "grams": None
                },
                [
                    "id", "species", "harvest_year", "viability", "grams"
                ]
        ),
        (
                {
                    "species": None, "harvest_year": None, "viability": None, "grams": None
                },
                [
                    "species", "harvest_year", "viability", "grams"
                ]
        ),
    ]
)
def test_bad_id_to_load_cvs(tmp_path, lots_maker, check_file, fieldnames):

    csv_path = tmp_path / "test_file.csv"
    lot = lots_maker()



    check_file["species"] = lot.species
    check_file["harvest_year"] = lot.harvest_year
    check_file["viability"] = lot.viability
    check_file["grams"] = lot.grams


    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(check_file)

    bank = SeedBank()

    bank.load_lots_csv(csv_path)

    assert bank.lots == {}

@pytest.mark.parametrize(
    "id, species, harvest_year, viability, grams",
    [
        ("EJ-001", "Cebolla (Allium cepa)", 2025, 0.85, 40),
        ("EJ-002", "Tomate (Solanum lycopersicum)", 2025, 0.92, 15.5),
        ("EJ-003", "Lechuga (Lactuca sativa)", 2024, 0.78, 8),
        ("EJ-004", "Zapallo (Cucurbita maxima)" , 2025, 0.9, 120),
        ("EJ-005", "Albahaca (Ocimum basilicum)", 2024, 0.7, 5.2)
    ]
)
def test_load_true_file(id, species, harvest_year, viability, grams):

    filedir = Path(__file__).resolve().parent.parent

    filename = filedir / "examples" / "lotes_ejemplo.csv"

    bank = SeedBank()

    bank.load_lots_csv(filename)

    assert len(bank.lots) == 5

    loaded_lot = bank.lots[id]

    assert loaded_lot.id == id
    assert loaded_lot.species == species
    assert loaded_lot.harvest_year == harvest_year
    assert loaded_lot.viability == pytest.approx(viability)
    assert loaded_lot.grams == pytest.approx(grams)


    assert isinstance(loaded_lot.harvest_year, int)
    assert isinstance(loaded_lot.viability, float)
    assert isinstance(loaded_lot.grams, float)



