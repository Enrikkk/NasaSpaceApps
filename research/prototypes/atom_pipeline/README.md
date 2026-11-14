# Prototipo: recintos SIGPAC desde el ATOM del FEGA (sin API en vivo)

PROTOTIPO de preparacion para T-011 (no es codigo de `app/`). Convierte los ZIP GPKG oficiales del ATOM del FEGA
(campana 2026, validez 2025-12-15, CC BY 4.0) en GeoJSON comprimido + indice, y los consulta en memoria
(punto -> recinto, bbox -> recintos). Contexto y condiciones de uso: `research/sigpac-atom-campo-cartagena.md`.

**Atribucion obligatoria** (en la app y en `submission/`): "Fuente de los datos: FONDO ESPAÑOL DE GARANTÍA AGRARIA O.A."
Licencia CC BY 4.0, indicar que los datos estan transformados y la fecha de extraccion. Sin logo ni sugerir respaldo del FEGA.

## Ejecutar

```bash
python3 -m venv /ruta/venv && /ruta/venv/bin/pip install -r requirements.txt        # pyogrio, shapely, numpy
# ZIP en un directorio FUERA del repo (ATOM: https://www.fega.gob.es/atom/2026/rec_2026/30%20-%20MURCIA/ ; descargas grandes de noche)
/ruta/venv/bin/python build_recintos.py --src /ruta/zips --out /ruta/build [--municipios 30037,30045] [--bbox minx,miny,maxx,maxy]
/ruta/venv/bin/python lookup.py --data /ruta/build --point 37.7383 -0.98838
ATOM_BUILD_DIR=/ruta/build /ruta/venv/bin/python -m unittest discover -s tests -v   # o ATOM_SRC_DIR=/ruta/zips (construye 30037+30045)
```

Los ZIP se leen directamente (`/vsizip/`), sin extraer. No se ejecuta nada de lo descargado. La salida (`/ruta/build`) no va al repo.
`sample/` trae solo una muestra de 60 kB (66 recintos alrededor de la parcela demo) y el bloque `parcela` resultante.

## Que genera

Por municipio (codigo SIGPAC = `30` + 3 cifras, ojo: no siempre INE; ver informe): `CODIGO_recintos.geojson.gz` (un feature por linea,
sigue siendo GeoJSON valido, 6 decimales, geometrias validas via `shapely.set_precision`), `CODIGO.index.json` y un `index.json` global
(atribucion, tablas de codigos uso/incidencia/region leidas del propio GPKG, estadisticas por uso). Propiedades: `ref`
(`30/37/0/0/18/426/1`), `ha` (m2/10000), `pend_pct` (milesimas/10), `uso`, `coef_reg` (0-100, se omite si nulo), `alt`, `region`, `inc[]`.

`lookup.py`: `RecintoIndex.load(dir)`, `recinto_por_punto(lat, lon, tol_m=0, detalle=False)` devuelve el bloque `parcela` del contrato v1
(valida contra `contract.schema.json`; `_status: "precalculado"`, `fuente_id: "sigpac"`, `zonas: []` porque no sale del ATOM; `id`
= `30-37-0-0-18-426-1`) y `recintos_en_bbox(bbox)` / `recintos_en_bbox_json(bbox)` (FeatureCollection con la atribucion).

Parcela demo (lat 37.7383, lon -0.98838) = 30/37/0/0/18/426/1: ha 4,0868, pendiente 0,8 %, TA, regadio 100, altitud 53, region 7,
incidencia 221. Coincide con la respuesta de `recinfobypoint` (1 peticion, guardada en `tests/fixtures/`): mismos atributos, geometria con
IoU 0,9995 (efecto del redondeo a 6 decimales). Nota: el borrador del contrato dice pendiente 1,2 % (dato simulado); el real es 0,8 %.

## Resultados medidos (portatil, Python 3.11, 5 municipios pequenos, 14-11-2026)

