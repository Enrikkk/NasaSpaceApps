---
id: T-018
title: Engine: price scenarios P10/P50/P90, oversupply as uncertain price shift, costs and cash peak (submodels E, F)
status: todo
owner:
branch: t018-engine-price-costs
paths: app/backend/engine/price/, app/backend/engine/costs/
depends: T-009, T-021
---
Seat (plan): enrique. See coordination/PLAN.md and research/predictive-model-research.md sections E and F.
Prices: real deflated Eurostat apri_ap_crpouta per historical year (paired with the same climate year), P10/P50/P90.
Oversupply: P_adj = P * exp(beta * a), a = ln(area now / 5-year mean), beta uncertain; output sobreoferta_detalle{efecto_precio_pct, semaforo}.
Costs: from app/data/tables/ (T-021), +-15% band, label 'precios 2018-19 actualizados'. Output margen_eur_ha{p10,p50,p90,breakeven_precio_eur_kg} and inversion{pico_caja_negativa_eur_ha, meses_hasta_primer_ingreso}.
Done when: a function margin_scenarios(crop, sowing_date) returns 20 paired-year margins for the 8 demo crops, with a unit test.
