"""Compose submodels A-D with market prices and costs into one scenario per historical year (D-008 PROPOSED).

For a PRODUCT (crop type, e.g. lechuga_iceberg) sown on (month, day): one cycle per start year whose whole cycle is
inside the station record. Each cycle is paired with the price of its own harvest months (CARM Murcia quotes by type)
or, failing that, its harvest year (Eurostat). A year is bad if climate loss >= L* (20 %) OR margin < 0.
Years without a price are LEFT OUT of the success count (never counted as good) and reported as coverage.
Success = 1 - k/n with a Wilson 95 % interval. Money in euros of `base_year` (Spain HICP); each cost row is
deflated from its own base year (`price_base_year` column, default 2018 = IMIDA).

Run:  python3 -m app.backend.engine.core.evaluate [base_year] [--interno]   (--interno: use licence-restricted CARM
      prices, internal runs only; default = open data only, as any published output must be)
"""
import datetime as dt
import sys

from . import data, market as mk, stats, submodels as sm

DEFAULT_META = {"variety": "", "quality": "", "price_unit": "eur_kg", "harvest_window": "late", "cost_from": ""}


def deflator(hicp, base_year, from_year):
    return hicp[base_year] / hicp[from_year]


def quantities(crop):
    """(kg_net_ref, ud_ref, evidence, gaps): reference marketable kg/ha and units/ha per cycle."""
    gaps, ev = [], []
    kg = ud = None
    if crop.has("coste_total", "coste_unitario"):
        kg = crop.get("coste_total") / crop.get("coste_unitario")
        ev.append({"param": "kg_netos_ha", "valor": round(kg), "unidad": "kg/ha", "fuente": crop.ref("coste_total")["fuente"],
                   "conf": "M", "nota": "derivado: coste total / coste unitario por kg neto (IMIDA)"})
    elif crop.has("produccion_media"):
        kg = crop.get("produccion_media")
        gaps.append("kilos = producción bruta (sin descontar destrío): margen algo optimista")
    if crop.has("coste_total", "coste_unitario_ud"):
        ud = crop.get("coste_total") / crop.get("coste_unitario_ud")
        ev.append({"param": "piezas_ha", "valor": round(ud), "unidad": "ud/ha", "fuente": crop.ref("coste_total")["fuente"],
                   "conf": "M", "nota": "derivado: coste total / coste unitario por pieza (IMIDA)"})
    return kg, ud, ev, gaps


