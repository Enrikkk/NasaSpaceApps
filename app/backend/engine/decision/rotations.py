"""Cycles, calendar and one-year plans for the rotation DP (T-020).

A CYCLE is one product sown on a (month, day): the T-012 engine gives one scenario per historical year for it.
A YEAR OPTION is a set of cycles that fit in a 365-day year without overlapping (14 days of soil preparation
between them), optionally with a winter cover crop (veza) sown into the longest bare autumn-winter gap.
A ROTATION is a path of year options over the planning horizon (3 years: BCAM 7 asks every plot to rotate once in 3).

Calendar assumptions (labelled "supuesto" in the export): each product is tried at its base sowing date and 15 days
later (never earlier while frost thresholds are unvalidated); 14 days between cycles; cover crop cost 120 EUR/ha (no IMIDA study for it: placeholder).
"""
import dataclasses
import datetime as dt
import itertools

from ..core import evaluate as ev, stage_risk, stats, submodels as sm
from . import rules

GAP_DAYS = 14
COVER_COST_EUR_HA = 120.0     # SUPUESTO sin fuente: semilla + siembra + incorporación de la cubierta de veza
COVER_PRODUCT = "veza"
CATALOG = ["lechuga_iceberg", "brocoli", "melon_piel_de_sapo", "alcachofa"]
HORIZON = 3
ET0_PER_DEGC = 0.04           # SUPUESTO: +4 % de ET0 por °C (orden de magnitud; sin fuente verificada)


def doy(month, day):
    return dt.date(2001, month, day).timetuple().tm_yday


def sowing_options(base_month):
    """Base date and 15 days later. NOT earlier: earlier sowing looks better on price (harvest lands in better-paid
    months) but frost thresholds are still unvalidated (T-021), so the engine cannot see its risk. Revisit with them."""
    return [(base_month, 1), (base_month, 15)]


def perturb(climate, rain_pct=0.0, temp_c=0.0):
    """Simulated climate: rain x (1+pct/100), temperatures + temp_c, ET0 + ET0_PER_DEGC per degC."""
    return {d: dataclasses.replace(v, tmin=v.tmin + temp_c, tmax=v.tmax + temp_c, rain=v.rain * (1 + rain_pct / 100),
                                   et0=v.et0 * (1 + ET0_PER_DEGC * temp_c)) for d, v in climate.items()}


def run_cycles(products, climate, prices, hicp, area, carm, base_year, allow_restricted, catalog=None):
    """Evaluate every catalog product at every sowing option. Returns {key: {static..., "years": {y0: rec}}} where
    key = (product_id, 'MM-DD'). Static info does not depend on the climate; years do."""
    out = {}
    for pid in catalog or CATALOG:
        if pid not in products:
            continue
        crop, pm = products[pid]
        base = int(crop.get("sowing_month", 1))
        for (m, d) in sowing_options(base):
            r = ev.evaluate(crop, climate, prices, hicp, area, sowing=(m, d), base_year=base_year, meta=pm, carm=carm,
                            allow_restricted=allow_restricted)
            if "anios" not in r or not r["anios"]:
                continue
            lengths = sm.stages(crop, "stages_days_murcia") or sm.stages(crop, "stages_days")
            window = pm.get("harvest_window") or "late"
            first_harvest = {"late": sum(lengths[:3]), "mid+late": sum(lengths[:2]), "all": lengths[0]}.get(window, sum(lengths[:3]))
            k_cost = ev.deflator(hicp, base_year, crop.params["coste_total"].base_year) if crop.get("coste_total") else None
            caja = crop.get("caja_antes_de_venta")
            out[(pid, f"{m:02d}-{d:02d}")] = {
                "product": pid, "crop": pm.get("crop_id") or crop.crop_id, "label": pm.get("label", pid),
                "start_doy": doy(m, d), "days": r["ciclo_dias"], "first_harvest_day": first_harvest,
                "caja": caja * k_cost if (caja is not None and k_cost) else None,
                "riesgo_etapas": stage_risk.assess(pm.get("crop_id") or crop.crop_id, lengths, m, d, climate),
                "years": {int(a["siembra"][:4]): a for a in r["anios"]},
                "report": {"huecos": r["huecos"], "evidencia": r["evidencia"], "precio": r["precio"],
                           "licencia": r["licencia"], "exito": r["exito_pct"]},
            }
    return out


def fits(cycles):
    """True if the cycles (static dicts) do not overlap inside one cyclic year, with GAP_DAYS between them."""
    cs = sorted(cycles, key=lambda c: c["start_doy"])
    for i, c in enumerate(cs):
        nxt = cs[i + 1]["start_doy"] if i + 1 < len(cs) else cs[0]["start_doy"] + 365
        if c["start_doy"] + c["days"] + GAP_DAYS > nxt:
            return False
    return True


