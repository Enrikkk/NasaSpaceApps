---
id: T-010
title: Frontend: map -> parcel card -> priorities -> rotation comparator
status: todo
owner:
branch: t010-frontend-skeleton
paths: app/frontend/
depends: T-009
---
React + Vite + MapLibre (or what the owner knows). Reads only the JSON contract. Screens in plain language for a
non-technical farmer (max 4 screens): 1 map + parcel card, 2 'your parcel's past' timeline (crops + bare months),
3 priorities (sliders: profit, water, soil, risk), 4 comparator: current rotation + 2 alternatives as cards with
success %, EUR/ha, water, legal traffic light, 'why / evidence / what we don't know / ask your technician'.
Works first on the mock JSON. Add a 'what if' slider (rain/temperature) and a '2050' toggle if time allows.
