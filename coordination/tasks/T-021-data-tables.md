---
id: T-021
title: Data tables: crops.csv (8 crops), Eurostat prices, IMIDA/MAPA costs (human transcription)
status: review
owner: arturo
branch: arturo-inbox-followup
paths: app/data/tables/
depends: 
---
Seat (plan): arturo (+ ~2 h human transcription from the browser).
Crops: lechuga, brocoli, melon, alcachofa, haba, cebada, veza (cover), limon. Columns: family, legal group (Ley 3/2020), FAO-56 Kc and stage days, root depth, FAO-29 salinity a/b, frost/heat thresholds, Y_ref t/ha, N need / N credit, legume yes/no, source URL per value, confidence.
Prices: Eurostat apri_ap_crpouta ES 2000-2024 (JSON API, free) -> prices.csv. Costs EUR/ha per cycle -> costs.csv, each row with source and year.
Values come from research/predictive-model-research.md and its sources; never invent a number, leave blank + confidence=low. Record licenses in submission/data-citations.md.

- 2026-11-14 14:36 | arturo: tables + reproducible builder prepared from 519849b; provenance, units, proxy flags and missing values retained. See app/data/tables/README.md and manifest.json. Missing costs remain empty/P; rights checks and engine-side parameter completion documented. Engine review requested; no merge to main.

- 2026-11-14 15:20 | arturo: review update from Enrique 8b3a214: sowing month, Murcia artichoke phases, HICP, four exact threshold names with explicit P gaps. ECREA B candidates separated by water regime/native year, excluded from canonical costs until engine supports selection and monetary bases. Six builder tests and engine loader/submodel compatibility passed; full engine tests blocked locally by missing pytest/numpy/scipy. Consumer evaluation requested; no merge.

- 2026-11-14 15:38 | arturo: thermal research delivered in threshold-evidence.md for all eight crops (cold + heat), with cultivar/stage/exposure/variable/result and transferability. No valid daily whole-crop t0/t100 pair established; P rows retain specific source-based reasons. Original regional artichoke study found, proposals for episode/partial-response model sent to Enrique. Products from 27d51d9 integrated; CARM monthly excluded after restrictive terms confirmed #104.
