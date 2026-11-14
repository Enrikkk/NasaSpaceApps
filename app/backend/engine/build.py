"""Build the per-parcel JSON (T-020): rotations with criteria, scenario samples, legal light, evidence, slider variants.

  python3 -m app.backend.engine.build torre-pacheco            -> app/data/torre-pacheco.json         (WITH CARM Murcia prices)
  python3 -m app.backend.engine.build torre-pacheco --abierto  -> app/data/torre-pacheco.abierto.json (no CARM prices: fallback)

DECISION Enrique 2026-11-14 (chat, overrides the earlier "nothing published with CARM until permission"): the published JSON
uses the CARM yearbook prices although written permission is still pending (email to agri-estadistica@carm.es not yet
answered). Risk: esam.carm.es/legal allows personal non-commercial use and no modification. The JSON states this in
`licencia` and cites the source; keep the open-data twin file so we can switch back at once if CARM refuses.

Blocks the engine does not produce yet (parcel, ndvi, soil: T-011/T-013) are copied from the contract mock and keep
their MOCK label in `_estado_bloques`. The block `clima` is computed here from the SIAM station series.
"""
import csv
import datetime as dt
import json
import pathlib
import statistics
import sys

from . import parcela as pc
from .core import data, market as mk_mod, stage_risk, stats
from .decision import rotations as rt, rules, strategies as st, texts

DATA = pathlib.Path(__file__).resolve().parents[2] / "data"
VARIANTS = {"lluvia_-30": (-30, 0.0), "lluvia_-15": (-15, 0.0), "lluvia_+10": (10, 0.0), "temp_+1": (0, 1.0),
            "temp_+2": (0, 2.0), "2050": (-12, 1.8)}   # 2050 = deltas of the contract mock, SIMULATED (no NEX-GDDP yet)
ACTUAL = (("melon_piel_de_sapo", "05-01"), ("lechuga_iceberg", "11-01"))   # melon, fallow, lettuce (the parcel's habit)
mk_restricted = mk_mod.RESTRICTED_SOURCES
MAPA_LABEL = "MAPA, media nacional anual del cultivo en general (proxy)"
SOURCES = {r["source_id"]: r for r in csv.DictReader(open(data.OFFICIAL / "sources.csv", encoding="utf-8"))}


def r0(x):
    return None if x is None else round(x)


def sequence(opt_static):
    """['melon','barbecho','lechuga'] for one plan-year: fallow shown where the gap between cycles exceeds 30 days;
    the winter cover is named in the gap that holds the longest bare autumn-winter stretch."""
    cs = sorted(opt_static["cycles"], key=lambda c: c["start_doy"])
    gaps = []
    for i, c in enumerate(cs):
        nxt = cs[i + 1]["start_doy"] if i + 1 < len(cs) else cs[0]["start_doy"] + 365
        end = c["start_doy"] + c["days"] + rt.GAP_DAYS
        gaps.append((sum(rules.in_winter((d - 1) % 365 + 1) for d in range(end, nxt)), nxt - c["start_doy"] - c["days"]))
    cover_at = max(range(len(cs)), key=lambda i: gaps[i][0]) if opt_static["covered"] else None
    out = []
    for i, c in enumerate(cs):
        out.append(c["label"])
        if i == cover_at:
            out.append("cubierta de veza")
        elif gaps[i][1] > 30 and i + 1 < len(cs):
            out.append("barbecho")
    return out


def plan_text(path, run_static):
    years = [", ".join(sequence(rt.option_static(o, run_static))) for o in path]
    return years[0] if len(set(years)) == 1 else " → ".join(f"año {i + 1}: {y}" for i, y in enumerate(years))


