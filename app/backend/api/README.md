# Agrockham API (T-024, D-009)

API FastAPI en vivo de Agrockham. `POST /analyze {lat, lon, recinto?}` devuelve el **contrato v1.1 por bloques**
(`app/data/contract.schema.json`) con datos **reales o precalculados donde ya existen** y bloques **simulados** (con
`_status: "simulado"` y aviso `MOCK PARCIAL`) en el resto. `GET /recintos` da los recintos SIGPAC al globo.
Vive en `app/backend/api/` (propietario: gonzalo). **No usa `.env` ni secretos y no se ha desplegado nada.**

No duplica código: importa `app.backend.pipeline.atom.lookup` (recintos SIGPAC, T-011), `app.backend.pipeline.clima_suelo.pipeline`
(clima y suelo, T-011) y `app.backend.rules` (semáforo legal, T-019). El prototipo de preparación sigue en `research/prototypes/integration/`
como registro histórico (no se borra; esta carpeta lo sustituye).

## Ejecutar (desde la raíz del repo)

```bash
python3 -m venv /ruta/venv && /ruta/venv/bin/pip install -r app/backend/api/requirements-dev.txt    # venv FUERA del repo (o .venv, ignorado)
ATOM_BUILD_DIR=/ruta/build /ruta/venv/bin/uvicorn app.backend.api.main:app --reload --port 8080    # http://localhost:8080/docs
/ruta/venv/bin/python -m pytest app/backend/api -q                                                  # tests, sin red
/ruta/venv/bin/python app/backend/api/smoke.py http://127.0.0.1:8080 [--sin-red]                    # prueba real + latencias + validación
```

Producción / Cloud Run: `uvicorn app.backend.api.main:app --host 0.0.0.0 --port ${PORT:-8080}` (hay que lanzarlo **desde la raíz**:
el código importa `app.backend...` y lee `app/data/`).

`ATOM_BUILD_DIR` = carpeta con los GeoJSON de ATOM (`*_recintos.geojson.gz` + `*.index.json`), salida de
`python -m app.backend.pipeline.atom.build_recintos --src /ruta/zips --out /ruta/build` (ver `app/backend/pipeline/README.md`;
descargas grandes de noche). Por defecto la API busca `app/backend/api/atom_build/` (ignorada por git). **Si no existe, la API arranca igualmente**:
`/health` avisa, `/recintos` da 503 y `/analyze` sale sin parcela (cobertura básica).

## Endpoints

| Endpoint | Qué hace |
|---|---|
| `GET /health` | `{status:"ok", version, recintos:{cargado, n, municipios, segundos_carga}}`; sin recintos añade `avisos[]` (sigue en `ok`) |
| `POST /analyze[?bloques=a,b]` | contrato por bloques. `bloques` ⊂ `parcela,historia,ndvi,clima,suelo,rotaciones`; los no pedidos salen `cargando` (`historia` y `rotaciones`, que son listas en v1.1, salen `[]`) |
| `GET /parcel/{id}` | último contrato de esa consulta (`parcela.id` o `_meta.consulta_id`), fusionando peticiones por bloques. En memoria del proceso (no se comparte entre instancias) |
| `GET /recintos?bbox=minlon,minlat,maxlon,maxlat` | GeoJSON de los recintos que intersecan el rectángulo, para el globo |

### `POST /analyze`

```json
{"lat": 37.7383, "lon": -0.98838,
 "recinto": {"provincia": 30, "municipio": 37, "agregado": 0, "zona": 0, "poligono": 18, "parcela": 426, "recinto": 1},
 "zona": "por_verificar"}
```
- `lat`/`lon` obligatorios y finitos. `recinto` opcional: **objeto** (no cadena) con enteros ≥ 0 opcionales. `zona` opcional
  (`zona_1 | zona_2 | por_verificar`, por defecto `por_verificar`) = zona legal del Mar Menor para el semáforo. Campos extra o valores fuera de rango: **422** sin eco del valor.
