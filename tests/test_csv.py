import pytest

from vivero_seedbank import SeedBank, ValidationError, parse_viability

HEADER = "id,species,harvest_year,viability,grams\n"


def test_csv_de_ejemplo(example_csv):
    bank = SeedBank()
    assert bank.load_lots_csv(str(example_csv)) == 5
    assert list(bank.lots) == ["EJ-001", "EJ-002", "EJ-003", "EJ-004", "EJ-005"]
    tomate = bank.lots["EJ-002"]
    assert tomate.species == "Tomate (Solanum lycopersicum)"
    assert isinstance(tomate.harvest_year, int) and tomate.harvest_year == 2025
    assert isinstance(tomate.viability, float) and tomate.viability == pytest.approx(0.92)
    assert isinstance(tomate.grams, float) and tomate.grams == pytest.approx(15.5)
    assert tomate.origin == ""


def test_salta_filas_vacias_y_limpia_espacios(write_csv):
    path = write_csv(HEADER + "L1,Tomate,2025,0.9,12.5\n\n,,,,\n L2 , Lechuga ,2024,0.8,3\n")
    bank = SeedBank()
    assert bank.load_lots_csv(str(path)) == 2
    assert bank.lots["L2"].species == "Lechuga"


def test_columna_origin_opcional(write_csv):
    path = write_csv(
        "id,species,harvest_year,viability,grams,origin\n"
        "L1,Tomate,2025,0.9,12,Huerta escolar\n"
        "L2,Lechuga,2024,0.8,3,\n"
    )
    bank = SeedBank()
    bank.load_lots_csv(str(path))
    assert bank.lots["L1"].origin == "Huerta escolar"
    assert bank.lots["L2"].origin == ""


@pytest.mark.parametrize(
    "raw,expected",
    [("0.85", 0.85), ("85%", 0.85), ("85 %", 0.85), (" 0,85 ", 0.85), ("100%", 1.0), ("0", 0.0)],
)
def test_parse_viability(raw, expected):
    assert parse_viability(raw) == pytest.approx(expected)


def test_viabilidad_porcentaje_en_csv(write_csv):
    path = write_csv(HEADER + "L1,Tomate,2025,85%,12\nL2,Lechuga,2024,0.85,3\n")
    bank = SeedBank()
    bank.load_lots_csv(str(path))
    assert bank.lots["L1"].viability == pytest.approx(bank.lots["L2"].viability)


def test_viabilidad_invalida_con_numero_de_fila(write_csv):
    path = write_csv(HEADER + "L1,Tomate,2025,0.9,12\nL2,Lechuga,2024,mucha,3\n")
    with pytest.raises(ValidationError) as e:
        SeedBank().load_lots_csv(str(path))
    msg = str(e.value)
    assert "Fila 3" in msg and "L2" in msg and "'mucha'" in msg and "85%" in msg


@pytest.mark.parametrize("value", ["120%", "1.5", "85", "-0.1"])
def test_viabilidad_fuera_de_rango(write_csv, value):
    path = write_csv(HEADER + f"L1,Tomate,2025,{value},12\n")
    with pytest.raises(ValidationError, match="Fila 2.*viabilidad"):
        SeedBank().load_lots_csv(str(path))


@pytest.mark.parametrize(
    "row,fragment",
    [
        ("L1,Tomate,dosmil,0.9,12", "año de cosecha"),
        ("L1,Tomate,1850,0.9,12", "año de cosecha"),
        ("L1,Tomate,2025,0.9,-3", "gramos"),
        ("L1,Tomate,2025,0.9,muchos", "gramos"),
        ("L1,,2025,0.9,12", "especie"),
    ],
)
def test_errores_de_fila(write_csv, row, fragment):
    path = write_csv(HEADER + row + "\n")
    with pytest.raises(ValidationError, match=f"Fila 2.*{fragment}"):
        SeedBank().load_lots_csv(str(path))


def test_todo_o_nada(write_csv):
    path = write_csv(HEADER + "L1,Tomate,2025,0.9,12\nL2,Lechuga,2024,2,3\n")
    bank = SeedBank()
    with pytest.raises(ValidationError):
        bank.load_lots_csv(str(path))
    assert bank.lots == {}


def test_id_repetido_en_el_archivo(write_csv):
    path = write_csv(HEADER + "L1,Tomate,2025,0.9,12\nL1,Lechuga,2024,0.8,3\n")
    with pytest.raises(ValidationError, match="Fila 3.*repetido.*fila 2"):
        SeedBank().load_lots_csv(str(path))


def test_lote_ya_existente_y_reemplazo(write_csv, example_csv):
    bank = SeedBank()
    bank.load_lots_csv(str(example_csv))
    path = write_csv(HEADER + "EJ-001,Cebolla morada,2025,0.5,10\n")
    with pytest.raises(ValidationError, match="ya existe"):
        bank.load_lots_csv(str(path))
    assert bank.lots["EJ-001"].species == "Cebolla (Allium cepa)"
    bank.load_lots_csv(str(path), replace=True)
    assert bank.lots["EJ-001"].species == "Cebolla morada"


def test_faltan_columnas(write_csv):
    path = write_csv("id,species,viability\nL1,Tomate,0.9\n")
    with pytest.raises(ValidationError, match="Faltan columnas.*harvest_year.*grams"):
        SeedBank().load_lots_csv(str(path))


def test_archivo_vacio(write_csv):
    path = write_csv("")
    with pytest.raises(ValidationError, match="vacío"):
        SeedBank().load_lots_csv(str(path))


def test_excel_punto_y_coma_bom_y_coma_decimal(write_csv):
    path = write_csv(
        "ID;Species;Harvest_Year;Viability;Grams;Origin\nL1;Tomate;2025;0,85;12,5;Vivero\n",
        encoding="utf-8-sig",
    )
    bank = SeedBank()
    assert bank.load_lots_csv(str(path)) == 1
    lot = bank.lots["L1"]
    assert (lot.viability, lot.grams, lot.origin) == (pytest.approx(0.85), pytest.approx(12.5), "Vivero")