def stage_summary(path, static, compact=False):
    """Stage-risk blocks of the cycles in the rotation (each product/sowing once)."""
    seen, out = set(), []
    for o in path:
        for k in o.keys:
            if k in seen:
                continue
            seen.add(k)
            etapas = static[k]["riesgo_etapas"]["etapas"]
            if compact:
                etapas = [{"id": e["id"], "anios_con_episodio": e["anios_con_episodio"], "n": e["n"], "nivel": e["nivel"]}
                          for e in etapas if e["nivel"] != "sin evidencia"]
            out.append({"producto": static[k]["label"], "siembra": k[1], "n_ciclos": static[k]["riesgo_etapas"]["n_ciclos"],
                        "etapas": etapas})
    return out


def stage_risk_texts(path, static):
    out = []
    for blk in stage_summary(path, static):
        for e in blk["etapas"]:
            if e["nivel"] in ("medio", "alto"):
                out.append(f"{blk['producto']}, {e['organo']} ({e['desde']} a {e['hasta']}): {e['anios_con_episodio']} de {e['n']} años con "
                           f"exposición ({e['condicion']}; proxy de estación, no daño observado) → riesgo {e['nivel']} "
                           f"({e['gravedad']}; {e['fuente']}, confianza {e['conf']})")
        sin = [e for e in blk["etapas"] if e["nivel"] == "sin evidencia"]
        if sin:
            out.append(f"{blk['producto']}: sin evidencia documentada en " + "; ".join(
                f"{e['etapas_fao'][0]} ({e['peligro']})" for e in sin) + ": no es lo mismo que riesgo bajo")
    return out


def evidence_for(keys_used, static, extra):
    seen, out = set(), []
    for k in keys_used:
        for e in static[k]["report"]["evidencia"]:
            tag = (static[k]["crop"], e["param"], e["fuente"])
            if tag in seen:
                continue
            seen.add(tag)
            s = SOURCES.get(e["fuente"], {})
            out.append({"dato": f"{static[k]['label']}: {e['param']} = {e['valor']} {e.get('unidad', '')}".strip(),
                        "dataset": s.get("dataset", e["fuente"]), "fuente_id": e["fuente"], "url": s.get("url", ""),
                        "escala": "cultivo en Murcia (no de la parcela)", "confianza": e.get("conf")})
    if any(static[k]["report"]["precio"]["nivel"] in (1, 2) for k in keys_used):
        c = SOURCES["CARM-ANUARIO"]
        out.append({"dato": "Precios mensuales percibidos por el agricultor, por variedad (orientativos)", "dataset": c["dataset"],
                    "fuente_id": "CARM-ANUARIO", "url": c["url"], "escala": "Región de Murcia, 2002-2023",
                    "confianza": "M", "aviso": "uso bajo permiso pendiente de la CARM; cotización orientativa, no precio pactado"})
    proxies = [static[k]["label"] for k in keys_used if static[k]["report"]["precio"].get("tipo") == "proxy"]
    if proxies:
        out.append({"dato": "Precio medio nacional anual percibido por el agricultor, cultivo en general (PROXY): "
                            + ", ".join(sorted(set(proxies))),
                    "dataset": "MAPA, Índices y Precios Percibidos Agrarios (anual)", "fuente_id": "MAPA-PER-2024",
                    "url": data.load_mapa_prices()[1]["MAPA-PER-2024"]["url"],
                    "escala": "España, 2005-2024 (no Murcia, no la variedad)", "confianza": "B",
                    "aviso": "proxy nacional genérico; reutilización citando la fuente (Ley 37/2007), no es licencia CC; "
                             "no verificado si el precio incluye la recolección"})
    return extra + out


def price_notes(keys_used, static):
    notes = set()
    for k in keys_used:
        p = static[k]["report"]["precio"]
        notes.add(f"{static[k]['label']}: precio de referencia = {p['fuente']} (nivel {p['nivel']})" if p["nivel"] else
                  f"{static[k]['label']}: SIN precio de referencia abierto (el agricultor debe introducir el suyo)")
    return sorted(notes)


