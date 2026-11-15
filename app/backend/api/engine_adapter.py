"""PUNTO DE EXTENSION del motor de rotaciones (enrique, T-012/T-020). Los endpoints NO cambian al enchufarlo.

Contrato interno (lo unico que `blocks.py` conoce del motor):

    class Engine:
        nombre: str
        def run(self, ctx: EngineInput) -> EngineOutput

`EngineOutput.rotaciones` ya en forma de contrato v1.1 (lista de rotaciones; el semaforo legal lo recalcula `blocks.py` con
app.backend.rules.check(), el motor no tiene que producirlo), `escenarios_meta` opcional y `fuentes` extra (las que citan
sus rotaciones). `EngineInput` lleva los bloques reales que la API ya tiene (`parcela`, `clima`, `suelo`) para que el motor
los lea en vez de los suyos mock.

Motores disponibles (los elige `get_engine(cfg, borrador)`):
  1. `DraftEngine` (por defecto): sirve las rotaciones del contrato de ejemplo (app/data/torre-pacheco.contract.example.json).
     TODO `simulado`, igual para cualquier punto.
  2. `JsonFileEngine` (ENGINE_JSON=/ruta/torre-pacheco.json): lee el JSON precalculado de enrique (rama t012-motor-nucleo,
     app/data/torre-pacheco.json) y lo convierte con `app/data/contract/adapt_enrique.py` (v1.1, no se duplica aqui). Sirve el
     mismo resultado para cualquier punto: es la parcela demo. `_status` = lo que diga su `_estado_bloques.rotaciones`.
  3. `LiveEngine` (ENGINE_MODE=vivo; enrique, H-002): llama a `app.backend.engine.build.run_parcel(parcel_input)` en cada
     consulta (~0,8 s, sin red: solo lee tablas del repo). `parcel_input` = `parcel_input.construir(ctx)`. Precios abiertos
     por defecto; CARM solo con ENGINE_PRECIOS=carm explicito (D-010). Si el motor falla, cae al motor anterior (JSON o
     ejemplo) y lo dice en `extra["avisos"]` (blocks.py lo pasa a `_meta.avisos`). `extra` lleva ademas los bloques por
     parcela: `idoneidad`, `clima_origen`, `no_evaluable`, `actual_origen` y `por_parcela: True`.

De lo que devuelve `adapt_enrique` solo se usan `rotaciones`, `escenarios_meta` y `fuentes`; sus `parcela/historia/ndvi/clima/suelo`
se IGNORAN (la API sirve los suyos, reales o del ejemplo) y su `semaforo_legal` se descarta (se recalcula).
`escenarios_meta.alineados` se respeta tal cual lo declara el motor y es `false` mientras enrique no lo declare (D-011): la
UI no debe presentar "B gana X %" como firme.
"""
import copy
import importlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Protocol

from . import settings

log = logging.getLogger("agrockham.engine")


@dataclass
class EngineInput:
    lat: float
    lon: float
    parcela: dict
    clima: Optional[dict] = None   # bloque real o None si no esta disponible
    suelo: Optional[dict] = None
    zona: str = "por_verificar"            # zona legal (Ley 3/2020) que pasa el cliente; nunca se afirma sin verificar
    historia: Optional[list] = None        # bloque historia (cultivos declarados FEGA, 0..N) si es real


@dataclass
class EngineOutput:
    rotaciones: list
    escenarios_meta: Optional[dict] = None
    motor: str = ""
    aviso: str = ""
    fuentes: list = field(default_factory=list)   # fuentes que citan las rotaciones y que el ejemplo base puede no traer
    extra: dict = field(default_factory=dict)     # p. ej. {"variantes": ...} cuando enrique los exporte


class Engine(Protocol):
    nombre: str

    def run(self, ctx: EngineInput) -> EngineOutput: ...


# ------------------------------------------------------------------------------------------------ contrato de ejemplo
def cargar_json(ruta) -> dict:
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


class Borrador:
    """Contrato de ejemplo (MOCK, Torre-Pacheco). Fuente de los bloques que aun no son reales: historia, ndvi, etc."""

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
            aviso="Rotaciones SIMULADAS (contrato de ejemplo, parcela demo), iguales para cualquier punto.")


# ------------------------------------------------------------------------------------------ JSON de enrique
def _adaptador():
    """`app/data/contract/adapt_enrique.py` (v1.1). Import perezoso: solo hace falta si se usa ENGINE_JSON."""
    return importlib.import_module("app.data.contract.adapt_enrique")


