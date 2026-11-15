"""Run: python3 -m pytest app/backend/ndvi -q   (synthetic data only, no network, no credentials)"""
import datetime as dt
import json
import os

import numpy as np
import pytest

from app.backend.ndvi import appeears_csv, appeears_request, bare_soil as bs

MOCK = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "torre-pacheco.mock.json")


# ---- helpers: build raw HLS int16 pixels that have a chosen NDVI ------------------------------------------------------
def raw_pixels(target_ndvi, shape=(3, 3), red=0.10):
    nir = red * (1 + target_ndvi) / (1 - target_ndvi)
    r = np.full(shape, round(red / 0.0001), dtype=np.int16)
    n = np.full(shape, round(nir / 0.0001), dtype=np.int16)
    return r, n


def synthetic_year(bare_months=(7, 8, 9), cloudy=lambda d: False, step=5, year=2025, cover=0.60, bare=0.10):
    """Observation every `step` days over `year`: NDVI `bare` in bare_months else `cover`; cloudy dates get Fmask cloud."""
    obs = []
    d = dt.date(year, 1, 1)
    while d.year == year:
        r, n = raw_pixels(bare if d.month in bare_months else cover)
        fm = np.full((3, 3), 2 if cloudy(d) else 0, dtype=np.uint8)   # 2 = bit 1 = cloud
        obs.append((d, bs.observation_from_bands(r, n, fm)))
        d += dt.timedelta(days=step)
    return obs


# ---- NDVI -------------------------------------------------------------------------------------------------------------
def test_ndvi_values_and_invalid():
    assert float(bs.ndvi(0.1, 0.3)) == pytest.approx(0.5)
    assert float(bs.ndvi(0.2, 0.2)) == 0.0
    assert np.isnan(bs.ndvi(0.0, 0.0))                 # zero denominator
    assert np.isnan(bs.ndvi(np.nan, 0.3))
    assert np.isnan(bs.ndvi(-0.5, 0.2))                # sum <= 0


def test_scale_reflectance_fill_to_nan():
    out = bs.scale_reflectance(np.array([1000, -9999, 0]))
    assert out[0] == pytest.approx(0.1) and np.isnan(out[1]) and out[2] == 0.0


# ---- Fmask (HLS V2.0 User Guide, Table 9) -------------------------------------------------------------------------------
@pytest.mark.parametrize("value,usable", [
    (0, True),
    (2, False),      # bit 1 cloud
    (4, False),      # bit 2 adjacent to cloud/shadow
    (8, False),      # bit 3 cloud shadow
    (16, False),     # bit 4 snow/ice
    (32, False),     # bit 5 water
    (1, True),       # bit 0 cirrus: reserved, unused in V2.0 -> ignored
    (64, True), (128, True), (192, True),   # aerosol level bits alone do not discard a pixel
    (100, False),    # the User Guide's own Appendix A example: adjacent + water + aerosol bit
    (255, False),    # fill value
])
def test_fmask_bits(value, usable):
    assert bool(bs.fmask_clear(np.array([value]))[0]) is usable


def test_fmask_custom_bad_bits_allows_water():
    assert bool(bs.fmask_clear(np.array([32]), bad_bits=(bs.BIT_CLOUD, bs.BIT_SHADOW))[0])


# ---- per-date parcel mean ----------------------------------------------------------------------------------------------
def test_parcel_mean_ignores_masked_pixels():
    n = np.array([0.5, 0.5, 0.5, 0.9])
    clear = np.array([True, True, True, False])            # the 0.9 pixel is cloud -> excluded
    assert bs.parcel_mean_ndvi(n, clear) == pytest.approx(0.5)


def test_parcel_mean_too_cloudy_is_none():
    n = np.full(10, 0.5)
    clear = np.array([True] * 4 + [False] * 6)             # 40% clear < 50%
    assert bs.parcel_mean_ndvi(n, clear) is None
    assert bs.parcel_mean_ndvi(n, np.zeros(10, bool)) is None


