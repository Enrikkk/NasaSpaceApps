"""Semáforo legal determinista (Ley 3/2020 Mar Menor + PAC). PROTOTIPO de preparación de T-019.

Regla del proyecto: el motor calcula, el LLM no. Solo librería estándar.
Herramienta de apoyo, no es asesoría legal. Consulta a tu técnico.

API
    check(rotacion, parcela, zona, contrato=False) -> dict semaforo_legal
    allowed(prev, cur, zona, ciclo_dias=None, conservador=False) -> (bool, motivo, articulo)
    to_contract(semaforo) -> dict compatible con contract.schema.json (vocabulario del esquema)

`zona`: "zona_1" | "zona_2" | "por_verificar" (los demás valores -> gris, sin cobertura legal del Mar Menor).

Entradas de `rotacion` (todas opcionales salvo `ciclos`):
    ciclos               lista de cultivos en orden (str, p. ej. ["melon", "barbecho", "lechuga"]); la rotación se repite
    ciclos_por_anio      int: cuántos elementos de `ciclos` caen en cada año (los agrupa en años consecutivos)
    anios                alternativa: lista de listas de cultivos por año
    ciclo_dias           {cultivo: días del ciclo}; necesario para las excepciones de 45 días
    suelo_desnudo_meses  nº de meses de suelo desnudo en otoño-invierno (si falta y es_actual, se usa parcela.ndvi.meses_desnudo)
    cobertera_invierno   bool: la rotación incluye cobertera enterrada/estructura de retención en otoño-invierno
    n_kg_ha_anio         kg N/ha y año
    abonado              lista de {forma_n: "urea"|"nitrato_amonico"|otro, fondo: bool, ultimo_tercio: bool}
Entradas de `parcela`: regadio (bool), invernadero (bool), distancia_orilla_m, explotacion_ha,
    ndvi{meses_desnudo: ["2025-10", ...]}, cobertura ("basico" -> gris).

Qué se comprueba y qué no: ver README.md. Nada se afirma como verificado: todas las reglas salen `por_verificar`.
"""
import csv
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent

NOTA = "Herramienta de apoyo, no es asesoría legal. Consulta a tu técnico."
VERSION_REGLAS = "borrador-2026-11-14"
ZONAS_OK = ("zona_1", "zona_2", "por_verificar")

# Umbrales del informe research/ley-3-2020-reglas.md (todos por verificar en el BOE)
MAX_CICLOS_ANIO = 2          # art. 39.2 y 51.2
MAX_CICLOS_HOJA_CORTA = 3    # art. 39.2: tres solo hortícolas de hoja de ciclo < 45 días
CICLO_CORTO_DIAS = 45        # art. 39.2 y 51.3
MAX_G1_ANIO = 1              # art. 51.2
MESES_DESNUDO_MAX = 2        # art. 51.6: "superior a dos meses"
VENTANA_OTONO_INVIERNO = {10, 11, 12, 1, 2, 3}  # INFERIDO: el texto no define "otoño e invierno"
FRANJA_M = 1500              # art. 29.1
MAX_N_FRANJA = 170           # art. 29.4.b, kg N/ha/año
BCAM7_VENTANA_ANIOS = 3      # BCAM 7: cambio de cultivo al menos una vez cada tres años
BCAM7_EXENCION_HA = 10       # explotaciones <= 10 ha exentas

ORDEN = ["L-07", "L-14", "L-15", "L-17", "L-16", "L-02", "L-03", "L-09", "L-10", "L-11", "P-02"]
NIVEL = {None: 0, "amarillo": 1, "rojo": 2}


