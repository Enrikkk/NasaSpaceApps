"""Risk indicator PER GROWTH STAGE from documented thermal alerts (T-021 evidence, decision Enrique 2026-11-14).

No crop has a validated t0/t100 pair, so the engine does NOT turn temperature into lost kilos. Instead each documented
observation is an ALERT: a temperature, how many consecutive days, which organ, in which stage. For every stage of a cycle we
count in how many of the historical cycles (SIAM TP91 daily series) the alert would have fired, and say it plainly:
"en 3 de 19 años hubo una noche de -2,8 °C con el limón en flor". A stage with no documented alert says "sin evidencia"
(never "riesgo bajo"). The alerts do not change the success % or the margin.

Levels (design values, labelled as such): frequency < 10 % bajo, 10-30 % medio, > 30 % alto.
Every alert carries source, confidence and a transfer note (where the study was done, what it did NOT measure).
Stage windows are phenology -> FAO stage mappings: ASSUMPTIONS, traceable in `ventana_nota`; calendar windows for lemon
(perennial) are assumptions too and must be checked with a local agronomist before the pitch.
"""
import datetime as dt

from . import stats, submodels as sm

# Citation records for the alerts (from app/data/tables/threshold-evidence.md, T-021). Facts are summarised, never copied.
SOURCES = {
    "UC-ANR-8100": ("UC ANR Publication 8100, tabla 2 (temperaturas críticas de cítricos)",
                    "https://class.ucanr.edu/sites/default/files/2025-03/UC%20ANR%20Publication%208100.pdf", "UC 2003, todos los derechos reservados: solo hechos atribuidos"),
    "NSW-PRIMEFACT-1729": ("NSW DPI Primefact 1729, Eureka SL lemon", "https://www.dpi.nsw.gov.au/__data/assets/pdf_file/0015/1206150/Eureka-SL-lemon.pdf", "derechos NSW no abiertos verificados: solo hechos atribuidos"),
    "UMASS-EXT-BROCOLI-CALOR": ("UMass Extension, broccoli summer heat", "https://www.umass.edu/agriculture-food-environment/ht/vegetable/fact-sheets/broccoli-summer-heat", "sin licencia abierta identificada: solo síntesis"),
    "ALHARBI-2021": ("Alharbi et al. 2021, Plants 10:1925 (haba, helada)", "https://www.mdpi.com/2223-7747/10/9/1925", "acceso abierto; licencia exacta por verificar"),
    "BISHOP-2016": ("Bishop et al. 2016, J Agron Crop Sci (haba, calor), DOI 10.1111/jac.12172", "https://onlinelibrary.wiley.com/doi/full/10.1111/jac.12172", "acceso abierto declarado; licencia por verificar"),
    "GIMENEZ-BERENGUER-2023": ("Giménez-Berenguer et al. 2023, Antioxidants 12:1960 (alcachofa, helada en Orihuela)", "https://doi.org/10.3390/antiox12111960", "CC BY 4.0"),
    "LEE-2023": ("Lee et al. 2023, BMC Plant Biology 23:106 (lechuga, calor)", "https://doi.org/10.1186/s12870-023-04101-5", "CC BY 4.0"),
    "FAO-FROST-PROTECTION-T4.5": ("FAO, Frost Protection vol. 1, cap. 4, tabla 4.5", "https://www.fao.org/4/y7223e/y7223e0a.htm", "derechos FAO por comprobar"),
}

LEVELS = ((0.10, "bajo"), (0.30, "medio"), (1.01, "alto"))

