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

## License review (gonzalo's agent, 2026-11-14; web search only, NOT yet checked on the official pages)

Status: `ok` = license found in 2+ sources; `verify` = must be confirmed on the official page before submitting.

| Source | License / terms found | Required attribution | Status |
|---|---|---|---|
| SIGPAC recintos (FEGA, via sigpac-hubcloud.es) | CC BY 4.0, commercial and non-commercial use allowed. FEGA's "Terminos de uso de la informacion de alto valor del SIGC" (Feb 2026, read in the PDF 2026-11-14: [PDF](https://www.fega.gob.es/orig/pdfs/Terminos_de_uso_de_informacion_de_alto_valor_del_SIGC.pdf)) names the SIGPAC OGC API and states no formal requirement or express authorisation from FEGA is needed for access, download or copy. Also in [INSPIRE](https://inspire-geoportal.ec.europa.eu/srv/api/records/af7aeed6-cd6c-4456-92ff-d1026c60a27e) and [datos.gob.es](https://datos.gob.es/eu/catalogo/e05024401-sistema-de-informacion-geografica-de-parcelas-agricolas-sigpac). **Caveat:** a MAPA reply of 26/06/2023 on datos.gob.es says third-party access from code is not allowed; nothing official repeals it expressly, so treating the 2026 terms as superseding it is our inference. `recinfobypoint` is not named in the terms and no rate limit is published. Fallback: official ATOM per municipality (`research/sigpac-atom-campo-cartagena.md`) | "Fuente de los datos: FONDO ESPAÑOL DE GARANTÍA AGRARIA O.A." | ok for use and attribution; **verify** `recinfobypoint` and rate limits (email draft to sg.ayudasdirectas@fega.es, not sent) |
| FEGA declared crop (cultivo_declarado) | Same publisher; license not confirmed separately | "Fuente: FEGA" | verify |
| PNOA orthophoto (IGN) | CC BY 4.0, "CC-BY 4.0 scne.es <year>"; derived works: "Obra derivada de PNOA ... CC-BY scne.es" ([IGN conditions](https://www.ign.es/resources/licencia/Condiciones_licenciaUso_IGN.pdf)). Attribution must be visible next to the data | "CC-BY 4.0 scne.es 2025" on the map | ok (confirm year at scne.es) |
| NASA GIBS imagery | NASA material not copyrighted unless stated; credit NASA; no implied endorsement ([Earthdata data use policy](https://www.earthdata.nasa.gov/earth-observation-data/data-use-policy)). GIBS asks for an acknowledgement "provided by GIBS, operated by NASA/GSFC/ESDIS" (archived wording) | GIBS acknowledgement + the layer's own citation (MODIS/IMERG) | verify wording on live GIBS page |
| NASA POWER, GPM IMERG, HLS, MODIS, SRTM | NASA open data, cite the dataset DOI/page | dataset citation per product page | verify DOIs |
| ISRIC SoilGrids 2.0 | CC BY 4.0 per LifeWatch and GEE catalog; V1 was ODbL (not ours) | Poggio et al. 2021, SOIL 7, 217-240, https://doi.org/10.5194/soil-7-217-2021 | verify on soilgrids.org; check REST API fair-use limit (5 calls/min) |
| Open-Meteo (ET0) | Data CC BY 4.0, but the **free API is non-commercial only** (<10,000 calls/day) ([terms](https://open-meteo.com/en/terms), [licence](https://open-meteo.com/en/licence)) | "Weather data by Open-Meteo.com" | ok for the hackathon; flag in the business slide |
| Nominatim / OSM geocoder (if used) | ODbL; public instance usage policy (about 1 request/s, attribution) | "(c) OpenStreetMap contributors" | verify |
| SIAM-IMIDA stations (hourly series, station TP91; used by enrique's engine for frost/heat) | Published on CARM open data (`datosabiertos.carm.es/odata/Agricultura/IMIDA_estaciones.csv`, `siam.imida.es`); **no explicit open licence found** (enrique's JSON says "cite source"). These are the 2 CARM mentions left in the open engine JSON metadata: they are source links, not prices | "Fuente: SIAM-IMIDA, Region de Murcia (CARM)" | **verify** (no price data; licence to confirm before submission) |
| CARM / ESAM prices (esam.carm.es) | **NOT an open licence.** Per Enrique (team-bus #104, 2026-11-14, checked on esam.carm.es/legal): reproduction allowed citing the origin, but only personal non-commercial use is authorised and modification is not allowed. **DECISION D-010 (2026-11-14): the published `torre-pacheco.json` DOES use CARM prices while written permission is still pending; the risk was assumed knowingly (enrique decided, gonzalo acknowledged).** Conflicts with AGENTS.md section 6 (submission attestation: no copyrighted material without permission) and must be re-reviewed before filing the submission. Open-data twin `torre-pacheco.abierto.json` kept to switch back; open price sources are being searched in `research/precios-abiertos.md` | cite "CARM-ANUARIO" in the card and here, and state "permiso pendiente" | **PENDING PERMISSION, USED UNDER D-010 (risk accepted)** |
| MAPA, Indices y Precios Percibidos Agrarios + Precios Medios Nacionales (national, open alternative to CARM) | Not a CC licence: reuse without express authorisation citing the source, keeping the update-date and reuse-conditions metadata ([MAPA aviso legal](https://www.mapa.gob.es/es/atencion-al-ciudadano/aviso-legal), Ley 37/2007). Reserve: the notice is the portal's, not specific to the statistic; low risk. Not Murcia-specific. Details: `research/precios-abiertos.md` | "Fuente: Ministerio de Agricultura, Pesca y Alimentacion (MAPA), Indices y Precios Percibidos Agrarios / Precios Medios Nacionales (consultado 2026-11-14). Reutilizacion conforme al aviso legal de MAPA." | ok (confirm wording on the live page) |
| Eurostat `apri_ap_crpouta` (annual prices, cross-check) | "Reuse ... is authorised provided the source is acknowledged" ([copyright notice](https://ec.europa.eu/eurostat/help/copyright-notice)); state if data are modified | "Source: Eurostat, apri_ap_crpouta, accessed 2026-11-14" | ok |
| FAOSTAT Producer Prices (annual, cross-check) | CC BY 4.0 plus additional terms ([terms](https://www.fao.org/contact-us/terms/db-terms-of-use/en/)): data must not be used in conjunction with the promotion of a commercial enterprise or its products; no implied FAO endorsement. Low risk for a research demo, **team to decide** if Agrockham is presented as a commercial product | "FAO. 2026. FAOSTAT: Producer Prices. Accessed 14 November 2026. https://www.fao.org/faostat/en/#data/PP Licence: CC-BY-4.0." | ok with reservation (confirm update year on the page) |
| CREM areas | not reviewed | | verify |
| Ley 3/2020 (BOE) | Spanish legislation, public sector information, reuse allowed | cite BOE-A-2020-9793 | ok |
| ESA Sentinel-2 / CDSE, HRL Croplands | not reviewed | | verify |

Open items for the team: (1) FEGA access-from-code question; (2) exact GIBS wording; (3) review of the rows marked `verify` before the submission form.
