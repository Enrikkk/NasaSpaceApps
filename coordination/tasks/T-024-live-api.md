---
id: T-024
title: Live API (FastAPI): /analyze, /parcel, /recintos, /health (D-009), Cloud Run packaging
status: review
owner: gonzalo
branch: t024-live-api
paths: app/backend/api/
depends: T-009
---
D-009 (accepted by jaime): live backend + SIGPAC globe. Prep prototype with 82 tests in research/prototypes/integration/ (ATOM recintos, clima/suelo con cache, semaforo legal, engine_adapter for enrique's JSON). Moves to app/backend/api/.
Coordinates with arturo (T-017: Dockerfile, health, CORS, port) and enrique (T-020: engine as function or JSON via engine_adapter). GCP project agrockham-nasa-2026 ready (billing, 50 EUR alert).
Done when: POST /analyze returns the contract by blocks for the demo parcel and any recinto in the covered municipalities; deployed on Cloud Run.

- 2026-11-14 16:40 | gonzalo claimed (new task, next free number).

- 2026-11-14 18:15 | merged into main (t024-live-api, 80 tests OK): app/backend/api/ (/health, /analyze, /parcel, /recintos). Next: Cloud Run deploy (agrockham-api, europe-west1).
