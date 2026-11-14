#!/usr/bin/env python3
"""Valida un JSON de contrato v1 contra contract.schema.json y comprueba invariantes.

Requiere la libreria `jsonschema` (instalada en un venv, no en el sistema):
    python3 -m venv /ruta/venv && /ruta/venv/bin/pip install jsonschema
    /ruta/venv/bin/python validate.py [fichero.json] [--schema contract.schema.json] [--selftest]

Salida: lista de errores de esquema, lista de invariantes con OK/FALLO, resumen. Codigo de salida 0 si todo OK.
--selftest: aplica mutaciones conocidas al JSON y comprueba que el validador las detecta (prueba del propio validador).
"""
import argparse
import copy
import json
import math
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    sys.exit("Falta jsonschema. Crea un venv e instala: pip install jsonschema")

HERE = Path(__file__).resolve().parent
CARGADO = {"real", "precalculado", "simulado"}
TOP_CONOCIDOS = {"schema_version", "_meta", "parcela", "historia", "ndvi", "clima", "suelo", "prioridades_defecto",
                 "escenarios_meta", "rotaciones", "variantes", "sensores", "fuentes", "no_sustituye"}


def percentile(values, q):
    v = sorted(values)
    pos = (len(v) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return v[lo] + (v[hi] - v[lo]) * (pos - lo)


def wilson(successes, n, z=1.959964):
    p = successes / n
    d = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    mitad = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, centro - mitad), min(1.0, centro + mitad)


