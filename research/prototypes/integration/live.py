"""Bloques `clima` y `suelo` reales (cache por celda; red en vivo con limites) sobre vendor/pipeline.py.

- La cache de ejecucion vive en `cfg.pipeline_cache_dir` y se siembra con `data/pipeline_cache/` (parcela demo).
- Si la celda no esta en cache y hay red, se llama al pipeline (POWER x2, Open-Meteo, SoilGrids) con los limites ya
  implementados en el (SoilGrids 5 llamadas/min entre procesos, reintentos) pero con timeout y reintentos acotados
  para una API en vivo (LIVE_HTTP_TIMEOUT_S, LIVE_RETRIES) y un plazo total por bloque (LIVE_DEADLINE_S).
- Si el plazo vence, el bloque sale `cargando` y el hilo sigue descargando: la siguiente peticion ya encuentra la cache.
- `AGROCKHAM_OFFLINE=1` (variable del propio pipeline) prohibe la red: sin cache -> bloque `cargando` con aviso.
- Nunca lanza hacia el endpoint: devuelve (bloque, aviso|None).
"""
import logging
import shutil
import threading
from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError as FutureTimeout
from pathlib import Path
from typing import Optional

from vendor import pipeline as P

import settings

log = logging.getLogger("agrockham.live")

SEMILLA = Path(__file__).resolve().parent / "data" / "pipeline_cache"
_EXEC = ThreadPoolExecutor(max_workers=8, thread_name_prefix="live")
_LOCKS = {"clima": threading.Lock(), "suelo": threading.Lock()}  # una descarga a la vez por tipo de bloque


def preparar(cfg: settings.Settings) -> None:
    """Fija el directorio de cache, lo siembra con la parcela demo y acota reintentos/timeout de la red en vivo."""
    cfg.pipeline_cache_dir.mkdir(parents=True, exist_ok=True)
    P.CACHE_DIR = cfg.pipeline_cache_dir
    for f in SEMILLA.glob("*.json"):
        destino = cfg.pipeline_cache_dir / f.name
        if not destino.exists():
            shutil.copyfile(f, destino)
    # http_get_json(url, timeout, retries, backoff, host_key): los valores por defecto (120 s, 4 reintentos, hasta
    # 130 s de esperas) son para un script; en una API se acotan sin tocar el codigo del pipeline.
    P.http_get_json.__defaults__ = (cfg.live_http_timeout_s, cfg.live_retries, (5, 10), None)


def _vacio(motivo: str, **extra) -> dict:
    return {"_status": "cargando", "aviso": motivo, **extra}


def _construir(nombre: str, lat: float, lon: float) -> dict:
    fn = P.build_clima if nombre == "clima" else P.build_suelo
    with _LOCKS[nombre]:
        return fn(lat, lon)


def lanzar(nombre: str, lat: float, lon: float) -> Future:
    return _EXEC.submit(_construir, nombre, lat, lon)


def recoger(nombre: str, fut: Future, cfg: settings.Settings) -> tuple[dict, Optional[str]]:
    """Espera el futuro (plazo LIVE_DEADLINE_S) y devuelve (bloque, aviso)."""
    try:
        bloque = fut.result(timeout=cfg.live_deadline_s)
    except FutureTimeout:
        msg = (f"{nombre}: la descarga supera {cfg.live_deadline_s:.0f} s; sigue en segundo plano. "
               "Vuelve a pedir este bloque en unos segundos (saldra de la cache).")
        return _vacio(msg), msg
    except P.RedBloqueada:
        msg = f"{nombre}: sin datos en cache para esta celda y la red esta desactivada (AGROCKHAM_OFFLINE=1)."
        return _vacio(msg), msg
    except ValueError as exc:  # SoilGrids sin datos (mar, urbano...)
        log.info("%s sin datos en el punto: %s", nombre, exc)
        msg = f"{nombre}: sin datos en este punto (agua, urbano o fuera de la rejilla)."
        return _vacio(msg, sin_datos=True), msg
    except Exception as exc:  # red caida, API upstream rota...: el endpoint no debe tumbarse ni filtrar detalles
        log.warning("%s fallo en vivo: %r", nombre, exc)
        msg = f"{nombre}: no se pudo obtener ahora (servicio externo no disponible). Reintenta en un minuto."
        return _vacio(msg), msg
    return bloque, None


def fuentes_nuevas() -> list[dict]:
    return P.fuentes_nuevas()
