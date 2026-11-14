# Prior art and realistic stack for a Field Shift crop-recommendation app (Campo de Cartagena, 30 h, 4 CS students)

Research date: 2026-11-14 (event day 1; most 2026 repos below are still being pushed to). The official challenge page could NOT be fetched from this environment (TLS / fetch failures), but the repo's own verbatim transcription (captured 2026-11-10) was read afterwards and is now the authority: `/home/enrikkk/Desktop/Computer Science/Hackathons/NasaSpaceApps/context/challenges/06-adapting-farms-with-nasa-data.md` (canonical URL there: https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/ — so Ichya20's slug is right and Zul-Qarnain's `field-shift-...` slug is wrong/unverified).

## 0. Verified challenge brief (from the repo transcription) — read before anything else
- Goal: a decision-support tool using NASA Earth observations plus local soil info, crop characteristics and farmer priorities "to help farmers explore rotation strategies that could strengthen soil health and adapt their farms to changing conditions". The brief itself says to "compare at least three rotation strategies, including the existing rotation", and for each explain why suggested, supporting evidence, benefits, information gaps and risks needing local review. — [local transcription](file:///home/enrikkk/Desktop/Computer%20Science/Hackathons/NasaSpaceApps/context/challenges/06-adapting-farms-with-nasa-data.md)
- Named datasets: SMAP, ECOSTRESS, GPM, Landsat, MODIS, NASA POWER, GRACE/GRACE-FO, SRTM/NASA elevation (HLS is not named but is Landsat+Sentinel-2 harmonised). Farmer priorities named: water use, forage value, nitrogen fixation, erosion reduction, organic matter, market suitability, supplemental income. It also asks for bare-field periods, crop-vulnerability seasons, uncertainty explanation, scenario sliders, farmer-input constraints, and a "supports, not replaces, local expertise" message. — same file
- IMPLICATION: market prices / profitability are only a "may consider" (market suitability, supplemental income). The brief is rotation + soil health + resilience first. A profit-ranked crop recommender that ignores soil-health/rotation sequencing would be off-centre; profit should be one axis among soil health, water, and resilience.
- The "Resources" tab was marked NOT LOADED in the transcription (published 13 Nov), so extra official data links may exist that were not seen.

## 1. What did the 2026 Field Shift repos build (the bar, and how to differentiate)?

### Takeaway
Roughly 40+ public repos already exist for Field Shift 2026, mostly "NASA POWER + rule-based rotation scoring + explainable UI", with one or two well-engineered outliers (Zul-Qarnain, Ichya20). Almost all frame the task as crop ROTATION comparison for soil health, water and climate resilience; the ones I read use no HLS NDVI pipeline and no market-price/profit module beyond demo coefficients, which is the clearest gap your plan (parcel-level HLS + prices + farmer constraints + uncertainty) can fill.

### Cited Findings
**Challenge framing (second-hand).**
- Zul-Qarnain's README maps the challenge requirements as: NASA Earth observations; local soil information; crop characteristics; farmer priorities; explore rotation strategies; soil health; water conservation; resilience to changing conditions; accessible to farmers. So the brief is about rotation strategies, not only single-crop recommendation. — [Zul-Qarnain/field-shift README](https://github.com/Zul-Qarnain/field-shift)
- Ichya20 states the question as "What should I consider if I change the crop rotation at this location?" and compares the current rotation plus two alternatives. — [Ichya20/FieldShift](https://github.com/Ichya20/FieldShift)
- The two repos link different challenge slugs; the repo's own verbatim capture uses `adapting-farms-with-nasa-data` (Ichya20's), so Zul-Qarnain's link looks wrong. — [Zul-Qarnain](https://github.com/Zul-Qarnain/field-shift); [Ichya20](https://github.com/Ichya20/FieldShift)
- Space Apps judging uses five criteria: Impact, Creativity, Validity, Relevance, Presentation; local panels pick projects for global judging; about 40 subject-matter experts review global-track projects; projects must answer an official challenge. — [Space Apps Judging & Awards Guide](https://www.spaceappschallenge.org/resources/judging-awards-guide) and [Project submission guide](https://www.spaceappschallenge.org/resources/project-submission-guide/) (as summarised by search result, not fetched in full)

**Zul-Qarnain/field-shift (Team Orion, Bangladesh) — the strongest one found.**
- Stack: Next.js 16 + TypeScript front end, Python build step, no server at runtime; committed JSON "packs" for 6 farms + 64 districts; rotation engine in `web/lib/engine.ts` runs in the browser; live NASA POWER call only for a "this season so far" card, with an outage banner and saved fallback. LightGBM used for an offline monsoon-onset forecast. PWA + Android APK. Bangla/English UI. — [README](https://github.com/Zul-Qarnain/field-shift)
- Data: NASA POWER daily 1981-2026 (70 locations), GPM IMERG V07 cross-check, MERRA-2 SST (Nino 3.4/DMI), SMAP L4, MODIS MOD13Q1, GRACE; local SRDI salinity map and FAO-29 salt tolerance; geoBoundaries; GIBS basemap. — [README](https://github.com/Zul-Qarnain/field-shift)
- Method: enumerates all legal Aman-Rabi-pre-monsoon crop sequences from a 12-crop pool, hard constraints then 8 weighted components, penalties (same-family carryover etc.), confidence level (high/medium/low from data quality), four priority sliders, what-if scenarios (rain -10/-20 %, +1/+2 C, onset +7/+15 days), "See why" drawer showing the arithmetic, SMS-length advice. — [README](https://github.com/Zul-Qarnain/field-shift); [engine.ts](https://github.com/Zul-Qarnain/field-shift/blob/main/web/lib/engine.ts)
- Honest limitation in code: scoring coefficients are labelled "ESTIMATE ... demo coefficient ... not calibrated against a crop register or an irrigation survey". — [engine.ts](https://github.com/Zul-Qarnain/field-shift/blob/main/web/lib/engine.ts)
- Self-scored against judging criteria in the README (a "Scorecard" section mapping each of the five criteria + teamwork + UX), ~266 pytest / 700 Vitest / 12 Playwright tests, full AI-use disclosure doc. This is the polish bar for README/presentation. — [README](https://github.com/Zul-Qarnain/field-shift)

**Ichya20/FieldShift (Indonesia, Klaten).**
- FastAPI + React 19/TypeScript/Vite + Leaflet + three.js diorama. Data: NASA POWER, MODIS NDVI/EVI via ORNL DAAC web service (QA-filtered), SoilGrids (mean/Q05/Q95), Copernicus DEM, ESA WorldCover, FAO GAEZ v5, FAO-56. Data package with SHA-256 manifests verified at startup. 12 agronomic/calendar checks per strategy, three strategies compared on a shared calendar. — [README](https://github.com/Ichya20/FieldShift)
- Deliberate guardrails: returns NO ranking, score, yield, profit or water-saving figure (nulls) because "the method is not calibrated"; blank inputs recorded as "don't know", never zero; no silent nearest-neighbour fallback; flag `local_agronomic_validation: false`. — [README](https://github.com/Ichya20/FieldShift)

**Stalker-a/field-shift-kz (Team DDT, Almaty).**
- Streamlit + Plotly, Python 3.11, live demo on Streamlit Cloud. Four tabs: climate shift (2006-2025 vs 1981-2000), crop fit for 16 crops now vs 2035 with limiting factor (temperature / water / season length / salinity), three 4-year rotations scored on soil health, water saving, income, climate resilience, data & method tab with CSV download. NASA POWER only (T2M, PRECTOTCORR, GWETROOT), ET0 via Hargreaves. Parameters admitted to be "approximate prototype values". — [README](https://github.com/Stalker-a/field-shift-kz)
- Crop suitability = product of per-factor fits (temperature, water, season, salinity); min suitability 0.4; rotation search over top-10 crops plus fallow with hard/soft agronomic rules. Has an agronomic-parameter audit file (SOURCES.md, in Russian). — [rotation.py](https://github.com/Stalker-a/field-shift-kz/blob/main/fieldshift/rotation.py); [SOURCES.md](https://github.com/Stalker-a/field-shift-kz/blob/main/SOURCES.md)

**ada-th25 and MaksimDar.**
- ada-th25 has two repos (`field-shift`, `nasa-field-shift-crop-rotation`) whose READMEs contain only a planned structure: FastAPI backend with `engine/` (scoring, constraints, ranking), POWER/SMAP/SoilGrids clients, `crops.json` agronomic matrix, per-demo-farm cached API responses, an API contract doc. Early-stage on 2026-11-14. — [ada-th25/field-shift](https://github.com/ada-th25/field-shift); [ada-th25/nasa-field-shift-crop-rotation](https://github.com/ada-th25/nasa-field-shift-crop-rotation)
- MaksimDar/field-shift-crop-rotation-advisor ("Multi-source decision-support tool for comparing crop rotation strategies") contains only README, LICENSE, .gitignore (created 2026-11-13). Nothing to learn yet. — [MaksimDar/field-shift-crop-rotation-advisor](https://github.com/MaksimDar/field-shift-crop-rotation-advisor)

**Other 2026 repos found (README-level only).**
- sagar25446-prog/FieldShift-NASA: Streamlit + interactive globe, NASA POWER, optional SoilGrids/MODIS; rule-based rotations ONLY for four pilot regions including Andalusia and US Corn Belt; explicitly no yield/profit prediction. — [repo](https://github.com/sagar25446-prog/FieldShift-NASA)
- AbelAnil/FieldShift-AI (solo, Kerala): FastAPI + Next.js 16 + MapLibre polygon drawing; GPM IMERG, POWER, SMAP L4, Landsat/Sentinel NDVI/NDMI, SoilGrids, NASADEM TWI; 18 crops, 5-factor suitability, 3-strategy rotation planner, what-if stress simulator, multilingual LLM assistant with STT/TTS, carbon-credit module (scope-creep example). — [repo](https://github.com/AbelAnil/FieldShift-AI)
- AHMED-TECH-01/FieldShift: crop DB, farmer priorities (income, soil health, water, resilience, risk), rotation engine; POWER, GPM, SMAP. — [repo](https://github.com/AHMED-TECH-01/FieldShift)
- Others by description only: Wingman-Clutch/field-shift-banyumas (offline PWA) [link](https://github.com/Wingman-Clutch/field-shift-banyumas); lucoslabs-cloud/tanamtenang-spaceapps (zero-install, scored in browser) [link](https://github.com/lucoslabs-cloud/tanamtenang-spaceapps); Satyam6300/FarmVerseAI (Kalaburagi digital twin) [link](https://github.com/Satyam6300/FarmVerseAI); haryana2x4/field-shift-nasa (Flask) [link](https://github.com/haryana2x4/field-shift-nasa); impugowda17/Field-Shift-Advisor- [link](https://github.com/impugowda17/Field-Shift-Advisor-).
- Chitransh007-ww repo is named "...Challenge-Winner" but was created 2026-11-10, before the event; the name is self-assigned and meaningless. — [repo](https://github.com/Chitransh007-ww/FieldShift-Kisan-Mitra-NASA-Space-Apps-Challenge-Winner)
- GitHub search `gh search repos "field shift" --created ">2026-08-01"` returned 25+ repos named FieldShift; a second search on "Field Shift: Adapting Farms with NASA Data" returned another ~18 (Brazil, Egypt, Indonesia, Turkey, Ukraine etc.). Many are empty stubs.

### Inferences
- The field is crowded in "POWER + rules + explainable bars". Differentiators that I did not see in any README read: (a) parcel-level HLS NDVI time series used as evidence (e.g. observed crop calendar, bare-field windows); (b) explicit market-price / profitability layer with price uncertainty; (c) Mediterranean horticulture (multi-cycle leafy vegetables, not cereal/rice) - Spain-based entries seen only cover Andalusia as a rule region in sagar25446; (d) conformal/interval uncertainty rather than ordinal "confidence: high/medium/low".
- The brief seems to reward rotation (sequence) reasoning: your "compare >=3 rotations" requirement already matches; make sure the rotation framing (soil health, legume/brassica breaks, water, resilience) is visible alongside profit, otherwise judges comparing to Zul-Qarnain may see a single-axis tool.
- Honest-limitations behaviour (Ichya20 nulls, Zul-Qarnain "ESTIMATE" comments, Stalker "approximate prototype values") is the norm among the strongest entries; shipping an uncalibrated profit number without caveats would look weaker than these.
- Judging rubric copy: Zul-Qarnain explicitly mirrors the five criteria in the README; cheap to imitate in structure (not text).

### Gaps
- Official challenge text is now covered by section 0 (local transcription); the live "Resources" tab (published 13 Nov) was not seen by anyone and needs a human read.
- I did not read engine code for all 40+ repos; "none uses HLS / market prices" is verified only for the repos listed above, not exhaustively. AbelAnil mentions Landsat/Sentinel NDVI but I did not check how.
- Ichya20's README is cut off in my read after the API/verification section; I did not read the method spec.

## 2. Production / academic decision-support systems: modules and how they present recommendations and uncertainty

### Takeaway
Commercial platforms (OneSoil, EOSDA, FieldView/Azure Data Manager) are monitoring + zoning + weather tools, not crop-choice optimisers; public advisory systems (FAO CROPWAT, SIAM Murcia, FaST) are irrigation/nutrient calculators built on FAO-56-style water balances. None of those I looked at presents crop-choice uncertainty prominently, so uncertainty display is a differentiator.

### Cited Findings
- FAO CROPWAT 8.0 (Windows): computes reference ET, crop water requirements and irrigation requirements from climate, soil and crop data; builds irrigation schedules from a daily soil-water balance with user-defined supply/management options; includes paddy rice; based on FAO Irrigation & Drainage Papers 56 and 33; climate station data from CLIMWAT (5,000+ stations). — [FAO CROPWAT](https://www.fao.org/land-water/databases-and-software/cropwat); [OpenEI summary](https://openei.org/wiki/CROPWAT_8.0)
- AquaCrop-OSPy (`pip install aquacrop`, latest listed 3.1.0): open-source Python version of AquaCrop-OS, University of Manchester; mirrors most of FAO AquaCrop 7.1 except salinity and fertility stress, weeds, perennial herbaceous crops; NOT an official FAO implementation. — [PyPI](https://pypi.org/project/aquacrop/); [docs](https://aquacropos.github.io/aquacrop)
- PCSE / WOFOST: pure-Python crop simulation framework, release 6.0 (Nov 2025), WOFOST implementations for potential/water-limited production; docs at pcse.readthedocs.io. — [PCSE docs](https://pcse.readthedocs.io/en/stable/); [PyPI](https://pypi.org/project/pcse/)
- Azure Data Manager for Agriculture: data platform (hierarchy model, satellite, weather-forecast and sensor ingestion), in preview for approved customers as of 2023 sources; Bayer builds crop-health/growth tracking, yield-potential and field-level 40-year historical weather on it, and FieldView uses its satellite and weather pipelines for yield-limiting-factor insight. — [Microsoft Learn overview](https://learn.microsoft.com/bg-bg/azure/data-manager-for-agri/overview-azure-data-manager-for-agriculture); [Bayer](https://www.bayer.com/de/node/39006)
- EOSDA Crop Monitoring: NDVI/NDRE/ReCl/MSAVI indices, NDVI-based productivity zoning into 2-7 zones with VRA export, historical weather, 14-day forecast, weather risk alerts, 5-year weather archive (vendor claims). — [EOSDA zoning](https://eos.com/products/crop-monitoring/key-functions/zoning/); [EOSDA key functions](https://eos.com/eos-crop-monitoring/key-functions)
- OneSoil: multi-season productivity zones, NDVI-based VRA maps, 7-day weather on a field status tab, AI agronomist ranking fields by urgency (third-party description). — [OneSoil changelog](https://updates.onesoil.ai); [agtecher review](https://agtecher.com/software/onesoil)
- EU FaST (Farm Sustainability Tool for nutrients): CAP regulation (EU) 2021/2115 Art. 15.4(b) requires member states to make a FaST-type platform available to farmers by 2024; features: Copernicus Sentinel RGB+NDVI, campaign management with farmer data import, fertilisation recommendations; free to farmers, paying agencies, advisors; pilot regions included Andalucia and Castilla y Leon in Spain. — [DESIRA news](https://desira2020.agr.unipi.it/2021/05/18/news-farm-sustainability-tool-fast-released/); [FAO Agritech Observatory](https://agritechobservatory.review.fao.org/en/farm-sustainability-tool-for-nutrients-fast); [EC FaST Navigator study](https://agriculture.ec.europa.eu/media/news/fast-navigator-study-identifies-models-necessary-to-provide-accurate-advice-on-the-use-of-fertilisers-to-eu-farmers-2022-05-25_en)
- Murcia SIAM (IMIDA): public free irrigation and fertilisation programmes for citrus, fruit trees and vegetables from agrometeorological data and field-derived crop coefficients; station network reported at 55 stations (2025 article), 50 (2020); also interprets irrigation-water analyses (salinity relevant to Campo de Cartagena). — [Interempresas](https://www.interempresas.net/Agricola/326756-Murcia-trabaja-en-practicas-de-riego-y-abonado-mas-eficientes.html); [Infoagro 2025](https://www.infoagro.com/noticias/2025/murcia_cuenta_con_una_red_de_55_estaciones_agrometeorologicas_que_anal.asp); [iAgua](https://www.iagua.es/noticias/murcia/12/12/09/el-sistema-de-informacion-agrario-de-murcia-amplia-su-oferta-de-servicios-gratuitos-e-incrementa-el-244)
- UPCT received about EUR 3 million EU funding to digitalise irrigation and is sensorising parcels of irrigation communities in Campo de Cartagena. — [iAgua](https://www.iagua.es/noticias/universidad-politecnica-cartagena/casi-tres-millones-euros-ue-digitalizar-riego)
- Prithvi-EO-2.0 (IBM/NASA): foundation model pre-trained on HLS V2 (30 m), 300M/600M, TL variants, usable via TerraTorch; a multitemporal crop segmentation Colab exists in the NASA-IMPACT repo; no ready 2.0 crop-type demo Space found (older 1.0 crop classification demo exists). — [HF Prithvi-EO-2.0-600M](https://huggingface.co/ibm-nasa-geospatial/Prithvi-EO-2.0-600M); [arXiv 2412.02732](https://arxiv.org/pdf/2412.02732v3)
- Adoption evidence: South Dakota survey (n=312 corn/soy farmers): cost is a deterrent, lack of confidence in recommendations and reliance on trusted consultants slow adoption, farmers still field-check DSS output. — [Crops & Soils: Building trust in AI farming tools](https://www.sciencesocieties.org/publications/crops-soils/2024/september-october/building-trust-in-ai-farming-tools); [ASA print PDF](https://sciencesocieties.org/print/pdf/node/288)
- A 2026 systematic review of agricultural-extension DSS in India (2015-2025) notes multi-source decision support for crop selection/input management is comparatively under-studied. — [Plant Archives review](https://plantarchives.org/article/97%20DECISION-SUPPORT-SYSTEMS-IN-AGRICULTURAL-EXTENSION-A-SYSTEMATIC-REVIEW-OF-ARCHITECTURES,-TECHNIQUES-AND-APPLICATION.pdf)

### Inferences
- A defensible module list for a student DSS, mirroring production tools: (1) field/parcel selection, (2) weather/water-balance (FAO-56 style), (3) satellite NDVI crop-calendar evidence, (4) crop suitability, (5) economics, (6) rotation rules, (7) preference weighting, (8) explanation + uncertainty. Production tools omit (5)-(7) at the crop-choice level; farmers' reliance on advisors suggests framing output as "advice to discuss with your technician", as Ichya20/sagar25446 do.
- SIAM (free, Murcia-specific, official) is a credibility anchor: cite it and, if possible, benchmark your water-need numbers against it rather than competing with it.

### Gaps
- Not researched with sources: Microsoft FarmBeats details, Climate FieldView UI, CGIAR / Digital Green, India Kisan/ICAR apps, FAO AquaCrop GUI uncertainty presentation. No cited evidence on how these present uncertainty.
- FaST national implementation status in Spain, and whether it covers Murcia, was not found (only pilot regions Andalucia and Castilla y Leon and a MITECO slide deck of unclear status).
- Azure Data Manager for Agriculture sources are 2023 (preview); current status unknown.

## 3. Prior Space Apps agriculture winners/finalists and other hackathon crop recommenders; what judges rewarded

### Takeaway
I found very few verifiable past agriculture winners: 2025 Global Winner "Zumorroda-X" (Art & Technology award, Farm Navigators challenge), 2024 Global Nominee "Ometeotl: Crop Connect" (Mexico), and a 2017 crop-sowing recommender "Feedr". The public record of what judges rewarded for agriculture is thin; the official rubric is the only firm evidence.

### Cited Findings
- 2025: Zumorroda-X (Cairo, Egypt; 4 members) won the Art & Technology award for the "NASA Farm Navigators: Using NASA Data Exploration in Agriculture" challenge; 2025 winners were the top 10 of 11,500+ submissions. — [NASA 2025 winners announcement](https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-announces-2025-international-space-apps-challenge-global-winners/); [Military Aerospace summary](https://militaryaerospace.com/home/article/55261943/nasa-announces-winners-for-its-space-apps-challenge)
- 2024: "Ometeotl: Crop Connect" (Tecnologico de Monterrey) was a Global Nominee, an agricultural platform giving farmers data-driven insights (Meteomatics customer story). — [Meteomatics](https://meteomatics.com/en/news/ometeotl-crop-connect) (URL seen in search results; direct fetch returned 404 so content is from the search snippet only)
- 2017: "Feedr" recommended crops to sow each season. — [2017 Feedr page](https://2017.spaceappschallenge.org/challenges/earth-and-us/live-smart/teams/feedr)
- Official criteria: Impact, Creativity, Validity, Relevance, Presentation (equal attention to Presentation advised). — [Judging & Awards Guide](https://www.spaceappschallenge.org/resources/judging-awards-guide)
- NASA's own parallel programme: NASA Acres / Space-to-Soil challenge exist, showing NASA's agriculture priorities (soil + satellite data to farmers). — [Oklahoma Farm Report on NASA Acres](https://www.oklahomafarmreport.com/2026/03/11/from-satellites-to-seeds-nasa-acres-fiat-bridging-the-gap-between-space-and-the-soil/); [NASA Space to Soil winners](https://esto.nasa.gov/nasas-soil-to-ag-challenge-selects-winners/)

### Inferences
- Based on the one criterion set available, the winnable axes are Validity (cite sources, show checks, state limits) and Presentation (video/story), where the strongest 2026 repos invest heavily; hackathon-grade ML accuracy alone is not a rubric item.
- A farmer persona/story (Zul-Qarnain's "Karim") and a working live demo link are now table stakes among top 2026 entries.

### Gaps
- No verifiable list of 2019-2023 agriculture winners/finalists and no judge comments. The 2025 winners page itself could not be fetched. Needs manual pass on spaceappschallenge.org awards pages (2019-2025).
- "Nave" (2024 Galactic Impact winner) not confirmed as agriculture-related.

## 4. Stack for a fast build: data access, backend, frontend, models, optimisation, gotchas

### Takeaway
A 30-hour build is realistic if all NASA/soil data is pre-fetched offline for a handful of demo parcels into static files, and the live app is a thin FastAPI (or Streamlit) layer serving precomputed tables plus a deterministic scoring/optimisation engine. The most robust public, key-free sources are NASA POWER and Planetary Computer's HLS STAC; SoilGrids REST is rate-limited and unreliable.

### Cited Findings
**Data access.**
- HLS v2.0: Planetary Computer STAC collections `hls2-s30` (Sentinel-2) and `hls2-l30` (Landsat), cloud-optimised GeoTIFFs, 30 m, global, time extent from 2020-01-01, 2-3 day combined revisit, latency about 1.7 days, MGRS tiles stackable for time series. — [hls2-s30 STAC collection](https://planetarycomputer.microsoft.com/api/stac/v1/collections/hls2-s30); [hls2-l30](https://planetarycomputer.microsoft.com/api/stac/v1/collections/hls2-l30)
- Typical Python pattern for HLS on the Planetary Computer: pystac_client + planetary_computer signing + stackstac; Red (B04), NIR (B08) and the Fmask for cloud masking when computing NDVI. Tutorial examples: [pcxarray HLS time series](https://pcxarray.readthedocs.io/en/latest/examples/hls_timeseries.html); [NASA/Earthdata blog on HLS on PC](https://www.earthdata.nasa.gov/news/blog/harmonized-landsat-sentinel-2-hls-data-now-available-microsofts-planetary-computer). I found no verified odc-stac example.
- earthaccess (NASA Earthdata client): credentials from `.netrc` or `EARTHDATA_USERNAME`/`EARTHDATA_PASSWORD` env vars, prompts otherwise; `persist=True` writes `.netrc`; Earthdata Login tokens expire after a month. Needs a free Earthdata account (for HLS from LP DAAC, SMAP, IMERG). — [earthaccess quick-start](https://earthaccess.readthedocs.io/en/latest/quick-start/); [PyPI](https://pypi.org/project/earthaccess)
- NASA POWER REST API: no key; HTTP 429 returned when too many requests; Application API slowest (can take up to about a minute). The AWS Open Data Zarr archive is an alternative for bulk pulls (used by Zul-Qarnain). — [POWER API docs](https://power.larc.nasa.gov/docs/services/api/); [POWER on AWS Open Data](https://registry.opendata.aws/nasa-power/)
- SoilGrids REST (`rest.isric.org/soilgrids/v2.0/properties/query`): documented as beta; one third-party doc cites a Fair Use limit of 5 calls per minute (not found on ISRIC's own page); ISRIC has at times paused the service. Query supports `value=mean&value=uncertainty` and Q05/Q95 (Ichya20 uses those). — [SoilGrids access FAQ](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_02.html); [QGIS plugin doc citing 5/min](https://soilgrids-downloader-qgis-plugin.readthedocs.io/en/latest/); [rest.isric.org](https://rest.isric.org/)
- Google Earth Engine requires registration (not verified in this research; known from general knowledge only, not cited).
- Competitors' pattern: MODIS NDVI via ORNL DAAC subsets web service (point/small-area, no big downloads) — [ORNL DAAC MODIS web service](https://modis.ornl.gov/data/modis_webservice.html) (linked by Ichya20 README).

**Models/uncertainty/optimisation.**
- MAPIE (scikit-learn-contrib) gives distribution-free prediction intervals (conformal), works with any scikit-learn-compatible regressor including LightGBM; supports conformalised quantile regression; API changed across versions so pin the version. — [MAPIE docs](https://mapie.readthedocs.io/en/latest/); [arXiv 2207.12274](https://arxiv.org/pdf/2207.12274v1)
- Crop models: AquaCrop-OSPy (water-limited yield, irrigation scenarios) and PCSE/WOFOST (see section 2). — [AquaCrop-OSPy](https://aquacropos.github.io/aquacrop); [PCSE](https://pcse.readthedocs.io/en/stable/)
- Simple physically grounded alternative used by a competitor: Hargreaves ET0 from POWER temperatures (FAO-56) and a product-of-fits suitability score. — [Stalker-a/field-shift-kz](https://github.com/Stalker-a/field-shift-kz)
- Local market data: MAPA publishes weekly fruit & vegetable price bulletins as PDFs (lettuce, broccoli, artichoke, cauliflower etc., Murcia market referenced); I found no machine-readable series. — [MAPA weekly bulletin example, wk 44/2024](https://servicio.mapa.gob.es/ca/ganaderia/estadisticas/442024boletinsemanaldepreciosdefrutasyhortalizas28octubre-3noviembre_tcm34-696459.pdf); [wk 18/2025](https://servicio.mapa.gob.es/ca/ganaderia/estadisticas/182025boletinsemanaldepreciosdefyh28abril-4mayo_tcm34-707878.pdf)
- Campo de Cartagena crop mix: lettuce is the largest crop (15,420 ha, 46 % of national total per a 2024-era article), then broccoli, artichoke, melon, watermelon, cauliflower, celery, etc., mainly outdoors; cold and heat episodes have caused price swings and crop damage. — [Cajamar outdoor vegetables 2021/22](https://publicacionescajamar.es/wp-content/uploads/2023/03/horticolas-aire-libre-c1-2022.pdf); [MAPA Vrural](https://www.mapa.gob.es/ministerio/pags/Biblioteca/Revistas/pdf_Vrural/Vrural_2012_344_15_18.pdf); [ASAJA cold damage](https://www.agronewscastillayleon.com/asaja-murcia-estima-que-el-frio-ha-danado-duramente-mas-del-40-de-las-hortalizas-del-guadalentin)
- Frontends actually used by competitors: Next.js (Zul-Qarnain, AbelAnil with MapLibre), React+Leaflet+FastAPI (Ichya20), Streamlit (Stalker, sagar25446). — repos linked in section 1.

### Inferences
- Fastest credible path: Python offline pipeline (POWER + HLS via Planetary Computer STAC, no login needed for reading signed COGs; earthaccess only if SMAP/IMERG needed) -> parquet/JSON per parcel -> FastAPI or Streamlit. Streamlit proved deployable in a day by a competitor (live Streamlit Cloud demo).
- Because SoilGrids REST is rate-limited and sometimes paused, pre-fetch the 5-10 demo points once (cache JSON in repo) and keep a regional-average fallback; Ichya20's no-silent-fallback rule is a good guardrail to copy as a concept.
- Optimisation: with 3-6 candidate crops and short rotation lengths, brute-force enumeration (as Zul-Qarnain and Stalker do) with weights is sufficient; PuLP/OR-Tools only needed if you add constraints over multiple parcels (e.g. total water allocation or labour); mention as stretch (not verified from sources).
- Prithvi fine-tuning for crop-type is a heavy GPU/time risk in 30 h and not required by the rubric; using plain HLS NDVI phenology (green-up/harvest dips = bare-field windows) is cheaper and more explainable (inference; no source tested this).
- Market price: only PDF bulletins found, so a hand-curated small price table with min/max range from several weeks of bulletins (documented as manual extraction) is likely the realistic route; label as scenario input, not forecast.

### Gaps
- Planetary Computer rate limits/SAS token behaviour, HLS file sizes and per-scene download volume not verified. earthaccess `search_data` short names for HLS (HLSS30/HLSL30) not verified.
- GEE registration requirement and Cartagena-specific STAC tile (MGRS tile ID for Campo de Cartagena, e.g. 30SXG/30SXH) not verified; check with a STAC search.
- IMERG/SMAP access details (Earthdata login, GES DISC subsetting) not researched. POWER request-rate figures not found (only 429 mentioned).
- Poolred / Lonja de Murcia / Spain open-data price APIs not found; no machine-readable price source verified. AquaCrop-OSPy default crop library has no lettuce/broccoli/artichoke confirmed (not checked).

## 5. Explainability patterns for farmers (SHAP, "why this crop" cards, limiting factor display)

### Takeaway
The strongest 2026 entries use deterministic, additive explanations (score bars summing to the total, a "See why" drawer, per-crop limiting factor) rather than SHAP on a black-box model; literature says feature importance alone is insufficient for farmer trust.

### Cited Findings
- Zul-Qarnain: stacked score breakdown that visibly adds to the total; "See why" panel showing the arithmetic and data source; penalties listed with rule + source; confidence label; bilingual reasons/risks; SMS-length advice with 160-char counter; same inputs always give same answer. — [README](https://github.com/Zul-Qarnain/field-shift); [engine.ts](https://github.com/Zul-Qarnain/field-shift/blob/main/web/lib/engine.ts)
- Stalker-a: crop fit shows per-factor fits (temperature, water, season, salinity) whose product is the suitability, so the limiting factor is the smallest fit; per-rotation plain-language explanation compared against the current rotation. — [rotation.py](https://github.com/Stalker-a/field-shift-kz/blob/main/fieldshift/rotation.py); [README](https://github.com/Stalker-a/field-shift-kz)
- Ichya20: 12 checks matrix per strategy with status (pass/fail/unknown) and listing of missing inputs; layer availability panel stating source, period, spatial support. — [README](https://github.com/Ichya20/FieldShift)
- Literature: black-box models make farmers hesitant; feature-importance explanations remain insufficient for detailed decision pathways; decision-tree-based explanations were reported to improve transparency (2025 interpretable crop selection and XAI-CROP papers, via search summary). — [Springer s00521-023-09391-2](https://link.springer.com/article/10.1007/s00521-023-09391-2); [Crops & Soils](https://www.sciencesocieties.org/publications/crops-soils/2024/september-october/building-trust-in-ai-farming-tools)
- Farmers field-check DSS recommendations and trust consultants, so advice should be presented as something to verify. — [ASA print PDF](https://sciencesocieties.org/print/pdf/node/288)

### Inferences
- For a ranked profitability list, the most transferable pattern is: decomposable score (profit, water, soil/rotation, risk) as a stacked bar + one "limiting factor" chip per crop + a "what would change this ranking" what-if (e.g., price -20 %, water cut) + uncertainty band on profit (conformal or scenario min/max). SHAP is only warranted if you train an ML model; with rule/physics-based scoring, direct decomposition is exact and cheaper.
- Show data provenance and "unknown" explicitly (Ichya20) rather than defaulting; this directly serves the Validity criterion.

### Gaps
- No evidence found of user testing of explanation formats with farmers; claims are from papers' abstracts/summaries, not full-text reads.

## 6. Concrete MVP scope cuts other teams used, and what to precompute vs compute live

### Takeaway
Top 2026 teams precompute everything NASA-related into committed static files, keep one live call as an optional "nowcast" with graceful outage fallback, restrict to a small crop pool (3-18 crops), a few demo farms/points, and spend remaining time on explanation, honesty and presentation.

### Cited Findings
- Zul-Qarnain: "No server, no API key, no AI model runs inside the app"; science runs in Python before build; 6 demo farms + 70 points precomputed as JSON; browser snaps a map click to nearest precomputed point and names the point + distance; live POWER only for the last 75 days with 8 s timeout and a fallback banner; 12-crop pool. — [README](https://github.com/Zul-Qarnain/field-shift)
- Ichya20: three crops, two sample points, one location + one planning horizon + three strategies; 916 data files hash-verified at startup; no ranking/profit because uncalibrated; field polygons not supported ("point-based analysis"). — [README](https://github.com/Ichya20/FieldShift)
- Stalker-a: twelve preset regions shipped with the repo so the demo works offline; derived tables cached; 16 crops; POWER only. — [README](https://github.com/Stalker-a/field-shift-kz)
- sagar25446: rule-based rotations only in four pilot regions; outside them shows climate data only and refuses to recommend. — [README](https://github.com/sagar25446-prog/FieldShift-NASA)
- ada-th25 plan: per-demo-farm cached API responses under `data/cache/`, crop agronomic matrix in `crops.json`, API contract documented first. — [ada-th25/field-shift](https://github.com/ada-th25/field-shift)
- AbelAnil (solo) built eleven phases including LLM assistant, carbon credits, livestock; example of scope creep on a one-person team. — [AbelAnil/FieldShift-AI](https://github.com/AbelAnil/FieldShift-AI)

### Inferences
- Precompute offline: HLS NDVI time series per demo parcel (cloud-masked, gap-filled, phenology metrics, bare-field windows), POWER daily 1981-2025 aggregates and ET0, SoilGrids point values (mean + Q05/Q95), price table, crop parameter table, and all candidate-rotation scores for default preference weights.
- Compute live: re-weighting by farmer preferences (time to return, investment, risk, water) over precomputed component scores; what-if sliders; rotation comparison; optional POWER nowcast with cached fallback. This keeps the demo deterministic and offline-safe, matching the strongest competitor.
- Scope cuts that preserve the five criteria: 5-8 parcels (clickable on a map) in Campo de Cartagena, 6-8 crops (lettuce, broccoli, artichoke, cauliflower, melon, fallow/legume break, etc.), >=3 rotation candidates with explicit hard rules, no LLM chat, no user accounts, no mobile native app; bilingual ES/EN is optional.
- Differentiation priority (largest gap vs competitors, from section 1): profit with a price-uncertainty band + HLS-derived bare-field windows + parcel polygons rather than single points.

### Gaps
- No published post-mortems from other hackathon teams on time allocation; the above is inferred from repo structure and READMEs.
- Time-to-build for an HLS pipeline over several parcels was not measured; recommend a 1-2 h spike on a single MGRS tile before committing.