def rotation(rid, name, path, static, runs, shared, crops, actual=False, strategies=(), common=None, zona=None, regadio=True):
    sim = st.simulate(path, runs, shared, common=common)
    water_draws = sim["agua"] if sim else st.simulate_water(path, runs, shared)
    raw = st.raw_criteria(path, static, runs, sim, None)
    sts = [rt.option_static(o, static) for o in path]
    keys_used = sorted({k for o in path for k in o.keys})
    legal = rules.semaforo([{"cycles": s["cycles"], "bare_run": s["bare_run"], "covered": s["covered"]} for s in sts],
                           zona=zona, regadio=regadio)
    first = sorted(sts[0]["cycles"], key=lambda c: c["start_doy"])[0]
    caja = [c["caja"] for s in sts for c in s["cycles"] if c["caja"] is not None]
    waters = [sum(v["agua"] for v in rt.year_values(o, runs).values()) / len(rt.year_values(o, runs)) for o in path]
    gaps = [f"{static[k]['label']}: {h}" for k in keys_used for h in static[k]["report"]["huecos"]
            if "umbral de" not in h and "CE del agua" not in h]
    gaps += ["ningún cultivo tiene un par t0/t100 de daño por frío o calor validado (T-021): el clima NO resta kilos; "
             "se avisa por etapa con riesgo_etapas (frecuencia en 19 años)",
             "CE del agua de riego de la parcela desconocida: no se aplica la pérdida por sal",
             "sobreoferta (efecto de la superficie plantada en el precio) pendiente de diseñar",
             "alcachofa se trata como cultivo de un año (en realidad dura varios)",
             "cubierta de veza: coste (120 €/ha) y crédito de nitrógeno (110 kg N/ha) son supuestos, no medidos",
             "semáforo legal provisional: tabla T-019 pendiente y Zona 1/2 de la parcela sin confirmar"]
    if sim is None:
        gaps.insert(0, "sin precio de referencia para algún cultivo de esta rotación: margen y % de éxito NO evaluables")
    risks = []
    if sim:
        risks.append(f"peores años del histórico para el primer año del plan: {', '.join(map(str, sim['peores_anios']))}")
    risks += stage_risk_texts(path, static)
    risks += price_notes(keys_used, static)
    risks.append("clima: la rotación se evalúa con 19 años de SIAM, no con un pronóstico")
    out = {"id": rid, "nombre": name, "es_actual": actual, "estrategias": list(strategies),
           "ciclos": sequence(sts[0]),
           "plan_anios": [{"anio_plan": i + 1, "ciclos": sequence(s), "opcion": o.name(static),
                           "ciclos_por_anio": len(o.keys),
                           "ciclos_detalle": [{"producto": static[k]["label"], "cultivo": static[k]["crop"], "siembra": k[1],
                                               "ciclo_dias": static[k]["days"],
                                               "primera_cosecha_dias": static[k]["first_harvest_day"]} for k in o.keys],
                           "siembras": {static[k]["label"]: k[1] for k in o.keys}} for i, (o, s) in enumerate(zip(path, sts))],
           "horizonte_anios": len(path),
           "anios": [[c["crop"] for c in sorted(s["cycles"], key=lambda c: c["start_doy"])] for s in sts],
           "ciclos_por_anio": max(len(s["cycles"]) for s in sts),
           "ciclo_dias": {c["crop"]: c["days"] for s in sts for c in s["cycles"]},
           "semaforo_legal": legal,
           "riesgo_etapas": stage_summary(path, static),
           "inversion": {"pico_caja_negativa_eur_ha": r0(max(caja)) if caja else None,
                         "meses_hasta_primer_ingreso": round(first["first_harvest_day"] / 30.4, 1)},
           "agua_m3_ha": r0(statistics.median(water_draws)) if water_draws else r0(statistics.mean(waters)),
           "agua_detalle": {"bruto_m3_ha": {"p10": r0(stats.quantile(water_draws, .1)), "p50": r0(stats.quantile(water_draws, .5)),
                                            "p90": r0(stats.quantile(water_draws, .9))} if water_draws else
                            {"media_anual": r0(statistics.mean(waters))},
                            "coste_eur_ha": None, "perdida_sal_pct": None},
           "sobreoferta": None, "sobreoferta_detalle": {"semaforo": "gris", "_status": "cargando",
                                   "nota": "sobreoferta (efecto de la superficie plantada en el precio) pendiente de diseñar"},
           "_raw": raw, "_sim": sim, "huecos": gaps, "riesgos": risks,
           "evidencia": evidence_for(keys_used, static, [
               {"dato": "Clima diario 2005-2024 de la estación más cercana (Torre Pacheco)", "dataset": SOURCES["SIAM-TP91"]["dataset"],
                "fuente_id": "SIAM-TP91", "url": SOURCES["SIAM-TP91"]["url"], "escala": "estación a pocos km de la parcela"},
               {"dato": "Costes por hectárea y tipo de cultivo (IMIDA)", "dataset": SOURCES["IMIDA-HORT2020"]["dataset"],
                "fuente_id": "IMIDA-HORT2020", "url": SOURCES["IMIDA-HORT2020"]["url"], "escala": "Región de Murcia"}])}
    if sim:
        q = lambda p: stats.quantile(sim["margen"], p)
        out["exito_pct"] = {**{k: v for k, v in stats.success(sim["k_malos"], sim["n"]).items()},
                            "n_anios_historicos": sim["n"], "n_efectivo": sim["n"], "n_muestras": sim["n_muestras"],
                            "peores_anios": [{"anio": y, "margen_eur_ha": r0(m)} for y, m in sim["peores_anios_margen"]],
                            "definicion": f"n = n_anios_historicos = {sim['n']}: años del histórico en los que todos los años del plan "
                                          "tienen precio. Un año es malo si algún año del plan tiene pérdida de clima, o si el margen medio "
                                          "del plan en ese año es negativo. El intervalo de Wilson usa ese n. " + f"n_muestras = {sim['n_muestras']} "
                                          "conserva el conteo antiguo (año del plan x año del histórico), que no son observaciones independientes."}
        out["exito_pct"]["valor"] = round(out["exito_pct"]["valor"] * 100, 1)
        out["exito_pct"]["horquilla"] = [round(x * 100, 1) for x in out["exito_pct"]["horquilla"]]
        out["margen_eur_ha"] = {"valor": r0(q(.5)), "horquilla": [r0(q(.1)), r0(q(.9))], "p10": r0(q(.1)), "p50": r0(q(.5)),
                                "p90": r0(q(.9)), "media": r0(sim["margen_medio"]), "cvar80": r0(stats.cvar(sim["margen"], .8)),
                                "unidad": "€ de 2025 por hectárea y año (media del plan)"}
        out["escenarios"] = [r0(x) for x in sim["margen"]]
        out["escenarios_margen_eur_ha"] = out["escenarios"]     # same list under the name gonzalo's UI reads
        out["escenarios_meta"] = {"n": len(out["escenarios"]), "semilla": sim["semilla"], "anio_clima": sim["anio_clima"],
                                  "factor_coste": sim["factor_coste"], "alineados": common is not None,
                                  "n_anios_comunes": len(common) if common is not None else None,
                                  "nota": "misma semilla y mismos números aleatorios en todas las rotaciones. Si alineados, el escenario i "
                                          "usa en cada año del plan el mismo año histórico (clima y precio emparejados) en todas las "
                                          "rotaciones evaluables: el conjunto común de años con precio."}
    else:
        out["exito_pct"] = {"valor": None, "horquilla": None, "k_malos": None, "n": 0, "metodo": None,
                            "definicion": "NO EVALUABLE: falta el precio de algún cultivo con datos abiertos"}
        out["margen_eur_ha"] = None
        out["escenarios"] = None
    out["suelo_desnudo_dias"] = round(statistics.mean(s["bare_days"] for s in sts))
    out["ambiente"] = pc.ambiente(out["agua_m3_ha"], statistics.mean(s["bare_days"] for s in sts),
                                  statistics.mean(s["n_credit"] for s in sts), legal)
    return out