def test_observation_from_bands_cloud_and_clear():
    r, n = raw_pixels(0.5)
    assert bs.observation_from_bands(r, n, np.zeros((3, 3), np.uint8)) == pytest.approx(0.5, abs=1e-3)
    assert bs.observation_from_bands(r, n, np.full((3, 3), 2, np.uint8)) is None
    fm = np.zeros((3, 3), np.uint8)
    fm[0, :] = 2                                           # one row cloudy: 6/9 clear -> kept, NDVI still 0.5
    assert bs.observation_from_bands(r, n, fm) == pytest.approx(0.5, abs=1e-3)


# ---- monthly aggregation ----------------------------------------------------------------------------------------------
def test_full_year_bare_jul_sep():
    months = bs.monthly_aggregate(synthetic_year(), "2025-01", "2025-12")
    cls = {m: bs.classify_month(s.ndvi_median) for m, s in months.items()}
    assert [m for m, c in cls.items() if c == bs.DESNUDO] == ["2025-07", "2025-08", "2025-09"]
    assert all(c == bs.CUBIERTO for m, c in cls.items() if m not in ("2025-07", "2025-08", "2025-09"))
    assert all(s.n_observaciones >= 5 for s in months.values())


def test_monthly_median_resists_an_outlier():
    obs = [(dt.date(2025, 3, d), v) for d, v in [(1, 0.6), (6, 0.6), (11, 0.6), (16, 0.05)]]   # one wrong low value
    assert bs.monthly_aggregate(obs)["2025-03"].ndvi_median == pytest.approx(0.6)


def test_cloud_masked_dates_do_not_count():
    # in March only two clear dates survive, the rest is cloudy
    clear_dates = {dt.date(2025, 3, 7), dt.date(2025, 3, 22)}
    obs = synthetic_year(cloudy=lambda d: d.month == 3 and d not in clear_dates, step=5)
    m = bs.monthly_aggregate(obs)["2025-03"]
    assert m.n_observaciones == 2 and m.ndvi_median == pytest.approx(0.6, abs=1e-3)


def test_single_observation_month_is_sin_dato():
    obs = synthetic_year(cloudy=lambda d: d.month == 5 and d != dt.date(2025, 5, 6), step=5)
    m = bs.monthly_aggregate(obs)["2025-05"]
    assert m.n_observaciones == 1 and m.ndvi_median is None
    assert bs.classify_month(m.ndvi_median) == bs.SIN_DATO


def test_fully_cloudy_and_missing_months_are_sin_dato():
    obs = synthetic_year(cloudy=lambda d: d.month == 11, step=5)
    months = bs.monthly_aggregate([o for o in obs if o[0].month != 12], "2025-01", "2025-12")
    assert months["2025-11"] == bs.MonthStat(None, 0)      # observed but always cloudy
    assert months["2025-12"] == bs.MonthStat(None, 0)      # no observation at all, forced by start/end


def test_same_date_two_sensors_count_as_one_clear_date():
    d = dt.date(2025, 4, 10)
    m = bs.monthly_aggregate([(d, 0.5), (d, 0.7)])["2025-04"]
    assert m.n_observaciones == 1 and m.ndvi_median is None   # one date only -> sin dato
    m2 = bs.monthly_aggregate([(d, 0.5), (d, 0.7), (dt.date(2025, 4, 20), 0.6)])["2025-04"]
    assert m2.n_observaciones == 2 and m2.ndvi_median == pytest.approx(0.6)


# ---- thresholds -------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("v,cls", [
    (-0.1, bs.DESNUDO), (0.0, bs.DESNUDO), (0.1999, bs.DESNUDO),
    (0.20, bs.VULNERABLE), (0.30, bs.VULNERABLE), (0.3499, bs.VULNERABLE),
    (0.35, bs.CUBIERTO), (0.8, bs.CUBIERTO), (None, bs.SIN_DATO), (float("nan"), bs.SIN_DATO),
])
def test_thresholds(v, cls):
    assert bs.classify_month(v) == cls


