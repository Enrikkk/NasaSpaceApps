"""API Agrockham (T-024, D-009): contrato v1.1 por bloques con datos reales donde ya existen. Ver README.md.

Arranque desde la raiz del repo:  uvicorn app.backend.api.main:app --host 0.0.0.0 --port ${PORT:-8080}
Endpoints: /health, POST /analyze[?bloques=], GET /parcel/{id}, GET /recintos?bbox=.
"""
import json
import logging
import math
import threading
from collections import OrderedDict
from contextlib import asynccontextmanager
from typing import Annotated, Literal, Optional

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.gzip import GZipMiddleware

from . import blocks, settings, store

log = logging.getLogger("agrockham.api")
KM_POR_GRADO = 111.32
TOLERANCIA_KM = 1.02


class Recinto(BaseModel):
    """Referencia SIGPAC del recinto clicado. Todo opcional: lo no enviado queda AUSENTE en la respuesta (nunca 0)."""
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
    recinto: Optional[Recinto] = Field(None, description="Referencia SIGPAC {provincia, municipio, agregado, zona, poligono, parcela, recinto}.")
    zona: Literal["zona_1", "zona_2", "por_verificar"] = Field(
        "por_verificar", description="Zona legal del Mar Menor para el semaforo (Ley 3/2020). Por defecto sin verificar.")