def _leer_csv(nombre):
    with open(HERE / nombre, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _norm(s):
    s = unicodedata.normalize("NFKD", str(s).strip().lower())
    return re.sub(r"\s+", " ", "".join(c for c in s if not unicodedata.combining(c)))


REGLAS = {r["id"]: r for r in _leer_csv("rules.csv")}
GRUPOS = {}
for _r in _leer_csv("grupos_cultivo.csv"):
    for _nombre in [_r["cultivo"]] + [a for a in _r["alias"].split("|") if a]:
        GRUPOS[_norm(_nombre)] = _r


# --------------------------------------------------------------------------- cultivos
def info_cultivo(cultivo):
    """-> dict {nombre, tipo 'cultivo'|'sin_cultivo', grupo 1|2|None, confianza, hoja, conocido}."""
    if isinstance(cultivo, dict):
        cultivo = cultivo.get("cultivo", "")
    n = _norm(cultivo)
    fila = GRUPOS.get(n)
    if fila is None:
        return {"nombre": n, "tipo": "cultivo", "grupo": None, "confianza": "no_confirmado", "hoja": "desconocido", "conocido": False}
    grupo = int(fila["legal_group"]) if fila["legal_group"] in ("1", "2") else None
    return {"nombre": n, "tipo": fila["tipo"], "grupo": grupo, "confianza": fila["confianza"], "hoja": fila["hoja"], "conocido": True}


def _dias(nombre, ciclo_dias):
    if not ciclo_dias:
        return None
    for k, v in ciclo_dias.items():
        if _norm(k) == nombre:
            return v
    return None


def _par_grupo1(a, b, ciclo_dias):
    """Dos ciclos consecutivos de cultivo (dicts de info_cultivo). -> 'ok' | 'falla' | 'incierto' | 'desconocido' | 'inferido_falla'."""
    if a["grupo"] is None or b["grupo"] is None:
        # si uno es Grupo 2 conocido, el par no puede ser G1-G1
        if (a["grupo"] == 2) or (b["grupo"] == 2):
            return "ok"
        return "desconocido"
    if not (a["grupo"] == 1 and b["grupo"] == 1):
        return "ok"
    da, db = _dias(a["nombre"], ciclo_dias), _dias(b["nombre"], ciclo_dias)
    if da is not None and db is not None and da < CICLO_CORTO_DIAS and db < CICLO_CORTO_DIAS:
        return "ok"
    if da is None or db is None:
        # la excepción de 45 días podría aplicar, pero no lo sabemos
        return "incierto"
    return "inferido_falla" if "inferido" in (a["confianza"], b["confianza"]) else "falla"


# --------------------------------------------------------------------------- años y datos
def _anios(rot):
    """Lista de años, cada uno lista de nombres de cultivo; None si no se puede agrupar."""
    if rot.get("anios"):
        return [list(a) for a in rot["anios"]]
    n = rot.get("ciclos_por_anio")
    ciclos = rot.get("ciclos") or []
    if isinstance(n, int) and n >= 1:
        return [list(ciclos[i:i + n]) for i in range(0, len(ciclos), n)]
    return None


def _ciclos_reales(rot):
    return [info_cultivo(c) for c in (rot.get("ciclos") or []) if info_cultivo(c)["tipo"] == "cultivo"]


def _meses_desnudo(rot, parcela):
    """-> (meses_seguidos, nota) o None. Usa el valor de la rotación; si no, el NDVI de la parcela solo para la rotación actual."""
    v = rot.get("suelo_desnudo_meses")
    if isinstance(v, (int, float)):
        return v, "meses de suelo desnudo declarados en la rotación"
    lista = ((parcela or {}).get("ndvi") or {}).get("meses_desnudo")
    if lista and rot.get("es_actual"):
        ords = sorted({int(a) * 12 + int(m) for a, m in (x.split("-") for x in lista) if int(m) in VENTANA_OTONO_INVIERNO})
        mejor = actual = 0
        prev = None
        for o in ords:
            actual = actual + 1 if prev is not None and o == prev + 1 else 1
            mejor, prev = max(mejor, actual), o
        return mejor, "máximo de meses seguidos de suelo desnudo en oct-mar (ventana INFERIDA, el texto no define otoño-invierno)"
    return None


# --------------------------------------------------------------------------- comprobaciones
def _c(rid, resultado, nota="", efecto=None, sev=0, would=None):
    r = REGLAS[rid]
    d = {"id": rid, "regla": r["nombre"], "resultado": resultado,
         "articulo": f"{r['norma']} {r['articulo']}", "estado": r["estado"]}
    if nota:
        d["nota"] = nota
    d["_efecto"], d["_sev"], d["_would"] = efecto, sev, would
    return d


def _solo_z1(rid, zona, fn):
    """Reglas exclusivas de Zona 1: no_aplica en Zona 2; en 'por_verificar' no se afirman (ámbar)."""
    if zona == "zona_2":
        return _c(rid, "no_aplica", "Solo exigible en Zona 1 (arts. 50-54); no aplica en Zona 2")
    d = fn()
    if zona == "por_verificar" and d["resultado"] != "no_aplica":
        would = d["resultado"]
        nota = f"Zona del Mar Menor por verificar: no se afirma. Si fuese Zona 1 el resultado sería «{would}»"
        if d.get("nota"):
            nota += f" ({d['nota']})"
        sev = d.get("_sev", 0) if would != "ok" else 1
        return _c(rid, "no_evaluable", nota, "amarillo", sev, would)
    return d


def _l07(rot, parcela, zona):
    anios = _anios(rot)
    if anios is None:
        return _c("L-07", "no_evaluable", "Falta `ciclos_por_anio` o `anios`: no se puede contar ciclos por año", "amarillo", 2)
    peor = 0
    for a in anios:
        peor = max(peor, sum(1 for c in a if info_cultivo(c)["tipo"] == "cultivo"))
    if peor <= MAX_CICLOS_ANIO:
        return _c("L-07", "ok", f"Máximo {peor} ciclo(s) de cultivo en un año")
    if peor == MAX_CICLOS_HOJA_CORTA:
        for a in anios:
            cult = [info_cultivo(c) for c in a if info_cultivo(c)["tipo"] == "cultivo"]
            if len(cult) == 3:
                for c in cult:  # primero lo que ya incumple, luego lo que no se sabe
                    d = _dias(c["nombre"], rot.get("ciclo_dias"))
                    if c["hoja"] == "no":
                        return _c("L-07", "falla", f"3 ciclos en un año con {c['nombre']}, que no es hortícola de hoja", "rojo", 3)
                    if d is not None and d >= CICLO_CORTO_DIAS:
                        return _c("L-07", "falla", f"3 ciclos en un año con {c['nombre']} de {d} días (>= 45)", "rojo", 3)
                for c in cult:
                    if c["hoja"] != "si" or _dias(c["nombre"], rot.get("ciclo_dias")) is None:
                        return _c("L-07", "no_evaluable", f"3 ciclos en un año: solo permitido con hortícolas de hoja de ciclo < 45 días y no consta para {c['nombre']}", "amarillo", 3)
        return _c("L-07", "ok", "3 ciclos de hoja de ciclo < 45 días")
    return _c("L-07", "falla", f"{peor} ciclos de cultivo en un año (máximo 2; 3 solo hoja < 45 días)", "rojo", 3)


def _l16(rot, parcela, zona):
    def fn():
        desc = sorted({c["nombre"] for c in _ciclos_reales(rot) if c["grupo"] is None})
        if desc:
            return _c("L-16", "no_evaluable", "Grupo legal NO CONFIRMADO para: " + ", ".join(desc) + " (art. 51.4: se adscribe por profundidad radicular y manejo y se comunica a la Consejería)", "amarillo", 3)
        inf = sorted({c["nombre"] for c in _ciclos_reales(rot) if c["confianza"] == "inferido"})
        return _c("L-16", "ok", "Todos los cultivos tienen grupo" + (f" (INFERIDO para {', '.join(inf)})" if inf else ""))
    return _solo_z1("L-16", zona, fn)


def _l14(rot, parcela, zona):
    def fn():
        anios = _anios(rot)
        if anios is None:
            return _c("L-14", "no_evaluable", "Falta `ciclos_por_anio` o `anios`", "amarillo", 2)
        incierto = desconocido = False
        for a in anios:
            cult = [info_cultivo(c) for c in a if info_cultivo(c)["tipo"] == "cultivo"]
            if len(cult) > MAX_CICLOS_ANIO and not all(c["hoja"] == "si" for c in cult):
                return _c("L-14", "falla", f"{len(cult)} ciclos en un año en Zona 1 (máximo 2)", "rojo", 3)
            g1 = [c for c in cult if c["grupo"] == 1]
            desconocido = desconocido or any(c["grupo"] is None for c in cult)
            if len(g1) > MAX_G1_ANIO:
                cortos = [(_dias(c["nombre"], rot.get("ciclo_dias")) or 999) < CICLO_CORTO_DIAS for c in g1]
                known = all(_dias(c["nombre"], rot.get("ciclo_dias")) is not None for c in g1)
                if known and all(cortos):
                    continue
                if known:
                    ef = "amarillo" if any(c["confianza"] == "inferido" for c in g1) else "rojo"
                    return _c("L-14", "falla", f"{len(g1)} ciclos de Grupo 1 en un año (máximo 1)" + (" (alguno con grupo INFERIDO)" if ef == "amarillo" else ""), ef, 3)
                incierto = True
        if incierto:
            return _c("L-14", "no_evaluable", "Más de un ciclo de Grupo 1 en un año y falta `ciclo_dias` para la excepción de 45 días", "amarillo", 2)
        if desconocido:
            return _c("L-14", "no_evaluable", "Hay cultivos con grupo desconocido; no se puede contar el Grupo 1", "amarillo", 2)
        return _c("L-14", "ok", "Máximo 2 ciclos al año y 1 de Grupo 1")
    return _solo_z1("L-14", zona, fn)


def _l15(rot, parcela, zona):
    def fn():
        seq = _ciclos_reales(rot)
        if not seq:
            return _c("L-15", "no_evaluable", "Sin ciclos de cultivo", "amarillo", 2)
        estados = []
        for i, a in enumerate(seq):
            b = seq[(i + 1) % len(seq)]  # la rotación se repite: el último enlaza con el primero
            estados.append(_par_grupo1(a, b, rot.get("ciclo_dias")))
        if "falla" in estados:
            return _c("L-15", "falla", "Dos ciclos consecutivos de Grupo 1", "rojo", 3)
        if "inferido_falla" in estados:
            return _c("L-15", "falla", "Dos ciclos consecutivos de Grupo 1 (con grupo INFERIDO, p. ej. lechuga)", "amarillo", 3)
        if "incierto" in estados:
            return _c("L-15", "no_evaluable", "Dos Grupo 1 seguidos; la excepción de ciclo < 45 días no se puede comprobar sin `ciclo_dias`", "amarillo", 2)
        if "desconocido" in estados:
            return _c("L-15", "no_evaluable", "Hay cultivos con grupo desconocido en la secuencia", "amarillo", 2)
        return _c("L-15", "ok", "Sin dos ciclos de Grupo 1 consecutivos (barbecho se salta, la rotación se repite)")
    return _solo_z1("L-15", zona, fn)


def _l17(rot, parcela, zona):
    def fn():
        p = parcela or {}
        if p.get("invernadero"):
            return _c("L-17", "no_aplica", "Invernadero: art. 51.6 no aplica")
        if p.get("regadio") is False:
            return _c("L-17", "no_aplica", "Parcela de secano: art. 51.6 es para regadío")
        if p.get("regadio") is None:
            return _c("L-17", "no_evaluable", "No consta si es regadío", "amarillo", 2)
        m = _meses_desnudo(rot, p)
        if m is None:
            return _c("L-17", "no_evaluable", "Faltan meses de suelo desnudo (`suelo_desnudo_meses` o NDVI)", "amarillo", 2)
        valor, fuente = m
        if valor <= MESES_DESNUDO_MAX:
            return _c("L-17", "ok", f"{valor} mes(es) de suelo desnudo (límite: más de {MESES_DESNUDO_MAX}) - {fuente}")
        if rot.get("cobertera_invierno"):
            return _c("L-17", "ok", f"{valor} meses de suelo desnudo pero la rotación declara cobertera")
        return _c("L-17", "falla", f"{valor} meses de suelo desnudo (> {MESES_DESNUDO_MAX}) sin cobertera declarada - {fuente}", "rojo", 3)
    return _solo_z1("L-17", zona, fn)


def _franja(parcela):
    d = (parcela or {}).get("distancia_orilla_m")
    return None if d is None else d <= FRANJA_M


def _l02(rot, parcela, zona):
    en = _franja(parcela)
    if en is None:
        return _c("L-02", "no_evaluable", "Falta `distancia_orilla_m`: no se sabe si la parcela está en la franja de 1.500 m")
    if not en:
        return _c("L-02", "no_aplica", "Parcela a más de 1.500 m de la ribera")
    return _c("L-02", "no_evaluable", "Parcela en la franja de 1.500 m (art. 29): fertilizantes y abono en verde prohibidos; el alcance exacto no está cerrado, consultar al técnico", "amarillo", 3)


def _l03(rot, parcela, zona):
    en = _franja(parcela)
    if en is None:
        return _c("L-03", "no_evaluable", "Falta `distancia_orilla_m`")
    if not en:
        return _c("L-03", "no_aplica", "Parcela a más de 1.500 m de la ribera")
    n = rot.get("n_kg_ha_anio")
    if n is None:
        return _c("L-03", "no_evaluable", "En franja y falta `n_kg_ha_anio`", "amarillo", 2)
    if n > MAX_N_FRANJA:
        return _c("L-03", "falla", f"{n} kg N/ha/año en la franja (máximo {MAX_N_FRANJA})", "rojo", 3)
    return _c("L-03", "ok", f"{n} kg N/ha/año (máximo {MAX_N_FRANJA})")


def _abonado(rot, rid, fn_fallo, nota_ok, nota_falla):
    ab = rot.get("abonado")
    if not ab:
        return _c(rid, "no_evaluable", "Falta `abonado` (plan de abonado de la rotación)")
    if any(fn_fallo(a) for a in ab):
        return _c(rid, "falla", nota_falla, "rojo", 3)
    return _c(rid, "ok", nota_ok)


def _l09(rot, parcela, zona):
    return _abonado(rot, "L-09", lambda a: _norm(a.get("forma_n", "")) in ("urea", "ureico"),
                    "Sin urea ni N ureico en el plan", "El plan de abonado usa urea o N ureico")


def _l10(rot, parcela, zona):
    return _abonado(rot, "L-10", lambda a: bool(a.get("fondo")) and _norm(a.get("forma_n", "")) not in ("", "ninguno", "organico"),
                    "Sin abonado mineral de fondo con N", "El plan incluye abonado mineral de fondo con N")


def _l11(rot, parcela, zona):
    return _abonado(rot, "L-11", lambda a: _norm(a.get("forma_n", "")) == "nitrato_amonico" and bool(a.get("ultimo_tercio")),
                    "Sin nitrato amónico en el último tercio del ciclo", "Nitrato amónico en el último tercio del ciclo de hortícolas")


def _p02(rot, parcela, zona):
    anios = _anios(rot)
    if anios is None:
        principal = [info_cultivo(c)["nombre"] for c in (rot.get("ciclos") or [])]  # cada elemento = una campaña
    else:
        principal = []
        for a in anios:
            reales = [info_cultivo(c)["nombre"] for c in a if info_cultivo(c)["tipo"] == "cultivo"]
            principal.append(reales[0] if reales else "barbecho")  # "cultivo principal" INFERIDO = el primero del año
    if not principal:
        return _c("P-02", "no_evaluable", "Sin ciclos", "amarillo", 2)
    n = len(principal)
    for i in range(n):
        ventana = {principal[(i + k) % n] for k in range(BCAM7_VENTANA_ANIOS)}
        if len(ventana) < 2:
            ha = (parcela or {}).get("explotacion_ha")
            if ha is not None and ha > BCAM7_EXENCION_HA:
                return _c("P-02", "falla", "Mismo cultivo durante 3 años seguidos (BCAM 7)", "rojo", 3)
            return _c("P-02", "falla", "Mismo cultivo durante 3 años seguidos (BCAM 7); la exención de explotaciones <= 10 ha no se puede descartar sin `explotacion_ha`", "amarillo", 3)
    return _c("P-02", "ok", "Hay cambio de cultivo en toda ventana de 3 años (BCAM 7, nivel parcela)")


_EVAL = {"L-07": _l07, "L-16": _l16, "L-14": _l14, "L-15": _l15, "L-17": _l17, "L-02": _l02, "L-03": _l03,
         "L-09": _l09, "L-10": _l10, "L-11": _l11, "P-02": _p02}


# --------------------------------------------------------------------------- check
def _gris(motivo, zona):
    return {"color": "gris", "motivo": motivo, "articulo": "Ley 3/2020 (sin cobertura legal evaluada)",
            "comprobaciones": [], "zona": zona, "version_reglas": VERSION_REGLAS, "nota": NOTA}


def check(rotacion, parcela, zona, contrato=False):
    """Semáforo legal de una rotación. Con contrato=True devuelve el vocabulario de contract.schema.json."""
    if zona not in ZONAS_OK:
        return _gris(f"Zona «{zona}»: sin reglas legales del Mar Menor evaluadas.", zona)
    if (parcela or {}).get("cobertura") == "basico" or not (rotacion.get("ciclos") or []):
        return _gris("Cobertura básica o rotación sin ciclos: no se evalúa el semáforo legal.", zona)

    comps = [_EVAL[rid](rotacion, parcela, zona) for rid in ORDEN]
    orden = {rid: i for i, rid in enumerate(ORDEN)}
    rojos = [c for c in comps if c["_efecto"] == "rojo"]
    ambar = [c for c in comps if c["_efecto"] == "amarillo"]
    neutros = [c for c in comps if c["resultado"] == "no_evaluable" and c["_efecto"] is None]

    if rojos:
        color, lead = "rojo", sorted(rojos, key=lambda c: (-c["_sev"], orden[c["id"]]))
        motivo = f"Incumple {lead[0]['regla'].lower()}: {lead[0].get('nota', '')}"
        if len(lead) > 1:
            motivo += f" (y {len(lead) - 1} incumplimiento(s) más)"
    elif ambar:
        color, lead = "amarillo", sorted(ambar, key=lambda c: (-c["_sev"], orden[c["id"]]))
        pend = [c for c in lead if c["_would"] is not None]
        otros = [c for c in lead if c["_would"] is None]
        partes = []
        if pend:
            arts = ", ".join(sorted({c["articulo"].replace("Ley 3/2020 ", "") for c in pend}))
            peor = pend[0]
            partes.append(f"Zona del Mar Menor por verificar: las reglas exclusivas de Zona 1 ({arts}) no se afirman. "
                          f"Si fuese Zona 1: {peor['regla'].lower()} -> «{peor['_would']}»")
        for c in otros[:3]:
            partes.append(f"{c['articulo']}: {c.get('nota', c['regla'])}")
        motivo = ". ".join(partes)
    else:
        color = "verde"
        ok = [c for c in comps if c["resultado"] == "ok"]
        lead = ok
        etiqueta = {"zona_1": "Zona 1", "zona_2": "Zona 2"}[zona]
        motivo = f"Ninguna de las reglas evaluables para {etiqueta} falla (reglas aún por verificar en el BOE)"
    if color == "verde" and zona == "zona_2":
        m = _meses_desnudo(rotacion, parcela)
        if m is not None and m[0] > MESES_DESNUDO_MAX:
            motivo += (f". {m[0]} meses de suelo desnudo: en Zona 2 no es obligación legal (art. 51.6 es solo Zona 1); "
                       "una cubierta sería una mejora agronómica")
    if neutros:
        motivo += f". {len(neutros)} comprobación(es) no evaluable(s) por falta de datos: " + ", ".join(c["id"] for c in neutros)

    if color == "verde":
        arts = []
        for c in lead:
            if c["articulo"] not in arts:
                arts.append(c["articulo"])
        articulo = "; ".join(arts[:4]) or "Ley 3/2020 (sin regla evaluada)"
    else:
        articulo = lead[0]["articulo"]

    limpias = []
    for c in comps:
        d = {k: v for k, v in c.items() if not k.startswith("_")}
        limpias.append(d)
    sem = {"color": color, "motivo": motivo, "articulo": articulo, "comprobaciones": limpias,
           "zona": zona, "version_reglas": VERSION_REGLAS, "nota": NOTA}
    return to_contract(sem) if contrato else sem


MAPA_RESULTADO = {"ok": "cumple", "falla": "no_cumple", "no_evaluable": "indeterminado"}


def to_contract(sem):
    """Vocabulario de contract.schema.json: ok/falla/no_evaluable -> cumple/no_cumple/indeterminado.
    `no_aplica` no existe en el esquema: se omite (propuesta: añadirlo al enum)."""
    out = dict(sem)
    out["comprobaciones"] = [dict(c, resultado=MAPA_RESULTADO[c["resultado"]])
                             for c in sem["comprobaciones"] if c["resultado"] in MAPA_RESULTADO]
    return out


# --------------------------------------------------------------------------- allowed (para la DP de T-020)
def allowed(prev, cur, zona, ciclo_dias=None, conservador=False):
    """¿Puede `cur` seguir a `prev` en la misma parcela? -> (bool, motivo, articulo).

    Solo reglas de secuencia entre dos ciclos consecutivos (art. 51.3, solo Zona 1). Las reglas que necesitan el
    año completo (art. 39.2, 51.2) o la parcela (51.6) las evalúa check(). Si prev es barbecho, el llamador
    debe pasar el último cultivo real (el barbecho no es ciclo, INFERIDO).
    zona_2: siempre True. por_verificar: True con motivo «por verificar» (conservador=True -> trata como Zona 1).
    Grupo desconocido: True con aviso (conservador=True -> False).
    """
    art = f"{REGLAS['L-15']['norma']} {REGLAS['L-15']['articulo']}"
    if zona not in ZONAS_OK:
        return True, "Sin reglas legales del Mar Menor para esta zona.", art
    if zona == "zona_2":
        return True, "En Zona 2 no hay regla de secuencia entre ciclos (el art. 51.3 solo obliga en Zona 1).", art
    a, b = info_cultivo(prev), info_cultivo(cur)
    if a["tipo"] != "cultivo" or b["tipo"] != "cultivo":
        return True, "El barbecho no es ciclo de cultivo (INFERIDO): no hay dos ciclos consecutivos.", art
    estado = _par_grupo1(a, b, ciclo_dias)
    z1 = zona == "zona_1" or conservador
    pref = "" if zona == "zona_1" else "por verificar (zona sin confirmar): "
    if estado in ("falla", "inferido_falla"):
        extra = " (grupo INFERIDO)" if estado == "inferido_falla" else ""
        return (not z1), f"{pref}dos ciclos consecutivos de Grupo 1 ({a['nombre']}, {b['nombre']}){extra}", art
    if estado == "incierto":
        return (not z1), f"{pref}dos Grupo 1 seguidos y sin `ciclo_dias` no se puede aplicar la excepción de 45 días", art
    if estado == "desconocido":
        art41 = f"{REGLAS['L-16']['norma']} {REGLAS['L-16']['articulo']}"
        return (not conservador), f"por verificar: grupo legal NO CONFIRMADO ({a['nombre']}, {b['nombre']}); se admite pero check() sale ámbar", art41
    return True, "Sin dos ciclos de Grupo 1 consecutivos.", art