- **Acuerdo con Arturo sobre `recinto`:** `_meta.consulta.recinto` repite **solo los componentes enviados** (un componente omitido no aparece nunca;
  un `0` solo aparece si vino `0` explícito; `null` = omitido; si no se envía `recinto`, la clave tampoco). `_meta.consulta.recinto_completo` = `true`
  solo con **los 7 componentes**. Si se envía algún componente se compara con el recinto que contiene el punto: `_meta.consulta.recinto_coincide` y un aviso si difiere
  (se devuelve el recinto del punto). `parcela.sigpac` lleva siempre los 7 componentes del recinto encontrado.
- `_meta` añade `estado_bloques`, `bloques_pendientes` (en carga y que pueden llegar), `bloques_sin_datos` (vacíos que no van a llegar), `cobertura {nivel, ambito}`,
  `consulta`, `consulta_id`, `avisos[]`, `atribuciones[]`, `latencia_ms`, `motor`, `aviso` (MOCK parcial) y `aviso_legal`.
- **Cobertura completa / básica (D-009).** Completa = el punto cae en un recinto de los municipios cargados. Básica = fuera: `parcela` sale
  `{"_status":"cargando","sin_cobertura":true,"aviso":"..."}`, `bloques_sin_datos:["parcela"]` y **todos los semáforos legales en gris**; clima y suelo siguen siendo reales (fuentes globales).
- Clima/suelo no disponibles (red caída, plazo vencido, `AGROCKHAM_OFFLINE=1` sin caché) salen `cargando` con `aviso` y sin detalles internos; el cliente reintenta.
  Si vence `LIVE_DEADLINE_S` la descarga sigue en segundo plano y el siguiente intento sale de la caché.

### `GET /recintos`
`bbox` en grados. Respuesta `application/geo+json` (gzip si el cliente manda `Accept-Encoding: gzip`) con `attribution`, `n`, `n_total`, `truncado` y
`features` (propiedades `ref, ha, pend_pct, uso, coef_reg, alt, region, inc`). Topes: **3000 recintos** (`RECINTOS_MAX`; devuelve los primeros con `truncado:true` y `n_total`)
y **5 km** de lado (`RECINTOS_MAX_KM`): por encima, `200` con `features:[]`, `truncado:true`, `limite:"extension"` y `aviso` ("Acerca el mapa"), para que el globo pueda
pedir en cada `moveend`. `422` bbox mal formado; `503` sin recintos. `Cache-Control: public, max-age=3600` y cabecera `X-Recintos-Total`.
**Atribución obligatoria (FEGA, CC BY 4.0):** "Fuente de los datos: FONDO ESPAÑOL DE GARANTÍA AGRARIA O.A." va en `attribution` de cada respuesta, en
`_meta.atribuciones`, en `parcela.atribucion` y en `fuentes[sigpac]`; la UI debe mostrarla junto al mapa.

CORS: siempre `http://localhost:5173` más los de `FRONTEND_ORIGIN`; sin credenciales, solo GET y POST.

## Qué es real, precalculado y simulado

| Bloque | `_status` | Origen |
|---|---|---|
| `parcela` | `precalculado` | ATOM del FEGA (campaña 2026, validez 2025-12-15), GeoJSON offline; recinto por punto en memoria (~0,4 ms). `zonas: []` (el ATOM no trae nitratos ni Mar Menor) |
| `clima` | `real` | NASA POWER (MERRA-2 + IMERG) y Open-Meteo (ERA5, ET0 FAO-56), caché por celda; `dias_helada` sigue **provisional** (pendiente SIAM) |
| `suelo` | `real` | ISRIC SoilGrids 2.0 a 250 m, caché por celda de 0,0025° |
| `semaforo_legal` de cada rotación | `simulado` (provisional) | `app.backend.rules.check()` con la zona de la petición; **todas las reglas `por_verificar`** (nunca `real`, lo prohíbe el esquema) |
| `rotaciones`, `escenarios_meta` | `simulado` | `app/data/torre-pacheco.contract.example.json` (MOCK) o el JSON de enrique (abajo): iguales para cualquier punto (son los de la parcela demo) |
| `historia`, `ndvi` | `simulado` | contrato de ejemplo; la historia real vendría de `cd_2025` del FEGA, el NDVI de T-013 |
| `fuentes[]` | n/a | ejemplo + `sigpac` reescrita (ATOM, CC BY 4.0) + las del pipeline (`open-meteo`...) + las del motor si lo hay |

