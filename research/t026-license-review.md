# T-026 official-source licence and citation review

Reviewed 2026-11-14, Arturo. Base main 7760056, handoff #204. Scope is the
listed data citations, not a global licence choice or publication approval.
Short evidence statements below are paraphrases, not copied licence texts.
No product is asserted actually downloaded merely because its citation exists.

| Item | Official evidence URL | Evidence summary (<=25 words) | Outcome / exact remaining dependency |
|---|---|---|---|
| GIBS acknowledgement | https://nasa-gibs.github.io/gibs-api-docs/#data-use-guidance-and-acknowledgements | Credit NASA GIBS imagery services and ESDIS; the live documentation supplies the full acknowledgement. | Service credit verified; Jaime must name actual layer so underlying data credit can match. |
| POWER reference | https://power.larc.nasa.gov/docs/referencing/ | Cite NASA LaRC POWER, service name, version and access date. | Seed files record daily API v2.10.3, downloaded 2026-11-14T14:36Z. No invented universal POWER dataset DOI. |
| IMERG through POWER | https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/#imerg | Daily UTC output sums half-hourly precipitation; Final and Late runs are used depending on latency. | Cache has IMERG_PRECTOT but no upstream collection DOI/version. Gonzalo must confirm mapping; do not assert GPM_3IMERGDF was downloaded. |
| Candidate daily IMERG DOI | https://www.earthdata.nasa.gov/data/catalog/ges-disc-gpm-3imergdf-07 | GPM_3IMERGDF V07 daily Final data are openly shared; the page provides its citation. | Huffman et al. 2023, DOI 10.5067/GPM/IMERGDF/DAY/07 verified; candidate only, not a claim about POWER upstream. |
| HLS dataset citations | https://hls.gsfc.nasa.gov/documents/ ; https://water.usgs.gov/catalog/datasets/cd4013e0-a2fa-414b-915a-f94f3a176387/ ; https://data.nasa.gov/dataset/hls-sentinel-2-multi-spectral-instrument-surface-reflectance-daily-global-30m-v2-0-bee8f | HLS L30/S30 have separate dataset DOIs; S30 catalogue links government-works terms. | Masek et al. 2021, 10.5067/HLS/HLSL30.002 and 10.5067/HLS/HLSS30.002. T013 confirms actual usage; licence checked explicitly on S30 metadata, not a blanket declaration for every HLS-derived product. |
| MODIS citation/terms | https://data.nasa.gov/dataset/modis-terra-vegetation-indices-16-day-l3-global-250m-sin-grid-v061-2eb0d ; https://modis.ornl.gov/cgi-bin/sites/site/?network=AMERIFLUX&network_siteid=US-KFS&product=MOD13Q1 | NASA lists MOD13Q1 V061 DOI and government-works terms; ORNL names Didan and publication year. | Didan 2021, 10.5067/MODIS/MOD13Q1.061. Kansas subset is only citation evidence; no claim of using that subset/tool. |
| SRTM citation/terms | https://water.usgs.gov/catalog/datasets/22c70bf3-57b2-4027-8f2c-7d1f6e808964/ ; https://data.nasa.gov/dataset/nasa-shuttle-radar-topography-mission-global-1-arc-second-v003-e47e1 | USGS names NASA JPL 2013, SRTMGL1 V003 DOI; NASA catalogue links government-works terms. | 10.5067/MEaSUREs/SRTM/SRTMGL1.003. Confirm actual DEM before claiming used. |
| SoilGrids licence | https://isric.org/explore/soilgrids/ | ISRIC explicitly licenses SoilGrids maps under CC BY 4.0. | Licence resolved. Page also reports REST paused, no recovery date or uptime guarantee; producer notified #207. |
| SoilGrids API/citation | https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_04.html | REST fair use is five calls per minute; cite Poggio for soil properties, Turek for water-retention layers. | Poggio 2021 DOI10.5194/soil-7-217-2021 verified in existing citation; use Turek citation if those layers are added. |
| PNOA licence | https://www.ign.es/resources/licencia/Condiciones_licenciaUso_IGN.pdf ; https://www.scne.es/productos.php | CC BY 4.0 attribution belongs beside imagery; identify product, date and producers, and mark derived works. | Licence pp.1–2; short credit PNOA 2025 CC-BY 4.0 scne.es for the Murcia product. |
| PNOA Murcia year | https://pnoa.ign.es/pnoa-imagen/estado-del-proyecto | Official orthophoto table lists MUR, Murcia, 2025, 0.25 metres and an available maximum-actuality mosaic. | Year verified for that product/region, not all Spanish map tiles. Frontend layer remains unconfirmed. |
| SIAM locations | https://datosabiertos.regiondemurcia.es/carm/catalogo/medio-ambiente/estaciones-meteorologicas-de-la-red-siam-carm ; https://datosabiertos.regiondemurcia.es/avisolegal | Catalogue links terms allowing commercial/non-commercial reuse and adaptation, requiring source, retained dates/terms and no endorsement. | Location dataset terms resolved; catalogue last modification 2024-02-14. Not an ESAM price permission. |
| TP91 published catalogue | https://datosabiertos.regiondemurcia.es/admin/dataset/informe-meteorologico-diario-carm-anos-2000-a-2017-estacion-meteorologica-tp91 | TP91 has licenseURI pointing to reuse terms, but a missing-licence banner and dictionary describing annual aggregates. | Contradictory metadata documented. It does not establish the scope of the engine's separate personalised daily report. |
| Engine daily TP91 | http://siam.imida.es/apex/f?p=101:46 | Engine sources.csv names this personalised daily report, not the geolocated station catalogue. | UNRESOLVED: confirm applicable terms for the exact daily export and 2005–2024 coverage with IMIDA; no blanket open-licence claim. |

## Read-only provenance checks

Main 7760056 pipeline cache files power-merra2_75_-2.json and
power-imerg_377_-10.json record api_version v2.10.3 and descargado
2026-11-14T14:36Z, start 2005-01-01, 7305 days, daily UTC API URLs.
They do not record an IMERG upstream collection version. This review read only
metadata, without redownloading series or changing pipeline/engine files.
Engine t020-jaime 57561e9 sources.csv points SIAM-TP91 at apex 101:46.

Several direct LP DAAC/DOI/Earthdata requests returned HTTP403 through the
browser. Official NASA/USGS alternate catalogues above supplied the evidence;
no citation was marked verified from an inaccessible page alone.

Existing FEGA declared-crop/access-method, CREM, OSM and ESA/HRL rows are outside
this handoff's enumerated checks and remain explicit verify items. D-010 and
CARM permission status are preserved. No contact emails were sent.

## Producer clarification #211

Gonzalo confirms no upstream IMERG collection/version is returned or retained;
this cannot be reconstructed from the saved cache. Service citation is POWER
Daily API v2.10.3, downloaded 2026-11-14T14:36Z; IMERG upstream remains partial.
Gonzalo observed SoilGrids responding today (34s direct, 27s via API), with seeded
demo cache and cargando fallback. This producer observation is not a receiver
measurement and does not cancel the official no-uptime-guarantee notice.
