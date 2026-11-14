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