`_meta.aviso` lleva `MOCK PARCIAL` y nombra los bloques simulados mientras los haya (el validador lo exige; también en `/parcel/{id}` tras fusionar).
Con zona sin verificar todas las rotaciones demo salen `amarillo`; `zona_2` → `verde, verde, verde`; `zona_1` → `rojo, verde, amarillo`.
`escenarios_meta.alineados` = `false` mientras enrique no lo declare (D-011): la UI no debe presentar "B gana X %" como firme.

## Punto de extensión del motor: `engine_adapter.py`

Los endpoints no cambian al enchufar el motor. Protocolo `Engine.run(EngineInput) -> EngineOutput` (`EngineInput` lleva los bloques `parcela/clima/suelo` reales). `get_engine` elige:
1. `DraftEngine` (por defecto): rotaciones del contrato de ejemplo, `simulado`.
2. `JsonFileEngine` con `ENGINE_JSON=/ruta/torre-pacheco.json`: lee el JSON del motor de enrique (`git show origin/t012-motor-nucleo:app/data/torre-pacheco.json`) y lo convierte con
   `app/data/contract/adapt_enrique.py` (v1.1; no se duplica su lógica). Se usan sus `rotaciones` (con `_status` de su `_estado_bloques`), `escenarios_meta` y `fuentes`;
   se ignoran sus `parcela/historia/ndvi/clima/suelo` y se recalcula su semáforo. Si el fichero no carga, se cae al ejemplo con un error en el log.
   Probado con la rama de enrique de hoy (4 rotaciones, 200 muestras): 0 errores de esquema, 0 invariantes fallidas.
3. Futuro: `LiveEngine` que llame a `run(parcela, clima, suelo)` de enrique por punto (cuando enrique lo exponga como función, T-020).

## Variables de entorno

| Variable | Por defecto | Uso |
|---|---|---|
| `PORT` | `8080` | puerto de uvicorn (Cloud Run lo inyecta) |
| `ATOM_BUILD_DIR` | `app/backend/api/atom_build`; en Docker `/data/atom` | GeoJSON de ATOM. Si no existe, la API arranca y avisa |
| `FRONTEND_ORIGIN` | vacío | orígenes CORS extra, separados por comas, sin `/` final (se ignora `*`) |
| `GIT_SHA` | `dev` | versión de `/health` |
| `ENGINE_JSON` | vacío | JSON de enrique (ver arriba) |
| `CONTRACT_PATH` | `app/data/torre-pacheco.contract.example.json` | contrato de ejemplo que sirve el motor por defecto |
| `PIPELINE_CACHE_DIR` | `<tmp>/agrockham-pipeline-cache` | caché de ejecución de clima/suelo; se siembra con `app/data/cache/pipeline/clima_suelo/` (parcela demo) |
| `AGROCKHAM_OFFLINE` | sin definir | `1` prohíbe la red del pipeline (sin caché → bloque `cargando`). Los tests lo ponen siempre |
| `LIVE_HTTP_TIMEOUT_S` / `LIVE_RETRIES` | `40` / `1` | red en vivo acotada (el pipeline por defecto espera hasta 120 s y reintenta 4 veces) |
| `LIVE_DEADLINE_S` | `60` | plazo total por bloque de clima/suelo; vencido → `cargando` y sigue en segundo plano |
| `RECINTOS_MAX` / `RECINTOS_MAX_KM` | `3000` / `5` | topes de `/recintos` |
| `CACHE_MAX` | `256` | entradas de `/parcel/{id}` |

