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


def _canon(legal, nombre):
    """Same normalisation as Gonzalo's legal_blocks.canon_cultivo. Unknown names stay unknown."""
    n = legal._norm(nombre)
    if n in legal.GRUPOS:
        return nombre
    sin_par = legal._norm(n.split("(")[0])
    if sin_par in legal.GRUPOS:
        return sin_par
    for clave in sorted(legal.GRUPOS, key=len, reverse=True):
        if sin_par.startswith(clave + " "):
            return clave
    return nombre


def semaforo(plan_years, zone_confirmed=False):
    """Traffic light via Gonzalo's legal.check. The agronomic DP filter is allowed(), not this.

    The parcel's Mar Menor zone is unconfirmed, so the call uses Gonzalo's default `por_verificar`
    (not zona_1 or zona_2). That assumption is written on the result. Every rule stays por_verificar.
    """
    from .vendor import legal as L
    zona = "por_verificar"
    anios, ciclo_dias = [], {}
    for p in plan_years:
        year = []
        for c in p["cycles"]:
            name = _canon(L, c.get("crop") or c.get("label") or "")
            year.append(name)
            if c.get("days"):
                ciclo_dias[name] = c["days"]
        anios.append(year)
    rot = {"anios": anios, "ciclos": [c for a in anios for c in a], "ciclo_dias": ciclo_dias,
           "cobertera_invierno": any(p.get("covered") for p in plan_years)}
    sem = L.check(rot, {"regadio": True}, zona, contrato=True)
    sem["_status"] = "simulado"
    sem["provisional"] = True
    sem["motor_legal"] = f"legal.check (reglas {L.VERSION_REGLAS}, todas por_verificar)"
    sem["supuestos"] = ["Zona del Mar Menor sin confirmar: se evalúa como por_verificar "
                        "(defecto de Gonzalo), no como Zona 1 ni Zona 2."]
    return sem
