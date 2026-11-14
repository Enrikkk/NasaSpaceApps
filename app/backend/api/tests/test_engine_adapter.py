"""Punto de extension del motor: ejemplo por defecto y adaptador v1.1 del JSON de enrique (rama t012-motor-nucleo).

ENRIQUE_JSON=/ruta/torre-pacheco.json (git show origin/t012-motor-nucleo:app/data/torre-pacheco.json) activa los tests con el
JSON real de enrique; el resto usan un JSON sintetico con su forma, sin depender de otra rama.
"""
import copy
import json
import os
from pathlib import Path

import pytest

from app.backend.api import engine_adapter as EA
from api_helpers import DATA, DEMO, assert_valido, validar


def _enrique_real():
    p = os.environ.get("ENRIQUE_JSON")
    if not p or not Path(p).exists():
        pytest.skip("define ENRIQUE_JSON=/ruta/torre-pacheco.json (git show origin/t012-motor-nucleo:app/data/torre-pacheco.json)")
    return p


@pytest.fixture
def enrique_sintetico(tmp_path):
    """JSON con la forma del de enrique (campos `_estado_bloques`, `plan_anios`, `escenarios`...), hecho con las rotaciones del ejemplo."""
    ej = json.loads((DATA / "torre-pacheco.contract.example.json").read_text(encoding="utf-8"))
    rots = []
    for i, r in enumerate(copy.deepcopy(ej["rotaciones"])):
        r.pop("_status", None)
        r["anios"] = [["melon", "lechuga"], ["brocoli"]] if i == 0 else [["lechuga"], ["melon"]]
        r["plan_anios"] = [{"anio_plan": k + 1, "ciclos": a} for k, a in enumerate(r["anios"])]
        rots.append(r)
    doc = {"_status": "MOCK sintetico de test", "_estado_bloques": {"rotaciones": "real", "semaforo_legal": "provisional"},
           "rotaciones": rots, "fuentes": ej["fuentes"] + [{"id": "FUENTE-MOTOR", "nombre": "Fuente solo del motor", "url": "https://example.org",
                                                           "licencia": "por verificar", "licencia_estado": "verify"}]}
    ruta = tmp_path / "enrique.json"
    ruta.write_text(json.dumps(doc), encoding="utf-8")
    return ruta


def test_motor_por_defecto_es_el_ejemplo(client_mini):
    d = client_mini.post("/analyze", json=DEMO).json()
    assert d["_meta"]["motor"].startswith("borrador") and [r["id"] for r in d["rotaciones"]] == ["actual", "alt-a", "alt-b"]
    assert d["escenarios_meta"]["alineados"] is False   # D-011: no alineado hasta que enrique lo declare


def test_engine_json_inexistente_cae_al_ejemplo(make_client, atom_mini, tmp_path):
    c = make_client(atom_mini, engine_json=str(tmp_path / "no.json"))
    assert c.post("/analyze", json=DEMO).json()["_meta"]["motor"].startswith("borrador")


def test_engine_json_corrupto_cae_al_ejemplo(make_client, atom_mini, tmp_path):
    malo = tmp_path / "malo.json"
    malo.write_text("[1, 2, 3]", encoding="utf-8")
    c = make_client(atom_mini, engine_json=str(malo))
    assert c.post("/analyze", json=DEMO).json()["_meta"]["motor"].startswith("borrador")


def test_adaptador_estructura(enrique_sintetico):
    out = EA.adapt_enrique(json.loads(enrique_sintetico.read_text(encoding="utf-8")))
    ids = [r["id"] for r in out.rotaciones]
    assert len(ids) >= 3 and len(set(ids)) == len(ids) and sum(bool(r.get("es_actual")) for r in out.rotaciones) == 1
    for r in out.rotaciones:
        assert "semaforo_legal" not in r and "escenarios_margen_eur_ha" not in r and r["_status"] == "real"
        assert r["anios"] and all(isinstance(a, list) for a in r["anios"])
    assert out.escenarios_meta["alineados"] is False and out.escenarios_meta["n"] == len(out.rotaciones[0]["escenarios"])
    assert "FUENTE-MOTOR" in {f["id"] for f in out.fuentes}


def test_enchufar_el_json_sintetico_no_cambia_los_endpoints(make_client, atom_mini, enrique_sintetico):
    """Mismos endpoints y misma forma; el semaforo legal se recalcula con las rotaciones/anios del motor; sus fuentes se citan."""
    c = make_client(atom_mini, engine_json=str(enrique_sintetico))
    d = c.post("/analyze", json={**DEMO, "zona": "zona_2"}).json()
    assert d["_meta"]["motor"].startswith("JSON de enrique") and len(d["rotaciones"]) >= 3
    assert d["_meta"]["estado_bloques"]["rotaciones"] == "real"
    assert {r["semaforo_legal"]["_status"] for r in d["rotaciones"]} == {"simulado"}   # reglas por_verificar: nunca `real`
    for r in d["rotaciones"]:
        s = r["semaforo_legal"]
        assert s["color"] in ("verde", "amarillo", "rojo") and s["comprobaciones"] and "supuestos" not in s   # usa anios del motor
    assert d["parcela"]["_status"] == "precalculado" and d["clima"]["_status"] == "real"
    assert "FUENTE-MOTOR" in {f["id"] for f in d["fuentes"]} and "sigpac" in {f["id"] for f in d["fuentes"]}
    assert d["escenarios_meta"]["alineados"] is False
    assert_valido(d)


def test_json_real_de_enrique(make_client, atom_mini):
    """Con el JSON real de la rama de enrique: carga, semaforo recalculado, respuesta sin errores de esquema."""
    ruta = _enrique_real()
    c = make_client(atom_mini, engine_json=ruta)
    d = c.post("/analyze", json={**DEMO, "zona": "zona_2"}).json()
    assert d["_meta"]["motor"].startswith("JSON de enrique") and len(d["rotaciones"]) >= 3
    assert d["escenarios_meta"]["alineados"] is False or d["escenarios_meta"]["alineados"] is True   # lo que declare enrique
    ee, fallos = validar(d)
    print(f"\n[informativo] esquema con el JSON real de enrique: {len(ee)} errores, {len(fallos)} invariantes en FALLO")
    for e in ee[:12]:
        print("   -", e)
    assert not ee and not fallos


def test_alineados_respeta_lo_declarado(enrique_sintetico):
    doc = json.loads(enrique_sintetico.read_text(encoding="utf-8"))
    assert EA.adapt_enrique(doc).escenarios_meta["alineados"] is False
    doc["escenarios_meta"] = {"alineados": True}
    assert EA.adapt_enrique(doc).escenarios_meta["alineados"] is True