## Pruebas

`python -m pytest app/backend/api -q` desde la raíz (`pytest.ini` pone la raíz en el `PYTHONPATH`). **Sin red** (`AGROCKHAM_OFFLINE=1` en todos los tests; `TEST_LIVE=1` la permite).
Con `ATOM_BUILD_DIR=/ruta/build` (municipios completos, 50 368 recintos) corren todos; sin él se omiten los que lo necesitan y el resto usa la muestra de 66 recintos de
`app/data/cache/pipeline/atom/`. `ENRIQUE_JSON=/ruta/torre-pacheco.json` activa el test con el JSON real de enrique (sin él, un JSON sintético con su forma).
Validan cada tipo de respuesta contra `app/data/contract.schema.json` + las invariantes de `app/data/contract/validate_contract.py` (requiere `jsonschema`, en el venv de desarrollo):
recinto parcial/cero/`null`/completo/discordante, 422, cobertura (fuera, sin recinto, sin ATOM, ATOM corrupto), `?bloques=` y fusión, `/recintos` (topes, gzip, CORS, bbox inválido),
semáforo por zona, clima/suelo en vivo simulados (plazo, errores sin filtrar detalles, caché), motor de enrique, y que los imports sean los del producto (`test_imports.py`, sin `vendor/`).

Validar a mano contra el contrato (con uvicorn en marcha):
```bash
curl -s -X POST localhost:8080/analyze -H 'Content-Type: application/json' -d '{"lat":37.7383,"lon":-0.98838}' > /tmp/analyze.json
/ruta/venv/bin/python app/data/contract/validate_contract.py /tmp/analyze.json
```

Mediciones (portátil de gonzalo, 14-nov-2026, 5 municipios = 50 368 recintos, caché caliente): `/analyze` demo 15-23 ms (43 kB); `?bloques=parcela` 8 ms; `/recintos` de 1 km 9 ms (188 recintos),
de 5 km 66 ms (3000 de 5127, truncado). Punto fuera de cobertura **sin caché**: 7-9 s (SoilGrids, 5 llamadas/min por IP); repetido, milisegundos. Carga de los 5 municipios al arrancar: ~1,2 s.

## Imagen Docker (probada en local, no subida a ningún registro)

**Contexto = raíz del repo** (el Dockerfile está en `app/backend/api/` y copia código de `app/backend/pipeline`, `app/backend/rules` y datos de `app/data`).
La imagen **no lleva los GeoJSON de ATOM**: hay que dejarlos antes de construir en `app/backend/api/atom_build/` (ignorada por git, `.gitignore` de esta carpeta):

```bash
cp -r /ruta/build app/backend/api/atom_build        # salida de build_recintos.py (~9 MB para 5 municipios)
docker build -f app/backend/api/Dockerfile --build-arg GIT_SHA=<sha corto> -t agrockham-api .
docker run --rm -p 8080:8080 agrockham-api          # http://localhost:8080/docs
```

326 MB, usuario `uid 10001`, arranca en ~1 s con los 50 368 recintos. `Dockerfile.dockerignore` es una lista blanca (solo entra lo que se copia).

## Despliegue en Cloud Run (SOLO documentado: lo ejecuta un humano; proyecto `agrockham-nasa-2026`, créditos GCP, aviso de 50 EUR)

Desde la raíz del repo, con los GeoJSON ya en `app/backend/api/atom_build/`:

```bash
gcloud run deploy agrockham-api --source . --project agrockham-nasa-2026 --region europe-west1 \
    --max-instances 3 --min-instances 0 --allow-unauthenticated \
    --set-env-vars FRONTEND_ORIGIN=https://<origen-del-frontend>,GIT_SHA=<sha corto>
```

