---
id: T-020
title: Decision layer: rotation DP (current + >=2), normalised criteria, scenario samples, slider variants -> torre-pacheco.json
status: todo
owner:
branch: t020-decision-layer
paths: app/backend/engine/decision/, app/data/torre-pacheco.json
depends: T-012, T-018, T-019
---
Seat (plan): enrique. Strategies: S0 current (melon -> fallow -> lettuce), S1 max expected margin under rules, S2 soil/water (legume or cover in every bare window), S3 low risk optional.
Export per rotation: criterios{margen, agua, suelo_n, riesgo} normalised 0-1, ~200 margin scenario samples (escenarios[]), evidencia[] (dataset, valor, url, escala), huecos[], riesgos[].
Export variantes for the UI sliders: lluvia -30/-15/0/+10 %, temp +0/+1/+2 C, 2050 (simulated deltas, labelled). The UI does the weighting and 'B wins X %' itself.
Done when: `python3 -m app.backend.engine.build torre-pacheco` writes app/data/torre-pacheco.json that validates against the T-009 contract.
