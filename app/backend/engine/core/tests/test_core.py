"""Run: python3 -m pytest app/backend/engine/core/tests -q"""
import datetime as dt

from app.backend.engine.core import data, stats, submodels as sm
from app.backend.engine.core.evaluate import evaluate


def test_wilson_n20_matches_research_table():
    # research/predictive-model-research.md: 0 bad of 20 -> Wilson 0-0.161; 2 -> 0.028-0.301
    assert stats.wilson(0, 20)[0] == 0.0 and abs(stats.wilson(0, 20)[1] - 0.161) < 1e-3
    lo, hi = stats.wilson(2, 20)
    assert abs(lo - 0.028) < 1e-3 and abs(hi - 0.301) < 1e-3


def test_jeffreys_n20():
    assert abs(stats.jeffreys(0, 20)[1] - 0.117) < 2e-3
    lo, hi = stats.jeffreys(4, 20)
    assert abs(lo - 0.072) < 2e-3 and abs(hi - 0.408) < 2e-3


def test_cvar_is_mean_of_4_worst_of_20():
    assert stats.cvar(list(range(20)), 0.8) == 1.5


def test_kc_curve_fao56_shape():
    k = sm.kc_curve((2, 2, 2, 2), 0.5, 1.0, 0.8)
    assert k == [0.5, 0.5, 0.75, 1.0, 1.0, 1.0, 0.9, 0.8]


def test_damage_graded_cold_and_heat():
    assert sm.daily_damage(0.5, 0.0, -2.0) == 0.0
    assert sm.daily_damage(-1.0, 0.0, -2.0) == 0.5
    assert sm.daily_damage(-5.0, 0.0, -2.0) == 1.0
    assert sm.daily_damage(39.0, 35.0, 43.0) == 0.5


def _crop(**p):
    c = data.Crop("test")
    for k, v in p.items():
        c.params[k] = data.Param(v, "", "TEST", "A", "sourced", "")
    return c


def _climate(n=800, tmin=5.0):
    d0 = dt.date(2010, 1, 1)
    return {d0 + dt.timedelta(days=i): data.Day(tmin, 25.0, 0.0, 3.0) for i in range(n)}


def test_frost_year_is_bad_and_counted():
    c = _crop(stages_days="10/10/10/10", kc_ini=0.5, kc_mid=1.0, kc_end=0.8, frost_t0=0.0, frost_t100=-2.0,
              sowing_month=1.0)
    clim = _climate()
    clim[dt.date(2010, 1, 15)] = data.Day(-1.0, 10.0, 0.0, 1.0)  # one night: 50 % damage in 2010
    r = evaluate(c, clim, {}, {2018: 100.0, 2025: 120.0})
    assert r["exito_pct"]["n"] == 3 and r["exito_pct"]["k_malos"] == 1  # cycles from Jan 2010, 2011, 2012
    assert abs(r["anios"][0]["perdida_helada"] - 0.5) < 1e-9


def test_nothing_tested_is_not_shown_as_100():
    c = _crop(stages_days="10/10/10/10", kc_ini=0.5, kc_mid=1.0, kc_end=0.8, sowing_month=1.0)
    r = evaluate(c, _climate(), {}, {2018: 100.0, 2025: 120.0})
    assert r["exito_pct"]["valor"] is None


def test_water_no_rain_equals_gross_of_etc():
    c = _crop(stages_days="10/10/10/10", kc_ini=1.0, kc_mid=1.0, kc_end=1.0)
    w = sm.water(c, list(_climate(40).values()), (10, 10, 10, 10))
    assert abs(w["etc_mm"] - 120.0) < 1e-9 and abs(w["bruto_m3_ha"] - 120.0 / 0.9 * 10) < 1e-6


def test_salt_fao29_lettuce():
    c = _crop(ece_threshold=1.3, ece_slope=13.0)
    assert abs(sm.salt_factor(c, 2.0) - (100 - 13.0 * (3.0 - 1.3)) / 100) < 1e-9
    assert sm.salt_factor(c, None) is None


