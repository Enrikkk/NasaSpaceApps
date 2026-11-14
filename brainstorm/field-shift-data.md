> ## 🎯 RESUME HERE (2026-11-14 ~15:45, Sat): enrique's engine (T-012 core + T-018 price/costs)
>
> **State.** Engine runs end-to-end on real data per crop TYPE, branch `t012-motor-nucleo` @ 27d51d9 (not merged; 15 tests:
> `python3 -m pytest app/backend/engine/core/tests -q`; demo table: `python3 -m app.backend.engine.core.evaluate`).
> Climate = SIAM TP91 station 2005-07..2024 (frost from station; POWER only fills gaps). Prices = CARM yearbook monthly quotes
> by variety 2002-2023 (`engine/data/official/carm_precios_mensuales.csv`, orientative), priced on each cycle's harvest months,
> tier CARM type → CARM crop → Eurostat national. Costs/kilos per type from IMIDA (net kg = coste_total/coste_unitario).
> Money in 2025 euros (HICP). Farmer can override the price in the UI (options in `precio.opciones_usuario`; per-year
> `cantidad_ha`, `coste_eur_ha`, `coste_recoleccion_eur_ha`, `clima_malo` exported for live recompute).
>
> **Next.** (1) Integrate arturo's tables `origin/arturo-inbox-followup` @ d3b1abf (frost_t0/t100, heat_t0/t100, ECREA proxies)
> — careful: when `app/data/tables/crop_params.csv` exists the engine reads only it, so it must carry the product rows too.
> (2) T-020 decision layer → `app/data/torre-pacheco.json` (contract v1). D-009 accepted: live backend later.
>
> **Decided by Enrique (don't reopen):** 2025 euros · artichoke on Murcia calendar · UI shows only FAO-calculated water ·
> no ML price/yield regressor (walk-forward backtest: loses to the median in 5/6 crops) · products per type + farmer's own price.
>
> **Money-only results (no climate thresholds yet):** limón fino 89 %, alcachofa 78 %, brócoli 62 %, melón piel de sapo 56 %,
> lechuga iceberg 39 % (0.21 €/pieza vs 0.24 cost), little gem 24 %; haba/cebada not evaluable.
> **Open:** does CARM "s/finca" include harvest? (default: farmer pays; UI toggle).
> **⚠️ Licence:** CARM yearbook prices = personal non-commercial use only, no modification (esam.carm.es/legal). Permission
> requested (Enrique emails agri-estadistica@carm.es). Engine uses them only with `--interno` / `allow_restricted=True`
> (branch @ 2f8b3b9, 16 tests); anything PUBLISHED uses open data only (Eurostat) until written permission.

# Field Shift (challenge 06): data brainstorm

Written 2026-11-14 by Claude (seat enrique). Sources:
- the official Resources tab, captured via Chrome on 2026-11-14
- live access checks against Murcia on the same day (commands at the bottom)

Read `context/challenges/06-adapting-farms-with-nasa-data.md` first.

## 1. What NASA published (Resources tab)

**Global (usable for Murcia):**

| Dataset | What the challenge says it's for |
|---|---|
| SMAP | soil moisture, freeze/thaw |
| GPM IMERG | rain, extremes, erosion |
| Landsat + MODIS/VIIRS | NDVI, bare ground, seasonal change |
| NASA POWER | temperature, radiation, frost, crop water use |
| SRTM | slope, runoff, erosion |
| ECOSTRESS | land-surface temperature and ET at about 70 m |
| GLDAS | continuous land-surface time series |
| GEDI | biomass, only weakly relevant to crops |
| FAO GAEZ | crop suitability, yield potential |
| ESA Sentinel-2 (partner) | 10–20 m |
| ECMWF ERA5 (partner) | hourly reanalysis |

GRACE/GRACE-FO is named in the challenge text but not in the Resources tab.

**US only, so not usable for Murcia:**
- USDA: Ag Data Commons, Web Soil Survey, SSURGO/STATSGO2, **Cropland Data Layer (CDL)**, AMS Market News, **NASS QuickStats**
- PRISM, NAIP, NLCD, CoCoRaHS, NWIS, **OpenET**, LANDFIRE, NLDAS

The ground truth the challenge suggests for training models (CDL rotations, NASS yields, OpenET) exists only in the US.

## 2. Access checks over Murcia (2026-11-14)

All checks used the huerta / Campo de Cartagena.

| Dataset | Resolution | Result | Verdict |
|---|---|---|---|
| NASA POWER API (AG) | ~0.5° (~50 km) | OK, no login. Monthly 2015–2024: T2M_MAX/MIN, PRECTOTCORR, FROST_DAYS, GWETROOT | climate context, ET0 input |
| POWER `EVLAND` | ~50 km | 0.2–1.8 mm/day in 2023 | **trap**: model ET of unirrigated land. It doesn't see irrigation. (`EVPTRNS` is in MJ/m²/day, not mm) |
| SoilGrids v2 (ISRIC, not NASA) | 250 m, modelled | Campo de Cartagena (−1.02, 37.78), 0–5 cm: clay 41.7 %, sand 16.6 %, pH 7.9, SOC 20 g/kg, N 1.79 g/kg. **Null over urban Murcia** | usable. SOC looks high for Murcia, so treat as modelled |
| HLS L30 + S30 (Landsat + Sentinel-2 harmonised) | 30 m | 79 + 95 = **174 granules in 2025** | **the workhorse**: per-field NDVI phenology |
| ECOSTRESS LSTE (L2T) | 70 m | 44 granules in 2025 | heat-stress snapshots |
| ECOSTRESS ET (L3T JET) | 70 m | **only 6 granules in 2025** | snapshots, not a time series |
| SMAP L3 enhanced (SPL3SMP_E) | 9 km | 364 granules in 2025 | sector-scale soil moisture |
| SMAP/Sentinel-1 (SPL2SMAP_S) | 1–3 km | 171 granules in 2025 | best SMAP resolution available |
| GPM IMERG daily final | 0.1° (~10 km) | 273 granules in 2025 (the final run lags by months) | rain and extremes. Use the Late run for recent dates |

Not checked yet:
- MODIS ET MOD16 (500 m, 8-day): possible ET time series
- GRACE (~300 km, basin scale only)
- SRTM, GAEZ, ERA5
- Earthdata login download of HLS (CMR search needs no login, download does)

## 3. Data insights (the brainstorm)

### a) Two honest scales
- **Field layer:** HLS/Sentinel-2 NDVI 30 m, ECOSTRESS 70 m, SRTM 30 m, SoilGrids 250 m.
- **Context layer:** SMAP 1–9 km, IMERG 10 km, POWER 50 km, ERA5, GRACE basin.

Never show a 9 km value as if it were "your field". The challenge explicitly asks to explain uncertainty and where
satellite data differs from ground data.

### b) Bare-field windows (literally asked)
Per-parcel HLS NDVI time series → months with NDVI below about 0.2 = bare soil. Those are the windows where a cover
crop or legume fits.

This is computable, visual and directly in the challenge text: "highlight times when fields are typically bare".

### c) Irrigation fingerprint
Model ET from POWER/GLDAS assumes no irrigation. Satellite ET (ECOSTRESS snapshots, maybe MOD16) shows the real
evapotranspiration. The gap approximates applied irrigation.

In Murcia water is *the* constraint, so this matters. **To verify**: ECOSTRESS has only 6 ET scenes a year, so check
MOD16 for a time series.

### d) Crop water demand per rotation (FAO-56)
Water demand per crop = Kc(stage) × ET0, with ET0 computed from POWER (Hargreaves or Penman-Monteith).

FAO-56 publishes Kc tables for lettuce, broccoli, melon, artichoke, faba bean, barley and so on. This is the bridge
from NASA climate data to "how much water does rotation X need", and it is defensible.

### e) The "model trained on pairs" (Enrique's idea)
Labelled pairs exist at scale only in the US: CDL gives the crop per 30 m pixel per year (2008→), NASS gives county
yields, OpenET gives field ET.

Pairs = (previous crop + this year's NASA conditions → this year's outcome), with the outcome being season-integrated
NDVI or yield. That gives millions of samples.

Options:
1. Murcia only: local hook, no labels, rules plus FAO-56 instead of ML. The 4 local teams will likely do this.
2. US only: rich labels, no local story.
3. **Train/validate on a US Mediterranean irrigated analog (California Central Valley: CDL + OpenET + SSURGO), apply
   to Murcia with explicit domain-shift caveats.** "Calibrated where ground truth exists, demonstrated at home."

### f) Spanish/EU equivalents (NOT verified, check before relying on them)
| Purpose | Candidate |
|---|---|
| Parcels | SIGPAC (MAPA) |
| Crop type | ESA WorldCereal (global 10 m), EuroCrops |
| Area and yield stats | ESYRCE (MAPA) |
| Weather ground truth to validate POWER/IMERG | SIAM-IMIDA stations (Murcia) |
| Water | Confederación Hidrográfica del Segura |
| Prices | MAPA prices |
| EU soil measurements to contrast SoilGrids | LUCAS soil |

### g) Local impact angle
In Campo de Cartagena, nitrates from intensive horticulture leaching into the Mar Menor are a major regional issue.
Cover crops in bare windows and legume rotations that reduce N fertiliser are a strong "why it matters" story.
Get facts and sources before claiming specifics.

## 4. How to reproduce the checks
- POWER: `https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=T2M_MAX,T2M_MIN,PRECTOTCORR,FROST_DAYS,GWETROOT,EVLAND&community=AG&longitude=-1.13&latitude=38.0&start=2015&end=2024&format=JSON`
- SoilGrids: `https://rest.isric.org/soilgrids/v2.0/properties/query?lon=-1.02&lat=37.78&property=clay&property=soc&depth=0-5cm&value=mean`
- CMR counts (no login): `https://cmr.earthdata.nasa.gov/search/granules.json?short_name=<SN>&bounding_box=-1.25,37.95,-1.0,38.1&temporal=2025-01-01T00:00:00Z,2025-12-31T23:59:59Z&page_size=0`
  → read the `CMR-Hits` header. SN = HLSL30, HLSS30, ECO_L2T_LSTE, ECO_L3T_JET, SPL3SMP_E, SPL2SMAP_S, GPM_3IMERGDF.
