#!/usr/bin/env python3
"""Valida un JSON contra contract.schema.v1.1.json y comprueba invariantes.

Requiere `jsonschema` (en un venv, no en el sistema):
    python3 -m venv /ruta/venv && /ruta/venv/bin/pip install jsonschema
    /ruta/venv/bin/python validate_v1_1.py fichero.json [--schema ...] [--selftest] [--strict-licencia]

Salida: errores de esquema, invariantes (OK / FALLO / AVISO) y resumen. Codigo de salida 0 si no hay errores de esquema
ni invariantes en FALLO. Los AVISO (comprobaciones blandas) no hacen fallar.
--strict-licencia: las menciones de 'CARM'/'esam' en el JSON pasan de AVISO a FALLO (politica: el JSON publicable debe tener 0).
--selftest: aplica mutaciones conocidas y comprueba que el validador las detecta.
"""
import argparse
import copy
import json
import math
import re
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    sys.exit("Falta jsonschema. Crea un venv e instala: pip install jsonschema")

HERE = Path(__file__).resolve().parent
CARGADO = {"real", "precalculado", "simulado"}
TOP_CONOCIDOS = {"schema_version", "_meta", "parcela", "historia", "ndvi", "clima", "suelo", "prioridades_defecto", "escenarios_meta",
                 "rotaciones", "variantes", "sensores", "fuentes", "no_sustituye",
                 # campos propios de enrique (documentados en el schema)
                 "_estado_bloques", "licencia", "criterios_sentido", "supuestos_decision", "generado"}
POLITICA_LICENCIA = re.compile(r"carm|esam", re.I)


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


