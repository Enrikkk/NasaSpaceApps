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


def test_engine_json_por_defecto_desde_engine_data(tmp_path, monkeypatch):
    """Contrato de montaje: sin ENGINE_JSON, la API usa engine_data/engine.json si existe (T-017)."""
    from app.backend.api import settings as st
    monkeypatch.delenv("ENGINE_JSON", raising=False)
    falso = tmp_path / "engine.json"
    monkeypatch.setattr(st, "ENGINE_DATA_JSON", falso)
    assert st.get_settings().engine_json == ""
    falso.write_text("{}")
    assert st.get_settings().engine_json == str(falso)
    monkeypatch.setenv("ENGINE_JSON", "/otra/ruta.json")
    assert st.get_settings().engine_json == "/otra/ruta.json"


def test_rotaciones_referencia_en_meta(client):
    """Las rotaciones son las de la parcela de referencia: la API lo dice en _meta (hasta que haya motor por punto)."""
    d = client.post("/analyze", json={"lat": 37.7383, "lon": -0.98838}).json()
    ref = d["_meta"]["rotaciones_referencia"]
    assert ref["parcela_referencia"] == "30-37-0-0-18-426-1" and ref["aplica_a_esta_parcela"] is True
    assert not any("parcela de referencia" in a for a in d["_meta"].get("avisos", []))


def test_rotaciones_referencia_avisa_en_otra_parcela(client):
    """En otra parcela cubierta (aqui, San Javier) las rotaciones siguen siendo las de referencia y la API lo avisa."""
    d = client.post("/analyze", json={"lat": 37.80, "lon": -0.84}).json()
    if d["parcela"].get("_status") != "precalculado":
        import pytest
        pytest.skip("sin recintos de San Javier en este entorno de test")
    ref = d["_meta"]["rotaciones_referencia"]
    assert ref["aplica_a_esta_parcela"] is False
    assert any("parcela de referencia" in a for a in d["_meta"]["avisos"])
