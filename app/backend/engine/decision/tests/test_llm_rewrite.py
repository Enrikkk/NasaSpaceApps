"""Tests of the LLM rewriter (T-022, J3) with FakeBackend: no network, no model."""
import copy
import json

import pytest

from app.backend.engine import build as bd
from app.backend.engine.decision import llm_rewrite as lr

T = ("En un año típico dejaría unos 3.956 € por hectárea y año y, en años simulados, sale bien el 73 % de las veces. "
     "Los precios son cotizaciones orientativas de la CARM.")
GOOD = "En un año normal te quedarían unos 3.956 € por hectárea. Sale bien el 73 % de los años simulados. Ojo: precios orientativos."


@pytest.fixture(autouse=True)
def _no_cache_no_log(monkeypatch, tmp_path):
    lr._CACHE.clear()
    monkeypatch.setattr(lr, "LOG_DIR", tmp_path)


def test_checker_accepts_a_valid_rewrite_and_the_template_itself():
    assert lr.check(T, GOOD) == []
    assert lr.check(T, T) == []


@pytest.mark.parametrize("bad, needle", [
    (GOOD.replace("73 %", "75 %"), "la cifra 75 no está"),
    (GOOD.replace("73 %", "75 %"), "falta la cifra 73"),
    (GOOD.replace("3.956", "4.000"), "la cifra 4.000 no está"),
    (GOOD.replace("Sale bien el 73 % de los años simulados.", "Sale bien el 73 % de los años, tres de cada cuatro."), "«tres»"),
    (GOOD.replace("Ojo: precios orientativos.", "Ojo con los precios."), "«orientativ»"),
    (GOOD.replace("Sale bien", "Seguro que sale bien"), "«seguro que»"),
    (GOOD + " Además conviene que lo hables con calma con tu familia antes de decidir nada este año.", "debe ser igual de corto"),
    ("- " + GOOD, "formato"),
    ("", "vacío"),
    (GOOD.replace("el 73 %", "la mitad, el 73 %"), "«la mitad»"),
])
def test_checker_rejects(bad, needle):
    assert any(needle in e for e in lr.check(T, bad)), lr.check(T, bad)


def test_valid_at_first_try():
    b = lr.FakeBackend([GOOD])
    r = lr.rewrite_text(T, "por_que", b)
    assert r == {"texto": GOOD, "modelo": "fake", "intentos": 1, "valido": True, "errores": []}
    assert len(b.calls) == 1 and "3.956 · 73" in b.calls[0][1]["content"]


def test_retry_carries_the_exact_error_back_to_the_model():
    b = lr.FakeBackend([GOOD.replace("73 %", "75 %"), GOOD])
    r = lr.rewrite_text(T, "por_que", b)
    assert r["valido"] and r["intentos"] == 2 and r["texto"] == GOOD
    feedback = b.calls[1][-1]["content"]
    assert "la cifra 75 no está" in feedback and "falta la cifra 73" in feedback
    assert b.calls[1][-2] == {"role": "assistant", "content": GOOD.replace("73 %", "75 %")}


def test_three_failures_keep_the_template():
    b = lr.FakeBackend(["Ganarás 9.999 € seguro."] * 5)
    r = lr.rewrite_text(T, "por_que", b)
    assert r["valido"] is False and r["intentos"] == 3 and r["texto"] == T and r["errores"]
    assert len(b.calls) == 3


def test_answer_is_cleaned_of_quotes_and_prefix():
    r = lr.rewrite_text(T, "por_que", lr.FakeBackend(["Salida: «" + GOOD + "»"]))
    assert r["valido"] and r["texto"] == GOOD


def test_apply_touches_only_texto_llm_and_uso_ia():
    doc = bd.build("torre-pacheco", allow_restricted=False)
    before = copy.deepcopy(doc)
    lr.apply(doc, lr.FakeBackend(), campos=("por_que", "no_sabemos"))
    for r in doc["rotaciones"]:
        tl = r.pop("texto_llm")
        assert set(tl) == {"por_que", "no_sabemos"}
        assert all(v["valido"] and v["texto"] == lr.template_of(r, c) for c, v in tl.items())   # dry run echoes the template
    assert doc["_meta"].pop("uso_ia")["finalidad"].startswith("reformular")
    assert json.dumps(doc, sort_keys=True) == json.dumps(before, sort_keys=True)


def test_every_real_template_passes_its_own_check():
    for restricted in (True, False):
        doc = bd.build("torre-pacheco", allow_restricted=restricted)
        for r in doc["rotaciones"]:
            for c in lr.CAMPOS:
                t = lr.template_of(r, c)
                assert lr.check(t, t) == [], (r["id"], c, lr.check(t, t))


def test_ollama_backend_reports_a_dead_server_without_looping():
    b = lr.OllamaBackend(url="http://127.0.0.1:9", model="x", timeout=1)
    ok, why = b.available()
    assert not ok and "no responde" in why
