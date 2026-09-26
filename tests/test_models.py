from datetime import date

import pytest

from vivero_seedbank import Lot, NotFoundError, SeedBank, Tray, ValidationError
from vivero_seedbank.lots import max_harvest_year


def make_lot(**kw):
    data = dict(id="L1", species="Tomate", harvest_year=2025, viability=0.9, grams=10.0)
    data.update(kw)
    return Lot(**data)


def make_bank():
    bank = SeedBank()
    bank.add_lot(make_lot())
    return bank


# --- Lot ---------------------------------------------------------------------


def test_lot_valido_y_normalizado():
    lot = make_lot(id="  L1 ", species=" Tomate ", origin=" Huerta ", grams=3)
    assert lot.id == "L1"
    assert lot.species == "Tomate"
    assert lot.origin == "Huerta"
    assert isinstance(lot.grams, float)


@pytest.mark.parametrize("viability", [-0.01, 1.01, 85, "0.9", None])
def test_lot_viabilidad_invalida(viability):
    with pytest.raises(ValidationError, match="viabilidad"):
        make_lot(viability=viability)


@pytest.mark.parametrize("viability", [0, 0.0, 1, 1.0, 0.5])
def test_lot_viabilidad_limites_validos(viability):
    assert make_lot(viability=viability).viability == float(viability)


@pytest.mark.parametrize("grams", [-0.1, -5, None, "3"])
def test_lot_gramos_invalidos(grams):
    with pytest.raises(ValidationError, match="gramos"):
        make_lot(grams=grams)


def test_lot_gramos_cero_valido():
    assert make_lot(grams=0).grams == 0.0


@pytest.mark.parametrize("year", [1899, max_harvest_year() + 1, 3025, 2025.0, True, "2025"])
def test_lot_anio_imposible(year):
    with pytest.raises(ValidationError, match="año de cosecha"):
        make_lot(harvest_year=year)


@pytest.mark.parametrize("year", [1900, date.today().year, max_harvest_year()])
def test_lot_anio_limites_validos(year):
    assert make_lot(harvest_year=year).harvest_year == year


@pytest.mark.parametrize("field,value", [("id", ""), ("id", "   "), ("species", "")])
def test_lot_campos_vacios(field, value):
    with pytest.raises(ValidationError):
        make_lot(**{field: value})


def test_mensajes_en_espanol_con_id_del_lote():
    with pytest.raises(ValidationError) as e:
        make_lot(id="EJ-009", grams=-5)
    assert "Lote EJ-009" in str(e.value)
    assert "negativos" in str(e.value)


# --- Tray --------------------------------------------------------------------


def test_tray_valida():
    t = Tray("B1", "L1", date(2026, 9, 1), 72, 60)
    assert (t.cells, t.germinated) == (72, 60)


@pytest.mark.parametrize("cells", [0, -1, 1.5, None])
def test_tray_celdas_invalidas(cells):
    with pytest.raises(ValidationError, match="celdas"):
        Tray("B1", "L1", date(2026, 9, 1), cells)


@pytest.mark.parametrize("germinated", [-1, 11, 2.5])
def test_tray_germinadas_invalidas(germinated):
    with pytest.raises(ValidationError, match="germinadas"):
        Tray("B1", "L1", date(2026, 9, 1), 10, germinated)


def test_tray_germinadas_igual_a_celdas_valido():
    assert Tray("B1", "L1", date(2026, 9, 1), 10, 10).germinated == 10


def test_tray_fecha_invalida():
    with pytest.raises(ValidationError, match="fecha"):
        Tray("B1", "L1", "2026-09-01", 10)


# --- SeedBank ----------------------------------------------------------------


def test_add_lot_duplicado_rechazado():
    bank = make_bank()
    with pytest.raises(ValidationError, match="Ya existe un lote con id 'L1'"):
        bank.add_lot(make_lot(species="Otra"))
    assert bank.lots["L1"].species == "Tomate"


def test_add_lot_replace_explicito():
    bank = make_bank()
    bank.add_lot(make_lot(species="Otra"), replace=True)
    assert bank.lots["L1"].species == "Otra"


def test_sow_lote_inexistente():
    bank = make_bank()
    with pytest.raises(NotFoundError, match="No existe el lote 'NOPE'"):
        bank.sow(Tray("B1", "NOPE", date(2026, 9, 1), 10))
    # sigue siendo KeyError, como antes
    with pytest.raises(KeyError):
        bank.sow(Tray("B1", "NOPE", date(2026, 9, 1), 10))


def test_sow_bandeja_duplicada():
    bank = make_bank()
    bank.sow(Tray("B1", "L1", date(2026, 9, 1), 10))
    with pytest.raises(ValidationError, match="bandeja"):
        bank.sow(Tray("B1", "L1", date(2026, 9, 2), 20))


def test_germ_rate():
    bank = make_bank()
    bank.sow(Tray("B1", "L1", date(2026, 9, 1), 72, 60))
    assert bank.germ_rate("B1") == pytest.approx(60 / 72)


def test_germ_rate_bandeja_inexistente():
    with pytest.raises(NotFoundError, match="bandeja 'X'"):
        make_bank().germ_rate("X")


def test_record_germination():
    bank = make_bank()
    bank.sow(Tray("B1", "L1", date(2026, 9, 1), 10))
    bank.record_germination("B1", 7)
    assert bank.germ_rate("B1") == pytest.approx(0.7)
    with pytest.raises(ValidationError, match="más germinadas"):
        bank.record_germination("B1", 11)
    assert bank.trays["B1"].germinated == 7


def test_next_tray_id():
    bank = make_bank()
    assert bank.next_tray_id() == "B001"
    bank.sow(Tray("B001", "L1", date(2026, 9, 1), 10))
    bank.sow(Tray("B003", "L1", date(2026, 9, 1), 10))
    new_id = bank.next_tray_id()
    assert new_id not in bank.trays


def test_lot_report():
    bank = make_bank()
    bank.add_lot(make_lot(id="L2", species="Lechuga"))
    bank.sow(Tray("B1", "L1", date(2026, 9, 1), 10, 8))
    bank.sow(Tray("B2", "L1", date(2026, 9, 2), 10, 6))
    report = {s.lot.id: s for s in bank.lot_report()}
    assert report["L1"].trays == 2
    assert report["L1"].cells == 20
    assert report["L1"].germinated == 14
    assert report["L1"].germ_rate == pytest.approx(0.7)
    assert report["L2"].trays == 0
    assert report["L2"].germ_rate is None
