"""PUNTO DE EXTENSION del motor de rotaciones (enrique, T-012/T-020). Los endpoints NO cambian al enchufarlo.

Contrato interno (lo unico que `blocks.py` conoce del motor):

    class Engine:
        nombre: str
        def run(self, ctx: EngineInput) -> EngineOutput

`EngineOutput.rotaciones` ya en forma de contrato v1 (lista de rotaciones; el semaforo legal lo recalcula `blocks.py` con
legal.check(), el motor no tiene que producirlo) y `escenarios_meta` opcional. `EngineInput` lleva los bloques reales que la
API ya tiene (`parcela`, `clima`, `suelo`) para que el motor los lea en vez de los suyos mock.

Motores disponibles (los elige `get_engine(cfg)`):
  1. `DraftEngine` (por defecto): sirve las rotaciones del borrador de contrato. TODO `simulado`, igual para cualquier punto.
  2. `JsonFileEngine` (ENGINE_JSON=/ruta/torre-pacheco.json): lee el JSON precalculado de enrique (rama
     origin/t012-motor-nucleo, app/data/torre-pacheco.json) y lo convierte con `adapt_enrique()` (tabla abajo). Sirve el
     mismo resultado para cualquier punto: es la parcela demo. `_status` = lo que diga su `_estado_bloques.rotaciones`.
  3. FUTURO: `LiveEngine.run(ctx)` llamando a `run(parcela, clima, suelo)` de enrique, calculado por punto. Solo hay que
     implementar esa clase y devolverla en `get_engine`.

Conversion enrique -> contrato v1 (`adapt_enrique`), segun research/contract-v1-draft/DIFERENCIAS-con-torre-pacheco-json.md:
  - rotaciones[].escenarios            -> escenarios_margen_eur_ha
  - rotaciones[].plan_anios[].ciclos   -> rotaciones[].anios (lo lee legal.check para ciclos por anio)
  - rotaciones[]._status               <- _estado_bloques.rotaciones (`mock`/`provisional` -> `simulado`; resto igual)
  - rotaciones[].semaforo_legal        -> se descarta (blocks.py lo recalcula con legal.check)
  - escenarios_meta                    -> sintetizado {n, metodo} si el JSON no lo trae (el motor aun no exporta anio/beta/coste)
  - parcela, historia, ndvi, clima, suelo del JSON de enrique se IGNORAN: la API sirve los suyos (reales o borrador).
  Lo que sigue sin cumplir el esquema se mide en tests/test_engine_adapter.py (informativo, no bloquea).
"""
import copy
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Protocol

import settings

log = logging.getLogger("agrockham.engine")

ESTADO_MAPA = {"real": "real", "precalculado": "precalculado", "simulado": "simulado", "mock": "simulado",
               "provisional": "simulado", "pendiente": "simulado"}


@dataclass
class EngineInput:
    lat: float
    lon: float
    parcela: dict
    clima: Optional[dict] = None   # bloque real o None si no esta disponible
    suelo: Optional[dict] = None


@dataclass
class EngineOutput:
    rotaciones: list
    escenarios_meta: Optional[dict] = None
    motor: str = ""
    aviso: str = ""
    extra: dict = field(default_factory=dict)  # p. ej. {"variantes": ...} cuando enrique los exporte


class Engine(Protocol):
    nombre: str

    def run(self, ctx: EngineInput) -> EngineOutput: ...


# ------------------------------------------------------------------------------------------------ borrador
def cargar_json(ruta) -> dict:
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


class Borrador:
    """Contrato borrador (Torre-Pacheco, ilustrativo). Fuente de los bloques que aun no son reales: historia, ndvi, etc."""

    def __init__(self, ruta):
        self._doc = cargar_json(ruta)

    def copia(self) -> dict:
        return copy.deepcopy(self._doc)


class DraftEngine:
    nombre = "borrador (simulado)"

    def __init__(self, borrador: Borrador):
        self.borrador = borrador

    def run(self, ctx: EngineInput) -> EngineOutput:
        d = self.borrador.copia()
        return EngineOutput(
            rotaciones=d["rotaciones"], escenarios_meta=d.get("escenarios_meta"), motor=self.nombre,
            aviso="Rotaciones SIMULADAS (borrador de contrato, parcela demo), iguales para cualquier punto.")


# ------------------------------------------------------------------------------------------ JSON de enrique
def adapt_enrique(doc: dict) -> EngineOutput:
    """Convierte el JSON de enrique (rama t012-motor-nucleo) a rotaciones + escenarios_meta del contrato v1."""
    estado = ESTADO_MAPA.get((doc.get("_estado_bloques") or {}).get("rotaciones", "simulado"), "simulado")
    rots = []
    for r in doc.get("rotaciones", []):
        r = copy.deepcopy(r)
        r["_status"] = estado
        if "escenarios" in r:
            r["escenarios_margen_eur_ha"] = r.pop("escenarios") or []
        if not r.get("escenarios_margen_eur_ha"):
            r.pop("escenarios_margen_eur_ha", None)
        if r.get("plan_anios"):
            r["anios"] = [list(a.get("ciclos", [])) for a in r["plan_anios"]]
        r.pop("semaforo_legal", None)   # lo recalcula blocks.py con legal.check()
        rots.append(r)
    ns = {len(r["escenarios_margen_eur_ha"]) for r in rots if r.get("escenarios_margen_eur_ha")}
    meta = None
    if ns:
        meta = {"n": max(ns), "metodo": "motor T-012 de enrique (JSON precalculado; sin anio/beta/coste alineados)",
                "rotaciones_orden": [r["id"] for r in rots]}
        if doc.get("generado"):
            meta["generado"] = doc["generado"]
    return EngineOutput(
        rotaciones=rots, escenarios_meta=meta, motor="JSON de enrique (t012-motor-nucleo)",
        aviso=("Rotaciones del motor de enrique (JSON precalculado de la parcela demo), iguales para cualquier punto. "
               f"Estado declarado por el motor: {(doc.get('_estado_bloques') or {}).get('rotaciones', 'desconocido')}."),
        extra={"supuestos_decision": doc.get("supuestos_decision"), "licencia_motor": doc.get("licencia"),
               "criterios_sentido": doc.get("criterios_sentido")})


class JsonFileEngine:
    nombre = "JSON de enrique"

    def __init__(self, ruta):
        self.ruta = Path(ruta)
        self._out = adapt_enrique(cargar_json(self.ruta))  # falla al arrancar si el fichero no existe o no es JSON

    def run(self, ctx: EngineInput) -> EngineOutput:
        return copy.deepcopy(self._out)


def get_engine(cfg: settings.Settings, borrador: Borrador) -> Engine:
    """Elige el motor. Si ENGINE_JSON falla, se cae al borrador (la API no se rompe) y se avisa en el log."""
    if cfg.engine_json:
        try:
            return JsonFileEngine(cfg.engine_json)
        except (OSError, ValueError, KeyError) as exc:
            log.error("ENGINE_JSON=%s no se pudo cargar (%s): se usa el borrador simulado", cfg.engine_json, exc)
    return DraftEngine(borrador)
