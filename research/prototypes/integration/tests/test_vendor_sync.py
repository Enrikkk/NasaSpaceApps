"""Las copias (vendor/ y data/) deben ser identicas a su origen. Si un prototipo cambia, este test falla y hay que recopiar.

Si el origen ya no existe (p. ej. tras mover todo a app/backend/), el test de ese fichero se omite.
"""
import hashlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PROTO = ROOT.parent
CONTRATO = PROTO.parent / "contract-v1-draft"

PARES = [  # (copia, origen)
    ("vendor/pipeline.py", PROTO / "pipeline_clima_suelo" / "pipeline.py"),
    ("vendor/legal.py", PROTO / "legal_rules" / "legal.py"),
    ("vendor/rules.csv", PROTO / "legal_rules" / "rules.csv"),
    ("vendor/grupos_cultivo.csv", PROTO / "legal_rules" / "grupos_cultivo.csv"),
    ("vendor/lookup.py", PROTO / "atom_pipeline" / "lookup.py"),
    ("data/torre-pacheco.contract-v1.draft.json", CONTRATO / "torre-pacheco.contract-v1.draft.json"),
] + [(f"data/pipeline_cache/{f.name}", f) for f in sorted((PROTO / "pipeline_clima_suelo" / "cache").glob("*.json"))]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.mark.parametrize("copia,origen", PARES, ids=[c for c, _ in PARES])
def test_copia_identica_al_origen(copia, origen):
    if not origen.exists():
        pytest.skip(f"origen ausente: {origen}")
    assert sha(ROOT / copia) == sha(origen), f"{copia} diverge de {origen}: vuelve a copiarlo (o decide cual manda)"


def test_la_semilla_de_cache_esta_completa():
    nombres = {f.name for f in (ROOT / "data" / "pipeline_cache").glob("*.json")}
    assert nombres == {"openmeteo-era5_377_-10.json", "power-imerg_377_-10.json", "power-merra2_75_-2.json", "soilgrids_15095_-396.json"}