| Municipio (codigo) | Recintos | GeoJSON | gzip | Construccion |
|---|---|---|---|---|
| Torre-Pacheco (30037) | 29 859 | 26,22 MB | 5,25 MB | 4,66 s |
| San Javier (30035) | 13 254 (1 astilla de 0,4 m2 descartada) | 11,10 MB | 2,25 MB | 1,90 s |
| La Union (30041) | 2 515 | 2,86 MB | 0,59 MB | 0,51 s |
| San Pedro del Pinatar (30036) | 2 925 | 2,40 MB | 0,47 MB | 0,43 s |
| Los Alcazares (30045) | 1 815 | 1,54 MB | 0,30 MB | 0,26 s |
| **Total** | **50 368** | **44,1 MB** | **8,9 MB** | **7,8 s** |

- ~876 B/recinto sin comprimir, ~176 B con gzip; ~0,15 ms de construccion por recinto; pico de RAM al construir Torre-Pacheco: 168 MB.
  Tras el redondeo, 41 recintos de Torre-Pacheco (22 en San Javier) pasan a MultiPolygon; la superficie total cambia 0,04 %.
- Carga en memoria de `lookup.py` (STRtree + lineas ya serializadas): 30 037 -> 0,61 s y +61 MB; los 5 municipios -> 1,0 s y +102 MB
  (~2 KB/recinto). Extrapolado: Campo de Cartagena (~165 mil) ~3-4 s y ~330 MB; con Murcia entero (~360 mil) ~7 s y ~730 MB.
- `recinto_por_punto`: 0,05 ms por consulta. `recintos_en_bbox_json`: viewport de ~1 km 170 recintos, 0,14 MB (0,03 MB gzip), 0,3 ms;
  de ~5 km 2 980 recintos, 2,8 MB (0,57 MB gzip), 4 ms; Torre-Pacheco entero 32 ms y 26 MB (5,3 MB gzip).
- Extrapolacion a Cartagena+Fuente Alamo+San Javier+San Pedro+La Union+Alcazares+Torre-Pacheco: ~145 MB GeoJSON, ~29 MB gzip, ~25 s de build.

## Servir recintos al globo MapLibre desde FastAPI

`tippecanoe`: no esta instalado en el equipo. Existe una rueda en PyPI (`tippecanoe` 2.72.0, autor Ryan Mast, BSD, enlaza a
https://github.com/felt/tippecanoe) que se instalaria en un venv sin sudo, y tambien se puede compilar (hay gcc/g++/make/cmake y cabeceras de
zlib y sqlite3). NO se ha instalado ni ejecutado: es un binario o codigo de terceros y queda pendiente de que un humano lo apruebe
(solo se descargo la rueda para leer sus metadatos y se borro).

| Opcion | Medido | Pros | Contras |
|---|---|---|---|
| A. FastAPI: GeoJSON por bbox desde memoria (STRtree) | 0,3-4 ms de servidor; 0,03 MB (1 km) a 0,57 MB gzip (5 km); ~2 KB RAM/recinto | Cero herramientas extra, misma indexacion que el punto->recinto, atributos completos, se puede limitar con `limit` | Hay que pedir al mover el mapa; no sirve a zoom bajo (>10 km: 26 MB/municipio); necesita el backend vivo |
| B. PMTiles generado con GDAL (driver `PMTiles` de pyogrio, sin tippecanoe) | Torre-Pacheco z10-15: 10,6 MB, 24 s; 5 municipios z10-15: 18,0 MB, 38 s (357 B/recinto; Cartagena+resto ~59 MB, ~2 min); Torre-Pacheco z12-14: 6,3 MB, 12 s | Fichero estatico, offline, MapLibre lo pinta sin consultas; funciona sin backend | GDAL no simplifica ni descarta por zoom: a z10-12 las teselas pesan hasta 470 KB gzip (avisa de "tile > 500000 B"); usar z>=12-13 |
| C. tippecanoe -> PMTiles | no medido | Mejor control de simplificacion/densidad | Binario de terceros sin aprobar |

**Recomendacion: A para T-011** (menos piezas, cifras mucho mejores a zoom de parcela, mismo indice que `recinto_por_punto`), con
tope de bbox (~5 km o ~3 000 recintos) y compresion gzip en FastAPI; y **B como respaldo offline/demo**, solo z12-15 (~6-12 MB por
municipio grande) si el venue no tiene Wi-Fi o si el globo necesita la capa sin backend. En la demo, cargar el municipio en memoria
al arrancar (1-4 s).

