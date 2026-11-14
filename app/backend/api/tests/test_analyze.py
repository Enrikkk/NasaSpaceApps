"""POST /analyze, /health, /parcel: contrato valido, bloques reales/precalculados/simulados, cobertura, recinto, zona."""
import pytest

from api_helpers import DEMO, DEMO_RECINTO, VALLADOLID, assert_valido

BLOQUES = ("parcela", "historia", "ndvi", "clima", "suelo")


def analizar(c, **cuerpo):
    r = c.post("/analyze", json={**DEMO, **cuerpo})
    assert r.status_code == 200, r.text
    return r.json()


def test_health(client_mini):
    h = client_mini.get("/health").json()
    assert h["status"] == "ok" and h["version"] == "dev"
    assert h["recintos"]["cargado"] and h["recintos"]["n"] == 66


def test_demo_completa_valida_y_con_estados(client_mini):
    d = analizar(client_mini, recinto=DEMO_RECINTO)
    assert_valido(d)
    m = d["_meta"]
    assert m["estado_bloques"] == {"parcela": "precalculado", "historia": "simulado", "ndvi": "simulado",
                                   "clima": "real", "suelo": "real", "rotaciones": "simulado"}
    assert m["bloques_pendientes"] == [] and "bloques_sin_datos" not in m
    assert "MOCK" in m["aviso"] and m["cobertura"]["nivel"] == "completo"
    p = d["parcela"]
    assert p["id"] == "30-37-0-0-18-426-1" and p["ha"] == pytest.approx(4.0868) and p["pendiente_pct"] == 0.8
    assert p["sigpac"] == DEMO_RECINTO and p["fuente_id"] == "sigpac" and p["geometry"]["type"] in ("Polygon", "MultiPolygon")
    assert "FEGA" in p["atribucion"] or "FONDO ESPAÑOL" in p["atribucion"]
    assert any("FONDO ESPAÑOL DE GARANTÍA AGRARIA" in a for a in m["atribuciones"])
    assert d["clima"]["lluvia_anual_mm"]["valor"] == pytest.approx(308, abs=1) and len(d["clima"]["serie_anual"]) == 20
    assert d["suelo"]["textura"] == "franco-arcillo-limoso"
    ids = {f["id"] for f in d["fuentes"]}
    assert {"sigpac", "power", "imerg", "soilgrids", "open-meteo"} <= ids
    sig = next(f for f in d["fuentes"] if f["id"] == "sigpac")
    assert "CC BY 4.0" in sig["licencia"] and "atribucion" in sig


def test_latencias_en_meta(client_mini):
    lat = analizar(client_mini)["_meta"]["latencia_ms"]
    assert {"parcela", "clima", "suelo", "rotaciones", "total"} <= lat.keys() and lat["total"] < 2000


# ---------------------------------------------------------------------------------------------- recinto (acuerdo con Arturo)
def test_recinto_ausente_no_hay_clave_y_no_es_completo(client_mini):
    c = analizar(client_mini)["_meta"]["consulta"]
    assert "recinto" not in c and c["recinto_completo"] is False and "recinto_coincide" not in c


def test_recinto_parcial_omite_componentes_ausentes(client_mini):
    c = analizar(client_mini, recinto={"poligono": 18, "parcela": 426})["_meta"]["consulta"]
    assert c["recinto"] == {"poligono": 18, "parcela": 426}      # ni provincia ni agregado=0 inventados
    assert c["recinto_completo"] is False and c["recinto_coincide"] is True


def test_recinto_cero_explicito_se_conserva(client_mini):
    c = analizar(client_mini, recinto={"agregado": 0, "zona": 0, "recinto": 1})["_meta"]["consulta"]
    assert c["recinto"] == {"agregado": 0, "zona": 0, "recinto": 1}


def test_recinto_null_y_campos_null_se_tratan_como_ausentes(client_mini):
    c = analizar(client_mini, recinto={"poligono": 18, "zona": None})["_meta"]["consulta"]
    assert c["recinto"] == {"poligono": 18}
    assert "recinto" not in analizar(client_mini, recinto=None)["_meta"]["consulta"]


def test_recinto_completo_true_con_los_siete(client_mini):
    c = analizar(client_mini, recinto=DEMO_RECINTO)["_meta"]["consulta"]
    assert c["recinto_completo"] is True and c["recinto"] == DEMO_RECINTO


def test_recinto_que_no_coincide_avisa(client_mini):
    d = analizar(client_mini, recinto={**DEMO_RECINTO, "parcela": 999})
    assert d["_meta"]["consulta"]["recinto_coincide"] is False
    assert any("no coincide" in a for a in d["_meta"]["avisos"]) and d["parcela"]["id"] == "30-37-0-0-18-426-1"
    assert_valido(d)


@pytest.mark.parametrize("cuerpo", [
    {"recinto": "30/37/18/426/1"},                 # cadena: solo se admite objeto
    {"recinto": {"poligono": -1}}, {"recinto": {"provincia": 100}},
    {"lat": 91}, {"lon": -181}, {"lat": "x"}, {"zona": "zona_3"}, {"campo_extra": 1},
])
def test_422_sin_eco_del_valor(client_mini, cuerpo):
    r = client_mini.post("/analyze", json={**DEMO, **cuerpo})
    assert r.status_code == 422
    assert '"input"' not in r.text


def test_422_sin_lat(client_mini):
    assert client_mini.post("/analyze", json={"lon": 0}).status_code == 422


