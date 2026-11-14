# Agrockham API integrada (prototipo de preparación, D-009)

Une en **una** API FastAPI los cuatro prototipos de `research/prototypes/` (`api_skeleton`, `atom_pipeline`,
`pipeline_clima_suelo`, `legal_rules`). `POST /analyze {lat, lon, recinto?}` devuelve el contrato v1 por bloques con datos
**reales donde ya existen** y el borrador simulado en el resto. Sucesor de `api_skeleton` (mismos `/health`, `/analyze`,
`/parcel/{id}`, mismo `?bloques=`; añade `/recintos` y los bloques reales). **No está en `app/` ni en `coordination/`,
no se ha desplegado nada, no usa `.env` ni secretos.**

## Ejecutar

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt          # .venv está en .gitignore
ATOM_BUILD_DIR=/ruta/atom_out/build .venv/bin/uvicorn main:app --reload --port 8080   # http://localhost:8080/docs
.venv/bin/python -m pytest -q                                                    # 84 tests (2 omitidos sin ENRIQUE_JSON)
.venv/bin/python smoke.py http://127.0.0.1:8080                                  # prueba real + latencias + validación contra el esquema
```

Arranque de producción (Cloud Run): `uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}`.
Imagen: ver la cabecera del `Dockerfile` (hay que copiar los GeoJSON de ATOM a `./atom_build`; está en `.gitignore`).
Probada en local (`docker build` + `docker run`, no se subió a ningún registro): 325 MB, usuario uid 10001, arranca en ~1 s con los 50 368 recintos.

## Endpoints

| Endpoint | Qué hace |
|---|---|
| `GET /health` | `{status:"ok", version, recintos:{cargado, n, municipios, segundos_carga}}`; si no hay recintos añade `avisos[]` (sigue en `ok`: la API arranca igualmente) |
| `POST /analyze[?bloques=a,b]` | contrato v1 por bloques. `bloques` ⊂ `parcela,historia,ndvi,clima,suelo,rotaciones`; los no pedidos salen `{"_status":"cargando"}` (`rotaciones: []`) |
| `GET /parcel/{id}` | último contrato de esa consulta (`parcela.id` o `_meta.consulta_id`), fusionando peticiones por bloques. En memoria del proceso (no compartida entre instancias) |
| `GET /recintos?bbox=minlon,minlat,maxlon,maxlat` | GeoJSON de los recintos que intersecan el rectángulo, para el globo |

### `POST /analyze`

```json
{"lat": 37.7383, "lon": -0.98838,
 "recinto": {"provincia": 30, "municipio": 37, "agregado": 0, "zona": 0, "poligono": 18, "parcela": 426, "recinto": 1},
 "zona": "por_verificar"}