Ojo: `--source .` busca un `Dockerfile` **en la raíz del directorio fuente** y el de esta API está en `app/backend/api/`. Opciones sin tocar nada fuera de esta carpeta:
(a) copiarlo temporalmente (`cp app/backend/api/Dockerfile ./Dockerfile` y `cp app/backend/api/Dockerfile.dockerignore ./Dockerfile.dockerignore`) y borrarlos después;
(b) construir con `gcloud builds submit --config app/backend/api/cloudbuild.yaml --substitutions _IMAGE=<imagen> .` y desplegar con `gcloud run deploy agrockham-api --image <imagen> ...` (mismas banderas).
`app/backend/api/cloudbuild.yaml` no se ha ejecutado. Si `.gcloudignore`/`.gitignore` excluyen `atom_build/`, `--source` no la subirá: usar (b) o un `.gcloudignore` propio
(gcloud respeta `.gitignore` por defecto). Cloud Run con varias instancias: cada una calienta su propia caché de `/parcel` y de clima/suelo en `/tmp`.

## Limitaciones y honestidad

- `rotaciones`, `historia` y `ndvi` son del **contrato de ejemplo** (MOCK) y no corresponden al punto: están `simulado` y el aviso lo dice. No hay motor por punto todavía.
- Cobertura = municipios cargados (San Javier, San Pedro, Torre-Pacheco, La Unión, Los Alcázares). Cartagena y Fuente Álamo (Campo de Cartagena) **no están descargados**: sus puntos salen `basico`.
  La caja de cobertura es la del municipio, no su límite administrativo exacto.
- El semáforo legal depende de reglas **sin verificar en el BOE** y de la zona (Anexo I sin leer): `por_verificar` por defecto. No es asesoría legal.
- `clima.dias_helada` provisional y `dias_calor_gt_38` subestimado (MERRA-2 a ~50 km): faltan los datos de SIAM (T-014).
- Open-Meteo: la API gratuita es **solo no comercial** (vale para el hackathon; ver `app/backend/pipeline/README.md`).
- Sin límite de peticiones: una ráfaga de puntos nuevos satura las APIs externas (SoilGrids 5/min por IP; en Cloud Run la IP de salida es compartida). Precalentar celdas del Campo de Cartagena antes de la demo.
- El validador avisa (AVISO, no FALLO) de 1 mención de `CARM/esam` en `fuentes[].url` del contrato de ejemplo (D-010): viene de `app/data/`, no de esta API.

## Dependencias y licencias

Versiones fijadas (comprobadas en PyPI el 2026-11-14; licencias de los metadatos instalados). Imagen base `python:3.12-slim` (Docker Official Image). Para `submission/data-citations.md`.

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
| pytest / httpx / jsonschema | 9.2.0 / 0.28.1 / 4.26.0 | MIT / BSD-3-Clause / MIT | solo pruebas (`requirements-dev.txt`) |

Datos: FEGA ATOM (CC BY 4.0), NASA POWER, GPM IMERG, Open-Meteo (CC BY 4.0, API gratuita no comercial; origen ERA5 de Copernicus C3S), SoilGrids 2.0 (CC BY 4.0), BOE (Ley 3/2020).
Citas completas y estado de licencia: `app/backend/pipeline/README.md`.

## Pendiente (no lo hace esta tarea)

- Despliegue real en Cloud Run y la URL pública para el frontend (arturo T-017 / un humano). Probar la imagen con `FRONTEND_ORIGIN` real.
- Descargar Cartagena y Fuente Álamo con `build_recintos.py` (de noche) y rehacer `atom_build/`.
- Filas de `submission/data-citations.md` (no es de esta carpeta).
- Enchufar el motor por punto (T-020) y pasar `rotaciones` de `simulado` a `real` cuando enrique lo declare.
- Revisar con el FEGA el uso en producción del ATOM y decidir si el semáforo `gris` del nivel básico es lo que quiere la UI.

