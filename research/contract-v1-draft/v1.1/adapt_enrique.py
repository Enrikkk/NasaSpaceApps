#!/usr/bin/env python3
"""Convierte el JSON del motor de enrique (app/data/torre-pacheco.json, rama t012-motor-nucleo) al contrato v1.1-draft.

Solo libreria estandar. NO inventa datos: solo renombra, normaliza vocabulario, anade metadatos deducibles y avisa de lo que falta.

    python3 adapt_enrique.py enrique_torre-pacheco.json -o torre-pacheco.contract-v1.1.draft.json \
        --origen "enrique app/data/torre-pacheco.json @ origin/t012-motor-nucleo f3be98b"
    python3 adapt_enrique.py borrador_v1.json --formato draft-v1 -o salida.json   # adaptacion minima del borrador v1 antiguo

Que hace (todo queda anotado en _meta.adaptaciones / _meta.avisos del resultado):
  * schema_version "1.1.0-draft" y _meta {aviso, generado, origen, adaptado_por, adaptado, estado_bloques, ...}.
    El texto de `_status` de primer nivel de enrique pasa a _meta.aviso.
  * `_status` por bloque derivado de `_estado_bloques`: mock -> simulado; provisional -> simulado + provisional:true; real -> real.
    Los `_status` en prosa ("provisional: tabla ...", "simulado (deltas ...)") se reducen a la palabra de estado y el resto va a `nota`.
    Se conserva `_estado_bloques` tal cual (referencia legacy).
  * semaforo legal: mismo color y mismo articulo. resultado: ok->ok; aviso->no_evaluable; por_verificar->no_evaluable; no_evaluado->no_evaluable
    (el valor original queda en `resultado_original`; `estado: por_verificar` porque su semaforo es provisional). Edita MAPA_RESULTADO si enrique dice otra cosa.
  * parcela.zonas: mar_menor_zona_1/2 -> mar_menor_zona_por_verificar (Anexo I sin verificar).
  * fuentes[] minimo: una entrada por fuente_id de evidencia (nombre=dataset, url) mas los ids de clima.lluvia_anual_mm.fuentes;
    licencia "por verificar" + licencia_estado "verify" salvo que el propio JSON de enrique traiga texto de licencia (licencia.fuentes_restringidas).
  * rotaciones sin `escenarios` (o con null): se deja la clave ausente y se avisa. Nunca se inventan muestras.
  * sobreoferta_detalle con todo null y _status 'pendiente': se omite (sobreoferta se queda en null).
"""
import argparse
import copy
import datetime as dt
import json
import re
import sys
from pathlib import Path

SCHEMA_VERSION = "1.1.0-draft"
ADAPTADOR = "research/contract-v1-draft/v1.1/adapt_enrique.py"
LICENCIA_PENDIENTE = "por verificar (ver submission/data-citations.md)"

# Vocabulario de comprobaciones legales -> v1.1. Cambiar aqui si enrique aclara el significado de 'aviso'.
MAPA_RESULTADO = {
    "ok": "ok", "falla": "falla", "no_aplica": "no_aplica", "no_evaluable": "no_evaluable",
    # 'aviso' = regla exclusiva de Zona 1 (art. 51.6) con la zona sin confirmar: segun legal.py es no_evaluable ("si fuese Zona 1: falla");
    # el detalle numerico (77 dias > 60) se conserva en `detalle`. Mismo criterio para el 'aviso' del borrador v1 (abonado: depende del plan).
    "aviso": "no_evaluable",
    "por_verificar": "no_evaluable", "no_evaluado": "no_evaluable",
    # borrador v1 antiguo
    "cumple": "ok", "no_cumple": "falla", "indeterminado": "no_evaluable",
}
# Vocabulario de estado de bloque -> v1.1 (estado, provisional)
MAPA_ESTADO = {
    "mock": ("simulado", False), "simulado": ("simulado", False), "provisional": ("simulado", True),
    "real": ("real", False), "precalculado": ("precalculado", False), "cargando": ("cargando", False),
}
BLOQUES_DICT = ("parcela", "ndvi", "suelo", "clima")
ZONAS_SIN_VERIFICAR = {"mar_menor_zona_1", "mar_menor_zona_2"}


def norm_estado(raw):
    """'provisional: texto' / 'simulado (texto)' / 'mock' -> (estado|None, provisional, resto_de_texto)."""
    if not isinstance(raw, str):
        return None, False, None
    m = re.match(r"^\s*([A-Za-zñÑ_]+)\s*(?:[:(]\s*(.*?)\)?)?\s*$", raw, re.S)
    if not m:
        return None, False, raw
    palabra = m.group(1).lower()
    resto = (m.group(2) or "").strip() or None
    if palabra not in MAPA_ESTADO:
        return None, False, raw
    est, prov = MAPA_ESTADO[palabra]
    return est, prov, resto


