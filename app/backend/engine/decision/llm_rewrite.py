"""LLM rewriter of the card texts (T-022, J3): a local model REWORDS a text that the engine already computed.

The model never computes anything. Pipeline per text:
  1. system prompt (prompts/rewrite_system_es.md: short, plain words, for farmers) + the template + its closed list of figures;
  2. a DETERMINISTIC checker reads the answer: no new figure, no missing figure, no quantity written in words, no
     forbidden promise, every caveat kept, not longer than the template, no markup;
  3. if it fails, the model is told exactly what failed and rewrites; up to MAX_TRIES (3) attempts;
  4. after the third failure the deterministic template is kept (`valido: false`).
The card shows the LLM text only when `valido` is true.

Backends: OllamaBackend (stdlib urllib, POST /api/chat; model from OLLAMA_MODEL, default gpt-oss:20b) and FakeBackend
(tests and --dry-run; no network). Nothing is downloaded: if the model is not installed the run stops and says so.

  python3 -m app.backend.engine.decision.llm_rewrite app/data/torre-pacheco.abierto.json [--dry-run] [--campos por_que,riesgos_texto]
"""
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

from . import texts

HERE = pathlib.Path(__file__).resolve().parent
PROMPT_PATH = HERE / "prompts" / "rewrite_system_es.md"
LOG_DIR = HERE.parents[3] / "data" / "cache" / "llm_log"
MAX_TRIES = 3
MAX_LEN_RATIO = 1.0          # "más corto que la plantilla, nunca más largo"
CAMPOS = ("por_que", "evidencia_resumen", "no_sabemos", "riesgos_texto", "consulta")
CAMPOS_DEFECTO = ("por_que",)
FORBIDDEN = ("garantizado", "garantizada", "seguro que", "sin riesgo", "asegura", "sin duda", "te hará ganar",
             "cumple la ley")
# A caveat of the template must survive the rewrite: if one of these stems is in the template it must be in the answer.
CAVEATS = ("provisional", "supuesto", "proxy", "orientativ", "aproximaci", "no sabemos", "no podemos", "no hemos podido",
           "por verificar", "sin verificar", "simulad", "optimista", "no evaluable")
_WORD_QTY = re.compile(r"\b(la mitad|el doble|el triple|un tercio|un cuarto|por ciento|docena|decena|centenar|millar)\b", re.I)
_MARKUP = re.compile(r"(\*\*|__|^\s*#|^\s*[-*•]\s|`)", re.M)
_CACHE = {}


def system_prompt():
    return PROMPT_PATH.read_text(encoding="utf-8")


def _figures(text):
    """Figures as written, normalised: '3.956' -> '3956', '2,2' -> '2.2'. Order kept, duplicates removed."""
    out = []
    for raw, v, dec in texts._numbers_raw(text):
        key = f"{v:.{dec}f}"
        if key not in out:
            out.append(key)
    return out


def _figures_raw(text):
    seen, out = set(), []
    for raw, v, dec in texts._numbers_raw(text):
        if raw not in seen:
            seen.add(raw)
            out.append(raw)
    return out


def check(template, answer):
    """Deterministic checker. Returns a list of plain-Spanish error messages (empty = the answer may be shown)."""
    errs = []
    a = (answer or "").strip()
    if not a:
        return ["el texto está vacío"]
    low_t, low_a = template.lower(), a.lower()
    allowed, got = _figures(template), _figures(a)
    raw_by_key = {}
    for raw, v, dec in texts._numbers_raw(a):
        raw_by_key.setdefault(f"{v:.{dec}f}", raw)
    for k in got:
        if k not in allowed:
            errs.append(f"la cifra {raw_by_key[k]} no está en la lista de cifras permitidas: quítala o usa una de la lista")
    t_raw = {}
    for raw, v, dec in texts._numbers_raw(template):
        t_raw.setdefault(f"{v:.{dec}f}", raw)
    for k in allowed:
        if k not in got:
            errs.append(f"falta la cifra {t_raw[k]}: la plantilla la lleva y el texto nuevo también debe llevarla, escrita igual")
    for m in texts._WORD_NUM.finditer(a):
        if m.group(1).lower() not in low_t:
            errs.append(f"hay una cantidad escrita con letras («{m.group(1)}»): usa solo cifras de la lista o quítala")
    for m in _WORD_QTY.finditer(a):
        if m.group(1).lower() not in low_t:
            errs.append(f"hay una cantidad escrita con palabras («{m.group(1)}»): no está permitida")
    for w in FORBIDDEN:
        if w in low_a and w not in low_t:
            errs.append(f"aparece la expresión prohibida «{w}»: no prometas resultados ni des consejo legal")
    for c in CAVEATS:
        if c in low_t and c not in low_a:
            errs.append(f"falta una salvedad de la plantilla (la palabra que empieza por «{c}»): el texto nuevo debe conservarla")
    if len(a) > len(template) * MAX_LEN_RATIO:
        errs.append(f"el texto tiene {len(a)} caracteres y la plantilla {len(template)}: debe ser igual de corto o más corto")
    if _MARKUP.search(a):
        errs.append("hay listas, títulos o formato (asteriscos, guiones, almohadillas): devuelve solo frases seguidas")
    if texts._BAD_WORD.search(a):
        errs.append("aparece una palabra técnica vacía (None, null, nan): quítala")
    seen, out = set(), []
    for e in errs:
        if e not in seen:
            seen.add(e)
            out.append(e)
    return out


