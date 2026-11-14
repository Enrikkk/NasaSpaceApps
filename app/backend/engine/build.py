"""Build the per-parcel JSON (T-020): rotations with criteria, scenario samples, legal light, evidence, slider variants.

  python3 -m app.backend.engine.build torre-pacheco            -> app/data/torre-pacheco.json         (OPEN DATA ONLY: publishable)
  python3 -m app.backend.engine.build torre-pacheco --interno  -> app/data/torre-pacheco.interno.json (uses CARM prices: NEVER publish)

Blocks the engine does not produce yet (parcel, ndvi, soil: T-011/T-013) are copied from the contract mock and keep
their MOCK label in `_estado_bloques`. The block `clima` is computed here from the SIAM station series.
"""
import csv
import datetime as dt
import json
import pathlib
import statistics
import sys

from .core import data, stats
from .decision import rotations as rt, rules, strategies as st

DATA = pathlib.Path(__file__).resolve().parents[2] / "data"
VARIANTS = {"lluvia_-30": (-30, 0.0), "lluvia_-15": (-15, 0.0), "lluvia_+10": (10, 0.0), "temp_+1": (0, 1.0),
            "temp_+2": (0, 2.0), "2050": (-12, 1.8)}   # 2050 = deltas of the contract mock, SIMULATED (no NEX-GDDP yet)
ACTUAL = (("melon_piel_de_sapo", "05-01"), ("lechuga_iceberg", "11-01"))   # melon, fallow, lettuce (the parcel's habit)
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
    return extra + out


def price_notes(keys_used, static):
    notes = set()
    for k in keys_used:
        p = static[k]["report"]["precio"]
        notes.add(f"{static[k]['label']}: precio de referencia = {p['fuente']} (nivel {p['nivel']})" if p["nivel"] else
                  f"{static[k]['label']}: SIN precio de referencia abierto (el agricultor debe introducir el suyo)")
    return sorted(notes)


