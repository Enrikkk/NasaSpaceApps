# Pipeline de datos por parcela (T-011)

Dado un punto (lat, lon) produce los bloques del contrato v1.1 que dependen del sitio y los cachea en disco para que la
demo no dependa de la Wi-Fi del venue.

| Subpaquete | Produce | Fuente | Dependencias |
|---|---|---|---|
| `atom/` | bloque `parcela` (recinto SIGPAC) + recintos por bbox | ATOM del FEGA (GPKG por municipio, campana 2026) | pyogrio, shapely, numpy |
| `clima_suelo/` | bloques `clima` y `suelo` (+ `fuentes_nuevas`) | NASA POWER (MERRA-2 e IMERG), Open-Meteo (ERA5, ET0 FAO-56), SoilGrids 2.0 | solo libreria estandar |

`contract.py` localiza el esquema del contrato (`$AGROCKHAM_CONTRACT_SCHEMA` > `app/data/contract.schema.json` >
`research/contract-v1-draft/v1.1/contract.schema.v1.1.json` > borrador v1) y no falla si no hay ninguno: los tests y
`validate_blocks` se omiten o avisan.

Se ejecuta siempre **desde la raiz del repo** con `python -m`. Las rutas de datos son relativas a la raiz (`app/data/cache/pipeline/`).
Estos dos prototipos siguen tambien en `research/prototypes/` (no se han borrado; otros agentes los usan). La copia de aqui es la
de producto: arreglar bugs aqui.

## Atribucion obligatoria (FEGA) y otras

Toda pantalla o documento que muestre recintos SIGPAC debe llevar: **"Fuente de los datos: FONDO ESPAÑOL DE GARANTÍA AGRARIA O.A."**
(CC BY 4.0; indicar que los datos estan transformados y la fecha de extraccion; sin logo del FEGA ni sugerir respaldo).
`lookup.ATTRIBUTION` y el campo `attribution` de `recintos_en_bbox` ya la llevan. El resto de atribuciones esta en "Licencias y citas".

## Ejecutar

```bash
python3 -m venv /ruta/venv && /ruta/venv/bin/pip install -r app/backend/pipeline/requirements.txt   # venv FUERA del repo

# clima + suelo de una parcela (usa y rellena la cache; segunda ejecucion: 0 llamadas de red)
python3 -m app.backend.pipeline.clima_suelo.build_blocks 37.7383 -0.98838          # resumen + app/data/cache/pipeline/blocks/<lat>_<lon>.blocks.json
python3 -m app.backend.pipeline.clima_suelo.build_blocks 37.7383 -0.98838 --json   # solo el JSON {clima, suelo, fuentes_nuevas}
AGROCKHAM_OFFLINE=1 python3 -m app.backend.pipeline.clima_suelo.build_blocks ...   # prohibe la red: falla si falta algo en cache
/ruta/venv/bin/python -m app.backend.pipeline.clima_suelo.validate_blocks          # esquema + invariantes + cordura

# SIGPAC desde el ATOM (ZIP en un directorio FUERA del repo; https://www.fega.gob.es/atom/2026/rec_2026/30%20-%20MURCIA/ ; descargas grandes de noche)
/ruta/venv/bin/python -m app.backend.pipeline.atom.build_recintos --src /ruta/zips --out /ruta/build [--municipios 30037,30045] [--bbox minx,miny,maxx,maxy]
/ruta/venv/bin/python -m app.backend.pipeline.atom.lookup --data /ruta/build --point 37.7383 -0.98838
```

En Python (API):

```python
from app.backend.pipeline.atom.lookup import RecintoIndex
from app.backend.pipeline.clima_suelo import pipeline as P
idx = RecintoIndex.load("/ruta/build")            # carga 1-4 s; hacerlo una vez al arrancar el backend
parcela = idx.recinto_por_punto(37.7383, -0.98838)   # bloque `parcela` (dict) o None
clima, suelo = P.build_clima(37.7383, -0.98838), P.build_suelo(37.7383, -0.98838)
```

## Tests (sin red)

```bash
# todos (desde la raiz). Con venv que tenga shapely/numpy/pyogrio/jsonschema:
/ruta/venv/bin/python -m unittest discover -s app/backend/pipeline -t .
# con los GeoJSON completos del ATOM (Torre-Pacheco 30037 + Los Alcazares 30045 como minimo):
ATOM_BUILD_DIR=/ruta/build /ruta/venv/bin/python -m unittest discover -s app/backend/pipeline -t .
# o construyendolos desde los ZIP: ATOM_SRC_DIR=/ruta/zips ...
```

