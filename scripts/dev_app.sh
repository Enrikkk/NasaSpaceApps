#!/usr/bin/env bash
# Agrockham integrada en local: API (motor en vivo por parcela) en :8080. El frontend se arranca aparte (ver abajo).
#   bash scripts/dev_app.sh            # API con el motor en vivo, precios abiertos
#   ENGINE_PRECIOS=carm bash scripts/dev_app.sh    # solo en local: precios CARM (permiso pendiente, no publicar)
#   OLLAMA_URL=http://127.0.0.1:11434 OLLAMA_MODEL=gpt-oss:20b NARRATIVA_GUARDAR=1 bash scripts/dev_app.sh   # textos del LLM en vivo
# Frontend, en otra terminal:  cd app/frontend && npm install && npm run dev   -> http://127.0.0.1:5173
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${AGROCKHAM_PY:-$HOME/.venvs/agrockham-api/bin/python}"
[ -x "$PY" ] || { echo "Falta el entorno de Python: python3 -m venv ~/.venvs/agrockham-api && ~/.venvs/agrockham-api/bin/pip install -r app/backend/api/requirements-dev.txt"; exit 1; }
if [ -z "${ATOM_BUILD_DIR:-}" ] && [ ! -d app/backend/api/atom_build ]; then
  # Sin los recintos completos (no van en git): muestra de 66 recintos alrededor de la parcela demo, la misma de los tests.
  export ATOM_BUILD_DIR="${TMPDIR:-/tmp}/agrockham-atom-mini"
  "$PY" - "$ATOM_BUILD_DIR" <<'PYEOF'
import gzip, json, pathlib, sys
d = pathlib.Path(sys.argv[1]); d.mkdir(parents=True, exist_ok=True)
fc = json.loads(pathlib.Path("app/data/cache/pipeline/atom/torre-pacheco_demo_viewport.geojson").read_text(encoding="utf-8"))
with gzip.open(d / "30037_recintos.geojson.gz", "wt", encoding="utf-8") as fh:
    fh.write('{"type":"FeatureCollection","features":[\n' + ",\n".join(json.dumps(f, separators=(",", ":")) for f in fc["features"]) + "\n]}\n")
xs = [c[0] for f in fc["features"] for c in f["geometry"]["coordinates"][0]]
ys = [c[1] for f in fc["features"] for c in f["geometry"]["coordinates"][0]]
(d / "30037.index.json").write_text(json.dumps({"codigo": "30037", "municipio": "Torre-Pacheco", "bbox": [min(xs), min(ys), max(xs), max(ys)]}))
print(f"AVISO: recintos de muestra ({len(fc['features'])}) en {d}; fuera de esa zona /analyze no encuentra parcela.")
PYEOF
fi
export ENGINE_MODE="${ENGINE_MODE:-vivo}"
export FRONTEND_ORIGIN="${FRONTEND_ORIGIN:-http://127.0.0.1:5173}"
exec "$PY" -m uvicorn app.backend.api.main:app --host 127.0.0.1 --port "${PORT:-8080}"
