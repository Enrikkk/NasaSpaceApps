"""Punto de extension del motor: borrador por defecto y adaptador del JSON de enrique (rama t012-motor-nucleo)."""
import json
import os
from pathlib import Path

import pytest

import engine_adapter as EA
from conftest import DEMO, SCHEMA, V, assert_valido


def _enrique():
    p = os.environ.get("ENRIQUE_JSON")
    if not p or not Path(p).exists():
        pytest.skip("define ENRIQUE_JSON=/ruta/torre-pacheco.json (git show origin/t012-motor-nucleo:app/data/torre-pacheco.json)")
    return json.loads(Path(p).read_text(encoding="utf-8"))


def test_motor_por_defecto_es_el_borrador(client_mini):
    d = client_mini.post("/analyze", json=DEMO).json()
    assert d["_meta"]["motor"].startswith("borrador") and [r["id"] for r in d["rotaciones"]] == ["actual", "alt-a", "alt-b"]


def test_engine_json_inexistente_cae_al_borrador(make_client, atom_mini, tmp_path):
    c = make_client(atom_mini, engine_json=str(tmp_path / "no.json"))
    assert c.post("/analyze", json=DEMO).json()["_meta"]["motor"].startswith("borrador")


def test_adaptador_estructura(tmp_path):
    out = EA.adapt_enrique(_enrique())
    ids = [r["id"] for r in out.rotaciones]
    assert len(ids) >= 3 and len(set(ids)) == len(ids) and sum(bool(r.get("es_actual")) for r in out.rotaciones) == 1
    for r in out.rotaciones:
        assert "escenarios" not in r and "semaforo_legal" not in r and r["_status"] in ("real", "simulado")
        assert len(r.get("escenarios_margen_eur_ha", [])) == out.escenarios_meta["n"]
        assert r["anios"] and all(isinstance(a, list) for a in r["anios"])
    assert out.escenarios_meta["rotaciones_orden"] == ids


def test_enchufar_el_json_de_enrique_no_cambia_los_endpoints(make_client, atom_mini):
    """Mismos endpoints y misma forma; el semaforo legal se recalcula con las rotaciones de enrique."""
    ruta = os.environ.get("ENRIQUE_JSON")
    _enrique()
    c = make_client(atom_mini, engine_json=ruta)
    d = c.post("/analyze", json={**DEMO, "zona": "zona_2"}).json()
    assert d["_meta"]["motor"].startswith("JSON de enrique") and len(d["rotaciones"]) >= 3
    for r in d["rotaciones"]:
        s = r["semaforo_legal"]
        assert s["color"] in ("verde", "amarillo", "rojo") and s["comprobaciones"] and "supuestos" not in s   # usa plan_anios
    assert d["parcela"]["_status"] == "precalculado" and d["clima"]["_status"] == "real"
    # cuanto falta para cumplir el esquema: informativo (el JSON de enrique aun no es contrato v1)
    errores = V.validar(d, SCHEMA)
    print(f"\n[informativo] esquema con el JSON de enrique enchufado: {len(errores)} errores")
    for e in errores[:12]:
        print("   -", e)
