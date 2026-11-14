"""Fixtures. Por defecto SIN red (AGROCKHAM_OFFLINE=1) y con la cache de la parcela demo.

Se ejecutan desde la raiz del repo:  python -m pytest app/backend/api   (pytest.ini pone la raiz en el PYTHONPATH)

Variables de los tests:
  ATOM_BUILD_DIR   directorio con los GeoJSON de ATOM de los municipios completos (si no existe, esos tests se omiten y
                   el resto usa la muestra de 66 recintos de app/data/cache/pipeline/atom)
  ENRIQUE_JSON     JSON de enrique para probar el adaptador (si no, esos tests se omiten)
  TEST_LIVE=1      permite la red real
"""
import gzip
import json
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))   # raiz del repo (por si se invoca sin pytest.ini)

from app.backend.api import main, settings  # noqa: E402
from api_helpers import SAMPLE  # noqa: E402


# ---------------------------------------------------------------------------------------------- datos ATOM
def _atom_dir_real():
    d = Path(os.environ.get("ATOM_BUILD_DIR") or settings.ATOM_BUILD_DIR_DEFECTO)
    return d if d.is_dir() and list(d.glob("*_recintos.geojson.gz")) else None


@pytest.fixture(scope="session")
def atom_real():
    d = _atom_dir_real()
    if d is None:
        pytest.skip("sin ATOM_BUILD_DIR con los municipios completos")
    return d


@pytest.fixture(scope="session")
def atom_mini(tmp_path_factory):
    """Muestra de 66 recintos alrededor de la parcela demo, en el formato de build_recintos.py."""
    d = tmp_path_factory.mktemp("atom_mini")
    fc = json.loads(SAMPLE.read_text(encoding="utf-8"))
    lines = [json.dumps(f, separators=(",", ":")) for f in fc["features"]]
    with gzip.open(d / "30037_recintos.geojson.gz", "wt", encoding="utf-8") as fh:
        fh.write('{"type":"FeatureCollection","features":[\n' + ",\n".join(lines) + "\n]}\n")
    xs = [c[0] for f in fc["features"] for c in f["geometry"]["coordinates"][0]]
    ys = [c[1] for f in fc["features"] for c in f["geometry"]["coordinates"][0]]
    (d / "30037.index.json").write_text(json.dumps({"codigo": "30037", "municipio": "Torre-Pacheco", "bbox": [min(xs), min(ys), max(xs), max(ys)]}))
    return d


@pytest.fixture(autouse=True)
def sin_red(monkeypatch):
    """Los tests no tocan la red salvo TEST_LIVE=1."""
    if os.environ.get("TEST_LIVE") != "1":
        monkeypatch.setenv("AGROCKHAM_OFFLINE", "1")


def _cfg(tmp_path, atom_dir, **extra):
    base = dict(atom_build_dir=Path(atom_dir), pipeline_cache_dir=tmp_path / "cache")
    base.update(extra)
    return settings.Settings(**base)


@pytest.fixture
def make_client(tmp_path):
    """Fabrica de clientes con configuracion propia: make_client(atom_dir, **ajustes)."""
    abiertos = []

    def _make(atom_dir, **extra):
        cm = TestClient(main.create_app(_cfg(tmp_path, atom_dir, **extra)))
        abiertos.append(cm)
        return cm.__enter__()

    yield _make
    for cm in abiertos:
        cm.__exit__(None, None, None)


@pytest.fixture
def client(make_client, atom_real):
    return make_client(atom_real)


@pytest.fixture
def client_mini(make_client, atom_mini):
    return make_client(atom_mini)