def rotation(rid, name, path, static, runs, shared, crops, actual=False, strategies=()):
    sim = st.simulate(path, runs, shared)
    raw = st.raw_criteria(path, static, runs, sim, None)
    sts = [rt.option_static(o, static) for o in path]
    keys_used = sorted({k for o in path for k in o.keys})
    legal = rules.semaforo([{"cycles": s["cycles"], "bare_run": s["bare_run"], "covered": s["covered"]} for s in sts])
    first = sorted(sts[0]["cycles"], key=lambda c: c["start_doy"])[0]
    caja = [c["caja"] for s in sts for c in s["cycles"] if c["caja"] is not None]
    waters = [sum(v["agua"] for v in rt.year_values(o, runs).values()) / len(rt.year_values(o, runs)) for o in path]
    gaps = [f"{static[k]['label']}: {h}" for k in keys_used for h in static[k]["report"]["huecos"]
            if "umbral de" not in h and "CE del agua" not in h]
    gaps += ["umbrales de helada y calor sin evidencia primaria validada (T-021 en curso): el clima NO resta rendimiento todavía",
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
    risks += price_notes(keys_used, static)
    risks.append("clima: la rotación se evalúa con 19 años de SIAM, no con un pronóstico")
    out = {"id": rid, "nombre": name, "es_actual": actual, "estrategias": list(strategies),
           "ciclos": sequence(sts[0]),
           "plan_anios": [{"anio_plan": i + 1, "ciclos": sequence(s), "opcion": o.name(static),
                           "siembras": {static[k]["label"]: k[1] for k in o.keys}} for i, (o, s) in enumerate(zip(path, sts))],
           "horizonte_anios": len(path),
           "semaforo_legal": legal,
           "inversion": {"pico_caja_negativa_eur_ha": r0(max(caja)) if caja else None,
                         "meses_hasta_primer_ingreso": round(first["first_harvest_day"] / 30.4, 1)},
           "agua_m3_ha": r0(statistics.median(sim["agua"])) if sim else r0(statistics.mean(waters)),
           "agua_detalle": {"bruto_m3_ha": {"p10": r0(stats.quantile(sim["agua"], .1)), "p50": r0(stats.quantile(sim["agua"], .5)),
                                            "p90": r0(stats.quantile(sim["agua"], .9))} if sim else
                            {"media_anual": r0(statistics.mean(waters))},
                            "coste_eur_ha": None, "perdida_sal_pct": None},
           "sobreoferta": None, "sobreoferta_detalle": {"efecto_precio_pct": None, "semaforo": None, "_status": "pendiente"},
           "_raw": raw, "_sim": sim, "huecos": gaps, "riesgos": risks,
           "evidencia": evidence_for(keys_used, static, [
               {"dato": "Clima diario 2005-2024 de la estación más cercana (Torre Pacheco)", "dataset": SOURCES["SIAM-TP91"]["dataset"],
                "fuente_id": "SIAM-TP91", "url": SOURCES["SIAM-TP91"]["url"], "escala": "estación a pocos km de la parcela"},
               {"dato": "Costes por hectárea y tipo de cultivo (IMIDA)", "dataset": SOURCES["IMIDA-HORT2020"]["dataset"],
                "fuente_id": "IMIDA-HORT2020", "url": SOURCES["IMIDA-HORT2020"]["url"], "escala": "Región de Murcia"}])}
    if sim:
        q = lambda p: stats.quantile(sim["margen"], p)
        out["exito_pct"] = {**{k: v for k, v in stats.success(sim["k_malos"], sim["n"]).items()}, "peores_anios": sim["peores_anios"],
                            "definicion": "años (de cada año del plan) sin pérdida de clima >= 20 % y con margen >= 0; "
                                          "los años del histórico se reutilizan, por eso el intervalo es optimista"}
        out["exito_pct"]["valor"] = round(out["exito_pct"]["valor"] * 100, 1)
        out["exito_pct"]["horquilla"] = [round(x * 100, 1) for x in out["exito_pct"]["horquilla"]]
        out["margen_eur_ha"] = {"valor": r0(q(.5)), "horquilla": [r0(q(.1)), r0(q(.9))], "p10": r0(q(.1)), "p50": r0(q(.5)),
                                "p90": r0(q(.9)), "media": r0(sim["margen_medio"]), "cvar80": r0(stats.cvar(sim["margen"], .8)),
                                "unidad": "€ de 2025 por hectárea y año (media del plan)"}
        out["escenarios"] = [r0(x) for x in sim["margen"]]
    else:
        out["exito_pct"] = {"valor": None, "horquilla": None, "k_malos": None, "n": 0, "metodo": None,
                            "definicion": "NO EVALUABLE: falta el precio de algún cultivo con datos abiertos"}
        out["margen_eur_ha"] = None
        out["escenarios"] = None
    return out


def climate_block(climate):
    years = sorted({d.year for d in climate})
    full = [y for y in years if sum(1 for d in climate if d.year == y) >= 360]
    rain = [sum(v.rain for d, v in climate.items() if d.year == y) for y in full]
    hot = [sum(1 for d, v in climate.items() if d.year == y and v.tmax > 38) for y in full]
    frost = [sum(1 for d, v in climate.items() if d.year == y and v.tmin < 0) for y in full]
    return {"lluvia_anual_mm": {"valor": r0(statistics.median(rain)), "horquilla": [r0(stats.quantile(rain, .1)), r0(stats.quantile(rain, .9))],
                                "fuentes": ["SIAM TP91"], "anios": f"{full[0]}-{full[-1]} ({len(full)} años completos)"},
            "dias_calor_gt_38": {"valor": r0(statistics.median(hot)), "media": round(statistics.mean(hot), 1)},
            "dias_helada": {"valor": r0(statistics.median(frost)), "media": round(statistics.mean(frost), 1),
                            "nota": "días con mínima < 0 °C en la estación SIAM"},
            "escenario_2050": {"lluvia_pct": -12, "temp_c": 1.8, "_status": "simulado (deltas del contrato, no NEX-GDDP)"}}


def build(parcel="torre-pacheco", allow_restricted=False, base_year=2025):
    crops = data.load_crops()
    products = data.load_products(crops)
    climate, cmeta = data.load_climate()
    prices, hicp, area, carm = data.load_prices(), data.load_hicp(), data.load_area(), data.load_carm_monthly()
    static = rt.run_cycles(products, climate, prices, hicp, area, carm, base_year, allow_restricted)
    shared = st.draws()
    opts = rt.build_options(static, crops)
    scores = st.option_scores(opts, static, static)
    paths = {}
    actual_opt = rt.Option(ACTUAL)
    actual_path = [actual_opt] * rt.HORIZON
    named = [("actual", None, actual_path)]
    for sid, cfg in st.STRATEGIES.items():
        p = st.dp(scores, static, crops, cfg["w"], cfg["ruinosa"])
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
            return "actual", "Lo que haces hoy: " + plan_text(m["path"], run_static)
        sid = m["strategies"][0].lower()
        return f"{sid}-{'-'.join(m['strategies'][1:]).lower()}".rstrip("-") if len(m["strategies"]) > 1 else sid, \
            " / ".join(labels[s] for s in m["strategies"]) + ": " + plan_text(m["path"], run_static)

    def assemble(run_static, runs):
        rots = []
        for m in merged:
            rid, nm = names(m, static)
            rots.append(rotation(rid, nm, m["path"], static, runs, shared, crops, actual=m["strategies"] == ["actual"],
                                 strategies=m["strategies"]))
        crit = st.normalise_rotations([r["_raw"] for r in rots])
        for r, c in zip(rots, crit):
            r["criterios"] = c
        return rots

    rots = assemble(static, static)
    for rr in rots:
        sim = rr["_sim"]
    variants = {}
    for vid, (rain, temp) in VARIANTS.items():
        vs = rt.run_cycles(products, rt.perturb(climate, rain, temp), prices, hicp, area, carm, base_year, allow_restricted)
        vr = assemble(vs, vs)
        variants[vid] = {"lluvia_pct": rain, "temp_c": temp,
                         "_status": "simulado: lluvia/temperatura desplazadas sobre el histórico; ET0 +4 %/°C (supuesto)",
                         "rotaciones": {r["id"]: {"exito_pct": r["exito_pct"]["valor"], "margen_p50": (r["margen_eur_ha"] or {}).get("p50"),
                                                  "agua_m3_ha": r["agua_m3_ha"], "criterios": r["criterios"], "escenarios": r["escenarios"]}
                                        for r in vr}}
    for r in rots:
        r["variantes"] = {vid: {"exito_pct": v["rotaciones"][r["id"]]["exito_pct"], "margen_p50": v["rotaciones"][r["id"]]["margen_p50"],
                                "agua_m3_ha": v["rotaciones"][r["id"]]["agua_m3_ha"], "criterios": v["rotaciones"][r["id"]]["criterios"],
                                "escenarios": v["rotaciones"][r["id"]]["escenarios"], "lluvia_pct": v["lluvia_pct"], "temp_c": v["temp_c"],
                                "_status": v["_status"]} for vid, v in variants.items()}
        r.pop("_raw"), r.pop("_sim")
        why = {"actual": "Es lo que haces hoy; sirve de referencia para comparar."}
        r["por_que"] = why.get(r["id"]) or ("Sale de recorrer todas las combinaciones de cultivos permitidas durante 3 años y quedarse con la "
                                            f"mejor según el criterio «{r['nombre'].split(':')[0]}»; la web solo reordena con tus pesos.")
    mock = json.load(open(DATA / "torre-pacheco.mock.json", encoding="utf-8"))
    out = {k: v for k, v in mock.items() if k != "rotaciones"}
    out["clima"] = climate_block(climate)
    out["_status"] = ("Bloque `rotaciones` y `clima`: calculados por el motor con datos "
                      + ("INTERNOS (precios CARM): NO PUBLICAR" if allow_restricted else "ABIERTOS (SIAM, Eurostat, FAO, IMIDA)")
                      + ". Bloques parcela, historia, ndvi, suelo: MOCK hasta T-011/T-013.")
    out["_estado_bloques"] = {"rotaciones": "real", "clima": "real", "escenario_2050": "simulado", "variantes": "simulado",
                              "parcela": "mock", "historia": "mock", "ndvi": "mock", "suelo": "mock", "semaforo_legal": "provisional"}
    out["licencia"] = {"solo_uso_interno": allow_restricted}
    out["rotaciones"] = rots
    out["criterios_sentido"] = "1 = mejor en los cuatro (más margen, MENOS agua, más suelo/N, MENOS riesgo), relativo a las rotaciones mostradas"
    out["supuestos_decision"] = {"horizonte_anios": rt.HORIZON, "muestras": st.N_SAMPLES,
                                 "coste_banda": list(st.COST_BAND), "dias_entre_ciclos": rt.GAP_DAYS,
                                 "siembra": "fecha base y +15 días (no se adelanta mientras no haya umbrales de helada validados)",
                                 "cubierta_coste_eur_ha": rt.COVER_COST_EUR_HA, "et0_por_grado": rt.ET0_PER_DEGC}
    out["generado"] = dt.date.today().isoformat()
    return out


def main(argv):
    parcel = argv[0] if argv and not argv[0].startswith("--") else "torre-pacheco"
    internal = "--interno" in argv
    out = build(parcel, allow_restricted=internal)
    path = DATA / f"{parcel}{'.interno' if internal else ''}.json"
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"escrito {path} ({path.stat().st_size // 1024} KB)")
    for r in out["rotaciones"]:
        e, m = r["exito_pct"], r["margen_eur_ha"]
        print(f"{r['id']:9} {r['nombre'][:62]:62} éxito {e['valor']} {e['horquilla']}  margen {m and (m['p10'], m['p50'], m['p90'])}  "
              f"agua {r['agua_m3_ha']}  legal {r['semaforo_legal']['color']}  crit {r['criterios']}")


if __name__ == "__main__":
    main(sys.argv[1:])
