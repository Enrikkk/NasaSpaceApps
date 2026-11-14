"""Bare-soil months from satellite NDVI. Pure functions, no network, no file I/O.

Pipeline (one parcel, one sensor product at a time):
  raw HLS int16 bands + uint8 Fmask  ->  observation_from_bands()  ->  one parcel-mean NDVI per date (or None if cloudy)
  list of (date, ndvi|None)          ->  monthly_aggregate()       ->  median of clear dates per month, 'sin dato' if < 2
  monthly stats                      ->  ndvi_block()              ->  the `ndvi` block of torre-pacheco.mock.json (+ extras)
  ndvi_block                         ->  bare_run_days()           ->  consecutive bare days in the Oct-Mar window (rules.py)

Sources actually checked (see README for the full list and what could NOT be verified):
  * HLS V2.0 User Guide (LP DAAC, April 2026), https://lpdaac.usgs.gov/documents/1698/HLS_User_Guide_V2.pdf
    - section 6.2 Tables 6-7: reflectance layers are int16, scale 0.0001, fill value -9999; Fmask is uint8, fill 255.
    - section 6.4 Table 9: Fmask bits (bit 0 = least significant). Bit 0 cirrus (reserved, unused in V2.0), bit 1 cloud,
      bit 2 adjacent to cloud/shadow, bit 3 cloud shadow, bit 4 snow/ice, bit 5 water, bits 6-7 aerosol level.
      "The lower six bits in the QA byte may not be mutually exclusive" (several bits can be set at once).
    - section 4.2: cloud and cloud shadow are dilated by 150 m (5 px) and the dilation is the 'adjacent' bit.
    - NIR band: HLSL30 (Landsat OLI) uses B05, HLSS30 (Sentinel-2) uses B8A (narrow NIR); red is B04 in both.

THRESHOLDS ARE DESIGN VALUES ('supuesto'), not measurements; see README for the literature that could be verified.
"""
import calendar
import datetime as dt
import math
from collections import defaultdict
from typing import Dict, Iterable, List, NamedTuple, Optional, Tuple

import numpy as np

# --- HLS constants (HLS V2.0 User Guide, Tables 6, 7, 9) -------------------------------------------------------------
REFLECTANCE_SCALE = 0.0001
REFLECTANCE_FILL = -9999
FMASK_FILL = 255
BIT_CIRRUS, BIT_CLOUD, BIT_ADJACENT, BIT_SHADOW, BIT_SNOW, BIT_WATER = 0, 1, 2, 3, 4, 5
# Default: discard cloud, adjacent to cloud/shadow, shadow, snow/ice and water. Cirrus (bit 0) is reserved/unused;
# aerosol (bits 6-7) is not a reason to drop a pixel here (design choice, 'supuesto').
DEFAULT_BAD_BITS = (BIT_CLOUD, BIT_ADJACENT, BIT_SHADOW, BIT_SNOW, BIT_WATER)

# --- classification thresholds: SUPUESTO (design values) -------------------------------------------------------------
NDVI_BARE_MAX = 0.20      # supuesto. NDVI < 0.20 -> 'desnudo' (literatura de contexto en el README; no medido aquí)
NDVI_COVER_MIN = 0.35     # supuesto, sin fuente. NDVI >= 0.35 -> 'cubierto'; entre ambos -> 'vulnerable'
MIN_CLEAR_DATES = 2       # fewer clear dates in a month -> 'sin dato' (design value)
MIN_CLEAR_PIXEL_FRACTION = 0.5   # parcel mean needs >= 50% clear valid pixels on that date (design value)

DESNUDO, VULNERABLE, CUBIERTO, SIN_DATO = "desnudo", "vulnerable", "cubierto", "sin_dato"
STATUSES = ("real", "precalculado")
WINTER_MONTHS = (10, 11, 12, 1, 2, 3)   # Oct-Mar window of Ley 3/2020 art. 51.6 (same window as rules.WINTER)


class MonthStat(NamedTuple):
    ndvi_median: Optional[float]   # None -> 'sin dato'
    n_observaciones: int           # number of clear dates that month