def check_invariantes(doc):
    """Devuelve lista de (nombre, [errores]). Lista vacia de errores = OK."""
    res = []

    def inv(nombre, errores):
        res.append((nombre, errores))

    rots = doc.get("rotaciones", [])
    pend = set(doc.get("_meta", {}).get("bloques_pendientes", []))
    cargadas = [r for r in rots if r.get("_status") in CARGADO]

    # 1. estructura de rotaciones
    e = []
    if "rotaciones" not in pend:
        if len(rots) < 3:
            e.append(f"hay {len(rots)} rotaciones, se exigen >= 3 (actual + 2)")
        actuales = [r.get("id") for r in rots if r.get("es_actual")]
        if len(actuales) != 1:
            e.append(f"debe haber exactamente 1 rotacion es_actual, hay {len(actuales)}: {actuales}")
    ids = [r.get("id") for r in rots]
    if len(set(ids)) != len(ids):
        e.append(f"ids de rotacion repetidos: {ids}")
    inv("rotaciones: >= 3, una sola es_actual, ids unicos", e)

    # 2. horquilla == [p10, p90], p10 <= p50 <= p90, valor dentro, percentiles coherentes con las muestras
    e = []
    for r in cargadas:
        m = r.get("margen_eur_ha", {})
        if m.get("_status") == "cargando":
            continue
        h = m.get("horquilla")
        if "p10" in m and "p90" in m and h != [m["p10"], m["p90"]]:
            e.append(f"{r['id']}: horquilla {h} != [p10, p90] = [{m['p10']}, {m['p90']}]")
        if all(k in m for k in ("p10", "p50", "p90")) and not m["p10"] <= m["p50"] <= m["p90"]:
            e.append(f"{r['id']}: p10 <= p50 <= p90 no se cumple ({m['p10']}, {m['p50']}, {m['p90']})")
        if h and not h[0] <= h[1]:
            e.append(f"{r['id']}: horquilla de margen invertida {h}")
        if h and "valor" in m and not h[0] <= m["valor"] <= h[1]:
            e.append(f"{r['id']}: valor {m['valor']} fuera de la horquilla {h}")
        s = r.get("escenarios_margen_eur_ha")
        if s and all(k in m for k in ("p10", "p50", "p90")):
            for k, q in (("p10", 0.10), ("p50", 0.50), ("p90", 0.90)):
                calc = percentile(s, q)
                if abs(calc - m[k]) > 1:
                    e.append(f"{r['id']}: {k}={m[k]} no coincide con las muestras (calculado {calc:.1f})")
    inv("margen: horquilla == [p10,p90], p10<=p50<=p90, percentiles == los de las muestras", e)

    # 3. exito_pct
    e = []
    for r in cargadas:
        x = r.get("exito_pct", {})
        if x.get("_status") == "cargando":
            continue
        h = x.get("horquilla")
        if h and not (0 <= h[0] <= x["valor"] <= h[1] <= 100):
            e.append(f"{r['id']}: horquilla {h} no encierra el valor {x['valor']} dentro de 0-100")
        if "k_malos" in x and "n" in x:
            k, n = x["k_malos"], x["n"]
            if k > n:
                e.append(f"{r['id']}: k_malos {k} > n {n}")
            elif abs(x["valor"] - 100 * (n - k) / n) > 1:
                e.append(f"{r['id']}: valor {x['valor']} != 100*(n-k)/n = {100 * (n - k) / n:.1f}")
            elif h:
                lo, hi = wilson(n - k, n)
                if abs(h[0] - 100 * lo) > 1 or abs(h[1] - 100 * hi) > 1:
                    e.append(f"{r['id']}: horquilla {h} != Wilson 95 % [{100 * lo:.0f}, {100 * hi:.0f}]")
            d = x.get("desglose", {})
            for nombre, it in d.items():
                if it["k_malos"] > it["n"]:
                    e.append(f"{r['id']}: desglose.{nombre}.k_malos > n")
            if {"clima", "economico", "conjunto"} <= d.keys():
                kc, ke, kj = d["clima"]["k_malos"], d["economico"]["k_malos"], d["conjunto"]["k_malos"]
                if not max(kc, ke) <= kj <= kc + ke:
                    e.append(f"{r['id']}: conjunto {kj} debe estar entre max(clima,economico)={max(kc, ke)} y su suma {kc + ke}")
                if kj != k:
                    e.append(f"{r['id']}: desglose.conjunto.k_malos {kj} != k_malos {k}")
            if len(x.get("peores_anios", [])) > k:
                e.append(f"{r['id']}: hay mas peores_anios que anios malos")
    inv("exito_pct: k_malos<=n, valor==100(n-k)/n, horquilla==Wilson 95 %, desglose coherente", e)

    # 4. criterios en [0,1] y pesos
    e = []
    for r in cargadas:
        for k, v in r.get("criterios", {}).items():
            if not (isinstance(v, (int, float)) and 0 <= v <= 1):
                e.append(f"{r['id']}: criterios.{k} = {v} fuera de [0,1]")
    p = doc.get("prioridades_defecto", {})
    if p and abs(sum(p.values()) - 1) > 1e-6:
        e.append(f"prioridades_defecto suman {sum(p.values()):.4f}, deben sumar 1")
    inv("criterios en [0,1]; prioridades_defecto suman 1", e)

    # 5. escenarios alineados
    e = []
    meta = doc.get("escenarios_meta")
    longitudes = {r["id"]: len(r["escenarios_margen_eur_ha"]) for r in cargadas if "escenarios_margen_eur_ha" in r}
    if len(set(longitudes.values())) > 1:
        e.append(f"nº de escenarios distinto entre rotaciones: {longitudes}")
    if meta:
        n = meta["n"]
        for rid, ln in longitudes.items():
            if ln != n:
                e.append(f"{rid}: {ln} muestras != escenarios_meta.n {n}")
        for campo in ("anio_clima", "beta_sobreoferta", "factor_coste"):
            if campo in meta and len(meta[campo]) != n:
                e.append(f"escenarios_meta.{campo}: {len(meta[campo])} elementos != n {n}")
        orden = meta.get("rotaciones_orden")
        if orden and orden != [r["id"] for r in rots]:
            e.append(f"escenarios_meta.rotaciones_orden {orden} != orden de rotaciones {[r['id'] for r in rots]}")
    elif longitudes:
        e.append("hay escenarios_margen_eur_ha pero falta escenarios_meta")
    for r in cargadas:
        for v in r.get("escenarios_margen_eur_ha", []):
            if not math.isfinite(v):
                e.append(f"{r['id']}: muestra no finita")
                break
    inv("escenarios: mismo nº en todas las rotaciones, == escenarios_meta.n, listas auxiliares alineadas", e)

    # 6. alt-b sin alcaparra (D-008)
    e = []
    con_alcaparra = [r["id"] for r in rots if any("alcaparra" in c.lower() for c in r.get("ciclos", []))]
    if con_alcaparra:
        e.append(f"rotaciones con alcaparra (D-008 la quita): {con_alcaparra}")
    altb = [r for r in rots if r.get("id") == "alt-b"]
    if "rotaciones" in pend and not rots:
        pass  # bloque aun cargando
    elif len(altb) != 1:
        e.append(f"debe haber un unico alt-b, hay {len(altb)}")
    elif altb[0].get("ciclos") != ["cebada", "veza", "cebada"]:
        e.append(f"alt-b.ciclos = {altb[0].get('ciclos')}, se esperaba ['cebada', 'veza', 'cebada']")
    inv("D-008: ninguna rotacion con alcaparra y un unico alt-b == cebada, veza, cebada", e)

    # 7. zona legal no afirmada sin verificar
    e = []
    zonas = doc.get("parcela", {}).get("zonas", [])
    afirmadas = [z for z in zonas if z in ("mar_menor_zona_1", "mar_menor_zona_2")]
    if afirmadas:
        e.append(f"zonas afirma {afirmadas}: el Anexo I de la Ley 3/2020 no esta verificado; usar mar_menor_zona_por_verificar")
    inv("parcela.zonas no afirma zona 1/2 sin verificar", e)

    # 8. agua
    e = []
    for r in cargadas:
        a = r.get("agua_detalle")
        if not a:
            continue
        if "bruto_m3_ha" in a and a["bruto_m3_ha"] != r.get("agua_m3_ha"):
            e.append(f"{r['id']}: agua_detalle.bruto_m3_ha {a['bruto_m3_ha']} != agua_m3_ha {r.get('agua_m3_ha')}")
        if {"bruto_m3_ha", "tarifa_eur_m3", "coste_eur_ha"} <= a.keys() and abs(a["bruto_m3_ha"] * a["tarifa_eur_m3"] - a["coste_eur_ha"]) > 1:
            e.append(f"{r['id']}: coste_eur_ha != bruto * tarifa")
        if {"etc_mm", "bruto_m3_ha", "eficiencia_riego", "precipitacion_efectiva_mm"} <= a.keys():
            esperado = a["bruto_m3_ha"] * a["eficiencia_riego"] / 10 + a["precipitacion_efectiva_mm"]
            if abs(esperado - a["etc_mm"]) > 1:
                e.append(f"{r['id']}: etc_mm {a['etc_mm']} != bruto*eficiencia/10 + P_ef = {esperado:.0f}")
        if {"ecw_dSm", "ece_dSm"} <= a.keys() and abs(1.5 * a["ecw_dSm"] - a["ece_dSm"]) > 0.01:
            e.append(f"{r['id']}: ece_dSm != 1,5 * ecw_dSm (regla practica del borrador)")
    inv("agua_detalle coherente con agua_m3_ha, tarifa, eficiencia y ECe", e)

    # 9. historia
    e = []
    for c in doc.get("historia", {}).get("cultivos_declarados", []):
        if "anio" in c and "campana" in c and int(c["campana"][:4]) != c["anio"]:
            e.append(f"campana {c['campana']} no coincide con anio {c['anio']}")
    inv("historia: campana explicita y coherente con anio", e)

    # 10. semaforo legal: comprobaciones con articulo; color gris/verde coherente con 'no_cumple'
    e = []
    for r in cargadas:
        s = r.get("semaforo_legal", {})
        comps = s.get("comprobaciones", [])
        if s.get("color") == "verde" and any(c["resultado"] == "no_cumple" for c in comps):
            e.append(f"{r['id']}: semaforo verde con una comprobacion no_cumple")
        if s.get("color") == "rojo" and comps and not any(c["resultado"] == "no_cumple" for c in comps):
            e.append(f"{r['id']}: semaforo rojo sin ninguna comprobacion no_cumple")
    inv("semaforo_legal: color coherente con las comprobaciones", e)

    # 11. fuentes: ids unicos y referencias existentes
    e = []
    fids = [f["id"] for f in doc.get("fuentes", [])]
    if len(set(fids)) != len(fids):
        e.append("ids de fuentes repetidos")
    usados = set()
    for b in ("parcela", "historia", "ndvi", "suelo", "sensores"):
        if doc.get(b, {}).get("fuente_id"):
            usados.add((b, doc[b]["fuente_id"]))
    for fid in doc.get("clima", {}).get("lluvia_anual_mm", {}).get("fuentes", []):
        usados.add(("clima.lluvia_anual_mm", fid))
    for r in rots:
        for ev in r.get("evidencia", []):
            if ev.get("fuente_id"):
                usados.add((f"{r['id']}.evidencia", ev["fuente_id"]))
    for donde, fid in sorted(usados):
        if fid not in fids:
            e.append(f"{donde} referencia la fuente '{fid}' que no esta en fuentes[]")
    inv("fuentes: ids unicos y todas las referencias fuente_id existen", e)

    # 12. _status y aviso
    e = []
    if any(b.get("_status") == "simulado" for b in [doc.get(k, {}) for k in ("parcela", "clima", "suelo", "ndvi", "historia")]) \
            and "MOCK" not in doc.get("_meta", {}).get("aviso", ""):
        e.append("hay bloques simulados pero _meta.aviso no lleva el aviso MOCK")
    desconocidos = sorted(set(doc) - TOP_CONOCIDOS)
    if desconocidos:
        e.append(f"claves de primer nivel no definidas en el borrador: {desconocidos} (aviso, no error de esquema)")
    inv("_meta.aviso presente con bloques simulados; sin claves de primer nivel desconocidas", e)

    return res


