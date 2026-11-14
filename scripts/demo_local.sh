#!/usr/bin/env bash
# Agrockham completa en un portatil: API (motor en vivo) + frontend + textos del modelo local (si hay Ollama).
#   bash scripts/demo_local.sh            # arranca la API en :8080 y el frontend en :5173
# Antes (una sola vez): entorno de Python y, para el texto del modelo, Ollama con el modelo ya descargado:
#   python3 -m venv ~/.venvs/agrockham-api && ~/.venvs/agrockham-api/bin/pip install -r app/backend/api/requirements-dev.txt
#   ollama pull gpt-oss:20b          # ~13 GB; sin el, la ficha muestra el texto de plantilla de siempre
# Variables opcionales: OLLAMA_MODEL (def. gpt-oss:20b), ENGINE_PRECIOS=carm (solo local, no publicar), ATOM_BUILD_DIR.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"
OLLAMA="${OLLAMA_URL:-http://127.0.0.1:11434}"
if curl -s -m 3 "$OLLAMA/api/tags" >/dev/null 2>&1; then
  if [ -z "${OLLAMA_MODEL:-}" ]; then   # el nombre varia entre portatiles (gpt-oss:20b, gpt-oss-20b:latest...): se usa el primero que contenga "gpt-oss"
    OLLAMA_MODEL="$(curl -s -m 3 "$OLLAMA/api/tags" | python3 -c 'import json,sys; n=[m["name"] for m in json.load(sys.stdin).get("models",[]) if "gpt-oss" in m["name"]]; print(n[0] if n else "gpt-oss:20b")' 2>/dev/null || echo gpt-oss:20b)"
  fi
  export OLLAMA_URL="$OLLAMA" OLLAMA_MODEL NARRATIVA_GUARDAR=1
  echo "Ollama detectado en $OLLAMA (modelo $OLLAMA_MODEL): textos del modelo activados (se guardan los validos)."
else
  echo "AVISO: no hay Ollama en $OLLAMA: la ficha mostrara los textos de plantilla (sin reescritura del modelo)."
fi
bash scripts/dev_app.sh > "${TMPDIR:-/tmp}/agrockham-api.log" 2>&1 &
API_PID=$!
trap 'kill $API_PID 2>/dev/null || true' EXIT
for i in $(seq 1 30); do curl -s -m 2 http://127.0.0.1:8080/health >/dev/null 2>&1 && break; sleep 1; done
curl -s -m 5 http://127.0.0.1:8080/health | head -c 400; echo
cd "$ROOT/app/frontend"
[ -d node_modules ] || npm install
echo "Abre http://127.0.0.1:5173  -> 'Ir a mis parcelas' -> clic en un recinto. API log: ${TMPDIR:-/tmp}/agrockham-api.log"
npm run dev
