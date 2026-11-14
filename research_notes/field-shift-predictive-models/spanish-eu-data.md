# Spanish / EU ground-truth and economic datasets for Campo de Cartagena (Field Shift, Space Apps 2026)

Research date: 2026-11-14. Method note: "VERIFIED" means I actually fetched the URL or downloaded/queried the data from this machine on that date. "SEARCH-ONLY" means I only saw it in a search snippet or an aggregator and did not open the primary page. "BLOCKED" means the site could not be opened from this machine. Environment trap: **every `mapa.gob.es` / `servicio.mapa.gob.es` page failed TLS verification here (curl `ssl_verify_result=19`, WebFetch "self signed certificate in certificate chain")**, as did `inspire-geoportal.ec.europa.eu` (DNS) and `siam.imida.es` (connection refused from the fetch tool). So MAPA pages (ESYRCE, Anuario, price series, RECAN, cost PDFs) are NOT verified by visiting; a teammate on a normal browser should open them. I did not bypass certificate checks.

---

## 1. Parcels and declared crop (SIGPAC / FEGA / Catastro)

### Takeaway
The single best ground-truth find is the **FEGA "Cultivo declarado SIGC" layer**: free, no login, CC BY 4.0, per-parcel-polygon declared crop code plus irrigated/rain-fed flag, for the 2025 campaign, downloadable per municipality (Cartagena zip is 6.6 MB) or queryable live via an OGC API. It is the closest Spanish analogue to USDA CDL, at parcel level. Caveats: crop codes are numeric and I could not find the code-to-name dictionary, and ~41% of Cartagena polygons have no crop code.

