import importlib.util
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

BORRADOR = RAIZ.parents[1] / "contract-v1-draft"
ESQUEMA = BORRADOR / "contract.schema.json"
VALIDATE = BORRADOR / "validate.py"


@pytest.fixture(scope="session")
def esquema():
    if not ESQUEMA.exists():
        pytest.skip(f"no esta {ESQUEMA}")
    return json.loads(ESQUEMA.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def validate_mod():
    if not VALIDATE.exists():
        pytest.skip(f"no esta {VALIDATE}")
    spec = importlib.util.spec_from_file_location("validate_contrato", VALIDATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    import main

    main._cache.clear()
    return TestClient(main.app)


@pytest.fixture()
def comprobar(esquema, validate_mod):
    """Valida un contrato contra el esquema + invariantes del borrador; falla con la lista de errores."""
    def _f(doc):
        errores = validate_mod.validar(doc, esquema)
        assert not errores, errores
        fallos = [(n, e) for n, e in validate_mod.check_invariantes(doc) if e]
        assert not fallos, fallos
    return _f
