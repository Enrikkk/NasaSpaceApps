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