def slug_id(nombre):
    """'SIAM TP91' -> 'SIAM-TP91' (mismo id que usa enrique en evidencia[].fuente_id)."""
    return re.sub(r"[^A-Za-z0-9_-]+", "-", nombre.strip()).strip("-")


class Ctx:
    def __init__(self):
        self.adaptaciones = []
        self.avisos = []
        self.transiciones = set()

    def ad(self, txt):
        if txt not in self.adaptaciones:
            self.adaptaciones.append(txt)

    def av(self, txt):
        if txt not in self.avisos:
            self.avisos.append(txt)


def adapt_comprobaciones(sem, ctx, provisional):
    for c in sem.get("comprobaciones", []):
        orig = c.get("resultado")
        nuevo = MAPA_RESULTADO.get(orig)
        if nuevo is None:
            ctx.av(f"semaforo_legal: resultado desconocido '{orig}' (regla '{c.get('regla')}') se deja tal cual")
            continue
        if nuevo != orig:
            c["resultado_original"] = orig
            ctx.transiciones.add(f"{orig}->{nuevo}")
        c["resultado"] = nuevo
        if "estado" not in c and provisional:
            c["estado"] = "por_verificar"
    if provisional:
        ctx.ad("semaforo_legal.comprobaciones[].estado = por_verificar (el semaforo de enrique es provisional)")


def adapt_semaforo(sem, estado_global, ctx):
    est, prov, resto = norm_estado(sem.get("_status"))
    if est is None:  # sin _status propio: usa el estado global del bloque
        est, prov, resto = norm_estado(estado_global)
    if est is None:
        est, prov = "simulado", False
        ctx.av("semaforo_legal sin estado derivable: se marca simulado")
    sem["_status"] = est
    if prov or estado_global == "provisional":
        sem["provisional"] = True
    if resto and "nota" not in sem:
        sem["nota"] = resto
    adapt_comprobaciones(sem, ctx, bool(sem.get("provisional")))


def adapt_rotacion(r, estado_rotaciones, estado_semaforo, ctx):
    rid = r.get("id", "?")
    est, _, _ = norm_estado(estado_rotaciones)
    if "_status" in r and norm_estado(r["_status"])[0]:
        est = norm_estado(r["_status"])[0]
    if est is None:
        est = "simulado"
        ctx.av(f"rotacion {rid}: sin estado en _estado_bloques; se marca simulado")
    r["_status"] = est

    if isinstance(r.get("semaforo_legal"), dict):
        adapt_semaforo(r["semaforo_legal"], estado_semaforo, ctx)

    sd = r.get("sobreoferta_detalle")
    if isinstance(sd, dict) and all(v is None for k, v in sd.items() if k != "_status") and norm_estado(sd.get("_status"))[0] is None:
        del r["sobreoferta_detalle"]
        ctx.ad("rotaciones[].sobreoferta_detalle omitido: todo null y _status 'pendiente' (no es un estado del contrato)")

    ad = r.get("agua_detalle")
    if isinstance(ad, dict) and isinstance(ad.get("bruto_m3_ha"), (int, float)):
        ad["bruto_m3_ha"] = {"p10": None, "p50": ad["bruto_m3_ha"], "p90": None}
        ctx.ad("agua_detalle.bruto_m3_ha numero -> {p10:null, p50:valor, p90:null}")

    for k, v in list((r.get("variantes") or {}).items()):
        e, _, resto = norm_estado(v.get("_status"))
        if e:
            v["_status"] = e
            if resto and "nota" not in v:
                v["nota"] = resto
            ctx.ad("rotaciones[].variantes[*]._status en prosa -> palabra de estado + nota")

    if "escenarios_margen_eur_ha" in r and "escenarios" not in r:
        r["escenarios"] = r.pop("escenarios_margen_eur_ha")
        ctx.ad("escenarios_margen_eur_ha -> escenarios (nombre de enrique)")
    if r.get("escenarios") is None:
        r.pop("escenarios", None)
        ctx.av(f"rotacion {rid}: sin 'escenarios' (muestras de margen). Se deja ausente; no se inventan muestras")

    margen = r.get("margen_eur_ha")
    if isinstance(margen, dict) and "unidad" not in margen:
        ctx.av(f"rotacion {rid}: margen_eur_ha sin 'unidad' (obligatoria en v1.1)")
    nulos = [k for k in ("exito_pct", "margen_eur_ha", "criterios") if k in r and r[k] is None]
    if nulos and not r.get("huecos"):
        ctx.av(f"rotacion {rid}: {nulos} = null sin huecos[] que lo expliquen (el esquema lo rechaza)")
    return r


