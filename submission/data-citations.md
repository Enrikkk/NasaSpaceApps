# Data and sources cited (add every source actually used; licenses required for non-NASA items)

## NASA
- NASA POWER (temperature, rain via IMERG, radiation): https://power.larc.nasa.gov/
- GPM IMERG: https://gpm.nasa.gov/data
- HLS / Landsat / MODIS vegetation indices (NDVI): https://lpdaac.usgs.gov/ , https://earthexplorer.usgs.gov/
- SMAP soil moisture: https://www.earthdata.nasa.gov/data/platforms/space-based-platforms/smap
- SRTM elevation: https://www.earthdata.nasa.gov/data/instruments/srtm
- (optional) ECOSTRESS: https://ecostress.jpl.nasa.gov/data

## Space agency partners and other data (name, URL, license)
- ESA Copernicus Sentinel-2 / CDSE; HRL Croplands: https://dataspace.copernicus.eu/
- ISRIC SoilGrids: https://soilgrids.org/
- SIGPAC / FEGA declared crop, SIAM-IMIDA stations, MAPA/ESAM prices, CREM areas, Ley 3/2020 Mar Menor
- See `research/field-shift-datasets.md` for exact endpoints; confirm each license before submitting.


## T-021 — snapshot 519849b (Arturo / Enrique)

Tables integrated by Arturo from the official-data snapshot prepared by Enrique. See `app/data/tables/sources.csv` and `manifest.json` for full provenance. Copyright statements below do not constitute verified reuse permission. FAO/IMIDA/secondary rights review remains pending before public redistribution.

