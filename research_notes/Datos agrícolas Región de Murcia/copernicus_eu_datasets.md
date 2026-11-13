# Copernicus and other European/global open datasets for crop-rotation decision support in Región de Murcia: datasheets, access paths, live API tests, verdicts

Researched 2026-11-13 (the evening before hacking starts). Test points: Campo de Cartagena (lat 37.72, lon -0.97); Altiplano/Jumilla (lat 38.47, lon -1.33). Note that the Jumilla coordinate falls on the town itself: CORINE 2018 returns "Continuous urban fabric" there, so pick a point a few km outside town for real field demos. All live-test raw responses are under `/private/tmp/claude-501/-Users-jaime-Documents-NasaSpaceApps/324b317c-8037-4e23-a8f2-fde635abe82e/scratchpad/api-tests/copernicus/` (untrusted data, read with `python3 -I`). No accounts were created and no credentials were used.

## Q1. Live API tests: what answers without an account, how fast, and what it returns

### Takeaway
Every catalogue or metadata endpoint tested answered without login: the CDSE STAC and OData catalogues, openEO capabilities, the CDS process schemas, the EEA/CLMS ArcGIS identify services, Planetary Computer STAC, Earth Search STAC with public COGs, and Open-Meteo's ERA5 archive. SoilGrids also needs no login, but it is slow and unreliable for the Cartagena point (2 timeouts at 60 s, then about 35 s per call). Downloading pixels from CDSE (Sentinel, CLMS HRL Croplands) and running any processing (Sentinel Hub, openEO, CDS retrieve) needs a free account.

