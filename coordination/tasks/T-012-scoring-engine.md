---
id: T-012
title: Scoring engine: success % x price x (1 - oversupply), crops table, Monte Carlo band
status: todo
owner:
branch: t012-scoring-engine
paths: app/backend/engine/, app/data/crops.csv
depends: T-009
---
Implement the whiteboard formula. crops.csv for 8-10 Murcia crops (Kc, root depth, salinity, N, frost/heat limits,
price min/max, breakeven EUR/ha, legume yes/no). 'Success %' (honest definition, D-005): share of the last 20 years
of POWER/IMERG climate in which the crop's thresholds (frost, heat, water) are NOT exceeded, times price >= breakeven.
Oversupply = declared area of the crop in the comarca (FEGA) vs a baseline. Priorities weights via TOPSIS/weighted sum;
Monte Carlo over price range and rainfall sources -> 'rotation B wins in X% of scenarios'. Engine computes, LLM only explains.