### Cited Findings
- FEGA ATOM service index lists datasets: Recintos SIGPAC 2026 and 2025, Elementos del paisaje 2026 and 2025, and **Cultivo declarado SIGC de 2025**; use is "libre y gratuito" if FEGA is credited as author; updated 2026-01-26 — [FEGA ATOM index (VERIFIED)](https://www.fega.gob.es/atom/es.fega.sigpac.xml)
- Cultivo declarado 2025 feed offers GPKG and SHP zips, CRS EPSG:4258 (ETRS89) — [FEGA ATOM cd_2025 feed (VERIFIED)](https://www.fega.gob.es/atom/es.fega.sigpac.cd.2025.xml)
- Files are a plain Apache directory listing, one folder per province, one zip per municipality, e.g. `https://www.fega.gob.es/atom/2025/cd_2025/30%20-%20MURCIA/30016_cd_2025_20250110_gpkg.zip` (INE code 30016 = Cartagena; 6.6 MB zip, 13 MB GPKG). No login, no form. Province 30 folder has files for municipality codes 30001 onward (listing viewed; I did not check every code) — [directory listing (VERIFIED)](https://www.fega.gob.es/atom/2025/cd_2025/30%20-%20MURCIA/)
- I downloaded and opened the Cartagena GPKG. Layer `cultivo_declarado`, SRS 4258, 13,936 polygons, all `exp_ano` = 2025. Columns: `provincia, municipio, poligono, parcela, recinto, dn_surface` (m2), `exp_num` (holding id), `parc_producto` (integer crop code), `parc_sistexp` (`R` = regadío, `S` = secano), `parc_supcult` (cultivated m2), `parc_ayudasol`, `cultsecun_producto` (secondary crop code), `tipo_aprovecha` — [my own inspection of the downloaded GPKG (VERIFIED)](https://www.fega.gob.es/atom/2025/cd_2025/30%20-%20MURCIA/30016_cd_2025_20250110_gpkg.zip)
- In that file: 5,722 of 13,936 polygons have `parc_producto` NULL (and 5,720 NULL `parc_sistexp`); among the rest, R = 5,398 polygons / 8,343 ha total polygon area, S = 2,818 polygons / 2,986 ha. Top irrigated codes by cultivated area: 99 (~1,593 ha), 207 (~1,315 ha), 153 (~1,239 ha), 20 (~849 ha), 155 (~509 ha), 206 (~399 ha); top rain-fed: 104 (~1,039 ha), 62 (~553 ha), 20, 1 — [my own query of the GPKG (VERIFIED)](https://www.fega.gob.es/atom/2025/cd_2025/30%20-%20MURCIA/30016_cd_2025_20250110_gpkg.zip). `cultsecun_producto` is populated for ~1,300 polygons (most common 155, 154, 158, 189), which suggests double-cropping (vegetable rotations) is recorded.
- **Crop code dictionary NOT found.** The FEGA SIGPAC document list has layer information sheets (Fichas 2026), usage tables and municipality code equivalences, but no product-code table surfaced — [FEGA documents list (VERIFIED)](https://www.fega.gob.es/es/el-fega/documentos-fega/documentos-campanas-clasificadas-por-actividad/actividad/SIGPAC); the HVD catalogue entry also links no code table — [datos.gob.es record (VERIFIED)](https://datos.gob.es/es/catalogo/e0dat0002-cultivo-declarado-del-sistema-integrado-de-gestion-y-control-espana)
- Live API: OGC API Features at `https://sigpac-hubcloud.es/ogcapi` with collections `recintos`, `cultivo_declarado`, `elementos_paisaje_area/linea/punto`; GeoJSON, CRS84 or EPSG:4258; supports `bbox` and `limit`. I queried `.../collections/cultivo_declarado/items?f=json&limit=1&bbox=-0.98,37.62,-0.95,37.65` and got a Cartagena polygon with `parc_producto: 20, parc_sistexp: "R"` — [OGC API (VERIFIED)](https://sigpac-hubcloud.es/ogcapi/collections?f=json), [queryables (VERIFIED)](https://sigpac-hubcloud.es/ogcapi/collections/cultivo_declarado/queryables?f=json)
- Licence: Recintos, Elementos del paisaje and Línea de declaración (cultivo declarado) are High-Value Datasets under CC BY 4.0; other layers fall under a FEGA distribution agreement. Legal terms PDFs: [Términos de uso HVD](https://www.fega.gob.es/orig/pdfs/Terminos_de_uso_de_informacion_de_alto_valor_del_SIGC.pdf), [Acuerdo de distribución](https://www.fega.gob.es/orig/pdfs/240801_MESA_SGC_Acuerdo_Distribucion_Datos_SIGC_fdo.pdf) (PDFs not opened) — [FEGA SIGPAC page (VERIFIED)](https://www.fega.gob.es/es/pepac-2023-2027/sistemas-gestion-y-control/sigpac); CC BY 4.0 also stated at [datos.gob.es (VERIFIED)](https://datos.gob.es/es/catalogo/e0dat0002-cultivo-declarado-del-sistema-integrado-de-gestion-y-control-espana)
- Other SIGPAC entry points: national viewer https://sigpac.mapa.gob.es/fega/visor/, WMS https://sigpac-hubcloud.es/wms?request=getcapabilities&service=wms (service description page https://sigpac-hubcloud.es/html/wms/descServicio.html) — [FEGA SIGPAC page (VERIFIED)](https://www.fega.gob.es/es/pepac-2023-2027/sistemas-gestion-y-control/sigpac). One search summary says FEGA forbids programmatic access to the SIGPAC database from code via the viewer (SEARCH-ONLY, [datos.gob.es via search](https://datos.gob.es/en/catalogo/e05024401-sistema-de-informacion-geografica-de-parcelas-agricolas-sigpac)); the ATOM files and OGC API are the sanctioned routes.
- FEGA publishes an INE-vs-Catastro municipality code equivalence Excel (2026): https://www.fega.gob.es/sites/default/files/files/document/RELACION_MUNICIPIOS_RUSECTOR_AGREGADO_ZONA_C2026.xlsx and "Tabla resumen del SIGPAC por usos y CCAA 2026" https://www.fega.gob.es/sites/default/files/files/document/TABLA_RESUMEN_X_USOS_Y_X_CCAA_2026_VR2.xlsx; layer info sheet PDF https://www.fega.gob.es/sites/default/files/files/document/260204-AD-Ficha_Visor_SIGPAC_2026.pdf — [FEGA documents list (VERIFIED as links; files not opened)](https://www.fega.gob.es/es/el-fega/documentos-fega/documentos-campanas-clasificadas-por-actividad/actividad/SIGPAC)
- Catastro parcels (INSPIRE WFS 2.0.0): `https://ovc.catastro.meh.es/INSPIRE/wfsCP.aspx?service=wfs&version=2.0.0&request=GetCapabilities` works, abstract "Spanish INSPIRE Download Service - Cadastral Parcels", Fees "No conditions apply". A working bbox query: `...wfsCP.aspx?service=wfs&version=2.0.0&request=GetFeature&typenames=cp:CadastralParcel&bbox=37.62,-0.98,37.623,-0.977&srsname=urn:ogc:def:crs:EPSG::4326` returned 13 GML parcels with area (`areaValue`, m2) and geometry in the right place (axis order lat,lon). The stored-query form I first tried (`STOREDQUERY_ID=GetFeatureByBox`) failed ("Unknown STOREDQUERIE_ID parameter" — Catastro's own spelling). Catastro municipality codes differ from INE (Cartagena parcels start `51016...`), hence the FEGA equivalence table — [Catastro WFS (VERIFIED)](https://ovc.catastro.meh.es/INSPIRE/wfsCP.aspx?service=wfs&version=2.0.0&request=GetCapabilities), [Catastro INSPIRE hub (VERIFIED)](https://www.catastro.hacienda.gob.es/webinspire/index.html). Catastro has NO crop information on this service; it is geometry/area only. I did not check bbox size limits.

### Inferences
- Ground truth for "what do farmers actually grow here, irrigated or not" = FEGA cultivo declarado GPKGs for the Campo de Cartagena municipalities (Cartagena 30016 confirmed; verify codes for Torre-Pacheco, Fuente Álamo, San Javier, Los Alcázares, Murcia from the FEGA/INE tables). Download size is tiny (a few MB each), so this is hackathon-feasible today.
- 41% null crop codes in Cartagena likely means polygons with no PAC declaration (or non-agricultural use, forest, fallow, pasture), not a data error, but I did not verify this. Weight analyses by polygons with non-null `parc_producto`.
- The declared layer is a single campaign year (2025). A multi-year time series would require the 2024/2023 versions of the ATOM service (I only saw 2025 for this layer; Recintos exists for 2025 and 2026). Whether older cultivo declarado years exist is unknown.
- Declared crop is a PAC subsidy declaration: it under-represents farmers who do not apply for PAC aid. Likely a bias, not verified for this area.

### Gaps
- Numeric product code to crop name table (needed to identify lettuce/broccoli/melon/artichoke/citrus/almond). Possible sources not checked: Murcia SGA manual product table at sede.carm.es/sga-manuales (a search result referenced a "Código Producto" field), FEGA layer info sheet PDF, or cross-checking codes against Murcia municipality statistics. Quick workaround: inspect parcels in the SIGPAC viewer and match codes by eye.
- Whether earlier years (2020–2024) of cultivo declarado are downloadable.
- Murcia regional land-use maps (CARM/SIOSE-Murcia) and Región de Murcia open "declaración" data: not checked.
- SIOSE: not checked.

---

## 2. Crop-type maps (WorldCereal, EuroCrops, CLMS HRL Crop Types, Corine)

### Takeaway
WorldCereal 2021 is of limited use here (no vegetable/citrus classes; irrigation only for maize and winter cereals). EuroCrops v11 does include "whole of Spain" (ES_2023, 9.8 GB), which is almost certainly derived from SIGPAC declarations, so for this area it is redundant with the FEGA layer and much bigger. The Copernicus CLMS HRL Crop Types 10 m raster is a plausible satellite-derived full-coverage product, but I could not verify classes, access or licence.

### Cited Findings
- WorldCereal 2021 v100 on Zenodo (dataset record 10.5281/zenodo.7875105; the ESSD paper cites 10.5281/zenodo.7875104, which is the other record), CC BY 4.0, 10 m, year 2021 only, 236.9 GB total in ZIPs per AEZ. Products: annual temporary crops (classification + confidence), maize (main and second season), spring cereals, winter cereals, active cropland and irrigation maps (irrigation only for maize main, maize second, winter cereals; AEZs lacking thermal Landsat data had no irrigation product). Plus `WorldCereal_AEZ.geojson` outlines. Direct download from Zenodo (`zenodo.org/records/7875105/files/<name>?download=1`); the page does not mention Terrascope or Spain specifically — [Zenodo record (VERIFIED via WebFetch)](https://zenodo.org/records/7875104)
- Paper: temporary-crop extent validated at user's/producer's accuracy 88.5 % / 92.1 % globally; irrigation product described as conservative — [Van Tricht et al. 2023 ESSD](https://essd.copernicus.org/articles/15/5491/2023/) (SEARCH-ONLY summary; paper not opened)
- My direct `curl` to the Zenodo API returned 403 "unusual traffic" from this network, so Zenodo may block automated clients; WebFetch worked for record pages.
- EuroCrops: Zenodo record 6866846, v11 (Nov 2024), CC BY-SA 4.0, 19 countries including Spain. Changelog: "v11: Added all of Spain, Finland, Ireland, Wallonia". Spain files: `ES_2023.zip` (9.8 GB) + `es_2023.csv` mapping, and a Navarra-style `ES_NA_2020.zip` (468 MB) + `es_ne_2021.csv`. Maps declared crops to HCAT3 hierarchy. Page does not state regional coverage or Murcia explicitly — [Zenodo record (VERIFIED via WebFetch)](https://zenodo.org/records/6866846)
- CLMS HRL Croplands "Crop Types" 10 m yearly raster, Europe, from reference year 2017; sensors Sentinel-2/-1, AgERA5; EEA catalogue says download requires authentication via WEkEO; WEkEO dataset id `clms_vlcc_crop-types_europe_10m_yearly_v1` — [CLMS product page (SEARCH-ONLY)](https://land.copernicus.eu/en/products/high-resolution-layer-croplands/crop-types-2017-raster-10-m-europe-yearly), [WEkEO transition guide (SEARCH-ONLY)](https://help.wekeo.eu/en/articles/16540530-hrl-datasets-transition-how-to-access-croplands-grasslands-and-tree-cover-data). My WebFetch of the CLMS product page returned HTTP 404 (URL may have moved), so class list and licence are unconfirmed.

### Inferences
- If the app needs a vegetable-vs-tree-crop-vs-fallow map for the whole Campo, rasterised FEGA declared crop is better ground truth than WorldCereal. WorldCereal only helps as an independent "active cropland / temporary crop" mask.
- EuroCrops adds a harmonised crop taxonomy (HCAT3) and its `es_2023.csv` is probably the quickest route to a code-to-name mapping, if you can download that 30 kB CSV from Zenodo. This is an inference; I did not open the CSV.

### Gaps
- CLMS HRL Crop Types class list, licence and whether it needs a login (likely a free WEkEO/CLMS account; unconfirmed).
- Whether EuroCrops ES_2023 covers Murcia (probable but unconfirmed) and its crop-code mapping.
- Corine Land Cover and SIOSE: not checked (low priority: 100 m / 1:25,000 land cover, no crop type).

---

## 3. Yields, areas and statistics (ESYRCE, Anuario, CREM)

### Takeaway
Official statistics exist (ESYRCE, Anuario chapter 7 vegetables, CARM CREM), but MAPA pages were unreachable from this machine, so access format and Murcia-level granularity for specific vegetables are unconfirmed.

### Cited Findings
- MAPA publishes ESYRCE area/yield pages and a Power BI explorer; ESYRCE tendencies report Dec 2025 includes a vegetables section; 2025 data provisional — [ESYRCE portal URLs per search summary](https://www.mapa.gob.es/es/estadistica/temas/estadisticas-agrarias/agricultura/esyrce/default.aspx), [ESYRCE Power BI](https://www.mapa.gob.es/es/estadistica/temas/estadistica-digital/powerbi-esyrce) (SEARCH-ONLY; BLOCKED by TLS)
- Anuario de Estadística chapter 7 covers vegetables by group; area/yield/production by autonomous community and province per the search summary (SEARCH-ONLY): https://www.mapa.gob.es/estadistica/pags/anuario/2025/FORMATO%20PDF/AE25-C07/CAPÍTULO%2007.pdf. Chapter 4 PDFs (e.g. `AE25-C04/4.1.6.pdf`) exist. Whether the vegetable tables have Murcia province rows per crop was not confirmed.
- MAPA annual crop surface/production page: https://www.mapa.gob.es/es/estadistica/temas/estadisticas-agrarias/agricultura/superficies-producciones-anuales-cultivos/ (SEARCH-ONLY; BLOCKED)
- CARM CREM (Centro Regional de Estadística de Murcia) econet pages with agricultural tables exist, e.g. https://econet.carm.es/inicio/-/crem/sicrem/pu_datosbasicos/pdf/sec49.pdf (SEARCH-ONLY; not opened)
- Secondary figure: Murcia broccoli output 2024 reported up 3% to over 190,000 t — [regional report via search](https://www.institutofomentomurcia.es/documents/20147/275736/Datos+Clave+Regi%C3%B3n+de+Murcia+(esp)+2024.pdf/6dcdb5c2-35ce-9196-4a70-7f7ec3daa760) (SEARCH-ONLY, secondary)

### Inferences
- For yields, provincial MAPA figures (Murcia province) will be the realistic resolution; there is no sign of comarca-level yield data. Treat as a coarse sanity check on any modelled yield, not parcel ground truth.

### Gaps
- Exact downloadable tables (xlsx/csv) and Murcia vegetable yields by crop; ESYRCE comarcal/municipal detail; CREM downloadable series. All need a browser without the TLS problem.

---

## 4. Prices

### Takeaway
The only price source I fully verified is **Eurostat `apri_ap_crpouta`** (free JSON API, national Spain annual prices 2000-2024) which covers lettuce, cauliflower, melon, almond, orange, mandarin, lemon, tomato but NOT broccoli or artichoke. Weekly/weekly-origin prices from MAPA exist as PDFs and Excel/PowerBI but I could not open them. FAOSTAT API needs a token.

### Cited Findings
- Eurostat API works with no key: `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/apri_ap_crpouta?format=JSON&geo=ES&lastTimePeriod=3`. Dataset "Selling prices of crop products (absolute prices) - annual price (2000-2024)", updated 2025-05-15, EUR and national currency, per 100 kg, first marketing stage — [Eurostat API (VERIFIED)](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/apri_ap_crpouta?format=JSON&geo=ES&lastTimePeriod=3)
- Spain, EUR per 100 kg, 2022 / 2023 / 2024 (from my API query): lettuce in the open 27.41 / 34.22 / 31.42; cauliflower 56.16 / 96.27 / 69.06; melons 45.50 / 58.52 / 47.57; almonds 119.37 / 96.47 / 103.30; oranges 16.78 / 34.49 / 29.01; mandarins 37.08 / 47.53 / 49.91; lemons 40.74 / 38.36 / 30.80; tomatoes in the open 94.93 / 104.89 / 69.70 — [Eurostat API (VERIFIED)](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/apri_ap_crpouta?format=JSON&geo=ES&lastTimePeriod=3). Product codes: lettuce open 04192100, melons 04199913, cauliflower 04110000, almonds 06194130, oranges 06210000, mandarins 06220000, lemons 06230000. No broccoli or artichoke code among the 98 products. These are national averages, not Murcia, and almond is a dry-in-shell/kernel basis question I did not resolve.
- Dataset is in the Eurostat catalogue as [apri_ap_crpouta](https://db.nomics.world/Eurostat/apri_ap_crpouta) (mirror). An 8-year gap in my check: time series for 2000-2021 exist in the same dataset but I only pulled 2022-2024.
- MAPA weekly "Informe Semanal de Coyuntura" (e.g. week 37 of 2026) lists artichoke, broccoli, romaine lettuce and "piel de sapo" melon with prices in EUR/100 kg (lettuce per 100 units); it says national mean prices are also published in Excel/PowerBI. Weekly fruit-and-vegetable price bulletins (boletines semanales de precios de FyH) exist for 2024-2025 — [MAPA weekly report S-37 2026 (SEARCH-ONLY)](https://www.mapa.gob.es/es/dam/jcr:e5135043-2f1c-470c-a047-20ab5befe5b9/Informe%20Semanal%20de%20Coyuntura%202026%20S-37.eb96f778053a35885949ed82ed93ef71.pdf), [boletín example (SEARCH-ONLY)](https://servicio.mapa.gob.es/ca/ganaderia/estadisticas/182025boletinsemanaldepreciosdefyh28abril-4mayo_tcm34-707878.pdf)
- FAOSTAT producer-price API returned HTTP 401 without a token (FAOSTAT's REST needs a bearer token; bulk CSV downloads from the FAOSTAT website are the usual alternative, not tested) — [FAOSTAT API endpoint tried](https://faostatservices.fao.org/api/v1/en/data/PP)
- Mercamurcia prices: not found/verified.

### Inferences
- For a hackathon, the Eurostat annual price per 100 kg (EUR/t = x10) is enough to compute revenue per ha as yield (t/ha) x price, for lettuce/melon/citrus/almond. Broccoli and artichoke need MAPA weekly data or another source. Annual national averages hide large intra-year swings, so propagate price uncertainty (2022-2024 range moved by up to ~70% for oranges, cauliflower ~70%).

### Gaps
- Machine-readable MAPA weekly/monthly price series (Excel/PowerBI "precios medios nacionales") and their URLs; Mercamurcia and Lonja de Murcia series; FAOSTAT bulk files; broccoli/artichoke prices.

---

## 5. Costs (RECAN, IMIDA/MAPA cost studies)

### Takeaway
There is an IMIDA study of production-cost structures (EUR/ha) for Murcia outdoor horticulture incl. broccoli and lettuce, hosted by MAPA's Observatorio de la Cadena Alimentaria, which is exactly what a crop-economics model needs, but I could not open the PDF to extract numbers.

### Cited Findings
- MAPA-hosted PDF "Estructura de costes de las orientaciones productivas agrícolas de la Región de Murcia: horticultura al aire libre y bajo (plástico)": per the search summary its index lists "Estructura de costes (€/ha)" tables for broccoli and iceberg/Little Gem lettuce (tables 27-29) and establishment investment tables (6-8) — [PDF (SEARCH-ONLY; BLOCKED by TLS)](https://mapa.gob.es/es/alimentacion/temas/observatorio-cadena/estructuradecostesdelasorientacionesproductivasagricolasdelaregiondemurciahorticulturaalairelibreybajo_tcm30-690251.pdf). Sibling PDFs: [citrus and stone fruit](https://mapa.gob.es/en/alimentacion/temas/observatorio-cadena/estructuradecostesdelasorientacionesproductivasagricolasdelaregiondemurciafrutalesdehuesoycitricos_tcm38-690249.pdf), [organic crops](https://mapa.gob.es/en/alimentacion/temas/observatorio-cadena/estructuradecostesdelosprincipalescultivosenagriculturaecologicadelaregiondemurcia_tcm38-690252.pdf) (SEARCH-ONLY)
- RECAN (Spanish FADN): microdata anonymised, available from accounting year 2014 on request under a commitment document; MAPA also offers RECAN Analytica and a Power BI report — [MAPA RECAN page (SEARCH-ONLY)](https://www.mapa.gob.es/es/estadistica/temas/estadisticas-agrarias/economia/red-contable-recan). So RECAN microdata is NOT a login-free download.
- A 2010 MAPA study cites net margin 667.55 EUR/ha for irrigated lettuce in Murcia — old, indicative only — [MAPA study (SEARCH-ONLY)](https://mapa.gob.es/es/ministerio/servicios/analisis-y-prospectiva/Hort%C3%ADcolas.2010_tcm30-88515.pdf)
- MAPA lettuce cost sheet gives 0.33 EUR/kg total cost and ~11,160 EUR/ha direct cost per cycle, but for the Canary Islands 2019/20, so not transferable — [MAPA sheet (SEARCH-ONLY)](https://servicio.mapama.gob.es/en/alimentacion/temas/observatorio-cadena/ficha-costes-lechuga_tcm38-689119.pdf)

### Inferences
- The IMIDA cost-structure PDF is the best candidate for per-crop EUR/ha costs. Whoever has a working browser should open it and transcribe the tables (broccoli, lettuce, citrus, almond) with the year and assumed yield. Do not use the Canary figure.

### Gaps
- All actual EUR/ha values for Campo de Cartagena crops; melon, artichoke, almond cost tables; reference year of the IMIDA study.

---

## 6. Weather and soil ground truth (SIAM, AEMET, LUCAS, soil maps)

### Takeaway
SIAM is the right local ET0 source but I found no working programmatic download: the CARM open-data "Efemérides" CSV endpoints return HTTP 500 (service key missing), and `siam.imida.es` was unreachable from the fetch tool. AEMET OpenData is free with a key. LUCAS 2018 topsoil needs a short registration form (instant-ish, free).

### Cited Findings
- SIAM: ~45 automatic stations, mostly in irrigated areas, data free via siam.imida.es; stations include Torre Pacheco, San Javier, Santiago de la Ribera (per a 2012 news item); records at 10-minute intervals; irrigation and fertilisation programmes for citrus/fruit/vegetables — [iAgua article (SEARCH-ONLY, 2012, may be outdated)](https://www.iagua.es/noticias/murcia/12/12/09/el-sistema-de-informacion-agrario-de-murcia-amplia-su-oferta-de-servicios-gratuitos-e-incrementa-el-244). `siam.imida.es` itself: connection failed / refused (BLOCKED).
- CARM open data dataset "Efemérides meteorológicas de la Región de Murcia": per-station extremes since 2000 (11 variables incl. max one-day evapotranspiration, max precip, radiation, wind), published by IMIDA, last updated 2025-03-31; listed URLs `https://datosabiertos.carm.es/rest-services/services/restFile/ImidaEfemerides.{csv,json,txt,xml}` — [datos.gob.es record (VERIFIED)](https://datos.gob.es/es/catalogo/a14002961-efemerides-meteorologicas-de-la-region-de-murcia1). **I tested those URLs and `ImidaMeteoMes.csv`: all return HTTP 500 "No se ha localizado un servicio con la clave url.getImidaEfemerides"** (VERIFIED failure on 2026-11-14). Licence only links to the portal legal notice. These are extremes, not daily ET0 series, so they would not suffice anyway.
- National SiAR (MAPA) has an HTTP/JSON API (needs an API key emailed on request; endpoint listed as `servicio.mapama.gob.es/apisiar/API/v1/datos` and also `siar.es/api/v1/datos` in the same manual) computing ET0 by FAO Penman-Monteith; data for the current day not yet validated — [SiAR API manual v1.0 (SEARCH-ONLY)](https://servicio.mapa.gob.es/websiar/ControlesDatosAPI/Manual%20Web%20API%20SiAR%20Versi%C3%B3n%201.0.pdf). Whether SiAR includes the Murcia SIAM stations: unconfirmed.
- AEMET OpenData: key via https://opendata.aemet.es/centrodedescargas/altaUsuario (free, email only per a search summary); use "autorizado citando a AEMET" (VERIFIED footer on https://opendata.aemet.es/centrodedescargas/inicio). Daily climatology path pattern `valores/climatologicos/diarios/datos/fechaini/{..}/fechafin/{..}/estacion/{indicativo}`, max ~6-month window per request; auth as `api_key` query parameter or header (sources disagree) — [community docs via search (SEARCH-ONLY)](https://wetterdienst.readthedocs.io/en/latest/data/provider/aemet/observation/index.html). AEMET has a Torre-Pacheco station 7026X (SEARCH-ONLY, [AEMET](https://www.aemet.es/en/eltiempo/observacion/ultimosdatos?k=mur&l=7026X)). AEMET's own station data do not include ET0 as far as confirmed.
- LUCAS 2018 topsoil (ESDAC node 80774): registration via Request Form (name, email, organisation, country, purpose of at least 30 characters, accept terms), then CSV + shapefile of points + readme; 18,984 samples; variables pH (CaCl2, H2O), organic carbon, CaCO3, N, P, K, EC, oxalate Fe/Al; texture is a separate package; licence free, any purpose, personal, non-transferable, aggregate outputs, cite EC/ESDAC — [ESDAC LUCAS 2018 topsoil (VERIFIED)](https://esdac.jrc.ec.europa.eu/node/80774). Number of points inside Campo de Cartagena: unknown (LUCAS is a ~2 km grid so expect few).
- SoilGrids is already covered by the team; Spanish soil maps (IGME/CSIC/IMIDA) not checked.

### Inferences
- Realistic ET0 validation plan: compare NASA POWER/ECOSTRESS ET against SiAR or SIAM station ET0 for a few Campo stations, but data access needs either a SiAR key request (days?) or manual SIAM site download in a browser. If time is short, use AEMET (key in minutes) for temperature/precipitation validation and compute FAO-56 ET0 yourself only if radiation/wind/humidity are available.
- LUCAS is a quick, legitimate local soil check (EC and pH are useful for salinity in Campo de Cartagena) if the form returns the CSV promptly; treat access time as unknown.

### Gaps
- SIAM download mechanism, station codes for the Campo (La Palma, Torre Pacheco, Fuente Álamo, San Javier etc.), and daily ET0 availability. SiAR API key turnaround. AEMET authentication method and rate limits (official docs not reached). Spanish soil maps.

---

## 7. Water, Mar Menor regulation, nitrates

### Takeaway
Ley 3/2020 (BOE-A-2020-9793) is verified from the consolidated BOE text and gives concrete, quantifiable constraints that an advisory app should encode (no new irrigation in Zones 1 and 2, fertiliser ban within 1,500 m, 5%/20% nutrient-retention land). CHS water allocation and salinity datasets were not found.

### Cited Findings
- Art. 26: obligations depend on the zone of the farm per the delimitation in Annex I — [BOE consolidated Ley 3/2020 (VERIFIED, read by me)](https://www.boe.es/buscar/act.php?id=BOE-A-2020-9793)
- Art. 28: in Zones 1 and 2, conversion from rain-fed to irrigation is prohibited unless covered by a water right obtained before the law; new or expanded rain-fed cropland on non-forest land needs authorisation — same source
- Art. 29: within 1,500 m of the inner shore, application of all fertilisers, manures and green manure is prohibited, except organic, "sustainable" and precision agriculture more than 500 m from the coast under further conditions; parcels (even partly) in the strip must reserve 20% of the holding for nutrient-retention actions or forest spaces; up to 15% of the plot can be assigned from adjacent land within 500 m of the shore — same source
- Art. 30: holdings in Zones 1 and 2 must be registered in the regional Registro de Explotaciones Agrarias; Art. 31: irrigation needs a water-use right; Art. 32: farmers in Zones 1 and 2 must report actual water volume by source before 31 December each year; Art. 33-35: restitution to rain-fed/forest state of irrigation without water rights and loss of irrigation aid; Art. 36: vegetation structures/strips mandatory on irrigated land; Art. 37: 5% of each holding in Zones 1 and 2 must go to nutrient-retention systems — same source
- Preamble (first 100k characters read): two zones (Zone 1, Zone 2; old Zone 3 merged into 2); Zone 1 agricultural measures include only one annual cycle of the most sensitive species alternated with less sensitive crops, no bare soil more than two months in autumn/winter with N-capturing cover crop, no direct slurry (purines) application; nitrate action programme for the Campo de Cartagena vulnerable zone to be revised — same source. **I read only part of the 278k-character text; the Zone 1 detail articles (38+, additional Zone 1 measures, "cultivos admisibles") and Annex I zone maps were not read.** The version is a "consolidated" BOE text; a later decree-law reportedly extended the nitrogen fertilisation ban to all of Zone 1 (SEARCH-ONLY: [Ecomercio Agrario](https://ecomercioagrario.com/?p=79421)), so check for amendments.
- Constitutional Court rulings 112/2021 and 126/2023 upheld the main restrictions (SEARCH-ONLY, [TSJ Murcia note](https://www.poderjudicial.es/cgpj/es/Poder-Judicial/Tribunales-Superiores-de-Justicia/TSJ-Region-de-Murcia/Noticias-Judiciales-TSJ-Region-de-Murcia/El-TSJ-de-Murcia-rechaza-la-peticion-de-centenares-de-agricultores-para-dejar-sin-efecto-las-limitaciones-de-la-Ley-del-Mar-Menor))
- Aquifer monitoring: 20 boreholes in a control network for discharge to the Mar Menor, with sensors every 5 minutes for water level, temperature and salinity (news, Sept 2026); Campo de Cartagena aquifer declared at risk of not reaching good chemical status due to nitrates; a MITECO environmental impact declaration for "green filters" published in BOE on 17 Sept 2026 — [MITECO/iAgua via search (SEARCH-ONLY)](https://www.miteco.gob.es/es/prensa/ultimas-noticias/2026/septiembre/el-miteco-avanza-en-el-cinturon-verde-del-mar-menor-con-el-visto.html), [BOE-A-2026-19403](https://www.boe.es/boe/dias/2026/09/17/pdfs/BOE-A-2026-19403.pdf). Whether the borehole data is public: unknown.
- CHS Mar Menor documents exist (e.g. Plan Vertido Cero actuaciones PDF) — [CHS](https://www.chsegura.es/export/sites/chs/descargas/cuenca/marmenor/docsdescarga/PlanVertidoCero_Actuaciones.pdf) (SEARCH-ONLY)

### Inferences
- Concretely modellable constraints: (a) distance-to-shore buffers of 500 and 1,500 m from the lagoon; (b) Zone 1/2 membership from Annex I (map still needed); (c) a "no new irrigation" flag for parcels currently rain-fed (`parc_sistexp = 'S'` in FEGA data) inside Zones 1 and 2. This ties neatly to the FEGA layer.

### Gaps
- Zone 1/2 geometry as downloadable GIS (Annex I, CARM IDE/CHS); CHS water allocation, salinity, Tajo-Segura transfer volumes/prices, desalinated water price; "Canal Observatory" data; Mar Menor nitrate/chlorophyll monitoring open data (IEO/CARM). None found in this pass.

---

## 8. Quick priority list for the team (what is downloadable today without login)

1. FEGA Cultivo declarado 2025, municipal GPKG/SHP (CC BY 4.0) or OGC API: verified end to end.
2. Catastro INSPIRE WFS parcels (free, verified), only needed if SIGPAC recintos geometry is insufficient; FEGA `recintos` already carries geometry.
3. Eurostat `apri_ap_crpouta` Spain annual prices (verified API).
4. BOE Ley 3/2020 text (verified) for constraint rules.
5. LUCAS 2018 topsoil: free registration form; 10-minute step.
6. AEMET OpenData: free key (not tested).
7. Anything from mapa.gob.es (IMIDA cost PDF, ESYRCE, price series, RECAN): open in a normal browser; unverified here.
8. Not downloadable today: RECAN microdata (request + commitment), CLMS HRL Crop Types (WEkEO/EEA authentication per EEA catalogue), WorldCereal not useful for vegetables.

## Trap list
- `curl -k` / skipping certificate checks to read mapa.gob.es was refused by the permission layer and was not used; try another network or browser instead.
- Zenodo API via curl returned 403; use the browser or WebFetch on record pages.
- CARM "datosabiertos" REST URLs listed in datos.gob.es are currently broken (HTTP 500).
- FEGA cultivo declarado: numeric product codes without a dictionary; ~41% null in Cartagena.
- Catastro WFS: use `typenames=cp:CadastralParcel&bbox=lat,lon,lat,lon` with `srsname=urn:ogc:def:crs:EPSG::4326`; Catastro municipality codes (51016...) differ from INE (30016).
- Eurostat price dataset: no broccoli or artichoke; prices per 100 kg; national, not Murcia.
