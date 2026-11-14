"""Carga el contrato v1 borrador y arma la respuesta por bloques de POST /analyze.

STUB: los bloques que servimos salen del JSON borrador (Torre-Pacheco, valores ilustrativos, `_status: "simulado"`).
Los demas salen `cargando` y vacios pero validos segun contract.schema.json. Nada de esto es dato real.
"""
import copy
import json
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import settings

# Bloques de primer nivel que el cliente puede pedir con ?bloques=
BLOQUES = ("parcela", "historia", "ndvi", "clima", "suelo", "rotaciones")
# Bloques que el stub sabe servir desde el borrador. ndvi (Enrique, T-013) aun no existe: siempre "cargando".
SERVIDOS = ("parcela", "historia", "clima", "suelo", "rotaciones")
# Bloques adicionales que viajan con "rotaciones" (la UI los necesita juntos).
ACOMPANANTES = {"rotaciones": ("escenarios_meta",)}

AVISO_STUB = (
    "MOCK (STUB DE API, sin datos reales): los bloques con _status 'simulado' son los del borrador Torre-Pacheco "
    "y NO corresponden al punto consultado. "
)


@lru_cache(maxsize=4)
def _borrador(ruta: str) -> dict:
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def cargar_borrador(ruta: Path | None = None) -> dict:
    """Copia profunda del borrador (el llamador puede mutarla)."""
    ruta = ruta or settings.get_settings().contract_path
    return copy.deepcopy(_borrador(str(ruta)))


def _vacio(nombre: str):
    """Bloque `cargando` valido: dict con solo _status, o lista vacia para rotaciones."""
    return [] if nombre == "rotaciones" else {"_status": "cargando"}


def consulta_id(lat: float, lon: float) -> str:
    """Id estable de una consulta (celda de ~1 m). Sirve para GET /parcel/{id}."""
    return f"q-{lat:.5f}_{lon:.5f}"


def cobertura(lat: float, lon: float) -> tuple[dict, list[str]]:
    """(cobertura, avisos) segun el punto. 'completo' solo dentro de la bbox del Campo de Cartagena."""
    lon0, lat0, lon1, lat1 = settings.BBOX_CAMPO_CARTAGENA
    avisos: list[str] = []
    if lon0 <= lon <= lon1 and lat0 <= lat <= lat1:
        return {"nivel": "completo", "ambito": "Campo de Cartagena (por municipio, D-009)"}, avisos
    avisos.append(
        "Punto fuera del Campo de Cartagena: cobertura 'basico' (parcela, clima, suelo y reglas nacionales). "
        "Las rotaciones serian solo indicativas, sin normativa autonomica ni precios locales."
    )
    elon0, elat0, elon1, elat1 = settings.BBOX_ESPANA_PENINSULAR
    if not (elon0 <= lon <= elon1 and elat0 <= lat <= elat1):
        avisos.append("Punto fuera de Espana peninsular: SIGPAC no cubre esta zona, no habra datos de parcela reales.")
    return {"nivel": "basico", "ambito": "Fuera del Campo de Cartagena: nivel basico/indicativo"}, avisos


def _pendientes(doc: dict) -> list[str]:
    """Bloques aun en carga, en el orden canonico."""
    pend = []
    for b in BLOQUES:
        v = doc.get(b)
        if b == "rotaciones":
            if not v:
                pend.append(b)
        elif not v or v.get("_status") == "cargando":
            pend.append(b)
    return pend


def construir(lat: float, lon: float, recinto=None, bloques=None) -> dict:
    """Arma el contrato. `bloques`: iterable de nombres a rellenar (None = todos los servibles).

    Los bloques no pedidos o no disponibles salen como `cargando`; asi la respuesta siempre valida contra el
    esquema y el cliente solo tiene que sustituir los bloques `cargando` por los que reciba despues.
    """
    pedidos = list(BLOQUES) if bloques is None else list(bloques)
    desconocidos = [b for b in pedidos if b not in BLOQUES]
    if desconocidos:
        raise ValueError(f"bloques desconocidos: {desconocidos}; validos: {list(BLOQUES)}")

    base = cargar_borrador()
    doc: dict = {"schema_version": base["schema_version"], "_meta": base["_meta"]}
    servidos = [b for b in pedidos if b in SERVIDOS]
    for b in BLOQUES:
        doc[b] = copy.deepcopy(base[b]) if b in servidos else _vacio(b)
    for b in servidos:
        for extra in ACOMPANANTES.get(b, ()):
            if extra in base:
                doc[extra] = base[extra]
    doc["prioridades_defecto"] = base["prioridades_defecto"]
    doc["fuentes"] = base["fuentes"]
    doc["no_sustituye"] = base["no_sustituye"]

    cob, avisos = cobertura(lat, lon)
    meta = doc["_meta"]
    meta["aviso"] = AVISO_STUB + meta["aviso"]
    meta["stub"] = True
    meta["cobertura"] = cob
    meta["bloques_pendientes"] = _pendientes(doc)
    meta["consulta"] = {"lat": lat, "lon": lon, "recinto": recinto}
    meta["consulta_id"] = consulta_id(lat, lon)
    meta["generado_en"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if avisos:
        meta["avisos"] = avisos
    return doc


def fusionar(previo: dict | None, nuevo: dict) -> dict:
    """Contrato guardado: lo ya cargado no se pierde cuando llega una peticion posterior con otros bloques.

    Un bloque `cargando` en `nuevo` se sustituye por el cargado de `previo` (si es de la misma consulta).
    """
    if not previo or previo.get("_meta", {}).get("consulta_id") != nuevo["_meta"].get("consulta_id"):
        return nuevo
    out = copy.deepcopy(nuevo)
    for b in BLOQUES:
        cargado_antes = previo.get(b) and (b == "rotaciones" or previo[b].get("_status") != "cargando")
        sigue_vacio = not out.get(b) if b == "rotaciones" else out[b].get("_status") == "cargando"
        if cargado_antes and sigue_vacio:
            out[b] = copy.deepcopy(previo[b])
            for extra in ACOMPANANTES.get(b, ()):
                if extra in previo:
                    out[extra] = copy.deepcopy(previo[extra])
    out["_meta"]["bloques_pendientes"] = _pendientes(out)
    return out


def id_parcela(doc: dict) -> str | None:
    p = doc.get("parcela", {})
    return p.get("id") if p.get("_status") != "cargando" else None