def occupancy(cycles):
    occ = [False] * 365
    for c in cycles:
        for k in range(c["days"]):
            occ[(c["start_doy"] - 1 + k) % 365] = True
    return occ


def winter_bare_run(occ):
    """Longest run of consecutive bare days inside the Oct 1 - Mar 31 window (Ley 3/2020 art. 51.6)."""
    days = list(range(274, 366)) + list(range(1, 91))
    best = cur = 0
    for d in days:
        cur = 0 if occ[d - 1] else cur + 1
        best = max(best, cur)
    return best


@dataclasses.dataclass(frozen=True)
class Option:
    keys: tuple          # ((product, 'MM-DD'), ...) sorted by sowing day
    cover: bool = False  # winter cover crop in the longest bare gap

    def name(self, static):
        parts = [static[k]["label"] for k in self.keys] or ["barbecho"]
        return " + ".join(parts) + (" + cubierta de veza" if self.cover else "")


def build_options(static, crops, max_cycles=3):
    """All year options: subsets of distinct products at one sowing option each, non-overlapping, agronomic filter
    inside the year. The all-fallow year is not an option. Cover variants only where the bare winter gap exceeds the limit."""
    by_product = {}
    for k in static:
        by_product.setdefault(k[0], []).append(k)
    products = sorted(by_product)
    opts = []
    for n in range(1, max_cycles + 1):
        for combo in itertools.combinations(products, n):
            for keys in itertools.product(*[by_product[p] for p in combo]):
                cs = [static[k] for k in keys]
                if not fits(cs):
                    continue
                keys = tuple(sorted(keys, key=lambda k: static[k]["start_doy"]))
                seq = [static[k]["crop"] for k in keys]
                if any(not rules.allowed(crops, a, b) for a, b in zip(seq, seq[1:])):
                    continue
                opts.append(Option(keys))
                if winter_bare_run(occupancy(cs)) > rules.BARE_LIMIT_DAYS:
                    opts.append(Option(keys, cover=True))
    return opts


def option_static(opt, static):
    cs = [static[k] for k in opt.keys]
    occ = occupancy(cs)
    run = winter_bare_run(occ)
    cover_days = run if opt.cover else 0
    return {"cycles": cs, "bare_run": run, "covered": opt.cover,
            "bare_days": 365 - sum(occ) - cover_days, "n_credit": rules.N_CREDIT[COVER_PRODUCT] if opt.cover else 0.0}


def year_values(opt, runs, mult=1.0):
    """{hist_year: dict(margen, agua, malo)} for the historical years where EVERY cycle of the option has data.
    margen is None-free only for years with price (money-valid); water-only years are kept with margen None."""
    cycles = [runs[k] for k in opt.keys]
    all_years = {y for c in runs.values() for y in c["years"]}
    ys = set.intersection(*[set(c["years"]) for c in cycles]) if cycles else all_years
    out = {}
    for y in sorted(ys):
        recs = [c["years"][y] for c in cycles]
        money = all(r["con_precio"] for r in recs)
        cost = sum(r["coste_eur_ha"] for r in recs) * mult if money else None
        if opt.cover and cost is not None:
            cost += COVER_COST_EUR_HA * mult
        rev = sum(r["cantidad_ha"] * r["precio"] for r in recs) if money else None
        agua = sum(r["agua"]["bruto_m3_ha"] for r in recs if r["agua"]) if recs else 0.0
        clima_malo = any(r["clima_malo"] for r in recs)
        out[y] = {"rev": rev, "cost": cost, "margen": None if not money else rev - cost, "agua": agua, "clima_malo": clima_malo,
                  "money": money}
    return out


def option_metrics(opt, static, runs):
    """Plan-year level raw criteria (higher margin / lower water / more soil-N / higher CVaR are better)."""
    st = option_static(opt, {k: static[k] for k in opt.keys} if opt.keys else {})
    yv = year_values(opt, runs)
    money = [v["margen"] for v in yv.values() if v["margen"] is not None]
    if not money:
        return None
    suelo = 0.5 * min(1.0, st["n_credit"] / rules.N_CREDIT[COVER_PRODUCT]) + 0.5 * (1 - st["bare_days"] / 365)
    return {"margen": sum(money) / len(money), "agua": sum(v["agua"] for v in yv.values()) / len(yv),
            "suelo_n": suelo, "cvar": stats.cvar(money, 0.8), "n_years": len(money),
            "bare_days": st["bare_days"]}
