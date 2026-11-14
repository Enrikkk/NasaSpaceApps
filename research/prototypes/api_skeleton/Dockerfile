# Agrockham API (esqueleto). Sin secretos en la imagen: la configuracion llega por variables de entorno.
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

COPY main.py contract.py settings.py ./
COPY data ./data

# Version opcional: docker build --build-arg GIT_SHA=$(git rev-parse --short HEAD) .
ARG GIT_SHA=dev
ENV GIT_SHA=${GIT_SHA}

USER app
EXPOSE 8080
# Cloud Run inyecta PORT (8080 por defecto). sh -c expande ${PORT}; exec deja a uvicorn como PID 1 (recibe SIGTERM).
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
