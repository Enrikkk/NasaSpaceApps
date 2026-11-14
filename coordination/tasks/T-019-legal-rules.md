---
id: T-019
title: Legal traffic light: Ley 3/2020 Mar Menor + CAP rules table with articles, allowed(prev, cur)
status: doing
owner: gonzalo
branch: t019-legal-rules
paths: app/backend/rules/
depends: T-009
---
Seat (plan): gonzalo. Rules from research/predictive-model-research.md section G (arts. 29, 37, 39, 40, 51, 51.6; BCAM 7; ecorregimen P3).
Deterministic table (CSV/YAML) with article per rule; check(rotation, parcel) -> semaforo_legal{color, motivo, articulo, comprobaciones[]}; allowed(prev, cur) for the DP in T-020.
Zone 1 rules stay amber 'por verificar' until a human confirms the parcel's zone in the BOE Annex I.
Done when: the 3 demo rotations get a colour + article each, with tests. Not legal advice: say so in the output.

- 2026-11-14 16:40 | gonzalo claimed. Prep: research/prototypes/legal_rules/ (rules.csv, grupos_cultivo.csv, legal.py, 31 tests) from research/ley-3-2020-reglas.md. All rules por_verificar until gonzalo checks the BOE; zone 1/2 of the demo parcel still unverified (probably zona 2).
