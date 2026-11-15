# T-013 Meses de suelo desnudo desde NDVI de satélite (HLS)

Estado: **solo preparación**. No se ha descargado ningún dato de satélite ni se ha hecho ninguna petición con credenciales.
Los tests usan arrays sintéticos. Hasta que existan datos reales, el bloque `ndvi` del demo sigue siendo el mock
(`_status: "precalculado"` o el mock original). Nunca debe etiquetarse `real` algo que no salga de una descarga real.

## Qué hay
| Archivo | Qué hace |
|---|---|
| `bare_soil.py` | Funciones puras: `ndvi`, máscara Fmask, media de parcela por fecha, agregación mensual, clasificación, `ndvi_block`, `bare_run_days` / `bare_run_range` (días desnudos consecutivos en oct-mar). |
| `appeears_request.py` | Cuerpo JSON de la tarea *point* de AppEEARS, `main()` (solo imprime) y `submit()`, `get_status()`, `download_bundle()` (red + credenciales, nunca llamadas por tests). |
| `appeears_csv.py` | Puente CSV de AppEEARS a `[(fecha, NDVI parcela)]`. Nombres de columna **sin verificar**. |
| `tests/test_bare_soil.py` | 50 tests sintéticos (con parametrizados) (año con suelo desnudo jul-sep, nubes, mes con 1 observación, límites de umbrales, ventana oct-mar). |

Ejecutar: `python3 -m pytest -q app/backend/ndvi app/backend/engine`. Ver la petición: `python3 -m app.backend.ndvi.appeears_request`.

## Qué se verificó contra documentación oficial (leída el 2026-11-14)
- **Bits de Fmask**: HLS V2.0 User Guide (abril 2026), sección 6.4, Tabla 9, https://lpdaac.usgs.gov/documents/1698/HLS_User_Guide_V2.pdf .
  Bit 0 cirro (reservado, no usado), 1 nube, 2 adyacente a nube/sombra, 3 sombra, 4 nieve/hielo, 5 agua, 6-7 nivel de aerosol.
  "Los seis bits bajos pueden no ser excluyentes". Las nubes se dilatan 150 m (5 píxeles) y esa dilatación es el bit 2 (sección 4.2).
  Reflectancia int16, factor 0,0001, relleno -9999; Fmask uint8, relleno 255 (Tablas 6 y 7). NIR: B05 en HLSL30, B8A en HLSS30; rojo B04 en ambos.
  Errata de la guía: la Tabla 9 dice aerosol 10 = bajo, 01 = medio, pero el ejemplo del Apéndice A trata 01 como bajo. No afecta: no usamos los bits 6-7.
- **API de AppEEARS**: https://appeears.earthdatacloud.nasa.gov/api/ . `POST /login` (Basic, token ~48 h), `POST /task` (HTTP 202, `task_id`),
  `GET /status/{id}`, `GET /bundle/{id}`, `GET /bundle/{id}/{file_id}` (302 a URL S3 prefirmada, 48 h). Esquema *point*: `task_type`,
  `task_name`, `params.dates[{startDate,endDate}]` en `MM-DD-YYYY`, `params.layers[{product,layer}]`, `params.coordinates[{latitude,longitude,id,category}]`.
- **Productos y capas** (catálogo público, sin login): https://appeears.earthdatacloud.nasa.gov/api/product . AppEEARS los llama
  **`HLSL30.020`** (capas B04, B05, Fmask) y **`HLSS30.020`** (B04, B8A, Fmask), no `.002` como decía el encargo (`.002` da 404). Existen
  `HLSL30_VI.020` / `HLSS30_VI.020` con capa `NDVI`, pero **sin capa de calidad** (`IsQA` falso), así que no se podrían enmascarar nubes:
  por eso se piden las bandas y se calcula el NDVI aquí. Fmask decodificado: https://appeears.earthdatacloud.nasa.gov/api/quality/HLSS30.020/Fmask .

## Qué NO se pudo verificar
- Nombres exactos de las columnas del CSV de salida y si el CSV trae la reflectancia ya escalada o el entero crudo (el lector tolera ambos). Ajustar `appeears_csv.py` tras la primera descarga real.
- Si AppEEARS acepta un token de usuario de Earthdata (`EARTHDATA_TOKEN`) o solo el token de `POST /login`. `submit()` usa usuario/contraseña por defecto.
- Límites de tamaño de las tareas *point*, tiempos de cola y tamaño real de la descarga (las estimaciones de abajo son mías).
- Que la cuadrícula 3x3 a 30 m (60 x 60 m) caiga dentro de la parcela SIGPAC 18/426/1: comprobar con el polígono. Un punto AppEEARS es un solo píxel de 30 m.
- URLs de registro de Earthdata y CDSE (de memoria, no abiertas) y si AppEEARS pide aceptar condiciones adicionales en el primer acceso.
- Calidad de Fmask: la documentación de LP DAAC avisa de problemas conocidos en HLSL30 anteriores a abril de 2022 y de errores de agua/sombra en relieve fuerte; nuestro rango empieza en 2024.