def test_real_data_runs():
    crops = data.load_crops()
    clim, meta = data.load_climate()
    r = evaluate(crops["brocoli"], clim, data.load_prices(), data.load_hicp(), data.load_area())
    assert r["exito_pct"]["n"] >= 19 and r["margen_eur_ha"]["euros_de"] == 2025


def test_price_trend_only_when_backtest_wins():
    from app.backend.engine.core import price
    import numpy as np
    rng = np.random.default_rng(0)
    flat = {2000 + i: 1.0 + float(v) for i, v in enumerate(rng.normal(0, 0.3, 25))}  # pure noise, no trend
    trend = {2000 + i: 2.0 - 0.05 * i + (0.01 if i % 2 else -0.01) for i in range(20)}  # strong fall
    assert not price.backtest(flat)["usa_tendencia"]
    adj, info = price.scenarios(trend, 2025)
    assert info["usa_tendencia"] and abs(adj[2000] - (2.0 - 0.05 * 25 - 0.01)) < 0.02


def _priced_crop(**extra):
    return _crop(stages_days="10/10/10/10", kc_ini=0.5, kc_mid=1.0, kc_end=0.8, sowing_month=1.0,
                 coste_total=1000.0, coste_unitario=0.5, recoleccion=200.0, **extra)


def test_year_without_price_is_left_out_not_counted_good():
    # Arturo review #88 (1): a harvest year with no price must not enter the success count as a good year
    c = _priced_crop(frost_t0=0.0, frost_t100=-2.0)
    clim = _climate(800)
    prices = {"test": {2010: 1.0}}  # 2011 and 2012 have no price
    r = evaluate(c, clim, prices, {2010: 100.0, 2011: 100.0, 2012: 100.0, 2015: 100.0, 2018: 100.0, 2025: 100.0})
    assert r["exito_pct"]["n"] == 1 and r["exito_pct"]["anios_totales"] == 3
    assert any("sin precio" in g for g in r["huecos"])


def test_money_only_label_when_no_climate_thresholds():
    # Arturo review #88 (2): price/cost present but no thresholds -> must say SOLO ECONÓMICO
    c = _priced_crop()
    r = evaluate(c, _climate(800), {"test": {2010: 1.0, 2011: 1.0, 2012: 1.0}},
                 {y: 100.0 for y in (2010, 2011, 2012, 2015, 2018, 2025)})
    assert r["exito_pct"]["definicion"].startswith("SOLO ECONÓMICO")


def test_cost_uses_its_own_base_year():
    # Arturo #86: an ECREA 2021 cost must be deflated from 2021, not 2018
    c = _priced_crop()
    c.params["coste_total"].base_year = 2021
    hicp = {2010: 100.0, 2011: 100.0, 2012: 100.0, 2015: 100.0, 2018: 50.0, 2021: 100.0, 2025: 100.0}
    r = evaluate(c, _climate(800), {"test": {2010: 1.0}}, hicp)
    assert abs(r["anios"][0]["coste_eur_ha"] - 1000.0) < 1e-6  # 2021 -> 2025 factor 1, not 2018's factor 2


def test_harvest_cost_exported_separately():
    c = _priced_crop()
    r = evaluate(c, _climate(800), {"test": {2010: 1.0}}, {y: 100.0 for y in (2010, 2011, 2012, 2015, 2018, 2025)})
    y = r["anios"][0]
    assert abs(y["coste_recoleccion_eur_ha"] - 200.0) < 1e-9 and abs(y["coste_eur_ha"] - 1000.0) < 1e-9


def test_restricted_carm_prices_off_by_default():
    # licence gate: CARM quotes (personal non-commercial use only) never reach an output unless asked for
    c = _priced_crop()
    carm = {("test", "", ""): {2010: {1: (9.0, "eur_kg"), 2: (9.0, "eur_kg")}}}
    hicp = {y: 100.0 for y in (2010, 2011, 2012, 2015, 2018, 2025)}
    open_ = evaluate(c, _climate(800), {}, hicp, carm=carm)
    internal = evaluate(c, _climate(800), {}, hicp, carm=carm, allow_restricted=True)
    assert open_["precio"]["nivel"] is None and not open_["licencia"]["solo_uso_interno"]
    assert internal["precio"]["nivel"] == 1 and internal["licencia"]["solo_uso_interno"]
