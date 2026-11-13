# Field Shift: datasets filtrados para la Región de Murcia (chuleta)

Versión corta de una pantalla. El detalle (fuentes, cifras, citas) está en
`reports/Datos agrícolas Región de Murcia.md` y las notas brutas en `research_notes/Datos agrícolas Región de Murcia/`.
Pruebas en vivo: `python3 research/api_smoke_test.py` (11/11 fuentes respondieron sin clave el 13-nov-2026).

Regla de escala: la unidad es **el polígono de la parcela** (SIGPAC). Capas de 5–30 m → estadística zonal dentro
de la parcela. Capas de 9 km o más → la celda que la contiene, y la interfaz lo dice ("tu comarca de ~10 km").

## KEEP: el núcleo (12 fuentes)

| # | Fuente | Para qué | Acceso | Cuenta |
|---|---|---|---|---|
| 1 | **SIGPAC hubcloud** | Polígono, ha, pendiente, % regadío, uso | `sigpac-hubcloud.es/servicioconsultassigpac/query/recinfobypoint/4258/{lon}/{lat}.json` (0,2 s, gzip) | No |
| 2 | **Cultivo declarado FEGA** | **Rotación real**: campaña en curso (OGC API) + 2025 (GPKG por municipio) | `sigpac-hubcloud.es/ogcapi/collections/cultivo_declarado/items?bbox=…` (páginas de 250) + `fega.gob.es/atom/2025/cd_2025/30 - MURCIA/` | No |
| 3 | **HRL Croplands (Copernicus)** | Tipo de cultivo 10 m 2017–2024, diversidad en 3 años, suelo desnudo | CDSE STAC + COG (~2 MB/año/tile; Cartagena `E33N16`) | CDSE |
| 4 | **NASA POWER** | Tmax/Tmin, heladas (calcular Tmin<0), días >35 °C, 1981→ | API de punto, ~2 s por 20 años | No |
| 5 | **GPM IMERG vía POWER** | Lluvia 0,1°, extremos, DANAs | Misma API: `IMERG_PRECTOT` + `&time-standard=UTC` | No |
| 6 | **HLS-VI (NASA)** | NDVI 30 m → meses desnudos, calendario real | AppEEARS (tarea de área) | Earthdata |
| 7 | **Sentinel-2 L2A** | NDVI 10 m (~50 píxeles en 0,5 ha) | Earth Search COG anónimo / CDSE | No / CDSE |
| 8 | **MODIS MOD13Q1** | 25 años de NDVI, anomalías | AppEEARS | Earthdata |
| 9 | **SIAM-IMIDA** | Estaciones con ET0 Penman-Monteith (dato de ayer); feed "IoT de tierra" | Geoportal ArcGIS IMIDA (`SIAM_DATOS`) | No |
| 10 | **Zonas nitratos / Mar Menor (IMIDA)** | Etiqueta legal de la parcela | Geoportal ArcGIS IMIDA | No |
| 11 | **IGN MDT05 + PNOA** / SRTM | Pendiente, hondonadas frías; mapa base | WCS/WMS IGN; SRTM vía AppEEARS para citar NASA | No / Earthdata |
| 12 | **SoilGrids** + suelos IMIDA | Textura, carbono, pH | REST (5/min, hasta 60 s): **cachear, nunca en directo** | No |
| + | **Open-Meteo (ERA5)** | ET0 FAO diaria y lluvia de respaldo | REST 0,5 s, `models=era5` (no `era5_land`) | No |
| + | **Precios ESAM-CARM / MAPA, CREM** | €/kg, superficies | PDF → `crops.csv` a mano | No |

## OPTIONAL (si sobra tiempo o para el pitch)

NEX-GDDP-CMIP6 en AWS (clima 2040–2060, análogos; sin cuenta) · SMAP L4 raíz 9 km · MOD16 ET · un mapa ECOSTRESS LST
· GRACE-FO (gráfico de pitch, celda ~112.000 km²) · HR-VPP fenología 10 m (validación) · CDS ERA5-Land e indicadores
agroclimáticos (colas de 2–9 h) · EGMS subsidencia Guadalentín · CORINE · EMS inundación DANA 2019 · AEMET (clave por
email) · piezómetros CHS vía IMIDA · SIGPAC histórico IMIDA 2011–2024.

## DROP

IMERG directo (GES DISC/Giovanni) · SMAP L3 · ECOSTRESS ET/ESI · Landsat C2 bruto · `FROST_DAYS`/`GWETROOT`/`EVLAND` de
POWER · Sentinel-1/3 brutos · EuroCrops v2 (5–11 GB) · WorldCereal 2021 · API SiAR (exige NIF) · SAIH iVisor ·
Agroseguro · MCA 1980–2010 · todo lo que solo existe en EE. UU. (CropScape, QuickStats, OpenET, Web Soil Survey,
LANDFIRE) · GEDI.

## Cuentas que hay que tener (las crea cada humano, no los agentes)

1. **Earthdata Login** (AppEEARS: HLS, MODIS, SRTM). Token ~48 h.
2. **Copernicus Data Space** (HRL Croplands).
Opcionales: CDS, AEMET, Google Earth Engine.

## Parcela de demo propuesta

Torre-Pacheco (30037), SIGPAC **18/426/1**, centroide lat 37.73830, lon −0.98838: 4,09 ha, tierra arable, 100 %
regadío, pendiente 0,8 %, zona vulnerable a nitratos ES62_1, estación SIAM TP91 a 1,1 km.
Cultivo declarado: **2025 melón → campaña en curso barbecho** (suelo desnudo: historia de Mar Menor y cubiertas).
Alternativa: 18/443/4 (8,5 ha, 2025 apio → actual lechuga). Hay que confirmarla el sábado con el NDVI.

## Trampas

- Tres fuentes de lluvia difieren un 43 % en la misma parcela (2024: ERA5 185 mm, POWER 211, IMERG 263); en la DANA
  de 2019 todas se quedaron cortas. Enseñar la horquilla, no un número.
- El acolchado plástico puede parecer "suelo desnudo" en el NDVI.
- `exp_num` del cultivo declarado es un nº de expediente: **nunca** mostrarlo.
- AppEEARS y CDS: colas impredecibles. Lanzar el sábado a las 9:00 y guardar todo en caché (JSON/Parquet).