def evaluate(crop, climate, prices, hicp, area=None, sowing=None, base_year=2025, ecw=None, stage_key="stages_days",
             meta=None, carm=None, allow_restricted=False):
    meta = {**DEFAULT_META, **(meta or {})}
    gaps, evidence = [], []
    if stage_key == "stages_days" and sm.stages(crop, "stages_days_murcia"):
        stage_key = "stages_days_murcia"  # local calendar beats a foreign FAO example row when we have one
    lengths = sm.stages(crop, stage_key)
    salt = sm.salt_factor(crop, ecw)
    why_not = sm.aptitude(crop, salt)
    if why_not and lengths is None:
        return {"producto": crop.crop_id, "apto": False, "motivos": why_not}
    month, day = sowing or (int(crop.get("sowing_month", 1)), 1)
    n_days = sum(lengths)

    # --- quantities and costs -------------------------------------------------------------------------------------
    kg_ref, ud_ref, q_ev, q_gaps = quantities(crop)
    if kg_ref is None:
        kg_ref, y_ev = sm.reference_yield(crop, (area or {}).get(meta.get("crop_id") or crop.crop_id))
        if y_ev:
            q_ev.append(y_ev)
    gaps += q_gaps
    evidence += q_ev
    cost_total, harvest = crop.get("coste_total"), crop.get("recoleccion", 0.0)
    if cost_total is not None:
        k_cost = deflator(hicp, base_year, crop.params["coste_total"].base_year)
    if meta.get("cost_from") and meta["cost_from"] != crop.crop_id and cost_total is not None:
        gaps.append(f"costes tomados de '{meta['cost_from']}': no hay estudio IMIDA propio de este tipo")

    # --- market -----------------------------------------------------------------------------------------------------
    unit = meta["price_unit"] or "eur_kg"
    m = mk.Market(carm or {}, prices, hicp, base_year, allow_restricted)
    base_crop = meta.get("crop_id") or crop.crop_id
    tier, tier_label, series, keys, dropped = m.series_for(base_crop, meta["variety"], meta["quality"], unit)
    euro, euro_info = (m.eurostat_series(base_crop) if unit == "eur_kg" else (None, None))
    if tier == 3 and not euro:
        tier, tier_label = None, "sin precio"
    qty_ref = ud_ref if unit == "eur_ud" else kg_ref
    if unit == "eur_ud" and ud_ref is None:
        gaps.append("precio por pieza pero sin piezas/ha (coste unitario por pieza IMIDA): no hay margen")
    if tier in (1, 2):
        gaps.append("precio = cotización orientativa CARM (anuarios), no el precio pactado de esta finca")
    elif tier == 3:
        gaps.append("precio = media nacional anual Eurostat (primera venta), no el precio de Murcia ni de este tipo")
    if dropped:
        gaps.append(f"{len(dropped)} cotizaciones CARM excluidas por atípicas (> {mk.OUTLIER_X:.0f}x la mediana; "
                    f"p. ej. {dropped[0][0]}-{dropped[0][1]:02d}: {dropped[0][2]})")
    for hazard in ("frost", "heat"):
        if sm.thresholds(crop, hazard) is None:
            gaps.append(f"umbral de {'helada' if hazard == 'frost' else 'calor'} sin fuente: ese peligro NO se evalúa")
    if salt is None:
        gaps.append("CE del agua de riego de la parcela desconocida: no se aplica la pérdida por sal")
    if cost_total is None:
        gaps.append("sin costes de cultivo (IMIDA/MAPA): no hay margen")
    can_margin = qty_ref is not None and cost_total is not None and tier is not None
    evidence += [crop.ref(p) for p in ("kc_ini", "kc_mid", "kc_end", "coste_total", "ece_threshold") if crop.has(p)]

    # --- one scenario per historical cycle --------------------------------------------------------------------------
    years, first = [], min(climate)
    channel_list = m.channels(base_crop, unit, keys) if tier in (1, 2) else []
    for y0 in range(first.year, max(climate).year + 1):
        start = dt.date(y0, month, day)
        days = sm.cycle_days(climate, start, n_days)
        if days is None:
            continue
        harvest_year = (start + dt.timedelta(days=n_days - 1)).year
        months = mk.harvest_months(start, lengths, meta["harvest_window"])
        cl = sm.climate_loss(crop, days, lengths)
        w = sm.water(crop, days, lengths)
        keep = (1 - cl["total"]) * (salt if salt is not None else 1.0)
        qty = None if qty_ref is None else qty_ref * keep
        p_year, p_how = (None, "sin precio")
        if tier in (1, 2):
            p_year, p_how = m.cycle_price(series, months)
        elif tier == 3:
            p_year, p_how = euro.get(harvest_year), "año de cosecha (Eurostat)"
        cost = cost_harvest = None
        if cost_total is not None:
            cost_harvest = harvest * keep * k_cost  # harvest cost scales with what is picked
            cost = (cost_total - harvest) * k_cost + cost_harvest
        margin = qty * p_year - cost if (can_margin and p_year is not None) else None
        bad_climate = cl["total"] >= sm.ASSUMPTIONS["loss_threshold"][0]
        bad_money = margin is not None and margin < 0
        years.append({"siembra": start.isoformat(), "anio_cosecha": harvest_year, "perdida_clima": cl["total"],
                      "perdida_helada": cl["frost"], "perdida_calor": cl["heat"], "peor_dia": cl["peor_dia"],
                      "cantidad_ha": qty, "unidad_cantidad": "ud" if unit == "eur_ud" else "kg",
                      "coste_eur_ha": cost, "coste_recoleccion_eur_ha": cost_harvest, "precio": p_year, "precio_como": p_how,
                      "precio_minimo": (cost / qty) if (cost is not None and qty) else None,
                      "canales": {c["id"]: m.cycle_price(c["serie"], months)[0] for c in channel_list},
                      "margen_eur_ha": margin, "agua": w, "clima_malo": bad_climate,
                      "malo": bad_climate or bad_money, "con_precio": margin is not None,
                      "por_que_malo": [r for r, b in (("clima", bad_climate), ("dinero", bad_money)) if b],
                      "dias_rellenados": sum(bool(d.filled) for d in days)})

    hazards = [h for h in ("frost", "heat") if sm.thresholds(crop, h) is not None]
    counted = [r for r in years if r["con_precio"]] if can_margin else years
    n, bad = len(counted), sum(r["malo"] for r in counted)
    if can_margin and len(counted) < len(years):
        gaps.append(f"{len(years) - len(counted)} de {len(years)} años sin precio: fuera del % de éxito")
    if not hazards and not can_margin:
        exito = {"valor": None, "horquilla": None, "k_malos": None, "n": len(years), "metodo": None,
                 "definicion": "NO EVALUABLE: sin umbrales de clima ni precio/coste; no se muestra % de éxito"}
    else:
        worst = sorted(counted, key=lambda r: (-(r["perdida_clima"]), r["margen_eur_ha"] or 0))[:3]
        definicion = ("años con pérdida clima < 20 % Y margen >= 0" if hazards and can_margin else
                      "SOLO ECONÓMICO (clima no evaluado: faltan umbrales): años con margen >= 0" if can_margin else
                      "SOLO CLIMA (falta precio/coste/rendimiento): años con pérdida clima < 20 %")
        exito = {**stats.success(bad, n), "peores_anios": [r["anio_cosecha"] for r in worst if r["malo"]],
                 "definicion": definicion, "anios_con_dato": n, "anios_totales": len(years)}
    margins = [r["margen_eur_ha"] for r in counted if r["margen_eur_ha"] is not None]
    gross = [r["agua"]["bruto_m3_ha"] for r in years if r["agua"]]
    mins = [r["precio_minimo"] for r in years if r["precio_minimo"] is not None]
    return {
        "producto": crop.crop_id, "etiqueta": meta.get("label", crop.crop_id), "cultivo_base": base_crop,
        "apto": not why_not, "motivos": why_not, "siembra": f"{month:02d}-{day:02d}", "ciclo_dias": n_days,
        "exito_pct": exito,
        "margen_eur_ha": None if not margins else {
            "p10": stats.quantile(margins, 0.1), "p50": stats.quantile(margins, 0.5),
            "p90": stats.quantile(margins, 0.9), "media": sum(margins) / len(margins),
            "cvar80": stats.cvar(margins, 0.8), "n": len(margins), "euros_de": base_year},
        "agua_m3_ha": None if not gross else {"p10": stats.quantile(gross, 0.1), "p50": stats.quantile(gross, 0.5),
                                              "p90": stats.quantile(gross, 0.9)},
        "_validacion_agua_imida_m3_ha": crop.get("riego_dosis"),  # internal check only, not shown (Enrique)
        "precio": {"nivel": tier, "fuente": tier_label, "unidad": unit, "euros_de": base_year,
                   "precio_minimo_p50": stats.quantile(mins, 0.5) if mins else None,
                   "canales": [c["id"] for c in channel_list], "nacional_eurostat_info": euro_info,
                   "opciones_usuario": mk.USER_PRICE_OPTIONS,
                   "recalculo": "margen_anio = cantidad_ha x precio_elegido - coste_eur_ha; año malo si "
                                "clima_malo o margen < 0"},
        "licencia": {"solo_uso_interno": m.restricted_used,
                     "fuentes_restringidas": mk.RESTRICTED_SOURCES if m.restricted_used else {}},
        "huecos": gaps, "evidencia": evidence,
        "supuestos": {k2: v[1] for k2, v in sm.ASSUMPTIONS.items()},
        "anios": years,
    }