## Despliegue real (2026-11-14)
- Servicio: `agrockham-api` en Cloud Run, proyecto `agrockham-nasa-2026`, region `europe-west1`, publico, `--max-instances 3 --min-instances 0 --memory 1Gi`. Imagen `europe-west1-docker.pkg.dev/agrockham-nasa-2026/agrockham/agrockham-api:v1` (Artifact Registry repo `agrockham`).
- URL: https://agrockham-api-530791362085.europe-west1.run.app (`/health`, `/docs`).
- Como se hizo: un contexto limpio fuera del repo (app/backend/api, pipeline, rules, app/data minimo y los GeoJSON de ATOM en `app/backend/api/atom_build`), `gcloud builds submit --config app/backend/api/cloudbuild.yaml --substitutions _IMAGE=<imagen>` y `gcloud run deploy agrockham-api --image <imagen> --allow-unauthenticated ...`. Los GeoJSON de ATOM NO estan en git (los genera `app/backend/pipeline/atom/build_recintos.py`).
- Comprobado: `/health` (50 368 recintos cargados), `POST /analyze` en la parcela demo (0,4 s; clima y suelo reales, parcela precalculada, semaforo verde con `zona=zona_2`), `/recintos?bbox=` y CORS para `http://localhost:5173`.
- Pendiente: `FRONTEND_ORIGIN` con el origen publico del frontend de jaime (CORS), descargar Cartagena y Fuente Alamo, enchufar el motor de enrique (`ENGINE_JSON`).

## Empaquetado: GIT_SHA y JSON del motor (2026-11-14, hallazgos de arturo #162)
- `cloudbuild.yaml` pasa `--build-arg GIT_SHA=${_GIT_SHA}`: construir con `--substitutions _GIT_SHA=$(git rev-parse --short HEAD),_IMAGE=<imagen>` para que `/health` devuelva el commit real.
- Contrato de montaje del motor: la API no lleva el codigo del motor, solo su JSON publicado. Copia ese JSON a `app/backend/api/engine_data/engine.json` antes de construir (ignorado por git; puede llevar precios CARM, D-010) o monta un volumen / fija `ENGINE_JSON`. Ver `engine_data/README.md`.

## Cobertura v4 (2026-11-14, 17:16 hora de Madrid)
Imagen v4 (commit c281ac1): 7 municipios del ATOM del FEGA, **170 265 recintos** (Cartagena 76 231, Fuente Alamo 43 666, Torre-Pacheco 29 859, San Javier 13 254, San Pedro del Pinatar 2 925, La Union 2 515, Los Alcazares 1 815; ~30 MB comprimidos), servicio con 2 GiB de memoria (carga ~11 s al arrancar en frio). Probados puntos de Cartagena y Fuente Alamo: `parcela` precalculada y cobertura completa. Descarga hecha con el permiso explicito de gonzalo a las 17:15 (el ATOM pide descargas grandes fuera de 8:00-18:00).

## Control de gasto en GCP (2026-11-14; proyecto agrockham-nasa-2026, tope de equipo 50 EUR)
Recursos existentes (auditados con gcloud): UN servicio Cloud Run (`agrockham-api`), el repo Artifact Registry `agrockham` (imagenes v3 y v4; v1 y v2 borradas) y el bucket de Cloud Build. No hay VMs, GKE, Cloud SQL, funciones ni jobs; Compute y Cloud Functions no estan habilitados.
Protecciones activas:
- Cloud Run: `--max-instances 2`, `--min-instances 0` (escala a cero: sin trafico no cuesta), `--timeout 120`, concurrencia 80, CPU solo durante las peticiones, 1 vCPU / 2 GiB. Peor caso teorico con trafico continuo: ~2 instancias x 24 h.
- Bucket `agrockham-nasa-2026_cloudbuild`: ciclo de vida que borra objetos con mas de 1 dia (las fuentes de cada build).
- Presupuesto "Agrockham alerta 50 EUR" (50 EUR): avisos por correo al 10, 20, 50, 80 y 100 % del gasto real y al 100 % de la prevision. OJO: un presupuesto solo AVISA, no corta el servicio.
- La cuenta es una prueba gratuita con credito (~269 EUR en la consola) y sin pasar a cuenta completa no se cobra mas alla del credito.
Parada de emergencia (si el gasto sube sin motivo):
- Cortar el trafico publico: `gcloud run services remove-iam-policy-binding agrockham-api --project agrockham-nasa-2026 --region europe-west1 --member=allUsers --role=roles/run.invoker`
- Borrar el servicio: `gcloud run services delete agrockham-api --project agrockham-nasa-2026 --region europe-west1`
- Desvincular la facturacion del proyecto: `gcloud billing projects unlink agrockham-nasa-2026`
Antes de cualquier despliegue nuevo: mantener `--max-instances 2 --min-instances 0 --allow-unauthenticated` solo para `agrockham-api`, no crear otros servicios ni recursos de coste continuo, y borrar imagenes antiguas.