```
- `lat`/`lon` obligatorios y finitos. `recinto` opcional: **objeto** (no cadena) con enteros ≥ 0 opcionales; `zona` opcional
  (`zona_1 | zona_2 | por_verificar`, por defecto `por_verificar`) = zona legal del Mar Menor para el semáforo. Campos extra o valores
  fuera de rango: **422** sin eco del valor.
- **Acuerdo con Arturo sobre `recinto`:** `_meta.consulta.recinto` repite **solo los componentes enviados** (un componente omitido
  no aparece nunca; un `0` solo aparece si vino `0` explícito; `null` = omitido). Si no se envía `recinto`, la clave tampoco aparece.
  `_meta.consulta.recinto_completo` = `true` solo si vinieron **los 7 componentes**. Si se envía algún componente, se compara con el
  recinto que contiene el punto: `_meta.consulta.recinto_coincide` (bool) y un aviso si difiere (se devuelve el recinto del punto).
- `parcela.sigpac` lleva los 7 componentes del recinto encontrado (`provincia, municipio, agregado, zona, poligono, parcela, recinto`).
- `_meta` añade: `estado_bloques`, `bloques_pendientes` (en carga y que pueden llegar), `bloques_sin_datos` (vacíos que **no** van a
  llegar: sin recinto, SoilGrids sin dato), `cobertura {nivel, ambito}`, `consulta`, `consulta_id`, `avisos[]`, `atribuciones[]`,
  `latencia_ms`, `motor`, `aviso` (MOCK parcial, nombra los bloques simulados) y `aviso_legal`.
- **Fuera de cobertura:** si el punto no cae en ningún recinto cargado (otro municipio, camino, mar…) `parcela` sale
  `{"_status":"cargando","sin_cobertura":true,"aviso":"..."}` (válido según el esquema), `bloques_sin_datos:["parcela"]`,
  `cobertura.nivel:"basico"`, aviso, y **todos los semáforos legales en gris** (D-009). Clima y suelo siguen siendo reales (fuentes globales).
- Los bloques de clima/suelo que no se pueden dar (red caída, plazo vencido, `AGROCKHAM_OFFLINE=1` sin caché) salen `cargando` con
  `aviso` y sin detalles internos; el cliente reintenta. Si el plazo (`LIVE_DEADLINE_S`) vence, la descarga sigue en segundo plano y
  el siguiente intento sale de la caché.

### `GET /recintos`
`bbox` en grados lon/lat. Respuesta `application/geo+json` (gzip si el cliente manda `Accept-Encoding: gzip`, que los navegadores
mandan siempre) con `attribution`, `n`, `n_total`, `truncado` y `features` (propiedades `ref, ha, pend_pct, uso, coef_reg, alt, region, inc`).
Topes: **3000 recintos** (`RECINTOS_MAX`; si hay más devuelve los 3000 primeros con `truncado:true` y `n_total`) y **5 km** de lado
(`RECINTOS_MAX_KM`, tolerancia 2 %): por encima devuelve `200` con `features:[]`, `truncado:true`, `limite:"extension"` y `aviso`
("Acerca el mapa") en vez de un error, para que el globo pueda pedir en cada `moveend`. `422` para bbox mal formado; `503` si no hay
recintos cargados. `Cache-Control: public, max-age=3600` (datos estáticos, campaña 2026) y cabecera `X-Recintos-Total`.

## Qué es real, precalculado y simulado

| Bloque | `_status` | Origen | Detalle |
|---|---|---|---|
| `parcela` | `precalculado` | ATOM del FEGA (campaña 2026, validez 2025-12-15), convertido offline a GeoJSON | recinto por punto en memoria (0,05 ms). `zonas: []` (el ATOM no trae nitratos ni Mar Menor). Incluye `geometry` del recinto, `uso_sigpac`, `coef_regadio`, `altitud_m`, `incidencias`, `atribucion` |
| `clima` | `real` | NASA POWER (MERRA-2 + IMERG), Open-Meteo (ERA5, ET0 FAO-56) | caché por celda; si falta y hay red, se llama al pipeline. `dias_helada` sigue **provisional** (pendiente SIAM) |
| `suelo` | `real` | ISRIC SoilGrids 2.0 (modelo a 250 m) | caché por celda de 0,0025° |
| `semaforo_legal` (cada rotación) | el de la rotación (hoy `simulado`) | `legal.check()` sobre la rotación, con la zona de la petición | determinista; **todas las reglas `por_verificar`**; `supuestos` explica `ciclos_por_anio = 1` |
| `rotaciones`, `escenarios_meta` | `simulado` | borrador de contrato (o JSON de enrique, ver abajo) | iguales para cualquier punto: son los de la parcela demo |
| `historia`, `ndvi` | `simulado` | borrador | `historia` real vendría de `cd_2025` del FEGA, `ndvi` de T-013 |
| `fuentes[]` | n/a | borrador + `sigpac` reescrita (ATOM, CC BY 4.0, `licencia_estado: ok`, con `atribucion`) + `open-meteo` | |

`_meta.aviso` lleva `MOCK PARCIAL` y nombra los bloques simulados mientras los haya (el validador lo exige). La atribución FEGA
("Fuente de los datos: FONDO ESPAÑOL DE GARANTÍA AGRARIA O.A.", CC BY 4.0, datos transformados) va en `_meta.atribuciones`,
`parcela.atribucion`, `fuentes[sigpac].atribucion` y en cada respuesta de `/recintos`.

El semáforo calculado **difiere del borrador a propósito** (ver `legal_rules/README.md`): con la zona sin verificar todas las
rotaciones demo salen `amarillo`; `zona_2` → `verde, verde, verde`; `zona_1` → `rojo, verde, amarillo`.

## Punto de extensión del motor: `engine_adapter.py`

Los endpoints no cambian al enchufar el motor de enrique. `get_engine(cfg)` elige entre:
1. `DraftEngine` (por defecto): rotaciones del borrador, `simulado`.
2. `JsonFileEngine` con `ENGINE_JSON=/ruta/torre-pacheco.json`: lee el JSON de enrique (`git show origin/t012-motor-nucleo:app/data/torre-pacheco.json`)
   y lo convierte con `adapt_enrique()`: `escenarios`→`escenarios_margen_eur_ha`, `plan_anios[].ciclos`→`anios` (lo lee `legal.check`, así no hace
   falta el supuesto de ciclos por año), `_status` ← su `_estado_bloques.rotaciones`, `escenarios_meta` sintetizado, su `semaforo_legal` se
   descarta (se recalcula), y se ignoran sus `parcela/historia/ndvi/clima/suelo` (la API sirve los suyos). Si el fichero no carga, cae al borrador con un error en el log.
3. Futuro: `LiveEngine.run(EngineInput)` llamando a `run(parcela, clima, suelo)` de enrique por punto; `EngineInput` ya lleva los bloques reales.

Probado con la rama de enrique @ hoy (4 rotaciones `actual, s1, s2, s3`, 200 muestras cada una): carga, semáforo recalculado con sus años del plan y
la parcela/clima/suelo reales de la API. Con su JSON enchufado quedan **36 errores de esquema v1** (informativos, en `tests/test_engine_adapter.py -s`),
todos de la lista `research/contract-v1-draft/DIFERENCIAS-con-torre-pacheco-json.md` (`agua_detalle.bruto_m3_ha` en percentiles, `null` en `coste_eur_ha`/`sobreoferta`,
`peores_anios` como números, `sobreoferta_detalle._status: "pendiente"`) que el esquema v1.1 debe aceptar. Hay un `research/contract-v1-draft/v1.1/adapt_enrique.py` sin versionar de otro
agente: **al aterrizar v1.1, sustituir `adapt_enrique()` por el suyo** (misma firma de salida: rotaciones + escenarios_meta).

## Variables de entorno

| Variable | Por defecto | Uso |
|---|---|---|
| `PORT` | `8080` | puerto de uvicorn (Cloud Run lo inyecta) |
| `ATOM_BUILD_DIR` | scratchpad de desarrollo de gonzalo; en Docker `/data/atom` | GeoJSON de ATOM (`*_recintos.geojson.gz` + `*.index.json`). Si no existe, la API arranca y avisa |
| `FRONTEND_ORIGIN` | vacío | orígenes CORS extra, separados por comas, sin `/` final (se ignora `*`). Siempre `http://localhost:5173`. Sin credenciales, solo GET/POST |
| `GIT_SHA` | `dev` | versión de `/health` |
| `ENGINE_JSON` | vacío | JSON de enrique (ver arriba) |
| `CONTRACT_PATH` | `data/torre-pacheco.contract-v1.draft.json` | borrador que sirve el motor por defecto |
| `PIPELINE_CACHE_DIR` | `<tmp>/agrockham-pipeline-cache` | caché de ejecución de clima/suelo; se siembra con `data/pipeline_cache/` (parcela demo) |
| `AGROCKHAM_OFFLINE` | sin definir | `1` prohíbe la red del pipeline (sin caché → bloque `cargando`). Los tests lo ponen siempre |
| `LIVE_HTTP_TIMEOUT_S` / `LIVE_RETRIES` | `40` / `1` | red en vivo acotada (el pipeline por defecto espera hasta 120 s y reintenta 4 veces con 130 s de esperas) |
| `LIVE_DEADLINE_S` | `60` | plazo total por bloque de clima/suelo; vencido → `cargando` y sigue en segundo plano |
| `RECINTOS_MAX` / `RECINTOS_MAX_KM` | `3000` / `5` | topes de `/recintos` |
| `CACHE_MAX` | `256` | entradas de `/parcel/{id}` |

