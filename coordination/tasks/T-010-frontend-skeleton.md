---
id: T-010
title: Frontend: map -> parcel card -> priorities -> rotation comparator
status: doing
owner: jaime
branch: t010-frontend-skeleton
paths: app/frontend/
depends: T-009
---
React + Vite + MapLibre (or what the owner knows). Reads only the JSON contract. Screens in plain language for a
non-technical farmer (max 4 screens): 1 map + parcel card, 2 'your parcel's past' timeline (crops + bare months),
3 priorities (sliders: profit, water, soil, risk), 4 comparator: current rotation + 2 alternatives as cards with
success %, EUR/ha, water, legal traffic light, 'why / evidence / what we don't know / ask your technician'.
Works first on the mock JSON. Add a 'what if' slider (rain/temperature) and a '2050' toggle if time allows.

- 2026-11-14 13:20 | plan v1 (coordination/PLAN.md): Seat (plan): jaime. Split: 10a Vite+React+MapLibre skeleton, map (PNOA) + parcel card; 10b timeline 2017-2026 with bare months; 10c priorities sliders + comparator cards, weighting and 'B gana X %' computed in the browser from criterios + escenarios; 10d (P2) what-if / 2050 variants + sensor panel. Labels real/precalculado/simulado from _status. Static build, no server.
- 2026-11-14 16:23 | jaime: claimed. First step: static prototype of the home layout (logo, REGIONES bar, FILTROS panel, MUNDO globe) in app/frontend/prototype/.
