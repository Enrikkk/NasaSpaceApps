"""Localiza el esquema JSON del contrato para validar los bloques. Nunca lanza si falta: devuelve None.

Orden de busqueda (la primera ruta que exista):
  1. $AGROCKHAM_CONTRACT_SCHEMA
  2. app/data/contract.schema.json                                   (esquema vigente cuando T-009 lo publique ahi)
  3. research/contract-v1-draft/v1.1/contract.schema.v1.1.json       (borrador v1.1, esta en main)
  4. research/contract-v1-draft/contract.schema.json                 (borrador v1)
"""
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CANDIDATOS = (
    REPO_ROOT / "app" / "data" / "contract.schema.json",
    REPO_ROOT / "research" / "contract-v1-draft" / "v1.1" / "contract.schema.v1.1.json",
    REPO_ROOT / "research" / "contract-v1-draft" / "contract.schema.json",
)


def schema_path():
    env = os.environ.get("AGROCKHAM_CONTRACT_SCHEMA")
    for p in ([Path(env)] if env else []) + list(CANDIDATOS):
        if p.is_file():
            return p
    return None


def load_schema():
    """(dict, Path) o (None, None) si no hay ningun esquema disponible."""
    p = schema_path()
    return (json.loads(p.read_text(encoding="utf-8")), p) if p else (None, None)