## Umbrales (SUPUESTO de diseño, no medidos)
| Clase | NDVI mediano mensual | Fuente |
|---|---|---|
| `desnudo` | < 0,20 | Supuesto. Contexto verificado: NASA Earth Observatory (https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi) dice "valores muy bajos (0,1 o menos) = roca, arena o nieve" y "matorral y pastizal 0,2 a 0,3". Un resumen EGU21-11153 (Dvorakova y van Wesemael) usa NDVI < 0,25 para suelo expuesto en cultivos, y una revisión (Remote Sensing 14(18):4526) lista 0,25, 0,27 y 0,20 en distintos estudios: **solo leí los resúmenes de búsqueda, no los artículos**. Los umbrales varían por sitio y método. |
| `vulnerable` | 0,20 a < 0,35 | Supuesto, cobertura baja. **Sin fuente verificada para 0,35.** |
| `cubierto` | >= 0,35 | Supuesto, sin fuente verificada. |
| `sin_dato` | < 2 fechas despejadas en el mes | Supuesto de diseño (`MIN_CLEAR_DATES`). Además, una fecha con < 50 % de píxeles útiles cuenta como nublada. |

Calibrar con la serie real de la parcela (un suelo oscuro y húmedo, el acolchado plástico o una cubierta marchita pueden salirse de estos rangos).
Con píxeles de 30 m, una parcela de 4,1 ha tiene unos 45 píxeles y los de borde mezclan vecinos.

## Salida: bloque `ndvi`
Forma exacta del mock (`fuente`, `meses_desnudo[]`, `meses_vulnerable[]`, meses `YYYY-MM`) más `meses_sin_dato[]`,
`n_observaciones` (`{mes: fechas despejadas}`) y `_status` (`real` | `precalculado`).
`bare_run_days(bloque, año_invierno, unknown="break"|"bare")` devuelve el tramo desnudo más largo entre oct del año y mar del siguiente;
`bare_run_range` da (mínimo, máximo) tratando los meses sin dato como no desnudos / desnudos.
**Aviso para `rules.py`**: la granularidad es mensual, así que "2 meses completos" son 59 a 62 días (oct+nov = 61, ene+feb = 59) frente a
`BARE_LIMIT_DAYS = 60`. Decidir en el motor si el aviso salta con `> 62` (3 meses) o se acepta el ruido de un día.

## Pasos que debe hacer el humano
1. Crear cuenta gratuita de NASA Earthdata Login (https://urs.earthdata.nasa.gov/users/new) y confirmar el correo. Unos 5 min.
2. Entrar una vez en https://appeears.earthdatacloud.nasa.gov/ con esa cuenta y aceptar los términos o autorizar la app si los pide.
3. Opción A (navegador): *Extract > Point Samples > Start a new request*; pegar las coordenadas de `python3 -m app.backend.ndvi.appeears_request`,
   fechas 09-01-2024 a 10-31-2026, las 6 capas listadas, formato CSV, enviar.
   Opción B (script): `export EARTHDATA_USER=... EARTHDATA_PASS=...` en la terminal (nunca en un archivo ni en el chat) y llamar a `submit()`; después `get_status(id)` y `download_bundle(id, "app/data/cache/ndvi")`.
4. Esperar a que la tarea pase a `done` (minutos a unas horas, colas impredecibles; PLAN.md propone lanzarlo ya).
5. Dejar los CSV en `app/data/cache/ndvi/` y avisar al agente.
6. Opcional, Copernicus Data Space (https://dataspace.copernicus.eu/): solo como plan B con Sentinel-2 a 10 m; no hay código para ello todavía.

Tamaño esperado (estimación, no verificada): 9 puntos x ~2 años x ~100-200 fechas por producto = unos miles de filas, del orden de 1 MB de CSV. El tiempo lo domina la cola.

## Qué pasa cuando haya credenciales
1. `build_request()` a `submit()` a `download_bundle()` (o descarga manual).
2. `appeears_csv.load_csv(...)` para cada CSV, juntar las listas, `monthly_aggregate(obs, "2024-09", "2026-10")`, `ndvi_block(meses, "real")`.
3. Contrastar con el mock (oct 2025 a feb 2026 desnudo, ago 2025 vulnerable). Si no coincide, ajustar umbrales y documentarlo; el mock deja de ser verdad.
4. Guardar el JSON en `app/data/cache/ndvi/` y que el demo lo lea (precalculado offline, como pide la tarea); pasar `bare_run_days` a `rules.py`/semáforo.
Nada de esto ocurre sin los CSV.
