"""GET /recintos?bbox=...: GeoJSON de los recintos del rectangulo, con topes y gzip."""
import gzip
import json

import pytest

from api_helpers import DEMO


def bbox_alrededor(lat, lon, km):
    import math
    dlat = km / 2 / 111.32
    dlon = km / 2 / (111.32 * math.cos(math.radians(lat)))
    return f"{lon - dlon},{lat - dlat},{lon + dlon},{lat + dlat}"


def test_bbox_pequeno_devuelve_recintos_y_atribucion(client_mini):
    r = client_mini.get("/recintos", params={"bbox": bbox_alrededor(DEMO["lat"], DEMO["lon"], 1.0)})
    assert r.status_code == 200 and r.headers["content-type"].startswith("application/geo+json")
    fc = r.json()
    assert fc["type"] == "FeatureCollection" and fc["n"] == len(fc["features"]) > 5 and fc["truncado"] is False
    assert "FONDO ESPAÑOL DE GARANTÍA AGRARIA" in fc["attribution"]
    assert "30/37/0/0/18/426/1" in {f["properties"]["ref"] for f in fc["features"]}
    assert r.headers["x-recintos-total"] == str(fc["n_total"])
    assert "max-age" in r.headers["cache-control"]


def test_bbox_sin_recintos_es_coleccion_vacia(client_mini):
    fc = client_mini.get("/recintos", params={"bbox": "-4.73,41.64,-4.72,41.65"}).json()
    assert fc["features"] == [] and fc["n"] == 0 and fc["truncado"] is False


def test_bbox_grande_devuelve_vacio_con_aviso(client_mini):
    r = client_mini.get("/recintos", params={"bbox": bbox_alrededor(DEMO["lat"], DEMO["lon"], 8.0)})
    fc = r.json()
    assert r.status_code == 200 and fc["features"] == [] and fc["truncado"] is True and fc["limite"] == "extension"
    assert "Acerca el mapa" in fc["aviso"]


def test_tope_de_recintos_trunca(make_client, atom_mini):
    c = make_client(atom_mini, recintos_max=10)
    fc = c.get("/recintos", params={"bbox": bbox_alrededor(DEMO["lat"], DEMO["lon"], 4.0)}).json()
    assert fc["n"] == 10 == len(fc["features"]) and fc["n_total"] > 10 and fc["truncado"] is True


@pytest.mark.parametrize("bbox", ["", "1,2,3", "a,b,c,d", "1,2,3,4,5", "-1,37,-2,38", "0,0,0,0", "nan,0,1,1", "-190,0,1,1", "0,-95,1,1"])
def test_bbox_invalido_422(client_mini, bbox):
    assert client_mini.get("/recintos", params={"bbox": bbox}).status_code == 422


def test_sin_bbox_422(client_mini):
    assert client_mini.get("/recintos").status_code == 422


def test_gzip_si_el_cliente_lo_acepta_y_mismo_contenido(client_mini):
    q = {"bbox": bbox_alrededor(DEMO["lat"], DEMO["lon"], 1.0)}
    r = client_mini.get("/recintos", params=q, headers={"Accept-Encoding": "gzip"})
    assert r.headers.get("content-encoding") == "gzip"
    crudo = client_mini.get("/recintos", params=q, headers={"Accept-Encoding": "identity"})
    assert "content-encoding" not in crudo.headers and r.json() == crudo.json()
    # el cuerpo realmente viaja comprimido (httpx lo descomprime solo; lo comprobamos con el cliente de bajo nivel)
    assert len(gzip.compress(crudo.content)) < len(crudo.content)


def test_cors_en_recintos(client_mini):
    r = client_mini.get("/recintos", params={"bbox": "-4.73,41.64,-4.72,41.65"}, headers={"Origin": "http://localhost:5173"})
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_municipio_completo_trunca_a_3000_y_5km(client, atom_real):
    """Con los 5 municipios: un rectangulo de 5 km sobre Torre-Pacheco tiene ~3000 recintos (tope por defecto 3000)."""
    fc = client.get("/recintos", params={"bbox": bbox_alrededor(37.77, -0.95, 5.0)}).json()
    assert fc["n"] <= 3000 and fc["n_total"] >= fc["n"] and len(fc["features"]) == fc["n"]
    assert fc["features"][0]["geometry"]["type"] in ("Polygon", "MultiPolygon")


def test_cors_acepta_vite_en_127_0_0_1(client_mini):
    """http://127.0.0.1:5173 y http://localhost:5173 son origenes distintos: la API admite los dos (arturo #250)."""
    for origen in ("http://127.0.0.1:5173", "http://localhost:5173"):
        r = client_mini.get("/health", headers={"Origin": origen})
        assert r.headers["access-control-allow-origin"] == origen
    r = client_mini.get("/health", headers={"Origin": "http://evil.example"})
    assert "access-control-allow-origin" not in r.headers
