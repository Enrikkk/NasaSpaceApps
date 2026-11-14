"""Recintos SIGPAC en memoria (GeoJSON del ATOM del FEGA) y cobertura por municipio.

Envuelve `app.backend.pipeline.atom.lookup`. Si el directorio no existe o esta vacio, la API arranca
igualmente con `Atom.cargado = False` y los endpoints avisan (D-009: el globo y /analyze degradan, no se caen).
"""
import glob
import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Optional

from app.backend.pipeline.atom.lookup import ATTRIBUTION, RecintoIndex

log = logging.getLogger("agrockham.store")

COMPONENTES = ("provincia", "municipio", "agregado", "zona", "poligono", "parcela", "recinto")
ATRIBUCION_LARGA = (ATTRIBUTION + " Licencia CC BY 4.0. Datos transformados por Agrockham (unidades, redondeo a 6 decimales); "
                    "campana 2026, validez 2025-12-15. Sin respaldo ni patrocinio del FEGA.")


class Recintos(RecintoIndex):
    """RecintoIndex mas: GeoJSON por bbox con tope y total (para avisar de truncado)."""

    def bbox_geojson(self, bbox, limit: int) -> tuple[str, int, int]:
        """(FeatureCollection como str JSON, n_total, n_devueltos). Reutiliza las lineas ya serializadas."""
        ids = self._indices_bbox(bbox)
        total = len(ids)
        usados = ids[:limit]
        cuerpo = ",".join(self._lines[i] for i in usados)
        fc = ('{"type":"FeatureCollection","attribution":' + json.dumps(ATRIBUCION_LARGA, ensure_ascii=False)
              + f',"n_total":{total},"n":{len(usados)},"truncado":{"true" if total > len(usados) else "false"}'
              + ',"features":[' + cuerpo + "]}")
        return fc, total, len(usados)


@dataclass
class Atom:
    dir: str
    index: Optional[Recintos] = None
    municipios: list[dict] = field(default_factory=list)  # [{codigo, municipio, bbox}]
    segundos_carga: float = 0.0
    error: Optional[str] = None

    @property
    def cargado(self) -> bool:
        return self.index is not None and len(self.index) > 0

    def en_cobertura(self, lat: float, lon: float) -> bool:
        """Dentro de la caja de algun municipio cargado (aproximacion: no es el limite administrativo)."""
        return any(m["bbox"][0] <= lon <= m["bbox"][2] and m["bbox"][1] <= lat <= m["bbox"][3] for m in self.municipios)

    def nombres(self) -> list[str]:
        return [m.get("municipio") or m["codigo"] for m in self.municipios]


def cargar(directorio) -> Atom:
    """Carga todos los *_recintos.geojson.gz de `directorio`. Nunca lanza: devuelve un Atom con `error`."""
    directorio = str(directorio)
    atom = Atom(dir=directorio)
    if not os.path.isdir(directorio):
        atom.error = "directorio de recintos inexistente"
        log.warning("ATOM: %s: %s (la API arranca sin recintos)", atom.error, directorio)
        return atom
    t0 = time.perf_counter()
    try:
        atom.index = Recintos.load(directorio)
    except FileNotFoundError:
        atom.error = "sin ficheros *_recintos.geojson.gz"
        log.warning("ATOM: %s en %s (la API arranca sin recintos)", atom.error, directorio)
        return atom
    except Exception as exc:  # fichero corrupto, etc.: no tumbar la API
        atom.error = f"error al cargar recintos ({type(exc).__name__})"
        log.error("ATOM: %s en %s: %s", atom.error, directorio, exc)
        return atom
    atom.segundos_carga = round(time.perf_counter() - t0, 2)
    for ip in sorted(glob.glob(os.path.join(directorio, "[0-9]*.index.json"))):
        try:
            with open(ip, encoding="utf-8") as fh:
                d = json.load(fh)
            atom.municipios.append({"codigo": d["codigo"], "municipio": d.get("municipio"), "bbox": d["bbox"]})
        except (OSError, ValueError, KeyError) as exc:
            log.warning("ATOM: indice ilegible %s: %s", ip, exc)
    log.info("ATOM: %d recintos, %d municipios, %.2f s", len(atom.index), len(atom.municipios), atom.segundos_carga)
    return atom