def validar(doc, schema):
    v = Draft202012Validator(schema)
    errores = sorted(v.iter_errors(doc), key=lambda er: list(er.absolute_path))
    return [f"{'/'.join(str(p) for p in er.absolute_path) or '(raiz)'}: {er.message[:220]}" for er in errores]


def informe(doc, schema, verbose=True):
    ee = validar(doc, schema)
    try:
        inv = check_invariantes(doc)
    except (KeyError, TypeError, IndexError, ValueError) as exc:  # documento tan roto que una invariante no se puede evaluar
        inv = [(f"invariantes no evaluables por estructura invalida ({type(exc).__name__}: {exc})", ["ver errores de esquema"])]
    fallos = sum(1 for _, e in inv if e)
    if verbose:
        print(f"Esquema (draft 2020-12): {'OK, 0 errores' if not ee else f'{len(ee)} ERRORES'}")
        for m in ee[:40]:
            print("   -", m)
        print("Invariantes:")
        for nombre, errs in inv:
            print(f"   [{'OK' if not errs else 'FALLO'}] {nombre}")
            for m in errs:
                print("        ->", m)
    return len(ee), fallos


def selftest(doc, schema):
    """Mutaciones que el validador DEBE detectar."""
    def mut(f):
        d = copy.deepcopy(doc)
        f(d)
        return d

    casos = {
        "horquilla != [p10,p90]": lambda d: d["rotaciones"][1]["margen_eur_ha"].__setitem__("horquilla", [0, 1]),
        "k_malos > n": lambda d: d["rotaciones"][0]["exito_pct"].__setitem__("k_malos", 99),
        "criterio fuera de [0,1]": lambda d: d["rotaciones"][2]["criterios"].__setitem__("agua", 1.4),
        "distinto nº de escenarios": lambda d: d["rotaciones"][1]["escenarios_margen_eur_ha"].pop(),
        "alcaparra vuelve": lambda d: d["rotaciones"][2].__setitem__("ciclos", ["cebada", "vezas", "alcaparra"]),
        "zona 2 afirmada": lambda d: d["parcela"]["zonas"].append("mar_menor_zona_2"),
        "falta bloque P0 (clima)": lambda d: d.pop("clima"),
        "_status invalido": lambda d: d["ndvi"].__setitem__("_status", "real_o_casi"),
        "estado de comprobacion invalido": lambda d: d["rotaciones"][0]["semaforo_legal"]["comprobaciones"][0].__setitem__("estado", "seguro"),
        "historia sin campana": lambda d: d["historia"]["cultivos_declarados"][0].pop("campana"),
        "referencia a fuente inexistente": lambda d: d["rotaciones"][0]["evidencia"][0].__setitem__("fuente_id", "no-existe"),
    }
    ok = True
    print("Autoprueba del validador (cada mutacion debe ser rechazada):")
    for nombre, f in casos.items():
        ee, fallos = informe(mut(f), schema, verbose=False)
        detectado = ee > 0 or fallos > 0
        ok &= detectado
        print(f"   [{'detectado' if detectado else 'NO DETECTADO'}] {nombre}  (errores de esquema: {ee}, invariantes fallidas: {fallos})")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json", nargs="?", default=str(HERE / "torre-pacheco.contract-v1.draft.json"))
    ap.add_argument("--schema", default=str(HERE / "contract.schema.json"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    schema = json.loads(Path(a.schema).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    doc = json.loads(Path(a.json).read_text(encoding="utf-8"))
    print(f"Fichero: {a.json}\nSchema:  {a.schema}")
    ee, fallos = informe(doc, schema)
    ok = ee == 0 and fallos == 0
    if a.selftest:
        ok &= selftest(doc, schema)
    n = len(doc.get("rotaciones", []))
    print(f"\nRESUMEN: {'OK' if ok else 'FALLO'} | errores de esquema: {ee} | invariantes fallidas: {fallos} | "
          f"rotaciones: {n} | escenarios/rotacion: {[len(r.get('escenarios_margen_eur_ha', [])) for r in doc.get('rotaciones', [])]}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