## Pruebas y mediciones (portátil de gonzalo, 14-nov-2026, 5 municipios = 50 368 recintos)

- `pytest`: **82 pasan, 2 omitidos** (los 2 que necesitan `ENRIQUE_JSON`; con él, **84/84**). Sin red (`AGROCKHAM_OFFLINE=1`) y con las cachés existentes;
  `TEST_LIVE=1` la permite. Usan los municipios completos si existe `ATOM_BUILD_DIR` y una muestra de 66 recintos (de `atom_pipeline/sample`) para el resto.
  Cubren: validez contra `contract.schema.json` + las 12 invariantes de `validate.py` en cada tipo de respuesta, recinto parcial/cero/`null`/completo/discordante, 422,
  cobertura (fuera, sin recinto, sin ATOM, ATOM corrupto), `?bloques=` y fusión, `/recintos` (topes, gzip, CORS, bbox inválido), semáforo por zona,
  clima/suelo en vivo simulados (plazo, errores sin filtrar detalles, caché), y **divergencia de las copias** (`test_vendor_sync.py`).
- **Real con `uvicorn` + `smoke.py`** (todas las respuestas validadas: 0 errores de esquema, 0 invariantes fallidas):

| Petición | Latencia |
|---|---|
| `/analyze` parcela demo, recinto completo (todo en caché) | 13-19 ms de extremo a extremo (servidor: parcela 0,3 ms, clima+suelo ~8 ms en paralelo, rotaciones+legal 1,5 ms); 41 kB |
| `/analyze?bloques=parcela` | 4-5 ms, 6 kB |
| punto fuera de cobertura con caché | 13-26 ms (parcela `cargando` + aviso, semáforos gris) |
| punto fuera de cobertura **sin caché** (Albacete rural, red real) | **8,7 s** (clima 3,8 s, suelo 8,6 s con SoilGrids); repetido: 26 ms. Si SoilGrids acaba de usarse, sube a ~18 s por su límite de 5 llamadas/min |
| `/recintos` viewport de 1 km | 7 ms, 188 recintos, 27 kB gzip |
| `/recintos` viewport de 5 km | 44 ms, 3000 de 5127 recintos (truncado), 2,5 MB sin comprimir |
| rectángulo de 8 km | 4 ms, vacío + aviso |
| carga de los 5 municipios al arrancar | ~1,05 s (RAM ~+100 MB según `atom_pipeline`; no re-medida aquí) |

