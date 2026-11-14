"""Submodels A-D of the engine (coordination/PLAN.md, research/predictive-model-research.md).

A aptitude      hard "cannot evaluate / not apt" reasons (missing core params, salt kills > half the yield)
B climate risk  graded daily frost/heat damage over the crop's sensitive window, season loss = 1 - prod(1 - d_t)
C water + salt  FAO-56 single-Kc curve x station ET0, effective rain, gross irrigation; FAO-29 salt yield factor
D yield         reference yield (IMIDA survey, else Eurostat national) x (1 - climate loss) x salt factor

Every number without a source is in ASSUMPTIONS with status "supuesto" and is reported in the output.
"""
import datetime as dt

# Design values with no primary source yet. Each is reported to the UI as "supuesto" (never shown as data).
ASSUMPTIONS = {
    "loss_threshold": (0.20, "L* = 20 %: año malo si la pérdida climática >= 20 % (diseño, alineado con franquicias "
                             "de seguro agrario 10-30 %, research/predictive-model-research.md)"),
    "eff_rain_frac": (0.80, "lluvia efectiva = 80 % de la lluvia diaria (opción 'fixed percentage' de CROPWAT; "
                            "0,7-0,8 en las notas, sin fuente primaria verificada)"),
    "irrigation_efficiency": (0.90, "eficiencia de riego por goteo 0,90 (plan de cuenca del Segura, fuente antigua B)"),
    "ece_from_ecw": (1.5, "ECe = 1,5 x ECw con fracción de lavado ordinaria 15-20 % (regla práctica FAO-29, "
                          "sin verificar en el texto)"),
    "window_default": ("all", "si el cultivo no tiene ventana sensible documentada, se evalúa todo el ciclo "
                              "(lo más prudente)"),
}
STAGES = ("ini", "dev", "mid", "late")


def stages(crop, key="stages_days"):
    """Stage lengths (ini, dev, mid, late) in days from a '30/40/25/10' param, or None."""
    v = crop.get(key)
    if not isinstance(v, str) or v.count("/") != 3:
        return None
    return tuple(int(float(x)) for x in v.split("/"))


def kc_curve(lengths, kc_ini, kc_mid, kc_end):
    """FAO-56 single crop coefficient per day: flat ini, linear dev, flat mid, linear late (FAO-56 ch. 6, Fig. 25)."""
    li, ld, lm, ll = lengths
    out = [kc_ini] * li
    out += [kc_ini + (kc_mid - kc_ini) * (i + 1) / ld for i in range(ld)]
    out += [kc_mid] * lm
    out += [kc_mid + (kc_end - kc_mid) * (i + 1) / ll for i in range(ll)]
    return out


def stage_of_day(lengths):
    names = []
    for name, n in zip(STAGES, lengths):
        names += [name] * n
    return names


def cycle_days(climate, start, n):
    """The n consecutive climate days from `start`, or None if the record doesn't cover them all."""
    out = []
    for i in range(n):
        d = start + dt.timedelta(days=i)
        if d not in climate:
            return None
        out.append(climate[d])
    return out


def thresholds(crop, hazard):
    """(t0, t100) for 'frost' or 'heat': damage starts at t0 and is total at t100. None if not documented."""
    t0 = crop.get(f"{hazard}_t0", crop.get(f"{hazard}_threshold"))
    t100 = crop.get(f"{hazard}_t100", crop.get(f"{hazard}_lethal"))
    if not isinstance(t0, float) or not isinstance(t100, float) or t0 == t100:
        return None
    return t0, t100


def daily_damage(t, t0, t100):
    """Graded damage of one day in [0, 1]: 0 before t0, 1 beyond t100, linear in between (works for cold and heat)."""
    return min(1.0, max(0.0, (t - t0) / (t100 - t0)))


