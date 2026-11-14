"""Per-parcel layer of the engine (H-002): what changes when the user clicks a parcel that is not the demo one.

It never touches euros, kilos or probabilities. It only:
  * drops from the catalog the crops the parcel cannot grow (suitability exclusions, Arturo's table),
  * gives every other crop a score factor 0-1 used by the rotation DP (a penalised crop is recommended less),
  * decides which rotation is the reference ("actual"): the FEGA declaration when it maps to the catalog, else the
    typical rotation of the area, labelled as an assumption,
  * builds the environmental label and the plain sentences the card shows.

Missing data is never invented: factor 1 and a "no tenemos dato de ..." sentence.
The climate is still ONE station (SIAM TP91, Torre-Pacheco) for every parcel: `clima_origen` says so and how far the
parcel is from the reference parcel.
"""
import itertools
import math
import unicodedata

from .decision import rotations as rt
from .suitability import suitability as su

REF_PARCEL = {"lat": 37.7383, "lon": -0.98838, "nombre": "Torre-Pacheco, SIGPAC 18/426/1"}
LEJOS_KM = 30.0   # SUPUESTO sin fuente: a partir de aquí avisamos de que la estación puede no representar la parcela

# FEGA declared product name (normalised, substring) -> engine product id
DECLARED_TO_PRODUCT = (("lechuga", "lechuga_iceberg"), ("brocoli", "brocoli"), ("brecol", "brocoli"),
                       ("melon", "melon_piel_de_sapo"), ("alcachofa", "alcachofa"))
FIELD_LABEL = {"regadio": "si la parcela es de regadío o de secano", "pendiente_pct": "la pendiente",
               "textura": "la textura del suelo", "salinidad_ce_dsm": "la salinidad del suelo", "ph": "el pH del suelo",
               "drenaje": "el drenaje del suelo", "profundidad_cm": "la profundidad del suelo"}
VAR_LABEL = {"pendiente_pct": "la pendiente de la parcela", "ph": "el pH del suelo", "drenaje": "el drenaje del suelo",
             "textura": "la textura del suelo", "salinidad_ce_dsm": "la salinidad del suelo",
             "profundidad_cm": "la profundidad del suelo", "regadio": "ser de secano"}
VAR_UNIT = {"pendiente_pct": " %", "salinidad_ce_dsm": " dS/m", "profundidad_cm": " cm"}


def _norm(s):
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().strip()