def _clean(answer):
    a = (answer or "").strip()
    a = re.sub(r"^(salida|texto|respuesta)\s*:\s*", "", a, flags=re.I)
    if len(a) >= 2 and a[0] in "«\"“'" and a[-1] in "»\"”'":
        a = a[1:-1].strip()
    return re.sub(r"\s*\n\s*", " ", a)


# ------------------------------------------------------------------------------------------------------------ backends
class BackendError(RuntimeError):
    pass


class FakeBackend:
    """No network. `answers` = list of strings returned in order; when exhausted (or None) it echoes the template."""
    nombre = "fake"

    def __init__(self, answers=None):
        self.answers = list(answers or [])
        self.calls = []

    def info(self):
        return {"modelo": "fake", "runtime": "ninguno (prueba sin modelo)", "cuantizacion": None}

    def chat(self, messages):
        self.calls.append(messages)
        if self.answers:
            return self.answers.pop(0)
        first = messages[1]["content"]
        return first.split("Texto de plantilla: «", 1)[1].split("»\nCifras permitidas", 1)[0]


class OllamaBackend:
    """Local Ollama server. Only message.content is used (a reasoning model's `thinking` is discarded)."""

    def __init__(self, url=None, model=None, timeout=None):
        self.url = (url or os.getenv("OLLAMA_URL") or "http://127.0.0.1:11434").rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL") or "gpt-oss:20b"
        self.timeout = float(timeout or os.getenv("OLLAMA_TIMEOUT_S") or 300)
        self.think = os.getenv("OLLAMA_THINK", "low" if "gpt-oss" in self.model else "")
        self._details = None

    @property
    def nombre(self):
        return self.model

    def _req(self, path, payload=None, timeout=None):
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(self.url + path, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout or self.timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise BackendError(f"Ollama respondió {e.code}: {e.read().decode('utf-8', 'ignore')[:300]}") from e
        except (urllib.error.URLError, OSError, ValueError) as e:
            raise BackendError(f"Ollama no responde en {self.url}: {e}") from e

    def available(self):
        """(ok, reason). Checks the server and that the model is installed. Never pulls a model."""
        try:
            tags = self._req("/api/tags", timeout=5)
        except BackendError as e:
            return False, str(e)
        for m in tags.get("models", []):
            if self.model in (m.get("name"), m.get("model")) or m.get("name", "").split(":")[0] == self.model:
                self._details = m.get("details") or {}
                return True, ""
        names = ", ".join(m.get("name", "?") for m in tags.get("models", [])) or "ninguno"
        return False, f"el modelo «{self.model}» no está instalado en Ollama (instalados: {names}); no se descarga solo"

    def info(self):
        if self._details is None:
            self.available()
        d = self._details or {}
        return {"modelo": self.model, "runtime": "ollama (local)", "cuantizacion": d.get("quantization_level"),
                "parametros": d.get("parameter_size")}

    def chat(self, messages):
        payload = {"model": self.model, "messages": messages, "stream": False,
                   "options": {"temperature": 0.2, "seed": 2026, "num_ctx": 4096}}
        if self.think:
            payload["think"] = self.think
        try:
            out = self._req("/api/chat", payload)
        except BackendError as e:
            if self.think and "think" in str(e).lower():     # model without a reasoning mode: retry once without it
                self.think = ""
                payload.pop("think")
                out = self._req("/api/chat", payload)
            else:
                raise
        return (out.get("message") or {}).get("content") or ""


# ------------------------------------------------------------------------------------------------------------ pipeline
def _log(entry):
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_DIR / f"{dt.date.today().isoformat()}.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def rewrite_text(template, campo, backend, log=True):
    """One text -> {texto, modelo, intentos, valido, errores}. `texto` is the LLM text if valid, else the template."""
    template = (template or "").strip()
    modelo = backend.info()["modelo"]
    if not template:
        return {"texto": template, "modelo": modelo, "intentos": 0, "valido": False, "errores": ["plantilla vacía"]}
    key = (modelo, campo, hashlib.sha256(template.encode("utf-8")).hexdigest())
    if key in _CACHE:
        return dict(_CACHE[key], cache=True)
    cifras = " · ".join(_figures_raw(template)) or "ninguna (el texto no lleva cifras: no añadas ninguna)"
    messages = [{"role": "system", "content": system_prompt()},
                {"role": "user", "content": f"Campo: {campo}\nTexto de plantilla: «{template}»\nCifras permitidas: {cifras}\n"
                                            "Reescríbelo según tus reglas. Devuelve solo el texto."}]
    trace, errs, answer = [], [], ""
    for attempt in range(1, MAX_TRIES + 1):
        answer = _clean(backend.chat(messages))
        errs = check(template, answer)
        trace.append({"intento": attempt, "respuesta": answer, "errores": errs})
        if not errs:
            break
        messages += [{"role": "assistant", "content": answer},
                     {"role": "user", "content": "Tu texto no se puede usar. Errores encontrados por el comprobador:\n- "
                                                 + "\n- ".join(errs) + "\nReescríbelo corrigiendo exactamente eso y "
                                                 "cumpliendo todas las reglas. Devuelve solo el texto."}]
    ok = not errs
    res = {"texto": answer if ok else template, "modelo": modelo, "intentos": len(trace), "valido": ok,
           "errores": [] if ok else errs}
    if log:
        _log({"cuando": dt.datetime.now().isoformat(timespec="seconds"), "modelo": modelo, "campo": campo,
              "plantilla": template, "intentos": trace, "valido": ok})
    _CACHE[key] = res
    return dict(res)


def template_of(rot, campo):
    """The template text of a field: a string as is; a list of sentences joined into one paragraph."""
    v = (rot.get("texto") or {}).get(campo)
    if isinstance(v, list):
        return " ".join(x.strip() for x in v if isinstance(x, str) and x.strip())
    return v or ""


def rewrite_rotation(rot, backend, campos=CAMPOS_DEFECTO):
    return {c: rewrite_text(template_of(rot, c), c, backend) for c in campos if template_of(rot, c)}


def uso_ia(backend):
    return {**backend.info(), "fecha": dt.date.today().isoformat(), "finalidad": "reformular textos de tarjetas; no calcula",
            "verificacion": f"comprobador determinista de cifras y salvedades; hasta {MAX_TRIES} intentos; si falla, plantilla"}


def apply(doc, backend, campos=CAMPOS_DEFECTO):
    """Add `texto_llm` to every rotation and `_meta.uso_ia`. `texto` (the template) is never modified."""
    for r in doc.get("rotaciones", []):
        r["texto_llm"] = rewrite_rotation(r, backend, campos)
    doc.setdefault("_meta", {})["uso_ia"] = uso_ia(backend)
    return doc


def main(argv):
    if not argv or argv[0].startswith("--"):
        print(__doc__)
        return 2
    path = pathlib.Path(argv[0])
    dry = "--dry-run" in argv
    campos = CAMPOS_DEFECTO
    if "--campos" in argv:
        campos = tuple(c for c in argv[argv.index("--campos") + 1].split(",") if c in CAMPOS)
    backend = FakeBackend() if dry else OllamaBackend()
    if not dry:
        ok, why = backend.available()
        if not ok:
            print("NO SE EJECUTA:", why)
            return 1
    doc = apply(json.load(open(path, encoding="utf-8")), backend, campos)
    out = path.with_suffix(".llm.json")
    json.dump(doc, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    por_intento = {}
    for r in doc["rotaciones"]:
        for c, v in r["texto_llm"].items():
            k = f"válido al intento {v['intentos']}" if v["valido"] else "plantilla (falló)"
            por_intento[k] = por_intento.get(k, 0) + 1
            print(f"\n[{r['id']} · {c}] {k}\n  ANTES:   {template_of(r, c)}\n  DESPUÉS: {v['texto']}")
            for e in v["errores"]:
                print("  error:", e)
    print(f"\nescrito {out} · modelo {backend.info()['modelo']} · {por_intento}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
