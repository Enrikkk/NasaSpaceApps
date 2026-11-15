#!/usr/bin/env python3
"""Prueba real contra un servidor en marcha: peticiones, latencias y validacion contra el esquema del contrato v1.

    uvicorn app.backend.api.main:app --port 8099 &            # desde la raiz del repo
    python app/backend/api/smoke.py http://127.0.0.1:8099 [--sin-red]     # --sin-red: pide solo el bloque parcela fuera de cobertura y omite Albacete (llamarian a POWER/Open-Meteo/SoilGrids); para CERO red real arranca el servidor con AGROCKHAM_OFFLINE=1 o el contenedor con --network none

Necesita jsonschema (venv). Esquema y validador: app/data/contract.schema.json y app/data/contract/validate_contract.py.
"""
import argparse
import gzip
import importlib.util
import json
import math
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data"     # app/data
spec = importlib.util.spec_from_file_location("validate_contract", DATA / "contract" / "validate_contract.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
SCHEMA = json.loads((DATA / "contract.schema.json").read_text(encoding="utf-8"))

DEMO = {"lat": 37.7383, "lon": -0.98838}
RECINTO = {"provincia": 30, "municipio": 37, "agregado": 0, "zona": 0, "poligono": 18, "parcela": 426, "recinto": 1}
FALLOS = []


def http(base, metodo, ruta, cuerpo=None, cabeceras=None):
    data = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(base + ruta, data=data, method=metodo, headers={"Content-Type": "application/json", **(cabeceras or {})})
    t = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            raw, status, h = r.read(), r.status, dict(r.headers)
    except urllib.error.HTTPError as e:
        raw, status, h = e.read(), e.code, dict(e.headers)
    dt = (time.perf_counter() - t) * 1000
    h = {k.title(): v for k, v in h.items()}
    if h.get("Content-Encoding") == "gzip":
        raw = gzip.decompress(raw)
    return status, json.loads(raw), h, dt, len(raw)


def valida(nombre, doc):
    ee = V.validar(doc, SCHEMA)
    fallos = [n for n, nivel, m in V.check_invariantes(doc) if m and nivel == "error"]
    ok = not ee and not fallos
    print(f"   validacion: {'OK' if ok else 'FALLO'} (esquema: {len(ee)} errores; invariantes que fallan: {len(fallos)})")
    for e in ee[:5]:
        print("     -", e)
    if not ok:
        FALLOS.append(nombre)


def analizar(base, nombre, cuerpo, query=""):
    s, d, h, ms, n = http(base, "POST", "/analyze" + query, cuerpo)
    m = d.get("_meta", {})
    print(f"[{nombre}] HTTP {s} en {ms:.0f} ms, {n/1024:.1f} kB; servidor: {m.get('latencia_ms')}")
    print(f"   estados: {m.get('estado_bloques')}; cobertura: {m.get('cobertura', {}).get('nivel')}; pendientes: {m.get('bloques_pendientes')}; sin datos: {m.get('bloques_sin_datos')}")
    for a in m.get("avisos", []):
        print("   aviso:", a[:150])
    if s != 200:
        FALLOS.append(nombre)
        return d, ms
    valida(nombre, d)
    return d, ms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--sin-red", action="store_true")
    a = ap.parse_args()
    base = a.base.rstrip("/")
    s, h, _, ms, _ = http(base, "GET", "/health")
    print(f"[health] {s} {ms:.0f} ms {h}")
    d, _ = analizar(base, "demo recinto completo", {**DEMO, "recinto": RECINTO})
    p = d["parcela"]
    print(f"   parcela {p['id']} {p['ha']} ha, pend {p.get('pendiente_pct')} %, municipio {p.get('municipio')}; lluvia {d['clima']['lluvia_anual_mm']['valor']} mm; suelo {d['suelo']['textura']}")
    print("   semaforos:", [r["semaforo_legal"]["color"] for r in d["rotaciones"]], "recinto_completo:", d["_meta"]["consulta"]["recinto_completo"])
    t = [analizar(base, f"demo repetida {i}", DEMO)[1] for i in range(3)]
    print(f"   latencias repetidas (cache): {[round(x) for x in t]} ms")
    d, _ = analizar(base, "demo zona_2 y recinto parcial", {**DEMO, "zona": "zona_2", "recinto": {"poligono": 18, "parcela": 426}})
    print("   semaforos zona_2:", [r["semaforo_legal"]["color"] for r in d["rotaciones"]], "recinto:", d["_meta"]["consulta"]["recinto"], d["_meta"]["consulta"]["recinto_completo"])
    d, _ = analizar(base, "demo solo parcela", DEMO, "?bloques=parcela")
    # Con --sin-red solo se pide el bloque parcela: pedir todos los bloques hace que el servidor salga a POWER/Open-Meteo/SoilGrids.
    d, _ = analizar(base, "fuera de cobertura (Murcia ciudad, sin ATOM)", {"lat": 37.9922, "lon": -1.1307}, "?bloques=parcela" if a.sin_red else "")
    if not a.sin_red:
        punto = {"lat": 38.95, "lon": -1.85}   # campo cerca de Albacete: clima y suelo globales, sin recintos cargados
        d, _ = analizar(base, "fuera de cobertura (Albacete rural; clima y suelo en vivo)", punto)
        print("   Albacete clima:", d["clima"].get("lluvia_anual_mm", {}).get("valor"), "mm; suelo:", d["suelo"].get("textura"))
        d, _ = analizar(base, "Albacete de nuevo (ya en cache)", punto)
    for nombre, cuerpo in (("lat fuera de rango", {"lat": 95, "lon": 0}), ("recinto cadena", {**DEMO, "recinto": "x"})):
        s, d, _, ms, _ = http(base, "POST", "/analyze", cuerpo)
        print(f"[{nombre}] HTTP {s} ({ms:.0f} ms)")
        if s != 422:
            FALLOS.append(nombre)
    for nombre, km in (("viewport ~1 km", 1.0), ("viewport ~5 km", 4.9), ("rectangulo 8 km (sobre el limite)", 8.0)):
        dlat = km / 2 / 111.32
        dlon = km / 2 / (111.32 * math.cos(math.radians(37.77)))
        q = f"?bbox={-0.95-dlon},{37.77-dlat},{-0.95+dlon},{37.77+dlat}"
        s, fc, h, ms, n = http(base, "GET", "/recintos" + q, cabeceras={"Accept-Encoding": "gzip"})
        print(f"[/recintos {nombre}] HTTP {s} {ms:.0f} ms; {fc.get('n')} de {fc.get('n_total')} recintos, truncado={fc.get('truncado')}, "
              f"{n/1024:.0f} kB sin comprimir, Content-Encoding={h.get('Content-Encoding')}")
    print("\nRESULTADO:", "FALLOS " + str(FALLOS) if FALLOS else "todo OK")
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
