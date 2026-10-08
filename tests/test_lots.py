from datetime import  date
from src.lots import SeedBank, Lot, Tray
import pytest

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
    "id, viability",
    [
        ("EJ-002", 0.56),
        ("EJ-003", 0),
        ("EJ-004",  1),
        ("EJ-005", 0.17),
    ]
)
def test_add_good_lot(id, viability, lots_maker):

    lot = lots_maker(id=id, viability=viability)

    bank = SeedBank()


    bank.add_lot(lot)

    assert lot.id in bank.lots
    assert bank.lots[lot.id] == lot


@pytest.mark.parametrize(
    "id, viability",
    [
        ("EJ-001",  -0.01),
        ("EJ-002",  -0.98),
        ("EJ-003",  1.17),
        ("EJ-004", 2.23),
        ("EJ-005", 1.01),
    ]
)
def test_add_bad_lot(id, viability, lots_maker):
    lot = lots_maker(id=id, viability=viability)

    bank = SeedBank()

    with pytest.raises(ValueError, match="viability"):
        bank.add_lot(lot)

    assert bank.lots == {}

@pytest.mark.parametrize(
    "id, species, viability, trey_di, sown, cells, germinated",

    [
        ("EJ-001", "Potato", 0.56, "A1", date(year=2025, month=10, day=2), 34, 13),
        ("EJ-002", "Cucumber", 0, "A2",date(year=2025, month=10, day=12), 25, 11),
        ("EJ-003", "Carrot", 1, "A3" ,date(year=2025, month=10, day=25), 31, 9),
        ("EJ-004", "Melon", 0.17, "A4",date(year=2025, month=10, day=30), 22, 5),
    ]
)
def test_sow(lots_maker, trey_maker, id, species, viability, trey_di, sown, cells, germinated):

    lot = lots_maker(id=id, species=species, viability=viability)
    print(lot)

    trey = trey_maker(id=trey_di, id_lot=id, sown=sown, cells=cells, germinated=germinated)
    print(trey)

    bank = SeedBank()

    bank.add_lot(lot)

    bank.sow(trey)

    assert trey.lot_id in bank.lots

@pytest.mark.parametrize(
    "id, species, viability, trey_di, unknowing_id, sown, cells, germinated",

    [
        ("EJ-001", "Potato", 0.56, "A1", "EJ-005" ,date(year=2025, month=10, day=2), 34, 13),
        ("EJ-002", "Cucumber", 0, "A2", "EJ-006",date(year=2025, month=10, day=12), 25, 11),
        ("EJ-003", "Carrot", 1, "A3" , "EJ-007", date(year=2025, month=10, day=25), 31, 9),
        ("EJ-004", "Melon", 0.17, "A4", "EJ-008", date(year=2025, month=10, day=30), 22, 5),
    ]
)
def test_error_sow(lots_maker, trey_maker, id, species, viability, trey_di, unknowing_id, sown, cells, germinated):

    lot = lots_maker(id=id, species=species, viability=viability)
    print(lot)

    trey = trey_maker(id=trey_di, id_lot=unknowing_id, sown=sown, cells=cells, germinated=germinated)
    print(trey)

    bank = SeedBank()

    bank.add_lot(lot)

    with pytest.raises(KeyError, match="unknown lot"):
        bank.sow(trey)

@pytest.mark.parametrize(
    "id_lot, species, viability, trey_di, sown, cells, germinated, expected",

    [
        ("EJ-001", "Potato", 0.56, "A1",date(year=2025, month=10, day=2), 34, 13, 0.38235294117647056),
        ("EJ-002", "Cucumber", 0, "A2",date(year=2025, month=10, day=12), 25, 11 ,0.44),
        ("EJ-003", "Carrot", 1, "A3" , date(year=2025, month=10, day=25), 31, 9, 0.2903225806451613),
        ("EJ-004", "Melon", 0.17, "A4", date(year=2025, month=10, day=30), 22, 5, 0.22727272727272727),
    ]
)
def test_good_germ_rate(lots_maker, trey_maker, id_lot, species, viability, trey_di,sown, cells, germinated, expected):

    lot = lots_maker(id=id_lot, species=species, viability=viability)

    trey = trey_maker(id=trey_di, id_lot=id_lot, sown=sown, cells=cells, germinated=germinated)

    bank = SeedBank()

    bank.add_lot(lot)

    bank.sow(trey)

    result = bank.germ_rate(trey_di)

    assert result == expected

@pytest.mark.parametrize(
    "id_lot, species, viability, trey_di, sown, cells, germinated, expected",

    [
        (
                "EJ-001", "Potato", 0.56, "A1",
                date(year=2025, month=10, day=2), 10, 0,
                0.0),
        (
                "EJ-002", "Cucumber", 0, "A2",
                date(year=2025, month=10, day=12), 0,  0,
                0.0),

    ]
)
def test_bad_germ_rate(lots_maker, trey_maker, id_lot, species, viability, trey_di,sown, cells, germinated, expected):

    lot = lots_maker(id=id_lot, species=species, viability=viability)

    trey = trey_maker(id=trey_di, id_lot=id_lot, sown=sown, cells=cells, germinated=germinated)

    bank = SeedBank()

    bank.add_lot(lot)

    bank.sow(trey)

    result = bank.germ_rate(trey_di)

    assert result == expected