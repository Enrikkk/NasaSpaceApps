# IoT/sensor data and ML approaches that a 4-person team can realistically use in 36 h for a Murcia crop-rotation decision-support tool (Field Shift, Space Apps 2026)

Researched 2026-11-13 (the day before hacking starts). Challenge text: `context/challenges/06-adapting-farms-with-nasa-data.md`.
Endpoint tests (curl, no credentials) were saved under
`/private/tmp/claude-501/-Users-jaime-Documents-NasaSpaceApps/324b317c-8037-4e23-a8f2-fde635abe82e/scratchpad/api-tests/iot-ml/`.
Statements marked "Inference" are my reasoning, not something a source says. Time estimates for hackathon tasks are always inferences.

---

## Q1. What open ground-sensor data exists for the Región de Murcia / SE Spain? (SIAM, SiAR, AEMET, CHS SAIH, ISMN, Mar Menor, TTN)

### Takeaway
Murcia has dense **agrometeorological** ground data (SIAM-IMIDA, about 49–55 stations, plus SiAR, AEMET and the CHS SAIH rain gauges), but **no open in-situ soil-moisture network**. None of the ISMN networks is in Murcia; the closest is the 3-station Valencia Anchor Station (VAS). For a soil-moisture "ground truth", the team will have to build the sensor themselves (Q3) or borrow validation figures from other Spanish sites (Q2).