def construir_fuentes(d, ctx):
    fuentes, ids = [], {}
    restringidas = (d.get("licencia") or {}).get("fuentes_restringidas") or {}

    def anadir(fid, nombre, url=None, nota=None):
        if fid in ids:
            return
        f = {"id": fid, "nombre": nombre}
        if url:
            f["url"] = url
        lic = restringidas.get(fid)
        f["licencia"] = lic if lic else LICENCIA_PENDIENTE
        f["licencia_estado"] = "verify"
        if nota:
            f["nota"] = nota
        ids[fid] = f
        fuentes.append(f)

    for r in d.get("rotaciones", []):
        for ev in r.get("evidencia", []):
            fid = ev.get("fuente_id")
            if fid:
                anadir(fid, ev.get("dataset") or fid, ev.get("url"), ev.get("aviso"))
    llu = (d.get("clima") or {}).get("lluvia_anual_mm")
    if isinstance(llu, dict) and llu.get("fuentes"):
        nuevos = []
        for nombre in llu["fuentes"]:
            fid = nombre if nombre in ids else slug_id(nombre)
            if fid != nombre:
                ctx.ad(f"clima.lluvia_anual_mm.fuentes: '{nombre}' -> id '{fid}'")
            anadir(fid, nombre)
            nuevos.append(fid)
        llu["fuentes"] = nuevos
    sin_entrada = []
    for b in ("ndvi", "suelo", "parcela"):
        f = (d.get(b) or {}).get("fuente")
        if f:
            sin_entrada.append(f"{b}: {f}")
    for h in d.get("historia", []) if isinstance(d.get("historia"), list) else []:
        if h.get("fuente"):
            sin_entrada.append(f"historia: {h['fuente']}")
    if sin_entrada:
        ctx.av("fuentes citadas en bloques de entrada sin entrada en fuentes[] (bloques en MOCK, aun no se usa el dato real): "
               + "; ".join(sorted(set(sin_entrada))))
    if not fuentes:
        ctx.av("no se pudo deducir ninguna fuente: fuentes[] vacio (el esquema exige minItems 1)")
    ctx.ad("fuentes[] construido de evidencia[] y clima.lluvia_anual_mm.fuentes; licencia 'por verificar' + licencia_estado 'verify'")
    return fuentes