# window: ("etapas", [names], start_offset_days_in_first_stage, length_days or None)  or  ("calendario", "MM-DD", "MM-DD")
ALERTS = [
    {"id": "limon_flor_helada", "crop": "limon", "peligro": "frío", "var": "tmin", "op": "<=", "umbral": -2.8, "dias": 1,
     "organo": "botones y flores", "efecto": "daño en botones y flores (temperatura crítica del aire)",
     "ventana": ("calendario", "02-15", "04-15"), "ventana_nota": "supuesto: floración de primavera del limón (no verificado en Murcia)",
     "fuente": "UC-ANR-8100", "conf": "B", "transfer": "California; temperatura crítica por órgano, sin % de pérdida ni duración tabulada"},
    {"id": "limon_cuajado_aviso", "crop": "limon", "peligro": "frío", "var": "tmin", "op": "<=", "umbral": -0.8, "dias": 1,
     "organo": "fruto joven (< 13 mm)", "efecto": "aviso: el fruto joven empieza a dañarse (rango crítico -1,4 a -0,8 °C)",
     "ventana": ("calendario", "04-01", "05-31"), "ventana_nota": "supuesto: cuajado en abril-mayo",
     "fuente": "UC-ANR-8100", "conf": "B", "transfer": "California; rango, no un valor único; sin % de pérdida"},
    {"id": "limon_verde_aviso", "crop": "limon", "peligro": "frío", "var": "tmin", "op": "<=", "umbral": -1.4, "dias": 1,
     "organo": "fruto verde (> 13 mm)", "efecto": "aviso: daño al fruto verde (rango crítico -2,8 a -1,4 °C)",
     "ventana": ("calendario", "06-01", "10-15"), "ventana_nota": "supuesto: fruto verde de junio a mediados de octubre",
     "fuente": "UC-ANR-8100", "conf": "B", "transfer": "California; rango, sin % de pérdida"},
    {"id": "limon_maduro_aviso", "crop": "limon", "peligro": "frío", "var": "tmin", "op": "<=", "umbral": -0.8, "dias": 1,
     "organo": "fruto maduro en el árbol", "efecto": "aviso: el fruto maduro puede dañarse (rango crítico -3,3 a -0,8 °C)",
     "ventana": ("calendario", "10-15", "02-15"), "ventana_nota": "supuesto: fruto maduro en el árbol de octubre a febrero",
     "fuente": "UC-ANR-8100", "conf": "B", "transfer": "California; rango muy ancho; sin % de pérdida"},
    {"id": "limon_joven_dano", "crop": "limon", "peligro": "frío", "var": "tmin", "op": "<=", "umbral": -1.4, "dias": 1,
     "organo": "fruto joven (< 13 mm)", "efecto": "daño probable al fruto joven (extremo frío del rango crítico -1,4 a -0,8 °C)",
     "ventana": ("calendario", "04-01", "05-31"), "ventana_nota": "supuesto: cuajado en abril-mayo",
     "fuente": "UC-ANR-8100", "conf": "B", "transfer": "California; rango, sin % de pérdida"},
    {"id": "limon_verde_dano", "crop": "limon", "peligro": "frío", "var": "tmin", "op": "<=", "umbral": -2.8, "dias": 1,
     "organo": "fruto verde (> 13 mm)", "efecto": "daño probable al fruto verde (extremo frío del rango -2,8 a -1,4 °C)",
     "ventana": ("calendario", "06-01", "10-15"), "ventana_nota": "supuesto: fruto verde de junio a mediados de octubre",
     "fuente": "UC-ANR-8100", "conf": "B", "transfer": "California; rango, sin % de pérdida"},
    {"id": "limon_maduro_dano", "crop": "limon", "peligro": "frío", "var": "tmin", "op": "<=", "umbral": -3.3, "dias": 1,
     "organo": "fruto maduro en el árbol", "efecto": "daño probable al fruto maduro (extremo frío del rango -3,3 a -0,8 °C)",
     "ventana": ("calendario", "10-15", "02-15"), "ventana_nota": "supuesto: fruto maduro en el árbol de octubre a febrero",
     "fuente": "UC-ANR-8100", "conf": "B", "transfer": "California; rango muy ancho; sin % de pérdida"},
    {"id": "limon_calor_episodio", "crop": "limon", "peligro": "calor", "var": "tmax", "op": ">", "umbral": 40.0, "dias": 12,
     "organo": "fruto expuesto y fruto dentro del dosel", "efecto": "quemaduras en el fruto expuesto y desecación interna del fruto dentro del dosel",
     "ventana": ("calendario", "06-01", "09-30"), "ventana_nota": "supuesto: verano",
     "fuente": "NSW-PRIMEFACT-1729", "conf": "C", "transfer": "Australia, cultivar Eureka (no Fino ni Verna); un solo episodio observado"},
    {"id": "brocoli_calor_iniciacion", "crop": "brocoli", "peligro": "calor", "var": "tmax", "op": ">", "umbral": 35.0, "dias": 5,
     "organo": "meristemo en iniciación floral", "efecto": "cabezas deformes",
     "ventana": ("etapas", ["mid"], 0, 20), "ventana_nota": "supuesto: iniciación floral ≈ 20 primeros días de la etapa media FAO",
     "fuente": "UMASS-EXT-BROCOLI-CALOR", "conf": "M", "transfer": "UMass resume un ensayo Cornell con la variedad Galaxy (> 35 °C más de 4 días); el original (Björkman y Pearson 1998) usa 35 °C diurnos durante una semana. Tmax consecutivos de estación son un proxy, no la misma dosis; sin % de cabezas dañadas"},
    {"id": "haba_flor_helada", "crop": "haba", "peligro": "frío", "var": "tmin", "op": "<=", "umbral": -4.19, "dias": 1,
     "organo": "grupo floral", "efecto": "aborto de las flores expuestas (la planta sobrevivió)",
     "ventana": ("etapas", ["dev", "mid"], 0, None), "ventana_nota": "supuesto: floración entre el final de desarrollo y la etapa media",
     "fuente": "ALHARBI-2021", "conf": "B", "transfer": "Arabia (Dirab); no se midió rendimiento; no es pérdida de cosecha"},
    {"id": "haba_flor_calor", "crop": "haba", "peligro": "calor", "var": "tmax", "op": ">=", "umbral": 28.0, "dias": 5,
     "organo": "flores ya formadas", "efecto": "aviso: el modelo ajustado a los tratamientos (18/22/26/30/34 °C de día, noches 8 °C más frías) sitúa en ≈ 28 °C el t50 del rendimiento de las flores ya formadas; la planta compensa en otros nudos",
     "ventana": ("etapas", ["dev", "mid"], 0, None), "ventana_nota": "supuesto: floración entre desarrollo y etapa media",
     "fuente": "BISHOP-2016", "conf": "B", "transfer": "cámara, 5 días; el 28 °C sale de un ajuste, no de un tratamiento aplicado; 5 días con Tmax ≥ 28 en estación no equivalen a perder el 50 % de la cosecha"},
    {"id": "alcachofa_capitulo_helada", "crop": "alcachofa", "peligro": "frío", "var": "tmin", "op": "<=", "umbral": -1.3, "dias": 1,
     "organo": "capítulos (brácteas)", "efecto": "lesiones en brácteas (escala 0-5); no es pérdida de rendimiento",
     "ventana": ("etapas", ["mid", "late"], 0, None), "ventana_nota": "supuesto: capítulos presentes durante la cosecha (etapas media y final)",
     "fuente": "GIMENEZ-BERENGUER-2023", "conf": "A", "transfer": "Orihuela, Blanca de Tudela, invierno 2022-23: misma zona; un solo episodio observado"},
    {"id": "lechuga_calor_espigado", "crop": "lechuga", "peligro": "calor", "var": "tmax", "op": ">=", "umbral": 35.0, "dias": 3,
     "organo": "meristemo", "efecto": "aviso: el meristemo cambia (compatible con inicio de espigado); sin % de pérdida",
     "ventana": ("etapas", ["dev", "mid", "late"], 0, None), "ventana_nota": "supuesto: fases tras el establecimiento",
     "fuente": "LEE-2023", "conf": "C", "transfer": "cámara 35/25 °C 72 h, variedad Detenicka atrakce; no validado en iceberg de Murcia"},
    {"id": "melon_helada_germinacion", "crop": "melon", "peligro": "frío", "var": "tmin", "op": "<=", "umbral": -0.5, "dias": 1,
     "organo": "germinación y plántula", "efecto": "aviso: temperatura crítica de germinación (FAO, sin duración)",
     "ventana": ("etapas", ["ini"], 0, None), "ventana_nota": "germinación = etapa inicial",
     "fuente": "FAO-FROST-PROTECTION-T4.5", "conf": "B", "transfer": "tabla de rangos críticos de síntesis FAO, sin duración ni %"},
    {"id": "melon_helada_floracion", "crop": "melon", "peligro": "frío", "var": "tmin", "op": "<=", "umbral": -1.0, "dias": 1,
     "organo": "floración y fructificación", "efecto": "aviso: temperatura crítica en floración y fructificación (FAO, sin duración)",
     "ventana": ("etapas", ["dev", "mid"], 0, None), "ventana_nota": "floración = desarrollo; fructificación = etapa media",
     "fuente": "FAO-FROST-PROTECTION-T4.5", "conf": "B", "transfer": "tabla de rangos críticos de síntesis FAO, sin duración ni %"},
    {"id": "cebada_helada_floracion", "crop": "cebada", "peligro": "frío", "var": "tmin", "op": "<=", "umbral": -1.0, "dias": 1,
     "organo": "floración", "efecto": "aviso: temperatura crítica en floración (FAO, sin duración)",
     "ventana": ("etapas", ["mid"], 0, 20), "ventana_nota": "supuesto: floración ≈ 20 primeros días de la etapa media",
     "fuente": "FAO-FROST-PROTECTION-T4.5", "conf": "B", "transfer": "tabla de rangos críticos de síntesis FAO, sin duración ni %"},
    {"id": "cebada_helada_llenado", "crop": "cebada", "peligro": "frío", "var": "tmin", "op": "<=", "umbral": -2.0, "dias": 1,
     "organo": "llenado de grano", "efecto": "aviso: temperatura crítica en fructificación (FAO, sin duración)",
     "ventana": ("etapas", ["mid", "late"], 20, None), "ventana_nota": "supuesto: llenado = resto de la etapa media y etapa final",
     "fuente": "FAO-FROST-PROTECTION-T4.5", "conf": "B", "transfer": "tabla de rangos críticos de síntesis FAO, sin duración ni %"},
]