def demo(base_year=2025, allow_restricted=False):
    crops = data.load_crops()
    products = data.load_products(crops)
    climate, meta = data.load_climate()
    prices, hicp, area, carm = data.load_prices(), data.load_hicp(), data.load_area(), data.load_carm_monthly()
    print(f"clima: {meta}")
    print("precios CARM (licencia restringida, SOLO USO INTERNO)" if allow_restricted else
          "solo datos abiertos (Eurostat); añade --interno para usar precios CARM")
    print(f"{'producto':20} {'precio':6} {'n':>3} {'malos':>5} {'éxito':>6} {'horquilla':>10}  "
          f"{'margen P10/P50/P90 €/ha':>24}  {'P50 precio / mínimo':>21}  agua P50")
    for pid, (crop, pm) in products.items():
        if pid == "veza":
            continue
        r = evaluate(crop, climate, prices, hicp, area, base_year=base_year, meta=pm, carm=carm,
                     allow_restricted=allow_restricted)
        if "exito_pct" not in r:
            print(f"{pid:20} no evaluable: {r['motivos']}")
            continue
        e, mg, a, p = r["exito_pct"], r["margen_eur_ha"], r["agua_m3_ha"], r["precio"]
        if e["valor"] is None:
            print(f"{pid:20} {'-':6} {e['n']:>3}  no evaluable; agua P50 {a['p50'] if a else 0:.0f}")
            continue
        ps = [x["precio"] for x in r["anios"] if x["precio"] is not None]
        u = "€/ud" if p["unidad"] == "eur_ud" else "€/kg"
        pmin = p["precio_minimo_p50"]
        ms = "-" if not mg else f"{mg['p10']:>7.0f}/{mg['p50']:>7.0f}/{mg['p90']:>7.0f}"
        price_s = f"{stats.quantile(ps, .5):.2f}/{pmin:.2f} {u}" if ps and pmin else "-"
        print(f"{pid:20} {'nivel' + str(p['nivel']):6} {e['n']:>3} {e['k_malos']:>5} {e['valor'] * 100:>5.0f}% "
              f"{e['horquilla'][0] * 100:>4.0f}-{e['horquilla'][1] * 100:<4.0f}%  {ms:>24}  {price_s:>21}  "
              f"{a['p50'] if a else 0:.0f}")
    return products


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--interno"]
    demo(int(args[0]) if args else 2025, allow_restricted="--interno" in sys.argv)
