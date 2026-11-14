"""Configuracion de la API: solo variables de entorno, sin secretos."""
import os
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Origen del frontend en desarrollo (Vite). El de produccion llega por FRONTEND_ORIGIN.
ORIGEN_DEV = "http://localhost:5173"

# Campo de Cartagena, bbox aproximada (lon_min, lat_min, lon_max, lat_max). Fuera de ella: cobertura "basico".
BBOX_CAMPO_CARTAGENA = (-1.35, 37.45, -0.65, 37.95)
# Caja gruesa de Espana peninsular + Baleares + Canarias no se distingue: solo un aviso orientativo.
BBOX_ESPANA_PENINSULAR = (-9.5, 35.9, 4.5, 43.9)


def _origenes() -> list[str]:
    """localhost:5173 + FRONTEND_ORIGIN (admite varios separados por comas). Nunca '*'."""
    extra = os.getenv("FRONTEND_ORIGIN", "")
    lista = [ORIGEN_DEV] + [o.strip().rstrip("/") for o in extra.split(",")]
    vistos: list[str] = []
    for o in lista:
        if o and o != "*" and o not in vistos:
            vistos.append(o)
    return vistos


def _contract_path() -> Path:
    """CONTRACT_PATH si existe; si no, la copia local data/ (la que viaja en la imagen)."""
    explicito = os.getenv("CONTRACT_PATH")
    if explicito:
        return Path(explicito)
    return HERE / "data" / "torre-pacheco.contract-v1.draft.json"


@dataclass(frozen=True)
class Settings:
    version: str = field(default_factory=lambda: os.getenv("GIT_SHA") or "dev")
    cors_origins: list[str] = field(default_factory=_origenes)
    contract_path: Path = field(default_factory=_contract_path)
    cache_max: int = field(default_factory=lambda: int(os.getenv("CACHE_MAX", "256")))


def get_settings() -> Settings:
    return Settings()
