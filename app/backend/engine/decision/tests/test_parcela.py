"""Tests of the per-parcel engine (H-002): run_parcel, suitability wiring, reference rotation, labels, J1 fixes."""
import functools
import json

from app.backend.engine import build as bd, parcela as pc
from app.backend.engine.decision import texts

DEMO = {"parcel_id": "demo", "lat": 37.7383, "lon": -0.98838, "area_ha": 4.0, "regadio": True, "pendiente_pct": 1.2,
        "suelo": {"textura": "franco-arcillosa", "ph": 8.1, "materia_organica_pct": 1.4, "salinidad_ce_dsm": None,
                  "profundidad_cm": None, "drenaje": None},
        "zona_legal": "zona_2", "cultivos_declarados": []}


@functools.lru_cache(maxsize=None)
def _base():
    return bd.build("torre-pacheco", allow_restricted=True)


@functools.lru_cache(maxsize=None)
def _run(**changes):
    return bd.run_parcel({**DEMO, **{k: (list(v) if isinstance(v, tuple) else v) for k, v in changes.items()}},
                         allow_restricted=True)


def _money(o):
    return {r["id"]: (r["margen_eur_ha"], r["exito_pct"]["valor"], r["agua_m3_ha"], r["escenarios"]) for r in o["rotaciones"]}


def test_demo_parcel_keeps_the_same_money_as_the_default_build():
    assert _money(_run()) == _money(_base())


def test_empty_input_runs_and_invents_nothing():
    o = bd.run_parcel({}, allow_restricted=True)
    assert _money(o) == _money(_base())
    assert set(o["idoneidad"]["sin_dato"]) >= {"regadio", "pendiente_pct", "ph", "textura"}
    assert o["idoneidad"]["factores_puntuacion"] == {} and o["idoneidad"]["excluidos"] == []
    assert all(r["idoneidad"]["factor_puntuacion"] == 1.0 for r in o["rotaciones"])
    assert all("totales_parcela" not in r for r in o["rotaciones"])


def test_rainfed_parcel_is_not_evaluable_and_says_why():
    o = _run(regadio=False)
    assert o["rotaciones"] == []
    assert "secano" in o["no_evaluable"]["motivo"]
    assert len(o["idoneidad"]["excluidos"]) == 4
    assert o["actual_origen"] == "sin_referencia"


def test_steep_slope_lowers_the_score_not_the_money():
    flat, steep = _run(), _run(pendiente_pct=25.0)
    assert _money(steep) == _money(flat)
    assert all(r["idoneidad"]["factor_puntuacion"] == 0.65 for r in steep["rotaciones"])
    assert all(r["idoneidad"]["factor_puntuacion"] == 1.0 for r in flat["rotaciones"])
    assert any("35 %" in f and "supuesto" in f for f in steep["idoneidad"]["frases"])
    assert _run(pendiente_pct=15.0)["rotaciones"][0]["idoneidad"]["factor_puntuacion"] == 0.85


def test_option_factor_is_the_mean_of_its_cycles():
    class O:
        keys = (("a", "01-01"), ("b", "05-01"))
    assert pc.option_factor(O, {"a": 0.5}) == 0.75
    class Empty:
        keys = ()
    assert pc.option_factor(Empty, {}) == 1.0


def test_declared_crop_in_catalog_becomes_the_reference():
    o = bd.run_parcel({**DEMO, "cultivos_declarados": [{"cultivo": "BRÓCOLI", "sistema_explotacion": "R"}]}, allow_restricted=True)
    ref = next(r for r in o["rotaciones"] if r["es_actual"])
    assert o["actual_origen"] == "declaracion_fega"
    assert ref["anios"] == [["brocoli"]] * 3
    assert "FEGA" in ref["nombre"]


def test_declared_crop_outside_catalog_uses_the_area_reference_and_never_says_hoy():
    o = _run(cultivos_declarados=("BARBECHO TRADICIONAL",))
    assert o["actual_origen"] == "supuesto_zona"
    ref = next(r for r in o["rotaciones"] if r["es_actual"])
    assert ref["nombre"].startswith("Referencia de la zona (supuesto)")
    blob = json.dumps([r["texto"] for r in o["rotaciones"]], ensure_ascii=False)
    assert "haces hoy" not in blob and "de hoy" not in blob and "rotación actual" not in blob
    assert any("BARBECHO TRADICIONAL" in f for f in o["idoneidad"]["frases"])
    assert texts.check(o) == []


def test_legal_zone_of_the_request_reaches_the_traffic_light():
    z2 = {r["id"]: r["semaforo_legal"]["color"] for r in _run()["rotaciones"]}
    sin = {r["id"]: r["semaforo_legal"]["color"] for r in _run(zona_legal=None)["rotaciones"]}
    assert set(sin.values()) == {"amarillo"}
    assert "verde" in z2.values()


def test_environment_label_and_totals_are_present():
    o = _run()
    for r in o["rotaciones"]:
        assert r["ambiente"]["nivel"] in ("alto", "medio", "bajo") and r["ambiente"]["estado"] == "supuesto"
        if r["margen_eur_ha"]:
            assert r["totales_parcela"]["margen_eur"]["p50"] == round(r["margen_eur_ha"]["p50"] * 4.0)
    assert all(r["ambiente"]["nivel"] in ("alto", "medio", "bajo") for r in _base()["rotaciones"])


def test_climate_origin_states_the_single_station_and_the_distance():
    near, far = _run()["clima_origen"], _run(lat=38.1, lon=-1.86)["clima_origen"]
    assert near["distancia_a_parcela_referencia_km"] == 0 and not near["lejos"]
    assert far["lejos"] and "menos fiables" in far["frase"]


def test_root_alineados_and_no_unformatted_braces():
    for o in (_base(), _run(), bd.build("torre-pacheco", allow_restricted=False)):
        con = [r for r in o["rotaciones"] if isinstance(r.get("escenarios"), list)]
        assert o["escenarios_meta"]["alineados"] is (bool(con) and all(r["escenarios_meta"]["alineados"] for r in con))
        blob = json.dumps(o, ensure_ascii=False)
        assert "{sim" not in blob and "{r[" not in blob and "']}" not in blob
    assert _base()["escenarios_meta"]["alineados"] is True


def test_run_parcel_rejects_non_dict():
    try:
        bd.run_parcel(None)
    except TypeError:
        return
    raise AssertionError("run_parcel(None) debe fallar")
