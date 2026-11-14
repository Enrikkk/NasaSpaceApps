"""Configuracion de la API: solo variables de entorno, sin secretos (no se lee .env)."""
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent          # app/backend/api
REPO_ROOT = HERE.parents[2]                      # raiz del repo (en Docker: /app)
DATA_DIR = REPO_ROOT / "app" / "data"

# Origen del frontend en desarrollo (Vite). El de produccion llega por FRONTEND_ORIGIN.
ORIGEN_DEV = "http://localhost:5173"

# Directorio por defecto de los GeoJSON de ATOM (salida de app/backend/pipeline/atom/build_recintos.py; ver README.md).
# Ignorado por git. Si no existe, la API arranca sin recintos y lo avisa. En Docker se fija con ENV ATOM_BUILD_DIR=/data/atom.
ATOM_BUILD_DIR_DEFECTO = HERE / "atom_build"

# Contrato de ejemplo (MOCK) del que salen los bloques simulados, y semilla de la cache de clima/suelo (parcela demo).
CONTRATO_EJEMPLO = DATA_DIR / "torre-pacheco.contract.example.json"
SEMILLA_PIPELINE = DATA_DIR / "cache" / "pipeline" / "clima_suelo"

# Caja gruesa de Espana peninsular: solo para un aviso orientativo.
BBOX_ESPANA_PENINSULAR = (-9.5, 35.9, 4.5, 43.9)

ZONAS_LEGALES = ("zona_1", "zona_2", "por_verificar")


def _origenes() -> list[str]:
    """localhost:5173 + FRONTEND_ORIGIN (varios separados por comas, sin '/' final). Nunca '*'."""
    extra = os.getenv("FRONTEND_ORIGIN", "")
    lista = [ORIGEN_DEV] + [o.strip().rstrip("/") for o in extra.split(",")]
    vistos: list[str] = []
    for o in lista:
        if o and o != "*" and o not in vistos:
            vistos.append(o)
    return vistos


def _int(nombre: str, defecto: int) -> int:
    try:
        return int(os.getenv(nombre, str(defecto)))
    except ValueError:
        return defecto


def _float(nombre: str, defecto: float) -> float:
    try:
        return float(os.getenv(nombre, str(defecto)))
    except ValueError:
        return defecto


# JSON publicado del motor (enrique) copiado en tiempo de construccion: app/backend/api/engine_data/engine.json (ignorado por git; ver engine_data/README.md)
ENGINE_DATA_JSON = Path(__file__).resolve().parent / "engine_data" / "engine.json"

@dataclass(frozen=True)
class Settings:
    version: str = field(default_factory=lambda: os.getenv("GIT_SHA") or "dev")
    cors_origins: list[str] = field(default_factory=_origenes)
    # contrato de ejemplo (MOCK) que sirve el motor por defecto: app/data/torre-pacheco.contract.example.json
    contract_path: Path = field(default_factory=lambda: Path(os.getenv("CONTRACT_PATH") or CONTRATO_EJEMPLO))
    cache_max: int = field(default_factory=lambda: _int("CACHE_MAX", 256))
    # recintos ATOM
    atom_build_dir: Path = field(default_factory=lambda: Path(os.getenv("ATOM_BUILD_DIR") or ATOM_BUILD_DIR_DEFECTO))
    recintos_max: int = field(default_factory=lambda: _int("RECINTOS_MAX", 3000))
    recintos_max_km: float = field(default_factory=lambda: _float("RECINTOS_MAX_KM", 5.0))
    # clima/suelo: cache de ejecucion (se siembra con app/data/cache/pipeline/clima_suelo) y limites de la red en vivo
    pipeline_cache_dir: Path = field(default_factory=lambda: Path(os.getenv("PIPELINE_CACHE_DIR") or Path(tempfile.gettempdir()) / "agrockham-pipeline-cache"))
    live_http_timeout_s: int = field(default_factory=lambda: _int("LIVE_HTTP_TIMEOUT_S", 40))
    live_retries: int = field(default_factory=lambda: _int("LIVE_RETRIES", 1))
    live_deadline_s: float = field(default_factory=lambda: _float("LIVE_DEADLINE_S", 60.0))
    # motor de rotaciones: vacio = borrador simulado; ENGINE_JSON = ruta al JSON de enrique (ver engine_adapter.py)
    engine_json: str = field(default_factory=lambda: os.getenv("ENGINE_JSON") or (str(ENGINE_DATA_JSON) if ENGINE_DATA_JSON.is_file() else ""))


def get_settings() -> Settings:
    return Settings()