def level(freq):
    return next(name for top, name in LEVELS if freq < top)


def _mmdd(s):
    return int(s[:2]), int(s[3:])


def _window_indices(alert, start, lengths):
    """Day offsets (0-based) of the cycle that the alert's window covers."""
    n = sum(lengths)
    w = alert["ventana"]
    if w[0] == "calendario":
        a, b = _mmdd(w[1]), _mmdd(w[2])
        out = []
        for i in range(n):
            d = start + dt.timedelta(days=i)
            md = (d.month, d.day)
            if (a <= md <= b) if a <= b else (md >= a or md <= b):
                out.append(i)
        return out
    _, names, offset, length = w
    order = ("ini", "dev", "mid", "late")
    cum = [0]
    for ln in lengths:
        cum.append(cum[-1] + ln)
    idx = [i for nm in names for i in range(cum[order.index(nm)], cum[order.index(nm) + 1])]
    idx = idx[offset:]
    return idx if length is None else idx[:length]


def _fires(alert, days, idx):
    """True if the window contains a run of >= alert['dias'] consecutive days meeting the condition."""
    run = 0
    for i in idx:
        v = getattr(days[i], alert["var"])
        ok = v <= alert["umbral"] if alert["op"] == "<=" else v >= alert["umbral"] if alert["op"] == ">=" else v > alert["umbral"]
        run = run + 1 if ok else 0
        if run >= alert["dias"]:
            return True
    return False


