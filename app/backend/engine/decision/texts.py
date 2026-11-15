"""T-022: deterministic Spanish text layer for the rotation cards (no network, no LLM).

Every sentence is built from numbers that already exist in the rotation JSON. `check(out)` re-reads the
generated text, extracts every number and verifies it can be derived from that rotation's own JSON
(same value rounded to the same precision, or a difference / ratio of two values in the JSON, the second
one possibly from the current rotation, which is the reference of every comparison).
`apply(out)` writes `texto` into each rotation and raises AssertionError if `check` finds anything.
"""
import re
from decimal import Decimal, ROUND_HALF_UP

CONSULTA = "Herramienta de apoyo. Consulta a tu técnico agrícola antes de decidir."

STRATEGY_PREDICATE = {
    "S1": "más margen deja en un año típico",
    "S2": "mejor cuida el suelo y menos agua gasta",
    "S3": "menos riesgo de un mal año tiene",
}

# ---------------------------------------------------------------------------------------------- number parsing

_NUM = re.compile(r"(?<![\w.,])(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)")
_DATE = re.compile(r"\b\d{2}-\d{2}\b")
_SENT = re.compile(r"(?<=[.!?])\s+")
_BAD_WORD = re.compile(r"\b(None|nan|NaN|null)\b")
# Cardinals written out hide a quantity from `_NUM` («tres», «diez»). Articles «un»/«una» are not included.
_WORD_NUM = re.compile(
    r"\b(cero|uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|trece|catorce|quince|"
    r"veinte|treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|noventa|cien|ciento|mil)\b",
    re.IGNORECASE,
)


def _numbers_raw(text):
    """[(raw, value, decimals)] for every number written in Spanish style (3.956 / 2,2 / 73). Sign is ignored."""
    out = []
    for m in _NUM.finditer(text):
        raw = m.group(1)
        dec = len(raw.split(",")[1]) if "," in raw else 0
        out.append((raw, float(raw.replace(".", "").replace(",", ".")), dec))
    return out


def numbers_in(text):
    """All numbers (absolute values, as floats) written in `text`."""
    return [v for _, v, _ in _numbers_raw(text)]


# ---------------------------------------------------------------------------------------------- formatting