def climate_block(climate):
    years = sorted({d.year for d in climate})
    full = [y for y in years if sum(1 for d in climate if d.year == y) >= 360]
    rain = [sum(v.rain for d, v in climate.items() if d.year == y) for y in full]
    hot = [sum(1 for d, v in climate.items() if d.year == y and v.tmax > 38) for y in full]
    frost = [sum(1 for d, v in climate.items() if d.year == y and v.tmin < 0) for y in full]
    serie = [{"anio": y, "lluvia_mm": r0(rain[i]), "tmax_abs_c": round(max(v.tmax for d, v in climate.items() if d.year == y), 1),
              "tmin_abs_c": round(min(v.tmin for d, v in climate.items() if d.year == y), 1), "dias_calor_gt_38": hot[i],
              "dias_helada": frost[i]} for i, y in enumerate(full)]
    return {"serie_anual": serie, "lluvia_anual_mm": {"valor": r0(statistics.median(rain)), "horquilla": [r0(stats.quantile(rain, .1)), r0(stats.quantile(rain, .9))],
                                "fuentes": ["SIAM TP91"], "anios": f"{full[0]}-{full[-1]} ({len(full)} años completos)"},
            "dias_calor_gt_38": {"valor": r0(statistics.median(hot)), "media": round(statistics.mean(hot), 1)},
            "dias_helada": {"valor": r0(statistics.median(frost)), "media": round(statistics.mean(frost), 1),
                            "nota": "días con mínima < 0 °C en la estación SIAM"},
            "escenario_2050": {"lluvia_pct": -12, "temp_c": 1.8, "_status": "simulado (deltas del contrato, no NEX-GDDP)"}}