# ---- output block ------------------------------------------------------------------------------------------------------
def test_ndvi_block_shape_matches_mock_plus_extras():
    months = {"2025-07": bs.MonthStat(0.1, 6), "2025-08": bs.MonthStat(0.25, 6), "2025-09": bs.MonthStat(None, 1),
              "2025-10": bs.MonthStat(0.6, 5)}
    blk = bs.ndvi_block(months, "precalculado")
    mock = json.load(open(MOCK))["ndvi"]
    assert set(mock) <= set(blk)
    assert set(blk) == set(mock) | {"meses_sin_dato", "n_observaciones", "_status"}
    assert blk["meses_desnudo"] == ["2025-07"] and blk["meses_vulnerable"] == ["2025-08"]
    assert blk["meses_sin_dato"] == ["2025-09"]
    assert blk["n_observaciones"] == {"2025-07": 6, "2025-08": 6, "2025-09": 1, "2025-10": 5}
    assert blk["_status"] == "precalculado"
    json.dumps(blk)                                          # serialisable


def test_ndvi_block_rejects_bad_status():
    with pytest.raises(ValueError):
        bs.ndvi_block({}, "mock")


def test_end_to_end_synthetic_year_block():
    blk = bs.ndvi_block(bs.monthly_aggregate(synthetic_year(), "2025-01", "2025-12"), "real")
    assert blk["meses_desnudo"] == ["2025-07", "2025-08", "2025-09"]
    assert blk["meses_vulnerable"] == [] and blk["meses_sin_dato"] == [] and blk["_status"] == "real"


# ---- Oct-Mar consecutive bare days --------------------------------------------------------------------------------------
def block(bare=(), vul=(), nodata=(), analysed=None):
    allm = bs.winter_months(2025)
    analysed = allm if analysed is None else analysed
    return {"meses_desnudo": list(bare), "meses_vulnerable": list(vul), "meses_sin_dato": list(nodata),
            "n_observaciones": {m: (0 if m in nodata else 5) for m in analysed}}


def test_winter_window_months():
    assert bs.winter_months(2025) == ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03"]


def test_bare_run_mock_like_oct_to_feb():
    blk = block(bare=["2025-10", "2025-11", "2025-12", "2026-01", "2026-02"])
    assert bs.bare_run_days(blk, 2025) == 31 + 30 + 31 + 31 + 28 == 151


def test_bare_run_summer_bare_is_zero_in_winter():
    blk = bs.ndvi_block(bs.monthly_aggregate(synthetic_year(), "2025-01", "2025-12"), "real")
    assert bs.bare_run_days(blk, 2025) == 0                  # bare Jul-Sep is outside the Oct-Mar window


def test_bare_run_takes_the_longest_run_and_vulnerable_breaks_it():
    blk = block(bare=["2025-10", "2026-01", "2026-02", "2026-03"], vul=["2025-11", "2025-12"])
    assert bs.bare_run_days(blk, 2025) == 31 + 28 + 31 == 90   # Jan-Mar beats Oct


def test_sin_dato_lower_and_upper_bound():
    blk = block(bare=["2025-10", "2025-12", "2026-01"], nodata=["2025-11"], vul=["2026-02", "2026-03"])
    assert bs.bare_run_days(blk, 2025, "break") == 31 + 31            # Dec+Jan = 62
    assert bs.bare_run_days(blk, 2025, "bare") == 31 + 30 + 31 + 31   # Oct-Jan = 123
    assert bs.bare_run_range(blk, 2025) == (62, 123)


def test_months_not_analysed_follow_unknown_policy():
    blk = block(bare=["2025-10", "2025-11"], analysed=["2025-10", "2025-11"])   # Dec-Mar never analysed
    assert bs.bare_run_days(blk, 2025, "break") == 61
    assert bs.bare_run_days(blk, 2025, "bare") == 31 + 30 + 31 + 31 + 28 + 31


