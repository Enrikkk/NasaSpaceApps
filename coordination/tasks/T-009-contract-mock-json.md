---
id: T-009
title: Data contract + mock parcel JSON (unblocks UI and engine)
status: doing
owner: gonzalo
branch: t009-contract-mock-json
paths: app/data/, app/README.md
depends: 
---
Fix the JSON contract described in `brainstorm/field-shift-plan.md` and the factor model in `brainstorm/pizarra-2026-11-14.md`
and publish `app/data/torre-pacheco.mock.json` (already drafted, see `app/README.md`). Everyone codes against it.
Done when: backend, engine and UI owners have read it and agreed (or amended it) by Sat 10:30.

- 2026-11-14 13:20 | plan v1 (coordination/PLAN.md): Seat (plan): gonzalo. Contract v1 frozen Sat 14:30: extend the mock with the fields listed in coordination/PLAN.md section 2 (exito_pct with Wilson band, margen p10/p50/p90, agua_detalle, criterios 0-1, escenarios[], semaforo comprobaciones[], sobreoferta_detalle, inversion, variantes, _status per block). Add a JSON Schema (app/data/contract.schema.json). Rename product to Agrockham in app/README.md. After 14:30 only add fields; changes go to the bus (to: all).

- 2026-11-14 16:40 | gonzalo claimed (option agreed in chat; jaime already working on T-010). Prep is done in research/ (b4807a5, 2e1b93c, 18e8275): contract v1/v1.1 + schema + validator in research/contract-v1-draft/, then moves to app/data/.
