"""Arma el contrato v1 por bloques de POST /analyze con datos reales donde ya existen.

parcela      -> ATOM del FEGA (app.backend.pipeline.atom.lookup)              _status "precalculado"
clima, suelo -> app.backend.pipeline.clima_suelo (cache por celda + red)  _status "real"
semaforo     -> app.backend.rules.check() por rotacion                    _status = el de la rotacion
rotaciones, historia, ndvi, escenarios_meta -> motor (engine_adapter.py) o contrato de ejemplo   _status "simulado"
Un bloque que no se puede dar sale `cargando` (valido segun el esquema) con `aviso`; el cliente sustituye los bloques
`cargando` por los que reciba despues.
"""
import copy
import time
from datetime import datetime, timezone
from typing import Iterable, Optional

from . import engine_adapter as EA
from . import legal_blocks, live, settings, store

BLOQUES = ("parcela", "historia", "ndvi", "clima", "suelo", "rotaciones")
LISTAS = ("historia", "rotaciones")   # bloques que son lista en v1.1: su estado va en _meta.estado_bloques / en cada rotacion
ACOMPANANTES = {"rotaciones": ("escenarios_meta",)}   # viajan con el bloque (la UI los necesita juntos)
COMPONENTES = store.COMPONENTES

SIGPAC_ID = "sigpac"
SIGPAC_FUENTE = {
    "id": SIGPAC_ID,
    "nombre": "SIGPAC: recintos (descarga oficial ATOM del FEGA, campana 2026, validez 2025-12-15)",
    "url": "https://www.fega.gob.es/atom/es.fega.sigpac.rec.2026.xml",
    "licencia": "CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/deed.es); datos transformados por Agrockham",
    "licencia_estado": "ok",
    "atribucion": store.ATRIBUCION_LARGA,
}


def consulta_id(lat: float, lon: float) -> str:
    """Id estable de una consulta (celda de ~1 m). Sirve para GET /parcel/{id}."""
    return f"q-{lat:.5f}_{lon:.5f}"


def _ref_dict(ref: str) -> dict:
    return dict(zip(COMPONENTES, (int(x) for x in ref.split("/"))))


