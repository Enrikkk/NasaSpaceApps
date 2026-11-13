# NASA Earth-observation datasets for crop-rotation decision support in Región de Murcia (status 13 Nov 2026)

Scope: Field Shift challenge (`context/challenges/06-adapting-farms-with-nasa-data.md`). Test points: **Campo de Cartagena
37.72 N, -0.97 E** and **Altiplano/Jumilla 38.47 N, -1.33 E**. All live tests below ran on 2026-11-13 from this laptop with no
credentials. Raw responses are in
`/private/tmp/claude-501/-Users-jaime-Documents-NasaSpaceApps/324b317c-8037-4e23-a8f2-fde635abe82e/scratchpad/api-tests/nasa/`
(untrusted data, read only with `python3 -I`). Nothing requiring Earthdata Login (EDL) was executed.

---

## Q1. What actually works today? Live API tests (no login)

### Takeaway
NASA POWER and NASA CMR answered every request in under 2.5 s with no login. The biggest finding is that **POWER now serves
IMERG precipitation at 0.1° with no login** (`IMERG_PRECTOT`, needs `time-standard=UTC`), from 2000-01-01 to about two months
before today. You therefore don't need GES DISC, Giovanni or OPeNDAP for rainfall. CMR confirms that HLS, ECOSTRESS, SMAP,
MODIS, VIIRS, OPERA, GRACE and even NISAR soil moisture have granules over the Cartagena point.

### Cited Findings