## Imagen con el motor en vivo (2026-11-14, prueba hecha con la rama integracion 3c225b7)
- `Dockerfile.engine` + `Dockerfile.engine.dockerignore`: copian `app/backend/engine` SIN tests y SIN `carm_precios_mensuales.csv` (restringido, D-010), `mapa_prices.csv` y `torre-pacheco.mock.json`; fijan `ENGINE_MODE=vivo` y `ENGINE_PRECIOS=abierto`. Solo necesita numpy (ya en requirements).
- Probado sin red (`--network none`): /analyze 0,6-0,7 s por parcela, motor "en vivo por parcela", 4 rotaciones; el contenedor arranca con 170 265 recintos.
- Datos incluidos: serie SIAM TP91 diaria y POWER diaria de la parcela (el motor las lee). SIAM sin licencia abierta explicita (fila "verify" de data-citations.md): atribucion "Fuente: SIAM-IMIDA, Region de Murcia".
- NO desplegada todavia: pendiente de que enrique confirme las cifras del modo abierto (ver LOG).
- Verificado (2026-11-14, hallazgo de arturo #267): construido con un arbol que SI contiene `carm_precios_mensuales.csv`, la imagen queda con 0 ficheros `*carm_precios*` y sin carpetas `tests`: `Dockerfile.engine.dockerignore` los excluye tras la lista blanca y `Dockerfile.engine` lleva un RUN que borra y FALLA el build si aparece alguno.

## Procedencia de la imagen v9 (2026-11-14, respuesta a arturo #334)
La v9 NO sale de un unico commit: es `integracion` @ f964717 + el alias `/api` aplicado como parche local. Manifiesto:
- Revision `agrockham-api-00011-tqd`, imagen `agrockham-api:v9`, digest `sha256:f3d46f526d4cf1ea5ea74e3a272f85153d3dec7e717d19b9f582664eb2c4c508`, `GIT_SHA=f964717` (lo que devuelve /health: es el SHA BASE, no incluye el parche).
- Motor y resto del backend, `engine.json` y frontend: de integracion f964717. `engine.json` = `app/data/torre-pacheco.abierto.json` de f964717 (sha256 `da55e39e063d4cb9…`). Frontend: `dist` de t010-cierre ffdf168 (= c00f735, mismo diff) compilado con `VITE_API_BASE=<URL>/api`; sin ficheros .ttf; solo `dist` en `frontend_dist`.
- API: `app/backend/api/main.py` de f964717 (sha256 `6b32af1d6d092ea8…`) + el bloque `alias /api` de `tools/patch_api_prefix.py` (mismo cambio que main bfab7ce) = `main.py` de la imagen (sha256 `479d4ab02c8bbe70…`). El resto de `app/backend/api` es el de f964717.
- Contexto de construccion: copia limpia (api, pipeline, rules, engine SIN tests y SIN `carm_precios_mensuales.csv`, `mapa_prices.csv`, mock, contrato, cache del pipeline, GeoJSON de ATOM de 7 municipios), Dockerfile = `Dockerfile.engine`.
- Para dejar UN solo hash: cuando enrique haga `git merge origin/main` en integracion, ese merge ya contiene el alias; reconstruir desde ese commit da la v10 equivalente, con SHA unico.