- Puntos urbanos (Murcia ciudad, Valladolid centro) devuelven `suelo` sin datos de SoilGrids → `suelo: cargando` + `sin_datos:true` + aviso; no es un fallo.

## Limitaciones y honestidad

- `rotaciones`, `historia` y `ndvi` son del **borrador** y no corresponden al punto: están marcados `simulado` y el aviso `MOCK PARCIAL` lo dice. No hay motor por punto todavía.
- Cobertura = municipios cargados (San Javier, San Pedro, Torre-Pacheco, La Unión, Los Alcázares). Cartagena y Fuente Álamo (Campo de Cartagena) **no están descargados**: sus puntos salen `basico`. La caja de cobertura es la del municipio (no su límite administrativo exacto).
- El semáforo legal depende de reglas **sin verificar en el BOE** y de la zona (Anexo I sin leer): por eso `por_verificar` por defecto. No es asesoría legal.
- `clima.dias_helada` provisional y `dias_calor_gt_38` subestimado (MERRA-2 a ~50 km): faltan los datos de SIAM (T-014).
- La caché de `/parcel/{id}` y la de clima/suelo en disco son por instancia (Cloud Run con varias instancias: cada una calienta la suya; `/tmp` se pierde al reiniciar salvo la parcela demo, que se resiembra).
- Licencia/condiciones de Open-Meteo: la API gratuita es **solo no comercial** (vale para el hackathon; ver `pipeline_clima_suelo/README.md`).
- Sin límite de peticiones: una ráfaga de puntos nuevos satura las APIs externas (SoilGrids 5/min por IP; en Cloud Run la IP de salida es compartida). Precalentar celdas del Campo de Cartagena antes de la demo.

## Copias y origen (no duplicar a mano; `tests/test_vendor_sync.py` falla si divergen)

| Copia aquí | Origen | Cambios |
|---|---|---|
| `vendor/pipeline.py` | `pipeline_clima_suelo/pipeline.py` | ninguno (`CACHE_DIR` y los reintentos se fijan desde `live.preparar()`) |
| `vendor/legal.py`, `rules.csv`, `grupos_cultivo.csv` | `legal_rules/` | ninguno |
| `vendor/lookup.py` | `atom_pipeline/lookup.py` | ninguno (`store.Recintos` la extiende por herencia) |
| `data/torre-pacheco.contract-v1.draft.json` | `contract-v1-draft/` | ninguno |
| `data/pipeline_cache/*.json` (224 kB) | `pipeline_clima_suelo/cache/` | ninguno (semilla de la parcela demo) |
| `main.py`, `settings.py` | `api_skeleton/` | adaptados: `recinto` solo objeto, `zona`, `/recintos`, lifespan, gzip, `recinto_completo` |

`build_recintos.py` (ATOM→GeoJSON) **no** va a la imagen: es de preparación offline y necesita `pyogrio`.

## Qué falta para mover esto a `app/backend/` (cuando jaime dé el go y se reclame T-011/T-017/T-019)

Propiedad (`.claude/ownership.json`): gonzalo ya tiene `app/backend/api/`, `pipeline/`, `rules/`, `app/data/cache/pipeline/` y `app/data/contract.schema.json`.

