"""API Agrockham (esqueleto, T-017): FastAPI listo para Cloud Run.

STUB: devuelve el contrato v1 por bloques con datos del borrador (`simulado`). Ver README.md.
"""
import logging
import threading
from collections import OrderedDict
from typing import Annotated, Optional, Union

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

import contract
import settings

log = logging.getLogger("agrockham.api")
cfg = settings.get_settings()

app = FastAPI(
    title="Agrockham API (esqueleto)",
    version=cfg.version,
    description="STUB: devuelve el contrato v1 por bloques. Nada de lo que devuelve es dato real.",
)

# Sin credenciales (no hay cuentas ni cookies); solo GET y POST; solo los origenes declarados.
app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(RequestValidationError)
async def _validacion(_: Request, exc: RequestValidationError) -> JSONResponse:
    """422 sin devolver el valor recibido (`input`): evita reenviar NaN/Infinity (JSON invalido) o cadenas largas."""
    detalle = [{"loc": e.get("loc"), "msg": e.get("msg"), "type": e.get("type")} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": detalle})


class Recinto(BaseModel):
    """Referencia SIGPAC del recinto clicado (todo opcional; el frontend manda lo que tenga)."""
    model_config = ConfigDict(extra="ignore")
    provincia: Optional[int] = Field(None, ge=0, le=99)
    municipio: Optional[int] = Field(None, ge=0, le=999)
    agregado: Optional[int] = Field(None, ge=0)
    zona: Optional[int] = Field(None, ge=0)
    poligono: Optional[int] = Field(None, ge=0)
    parcela: Optional[int] = Field(None, ge=0)
    recinto: Optional[int] = Field(None, ge=0)


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lat: float = Field(..., ge=-90, le=90, allow_inf_nan=False, examples=[37.7383])
    lon: float = Field(..., ge=-180, le=180, allow_inf_nan=False, examples=[-0.98838])
    recinto: Optional[Union[Recinto, Annotated[str, Field(max_length=64)]]] = Field(
        None, description="Referencia SIGPAC: objeto {provincia, municipio, poligono, parcela, recinto} o cadena."
    )


# Ultimo contrato por id (memoria del proceso: se pierde al reiniciar o con otra instancia; ver README).
_cache: "OrderedDict[str, dict]" = OrderedDict()
_lock = threading.Lock()


def _guardar(doc: dict) -> dict:
    """Guarda (fusionando con lo ya cargado de la misma consulta) y devuelve el contrato guardado."""
    qid = doc["_meta"]["consulta_id"]
    with _lock:
        guardado = contract.fusionar(_cache.get(qid), doc)
        claves = [qid]
        pid = contract.id_parcela(guardado)
        if pid:
            claves.append(pid)
        for k in claves:
            _cache[k] = guardado
            _cache.move_to_end(k)
        while len(_cache) > cfg.cache_max:
            _cache.popitem(last=False)
    return guardado


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": cfg.version}


@app.post("/analyze")
def analyze(
    req: AnalyzeRequest,
    bloques: Annotated[
        Optional[str],
        Query(description="Lista separada por comas de bloques a rellenar: " + ",".join(contract.BLOQUES)
              + ". Los demas salen `cargando`. Sin parametro = todos."),
    ] = None,
) -> dict:
    pedidos = None
    if bloques is not None:
        pedidos = [b.strip() for b in bloques.split(",") if b.strip()]
        if not pedidos:
            raise HTTPException(422, detail="?bloques= vacio: indica al menos un bloque o quita el parametro")
        malos = [b for b in pedidos if b not in contract.BLOQUES]
        if malos:
            raise HTTPException(422, detail=f"bloques desconocidos {malos}; validos: {list(contract.BLOQUES)}")
    recinto = req.recinto.model_dump(exclude_none=True) if isinstance(req.recinto, Recinto) else req.recinto
    doc = contract.construir(req.lat, req.lon, recinto, pedidos)
    _guardar(doc)
    return doc


@app.get("/parcel/{parcel_id:path}")
def get_parcel(parcel_id: str) -> dict:
    with _lock:
        doc = _cache.get(parcel_id)
    if doc is None:
        raise HTTPException(404, detail="parcela no encontrada en cache (haz primero POST /analyze)")
    return doc
