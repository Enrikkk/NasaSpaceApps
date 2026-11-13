# Prior art: crop-rotation and agricultural decision-support tools (for "Field Shift", Murcia, Nov 2026)

Scope: tools a judge or farmer in Región de Murcia might compare us to. Researched 2026-11-13. Each tool entry
follows this pattern: who / region | what it does | data | how it presents advice | explainability | price/open | gaps.
"Not verified" means I could not confirm it this session, so it is listed under Gaps rather than invented.

---

## Q1. What exists in Spain / Región de Murcia (public advisory, mandatory records, commercial apps, EU projects)?

### Takeaway
Murcia farmers already get free public **irrigation** advice (SIAM/IMIDA, SiAR/MAPA), **climate alerts** (ClimAlert),
and are being pushed toward **digital record-keeping** (CUE/SIEX). Commercial Spanish apps are mostly
field notebooks for compliance and traceability. **None of the Spanish tools found compares rotation strategies.**
The only Murcia rotation/diversification DSS found is the H2020 Diverfarming "SusDiver" app. It is generic and
predates the newer regulations.

### Cited Findings

**Public advisory (Murcia/Spain)**
- **SIAM (Sistema de Información Agrario de Murcia), IMIDA, CARM.** Free regional agro-met network. Using station
  data and field-derived crop coefficients, it publishes irrigation and fertilisation programmes for citrus, fruit trees and
  vegetables. It also interprets irrigation-water and foliar analyses (relevant because of saline water). Advice
  comes as tables/programmes per crop with no rotation logic. — [iagua 2012](https://www.iagua.es/noticias/murcia/12/12/09/el-sistema-de-informacion-agrario-de-murcia-amplia-su-oferta-de-servicios-gratuitos-e-incrementa-el-244)
- **Agroclima app (IMIDA).** Free app combining SIAM weather data with irrigation programmes by plot and crop. Fed by 52
  stations (other, older sources give 45–50). — [Blueberries Consulting](https://blueberriesconsulting.com/en/una-app-gratuita-del-imida-ofrece-datos-meteorologicos-y-programas-de-riego-segun-parcela-y-cultivo/)
- **ClimAlert (IMIDA + regional Civil Protection, 2023), climalert.imida.es.** Early warning for water-related climate
  risks. Integrates soil-moisture probes, well water-level sensors, agro-met stations and unnamed satellite data.
  Has a simplified farmer version with mobile alerts (wind, rain, drought) for a user-defined zone and helps compute crop
  water needs and irrigation frequency. No crop or rotation advice. Registration is required. — [Agronews CyL, 31 Aug 2023](https://www.agronewscastillayleon.com/murcia-crea-una-plataforma-para-luchar-contra-la-sequia-que-integra-informacion-agroclimatica-de-sensores-y-satelites)
- **SiAR (MAPA, national).** >500 stations: >360 run by the Ministry and >160 by the regions. Measures daily FAO
  Penman-Monteith ET0. Data available by manual download or the API-SIAR service. The SiAR app and the "Espacio SiAR" WebGIS
  combine station data with Landsat 8 / Sentinel-2 time series and compute water needs and irrigation doses for
  104 crops. ET0 is backward-looking (past week). — [MAPA SiAR](https://www.mapa.gob.es/es/desarrollo-rural/temas/gestion-sostenible-regadios/sistema-informacion-agroclimatica-regadio/presentacion.aspx); [MAPA ponencia](https://mapa.gob.es/images/ca/2-ponencia_tcm34-522284.pdf); [UPA Anuario 2025](https://www.upa.es/Anuario2025/115-GARCIA-ET-AL.pdf)
- **CARM precision-ag drone pilot.** Six-band multispectral drone at the Purias demonstration farm (Lorca), run with
  Fundación Alimer and CIFEA Lorca. A demonstration project, not a farmer product. — [iagua](https://www.iagua.es/noticias/gobierno-region-murcia/region-murcia-pone-marcha-proyecto-agricultura-precision-drones-y)

**Mandatory / regulatory systems**
- **SIEX + REA + CUE (Cuaderno Digital de Explotación), RD 1054/2022.** The CUE logs treatments, fertilisation, sowing,
  irrigation, field work and harvests per parcel. A compatible digital CUE can push data to SIEX. It is a
  **record, not an advisor**. For the 2023–2027 CAP period the digital CUE is voluntary except for specific cases
  (phytosanitary, soil nutrition), and keeping a log on paper or digital is still mandatory. The EU committee backed moving
  digital phyto records from 1 Jan 2026 to 1 Jan 2027. The article says CAP 2028–2034 would make it mandatory for holdings of
  >30 ha, >5 ha irrigated or >0.1 ha greenhouse (not yet in official regulation). — [Interempresas, 13 Nov 2025](https://www.interempresas.net/Grandes-cultivos/610490-Cuaderno-Digital-de-Explotacion-en-Espana-(CUE)-mucho-mas-que-un-'excel'-obligatorio.html)
- Castilla-La Mancha's 2026 briefing says the digital CUE is not mandatory until 1/1/2027. Fertiliser and pesticide
  records are mandatory (paper allowed), and a fertilisation plan is needed for some eco-schemes. — [JCCM REA/CUE 2026 PDF](https://apliagri.castillalamancha.es/sites/default/files/2026-02/PRESENTACI%C3%93N_REA_CUE_2026_smd.pdf); [Banco Santander blog](https://www.bancosantander.es/blog/pymes-negocios/siex). Sources disagree on regional details, so verify in the BOE.
- **FaST (EU Farm Sustainability Tool for Nutrients).** Spanish pilots were in Andalucía (IFAPA + PwC France) and
  Castilla y León. v1.0 was released to pilot regions in March 2021. It produces a nutrient-management plan with
  customised fertilisation recommendations. Member States were to supply FaST through CAP strategic plans. The FaST
  Navigator study was published 25 May 2022. — [DESIRA](https://desira2020.agr.unipi.it/2021/05/18/news-farm-sustainability-tool-fast-released/); [Future Farming 2019](https://www.futurefarming.com/Tools-data/Articles/2019/2/New-tool-for-EU-farmers-to-help-manage-nutrients-395592E/); [Agroportal](https://www.agroportal.pt/fast-navigator-study-identifies-models-necessary-to-provide-accurate-advice-on-the-use-of-fertilisers-to-eu-farmers). **Current (2026) Spanish rollout status not confirmed** (see Gaps).
- **CAP Area Monitoring System (Sistema de Monitorización de Superficies).** Uses Copernicus Sentinel signals to check
  declared parcels automatically. Covers 100% of farmland, with field checks on about 5% of applications (2019–2022 figure). The CARM
  signed an agreement for monitoring-based controls in 2021. FEGA Circular 28/2025 governs the 2025 control plan. — [Aragón PAC 2025](https://www.aragon.es/pac-2025/controles-preliminares-administrativos-monitorizacion); [MAPA ponencia](https://mapa.gob.es/images/ca/ponencia1_tcm34-636325.pdf); [CARM Consejo de Gobierno 2021](https://transparencia.carm.es/wres/transparencia/doc/Consejo_Gobierno/2021-06-25/punto_18_monitorizacion.pdf); [Agronews CyL](https://www.agronewscastillayleon.com/plan-nacional-controles-pac)
- **Mar Menor law (Ley 3/2020), rules that directly constrain rotations** (consolidated text):
  Art. 39 encourages rotation and caps a plot at **2 crop cycles/year** (3 for leafy vegetables under 45 days).
  Art. 51.2–51.3 (Zona 1): at most 2 cycles/year, only one of them a "Group 1" (most N-sensitive) crop, and **two
  consecutive Group 1 cycles are banned** (they must alternate with Group 2).
  Art. 51.6: irrigated land left **bare for more than 2 months in winter must get a cover crop** that is ploughed in as green manure.
  Art. 29: 1,500 m band from the shoreline with fertiliser bans and a 170 kg N/ha/yr cap.
  Art. 37.1: 5% of each farm in Zonas 1–2 must be a nutrient-retention surface.
  Art. 39.2/51.5: sowing and harvest dates must go in the farm notebook.
  Chapter V has **no satellite/remote-sensing provision**. Art. 32.2 requires sensor-based soil-moisture monitoring. — [BOE-A-2020-9793 consolidated](https://www.boe.es/buscar/act.php?id=BOE-A-2020-9793). The TSJ Murcia rejected hundreds of farmers' claims to lift the law's limitations. — [TSJ Murcia news](https://www.poderjudicial.es/cgpj/es/Poder-Judicial/Tribunales-Superiores-de-Justicia/TSJ-Region-de-Murcia/Noticias-Judiciales-TSJ-Region-de-Murcia/El-TSJ-de-Murcia-rechaza-la-peticion-de-centenares-de-agricultores-para-dejar-sin-efecto-las-limitaciones-de-la-Ley-del-Mar-Menor). (A search summary also said the Constitutional Court upheld the main restrictions in STC 112/2021 and 126/2023. Not verified against the rulings.)
- **CAP eco-scheme "rotación con especies mejorantes".** Castilla y León cut the share of land that must change crop
  each year to 25% for 2026, and fallow after a legume counts toward it. Provisional FEGA 2026 rates for this
  practice plus direct seeding on irrigated land: €137.46/ha up to 25 ha (€162.46 with multi-year commitment). — [Agronews CyL](https://www.agronewscastillayleon.com/castilla-leon-flexibiliza-ecorregimenes-pac-rotacion-25); [Agronews CyL importes 2026](https://www.agronewscastillayleon.com/ecorregimenes-pac-2026-importes-hectarea-anticipo-75). Murcia-specific parameters not checked.

**Commercial Spanish apps (mostly CUE/field notebooks)**
- **Visualnacert (Valencia).** On the official lists of CUE developers ("Visual cuaderno de campo digital"). Syncs farms from
  REA and outputs the SIEX notebook. Covers treatments, pest monitoring and GlobalGAP compliance. No rotation feature found.
  Paid. — [Asturias list of authorised CUE developers](https://www.asturias.es/documents/d/guest/listado-empresas-autorizadas-desarrollo-cue-comercial-pdf-); [Facilitea dossier](https://www.facilitea.com/on/demandware.static/-/Sites-promocaixa-m-catalog/default/DOSSIERVisual360agrocooperativa.pdf)
- **Agroptima (ISAGRI).** Farm-activity management app on the Basque register of CUE developers. No rotation or SIEX
  detail found. — [Euskadi register](https://www.euskadi.eus/contenidos/registro/reg_cuaderno_explotacion/eu_def/adjuntos/Web_Koaderno_digital_komertzialak_garatzen_dituzten_entitateen_erregistroa.pdf); [softwaredoit](https://www.softwaredoit.es/software-para-agricultura/directorio-proveedores.html)
- **Hispatec (Almería; ERPagro, C3 "Cuaderno de Campo Cooperativo", EFEMIS).** Cooperative-oriented ERP/notebook built with
  Cooperativas Agro-alimentarias. A directory lists a "Rotación" function without saying which product. — [softwaredoit Hispatec](https://www.softwaredoit.es/hispatec/hispatec.html); [Cooperativas Agro-alimentarias](https://agro-alimentarias.coop/docs_download/cooperativas-agro-alimentarias-n-57-el-siex-bajo-control-con-el-cuaderno-de-campo-cooperativo)
- **CXTierra (Grupo Cajamar).** Digital CUE app, presented as improving productivity. — [Interempresas](https://www.interempresas.net/Grandes-cultivos/610490-Cuaderno-Digital-de-Explotacion-en-Espana-(CUE)-mucho-mas-que-un-'excel'-obligatorio.html); [App Store](https://apps.apple.com/es/app/cxtierra/id6447681620?l=en-GB)
- **Hemav (Spain; "Layers").** Merges drone and satellite remote sensing, and its AI produces recommendations for field
  actions (fertilisation, irrigation). Partnered with Azucarera/Agroteo for sugar beet. Offers online training and phone support. No evidence of
  Murcia deployment or rotation planning. — [Agronews CyL](https://www.agronewscastillayleon.com/azucarera-traves-de-agroteo-se-une-hemav-para-lanzar-un-nuevo-proyecto-de-agricultura-de-precision)

**EU research projects with a Murcia link**
- **Diverfarming (H2020, 2017–2022), "SusDiver" DSS.** Free app on Google/Apple stores. Integrates agronomic,
  environmental and economic indicators to tailor diversified cropping systems, low-input practices and machinery.
  The Murcia case study (UPCT, CEBAS-CSIC, Asaja Murcia and others) covered vegetables, mandarin and almond. One trial
  intercropped thyme and caper with rainfed almonds. Project-wide finding: diversification causes no significant farm-level economic
  change, and where it does, the change tends to be positive. — [Diverfarming project page](https://uco.es/investigacion/proyectos/diverfarming/index.php/en/project-2/project-5); [CORDIS](https://www.cordis.europa.eu/article/id/434316-sowing-diversity-reaping-sustainability-why-europe-needs-more-diverfarmers); [Interempresas](https://www.interempresas.net/Horticola/376565-El-proyecto-Diverfarming-presenta-sus-resultados-de-diversificacion-de-cultivos.html)
- **LIFE AgriAdapt (Lake Constance Foundation, Fundación Global Nature (ES), Solagro, EMU).** Farm Vulnerability Tool and
  AgroClimaticZone tool. The webtool has three modules: vulnerability quiz, then yield and climate data, then sustainable
  adaptation measures. 126 pilot farms in EE/DE/FR/ES (the Spanish ones in Castilla y León, not Murcia). Vulnerability is
  scored qualitatively. — [Climate-ADAPT tool](https://climate-adapt.eea.europa.eu/en/metadata/tools/agriadapt-webtool-for-adaptation-of-typical-eu-farming-systems-to-climate-change-awa); [Layman report](https://www.bodensee-stiftung.org/wp-content/uploads/LAYMAN_REPORTagriadapt_ENG_FINAL.pdf)
- **CEBAS-CSIC modelling (academic).** A Univ. Twente MSc thesis done at CEBAS-CSIC (Murcia) modelled rotation plus deficit
  irrigation with the SPHY model and found rotation improved water use. — [UTwente thesis PDF](https://www.utwente.nl/en/et/cem/research/wem/education/msc-thesis/2020/furii.pdf)

### Inferences
- In Murcia the "irrigation advisor" niche is filled by free public tools. A hackathon tool should **consume** SiAR/SIAM
  ET0 (as evidence) rather than compete with them.
- The CUE/SIEX push means farmers will soon have structured parcel histories (crop, sowing and harvest dates). A rotation tool that
  reads or writes those fields fits the farmer's real workflow. This is an inference: no tool found does this for rotations.
- Ley 3/2020 Art. 39/51 rules are **machine-checkable constraints** (cycles/year, no consecutive Group 1 crops, bare
  soil over 2 months in winter). No tool found encodes them.

### Gaps
- Not verified this session: Agricolus (IT, active in ES?), "Agromap", Satellogic (a satellite operator, not a DSS),
  "Plataforma Agroasesor", Bioaggregator, Agrosmart (Brazil), Sensoterra users in Murcia, Telefónica smart-agro
  pilots, UPCT "Smart Agro", SMARTAGRIHUBS, DIVINFOOD, SoildiverAgro, ARISTOTELES. A search for SoildiverAgro + Murcia
  returned nothing relevant.
- Spain's official 2026 FaST implementation (whether the CUE/SIEX or a regional tool is the designated FaST) is not confirmed.
- Murcia's own eco-scheme rotation parameters and the definitions of "Group 1/Group 2" crops (annex of Ley 3/2020) were
  not extracted. Read the BOE annexes before encoding rules.
- No source on SIAM's current station count or on how many Murcia farmers use SIAM/Agroclima.

---

## Q2. Which tools explicitly compare multiple rotation scenarios with trade-offs, and which explain uncertainty?

### Takeaway
Real multi-rotation comparison with trade-offs is **rare**. It exists in **ROTOR** (German, organic-only, password-restricted,
dated) and in academic generators/optimisers (ROTAT, CropRota, MO-MILP, RL). Footprint calculators such as Cool Farm Tool and Fieldprint
run "what-if" practice scenarios but are not rotation planners. Commercial platforms (EOSDA, OneSoil, xarvio) offer rotation
**history/logging**, not comparison. **No tool found communicates uncertainty** of rotation outcomes to farmers.

### Cited Findings
- **ROTOR (ZALF, Germany).** Field-level, long-term planner for **organic** rotations, for farmers and advisors. Users compare
  rotation options on provisioning, N supply (maximising legume N fixation, avoiding leaching) and pest/disease/weed
  control. Restricted access (password from ZALF). Basis: Bachinger & Zander 2007, Eur. J. Agron. — [EU CAP Network practice abstract](https://eu-cap-network.ec.europa.eu/projects/practice-abstracts/rotor-organic-crop-rotation-planner_en); [Orgprints](https://orgprints.org/id/eprint/30580). No recent version found, so it may be dated.
- **ROTAT (Dogliotti, Rossing & van Ittersum, 2003, Agric. Systems).** Generates all rotations from a crop list, then filters out
  agronomically infeasible successions with transparent rules. NL case study. — [record](https://data.zhenzhi.com/details/1/880239192); [CropRota DP citing ROTAT](https://ideas.repec.org/p/zbw/inwedp/dp452009.html)
- **CropRota (BOKU Vienna; Schönhart, Schmid, Schneider).** Optimisation model combining agronomic criteria with observed crop
  mixes. Validated on 579 farms (Mostviertel, AT) with about 10% weighted deviation for the main two-crop sequences. — [IDEAS/RePEc](https://ideas.repec.org/p/zbw/inwedp/dp452009.html); [BOKU PDF](https://boku.ac.at/fileadmin/data/H03000/H73000/H73100/Diskussionspapiere_ab_2004/452009.pdf)
- **Cool Farm Tool (Cool Farm Alliance).** Quantifies on-farm GHG and soil-carbon sequestration, water (irrigation needs,
  blue/green footprint) and biodiversity (Temperate Forest, **Mediterranean** and Semi-Arid biomes). Lets users compare
  alternative practices ("what-if"). Reviewers call it **directional**, not policy-grade. — [coolfarm.org](https://coolfarm.org/?p=22); [Net Zero Compare](https://netzerocompare.com/software/cool-farm-tool); [Farmers Weekly 2025 comparison](https://www.fwi.co.uk/business/business-management/agricultural-transition/4-popular-carbon-calculators-for-farms-compared)
- **Field to Market Fieldprint Platform (US).** 8 sustainability indicators plus EDF's N Balance model. Membership and a data licence
  are required. US commodity supply chains only. — [Fieldprint overview](https://fieldtomarket.org/fieldprint-platform-overview); [API reference](https://support.fieldtomarket.org/knowledge-base/version-5-fieldprint-api-input-reference/)
- **Midwest Cover Crops Council Cover Crop Selector (US/CA).** Farmer picks state/county and goals (erosion control, N
  scavenging, weed suppression, forage) and gets ranked species and seeding windows. Data updated 2025 (MI, IA, MN) and 2026 (WI);
  the WI update shows the whole cash-crop window. A good UX model for "goals, then ranked options", but it covers cover crops, not
  full rotations. — [MSU Extension](https://www.canr.msu.edu/news/michigan-cover-crop-selector-tool-updates); [Iowa State](https://crops.extension.iastate.edu/post/iowa-cover-crop-decision-tool-updated); [UW-Madison](https://cropsandsoils.extension.wisc.edu/wisconsin-cover-crop-selector-tool-updated/)
- **SARE "Crop Rotation on Organic Farms: A Planning Manual".** A paper procedure for rotation planning maps, not software. — [SARE](https://www.sare.org/publications/crop-rotation-on-organic-farms/a-crop-rotation-planning-procedure/)
- **EOSDA Crop Monitoring (EOS Data Analytics).** Claims users "can develop a crop rotation plan" and view per-field rotation
  history (about 5 years) with NDVI trends, to "analyze the field state after each species". The page shows **no scenario
  comparison or recommendation engine** and does not name data sources. Freemium ("Free Pro field"), then sales contact. — [EOSDA crop rotation page](https://eos.com/agriculture/crop-rotation)
- **OneSoil (Belarus-founded, now global).** Free web and Scouting app with satellite NDVI, automatic field-boundary and crop
  detection, notes, weather and "planning crop rotation" (a logging feature). Paid Pro adds VRA, yield analysis and trials. — [OneSoil help](https://help.onesoil.ai/en/articles/5237584-how-the-onesoil-web-and-mobile-apps-differ); [OneSoil freemium blog](https://blog.onesoil.ai/en/onesoil-mob-app-is-moving-to-freemium); [Future Farming](https://futurefarming.com/smart-farming/tools-data/onesoil-a-handy-free-fieldmap-and-scouting-app)
- **xarvio FIELD MANAGER (BASF).** Builds multi-year management zones automatically and uses field history as input to nutrient
  management. No rotation-planning feature found. — [HortiDaily platform study](https://www.hortidaily.com/article/9889394/new-study-offers-a-glimpse-into-differences-between-booming-precision-agriculture-platforms/); [xarvio Field Manager](https://global.xarvio.com/field-manager)
- **Cropwise (Syngenta).** Owned by Syngenta. No rotation-comparison feature found. — [CB Insights](https://www.cbinsights.com/company/cropwise-operations/alternatives-competitors)
- **Agmatix (ICL-owned).** Platform for standardising trial data (more than 50,000 trials, 17M measurements, 70+ crops) with the "Leafy" GenAI
  assistant on Amazon Bedrock. Blogs about rotation, but **no dedicated rotation product** found. — [SIAL newsroom](https://newsroom.sialparis.com/?p=4098); [AWS blog](https://aws.amazon.com/blogs/machine-learning/generative-ai-for-agriculture-how-agmatix-is-improving-agriculture-with-amazon-bedrock)
- **Diverfarming SusDiver** (see Q1) integrates agronomic, environmental and economic indicators for diversified systems, the nearest
  Spanish analogue to multi-criteria comparison. — [Diverfarming](https://uco.es/investigacion/proyectos/diverfarming/index.php/en/project-2/project-5)
- **Defunct / shrinking:** Corteva discontinued **Granular Agronomy** and sold **Granular Business** to Traction Ag (2022); only
  Granular Insights remains. — [Farm Progress, Nov 2022](https://www.farmprogress.com/farm-business/traction-ag-accounting-startup-acquires-granular-business). Bayer **discontinued Climate FieldView in the UK**
  but says the global commitment is unchanged. — [Bayer UK FieldView](https://cropscience.bayer.co.uk/our-products/fieldview/)

### Inferences
- The "compare 3+ rotations side-by-side, with why/benefit/risk" UX requested by the challenge is essentially **unoccupied in
  farmer-facing products**. ROTOR is closest but is organic-only, German, gated and old.
- Uncertainty display (ranges, confidence, "what we don't know") is absent everywhere we looked. Showing it honestly is
  a credible differentiator, and it also matches the challenge's explicit "gaps and risks" requirement.

### Gaps
- Not verified: AHDB (UK) rotation planner (none found), PLANETE, any "USDA Crop Rotation Tool", FarmLogs/Bushel status,
  Climate FieldView's rotation features, Cropwise Planning features. I did not open the product pages.
- No independent evaluation of EOSDA or OneSoil rotation features. These are vendor claims.

---

## Q3. Which tools use NASA / Copernicus data, and how?

### Takeaway
Satellite use is overwhelmingly **Sentinel-2 / Landsat NDVI for monitoring** (vegetation status, boundaries, crop type, CAP compliance)
and **ET-based water use**. NASA data powers mostly US tools (OpenET, Crop-CASMA, NASA Harvest). **No tool found uses satellite
data as evidence for comparing rotations** (e.g., detecting bare-soil months or legume cover in the current rotation).

### Cited Findings
- **Spain CAP Area Monitoring System** checks 100% of declared parcels with Sentinel signals. — [Aragón PAC](https://www.aragon.es/pac-2025/controles-preliminares-administrativos-monitorizacion); [MAPA](https://mapa.gob.es/images/ca/ponencia1_tcm34-636325.pdf)
- **Espacio SiAR** overlays Landsat 8 / Sentinel-2 time series on station ET0 to give irrigation doses for 104 crops. — [MAPA ponencia](https://mapa.gob.es/images/ca/2-ponencia_tcm34-522284.pdf)
- **ClimAlert (IMIDA)** combines satellites (type unstated) with probes and stations. — [Agronews CyL](https://www.agronewscastillayleon.com/murcia-crea-una-plataforma-para-luchar-contra-la-sequia-que-integra-informacion-agroclimatica-de-sensores-y-satelites)
- **OneSoil / EOSDA / xarvio:** satellite NDVI, boundaries, multi-year zones (see Q2).
- **OpenET (NASA, USGS, DRI, CSUMB and others).** Field-scale satellite ET, expanded to all 48 contiguous US states (Dec 2025). **US only.** No field
  boundaries in the East Coast expansion. — [Maven's Notebook, Dec 2025](https://mavensnotebook.com/2025/12/17/openet-expands-satellite-based-water-use-data-across-48-states-providing-critical-information-to-farmers-and-water-managers-across-the-nation); [DRI](https://dri.edu/?p=1383625)
- **NASA Applied Sciences** lists producer tools: NASA Harvest precision nutrient-management tools, OpenET, Crop-CASMA. All NASA data
  is open. — [NASA Applied Sciences – Food Security & Agriculture](https://appliedsciences.nasa.gov/what-we-do/food-security-agriculture)
- **NASA Harvest OpenMapFlow** (rapid ML crop maps from EO). GitHub repo not archived, last push 2024-11-21. — [GitHub nasaharvest/openmapflow](https://github.com/nasaharvest/openmapflow)
- **Microsoft FarmVibes.AI.** Open-source multi-modal geospatial ML for agriculture. **Active**: not archived, last push
  2026-11-03 (GitHub API checked 2026-11-13). — [GitHub microsoft/farmvibes-ai](https://github.com/microsoft/farmvibes-ai); [Microsoft launch](https://news.microsoft.com/source/features/ai/microsoft-open-sources-its-farm-of-the-future-toolkit/)
- **Google AMED API (Jul 2025, India).** ML on satellite imagery giving field-level crop type, field size, and sowing and harvest dates,
  with 3 years of history and roughly fortnightly refresh. India only. — [Google India blog](https://blog.google/intl/en-in/company-news/new-milestones-in-our-journey-to-build-inclusive-and-helpful-ai-for-india/); [IASgyan summary](https://www.iasgyan.in/daily-current-affairs/google-launches-agricultural-monitoring-and-event-detection-amed)
- **Ley 3/2020 Chapter V has no remote-sensing provision.** Compliance relies on notebooks and on-farm sensors. — [BOE](https://www.boe.es/buscar/act.php?id=BOE-A-2020-9793)

### Inferences
- AMED shows that "sowing and harvest dates per field from satellite" is a recognised product. Doing the equivalent for a Murcia parcel
  with HLS (NASA Harvest Landsat-Sentinel) NDVI, to **reconstruct the current rotation and flag bare-soil months**,
  is technically feasible in a hackathon and unseen in Spanish tools.
- Positioning NASA data as **evidence for a decision** (rotation choice), not as a map to look at, separates us from
  NDVI dashboards.

### Gaps
- Did not verify whether any Spanish commercial app uses NASA products (HLS, SMAP, GPM, ECOSTRESS) rather than Sentinel only.
- OpenET has no European coverage. No European equivalent (e.g., Copernicus-based ET for Murcia) was researched here.

---

## Q4. LLM / AI farm advisors (2025–2026): what exists and how do they ground answers?

### Takeaway
Production farm LLMs (Farmer.Chat, KissanAI Dhenu, Agmatix Leafy) are **Q&A assistants grounded in curated text or trial
data**, focused on the Global South or agronomists. They answer questions. **None found generates or compares multi-year
rotations**, and the research literature on LLM rotation advice is thin. Best-practice grounding is RAG over an approved
knowledge base plus fact-level evaluation.

### Cited Findings
- **Farmer.Chat (Digital Green).** RAG over an approved knowledge base. "RAG accuracy" (faithfulness and relevance) is scored by an
  LLM-as-judge on a 0/1 scale. Reported 20k+ farmers and 340k queries in a year (2024). — [Hugging Face case study](https://www.huggingface.co/blog/digital-green-llm-judge); [Digital Green tech blog](https://medium.com/digitalgreen-techblog/under-the-hood-of-farmer-chat-journey-to-an-optimised-production-ready-rag-powered-chatbot-589bf5716e27)
- Digital Green's 2026 paper proposes separating **fact retrieval from response delivery** and evaluating with **DG-EVAL**
  (atomic facts checked against expert-curated ground truth: recall, precision, contradiction). A fine-tuned small model matched
  frontier-model factual quality at lower cost. It cites 1.5M queries across 4 countries. — [arXiv 2603.03294](https://arxiv.org/html/2603.03294)
- **KissanAI "Dhenu".** Agri LLMs (Dhenu 1.0, about 7B parameters, English/Hindi; Dhenu Llama 3 8B on Hugging Face). Voice-first assistant in 9–10 Indian
  languages, aimed at low-literacy users. UNDP partnership (Jan 2025) for a climate-resilience co-pilot. — [AIM: Dhenu Llama 3](https://analyticsindiamag.com/kissanai-releases-dhenu-llama-3-an-indic-llm-for-farmers/); [AIM: UNDP](https://analyticsindiamag.com/kissanai-partners-with-undp-to-launch-copilot-for-farmers/)
- **Agmatix "Leafy".** GenAI assistant over standardised field-trial data (Amazon Bedrock). Reports 3x analysis throughput. — [AWS blog](https://aws.amazon.com/blogs/machine-learning/generative-ai-for-agriculture-how-agmatix-is-improving-agriculture-with-amazon-bedrock)
- **Academic explainable crop advisors.** "RAGCrop" pairs a crop-prediction model (80+ features) with LIME feature attributions
  and a RAG LLM that turns them into natural-language explanations (single-season crop choice, not rotation). — [SEU JICT PDF](https://www.seu.ac.lk/jict/publication\vl03sp\1-8%20RAGCrop%20Intelligent%20Crop.pdf). "Agri-SAGE: Simulation-Grounded Multi-Agent LLM for Context-Aware Agricultural Advisory Generation" (2026 preprint; title only seen). — [takara summary](https://tldr.takara.ai/p/2607.00454)
- UW-Madison Extension: multimodal LLMs can give farmers location-specific advice "from crop rotation decisions to
  market timing" (overview, not validated). — [UW Extension](https://farms.extension.wisc.edu/articles/large-language-models-a-powerful-new-tool-for-wisconsin-agriculture)
- **Google AMED** (see Q3) is EO-derived structured data that LLM apps can call. **FarmVibes.AI** (see Q3) is an open geospatial ML
  toolkit that can serve as an engine.

### Inferences
- Pattern to borrow: a **deterministic engine computes the scores, and the LLM only explains them**, citing each number's source
  (DG-EVAL-style "every claim traceable to a fact"). This avoids hallucinated agronomy and is easy to show to judges.
- A Spanish, plain-language, optionally voice explanation layer (KissanAI-style) suits "farmers with limited technical skills". Few
  European tools do this.

### Gaps
- Not verified: "Google AgriBenchmark"/AMIE-for-agriculture, specific "AgriLLM" papers, any Spanish-language farm LLM
  (e.g., from MAPA, Cajamar or cooperatives). The search found none for rotation planning.

---

## Q5. Past NASA Space Apps agriculture projects: what won and why?

### Takeaway
Agriculture appears among global winners but **not as a classic dashboard**. The 2025 agriculture winner was an educational **game**
(Art & Technology award). The winners pattern rewards specific named NASA datasets, a clear story, a working demo, and honest
AI-use and limits sections. 2024 had an EO-for-agriculture challenge, but I could not confirm an agriculture global winner.

### Cited Findings
- 2025: 10 global winners chosen from 11,500+ submissions. **Zumorroda-X** (Cairo) won Art & Technology on "NASA Farm Navigators" with
  pixel-style mini-games where players are farmers adapting to heat waves and floods. **Twisters** (Monterrey) won Best Use of
  Technology with "SkySense" (NASA POWER + Open-Meteo + Gemini assistant for weather-risk windows). **QUEÑARIS** (Arequipa) won Local
  Impact with EO/phenology, AI and drones for water-related reforestation. — [NASA 2025 winners announcement](https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-announces-2025-international-space-apps-challenge-global-winners/); repo file `context/past-winners-2025.md` (captured from [Space Apps global winners](https://www.spaceappschallenge.org/2025/awards/global-winners/))
- Winning pages share a one-paragraph summary, a demo video, a working link, an explicit "Use of AI" disclosure, and itemised NASA
  datasets (e.g., POWER, DONKI, GeneLab OSD-288) central to the story, plus stated limits and future work. — repo `context/past-winners-2025.md`
- 2024: 9,996 submissions; global winners picked by executive judges from 40 global finalists. Challenge "Leveraging Earth
  Observation Data for Informed Agricultural Decision-Making". Meteomatics reports "Ometeotl: Crop Connect" as a **2024 global
  nominee** in agriculture. — [NASA 2024 winners](https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-international-space-apps-challenge-announces-2024-global-winners/); [Meteomatics](https://meteomatics.com/en/news/ometeotl-crop-connect)

### Inferences
- With at least 4 Murcia teams on the same challenge, the local podium will likely go to whoever ties NASA data to a **specific local
  story** (Mar Menor, drought, Segura basin) with a working end-to-end demo. A generic NDVI and chatbot product is the expected baseline.

### Gaps
- 2024 agriculture global winner and 2023 agriculture winners not confirmed (the official 2024 winners page could not be fully read and a third-party
  list was garbled). Global finalist/nominee lists for 2025 agriculture challenges were not opened.

---

## Q6. Academic approaches the ML teammate could borrow

### Takeaway
Three borrowable patterns: (1) **rule-filtered rotation generation** (ROTAT style: enumerate, then filter by agronomic rules);
(2) **multi-objective MILP / Pareto front** (income vs diversity vs N or water); (3) **RL over successor-crop matrices**,
preferably the **tabular, explainable** variant. For 36 hours, (1) plus a simple weighted or Pareto scoring is realistic. (3) is a stretch.

### Cited Findings
- **Dury et al. 2012 review** (Agron. Sustain. Dev.): more than 120 references. Most models optimise a **single monetary criterion** rather
  than multiple criteria, and treat cropping-plan decisions as **static** (once per year or rotation). — [record](https://data.zhenzhi.com/details/1/866585742)
- **Pontes et al. 2024 (Agricultural Systems), "Multi-objective models for crop rotation planning problems".** Four multi-objective
  MILP models (maximise net income, crop diversity and land use). Reported +60% crop diversity for <5% net-return loss. — [Bohrium record](https://www.bohrium.com/paper-details/multi-objective-models-for-crop-rotation-planning-problems/1039281237635629068-1360)
- **Fenz et al. 2023 (Computers & Electronics in Agriculture), "AI- and data-driven crop rotation planning".** DQN agent over
  **successor-crop suitability matrices** and crop attributes (contribution margin, N demand). Experts judged most generated
  sequences realistic. — [TU Wien repositum](https://repositum.tuwien.at/handle/20.500.12708/188009); [PDF](https://publications.sba-research.org/publications/2023%20-%20Fenz%20-%20AI-%20and%20data-driven%20crop%20rotati_Stefan%20Fenz.pdf)
- **Goldenits et al. 2024 (preprint, EGU24).** Tabular RL matches deep RL on 5–7-step rotations, is more robust to perturbed
  rewards, and stays **explainable**. — [Preprints.org](https://www.preprints.org/manuscript/202410.2391/v1); [EGU24 abstract](https://meetingorganizer.copernicus.org/EGU24/EGU24-9018.html)
- **CropRota** weights generated rotations by **observed** regional crop mixes, a realism prior. — [IDEAS](https://ideas.repec.org/p/zbw/inwedp/dp452009.html)
- **Dong & Liu review** (Advances in Resources Research) covers multi-objective optimisation, RL and scenario analysis for rotations. — [J-STAGE](https://www.jstage.jst.go.jp/article/arr/6/4/6_3489/_article/-char/en)
- **AquaCrop (FAO).** Free crop-water productivity model. **Single-crop, field-scale**, so rotations must be chained crop by crop.
  Python port: AquaCrop-OSPy. — [IICA AquaCrop](https://aguayagricultura.iica.int/en/tecnologias-1/aquacrop); [ULiège chapter](https://orbi.uliege.be/bitstream/2268/341305/1/Chapter_17%20AquaCrop.pdf)

### Inferences
- A successor-crop matrix for Murcia's main crops (lettuce, broccoli, melon, artichoke, cereal, legume, cover) plus Ley 3/2020
  constraints (Q1) gives a small, explainable generator. Scoring can then be Pareto (water, N risk, income, eco-scheme €), and an
  LLM explains it. This combines ROTAT, MO-MILP and the "engine computes, LLM explains" pattern.

### Gaps
- DSSAT and APSIM were not researched this session (well-known crop-model engines, but setup cost in 36 hours is likely high;
  not verified). No paper found that validates rotation optimisation specifically for Murcia's intensive vegetable systems.

---

## Q7. What do farmers in Spain actually use, and what complaints/gaps are reported?

### Takeaway
Spanish farmers' digital tools are dominated by **compliance notebooks (CUE/SIEX), cooperative ERPs and free public irrigation
advice**. Complaints centre on **bureaucratic fragmentation, connectivity, training and support**, not on missing analytics.
A new tool must be **simpler than what they have**, work offline or with little data, and reduce paperwork rather than add to it.

### Cited Findings
- CUE/SIEX pain points: each autonomous community has its own portal, keys, formats and deadlines. Portals fail at peak campaign times.
  Interoperability is "more theoretical than practical". The holder stays legally liable for data entered by technicians or software.
  Poor rural connectivity and no offline mode make some software unusable. Training is lacking and some workers resist tablets.
  Overlapping treatment, fertilisation and CAP rules confuse farmers about the correct format. Support is limited to PDF manuals or unresponsive hotlines. — [Interempresas, 13 Nov 2025](https://www.interempresas.net/Grandes-cultivos/610490-Cuaderno-Digital-de-Explotacion-en-Espana-(CUE)-mucho-mas-que-un-'excel'-obligatorio.html)
- Spain has about 900,000 mostly small farms, and the **complexity and cost** of traditional systems has been a historic barrier. Only SaaS/modular
  offers are opening access (commercial source, treat with caution). — [Portal ERP](https://portalerp.com/es/noticia/del-surco-al-dato-el-erp-en-la-digitalizacion-del-campo-espanol)
- Connectivity: a UPC European survey (147 responses, 2025–2026) found digitalisation outpacing rural communications
  infrastructure, even in "accessible" rural areas. — [Interempresas](https://www.interempresas.net/Agricola/649359-Agricultura-de-Precision-tenemos-suficiente-cobertura.html)
- Diverfarming's Murcia-area follow-up: producers prefer incentives that embed crop diversification in the **producer
  organisations' operational programmes**. — [UPCT portal](https://portalinvestigacion.upct.es/documentos/66e47f555364794065fafe81)

### Inferences
- Farmers will trust a tool that **speaks their regulatory language** (Mar Menor zones, eco-scheme %, notebook dates) and is
  delivered through their **cooperative or technician**, more than a standalone app.
- The design should be "one parcel, one screen, 3 cards" and work from a cached demo. Venue Wi-Fi and rural connectivity are both risks.

### Gaps
- No quantitative Spanish/Murcian farmer survey on DSS usability or language was found. The MAPA Digitalisation Observatory survey and
  the AgriTech SUDOE diagnosis (CONETIC, 31 Jan 2026) exist, but their results were not retrieved: [MAPA Observatorio](https://www.mapa.gob.es/es/prensa/ultimas-noticias/detalle_noticias/el-observatorio-de-la-digitalizaci-n-en-el-sector-agroalimentario-lanza-una-encuesta-online-para-conocer-el-grado-de-adopci-n-de-nuevas-tecnolog-as-digitales-en-la-producci-n-primaria-y-la-industria/7a7ad991-6a8e-45c5-a577-acae30c68eeb); [INTIA/AgriTech PDF](https://www.intiasa.es/sites/default/files/assets/files/Experimentacion/ProyectosID/E1.1.1%20Diagnosis%20of%20the%20Level%20of%20Digitalization%20of%20Small%20Agricultural%20Enterprises_ES_REV_Final.pdf)
- No usage numbers for Murcia-specific apps (SIAM/Agroclima/ClimAlert).
- A search summary claimed that "Informe Cátedra Datagri 2025" puts Spain above 90% agri-tech adoption vs 78% EU average. The
  primary source was not identified or opened, so do not cite it without checking.

---

## Q8. Synthesis: what is commoditised, what is rare, and what would make a judge say "I haven't seen this before"?

### Takeaway
**Commoditised:** NDVI maps, field boundaries, crop-type detection, weather/ET0 irrigation advice, digital field notebooks, generic
farm chatbots. **Rare or absent:** side-by-side rotation comparison with trade-offs, uncertainty shown to the farmer,
climate-shift-aware rotations, **regulation-aware rotations (Ley 3/2020 Mar Menor and CAP eco-schemes)**, and satellite
evidence of the *current* rotation's weak points (bare-soil months). That second list is where to differentiate.

### Cited Findings (evidence for the classification)
- NDVI, boundaries and rotation **logging** are free in OneSoil and EOSDA. — [OneSoil](https://help.onesoil.ai/en/articles/5237584-how-the-onesoil-web-and-mobile-apps-differ); [EOSDA](https://eos.com/agriculture/crop-rotation)
- Irrigation/ET0 advice is free from public bodies (SiAR 500+ stations with API; SIAM/Agroclima). — [MAPA SiAR](https://www.mapa.gob.es/es/desarrollo-rural/temas/gestion-sostenible-regadios/sistema-informacion-agroclimatica-regadio/presentacion.aspx); [Blueberries Consulting](https://blueberriesconsulting.com/en/una-app-gratuita-del-imida-ofrece-datos-meteorologicos-y-programas-de-riego-segun-parcela-y-cultivo/)
- Digital notebooks are a crowded, regulated market (official developer lists). — [Asturias CUE list](https://www.asturias.es/documents/d/guest/listado-empresas-autorizadas-desarrollo-cue-comercial-pdf-)
- Rotation trade-off comparison exists only in ROTOR (gated, organic, DE) and academic models. — [EU CAP Network](https://eu-cap-network.ec.europa.eu/projects/practice-abstracts/rotor-organic-crop-rotation-planner_en); [Pontes 2024](https://www.bohrium.com/paper-details/multi-objective-models-for-crop-rotation-planning-problems/1039281237635629068-1360)
- Climate adaptation tools assess **vulnerability**, not rotation choice (LIFE AgriAdapt). — [Climate-ADAPT](https://climate-adapt.eea.europa.eu/en/metadata/tools/agriadapt-webtool-for-adaptation-of-typical-eu-farming-systems-to-climate-change-awa)
- Ley 3/2020 contains crisp rotation rules (2 cycles/yr, no consecutive Group 1 crops in Zona 1, winter cover crop if bare soil lasts over 2 months,
  170 kg N/ha in the 1,500 m band, 5% retention surface) and **no satellite control provision**. — [BOE](https://www.boe.es/buscar/act.php?id=BOE-A-2020-9793)
- Eco-scheme rotation thresholds and €/ha are public and change yearly (e.g., 25% rotation in CyL 2026; €137–162/ha irrigated). — [Agronews CyL](https://www.agronewscastillayleon.com/castilla-leon-flexibiliza-ecorregimenes-pac-rotacion-25); [Agronews CyL importes](https://www.agronewscastillayleon.com/ecorregimenes-pac-2026-importes-hectarea-anticipo-75)
- Best-practice LLM grounding is "retrieve facts, then deliver" with fact-level checks. — [arXiv 2603.03294](https://arxiv.org/html/2603.03294)

### Inferences: concrete differentiation opportunities for a 36-hour build (ranked by wow per hour)
1. **"Satellite rotation X-ray" of the current rotation.** Reconstruct the parcel's last 2–3 years from HLS/Sentinel-2 NDVI
   (green vs bare periods) and auto-flag **bare-soil windows over 2 months in autumn/winter**, linking them to nitrate leaching and
   DANA runoff toward the Mar Menor and to Art. 51.6. No tool found does this. It turns NASA data into *evidence* about the farmer's own practice.
2. **Regulation-aware rotation check.** Each candidate rotation gets a green/amber/red "legal & eco-scheme" badge with the article
   cited (cycles/yr, consecutive Group 1 crops, cover crop, N cap) and an estimate of eco-scheme €/ha gained or lost. Judges from
   Murcia will recognise Mar Menor instantly, and other teams are unlikely to read the BOE.
3. **Uncertainty-first comparison cards.** For each of 3+ rotations (current, plus 2 alternatives) show benefit, risk, evidence (dataset +
   link) and a **confidence level / range**. Use ranges from multiple climate sources (e.g., NASA POWER history vs NEX-GDDP-CMIP6
   2050) and say explicitly "what we don't know". Nobody in the prior art does this, and the challenge asks for "gaps and risks".
4. **Climate-shift aware ranking.** Re-score the same rotations under the parcel's 2040–2050 climate (heat days, ET0, rainfall). A
   "your field in 2050 looks like X today" climate analogue makes it tangible. AgriAdapt does vulnerability, not rotation re-ranking.
5. **"Engine computes, LLM explains" in plain Spanish (optional voice).** A rule/Pareto engine (ROTAT + MO-MILP inspired) produces numbers,
   and the LLM only paraphrases them with citations, so it never invents agronomy. This is a DG-EVAL-style guardrail you can demo
   ("every sentence links to a fact").
6. **Notebook-ready output.** Export the chosen rotation as the sowing and harvest dates and fertilisation entries the CUE/SIEX and Ley 3/2020
   Art. 39.2 require. This reduces paperwork, which is the main reported pain point.
- Avoid leading with an NDVI map or a generic chatbot. That is the baseline other Murcia teams (and OneSoil/EOSDA for free) will show.

### Gaps
- Not verified that the other 4 Murcia teams are not doing similar things. Monitor their public project pages on submission.
- HLS/Sentinel-2 bare-soil detection accuracy in Murcia's plastic-mulch and greenhouse landscapes is untested. Risk of false "bare" flags
  under plastic should be stated as a limitation.
- Exact "Group 1 / Group 2" crop lists and Zona 1 / Zona 2 boundaries need extracting from the Ley 3/2020 annexes and CARM GIS
  before building the legal checker.