| Origen (`research/prototypes/…`) | Destino |
|---|---|
| `integration/main.py`, `blocks.py`, `settings.py`, `live.py`, `store.py`, `legal_blocks.py`, `engine_adapter.py` | `app/backend/api/` |
| `integration/Dockerfile`, `.dockerignore`, `.gitignore`, `requirements*.txt`, `pytest.ini` | `app/backend/api/` |
| `integration/tests/` (sin `test_vendor_sync.py`) y `smoke.py` | `app/backend/api/tests/` y `app/backend/api/smoke.py` |
| `integration/vendor/pipeline.py` (= `pipeline_clima_suelo/pipeline.py`) | `app/backend/pipeline/pipeline.py` |
| `atom_pipeline/lookup.py`, `build_recintos.py`, `requirements.txt` | `app/backend/pipeline/` (`build_recintos` solo offline) |
| `integration/vendor/legal.py`, `rules.csv`, `grupos_cultivo.csv` (= `legal_rules/`) | `app/backend/rules/` |
| `integration/data/pipeline_cache/*.json` | `app/data/cache/pipeline/` |
| `contract-v1-draft/contract.schema.json` (o la v1.1) y `validate.py` | `app/data/contract.schema.json`; el borrador JSON → `app/data/` |
| datos ATOM (`atom_out/build`, ~9 MB) | fuera del repo (`ATOM_BUILD_DIR`); a la imagen con `COPY atom_build /data/atom` |

Pasos al mover: (1) borrar `vendor/` y cambiar `from vendor import pipeline as P` → `import pipeline as P`, `from vendor import legal as L` → `import legal as L`, `from vendor.lookup import …` → `from lookup import …`
(ajustando `sys.path`/paquetes; el `Dockerfile` copia cada carpeta); (2) que `CONTRACT_PATH`/el esquema salgan de `app/data/`; (3) `tests/conftest.py`: `CONTRACT_DIR` → `app/data/`; (4) escribir las
filas de `submission/data-citations.md` (FEGA ATOM CC BY 4.0, POWER, IMERG, Open-Meteo, SoilGrids, librerías de abajo); (5) cuando exista, enchufar el motor en `engine_adapter.py` y cambiar `rotaciones` de `simulado` a `real`;
(6) cobertura: descargar Cartagena y Fuente Álamo con `build_recintos.py` (de noche) y subir `ATOM_BUILD_DIR`; (7) `gcloud run deploy` lo hace un humano (ver `api_skeleton/README.md`, sección Cloud Run: `--max-instances 3`, `--set-env-vars FRONTEND_ORIGIN=…`); (8) revisar con el FEGA
el uso en producción (ATOM está claro; `recinfobypoint` no se usa) y decidir si el semáforo `gris` del nivel básico es lo que quiere la UI.

## Dependencias y licencias

Versiones fijadas (las de `api_skeleton` y `atom_pipeline`, comprobadas en PyPI el 2026-11-14; licencias leídas de los metadatos instalados). El código propio solo usa la librería estándar además de esto.

| Paquete | Versión | Licencia | Uso |
|---|---|---|---|
| fastapi | 0.162.7 | MIT | framework |
| starlette | 1.10.0 | BSD-3-Clause | base de FastAPI (CORS, gzip) |
| uvicorn | 0.54.0 | BSD-3-Clause | servidor ASGI |
| pydantic / pydantic_core | 2.14.3 / 2.50.4 | MIT | validación |
| numpy | 2.4.6 | BSD-3-Clause (y 0BSD, MIT, Zlib, CC0 de componentes) | índice espacial |
| shapely (incluye GEOS 3.14.1) | 2.2.0 | BSD-3-Clause (GEOS: LGPL-2.1, biblioteca dinámica de la rueda) | recinto por punto y por bbox |
| annotated-types, annotated-doc, anyio, idna, typing-inspection | 0.8.0, 0.0.6, 4.16.0, 3.20, 0.4.5 | MIT / BSD-3-Clause | transitivas |
| click, h11 | 8.5.1, 0.16.0 | BSD-3-Clause, MIT | transitivas (uvicorn) |
| opentelemetry-api | 1.45.2 | Apache-2.0 | transitiva (la trae fastapi 0.162) |
| typing_extensions | 4.16.0 | PSF-2.0 | transitiva |
| pytest / httpx / jsonschema | 9.2.0 / 0.28.1 / 4.26.0 | MIT / BSD-3-Clause / MIT | solo pruebas |

Imagen base `python:3.12-slim` (Docker Official Image). Datos: FEGA ATOM (CC BY 4.0), NASA POWER, GPM IMERG, Open-Meteo (CC BY 4.0, API gratuita no comercial; origen ERA5 de Copernicus C3S),
SoilGrids 2.0 (CC BY 4.0), BOE (Ley 3/2020). Ver `pipeline_clima_suelo/README.md` y `atom_pipeline/README.md` para citas completas; todo `licencia_estado: verify` salvo FEGA ATOM, BOE y propias.