def adapt_enrique(src, origen="app/data/torre-pacheco.json (enrique, t012-motor-nucleo)", hoy=None):
    d = copy.deepcopy(src)
    ctx = Ctx()
    hoy = hoy or dt.date.today().isoformat()
    estado = d.get("_estado_bloques") or {}
    if not estado:
        ctx.av("falta _estado_bloques: los estados por bloque se marcan 'simulado' por prudencia")

    # aviso: el _status (texto) de primer nivel pasa a _meta.aviso
    aviso = d.pop("_status", None)
    if isinstance(aviso, str):
        ctx.ad("_status (texto) de primer nivel -> _meta.aviso")
    else:
        aviso = "MOCK: aviso de procedencia no incluido en el origen; revisar bloques simulados."
        ctx.av("el origen no trae _status de primer nivel: _meta.aviso es un texto generico")

    # parcela.zonas
    zonas = (d.get("parcela") or {}).get("zonas")
    if isinstance(zonas, list):
        afirmadas = [z for z in zonas if z in ZONAS_SIN_VERIFICAR]
        if afirmadas:
            d["parcela"]["zonas"] = [z for z in zonas if z not in ZONAS_SIN_VERIFICAR] + ["mar_menor_zona_por_verificar"]
            ctx.ad(f"parcela.zonas: {afirmadas} -> mar_menor_zona_por_verificar (Anexo I sin verificar)")

    # historia: lista (forma de enrique); el borrador v1 la traia como objeto
    estado_bloques = {}
    hist = d.get("historia")
    if isinstance(hist, dict) and "cultivos_declarados" in hist:
        d["historia"] = historia_desde_objeto(hist, ctx)
        e, _, _ = norm_estado(hist.get("_status"))
        estado_bloques["historia"] = e or "simulado"
    # estado por bloque
    for b in BLOQUES_DICT:
        if not isinstance(d.get(b), dict):
            continue
        e, _, resto = norm_estado(estado.get(b)) if b in estado else norm_estado(d[b].get("_status"))
        if e is None:
            e = "simulado"
            ctx.av(f"bloque {b}: sin estado en _estado_bloques; se marca simulado")
        d[b]["_status"] = e
        estado_bloques[b] = e
    if "historia" not in estado_bloques:
        e, _, _ = norm_estado(estado.get("historia"))
        estado_bloques["historia"] = e or "simulado"
    ctx.ad("_status por bloque derivado de _estado_bloques (mock->simulado, provisional->simulado+provisional:true, real->real)")

    clima = d.get("clima") or {}
    e50 = clima.get("escenario_2050")
    if isinstance(e50, dict):
        e, _, resto = norm_estado(e50.get("_status"))
        if e is None:
            e, _, resto = norm_estado(estado.get("escenario_2050"))
        if e:
            e50["_status"] = e
            if resto and "nota" not in e50:
                e50["nota"] = resto
        else:
            ctx.av("clima.escenario_2050 sin estado derivable")

    # rotaciones
    rots = d.get("rotaciones") or []
    for r in rots:
        adapt_rotacion(r, estado.get("rotaciones"), estado.get("semaforo_legal"), ctx)
    e_rot, _, _ = norm_estado(estado.get("rotaciones"))
    estado_bloques["rotaciones"] = e_rot or "simulado"
    if "semaforo_legal" in estado:
        e_s, prov_s, _ = norm_estado(estado["semaforo_legal"])
        estado_bloques["semaforo_legal"] = e_s or "simulado"
    if "variantes" in estado:
        e_v, _, _ = norm_estado(estado["variantes"])
        estado_bloques["variantes"] = e_v or "simulado"
    if "escenario_2050" in estado:
        e_e, _, _ = norm_estado(estado["escenario_2050"])
        estado_bloques["escenario_2050"] = e_e or "simulado"

    if ctx.transiciones:
        ctx.ad("semaforo_legal.comprobaciones[].resultado: " + ", ".join(sorted(ctx.transiciones)) + " (original en resultado_original)")
    fuentes = construir_fuentes(d, ctx)

    # escenarios_meta minimo (solo lo deducible)
    longs = {r["id"]: len(r["escenarios"]) for r in rots if isinstance(r.get("escenarios"), list)}
    escenarios_meta = None
    if longs and len(set(longs.values())) == 1:
        n = next(iter(longs.values()))
        escenarios_meta = {"_status": estado_bloques["rotaciones"], "n": n,
                           "alineados": bool((d.get("escenarios_meta") or {}).get("alineados", False)),
                           "nota": "n deducido de len(escenarios). Alineacion del indice i entre rotaciones (mismo anio/precio/coste): pendiente de confirmar por enrique."}
        um = next((r["margen_eur_ha"].get("unidad") for r in rots if isinstance(r.get("margen_eur_ha"), dict) and r["margen_eur_ha"].get("unidad")), None)
        if um:
            escenarios_meta["unidad"] = um
        if not escenarios_meta["alineados"]:
            ctx.av("escenarios_meta.alineados = false: enrique confirmo (#138) que el indice i NO es hoy la misma muestra en todas las rotaciones; la UI no debe presentar 'B gana X %' como firme")
        ctx.ad("escenarios_meta {n, unidad} deducido de las muestras (sin semilla ni anio_clima: no existen en el origen)")
    elif longs:
        ctx.av(f"nº de escenarios distinto entre rotaciones {longs}: no se genera escenarios_meta")

    meta = {
        "aviso": aviso,
        "generado": d.get("generado"),
        "origen": origen,
        "adaptado_por": ADAPTADOR,
        "adaptado": hoy,
        "estado_bloques": estado_bloques,
        "bloques_pendientes": [],
        "adaptaciones": ctx.adaptaciones,
        "avisos": ctx.avisos,
    }
    meta = {k: v for k, v in meta.items() if v is not None}

    # orden de claves estable: primero las del contrato, luego los campos propios de enrique
    orden = ["schema_version", "_meta", "parcela", "historia", "ndvi", "clima", "suelo", "prioridades_defecto", "escenarios_meta",
             "rotaciones", "variantes", "sensores", "fuentes", "no_sustituye"]
    out = {"schema_version": SCHEMA_VERSION, "_meta": meta}
    d["fuentes"] = fuentes
    if escenarios_meta:
        d["escenarios_meta"] = escenarios_meta
    for k in orden[2:]:
        if k in d:
            out[k] = d.pop(k)
    for k, v in d.items():  # _estado_bloques, licencia, criterios_sentido, supuestos_decision, generado...
        out[k] = v
    return out