def _es(v):
    """Number as written in Spanish text: 12.5 -> '12,5', 12.0 -> '12'."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return str(v)
    return f"{v:.1f}".rstrip("0").rstrip(".").replace(".", ",")


def _join(items):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " y " + items[-1]


def evaluar(parcel_input, static):
    """Suitability of every catalog product for this parcel. static = rotations.run_cycles output (before filtering)."""
    catalog, labels = {}, {}
    for k, v in static.items():
        catalog[k[0]] = v["crop"]
        labels[k[0]] = v["label"]
    raw = su.evaluar(parcel_input, catalog)
    excl = [e["cultivo"] for e in raw["excluidos"]]
    return {"raw": raw, "excluidos_ids": set(excl), "labels": labels,
            "factores": {pid: e["factor"] for pid, e in raw["factores"].items() if pid not in excl}}


def option_factor(opt, factores):
    """Score factor of a year option = mean factor of its cycles (SUPUESTO de diseño: media, no producto)."""
    if not opt.keys:
        return 1.0
    return sum(factores.get(k[0], 1.0) for k in opt.keys) / len(opt.keys)


def declared_names(parcel_input):
    names = []
    for d in (parcel_input or {}).get("cultivos_declarados") or []:
        if isinstance(d, str):
            names.append(d)
        elif isinstance(d, dict):
            names += [d[k] for k in ("cultivo", "producto", "cultivo_secundario") if d.get(k)]
    out = []
    for n in names:
        if isinstance(n, str) and n.strip() and n.strip() not in out:
            out.append(n.strip())
    return out


def actual(parcel_input, static, default_keys):
    """(keys | None, origen, info). origen: 'declaracion_fega' | 'supuesto_zona' | 'sin_referencia'.

    The declared crops become the reference rotation only if at least one maps to a catalog product the parcel can
    grow. Otherwise the typical rotation of the area (default_keys) is used and labelled as an assumption.
    """
    names = declared_names(parcel_input)
    by_product = {}
    for k in static:
        by_product.setdefault(k[0], []).append(k)
    pids, mapped, unmapped = [], [], []
    for n in names:
        nn = _norm(n)
        hit = next((pid for needle, pid in DECLARED_TO_PRODUCT if needle in nn), None)
        if hit and hit in by_product:
            mapped.append(n)
            if hit not in pids:
                pids.append(hit)
        else:
            unmapped.append(n)
    info = {"declarados": names, "declarados_en_catalogo": mapped, "declarados_fuera_de_catalogo": unmapped}
    if pids:
        for n in range(len(pids), 0, -1):      # all the declared crops if they fit in one year, else the first ones
            for keys in itertools.product(*[sorted(by_product[p]) for p in pids[:n]]):
                if rt.fits([static[k] for k in keys]):
                    return tuple(sorted(keys, key=lambda k: static[k]["start_doy"])), "declaracion_fega", info
    if default_keys and all(k in static for k in default_keys):
        return tuple(default_keys), "supuesto_zona", info
    return None, "sin_referencia", info


def ambiente(agua_m3_ha, suelo_desnudo_dias, credito_n_kg_ha, legal):
    """Environmental label alto/medio/bajo (Arturo's heuristic; every cutoff is a labelled assumption)."""
    color = (legal or {}).get("color")
    res = {"verde": "ok", "rojo": "falla"}.get(color, "no_evaluable" if color else None)
    lab = su.etiqueta_ambiental({"agua_m3_ha": agua_m3_ha, "suelo_desnudo_dias": suelo_desnudo_dias,
                                 "credito_n_kg_ha": credito_n_kg_ha, "semaforo_legal": res})
    lab["metricas"] = {"agua_m3_ha": agua_m3_ha, "suelo_desnudo_dias": round(suelo_desnudo_dias),
                       "credito_n_kg_ha": round(credito_n_kg_ha), "color_legal": color}
    frase = {"alto": "Trato al medio ambiente: alto. Gasta poca agua, deja el suelo cubierto y aporta nitrógeno natural.",
             "medio": "Trato al medio ambiente: medio. No destaca ni para bien ni para mal con lo que sabemos.",
             "bajo": "Trato al medio ambiente: bajo. Gasta mucha agua, deja el suelo desnudo mucho tiempo o no pasa el "
                     "semáforo legal."}[lab["nivel"]]
    lab["frase"] = frase + " Es una etiqueta orientativa nuestra, no una certificación."
    return lab


def _frase_factor(label, a):
    pct = round((1 - float(a["factor"])) * 100)
    var = a["variable"]
    val = a.get("valor_entrada")
    val_txt = f" ({_es(val)}{VAR_UNIT.get(var, '')})" if val is not None and not isinstance(val, bool) else ""
    return (f"{label}: su puntuación baja un {pct} % por {VAR_LABEL.get(var, var)}{val_txt}. "
            "Ese porcentaje es un supuesto nuestro, no una medida. El dinero estimado no cambia.")


def idoneidad_rotacion(path, suit):
    """Per-rotation block: which factors touched the crops of THIS rotation."""
    raw, labels = suit["raw"], suit["labels"]
    pids = []
    for o in path:
        for k in o.keys:
            if k[0] not in pids:
                pids.append(k[0])
    aplicados, frases = [], []
    for pid in pids:
        for a in raw["factores"][pid]["factores_aplicados"]:
            if a["factor"] == "excluir":
                continue
            aplicados.append({"cultivo": labels[pid], "producto": pid, "variable": a["variable"],
                              "valor_entrada": a.get("valor_entrada"), "factor": float(a["factor"]),
                              "estado": a["estado"], "conf": a["conf"], "fuente_id": a["source_id"], "url": a["url"]})
            frases.append(_frase_factor(labels[pid], a))
    fac = [option_factor(o, suit["factores"]) for o in path]
    return {"factor_puntuacion": round(sum(fac) / len(fac), 3) if fac else 1.0, "factores_aplicados": aplicados,
            "frases": frases or ["Con los datos de la parcela que tenemos, ningún cultivo de esta rotación pierde puntuación."],
            "_status": "supuesto"}


def resumen(parcel_input, suit, origen, info):
    """Top-level block: exclusions, missing data and the sentences that explain how the parcel changed the result."""
    raw, labels = suit["raw"], suit["labels"]
    frases = []
    excl = [{"cultivo": labels[e["cultivo"]], "producto": e["cultivo"], "motivo": e["motivo"], "estado": e["estado"],
             "fuente_id": e["source_id"]} for e in raw["excluidos"]]
    if excl:
        frases.append(f"Fuera de las opciones: {_join(e['cultivo'] for e in excl)}. La parcela consta como secano y solo "
                      "tenemos datos de estos cultivos en regadío.")
    penal = {}
    for pid, f in suit["factores"].items():
        if f < 1:
            for a in raw["factores"][pid]["factores_aplicados"]:
                frases.append(_frase_factor(labels[pid], a))
            penal[pid] = round(f, 3)
    campos = []
    for g in raw["sin_dato"]:
        if g["motivo"].startswith("sin dato valido") and g["campo"] not in campos:
            campos.append(g["campo"])
    for c in campos:
        frases.append(f"No tenemos dato de {FIELD_LABEL.get(c, c)}: no se ha tenido en cuenta.".replace(" de el ", " del "))
    pend = sum(1 for g in raw["sin_dato"] if not g["motivo"].startswith("sin dato valido"))
    if pend:
        frases.append(f"Hay {pend} combinaciones de cultivo y condición de la parcela sin regla revisada todavía: no "
                      "cambian la puntuación.")
    if origen == "declaracion_fega":
        frases.append(f"Tu rotación de hoy sale de lo que declaraste a FEGA: {_join(info['declarados_en_catalogo'])}.")
    elif info["declarados"]:
        frases.append(f"Lo que declaraste a FEGA ({_join(info['declarados'])}) no está en nuestro catálogo de cultivos. "
                      "Comparamos con la rotación típica de la zona, que es un supuesto.")
    else:
        frases.append("No sabemos qué cultivas hoy en esta parcela. Comparamos con la rotación típica de la zona, que es "
                      "un supuesto.")
    return {"_status": "supuesto", "excluidos": excl, "factores_puntuacion": penal, "sin_dato": campos,
            "reglas_pendientes": pend, "referencia_origen": origen, **info, "frases": frases,
            "nota": "La idoneidad cambia qué rotaciones se recomiendan, nunca el dinero ni los kilos estimados. "
                    "Los porcentajes son supuestos del proyecto (confianza C)."}


def clima_origen(parcel_input, cmeta):
    """Which climate the numbers come from, and how far the parcel is from the reference parcel."""
    out = {"estacion": (cmeta or {}).get("estacion", "SIAM-TP91"), "parcela_referencia": REF_PARCEL["nombre"],
           "distancia_a_parcela_referencia_km": None, "_status": "real",
           "frase": "El clima del cálculo es el de la estación de Torre-Pacheco, la única que tenemos cargada."}
    lat, lon = (parcel_input or {}).get("lat"), (parcel_input or {}).get("lon")
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        p1, p2 = math.radians(lat), math.radians(REF_PARCEL["lat"])
        a = (math.sin((p2 - p1) / 2) ** 2
             + math.cos(p1) * math.cos(p2) * math.sin(math.radians(REF_PARCEL["lon"] - lon) / 2) ** 2)
        km = round(6371.0 * 2 * math.asin(math.sqrt(a)))
        out["distancia_a_parcela_referencia_km"] = km
        out["lejos"] = km > LEJOS_KM
        if km > LEJOS_KM:
            out["frase"] += (f" Tu parcela está a unos {km} km de la parcela de referencia: el clima real de tu parcela "
                             "puede ser distinto y los resultados son menos fiables.")
        elif km >= 1:
            out["frase"] += f" Tu parcela está a unos {km} km de la parcela de referencia."
    return out


def totales_parcela(rot, area_ha):
    """Per-hectare figures of a rotation times the parcel's area (only when the area is known). Plain arithmetic."""
    if isinstance(area_ha, bool) or not isinstance(area_ha, (int, float)) or area_ha <= 0:
        return None
    m = rot.get("margen_eur_ha")
    out = {"area_ha": area_ha, "unidad": "€ de 2025 al año en toda la parcela (media del plan)",
           "margen_eur": ({k: round(m[k] * area_ha) for k in ("p10", "p50", "p90")} if m else None),
           "agua_m3": round(rot["agua_m3_ha"] * area_ha) if rot.get("agua_m3_ha") is not None else None,
           "_status": "real", "nota": "cifra por hectárea multiplicada por la superficie del recinto"}
    return out
