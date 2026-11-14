"""Compose submodels A-D with prices and costs into one scenario per historical year (D-008 PROPOSED).

For crop c sown on (month, day): one cycle per start year whose whole cycle is inside the station record. Each cycle
is paired with the price of its HARVEST calendar year (keeps the climate-price coupling: a frost year tends to
raise prices). A year is bad if climate loss >= L* (20 %) OR margin < 0 at that year's price. Success = 1 - k/n with
a Wilson 95 % interval. Money in euros of `base_year` (Spain HICP): prices from real-2015, costs from 2018 nominal.

Run:  python3 -m app.backend.engine.core.evaluate [base_year]     prints the 7 evaluable demo crops
"""
import datetime as dt
import sys

from . import data, stats, submodels as sm

COST_BASE_YEAR = 2018  # IMIDA surveys 2017-19, agreed with arturo (bus #54)


def money(hicp, base_year):
    return {"from_real2015": hicp[base_year] / 100, "from_2018": hicp[base_year] / hicp[COST_BASE_YEAR]}


def evaluate(crop, climate, prices, hicp, area=None, sowing=None, base_year=2024, ecw=None, stage_key="stages_days"):
    gaps, evidence = [], []
    lengths = sm.stages(crop, stage_key)
    salt = sm.salt_factor(crop, ecw)
    why_not = sm.aptitude(crop, salt)
    if why_not and lengths is None:
        return {"cultivo": crop.crop_id, "apto": False, "motivos": why_not}
    month, day = sowing or (int(crop.get("sowing_month", 1)), 1)
    n_days = sum(lengths)
    y_ref, y_ev = sm.reference_yield(crop, (area or {}).get(crop.crop_id))
    k = money(hicp, base_year)
    cost_total, harvest = crop.get("coste_total"), crop.get("recoleccion", 0.0)
    price = prices.get(crop.crop_id, {})

    for hazard in ("frost", "heat"):
        if sm.thresholds(crop, hazard) is None:
            gaps.append(f"umbral de {'helada' if hazard == 'frost' else 'calor'} sin fuente: ese peligro NO se evalúa")
    if salt is None:
        gaps.append("CE del agua de riego de la parcela desconocida: no se aplica la pérdida por sal")
    if y_ref is None:
        gaps.append("sin rendimiento de referencia: no hay margen")
    if cost_total is None:
        gaps.append("sin costes de cultivo (IMIDA/MAPA): no hay margen")
    if not price:
        gaps.append("sin serie oficial de precio (Eurostat): no hay margen")
    else:
        gaps.append("precio = media nacional anual Eurostat (primera venta), no el precio de esta parcela ni su calidad")
    can_margin = y_ref is not None and cost_total is not None and bool(price)
    if y_ev:
        evidence.append(y_ev)
    evidence += [crop.ref(p) for p in ("kc_ini", "kc_mid", "kc_end", "coste_total", "ece_threshold") if crop.has(p)]

    years, first = [], min(climate)
    for y0 in range(first.year, max(climate).year + 1):
        start = dt.date(y0, month, day)
        days = sm.cycle_days(climate, start, n_days)
        if days is None:
            continue
        harvest_year = (start + dt.timedelta(days=n_days - 1)).year
        cl = sm.climate_loss(crop, days, lengths)
        w = sm.water(crop, days, lengths)
        y = None if y_ref is None else y_ref * (1 - cl["total"]) * (salt if salt is not None else 1.0)
        p_year = price.get(harvest_year)
        margin = None
        if can_margin and p_year is not None:
            revenue = y * p_year * k["from_real2015"]
            cost = ((cost_total - harvest) + harvest * (y / y_ref)) * k["from_2018"]  # harvest cost scales with kilos
            margin = revenue - cost
        bad_climate = cl["total"] >= sm.ASSUMPTIONS["loss_threshold"][0]
        bad_money = margin is not None and margin < 0
        years.append({"siembra": start.isoformat(), "anio_cosecha": harvest_year, "perdida_clima": cl["total"],
                      "perdida_helada": cl["frost"], "perdida_calor": cl["heat"], "peor_dia": cl["peor_dia"],
                      "kg_ha": y, "precio_eur_kg": None if p_year is None else p_year * k["from_real2015"],
                      "margen_eur_ha": margin, "agua": w, "malo": bad_climate or bad_money,
                      "por_que_malo": [r for r, b in (("clima", bad_climate), ("dinero", bad_money)) if b],
                      "dias_rellenados": sum(bool(d.filled) for d in days)})

    n, bad = len(years), sum(r["malo"] for r in years)
    hazards = [h for h in ("frost", "heat") if sm.thresholds(crop, h) is not None]
    if not can_margin:
        gaps.append("lechuga/hortaliza: precio nacional Eurostat 'todas las calidades', no precio de parcela") if False else None
    if not hazards and not can_margin:
        n_eval = None  # nothing was actually tested: never show a 100 % that measured nothing
    worst = sorted(years, key=lambda r: (-(r["perdida_clima"]), r["margen_eur_ha"] if r["margen_eur_ha"] is not None
                                         else 0))[:3]
    margins = [r["margen_eur_ha"] for r in years if r["margen_eur_ha"] is not None]
    gross = [r["agua"]["bruto_m3_ha"] for r in years if r["agua"]]
    out = {
        "cultivo": crop.crop_id, "apto": not why_not, "motivos": why_not,
        "siembra": f"{month:02d}-{day:02d}", "ciclo_dias": n_days,
        "exito_pct": {"valor": None, "horquilla": None, "k_malos": None, "n": n, "metodo": None,
                      "definicion": "NO EVALUABLE: sin umbrales de clima ni precio/coste; no se muestra % de éxito"}
        if not hazards and not can_margin else
                     {**stats.success(bad, n), "peores_anios": [r["anio_cosecha"] for r in worst if r["malo"]],
                      "definicion": "años con pérdida clima < 20 % Y margen >= 0" if margins else
                                    "SOLO CLIMA (falta precio/coste/rendimiento): años con pérdida clima < 20 %"},
        "margen_eur_ha": None if not margins else {
            "p10": stats.quantile(margins, 0.1), "p50": stats.quantile(margins, 0.5),
            "p90": stats.quantile(margins, 0.9), "media": sum(margins) / len(margins),
            "cvar80": stats.cvar(margins, 0.8), "n": len(margins), "euros_de": base_year},
        "agua_m3_ha": None if not gross else {"p10": stats.quantile(gross, 0.1), "p50": stats.quantile(gross, 0.5),
                                              "p90": stats.quantile(gross, 0.9),
                                              "imida_encuesta": crop.get("riego_dosis")},
        "huecos": gaps, "evidencia": evidence,
        "supuestos": {k2: v[1] for k2, v in sm.ASSUMPTIONS.items()},
        "anios": years,
    }
    return out


