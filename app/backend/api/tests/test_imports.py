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
    assert settings.SEMILLA_PIPELINE.is_dir() and len(list(settings.SEMILLA_PIPELINE.glob("*.json"))) >= 4   # demo + parcelas precalentadas (T-011)
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


def test_parcel_input_con_los_campos_de_h002():
    """H-002 (enrique): ParcelInput desde un clic; salinidad/profundidad/drenaje = None (sin dato), nada inventado."""
    from app.backend.api import engine_adapter as EA, parcel_input as PI
    ctx = EA.EngineInput(37.7383, -0.98838,
                         {"id": "30-37-0-0-18-426-1", "ha": 4.0868, "regadio": True, "pendiente_pct": 0.8},
                         None, {"textura": "franco-arcillo-limoso", "ph_h2o": 7.97, "materia_organica_pct": 2.14},
                         zona="zona_2",
                         historia=[{"anio": 2026, "cultivo": "barbecho tradicional", "fuente": "FEGA",
                                    "declaraciones": [{"campana": "2026", "cultivo": "barbecho tradicional", "producto_codigo": 20,
                                                       "sistema_explotacion": "R", "superficie_cultivada_ha": 4.09}]}])
    pi = PI.construir(ctx)
    assert pi["parcel_id"] == "30-37-0-0-18-426-1" and pi["area_ha"] == 4.0868 and pi["regadio"] is True
    assert pi["zona_legal"] == "zona_2" and pi["pendiente_pct"] == 0.8
    assert pi["suelo"]["ph"] == 7.97 and pi["suelo"]["salinidad_ce_dsm"] is None
    assert pi["cultivos_declarados"][0]["producto_codigo"] == 20
    assert {"suelo.salinidad_ce_dsm", "suelo.profundidad_cm", "suelo.drenaje"} <= set(pi["sin_dato"])
    vacio = PI.construir(EA.EngineInput(37.0, -1.0, {}, None, None))
    assert vacio["regadio"] is None and vacio["cultivos_declarados"] == [] and "cultivos_declarados" in vacio["sin_dato"]


def test_historia_real_desde_cache_fega(client, tmp_path, monkeypatch):
    """Con cultivos declarados FEGA en cache, el bloque historia sale `real` y conserva los 0..N registros."""
    import json
    from pathlib import Path
    from app.backend.pipeline.fega import declarados as D
    fix = json.loads((Path(D.__file__).parent / "tests" / "fixtures" / "cultivo_declarado_18_426.json").read_text(encoding="utf-8"))
    regs = D.normalizar(fix["features"], (30, 37, 0, 0, 18, 426, 1))
    cache_dir = client.app.state.servicio.cfg.pipeline_cache_dir
    cf = D._cache_file(cache_dir, (30, 37, 0, 0, 18, 426, 1))
    cf.parent.mkdir(parents=True, exist_ok=True)
    cf.write_text(json.dumps({"registros": regs, "campania": "en uso", "descargado": "t", "fuente": "t", "url": "u", "atribucion": "a"}))
    try:
        d = client.post("/analyze", json={"lat": 37.7383, "lon": -0.98838}).json()
        assert d["_meta"]["estado_bloques"]["historia"] == "real"
        h = d["historia"][0]
        assert h["cultivo"] == "barbecho tradicional" and len(h["declaraciones"]) == 2
    finally:
        cf.unlink(missing_ok=True)


def test_sirve_la_app_estatica_sin_tapar_la_api(tmp_path, monkeypatch):
    """Con FRONTEND_DIR/index.html la API sirve la app en / y las rutas de la API siguen mandando."""
    from fastapi.testclient import TestClient
    from app.backend.api.main import create_app
    from app.backend.api import settings as st
    (tmp_path / "index.html").write_text("<html><body>APP-AGROCKHAM</body></html>")
    monkeypatch.setenv("FRONTEND_DIR", str(tmp_path))
    with TestClient(create_app(st.Settings())) as c:       # `with` arranca el lifespan (servicio, recintos)
        assert "APP-AGROCKHAM" in c.get("/").text
        assert c.get("/health").json()["status"] == "ok"      # la API no queda tapada
        assert c.get("/openapi.json").status_code == 200


def test_alias_api_con_las_mismas_rutas(client):
    """/api/* repite las rutas de la API (la app estatica vive en /); las rutas sin prefijo siguen funcionando."""
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/health").json()["status"] == "ok"
    a = client.post("/api/analyze", json={"lat": 37.7383, "lon": -0.98838}).json()
    b = client.post("/analyze", json={"lat": 37.7383, "lon": -0.98838}).json()
    assert a["parcela"]["id"] == b["parcela"]["id"] == "30-37-0-0-18-426-1"
    assert client.get("/api/recintos", params={"bbox": "-0.995,37.733,-0.980,37.743"}).status_code == 200