def build(parcel="torre-pacheco", allow_restricted=False, base_year=2025, parcel_input=None):
    """Engine output for the demo parcel (parcel_input None: same figures as always) or for ANY parcel (H-002).

    parcel_input = dict ParcelInput (see run_parcel). The parcel changes: which crops are in the catalog (exclusions),
    the DP score of each year option (suitability factor), the reference rotation, the legal zone and the labels.
    It does NOT change euros, kilos or success figures of a given rotation: the climate is the same station."""
    crops = data.load_crops()
    products = data.load_products(crops)
    climate, cmeta = data.load_climate()
    prices, hicp, area, carm = data.load_prices(), data.load_hicp(), data.load_area(), data.load_carm_monthly()
    national, mapa_src = {}, {}
    if not allow_restricted:   # step E: open build -> MAPA generic national price as an explicit proxy (lettuce by the kilo)
        mapa, mapa_src = data.load_mapa_prices()
        prices = {**prices, **mapa}
        national = {c: MAPA_LABEL for c in mapa}
    cycles = lambda clim: rt.run_cycles(products, clim, prices, hicp, area, carm, base_year, allow_restricted,
                                        kg_fallback=False, national=national)   # lechuga: el MAPA nacional mezcla tipos y queda ~35 % bajo el iceberg de Murcia -> sin precio abierto (decision Enrique 2026-11-14)
    static = cycles(climate)
    suit = pc.evaluar(parcel_input, static) if parcel_input is not None else None
    keep = (lambda s_: {k: v for k, v in s_.items() if k[0] not in suit["excluidos_ids"]}) if suit else (lambda s_: s_)
    static = keep(static)
    zona = (parcel_input or {}).get("zona_legal")
    regadio = parcel_input.get("regadio") if parcel_input is not None else True
    regadio = regadio if isinstance(regadio, bool) else None
    factor = (lambda o: pc.option_factor(o, suit["factores"])) if suit else None
    shared = st.draws()
    opts = rt.build_options(static, crops) if static else []
    scores = st.option_scores(opts, static, static) if opts else {}
    if parcel_input is None:
        actual_keys, actual_origen, actual_info = ACTUAL, "habito_parcela_demo", {}
    else:
        actual_keys, actual_origen, actual_info = pc.actual(parcel_input, static, ACTUAL)
    named = [("actual", None, [rt.Option(actual_keys)] * rt.HORIZON)] if actual_keys else []
    for sid, cfg in st.STRATEGIES.items():
        p = st.dp(scores, static, crops, cfg["w"], cfg["ruinosa"], factor=factor) if scores else None
        if p:
            named.append((sid, cfg["nombre"], p))
    merged = []   # one rotation per distinct path
    for sid, nm, p in named:
        for m in merged:
            if m["path"] == p and sid != "actual":
                m["strategies"].append(sid)
                break
        else:
            merged.append({"path": p, "strategies": [sid], "name": nm})
    labels = {"S1": "Máximo margen", "S2": "Suelo y agua", "S3": "Riesgo bajo"}

    def names(m, run_static):
        if m["strategies"] == ["actual"]:
            head = {"supuesto_zona": "Referencia de la zona (supuesto): ",
                    "declaracion_fega": "Lo que haces hoy (según tu declaración a FEGA): "}.get(actual_origen, "Lo que haces hoy: ")
            return "actual", head + plan_text(m["path"], run_static)
        sid = m["strategies"][0].lower()
        return f"{sid}-{'-'.join(m['strategies'][1:]).lower()}".rstrip("-") if len(m["strategies"]) > 1 else sid, \
            " / ".join(labels[s] for s in m["strategies"]) + ": " + plan_text(m["path"], run_static)

    def common_years(runs):
        """Intersection of historical years with a price, over rotations that can be scored."""
        sets = []
        for m in merged:
            ys = st.money_years(m["path"], runs)
            if ys:
                sets.append(set(ys))
        return sorted(set.intersection(*sets)) if sets else []

    def assemble(run_static, runs):
        common = common_years(runs)
        rots = []
        for m in merged:
            own = st.money_years(m["path"], runs)
            rid, nm = names(m, static)
            rots.append(rotation(rid, nm, m["path"], static, runs, shared, crops, actual=m["strategies"] == ["actual"],
                                 strategies=m["strategies"], common=common if own else None, zona=zona, regadio=regadio))
            if suit:
                rots[-1]["idoneidad"] = pc.idoneidad_rotacion(m["path"], suit)
                tot = pc.totales_parcela(rots[-1], parcel_input.get("area_ha"))
                if tot:
                    rots[-1]["totales_parcela"] = tot
        crit = st.normalise_rotations([r["_raw"] for r in rots])
        for r, c in zip(rots, crit):
            r["criterios"] = c
        return rots, len(common)

    rots, n_common = assemble(static, static)
    for rr in rots:
        sim = rr["_sim"]
    variants = {}
    common_by_variant = {"base": n_common}
    for vid, (rain, temp) in VARIANTS.items():
        vs = keep(cycles(rt.perturb(climate, rain, temp)))
        vr, n_var = assemble(vs, vs)
        common_by_variant[vid] = n_var
        variants[vid] = {"lluvia_pct": rain, "temp_c": temp, "n_anios_comunes": n_var,
                         "_status": "simulado: lluvia/temperatura desplazadas sobre el histórico; ET0 +4 %/°C (supuesto)",
                         "rotaciones": {r["id"]: {"exito_pct": r["exito_pct"]["valor"], "margen_p50": (r["margen_eur_ha"] or {}).get("p50"),
                                                  "agua_m3_ha": r["agua_m3_ha"], "criterios": r["criterios"], "escenarios": r["escenarios"],
                                                  "riesgo_etapas": stage_summary(merged[i]["path"], vs, compact=True)}
                                        for i, r in enumerate(vr)}}
    for r in rots:
        r["variantes"] = {vid: {"exito_pct": v["rotaciones"][r["id"]]["exito_pct"], "margen_p50": v["rotaciones"][r["id"]]["margen_p50"],
                                "agua_m3_ha": v["rotaciones"][r["id"]]["agua_m3_ha"], "criterios": v["rotaciones"][r["id"]]["criterios"],
                                "escenarios": v["rotaciones"][r["id"]]["escenarios"], "riesgo_etapas": v["rotaciones"][r["id"]]["riesgo_etapas"], "lluvia_pct": v["lluvia_pct"], "temp_c": v["temp_c"],
                                "n_anios_comunes": v["n_anios_comunes"],
                                "_status": v["_status"]} for vid, v in variants.items()}
        r.pop("_raw"), r.pop("_sim")
        why = {"actual": "Es lo que haces hoy; sirve de referencia para comparar."}
        r["por_que"] = why.get(r["id"]) or ("Sale de recorrer todas las combinaciones de cultivos permitidas durante 3 años y quedarse con la "
                                            f"mejor según el criterio «{r['nombre'].split(':')[0]}»; la web solo reordena con tus pesos.")
    mock = json.load(open(DATA / "torre-pacheco.mock.json", encoding="utf-8"))
    out = {k: v for k, v in mock.items() if k != "rotaciones"}
    out["clima"] = climate_block(climate)
    out["parcela"] = {**out["parcela"], "zonas": ["zona_vulnerable_nitratos", "mar_menor_zona_por_verificar"]}
    for blk in ("parcela", "ndvi", "suelo"):
        out[blk] = {**out[blk], "_status": "simulado"}      # mock -> simulado (gonzalo's vocabulary) until T-011/T-013
    out["clima"]["_status"] = "real"
    out["_status"] = ("Bloque `rotaciones` y `clima`: calculados por el motor. Precios: "
                      + ("CARM (anuarios) con Eurostat de respaldo; permiso de la CARM pendiente" if allow_restricted else
                         "sin precios CARM; MAPA nacional como proxy (lechuga, melón, alcachofa) y Eurostat")
                      + ". Derechos del resto de fuentes (IMIDA, SIAM, FAO) según el registro de fuentes, sin verificar. "
                        "Bloques parcela, historia, ndvi, suelo: MOCK hasta T-011/T-013.")
    out["_estado_bloques"] = {"rotaciones": "real", "clima": "real", "escenario_2050": "simulado", "variantes": "simulado",
                              "parcela": "mock", "historia": "mock", "ndvi": "mock", "suelo": "mock", "semaforo_legal": "provisional"}
    out["licencia"] = {"incluye_precios_carm": allow_restricted,
                       "estado": ("permiso solicitado a la CARM, pendiente; su aviso legal permite uso personal no comercial y sin "
                                  "modificación; el equipo decidió usarlos igualmente (Enrique, 2026-11-14): citar la fuente"
                                  if allow_restricted else "sin precios CARM"),
                       "fuentes_restringidas": mk_restricted if allow_restricted else {}}
    out["rotaciones"] = rots
    con = [r for r in rots if isinstance(r.get("escenarios"), list)]
    out["escenarios_meta"] = {"alineados": bool(con) and all((r.get("escenarios_meta") or {}).get("alineados") is True for r in con),
                              "n": st.N_SAMPLES, "semilla": 2026, "n_anios_comunes": n_common,
                              "nota": "alineados = true solo si lo es en todas las rotaciones con escenarios (D-011)"}
    out["actual_origen"] = actual_origen
    if parcel_input is not None:
        out["parcela_input"] = parcel_input
        out["idoneidad"] = pc.resumen(parcel_input, suit, actual_origen, actual_info)
        out["clima_origen"] = pc.clima_origen(parcel_input, cmeta)
        if not rots:
            out["no_evaluable"] = {
                "motivo": ("No podemos evaluar esta parcela: consta como secano y solo tenemos datos de coste y de "
                           "rendimiento de cultivos de regadío." if suit["excluidos_ids"] and not static else
                           "No hemos encontrado ninguna rotación que se pueda evaluar en esta parcela."),
                "_status": "real"}
    out["criterios_sentido"] = "1 = mejor en los cuatro (más margen, MENOS agua, más suelo/N, MENOS riesgo), relativo a las rotaciones mostradas"
    out["supuestos_decision"] = {"horizonte_anios": rt.HORIZON, "muestras": st.N_SAMPLES,
                                 "coste_banda": list(st.COST_BAND), "dias_entre_ciclos": rt.GAP_DAYS,
                                 "siembra": "fecha base y +15 días (no se adelanta mientras no haya umbrales de helada validados)",
                                 "cubierta_coste_eur_ha": rt.COVER_COST_EUR_HA, "et0_por_grado": rt.ET0_PER_DEGC}
    out["generado"] = dt.date.today().isoformat()
    out["schema_version"] = "1.0.0"
    out["_meta"] = {"version": "1.0.0", "aviso": "Bloques parcela, historia, ndvi y suelo son MOCK (simulado) hasta T-011/T-013; "
                    "rotaciones y clima los calcula el motor con datos reales (SIAM, CARM/Eurostat, IMIDA, FAO)", "generado": out["generado"], "semilla_escenarios": 2026, "muestras": st.N_SAMPLES,
                    "euros_de": base_year, "motor": "app/backend/engine (T-012/T-018/T-020)"}
    used = sorted({e["fuente_id"] for r in rots for e in r["evidencia"]} | {"SIAM-TP91", "EUR-HICP"})
    out["fuentes"] = [{"id": i, "nombre": SOURCES[i]["dataset"], "url": SOURCES[i]["url"], "licencia": SOURCES[i]["licence"]}
                      for i in used if i in SOURCES]
    if any(e["fuente_id"].startswith("MAPA-PER") for r in rots for e in r["evidencia"]):
        out["fuentes"] += [{"id": i, "nombre": "MAPA, Índices y Precios Percibidos Agrarios (anual), libro " + i[-4:],
                            "url": m["url"], "licencia": m["licencia"], "aviso_legal": m["aviso_legal"],
                            "nota": "proxy nacional genérico (conf. " + m["conf"] + ")"} for i, m in sorted(mapa_src.items())]
    thermal = sorted({e["fuente"] for r in rots for b in r["riesgo_etapas"] for e in b["etapas"] if e["fuente"]})
    out["fuentes"] += [{"id": i, "nombre": stage_risk.SOURCES[i][0], "url": stage_risk.SOURCES[i][1],
                        "licencia": stage_risk.SOURCES[i][2]} for i in thermal]
    for r in rots:
        r["_status"] = "real"
    texts.apply(out)
    return out