## Limitaciones

- Datos del ATOM: campana 2026, validez 2025-12-15; no traen cultivo declarado (esta en `cd_2025`, otro esquema) ni zonas
  (nitratos, Mar Menor): `zonas` va vacio.
- Nombres de municipio solo para los 8 codigos verificados; el resto sale sin `municipio`. `comarca` = "Campo de Cartagena" es un supuesto
  para 7 codigos (sin Murcia), no viene del ATOM.
- `pendiente_media` en milesimas esta inferido de un recinto (8 -> 0,8 % en la API) y confirmado en un unico contraste; no se leyo
  el diccionario oficial del GPKG.
- Solo se probaron 5 municipios (<20 MB). Cartagena, Fuente Alamo y Murcia (descarga grande, fuera de 8:00-18:00) no se han descargado ni
  medido; sus cifras son extrapolaciones.
- Redondeo a 6 decimales (~0,1 m): geometrias validas pero no identicas (IoU 0,9995 con la API); astillas < 1 m2 pueden desaparecer.
- Salida en lon/lat ETRS89 (EPSG:4258), tratada como WGS84 (diferencia de decimetros, irrelevante en esta escala).
- La carga lee todo a memoria; sin carga perezosa ni concurrencia probada. Es sincrona y de un solo proceso.

## Licencias de las librerias usadas

| Libreria | URL | Licencia |
|---|---|---|
| pyogrio 0.13.0 (incluye GDAL 3.12.4) | https://github.com/geopandas/pyogrio | MIT (GDAL: MIT/X) |
| Shapely 2.2.0 (incluye GEOS 3.14.1) | https://github.com/shapely/shapely | BSD-3-Clause (GEOS: LGPL-2.1, biblioteca dinamica de la rueda) |
| NumPy 2.4.6 | https://numpy.org/ | BSD-3-Clause (y 0BSD, MIT, Zlib, CC0 de componentes) |
| jsonschema 4.26.0 (solo tests, opcional) | https://github.com/python-jsonschema/jsonschema | MIT |
| pmtiles 3.8.1 (solo para inspeccionar .pmtiles, opcional) | https://github.com/protomaps/pmtiles | BSD-3-Clause |

Licencias leidas de los metadatos de los paquetes instalados; no se ha auditado la licencia de sus dependencias transitivas.
Anotar estas filas en `submission/` al pasar a `app/`.

## Que falta para pasarlo a `app/backend/pipeline/` (cuando se reclame T-011)

1. Reclamar T-011 y acordar la ruta (`app/backend/pipeline/` + endpoints en `app/backend/`); no hay tarea ni ownership hoy.
2. Script de descarga reproducible del ATOM (nocturno, a directorio ignorado) + Cartagena (30016), Fuente Alamo (30021) y, si se quiere,
   Murcia (30030) recortada con `--bbox`; medir de verdad esas cifras. Confirmar el codigo SIGPAC de Santomera si se incluye.
3. Endpoints FastAPI: `GET /recinto?lat&lon` (con `tol_m` opcional) y `GET /recintos?bbox=..&limit=..` con gzip, CORS y cabeceras de cache;
   carga del indice una vez al arrancar (`lifespan`) y ruta de datos por variable de entorno; opcion de servir un `.pmtiles` estatico.
4. Completar `zonas` (nitratos / Mar Menor) con la capa que corresponda, `cultivo declarado` desde `cd_2025`, y decidir el formato de
   `id` y el valor de `_status` con jaime (contrato v1).
5. Tests dentro de `app/` (los de aqui con datos reales no deben depender de la red ni de datos en el repo), `.gitignore` del directorio de
   datos, anadir las filas de `submission/data-citations.md` (ATOM, licencias de librerias) y la atribucion en la interfaz.
6. Decidir con un humano: instalar/compilar tippecanoe (opcion C), y la respuesta del FEGA sobre `recinfobypoint` ya no seria necesaria
   para la demo si esto sustituye a la API en vivo.