def _n(v, d=0):
    """Spanish formatting without sign: 3956 -> '3.956', 2.2 (d=1) -> '2,2'."""
    q = Decimal(repr(float(abs(v)))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    s = f"{q:,.{d}f}"
    return s.replace(",", "\0").replace(".", ",").replace("\0", ".")


def _eur(v):
    return ("-" if round(v) < 0 else "") + _n(v) + " €"


def _join(items):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " y " + items[-1]


def _year_list(years):
    """Years as plain digits; items may be bare years or {'anio', 'margen_eur_ha'} (then the margin is quoted)."""
    out = []
    for y in years:
        if isinstance(y, dict):
            m = y.get("margen_eur_ha")
            out.append(f"{int(y['anio'])}" + (f" ({_eur(m)} por hectárea)" if m is not None else ""))
        else:
            out.append(str(int(y)))
    return _join(out)


# ---------------------------------------------------------------------------------------------- pool of allowed numbers

# keys not read when building the pool of allowed numbers: generated text, big simulations, dates, ids
_SKIP = {"escenarios", "variantes", "plan_anios", "texto", "por_que", "nombre", "fuente", "id", "etapas_fao",
         "ventana_nota", "transferencia", "desde", "hasta", "siembra", "siembras", "_status"}
# top-level blocks whose scalars can be compared one-to-one against the current rotation
_COMPARABLE = {"exito_pct", "margen_eur_ha", "agua_m3_ha", "agua_detalle", "criterios", "inversion"}


def _is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x == x


def _walk(node, path, leaves, groups):
    """leaves: [(path, number)]; groups: [[sibling numbers]] (for differences inside one dict or list)."""
    if isinstance(node, dict):
        kids = [(k, v) for k, v in node.items() if k not in _SKIP]
    elif isinstance(node, list):
        kids = list(enumerate(node))
    else:
        return
    sib = []
    for k, v in kids:
        if _is_num(v):
            leaves.append((path + (k,), float(v)))
            sib.append(float(v))
        elif isinstance(v, str):
            for x in numbers_in(_DATE.sub(" ", v)):
                leaves.append((path + (k, "~str"), x))
        else:
            _walk(v, path + (k,), leaves, groups)
    if len(sib) > 1:
        groups.append(sib)


def _collect(r):
    leaves, groups = [], []
    _walk(r, (), leaves, groups)
    return leaves, groups


def _allowed(r, ref):
    """Numbers that may appear in the text of rotation `r` (own values, x100 of fractions, own sibling
    differences, and difference / percentage / ratio against the same field of the reference rotation)."""
    leaves, groups = _collect(r)
    vals = {abs(v) for _, v in leaves}   # the text never carries the sign: compare absolute values
    cands = set(vals) | {v * 100 for v in vals if 0 < abs(v) <= 1}
    for g in groups:
        for i, a in enumerate(g):
            for b in g[i + 1:]:
                cands.add(abs(a - b))
    if ref is not None and ref is not r:
        own = {p: v for p, v in leaves if p and p[0] in _COMPARABLE and "~str" not in p}
        rl, _ = _collect(ref)
        refd = {p: v for p, v in rl if p and p[0] in _COMPARABLE and "~str" not in p}
        cands |= {abs(v) for _, v in rl}  # reference values (quoted next to the alternative's)
        for p, a in own.items():
            if p in refd:
                b = refd[p]
                cands.add(abs(a - b))
                if b:
                    cands.add(abs(a - b) / abs(b) * 100)
                    cands.add(a / b)
                    cands.add(abs(a / b - 1) * 100)
    return cands


def _ok(value, dec, cands):
    tol = 0.5 * 10 ** (-dec) + 1e-9
    return any(abs(c - value) <= tol for c in cands)


def _texts_of(r):
    t = r.get("texto") or {}
    items = [("por_que", t.get("por_que", ""))]
    for key in ("evidencia_resumen", "no_sabemos", "riesgos_texto"):
        items += [(key, s) for s in t.get(key, [])]
    items.append(("consulta", t.get("consulta", "")))
    return items


def _legal_blob(r):
    """Text of the legal light, so a word-number quoted from it is not an invented figure."""
    s = r.get("semaforo_legal") or {}
    parts = [str(s.get("motivo") or ""), str(s.get("nota") or "")]
    for c in s.get("comprobaciones") or []:
        parts.append(str(c.get("nota") or ""))
        parts.append(str(c.get("regla") or ""))
    return " ".join(parts).lower()


def check(out):
    """List of offending (rotation id, number as written, sentence). Empty list = every number is backed by the JSON."""
    rots = out.get("rotaciones", [])
    ref = next((r for r in rots if r.get("es_actual")), None)
    bad = []
    for r in rots:
        cands = _allowed(r, ref)
        for _, block in _texts_of(r):
            for sentence in _SENT.split(block):
                for raw, v, dec in _numbers_raw(sentence):
                    if not _ok(v, dec, cands):
                        bad.append((r["id"], raw, sentence))
                m = _BAD_WORD.search(sentence)
                if m:
                    bad.append((r["id"], m.group(1), sentence))
                w = _WORD_NUM.search(sentence)
                if w and w.group(1).lower() not in _legal_blob(r):
                    bad.append((r["id"], w.group(1), sentence))
    return bad


# ---------------------------------------------------------------------------------------------- helpers over a rotation


def _has_margin(r):
    m = r.get("margen_eur_ha")
    return bool(m) and m.get("p50") is not None


def _has_exito(r):
    return (r.get("exito_pct") or {}).get("valor") is not None


def _crops_without_price(r):
    return [x.split(":")[0] for x in r.get("riesgos", []) if "SIN precio" in x]


def _crops_with(r, marker):
    return [x.split(":")[0] for x in r.get("riesgos", []) if "precio de referencia = " + marker in x]


def _national(r):
    return _crops_with(r, "Eurostat") + _crops_with(r, "MAPA")


def _stage_levels(r):
    """(medium/high findings, products with 'sin evidencia' stages)."""
    found, blind, seen = [], [], set()
    for b in r.get("riesgo_etapas", []):
        for e in b.get("etapas", []):
            if e.get("nivel") in ("medio", "alto") and (b["producto"], e["id"]) not in seen:
                seen.add((b["producto"], e["id"]))
                found.append((b["producto"], e))
            elif e.get("nivel") == "sin evidencia" and b["producto"] not in blind:
                blind.append(b["producto"])
    return found, blind


def _legal_sentence(r):
    s = r["semaforo_legal"]
    return (f"Semáforo legal (provisional): {s['color']}, y la zona del Mar Menor no está confirmada, "
            "así que esto no dice que cumplas la ley.")


def _meaning(r):
    parts = [STRATEGY_PREDICATE[s] for s in r.get("estrategias", []) if s in STRATEGY_PREDICATE]
    return " y ".join("la que " + p for p in parts)


def _why_current(r):
    s = ["Es lo que haces hoy y sirve de referencia para comparar las demás."]
    if _has_margin(r):
        txt = f"En un año típico deja unos {_eur(r['margen_eur_ha']['p50'])} por hectárea y año"
        if _has_exito(r):
            txt += f" y, en años simulados, sale bien el {_n(r['exito_pct']['valor'])} % de las veces"
        s.append(txt + ".")
    else:
        crops = _join(_crops_without_price(r)) or "algún cultivo"
        s.append(f"No sale cifra de dinero: a esta rotación le falta el precio abierto de {crops}, y sin precio no se "
                 "puede calcular el margen ni el porcentaje de años buenos.")
    if r.get("agua_m3_ha") is not None:
        s.append(f"Usa unos {_n(r['agua_m3_ha'])} m³ de agua por hectárea y año.")
    s.append(_legal_sentence(r))
    return " ".join(s)


def _money_sentence(r, ref):
    if ref is None:
        return None
    if not _has_margin(r):
        crops = _join(_crops_without_price(r)) or "algún cultivo"
        return f"No hemos podido calcular el dinero de esta opción: falta el precio de {crops}."
    a = r["margen_eur_ha"]["p50"]
    if not _has_margin(ref):
        crops = _join(_crops_without_price(ref)) or "algún cultivo"
        src = ("con el precio medio nacional, que puede ser optimista para Murcia" if _national(r) else
               "con precios orientativos, no con los de tu finca")
        return (f"No podemos comparar el dinero con lo que haces hoy: a tu rotación actual le falta el precio abierto de "
                f"{crops}, y sin precio no hay margen. Para esta opción, un año típico saldría en {_eur(a)} por hectárea "
                f"y año {src}.")
    b = ref["margen_eur_ha"]["p50"]
    d = a - b
    if round(d) == 0:
        return "En un año típico dejaría casi lo mismo que lo que haces hoy."
    word = "más" if d > 0 else "menos"
    return (f"En un año típico dejaría unos {_n(d)} € por hectárea y año {word} que lo que haces hoy "
            f"({_eur(a)} frente a {_eur(b)}).")


def _water_success_sentence(r, ref):
    if ref is None:
        return None
    parts = []
    if r.get("agua_m3_ha") is not None and ref.get("agua_m3_ha"):
        a, b = r["agua_m3_ha"], ref["agua_m3_ha"]
        d = a - b
        pct = abs(d) / abs(b) * 100
        if round(d) == 0:
            parts.append("Gastaría casi la misma agua que ahora")
        else:
            word = "más" if d > 0 else "menos"
            parts.append(f"Gastaría unos {_n(d)} m³ {word} de agua por hectárea y año que ahora (un {_n(pct)} % {word})")
    if _has_exito(r):
        a = _n(r["exito_pct"]["valor"])
        if _has_exito(ref):
            tail = f"en años simulados, sale bien el {a} % de las veces, frente al {_n(ref['exito_pct']['valor'])} % de hoy"
        else:
            tail = (f"en años simulados, sale bien el {a} % de las veces"
                    + (" con el precio medio nacional" if _national(r) else "")
                    + " (no hay porcentaje comparable de lo de hoy)")
        parts.append(tail if parts else tail[0].upper() + tail[1:])
    if not parts:
        return None
    return (" y, ".join(parts) if len(parts) == 2 else parts[0]) + "."


def _why_alt(r, ref):
    h = r.get("horizonte_anios")
    meaning = _meaning(r)
    first = (f"Sale de probar las combinaciones de cultivos permitidas durante {h} años y quedarse con {meaning}."
             if meaning and h else "Es una alternativa calculada por el motor a partir de los datos de la parcela.")
    s = [first]
    for x in (_money_sentence(r, ref), _water_success_sentence(r, ref)):
        if x:
            s.append(x)
    if ref is None:
        s.append("No hay una rotación actual con la que comparar.")
    s.append(_legal_sentence(r))
    return " ".join(s)


# ---------------------------------------------------------------------------------------------- the four text blocks


def _evidencia(r):
    out = ["Un año típico es el año del medio entre todos los simulados; un mal año es del decil inferior."]
    if _has_margin(r):
        m = r["margen_eur_ha"]
        out.append(f"Margen por hectárea y año: {_eur(m['p50'])} en un año típico, {_eur(m['p10'])} en un mal año "
                   f"y {_eur(m['p90'])} en un buen año.")
    e = r.get("exito_pct") or {}
    if _has_exito(r):
        lo, hi = e["horquilla"]
        out.append(f"Años buenos: {_n(e['valor'])} % de los años simulados (entre {_n(lo)} % y {_n(hi)} %). Cuenta como bueno "
                   "un año con margen positivo y sin pérdida de clima grande; es un cálculo, no una promesa.")
    if r.get("agua_m3_ha") is not None:
        out.append(f"Agua de riego: unos {_n(r['agua_m3_ha'])} m³ por hectárea y año.")
    inv = r.get("inversion") or {}
    if inv.get("pico_caja_negativa_eur_ha") is not None:
        txt = f"Hay que adelantar hasta {_n(inv['pico_caja_negativa_eur_ha'])} € por hectárea antes de cobrar"
        if inv.get("meses_hasta_primer_ingreso") is not None:
            txt += f"; el primer ingreso llegaría a los {_n(inv['meses_hasta_primer_ingreso'], 1)} meses"
        out.append(txt + ".")
    for x in r.get("riesgos", []):
        m = re.search(r"con (\d+) años de SIAM", x)
        if m:
            out.append(f"Se ha probado con el clima real de {m.group(1)} años de la estación más cercana; no es un pronóstico.")
    return out


def _no_sabemos(r):
    out = []
    if not _has_margin(r):
        out.append("Para esta rotación no hay margen ni porcentaje de años buenos: falta el precio de algún cultivo con datos abiertos.")
    carm = _crops_with(r, "CARM")
    if carm:
        out.append(f"Los precios de {_join(carm)} son cotizaciones orientativas de la CARM, no el precio pactado de tu finca: "
                   "si vendes a otro precio, el resultado cambia.")
    euro = _crops_with(r, "Eurostat")
    if euro:
        out.append(f"Para {_join(euro)} el precio es la media nacional de Eurostat, que suele ser optimista para Murcia: "
                   "el margen puede salir más alto de lo real.")
    mapa = _crops_with(r, "MAPA")
    if mapa:
        out.append(f"Para {_join(mapa)} usamos el precio medio de toda España del Ministerio de Agricultura para el cultivo "
                   "en general. No es el precio de Murcia ni el de tu variedad: es una aproximación y el margen real puede "
                   "ser otro.")
    for c in _crops_without_price(r):
        out.append(f"Para {c} no hay precio abierto: tendrías que poner el tuyo.")
    if _has_exito(r):
        out.append(f"El porcentaje de años buenos cuenta cada año del histórico una sola vez, con el plan completo: "
                   f"hay {r['exito_pct']['n']} años. No es un pronóstico.")
    gaps = " ".join(r.get("huecos", []))
    if "el clima NO resta kilos" in gaps:
        out.append("El clima todavía no resta kilos de cosecha: si hay helada o calor, el aviso va por etapas, pero el margen no lo descuenta.")
    if "semáforo legal provisional" in gaps:
        out.append("El semáforo legal es provisional: falta la tabla de normas y no sabemos si la parcela está en Zona 1 o Zona 2.")
    if any(c.get("resultado") == "no_evaluable" for c in r["semaforo_legal"].get("comprobaciones", [])):
        out.append("El abonado (nitrógeno) no lo puede evaluar la herramienta: depende de tu plan de abonado.")
    if "costes tomados de" in gaps:
        out.append("Para algún cultivo no hay estudio de costes propio y se usan los de un cultivo parecido.")
    if "CE del agua" in gaps:
        out.append("No sabemos la salinidad de tu agua de riego, así que no se descuenta pérdida por sal.")
    if "sobreoferta" in gaps:
        out.append("No se tiene en cuenta que, si muchos agricultores plantan lo mismo, el precio baja.")
    label = (r.get("nombre", "") + " " + " ".join(map(str, r.get("ciclos", [])))).lower()
    if "alcachofa" in label and "alcachofa se trata" in gaps:
        out.append("La alcachofa se calcula como cultivo de un año, aunque en realidad dura varios.")
    if "veza" in label and "cubierta de veza" in gaps:
        out.append("El coste y el aporte de nitrógeno de la cubierta de veza son supuestos, no medidos.")
    return out


def _riesgos(r):
    out = []
    e = r.get("exito_pct") or {}
    if e.get("peores_anios"):
        out.append(f"Los años más duros del histórico para este plan fueron {_year_list(e['peores_anios'])}.")
    if _has_margin(r):
        p10 = r["margen_eur_ha"]["p10"]
        if round(p10) < 0:
            out.append(f"En un mal año (del decil inferior) podrías perder {_n(p10)} € por hectárea.")
        else:
            out.append(f"En un mal año (del decil inferior) el margen bajaría a {_n(p10)} € por hectárea.")
    found, blind = _stage_levels(r)
    for prod, e2 in found:
        where = f" en la etapa de {e2['organo']}" if e2.get("organo") else ""
        out.append(f"{prod}: en {e2['anios_con_episodio']} de {e2['n']} años del histórico hubo {e2['peligro']} fuerte{where} "
                   f"({e2['condicion']}); riesgo {e2['nivel']}. Es lo que midió la estación, no daño observado.")
    if not found:
        out.append("Con la evidencia disponible no sale ninguna etapa con riesgo medio o alto.")
    if blind:
        out.append(f"En {_join(blind)} hay etapas sin evidencia documentada de daño por frío o calor. "
                   "Eso no es lo mismo que riesgo bajo: significa que no lo sabemos.")
    if r["semaforo_legal"]["color"] != "verde":
        out.append(f"El semáforo legal sale {r['semaforo_legal']['color']}. El detalle está en la ficha legal; no es un dictamen.")
    return out


def build_texto(r, ref):
    por_que = _why_current(r) if r.get("es_actual") else _why_alt(r, ref)
    return {"por_que": por_que, "evidencia_resumen": _evidencia(r), "no_sabemos": _no_sabemos(r),
            "riesgos_texto": _riesgos(r), "consulta": CONSULTA}


_REFERENCE_WORDING = (
    ("Es lo que haces hoy y sirve de referencia para comparar las demás.",
     "No sabemos qué cultivas hoy en esta parcela. Esta es la rotación típica de la zona y sirve de referencia para "
     "comparar las demás."),
    ("a tu rotación actual le falta", "a la rotación de referencia le falta"),
    ("lo que haces hoy", "la rotación de referencia"),
    ("% de hoy", "% de la referencia"),
    ("lo de hoy", "la referencia"),
    ("casi la misma agua que ahora", "casi la misma agua que la referencia"),
    ("por hectárea y año que ahora", "por hectárea y año que la referencia"),
    ("No hay una rotación actual con la que comparar.", "No hay una rotación de referencia con la que comparar."),
)


def _reword_reference(texto):
    """Per-parcel run where the reference rotation is NOT what the farmer grows (H-002: typical rotation of the area,
    an assumption): the sentences must not say "lo que haces hoy". Only words change, never a number."""
    def fix(s):
        for old, new in _REFERENCE_WORDING:
            s = s.replace(old, new)
        return s
    return {k: fix(v) if isinstance(v, str) else [fix(x) if isinstance(x, str) else x for x in v] if isinstance(v, list) else v
            for k, v in texto.items()}


def apply(out):
    """Write `texto` into every rotation, replace the generic `por_que`, and refuse to ship a text with an unbacked number."""
    rots = out["rotaciones"]
    ref = next((r for r in rots if r.get("es_actual")), None)
    for r in rots:
        r["texto"] = build_texto(r, ref)
        if out.get("actual_origen") == "supuesto_zona":
            r["texto"] = _reword_reference(r["texto"])
        r["por_que"] = r["texto"]["por_que"]
    bad = check(out)
    assert not bad, "texts.py: números no respaldados por el JSON: " + "; ".join(f"{i}: {n} en «{s}»" for i, n, s in bad[:5])
    return out
