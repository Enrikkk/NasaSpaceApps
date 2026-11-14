"""Constantes y validacion compartidas por los tests (importables: `from api_helpers import ...`).

Esquema y validador: los del contrato v1.1 en app/data/ (contract.schema.json y contract/validate_contract.py).
"""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
API = HERE.parent                       # app/backend/api
REPO = API.parents[2]                   # raiz del repo
DATA = REPO / "app" / "data"
CONTRACT_DIR = DATA / "contract"
SAMPLE = DATA / "cache" / "pipeline" / "atom" / "torre-pacheco_demo_viewport.geojson"   # 66 recintos alrededor de la parcela demo

DEMO = {"lat": 37.7383, "lon": -0.98838}
DEMO_RECINTO = {"provincia": 30, "municipio": 37, "agregado": 0, "zona": 0, "poligono": 18, "parcela": 426, "recinto": 1}
VALLADOLID = {"lat": 41.65, "lon": -4.72}   # fuera de cobertura y sin cache de clima/suelo


def _cargar_validador():
    spec = importlib.util.spec_from_file_location("validate_contract", CONTRACT_DIR / "validate_contract.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = _cargar_validador()
SCHEMA = json.loads((DATA / "contract.schema.json").read_text(encoding="utf-8"))


def validar(doc: dict) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """(errores de esquema, invariantes en FALLO) segun app/data/contract/validate_contract.py. Los AVISO no cuentan."""
    ee = V.validar(doc, SCHEMA)
    fallos = [(n, m) for n, nivel, m in V.check_invariantes(doc) if m and nivel == "error"]
    return ee, fallos


def assert_valido(doc: dict):
    ee, fallos = validar(doc)
    assert not ee, ee
    assert not fallos, fallos
