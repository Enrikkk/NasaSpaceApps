"""T-022: template text layer. Run: python3 -m pytest -q app/backend/engine"""
import copy

import pytest

from app.backend.engine import build as bd
from app.backend.engine.decision import texts


@pytest.fixture(scope="module", params=[True, False], ids=["con_carm", "abierto"])
def out(request):
    return bd.build("torre-pacheco", allow_restricted=request.param)


def _all_strings(r):
    t = r["texto"]
    return [t["por_que"], t["consulta"], r["por_que"]] + t["evidencia_resumen"] + t["no_sabemos"] + t["riesgos_texto"]


def test_texts_exist_and_validate(out):
    assert texts.check(out) == []
    assert len(out["rotaciones"]) >= 2
    for r in out["rotaciones"]:
        t = r["texto"]
        assert set(t) == {"por_que", "evidencia_resumen", "no_sabemos", "riesgos_texto", "consulta"}
        assert r["por_que"] == t["por_que"]
        assert t["consulta"] == "Herramienta de apoyo. Consulta a tu técnico agrícola antes de decidir."
        assert t["evidencia_resumen"] and t["no_sabemos"] and t["riesgos_texto"]
        assert 2 <= len(t["por_que"].split(". ")) <= 5
        assert "provisional" in t["por_que"]          # legal light is always labelled provisional
        assert "técnico" in t["consulta"]


def test_no_none_or_nan(out):
    for r in out["rotaciones"]:
        for s in _all_strings(r):
            assert "None" not in s and "nan" not in s.lower().split() and "NaN" not in s


def test_validator_catches_planted_wrong_number(out):
    bad = copy.deepcopy(out)
    alt = next(r for r in bad["rotaciones"] if not r["es_actual"])
    alt["texto"]["por_que"] += " Dejaría 98.765 € más."
    alt["texto"]["evidencia_resumen"].append("Sale bien el 13,37 % de los años.")
    found = texts.check(bad)
    assert {n for i, n, s in found} == {"98.765", "13,37"}
    assert all(i == alt["id"] for i, _, _ in found)


def test_apply_refuses_to_ship_a_wrong_number(out, monkeypatch):
    orig = texts._eur
    monkeypatch.setattr(texts, "_eur", lambda v: orig(v + 12345))   # simulate a formatter bug
    with pytest.raises(AssertionError, match="no respaldados"):
        texts.apply(copy.deepcopy(out))


def test_numbers_in_parses_spanish_format():
    assert texts.numbers_in("3.956 € y 2,2 meses, el 73 % en 2019") == [3956.0, 2.2, 73.0, 2019.0]
    assert texts.numbers_in("sin cifras") == []


def test_derived_numbers_are_accepted(out):
    ref = next(r for r in out["rotaciones"] if r["es_actual"])
    alt = next(r for r in out["rotaciones"] if not r["es_actual"])
    d = abs(alt["agua_m3_ha"] - ref["agua_m3_ha"])
    p = d / ref["agua_m3_ha"] * 100
    ok = dict(out, rotaciones=[ref, copy.deepcopy(alt)])
    ok["rotaciones"][1]["texto"] = {"por_que": f"Gasta {texts._n(d)} m³ de diferencia, un {texts._n(p)} %.",
                                    "evidencia_resumen": [], "no_sabemos": [], "riesgos_texto": [], "consulta": ""}
    assert texts.check(ok) == []


def test_null_margin_says_money_comparison_impossible():
    o = bd.build("torre-pacheco", allow_restricted=False)
    ref = next(r for r in o["rotaciones"] if r["es_actual"])
    if ref["margen_eur_ha"] is not None:
        pytest.skip("la rotación actual ya tiene precio abierto")
    alts = [r for r in o["rotaciones"] if not r["es_actual"]]
    assert alts
    for r in alts:
        assert "No podemos comparar el dinero" in r["texto"]["por_que"]
        assert "precio" in r["texto"]["por_que"]
        assert "Eurostat" in " ".join(r["texto"]["no_sabemos"]) and "optimista para Murcia" in " ".join(r["texto"]["no_sabemos"])
    assert "No sale cifra de dinero" in ref["texto"]["por_que"]


def test_money_comparison_with_prices():
    o = bd.build("torre-pacheco", allow_restricted=True)
    ref = next(r for r in o["rotaciones"] if r["es_actual"])
    assert ref["margen_eur_ha"] is not None
    for r in o["rotaciones"]:
        if not r["es_actual"]:
            assert "frente a" in r["texto"]["por_que"]
            assert "orientativas de la CARM" in " ".join(r["texto"]["no_sabemos"])


def test_sin_evidencia_sentence_when_stage_has_that_level(out):
    for r in out["rotaciones"]:
        has = any(e["nivel"] == "sin evidencia" for b in r["riesgo_etapas"] for e in b["etapas"])
        joined = " ".join(r["texto"]["riesgos_texto"])
        if has:
            assert "sin evidencia" in joined and "no es lo mismo que riesgo bajo" in joined
        else:
            assert "sin evidencia" not in joined


def test_sin_evidencia_when_planted_and_absent_otherwise(out):
    r = copy.deepcopy(next(x for x in out["rotaciones"] if not x["es_actual"]))
    for b in r["riesgo_etapas"]:
        b["etapas"] = [e for e in b["etapas"] if e["nivel"] != "sin evidencia"]
    assert "sin evidencia" not in " ".join(texts._riesgos(r))
    r["riesgo_etapas"][0]["etapas"].append({"id": "x", "nivel": "sin evidencia"})
    assert "no es lo mismo que riesgo bajo" in " ".join(texts._riesgos(r))


def test_medium_stage_risk_is_reported():
    o = bd.build("torre-pacheco", allow_restricted=True)
    medios = [r for r in o["rotaciones"] if any(e["nivel"] in ("medio", "alto") for b in r["riesgo_etapas"] for e in b["etapas"])]
    assert medios, "se espera al menos una rotación con etapa de riesgo medio (alcachofa, helada en capítulos)"
    for r in medios:
        assert any("riesgo medio" in s or "riesgo alto" in s for s in r["texto"]["riesgos_texto"])


def test_apply_is_idempotent(out):
    again = copy.deepcopy(out)
    texts.apply(again)
    assert [r["texto"] for r in again["rotaciones"]] == [r["texto"] for r in out["rotaciones"]]