def textos(o, ruta=""):
    """Recorre todos los strings (claves y valores) con su ruta."""
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(k, str):
                yield f"{ruta}/{k} [clave]", k
            yield from textos(v, f"{ruta}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from textos(v, f"{ruta}[{i}]")
    elif isinstance(o, str):
        yield ruta, o


def estados_de_bloques(doc):
    out = dict((doc.get("_meta") or {}).get("estado_bloques") or {})
    for b in ("parcela", "ndvi", "clima", "suelo"):
        if isinstance(doc.get(b), dict) and "_status" in doc[b]:
            out[b] = doc[b]["_status"]
    return out


def check_invariantes(doc, strict_licencia=False):
    """Devuelve lista de (nombre, nivel, [mensajes]). nivel = 'error' | 'aviso'. Lista vacia = OK."""
    res = []

    def inv(nombre, mensajes, nivel="error"):
        res.append((nombre, nivel, mensajes))

    rots = doc.get("rotaciones", [])
    meta = doc.get("_meta", {})
    pend = set(meta.get("bloques_pendientes", [])) | {k for k, v in (meta.get("estado_bloques") or {}).items() if v == "cargando"}
    cargadas = [r for r in rots if r.get("_status") in CARGADO]

    # 1. estructura de rotaciones (ids libres, minimo 3)
    e = []
    if "rotaciones" not in pend:
        if len(rots) < 3:
            e.append(f"hay {len(rots)} rotaciones, se exigen >= 3")
        actuales = [r.get("id") for r in rots if r.get("es_actual")]
        if len(actuales) != 1:
            e.append(f"debe haber exactamente 1 rotacion es_actual, hay {len(actuales)}: {actuales}")
    ids = [r.get("id") for r in rots]
    if len(set(ids)) != len(ids):
        e.append(f"ids de rotacion repetidos: {ids}")
    inv("rotaciones: >= 3, una sola es_actual, ids unicos (ids libres)", e)

    # 2. margen: horquilla == [p10, p90] cuando exista; p10<=p50<=p90; valor dentro
    e = []
    for r in cargadas:
        m = r.get("margen_eur_ha")
        if not isinstance(m, dict):
            continue  # null: lo gobierna el esquema (huecos/definicion)
        h = m.get("horquilla")
        if h is not None and m.get("p10") is not None and m.get("p90") is not None and h != [m["p10"], m["p90"]]:
            e.append(f"{r['id']}: horquilla {h} != [p10, p90] = [{m['p10']}, {m['p90']}]")
        ps = [m.get(k) for k in ("p10", "p50", "p90")]
        if None not in ps and not ps[0] <= ps[1] <= ps[2]:
            e.append(f"{r['id']}: p10 <= p50 <= p90 no se cumple {ps}")
        if h is not None and not h[0] <= h[1]:
            e.append(f"{r['id']}: horquilla de margen invertida {h}")
        if h is not None and m.get("valor") is not None and not h[0] <= m["valor"] <= h[1]:
            e.append(f"{r['id']}: valor {m['valor']} fuera de la horquilla {h}")
    inv("margen: horquilla == [p10,p90] (si existe), p10<=p50<=p90, valor dentro de la horquilla", e)

    # 2b. (blando) percentiles == percentiles de las muestras, media == media de las muestras
    e = []
    for r in cargadas:
        m, s = r.get("margen_eur_ha"), r.get("escenarios")
        if isinstance(m, dict) and s:
            for k, q in (("p10", 0.10), ("p50", 0.50), ("p90", 0.90)):
                if m.get(k) is not None and abs(percentile(s, q) - m[k]) > 1.5:
                    e.append(f"{r['id']}: {k}={m[k]} no coincide con las muestras (calculado {percentile(s, q):.1f})")
            if m.get("media") is not None and abs(sum(s) / len(s) - m["media"]) > 1.5:
                e.append(f"{r['id']}: media={m['media']} no coincide con las muestras ({sum(s) / len(s):.1f})")
    inv("margen: p10/p50/p90 y media coherentes con escenarios (tolerancia 1,5)", e, "aviso")

    # 3. exito_pct
    e = []
    for r in cargadas:
        x = r.get("exito_pct")
        if not isinstance(x, dict):
            continue
        k, n, v, h = x.get("k_malos"), x.get("n"), x.get("valor"), x.get("horquilla")
        if v is not None and h is not None and not (0 <= h[0] <= v <= h[1] <= 100):
            e.append(f"{r['id']}: horquilla {h} no encierra el valor {v} dentro de 0-100")
        if k is not None and n:
            if k > n:
                e.append(f"{r['id']}: k_malos {k} > n {n}")
            elif v is not None and abs(v - 100 * (n - k) / n) > 0.1:
                e.append(f"{r['id']}: valor {v} != 100*(n-k)/n = {100 * (n - k) / n:.1f}")
            elif h is not None and "wilson" in str(x.get("metodo", "")).lower():
                lo, hi = wilson(n - k, n)
                if abs(h[0] - 100 * lo) > 0.6 or abs(h[1] - 100 * hi) > 0.6:  # 0,6 cubre redondeo a entero
                    e.append(f"{r['id']}: horquilla {h} != Wilson 95 % [{100 * lo:.1f}, {100 * hi:.1f}]")
        d = x.get("desglose", {})
        for nombre, it in d.items():
            if it["k_malos"] > it["n"]:
                e.append(f"{r['id']}: desglose.{nombre}.k_malos > n")
    inv("exito_pct: k_malos<=n, valor==100(n-k)/n, horquilla encierra el valor, Wilson si metodo=wilson", e)

    e = []
    for r in cargadas:
        x = r.get("exito_pct")
        if isinstance(x, dict) and x.get("k_malos") is not None and len(x.get("peores_anios", [])) > x["k_malos"]:
            e.append(f"{r['id']}: {len(x['peores_anios'])} peores_anios > k_malos {x['k_malos']}")
    inv("exito_pct: no hay mas peores_anios que anios malos", e, "aviso")

    # 4. criterios en [0,1] o null; pesos
    e = []
    for r in cargadas:
        for k, v in (r.get("criterios") or {}).items():
            if v is not None and not (isinstance(v, (int, float)) and 0 <= v <= 1):
                e.append(f"{r['id']}: criterios.{k} = {v} fuera de [0,1]")
        for vid, var in (r.get("variantes") or {}).items():
            for k, v in (var.get("criterios") or {}).items():
                if v is not None and not 0 <= v <= 1:
                    e.append(f"{r['id']}.variantes.{vid}: criterios.{k} = {v} fuera de [0,1]")
    p = doc.get("prioridades_defecto", {})
    if p and abs(sum(p.values()) - 1) > 1e-6:
        e.append(f"prioridades_defecto suman {sum(p.values()):.4f}, deben sumar 1")
    inv("criterios en [0,1] o null; prioridades_defecto suman 1", e)

    # 5. escenarios: mismo nº en todas las rotaciones que los tengan
    e = []
    longs = {r["id"]: len(r["escenarios"]) for r in cargadas if isinstance(r.get("escenarios"), list)}
    if len(set(longs.values())) > 1:
        e.append(f"nº de escenarios distinto entre rotaciones: {longs}")
    em = doc.get("escenarios_meta")
    if em:
        for rid, ln in longs.items():
            if ln != em["n"]:
                e.append(f"{rid}: {ln} muestras != escenarios_meta.n {em['n']}")
        for campo in ("anio_clima", "beta_sobreoferta", "factor_coste"):
            if campo in em and len(em[campo]) != em["n"]:
                e.append(f"escenarios_meta.{campo}: {len(em[campo])} elementos != n {em['n']}")
        orden = em.get("rotaciones_orden")
        if orden and orden != [r["id"] for r in rots]:
            e.append(f"escenarios_meta.rotaciones_orden {orden} != orden de rotaciones {[r['id'] for r in rots]}")
    for r in cargadas:
        if any(not math.isfinite(v) for v in (r.get("escenarios") or [])):
            e.append(f"{r['id']}: muestra no finita")
        for vid, var in (r.get("variantes") or {}).items():
            if var.get("escenarios") and r.get("escenarios") and len(var["escenarios"]) != len(r["escenarios"]):
                e.append(f"{r['id']}.variantes.{vid}: {len(var['escenarios'])} muestras != {len(r['escenarios'])} de la rotacion")
    sin = [r["id"] for r in cargadas if "escenarios" not in r]
    inv("escenarios: mismo nº en todas las rotaciones que los tienen, == escenarios_meta.n" +
        (f" (sin escenarios: {sin})" if sin else ""), e)

    # 6. ninguna rotacion con alcaparra (D-008): ciclos, nombre y plan_anios
    e = []
    for r in rots:
        trozos = [r.get("nombre", "")] + list(r.get("ciclos", []))
        for pa in r.get("plan_anios", []) or []:
            trozos += list(pa.get("ciclos", [])) + [pa.get("opcion", "")] + list((pa.get("siembras") or {}).keys())
        if any("alcaparra" in str(t).lower() for t in trozos):
            e.append(f"{r.get('id')}: contiene 'alcaparra' (D-008 la quita)")
    inv("D-008: ninguna rotacion con 'alcaparra'", e)

    # 7. zona legal no afirmada sin verificar
    e = []
    afirmadas = [z for z in doc.get("parcela", {}).get("zonas", []) if z in ("mar_menor_zona_1", "mar_menor_zona_2")]
    if afirmadas:
        e.append(f"zonas afirma {afirmadas}: el Anexo I de la Ley 3/2020 no esta verificado; usar mar_menor_zona_por_verificar")
    inv("parcela.zonas no afirma zona 1/2 sin verificar", e)

    # 8. agua
    e = []
    for r in cargadas:
        a = r.get("agua_detalle")
        if not a:
            continue
        b = a.get("bruto_m3_ha")
        if isinstance(b, dict):
            ps = [b.get(k) for k in ("p10", "p50", "p90")]
            if None not in ps and not ps[0] <= ps[1] <= ps[2]:
                e.append(f"{r['id']}: agua bruto p10<=p50<=p90 no se cumple {ps}")
            if b.get("p50") is not None and r.get("agua_m3_ha") is not None and abs(b["p50"] - r["agua_m3_ha"]) > 1:
                e.append(f"{r['id']}: agua_detalle.bruto_m3_ha.p50 {b['p50']} != agua_m3_ha {r['agua_m3_ha']}")
            if b.get("p50") is not None and a.get("tarifa_eur_m3") is not None and a.get("coste_eur_ha") is not None \
                    and abs(b["p50"] * a["tarifa_eur_m3"] - a["coste_eur_ha"]) > 1:
                e.append(f"{r['id']}: coste_eur_ha != bruto.p50 * tarifa")
    inv("agua_detalle: p10<=p50<=p90, p50 == agua_m3_ha, coste == bruto*tarifa si existen", e)

    # 9. historia
    e = []
    hist = doc.get("historia", [])
    anios = [h.get("anio") for h in hist if isinstance(h, dict)]
    if len(set(anios)) != len(anios):
        e.append(f"anios repetidos en historia: {anios}")
    for h in hist:
        for dcl in h.get("declaraciones", []) or []:
            if "campana" in dcl and int(dcl["campana"][:4]) != h["anio"]:
                e.append(f"historia {h['anio']}: declaracion de campana {dcl['campana']} no coincide con el anio")
        if h.get("cultivo") is None and h.get("declaraciones"):
            e.append(f"historia {h['anio']}: cultivo null pero hay declaraciones")
    inv("historia: lista con anios unicos; declaraciones coherentes con el anio", e)

    # 10. semaforo legal
    e = []
    for r in cargadas:
        s = r.get("semaforo_legal", {})
        comps = s.get("comprobaciones", [])
        if s.get("color") == "verde" and any(c["resultado"] == "falla" for c in comps):
            e.append(f"{r['id']}: semaforo verde con una comprobacion 'falla'")
        if s.get("color") == "rojo" and comps and not any(c["resultado"] == "falla" for c in comps):
            e.append(f"{r['id']}: semaforo rojo sin ninguna comprobacion 'falla'")
        if s.get("provisional") and s.get("_status") == "real":
            e.append(f"{r['id']}: semaforo provisional no puede ser _status real")
    inv("semaforo_legal: color coherente con las comprobaciones; provisional != real", e)

    # 11. fuentes: ids unicos y referencias existentes
    e = []
    fids = [f["id"] for f in doc.get("fuentes", [])]
    if len(set(fids)) != len(fids):
        e.append("ids de fuentes repetidos")
    usados = set()
    for b in ("parcela", "ndvi", "suelo", "sensores"):
        if isinstance(doc.get(b), dict) and doc[b].get("fuente_id"):
            usados.add((b, doc[b]["fuente_id"]))
    for h in doc.get("historia", []):
        if h.get("fuente_id"):
            usados.add(("historia", h["fuente_id"]))
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

    # 12. _status y aviso MOCK
    e = []
    estados = estados_de_bloques(doc)
    if any(v == "simulado" for v in estados.values()) and "MOCK" not in meta.get("aviso", ""):
        e.append("hay bloques simulados pero _meta.aviso no lleva el aviso MOCK")
    for b in ("historia", "rotaciones"):
        if b not in (meta.get("estado_bloques") or {}) and b not in pend:
            e.append(f"falta _meta.estado_bloques.{b} (las listas no pueden llevar _status)")
    inv("_meta.aviso con MOCK si hay bloques simulados; estado de las listas en _meta.estado_bloques", e)

    # 12b. claves de primer nivel desconocidas (informativo)
    desconocidos = sorted(set(doc) - TOP_CONOCIDOS)
    inv("sin claves de primer nivel desconocidas" + (f" (hay: {desconocidos})" if desconocidos else ""),
        [f"claves no definidas en v1.1: {desconocidos} (admitidas por additionalProperties, pero sin documentar)"] if desconocidos else [], "aviso")

    # 13. politica de licencia: el JSON publicable no debe mencionar CARM ni esam
    menciones = [(ruta, t) for ruta, t in textos(doc) if POLITICA_LICENCIA.search(t)]
    resumen = {}
    for ruta, _ in menciones:
        k = re.sub(r"\[\d+\]", "[]", ruta)
        resumen[k] = resumen.get(k, 0) + 1
    inv(f"politica de licencia: 0 menciones de CARM/esam (hay {len(menciones)})",
        [f"{n}x {k}" for k, n in sorted(resumen.items())], "error" if strict_licencia else "aviso")

    return res


def validar(doc, schema):
    v = Draft202012Validator(schema)
    errores = sorted(v.iter_errors(doc), key=lambda er: [str(p) for p in er.absolute_path])
    return [f"{'/'.join(str(p) for p in er.absolute_path) or '(raiz)'}: {er.message[:220]}" for er in errores]


def informe(doc, schema, verbose=True, strict_licencia=False):
    ee = validar(doc, schema)
    try:
        inv = check_invariantes(doc, strict_licencia)
    except (KeyError, TypeError, IndexError, ValueError, AttributeError) as exc:
        inv = [(f"invariantes no evaluables por estructura invalida ({type(exc).__name__}: {exc})", "error", ["ver errores de esquema"])]
    fallos = sum(1 for _, nivel, m in inv if m and nivel == "error")
    avisos = sum(1 for _, nivel, m in inv if m and nivel == "aviso")
    if verbose:
        print(f"Esquema (draft 2020-12): {'OK, 0 errores' if not ee else f'{len(ee)} ERRORES'}")
        for m in ee[:40]:
            print("   -", m)
        print("Invariantes:")
        for nombre, nivel, msgs in inv:
            etiqueta = "OK" if not msgs else ("FALLO" if nivel == "error" else "AVISO")
            print(f"   [{etiqueta}] {nombre}")
            for m in msgs:
                print("        ->", m)
    return len(ee), fallos, avisos


def selftest(doc, schema):
    """Mutaciones que el validador DEBE detectar (sobre el documento adaptado)."""
    def mut(f):
        d = copy.deepcopy(doc)
        f(d)
        return d
    r = lambda d, i=1: d["rotaciones"][i]
    casos = {
        "horquilla != [p10,p90]": lambda d: r(d)["margen_eur_ha"].__setitem__("horquilla", [0, 1]),
        "k_malos > n": lambda d: r(d, 0)["exito_pct"].__setitem__("k_malos", 999),
        "criterio fuera de [0,1]": lambda d: r(d, 2)["criterios"].__setitem__("agua", 1.4),
        "distinto nº de escenarios": lambda d: r(d)["escenarios"].pop(),
        "alcaparra vuelve": lambda d: r(d, 2).__setitem__("ciclos", ["cebada", "alcaparra"]),
        "zona 2 afirmada": lambda d: d["parcela"]["zonas"].append("mar_menor_zona_2"),
        "falta bloque P0 (clima)": lambda d: d.pop("clima"),
        "_status invalido": lambda d: d["ndvi"].__setitem__("_status", "mock"),
        "vocabulario antiguo (cumple)": lambda d: r(d, 0)["semaforo_legal"]["comprobaciones"][0].__setitem__("resultado", "cumple"),
        "null sin explicacion (exito_pct null y sin huecos)": lambda d: (r(d, 0).__setitem__("exito_pct", None), r(d, 0).__setitem__("huecos", [])),
        "margen sin unidad": lambda d: r(d)["margen_eur_ha"].pop("unidad"),
        "referencia a fuente inexistente": lambda d: r(d, 0)["evidencia"][0].__setitem__("fuente_id", "no-existe"),
        "menos de 3 rotaciones": lambda d: (d["rotaciones"].pop(), d["rotaciones"].pop()),
        "semaforo verde con falla": lambda d: (r(d, 0)["semaforo_legal"].__setitem__("color", "verde"),
                                              r(d, 0)["semaforo_legal"]["comprobaciones"][0].__setitem__("resultado", "falla")),
        "schema_version de otra mayor": lambda d: d.__setitem__("schema_version", "2.0.0"),
    }
    ok = True
    print("Autoprueba del validador (cada mutacion debe ser rechazada):")
    for nombre, f in casos.items():
        ee, fallos, _ = informe(mut(f), schema, verbose=False)
        detectado = ee > 0 or fallos > 0
        ok &= detectado
        print(f"   [{'detectado' if detectado else 'NO DETECTADO'}] {nombre}  (errores de esquema: {ee}, invariantes fallidas: {fallos})")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--schema", default=str(HERE / "contract.schema.v1.1.json"))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--strict-licencia", action="store_true")
    a = ap.parse_args()
    schema = json.loads(Path(a.schema).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    doc = json.loads(Path(a.json).read_text(encoding="utf-8"))
    print(f"Fichero: {a.json}\nSchema:  {a.schema}")
    ee, fallos, avisos = informe(doc, schema, strict_licencia=a.strict_licencia)
    ok = ee == 0 and fallos == 0
    if a.selftest:
        ok &= selftest(doc, schema)
    rots = doc.get("rotaciones", [])
    print(f"\nRESUMEN: {'OK' if ok else 'FALLO'} | errores de esquema: {ee} | invariantes fallidas: {fallos} | avisos: {avisos} | "
          f"rotaciones: {len(rots)} | escenarios/rotacion: {[len(r.get('escenarios', [])) for r in rots]}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
