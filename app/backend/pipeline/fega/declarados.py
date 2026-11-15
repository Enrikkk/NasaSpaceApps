"""Cultivos declarados (FEGA, SIGPAC `cultivo_declarado`, campana en uso) de un recinto: 0..N registros, con cache.

Fuente: OGC API de SIGPAC (sigpac-hubcloud.es), cubierta por los Terminos de uso de la informacion de alto valor del SIGC del FEGA
(CC BY 4.0; atribucion "Fuente de los datos: FONDO ESPAÑOL DE GARANTÍA AGRARIA O.A."). La capa lleva la declaracion PAC de la
campana en uso; el ATOM del FEGA trae la campana anterior (no se usa aqui).

Reglas:
- Un recinto puede tener 0, 1 o varios registros (varias explotaciones, doble cultivo, registros sin producto): se conservan todos,
  no se asume uno solo.
- NO se copian los identificadores de explotacion (exp_num, exp_ca...): son datos de la explotacion/agricultor y no hacen falta.
- Sin red (AGROCKHAM_OFFLINE=1) o si falla la API: se sirve la cache si existe; si no, `None` (el llamador degrada a "cargando").
- Los codigos de producto se traducen con `cod_producto.csv` (FEGA); `parc_producto` es la columna `codigo` de esa tabla.
"""
import csv
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://sigpac-hubcloud.es/ogcapi/collections/cultivo_declarado/items"
UA = {"User-Agent": "agrockham-hackathon/0.1 (educational)", "Accept-Encoding": "gzip"}
ATRIBUCION = "Fuente de los datos: FONDO ESPAÑOL DE GARANTÍA AGRARIA O.A."
_TABLA = Path(__file__).with_name("cod_producto.csv")
_PRODUCTOS = None


def productos():
    """{codigo(int): descripcion} desde cod_producto.csv."""
    global _PRODUCTOS
    if _PRODUCTOS is None:
        with open(_TABLA, encoding="utf-8", newline="") as f:
            _PRODUCTOS = {int(r["codigo"]): r["descripcion"] for r in csv.DictReader(f)}
    return _PRODUCTOS


def nombre_producto(cod):
    if cod is None:
        return None
    return productos().get(int(cod), f"PRODUCTO {int(cod)}")


CLAVES = ("provincia", "municipio", "agregado", "zona", "poligono", "parcela", "recinto")


def _clave(props):
    return tuple(int(props.get(k, 0) or 0) for k in CLAVES)


def normalizar(features, clave_recinto=None):
    """features OGC -> registros normalizados del recinto (si se da `clave_recinto`, solo los que coinciden)."""
    out = []
    for ft in features:
        p = ft.get("properties", {})
        if clave_recinto is not None and _clave(p) != tuple(clave_recinto):
            continue
        sup = p.get("parc_supcult")
        out.append({
            "producto_codigo": p.get("parc_producto"),
            "producto": nombre_producto(p.get("parc_producto")),
            "sistema_explotacion": p.get("parc_sistexp"),          # R regadio, S secano (codigo FEGA)
            "superficie_cultivada_ha": round(sup / 10000, 4) if isinstance(sup, (int, float)) else None,
            "cultivo_secundario_codigo": p.get("cultsecun_producto"),
            "cultivo_secundario": nombre_producto(p.get("cultsecun_producto")),
            "ayuda_solicitada": p.get("parc_ayudasol"),
            "indicador_cultivo_aprovechamiento": p.get("parc_indcultapro"),
            "tipo_aprovechamiento": p.get("tipo_aprovecha"),
        })
    return out


def _cache_file(cache_dir, clave):
    return Path(cache_dir) / "fega" / ("-".join(str(x) for x in clave) + ".json")


def buscar(lat, lon, clave_recinto, cache_dir, timeout=15, offline=None, abrir=urllib.request.urlopen):
    """-> dict {registros, campania, descargado, fuente, url, atribucion, de_cache} o None si no hay cache ni red."""
    clave = tuple(int(x) for x in clave_recinto)
    cf = _cache_file(cache_dir, clave)
    if cf.is_file():
        d = json.loads(cf.read_text(encoding="utf-8"))
        d["de_cache"] = True
        return d
    if offline is None:
        offline = os.environ.get("AGROCKHAM_OFFLINE") == "1"
    if offline:
        return None
    e = 0.0002
    url = BASE + "?" + urllib.parse.urlencode({"f": "json", "limit": 50, "bbox": f"{lon - e},{lat - e},{lon + e},{lat + e}"})
    try:
        with abrir(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
            raw = r.read()
        if raw[:2] == b"\x1f\x8b":
            import gzip
            raw = gzip.decompress(raw)
        feats = json.loads(raw).get("features", [])
    except Exception:
        return None
    d = {
        "registros": normalizar(feats, clave),
        "campania": "en uso",
        "descargado": time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()),
        "fuente": "FEGA, SIGPAC cultivo_declarado (OGC API, campana en uso)",
        "url": url, "atribucion": ATRIBUCION, "de_cache": False,
    }
    try:
        cf.parent.mkdir(parents=True, exist_ok=True)
        cf.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass
    return d


def cultivo_principal(registros):
    """Cultivo principal para `historia`: el primer registro con producto distinto de desconocido (0); None si no hay."""
    for r in registros:
        if r.get("producto_codigo") not in (None, 0):
            return r["producto"]
    return None