def historia_desde_objeto(h, ctx):
    """Borrador v1 {_status, cultivos_declarados[{campana, anio, cultivo, fuente}]} -> lista por anio con declaraciones 0..N."""
    por_anio = {}
    for c in h.get("cultivos_declarados", []):
        anio = c.get("anio", int(str(c["campana"])[:4]))
        por_anio.setdefault(anio, []).append(c)
    lista = []
    for anio in sorted(por_anio):
        cs = por_anio[anio]
        item = {"anio": anio, "cultivo": cs[0]["cultivo"], "fuente": cs[0].get("fuente", ""),
                "declaraciones": [{k: v for k, v in c.items() if k in ("campana", "anio", "cultivo", "fuente")} for c in cs]}
        if h.get("fuente_id"):
            item["fuente_id"] = h["fuente_id"]
        if len(cs) > 1:
            ctx.av(f"historia {anio}: {len(cs)} declaraciones; 'cultivo' toma la primera, las demas solo en declaraciones[]")
        lista.append(item)
    ctx.ad("historia objeto {_status, cultivos_declarados[]} -> lista por anio con declaraciones[] (estado en _meta.estado_bloques.historia)")
    return lista


def adapt_draft_v1(src, origen="research/contract-v1-draft/torre-pacheco.contract-v1.draft.json", hoy=None):
    """Adaptacion MINIMA del borrador v1 antiguo (solo para probar el validador v1.1). No toca los datos."""
    d = copy.deepcopy(src)
    ctx = Ctx()
    hoy = hoy or dt.date.today().isoformat()
    d["schema_version"] = SCHEMA_VERSION
    estado_bloques = {}
    if isinstance(d.get("historia"), dict):
        e, _, _ = norm_estado(d["historia"].get("_status"))
        d["historia"] = historia_desde_objeto(d["historia"], ctx)
        estado_bloques["historia"] = e or "simulado"
    for b in BLOQUES_DICT:
        if isinstance(d.get(b), dict) and norm_estado(d[b].get("_status"))[0]:
            estado_bloques[b] = d[b]["_status"]
    um = (d.get("_meta", {}).get("unidades") or {}).get("margen_eur_ha")
    for r in d.get("rotaciones", []):
        estado_bloques["rotaciones"] = r.get("_status", "simulado")
        if "escenarios_margen_eur_ha" in r:
            r["escenarios"] = r.pop("escenarios_margen_eur_ha")
        if isinstance(r.get("margen_eur_ha"), dict) and um and "unidad" not in r["margen_eur_ha"]:
            r["margen_eur_ha"]["unidad"] = um
        ad = r.get("agua_detalle")
        if isinstance(ad, dict) and isinstance(ad.get("bruto_m3_ha"), (int, float)):
            ad["bruto_m3_ha"] = {"p10": None, "p50": ad["bruto_m3_ha"], "p90": None}
        if isinstance(r.get("semaforo_legal"), dict):
            adapt_comprobaciones(r["semaforo_legal"], ctx, False)
    if ctx.transiciones:
        ctx.ad("semaforo_legal.comprobaciones[].resultado: " + ", ".join(sorted(ctx.transiciones)) + " (original en resultado_original)")
    ctx.ad("borrador v1 -> v1.1: schema_version, historia (lista), escenarios_margen_eur_ha -> escenarios, margen.unidad (de _meta.unidades), "
           "agua_detalle.bruto_m3_ha -> percentiles, vocabulario de comprobaciones")
    d["_meta"].update({"origen": origen, "adaptado_por": ADAPTADOR + " --formato draft-v1", "adaptado": hoy,
                       "estado_bloques": estado_bloques, "adaptaciones": ctx.adaptaciones, "avisos": ctx.avisos})
    return d


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("-o", "--salida", help="fichero de salida (por defecto stdout)")
    ap.add_argument("--formato", choices=["enrique", "draft-v1"], default="enrique")
    ap.add_argument("--origen", help="texto para _meta.origen (p. ej. rama y commit)")
    ap.add_argument("--hoy", help="fecha ISO para _meta.adaptado (por defecto, hoy; util para salida reproducible)")
    a = ap.parse_args()
    src = json.loads(Path(a.entrada).read_text(encoding="utf-8"))
    kw = {"hoy": a.hoy}
    if a.origen:
        kw["origen"] = a.origen
    out = (adapt_enrique if a.formato == "enrique" else adapt_draft_v1)(src, **kw)
    txt = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    if a.salida:
        Path(a.salida).write_text(txt, encoding="utf-8")
        print(f"escrito {a.salida} ({len(txt) // 1024} kB)", file=sys.stderr)
    else:
        sys.stdout.write(txt)
    for av in out["_meta"].get("avisos", []):
        print("AVISO:", av, file=sys.stderr)


if __name__ == "__main__":
    main()