- **EUR-HICP** — prc_hicp_aind. Source: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_aind?format=JSON&lang=en&geo=ES&coicop=CP00&unit=INX_A_AVG&sinceTimePeriod=1999. Retrieved: 2026-11-14. Rights as recorded: Eurostat, CC BY 4.0 (https://ec.europa.eu/eurostat/about-us/policies/copyright). Notes: Spain HICP all items, 2015=100, deflator.
- **EUR-PRICE** — apri_ap_crpouta. Source: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/apri_ap_crpouta?format=JSON&lang=en&geo=ES&sinceTimePeriod=2000&currency=EUR. Retrieved: 2026-11-14. Rights as recorded: Eurostat, CC BY 4.0 (https://ec.europa.eu/eurostat/about-us/policies/copyright). Notes: first-stage selling price EUR/100 kg, Spain, annual; broccoli = cauliflower proxy.
- **EUR-AREA** — apro_cpsh1. Source: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/apro_cpsh1?format=JSON&lang=en&geo=ES&sinceTimePeriod=1999. Retrieved: 2026-11-14. Rights as recorded: Eurostat, CC BY 4.0 (https://ec.europa.eu/eurostat/about-us/policies/copyright). Notes: area (kha), harvested production (kt), yield (t/ha), Spain, annual.
- **NASA-POWER-DAILY** — POWER daily point AG. Source: https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,T2M_MAX,T2M_MIN,T2MDEW,RH2M,WS2M,ALLSKY_SFC_SW_DWN,CLRSKY_SFC_SW_DWN,PRECTOTCORR,PS,GWETROOT&community=AG&latitude=37.7383&longitude=-0.98838&start=20050101&end=20241231&format=JSON&time-standard=UTC. Retrieved: 2026-11-14. Rights as recorded: NASA POWER, public domain (https://power.larc.nasa.gov/docs/referencing/). Notes: ~0.5 deg cell; 7305 days 2005-2024; 0 missing values.
- **F56-T11** — FAO-56 Table 11 (stage lengths). Source: https://www.fao.org/4/x0490e/x0490e0b.htm. Retrieved: 2026-11-14. Rights as recorded: FAO, (c) FAO 1998; cite: Allen et al. 1998, FAO Irrigation and Drainage Paper 56. Notes: transcribed from HTML.
- **F56-T12** — FAO-56 Table 12 (single crop coefficients Kc, max height). Source: https://www.fao.org/4/x0490e/x0490e0b.htm. Retrieved: 2026-11-14. Rights as recorded: FAO, (c) FAO 1998; cite: Allen et al. 1998, FAO-56. Notes: transcribed from HTML; footnote digits stripped (e.g. 1.152 = 1.15 + note 2).
- **F29-T4** — FAO-29 Table 4 (crop tolerance and yield potential vs ECe/ECw). Source: https://www.fao.org/4/t0234e/T0234E03.htm. Retrieved: 2026-11-14. Rights as recorded: FAO, (c) FAO 1985; cite: Ayers & Westcot 1985, FAO Irrigation and Drainage Paper 29 Rev.1. Notes: transcribed from HTML; slope derived = 100/(ECe0%-ECe100%).
- **F29-T6** — FAO-29 relative salt tolerance of agricultural crops. Source: https://www.fao.org/4/t0234e/T0234E03.htm. Retrieved: 2026-11-14. Rights as recorded: FAO, (c) FAO 1985; Ayers & Westcot 1985. Notes: class per crop; 'Artichoke' there is Helianthus tuberosus.
- **RES-F29** — research_notes/field-shift-predictive-models (secondary). Source: research/predictive-model-research.md. Retrieved: 2026-11-14. Rights as recorded: team research notes. Notes: value seen in a secondary source; verify in a primary table.
- **IMIDA-HORT2020** — García García J. (IMIDA) 2020, Estructura de costes de las orientaciones productivas agrícolas de la Región de Murcia: horticultura al aire libre y bajo invernadero (MAPA Observatorio). Source: https://www.mapa.gob.es/dam/mapa/contenido/alimentacion/servicios/observatorio-de-precios-de-los-alimentos/nueva-estructura-oca-2024/estudios-de-costes-y-otros-estudios-de-interes/estudios-regionales/murcia/estructuradecostesdelasorientacionesproductivasagricolasdelaregiondemurciahorticulturaalairelibreybajo.pdf. Retrieved: 2026-11-14. Rights as recorded: MAPA/IMIDA publication; cite source (no explicit open licence found). Notes: PDF 138 pp read with pdftotext; TLS via FNMT G2R root verified against system AC RAIZ FNMT-RCM.
- **IMIDA-CIT2018** — García García J. (IMIDA) 2018, Estructura de costes ...: frutales de hueso y cítricos (MAPA Observatorio). Source: https://www.mapa.gob.es/dam/mapa/contenido/alimentacion/servicios/observatorio-de-precios-de-los-alimentos/nueva-estructura-oca-2024/estudios-de-costes-y-otros-estudios-de-interes/estudios-regionales/murcia/estructuradecostesdelasorientacionesproductivasagricolasdelaregiondemurciafrutalesdehuesoycitricos.pdf. Retrieved: 2026-11-14. Rights as recorded: MAPA/IMIDA publication; cite source (no explicit open licence found). Notes: PDF 138 pp read with pdftotext.


### T-021 update: 6cd6d8e + taxonomic supplement

- **SIAM-TP91**: SIAM-IMIDA Informe Agrometeorologico Personalizado (diario); http://siam.imida.es/apex/f?p=101:46; retrieved 2026-11-14; rights recorded: SIAM-IMIDA, CARM: cite source (no explicit open licence found). station TP91; days per year 2005:169/365 2006:360/365 2007:362/365 2008:359/366 2009:360/365 2010:363/365 2011:362/365 2012:365/366 2013:365/365 2014:365/365 2015:365/365 2016:366/366 2017:365/365 2018:365/365 2019:365/365 2020:366/366 2021:364/365 2022:357/365 2023:365/365 2024:366/366. Rights review remains pending where no open permission is verified.
- **F56-T22**: FAO-56 Table 22 (max effective rooting depth Zr, depletion fraction p); https://www.fao.org/4/x0490e/x0490e0e.htm; retrieved 2026-11-14; rights recorded: FAO, cite source (Allen et al. 1998, FAO Irrigation and Drainage Paper 56). 8 demo crops. Rights review remains pending where no open permission is verified.
- **UC-FAMILIES**: University of California Cooperative Extension: Vegetable Gardening Handbook, p.13; https://www.ucanr.edu/sites/default/files/2017-11/274540.pdf; retrieved 2026-11-14; rights recorded: Copyright / reuse terms pending review; factual taxonomic attribution only. Botanical family table; no cultivation recommendations transferred from California. Rights review remains pending where no open permission is verified.
- **ECO-VETCH**: FAO Ecocrop Vicia sativa ssp. sativa; https://ecocrop.apps.fao.org/ecocrop/srv/en/cropView?id=238003; retrieved 2026-11-14; rights recorded: Copyright / reuse terms pending review; factual taxonomic attribution only. Leguminosae normalized to Fabaceae. Rights review remains pending where no open permission is verified.
- **ECO-LEMON**: FAO Ecocrop Citrus limon; https://ecocrop.apps.fao.org/ecocrop/srv/en/cropView?id=714; retrieved 2026-11-14; rights recorded: Copyright / reuse terms pending review; factual taxonomic attribution only. Rutaceae. Rights review remains pending where no open permission is verified.

### T-021 update 8b3a214 — calendar, HICP and ECREA candidates

- CARM/IMIDA, Incorporación alcachofa: https://sede.carm.es/documentos/205/7.2.%20Incorporaci%C3%B3n%20alcachofa.pdf — calendar from Enrique snapshot, planting Jul–Aug; scaled FAO phases are derived B. No explicit open licence verified; rights review pending.
- MAPA ECREA Cereales 2021: https://www.mapa.gob.es/dam/mapa/contenido/ministerio/servicios/servicios-de-informacion/analisis-y-prospectiva/ecrea/estudios-de-costes-explotaciones-agricolas/2021/cereales.pdf — pages 1–2, national barley by water regime.
- MAPA ECREA Proteaginosas y forrajeros 2020: https://www.mapa.gob.es/dam/mapa/contenido/ministerio/servicios/servicios-de-informacion/analisis-y-prospectiva/ecrea/estudios-de-costes-explotaciones-agricolas/2020/cultivos_proteaginosos_y_forrajeros.pdf — page 13, grouped peas/broadbeans irrigated.
Both ECREA PDF footers explicitly permit use with attribution to origin; no named standard licence asserted. Facts transcribed as confidence B proxy candidates; native 2020/2021 monetary bases retained. Not cover-vetch costs. HICP source and CC BY 4.0 citation above remain applicable; Spain annual index now included through 2025.

### T-021 thermal evidence review (2026-11-14)

Original factual summaries and bibliographic references in `app/data/tables/threshold-evidence.md`; no source articles, illustrations or editorial tables redistributed. These are research evidence, not validated daily crop-loss parameters. No numerical t100 is activated.

- Alharbi et al. (2021), faba bean field frost: https://doi.org/10.3390/plants10091925 — CC BY 4.0 verified in article footer, https://creativecommons.org/licenses/by/4.0/.
- Giménez-Berenguer et al. (2023), Blanca de Tudela artichoke frost in Orihuela: https://doi.org/10.3390/antiox12111960 — CC BY 4.0 verified in Europe PMC full-text XML. Own summary; no figure reproduced.
- Lee et al. (2023), lettuce heat/meristem: https://doi.org/10.1186/s12870-023-04101-5 — CC BY 4.0 verified under Rights and permissions.
- Dong et al. (2022), common vetch cold acclimation: https://doi.org/10.1186/s12864-022-09039-w — CC BY 4.0 verified under Rights and permissions.
- Okumuş et al. (2025), Vicia germination temperatures: https://doi.org/10.3390/pr13061845 — CC BY 4.0 verified in article footer; does not establish lethal heat limits.
- Shirdelmoghanloo et al. (2022), barley grain filling: https://doi.org/10.3389/fpls.2022.858652 — CC BY verified in article Copyright section.

Bibliographic review only, no copied material or active calibrated dataset: UC ANR 8100 https://class.ucanr.edu/sites/default/files/2025-03/UC%20ANR%20Publication%208100.pdf (copyright UC, no open licence verified); UMass broccoli https://www.umass.edu/agriculture-food-environment/ht/vegetable/fact-sheets/broccoli-summer-heat (no open licence verified); Bishop et al. https://doi.org/10.1111/jac.12172 (open access labelled, exact licence pending); Chen et al. https://doi.org/10.1007/s00122-009-1079-1 (abstract only, licence pending); Björkman/Pearson https://doi.org/10.1093/jxb/49.318.101 (original abstract only, OUP copyright); Maestro/Alvarez https://doi.org/10.1016/0304-4238(88)90051-9 (abstract only, licence pending); Schrader https://doi.org/10.17660/ActaHortic.2005.681.24 (abstract only, licence pending); NSW DPI Eureka SL https://www.dpi.nsw.gov.au/__data/assets/pdf_file/0015/1206150/Eureka-SL-lemon.pdf (copyright/reuse not verified); FAO frost chapter https://www.fao.org/4/y7223e/y7223e0a.htm and ECOCROP data sheets 1313/815/847/238003 (reuse not verified). Rights clearance is required before incorporating external material beyond these original attributed research summaries.

### T-021 — MAPA annual snapshot (bus #139, Arturo)

MAPA, Índices y Precios Percibidos Agrarios: https://www.mapa.gob.es/es/estadistica/temas/estadisticas-agrarias/economia/precios-percibidos-pagados/precios-percibidos-por-los-agricultores-y-ganaderos. Downloaded 2026-11-14 with verified FNMT TLS. `mapa_prices.csv` transcribes 60 annual-column observations, national generic lettuce/melon/artichoke, 2005–2024, EUR/100 kg; explicit product proxies. Exact workbook URLs, sheet/cell references, original modification metadata and SHA-256 in `app/data/tables/mapa_manifest.json`; derived real-2015 columns use the already cited Eurostat Spain HICP.

Reuse permission read directly at https://www.mapa.gob.es/es/atencion-al-ciudadano/aviso-legal: attribution required, update/reuse metadata retained, third-party rights excluded, Ley 37/2007; not a Creative Commons licence. Source records `MAPA-PER-2005/2015/2020/2024` in tables/sources.csv. Original workbook notes retained; prices are bulk at buyer warehouse, harvest-cost inclusion not verified. No assertion of a regional or cultivar-specific price, no piece/weight conversion, no independent cross-source validation claimed.
