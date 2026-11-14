---
id: T-017
title: Deployment preparation and preloaded demo fallback (D-009)
status: doing
owner: arturo
branch: t017-offline-deploy
paths: scripts/deploy.sh, coordination/deploy/, coordination/tasks/T-017-offline-deploy.md
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
