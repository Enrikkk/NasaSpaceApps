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
| SIGPAC recintos (FEGA, via sigpac-hubcloud.es) | CC BY 4.0 in INSPIRE Geoportal and the ATOM dataset record ([INSPIRE](https://inspire-geoportal.ec.europa.eu/srv/api/records/af7aeed6-cd6c-4456-92ff-d1026c60a27e), [datos.gob.es](https://datos.gob.es/eu/catalogo/e05024401-sistema-de-informacion-geografica-de-parcelas-agricolas-sigpac)). **Warning:** a FEGA reply on datos.gob.es says access from code by third parties to the SIGPAC database is not allowed | "Fuente: FEGA" | **verify** (ask FEGA or read the hubcloud terms before relying on live API calls) |
| FEGA declared crop (cultivo_declarado) | Same publisher; license not confirmed separately | "Fuente: FEGA" | verify |
| PNOA orthophoto (IGN) | CC BY 4.0, "CC-BY 4.0 scne.es <year>"; derived works: "Obra derivada de PNOA ... CC-BY scne.es" ([IGN conditions](https://www.ign.es/resources/licencia/Condiciones_licenciaUso_IGN.pdf)). Attribution must be visible next to the data | "CC-BY 4.0 scne.es 2025" on the map | ok (confirm year at scne.es) |
| NASA GIBS imagery | NASA material not copyrighted unless stated; credit NASA; no implied endorsement ([Earthdata data use policy](https://www.earthdata.nasa.gov/earth-observation-data/data-use-policy)). GIBS asks for an acknowledgement "provided by GIBS, operated by NASA/GSFC/ESDIS" (archived wording) | GIBS acknowledgement + the layer's own citation (MODIS/IMERG) | verify wording on live GIBS page |
| NASA POWER, GPM IMERG, HLS, MODIS, SRTM | NASA open data, cite the dataset DOI/page | dataset citation per product page | verify DOIs |
| ISRIC SoilGrids 2.0 | CC BY 4.0 per LifeWatch and GEE catalog; V1 was ODbL (not ours) | Poggio et al. 2021, SOIL 7, 217-240, https://doi.org/10.5194/soil-7-217-2021 | verify on soilgrids.org; check REST API fair-use limit (5 calls/min) |
| Open-Meteo (ET0) | Data CC BY 4.0, but the **free API is non-commercial only** (<10,000 calls/day) ([terms](https://open-meteo.com/en/terms), [licence](https://open-meteo.com/en/licence)) | "Weather data by Open-Meteo.com" | ok for the hackathon; flag in the business slide |
| Nominatim / OSM geocoder (if used) | ODbL; public instance usage policy (about 1 request/s, attribution) | "(c) OpenStreetMap contributors" | verify |
| SIAM-IMIDA stations | not reviewed | | verify |
| MAPA / ESAM prices, CREM areas | not reviewed | | verify |
| Ley 3/2020 (BOE) | Spanish legislation, public sector information, reuse allowed | cite BOE-A-2020-9793 | ok |
| ESA Sentinel-2 / CDSE, HRL Croplands | not reviewed | | verify |

Open items for the team: (1) FEGA access-from-code question; (2) exact GIBS wording; (3) review of the rows marked `verify` before the submission form.
