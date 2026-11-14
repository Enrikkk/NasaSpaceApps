"""Clima/suelo en vivo: cache sembrada, descarga simulada, plazo, errores y sin datos. Sin red real."""
import time

import pytest

import live
from conftest import DEMO, VALLADOLID, assert_valido
from vendor import pipeline as P


def test_la_cache_se_siembra_con_la_parcela_demo(client_mini, tmp_path):
    nombres = {f.name for f in (tmp_path / "cache").glob("*.json")}
    assert "soilgrids_15095_-396.json" in nombres and len(nombres) == 4


def test_los_valores_reales_coinciden_con_el_prototipo(client_mini):
    d = client_mini.post("/analyze", json=DEMO).json()
    c, s = d["clima"], d["suelo"]
    assert c["lluvia_anual_mm"]["horquilla"] == [262.3, 366.3] or c["lluvia_anual_mm"]["horquilla"][0] < c["lluvia_anual_mm"]["valor"]
    assert c["dias_helada"]["fuente"] == "pendiente SIAM" and c["dias_helada"]["provisional"] is True
    assert s["fuente_id"] == "soilgrids" and s["agua_disponible_mm"] == pytest.approx(44.9, abs=0.2)
    assert c["metadatos"]["cache"] == {"power_merra2": True, "power_imerg": True, "open_meteo": True}


def test_descarga_en_vivo_simulada_se_guarda_en_cache(client_mini, monkeypatch):
    """Celda nueva con red 'disponible': se llama al pipeline una vez; la segunda peticion sale de la cache."""
    llamadas = []
    modelo = P.build_clima(DEMO["lat"], DEMO["lon"])     # bloque real ya cacheado, usado como respuesta falsa

    def falso(lat, lon):
        llamadas.append((lat, lon))
        return modelo

    monkeypatch.setattr(P, "build_clima", falso)
    d = client_mini.post("/analyze?bloques=clima", json=VALLADOLID).json()
    assert d["clima"]["_status"] == "real" and len(llamadas) == 1
    assert_valido(d)


def test_plazo_vencido_devuelve_cargando_y_sigue_en_segundo_plano(make_client, atom_mini, monkeypatch):
    terminado = []

    def lento(lat, lon):
        time.sleep(0.6)
        terminado.append(1)
        return {"_status": "real"}

    monkeypatch.setattr(P, "build_suelo", lento)
    c = make_client(atom_mini, live_deadline_s=0.1)
    t = time.time()
    d = c.post("/analyze?bloques=suelo", json=VALLADOLID).json()
    assert time.time() - t < 0.5
    assert d["suelo"]["_status"] == "cargando" and "segundo plano" in d["suelo"]["aviso"] and "suelo" in d["_meta"]["bloques_pendientes"]
    assert_valido(d)
    time.sleep(0.8)
    assert terminado == [1]      # el hilo termino y dejaria la cache lista


@pytest.mark.parametrize("excepcion,texto,sin_datos", [
    (ValueError("SoilGrids sin datos"), "sin datos en este punto", True),
    (RuntimeError("api.example: agotados los reintentos: URLError('secreto-interno')"), "servicio externo no disponible", False),
])
def test_errores_del_pipeline_no_tumban_ni_filtran(client_mini, monkeypatch, excepcion, texto, sin_datos):
    def falla(lat, lon):
        raise excepcion

    monkeypatch.setattr(P, "build_suelo", falla)
    d = client_mini.post("/analyze", json=DEMO).json()
    assert d["suelo"]["_status"] == "cargando" and texto in d["suelo"]["aviso"]
    assert "secreto-interno" not in str(d)
    assert d["clima"]["_status"] == "real" and d["parcela"]["_status"] == "precalculado"
    assert ("bloques_sin_datos" in d["_meta"] and "suelo" in d["_meta"]["bloques_sin_datos"]) == sin_datos
    assert_valido(d)


def test_limites_de_red_acotados_para_api(client_mini):
    # live.preparar sustituye los valores por defecto del pipeline (120 s / 4 reintentos / hasta 130 s de espera)
    timeout, retries, backoff, _ = P.http_get_json.__defaults__
    assert timeout == 40 and retries == 1 and sum(backoff) <= 15
