"""Sustituye al antiguo test de sincronia de copias: la API no duplica codigo, importa el del producto (sin vendor/)."""
from pathlib import Path

from app.backend.api import blocks, engine_adapter, legal_blocks, live, main, settings, store
from api_helpers import API, DATA, REPO


def test_los_imports_son_los_del_producto():
    from app.backend.pipeline.atom import lookup
    from app.backend.pipeline.clima_suelo import pipeline
    from app.backend.rules import legal, check, to_contract
    assert store.RecintoIndex is lookup.RecintoIndex and store.ATTRIBUTION == lookup.ATTRIBUTION
    assert live.P is pipeline and legal_blocks.L is legal
    assert callable(check) and callable(to_contract)


def test_no_hay_copias_vendor():
    assert not (API / "vendor").exists() and not (API / "data").exists()


def test_rutas_por_defecto_existen():
    cfg = settings.Settings()
    assert cfg.contract_path == DATA / "torre-pacheco.contract.example.json" and cfg.contract_path.is_file()
    assert settings.SEMILLA_PIPELINE.is_dir() and len(list(settings.SEMILLA_PIPELINE.glob("*.json"))) == 4
    assert (DATA / "contract.schema.json").is_file() and (DATA / "contract" / "adapt_enrique.py").is_file()
    assert settings.REPO_ROOT == REPO and Path(settings.__file__).parent == API


def test_adaptador_v11_importable():
    assert hasattr(engine_adapter._adaptador(), "adapt_enrique")