Sin `ATOM_BUILD_DIR`/`ATOM_SRC_DIR` se omite solo `TestLookup` (necesita los GeoJSON completos). `TestMuestraDemo` si corre: usa la muestra
de 66 recintos de `app/data/cache/pipeline/atom/`. Sin `jsonschema` se omiten los tests de esquema. Los tests de `clima_suelo` nunca tocan la red.

## Que se cachea y donde (`app/data/cache/pipeline/`, 316 KB, versionado)

| Ruta | Contenido |
|---|---|
| `clima_suelo/<fuente>_<celda>.json` | respuestas crudas compactas de la parcela demo (series diarias 2005-2024, URL, fecha de descarga, unidades, licencia) |
| `blocks/37.7383_-0.98838.blocks.json` | salida de `build_blocks` para la parcela demo: `{clima, suelo, fuentes_nuevas}` |
| `atom/parcela_demo.json` | bloque `parcela` de la parcela demo (SIGPAC 30/37/0/0/18/426/1) |
| `atom/torre-pacheco_demo_viewport.geojson` | 66 recintos alrededor de la demo (60 KB, con atribucion) |
| `clima_suelo/.state/` | hora de la ultima llamada a SoilGrids (git-ignorado) |

Otra carpeta de cache: `AGROCKHAM_CACHE_DIR=/ruta` (solo `clima_suelo`). Los GeoJSON completos del ATOM (44 MB, 8,9 MB gzip para 5 municipios)
**no** van al repo (se generan con `build_recintos`).

Claves de celda (la consulta se hace siempre en el **centro de la celda**, asi la cache no depende de quien llega primero):

| Fuente | Celda |
|---|---|
| POWER MERRA-2 (T2M_MAX, T2M_MIN, PRECTOTCORR) | nodo 0,5 grados lat x 0,625 grados lon (`75_-2`) |
| POWER IMERG (IMERG_PRECTOT) | pixel 0,1 grados (`377_-10`). Dos llamadas a POWER distintas: con una sola celda de 0,5 se mezclarian ~25 pixeles IMERG |
| Open-Meteo (lluvia ERA5 + ET0 FAO-56) | celda 0,1 grados |
| SoilGrids (clay, sand, silt, soc, phh2o, nitrogen en 0-5, 5-15, 15-30 cm) | celda 0,0025 grados (~220 x 280 m) |

Primera ejecucion con cache vacia: 4 llamadas, ~9 s. Con cache: 0,09 s y 0 llamadas. Un anio se descarta de una serie con menos de 360 dias validos.

## Limites y trampas

- **SoilGrids: 5 llamadas/min por IP.** `pipeline.py` espera 12,5 s entre llamadas (compartido entre procesos via `.state/`) y reintenta
  con 15/30/60 s en 429/5xx/timeout. Con una celda nueva no espera; con 2+ celdas seguidas si. En Cloud Run la IP de salida es compartida:
  precalentar las celdas del Campo de Cartagena y no depender de SoilGrids en vivo durante la demo. Es un modelo de 250 m, no una medida:
  el SOC superficial (21,6 g/kg a 0-5 cm) es alto para regadio semiarido; cruzar con analisis locales/IMIDA.
- **`FROST_DAYS` de POWER no es Tmin < 0 °C**: no se usa. `dias_helada` va marcado `fuente: "pendiente SIAM"`, `provisional: true`
  (el contrato exige `valor`; lleva dias con T2M_MIN < 0 en el nodo MERRA-2, que promedia ~50 km incluyendo mar: minima de +1,4 °C en 20 anios).
  La cifra real vendra de SIAM (T-014). Por el mismo suavizado `dias_calor_gt_38` sale 0 (cota inferior).
- **`EVLAND` de POWER no ve el riego** (evaporacion del modelo de superficie): inutil en regadio. La ET0 sale de Open-Meteo (FAO-56).
- **IMERG via POWER exige `&time-standard=UTC`**; sin el, la serie queda desplazada. `-999` es relleno (se guarda `null` y se cuenta
  en `relleno_descartado`).
- Tres lluvias distintas (parcela demo, 2005-2024): POWER 297, IMERG 366, ERA5 262 mm; media 308. Por eso `lluvia_anual_mm` lleva
  `horquilla` (min-max entre fuentes, no intervalo de confianza) y `por_fuente_mm`. 2024: ERA5 185 / POWER 211 / IMERG 263 mm.