**NASA POWER (no key, no login)**
- Daily point, 1 year, 4 params, Cartagena. Command: `curl -s --max-time 60 "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M_MAX,T2M_MIN,PRECTOTCORR,GWETROOT&community=AG&longitude=-0.97&latitude=37.72&start=20240101&end=20241231&format=JSON"`. Result: **HTTP 200, 0.75 s, 24.6 KB**. API v2.10.3, sources `MERRA2, POWER`, fill value -999, time standard LST. Grid-cell elevation reported as 123.68 m. 2024 values: rainfall **210.9 mm**, max daily rainfall 14.1 mm (21 Sep), **0 days with Tmin<0** (min Tmin 5.9 °C), **2 days with Tmax>35 °C** (max 35.4 °C), GWETROOT 0.46–0.51 — [POWER daily API](https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M_MAX,T2M_MIN,PRECTOTCORR,GWETROOT&community=AG&longitude=-0.97&latitude=37.72&start=20240101&end=20241231&format=JSON)
- The same request for Jumilla (`latitude=38.47&longitude=-1.33`): **HTTP 200, 0.76 s**. Grid elevation 567.25 m. 2024 values: rainfall **254.3 mm**, max day 25.3 mm (19 Sep), **3 days with Tmin<0** (min -1.1 °C), **47 days with Tmax>35 °C**, 5 days >40 °C (max 43.6 °C), GWETROOT 0.34–0.42 — [POWER daily API](https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M_MAX,T2M_MIN,PRECTOTCORR,GWETROOT&community=AG&longitude=-1.33&latitude=38.47&start=20240101&end=20241231&format=JSON)
- Climatology, Cartagena: `.../api/temporal/climatology/point?parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,FROST_DAYS,ALLSKY_SFC_SW_DWN,GWETROOT&community=AG&longitude=-0.97&latitude=37.72&format=JSON`. Result: **HTTP 200, 0.62 s, 2.2 KB**. Sources SYN1DEG, MERRA2, POWER. Annual T2M 18.43 °C. PRECTOTCORR 0.79 mm/day (about 288 mm/yr). Monthly T2M_MIN is the extreme (January 1.43 °C). FROST_DAYS = 0 in every month. Solar radiation runs from 8.05 (Dec) to 26.67 MJ/m²/day (Jun) — [POWER climatology API](https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,FROST_DAYS,ALLSKY_SFC_SW_DWN,GWETROOT&community=AG&longitude=-0.97&latitude=37.72&format=JSON)
- **20-year daily series in one call** (2005–2024, 10 params: T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, RH2M, WS2M, ALLSKY_SFC_SW_DWN, GWETTOP, GWETROOT, GWETPROF). Cartagena: **HTTP 200, 2.37 s, 1.19 MB**. Jumilla: **2.00 s, 1.19 MB**. Cartagena results: mean annual rainfall **296.8 mm** (range 179 mm in 2005 to 453 mm in 2022), Tmin<0 on 0 days every year, Tmax>35 °C on 0.9 days/yr on average, wettest day 72.4 mm (2016). Jumilla results: mean rainfall **318.9 mm/yr**, **18.2 frost days/yr** (Tmin<0), **32.4 days/yr with Tmax>35 °C**, OLS trend **+0.86 hot days per year** (a naive trend over 20 points, not tested for significance) — [POWER daily API](https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,WS2M,ALLSKY_SFC_SW_DWN,GWETTOP,GWETROOT,GWETPROF&community=AG&longitude=-0.97&latitude=37.72&start=20050101&end=20241231&format=JSON)
- **IMERG through POWER (no login)**. `IMERG_PRECTOT` fails in LST mode with the message "The IMERG Source Data is not available at the Local Solar Time (LST) standard." It works with `&time-standard=UTC`, and the header then lists sources `MERRA2, IMERG` — [POWER daily API, IMERG test](https://power.larc.nasa.gov/api/temporal/daily/point?parameters=PRECTOTCORR,IMERG_PRECTOT,GWETROOT&community=AG&longitude=-0.97&latitude=37.72&start=20190910&end=20190915&format=JSON&time-standard=UTC)
  - DANA of 12–13 Sep 2019, Cartagena cell: IMERG **81.0 + 82.6 = 163.6 mm**, against MERRA-2 PRECTOTCORR 61.7 + 22.8 = 84.5 mm.
  - 2024 total: IMERG **263.4 mm** against PRECTOTCORR 210.9 mm — [same API, 2024](https://power.larc.nasa.gov/api/temporal/daily/point?parameters=IMERG_PRECTOT,PRECTOTCORR&community=AG&longitude=-0.97&latitude=37.72&start=20240101&end=20241231&format=JSON&time-standard=UTC)
  - 2000–2025 in one call: **HTTP 200, 1.65 s, 294 KB**. The first valid IMERG day is 2000-01-01. Mean annual rainfall 2001–2025 is **372.6 mm (IMERG) against 295.1 mm (MERRA-2 corrected)**. Wettest IMERG day: **108.3 mm on 2016-12-18** — [POWER daily API, 2000–2025](https://power.larc.nasa.gov/api/temporal/daily/point?parameters=IMERG_PRECTOT,PRECTOTCORR&community=AG&longitude=-0.97&latitude=37.72&start=20000101&end=20251231&format=JSON&time-standard=UTC)
  - Latency: the last valid IMERG day was **2026-09-14**, compared with 2026-11-11 for PRECTOTCORR (query sent 2026-11-13).
- **Regional endpoint limit.** A 1°×1.5° box over Murcia (`/api/temporal/monthly/regional?...latitude-min=37.5&latitude-max=38.5&longitude-min=-2.0&longitude-max=-0.5`) returned **HTTP 422** with "Please provide at least a 2 degree range in latitude; otherwise use the point endpoint" (and the same message for longitude) — [POWER monthly regional API](https://power.larc.nasa.gov/api/temporal/monthly/regional?parameters=PRECTOTCORR&community=AG&latitude-min=37.5&latitude-max=38.5&longitude-min=-2.0&longitude-max=-0.5&start=2020&end=2021&format=JSON)
- **Latency (MERRA-2/GEOS):** a request for 2026-10-20 to 2026-11-12 returned valid T2M_MAX up to **2026-11-10** and -999 for 11–12 Nov, so latency is about 2–3 days. The daily API `configuration` endpoint reports a date range of `1981-01-01` to `2026-11-13` — [POWER daily configuration](https://power.larc.nasa.gov/api/temporal/daily/configuration)
- **ET-like parameters (AG community, daily).** `EVPTRNS` ("Evapotranspiration Energy Flux", MJ/m²/day) returned **0.0** at Cartagena on 1–3 Jul 2024. `EVLAND` ("Evaporation Land", mm/day) returned 0.23–0.29 mm/day. Also available: T2MDEW, PS and TS (skin temperature). **No FAO-56 ET0 parameter appeared** in the daily AG parameter catalogue (152 params) — [POWER parameter manager](https://power.larc.nasa.gov/api/system/manager/parameters?community=AG&temporal=DAILY)
- **FROST_DAYS is not "Tmin<0".** POWER's definition reads: "A frost day occurs when the 2m temperature cools to the dew point temperature and both are less than 0 C". That explains why the Cartagena climatology shows 0 frost days even though the monthly minimum T2M_MIN is 1.4 °C — [POWER parameter manager](https://power.larc.nasa.gov/api/system/manager/parameters?community=AG&temporal=DAILY)
- **SMAP-backed POWER parameters.** SFMC, RZMC and RZMC_PRCNTL exist in the catalogue ("Top layer soil moisture (0-5 cm)", "Root zone soil moisture (0-100 cm)"), but at Cartagena they returned **-999 for every day of 2024**, in both LST and UTC mode — [POWER daily API](https://power.larc.nasa.gov/api/temporal/daily/point?parameters=IMERG_PRECTOT,PRECTOTCORR,SFMC,RZMC,RZMC_PRCNTL&community=AG&longitude=-0.97&latitude=37.72&start=20240101&end=20241231&format=JSON&time-standard=UTC). POWER docs say SMAP L4 replaces MERRA-2 soil moisture only "by enabling the high-resolution toggle in the DAV or request SMAP-aliased parameters through the API" — [POWER hydrology sources](https://power.larc.nasa.gov/docs/methodology/data/sources_hydrology/)
- The daily OpenAPI spec lists only these query params: start, end, latitude, longitude, community, parameters, format, units, user, header, time-standard, site-elevation, wind-elevation, wind-surface. There is **no "high-resolution" switch** — [POWER daily OpenAPI](https://power.larc.nasa.gov/api/temporal/daily/openapi.json)

**NASA CMR (no login), granule search over the Cartagena point**

Template: `curl -s -D hdr.txt --max-time 60 "https://cmr.earthdata.nasa.gov/search/granules.json?short_name=HLSS30&version=2.0&point=-0.97,37.72&temporal=2024-01-01T00:00:00Z,2024-12-31T23:59:59Z&page_size=2000"`. The total count is in the `CMR-Hits` header. Every call returned HTTP 200 in **0.22–0.65 s** — [CMR granule search](https://cmr.earthdata.nasa.gov/search/granules.json?short_name=HLSS30&version=2.0&point=-0.97,37.72&temporal=2024-01-01T00:00:00Z,2024-12-31T23:59:59Z&page_size=2000)

| Product (short_name, version) | Granules over Cartagena in 2024 | Latest granule (as of 2026-11-13) | Notes |
|---|---|---|---|
| HLSL30 v2.0 | **84** (all at 10 UTC); mean scene cloud 32 %; 43 scenes <20 % cloud | 2026-11-05 | MGRS tile **30SXG**; 783 granules all-time |
| HLSS30 v2.0 | **67** (11 UTC); mean cloud 29 %; 35 scenes <20 % | 2026-11-05 | 69 in 2024 at Jumilla |
| HLSL30_VI / HLSS30_VI v2.0 | 777 all-time (L30_VI) | 2026-11-05 | Ready-made NDVI/EVI |
| ECO_L2T_LSTE v002 | **37**, UTC hours spread over 0–23 (night and day); 0 scenes in April and 1 in June | 2026-11-05 | 46 at Jumilla. Per year at Cartagena: 2019 41, 2020 28, 2021 30, 2022 39, 2023 57, 2024 37, 2025 35, 2026 40 |
| ECO_L3T_JET / ECO_L4T_ESI v002 | **2** (Dec only) | — | Per year: 11, 8, 7, 13, 7, 2, 1, 2 (2019→2026) |
| ECO_L2T_LSTE v003 / ECO_L3T_JET v003 | 99 / 3 all-time | 2026-11-05 / 2026-10-08 | Collection 3 is rolling out |
| SPL3SMP_E v006 | 366 (daily global files) | **2026-11-12** (≈1 day latency) | |
| SPL4SMGP v008 | 33,961 all-time (3-hourly) | 2026-11-10 21:00 | |
| GPM_3IMERGDF v07 (Final) | — | **2025-09-30** (collection end date) | V07 Final has stopped (see Q2) |
| GPM_3IMERGDL v07 (Late) | — | 2026-11-12 (file tag V07C) | |
| MOD13Q1 / MYD13Q1 v061 | — | 2026-10-16 / 2026-10-24 | Terra and Aqua still producing |
| MOD11A2 v061 | — | 2026-11-01 | |
| MOD16A2GF v061 | — | 2025-12-27 (produced Feb 2026) | Gap-filled ET is produced yearly, after the year ends |
| MCD12Q1 v061 | 25 years | year 2025 (produced Oct 2026) | |
| VNP13A1 / VJ113A1 v002 | — | 2026-10-24 / 2026-10-16 | |
| VNP21A1D v002 | — | 2026-11-02 | |
| OPERA_L3_DSWX-HLS_V1 | 1,471 all-time | 2026-11-05 | |
| OPERA_L3_DIST-ALERT-HLS_V1 | 635 all-time | 2026-11-05 | |
| TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4 | 1 file | file `GRCTellus.JPL.200204_202609...` (to **Sep 2026**) | |
| NISAR_L3_SME2_PROVISIONAL_V1 | **50** all-time | 2026-10-16 | Provisional 200 m soil moisture |
| NISAR_L2_GCOV_V1 | 6 | 2026-10-28 | |

Sources: [CMR collections HLSL30](https://cmr.earthdata.nasa.gov/search/concepts/C2021957657-LPCLOUD.html), [HLSS30](https://cmr.earthdata.nasa.gov/search/concepts/C2021957295-LPCLOUD.html), [HLSL30_VI](https://cmr.earthdata.nasa.gov/search/concepts/C3246892554-LPCLOUD.html), [HLSS30_VI](https://cmr.earthdata.nasa.gov/search/concepts/C3246894861-LPCLOUD.html), [ECO_L2T_LSTE v002](https://cmr.earthdata.nasa.gov/search/concepts/C2076090826-LPCLOUD.html), [ECO_L2T_LSTE v003](https://cmr.earthdata.nasa.gov/search/concepts/C3998139651-LPCLOUD.html), [ECO_L3T_JET v002](https://cmr.earthdata.nasa.gov/search/concepts/C2076106409-LPCLOUD.html), [ECO_L3T_JET v003](https://cmr.earthdata.nasa.gov/search/concepts/C4057232489-LPCLOUD.html), [ECO_L4T_ESI v002](https://cmr.earthdata.nasa.gov/search/concepts/C2076104650-LPCLOUD.html), [SPL3SMP_E v006](https://cmr.earthdata.nasa.gov/search/concepts/C2938664763-NSIDC_CPRD.html), [SPL4SMGP v008](https://cmr.earthdata.nasa.gov/search/concepts/C3480440870-NSIDC_CPRD.html), [GPM_3IMERGDF v07](https://cmr.earthdata.nasa.gov/search/concepts/C2723754864-GES_DISC.html), [GPM_3IMERGDL v07](https://cmr.earthdata.nasa.gov/search/concepts/C2723754859-GES_DISC.html), [MOD13Q1](https://cmr.earthdata.nasa.gov/search/concepts/C1748066515-LPCLOUD.html), [MYD13Q1](https://cmr.earthdata.nasa.gov/search/concepts/C2307290656-LPCLOUD.html), [MOD16A2GF](https://cmr.earthdata.nasa.gov/search/concepts/C2565791021-LPCLOUD.html), [MOD11A2](https://cmr.earthdata.nasa.gov/search/concepts/C2269056084-LPCLOUD.html), [MCD12Q1](https://cmr.earthdata.nasa.gov/search/concepts/C2484079608-LPCLOUD.html), [VNP13A1](https://cmr.earthdata.nasa.gov/search/concepts/C2519127224-LPCLOUD.html), [VJ113A1](https://cmr.earthdata.nasa.gov/search/concepts/C2519122065-LPCLOUD.html), [VNP21A1D](https://cmr.earthdata.nasa.gov/search/concepts/C2545314555-LPCLOUD.html), [OPERA DSWx-HLS](https://cmr.earthdata.nasa.gov/search/concepts/C2617126679-POCLOUD.html), [OPERA DIST-ALERT](https://cmr.earthdata.nasa.gov/search/concepts/C2746980408-LPCLOUD.html), [JPL mascon CRI RL06.3 v04](https://cmr.earthdata.nasa.gov/search/concepts/C3195527175-POCLOUD.html), [NISAR SME2 provisional](https://cmr.earthdata.nasa.gov/search/concepts/C2854344945-ASF.html), [NISAR GCOV](https://cmr.earthdata.nasa.gov/search/concepts/C3622241360-ASF.html)

**AppEEARS product catalogue (public, no login)**
- `curl -s "https://appeears.earthdatacloud.nasa.gov/api/product"` returned **HTTP 200, 0.65 s, 193 products**. Products relevant to Murcia: MOD13Q1.061, MYD13Q1.061, MOD11A1/A2.061, MOD16A2GF.061, MOD16A3GF.061, MOD17A2HGF.061, MCD12Q1.061, MCD15A2H.061, MCD43A4.061, VNP13A1.002, VJ113A1.002, VNP21A1D/N.002, **SPL3SMP_E.006, SPL3SMP.009, SPL4SMGP.008**, **ECO_L2T_LSTE.002, ECO_L3T_JET.002, ECO_L4T_ESI.002, ECO_L4T_WUE.002, ECO_L3T_SM.002**, HLSL30.020, HLSS30.020, **HLSL30_VI.020, HLSS30_VI.020**, **SRTMGL1_NC.003, NASADEM_NC.001**, ASTGTM_NC.003, EMIT. **Not in AppEEARS:** GPM/IMERG, GRACE, ECOSTRESS v003 — [AppEEARS product list](https://appeears.earthdatacloud.nasa.gov/api/product)
- Exact layer names (from `GET /api/product/{id}`): MOD13Q1.061 `_250m_16_days_NDVI`, `_250m_16_days_EVI`, `_250m_16_days_pixel_reliability`, `_250m_16_days_VI_Quality`; SPL4SMGP.008 `Geophysical_Data_sm_rootzone`, `Geophysical_Data_sm_surface`, `Geophysical_Data_sm_rootzone_pctl`, `Geophysical_Data_sm_profile_wetness`; SPL3SMP_E.006 `Soil_Moisture_Retrieval_Data_AM_*` (86 layers, including `..._retrieval_qual_flag` and `..._radar_water_body_fraction`); ECO_L2T_LSTE.002 `LST`, `LST_err`, `QC`, `cloud`; ECO_L3T_JET.002 `ETdaily`, `ETinstUncertainty`; ECO_L4T_ESI.002 `ESI`, `PET`; HLSS30_VI.020 / HLSL30_VI.020 `NDVI`, `EVI`; SRTMGL1_NC.003 `SRTMGL1_DEM`; MOD16A2GF.061 `ET_500m`, `PET_500m`, `ET_QC_500m`; VNP13A1.002 `500_m_16_days_NDVI` — [AppEEARS product endpoint, e.g. MOD13Q1.061](https://appeears.earthdatacloud.nasa.gov/api/product/MOD13Q1.061)

### Inferences
- POWER alone covers temperature, frost, heat, rainfall (MERRA-2 and IMERG), humidity, wind and radiation for 1981–present (IMERG from 2000). The whole climate backbone for any field can be fetched live in about 2 s, so caching per field is cheap. Cache the demo fields anyway.
- MERRA-2 rainfall (PRECTOTCORR) under-represents Murcia's convective extremes. Over 2001–2025 it was about 21 % below IMERG on average, and it gave half of IMERG's total in the 2019 DANA. Use `IMERG_PRECTOT` for rainfall and extreme-rain features, and keep PRECTOTCORR only for the 1981–1999 extension.
- POWER's GWETROOT barely moves (Cartagena 0.46–0.51 over a whole year). The model knows nothing about irrigation, and its 0.5° cell mixes coast and sea. Don't present it as field soil moisture. The same applies to EVLAND/EVPTRNS: model evaporation over unirrigated dry soil is close to 0, while irrigated fields in Campo de Cartagena evaporate a lot.
- Compute "frost days" yourself as Tmin<0 °C (and maybe Tmin<-2 °C for damaging frost) from T2M_MIN, not from POWER's FROST_DAYS, and say so in the UI.
- The Cartagena 0.5° MERRA-2 cell shows no Tmin<0 days in 20 years and a minimum of 5.9 °C in 2024. That probably reflects sea influence within the cell, so inland Campo de Cartagena hollows could see frost the grid misses. This is a resolution caveat to state in the tool.

### Gaps
- I could not enable the POWER "SMAP-aliased" parameters through the public API. SFMC/RZMC returned -999 in both LST and UTC mode, and the docs give no alias name. Possibly the feature only works in the web DAV.
- IMERG_PRECTOT via POWER is valid up to 2026-09-14. The docs don't say which IMERG run (Final/Late) POWER uses after the V07 Final record ended in Sep 2025.
- I compared no station data (AEMET/SIAM) against POWER or IMERG for the DANA events. The claim that IMERG is "closer to reality" is not verified here.

---

## Q2. Per-dataset datasheet, Murcia quirks and verdict

### Takeaway
**KEEP:** NASA POWER (with IMERG via POWER), HLS-VI 30 m, MODIS MOD13Q1 250 m NDVI, SRTM/NASADEM 30 m.
**OPTIONAL:** SMAP L4 root-zone soil moisture, MOD16A2GF ET, ECOSTRESS (heat-stress snapshots only), GRACE/GRACE-FO (one regional trend chart for the pitch), OPERA DIST-ALERT/DSWx, VIIRS VI as MODIS continuity, NISAR (curiosity only).
**DROP for the hackathon:** direct GES DISC IMERG downloads, Giovanni, SPL3SMP_E L3, MCD12Q1, raw Landsat C2.

### Cited Findings

#### NASA POWER (KEEP, core climate backbone)
- Meteorology comes from MERRA-2 ("1981 to within several months of real time"), extended by GEOS FP-IT "within several days of real time". Native resolution is **½° lat × ⅝° lon** for meteorology and **1°×1°** for radiation (sources: SRB, CERES SYN1deg, FLASHFlux) — [POWER methodology](https://power.larc.nasa.gov/docs/methodology/)
- High-resolution sources inside POWER: **IMERG 0.1°, daily UTC, from 1998-06-01 to near real time** (the methodology page's table; the hydrology page says 2001 and also "reprocessed back to 2000"), and **SMAP L4 ~0.09°, from 2015-03-31**, plus NEX-GDDP-CMIP6 at ~0.25° for 2015–2100 — [POWER methodology](https://power.larc.nasa.gov/docs/methodology/); [POWER hydrology sources](https://power.larc.nasa.gov/docs/methodology/data/sources_hydrology/). The sources conflict on the IMERG start date. My live test got valid IMERG values from 2000-01-01.
- PRECTOTCORR is defined as "The average MERRA-2 bias corrected total precipitation"; IMERG_PRECTOT as "The average IMERG total precipitation" — [POWER parameter manager](https://power.larc.nasa.gov/api/system/manager/parameters?community=AG&temporal=DAILY)
- Agriculture-relevant daily AG parameters confirmed in the catalogue: T2M, T2M_MAX, T2M_MIN, T2MDEW, T2MWET, RH2M, WS2M, ALLSKY_SFC_SW_DWN, PRECTOTCORR, IMERG_PRECTOT, GWETTOP, GWETROOT, GWETPROF, SFMC, RZMC, PRMC, RZMC_PRCNTL, PRMC_PRCNTL, EVLAND, EVPTRNS, FROST_DAYS, TSOIL1–6, TS — [POWER parameter manager](https://power.larc.nasa.gov/api/system/manager/parameters?community=AG&temporal=DAILY)
- The API documents error codes 200, 422 (validation) and **429 (Too Many Requests)** but publishes no numeric quota. Application APIs "typically complete in under a minute" — [POWER API overview](https://power.larc.nasa.gov/docs/services/api/)
- Auth: none (all live tests ran without a key). Formats: JSON, CSV and others via `format=`. Communities: RE, SB, AG — [POWER daily configuration](https://power.larc.nasa.gov/api/temporal/daily/configuration)
- Murcia quirks: a 0.5° cell (~55 km × 55 km) mixes coast, sea, Mar Menor and inland hollows. Regional requests need a box of at least 2°×2° (see Q1).

#### GPM IMERG V07 (KEEP via POWER `IMERG_PRECTOT`; direct access DROP)
- Products: GPM_3IMERGDF (Final, daily, 0.1°), GPM_3IMERGM (Final, monthly), GPM_3IMERGDL/DE (Late/Early, daily), GPM_3IMERGHH/HHL/HHE (half-hourly). All are at GES DISC and cloud-hosted — [CMR GPM_3IMERGDF](https://cmr.earthdata.nasa.gov/search/concepts/C2723754864-GES_DISC.html)
- **The V07 Final record ends 30 Sep 2025.** The reason given: "the parent products feeding into the IMERG algorithm (CORRA and GPROF) are being upgraded to V08". The **V08 Final will reprocess Jan 1998 to present with the usual 4-month latency**. The August 2026 update said V08 Final was likely to be released in **fall 2026**. Early and Late runs continue on V07 in a "hybrid" mode with V08 GPROF inputs, so discontinuities are possible — [GPM IMERG V08 transition schedule](https://gpm.nasa.gov/data/news/imerg-v08-transition-schedule); [Earthdata alert](https://www.earthdata.nasa.gov/data/alerts-outages/transition-gpm-imerg-products-v08); [Earthdata forum](https://forum.earthdata.nasa.gov/viewtopic.php?p=25931)
- CMR on 2026-11-13: no V08 collection found; GPM_3IMERGDF V07 has time_end 2025-09-30; Late V07 (V07C) is current to 2026-11-12 — [CMR GPM_3IMERGDL](https://cmr.earthdata.nasa.gov/search/concepts/C2723754859-GES_DISC.html)
- Giovanni (area-averaged time series, time-averaged maps) needs EDL "to access full Giovanni functionality". Guest mode is limited, and you must also authorize the "NASA GESDISC DATA ARCHIVE" application — [Giovanni User Guide 2024.1](https://giovanni.gsfc.nasa.gov/giovanni/doc/UsersManualworkingdocument.docx.html)
- Murcia quirk: the Mar Menor and coastal cells may mix land and sea. GES DISC publishes a land/sea mask for IMERG (GPM_IMERG_LandSeaMask v2) — [CMR IMERG collections search](https://cmr.earthdata.nasa.gov/search/collections.json?keyword=IMERG&page_size=60)

#### SMAP (OPTIONAL: L4 SPL4SMGP via AppEEARS; DROP L3 SPL3SMP_E)
- **SPL4SMGP v008**: "SMAP L4 Global 3-hourly 9 km EASE-Grid Surface and Root Zone Soil Moisture Geophysical Data, Version 8". EASE-Grid 2.0 (EPSG:6933), 3-hourly, **31 Mar 2015 to present**, HDF5. Free EDL required. Access via Earthdata Search, HTTPS, **earthaccess**, **Harmony**, Worldview, S3 us-west-2 and **AppEEARS**. A geolocation issue affected **14 May–28 Jul 2026** and those files are being reprocessed — [NSIDC SPL4SMGP v8](https://nsidc.org/data/spl4smgp/versions/8)
- SPL3SMP_E v006: 9 km daily, from 2015-03-31, latest granule 2026-11-12 (about 1-day latency) — [CMR SPL3SMP_E](https://cmr.earthdata.nasa.gov/search/concepts/C2938664763-NSIDC_CPRD.html). Revisit is 2–3 days, so daily L3 files have swath gaps — [EGU24-11751](https://meetingorganizer.copernicus.org/EGU24/EGU24-11751.html)
- AppEEARS has SPL3SMP_E.006, SPL3SMP.009 (36 km) and SPL4SMGP.008, with layers including `Geophysical_Data_sm_rootzone` and `..._pctl` (percentile, i.e. a ready-made anomaly) — [AppEEARS product list](https://appeears.earthdatacloud.nasa.gov/api/product)
- Murcia quirk: SPL3SMP_E includes `radar_water_body_fraction` and `retrieval_qual_flag` layers, which you need to screen Mar Menor and coastal cells — [AppEEARS SPL3SMP_E.006 layers](https://appeears.earthdatacloud.nasa.gov/api/product/SPL3SMP_E.006)

#### MODIS (KEEP MOD13Q1/MYD13Q1; OPTIONAL MOD16A2GF, MOD11A2; DROP MCD12Q1) and VIIRS continuity (OPTIONAL)
- MOD13Q1 v061: Terra 250 m 16-day VI, from 2000-02-18. MYD13Q1 v061: Aqua, from 2002-07-04 — [CMR MOD13Q1](https://cmr.earthdata.nasa.gov/search/concepts/C1748066515-LPCLOUD.html); [CMR MYD13Q1](https://cmr.earthdata.nasa.gov/search/concepts/C2307290656-LPCLOUD.html). The two interleave, so together they give an 8-day cadence (standard MODIS VI design; inference from the two 16-day products, not verified on a doc page).
- MOD16A2GF v061: 500 m 8-day gap-filled ET (ET, PET), from 2000. MOD11A2 v061: 1 km 8-day LST. MCD12Q1 v061: 500 m yearly land cover (2001–2025) — [CMR MOD16A2GF](https://cmr.earthdata.nasa.gov/search/concepts/C2565791021-LPCLOUD.html); [CMR MOD11A2](https://cmr.earthdata.nasa.gov/search/concepts/C2269056084-LPCLOUD.html); [CMR MCD12Q1](https://cmr.earthdata.nasa.gov/search/concepts/C2484079608-LPCLOUD.html)
- **Terra/Aqua end of life:** NASA projects end of science for **Terra in February 2027 and Aqua in September 2027** (with an editor's note that this is not immediate) — [NASA "Terra: the end of an era"](https://science.nasa.gov/science-research/earth-science/terra-the-end-of-an-era). Earthdata says that in "late 2026/early 2027" the Terra and Aqua platforms "will begin shutting down operations" and recommends VIIRS — [Earthdata MODIS→VIIRS transition](https://www.earthdata.nasa.gov/data/alerts-outages/transition-from-modis-viirs). An older LAADS notice gave Aqua MODIS an end date of Aug 2026 — [LAADS Aqua acquisition plan](https://ladsweb.modaps.eosdis.nasa.gov/alerts-and-issues/171807). The MCST weekly report for 18–24 Jul 2026 shows Terra MODIS in nominal science mode — [MCST weekly](https://mcst.gsfc.nasa.gov/iot/am1weekly20261992026205). **CMR confirms MOD13Q1 granules up to 2026-10-16 and MYD13Q1 up to 2026-10-24.**
- VIIRS continuity: **VNP13A1/VJ113A1 v002 are 500 m** 16-day VI (from 2012-01-17 and 2018-01-01). There is no 250 m VIIRS VI in AppEEARS (VNP13Q1 was not found in CMR). VNP21A1D v002 is 1 km daily LST — [CMR VNP13A1](https://cmr.earthdata.nasa.gov/search/concepts/C2519127224-LPCLOUD.html); [AppEEARS product list](https://appeears.earthdatacloud.nasa.gov/api/product)

#### Landsat Collection 2 and HLS (KEEP HLS-VI; raw Landsat C2 DROP unless pre-2013 30 m needed)
- HLS: HLSL30 (Landsat 8/9 OLI) and HLSS30 (Sentinel-2A/B/C MSI) harmonized to **30 m**. Combined revisit "every 1.6 days" (1.4 days with five satellites in 2025). Latency is "two to three day". Format is COG on the MGRS tile system (109.8 km tiles). **HLS VI products were introduced in February 2025.** Sentinel-2C is incorporated. Low-latency HLS is expected in 2027 — [Earthdata HLS project page](https://www.earthdata.nasa.gov/data/projects/hls)
- Start dates: HLSL30 from 2013-04-11, HLSS30 from 2015-11-28 (the VI versions match) — [CMR HLSL30](https://cmr.earthdata.nasa.gov/search/concepts/C2021957657-LPCLOUD.html); [CMR HLSS30_VI](https://cmr.earthdata.nasa.gov/search/concepts/C3246894861-LPCLOUD.html)
- Murcia cloudiness (from the CMR test): 2024 had **151 HLS scenes over Cartagena (84 L30 + 67 S30)**, with mean scene cloud around 30 % and **78 scenes under 20 % cloud**. That is roughly 6–7 usable looks per month, enough for a monthly bare-soil calendar — [CMR granule search](https://cmr.earthdata.nasa.gov/search/granules.json?short_name=HLSL30&version=2.0&point=-0.97,37.72&temporal=2024-01-01T00:00:00Z,2024-12-31T23:59:59Z&page_size=2000)

#### ECOSTRESS (OPTIONAL: LST heat-stress snapshots; JET/ESI too sparse over Murcia)
- Collection 2 tiled products at 70 m (LPCLOUD), from 2018-07: ECO_L2T_LSTE, ECO_L3T_JET (ET), ECO_L4T_ESI, ECO_L4T_WUE — [CMR ECO_L2T_LSTE v002](https://cmr.earthdata.nasa.gov/search/concepts/C2076090826-LPCLOUD.html). The v003 catalogue lists coverage N 54° to S 54° — [Earthdata catalog ECO_L2T_LSTE v003](https://www.earthdata.nasa.gov/data/catalog/lpcloud-eco-l2t-lste-003)
- **Collection 3 (v003):**
  - Level 2 released 1 May 2026 (improved cloud mask, automated geolocation correction, improved NDVI/albedo) — [Earthdata alert L2 v3](https://www.earthdata.nasa.gov/data/alerts-outages/ecostress-version-3-level-2-data-products-released)
  - Level 1 notice dated 3 Aug 2026 — [Earthdata alert L1 v3](https://www.earthdata.nasa.gov/data/alerts-outages/ecostress-version-3-level-1-data-products-released)
  - Level 3/4 (ETAUX, JET PT-JPL, ESI, WUE) released **26 May 2026** as COG. They cover **only acquisitions from 1 Oct 2025 onward**, with "historical processing of the ECOSTRESS acquisition archive planned at a later date" — [Earthdata alert L3/L4 v3](https://www.earthdata.nasa.gov/data/alerts-outages/ecostress-version-3-higher-level-data-products-released)
- AppEEARS still lists only v002 ECOSTRESS products ("ISS-dependent" temporal granularity) — [AppEEARS product list](https://appeears.earthdatacloud.nasa.gov/api/product)
- Murcia coverage (CMR test): about **28–57 LSTE scenes per year** over Cartagena. Acquisition times are spread across the whole day and night (UTC 0–23), and months are uneven (0 in Apr 2024). Over the same point, ET (JET) and ESI v002 exist for only **1–13 scenes per year** (2 in 2024). See the Q1 table.

#### GRACE / GRACE-FO (OPTIONAL: one regional water-storage trend chart; not field-level)
- JPL mascons **RL06.3 v04**: 3° equal-area spherical-cap mascons (4,551 mascons) on a 0.5° grid (cells not independent). The CRI filter splits land and ocean in coastal mascons. Land gain factors are **not applied** (optional) and "may not suit trend quantification". The file is a single netCDF holding all months, with anomalies relative to 2004.0–2009.999, and the record has gaps — [JPL GRACE Tellus mascons](https://grace.jpl.nasa.gov/data/get-data/jpl_global_mascons/)
- PO.DAAC short name `TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4`, cloud-hosted. The current file runs **2002-04 to 2026-09** — [PO.DAAC dataset](https://podaac.jpl.nasa.gov/dataset/TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4); [CMR collection](https://cmr.earthdata.nasa.gov/search/concepts/C3195527175-POCLOUD.html)

#### SRTM / NASADEM (KEEP: slope, erosion risk, cold-air pockets)
- SRTMGL1 v003 (1 arc-second, ~30 m) and NASADEM_HGT v001 (1 arc-second). Both are static (Feb 2000) at LPCLOUD — [CMR SRTMGL1](https://cmr.earthdata.nasa.gov/search/concepts/C2763266360-LPCLOUD.html); [CMR NASADEM_HGT](https://cmr.earthdata.nasa.gov/search/concepts/C2763264762-LPCLOUD.html)
- AppEEARS serves SRTMGL1_NC.003 (layer `SRTMGL1_DEM`), SRTMGL3_NC.003 (90 m), NASADEM_NC.001 and ASTGTM_NC.003 — [AppEEARS product list](https://appeears.earthdatacloud.nasa.gov/api/product)

#### Newer NASA products (post-2024) relevant to Murcia
- **HLS-VI** (HLSL30_VI / HLSS30_VI v2.0, NDVI/EVI at 30 m, in AppEEARS): introduced Feb 2025. **KEEP** (this is the field-scale vegetation layer) — [Earthdata HLS](https://www.earthdata.nasa.gov/data/projects/hls)
- **OPERA DSWx-HLS** (surface water, 30 m, from 2016, 1,471 granules over Cartagena) and **DIST-ALERT/DIST-ANN-HLS** (vegetation disturbance from 2023, 635 granules) — [CMR DSWx](https://cmr.earthdata.nasa.gov/search/concepts/C2617126679-POCLOUD.html); [CMR DIST-ALERT](https://cmr.earthdata.nasa.gov/search/concepts/C2746980408-LPCLOUD.html). **OPTIONAL**
- **NISAR**: ASF hosts Beta (from Oct 2025), Provisional and "Validated" L1/L2 collections, plus **NISAR_L3_SME2 soil moisture** (Beta and Provisional) — [CMR NISAR search](https://cmr.earthdata.nasa.gov/search/collections.json?keyword=NISAR&page_size=60)
  - SME2 is "field-scale (200m) posting" from three algorithms, with an accuracy goal of 0.06 m³/m³ where vegetation water content is <5 kg/m² — [ASF NISAR products overview (test docs site)](https://nisar-docs-test.asf.alaska.edu/products-overview)
  - Provisional products cover acquisitions from **17 Jun 2026** (same source). The data.gov catalogue still labels the soil moisture dataset "Beta" — [data.gov NISAR Beta Soil Moisture](https://catalog.data.gov/dataset/nisar-beta-soil-moisture-version-1)
  - ISRO separately plans a 100 m L4 soil moisture product via its Bhoonidhi portal — [ISRO](https://www.isro.gov.in/NisarData_soil_moisture_products.html)
  - There is **no dedicated NISAR crop-area product**. GCOV is meant to support "crop area delineation" — [ASF overview](https://nisar-docs-test.asf.alaska.edu/products-overview)
  - CMR: **50 SME2 provisional granules over Cartagena**, latest 2026-10-16. **OPTIONAL/curiosity**: the record is too short for a climatology.

### Inferences
**Verdict table** (my synthesis of the facts above; "field" means a 0.5–10 ha Murcia parcel):

| Dataset | Variable it contributes | Pixel vs a 1 ha field | Auth | Fastest access | Verdict |
|---|---|---|---|---|---|
| POWER (MERRA-2) | Tmax/Tmin, heat days, frost (Tmin<0), RH, wind, radiation, 1981→ | ~3,000 km² cell | none | REST point API, 2 s per 20 years | **KEEP** |
| IMERG via POWER (`IMERG_PRECTOT`, UTC) | Rainfall, extreme-rain days, dry spells, 2000→ | ~100 km² cell | none | Same API | **KEEP** |
| IMERG direct (GES DISC / Giovanni / OPeNDAP) | Same as above | Same | EDL | Giovanni or earthaccess | **DROP** (POWER is enough) |
| HLS-VI 30 m (S30+L30) | NDVI/EVI, bare-soil months, crop calendar, 2013/2015→ | 0.09 ha, so ~11 px per ha | EDL | AppEEARS point/area | **KEEP** |
| MOD13Q1+MYD13Q1 250 m | 25-year NDVI history, multi-year stress anomalies | 6.25 ha (mixed pixels) | EDL | AppEEARS point | **KEEP** (history), say "neighbourhood-scale" |
| VNP13A1 500 m | MODIS continuity after 2027 | 25 ha | EDL | AppEEARS | OPTIONAL |
| MOD16A2GF 500 m | Actual ET/PET, water-use proxy | 25 ha | EDL | AppEEARS | OPTIONAL |
| MOD11A2 / VNP21A1D 1 km | LST, heat stress | 100 ha | EDL | AppEEARS | OPTIONAL |
| MCD12Q1 500 m | Land cover | 25 ha | EDL | AppEEARS | DROP (use SIGPAC/CORINE locally) |
| SMAP L4 SPL4SMGP 9 km | Root-zone soil moisture + percentile anomaly, 2015→ | 8,100 ha | EDL | AppEEARS point | OPTIONAL (regional water-stress context) |
| SMAP L3 SPL3SMP_E 9 km | Surface SM | 8,100 ha | EDL | AppEEARS | DROP (gaps, coastal flags) |
| ECOSTRESS LSTE v002 70 m | Hottest-day LST snapshot | 0.49 ha | EDL | AppEEARS area | OPTIONAL (one heat-stress map) |
| ECOSTRESS JET/ESI/WUE | ET, evaporative stress | 0.49 ha | EDL | AppEEARS / earthaccess | OPTIONAL-to-DROP (1–13 scenes/yr) |
| GRACE/GRACE-FO JPL mascon | Regional water-storage trend 2002→2026 | ~112,000 km² mascon | EDL | earthaccess, one netCDF | OPTIONAL (pitch chart) |
| SRTM / NASADEM 30 m | Slope (erosion), relative elevation (frost pockets), aspect | 0.09 ha | EDL | AppEEARS area or OpenTopography | **KEEP** |
| OPERA DIST-ALERT | Vegetation-loss alerts (harvest/clearing) | 0.09 ha | EDL | earthaccess | OPTIONAL |
| NISAR SME2 200 m | Field-scale soil moisture (provisional) | 4 ha | EDL | ASF / earthaccess | OPTIONAL (demo "wow", not analysis) |

- The pixel figures are arithmetic. 250 m² is 6.25 ha; 500 m² is 25 ha; 70 m² is 0.49 ha; 30 m² is 0.09 ha. 0.5°×0.625° at 38 °N is about 55 × 55 km. The mascon size is Earth's 510 M km² divided by 4,551.
- Terra/Aqua are still producing as of Nov 2026, but the team should label MODIS as "2000–2026 history" and show VIIRS VNP13A1 or HLS as the continuity path. Judges may ask about this.
- ECOSTRESS is not a time series over Murcia. Use it only as "the hottest observed afternoon LST on this parcel": filter LSTE scenes to local 12–16 h in Jun–Aug, cloud-free.

### Gaps
- No official doc gives AppEEARS per-request limits or queue times (see Q6).
- I did not verify the CSR GRACE mascon specifics (0.25° grid / ~1° mascons from memory) during this session.
- Prithvi (NASA/IBM HLS foundation model) status as of Nov 2026: not researched in this session.
- Raw Landsat C2 access (USGS M2M API / AWS `usgs-landsat` requester-pays bucket) was not checked live. HLS L30 covers the 2013→ need.
- Better alternatives to SRTM for Spain (Copernicus DEM GLO-30; IGN/CNIG LiDAR MDT05/MDT02 at https://centrodedescargas.cnig.es) were not fetched or verified in this session. IGN LiDAR is likely much better for frost-pocket and erosion modelling on small parcels.

---

## Q3. Fastest way to get a 20-year (or full-record) series for one field

### Takeaway
Climate and rain: one POWER call each, about 2 s, no login. Vegetation, soil moisture, LST, ET and DEM: **one AppEEARS point
task** with all layers (EDL token, queued, minutes to hours). GRACE: one netCDF via earthaccess. Everything else is slower.

### Cited Findings
- POWER 20-year daily (10 params): 2.0–2.4 s, ~1.2 MB. IMERG 2000–2025: 1.65 s — [POWER daily API](https://power.larc.nasa.gov/api/temporal/daily/point?parameters=IMERG_PRECTOT,PRECTOTCORR&community=AG&longitude=-0.97&latitude=37.72&start=20000101&end=20251231&format=JSON&time-standard=UTC)
- AppEEARS point task (one JSON, many layers, many coordinates) and area task (GeoJSON polygon, output `geotiff` or `netcdf4`). Point bundles include CSV — [AppEEARS API](https://appeears.earthdatacloud.nasa.gov/api/)
- GRACE JPL mascon is "a single file containing all months, updated with each new month" — [JPL GRACE Tellus](https://grace.jpl.nasa.gov/data/get-data/jpl_global_mascons/)

**Exact requests for EDL-protected services (documented, NOT executed):**

1) AppEEARS: one point task for both test points, 2005–2025:
```bash
TOKEN=$(curl -s -u "$EDL_USER:$EDL_PASS" -X POST https://appeears.earthdatacloud.nasa.gov/api/login | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')
cat > task.json <<'EOF'
{"task_type":"point","task_name":"murcia-fieldshift",
 "params":{"dates":[{"startDate":"01-01-2005","endDate":"12-31-2025"}],
  "layers":[
   {"product":"MOD13Q1.061","layer":"_250m_16_days_NDVI"},
   {"product":"MOD13Q1.061","layer":"_250m_16_days_pixel_reliability"},
   {"product":"MYD13Q1.061","layer":"_250m_16_days_NDVI"},
   {"product":"MOD16A2GF.061","layer":"ET_500m"},
   {"product":"SPL4SMGP.008","layer":"Geophysical_Data_sm_rootzone"},
   {"product":"SPL4SMGP.008","layer":"Geophysical_Data_sm_rootzone_pctl"},
   {"product":"HLSS30_VI.020","layer":"NDVI"},
   {"product":"HLSL30_VI.020","layer":"NDVI"},
   {"product":"ECO_L2T_LSTE.002","layer":"LST"},
   {"product":"SRTMGL1_NC.003","layer":"SRTMGL1_DEM"}],
  "coordinates":[{"id":"cartagena","latitude":37.72,"longitude":-0.97},
                 {"id":"jumilla","latitude":38.47,"longitude":-1.33}]}}
EOF
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d @task.json https://appeears.earthdatacloud.nasa.gov/api/task   # -> 202 + task_id
curl -s -H "Authorization: Bearer $TOKEN" https://appeears.earthdatacloud.nasa.gov/api/status/$TASK_ID   # pending|processing|done
curl -s -H "Authorization: Bearer $TOKEN" https://appeears.earthdatacloud.nasa.gov/api/bundle/$TASK_ID   # list files
curl -sL -H "Authorization: Bearer $TOKEN" https://appeears.earthdatacloud.nasa.gov/api/bundle/$TASK_ID/$FILE_ID -o out.csv
```
Endpoints and JSON shape come from [AppEEARS API](https://appeears.earthdatacloud.nasa.gov/api/). Layer names come from `GET /api/product/{id}` (Q1). Date format is `MM-DD-YYYY`.

2) GRACE (earthaccess, Python):
```python
import earthaccess
earthaccess.login(strategy="netrc")   # or environment variables; needs EDL
res = earthaccess.search_data(short_name="TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4")
earthaccess.download(res, "data/grace")   # single netCDF, all months 2002-04..2026-09
```
earthaccess is a listed NSIDC/Earthdata access method — [NSIDC SPL4SMGP v8](https://nsidc.org/data/spl4smgp/versions/8)

### Inferences
- Expected AppEEARS wait (an estimate, not documented): point tasks with MODIS/SMAP for 2 points over 20 years usually finish in minutes to roughly an hour. Adding HLS and ECOSTRESS can push that to hours. **Submit on Friday night, split into two tasks** (fast: MODIS+SMAP+SRTM; slow: HLS+ECOSTRESS), and cache the CSVs in the repo.
- For a field polygon (not a point), use an AppEEARS **area** task clipped to the parcel with HLS-VI + SRTM, output `geotiff`. Keep the date range short (e.g., 2023–2025) to stay within the time budget.
- The MODIS 250 m point series is the only vegetation record spanning 2000→2026 at near-field scale. HLS gives true field scale from 2013/2015.

### Gaps
- No measured AppEEARS turnaround times (not executed, no credentials).
- GRACE netCDF file size not checked (may exceed 50 MB; not downloaded).

---

## Q4. Which need Earthdata Login and which don't

### Takeaway
**No login:** POWER (all parameters, including IMERG_PRECTOT), CMR search (collections and granules), the AppEEARS product
catalogue. **EDL required:** every actual data download, i.e. AppEEARS tasks, GES DISC/OPeNDAP/Giovanni (full), NSIDC SMAP,
LP DAAC (HLS, MODIS, ECOSTRESS, SRTM), PO.DAAC GRACE, ASF NISAR, earthaccess, Harmony.

### Cited Findings
- POWER, CMR and the AppEEARS `/api/product` endpoints all returned HTTP 200 without credentials (Q1 tests) — [POWER](https://power.larc.nasa.gov/api/temporal/daily/configuration); [CMR](https://cmr.earthdata.nasa.gov/search/collections.json?short_name=HLSS30&page_size=10); [AppEEARS products](https://appeears.earthdatacloud.nasa.gov/api/product)
- AppEEARS `POST /api/login` uses Earthdata Login (HTTP Basic) and returns a Bearer token that expires "approximately 48 hours" later — [AppEEARS API](https://appeears.earthdatacloud.nasa.gov/api/)
- SMAP at NSIDC needs a free EDL account; S3 access needs extra credentials — [NSIDC SPL4SMGP v8](https://nsidc.org/data/spl4smgp/versions/8)
- Giovanni needs EDL for full functionality plus authorization of the GES DISC application; guest mode is limited — [Giovanni User Guide](https://giovanni.gsfc.nasa.gov/giovanni/doc/UsersManualworkingdocument.docx.html)

### Inferences
- **Each teammate who will run AppEEARS needs their own EDL account, created by the human** (agents must not create accounts). Store `EARTHDATA_USERNAME/PASSWORD` or `~/.netrc` locally. Never commit them.
- A demo built only on POWER + cached AppEEARS CSVs has zero runtime auth dependency. Good for venue Wi-Fi.

### Gaps
- Whether OPeNDAP at GES DISC still serves IMERG V07 Final after the V08 switch was not checked.

---

## Q5. Field scale vs regional scale

### Takeaway
Field scale (0.5–10 ha): HLS-VI 30 m, SRTM/NASADEM 30 m, ECOSTRESS 70 m (snapshots), NISAR SME2 200 m (provisional).
Neighbourhood: MODIS 250 m. Landscape: MODIS/VIIRS 500 m–1 km. Regional: SMAP 9 km, IMERG ~10 km, POWER ~55 km. Basin or
larger: GRACE (~112,000 km² mascons).

### Cited Findings
- HLS 30 m — [Earthdata HLS](https://www.earthdata.nasa.gov/data/projects/hls); ECOSTRESS 70 m — [CMR ECO_L2T_LSTE](https://cmr.earthdata.nasa.gov/search/concepts/C2076090826-LPCLOUD.html); MOD13Q1 250 m — [CMR MOD13Q1](https://cmr.earthdata.nasa.gov/search/concepts/C1748066515-LPCLOUD.html); SMAP 9 km — [NSIDC](https://nsidc.org/data/spl4smgp/versions/8); IMERG 0.1° and POWER ½°×⅝° — [POWER methodology](https://power.larc.nasa.gov/docs/methodology/); GRACE 3° mascons — [JPL](https://grace.jpl.nasa.gov/data/get-data/jpl_global_mascons/); NISAR SME2 200 m — [ASF overview](https://nisar-docs-test.asf.alaska.edu/products-overview)

### Inferences
- UI rule: label every chart with its scale ("your field", "your area ~6 ha", "your comarca ~10 km", "SE Spain ~300 km"). The challenge asks for transparent uncertainty.
- A 0.5 ha Campo de Cartagena plot is about 5–6 HLS pixels (a 10 ha plot is ~110), about 1 ECOSTRESS pixel, and 8 % of one MODIS 250 m pixel. MODIS is fine for the "typical bare months in this area" calendar but not for one parcel.
- Near the Mar Menor and the coast, SMAP and POWER cells include water or sea. Prefer the Altiplano/Jumilla or Vega del Segura inland points for soil-moisture storytelling, or screen with the SMAP water-fraction flags.

### Gaps
- No quantitative validation of HLS NDVI against Murcia parcel data was found in this session.

---

## Q6. AppEEARS API: auth, request types, limits, timing

### Takeaway
Token-based REST API: `POST /login` (EDL basic auth, then a ~48 h bearer token), `POST /task` (point or area JSON), poll
`/status/{id}`, download via `/bundle/{id}/{file}`, which redirects to S3 links valid 48 h. No published per-request limits; a
429 means slow down. Processing time "will vary depending on the temporal range, number of points, and products/layers".

### Cited Findings
- Endpoints: `/api/login`, `/api/logout`, `/api/task`, `/api/status/{task_id}` (pending / processing / done / error, with percent complete), `/api/task/{task_id}`, `/api/bundle/{task_id}` (files with SHA-256), `/api/bundle/{task_id}/{file_id}` (302 to an S3 URL valid 48 h), `/api/s3credentials` (1 h). Area output: `geotiff` or `netcdf4`. Projections from `/api/spatial/proj`. Dates use `MM-DD-YYYY`. Geometry must be EPSG:4326. `expires_on` in the examples is about 30 days after completion. A `pending` task is "waiting until resources are available" — [AppEEARS API](https://appeears.earthdatacloud.nasa.gov/api/)
- "The time required to receive the results of a request will vary depending on the temporal range, number of points, and products/layers selected" — [Earthdata AppEEARS point tutorial](https://www.earthdata.nasa.gov/learn/tutorials/access-landsat-8-surface-reflectance-point-data-appeears)
- The R `appeears` package notes most services are limited to ~20 concurrent requests (package default 2) — [appeears R manual](https://bluegreen-labs.r-universe.dev/appeears/doc/manual.html)
- 193 products available. GPM/IMERG, GRACE and ECOSTRESS v003 are absent — [AppEEARS product list](https://appeears.earthdatacloud.nasa.gov/api/product)

### Inferences
- Use one point task per data family so the slow HLS/ECOSTRESS extraction doesn't block MODIS/SMAP.
- Bundles expire (~30 days), so copy results into the repo's cached data folder right away.

### Gaps
- No official maximum on points per request, area size or queue length was found. The AppEEARS `/help` page could not be read by the fetch tool (JavaScript-rendered).

---

## Q7. Published studies using these datasets in Murcia / Segura basin / SE Spain

### Takeaway
There is solid literature on Landsat/MODIS ET and irrigated-area mapping in the Segura basin and Campo de Cartagena
(FutureWater/SIRRIMED, Hunink et al. 2015). I found GRACE studies for southern Spain and the Euro-Mediterranean region, but
**none specific to the Segura basin**. SMAP validation near SE Spain exists only as conference abstracts.

### Cited Findings
- **Hunink et al. (2015), Agricultural Water Management**: a remote-sensing water balance linking cropping patterns (perennial fruit trees vs seasonal row crops) to groundwater abstraction in Campo de Cartagena — [FutureWater PDF](https://futurewater.nl/wp-content/uploads/2015/09/Hunink_etal_2015_gw.pdf)
- **FutureWater / SIRRIMED (2014)**: a watershed information and decision-support system for Campo de Cartagena combining hydrological modelling and remote sensing, including mapped irrigated zones — [SIRRIMED WP5 report](https://www.futurewater.nl/wp-content/uploads/2014/07/SIRRIMED_WP5-FutureWater-Report125.pdf)
- Segura basin work found in the same search, not opened individually: Landsat 5 TM + SPOT 5 + MODIS (2012); Landsat-5 ET validated against eddy covariance in two **Campo de Cartagena citrus orchards (R² > 0.80, RMSE ± 50 W/m²)**; and Segura water accounting pairing Landsat (plot) with MODIS (basin). Candidate sources: [EGU2013-12229](https://meetingorganizer.copernicus.org/EGU2013/EGU2013-12229.pdf), [CIHEAM Options Méditerranéennes B67](https://ressources.ciheam.org/ressources/om/pdf/b67/00006601.pdf), [EGU21-14478](https://meetingorganizer.copernicus.org/EGU21/EGU21-14478.html). The search tool's summary did not say which claim belongs to which URL.
- Campo de Cartagena irrigated area of about 35,000 ha, mainly citrus and horticultural row crops (same search; source attribution uncertain, likely the FutureWater documents above) — [SIRRIMED WP5 report](https://www.futurewater.nl/wp-content/uploads/2014/07/SIRRIMED_WP5-FutureWater-Report125.pdf)
- 2024 UPM thesis: Sentinel-2 NDVI/NDMI used to map **illegally irrigated areas** (2019→) in the Segura area — [TFG Diego Celdrán (UPM)](https://blogs.upm.es/dynamicland/wp-content/uploads/sites/294/2024/05/TFG_DiegoCeldran.pdf)
- **GRACE, Euro-Mediterranean:** Xanke & Liesch (2022), Hydrogeology Journal 30(2):379–400. GRACE/GRACE-FO with ERA5-Land, 2003–2020. About 70 % of the region shows significantly negative groundwater trends, with a mean of **-2.1 mm/yr**. Southern Spain is named among the over-extraction regions — [KIT repository](https://publikationen.bibliothek.kit.edu/1000142673); [MedECC summary](https://www.medecc.org/quantification-and-possible-causes-of-declining-groundwater-resources-in-the-euro-mediterranean-region-from-2003-to-2020/)
- **GRACE, Andalucía (2023, Hydrology 10(9):187)**: GRACE with rainfall estimates. Groundwater storage depleted during the 2004–2010 drought had recovered almost to pre-drought level by 2016 — [Hydrology / MDPI](https://mdpi.com/2306-5338/10/9/187); [UGR repository](https://digibug.ugr.es/handle/10481/85357)
- **SMAP near SE Spain**: an EGU24 abstract evaluated SMAP L3 SPL3SMP_E against Copernicus SWI/SSM over an irrigated almond orchard (Tarazona de la Mancha, Albacete). SWI did best (RMSD 3.79 vol %, R² 0.36) — [EGU24-11751](https://meetingorganizer.copernicus.org/EGU24/EGU24-11751.html). EGU25 compared ASCAT/SMOS/SMAP/CCI in NE Spain and S France for 2015–2021 — [EGU25-5173](https://meetingorganizer.copernicus.org/EGU25/EGU25-5173.html)

### Inferences
- For the pitch: "Satellite ET at farm level has been validated in Campo de Cartagena citrus" supports using ET products, with caveats. "Southern Spain shows significant GRACE-detected groundwater decline" supports a water-scarcity framing. Cite both carefully: the GRACE number is Euro-Mediterranean, not Segura-specific.
- SMAP at 9 km performs poorly at field scale over irrigated plots (R² 0.36 for the best product in the almond study). That justifies labelling SMAP as regional context only.

### Gaps
- No peer-reviewed GRACE study isolating the Segura basin was found. The basin is much smaller than one 3° mascon.
- No peer-reviewed SMAP validation specifically in Murcia, Alicante or Almería was found.
- I did not open the full texts of the Segura ET/irrigation papers, so the attribution of individual numbers to specific URLs above rests on a search summary.
