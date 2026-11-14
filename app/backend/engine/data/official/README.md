# Official data cached by the engine (enrique, branch t012-datos-oficiales)

Fetched by `app/backend/engine/sources/*.py`; every file's URL, date and licence is in `sources.csv`.
Provisional engine-side copies: the team tables live in `app/data/tables/` (T-021, arturo) and the parcel climate
in `app/data/cache/pipeline/` (T-011, gonzalo). Switch to those when they land.

| File | What | Gaps |
|---|---|---|
| eurostat_prices_es.csv | Spain first-stage price EUR/100 kg 2000-2024, nominal + real (HICP 2015) | no artichoke, no vetch (not sold); broccoli = cauliflower proxy; haba = dry broad bean |
| eurostat_area_es.csv | Spain area/production/yield 1999-2026 for the 8 crops | vetch only 2025; yield blank in many years |
| power_daily_37.7383_-0.9884.csv | NASA POWER daily 2005-2024 at the demo parcel (FAO-56 PM inputs, rain) | **0 frost days in 20 years**: the ~50 km cell can't see frost |

Frost check 2026-11-14: POWER, ERA5-Land and ERA5 (Open-Meteo archive) at the parcel all give 0-1 frost years
in 2005-2024 (Dec 2010 minimum 1.3-2.9 degC). Frost risk needs a station (SIAM TP91, T-014) before it can be claimed.
