"""Configuracion de la API integrada: solo variables de entorno, sin secretos (no se lee .env)."""
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Origen del frontend en desarrollo (Vite). El de produccion llega por FRONTEND_ORIGIN.
ORIGEN_DEV = "http://localhost:5173"

# Directorio por defecto de los GeoJSON de ATOM (salida de atom_pipeline/build_recintos.py). Es el del scratchpad de
# desarrollo de gonzalo; en Docker se fija con ENV ATOM_BUILD_DIR=/data/atom.
ATOM_BUILD_DIR_DEFECTO = ("/tmp/claude-1000/-home-gonza--claude-spares-spare-Lt5F48/"
                          "e95c92e8-304d-4036-9411-fa5648316bbc/scratchpad/atom_out/build")

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


@dataclass(frozen=True)
class Settings:
    version: str = field(default_factory=lambda: os.getenv("GIT_SHA") or "dev")
    cors_origins: list[str] = field(default_factory=_origenes)
    # contrato borrador que sirve el motor por defecto (copia en data/, un test vigila que no diverja)
    contract_path: Path = field(default_factory=lambda: Path(os.getenv("CONTRACT_PATH") or HERE / "data" / "torre-pacheco.contract-v1.draft.json"))
    cache_max: int = field(default_factory=lambda: _int("CACHE_MAX", 256))
    # recintos ATOM
    atom_build_dir: Path = field(default_factory=lambda: Path(os.getenv("ATOM_BUILD_DIR") or ATOM_BUILD_DIR_DEFECTO))
    recintos_max: int = field(default_factory=lambda: _int("RECINTOS_MAX", 3000))
    recintos_max_km: float = field(default_factory=lambda: _float("RECINTOS_MAX_KM", 5.0))
    # clima/suelo: cache de ejecucion (se siembra con data/pipeline_cache) y limites de la red en vivo
    pipeline_cache_dir: Path = field(default_factory=lambda: Path(os.getenv("PIPELINE_CACHE_DIR") or Path(tempfile.gettempdir()) / "agrockham-pipeline-cache"))
    live_http_timeout_s: int = field(default_factory=lambda: _int("LIVE_HTTP_TIMEOUT_S", 40))
    live_retries: int = field(default_factory=lambda: _int("LIVE_RETRIES", 1))
    live_deadline_s: float = field(default_factory=lambda: _float("LIVE_DEADLINE_S", 60.0))
    # motor de rotaciones: vacio = borrador simulado; ENGINE_JSON = ruta al JSON de enrique (ver engine_adapter.py)
    engine_json: str = field(default_factory=lambda: os.getenv("ENGINE_JSON", ""))


def get_settings() -> Settings:
    return Settings()
