"""Turn an AppEEARS point-sample CSV (HLS, one file per product) into the (date, parcel-mean NDVI) list that
bare_soil.monthly_aggregate expects. Local file reading only, no network.

UNVERIFIED: the exact CSV column names could not be checked without a real download. Assumed (typical AppEEARS style):
columns 'Date', 'ID' and '<Product>_<Version>_<Layer>' such as 'HLSS30_020_B04', 'HLSS30_020_B8A', 'HLSS30_020_Fmask'.
Matching is by suffix and tolerant; if nothing matches, a clear error lists the columns found. Adjust here after the
first real download. Decoded Fmask columns (e.g. '..._Fmask_Cloud') are ignored: we decode the raw byte ourselves.
"""
import csv
import datetime as dt
from collections import defaultdict
from typing import List, Optional, Tuple

import numpy as np

from .bare_soil import FMASK_FILL, fmask_clear, ndvi, parcel_mean_ndvi

NIR_BAND = {"HLSL30": "B05", "HLSS30": "B8A"}   # HLS V2.0 User Guide section 6.2, Tables 6-7


def _num(s, default):
    try:
        return float(s)
    except (TypeError, ValueError):
        return default


def _reflectance(values):
    """UNVERIFIED whether AppEEARS writes scaled reflectance (0..1) or raw int16 into the CSV. Tolerate both: values
    with |v| > 2 are raw digital numbers (x 0.0001); anything <= -0.5 is a fill value (-9999 or its scaled form)."""
    v = np.array([_num(x, np.nan) for x in values], dtype=float)
    v = np.where(np.abs(v) > 2, v * 0.0001, v)
    return np.where(v <= -0.5, np.nan, v)


def observations_from_rows(rows: List[dict]) -> List[Tuple[dt.date, Optional[float]]]:
    """rows: dicts from csv.DictReader (one row per point per date). Groups by (product, date), builds the pixel arrays
    across the points and returns [(date, parcel-mean NDVI or None)]."""
    if not rows:
        return []
    cols = list(rows[0].keys())
    date_col = next((c for c in cols if c.strip().lower() == "date"), None)
    if date_col is None:
        raise ValueError(f"no 'Date' column; columns found: {cols}")
    prefixes = {}
    for c in cols:
        if c.endswith("_B04"):
            prefixes[c[:-4]] = None
    if not prefixes:
        raise ValueError(f"no '<product>_B04' column; columns found: {cols}")
    out = []
    for prefix in prefixes:
        sensor = prefix.split("_")[0]
        nir_col, red_col, fm_col = f"{prefix}_{NIR_BAND[sensor]}", f"{prefix}_B04", f"{prefix}_Fmask"
        for need in (nir_col, fm_col):
            if need not in cols:
                raise ValueError(f"missing column {need}; columns found: {cols}")
        groups = defaultdict(list)
        for r in rows:
            groups[r[date_col][:10]].append(r)
        for d, rs in groups.items():
            red, nir = _reflectance([r[red_col] for r in rs]), _reflectance([r[nir_col] for r in rs])
            fm = np.array([int(_num(r[fm_col], FMASK_FILL)) for r in rs])
            if np.isnan(red).all() and np.isnan(nir).all():
                continue   # no acquisition for this product on that date
            out.append((dt.date.fromisoformat(d), parcel_mean_ndvi(ndvi(red, nir), fmask_clear(fm))))
    return sorted(out, key=lambda t: t[0])


def load_csv(path: str) -> List[Tuple[dt.date, Optional[float]]]:
    with open(path, newline="", encoding="utf-8") as f:
        return observations_from_rows(list(csv.DictReader(f)))