### Cited Findings
| # | Endpoint (no auth) | Exact request (abridged) | HTTP | Time | Sample result |
|---|---|---|---|---|---|
| 1 | SoilGrids REST, Jumilla | `curl --max-time 60 "https://rest.isric.org/soilgrids/v2.0/properties/query?lon=-1.33&lat=38.47&property=clay&property=sand&property=soc&property=phh2o&depth=0-5cm&depth=5-15cm&value=mean"` | 200 | 4.75 s (server `query_time_s` 3.3) | clay 26.8 / 28.2 %, sand 31.8 / 30.6 %, SOC 22.2 / 13.2 g/kg, pH(H2O) 7.8 / 8.0 (0-5 / 5-15 cm), after dividing by `d_factor` 10 |
| 2 | SoilGrids REST, Cartagena (same query, lon=-0.97 lat=37.72) | as above | 000 (timeout) twice at 60 s; single property `clay&depth=0-5cm` 200 in 37.0 s; full query 200 in 35.1 s with `--max-time 170` | 35-60 s | clay 31.4 / 34.6 %, sand 20.0 / 18.2 %, SOC 20.6 / 12.9 g/kg, pH 7.7 / 7.9. Server-side `query_time_s` was only 3.0 s, so the delay is queueing or throttling. — [SoilGrids REST](https://rest.isric.org/soilgrids/v2.0/properties/query) |
| 3 | CDSE STAC search, S2 L2A 2025, cloud <20 %, Cartagena | `curl -X POST https://stac.dataspace.copernicus.eu/v1/search -H "Content-Type: application/json" -d '{"collections":["sentinel-2-l2a"],"intersects":{"type":"Point","coordinates":[-0.97,37.72]},"datetime":"2025-01-01T00:00:00Z/2025-12-31T23:59:59Z","filter-lang":"cql2-json","filter":{"op":"<","args":[{"property":"eo:cloud_cover"},20]},"limit":100}'` | 200 | 6.5 s, 3.3 MB JSON | 51 items, all MGRS tile 30SXG, platforms S2A and S2C. Example `S2C_MSIL2A_20251230T105451_N0511_R051_T30SXG_20251230T143210` (cloud 2.46 %). Assets are JP2 (`B04_10m` is 103,818,271 bytes). Asset hrefs are `s3://eodata/...` plus an HTTPS alternate on `zipper.dataspace.copernicus.eu` with `auth:refs: oidc`, so downloads need a token. — [CDSE STAC](https://stac.dataspace.copernicus.eu/v1/search) |
| 4 | CDSE STAC, Jumilla, same S2 query | same, coordinates [-1.33,38.47] | 200 | 5.3 s | 45 items, tile 30SXH, platforms S2A/S2B/S2C — [CDSE STAC](https://stac.dataspace.copernicus.eu/v1/search) |
| 5 | CDSE STAC collection list | `curl "https://stac.dataspace.copernicus.eu/v1/collections?limit=500"` | 200 | 5.1 s | 428 collections. Includes `sentinel-1-grd`, `sentinel-2-l2a`, `sentinel-3-*`, `cop-dem-*`, MODIS, Landsat, and many `clms_*` collections, among them HRL Croplands (`clms_vlcc_*`), SSM/SWI 1 km and ETa 300 m. Without `?limit=` it returns only 10. — [CDSE STAC collections](https://stac.dataspace.copernicus.eu/v1/collections?limit=500) |
| 6 | CDSE STAC, HRL Crop Types at Cartagena | POST search with `collections: ["clms_vlcc_crop-types_europe_10m_yearly_v1", ...]` and the point | 200 | 0.56 s | One COG per year, 2017-2024, tile `E33N16` (EPSG:3035, 100×100 km, 10000×10000 px, uint16), about 1.4-1.9 MB each (e.g. `CLMS_HRLVLCC_CTY_S2024_R10m_E33N16_03035_V01_R00`, 1,869,435 bytes). Download is via `https://download.dataspace.copernicus.eu/odata/v1/Products(<uuid>)/...` (OIDC) or S3. Jumilla is in tile `E33N17` (8 years). — [CDSE STAC](https://stac.dataspace.copernicus.eu/v1/search) |
| 7 | CDSE OData catalogue, S1, 1-15 Jun 2025 | `curl "https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Collection/Name eq 'SENTINEL-1' and OData.CSC.Intersects(area=geography'SRID=4326;POINT(-0.97 37.72)') and ContentDate/Start gt 2025-06-01T00:00:00.000Z and ContentDate/Start lt 2025-06-15T00:00:00.000Z&$top=5"` (URL-encoded) | 200 | 1.3 s | `S1A_IW_GRDH_1SDV_20250605T060249_..._COG.SAFE` (929,711,124 bytes) and `S1A_IW_GRDH_..._20250610T061059` (1,772,332,683 bytes), plus S1C products (`S1C_IW_ETA__...`, `S1C_IW_OCN__...`) — [CDSE OData](https://catalogue.dataspace.copernicus.eu/odata/v1/Products) |
| 8 | openEO capabilities and collections | `curl https://openeo.dataspace.copernicus.eu/openeo/1.2/` and `/collections` | 200 / 200 | 0.31 s / 0.64 s | "Copernicus Data Space Ecosystem openEO API", API 1.2.0, backend 0.74.0a6.dev20261109. 138 collections, including `SENTINEL2_L2A`, `SENTINEL1_GRD`, `COPERNICUS_VEGETATION_PHENOLOGY_PRODUCTIVITY_10M_SEASON1/2`, `COPERNICUS_PLANT_PHENOLOGY_INDEX`, `ESA_WORLDCOVER_10M_2021_V2`, and all `CLMS_VLCC_*` crop layers — [openEO CDSE](https://openeo.dataspace.copernicus.eu/openeo/1.2/collections) |
| 9 | Sentinel Hub Statistical API without a token | `curl -X POST https://sh.dataspace.copernicus.eu/api/v1/statistics -d '{}'` | 401 | 0.37 s | `"You are not authorized! Please provide a valid access token..."`, which confirms the endpoint and that a token is required — [SH statistics](https://sh.dataspace.copernicus.eu/api/v1/statistics) |
| 10 | CDSE OIDC discovery | `curl https://identity.dataspace.copernicus.eu/auth/realms/CDSE/.well-known/openid-configuration` | 200 | <1 s | token endpoint `https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token` — [CDSE OIDC](https://identity.dataspace.copernicus.eu/auth/realms/CDSE/.well-known/openid-configuration) |
| 11 | CDS process schema (no login) | `curl https://cds.climate.copernicus.eu/api/retrieve/v1/processes/reanalysis-era5-land-timeseries` | 200 | 0.35 s | inputs `variable` (20 options: `2m_temperature`, `total_precipitation`, `volumetric_soil_water_level_1..4`, `soil_temperature_level_1..4`, `surface_solar_radiation_downwards`, ...; **no evaporation variable**), `data_format` [`csv`,`netcdf`], `area`. Schemas for `reanalysis-era5-land`, `derived-era5-land-daily-statistics`, `sis-agroclimatic-indicators`, `insitu-gridded-observations-europe`, `projections-cmip6`, `seasonal-original-single-levels` and `satellite-soil-moisture` also answered 200 in 0.2-2.3 s — [CDS processes API](https://cds.climate.copernicus.eu/api/retrieve/v1/processes/reanalysis-era5-land-timeseries) |
| 12 | EEA/CLMS CORINE 2018 identify, Cartagena | `curl "https://image.discomap.eea.europa.eu/arcgis/rest/services/Corine/CLC2018_WM/MapServer/identify?geometry=-0.97,37.72&geometryType=esriGeometryPoint&sr=4326&layers=all&tolerance=1&mapExtent=-1.1,37.6,-0.8,37.8&imageDisplay=400,400,96&returnGeometry=false&f=json"` | 200 | 0.44 s | `Code_18: 212`, `LABEL3: Permanently irrigated land` — [EEA discomap CLC2018](https://image.discomap.eea.europa.eu/arcgis/rest/services/Corine/CLC2018_WM/MapServer/identify) |
| 13 | EEA discomap service list | `curl "https://image.discomap.eea.europa.eu/arcgis/rest/services?f=json"` | 200 | 0.34 s | folders include `Corine`, `CLC_plus`, `EGMS_ERM`, `GioLandPublic` (older HRLs 2012-2021: grassland, imperviousness, small woody features...), `LUCAS`, `MR_VPP` (Start/End/Length of season 2000-2019), `Land_Productivity`. Note: **HRL Croplands and HR-VPP 10 m are not exposed here.** — [EEA discomap](https://image.discomap.eea.europa.eu/arcgis/rest/services?f=json) |
| 14 | MR-VPP Start of season identify | `.../MR_VPP/Start_of_season_2000_2019/ImageServer/identify?geometry={x:-0.97,y:37.72,wkid:4326}...` | 200 | 0.51 s | `"value":"3"` (meaning not documented in the response) — [EEA MR_VPP](https://image.discomap.eea.europa.eu/arcgis/rest/services/MR_VPP/Start_of_season_2000_2019/ImageServer) |
| 15 | Planetary Computer STAC, ESA WorldCover | `curl -X POST https://planetarycomputer.microsoft.com/api/stac/v1/search -d '{"collections":["esa-worldcover"],"intersects":{"type":"Point","coordinates":[-0.97,37.72]}}'` | 200 | 0.25 s | `ESA_WorldCover_10m_2021_v200_N36W003` and `..._2020_v100_N36W003` (COG on Azure blob) — [Planetary Computer STAC](https://planetarycomputer.microsoft.com/api/stac/v1/search) |
| 16 | Earth Search (AWS) S2 C1 L2A COGs | `curl -X POST https://earth-search.aws.element84.com/v1/search -d '{"collections":["sentinel-2-c1-l2a"],"intersects":{...[-0.97,37.72]},"datetime":"2025-01-01T00:00:00Z/2025-12-31T23:59:59Z","query":{"eo:cloud_cover":{"lt":20}},"limit":100}'`, then `curl -I .../S2C_T30SXG_20251230T105452_L2A/B04.tif` | 200 / 200 | 1.6 s / <1 s | 51 matched, the same count as CDSE. The COG `B04.tif` is 181,208,983 bytes with `Accept-Ranges: bytes`, so pixel windows can be read over HTTP with GDAL/rasterio and no account — [Earth Search](https://earth-search.aws.element84.com/v1/search) |
| 17 | Open-Meteo archive (ERA5 / ERA5-Land, no key) | `curl "https://archive-api.open-meteo.com/v1/archive?latitude=37.72&longitude=-0.97&start_date=2024-01-01&end_date=2024-12-31&daily=precipitation_sum,et0_fao_evapotranspiration,temperature_2m_max&models=era5&timezone=Europe%2FMadrid"` | 200 | 0.29 s | ERA5 grid cell 37.75, -1.0: 2024 precipitation 184.7 mm, FAO ET0 1482.7 mm, max Tmax 35.5 °C. With `models=era5_land` (0.53 s), the grid cell is 37.70, -1.00, elevation 41 m. Hourly `soil_moisture_0_to_7cm` 2024: min 0.095, mean 0.134, max 0.423 m³/m³. **Daily `precipitation_sum` and `et0_fao_evapotranspiration` came back null for all 366 days with `era5_land`**, so use `era5` for those. — [Open-Meteo archive API](https://archive-api.open-meteo.com/v1/archive) |
| 18 | EuroCrops v2 file index (JRC FTP) | `curl https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/DRLL/EuroCropsV2/all_gpqt_files.csv`, then `curl -I .../gpqtv202/es_2023.parquet` | 200 | 0.27 s | Spain files: `es_2021`, `es_2022`, `es_2023`. Sizes (v2.0.2): es_2021 9,374,393,017 B; es_2023 11,313,319,610 B; es_stack 5,495,897,595 B — [EuroCropsV2 FTP](https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/DRLL/EuroCropsV2/) |

### Inferences
- With no account at all, the team can get, in under 30 minutes: S2 scene lists (CDSE or Earth Search), S2 10 m pixel time series (Earth Search COGs plus rasterio windowed reads), CORINE class, WorldCover tiles, ERA5/ERA5-Land daily point series (Open-Meteo), and SoilGrids texture/SOC/pH. The free CDSE account is the one that unlocks the most valuable EU-specific layer: HRL Croplands crop types 2017-2024 (Q3).
- The SoilGrids REST service should be called once per field and cached to JSON. Do not call it live during the demo: it took about 35 s for Cartagena and is officially limited to 5 calls/min.
- CDSE S2 L2A assets are JP2 and about 100 MB per band per tile, so they are not COGs. For field time series, use Sentinel Hub Statistical API or openEO (server-side) or Earth Search COGs (client-side windowed reads) rather than downloading SAFE products.
- The 51 clear scenes (<20 % cloud) in 2025 at Cartagena come to about 1 per week. That is ample for an NDVI time series and bare-soil detection in this dry climate.

### Gaps
- Not tested (account required): Sentinel Hub Statistical API, openEO `aggregate_spatial`, CDS `retrieve`, CDSE downloads, WEkEO HDA, EGMS API. Their queue and latency figures below come from documentation or forums, not from measurement.
- rasterio/GDAL are not installed on this machine, so no actual COG pixel was read. Only `Accept-Ranges: bytes` was confirmed.
- Open-Meteo's terms of use, licence and rate limits were not checked in this session.
- The MR-VPP identify value "3" was not decoded (it may be a class or date code).

## Q2. Copernicus Data Space Ecosystem (Sentinel-2 L2A, Sentinel-1 GRD, Sentinel-3): access methods, quotas, what needs an account

### Takeaway
Catalogue search (STAC v1 and OData) is open. Every download and every processing API (Sentinel Hub Process/Statistical, openEO, S3) needs a free CDSE account and OIDC token. Free-tier quotas are 10 000 Sentinel Hub PU/month (300/min), 10 000 openEO credits/month (a "temporary boost"), and 4 concurrent S3/OData connections at 20 MB/s each. For a hackathon, the Sentinel Hub Statistical API or openEO `aggregate_spatial` per field polygon is the fastest authenticated path. Earth Search COGs are the fastest anonymous path. **Verdict: S2 L2A KEEP; S1 GRD OPTIONAL (server-side only); S3 DROP.**

### Cited Findings
**Quotas (Copernicus General users)**: Sentinel Hub 10 000 PU/month and 300 PU/min; 10 000 requests/month and 300 requests/min. openEO 10 000 credits/month, footnoted as a "Temporary Boost of monthly openEO Credits to 10 000", and 12 requests/min (1 per 5 s, sync and batch). S3: 2000 requests/min. S3/OData/STAC: 20 MB/s per connection and 4 concurrent connections. Monthly quotas reset on the 1st. — [CDSE Quotas](https://documentation.dataspace.copernicus.eu/Quotas.html)

**Auth model**: STAC assets declare `auth:schemes` `s3` and `oidc` (`openIdConnectUrl: https://identity.dataspace.copernicus.eu/auth/realms/CDSE/.well-known/openid-configuration`). HTTPS alternates (`zipper.dataspace.copernicus.eu`, `download.dataspace.copernicus.eu`) carry `auth:refs: ["oidc"]`. — [CDSE STAC item, live](https://stac.dataspace.copernicus.eu/v1/search). The token endpoint is `https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token`. — [CDSE OIDC config, live](https://identity.dataspace.copernicus.eu/auth/realms/CDSE/.well-known/openid-configuration)

**Sentinel-2 L2A**: in the CDSE collection `sentinel-2-l2a`. Assets include B02/B03/B04/B08 at 10 m, B05-B07/B8A/B11/B12 at 20 m, SCL at 20 m, and AOT. 2025 items over Murcia come from S2A, S2B and S2C, with processing baseline N0511. — [CDSE STAC, live](https://stac.dataspace.copernicus.eu/v1/search)

**Statistical API request shape** (from the docs): `input.bounds` + `input.data: [{type: "sentinel-2-l2a"}]` + `aggregation.timeRange` + `aggregation.aggregationInterval.of: "P10D"` (or `"P1D"`) + `evalscript`. `evaluatePixel` must return a `dataMask` output. If the time range is not divisible by the interval, the last partial interval is skipped. — [CDSE Statistical API docs](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Statistical.html). Endpoint `POST https://sh.dataspace.copernicus.eu/api/v1/statistics`, which answers 401 without a Bearer token. — [live test](https://sh.dataspace.copernicus.eu/api/v1/statistics). Ready-to-use body for one field (not executed, needs a token):
  ```json
  {"input":{"bounds":{"geometry":{"type":"Polygon","coordinates":[[[-0.972,37.718],[-0.968,37.718],[-0.968,37.722],[-0.972,37.722],[-0.972,37.718]]]},"properties":{"crs":"http://www.opengis.net/def/crs/OGC/1.3/CRS84"}},
   "data":[{"type":"sentinel-2-l2a","dataFilter":{"maxCloudCoverage":40}}]},
   "aggregation":{"timeRange":{"from":"2019-01-01T00:00:00Z","to":"2025-12-31T23:59:59Z"},"aggregationInterval":{"of":"P10D"},
   "evalscript":"//VERSION=3\nfunction setup(){return{input:[{bands:[\"B04\",\"B08\",\"SCL\",\"dataMask\"]}],output:[{id:\"ndvi\",bands:1},{id:\"dataMask\",bands:1}]}}\nfunction evaluatePixel(s){var ok=s.dataMask*([3,8,9,10].indexOf(s.SCL)<0?1:0);return{ndvi:[(s.B08-s.B04)/(s.B08+s.B04)],dataMask:[ok]}}"}}
  ```
  The token comes from OAuth client-credentials (client id/secret) against the token endpoint above. The client is created in the CDSE user dashboard; that step was not verified this session.

**openEO** (Python `openeo` client; not executed, needs login):
  ```python
  import openeo
  con = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()  # device-code login in browser
  s2 = con.load_collection("SENTINEL2_L2A", spatial_extent={"west":-0.98,"south":37.71,"east":-0.96,"north":37.73},
                           temporal_extent=["2019-01-01","2025-12-31"], bands=["B04","B08","SCL"], max_cloud_cover=40)
  ndvi = s2.ndvi(nir="B08", red="B04")
  ts = ndvi.aggregate_spatial(geometries=fields_geojson, reducer="mean")
  ts.download("ndvi_fields.json")   # sync, small AOIs; use execute_batch() for bigger jobs (queue)
  ```
  The backend is live at API 1.2.0, and collections `SENTINEL2_L2A`, `SENTINEL1_GRD` and `SENTINEL3_SLSTR_L2_LST` are listed. — [openEO CDSE, live](https://openeo.dataspace.copernicus.eu/openeo/1.2/collections)

**Sentinel-1 GRD**: catalogue entries over Cartagena in June 2025 are S1A IW GRDH 1SDV (dual-pol VV+VH) products, now distributed as `_COG.SAFE`, with sizes of 0.93-1.77 GB per product. S1C products appear in the same query, so S1C is operational. — [CDSE OData, live](https://catalogue.dataspace.copernicus.eu/odata/v1/Products). `sentinel-1-grd` and `sentinel-1-global-mosaics` exist in STAC. — [CDSE STAC collections, live](https://stac.dataspace.copernicus.eu/v1/collections?limit=500)

**Sentinel-3**: OLCI L2 land (LFR/LRR) and SLSTR LST (NRT/NTC) are in STAC. — [CDSE STAC collections, live](https://stac.dataspace.copernicus.eu/v1/collections?limit=500). The CLMS 300 m ETa product is itself derived from Sentinel-3 OLCI+SLSTR. — [CDSE STAC `clms_eta_global_300m_10daily_v1_cog` description, live](https://stac.dataspace.copernicus.eu/v1/collections?limit=500)

**Copernicus DEM** in STAC: `cop-dem-glo-30-dged-cog` (30 m COG), `cop-dem-glo-90-dged-cog`, and `cop-dem-eea-10-laea-tif` (10 m EEA). — [CDSE STAC collections, live](https://stac.dataspace.copernicus.eu/v1/collections?limit=500)

**Anonymous alternative for S2**: Element84 Earth Search `sentinel-2-c1-l2a`, with public COGs on AWS us-west-2 and HTTP range reads. It returned the same 51 scenes as CDSE for the point. — [Earth Search, live](https://earth-search.aws.element84.com/v1/search)

### Inferences
- S2 L2A is the single most important EO input for 0.5-10 ha Murcian fields. A 0.5 ha field (5 000 m²) holds about 50 S2 pixels at 10 m, versus about 5-6 pixels at 30 m (HLS/Landsat). Use the SCL band to mask cloud, shadow and cirrus (SCL 3, 8, 9, 10).
- A year of 10-day NDVI aggregates for a few dozen fields via the Statistical API should cost only a small fraction of 10 000 PU/month. The exact PU per statistical request was not found, so this is a gap.
- S1 GRD (VV/VH) can give a cloud-independent soil-wetness and crop-structure proxy. Downloading 1-2 GB products is incompatible with a 36 h hackathon, so use it only via openEO or Sentinel Hub (server-side `aggregate_spatial`), and only if time permits. → OPTIONAL.
- S3 (300 m-1 km) is far too coarse for these fields. Its derived CLMS products (ETa, LST) are easier to use than raw S3. → DROP raw S3.

### Gaps
- PU cost per Statistical API request (formula) was not retrieved. The "temporary boost" of openEO credits has no end date on the page, and the page shows no last-updated date.
- openEO sync-request timeouts and batch queue times on CDSE were not documented in the sources read. Expect seconds to minutes for small sync requests and minutes or more for batch jobs (an inference, not measured).
- The CDSE dashboard OAuth-client creation flow was not verified this session.

## Q3. Copernicus Land Monitoring Service: HRL Croplands (crop types / cropping patterns), HR-VPP, soil moisture, ET, CORINE, EGMS

### Takeaway
The standout finding is the new **CLMS HRL Croplands (VLCC)** suite on CDSE: 10 m yearly **Crop Types 2017-2024**, Main/Secondary crop emergence, harvest and duration, Bare-soil before/after, and **"Cropping Seasons Types over 3 Years"** (the number of distinct crops in a rolling 3-year window, which is effectively a rotation-diversity map). It was published on CDSE in July-August 2026 in about 2 MB COG tiles and is reachable via STAC (open search, download with a free CDSE account) or openEO. HR-VPP 10 m phenology (SOSD/EOSD/LENGTH/TPROD, 2017-2024) is on CDSE openEO (marked EXPERIMENTAL) and on WEkEO. **EGMS** gives InSAR subsidence that shows aquifer overexploitation in the Guadalentín. Its download needs authentication, and it migrates to CDSE between Q4 2026 and Q1 2027. **Verdicts: HRL Croplands KEEP (top priority); HR-VPP KEEP-if-openEO-works / else OPTIONAL; EGMS KEEP for the Guadalentín storyline (precompute); CORINE KEEP (instant context); SSM/SWI 1 km OPTIONAL; ETa 300 m OPTIONAL; MR-VPP DROP.**

### Cited Findings
**HRL Croplands / VLCC (Vegetated Land Cover Characteristics)**
- CDSE STAC collections include: `clms_vlcc_crop-types_europe_10m_yearly_v1` (+ confidence layer), `clms_vlcc_cropping-seasons_europe_10m_yearly_v1`, `clms_vlcc_cropping-seasons-types_europe_10m_yearly_v1`, `clms_vlcc_main-crop-emergence/harvest/duration_europe_10m_yearly_v1`, `clms_vlcc_secondary-crop-types/emergence/duration_europe_10m_yearly_v1`, `clms_vlcc_bare-soil-before/after_europe_10m_yearly_v1`, plus grassland and tree-cover layers. — [CDSE STAC collections, live](https://stac.dataspace.copernicus.eu/v1/collections?limit=500)
- The CTY description (verbatim from the STAC collection) says it maps "the specific crop type grown during the main growing season for all pixels identified as arable or permanent cropland". It covers "18 crop types grouped into arable crops (cereals, dry pulses & vegetables, root/tuber crops, non-permanent industrial crops) and permanent crops (grapes, olives, fruits, nuts)". It is annual from 2017 in 10 m rasters in 100×100 km tiles (EEA-38). Licence link: `https://land.copernicus.eu/en/data-policy`. — [CDSE STAC collection, live](https://stac.dataspace.copernicus.eu/v1/collections?limit=500)
- CPCST: "number of unique crop types grown in the main agricultural season over a rolling three-year period (values: 1–3)… derived from the crop diversity count based on CTY data from three consecutive years… Permanent crops are excluded". Items exist for P2017-2019 through P2022-2024 over Cartagena. — [CDSE STAC, live](https://stac.dataspace.copernicus.eu/v1/search)
- CPMCE (Main Crop Emergence) is in YYDOY format. — [CDSE STAC collection, live](https://stac.dataspace.copernicus.eu/v1/collections?limit=500)
- Items over Cartagena: tile E33N16, years 2017-2024, about 1.0-1.9 MB per COG, `created 2026-07-17`, `published 2026-08-03`, `SDIResourceIdentifier copernicus_r_3035_10_m_cty_p_2017-now_v01_r00`. — [CDSE STAC, live](https://stac.dataspace.copernicus.eu/v1/search)
- The same layers are exposed in openEO as `CLMS_VLCC_CROP_TYPES_EUROPE_10M_YEARLY_V1`, `CLMS_VLCC_CROPPING_SEASONS_TYPES_EUROPE_10M_YEARLY_V1`, `CLMS_VLCC_MAIN_CROP_EMERGENCE_...`, `CLMS_VLCC_BARE_SOIL_BEFORE/AFTER_...`, and others. — [openEO CDSE collections, live](https://openeo.dataspace.copernicus.eu/openeo/1.2/collections)
- The class count conflicts between sources: 17 classes per the Copernicus service catalogue, 19 classes for 2017-2023 per the EEA catalogue, and 18 per the CDSE STAC description. The legend is in the Product User Manual (v2.3, 2025-11-03, Table 7-1). — [CLMS product page](https://land.copernicus.eu/en/products/high-resolution-layer-croplands/crop-types-2017-raster-10-m-europe-yearly); [PUM Croplands 2017-present](https://land.copernicus.eu/en/technical-library/product-user-manual-croplands-2017-present/@@download/file); [EEA catalogue record (DOI 10.2909/9db29b07-5968-4ce0-8351-1e356b3d7d47)](https://sdi.eea.europa.eu/catalogue/srv/api/records/9db29b07-5968-4ce0-8351-1e356b3d7d47); [copernicus.eu catalogue](https://www.copernicus.eu/en/node/114115)

**HR-VPP (High-Resolution Vegetation Phenology and Productivity, Sentinel-2 based, 10 m)**
- openEO collection `COPERNICUS_VEGETATION_PHENOLOGY_PRODUCTIVITY_10M_SEASON1` (and `_SEASON2`): "[EXPERIMENTAL] … parameters at 10m on yearly basis from 2017 onwards for EU countries". Temporal extent is 2017-01-01 to 2024-12-31. Bands: SOSD, EOSD, MAXD, SOSV, EOSV, MINV, MAXV, AMPL, LENGTH, LSLOPE, RSLOPE, SPROD, TPROD, QFLAG. `COPERNICUS_PLANT_PHENOLOGY_INDEX` (PPI and QFLAG, 10 m, from 2017, EXPERIMENTAL). — [openEO collection metadata, live](https://openeo.dataspace.copernicus.eu/openeo/1.2/collections/COPERNICUS_VEGETATION_PHENOLOGY_PRODUCTIVITY_10M_SEASON1)
- The official access route is the WEkEO catalogue (HDA API, account required). — [HR-VPP data access manual](https://land.copernicus.eu/en/technical-library/hr-vpp-data-access-manual/@@download/file). A third-party `pyvpp` package downloads VPP_ST (seasonal trajectories/PPI) and VPP_Pheno (SOSD, EOSD...) from WEkEO, and reported "VPP_Index Dataset Currently Unavailable (January 2025)". — [pyvpp on PyPI](https://pypi.org/project/pyvpp/0.3.1/)
- HR-VPP is not listed among CDSE Sentinel Hub CLMS collections. That page lists only the 300 m/1 km bio-geophysical products (LSP 300 m, NDVI, LAI, FAPAR, DMP, GPP), SWI/SSM, and global land cover. — [CDSE Additional/Complementary data](https://documentation.dataspace.copernicus.eu/Data/ComplementaryData/Additional.html)
- MR-VPP (medium resolution, 2000-2019: Start/End/Length of season, Large integral productivity) is served as public ArcGIS ImageServers. — [EEA discomap MR_VPP, live](https://image.discomap.eea.europa.eu/arcgis/rest/services/MR_VPP?f=json)

**Soil moisture and ET (CLMS on CDSE, COG)**
- `clms_ssm_europe_1km_daily_v1_cog`: "relative water content of the top few centimeters soil… expressed in percent saturation", daily, 1 km, continental Europe, October 2014 to present. — [CDSE STAC collection, live](https://stac.dataspace.copernicus.eu/v1/collections?limit=500)
- SWI Europe 1 km daily: V1 (2015-2025) and V2 (2025-present). SWI global 12.5 km: V3/V4. Both are also in Sentinel Hub. — [CDSE Additional data](https://documentation.dataspace.copernicus.eu/Data/ComplementaryData/Additional.html)
- `clms_eta_global_300m_10daily_v1_cog`: actual ET, soil evaporation and canopy transpiration, 10-daily, 300 m, **from November 2025 to present** (Sentinel-3 OLCI+SLSTR). — [CDSE STAC collection, live](https://stac.dataspace.copernicus.eu/v1/collections?limit=500)

**CORINE Land Cover**: CLC 1990-2018 and change layers are public ArcGIS MapServers with identify. At the Cartagena point, CLC2018 = 212 "Permanently irrigated land". — [EEA discomap Corine, live](https://image.discomap.eea.europa.eu/arcgis/rest/services/Corine/CLC2018_WM/MapServer/identify). `clms_clcplus_lulucf-instance_europe_100m_yearly_v1` (CLCplus) is in CDSE STAC. — [CDSE STAC collections, live](https://stac.dataspace.copernicus.eu/v1/collections?limit=500)

**Other High Resolution Layers**: grassland 2015/2018, imperviousness 2006-2018, small woody features 2015/2018/2021 (5 m and 100 m density), tree cover density, water and wetness are public ImageServers under `GioLandPublic`. — [EEA discomap GioLandPublic, live](https://image.discomap.eea.europa.eu/arcgis/rest/services/GioLandPublic?f=json)

**EGMS (European Ground Motion Service)**
- Calibrated product: 5×20 m resolution, position accuracy under 10 m, EU27+IS+NO+UK, updated annually. The two latest releases can be explored and downloaded in the EGMS Explorer (https://egms.land.copernicus.eu/). Older releases (Baseline 2015-2021, 2022, 2023 updates) are only via the CLMS Service Desk. Programmatic download uses the notebook at https://github.com/copernicus-land/egms-api. "These datasets will be progressively migrated to CDSE between Q4 2026 and Q1 2027" and "CDSE will allow only the download of the data tiles". — [CLMS EGMS Calibrated](https://land.copernicus.eu/en/products/european-ground-motion-service/egms-calibrated)
- The latest release covers 2020-2024. The Explorer offers the 2019-2023 and 2020-2024 releases, and a machine-to-machine API was added. Ortho is a 100 m resampled grid from ascending+descending (periods 2018-2022, 2019-2023, 2020-2024). — [CLMS news: EGMS annual update](https://land.copernicus.eu/en/news/egms-annual-update-brings-new-data-improvements-to-egms-explorer); [EEA catalogue EGMS](https://sdi.eea.europa.eu/catalogue/srv/api/records/4137af9a-e3b6-405b-b714-e0cb5e9ca7d5)
- The EEA metadata lists the Explorer download as "requires authentication". — [EEA catalogue EGMS](https://sdi.eea.europa.eu/catalogue/srv/api/records/4137af9a-e3b6-405b-b714-e0cb5e9ca7d5)

### Inferences
- **HRL Croplands answers the challenge's "current rotation" requirement directly.** Stacking CTY 2017-2024 per field (zonal mode of 10 m pixels inside a SIGPAC parcel or a hand-drawn polygon) reconstructs the observed 8-year crop sequence. CPCST (1-3 distinct crops per 3 years) flags monoculture versus rotation. Bare-soil before/after flags fallow and bare periods, which matter for erosion and nitrate leaching to the Mar Menor. Main and secondary crop emergence/harvest give the double-cropping calendar typical of Campo de Cartagena horticulture. The whole Murcia region spans a few 100 km tiles (E33N16, E33N17, plus likely neighbours), at about 2 MB × 8 years × a few layers, so it is under 100 MB total. Download once with a CDSE token and cache.
- No NASA product gives annual 10 m crop types for Europe, so this is the strongest "partner data" differentiator. (USDA CDL is US-only; that is general knowledge and was not re-verified this session.)
- HR-VPP SOSD/EOSD/LENGTH give season timing per pixel without fitting the team's own phenology. The openEO version is flagged EXPERIMENTAL and ends in 2024, so the team needs a fallback: compute NDVI-based season dates from the S2 Statistical API.
- EGMS: the Guadalentín (Lorca-Totana-Alhama) subsidence is a compelling "groundwater stress" layer for rotation strategies that cut irrigation demand. Download the 2020-2024 Ortho tiles (100 m) for the valley before the event. Because of the planned CDSE migration in Q4 2026-Q1 2027, the Explorer/API workflow may change during the hackathon week, which is another reason to precompute.
- SSM 1 km and SWI 1 km are useful as regional drought context but are too coarse for per-field decisions. ETa 300 m starts only in November 2025, so it is useless for multi-year rotation analysis.

### Gaps
- HRL Croplands legend (exact class codes for CTY values) was not retrieved. Get Table 7-1 from the PUM before decoding pixels.
- It is not confirmed whether the 2024 CTY is final or whether 2025 will be added soon.
- The HR-VPP WEkEO dataset IDs and current WEkEO queue times were not verified.
- The EGMS API's exact authentication (EU Login / CLMS account / token) is not stated on the pages read.
- The EGMS file size for the Guadalentín tiles is unknown.
- Whether CLMS SSM 1 km is derived from Sentinel-1 is not stated in the STAC description.

## Q4. Copernicus Climate Data Store: ERA5-Land, ERA5-Land time-series, agroclimatic indicators, CMIP6, seasonal forecasts, E-OBS

### Takeaway
The new CDS uses a personal access token in `~/.cdsapirc` (`url: https://cds.climate.copernicus.eu/api`), `cdsapi>=0.7.7`, and manual acceptance of each dataset's Terms of Use on the dataset page. The fastest CDS product for a field is **`reanalysis-era5-land-timeseries`**: an ARCO store built for long single-point series, hourly 1950-present, 0.1°, CSV/NetCDF, CC-BY. It has no evaporation variable, so ET must come from full ERA5-Land (`total_evaporation`, `potential_evaporation`, queued) or from Open-Meteo's FAO ET0. **`sis-agroclimatic-indicators`** gives ready-made crop-relevant indicators for future climate (0.5°, RCP2.6-8.5, 5 GCMs, 30-year periods to 2099). Queue times for classic CDS requests range from minutes to hours and are unpredictable. **Verdicts: ERA5-Land time-series KEEP; Open-Meteo ERA5 proxy KEEP as no-account fallback; agroclimatic indicators KEEP (future-climate scoring); full ERA5-Land hourly OPTIONAL (only for ET partitions); E-OBS OPTIONAL; CMIP6 raw DROP; seasonal forecasts DROP; C3S satellite soil moisture DROP.**

### Cited Findings
- API setup: register and log in; copy the token into `$HOME/.cdsapirc` as `url: https://cds.climate.copernicus.eu/api` / `key: <PERSONAL-ACCESS-TOKEN>`; `pip install "cdsapi>=0.7.7"`. "One must agree to the Terms of Use of a dataset before downloading any data out of it", done manually at the bottom of the download form. The optional new package is `ecmwf-datastores-client`. The page states no queue limits. — [CDS How to API](https://cds.climate.copernicus.eu/how-to-api)
- ERA5-Land time-series: hourly, 1950 to present, 0.1° (about 9 km), updated daily. Formats NetCDF and CSV. Stored in an "Analysis-Ready, Cloud-Optimised (ARCO) format specifically designed for retrieving long time-series for individual points". The nearest grid point is selected automatically. CC-BY licence. — [CDS ERA5-Land time-series](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-timeseries?tab=overview)
- Its live process schema lists `variable` (2m temperature/dewpoint, skin temperature, soil temperature levels 1-4, **`volumetric_soil_water_level_1..4`**, total precipitation, surface solar/thermal radiation, wind, snow, surface pressure), `data_format` (csv/netcdf), and `area`. There is no evaporation variable. Note that the variable naming differs from the main dataset (`..._level_1` here, `..._layer_1` in `reanalysis-era5-land`). — [CDS process schema, live](https://cds.climate.copernicus.eu/api/retrieve/v1/processes/reanalysis-era5-land-timeseries)
- Request template (not executed). Sibling-dataset examples use `location` + `date` + `data_format`, and CDS recommends copying the exact request from the dataset's "Show API request code" button. — [ECMWF forum, single-levels-timeseries example](https://forum.ecmwf.int/t/issue-with-reanalysis-era5-single-levels-timeseries-dataset-access-via-cds-api/12880); [CDS How to API](https://cds.climate.copernicus.eu/how-to-api)
  ```python
  import cdsapi
  cdsapi.Client().retrieve("reanalysis-era5-land-timeseries", {
      "variable": ["2m_temperature", "total_precipitation", "volumetric_soil_water_level_1",
                   "volumetric_soil_water_level_2", "surface_solar_radiation_downwards"],
      "location": {"latitude": 37.72, "longitude": -0.97},
      "date": ["2000-01-01/2025-12-31"],
      "data_format": "csv"}, "cartagena_era5land_ts.zip")
  ```
- The full `reanalysis-era5-land` variables include `total_evaporation`, `potential_evaporation`, `evaporation_from_bare_soil`, `evaporation_from_vegetation_transpiration`, `evaporation_from_the_top_of_canopy`, `volumetric_soil_water_layer_1..4`, and `soil_type`. — [CDS process schema, live](https://cds.climate.copernicus.eu/api/retrieve/v1/processes/reanalysis-era5-land). `derived-era5-land-daily-statistics` offers daily mean/max/min of the ERA5-Land state variables (temperature, soil water) from 1-hourly data. — [CDS process schema, live](https://cds.climate.copernicus.eu/api/retrieve/v1/processes/derived-era5-land-daily-statistics)
- Agroclimatic indicators (`sis-agroclimatic-indicators`): 26 indicators, including biologically effective degree days, frost days, growing season length, heavy precipitation days, max consecutive dry days, summer days, tropical nights, warm spell duration and precipitation sum. 0.5° global, 1951-2099, input is daily bias-corrected data from 5 CMIP5 GCMs (ISIMIP Fast Track). NetCDF-4, v1.1, CC-BY, last updated 2026-05-12, "no updates expected". — [CDS agroclimatic indicators](https://cds.climate.copernicus.eu/datasets/sis-agroclimatic-indicators?tab=overview). Live schema: origins `noresm1_m_model`, `gfdl_esm2m_model`, `hadgem2_es_model`, `ipsl_cm5a_lr_model`, `miroc_esm_chem_model`, `era_interim_reanalysis`; experiments `rcp2_6`, `rcp4_5`, `rcp6_0`, `rcp8_5`, `historical`; `temporal_aggregation` `10_day`/`annual`/`season`; periods `195101_198012` … `207101_209912`. — [CDS process schema, live](https://cds.climate.copernicus.eu/api/retrieve/v1/processes/sis-agroclimatic-indicators)
- CMIP6 (`projections-cmip6`): daily/monthly, experiments `ssp1_1_9` … `ssp5_8_5`, many models (`cesm2`, `ec_earth3`, `cmcc_esm2`, `miroc6`...). — [CDS process schema, live](https://cds.climate.copernicus.eu/api/retrieve/v1/processes/projections-cmip6)
- Seasonal forecasts (`seasonal-original-single-levels`): centres `ecmwf`, `meteo_france`, `dwd`, `cmcc`, `ukmo`, `ncep`, `jma`, `eccc`, `bom`. — [CDS process schema, live](https://cds.climate.copernicus.eu/api/retrieve/v1/processes/seasonal-original-single-levels)
- E-OBS (`insitu-gridded-observations-europe`): grids `0_1deg`/`0_25deg`; versions up to `34_0e`; variables Tmax/Tmean/Tmin, precipitation, RH, shortwave radiation, wind, SLP. — [CDS process schema, live](https://cds.climate.copernicus.eu/api/retrieve/v1/processes/insitu-gridded-observations-europe)
- C3S satellite soil moisture (`satellite-soil-moisture`): versions up to `v202505_2`, with surface and root-zone volumetric soil moisture. — [CDS process schema, live](https://cds.climate.copernicus.eu/api/retrieve/v1/processes/satellite-soil-moisture)
- Queue anecdotes: a one-month ERA5 request "queued for 2h"; "for them ERA5-land download takes approximately 20 days"; requests "queued for 9+ hours" during incidents. ECMWF advises checking https://status.ecmwf.int/. ECMWF also closes queues before maintenance. — [ECMWF forum: queue >1 h](https://forum.ecmwf.int/t/queue-for-more-than-1-hr-when-downloading/12786); [ECMWF forum: extremely slow ERA5-Land](https://forum.ecmwf.int/t/extremely-slow-download-of-era5-land/6979); [ECMWF forum: ERA5-Land forever waiting](https://forum.ecmwf.int/t/era5-land-hourly-data-download-forever-waiting/5060); [ECMWF forum: queue closures](https://forum.ecmwf.int/t/brief-closure-of-queues-for-era5-daily-requests-from-tuesday-17-march-5pm-gmt-until-end-of-maintenance-system-session-on-wednesday-18-march/14787)
- No-account ERA5 proxy: Open-Meteo `archive-api` returned a full year of daily ERA5 data (precipitation, FAO ET0, Tmax) and ERA5-Land hourly soil moisture for Cartagena in 0.3-0.5 s. — [Open-Meteo archive API, live](https://archive-api.open-meteo.com/v1/archive)

### Inferences
- The recommended pipeline is to download ERA5-Land time-series CSVs (2000-2025) once for about 5-10 representative points, one per comarca (Campo de Cartagena, Vega del Segura, Altiplano, Noroeste, Guadalentín). If the CDS queue stalls, fall back to Open-Meteo (same ERA5 lineage, instant). For the submission, cite Copernicus C3S ERA5-Land as the data source and Open-Meteo as the access tool.
- For "future climate" rotation scoring, `sis-agroclimatic-indicators` (seasonal or 10-day, RCP4.5 vs RCP8.5, periods 2011-2040 and 2041-2070) is far lighter than raw CMIP6. It is CMIP5-based and frozen ("no updates expected"), which should be flagged as a limitation. At 0.5°, the whole region falls in about 4-6 cells.
- E-OBS (station-based, 0.1°) is a good cross-check for ERA5-Land precipitation in SE Spain, where reanalysis underestimates heavy (DANA) rainfall (Q8). It is optional.
- Seasonal forecasts (multi-model GRIB ensembles) and raw CMIP6 are not worth the time in 36 h.

### Gaps
- Actual queue time for `reanalysis-era5-land-timeseries` (ARCO) was not measured, because it needs an account. It is designed to be fast, but no official latency figure was found.
- The ERA5-Land latency behind real time is not stated on the dataset page (only "updated daily").
- The exact `location`/`date` keys for the land time-series request were not confirmed. The public schema only exposes `variable`, `data_format` and `area`.
- The names of the 5 GCMs are visible in the schema, but which indicator uses which aggregation was not verified.

## Q5. Copernicus Emergency Management Service: DANA flood maps for Murcia

### Takeaway
The September 2019 DANA was covered by Rapid Mapping activation **EMSR388 "Flood in the Southeast of Spain"**, activated 12 Sept 2019 by Spanish Civil Protection (CECOP/DGPCE). It includes a delineation of the Murcia surroundings (4,263 ha flooded on 16 Sept 2019) and the Vega Baja/Orihuela. It is useful as a flood-exposure overlay for Vega del Segura fields. **Verdict: OPTIONAL (one vector overlay; skip if time is short).**

### Cited Findings
- EMS Rapid Mapping was activated on 12 September by the Centro de Coordinación Operativa (CECOP) de la Dirección General de Protección Civil y Emergencias. A delineation map of the Murcia surroundings shows 4,263 ha (42.6 km²) flooded on 16 September 2019. The first delineation used COSMO-SkyMed and Sentinel-1B radar. Vega Baja (Orihuela) was among the hardest-hit areas, and the Murcia surroundings were a separate AoI (AoI02). — [Copernicus EMS news, 27 Sept 2019](https://mapping.emergency.copernicus.eu/news/copernicus-ems-monitors-impact-of-flood-in-the-southeast-of-spain/)
- A Spanish Civil Protection presentation describes "Evento de inundaciones por la DANA en Murcia (11-15/09/2019)" and the EMS activation. — [MITECO presentation](https://www.miteco.gob.es/es/agua/formacion/presentacion-18-jornada-implantacion-pgris-lecciones-aprendidas-inundaciones2019_regmurcia_tcm30-503800.pdf)
- A University of Alicante thesis analyses how land subsidence affects flooding risk using InSAR and modelling, which links the EGMS and flood storylines. — [RUA, Univ. Alicante](https://rua.ua.es/dspace/handle/10045/136774?locale=en)

### Inferences
- An EMSR388 flood polygon intersected with a field gives a binary "flooded in 2019 DANA" flag. That feeds a risk criterion, for example avoiding high-value winter horticulture on flood-prone Vega parcels. CORINE plus EMS together take under 30 minutes.

### Gaps
- The exact EMSR388 product download URL and format (shapefile/GeoJSON/KMZ), and whether a login is required, were not verified.
- Later Murcia-relevant activations (DANA 2023, 2024) were not identified. The 2024 Valencia DANA products cover Valencia, not Murcia.

## Q6. Soil: SoilGrids 2.0, ESDAC/JRC (LUCAS topsoil, K-factor, erosion), EU Soil Observatory

### Takeaway
SoilGrids 2.0 REST works without a key but is beta, slow (35 s for Cartagena) and fair-use-limited to 5 calls/min. Query once, cache, and use WCS/WebDAV for anything larger. ESDAC data (LUCAS 2018 topsoil, the K-factor 500 m map) needs a registration or request form, so turnaround is uncertain. **Verdicts: SoilGrids KEEP (cached); ESDAC K-factor OPTIONAL (only if the form gives an instant link); LUCAS 2018 topsoil OPTIONAL/DROP (registration delay, sparse points); EU Soil Observatory not researched.**

### Cited Findings
- REST fair use is "5 API calls per 1 minute period". The REST API v2.0 "is still under active development (beta stage)" with no uptime guarantee. ISRIC recommends WebDAV or web services (WCS) for anything more than one-off queries. One FAQ page said the REST service had been temporarily paused, which conflicts with the other pages. Live tests on 2026-11-13 show it working (Q1). — [ISRIC REST entry page](https://rest.isric.org/); [SoilGrids access FAQ](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_02.html); [SoilGrids FAQ](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_04.html)
- Conversion factors: soc /10 (dg/kg → g/kg), phh2o /10, bdod /100 (cg/cm³ → kg/dm³). Accuracy is "still limited", with "variation explained by the models… between 30% and 70%". Alternatives are WebDAV (VRT), WCS, R and GEE, with 1000 m and 5000 m aggregates as COG on WebDAV. — [SoilGrids FAQ 01](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_01.html)
- Live values (0-5 / 5-15 cm): Cartagena clay 31.4/34.6 %, sand 20.0/18.2 %, SOC 20.6/12.9 g/kg, pH 7.7/7.9. Jumilla clay 26.8/28.2 %, sand 31.8/30.6 %, SOC 22.2/13.2 g/kg, pH 7.8/8.0. — [SoilGrids REST, live](https://rest.isric.org/soilgrids/v2.0/properties/query)
- LUCAS 2018 topsoil: users must register through the "Request Form" tab. Bulk density data derived from LUCAS 2018 was added. — [ESDAC LUCAS 2018 topsoil](https://esdac.jrc.ec.europa.eu/node/80774); [ESDAC LUCAS 2018 Soil Module](https://esdac.jrc.ec.europa.eu/node/83705)
- K-factor (soil erodibility): a 500 m map derived from LUCAS 2009 and the European Soil Database. Downloads (K, Kst with stoniness, stoniness effect) are obtained by compiling an online form. — [ESDAC K-factor](https://esdac.jrc.ec.europa.eu/node/34376); [ESDAC soil erodibility theme](https://esdac.jrc.ec.europa.eu/themes/soil-erodibility-europe)
- LUCAS 2015/2018 points are also visible as public ArcGIS MapServers (`LUCAS/LUCAS_2015`, `LUCAS/LUCAS_2018`). — [EEA discomap LUCAS, live](https://image.discomap.eea.europa.eu/arcgis/rest/services/LUCAS?f=json)

### Inferences
- SoilGrids SOC of about 21 g/kg in the 0-5 cm layer looks high for semi-arid irrigated SE Spain. This is an inference, not verified against LUCAS. Treat SoilGrids SOC as relative or indicative, and use texture (clay/sand) and pH, which are more robust, for crop-suitability rules (salinity, drainage, AWC proxies).
- Rule-of-thumb usage: call SoilGrids at most 5 times a minute in a background script for each demo field, and store the JSON in the repo cache.
- The K-factor gives a defensible erosion-risk term for rotations with long bare-soil periods, which pairs well with the HRL bare-soil layers. It is only worth doing if the form gives an immediate download.

### Gaps
- The EU Soil Observatory (EUSO) dashboards and any 2026 LUCAS 2022 topsoil release were not researched.
- The ESDAC form turnaround time is unknown.
- SoilGrids AWC-related properties (e.g., `wv0033`, `wv1500`) were not tested.

## Q7. Crop type and rotation datasets: ESA WorldCereal, ESA WorldCover, EuroCrops, JRC crop-sequence maps, JRC MARS

### Takeaway
For Murcia, **HRL Croplands (Q3) beats all of these**: it is annual, 10 m, 2017-2024 and EU-specific. **WorldCereal** only has a 2021 global release (maize, winter/spring cereals, active cropland, active irrigation), with "more products… by the end of 2026", and it does not resolve Murcian horticulture. **EuroCrops v2.0** (ESSD 2026) has real parcel-level IACS declarations for all of Spain for 2021-2023 plus a multi-year "stack" table built for rotation analysis. However, the files are 5.5-11 GB national GeoParquets, too heavy unless remote spatial filtering works. **Verdicts: WorldCereal OPTIONAL (active irrigation 2021 only); WorldCover OPTIONAL (cropland mask); EuroCrops v2 OPTIONAL→DROP (size); LUCAS crop-sequence map DROP (too coarse); JRC MARS/Agri4Cast DROP (25 km, registration); EFFIS DROP (fire, not relevant).**

### Cited Findings
- WorldCereal: "Currently, our product collection contains data for 2021, but more products will be added by the end of 2026". 2021 products are temporary crops, maize, winter cereals, spring cereals, active cropland and active irrigation, all at 10 m. Access via Zenodo (https://zenodo.org/records/7875105), GEE (`ESA_WorldCereal_2021_MODELS_v100`), the viewer (https://vdm.esa-worldcereal.org/), and a custom-AOI download hub (https://hub.esa-worldcereal.org/). — [ESA WorldCereal global maps](https://esa-worldcereal.org/en/products/global-maps)
- WorldCereal uses openEO for processing and is available on Terrascope. The harmonized reference data repository was made available on 10 Oct 2025 (WUR). — [Terrascope WorldCereal](https://terrascope.be/en/cases/worldcereal-worldwide-seasonal-temporary-cropland-and-crop-type-mapping); [WUR reference datasets](https://research.wur.nl/en/datasets/worldcereal-harmonized-reference-datasets-extended-and-updated/); [CDSE WorldCereal and openEO](https://dataspace.copernicus.eu/node/2163)
- ESA WorldCover 10 m 2020 (v100) and 2021 (v200) tiles are discoverable on Planetary Computer without auth (tile N36W003 covers Cartagena) — [Planetary Computer STAC, live](https://planetarycomputer.microsoft.com/api/stac/v1/search) — and as openEO collections `ESA_WORLDCOVER_10M_2020_V1` and `ESA_WORLDCOVER_10M_2021_V2`. — [openEO CDSE, live](https://openeo.dataspace.copernicus.eu/openeo/1.2/collections)
- EuroCrops v2.0 (ESSD 18, 4075, 2026): harmonized parcel-level GSA/IACS declarations from 18 paying agencies, about 47 million parcels and 21 million ha, 2008-2023 where available (at least 3 consecutive years including 2021). Spain is included except overseas regions. Distributed as GeoParquet per country-year in EPSG:3035, with HCAT4 mappings to AGRIPROD/HRL/EAGLE. "Stack" tables link each parcel's crops across years and are illustrated with maize-monoculture maps. DOI 10.2905/b9fb9e67-78a9-4327-9d59-39a928d812d3. — [ESSD EuroCrops v2.0](https://essd.copernicus.org/articles/18/4075/2026/)
- The JRC FTP readme lists Spain (`es`) among the covered NUTS. The stack schema is `cropfield`, `cf<YEAR>`, `c<YEAR>` (original crop code), `area_ha`, `geom` (EPSG:3035). The `gpqtv202` folder holds a "correction of geometry bug on overlaped parcels. mostly affected spain". Live sizes: es_2021 9.37 GB, es_2023 11.3 GB, es_stack 5.5 GB. — [EuroCropsV2 FTP + readme, live](https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/DRLL/EuroCropsV2/)
- The older EuroCrops v9 (Zenodo, CC BY-SA 4.0) had only `ES_NA_2020.zip` (468 MB) for Spain. — [Zenodo EuroCrops v9](https://zenodo.org/records/8229128)
- First map of dominant crop sequence types in Europe 2012-2018: 8 types from LUCAS 2012/2015/2018 points, covering the EU including Spain. For Spain it overestimated corn and sunflower and underestimated cereals versus Eurostat. Data: https://doi.org/10.5281/zenodo.7016986. — [ESSD 15, 5651, 2023](https://essd.copernicus.org/articles/15/5651/2023/essd-15-5651-2023.html)
- JRC MARS Agri4Cast: daily meteorological data on a 25×25 km grid for Europe, CSV. Access needs "non-discriminatory registration". MARS Bulletins give monthly crop-condition and yield-forecast analyses for EU Member States. — [JRC Agri4Cast collection](https://data.jrc.ec.europa.eu/collection/agri4cast); [JRC gridded weather dataset](https://data.jrc.ec.europa.eu/dataset/jrc-marsop4-7-weather_obs_grid_2019); [EEA catalogue Agri4Cast](https://cis2.eea.europa.eu/data/404); [Agri4Cast portal](https://agri4cast.jrc.ec.europa.eu)

### Inferences
- WorldCereal's 2021 "active irrigation" layer could validate the irrigated/rainfed split (Campo de Cartagena irrigated vs Altiplano dryland cereals and vineyards). Its crop classes miss lettuce, broccoli, melon, artichoke and citrus, which dominate Murcia.
- EuroCrops v2 is the ground-truth way to know "what the farmer declared" (2021-2023). The only hackathon-feasible route would be DuckDB `httpfs` + `spatial` reading `es_2023.parquet` remotely with a bbox filter on Murcia. That is untested and could still pull GBs if the row groups are not spatially sorted. Spain's own SIGPAC/FEGA declarations, which another researcher covers, are likely lighter.
- The LUCAS crop-sequence map, MARS 25 km grid and EFFIS add nothing at field scale.

### Gaps
- Whether a new WorldCereal release (2024-2026) appeared by November 2026 was not confirmed.
- No remote-read test of EuroCrops v2 Spain was done (file too large for the 50 MB limit).
- The EuroCrops licence for v2 data is not stated on the ESSD page.
- The EU Soil Observatory and any JRC "crop rotation indicator" dataset from IACS beyond EuroCrops v2 were not found.

## Q8. Fastest path per dataset, account/licence/queue matrix, and what is unique versus NASA

### Takeaway
A demo-ready EU data stack fits in about 3-4 hours of fetching. Create one free CDSE account (HRL Croplands, Statistical API/openEO) and one CDS account (ERA5-Land time-series, agroclimatic indicators; accept each licence). Everything else is anonymous. The unique EU contributions versus NASA are 10 m annual crop types 2017-2024 (HRL Croplands), 10 m S2 time series for 0.5-10 ha fields, HR-VPP season dates and bare-soil layers, EGMS subsidence over the overexploited Guadalentín aquifer, and EMS DANA flood polygons.

### Cited Findings
| Dataset | Fastest point/field path | Account / licence | Queue / speed (evidence) | Verdict |
|---|---|---|---|---|
| S2 L2A 10 m | Anonymous: Earth Search STAC + COG windowed reads. Authenticated: Sentinel Hub Statistical API per polygon (P10D NDVI) or openEO `aggregate_spatial` | CDSE free account for SH/openEO/downloads; none for Earth Search | STAC search 1.6-6.5 s, 51 scenes 2025 (<20 % cloud) — [CDSE STAC](https://stac.dataspace.copernicus.eu/v1/search), [Earth Search](https://earth-search.aws.element84.com/v1/search) | **KEEP** |
| S1 GRD | openEO/SH server-side only | CDSE account | products 0.9-1.8 GB — [OData](https://catalogue.dataspace.copernicus.eu/odata/v1/Products) | OPTIONAL |
| S3 OLCI/SLSTR | not needed | CDSE | — | DROP |
| HRL Croplands CTY/CPCST/emergence/bare-soil 10 m 2017-2024 | STAC search (anon), then download about 2 MB COG tiles with token, or openEO | CDSE account; CLMS data policy | 0.56 s search, about 2 MB/tile-year — [CDSE STAC](https://stac.dataspace.copernicus.eu/v1/search) | **KEEP (top)** |
| HR-VPP 10 m (SOSD/EOSD/LENGTH/TPROD) 2017-2024 | openEO `COPERNICUS_VEGETATION_PHENOLOGY_PRODUCTIVITY_10M_SEASON1` (EXPERIMENTAL); WEkEO HDA | CDSE or WEkEO account | not measured — [openEO metadata](https://openeo.dataspace.copernicus.eu/openeo/1.2/collections/COPERNICUS_VEGETATION_PHENOLOGY_PRODUCTIVITY_10M_SEASON1) | KEEP if it works, else OPTIONAL |
| CLMS SSM/SWI 1 km, ETa 300 m | CDSE STAC COGs | CDSE account for download | — [CDSE STAC collections](https://stac.dataspace.copernicus.eu/v1/collections?limit=500) | OPTIONAL |
| CORINE 2018 | ArcGIS identify | none | 0.28-0.44 s — [EEA discomap](https://image.discomap.eea.europa.eu/arcgis/rest/services/Corine/CLC2018_WM/MapServer/identify) | KEEP (context) |
| EGMS Ortho/Calibrated | EGMS Explorer / egms-api notebook (precompute Guadalentín tiles) | authentication required; migrating to CDSE Q4 2026-Q1 2027 | not measured — [CLMS EGMS](https://land.copernicus.eu/en/products/european-ground-motion-service/egms-calibrated) | KEEP (Guadalentín story) |
| EMS EMSR388 | activation page products | not verified | — [EMS news](https://mapping.emergency.copernicus.eu/news/copernicus-ems-monitors-impact-of-flood-in-the-southeast-of-spain/) | OPTIONAL |
| ERA5-Land time-series | `cdsapi` `reanalysis-era5-land-timeseries` CSV | CDS account + accept licence (CC-BY) | ARCO, designed for points; general CDS queues 2 h to 9+ h reported — [CDS](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-timeseries?tab=overview), [forum](https://forum.ecmwf.int/t/queue-for-more-than-1-hr-when-downloading/12786) | **KEEP** |
| ERA5/ERA5-Land via Open-Meteo | `archive-api.open-meteo.com` | none | 0.3-0.5 s — [Open-Meteo](https://archive-api.open-meteo.com/v1/archive) | **KEEP (fallback)** |
| Agroclimatic indicators (CMIP5, 0.5°) | `cdsapi` `sis-agroclimatic-indicators` | CDS account + licence (CC-BY) | not measured — [CDS](https://cds.climate.copernicus.eu/datasets/sis-agroclimatic-indicators?tab=overview) | KEEP |
| E-OBS 0.1° | `cdsapi` `insitu-gridded-observations-europe` | CDS account | not measured — [CDS schema](https://cds.climate.copernicus.eu/api/retrieve/v1/processes/insitu-gridded-observations-europe) | OPTIONAL |
| CMIP6 raw / seasonal forecasts / C3S SM | `cdsapi` | CDS account | heavy | DROP |
| SoilGrids 2.0 | REST `properties/query` (cache) | none; 5 calls/min | 4.7-37 s; timeouts seen — [ISRIC](https://rest.isric.org/) | **KEEP (cached)** |
| ESDAC K-factor / LUCAS 2018 | forms | registration | unknown — [ESDAC](https://esdac.jrc.ec.europa.eu/node/34376) | OPTIONAL / DROP |
| WorldCereal 2021 | GEE / Zenodo / hub | none for Zenodo | — [WorldCereal](https://esa-worldcereal.org/en/products/global-maps) | OPTIONAL |
| WorldCover 2020/2021 | Planetary Computer STAC / openEO | none for search | 0.25 s — [PC STAC](https://planetarycomputer.microsoft.com/api/stac/v1/search) | OPTIONAL |
| EuroCrops v2 (ES 2021-2023) | JRC FTP GeoParquet | none | 5.5-11.3 GB files — [JRC FTP](https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/DRLL/EuroCropsV2/) | OPTIONAL→DROP |
| LUCAS crop-sequence map, MARS Agri4Cast, EFFIS, MR-VPP | — | — | — | DROP |

### Inferences
- **Unique versus NASA:** (1) HRL Croplands gives an observed multi-year crop history at 10 m. NASA has no European crop-type map. (2) S2 at 10 m with a 5-day revisit (A/B/C) resolves 0.5 ha plots that HLS at 30 m blurs. (3) HR-VPP and HRL bare-soil layers give season start/end and bare-soil periods directly, which matter for erosion and nitrate-leaching scoring in the Mar Menor catchment. (4) EGMS provides operational, Europe-wide InSAR displacement for the Guadalentín. NASA OPERA displacement products target North America (general knowledge, not re-verified). (5) ERA5-Land at 0.1° is finer than NASA POWER/MERRA-2 at about 0.5°, and CDS offers bias-corrected agroclimatic indicators.
- A suggested demo layering: NASA (SMAP soil moisture, HLS/Landsat, POWER or IMERG) for the "NASA data" requirement; S2 + HRL Croplands for the field-level rotation history; ERA5-Land + agroclimatic indicators for the climate and water balance; SoilGrids for soil; EGMS for the Guadalentín groundwater-stress narrative.

### Gaps
- The revisit and resolution claims for S2/HLS rest on general knowledge plus the observed scene counts, and were not re-cited from official mission pages this session.
- Exact PU and credit costs for the recommended requests are unknown.
- CDSE and CDS account approval time was not measured. Both are normally self-service email verification (unverified).

## Q9. Studies using these datasets over Murcia / Segura basin / SE Spain

### Takeaway
There is solid evidence on ERA5/ERA5-Land precipitation over Spain: reasonable correlation, but it underestimates heavy and violent events, which matters for DANAs. Alto Guadalentín is documented as Europe's fastest groundwater-driven subsidence (>10 cm/yr historically, up to about 2.5 m cumulative 1992-2012), and an EGMS study of Lorca-Totana reports up to -44.4 mm/yr. Sentinel-2 irrigated-crop classification in semi-arid SE Spain is mature, but there are few peer-reviewed Campo de Cartagena-specific crop-type papers. Most work there focuses on the Mar Menor and nitrate pressures.

### Cited Findings
- ERA5 and ERA5-Land precipitation over Spain 1951-2020 (Gomis-Cebolla et al., 2023, *Atmospheric Research*): Spearman correlation mostly 0.5-0.9, RMSE mostly 2-8 mm/day. Light and moderate precipitation is overestimated and heavy or violent events underestimated, and complex orography also degrades performance. — [RiuNet UPV](https://riunet.upv.es/entities/publication/fd0cf74c-eb90-4301-a67e-4236ad4a811c/full)
- Alto Guadalentín: InSAR reports "the highest rates of groundwater-related land subsidence recorded in Europe (> 10 cm/yr)". A 1992-2012 DInSAR study found up to 2.50 m cumulative displacement, linked to a 100-200 m groundwater-level drop since the 1970s. Sentinel-1 + COSMO-SkyMed decomposition shows up to 1.5 cm/yr of horizontal motion toward the basin centre. These come from search-result summaries of the following sources and were not full-text verified. — [PIAHS 372, 45 (2015)](https://piahs.copernicus.org/articles/372/45/2015/piahs-372-45-2015-relations.html); [UPM CCS](https://www.ccs.upm.es/?p=2528); [core.ac.uk](https://core.ac.uk/download/237484366.pdf)
- EGMS-based analysis of the Lorca-Totana region: mean vertical velocities up to -44.4 mm/yr, corroborated by groundwater records (conference abstract). — [Sciforum ECRS-6](https://sciforum.net/paper/34576)
- 22 nonparametric classifiers on Landsat-8 + Sentinel-2A for irrigated crops in a semi-arid region of SE Spain, using more than 2000 field plots and 12 crops. Nearest-neighbour and SVM gave the best robustness and efficiency. The exact study area (Murcia versus neighbouring Albacete) was not confirmed. — [Remote Sensing 12(11):1735 (2020)](https://mdpi.com/2072-4292/12/11/1735/htm)
- CNN on Sentinel-2 time series for agricultural land-use classification: the ternary model detected irrigated fields with 97 % global accuracy. Study region not confirmed. — [Remote Sensing 14(21):5373 (2022), DOAJ](https://doaj.org/article/816625afc40d46c2998673ea4e2589c5)
- Mar Menor catchment: a UPM undergraduate thesis mapped illegally irrigated surfaces for 2019-2022 using Sentinel-2 NDVI/NDMI, SIGPAC parcels and SIOSE. It is a student thesis, so treat it as preliminary. — [UPM TFG Celdrán](https://blogs.upm.es/dynamicland/wp-content/uploads/sites/294/2024/05/TFG_DiegoCeldran.pdf). A Sentinel-2/Landsat-8 water-quality early-warning study for the Mar Menor describes Campo de Cartagena as one of Europe's most intensive agricultural areas, with nutrient runoff via the Albujón. — [CSIC Digital](https://digital.csic.es/bitstream/10261/285584/1/Sentinel-2_Landsat-8_Satellites.pdf)

### Inferences
- In the pitch, cite the ERA5-Land precipitation bias (it underestimates DANA extremes) to justify E-OBS or local AEMET/SIAM station checks, and to present rainfall-driven metrics as indicative.
- The Guadalentín subsidence literature plus EGMS 2020-2024 is a strong, locally grounded motivation for a "water-saving rotation" strategy (for example, swapping summer horticulture for rainfed cereal/legume or fallow in the Guadalentín). That ties farmer priorities to aquifer sustainability.

### Gaps
- No peer-reviewed validation of ERA5-Land soil moisture specifically in the Segura basin was found.
- No peer-reviewed HRL Croplands or HR-VPP accuracy assessment for Murcia was found.
- No published EGMS velocity specifically for the Alto Guadalentín basin was found (only Lorca-Totana and pre-EGMS InSAR).
- A peer-reviewed Sentinel-2 crop-type map specific to Campo de Cartagena was not found in the searches run.