# --- per-pixel / per-date ---------------------------------------------------------------------------------------------
def ndvi(red, nir):
    """NDVI = (nir - red) / (nir + red) for reflectances in 0..1. NaN where an input is NaN, the sum is <= 0 or the
    result falls outside [-1, 1] (negative reflectance artefacts). Works on scalars and arrays; returns float array."""
    red = np.asarray(red, dtype=float)
    nir = np.asarray(nir, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        s = nir + red
        out = np.where(s > 0, (nir - red) / s, np.nan)
    out = np.where(np.abs(out) <= 1.0, out, np.nan)
    return out


def scale_reflectance(raw):
    """HLS int16 digital numbers -> reflectance 0..1; the fill value (-9999) becomes NaN."""
    raw = np.asarray(raw)
    return np.where(raw == REFLECTANCE_FILL, np.nan, raw.astype(float) * REFLECTANCE_SCALE)


def fmask_clear(fmask, bad_bits: Iterable[int] = DEFAULT_BAD_BITS):
    """Boolean array, True where the pixel is usable: none of `bad_bits` set in the Fmask byte and not the fill value
    (255). Fmask bit layout: HLS V2.0 User Guide section 6.4, Table 9."""
    f = np.asarray(fmask).astype(np.int64)
    bad = 0
    for b in bad_bits:
        bad |= 1 << int(b)
    return ((f & bad) == 0) & (f != FMASK_FILL)


def parcel_mean_ndvi(ndvi_px, clear, min_clear_fraction: float = MIN_CLEAR_PIXEL_FRACTION) -> Optional[float]:
    """Mean NDVI over the clear, finite pixels of the parcel on one date. None when fewer than `min_clear_fraction` of
    the pixels are usable (the whole date is then treated as cloudy). Edge pixels of a 4 ha parcel (about 45 pixels of
    30 m) are mixed with the neighbours: a known limitation, see README."""
    v = np.asarray(ndvi_px, dtype=float)
    ok = np.asarray(clear, dtype=bool) & np.isfinite(v)
    if v.size == 0 or ok.sum() / v.size < min_clear_fraction or not ok.any():
        return None
    return float(v[ok].mean())


def observation_from_bands(red_raw, nir_raw, fmask, bad_bits: Iterable[int] = DEFAULT_BAD_BITS,
                           min_clear_fraction: float = MIN_CLEAR_PIXEL_FRACTION) -> Optional[float]:
    """One date: raw int16 red/nir pixels of the parcel + Fmask pixels -> parcel mean NDVI (or None if too cloudy)."""
    n = ndvi(scale_reflectance(red_raw), scale_reflectance(nir_raw))
    return parcel_mean_ndvi(n, fmask_clear(fmask, bad_bits), min_clear_fraction)


# --- monthly aggregation ----------------------------------------------------------------------------------------------
def month_key(d: dt.date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def _month_range(start: str, end: str) -> List[str]:
    y, m = int(start[:4]), int(start[5:7])
    ye, me = int(end[:4]), int(end[5:7])
    out = []
    while (y, m) <= (ye, me):
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def monthly_aggregate(observations: Iterable[Tuple[dt.date, Optional[float]]], start: Optional[str] = None,
                      end: Optional[str] = None, min_clear_dates: int = MIN_CLEAR_DATES) -> Dict[str, MonthStat]:
    """observations: (date, parcel mean NDVI or None). None = cloudy date, ignored. Several values on the same date
    (e.g. Landsat and Sentinel-2 the same day) are averaged into ONE clear date. Per month: median of the clear dates;
    fewer than `min_clear_dates` clear dates -> MonthStat(None, n) = 'sin dato'. `start`/`end` ('YYYY-MM') force months
    without any observation to appear as 'sin dato'. Result is sorted chronologically."""
    per_date: Dict[dt.date, List[float]] = defaultdict(list)
    months_seen = set()
    for d, v in observations:
        months_seen.add(month_key(d))
        if v is not None and not (isinstance(v, float) and math.isnan(v)):
            per_date[d].append(float(v))
    per_month: Dict[str, List[float]] = defaultdict(list)
    for d, vals in per_date.items():
        per_month[month_key(d)].append(sum(vals) / len(vals))
    if start and end:
        months_seen.update(_month_range(start, end))
    out = {}
    for m in sorted(months_seen):
        vals = per_month.get(m, [])
        med = float(np.median(vals)) if len(vals) >= min_clear_dates else None
        out[m] = MonthStat(med, len(vals))
    return out


def classify_month(ndvi_median: Optional[float], bare_max: float = NDVI_BARE_MAX, cover_min: float = NDVI_COVER_MIN) -> str:
    """'desnudo' (< bare_max), 'vulnerable' (bare_max <= x < cover_min), 'cubierto' (>= cover_min), 'sin_dato' (None)."""
    if ndvi_median is None or (isinstance(ndvi_median, float) and math.isnan(ndvi_median)):
        return SIN_DATO
    if ndvi_median < bare_max:
        return DESNUDO
    if ndvi_median < cover_min:
        return VULNERABLE
    return CUBIERTO


def ndvi_block(months: Dict[str, MonthStat], status: str, fuente: Optional[str] = None) -> dict:
    """The `ndvi` block of app/data/torre-pacheco.mock.json ({fuente, meses_desnudo[], meses_vulnerable[]}, 'YYYY-MM')
    plus `meses_sin_dato[]`, `n_observaciones` {month: clear dates} and `_status` ('real' | 'precalculado').
    'real' = computed from satellite data actually downloaded; 'precalculado' = a labelled precomputed sample."""
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}, got {status!r}")
    ordered = sorted(months)
    cls = {m: classify_month(months[m].ndvi_median) for m in ordered}
    return {
        "fuente": fuente or ("HLS (AppEEARS HLSL30/HLSS30 v2.0)" if status == "real" else "HLS (precalculado)"),
        "meses_desnudo": [m for m in ordered if cls[m] == DESNUDO],
        "meses_vulnerable": [m for m in ordered if cls[m] == VULNERABLE],
        "meses_sin_dato": [m for m in ordered if cls[m] == SIN_DATO],
        "n_observaciones": {m: months[m].n_observaciones for m in ordered},
        "_status": status,
    }


# --- Oct-Mar consecutive bare days (feeds rules.BARE_LIMIT_DAYS / semaforo) -----------------------------------------
def winter_months(winter_year: int) -> List[str]:
    """Oct winter_year ... Mar winter_year+1 as 'YYYY-MM'."""
    return [f"{winter_year + (0 if m >= 10 else 1):04d}-{m:02d}" for m in WINTER_MONTHS]


def days_in(month: str) -> int:
    return calendar.monthrange(int(month[:4]), int(month[5:7]))[1]


def _longest_run_days(flags: List[Tuple[str, bool]]) -> int:
    best = cur = 0
    for m, bare in flags:
        cur = cur + days_in(m) if bare else 0
        best = max(best, cur)
    return best


def bare_run_days(block: dict, winter_year: int, unknown: str = "break") -> int:
    """Longest run of consecutive bare calendar days in the Oct (winter_year) - Mar (winter_year+1) window, from an
    `ndvi_block`. Month granularity: a bare month counts all its days (coarse; 2 full months = 59-62 days, so compare
    against rules.BARE_LIMIT_DAYS = 60 with care, see README). 'vulnerable' and 'cubierto' months break the run.
    A month with no data, or not analysed at all, follows `unknown`: 'break' (not bare: lower bound, default) or
    'bare' (assume bare: upper bound)."""
    if unknown not in ("break", "bare"):
        raise ValueError("unknown must be 'break' or 'bare'")
    bare = set(block.get("meses_desnudo", []))
    analysed = set(block.get("n_observaciones", {})) | bare | set(block.get("meses_vulnerable", []))
    nodata = set(block.get("meses_sin_dato", []))
    flags = []
    for m in winter_months(winter_year):
        if m in bare:
            flags.append((m, True))
        elif m in nodata or m not in analysed:
            flags.append((m, unknown == "bare"))
        else:
            flags.append((m, False))
    return _longest_run_days(flags)


def bare_run_range(block: dict, winter_year: int) -> Tuple[int, int]:
    """(lower, upper) bound of consecutive bare days: unknown months as not-bare / as bare."""
    return bare_run_days(block, winter_year, "break"), bare_run_days(block, winter_year, "bare")