def climate_loss(crop, days, lengths):
    """Submodel B for one cycle. Returns {"frost": loss|None, "heat": loss|None, "total": loss, "peor_dia": ...}."""
    names = stage_of_day(lengths)
    out, total_keep, worst = {}, 1.0, None
    for hazard, temp in (("frost", lambda d: d.tmin), ("heat", lambda d: d.tmax)):
        th = thresholds(crop, hazard)
        if th is None:
            out[hazard] = None
            continue
        window = crop.get(f"{hazard}_window", ASSUMPTIONS["window_default"][0])
        keep = 1.0
        for i, d in enumerate(days):
            if window != "all" and names[i] not in str(window).split("+"):
                continue
            dmg = daily_damage(temp(d), *th)
            if dmg > 0:
                keep *= 1 - dmg
                if worst is None or dmg > worst[1]:
                    worst = (hazard, dmg, i, temp(d))
        out[hazard] = 1 - keep
        total_keep *= keep
    out["total"] = 1 - total_keep
    out["peor_dia"] = worst
    return out


def water(crop, days, lengths):
    """Submodel C (water): ETc, net and gross irrigation in mm and m3/ha for one cycle. None if Kc is missing."""
    if not crop.has("kc_ini", "kc_mid", "kc_end"):
        return None
    kc = kc_curve(lengths, crop.get("kc_ini"), crop.get("kc_mid"), crop.get("kc_end"))
    etc = sum(k * d.et0 for k, d in zip(kc, days))
    rain = sum(d.rain for d in days)
    eff = ASSUMPTIONS["eff_rain_frac"][0]
    # Effective rain can only cover that day's demand: rain on a day of low ETc runs off / drains.
    net = sum(max(0.0, k * d.et0 - eff * d.rain) for k, d in zip(kc, days))
    gross = net / ASSUMPTIONS["irrigation_efficiency"][0]
    return {"etc_mm": etc, "lluvia_mm": rain, "neto_mm": net, "bruto_mm": gross, "bruto_m3_ha": gross * 10,
            "et0_mm": sum(d.et0 for d in days)}


def salt_factor(crop, ecw):
    """Submodel C (salt): relative yield 0-1 from FAO-29 Yr = 100 - b (ECe - a). None if ECw or a/b are unknown."""
    if ecw is None or not crop.has("ece_threshold", "ece_slope"):
        return None
    ece = ASSUMPTIONS["ece_from_ecw"][0] * ecw
    yr = 100 - crop.get("ece_slope") * max(0.0, ece - crop.get("ece_threshold"))
    return max(0.0, min(1.0, yr / 100))


def reference_yield(crop, area=None):
    """Submodel D: (kg/ha per cycle, evidence dict). IMIDA survey yield first; else median Eurostat national yield
    of the last 10 years (national, mostly rainfed for grain: conf M, labelled as such). None if neither exists."""
    if crop.has("produccion_media"):
        return crop.get("produccion_media"), crop.ref("produccion_media")
    ys = sorted(v["yield_t_ha"] for y, v in (area or {}).items() if y >= 2015 and isinstance(v.get("yield_t_ha"), float))
    if ys:
        med = ys[len(ys) // 2] if len(ys) % 2 else (ys[len(ys) // 2 - 1] + ys[len(ys) // 2]) / 2
        return med * 1000, {"param": "produccion_media", "valor": med * 1000, "unidad": "kg/ha", "fuente": "EUR-AREA",
                            "conf": "M", "nota": f"mediana nacional {len(ys)} años desde 2015, no de parcela"}
    return None, None


def aptitude(crop, salt):
    """Submodel A: list of reasons why the crop cannot be evaluated or is not apt. Empty list = apt."""
    why = []
    if stages(crop) is None:
        why.append("sin duración de fases (FAO-56 Tabla 11): no se puede situar el ciclo")
    if not crop.has("kc_ini", "kc_mid", "kc_end"):
        why.append("sin Kc (FAO-56 Tabla 12): no se puede calcular el agua")
    if salt is not None and salt < 0.5:
        why.append(f"la sal del agua de riego quita {100 - salt * 100:.0f} % de la cosecha (FAO-29)")
    return why