### Cited Findings
**SIAM (Sistema de Información Agraria de Murcia, IMIDA)**
- The SIAM homepage (fetched 2026-11-13) says the network has **49 automatic stations**: 32 IMIDA, 15 Ministry of Agriculture, 1 UPCT and 1 Ayuntamiento de Mazarrón. Most sit on private farms in irrigated areas. The network was created after the 1979–1985 drought to **estimate reference evapotranspiration (ET0) and crop irrigation needs** — [SIAM homepage](http://siam.imida.es/)
- A 2025 news item puts the count at **55 stations** (counts differ by source and date) — [Infoagro 2025](https://www.infoagro.com/noticias/2025/murcia_cuenta_con_una_red_de_55_estaciones_agrometeorologicas_que_anal.asp)
- Variables: air temperature and relative humidity, wind speed and direction, global radiation, precipitation. Data reach an IMIDA server over GSM/GPRS and are free to consult on siam.imida.es — [datos.gob.es app record "Agroclima CARM"](https://datos.gob.es/es/aplicaciones/agroclima-carm); [iAgua](https://www.iagua.es/noticias/murcia/12/12/09/el-sistema-de-informacion-agrario-de-murcia-amplia-su-oferta-de-servicios-gratuitos-e-incrementa-el-244)
- Web products listed on the homepage: real-time station data, daily / 7-day / **"personalizado" (custom-range)** agrometeorological reports, a **low-temperature (frost) report**, chill-hours reports for fruit growing, and a map viewer at `geoportal.imida.es/siam`. The site is an Oracle APEX app (`siam.imida.es/apex/f?p=101:...`). I found no documented REST API for the time series — [SIAM homepage](http://siam.imida.es/)
- Demo-worthy records on the homepage: TMAXABS 47.10 °C at La Carrichosa (Cieza) on 07/07/2000; TMINABS −17.86 °C at Yecla-Pinillos on 29/01/2006; PREC 91.80 at Santiago de la Ribera (San Javier) on 13/09/2019 04:00 (the Sept-2019 DANA) — [SIAM homepage](http://siam.imida.es/)
- Machine-readable open data: the "Efemérides meteorológicas" dataset (station records since 2000: max daily ET0, max 1-h and 1-day precipitation, absolute Tmax/Tmin, wind…) is served as REST TXT/JSON at `datosabiertos.carm.es/rest-services/services/restFile/ImidaEfemerides.json`. This holds **records/extremes only, not time series** — [datos.gob.es API record](https://datos.gob.es/apidata/catalog/dataset/a14002961-efemerides-meteorologicas-de-la-region-de-murcia1) (tested 2026-11-13, HTTP 200)

**SiAR (Ministry of Agriculture, national irrigation agroclimatic network)**
- More than **500 stations** nationally. A **SiAR API** for programmatic download was announced on 19 Oct 2023, "accessible from the SiAR website itself". Other features: a frost-free-period calculator, net irrigation-need forecasts, and the "Espacio SiAR" viewer that combines stations and satellites — [MAPA press release PDF](https://www.mapa.gob.es/es/prensa/231019apiregadiossiar_tcm30-661910.pdf)
- Temperature and humidity are sampled every 10 min, radiation/precipitation/wind every 10 s. Daily, weekly and monthly records are open; **hourly records require registration** — [datos.gob.es blog on SiAR](https://datos.gob.es/ca/blog/el-sistema-de-informacion-agroclimatica-para-el-regadio-siar)
- My curl to `servicio.mapa.gob.es/websiar/` and `/apisiar/` returned HTTP 404 on 2026-11-13. The URL has moved and I could not locate the API documentation (see Gaps).

**AEMET OpenData**
- The download centre offers "API Key — Solicitar" (request a key) plus general and developer access. A (free) key is needed, which means creating an account. A human teammate has to do that — [AEMET OpenData](https://opendata.aemet.es/centrodedescargas/inicio) (fetched 2026-11-13)

**CHS SAIH (Segura basin hydrological network)**
- The public **iVisor** shows precipitation from the rain-gauge network, river/rambla flow and reservoir levels, updated **every 5 minutes**. Clicking a control point shows its history, which can be exported to Excel. Gauge counts conflict: a CHS press note says >350 rain gauges, iAgua says 162 control points. Real-time data are provisional until reviewed — [CHS press note](https://www.chsegura.es/export/sites/chs/descargas/informaciongeneral/comunicacion/noticias/docsdescarga/NP-CHS-reunion-SAIH_rev.pdf); [iAgua "Nuevo iVisor SAIH"](https://www.iagua.es/blogs/juan-carlos-caballero/nuevo-ivisor-saih-ojos-segura); [SAIH user manual 2009](https://www.miteco.gob.es:443/content/dam/miteco/es/agua/publicaciones/SAIH_-_Manual_de_Usuario_Nov_2009_tcm30-136205.pdf)

**ISMN (International Soil Moisture Network)**
- On the ISMN networks page (fetched 2026-11-13) the Spanish networks are: **REMEDHUS** (24 stations, Duero basin, Castilla y León), **XMS-CAT** (22, Catalonia), **VAS** (3, Valencia Anchor Station) and **IPE** (2, no link). None is in Murcia or Andalucía — [ISMN networks](https://ismn.earth/en/networks/)
- REMEDHUS: Hydra probes at 5 cm logging hourly, about 1,300 km² of semi-arid farmland, part of ISMN since its start. A second network used Inforiego stations in Castilla y León (2012–2014) — [Spanish Journal of Soil Science 2024](https://www.frontierspartnerships.org/journals/spanish-journal-of-soil-science/articles/10.3389/sjss.2024.12839/full); [ISPRS 2015 (SMOS/REMEDHUS)](https://isprs-archives.copernicus.org/articles/XL-7-W3/1183/2015/)
- ISMN data downloads require a free registration (from my prior knowledge; I did not verify on the site this session).

**Mar Menor**
- The regional government runs **8 buoys** that measure temperature, dissolved oxygen, chlorophyll and conductivity at several depths. They feed the IMIDA "Mar Menor digital twin", which also integrates **soil moisture and salinity** conditions and agrometeorological stations. The Observatorio del Mar Menor added control points on farm plots, wells and ponds — [iAgua](https://www.iagua.es/noticias/gobierno-region-murcia/murcia-impulsa-infraestructuras-observacion-biodiversidad-proteger)
- MITECO deployed a separate buoy/sensor network in 6 lagoon areas, run by IEO-CSIC (BELICH reports). The 2023 tender required historical download and third-party access — [MITECO 2023](https://www.miteco.gob.es/en/prensa/ultimas-noticias/2023/03/el_gobierno_centrallicitalaprimerareddeboyasmontessubmarinosysen.html); [BELICH report Oct 2025](https://www.miteco.gob.es/content/dam/miteco/es/ministerio/planes-estrategias/mar-menor/Reporte%20BELICH%20emergencia%20DANA%20151025.pdf)

**The Things Network (LoRaWAN) in Murcia**
- The TTN Murcia community is a "Campaign" (getting started), founded 2016, with 23 members. It reports **~23 online gateways within ~70 km** (from Packet Broker data; gateways with private locations are not counted). No updates have been posted — [TTN Murcia](https://www.thethingsnetwork.org/community/murcia/)
- A Lorca group proposed deploying TTN gateways in Lorca — [TTN forum "TTN Lorca"](https://thethingsnetwork.org/forum/t/ttn-lorca-spain/18644)
- The TTN Mapper API (`api.ttnmapper.org`) returned **HTTP 403 (Cloudflare challenge)** to curl on 2026-11-13, so I could not measure coverage at the venue.

### Inferences
- **SIAM is the best ground source for the demo.** It covers the right region, its ET0 is computed by agronomists, and it has a frost report and a 2019 DANA record. Because there is no API, plan for a one-off manual export (custom report → CSV/Excel) for 1–2 stations near the demo field. Cache it in the repo on Saturday morning.
- For **rain extremes and the DANA/erosion story**, CHS SAIH gauges (5-min data) are the best counterpoint to GPM IMERG (see Q2).
- The soil-moisture ground-truth gap in Murcia is a **real argument for the IoT add-on** (Q3), not a gimmick.
- With ~23 gateways inside 70 km, there is plausibly TTN coverage in Murcia city, but this is unverified for the venue. Use Wi-Fi/MQTT as the default demo path.

### Gaps
- Current SiAR API URL, documentation and whether it needs a key (old URLs return 404).
- Whether any SIAM station measures soil moisture or soil temperature (the homepage lists only atmospheric variables).
- No COSMOS (cosmic-ray neutron) site in Murcia could be confirmed. `cosmos-europe.eu` did not resolve from curl.
- TTN coverage at the venue itself (TTN Mapper blocked automated access).
- Whether IMIDA's digital-twin soil-moisture/salinity data are published openly. Not found.

---

## Q2. How do satellite and ground measurements compare in SE Spain? (the challenge asks to "clarify how satellite observations differ from ground-based measurements")

### Takeaway
The pattern to tell judges: satellites get the **timing** right (good correlation) but miss the **level and the extremes**. SMAP tracks soil-moisture dynamics well but carries a few vol% bias at single fields. IMERG strongly underestimates torrential rain in Spain. ERA5-Land tends to have a cold bias and errors that grow with terrain. Spain-specific temperature figures are thin.

### Cited Findings
**Soil moisture (SMAP and others vs in situ)**
- Irrigated almond orchard, Tarazona de la Mancha (Albacete, semi-arid, 2019–2023, top 10 cm):
  - **SMAP L3_SM_P_E (9 km): R² = 0.64, RMSD = 4.85 vol%, bias = 3.60 vol%**
  - Copernicus SSM (Sentinel-1, 1 km): R² 0.22, RMSD 4.34, bias 0.10
  - Copernicus SWI (1 km): R² 0.36, RMSD 3.79, ubRMSD 3.73, bias 0.66
  - The authors attribute SMAP's deviations partly to its coarse resolution. All products captured the temporal variability.
  - Source: [Sánchez et al., EGU24-11751](https://meetingorganizer.copernicus.org/EGU24/EGU24-11751.html) (conference abstract, the closest site to Murcia with numbers)
- SMAP Level-4 global benchmark: surface ubRMSE **0.038 m³/m³ at 9 km** (0.035 at 36 km), root zone 0.030 m³/m³ — [Reichle et al. 2017 assessment](https://typeset.io/pdf/assessment-of-the-smap-level-4-surface-and-root-zone-soil-5ahmy29q41.pdf). SMAP L2/L3 (R17000) "continues to meet mission requirements" (0.04 m³/m³ target) — [Colliander et al. 2022 via DOAJ](https://doaj.org/article/d5030cc9a9a147d7ba2994436d585a1c)
- REMEDHUS (Duero, semi-arid) work on SMOS shows that time-series agreement is good (R > 0.8) but **spatial agreement with in-situ data is poor**. Downscaled SMOS reached R ≈ 0.55–0.85, ubRMSD ≈ 0.04–0.07 m³/m³ — [USAL repository](https://gredos.usal.es/handle/10366/167260); [core.ac.uk PDF](https://core.ac.uk/download/80864302.pdf)

**Precipitation (GPM IMERG vs gauges)**
- Catalonia, 186 gauges: IMERG Final reduces error versus Early/Late, but rainfall classed as **very heavy and torrential is underestimated by more than 80%**, attributed to missed sub-daily extremes — [Peinó et al., Remote Sensing 14(20):5085](https://mdpi.com/2072-4292/14/20/5085)
- A 10-year Western Mediterranean study found underestimation that **increases with rainfall intensity and finer temporal resolution** — [Remote Sensing 16(3):457](https://mdpi.com/2072-4292/16/3/457); [EGU23-12109](https://meetingorganizer.copernicus.org/EGU23/EGU23-12109.html)
- First Spain-wide validation (Tapiador et al., via search summary): the largest discrepancies come from underestimated orographic rainfall and few gauges in the GPCC calibration. The estimate "improves greatly when at least one rain gauge is available" — [core.ac.uk PDF](https://core.ac.uk/download/326491031.pdf) (full text not opened; attribution from search summary)
- Conflicting detail: one abstract reports IMERG **over**estimates by >20% at flat-area gauges at daily+ scales. Bias depends on terrain and timescale, while extreme-rain underestimation is consistent — [EGU22-2933](https://meetingorganizer.copernicus.org/EGU22/EGU22-2933.html)

**Reanalysis (ERA5-Land vs stations)**
- Precipitation over Spain (1951–2020, vs AEMET grid): Spearman 0.5–0.9, RMSE mostly 2–8 mm/d, depending on region, intensity and orography — [UPV RiuNet](https://riunet.upv.es/handle/10251/204208)
- Soil temperature at 39 Spanish sites (1987–2018): climatology is well represented, but summer soil temperature and some trends are underestimated — [UCM eprints](https://eprints.ucm.es/id/eprint/75037/)
- Air temperature (Alps, not Spain, 159 stations): mean bias **−0.94 °C**, MAE 1.37 °C in the lowest band rising to 2.19 °C at altitude — [EGU26-6475](https://meetingorganizer.copernicus.org/EGU26/EGU26-6475.html)

### Inferences
- Explanation for the UI, in plain words:
  - "Satellites see a 9 km (SMAP) or 10 km (IMERG) square. Your field is a 1–5 ha dot inside it, and irrigated and dry plots are mixed in that square."
  - "Satellites are good at saying *when* soil dries or rain falls, worse at saying *how much*, especially in a DANA cloudburst."
  - "Ground stations are exact but only at one point."
  - The fusion step: anchor the satellite series to a local station or sensor (bias correction), then use the satellite for the spatial pattern and the long history.
- The SMAP bias of +3.6 vol% at an irrigated orchard is plausibly an **irrigation signal / heterogeneity artefact**. In Murcia (drip-irrigated woody crops beside dry rainfed land) the 9 km pixel mixes both. Say so explicitly; it scores on "explain uncertainty".
- **Frost:** ERA5-Land (~9 km) and NASA POWER (~0.5°) cannot resolve cold-air pooling in valley bottoms (Yecla's −17.86 °C record). This argues for SRTM-based frost-pocket mapping plus a local Tmin sensor (Q3).
- Demo opportunity: plot IMERG daily rain vs a SIAM/SAIH gauge for **12–13 Sept 2019 (DANA)**. The underestimation should be visible and lines up with the literature. This is an inference: I did not run it.

### Gaps
- No published SMAP L3 validation numbers specifically for REMEDHUS, VAS or any Murcia site.
- No Spain-specific ERA5-Land 2 m air-temperature bias/RMSE figure. The −0.94 °C is from the Alps.
- No IMERG validation found specifically for the Segura basin or Murcia (the papers found cover Catalonia, the W. Mediterranean and Spain-wide).

---

## Q3. What is the minimum IoT component that adds real value (not a gimmick), and how to demo it without a real field deployment?

### Takeaway
A **single ESP32 node** (capacitive soil-moisture probe plus a soil/air temperature probe) publishing over MQTT (Wi-Fi at the venue; LoRaWAN/TTN as the "production" path). It feeds two real functions: (1) **calibrating the satellite soil-moisture series** to the field, and (2) a **local frost / heat alert** that ERA5-Land/POWER cannot give. For the demo, **replay real SIAM station data as an MQTT stream** and put one physical node on the table, rather than inventing random numbers. Low-cost capacitive sensors need calibration, and salinity matters in Murcia; say so.

### Cited Findings
- Low-cost capacitance (low-frequency) sensors are "much cheaper but more sensitive to confounding effects of **salinity, temperature, soil texture**". In a 10-node LoRaWAN network:
  - Commercial node cost **EUR 185**, gateway **EUR 385**.
  - Range was ~500 m with the stock antenna and ~1,500 m with a 4.5 dBi 868 MHz antenna, in an urban setting without line of sight.
  - Packet drop rose with distance (up to 13.64% at 460 m).
  - Unit-specific standardisation against dielectric liquids gave R² = 0.99 vs measured θ.
  - Source: [Briciu-Burghina et al., Sensors 2022, 22(3):987](https://pmc.ncbi.nlm.nih.gov/articles/PMC8840329)
- Calibration of SEN0193-type low-cost capacitive sensors: 12 sensors × 3 replicas × 5 moisture levels (5–40%). Error varied with moisture level. Properly calibrated sensors can reach high accuracy — [Sensors 2025, PMC11768944](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11768944/)
- The cheap "v1.2" capacitive probe (FA3003-1) **overestimated at 36–46% VWC** in drip irrigation. The study compared pooled vs sensor-specific calibrations — per search summary of [Annals of Tropical Research 2025](https://atr.vsu.edu.ph/article/download/872/851/2756)
- Murcia precedent: a low-cost **LoRa Smart-Agri system for micro-plots (< 0.5 ha) in Pliego** (central Murcia), inside a water users' association's irrigation network that sends field sensor data to the cloud — [Chazarra-Zapata et al., Agronomy 2020, 10(9):1365](https://www.doi.org/10.3390/agronomy10091365) (mdpi.com returned 403 to WebFetch, so author affiliations are not verified)
- CEBAS-CSIC "Citrimad" proof of concept (Fundación Séneca): applying CEBAS's irrigation methodology with **TDR soil-moisture sensors** on commercial citrus farms — [La Verdad via fseneca.es](https://fseneca.es/web/sites/web/files/09-03-24-LaVerdad-Ababol.pdf)
- A LoRaWAN irrigation controller with low-cost, open-source prototypes and a precipitation-probability algorithm (Spain) — [Sánchez-Sutil & Cano-Ortega, Sensors 2021, 21(21):7041](https://www.mdpi.com/1424-8220/21/21/7041)
- TTN Murcia: ~23 online gateways within ~70 km (see Q1) — [TTN Murcia](https://www.thethingsnetwork.org/community/murcia/)
- Official rules:
  - Work may not start before 14 Nov 2026, 09:00.
  - Every source must be cited.
  - SI-tool use must be described.
  - I found no rule against simulated or replayed data.
  - Source: repo summary `context/official-rules.md` quoting the [Space Apps participant FAQ](https://www.spaceappschallenge.org/resources/participant-faqs/)

### Inferences
- **Minimal credible design (≈ 4–6 person-hours for the networks/IoT teammate):**
  - Hardware: ESP32 dev board, capacitive soil-moisture probe (analog), DS18B20 waterproof temperature probe (soil, or air at 1.5 m for frost), optional SHT3x/BME280 for air temperature and humidity.
  - Firmware: read every 5–15 min, publish JSON on MQTT topic `farm/<field_id>/node1` to a broker (Mosquitto on a laptop, or a public test broker for the demo only).
  - LoRaWAN path for the pitch slide: an RFM95/SX1276 or a LoRa32 board → TTN (EU868) → TTN MQTT integration → same backend topic. The backend does not care which radio path the data came from.
  - Bill of materials: a hobby build is tens of euros, vs EUR 185 for the commercial node above. I found no reliable source for exact hobby prices, so state "≈ order of €20–40" as an estimate only.
- **Why it is not a gimmick (the three functions to show):**
  1. **Satellite calibration.** A linear or CDF-matching rescale of SMAP/ERA5-Land soil moisture to the node's (calibrated) readings. The node shows the field-level offset; the satellite keeps the 10-year history. The literature's ~3.6 vol% SMAP bias at an irrigated Spanish orchard shows what the correction is for.
  2. **Frost/heat alert.** Node Tmin below threshold → alert. Compare with the ERA5-Land/POWER cell to show the microclimate gap. Ties to the challenge's "frost risk" and to SIAM's own frost report.
  3. **Bare-field / irrigation event detection.** A soil-moisture spike with no rain on the gauges = an irrigation event. This feeds the water-use priority.
- **Demo without a field:**
  - (a) **Replay** a real SIAM hourly series (temperature, humidity, and rain/ET0, e.g. the Jan-2006 Yecla frost or the Sept-2019 DANA) through MQTT at ×1000 speed, labelled "replayed historical station data".
  - (b) One live node in a pot of soil on the table. Water it during the pitch and the dashboard reacts within seconds.
  - (c) Label clearly any simulated soil-moisture curve as synthetic. Disclosure is what makes it acceptable. The rules require only citation and SI disclosure (inference from the rules summary).
- Mention salinity: irrigation water in the Campo de Cartagena is often saline. Cheap capacitive sensors drift with salinity and temperature, so the tool should show the node as "indicative" until it is calibrated against a gravimetric sample.

### Gaps
- Exact retail prices for ESP32, v1.2 probe and LoRa modules: not sourced.
- Whether venue Wi-Fi allows outbound MQTT (port 1883/8883). Unknown; bring a phone hotspot.
- Affiliations of the Pliego LoRa paper authors (UPCT / UMH / UMU?), and any UMU-specific agri-IoT project. Not verified.

---

## Q4. Which labelled datasets exist for Murcia crops?

### Takeaway
The standout is **EuroCrops v2.0 (JRC, CC BY 4.0)**. It includes **Spain-wide parcel-level declared crops for 2021, 2022 and 2023**, plus a **"stack" file that links each field's crop code across years**, i.e. **observed crop rotations**, very likely including Murcia. That is both a training-label source and an evidence base for "what nearby farmers actually rotate". SIGPAC gives land-use classes for every parcel. ESA WorldCereal gives 10 m cropland and cereal/maize maps. EuroCrops v1 covered only Navarra in Spain.

### Cited Findings
- **EuroCrops v1** (Zenodo, current v11): Spain is present only as **ES/NA (2020)** (`ES_NA_2020_EC21`), with HCAT taxonomy columns (`EC_hcat_n`, `EC_hcat_c`). Licence **CC BY-SA 4.0** — [EuroCrops GitHub](https://github.com/maja601/EuroCrops)
- **EuroCrops v2.0** (Claverie et al., ESSD 18, 4075–4095, 2026): multi-annual, parcel-level, harmonised GSA declarations from **18 paying agencies**, at least three consecutive years including 2021. Overseas regions of Spain are excluded. Spanish NUTS3 gaps noted: **León (2023), Jaén (2021)**. **Spanish crop-name translation accuracy was the lowest: 40.29%**. Geoparquet, EPSG:3035 — [ESSD article](https://essd.copernicus.org/articles/18/4075/2026/essd-18-4075-2026.html)
- JRC FTP listing (fetched 2026-11-13) contents — [JRC EuroCropsV2 FTP](https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/DRLL/EuroCropsV2/); [readme.md](https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/DRLL/EuroCropsV2/readme.md); [copyright.txt](https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/DRLL/EuroCropsV2/copyright.txt)
  - Files: `gpqtv202/es_2021.parquet` (8.7 GB), `es_2022.parquet` (9.4 GB), `es_2023.parquet` (11 GB), `es_stack.parquet` (5.1 GB).
  - Yearly table schema: `cropfield`, `original_code`, `area_ha`, `geom`.
  - Stack table: `cf<YEAR>` (field id) and `c<YEAR>` (crop code) per year.
  - Crop codes map to HCAT via `eurocrops.csv` in the EuroCropsV2 GitHub.
  - Licence **CC BY 4.0**.
- **SIGPAC** (FEGA plus the regions): national parcel/enclosure layer with agricultural land-use classes. Downloads via ATOM, plus OGC API and WMS. A "línea de declaración" layer derives from CAP declarations. Murcia's Consejería is a listed custodian of the declared-crop (GSAA) INSPIRE record — [INSPIRE Geoportal record](https://inspire-geoportal.ec.europa.eu/srv/api/records/87ce5171-d713-4eec-a1f3-2b9dd94cad91)
- **fiboa / Source Cooperative** hosts SIGPAC-derived field boundaries as GeoParquet: national "Spain SIGPAC Field Data" plus regional sets (Andalucía, Castilla y León, Castilla-La Mancha, Valencia, Navarra, Madrid, …). There is **no separate Murcia product**, so Murcia would come from the national set — [source.coop/fiboa](https://source.coop/fiboa) (listing fetched 2026-11-13)
- I found **no open Murcia-specific dataset of per-parcel CAP crop declarations**. Catalonia publishes its DUN declarations openly; Murcia appears not to — per search summary citing [agronewscastillayleon](https://www.agronewscastillayleon.com/?p=203146) and [CARM procedures](https://sede.carm.es/web/procedimiento/133)
- **ESA WorldCereal 2021** (10 m, Sentinel-1/2): temporary cropland, maize and winter/spring cereals, each with a confidence layer. Global temporary-crop validation: **user's accuracy 88.5%, producer's 92.1%**. Accuracy "may vary between locations" depending on reference data. A public **Reference Data Module** holds harmonised in-situ labels — [ESSD WorldCereal paper](https://essd.copernicus.org/preprints/essd-2023-184/essd-2023-184-ATC1.pdf); [CEOS GST](https://ceos.org/gst/agriculture.html); [GEE catalog](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCereal_2021_MODELS_v100?hl=es); [esa-worldcereal.org](https://esa-worldcereal.org/en)
- WorldCereal has its own Presto adaptation repo — [WorldCereal/presto-worldcereal](https://github.com/WorldCereal/presto-worldcereal)
- **LUCAS** (Eurostat land use/cover area-frame survey) is the EU-wide in-situ point survey — [Eurostat LUCAS](https://ec.europa.eu/eurostat/web/lucas) (page reachable; Murcia point counts not checked)
- Prithvi's crop-classification fine-tune uses **US CDL labels (13 classes)**, which do not transfer as labels to Murcia — [HF model card](https://huggingface.co/ibm-nasa-geospatial/Prithvi-EO-1.0-100M-multi-temporal-crop-classification)

### Inferences
- **Murcia inclusion in EuroCrops v2 `es_*` is likely but unverified.** The paper lists only León and Jaén as missing Spanish NUTS3 regions. **First Saturday task for the backend/ML person:** run a DuckDB/GeoPandas bbox query over HTTP range reads (filter by bounding box ≈ lon −2.35…−0.65, lat 37.37…38.75, re-projected to EPSG:3035). Do not download 11 GB.
- If Murcia is present, the stack gives **2021→2022→2023 crop sequences per field**. That makes possible:
  - (i) "Your current rotation" pre-filled from real data.
  - (ii) Statistics of the most common rotations near the field (evidence for the "why suggested" column).
  - (iii) Training labels for a crop-type classifier.
  - Watch out: Spanish crop-name translation is only ~40% accurate, so map `original_code` with care, and limit to ~6–10 classes (cereal, legume, horticulture, citrus, almond/nuts, vineyard, olive, fallow/bare).
- Fallback if Murcia is missing: SIGPAC land-use classes (arable vs citrus vs nuts vs vineyard vs olive) plus WorldCereal cereal masks give coarser but valid labels. Farmer input then supplies the rotation.

### Gaps
- Direct confirmation that Murcia (ES620) parcels are in `es_2021–2023.parquet` (DuckDB not installed here; not queried).
- WorldCereal accuracy for Spain/Murcia specifically.
- How many LUCAS 2018/2022 points fall in Murcia, and whether EUCROPMAP (JRC 10 m EU crop map) is current. Not checked.

---

## Q5. Which ML components are feasible in 36 h (CPU-only plus free Colab/Kaggle), and with what justification?

### Takeaway
Feasible in 36 h: **(2) phenology / bare-soil detection**, **(3) anomaly vs climatology**, **(4) FAO-56 water demand**, **(5) climate-analogue k-NN**, **(6) MCDA ranking with uncertainty**, and **(1) crop-type classification only if built on frozen pretrained embeddings** (Presto/AlphaEarth/TESSERA) with a gradient-boosting or k-NN head. Training a deep model from scratch, or yield ML without local yield labels, is not feasible.

### Cited Findings
- **(1) Crop/bare-soil classification.**
  - Presto has **0.40 M parameters**, needs **0.79 / 2.37 MFLOPs per pixel** (RGB / multispectral) vs ~303 M parameters for ViT-Large models, and is competitive "despite having up to **1000× fewer** trainable parameters".
  - "Fine-tuning Presto took **under 6 minutes on a 2017 MacBook Pro's CPU**" (fuel-moisture task). As a frozen encoder, a **random forest** was trained on its outputs with default scikit-learn settings.
  - Inputs: Sentinel-1, Sentinel-2, ERA5, SRTM, Dynamic World, location; a "full" input is **12 monthly timesteps**.
  - Source: [Tseng et al., arXiv 2304.14065](https://arxiv.org/abs/2304.14065) (PDF text extracted locally); [nasaharvest/presto, MIT](https://github.com/nasaharvest/presto)
- **(2) Phenology / season transitions.** Copernicus **HR-VPP**:
  - 10 m, Europe, **2017–present**, free and open.
  - **Start of season = Plant Phenology Index reaching 25% of season amplitude; end of season = 15%** on green-down. Also season length and total productivity.
  - Access via WEkEO, WMTS, and the CLMS portal (authentication needed).
  - Source: [CLMS product page](https://land.copernicus.eu/api/en/products/vegetation/high-resolution-season-length); [EEA catalogue](https://sdi.eea.europa.eu/catalogue/srv/api/records/c1c46cb2-b02b-4013-aae5-a54a8c018b1e); [WEkEO news](https://wekeo.copernicus.eu/news/clms-releases-hr-vpp-product-to-assess-ecosystems-and-biodiversity)
  - Change-point detection library: [ruptures](https://centre.io/ruptures/)
- **(4) Water demand.** FAO-56 crop-coefficient method (ETc = Kc × ET0) is the standard reference — [FAO Irrigation & Drainage Paper 56](https://www.fao.org/4/x0490e/x0490e00.htm). SIAM was built specifically to estimate ET0 and crop irrigation needs in Murcia — [SIAM](http://siam.imida.es/)
- **(5) Climate analogues.**
  - Bastin et al. 2019 matched 520 cities' 2050 climates (RCP4.5, 3 GCMs, **19 bioclimatic variables**) to present-day cities. 77% of cities' future climate is closer to another existing city's. Cities shift ~1,000 km toward the subtropics, e.g. **Madrid 2050 ≈ Marrakech today** — [PLOS ONE 2019, doi:10.1371/journal.pone.0217592](https://doi.org/10.1371/journal.pone.0217592)
  - NASA **NEX-GDDP-CMIP6**: 0.25° daily, 1950–2100, nine variables from 35 CMIP6 GCMs. Open on AWS (`s3://nex-gddp-cmip6/`, no sign-in; COG bucket too) and on GEE. Licence stated as CC0 (registry) vs CC-BY-SA 4.0 (paper), so check. Number of SSPs differs by source (2 on GEE vs 4) — [AWS registry](https://registry.opendata.aws/nex-gddp-cmip6); [NCCS](https://www.nccs.nasa.gov/services/data-collections/land-based-products/nex-gddp-cmip6); [GEE catalog](https://developers.google.com/earth-engine/datasets/catalog/NASA_GDDP-CMIP6); [Sci. Data paper](https://www.nature.com/articles/s41597-022-01393-4)
  - NASA POWER REST API (no login) for present-day daily climate — [POWER API docs](https://power.larc.nasa.gov/docs/services/api/)
- **(6) Ranking and uncertainty tooling** (all docs reachable 2026-11-13):
  - MCDA (TOPSIS, AHP, etc.): [pymcdm](https://pymcdm.readthedocs.io/)
  - Multi-objective / Pareto: [pymoo](https://pymoo.org/)
  - Conformal prediction intervals: [MAPIE](https://mapie.readthedocs.io/en/stable/)
  - Quantile regression: [scikit-learn example](https://scikit-learn.org/stable/auto_examples/linear_model/plot_quantile_regression.html)
  - The 35-GCM NEX-GDDP ensemble gives a natural **ensemble spread** for future-climate uncertainty — [NCCS](https://www.nccs.nasa.gov/services/data-collections/land-based-products/nex-gddp-cmip6)

### Inferences
Feasibility table (owner = ML specialist unless noted; hours are estimates):

| # | Component | 36 h feasible? | Recommended method | Why / risk |
|---|---|---|---|---|
| 1 | Crop-type / bare-soil classification | **Yes, if frozen embeddings** (~6–10 h incl. data) | AlphaEarth or TESSERA annual embeddings (pre-computed, no inference) **or** Presto on monthly S2 composites → LightGBM/CatBoost/k-NN, labels from EuroCrops v2 Murcia | Labels and Murcia coverage are the risk (Q4). Never train a CNN from scratch. Annual embeddings classify the crop of a year but do **not** give intra-annual bare periods. |
| 2 | Seasonal transitions / bare-field calendar | **Yes** (~4 h) | Sentinel-2/HLS NDVI per field → monthly/dekadal median → Savitzky–Golay smoothing → threshold (NDVI < ~0.2–0.25 = bare) plus 25%/15% amplitude rule mimicking HR-VPP; `ruptures` for change points; **validate against HR-VPP SOSD/EOSD** | Highest value per hour. Directly answers "times when fields are typically bare". |
| 3 | Crop-stress anomaly vs climatology | **Yes** (~3 h) | z-scores per calendar month (NDVI, SMAP, LST, POWER/ERA5-Land) vs 2015/2017–2025 climatology; optionally IsolationForest on a multi-variable vector | Simple and explainable; climatology length limited for S2 (2017+) and SMAP (2015+). |
| 4 | Water demand | **Yes**, FAO-56 baseline (~2 h, backend) | ETc = Kc(stage) × ET0 (SIAM or POWER/ERA5-Land ET0), Kc stages from FAO-56 tables, dates from component 2 | ML is **not** worth it here (no ET ground truth for training). Optionally show ECOSTRESS ET as a satellite cross-check. |
| 4b | Yield | **No** | none | No open field-level yield labels found for Murcia. Listed as a gap/future work. |
| 5 | Climate analogue ("where is Murcia-2050 today?") | **Yes** (~4–6 h) | Build a 19-bioclim (or ~8 agro-relevant: GDD, frost days, Tmax>35 days, annual P, P seasonality, aridity) vector per 0.25° cell; Murcia 2041–2060 from NEX-GDDP-CMIP6 ensemble vs present-day global/Mediterranean cells (1991–2020) → standardise → k-NN (Euclidean/Mahalanobis); report top-5 analogues **per GCM**, so uncertainty = how much the analogue moves across models | Very "NASA-data", strong pitch. Then answer "what grows there now?" (e.g. via WorldCereal or literature) as evidence for drought-tolerant rotation options. |
| 6 | Rotation ranking | **Yes** (~4 h, backend + frontend) | Score each of ≥3 rotations on criteria (water use from #4, N-fixation, soil cover months from #2, erosion from SRTM slope + IMERG extremes, frost/heat risk, market) → farmer-weighted **TOPSIS** (AHP is too fiddly for a UI) + a **Pareto front** plot (water vs income vs soil-cover) | Uncertainty: Monte-Carlo over the criterion values (ranges from the GCM ensemble and data error), then report "rank stability %", e.g. "Rotation B ranks first in 78% of simulations". This is the most judge-readable uncertainty. Conformal/quantile intervals only where a real regression model exists (#1 probabilities via MAPIE). |

### Gaps
- No benchmark of Presto/AlphaEarth/TESSERA accuracy on Murcia or Spanish horticulture/woody crops.
- No CPU runtime figure for Prithvi-EO-2.0-tiny inference (Q6).

---

## Q6. Which pretrained geospatial foundation models are usable on CPU/Colab in Nov 2026 (licence, size, Murcia relevance)?

### Takeaway
For a CPU-only team, the best options are, in order:
1. **Pre-computed embeddings** (Google/DeepMind **AlphaEarth Satellite Embedding**, 64-d, 10 m, annual, CC-BY 4.0; or Cambridge **TESSERA**, 128-d, 10 m, annual, CC0 weights). No model inference at all.
2. **Presto** (0.4 M parameters, MIT, CPU fine-tuning in minutes).

**Prithvi-EO-2.0** (Apache-2.0, 5 M–600 M) is the most "NASA" choice and has a tiny 5 M variant, but its crop fine-tunes are US/CDL-based and its notebooks expect a Colab T4 GPU. Use it only if someone has spare GPU time; mention it in the pitch either way. None of these has a Murcia-specific fine-tune.

### Cited Findings
- **Prithvi-EO-2.0** (NASA/IBM). Hugging Face API, queried 2026-11-13, lists:
  - `Prithvi-EO-2.0-tiny-TL`, `-100M-TL`, `-300M`, `-300M-TL`, `-600M`, `-600M-TL`, `-300M-BurnScars`, `-300M-TL-Sen1Floods11`, plus `Prithvi-EO-1.0-100M-multi-temporal-crop-classification`.
  - All **Apache-2.0** (Prithvi-WxC is CDLA-permissive-2.0).
  - Source: [HF ibm-nasa-geospatial](https://huggingface.co/ibm-nasa-geospatial)
- Prithvi tiny-TL = **5 M parameters**. TL variants add lat/lon and date embeddings. Pre-trained on **HLS V2 (30 m), 4.2 M samples, 6 bands**. The tiny model "is much faster and needs less compute". A multitemporal crop-segmentation notebook runs on Colab ("Choose T4 GPU runtime"). Loads via TerraTorch `BACKBONE_REGISTRY.build("prithvi_eo_v2_tiny_tl", pretrained=True)` — [HF model card Prithvi-EO-2.0-tiny-TL](https://huggingface.co/ibm-nasa-geospatial/Prithvi-EO-2.0-tiny-TL); [TerraTorch](https://github.com/IBM/terratorch)
- Prithvi-EO-2.0 paper benchmarks:
  - US multi-temporal crop segmentation: 600M 50.7 mIoU vs 300M 48.6 vs U-Net 42.6.
  - Sen4Map crop type: weighted F1 76.1 (600M) vs 72.7 ViViT.
  - PASTIS: 37.4 vs U-TAE 36.9 mIoU.
  - Source: [arXiv 2412.02732](https://arxiv.org/abs/2412.02732)
- Prithvi-EO-1.0 crop-classification fine-tune: HLS chips **224×224×18 (6 bands × 3 timesteps)**, **13 CDL classes**, 80 epochs with mmseg. The card warns CDL labels are noisy — [HF model card](https://huggingface.co/ibm-nasa-geospatial/Prithvi-EO-1.0-100M-multi-temporal-crop-classification)
- **Presto**: 0.40 M parameters, CPU fine-tuning < 6 min, 12 monthly steps of S1/S2/ERA5/SRTM, MIT — [arXiv 2304.14065](https://arxiv.org/abs/2304.14065); [GitHub](https://github.com/nasaharvest/presto). TorchGeo hosts weights (`torchgeo/presto`, per HF API search)
- **Galileo** (NASA Harvest, ICML 2025):
  - Multimodal: optical, SAR, elevation, weather, pseudo-labels.
  - **MIT**. Nano weights are in the GitHub repo; other sizes are on HF `nasaharvest/galileo`.
  - The single-file encoder example loads on CPU. Inputs are space-time tensors `[B,H,W,T,bands]`.
  - Source: [GitHub nasaharvest/galileo](https://github.com/nasaharvest/galileo); [arXiv 2502.09356](https://arxiv.org/abs/2502.09356v1); [ICML 2025](https://icml.cc/virtual/2025/47917)
- **AlphaEarth Foundations / Google Satellite Embedding V1 Annual**:
  - 64-d vector per **10 m** pixel, annual; years **2017–2025** per the GCS readme (an older third-party write-up says 2018–2024).
  - **CC-BY 4.0**, with required attribution "The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind".
  - Access: on GEE as `GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL`; on a requester-pays GCS bucket; and as a **community mirror on Source Cooperative** (since Nov 2025, 8192×8192 64-band COGs by UTM zone, "bottom-up" COG orientation caveat).
  - Dataset version 1.1 from 17 Nov 2025.
  - Source: [GEE catalog](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_SATELLITE_EMBEDDING_V1_ANNUAL?hl=zh-tw); [AEF on GCS readme](https://developers.google.com/earth-engine/guides/aef_on_gcs_readme); [source.coop/tge-labs/aef](https://source.coop/tge-labs/aef); [DeepMind blog](https://deepmind.google/discover/blog/alphaearth-foundations-helps-map-our-planet-in-unprecedented-detail/?hl=ja)
- **TESSERA** (Cambridge):
  - Pixel-wise, one year of S1 + S2 compressed into a **128-d** embedding at 10 m. Barlow Twins self-supervision.
  - v2 adds Matryoshka dims (16/32/64/128) and distilled Nano/Small/Medium/Large students. Annual global embeddings **2017–2025**, downloadable with `pip install geotessera`.
  - Weights **CC0-1.0**, library MIT, plus an Acceptable Use Policy.
  - Source: [TESSERA README](https://geotessera-readme.static.hf.space/README.md); [geotessera GitHub](https://github.com/ucam-eo/geotessera); [arXiv 2506.20380](https://arxiv.org/pdf/2506.20380v5)
- Clay and SatMAE: not researched in depth this session. SatMAE (ViT-Large, ~303 M params) is listed in the Presto paper's size table as 1000× bigger than Presto — [arXiv 2304.14065](https://arxiv.org/abs/2304.14065)

### Inferences
- **CPU reality check:**
  - AlphaEarth/TESSERA = zero inference; you just sample vectors per field polygon (seconds to minutes).
  - Presto = millions of pixels per minute on CPU (0.8–2.4 MFLOPs/pixel). A 5 km × 5 km area at 10 m is 250 k pixels, which is trivial.
  - Prithvi tiny (5 M) is CPU-feasible for a few 224×224 chips. 300 M/600 M need Colab GPU.
- The **annual** embeddings (AlphaEarth/TESSERA) suit "which crop / which land use this year", and EuroCrops gives one label per year, so they match. Bare-field timing still needs the monthly NDVI pipeline (Q5 #2).
- Attribution and licence lines for whichever model/embedding is used must go in `submission/` (official rules require licences of third-party materials).
- A good NASA story even when using non-NASA embeddings: "Prithvi (NASA/IBM) was evaluated; we chose Presto (NASA Harvest) for CPU efficiency". Both are NASA-affiliated.

### Gaps
- Galileo nano/tiny parameter counts not found on the pages read.
- Clay v1.5 / later versions: licence, size and CPU speed not verified.
- Whether TESSERA/AlphaEarth tiles for Murcia download quickly (tile sizes, bandwidth at the venue) is untested.

---

## Q7. What is the single most impressive yet feasible ML component for judges?

### Takeaway
**"Rotation fingerprint" of the real field:** field-level crop/bare-soil timeline 2017–2025 from Sentinel-2/HLS. It is built from (a) a monthly NDVI-based **bare-field and season-transition detector**, validated against Copernicus HR-VPP, and (b) a **crop-type classifier on frozen pretrained embeddings** (AlphaEarth or TESSERA annual vectors, or Presto) **trained on real EuroCrops v2 Murcia declarations**. Output: calibrated probabilities (conformal sets via MAPIE) that pre-fill "your current rotation". The climate-analogue k-NN is the runner-up and the best pitch hook.

### Cited Findings
- The challenge explicitly asks the SI to "highlight seasonal transitions, bare-field periods, or times when current crops show increased stress" and to "explain how the model interprets uncertainty" — `context/challenges/06-adapting-farms-with-nasa-data.md` ([challenge page](https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/))
- Real multi-year parcel crop sequences for Spain are openly available (EuroCrops v2 `es_stack.parquet`, CC BY 4.0) — [JRC FTP](https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/DRLL/EuroCropsV2/)
- Pre-computed 10 m annual embeddings remove the need for GPU inference — [GEE Satellite Embedding](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_SATELLITE_EMBEDDING_V1_ANNUAL?hl=zh-tw); [TESSERA](https://geotessera-readme.static.hf.space/README.md)
- Presto, from NASA Harvest, runs fine-tuning on a laptop CPU in minutes — [arXiv 2304.14065](https://arxiv.org/abs/2304.14065)
- HR-VPP gives an independent 10 m phenology reference (SOS/EOS) to validate against — [CLMS](https://land.copernicus.eu/api/en/products/vegetation/high-resolution-season-length)
- Conformal prediction library — [MAPIE](https://mapie.readthedocs.io/en/stable/)

### Inferences
- Why it wins: it hits three judged things at once.
  - **Uses NASA data well**: HLS/Landsat; Presto from NASA Harvest; Prithvi in the comparison.
  - **Answers the challenge's SI bullet literally**: transitions, bare periods, uncertainty.
  - **Makes the farmer story concrete**: "We detected that your field was bare Jul–Oct in 6 of the last 8 years. Here is what a cover crop in that window would change."
- It shows **validation**, which most hackathon teams skip:
  - A held-out accuracy and confusion matrix on Murcia parcels.
  - Agreement of detected SOS with HR-VPP SOSD (e.g. median absolute difference in days).
- Fallback ladder if time runs short:
  - (1) Drop the classifier, keep the NDVI bare-field detector (always feasible).
  - (2) Use k-NN on embeddings instead of a trained model.
  - (3) Let the farmer input the rotation.
- Suggested split:
  - ML person: embeddings + classifier + conformal.
  - Backend: EuroCrops/SIGPAC query, NDVI pipeline, FAO-56.
  - Frontend: timeline strip per year (crop colour + bare months hatched) and rotation comparison cards.
  - IoT person: node + MQTT replay + frost alert (Q3), then help with the climate analogue.

### Gaps
- Unverified: Murcia coverage in EuroCrops v2, and achievable accuracy for Murcia crop classes (horticulture is often multi-cycle within a year, which may confuse annual labels).

---

## Q8. How should LLMs ("SI") be used responsibly in agricultural advice?

### Takeaway
Use the LLM only as a **narrator over numbers computed by the deterministic pipeline**, with **retrieval restricted to curated, local, cited sources** (FAO-56, SIAM, challenge datasets, regional extension guides). Show the evidence for every sentence and refuse dosage or pesticide advice. Recent agri-RAG studies report fewer hallucinations, but the numbers come from the authors' own evaluations. "SI" in the 2026 challenge texts simply means AI.

### Cited Findings
- 2026 terminology: the Space Apps FAQ quotes the **29 Sept 2026 US Executive Order**: "the executive branch shall use the terms 'Super Intelligence' and 'SI' in place of 'Artificial Intelligence' and 'AI'". Submissions **must describe how SI tools were used** — [Space Apps participant FAQ](https://www.spaceappschallenge.org/resources/participant-faqs/) (as transcribed in `context/official-rules.md`)
- **AgriRegion** (Dec 2025): restricts retrieval to verified local extension services with geo-spatial filters. Reports **10–20% fewer hallucinations** than state-of-the-art LLM systems (self-reported) — [arXiv 2512.10114](https://arxiv.org/abs/2512.10114v1)
- **Digital Green DG-EVAL** (2026): separates verified fact retrieval from conversational delivery and evaluates with expert-curated atomic facts. Flags acute risk from wrong dosages or banned pesticide recommendations — [arXiv 2603.03294](https://arxiv.org/html/2603.03294v1)
- WUR prototype (Dec 2025, project report, not peer-reviewed): RAG answers scored **4.1 vs 1.4** (5-point scale) on evidence grounding against non-RAG — [edepot.wur.nl/708809](https://edepot.wur.nl/708809)
- Open models (Llama 3.1, Mistral, Phi-3, Qwen2.5) compared in a RAG framework for agri recommendations — [J. Agricultural Engineering](https://www.agroengineering.org/jae/article/download/1908/1425/14785). A third-party claim that Mistral/Qwen beat GPT-4 on hallucination rates (6.2%/7.1% vs 14.3%) could **not** be verified.
- The challenge itself requires a "supportive tool… that does not replace farmer judgment" and asks for "information gaps" and "risks that would need local review" per strategy — [challenge page](https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/)

### Inferences
- Pattern for the app:
  1. The pipeline computes a **JSON evidence pack** per rotation: numbers, dataset name, URL, resolution, date range, uncertainty.
  2. The LLM writes the "why suggested / benefits / gaps / risks" text **only from that pack**, with an inline citation per sentence.
  3. A validator checks that every number in the text appears in the pack.
  4. Fixed disclaimer plus a "check with your local agronomist / OCA" box.
- Keep the LLM optional: the ranking (Q5 #6) must work without it, so the demo is not hostage to API keys or venue Wi-Fi. Cache generated texts for the demo field.
- In the SI-disclosure field of the submission: list the coding assistants used **and** the runtime LLM, with what it is allowed to do.

### Gaps
- No independent field trials of agri-LLM advice with farmers were found. All results are author-reported benchmarks.

---

## Q9. Data-harmonisation recipe: common grid, temporal aggregation, tools, Google Earth Engine access, pitfalls

### Takeaway
Do not force one raster grid. Use the **field polygon as the analysis unit**:
- 10–30 m data (S2, HLS, embeddings, SRTM): zonal statistics inside the polygon.
- Coarse data (SMAP 9 km, ERA5-Land ~9 km, IMERG 0.1°, POWER 0.5°, NEX-GDDP 0.25°, GRACE basin): value of the containing cell, flagged with its footprint.

Aggregate everything to **monthly** (dekadal for NDVI/phenology). GEE is free for non-commercial student use (Community tier 150 EECU-h/month) and hosts most of the datasets, but it needs a Google Cloud project registration that a human must do.

### Cited Findings
- **GEE non-commercial access** — [GEE noncommercial tiers](https://developers.google.com/earth-engine/guides/noncommercial_tiers); [GEE access guide](https://developers.google.com/earth-engine/guides/access)
  - Since **27 Apr 2026**, every non-commercial project gets a monthly free compute quota.
  - **Community tier = 150 EECU-hours**, "intended for undergraduate students". Contributor tier = 1,000 EECU-h (graduate students and researchers; needs a billing account but no charges).
  - Projects must be verified via a Cloud-console questionnaire (since 26 Sept 2025) and reverified yearly.
  - Using multiple projects to bypass quotas ("quota farming") violates the ToS.
  - An event host can create one project and add trainees.
- GEE hosts:
  - Satellite Embedding — [catalog](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_SATELLITE_EMBEDDING_V1_ANNUAL?hl=zh-tw)
  - NEX-GDDP-CMIP6 — [catalog](https://developers.google.com/earth-engine/datasets/catalog/NASA_GDDP-CMIP6)
  - WorldCereal 2021 — [catalog](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCereal_2021_MODELS_v100?hl=es)
  - Presto's own pre-training tiles were exported from GEE — [presto GitHub](https://github.com/nasaharvest/presto)
- Non-GEE NASA routes:
  - AppEEARS (polygon → CSV/GeoTIFF for MODIS, HLS, ECOSTRESS, SMAP, SRTM; Earthdata Login) — [AppEEARS](https://appeears.earthdatacloud.nasa.gov/); see also `research/field-shift-datasets.md`
  - NASA POWER API (no login) — [POWER API](https://power.larc.nasa.gov/docs/services/api/)
  - NEX-GDDP on AWS without sign-in — [AWS registry](https://registry.opendata.aws/nex-gddp-cmip6)
- Python stack: zonal stats with [rasterstats](https://pythonhosted.org/rasterstats/); raster I/O and reprojection with rioxarray/xarray (the docs URL `corteva.github.io/rioxarray/` returned 404 on 2026-11-13; use the GitHub/PyPI page).
- Scale and sampling facts:
  - Resolution and footprint mismatches: SMAP 9 km vs field — [EGU24-11751](https://meetingorganizer.copernicus.org/EGU24/EGU24-11751.html)
  - IMERG misses sub-daily extremes — [Remote Sensing 14(20):5085](https://mdpi.com/2072-4292/14/20/5085)
  - EuroCrops v2 geometry is in **EPSG:3035** — [JRC readme](https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/DRLL/EuroCropsV2/readme.md)
  - AlphaEarth COGs on Source Cooperative are "bottom-up" — [source.coop/tge-labs/aef](https://source.coop/tge-labs/aef)
  - HR-VPP SOS/EOS thresholds are 25%/15% of amplitude — [CLMS](https://land.copernicus.eu/api/en/products/vegetation/high-resolution-season-length)

### Inferences
- **Recipe (one table, one row per field × month):**
  1. **Unit:** field polygon (from SIGPAC/fiboa or drawn by the user), stored in EPSG:4326 for the UI and EPSG:3035/UTM 30N (EPSG:32630) for area-correct statistics.
  2. **10–30 m layers** (S2 SR with cloud mask, HLS, SRTM slope/aspect, AlphaEarth/TESSERA): median/mean inside a **−10 m buffer**, to avoid edge pixels from roads and neighbours. Record the valid-pixel fraction.
  3. **70 m–1 km** (ECOSTRESS LST/ET, MODIS NDVI 250 m): area-weighted mean. Mark "partially sees neighbours" if the field is < ~4 pixels.
  4. **≥ 9 km** (SMAP, ERA5-Land, IMERG, POWER, NEX-GDDP): the containing cell, with no fake downscaling. Show the cell outline on the map, and anchor the level with SIAM/IoT where available (Q2/Q3).
  5. **GRACE**: Segura basin only, as context ("the aquifer is falling"), never per field.
  6. **Time:** daily → monthly (sum for P and ET; mean for T and SM; counts for frost days Tmin<0 and heat days Tmax>35); NDVI → dekadal median, then smooth; climatology baselines 1991–2020 (POWER/ERA5-Land) and 2015/2017–present for SMAP/S2. Store `n_obs` per month.
  7. **Uncertainty columns** next to every value: footprint (m), source, n_obs, known bias note (e.g. "IMERG underestimates torrential rain >80% in Catalonia study").
- **GEE or not:** the networks/IoT or backend teammate should register a non-commercial GEE Cloud project **today** (account creation is a human action). Community tier (150 EECU-h) is ample for zonal stats on a few fields. Keep a non-GEE path (POWER API, AppEEARS, geotessera, AWS NEX-GDDP) in case registration stalls.
- **Pitfalls checklist:**
  - S2 cloud/shadow masks (SCL / Cloud Score+).
  - HLS L30/S30 band-name differences.
  - Mixed irrigated/rainfed pixels in coarse products.
  - ECOSTRESS overpass times vary, so LST is not comparable across dates without care.
  - NetCDF longitudes 0–360 vs −180–180 (NEX-GDDP).
  - CMIP6 calendars (noleap/360-day) when computing monthly means.
  - UTC vs local time for SIAM hourly data versus satellites.
  - EuroCrops crop-code translation errors in Spain.
  - Cache everything as Parquet/GeoJSON in the repo, so the demo never hits an API.

### Gaps
- No measured EECU cost for the specific zonal-stats jobs. The 150 EECU-h sufficiency is an inference.
- The rioxarray docs URL has moved; current URL not confirmed.