- Elevaciones distintas entre fuentes (MERRA-2 124 m, IMERG/POWER 299 m, ERA5 40 m): las temperaturas son del nodo, no de la parcela.
- `agua_disponible_mm` es la reserva de **0-30 cm** (Saxton y Rawls 2006), no de toda la zona radicular (~150 mm/m).
- `materia_organica_pct` = SOC (g/kg) / 10 x 1,724 (van Bemmelen). `suelo.metadatos.conversiones` documenta las unidades de SoilGrids.
- ATOM: `zonas` va vacio (nitratos / Mar Menor no salen del ATOM), sin cultivo declarado (esta en `cd_2025`, otro esquema); `comarca`
  "Campo de Cartagena" es un supuesto para 7 codigos SIGPAC; el nombre de municipio solo existe para 8 codigos verificados; geometrias
  redondeadas a 6 decimales (IoU 0,9995 frente a la API); salida ETRS89 tratada como WGS84. Solo se probaron 5 municipios pequenos.
  Detalle y medidas (rendimiento, memoria, opcion PMTiles frente a servir por bbox desde FastAPI) en `research/prototypes/atom_pipeline/README.md`
  y `research/sigpac-atom-campo-cartagena.md`.
- Valores reales de la parcela demo (Torre-Pacheco, 37.7383, -0.98838): recinto 30/37/0/0/18/426/1, 4,0868 ha, pendiente 0,8 % (el
  borrador simulado decia 1,2 %), regadio; ET0 1422 mm/anio; suelo franco-arcillo-limoso, pH 7,97, MO 2,14 %, agua 44,9 mm.

## Licencias y citas (para `submission/`, campos *NASA Data* y *Space Agency Partner & Other Data*)

Datos:

| Dato | Licencia / atribucion |
|---|---|
| ATOM SIGPAC (FEGA) https://www.fega.gob.es/atom/ | CC BY 4.0 (terminos FEGA 2026). "Fuente de los datos: FONDO ESPAÑOL DE GARANTÍA AGRARIA O.A."; indicar transformacion y fecha |
| NASA POWER (MERRA-2 / IMERG) https://power.larc.nasa.gov/ | Datos abiertos NASA. "NASA Prediction Of Worldwide Energy Resources (POWER)"; citar DOI de MERRA-2 (GMAO) |
| GPM IMERG (NASA/JAXA) https://gpm.nasa.gov/data/imerg | Datos abiertos NASA; citar el DOI del producto (GES DISC) |
| Open-Meteo (ERA5, ET0) https://open-meteo.com/ | Datos CC BY 4.0, "Weather data by Open-Meteo.com". **API gratuita solo para uso no comercial** (vale para el hackathon). Origen ERA5: "Generated using Copernicus Climate Change Service information" |
| SoilGrids 2.0 (ISRIC) https://soilgrids.org/ | CC BY 4.0. Poggio, L., et al. (2021), SOIL 7, 217-240, https://doi.org/10.5194/soil-7-217-2021 |
| Saxton y Rawls (2006), SSSAJ 70:1569-1578 | Ecuaciones publicadas, implementadas con codigo propio. El triangulo textural USDA tambien es codigo propio |

Librerias (`requirements.txt`; licencias leidas de los metadatos de los paquetes, sin auditar dependencias transitivas):

| Libreria | URL | Licencia |
|---|---|---|
| pyogrio 0.13.0 (incluye GDAL 3.12.4) | https://github.com/geopandas/pyogrio | MIT (GDAL: MIT/X) |
| Shapely 2.2.0 (incluye GEOS 3.14.1) | https://github.com/shapely/shapely | BSD-3-Clause (GEOS: LGPL-2.1) |
| NumPy 2.4.6 | https://numpy.org/ | BSD-3-Clause |
| jsonschema 4.26.0 (solo validacion) | https://github.com/python-jsonschema/jsonschema | MIT |

Ninguna fuente necesita clave; no se usa el token de Earthdata ni `.env`.

## Pendiente (no hecho en esta tarea)

- Heladas y calor reales de SIAM (T-014) en lugar del `dias_helada` provisional.
- Endpoints FastAPI (`/recinto`, `/recintos`, `POST /analyze`) en `app/backend/` y carga del indice ATOM al arrancar; esta carpeta es solo la libreria.
- Bloque `historia` (SIGPAC `cd_2025` / FEGA) y `zonas` (nitratos / Mar Menor); descarga reproducible del ATOM para Cartagena y Fuente Alamo.
- Anadir `open-meteo` a `fuentes[]` del contrato (entrada lista en `fuentes_nuevas`) y las filas de la tabla anterior a `submission/data-citations.md`.
- Uso en vivo: llamadas en paralelo, cola global para SoilGrids, fallback si POWER/Open-Meteo no responden, cache compartida.