# ---------------------------------------------------------------------------------------------- cobertura
def test_fuera_de_cobertura_parcela_cargando_con_aviso(client_mini):
    d = analizar(client_mini, **VALLADOLID)
    assert_valido(d)
    p = d["parcela"]
    assert p["_status"] == "cargando" and p["sin_cobertura"] is True and "cobertura basica" in p["aviso"]
    m = d["_meta"]
    assert m["cobertura"]["nivel"] == "basico" and m["bloques_sin_datos"] == ["parcela"] and "parcela" not in m["bloques_pendientes"]
    assert any("fuera de los municipios" in a for a in m["avisos"])
    assert "atribuciones" not in m
    assert {r["semaforo_legal"]["color"] for r in d["rotaciones"]} == {"gris"}   # D-009: basico -> gris


def test_punto_dentro_de_municipio_pero_sin_recinto(client_mini):
    # mar abierto al este de la muestra: dentro de la caja de la muestra no hay hueco facil; se usa un punto en su caja sin recinto
    from api_helpers import SAMPLE
    import json
    fc = json.loads(SAMPLE.read_text(encoding="utf-8"))
    xs = [c[0] for f in fc["features"] for c in f["geometry"]["coordinates"][0]]
    ys = [c[1] for f in fc["features"] for c in f["geometry"]["coordinates"][0]]
    # esquina de la caja: casi seguro sin recinto; si lo hubiera, el test se omite
    lat, lon = max(ys) - 1e-5, max(xs) - 1e-5
    d = analizar(client_mini, lat=lat, lon=lon)
    if d["parcela"]["_status"] != "cargando":
        pytest.skip("la esquina de la muestra cae en un recinto")
    assert d["parcela"]["sin_cobertura"] and any("ningun recinto" in a for a in d["_meta"]["avisos"])
    assert_valido(d)


def test_fuera_de_espana_aviso_extra(client_mini):
    d = analizar(client_mini, lat=48.85, lon=2.35)
    assert any("fuera de Espana" in a for a in d["_meta"]["avisos"])
    assert_valido(d)


# ---------------------------------------------------------------------------------------------- clima/suelo sin cache
def test_sin_cache_y_sin_red_clima_suelo_cargando(client_mini):
    d = analizar(client_mini, **VALLADOLID)
    for b in ("clima", "suelo"):
        assert d[b]["_status"] == "cargando" and "AGROCKHAM_OFFLINE" in d[b]["aviso"]
    assert set(d["_meta"]["bloques_pendientes"]) == {"clima", "suelo"}
    assert any("clima:" in a for a in d["_meta"]["avisos"])
    assert_valido(d)


# ---------------------------------------------------------------------------------------------- bloques=
def test_bloques_parcial_y_fusion_en_parcel(client_mini):
    r = client_mini.post("/analyze?bloques=parcela", json=DEMO).json()
    assert r["parcela"]["_status"] == "precalculado" and r["clima"]["_status"] == "cargando" and r["rotaciones"] == []
    assert set(r["_meta"]["bloques_pendientes"]) == {"historia", "ndvi", "clima", "suelo", "rotaciones"}
    assert_valido(r)
    client_mini.post("/analyze?bloques=clima,suelo", json=DEMO)
    g = client_mini.get("/parcel/30-37-0-0-18-426-1").json()
    assert g["parcela"]["_status"] == "precalculado" and g["clima"]["_status"] == "real" and g["suelo"]["_status"] == "real"
    assert client_mini.get("/parcel/q-37.73830_-0.98838").json()["_meta"]["consulta_id"] == "q-37.73830_-0.98838"
    client_mini.post("/analyze?bloques=rotaciones", json=DEMO)
    g = client_mini.get("/parcel/q-37.73830_-0.98838").json()
    assert len(g["rotaciones"]) == 3 and "escenarios_meta" in g and g["_meta"]["bloques_pendientes"] == ["historia", "ndvi"]
    assert_valido(g)


@pytest.mark.parametrize("q", ["?bloques=", "?bloques=nada", "?bloques=clima,nada"])
def test_bloques_invalidos_422(client_mini, q):
    assert client_mini.post("/analyze" + q, json=DEMO).status_code == 422


def test_parcel_404(client_mini):
    assert client_mini.get("/parcel/no-existe").status_code == 404


# ---------------------------------------------------------------------------------------------- CORS y compresion
def test_cors_localhost_y_frontend_origin(monkeypatch):
    from app.backend.api.settings import Settings
    monkeypatch.setenv("FRONTEND_ORIGIN", "https://agrockham.example/, *, http://localhost:5173")
    assert Settings().cors_origins == ["http://localhost:5173", "https://agrockham.example"]   # sin '/' final, sin '*', sin duplicados
    monkeypatch.delenv("FRONTEND_ORIGIN")
    assert Settings().cors_origins == ["http://localhost:5173"]


def test_cors_cabeceras(client_mini):
    r = client_mini.get("/health", headers={"Origin": "http://localhost:5173"})
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "access-control-allow-credentials" not in r.headers
    r = client_mini.get("/health", headers={"Origin": "https://malo.example"})
    assert "access-control-allow-origin" not in r.headers
    r = client_mini.options("/analyze", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST",
                                                  "Access-Control-Request-Headers": "content-type"})
    assert r.status_code == 200 and r.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_analyze_va_comprimido_si_el_cliente_acepta_gzip(client_mini):
    r = client_mini.post("/analyze", json=DEMO, headers={"Accept-Encoding": "gzip"})
    assert r.headers.get("content-encoding") == "gzip"
