# Agrockham API (T-024). Sin secretos en la imagen: la configuracion llega por variables de entorno.
#
# CONTEXTO DE CONSTRUCCION = RAIZ DEL REPO (importa app.backend.pipeline, app.backend.rules y lee app/data/):
#
#   # 1) GeoJSON de ATOM (salida de app/backend/pipeline/atom/build_recintos.py, ~9 MB): carpeta ignorada por git
#   cp -r "$ATOM_BUILD_DIR" app/backend/api/atom_build
#   # 2) desde la raiz del repo
#   docker build -f app/backend/api/Dockerfile --build-arg GIT_SHA=<sha corto> -t agrockham-api .
#   docker run --rm -p 8080:8080 agrockham-api            # http://localhost:8080/docs
#
# El .dockerignore de esta imagen es Dockerfile.dockerignore (lista blanca: solo entra lo que se copia abajo).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# Usuario sin privilegios
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin app
WORKDIR /app

COPY app/backend/api/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Codigo de la API y el del producto que importa (app/, app/backend/ y app/data/ son paquetes de espacio de nombres: sin __init__)
COPY app/backend/api/__init__.py app/backend/api/main.py app/backend/api/blocks.py app/backend/api/engine_adapter.py \
     app/backend/api/legal_blocks.py app/backend/api/parcel_input.py app/backend/api/live.py app/backend/api/settings.py app/backend/api/store.py \
     ./app/backend/api/
COPY app/backend/pipeline/__init__.py ./app/backend/pipeline/
COPY app/backend/pipeline/atom/__init__.py app/backend/pipeline/atom/lookup.py ./app/backend/pipeline/atom/
COPY app/backend/pipeline/clima_suelo/__init__.py app/backend/pipeline/clima_suelo/pipeline.py ./app/backend/pipeline/clima_suelo/
COPY app/backend/pipeline/fega/__init__.py app/backend/pipeline/fega/declarados.py app/backend/pipeline/fega/cod_producto.csv ./app/backend/pipeline/fega/
COPY app/backend/rules ./app/backend/rules
# Datos: contrato de ejemplo (bloques simulados), adaptador del JSON de enrique y semilla de la cache de clima/suelo (parcela demo)
COPY app/data/torre-pacheco.contract.example.json ./app/data/
COPY app/data/contract/adapt_enrique.py ./app/data/contract/
COPY app/data/cache/pipeline/clima_suelo ./app/data/cache/pipeline/clima_suelo
# Recintos SIGPAC (ATOM del FEGA): no estan en git, hay que dejarlos en app/backend/api/atom_build antes de construir
COPY app/backend/api/atom_build /data/atom
# JSON del motor (opcional): ver app/backend/api/engine_data/README.md
COPY app/backend/api/engine_data ./app/backend/api/engine_data
# app estatica (opcional): ver app/backend/api/frontend_dist/README.md
COPY app/backend/api/frontend_dist ./app/backend/api/frontend_dist

ARG GIT_SHA=dev
ENV GIT_SHA=${GIT_SHA} \
    ATOM_BUILD_DIR=/data/atom \
    PIPELINE_CACHE_DIR=/tmp/agrockham-pipeline-cache

USER app
EXPOSE 8080
# Cloud Run inyecta PORT (8080 por defecto). sh -c expande ${PORT}; exec deja a uvicorn como PID 1 (recibe SIGTERM).
CMD ["sh", "-c", "exec uvicorn app.backend.api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