class Servicio:
    """Estado de la API: configuracion, recintos ATOM, borrador y motor."""

    def __init__(self, cfg: settings.Settings, atom: store.Atom):
        self.cfg = cfg
        self.atom = atom
        self.borrador = EA.Borrador(cfg.contract_path)
        self.engine = EA.get_engine(cfg, self.borrador)
        live.preparar(cfg)

    # ------------------------------------------------------------------------------------------ parcela
    def _parcela(self, lat: float, lon: float, recinto: Optional[dict]) -> tuple[dict, list[str], dict]:
        """(bloque parcela, avisos, info) con info = {encontrado, ref, coincide}."""
        avisos: list[str] = []
        info = {"encontrado": False}
        if not self.atom.cargado:
            avisos.append("Recintos SIGPAC no cargados en este servidor: no hay datos de parcela.")
            return ({"_status": "cargando", "sin_cobertura": True, "aviso": avisos[0]}, avisos, info)
        p = self.atom.index.recinto_por_punto(lat, lon, detalle=True)
        if p is None:
            if self.atom.en_cobertura(lat, lon):
                msg = ("El punto no cae en ningun recinto SIGPAC cargado (camino, edificio, agua o municipio aun no cargado). "
                       "Haz clic dentro de un recinto dibujado.")
            else:
                msg = ("Punto fuera de los municipios con recintos cargados (" + ", ".join(self.atom.nombres()) + "): "
                       "cobertura basica, sin datos de parcela SIGPAC.")
            avisos.append(msg)
            return {"_status": "cargando", "sin_cobertura": True, "aviso": msg}, avisos, info
        ref = _ref_dict(p["ref"])
        p["sigpac"] = ref  # los 7 componentes (el ATOM da poligono/parcela/recinto en `sigpac`; aqui completo)
        info = {"encontrado": True, "ref": ref}
        if recinto:
            dif = [k for k, v in recinto.items() if k in ref and ref[k] != v]
            info["coincide"] = not dif
            if dif:
                avisos.append("El recinto indicado no coincide con el que contiene el punto en: " + ", ".join(dif)
                              + ". Se devuelve el recinto del punto.")
        return p, avisos, info

    # ------------------------------------------------------------------------------------------ fuentes
    @staticmethod
    def _fuentes(base: dict, del_motor: Optional[list] = None) -> list[dict]:
        fuentes = [f for f in base["fuentes"] if f["id"] != SIGPAC_ID]
        fuentes.append(copy.deepcopy(SIGPAC_FUENTE))
        ids = {f["id"] for f in fuentes}
        for f in list(live.fuentes_nuevas()) + list(del_motor or []):   # las del motor van las ultimas: no pisan a las reales
            if f["id"] not in ids:
                fuentes.append(copy.deepcopy(f))
                ids.add(f["id"])
        return fuentes

    # ------------------------------------------------------------------------------------------ analizar
    def construir(self, lat: float, lon: float, recinto: Optional[dict] = None, zona: str = "por_verificar",
                  bloques: Optional[Iterable[str]] = None) -> dict:
        t_total = time.perf_counter()
        pedidos = list(BLOQUES) if bloques is None else list(bloques)
        malos = [b for b in pedidos if b not in BLOQUES]
        if malos:
            raise ValueError(f"bloques desconocidos: {malos}; validos: {list(BLOQUES)}")
        lat_ms: dict[str, float] = {}
        base = self.borrador.copia()

        # clima y suelo en paralelo (lo mas lento: red si la celda no esta en cache)
        futs = {n: live.lanzar(n, lat, lon) for n in ("clima", "suelo") if n in pedidos}
        t0 = time.perf_counter()

        t = time.perf_counter()
        parcela, avisos, info = self._parcela(lat, lon, recinto)
        lat_ms["parcela"] = (time.perf_counter() - t) * 1000
        tiene_parcela = info["encontrado"]

        doc: dict = {"schema_version": base["schema_version"], "_meta": base["_meta"]}
        doc["parcela"] = parcela if "parcela" in pedidos else {"_status": "cargando"}
        doc["historia"] = base["historia"] if "historia" in pedidos else []
        doc["ndvi"] = base["ndvi"] if "ndvi" in pedidos else {"_status": "cargando"}
        reales: dict[str, Optional[dict]] = {"clima": None, "suelo": None}
        for n, fut in futs.items():
            bloque, aviso = live.recoger(n, fut, self.cfg)
            lat_ms[n] = (time.perf_counter() - t0) * 1000  # desde el lanzamiento: incluye la espera en paralelo
            doc[n] = bloque
            reales[n] = bloque if bloque["_status"] != "cargando" else None
            if aviso:
                avisos.append(aviso)
        for n in ("clima", "suelo"):
            if n not in pedidos:
                doc[n] = {"_status": "cargando"}

        motor_aviso = ""
        fuentes_motor: list = []
        doc["rotaciones"] = []
        if "rotaciones" in pedidos:
            t = time.perf_counter()
            out = self.engine.run(EA.EngineInput(lat, lon, parcela if tiene_parcela else {}, reales["clima"], reales["suelo"]))
            nivel_legal = "completo" if tiene_parcela else "basico"  # sin recinto no se evalua la ley (semaforo gris)
            ndvi = base["ndvi"]
            doc["rotaciones"] = legal_blocks.aplicar(out.rotaciones, parcela if tiene_parcela else {}, ndvi, nivel_legal, zona)
            if out.escenarios_meta:
                doc["escenarios_meta"] = out.escenarios_meta
            motor_aviso = out.aviso
            fuentes_motor = out.fuentes
            lat_ms["rotaciones"] = (time.perf_counter() - t) * 1000
        doc["prioridades_defecto"] = base["prioridades_defecto"]
        doc["fuentes"] = self._fuentes(base, fuentes_motor)
        doc["no_sustituye"] = base["no_sustituye"]

        # ------------------------------------------------------------------------------------------ _meta
        meta = doc["_meta"]
        meta["generador"] = "app/backend/api (API en vivo: ATOM + pipeline clima/suelo + reglas legales + motor)"
        meta["cobertura"] = self._cobertura(tiene_parcela)
        estados = {b: _estado(doc, b, base) for b in BLOQUES}
        simulados = [b for b, s in estados.items() if s == "simulado"]
        meta["estado_bloques"] = estados
        if simulados:
            meta["aviso"] = (f"MOCK PARCIAL: los bloques simulados ({', '.join(simulados)}) NO corresponden al punto consultado "
                             f"(son del borrador Torre-Pacheco). {motor_aviso or ''} Referencia del borrador: {base['_meta']['aviso']}").strip()
        else:
            meta["aviso"] = "Todos los bloques servidos proceden de datos reales o precalculados del punto (ver estado_bloques)."
        meta["aviso_legal"] = legal_blocks.L.NOTA
        meta["consulta"] = {"lat": lat, "lon": lon, "zona_legal": zona, **self._consulta_recinto(recinto, info)}
        meta["consulta_id"] = consulta_id(lat, lon)
        meta["generado_en"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        meta["motor"] = getattr(self.engine, "nombre", "?")
        meta["latencia_ms"] = {**{k: round(v, 1) for k, v in lat_ms.items()},
                               "total": round((time.perf_counter() - t_total) * 1000, 1)}
        if tiene_parcela:
            meta["atribuciones"] = [store.ATRIBUCION_LARGA]
        if not (lat >= settings.BBOX_ESPANA_PENINSULAR[1] and lat <= settings.BBOX_ESPANA_PENINSULAR[3]
                and settings.BBOX_ESPANA_PENINSULAR[0] <= lon <= settings.BBOX_ESPANA_PENINSULAR[2]):
            avisos.append("Punto fuera de Espana peninsular: SIGPAC no cubre esta zona.")
        if avisos:
            meta["avisos"] = avisos
        _marcar_pendientes(doc)
        return doc

    def _cobertura(self, tiene_parcela: bool) -> dict:
        if tiene_parcela:
            return {"nivel": "completo", "ambito": "SIGPAC por municipio (D-009): " + ", ".join(self.atom.nombres())}
        return {"nivel": "basico", "ambito": "Sin recinto SIGPAC en el punto: nivel basico/indicativo (clima y suelo globales, semaforo legal en gris)"}

    @staticmethod
    def _consulta_recinto(recinto: Optional[dict], info: dict) -> dict:
        """`recinto` solo con los componentes enviados (ausente = no enviado; 0 solo si vino 0). recinto_completo = los 7."""
        out: dict = {}
        if recinto is not None:
            out["recinto"] = dict(recinto)
        out["recinto_completo"] = bool(recinto) and all(k in recinto for k in COMPONENTES)
        if "coincide" in info:
            out["recinto_coincide"] = info["coincide"]
        return out


# ---------------------------------------------------------------------------------------------- pendientes y fusion
def _estado(doc: dict, b: str, base: Optional[dict] = None) -> str:
    """`_status` de un bloque. historia (lista) toma el estado del ejemplo base si va cargada; rotaciones, el de su 1.a rotacion."""
    if b == "historia":
        return ((base or {}).get("_meta", {}).get("estado_bloques", {}).get("historia", "simulado")) if doc[b] else "cargando"
    if b == "rotaciones":
        return doc[b][0]["_status"] if doc[b] else "cargando"
    return doc[b]["_status"]


def _vacio(doc: dict, b: str) -> bool:
    return (not doc.get(b)) if b in LISTAS else doc[b].get("_status") == "cargando"


def _sin_datos(bloque) -> bool:
    return isinstance(bloque, dict) and bool(bloque.get("sin_cobertura") or bloque.get("sin_datos"))


def _marcar_pendientes(doc: dict) -> None:
    """`bloques_pendientes` = aun en carga y que pueden llegar; `bloques_sin_datos` = vacios y no van a llegar."""
    pend, sin = [], []
    for b in BLOQUES:
        v = doc.get(b)
        if not _vacio(doc, b):
            continue
        (sin if _sin_datos(v) else pend).append(b)
    doc["_meta"]["bloques_pendientes"] = pend
    if sin:
        doc["_meta"]["bloques_sin_datos"] = sin
    else:
        doc["_meta"].pop("bloques_sin_datos", None)


def fusionar(previo: Optional[dict], nuevo: dict) -> dict:
    """Contrato guardado: lo ya cargado de la misma consulta no se pierde cuando llega una peticion con otros bloques."""
    if not previo or previo.get("_meta", {}).get("consulta_id") != nuevo["_meta"].get("consulta_id"):
        return nuevo
    out = copy.deepcopy(nuevo)
    estados = dict(out["_meta"].get("estado_bloques", {}))
    for b in BLOQUES:
        antes = previo.get(b) and (b in LISTAS or previo[b].get("_status") != "cargando")
        if antes and _vacio(out, b):
            out[b] = copy.deepcopy(previo[b])
            estados[b] = previo.get("_meta", {}).get("estado_bloques", {}).get(b) or _estado(previo, b)
            for extra in ACOMPANANTES.get(b, ()):
                if extra in previo:
                    out[extra] = copy.deepcopy(previo[extra])
    out["_meta"]["estado_bloques"] = estados
    _marcar_pendientes(out)
    return out


def id_parcela(doc: dict) -> Optional[str]:
    p = doc.get("parcela", {})
    return p.get("id") if p.get("_status") != "cargando" else None
