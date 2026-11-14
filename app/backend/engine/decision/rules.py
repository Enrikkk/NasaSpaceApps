"""Rotation rules for the decision layer: agronomic filter + PROVISIONAL legal traffic light.

T-019 (owner gonzalo, `app/backend/rules/`) will own the legal table. Until it lands, this module holds the same
interface (`allowed(prev, cur)`, `semaforo(...)`) with the rules we already verified in research/predictive-model-
research.md section G (Ley 3/2020 Mar Menor, BOE-A-2020-9793). Every legal rule carries its article. Nothing here is
legal advice. The parcel's Zone 1 / Zone 2 status is NOT confirmed (Annex I map not recovered), so rules that only
apply in Zone 1 give "por verificar" (amber) instead of red.
"""

# Ley 3/2020 art. 51: "grupo 1" = brassicas, leaf vegetables, onion, leek, aromatics. Alcachofa and haba are NOT confirmed.
GROUP1 = {"lechuga", "brocoli"}
UNCONFIRMED_GROUP = {"alcachofa", "haba"}
# kg N/ha left for the next crop by a legume or legume cover (research G: vezas 100-120, habas ~90-130; CSIC and
# Pommeresche & Hansen 2017, conf C). Used as a labelled assumption, not as a measurement.
N_CREDIT = {"veza": 110.0, "haba": 110.0}
WINTER = (274, 90)          # day-of-year window Oct 1 .. Mar 31 for art. 51.6 (bare irrigated soil)
BARE_LIMIT_DAYS = 60        # "more than 2 months" bare in autumn-winter


def family(crops, crop_id):
    c = crops.get(crop_id)
    return c.get("family") if c is not None else None


def allowed(crops, prev_crop, cur_crop):
    """Hard filter used by the DP between consecutive cycles. Conservative (safe side for the legal grey zone):
    never the same botanical family twice in a row (design value: minimum return = one cycle in between), and never
    two group-1 crops in a row (art. 51, Zone 1)."""
    if prev_crop is None or cur_crop is None:
        return True
    fp, fc = family(crops, prev_crop), family(crops, cur_crop)
    if fp and fc and fp == fc:
        return False
    if prev_crop in GROUP1 and cur_crop in GROUP1:
        return False
    return True


def in_winter(doy):
    return doy >= WINTER[0] or doy <= WINTER[1]


def semaforo(plan_years, zone_confirmed=False):
    """Traffic light for a multi-year plan. plan_years: [{"cycles": [{"crop","product"}...], "bare_run": int,
    "covered": bool}]. Returns {color, motivo, articulo, comprobaciones[]}; color = worst of the checks."""
    checks = []
    n_cycles = max(len(p["cycles"]) for p in plan_years)
    checks.append({"regla": "máximo 2 ciclos por año (3 solo hoja de < 45 días)", "articulo": "Ley 3/2020 art. 39",
                   "resultado": "ok" if n_cycles <= 2 else "incumple",
                   "detalle": f"{n_cycles} ciclos como máximo en un año"})
    g1_year = max(sum(c["crop"] in GROUP1 for c in p["cycles"]) for p in plan_years)
    seq = [c["crop"] for p in plan_years for c in p["cycles"]]
    g1_row = any(a in GROUP1 and b in GROUP1 for a, b in zip(seq, seq[1:] + seq[:1]) if len(seq) > 1)
    ok_g1 = g1_year <= 1 and not g1_row
    checks.append({"regla": "zona 1: un solo ciclo del grupo 1 al año y nunca dos seguidos", "articulo": "Ley 3/2020 art. 51",
                   "resultado": "ok" if ok_g1 else ("incumple_si_zona_1" if zone_confirmed is None else "por_verificar"),
                   "detalle": "grupo 1 = brásicas, hoja, cebolla, puerro, aromáticas; " +
                              ("no se repite" if ok_g1 else "se repite: solo es un problema en Zona 1 (parcela sin confirmar)")})
    unconf = sorted({c["crop"] for p in plan_years for c in p["cycles"] if c["crop"] in UNCONFIRMED_GROUP})
    if unconf:
        checks.append({"regla": "grupo legal del cultivo", "articulo": "Ley 3/2020 art. 51 (Anexo no leído)",
                       "resultado": "por_verificar", "detalle": f"grupo legal sin confirmar: {', '.join(unconf)}"})
    bare = max(p["bare_run"] for p in plan_years if not p["covered"]) if any(not p["covered"] for p in plan_years) else 0
    checks.append({"regla": "suelo de regadío desnudo más de 2 meses en otoño-invierno: cubierta", "articulo": "Ley 3/2020 art. 51.6",
                   "resultado": "ok" if bare <= BARE_LIMIT_DAYS else "aviso",
                   "detalle": f"tramo desnudo más largo sin cubierta: {bare} días (límite {BARE_LIMIT_DAYS})"})
    checks.append({"regla": "nitrógeno: sin urea ni N mineral de fondo; 170 kg N/ha", "articulo": "Ley 3/2020 arts. 29 y 40",
                   "resultado": "no_evaluado", "detalle": "depende del plan de abonado, que esta herramienta no define"})
    VOCAB = {"ok": "ok", "no_evaluado": "no_evaluable", "por_verificar": "no_evaluable", "aviso": "falla",
             "incumple_si_zona_1": "falla", "incumple": "falla"}
    for c in checks:   # team vocabulary (gonzalo, contract v1.1); the original severity stays in `severidad`
        c["severidad"] = c["resultado"]
        c["estado"] = "por_verificar"      # whole table is provisional until T-019 (gonzalo) verifies each rule
        c["resultado"] = VOCAB[c["resultado"]]
    rank = {"ok": 0, "no_evaluado": 0, "por_verificar": 1, "aviso": 1, "incumple_si_zona_1": 2, "incumple": 2}
    worst = max(checks, key=lambda c: rank[c["severidad"]])
    color = {0: "verde", 1: "amarillo", 2: "rojo"}[rank[worst["severidad"]]]
    reason = {"verde": "cumple las comprobaciones que podemos hacer; el abonado sigue por verificar",
              "amarillo": worst["detalle"], "rojo": worst["detalle"]}[color]
    if color == "verde":
        worst = next(c for c in checks if c["severidad"] == "ok")
    return {"color": color, "motivo": reason, "articulo": worst["articulo"], "comprobaciones": checks,
            "_status": "simulado", "provisional": True,
            "_nota": "provisional: tabla de T-019 pendiente; zona 1/2 de la parcela sin confirmar"}
