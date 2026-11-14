"""Semáforo legal determinista (Ley 3/2020 Mar Menor + PAC). T-019.

Herramienta de apoyo, no es asesoría legal. Consulta a tu técnico.

    from app.backend.rules import check, allowed, to_contract
"""
from .legal import (  # noqa: F401
    GRUPOS, NOTA, REGLAS, VERSION_REGLAS, ZONAS_OK,
    allowed, check, info_cultivo, to_contract,
)
