---
id: T-019
title: Legal traffic light: Ley 3/2020 Mar Menor + CAP rules table with articles, allowed(prev, cur)
status: todo
owner:
branch: t019-legal-rules
paths: app/backend/rules/
depends: T-009
---
Seat (plan): gonzalo. Rules from research/predictive-model-research.md section G (arts. 29, 37, 39, 40, 51, 51.6; BCAM 7; ecorregimen P3).
Deterministic table (CSV/YAML) with article per rule; check(rotation, parcel) -> semaforo_legal{color, motivo, articulo, comprobaciones[]}; allowed(prev, cur) for the DP in T-020.
Zone 1 rules stay amber 'por verificar' until a human confirms the parcel's zone in the BOE Annex I.
Done when: the 3 demo rotations get a colour + article each, with tests. Not legal advice: say so in the output.
