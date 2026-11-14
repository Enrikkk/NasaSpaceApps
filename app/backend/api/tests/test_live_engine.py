"""Motor EN VIVO por parcela (ENGINE_MODE=vivo, engine_adapter.LiveEngine, H-002) y POST /narrativa. Sin red.

Usan la muestra de 66 recintos de la parcela demo (atom_mini) y la cache de clima/suelo sembrada.
"""
import json

from app.backend.api import engine_adapter as EA, narrativa
from app.backend.engine.decision import llm_rewrite as lr
from api_helpers import DEMO, DEMO_RECINTO, VALLADOLID, assert_valido


def _vivo(make_client, atom_mini, **extra):
    return make_client(atom_mini, engine_mode="vivo", **extra)


def test_por_defecto_no_es_en_vivo_y_vivo_es_abierto(make_client, atom_mini):
    assert "en vivo" not in make_client(atom_mini).get("/health").json()["motor"]
    c = _vivo(make_client, atom_mini)
    assert c.get("/health").json()["motor"] == EA.LiveEngine.nombre
    doc = c.post("/analyze", json={**DEMO, "recinto": DEMO_RECINTO, "zona": "zona_2"}).json()
    blob = json.dumps(doc, ensure_ascii=False).lower()
    assert "carm-anuario" not in blob            # D-010: sin precios CARM salvo ENGINE_PRECIOS=carm explicito
    assert any(f["id"].startswith("MAPA-PER") for f in doc["fuentes"])


def test_analyze_en_vivo_cumple_el_contrato_y_trae_bloques_por_parcela(make_client, atom_mini):
    c = _vivo(make_client, atom_mini)
    r = c.post("/analyze", json={**DEMO, "recinto": DEMO_RECINTO, "zona": "zona_2"})
    assert r.status_code == 200
    doc = r.json()
    assert_valido(doc)
    assert doc["_meta"]["motor"] == EA.LiveEngine.nombre
    assert doc["_meta"]["rotaciones_referencia"]["por_parcela"] is True
    assert not any("parcela de referencia (Torre-Pacheco" in a for a in doc["_meta"].get("avisos", []))
    assert len(doc["rotaciones"]) >= 3
    for rot in doc["rotaciones"]:
        assert rot["ambiente"]["nivel"] in ("alto", "medio", "bajo")
        assert "factor_puntuacion" in rot["idoneidad"]
        assert rot["texto"]["por_que"]
        assert rot["semaforo_legal"]["color"] in ("verde", "amarillo", "rojo", "gris")
    assert doc["idoneidad"]["frases"] and doc["clima_origen"]["estacion"]
    assert doc["actual_origen"] in ("declaracion_fega", "supuesto_zona")
    assert doc["escenarios_meta"]["alineados"] is True
    assert c.get(f"/parcel/{doc['_meta']['consulta_id']}").json()["idoneidad"] == doc["idoneidad"]


def test_punto_sin_recinto_sigue_dando_rotaciones_y_dice_lo_que_no_sabe(make_client, atom_mini):
    doc = _vivo(make_client, atom_mini).post("/analyze", json=VALLADOLID).json()
    assert_valido(doc)
    assert "regadio" in doc["idoneidad"]["sin_dato"] and "pendiente_pct" in doc["idoneidad"]["sin_dato"]
    assert doc["clima_origen"]["lejos"] is True
    ref = doc["_meta"]["rotaciones_referencia"]       # sin recinto no se afirma "calculado para esta parcela"
    assert not ref.get("por_parcela")
    assert ref["aplica_a_esta_parcela"] is False
    assert any("no un calculo de esta parcela" in a for a in doc["_meta"]["avisos"])


def test_secano_es_no_evaluable(make_client, atom_mini, monkeypatch):
    from app.backend.api import parcel_input
    real = parcel_input.construir
    monkeypatch.setattr(parcel_input, "construir", lambda ctx: {**real(ctx), "regadio": False})
    doc = _vivo(make_client, atom_mini).post("/analyze", json={**DEMO, "recinto": DEMO_RECINTO}).json()
    assert doc["rotaciones"] == []
    assert "secano" in doc["no_evaluable"]["motivo"]


