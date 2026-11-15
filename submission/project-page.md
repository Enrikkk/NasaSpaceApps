# Project page draft (copy into the Project tab; keep it true to what is really built)

> DRAFT written by gonzalo's agent on 2026-11-14 (17:50 Madrid) from the repo state. Jaime and Enrique: please review. Anything marked
> **[confirm]** depends on work still in progress. Never claim here something that is not running.

**Challenge:** Field Shift: Adapting Farms with NASA Data
**Product name:** Agrockham (Agro + Ockham's razor: the simplest tool that works for a farmer without technical background)

## Summary
Farmers in the Campo de Cartagena (Murcia) face heat, scarce water and strict nitrate rules around the Mar Menor, and the data they need
is scattered across a dozen sources. Agrockham puts them together. The farmer finds a parcel on a globe, clicks its SIGPAC plot, and the
tool compares at least three crop rotations for it, the current one included, with the evidence, the information gaps and the risks of
each one, and a legal traffic light with the article of the Mar Menor law. It supports the farmer and the local technician; it does not
replace them.

## Project details
1. **Problem:** field data is scattered; rotation decisions are made without comparing options or the legal rules.
2. **What the farmer does:** search a place on a globe, zoom until the official SIGPAC plots appear, click one. A live API (Google Cloud
   Run) returns the analysis by blocks, each one labelled real, precalculated, simulated or loading.
3. **Data we use (real, cached, cited):**
   - NASA POWER and GPM IMERG (via POWER): 19-20 years of daily rain and temperature for the parcel's cell.
   - SIGPAC plots from the official FEGA download (CC BY 4.0), 170,265 plots in 7 municipalities of the Campo de Cartagena.
   - SoilGrids (ISRIC) soil texture and organic matter; Open-Meteo / ERA5 reference evapotranspiration.
   - SIAM-IMIDA station data (frost and heat days) for the engine.
   - Prices: MAPA, Eurostat and FAOSTAT (open); CARM yearbook under decision D-010, permission pending **[confirm before submission]**.
   - Ley 3/2020 (Mar Menor) and CAP rules, checked against the consolidated BOE text. Not legal advice.
4. **How rotations are compared:** the engine (rules and physics, no black box) simulates each rotation over the historical years with
   climate and prices paired by year. "Success %" is the share of historical years in which the climate does not cause a loss above
   20 % and the margin is not negative, shown **with a confidence interval** and never as a yield prediction. The AI only explains; the
   engine computes.
5. **Farmer priorities** (profit, water, soil, risk) re-weight the ranking in the browser. "Rotation B wins in X % of scenarios" is shown
   only as indicative until scenarios are aligned across rotations **[confirm: `escenarios_meta.alineados`]**.
6. **Uncertainty on purpose:** the three rain sources disagree by about 40 % on the same parcel, the intervals are wide, and every card
   has "what we do not know" and "ask your technician".
7. **Bare soil and vulnerable windows:** HLS (NASA) NDVI per parcel is being computed; in the current demo the NDVI block is **simulated
   and labelled as such** **[confirm]**.

## What is real, what is simulated, what is roadmap
| Piece | Status in the demo |
|---|---|
| Parcel (SIGPAC plot, area, slope, irrigation) | Real (FEGA download), 7 municipalities |
| Climate and soil of the clicked point | Real, cached by cell |
| Legal traffic light | Computed from a rules table with articles; demo parcel in Zone 2; some rules still unverified |
| Rotations, margins, success % | Computed by the engine for one **reference parcel** (Torre-Pacheco 18/426/1); the API states this for other parcels. Per-parcel engine = roadmap |
| NDVI and bare-soil months | Simulated in the demo **[confirm]** |
| 2050 scenario, what-if sliders | Simulated deltas **[confirm]** |
| Drones, aquifers, fruit quality, subscription and discount plan | Roadmap / mock, labelled as such |

## Limitations and roadmap
One reference parcel for the rotation numbers, national (not Murcia) open prices, wide intervals, rules not legally validated, no yield
labels exist for Mediterranean horticulture. Roadmap: engine per parcel, NDVI from HLS for every parcel, soil-moisture node (IoT),
learning loop where farmers share harvest results for a discount, more regions.

## Impact and business (slide, not demo)
Annual subscription by managed hectares; partner plan with a discount in exchange for harvest results that improve the model;
optional soil-sensor kit.

## Links
Live API: https://agrockham-api-530791362085.europe-west1.run.app (docs at /docs). Public repo: **[add URL and licence before submission]**.
