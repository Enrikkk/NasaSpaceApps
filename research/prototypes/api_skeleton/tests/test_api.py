import filecmp
import importlib
import urllib.parse

import pytest

import contract
import settings
from conftest import BORRADOR

DEMO = {"lat": 37.7383, "lon": -0.98838}
FUERA = {"lat": 41.65, "lon": -4.72}  # Valladolid


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "version": "dev"}


def test_analyze_demo_valido_y_completo(client, comprobar):
    r = client.post("/analyze", json=DEMO)
    assert r.status_code == 200
    d = r.json()
    comprobar(d)
    assert d["_meta"]["cobertura"]["nivel"] == "completo"
    assert "MOCK" in d["_meta"]["aviso"] and d["_meta"]["stub"] is True
    for b in ("parcela", "historia", "clima", "suelo"):
        assert d[b]["_status"] == "simulado"
    assert len(d["rotaciones"]) == 3 and all(x["_status"] == "simulado" for x in d["rotaciones"])
    # ndvi (Enrique) aun no existe
    assert d["ndvi"] == {"_status": "cargando"}
    assert d["_meta"]["bloques_pendientes"] == ["ndvi"]
    assert d["_meta"]["consulta"]["lat"] == DEMO["lat"]


def test_analyze_fuera_de_zona_es_basico(client, comprobar):
    d = client.post("/analyze", json=FUERA).json()
    comprobar(d)
    assert d["_meta"]["cobertura"]["nivel"] == "basico"
    assert any("fuera del Campo de Cartagena" in a for a in d["_meta"]["avisos"])
    assert not any("fuera de Espana" in a for a in d["_meta"]["avisos"])


def test_analyze_fuera_de_espana_avisa(client):
    d = client.post("/analyze", json={"lat": 48.85, "lon": 2.35}).json()
    assert d["_meta"]["cobertura"]["nivel"] == "basico"
    assert any("fuera de Espana" in a for a in d["_meta"]["avisos"])


@pytest.mark.parametrize("lat,lon", [(37.45, -1.35), (37.95, -0.65), (37.7, -1.0)])
def test_bbox_incluye_bordes(lat, lon):
    assert contract.cobertura(lat, lon)[0]["nivel"] == "completo"


@pytest.mark.parametrize("lat,lon", [(37.4499, -1.0), (37.7, -0.6499), (37.7, -1.3501), (37.9501, -1.0)])
def test_bbox_justo_fuera(lat, lon):
    assert contract.cobertura(lat, lon)[0]["nivel"] == "basico"


@pytest.mark.parametrize("cuerpo", [
    {"lat": 91, "lon": 0}, {"lat": -90.1, "lon": 0}, {"lat": 0, "lon": 180.5}, {"lat": 0, "lon": -181},
    {"lat": 0}, {"lon": 0}, {"lat": "abc", "lon": 0}, {}, {**DEMO, "otro": 1},
    {**DEMO, "recinto": {"poligono": -1}}, {**DEMO, "recinto": "x" * 65},
])
def test_cuerpo_invalido_422(client, cuerpo):
    assert client.post("/analyze", json=cuerpo).status_code == 422


def test_nan_rechazado(client):
    r = client.post("/analyze", content='{"lat": NaN, "lon": 0}', headers={"content-type": "application/json"})
    assert r.status_code == 422


def test_recinto_objeto_y_cadena(client):
    d = client.post("/analyze", json={**DEMO, "recinto": {"provincia": 30, "poligono": 18, "parcela": 426, "recinto": 1,
                                                          "basura": 5}}).json()
    assert d["_meta"]["consulta"]["recinto"] == {"provincia": 30, "poligono": 18, "parcela": 426, "recinto": 1}
    d = client.post("/analyze", json={**DEMO, "recinto": "30:0:0:0:18:426:1"}).json()
    assert d["_meta"]["consulta"]["recinto"] == "30:0:0:0:18:426:1"


def test_bloques_parciales(client, comprobar):
    d = client.post("/analyze?bloques=clima,suelo", json=DEMO).json()
    comprobar(d)
    assert d["clima"]["_status"] == "simulado" and d["suelo"]["_status"] == "simulado"
    assert d["parcela"] == {"_status": "cargando"} and d["historia"] == {"_status": "cargando"}
    assert d["rotaciones"] == [] and "escenarios_meta" not in d
    assert d["_meta"]["bloques_pendientes"] == ["parcela", "historia", "ndvi", "rotaciones"]