def run_parcel(parcel_input, allow_restricted=False, base_year=2025):
    """Engine for ANY parcel (H-002). parcel_input: dict with any of
        parcel_id, lat, lon, area_ha, regadio (bool|None), pendiente_pct, zona_legal ('zona_1'|'zona_2'|other),
        suelo {textura, ph, materia_organica_pct, salinidad_ce_dsm, profundidad_cm, drenaje},
        cultivos_declarados [str | {cultivo|producto, ...}]
    Every field may be missing or None ("sin dato": never invented). Returns the same JSON as build() plus, per
    rotation, `idoneidad`; and at the root `idoneidad`, `clima_origen`, `parcela_input` and, when nothing can be
    evaluated (e.g. a rainfed parcel: the catalog only has irrigated crops), `no_evaluable` with `rotaciones: []`."""
    if not isinstance(parcel_input, dict):
        raise TypeError("parcel_input debe ser un dict")
    return build("parcela", allow_restricted=allow_restricted, base_year=base_year, parcel_input=parcel_input)


def main(argv):
    parcel = argv[0] if argv and not argv[0].startswith("--") else "torre-pacheco"
    open_only = "--abierto" in argv
    out = build(parcel, allow_restricted=not open_only)
    path = DATA / f"{parcel}{'.abierto' if open_only else ''}.json"
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"escrito {path} ({path.stat().st_size // 1024} KB)")
    for r in out["rotaciones"]:
        e, m = r["exito_pct"], r["margen_eur_ha"]
        print(f"{r['id']:9} {r['nombre'][:62]:62} éxito {e['valor']} {e['horquilla']}  margen {m and (m['p10'], m['p50'], m['p90'])}  "
              f"agua {r['agua_m3_ha']}  legal {r['semaforo_legal']['color']}  crit {r['criterios']}")


if __name__ == "__main__":
    main(sys.argv[1:])
