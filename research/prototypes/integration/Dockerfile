# Agrockham API integrada (prototipo). Sin secretos en la imagen: la configuracion llega por variables de entorno.
#
# Antes de construir hay que dejar los GeoJSON de ATOM (salida de atom_pipeline/build_recintos.py, ~9 MB) en ./atom_build:
#   cp -r "$ATOM_BUILD_DIR" ./atom_build        (esa carpeta esta en .gitignore: son datos, no codigo)
#   docker build --build-arg GIT_SHA=$(git rev-parse --short HEAD) -t agrockham-api .
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Usuario sin privilegios
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin app
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py blocks.py engine_adapter.py legal_blocks.py live.py settings.py store.py ./
COPY vendor ./vendor
COPY data ./data
COPY atom_build /data/atom

ARG GIT_SHA=dev
ENV GIT_SHA=${GIT_SHA} \
    ATOM_BUILD_DIR=/data/atom \
    PIPELINE_CACHE_DIR=/tmp/agrockham-pipeline-cache

USER app
EXPOSE 8080
# Cloud Run inyecta PORT (8080 por defecto). sh -c expande ${PORT}; exec deja a uvicorn como PID 1 (recibe SIGTERM).
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
