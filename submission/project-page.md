# Project page draft (copy into the Project tab; fix to match what is really built)

**Challenge:** Field Shift: Adapting Farms with NASA Data
**Working name:** RotaSat (change freely)

## Summary
Farmers in Murcia face heat waves, DANA floods, water scarcity and strict nitrate rules, and their field data is scattered
across a dozen sources. RotaSat gathers NASA Earth observations (POWER, IMERG/GPM, HLS/MODIS NDVI, SMAP, SRTM) with local soil,
crop and market data, and compares at least three crop rotations for a parcel, the current one included. Each rotation shows a
success probability, expected profit, water need and a legal traffic light, with the evidence, the information gaps and the risks.
It supports the farmer and the local technician; it does not replace them.

## Project details (outline)
1. Problem: scattered field data; rotation decisions made without comparing options.
2. Parcel radiography: real crop history (FEGA declared crops), NDVI timeline, bare-soil months.
3. Factors: water, crop value, sowing window, climate extremes, soil (see `brainstorm/pizarra-2026-11-14.md`).
4. Score = success % x price x (1 - oversupply). Success % = share of the last 20 years in which climate thresholds
   (frost, heat, water) are not exceeded, and price covers breakeven. No yield labels exist; we say so.
5. Farmer priorities re-weight the ranking; Monte Carlo over rainfall sources and price range gives "wins in X% of scenarios".
6. Uncertainty shown on purpose: three rain sources disagree, so we show a range.
7. What-if sliders and a 2050 scenario.
8. Limitations and roadmap: one demo parcel, hand-entered prices, simulated 2050, learning loop from farmer results (roadmap).

## Impact and business (slide, not demo)
Annual subscription by managed hectares; partner plan with a discount in exchange for harvest results that improve the model;
optional soil-sensor kit.
