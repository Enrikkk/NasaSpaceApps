"""Textos de las tarjetas reescritos por un modelo LOCAL (T-022, enrique). Fuera de /analyze: POST /narrativa.

El modelo solo REFORMULA un texto que el motor ya calculo (app.backend.engine.decision.llm_rewrite): un comprobador
determinista rechaza cualquier cifra nueva, cifra que falte, cantidad en letra, promesa o salvedad perdida; tras 3 intentos
fallidos se sirve la plantilla. No hay proveedor externo, ni clave, ni coste: es un Ollama local.

Origen de cada texto, por orden:
  1. `precalculado`: fichero de NARRATIVA_DIR (app/data/cache/narrativa/<sha256 de la plantilla>.json). Sirve en cualquier
     despliegue, tambien sin modelo (Cloud Run). Antes de servirlo se vuelve a pasar el comprobador contra la plantilla
     actual: un fichero viejo o manipulado no puede colar una cifra.
  2. `en_vivo`: solo si OLLAMA_URL esta definida y el modelo instalado (portatil de la demo). Con NARRATIVA_GUARDAR=1 lo
     generado y valido se guarda en NARRATIVA_DIR (asi se precalienta la demo).
  3. `plantilla`: sin modelo ni fichero. La tarjeta muestra el texto determinista de siempre.
"""
import hashlib
import json
import logging
import threading
from pathlib import Path
from typing import Iterable, Optional

from app.backend.engine.decision import llm_rewrite as lr

log = logging.getLogger("agrockham.narrativa")
CAMPOS_DEFECTO = ("por_que",)


def clave(plantilla: str) -> str:
    return hashlib.sha256(plantilla.strip().encode("utf-8")).hexdigest()


class Narrador:
    def __init__(self, directorio: Path, ollama_url: str = "", guardar: bool = False):
        self.dir = Path(directorio)
        self.guardar = guardar
        self._lock = threading.Lock()          # un solo texto a la vez: el modelo local no gana nada con concurrencia
        self.backend: Optional[lr.OllamaBackend] = None
        self.motivo = "sin modelo configurado (OLLAMA_URL no definida)"
        if ollama_url:
            b = lr.OllamaBackend(url=ollama_url)
            ok, por_que = b.available()
            if ok:
                self.backend, self.motivo = b, ""
            else:
                self.motivo = por_que
                log.warning("narrativa en vivo desactivada: %s", por_que)

    def estado(self) -> dict:
        n = len(list(self.dir.glob("*.json"))) if self.dir.is_dir() else 0
        return {"en_vivo": self.backend is not None, "modelo": self.backend.info() if self.backend else None,
                "precalculados": n, "motivo": self.motivo or None}

    def _precalculado(self, plantilla: str) -> Optional[dict]:
        ruta = self.dir / f"{clave(plantilla)}.json"
        if not ruta.is_file():
            return None
        try:
            d = json.loads(ruta.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        texto = d.get("texto")
        if not isinstance(texto, str) or lr.check(plantilla, texto):     # se revalida siempre contra la plantilla actual
            return None
        return {"texto": texto, "valido": True, "origen": "precalculado", "modelo": d.get("modelo"),
                "intentos": d.get("intentos"), "errores": []}

    def _guardar(self, plantilla: str, campo: str, res: dict) -> None:
        try:
            self.dir.mkdir(parents=True, exist_ok=True)
            (self.dir / f"{clave(plantilla)}.json").write_text(json.dumps(
                {"campo": campo, "plantilla": plantilla, "texto": res["texto"], "modelo": res["modelo"],
                 "intentos": res["intentos"], "uso_ia": lr.uso_ia(self.backend)}, ensure_ascii=False, indent=1), encoding="utf-8")
        except OSError as exc:
            log.warning("no se pudo guardar la narrativa: %r", exc)

    def texto(self, plantilla: str, campo: str) -> dict:
        plantilla = (plantilla or "").strip()
        if not plantilla:
            return {"texto": "", "valido": False, "origen": "plantilla", "errores": ["sin texto de plantilla"]}
        pre = self._precalculado(plantilla)
        if pre:
            return pre
        if self.backend is None:
            return {"texto": plantilla, "valido": False, "origen": "plantilla", "errores": [], "motivo": self.motivo}
        with self._lock:
            try:
                res = lr.rewrite_text(plantilla, campo, self.backend)
            except lr.BackendError as exc:
                log.warning("narrativa: el modelo no responde (%s)", exc)
                return {"texto": plantilla, "valido": False, "origen": "plantilla", "errores": [],
                        "motivo": "el modelo local no responde"}
        if res["valido"] and self.guardar:
            self._guardar(plantilla, campo, res)
        return {**res, "origen": "en_vivo" if res["valido"] else "plantilla"}

    def rotacion(self, rot: dict, campos: Optional[Iterable[str]] = None) -> dict:
        campos = [c for c in (campos or CAMPOS_DEFECTO) if c in lr.CAMPOS]
        out = {c: self.texto(lr.template_of(rot, c), c) for c in campos if lr.template_of(rot, c)}
        return {"rotacion": rot.get("id"), "campos": out,
                "uso_ia": (lr.uso_ia(self.backend) if self.backend else
                           {"finalidad": "reformular textos de tarjetas; no calcula", "modelo": None}),
                "aviso": "Texto reescrito por un modelo de lenguaje local a partir de un texto ya calculado. Las cifras se "
                         "comprueban una a una; si la comprobación falla se muestra el texto original."}
