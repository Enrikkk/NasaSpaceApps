---
id: T-017
title: Deployment preparation and preloaded demo fallback (D-009)
status: doing
owner: arturo
branch: t017-offline-deploy
paths: scripts/deploy.sh, scripts/t017_smoke.py, coordination/deploy/, coordination/tasks/T-017-offline-deploy.md
depends: T-009, T-010, T-020, T-024
---
D-009 ACCEPTED supersedes the original static-only implementation: live FastAPI/Cloud Run backend and SIGPAC globe; internet is required for live queries, with a preloaded demo parcel as fallback. Full offline queries are not promised.

Current human authorization (Arturo, 2026-11-14): prepare/review isolated local checks and a reproducible execution plan. Do not deploy, create GCP resources/billing, or select/change the global licence. Gonzalo manages GCP and owns the API/Docker/dependencies. Jaime owns frontend source and build output. Actual publication remains a separate concrete human action.

Acceptance for this preparation increment:
- Check API build context, seed data, contract, Docker inputs and local smoke prerequisites with a reproducible command.
- Record exact frontend/API/engine commits and unresolved integration dependencies; distinguish sample/demo output from a point-specific engine.
- Verify offline fallback prerequisites without claiming the whole demo is finished.
- Provide an execution checklist for Gonzalo/human, keeping remote mutations outside the preparation script.

- 2026-11-14 13:20 | plan v1 (coordination/PLAN.md): Seat (plan): arturo. Sun 14:00-19:00.

- 2026-11-14 | arturo: claimed local preparation after explicit authorization; base origin/main b48ebae includes API, contract/pipeline/rules. Frontend currently only design assets; API 5d49ea0 README documents sample defaults and a separate engine-JSON adapter. Docker/gcloud unavailable on this laptop. Requests sent to Gonzalo #156 and orchestrator/Jaime #157; no deploy or licence change.

- 2026-11-14 17:12 | arturo: #166 smoke handoff implemented in scripts/t017_smoke.py (scripts scope agreed); API main2ec59e1 + motor473f2c2 JSON abierto passes13 checks locally with AGROCKHAM_OFFLINE=1,66recintos sample and producer contract validator. New source inspector profiles/negative checks pass. Docker-mode runner supplied (--pull=never/--network none/read-only mounts); not executed on this laptop. Gonzalo #169 reports Docker API-only checks with50368recintos; clarification #172 asks engine selection and schema evidence. Frontend/production origin/browser fallback remain absent. No deploy or global licence change; task remains doing.

- 2026-11-14T17:15:49+01:00 | arturo: #176 closes #166 integration increment. Gonzalo reran Docker02e4b89 with openengine473f2c2; preserved artifactc281ac1 hash6a6f934bc1b2cbbdfa5356bd93ee800184c5651e057dbf5bc6b92a772ed540d5 independently checked and producer validator passed0errors/0failedinvariants/3warnings. JSONEnrique/noDraft confirmed. Warnings sentEnrique#178. No new Docker run on Arturo. T017 stays doing: frontend build/APIorigin/browserfallback still need Jaime package.

- 2026-11-14 | arturo: lectura frontend publicado integracion393ef24 (React/Vite/base relativo). Desbloquea candidato estático; build/QA los realiza Desktop, no repetidos aquí. Pendientes precisos clienteAPIbase/origen CORS coherente127vs localhost y fallbackdemoficha etiquetado; solicitado Jaime/Gonzalo porbus. T017 sigue en curso, demo no acreditada.