def create_app(cfg: Optional[settings.Settings] = None) -> FastAPI:
    cfg = cfg or settings.get_settings()
    cache: "OrderedDict[str, dict]" = OrderedDict()   # ultimo contrato por id (memoria del proceso)
    lock = threading.Lock()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        atom = store.cargar(cfg.atom_build_dir)   # nunca lanza: sin recintos la API arranca y avisa
        app.state.servicio = blocks.Servicio(cfg, atom)
        yield

    app = FastAPI(title="Agrockham API", version=cfg.version, lifespan=lifespan,
                  description="Contrato v1 por bloques: parcela (ATOM/FEGA), clima y suelo (NASA POWER, Open-Meteo, SoilGrids), "
                              "semaforo legal (legal.check) y rotaciones (borrador simulado o motor de enrique).")
    app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=4)
    # Sin credenciales (no hay cuentas ni cookies); solo GET y POST; solo los origenes declarados. CORS al final = capa externa.
    app.add_middleware(CORSMiddleware, allow_origins=cfg.cors_origins, allow_credentials=False,
                       allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

    @app.exception_handler(RequestValidationError)
    async def _validacion(_: Request, exc: RequestValidationError) -> JSONResponse:
        """422 sin devolver el valor recibido (`input`): evita reenviar NaN/Infinity (JSON invalido) o cadenas largas."""
        detalle = [{"loc": e.get("loc"), "msg": e.get("msg"), "type": e.get("type")} for e in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": detalle})

    def servicio(request: Request) -> blocks.Servicio:
        return request.app.state.servicio

    def guardar(doc: dict, aviso) -> None:
        qid = doc["_meta"]["consulta_id"]
        with lock:
            guardado = blocks.fusionar(cache.get(qid), doc, aviso)
            claves = [qid] + ([blocks.id_parcela(guardado)] if blocks.id_parcela(guardado) else [])
            for k in claves:
                cache[k] = guardado
                cache.move_to_end(k)
            while len(cache) > cfg.cache_max:
                cache.popitem(last=False)

    @app.get("/health")
    def health(request: Request) -> dict:
        atom = servicio(request).atom
        out = {"status": "ok", "version": cfg.version,
               "recintos": {"cargado": atom.cargado, "n": len(atom.index) if atom.cargado else 0,
                            "municipios": atom.nombres(), "segundos_carga": atom.segundos_carga}}
        if not atom.cargado:
            out["avisos"] = [f"Recintos SIGPAC no cargados ({atom.error}): /recintos da 503 y /analyze no devuelve parcela."]
        return out

    @app.post("/analyze")
    def analyze(
        req: AnalyzeRequest, request: Request,
        bloques: Annotated[Optional[str], Query(
            description="Lista separada por comas de bloques a rellenar: " + ",".join(blocks.BLOQUES)
            + ". Los demas salen `cargando`. Sin parametro = todos.")] = None,
    ) -> dict:
        pedidos = None
        if bloques is not None:
            pedidos = [b.strip() for b in bloques.split(",") if b.strip()]
            if not pedidos:
                raise HTTPException(422, detail="?bloques= vacio: indica al menos un bloque o quita el parametro")
            malos = [b for b in pedidos if b not in blocks.BLOQUES]
            if malos:
                raise HTTPException(422, detail=f"bloques desconocidos {malos}; validos: {list(blocks.BLOQUES)}")
        recinto = req.recinto.model_dump(exclude_none=True) if req.recinto is not None else None
        doc = servicio(request).construir(req.lat, req.lon, recinto, req.zona, pedidos)
        guardar(doc, servicio(request).aviso)
        return doc

    @app.get("/parcel/{parcel_id:path}")
    def get_parcel(parcel_id: str) -> dict:
        with lock:
            doc = cache.get(parcel_id)
        if doc is None:
            raise HTTPException(404, detail="parcela no encontrada en cache (haz primero POST /analyze)")
        return doc

    @app.get("/recintos")
    def recintos(request: Request, bbox: Annotated[str, Query(description="minlon,minlat,maxlon,maxlat (grados)")]) -> Response:
        atom = servicio(request).atom
        if not atom.cargado:
            raise HTTPException(503, detail="recintos SIGPAC no cargados en este servidor")
        try:
            minx, miny, maxx, maxy = (float(x) for x in bbox.split(","))
        except ValueError:
            raise HTTPException(422, detail="bbox debe ser minlon,minlat,maxlon,maxlat (4 numeros separados por comas)")
        if not all(math.isfinite(v) for v in (minx, miny, maxx, maxy)) or not (-180 <= minx < maxx <= 180 and -90 <= miny < maxy <= 90):
            raise HTTPException(422, detail="bbox fuera de rango o con min >= max")
        ancho_km = (maxx - minx) * KM_POR_GRADO * math.cos(math.radians((miny + maxy) / 2))
        alto_km = (maxy - miny) * KM_POR_GRADO
        cab = {"Cache-Control": "public, max-age=3600"}   # datos estaticos (campana 2026)
        if max(ancho_km, alto_km) > cfg.recintos_max_km * TOLERANCIA_KM:   # 2 %: el cliente calcula la extension a su manera
            cuerpo = ('{"type":"FeatureCollection","attribution":' + _json(store.ATRIBUCION_LARGA)
                      + ',"n_total":null,"n":0,"truncado":true,"limite":"extension","aviso":' + _json(
                          f"Rectangulo de {max(ancho_km, alto_km):.1f} km: maximo {cfg.recintos_max_km:g} km. Acerca el mapa.") + ',"features":[]}')
            return Response(cuerpo, media_type="application/geo+json", headers=cab)
        cuerpo, total, n = atom.index.bbox_geojson((minx, miny, maxx, maxy), cfg.recintos_max)
        return Response(cuerpo, media_type="application/geo+json", headers={**cab, "X-Recintos-Total": str(total)})

    # alias /api: las mismas rutas tambien bajo /api/* (la app estatica vive en /; el cliente puede usar VITE_API_BASE=<url>/api).
    # Se mantienen las rutas sin prefijo por compatibilidad (QA, gates, /docs).
    from fastapi.routing import APIRoute
    for _r in list(app.routes):
        if isinstance(_r, APIRoute) and not _r.path.startswith("/api"):
            app.add_api_route("/api" + _r.path, _r.endpoint, methods=sorted(_r.methods or []), response_model=_r.response_model,
                              include_in_schema=False, response_class=_r.response_class)
    # La app estatica va AL FINAL: las rutas de la API (/health, /analyze, /parcel, /recintos, /docs) tienen prioridad.
    if (cfg.frontend_dir / "index.html").is_file():
        app.mount("/", StaticFiles(directory=str(cfg.frontend_dir), html=True), name="frontend")
    return app


def _json(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


app = create_app()
