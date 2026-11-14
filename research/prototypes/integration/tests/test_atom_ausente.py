"""Si los GeoJSON de ATOM no estan, la API arranca igualmente y avisa (no se cae)."""
from conftest import DEMO, assert_valido


def test_directorio_inexistente(make_client, tmp_path):
    c = make_client(tmp_path / "no_existe")
    h = c.get("/health").json()
    assert h["status"] == "ok" and h["recintos"]["cargado"] is False and h["recintos"]["n"] == 0
    assert "no cargados" in h["avisos"][0]
    assert "no_existe" not in str(h)       # no se filtra la ruta del servidor
    r = c.get("/recintos", params={"bbox": "-1,37,-0.99,37.01"})
    assert r.status_code == 503
    d = c.post("/analyze", json=DEMO).json()
    assert d["parcela"]["_status"] == "cargando" and d["parcela"]["sin_cobertura"] is True
    assert d["_meta"]["cobertura"]["nivel"] == "basico" and any("no cargados" in a for a in d["_meta"]["avisos"])
    assert d["clima"]["_status"] == "real"            # clima y suelo no dependen del ATOM
    assert_valido(d)


def test_directorio_vacio(make_client, tmp_path):
    d = tmp_path / "vacio"
    d.mkdir()
    c = make_client(d)
    assert c.get("/health").json()["recintos"]["cargado"] is False


def test_fichero_corrupto_no_tumba_el_arranque(make_client, tmp_path):
    d = tmp_path / "roto"
    d.mkdir()
    (d / "30037_recintos.geojson.gz").write_bytes(b"esto no es gzip")
    c = make_client(d)
    assert c.get("/health").json()["recintos"]["cargado"] is False