def test_bloque_ndvi_pedido_sigue_cargando(client):
    d = client.post("/analyze?bloques=ndvi", json=DEMO).json()
    assert d["ndvi"]["_status"] == "cargando"
    assert set(d["_meta"]["bloques_pendientes"]) == set(contract.BLOQUES)


@pytest.mark.parametrize("q", ["?bloques=", "?bloques=,", "?bloques=nada", "?bloques=clima,nada"])
def test_bloques_invalidos_422(client, q):
    assert client.post("/analyze" + q, json=DEMO).status_code == 422


def test_parcel_por_id_de_parcela_y_de_consulta(client, comprobar):
    d = client.post("/analyze", json=DEMO).json()
    for clave in (d["parcela"]["id"], d["_meta"]["consulta_id"]):
        r = client.get("/parcel/" + urllib.parse.quote(clave, safe=""))
        assert r.status_code == 200, clave
        assert r.json()["_meta"]["consulta_id"] == d["_meta"]["consulta_id"]
        comprobar(r.json())


def test_parcel_404(client):
    assert client.get("/parcel/no-existe").status_code == 404


def test_parcel_guarda_lo_cargado_progresivamente(client, comprobar):
    client.post("/analyze?bloques=parcela", json=DEMO)
    client.post("/analyze?bloques=clima", json=DEMO)
    g = client.get("/parcel/" + contract.consulta_id(**DEMO)).json()
    comprobar(g)
    assert g["parcela"]["_status"] == "simulado" and g["clima"]["_status"] == "simulado"
    assert g["suelo"]["_status"] == "cargando"
    assert g["_meta"]["bloques_pendientes"] == ["historia", "ndvi", "suelo", "rotaciones"]
    client.post("/analyze", json=DEMO)
    g = client.get("/parcel/" + contract.consulta_id(**DEMO)).json()
    assert g["_meta"]["bloques_pendientes"] == ["ndvi"]


def test_cache_limitado(client):
    import main
    object.__setattr__(main.cfg, "cache_max", 4)
    try:
        for i in range(10):
            client.post("/analyze", json={"lat": 37.5 + i * 0.01, "lon": -1.0})
        assert len(main._cache) <= 4
    finally:
        object.__setattr__(main.cfg, "cache_max", 256)


# ---- CORS ----
def test_cors_origen_permitido(client):
    r = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "access-control-allow-credentials" not in r.headers


def test_cors_preflight_post(client):
    r = client.options("/analyze", headers={"Origin": "http://localhost:5173",
                                            "Access-Control-Request-Method": "POST",
                                            "Access-Control-Request-Headers": "content-type"})
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "POST" in r.headers["access-control-allow-methods"] and "GET" in r.headers["access-control-allow-methods"]
    assert "DELETE" not in r.headers["access-control-allow-methods"]


def test_cors_origen_no_permitido(client):
    r = client.get("/health", headers={"Origin": "https://malo.example"})
    assert "access-control-allow-origin" not in r.headers
    r = client.options("/analyze", headers={"Origin": "https://malo.example", "Access-Control-Request-Method": "POST"})
    assert r.status_code == 400


def test_cors_metodo_no_permitido(client):
    r = client.options("/analyze", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "DELETE"})
    assert r.status_code == 400


def test_frontend_origin_env(monkeypatch):
    monkeypatch.setenv("FRONTEND_ORIGIN", "https://agrockham.example/, https://otro.example ,*")
    assert settings._origenes() == ["http://localhost:5173", "https://agrockham.example", "https://otro.example"]
    monkeypatch.delenv("FRONTEND_ORIGIN")
    assert settings._origenes() == ["http://localhost:5173"]


def test_frontend_origin_llega_al_middleware(monkeypatch):
    from fastapi.testclient import TestClient
    monkeypatch.setenv("FRONTEND_ORIGIN", "https://agrockham.example")
    import main
    main = importlib.reload(main)
    try:
        r = TestClient(main.app).get("/health", headers={"Origin": "https://agrockham.example"})
        assert r.headers["access-control-allow-origin"] == "https://agrockham.example"
    finally:
        monkeypatch.delenv("FRONTEND_ORIGIN")
        importlib.reload(main)


def test_version_desde_entorno(monkeypatch):
    monkeypatch.setenv("GIT_SHA", "abc1234")
    assert settings.get_settings().version == "abc1234"


def test_copia_del_borrador_al_dia():
    original = BORRADOR / "torre-pacheco.contract-v1.draft.json"
    if not original.exists():
        pytest.skip("no esta el borrador original")
    assert filecmp.cmp(original, settings.get_settings().contract_path, shallow=False), \
        "data/ ya no coincide con research/contract-v1-draft/: vuelve a copiar el JSON"
