---
id: T-011
title: Backend: per-parcel data pipeline with cache (POWER, IMERG, SoilGrids, SIGPAC, Open-Meteo)
status: doing
owner: gonzalo
branch: t011-parcel-data-pipeline
paths: app/backend/pipeline/, app/data/cache/pipeline/
depends: T-009
---
Start from `research/api_smoke_test.py` (11/11 open sources OK) and `research/field-shift-datasets.md`. For a given
lat/lon produce the `clima`, `suelo`, `historia`, `parcela` blocks of the contract and cache them as JSON.
Real for the demo parcel (Torre-Pacheco SIGPAC 18/426/1), cached so the demo never needs venue Wi-Fi.
Traps: IMERG via POWER needs `&time-standard=UTC`, SoilGrids 5 calls/min, POWER FROST_DAYS is not Tmin<0.

- 2026-11-14 13:20 | plan v1 (coordination/PLAN.md): Seat (plan): gonzalo. Output cached blocks parcela, historia, clima (POWER + IMERG 20 years daily, Open-Meteo ET0), suelo into app/data/cache/pipeline/. Frost comes from SIAM (T-014), not POWER Tmin.

- 2026-11-14 16:40 | gonzalo claimed. Prep prototypes (tested): research/prototypes/atom_pipeline/ (SIGPAC from ATOM, 5 municipalities) and research/prototypes/pipeline_clima_suelo/ (POWER/IMERG/Open-Meteo/SoilGrids with cache). Moves to app/backend/pipeline/. Licence: FEGA terms 2026 (CC BY 4.0, attribution).
