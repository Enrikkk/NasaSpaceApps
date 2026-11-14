"""Semaforo legal: app.backend.rules.check() sobre las rotaciones; colores esperados (app/backend/rules/README.md) y zona por peticion."""
import pytest

from app.backend.api import legal_blocks
from api_helpers import DEMO, assert_valido

ESPERADO = {   # actual, alt-a, alt-b
    "zona_2": ["verde", "verde", "verde"],
    "por_verificar": ["amarillo", "amarillo", "amarillo"],
    "zona_1": ["rojo", "verde", "amarillo"],
}


@pytest.mark.parametrize("zona", list(ESPERADO))
def test_colores_por_zona(client_mini, zona):
    d = client_mini.post("/analyze", json={**DEMO, "zona": zona}).json()
    assert_valido(d)
    assert [r["semaforo_legal"]["color"] for r in d["rotaciones"]] == ESPERADO[zona]
    assert d["_meta"]["consulta"]["zona_legal"] == zona
    for r in d["rotaciones"]:
        s = r["semaforo_legal"]
        assert s["zona"] == zona and s["nota"].startswith("Herramienta de apoyo") and s["_status"] == "simulado"
        assert s["comprobaciones"] and all(c["estado"] == "por_verificar" for c in s["comprobaciones"])
        assert all(c["resultado"] in ("ok", "falla", "no_aplica", "no_evaluable") for c in s["comprobaciones"])
        assert "ciclos_por_anio = 1" in s["supuestos"][0]


def test_zona_por_defecto_por_verificar(client_mini):
    d = client_mini.post("/analyze", json=DEMO).json()
    assert d["_meta"]["consulta"]["zona_legal"] == "por_verificar"


def test_semaforo_distinto_al_del_borrador(client_mini):
    """El borrador afirmaba verde para alt-a/alt-b con la zona sin verificar; el semaforo calculado no."""
    d = client_mini.post("/analyze", json=DEMO).json()
    assert d["rotaciones"][1]["semaforo_legal"]["color"] == "amarillo"


@pytest.mark.parametrize("nombre,esperado", [
    ("Alcachofa (gorda)", "alcachofa"), ("Lechuga iceberg", "lechuga"), ("Melón piel de sapo", "melon"),
    ("Brócoli", "Brócoli"), ("cubierta de veza", "cubierta"), ("barbecho", "barbecho"),
])
def test_canon_cultivo(nombre, esperado):
    assert legal_blocks.canon_cultivo(nombre) == esperado


def test_rotacion_con_anios_no_necesita_supuesto():
    ent, sup = legal_blocks.entrada_legal({"ciclos": ["a"], "anios": [["lechuga"], ["melon"]]})
    assert sup == [] and ent["ciclos"] == ["lechuga", "melon"] and "ciclos_por_anio" not in ent
