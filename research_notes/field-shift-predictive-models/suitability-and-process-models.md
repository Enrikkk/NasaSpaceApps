# Crop suitability models, crop-recommendation classifiers and process-based crop/water models (submodels for a Campo de Cartagena farmer app)

Research date 2026-11-14. Tools limited to web search plus a small-model page fetcher, so several primary pages (Kaggle, GAEZ docs, ECOCROP full record, FAO-29 equation images) could not be read in full. Items marked UNVERIFIED are not backed by a source I could open.

## 1. Crop-recommendation classifiers (Kaggle "Crop Recommendation", N/P/K/T/humidity/pH/rainfall -> 22 crops)

### Takeaway
The dataset is a 2,200-row, perfectly balanced, India-origin table with no location, date, irrigation or economics. Its provenance is murky (sources conflict: "sensor-collected", "ICFA compiled", "built by augmenting rainfall/climate/fertilizer datasets"), and the 99% accuracy papers do not transfer to Spain. Do not use it as a model. At most it is a loose cross-check of crop climate envelopes.

### Cited Findings
- The dataset description phrase "built by augmenting datasets of rainfall, climate and fertilizer data available for India" is traced to a Figshare copy (Saroj Mali, 2024), which credits the "Indian Chamber of Food and Agriculture (ICFA)". Fields: N, P, K ratios, pH, temperature, humidity, rainfall. — [Figshare via search result](https://figshare.com/articles/dataset/Crop_Recommendation_dataset/26308696) (page itself returned 403 to me; description only seen in search snippet)
- Sources disagree on origin. One paper says IoT-sensor collected; another says accumulated by the "Food and Agriculture Council of India" (a body I could not verify). 2,200 records, 22 crops, balanced, no missing values. — [JNSPS paper](https://journal.nsps.org.ng/index.php/jnsps/article/download/3291/534/19325), [Springer s44230-024-00081-3](https://link.springer.com/10.1007/s44230-024-00081-3)
- Several sources state "evenly distributed across 22 crops" / "balanced, 2,200 records"; none I opened states exactly 100/crop. — [Mendeley copy](https://data.mendeley.com/datasets/7j8cz7p7w9), [IRJET](https://issuu.com/irjet/docs/irjet-v12i12118)
- No source I found proves the data synthetic. But derivatives are explicitly synthetic: CTGAN-augmented (~1,000 extra rows concatenated, XGBoost 99.09% reported, so test/train separation vs. synthetic rows unclear), and SMOTE/VAE/CropGAN versions whose card warns of "minor distributional deviations" and non-generalisation across regions. — [MDPI Eng. Proc. 82/95](https://mdpi.com/2673-4591/82/1/95), [CropGAN dataset card](https://www.maratto.africa/research/crop-recommendation-dataset-with-smote-vae-and-cropgan-40b89927d9)
- Methodological critique of the field: studies share ad hoc model selection from point estimates, no formal statistical validation; one benchmark locked its test set to guarantee zero leakage, implying others do not. — [Indian J. Agric. Res. A-6614](https://arccjournals.com/journal/indian-journal-of-agricultural-research/A-6614)
- Heliyon 2024 (Dey et al.) tested SVM/XGBoost/RF/KNN/DT on the Kaggle data (NPK, pH, temp, rainfall, humidity); XGBoost best; authors suggest separating agricultural vs horticultural crops. — [DOAJ record](https://doaj.org/article/2036c72fa43f4f2b96d73c7412ae8156) (via search snippet; page 403)
- The 22 classes are mostly tropical/Indian crops (the one I can attest from the sources: includes cereals and pulses; I could not open the list). UNVERIFIED that lettuce, broccoli, artichoke or barley are absent; my recollection is they are absent but I did not confirm in this session.

### Inferences
- No location, season, irrigation, or price columns means it cannot answer "which crop where, when, with how much water". The inverse query cannot be derived from it either.
- Near-perfect accuracy on a balanced table where classes are probably separable by humidity/rainfall alone says nothing about Spanish horticulture. It tests nothing real-world.
- Salvageable only as a crude sanity prior of T/rain/pH ranges for crops not in ECOCROP, which is unnecessary since ECOCROP is better documented. Recommendation: cite as "considered and rejected" in the pitch.

### Gaps
- Could not read the original Kaggle page (author description, license) or find a rigorous peer-reviewed forensic critique of the dataset's synthetic nature. Provenance remains unconfirmed.

## 2. Rule/envelope suitability: ECOCROP/Recocrop, GAEZ, fuzzy and limiting-factor combination

### Takeaway
ECOCROP (via R `Recocrop`, ~1,710 taxa) is the cheapest defensible "is this crop viable here" filter, but it is monthly, expert-opinion, uses a limiting-factor (min) rule, and has no salinity or irrigation. GAEZ v4 gives ready-made suitability/attainable-yield rasters for 51 crops at 5 arc-min (~9 km), too coarse for parcels and likely missing lettuce/broccoli/artichoke. Practical approach for a hackathon: hand-built trapezoidal membership functions per crop, combined with min() or a geometric mean, with parameters from ECOCROP/FAO-56/FAO-29.

### Cited Findings
- Recocrop 0.4-0 (CRAN, July 2025) implements ECOCROP as a limiting-factor model: Sprengel-Liebig law of the minimum, interactions ignored; each variable is a trapezoid/plateau (0 below min, 1 between optimum min and max, linear in between). — [Recocrop manual](https://cropmodels.r-universe.dev/Recocrop/doc/manual.html), [CRAN refman](https://cran.r-project.org/web/packages/Recocrop/refman/Recocrop.html)
- Parameters: `prec` (4 thresholds, monthly precip, derived from FAO annual values divided by (growth duration in months + 1)), `tavg` (4 thresholds), `ktmp` (killing minimum temperature; only min + lower optimum used), duration in days. Heat damage not modelled. Time step is monthly (12 values per year). Default parameters for 1,710 taxa via `ecocropPars()`. Docs warn parameters are expert opinion and not necessarily optimal. — same Recocrop manual
- Lettuce ECOCROP record (id 1313): killing temp -1 C mature plants, -6 C seedlings; cycle 35-70 d (leaf) and 60-85 d (head); yield 5-15 t/ha. The page text I got did not expose optimal/absolute T, rain, pH. A mirror (EOL) gives optimal T ~12-21 C, rain ~1100-1400 mm/yr, pH 6-7, rooting 50 cm (secondary, verify). — [ECOCROP 1313](https://ecocrop.apps.fao.org/ecocrop/srv/en/cropView?id=1313), [EOL mirror](https://media.eol.org/pages/56983376/data)
- ECOCROP rain optimum for lettuce (1100-1400 mm/yr) is a rainfed-agronomy number and would wrongly reject irrigated Campo de Cartagena (~300 mm/yr rain, from my own prior verified POWER context, not a cited source here). So rain must be replaced by water-balance/irrigation-need logic. This is an inference, see below.
- GAEZ v4: 51 crops, rain-fed and irrigated, two management levels (high/low input), 5 arc-minute grid (~9 km at the equator), six modules including Theme 4 "Suitability and Attainable Yield"; climate 1961-2010 historical plus AR5 RCP futures; portal at gaez-v4-data.fao.org. — [FAO GAEZ v4](https://www.fao.org/gaez/gaezv4/en), [IIASA/EurekAlert ~600,000 layers at 9 km2](https://www.eurekalert.org/news-releases/549167)
- GAEZ raster file naming: `res05/CRUTS32/Hist/8110/ycHr0_whe.tif` pattern, variable codes `yc` (attainable yield of current cropland), `yl` (output density), `yx` (attainable yield of best suitability class in cell); input `H`/`L`; water supply code `r` = rainfed (irrigated codes not confirmed); base URL S3 bucket `data.gaezdev.aws.fao.org`. — [GAEZr docs (community R package)](https://floswald.github.io/GAEZr/reference/gaez_download.html)
- GAEZ documentation: Global Agro-Ecological Zones v4 Model documentation, FAO, DOI 10.4060/cb4744en. Not readable (403). — [search result](https://openknowledge.fao.org/items/039f7ec9-98af-49e1-8d24-850122c69bef)
- FAO land evaluation (Sys et al.) fuzzy / limiting factor combination: not retrieved. See Gaps.

### Inferences
- At ~9 km, a whole Campo de Cartagena (~1,200 km2) is roughly 10-15 cells. GAEZ can only serve as a regional sanity check ("GAEZ says X is suitable irrigated at 90%"), not parcel ranking. Crop list gap (lettuce/broccoli/artichoke not confirmed present) likely forces ECOCROP/FAO-56/FAO-29 anyway.
- For combination: min() (Liebig) is the transparent default for "limiting factor" explanations a farmer or jury will understand; a weighted geometric mean avoids one soft factor zeroing a crop. Offer min() for hard factors (frost kill, salinity > zero-yield ECe, pH) and geometric mean for soft factors (OM, drainage). This is my design suggestion, not a sourced claim.
- Because trapezoids need 4 numbers per factor, the data cost is ~5 factors x ~8 crops x 4 = 160 numbers; feasible in ~3 h if drawn from ECOCROP + FAO-29.

### Gaps
- GAEZ v4 crop list and irrigated codes, and whether lettuce/broccoli/artichoke/melon are included (I could not open the portal or documentation); GAEZ license terms.
- Sys et al. FAO land-evaluation parametric/fuzzy method: not retrieved.
- Full ECOCROP numeric records for broccoli, melon, artichoke, faba bean, barley (only lettuce partially seen). Run `Recocrop::ecocropPars()` in R to dump them (not done).

## 3. Species-distribution / MaxEnt-style suitability from presence-only crop data

### Takeaway
Feasible in principle but a poor fit for 30 hours and for this question: it needs crop presence points (SIGPAC declarations would be ideal, not verified), outputs relative environmental suitability not yield or water need, and ignores irrigation and management.

### Cited Findings
- Heumann, Walsh & McDaniel (2011) used MaxEnt for crop suitability in NE Thailand with three different presence datasets; results were highly sensitive to sample size and the distribution of points in geographic and environmental space; accuracy assessment without true absences is unresolved. — [PubMed 21860606](https://www.pubmed.gov/21860606/), [core.ac.uk PDF](https://core.ac.uk/download/345207549.pdf)
- Maxent output is relative environmental suitability, not probability of occurrence (default prevalence 0.5 assumption); bias-matched background points improve predictions. — [EcoCommons guide](https://support.ecocommons.org.au/support/solutions/articles/6000254294)
- A recent maize study cautions bioclimatic-only predictions omit soil, topography, land use, pests, and may overstate suitability. — [Belvisi & Tranchina 2026 (iris.unipa.it)](https://iris.unipa.it/retrieve/624c46e3-0e77-4dd2-a1ea-104a9af6b7d9/Belvisi%2b%26amp%3b%2bTranchina%2c%2b2026.pdf) (snippet only)

### Inferences
- In a single 1,200 km2 intensively irrigated district nearly all parcels have the same climate; presence points would mostly reveal grower habit and market, not agronomic suitability (all crops are "present" across the same climate). MaxEnt would learn soil/zone patterns at best and cannot rank profitability. Skip for the hackathon; mention as future work if SIGPAC crop-declaration data is used.

### Gaps
- Did not verify availability of SIGPAC/Murcia crop-declaration open data, or WorldCereal coverage of horticulture (WorldCereal is cereal/maize-oriented; unverified here).

## 4. Process models: AquaCrop-OSPy, WOFOST/PCSE, DSSAT, APSIM

### Takeaway
AquaCrop-OSPy is the only realistic water-driven option and it handles irrigation scheduling and GDD, but its built-in crop library has no lettuce, broccoli, melon or artichoke (37 entries, mostly field crops; closest are Tomato, Potato, Barley, Default). PCSE/WOFOST has 20 active crops, none of them Mediterranean vegetables except seed_onion, and its shown config is potential-production. For a 4-student 30 h project, a spreadsheet-style FAO-56 water balance plus GDD calendars is more realistic than calibrating a process model.

### Cited Findings
- AquaCrop-OSPy: Python implementation of FAO AquaCrop based on AquaCrop-OS; README says it mirrors most features of AquaCrop 7.1; Apache-2.0; paper Foster et al., Agric. Water Manag., DOI 10.1016/j.agwat.2021.106976. `pip install aquacrop`. Components: Soil, Crop (name + planting_date), InitialWaterContent, weather via `prepare_weather()`, `run_model(till_termination=True)`. Notebooks: irrigation demand, optimizing irrigation, climate change impacts. — [GitHub](https://github.com/aquacropos/aquacrop), [docs](https://aquacropos.github.io/aquacrop/)
- Built-in crop dictionary (37 keys) per `crop_params.py`: Barley(+GDD), Cotton, DryBean, Maize, PaddyRice, Potato (3 variants), Quinoa, Sorghum, Soybean, SugarBeet, SugarCane, Sunflower, Tomato(+GDD), Wheat variants, Tef, AlfalfaGDD, Cassava, Default. No lettuce, broccoli, melon, artichoke, citrus. Each can be CalendarType 1 (calendar days) or 2 (GDD). Examples: Barley GDD 98/160/1296 (emerge/flower/maturity), Tbase 0, Tupp 15, Zmax 1.3 m, HI0 0.33; Tomato GDD 43/750/1933, Tbase 7, Tupp 28, HI0 0.63, CCx 0.75; Potato GDD Tbase 2, Tupp 26. — [crop_params.py](https://raw.githubusercontent.com/aquacropos/aquacrop/master/aquacrop/entities/crops/crop_params.py) (via summarising fetcher; spot-check before quoting)
- Custom crops: `c_name="custom"` supported but must supply water-stress parameters (p_up1-4, p_lo1-4, fshape_w1-4); no salinity thresholds appear in the Crop class file. — [crop.py](https://raw.githubusercontent.com/aquacropos/aquacrop/master/aquacrop/entities/crop.py)
- Calibration literature exists for lettuce (Algeria, rainfed fertility study, v6.1) and cauliflower/spinach (Belgium, found cultivar-specific calibration needed for cauliflower); none found for broccoli, melon, artichoke. FAO says AquaCrop is meant to work without local calibration once conservative parameters are set per species. — [CIGR J. lettuce](https://cigrjournal.org/index.php/Ejounral/article/view/6195), [Frontiers Plant Sci. 2023](https://www.frontiersin.org/articles/10.3389/fpls.2023.1094677/full)
- PCSE/WOFOST: crop parameter repo `ajwdewit/WOFOST_crop_parameters` ("23 crops"; branches wofost72/73/80(deprecated)/81). Active `crops.yaml` on wofost81 lists 20: barley, cassava, chickpea, cotton, cowpea, fababean, groundnut, maize, mungbean, pigeonpea, potato, rapeseed, rice, soybean, sugarbeet, sunflower, sweetpotato, tobacco, wheat, seed_onion (millet, sorghum, sugarcane commented out). — [repo](https://github.com/ajwdewit/WOFOST_crop_parameters), [crops.yaml](https://raw.githubusercontent.com/ajwdewit/WOFOST_crop_parameters/wofost81/crops.yaml)
- PCSE: `NASAPowerWeatherDataProvider` fetches NASA POWER by lat/lon (doc states 0.25x0.25 deg); required daily weather TMAX, TMIN, VAP, WIND, RAIN, IRRAD (optional SNOWDEPTH); derives E0, ES0, ET0, TEMP. Agromanagement via YAML CropCalendar (crop_name, variety_name, crop_start_date, crop_end_date, max_duration) plus timed/state events. Docs example shown is potential production (`WaterbalancePP`). — [PCSE reference guide](https://pcse.readthedocs.io/en/stable/reference_guide.html)
- DSSAT and APSIM: not researched in depth (no sources opened). See Gaps.

### Inferences
- Best-case use of AquaCrop-OSPy: Tomato (processing-type), Potato, Barley, Wheat, Alfalfa entries are usable as-is; lettuce/broccoli/melon/artichoke would each need a custom parameter set (non-trivial: ~30 parameters each, no sourced values found). Not realistic in 30 h for 5 crops.
- Using the "Default" or Tomato crop as a stand-in for vegetables would produce plausible-looking but unvalidated yields; be explicit if used.
- PCSE's POWER provider is a confirmed in-ecosystem use of POWER for crop models (the user already verified the POWER API). The 0.25 deg figure in the docs may be outdated; POWER's native resolution differs by parameter (UNVERIFIED here).
- The rest of the app (profitability ranking, rotations) needs per-crop cycle length, ET demand and yield expectations, which are easier to supply from tables than from a model run.

### Gaps
- DSSAT and APSIM crop lists, licensing, installation effort and runtime; AquaCrop-OSPy runtime per season (not stated in sources); whether AquaCrop-OSPy supports salinity stress (not seen in the Crop class); PCSE water-limited (WaterbalanceFD) configuration details; AquaCrop conservative parameters (FAO I2800e06.pdf was suggested by search but not opened).

## 5. FAO-56 crop water requirement: Kc, stages, ET0, effective rain; FAO-29 salinity and leaching

### Takeaway
FAO-56 Tables 11/12 give directly usable Mediterranean stage lengths and Kc for lettuce, melon, artichoke, faba bean, barley. Salinity thresholds from FAO-29 show lettuce, melon, broccoli, citrus are sensitive (ECe threshold 1.0-2.8 dS/m), while artichoke and barley are tolerant. That is the key differentiator for saline Campo de Cartagena water. Hargreaves from POWER Tmin/Tmax is a workable ET0 proxy, with a bias risk.

### Cited Findings
**FAO-56 Table 11 (stage lengths, days: ini/dev/mid/late = total)** — [FAO-56 ch.6](https://www.fao.org/4/x0490e/x0490e0b.htm)
- Lettuce: 20/30/15/10 = 75 (April, Mediterranean); 30/40/25/10 = 105 (Nov/Jan, Mediterranean); 25/35/30/10 = 100 (Oct/Nov, arid); 35/50/45/10 = 140 (Feb, Mediterranean)
- Broccoli: 35/45/40/15 = 135 (Sept, California desert)
- Cabbage: 40/60/50/15 = 165 (Sept, California desert)
- Cantaloupe/melon: 30/45/35/10 = 120 (Jan, California); 10/60/25/25 = 120 (Aug, California)
- Artichoke: 40/40/250/30 = 360 (April, 1st year, California); 20/25/250/30 = 325 (May, 2nd year)
- Faba bean: 15/25/35/15 = 90 (May, Europe); 20/30/35/15 = 100 (Mar/Apr, Mediterranean); dry 90/45/40/60 = 235 (Nov, Europe)
- Barley/oats/wheat: 20/50/60/30 = 160 (Dec, California desert); 15/25/50/30 = 120 (Nov, Central India); 40/60/60/40 = 200 (Nov)

**FAO-56 Table 12 (Kc ini / mid / end, max height m)** — same source
- Lettuce: ini 0.7 (small-vegetable group; individual value was an image I could not read) / 1.00 / 0.95; 0.3 m
- Broccoli: 0.7 (group) / 1.05 / 0.95; 0.3 m
- Cabbage: 0.7 (group) / 1.05 / 0.95; 0.4 m
- Melon (cantaloupe): 0.5 / 0.85 / 0.60; 0.3 m
- Artichoke: 0.5 / 1.00 / 0.95; 0.7 m
- Faba bean: fresh 0.5 / 1.15 / 1.10; dry 0.5 / 1.15 / 0.30; 0.8 m (1.15 footnote for tall legumes)
- Barley: ini 0.3 (cereal group) / 1.15 / 0.25; 1 m
- Cover crops: no entries in Tables 11/12 as extracted.
- Caveat: values from a summarising fetcher over an HTML page with images; verify against the printed tables before quoting. Table 12 Kc ini for vegetables in FAO-56 is a function of wetting events (ini value depends on irrigation frequency), so 0.7 is typical for frequent irrigation, not fixed.

**FAO-29 Annex 1 salinity tolerance (ECe threshold dS/m; slope %yield loss per dS/m; rating)** — [FAO-29 Table A1.1/A1.2](https://www.fao.org/4/Y4263E/y4263e0e.htm)
- Lettuce 1.3; 13; MS (matches UC Davis extension)
- Broccoli 2.8; 9.2; MS
- Cabbage 1.8; 9.7; MS
- Muskmelon 1.0; 8.4; MS
- Artichoke (globe) 6.1; 11.5; MT
- Broad bean 1.6; 9.6; MS
- Barley (grain) 8.0; 5.0; T. Barley (forage) 6.0; 7.1; MT
- Tomato 2.5; 9.9; MS; Spinach 2.0; 7.6; MS
- Orange 1.3; 13.1; S. Lemon 1.5; 12.8; S. Grapefruit 1.2; 13.5; S. Almond 1.5; 19; S. Olive: MT, no threshold/slope given.
- Relative yield: Yr = 100 - b(ECe - a), a = threshold, b = slope, ECe = mean saturated-paste EC of the root zone. Plants on gypsiferous soils tolerate ~2 dS/m higher ECe. — same source
- Leaching: FAO-29 section 2.4.2 and Example 3 give an LR method (maize example ECw 1.2 dS/m, ET 800 mm, efficiency 0.65 -> 1230 mm applied, with leaching met by irrigation inefficiency, LF 0.10-0.16); equations (7) and (9) are images and could not be read. — [FAO-29 ch.2](https://www.fao.org/4/t0234e/T0234E03.htm)

**ET0**
- POWER ET0 vs FAO-56 PM: Sicily 2006-2014 study found POWER-derived daily ET0 tracked PM well (1 deg grid); Hargreaves-Samani underestimated PM by 5.5% (Mar-Aug) in a semi-arid Mexican test; accuracy varies by environment. — [Sicily study (MDPI Sensors 2023)](https://doi.org/10.3390/s23157007), [PMC10422496](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10422496/)
- Southern Spain, 16 stations: Hargreaves ET0 was 0.69 mm/d lower than PM at coastal stations and +0.13 mm/d at inland ones; calibrated Hargreaves does well in SE Spain; ratio HS/PM changes seasonally. — [NHESS 20, 859 (2020)](https://nhess.copernicus.org/articles/20/859/2020/nhess-20-859-2020.pdf), [Finisterra 2024](https://revistas.rcaap.pt/finisterra/article/view/33850/26532) (snippets)
- Local irrigation-advice source: Murcia's SIAM (created 1995, ~45 automatic stations, free data via siam.imida.es) provides irrigation/fertilization programs for citrus and vegetables including alcachofa, bróculi, lechuga, melón, based on field-determined Kc; IMIDA (Centeno & Rincón) measured Kc for drip-irrigated romaine lettuce in Campo de Cartagena. — [Vida Rural 2010 (MAPA)](https://mapa.gob.es/ministerio/pags/Biblioteca/Revistas/pdf%5FVrural%2FVrural%5F2010%5F306%5F14%5F17%2Epdf), [iAgua](https://www.iagua.es/noticias/murcia/12/12/09/el-sistema-de-informacion-agrario-de-murcia-amplia-su-oferta-de-servicios-gratuitos-e-incrementa-el-244)

### Inferences
- Season ET demand sketch (my arithmetic, not sourced): demand per crop = sum over stages of Kc_stage x ET0 x days. Needs only ET0 from POWER, Table 11 stage lengths shifted to local sowing date, and Kc.
- Salinity screening: if irrigation water ECw is ~1.5-3 dS/m (value to check; Tajo-Segura transfer vs desalinated vs well water differ), the soil ECe is roughly 1.5x ECw at ordinary leaching fractions (rule of thumb, UNVERIFIED here), implying lettuce/melon/citrus yield losses of 5-20% while artichoke and barley are unaffected. This is the strongest "water quality vs crop" ranking lever and pairs well with the FAO-29 formula: Yr = 100 - b(ECe - a).
- Effective rainfall: not sourced; with Campo de Cartagena autumn-winter rainfall of a few tens of mm per event, a simple USDA-SCS or fixed 0.7-0.8 factor is enough (assumption).
- Winter lettuce 100-140 d vs. spring 75 d: sowing-date dependency is large, so cycle length should be computed from GDD where possible (see section 6) with FAO-56 table days as defaults.

### Gaps
- Exact Kc ini for individual vegetables (image in source), FAO-56 Kc adjustment equations for climate, effective-rainfall formula, LR equation text (LR = ECw/(5ECe - ECw) is what I recall from FAO-29 but I could not verify it in the fetched page), SIAM current Kc tables and ET0 method, Campo de Cartagena m3/ha benchmarks per crop (not found), Kc/ET numbers for artichoke perennial first-year patterns in Spain, and cover-crop Kc (FAO-56 Table 12 as extracted had none; FAO-56 does have a cover-crop section for orchards in Table 17, not opened).
- The Murcia-measured POWER vs station ET0 bias is untested; the cited Spanish studies are for other stations.

## 6. Cycle length / time to harvest per crop and sowing date

### Takeaway
Three mechanisms are available: (a) fixed FAO-56 Table 11 stage lengths by planting month (simplest, already region-tagged), (b) ECOCROP cycle min/max days (coarse), (c) GDD accumulation from POWER Tmin/Tmax with crop Tbase/Tupp (AquaCrop-OSPy and WOFOST both do this internally, but only AquaCrop-OSPy has accessible GDD values per crop).

### Cited Findings
- AquaCrop-OSPy stores crop timing as either calendar days or GDD (CalendarType 2): e.g. Barley 1296 GDD to maturity (Tbase 0, Tupp 15), Tomato 1933 GDD (Tbase 7, Tupp 28), Potato 1276 GDD (Tbase 2, Tupp 26), Wheat 2400 GDD (Tbase 0, Tupp 26). — [crop_params.py](https://raw.githubusercontent.com/aquacropos/aquacrop/master/aquacrop/entities/crops/crop_params.py)
- ECOCROP gives a cycle range (lettuce 35-70 d leaf, 60-85 d head); Recocrop takes duration in days. — [ECOCROP 1313](https://ecocrop.apps.fao.org/ecocrop/srv/en/cropView?id=1313), [Recocrop manual](https://cropmodels.r-universe.dev/Recocrop/doc/manual.html)
- PCSE CropCalendar takes crop_start_date and an end condition (maturity or max_duration); phenology is temperature-sum driven (parameter-file based). — [PCSE guide](https://pcse.readthedocs.io/en/stable/reference_guide.html)
- FAO-56 Table 11 gives month-tagged totals, e.g. lettuce 75 d (April) vs 140 d (Feb), 105 d (Nov/Jan). — [FAO-56](https://www.fao.org/4/x0490e/x0490e0b.htm)

### Inferences
- A defensible hackathon scheme: take FAO-56 total days for the nearest planting month as the nominal cycle, derive an implied GDD (sum of daily (Tmean - Tbase) over that window from POWER history), then for any other sowing date step forward until the same GDD is reached. This yields date-specific cycles and harvest dates, and bare-field gaps = days between harvest and next sowing plus the unplanted period. Needs a Tbase per crop (not in FAO-56; for lettuce/broccoli/melon/artichoke I did not find sourced values; typical cool-season brassica/lettuce Tbase ~0-5 C and melon ~10-12 C are from memory, UNVERIFIED).
- Output from this and the Kc/stage tables also feeds directly into the "bare-field periods" and rotation comparison features.

### Gaps
- Sourced Tbase/Tupp and GDD-to-harvest for lettuce, broccoli, melon, artichoke; they are not in the tools I could reach.

## Cross-cutting recommendation (inferential, for the report writer)
1. Do not use the Kaggle classifier; cite as rejected with reasons.
2. Use a transparent rule layer: ECOCROP-style trapezoids on T (Tmin/frost kill, Tmean), pH, soil texture from SoilGrids, and FAO-29 ECe thresholds, combined by min() for hard limits.
3. Use FAO-56 Kc x POWER-derived ET0 (Hargreaves from Tmin/Tmax, or PM from POWER inputs) for crop water requirement, with the FAO-29 leaching term for saline water.
4. Optionally run AquaCrop-OSPy only for crops it ships (barley, tomato, potato, wheat) as a "process-model cross-check", not for lettuce/broccoli/melon/artichoke.
5. GAEZ v4 only as a regional-scale plausibility check (5 arc-min, 51 crops), pending verification of its crop list.

## Source reliability notes
- Several quotes came through a summarising fetcher; numbers for Kc, stage lengths, FAO-29 and crop_params should be spot-checked against the primary page before they go on a slide.
- Conflicting items: GAEZ crop counts (51 on FAO page vs "49 crops" in older v3 guide vs ">100 crops and sub-types" in a portal description); PCSE POWER resolution (0.25 deg in PCSE docs, may not match current POWER); Kaggle dataset origin (IoT sensors vs ICFA vs augmented datasets).
