---
id: T-027
title: Pure parcel suitability and environmental labels
status: doing
owner: arturo
branch: arturo-idoneidad
paths: app/backend/engine/suitability/
depends: T-020
---
Enrique H-002, bus #212/#213/#214/#221; base t020-jaime57561e9.
Only new suitability directory: sourced/licensed rule table, pure evaluar and
etiqueta_ambiental, >=15 meaningful cases. Exclude impossible irrigation crops
on dryland; numeric penalties affect scores only and are labelled supuesto when
not established by source. Missing data neutral with explicit unknowns. Audit
existing dryland economics without editing other engine/data paths. Deliver hash,
source/licence matrix and real pytest exit code. No main merge or deploy.

- 2026-11-14: claimed before implementation, handoff read at t01227f9430.