def test_si_el_motor_falla_cae_al_motor_anterior_y_lo_avisa(make_client, atom_mini, monkeypatch):
    c = _vivo(make_client, atom_mini)
    eng = c.app.state.servicio.engine
    monkeypatch.setattr(eng._build, "run_parcel", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("roto")))
    doc = c.post("/analyze", json={**DEMO, "recinto": DEMO_RECINTO}).json()
    assert_valido(doc)
    assert len(doc["rotaciones"]) >= 1
    assert any("ha fallado" in a for a in doc["_meta"]["avisos"])
    assert "idoneidad" not in doc


def test_precios_carm_solo_con_variable_explicita(make_client, atom_mini):
    c = _vivo(make_client, atom_mini, engine_precios="carm")
    doc = c.post("/analyze", json={**DEMO, "recinto": DEMO_RECINTO}).json()
    assert any(f["id"] == "CARM-ANUARIO" for f in doc["fuentes"])


# ------------------------------------------------------------------------------------------------------------ /narrativa
def _analizar(c):
    doc = c.post("/analyze", json={**DEMO, "recinto": DEMO_RECINTO, "zona": "zona_2"}).json()
    return doc, doc["_meta"]["consulta_id"], doc["rotaciones"][0]


def test_narrativa_sin_modelo_devuelve_la_plantilla(make_client, atom_mini, tmp_path):
    c = _vivo(make_client, atom_mini, narrativa_dir=tmp_path / "n")
    doc, qid, rot = _analizar(c)
    r = c.post("/narrativa", json={"id": qid, "rotacion": rot["id"]}).json()
    campo = r["campos"]["por_que"]
    assert campo == {"texto": rot["texto"]["por_que"], "valido": False, "origen": "plantilla", "errores": [],
                     "motivo": "sin modelo configurado (OLLAMA_URL no definida)"}
    assert c.get("/health").json()["narrativa"]["en_vivo"] is False


def test_narrativa_precalculada_se_sirve_solo_si_pasa_el_comprobador(make_client, atom_mini, tmp_path):
    d = tmp_path / "n"
    d.mkdir()
    c = _vivo(make_client, atom_mini, narrativa_dir=d)
    doc, qid, rot = _analizar(c)
    plantilla = rot["texto"]["por_que"]
    ruta = d / f"{narrativa.clave(plantilla)}.json"
    ruta.write_text(json.dumps({"texto": plantilla, "modelo": "prueba", "intentos": 1}), encoding="utf-8")
    campo = c.post("/narrativa", json={"id": qid, "rotacion": rot["id"]}).json()["campos"]["por_que"]
    assert campo["valido"] is True and campo["origen"] == "precalculado" and campo["modelo"] == "prueba"
    ruta.write_text(json.dumps({"texto": "Ganarás 99.999 € seguro.", "modelo": "prueba"}), encoding="utf-8")
    campo = c.post("/narrativa", json={"id": qid, "rotacion": rot["id"]}).json()["campos"]["por_que"]
    assert campo["valido"] is False and campo["texto"] == plantilla      # fichero manipulado: no se sirve


def test_narrativa_en_vivo_con_modelo_simulado_y_guardado(make_client, atom_mini, tmp_path, monkeypatch):
    d = tmp_path / "n"
    c = _vivo(make_client, atom_mini, narrativa_dir=d)
    nar = c.app.state.narrador
    fake = lr.FakeBackend()
    monkeypatch.setattr(lr, "LOG_DIR", tmp_path / "log")
    lr._CACHE.clear()
    nar.backend, nar.guardar = fake, True
    doc, qid, rot = _analizar(c)
    r = c.post("/narrativa", json={"id": qid, "rotacion": rot["id"], "campos": ["por_que", "no_sabemos"]}).json()
    assert set(r["campos"]) == {"por_que", "no_sabemos"}
    assert all(v["valido"] and v["origen"] == "en_vivo" for v in r["campos"].values())
    assert len(list(d.glob("*.json"))) == 2
    nar.backend = None                              # sin modelo: ahora sale del fichero guardado
    again = c.post("/narrativa", json={"id": qid, "rotacion": rot["id"]}).json()["campos"]["por_que"]
    assert again["origen"] == "precalculado" and again["valido"]


def test_narrativa_404_y_422(make_client, atom_mini):
    c = _vivo(make_client, atom_mini)
    assert c.post("/narrativa", json={"id": "no-existe", "rotacion": "s1"}).status_code == 404
    _, qid, _ = _analizar(c)
    assert c.post("/narrativa", json={"id": qid, "rotacion": "no-existe"}).status_code == 404
    assert c.post("/narrativa", json={"id": qid, "rotacion": "s1", "campos": ["otro"]}).status_code == 422
