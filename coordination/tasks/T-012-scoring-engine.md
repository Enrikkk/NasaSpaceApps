---
id: T-012
title: Scoring engine: success % x price x (1 - oversupply), crops table, Monte Carlo band
status: todo
owner:
branch: t012-scoring-engine
paths: app/backend/engine/core/
depends: T-009
---
Implement the whiteboard formula. crops.csv for 8-10 Murcia crops (Kc, root depth, salinity, N, frost/heat limits,
price min/max, breakeven EUR/ha, legume yes/no). 'Success %' (honest definition, D-005): share of the last 20 years
of POWER/IMERG climate in which the crop's thresholds (frost, heat, water) are NOT exceeded, times price >= breakeven.
Oversupply = declared area of the crop in the comarca (FEGA) vs a baseline. Priorities weights via TOPSIS/weighted sum;
Monte Carlo over price range and rainfall sources -> 'rotation B wins in X% of scenarios'. Engine computes, LLM only explains.

- 2026-11-14 13:20 | plan v1 (coordination/PLAN.md): Seat (plan): enrique. Scope narrowed by coordination/PLAN.md: submodels A (aptitude, hard filters), B (climate risk -> exito_pct with Wilson, L*=20 %), C (FAO-56 water + FAO-29 salinity), D (reference yield). crops.csv moved to T-021 (app/data/tables/). Price/costs = T-018, legal = T-019, DP/Monte Carlo = T-020.
