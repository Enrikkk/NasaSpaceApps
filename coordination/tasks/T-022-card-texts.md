---
id: T-022
title: Card texts: templates from the evidence pack (LLM narrator + number validator only if time, P2)
status: todo
owner:
branch: t022-card-texts
paths: app/backend/engine/explain/
depends: T-020
---
Seat (plan): enrique. Per rotation: por_que, evidencia, beneficios, huecos, riesgos, 'consulta a tu tecnico', in plain Spanish for a non-technical farmer (and English for the video).
Default: string templates filled from the JSON. P2: LLM at build time, reading ONLY the evidence pack, with a validator that rejects any number not in the pack. Removing the LLM must not break anything.