def test_two_full_months_vs_sixty_day_limit_is_ambiguous():
    # month granularity: 2 full bare months are 59..62 days, i.e. around rules.BARE_LIMIT_DAYS = 60
    assert bs.bare_run_days(block(bare=["2025-10", "2025-11"]), 2025) == 61
    assert bs.bare_run_days(block(bare=["2026-01", "2026-02"]), 2025) == 59


# ---- AppEEARS request (offline) -----------------------------------------------------------------------------------------
def test_request_body_shape():
    body = appeears_request.build_request()
    assert body["task_type"] == "point" and body["task_name"]
    p = body["params"]
    assert p["dates"] == [{"startDate": "09-01-2024", "endDate": "10-31-2026"}]       # MM-DD-YYYY
    assert {(l["product"], l["layer"]) for l in p["layers"]} == {
        ("HLSL30.020", "B04"), ("HLSL30.020", "B05"), ("HLSL30.020", "Fmask"),
        ("HLSS30.020", "B04"), ("HLSS30.020", "B8A"), ("HLSS30.020", "Fmask")}
    c = p["coordinates"]
    assert len(c) == 9 and len({x["id"] for x in c}) == 9
    assert all(abs(x["latitude"] - 37.7383) < 0.001 and abs(x["longitude"] + 0.98838) < 0.001 for x in c)
    mid = [x for x in c if x["id"] == "p11"][0]
    assert (mid["latitude"], mid["longitude"]) == (37.7383, -0.98838)
    json.dumps(body)


def test_request_single_point():
    assert len(appeears_request.build_request(n=1)["params"]["coordinates"]) == 1


def test_main_prints_without_network(capsys, monkeypatch):
    monkeypatch.delenv("EARTHDATA_USER", raising=False)
    monkeypatch.delenv("EARTHDATA_PASS", raising=False)
    appeears_request.main()
    out = capsys.readouterr().out
    assert '"task_type": "point"' in out and "MANUAL STEPS" in out


def test_credentials_helper_refuses_without_env(monkeypatch):
    for k in ("EARTHDATA_USER", "EARTHDATA_PASS", "EARTHDATA_TOKEN"):
        monkeypatch.delenv(k, raising=False)
    with pytest.raises(RuntimeError):
        appeears_request._token_from_env()                  # raises before any network call


# ---- CSV bridge (synthetic rows; real column names UNVERIFIED) ------------------------------------------------------------
def test_csv_rows_to_observations():
    def rows(date, ndvi_t, fmask, sensor="HLSS30_020", nir="B8A", scaled=True):
        r, n = raw_pixels(ndvi_t, (9,))
        out = []
        for i in range(9):
            rv, nv = (r[i] * 0.0001, n[i] * 0.0001) if scaled else (int(r[i]), int(n[i]))
            out.append({"ID": f"p{i}", "Date": date, f"{sensor}_B04": str(rv), f"{sensor}_{nir}": str(nv),
                        f"{sensor}_Fmask": str(fmask)})
        return out
    obs = appeears_csv.observations_from_rows(rows("2025-10-05", 0.1, 0) + rows("2025-10-10", 0.1, 2)
                                              + rows("2025-10-15", 0.1, 0, scaled=False))
    assert [d.isoformat() for d, _ in obs] == ["2025-10-05", "2025-10-10", "2025-10-15"]
    assert obs[0][1] == pytest.approx(0.1, abs=1e-3) and obs[1][1] is None and obs[2][1] == pytest.approx(0.1, abs=1e-3)
    m = bs.monthly_aggregate(obs)["2025-10"]
    assert m.n_observaciones == 2 and bs.classify_month(m.ndvi_median) == bs.DESNUDO


def test_csv_missing_columns_gives_clear_error():
    with pytest.raises(ValueError, match="columns found"):
        appeears_csv.observations_from_rows([{"Date": "2025-01-01", "x": "1"}])
