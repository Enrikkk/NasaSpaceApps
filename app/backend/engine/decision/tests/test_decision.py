"""Tests of the decision layer (T-020): rules, calendar fit, DP, shared scenarios, open-data build."""
import json

from app.backend.engine import build as bd
from app.backend.engine.core import data
from app.backend.engine.decision import rotations as rt, rules, strategies as st


class FakeCrops(dict):
    pass


class C:
    def __init__(self, fam):
        self.fam = fam

    def get(self, k, d=None):
        return self.fam if k == "family" else d


CROPS = {"melon": C("Cucurbitaceae"), "lechuga": C("Asteraceae"), "alcachofa": C("Asteraceae"), "brocoli": C("Brassicaceae")}


def test_allowed_family_and_group1():
    assert not rules.allowed(CROPS, "lechuga", "alcachofa")      # same family twice in a row
    assert not rules.allowed(CROPS, "lechuga", "brocoli")        # two group-1 crops in a row (art. 51)
    assert rules.allowed(CROPS, "melon", "lechuga")
    assert rules.allowed(CROPS, None, "melon")


def test_fits_overlap_and_gap():
    a = {"start_doy": 121, "days": 120}
    b = {"start_doy": 244, "days": 135}       # melon ends day 241 + 14 days gap = 255 > 244: overlap
    c = {"start_doy": 258, "days": 135}       # 15 days later: fits, and wraps to day 28 before melon
    assert not rt.fits([a, b])
    assert rt.fits([a, c])
    assert not rt.fits([{"start_doy": 100, "days": 360}])


def test_winter_bare_run_counts_only_oct_mar():
    occ = rt.occupancy([{"start_doy": 121, "days": 120}])     # May-Aug: Oct-Mar is all bare
    assert rt.winter_bare_run(occ) == 182
    occ = rt.occupancy([{"start_doy": 288, "days": 105}])     # Oct 15 - Jan 27
    assert rt.winter_bare_run(occ) < 182


def test_normalise_rotations_range_and_none():
    raws = [{"margen": 100, "agua": 5, "suelo_n": 0.1, "riesgo": -10}, {"margen": 300, "agua": 9, "suelo_n": 0.9, "riesgo": -50},
            {"margen": None, "agua": 7, "suelo_n": 0.5, "riesgo": None}]
    c = st.normalise_rotations(raws)
    assert c[1]["margen"] == 1.0 and c[0]["margen"] == 0.0 and c[2]["margen"] is None
    assert c[0]["agua"] == 1.0 and c[1]["agua"] == 0.0           # less water is better
    assert c[0]["riesgo"] == 1.0                                 # higher CVaR is better


def test_scenarios_share_the_same_year_and_cost():
    out = bd.build("torre-pacheco", allow_restricted=True)
    ev = [r for r in out["rotaciones"] if r.get("escenarios")]
    assert len(ev) >= 2
    ref = ev[0]["escenarios_meta"]
    assert ref["alineados"] is True and ref["n_anios_comunes"]
    for r in ev:
        meta = r["escenarios_meta"]
        assert meta["alineados"] is True
        assert meta["anio_clima"] == ref["anio_clima"]
        assert meta["factor_coste"] == ref["factor_coste"]
        for i, (years, cost) in enumerate(zip(meta["anio_clima"], meta["factor_coste"])):
            assert years == ref["anio_clima"][i] and cost == ref["factor_coste"][i]
        assert r["exito_pct"]["n"] == r["exito_pct"]["n_anios_historicos"] == r["exito_pct"]["n_efectivo"]
        assert r["exito_pct"]["n_muestras"] > r["exito_pct"]["n"]


def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _strings(v)


def test_exported_texts_have_no_format_braces_and_root_alignment():
    out = bd.build("torre-pacheco", allow_restricted=True)
    bad = [s for s in _strings(out) if "{" in s or "}" in s]
    assert bad == []
    ev = [r for r in out["rotaciones"] if r.get("escenarios")]
    assert out["escenarios_meta"]["alineados"] is True
    assert out["escenarios_meta"]["alineados"] is all(r["escenarios_meta"]["alineados"] for r in ev)
    assert "n_muestras = " in out["rotaciones"][0]["exito_pct"]["definicion"]
    assert "{sim" not in out["rotaciones"][0]["exito_pct"]["definicion"]


def test_shared_draws_deterministic():
    assert st.draws()[:3] == st.draws()[:3] and len(st.draws()) == st.N_SAMPLES


def test_open_build_is_publishable():
    out = bd.build("torre-pacheco", allow_restricted=False)
    text = json.dumps(out, ensure_ascii=False).lower()
    assert "carm-anuario" not in text and "anuarios" not in text and out["licencia"]["incluye_precios_carm"] is False
    rots = out["rotaciones"]
    assert len(rots) >= 3 and rots[0]["es_actual"]
    for r in rots:
        for k in ("criterios", "escenarios", "semaforo_legal", "evidencia", "huecos", "riesgos", "variantes", "inversion", "agua_detalle"):
            assert k in r
        assert set(r["variantes"]) == set(bd.VARIANTS)
        if r["escenarios"] is not None:
            assert len(r["escenarios"]) == st.N_SAMPLES
    alt = [r for r in rots if not r["es_actual"]]
    for r in alt:   # DP never puts the same botanical family twice in a row
        seq = [c for p in r["plan_anios"] for c in p["ciclos"] if c not in ("barbecho", "cubierta de veza")]
        assert all(a != b for a, b in zip(seq, seq[1:]))


def test_unpriced_rotation_is_not_evaluable_not_optimistic():
    out = bd.build("torre-pacheco", allow_restricted=False)
    actual = out["rotaciones"][0]
    assert actual["exito_pct"]["valor"] is None and actual["margen_eur_ha"] is None
    assert any("NO evaluables" in h for h in actual["huecos"])


def test_default_build_cites_carm_and_states_permission_pending():
    out = bd.build("torre-pacheco", allow_restricted=True)
    assert out["licencia"]["incluye_precios_carm"] is True and "pendiente" in out["licencia"]["estado"]
    actual = out["rotaciones"][0]
    assert actual["exito_pct"]["valor"] is not None                     # lettuce now has a Murcia price
    assert any(e["fuente_id"] == "CARM-ANUARIO" for r in out["rotaciones"] for e in r["evidencia"])
    assert "abiertos" not in out["_status"].lower()                       # no claim that every source is open
