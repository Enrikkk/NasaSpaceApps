"""Load the engine's inputs: crop parameters (long format), daily climate, prices, deflator.

Crop parameters come from the team table app/data/tables/crop_params.csv (T-021, arturo) when it exists, else from
the engine's own official snapshot (engine/data/official/fao_crop_params.csv + imida_costs.csv). Both use the long
format crop_id,param,value,unit,source_id,conf,status,nota. A param with an empty value (conf P) is treated as
MISSING: the engine never turns a gap into a number; the submodel that needs it is skipped and the gap is reported.
"""
import csv
import datetime as dt
import pathlib
from dataclasses import dataclass, field

ENGINE = pathlib.Path(__file__).resolve().parents[1]
REPO = ENGINE.parents[2]
OFFICIAL = ENGINE / "data" / "official"
TEAM_TABLE = REPO / "app" / "data" / "tables" / "crop_params.csv"


@dataclass
class Param:
    value: object
    unit: str
    source_id: str
    conf: str
    status: str
    nota: str


@dataclass
class Crop:
    crop_id: str
    params: dict = field(default_factory=dict)  # param -> Param (only params WITH a value)
    gaps: dict = field(default_factory=dict)    # param -> nota, for params present but empty

    def get(self, name, default=None):
        p = self.params.get(name)
        return p.value if p else default

    def has(self, *names):
        return all(n in self.params for n in names)

    def ref(self, name):
        """(value, source_id, conf) for the evidence pack."""
        p = self.params[name]
        return {"param": name, "valor": p.value, "unidad": p.unit, "fuente": p.source_id, "conf": p.conf}


def _value(v):
    v = (v or "").strip()
    if v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return v  # e.g. "30/40/25/10", "yes", "moderately sensitive"


def load_crops(paths=None):
    if paths is None:
        paths = [TEAM_TABLE] if TEAM_TABLE.exists() else [OFFICIAL / "fao_crop_params.csv", OFFICIAL / "imida_costs.csv"]
    crops = {}
    for path in paths:
        for r in csv.DictReader(open(path, encoding="utf-8")):
            c = crops.setdefault(r["crop_id"], Crop(r["crop_id"]))
            v = _value(r["value"])
            if v is None:
                c.params.pop(r["param"], None)
                c.gaps[r["param"]] = r.get("nota", "")
            else:
                c.params[r["param"]] = Param(v, r["unit"], r["source_id"], r["conf"], r["status"], r.get("nota", ""))
                c.gaps.pop(r["param"], None)
    return crops


def load_hicp():
    return {int(r["year"]): float(r["hicp_2015_100"]) for r in csv.DictReader(open(OFFICIAL / "eurostat_hicp_es.csv"))}


def load_prices():
    """{crop_id: {year: eur_kg_real2015}} from Eurostat first-stage national prices."""
    out = {}
    for r in csv.DictReader(open(OFFICIAL / "eurostat_prices_es.csv")):
        if r["eur_100kg_real2015"]:
            out.setdefault(r["crop_id"], {})[int(r["year"])] = float(r["eur_100kg_real2015"]) / 100
    return out


def load_area():
    out = {}
    for r in csv.DictReader(open(OFFICIAL / "eurostat_area_es.csv")):
        out.setdefault(r["crop_id"], {})[int(r["year"])] = {k: _value(r[k]) for k in ("area_kha", "prod_kt", "yield_t_ha")}
    return out


@dataclass
class Day:
    tmin: float      # absolute daily minimum, degC (frost)
    tmax: float      # absolute daily maximum, degC (heat)
    rain: float      # mm
    et0: float       # FAO-56 Penman-Monteith reference ET, mm
    filled: str = ""  # "" if measured at the station, else what filled it


def load_climate(station="TP91"):
    """Daily climate at the demo parcel: SIAM station first (measured), NASA POWER only to fill station gaps.

    Gap filling (reported per day in Day.filled): Tmin/Tmax from POWER minus the station-vs-POWER mean bias
    measured over the overlap (POWER nights are ~2.75 degC warmer); ET0 from the station's own mean for that
    calendar day; rain from POWER. Returns (days: {date: Day}, meta).
    """
    siam = {r["date"]: r for r in csv.DictReader(open(OFFICIAL / f"siam_{station}_daily.csv"))}
    power = {r["date"]: r for r in csv.DictReader(open(OFFICIAL / "power_daily_37.7383_-0.9884.csv"))}
    f = lambda x: float(x) if x not in ("", None) else None
    bmin, bmax, et0_doy = [], [], {}
    for d, r in siam.items():
        p = power.get(d)
        if p and f(r["TMINABS"]) is not None:
            bmin.append(float(p["T2M_MIN"]) - f(r["TMINABS"]))
        if p and f(r["TMAXABS"]) is not None:
            bmax.append(float(p["T2M_MAX"]) - f(r["TMAXABS"]))
        if f(r["ETO_PM_FAO"]) is not None:
            et0_doy.setdefault(d[5:], []).append(f(r["ETO_PM_FAO"]))
    bias_min, bias_max = sum(bmin) / len(bmin), sum(bmax) / len(bmax)
    et0_mean = {k: sum(v) / len(v) for k, v in et0_doy.items()}
    first, last = min(siam), max(siam)
    days, n_filled = {}, 0
    d = dt.date.fromisoformat(first)
    while d.isoformat() <= last:
        k = d.isoformat()
        r, p = siam.get(k, {}), power.get(k, {})
        tmin, tmax, rain, et0 = (f(r.get("TMINABS")), f(r.get("TMAXABS")), f(r.get("PREC")), f(r.get("ETO_PM_FAO")))
        filled = []
        if tmin is None:
            tmin, _ = float(p["T2M_MIN"]) - bias_min, filled.append("tmin")
        if tmax is None:
            tmax, _ = float(p["T2M_MAX"]) - bias_max, filled.append("tmax")
        if rain is None:
            rain, _ = float(p["PRECTOTCORR"]), filled.append("rain")
        if et0 is None:
            et0, _ = et0_mean.get(k[5:], et0_mean.get("02-28")), filled.append("et0")
        n_filled += bool(filled)
        days[d] = Day(tmin, tmax, rain, et0, ",".join(filled))
        d += dt.timedelta(days=1)
    meta = {"estacion": f"SIAM-{station}", "desde": first, "hasta": last, "dias": len(days), "dias_rellenados": n_filled,
            "sesgo_power_tmin_c": round(bias_min, 2), "sesgo_power_tmax_c": round(bias_max, 2)}
    return days, meta