def adapt_enrique(doc: dict, origen: str = "ENGINE_JSON") -> EngineOutput:
    """JSON de enrique (rama t012-motor-nucleo) -> rotaciones + escenarios_meta + fuentes, con el adaptador v1.1."""
    contrato = _adaptador().adapt_enrique(doc, origen=origen)
    rots = []
    for r in contrato.get("rotaciones", []):
        r = copy.deepcopy(r)
        r.pop("semaforo_legal", None)   # lo recalcula blocks.py con app.backend.rules.check()
        if r.get("escenarios") is not None:
            r.pop("escenarios_meta", None)
            r.pop("escenarios_margen_eur_ha", None)   # nombre antiguo (v1): duplicaria el payload
        rots.append(r)
    meta = copy.deepcopy(contrato.get("escenarios_meta"))
    if meta is not None:
        meta["alineados"] = bool(meta.get("alineados", False))   # false hasta que enrique lo declare (D-011)
    estado = (contrato.get("_meta") or {}).get("estado_bloques", {}).get("rotaciones", "desconocido")
    return EngineOutput(
        rotaciones=rots, escenarios_meta=meta, motor="JSON de enrique (t012-motor-nucleo)",
        aviso=("Rotaciones del motor de enrique (JSON precalculado de la parcela demo), iguales para cualquier punto. "
               f"Estado declarado por el motor: {estado}."),
        fuentes=copy.deepcopy(contrato.get("fuentes", [])),
        extra={"supuestos_decision": contrato.get("supuestos_decision"), "licencia_motor": contrato.get("licencia"),
               "criterios_sentido": contrato.get("criterios_sentido"),
               "avisos_adaptador": (contrato.get("_meta") or {}).get("avisos", [])})


class JsonFileEngine:
    nombre = "JSON de enrique"

    def __init__(self, ruta):
        self.ruta = Path(ruta)
        self._out = adapt_enrique(cargar_json(self.ruta), origen=f"ENGINE_JSON={self.ruta.name}")   # falla al arrancar si no carga

    def run(self, ctx: EngineInput) -> EngineOutput:
        return copy.deepcopy(self._out)


# ------------------------------------------------------------------------------------------ motor en vivo por parcela
class LiveEngine:
    """Motor de enrique calculado para la parcela de la consulta (H-002). Sin red. Ver la cabecera del modulo."""
    nombre = "motor en vivo por parcela (enrique, H-002)"

    def __init__(self, respaldo: Engine, precios: str = "abierto"):
        self.respaldo = respaldo
        self.con_carm = precios == "carm"          # solo con ENGINE_PRECIOS=carm explicito
        self._build = importlib.import_module("app.backend.engine.build")   # falla al arrancar si el motor no esta

    def run(self, ctx: EngineInput) -> EngineOutput:
        from . import parcel_input
        try:
            pi = parcel_input.construir(ctx)
            pi.pop("sin_dato", None)               # el motor calcula su propia lista de datos que faltan
            doc = self._build.run_parcel(pi, allow_restricted=self.con_carm)
            extra = {k: doc.get(k) for k in ("idoneidad", "clima_origen", "no_evaluable", "actual_origen")}
            out = adapt_enrique(doc, origen="motor en vivo (run_parcel)")
        except Exception as exc:                    # el motor nunca tumba la API: motor anterior + aviso
            log.error("motor en vivo fallo (%r): se usa el motor de respaldo", exc)
            out = self.respaldo.run(ctx)
            out.extra = {**(out.extra or {}), "avisos": [
                "El cálculo en vivo para esta parcela ha fallado: se muestran las rotaciones de la parcela de referencia."]}
            return out
        out.motor = self.nombre
        out.aviso = ("Rotaciones calculadas en vivo para esta parcela: idoneidad (regadío, pendiente, suelo), zona legal y "
                     "cultivo declarado. El clima es el de la estación SIAM de Torre-Pacheco para cualquier punto. Precios: "
                     + ("CARM (permiso pendiente)." if self.con_carm else "abiertos (MAPA nacional como proxy y Eurostat)."))
        out.extra = {**(out.extra or {}), **extra, "por_parcela": True}
        return out


def get_engine(cfg: settings.Settings, borrador: Borrador) -> Engine:
    """Elige el motor. Si ENGINE_JSON falla, se cae al ejemplo (la API no se rompe) y se avisa en el log.
    ENGINE_MODE=vivo envuelve al anterior con LiveEngine (motor por parcela); si no carga, se queda el anterior."""
    base: Engine = DraftEngine(borrador)
    if cfg.engine_json:
        try:
            base = JsonFileEngine(cfg.engine_json)
        except (OSError, ValueError, KeyError, TypeError, AttributeError, ImportError) as exc:
            log.error("ENGINE_JSON=%s no se pudo cargar (%r): se usa el contrato de ejemplo simulado", cfg.engine_json, exc)
    if getattr(cfg, "engine_mode", "") == "vivo":
        try:
            return LiveEngine(base, getattr(cfg, "engine_precios", "abierto"))
        except Exception as exc:
            log.error("ENGINE_MODE=vivo pero el motor no carga (%r): se usa %s", exc, getattr(base, "nombre", "?"))
    return base
