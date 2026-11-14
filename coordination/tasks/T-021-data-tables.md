---
id: T-021
title: Data tables: crops.csv (8 crops), Eurostat prices, IMIDA/MAPA costs (human transcription)
status: review
owner: arturo
branch: t021-data-tables
paths: app/data/tables/
depends: 
---
Seat (plan): arturo (+ ~2 h human transcription from the browser).
Crops: lechuga, brocoli, melon, alcachofa, haba, cebada, veza (cover), limon. Columns: family, legal group (Ley 3/2020), FAO-56 Kc and stage days, root depth, FAO-29 salinity a/b, frost/heat thresholds, Y_ref t/ha, N need / N credit, legume yes/no, source URL per value, confidence.
Prices: Eurostat apri_ap_crpouta ES 2000-2024 (JSON API, free) -> prices.csv. Costs EUR/ha per cycle -> costs.csv, each row with source and year.
Values come from research/predictive-model-research.md and its sources; never invent a number, leave blank + confidence=low. Record licenses in submission/data-citations.md.

- 2026-11-14 14:36 | arturo: tables + reproducible builder prepared from 519849b; provenance, units, proxy flags and missing values retained. See app/data/tables/README.md and manifest.json. Missing costs remain empty/P; rights checks and engine-side parameter completion documented. Engine review requested; no merge to main.