def demo(base_year=2024):
    crops = data.load_crops()
    climate, meta = data.load_climate()
    prices, hicp, area = data.load_prices(), data.load_hicp(), data.load_area()
    print(f"clima: {meta}")
    print(f"{'cultivo':10} {'n':>3} {'malos':>5} {'éxito':>6} {'horquilla':>11}  {'margen P10/P50/P90 €/ha':>26}  "
          f"{'agua P50 m³/ha':>14} (IMIDA)  huecos")
    for cid in ("lechuga", "brocoli", "melon", "alcachofa", "haba", "cebada", "limon"):
        r = evaluate(crops[cid], climate, prices, hicp, area, base_year=base_year)
        if "exito_pct" not in r:
            print(f"{cid:10} no evaluable: {r['motivos']}")
            continue
        e, m, a = r["exito_pct"], r["margen_eur_ha"], r["agua_m3_ha"]
        if e["valor"] is None:
            print(f"{cid:10} {e['n']:>3}  no evaluable (faltan umbrales y precio/coste); agua P50 "
                  f"{a['p50'] if a else 0:.0f} m³/ha  huecos {len(r['huecos'])}")
            continue
        ms = "-" if not m else f"{m['p10']:>8.0f}/{m['p50']:>7.0f}/{m['p90']:>7.0f}"
        imida = a.get("imida_encuesta") if a else None
        print(f"{cid:10} {e['n']:>3} {e['k_malos']:>5} {e['valor'] * 100:>5.0f}% "
              f"{e['horquilla'][0] * 100:>4.0f}-{e['horquilla'][1] * 100:<4.0f}%  {ms:>26}  "
              f"{a['p50'] if a else 0:>14.0f} ({imida if imida else '-'})  {len(r['huecos'])}")
    return crops


if __name__ == "__main__":
    demo(int(sys.argv[1]) if len(sys.argv) > 1 else 2024)