def assess(crop_id, lengths, month, day, climate, alerts=None):
    """Stage risk of one cycle type (sowing month/day) over every historical start year with a full record.
    Returns {"etapas": [...], "n_ciclos": n} ; each stage entry is a documented alert or 'sin evidencia'."""
    alerts = [a for a in (alerts or ALERTS) if a["crop"] == crop_id]
    n_days = sum(lengths)
    first, last = min(climate), max(climate)
    cycles = []
    for y0 in range(first.year, last.year + 1):
        start = dt.date(y0, month, day)
        days = sm.cycle_days(climate, start, n_days)
        if days is not None:
            cycles.append((start, days))
    ref = dt.date(2001, month, day)
    names = ("ini", "dev", "mid", "late")
    cum = [0]
    for ln in lengths:
        cum.append(cum[-1] + ln)
    out = []
    for a in alerts:
        k = sum(_fires(a, days, _window_indices(a, start, lengths)) for start, days in cycles)
        n = len(cycles)
        idx = _window_indices(a, ref, lengths)
        freq = k / n if n else None
        lo, hi = stats.wilson(k, n) if n else (0, 1)
        stg = sorted({names[next(j for j in range(4) if cum[j] <= i < cum[j + 1])] for i in idx})
        out.append({"id": a["id"], "peligro": a["peligro"], "organo": a["organo"], "efecto": a["efecto"],
                    "gravedad": "aviso" if a["efecto"].startswith("aviso") else "daño",
                    "lectura": "exposición: temperatura diaria de la estación como proxy; no es daño observado ese año ni pérdida de cosecha",
                    "condicion": f"{'mínima' if a['var'] == 'tmin' else 'máxima'} {a['op'].replace('<=', '≤').replace('>=', '≥')} "
                                 f"{str(a['umbral']).replace('.', ',')} °C"
                                 + (f" durante {a['dias']} días seguidos" if a["dias"] > 1 else ""),
                    "etapas_fao": stg,
                    "desde": (ref + dt.timedelta(days=idx[0])).strftime("%m-%d") if idx else None,
                    "hasta": (ref + dt.timedelta(days=idx[-1])).strftime("%m-%d") if idx else None,
                    "anios_con_episodio": k, "n": n, "frecuencia": None if freq is None else round(freq, 3),
                    "intervalo_95": [round(lo, 3), round(hi, 3)], "nivel": level(freq) if freq is not None else "sin datos",
                    "fuente": a["fuente"], "conf": a["conf"], "ventana_nota": a["ventana_nota"], "transferencia": a["transfer"]})
    covered = {(st, e["peligro"]) for e in out for st in e["etapas_fao"]}
    for j, nm in enumerate(names):
        for hz in ("frío", "calor"):
            if (nm, hz) in covered:
                continue
            out.append({"id": f"{crop_id}_{nm}_{'frio' if hz == 'frío' else 'calor'}_sin_evidencia", "peligro": hz, "organo": None,
                        "efecto": f"sin evidencia documentada de daño por {hz} en esta etapa", "condicion": None,
                        "etapas_fao": [nm], "desde": (ref + dt.timedelta(days=cum[j])).strftime("%m-%d"),
                        "hasta": (ref + dt.timedelta(days=cum[j + 1] - 1)).strftime("%m-%d"), "anios_con_episodio": None,
                        "n": len(cycles), "frecuencia": None, "intervalo_95": None, "nivel": "sin evidencia", "fuente": None,
                        "conf": None, "ventana_nota": None, "transferencia": None, "lectura": None})
    return {"etapas": out, "n_ciclos": len(cycles), "niveles": "frecuencia < 10 % bajo, 10-30 % medio, > 30 % alto (valores de diseño)"}
