# Agrockham API: esqueleto (prototipo de preparación, T-017)

**Estado: STUB.** Es el esqueleto de la API acordada con Arturo para que el despliegue en Cloud Run sea trivial cuando
se desbloquee T-011 (D-009). **No hay ningún dato real**: los bloques salen del borrador de contrato
(`research/contract-v1-draft/`, parcela demo de Torre-Pacheco) con `_status: "simulado"` y el aviso MOCK en `_meta.aviso`,
sea cual sea el punto consultado. No está en `app/` ni se ha desplegado nada.

Qué hace: `FastAPI` con `/health`, `POST /analyze` (contrato por bloques, con carga progresiva simulada) y
`GET /parcel/{id}` (último contrato guardado en memoria). Qué **no** hace aún: llamar a SIGPAC, POWER, SoilGrids, el motor
de Enrique ni las reglas legales (T-019).

```
main.py        endpoints, validación del cuerpo, CORS, caché en memoria
contract.py    carga el borrador y arma los bloques; cobertura completo/básico; fusión de bloques ya cargados
settings.py    variables de entorno (FRONTEND_ORIGIN, GIT_SHA, CONTRACT_PATH, CACHE_MAX), bbox del Campo de Cartagena
data/          copia del borrador de contrato (viaja en la imagen; un test comprueba que sigue igual al original)
tests/         pytest + TestClient; validan cada respuesta contra contract.schema.json y las invariantes de validate.py
Dockerfile · .dockerignore · requirements.txt · requirements-dev.txt · pytest.ini
```

## Ejecutar

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt     # .venv está en .gitignore
.venv/bin/uvicorn main:app --reload --port 8080                            # http://localhost:8080/docs (Swagger)
.venv/bin/python -m pytest -q                                              # 42 tests
```

Imagen (Cloud Run usa `PORT`, por defecto 8080):

```bash
docker build --build-arg GIT_SHA=$(git rev-parse --short HEAD) -t agrockham-api .
docker run --rm -p 8080:8080 -e FRONTEND_ORIGIN=https://TU-FRONTEND agrockham-api
```

## Contrato de la API

### `GET /health`
```json
{"status": "ok", "version": "a1b2c3d"}
```
`version` = variable `GIT_SHA` o `"dev"`.

### `POST /analyze[?bloques=a,b,c]`
Cuerpo:
```json
{"lat": 37.7383, "lon": -0.98838, "recinto": {"provincia": 30, "poligono": 18, "parcela": 426, "recinto": 1}}
```
- `lat` en [-90, 90], `lon` en [-180, 180] (obligatorios, finitos). Fuera de rango o campos extra: **422**.
- `recinto` opcional: objeto con campos SIGPAC enteros opcionales (`provincia, municipio, agregado, zona, poligono, parcela,
  recinto`) o una cadena de hasta 64 caracteres. Se devuelve tal cual en `_meta.consulta` (suposición mía sobre lo acordado
  con Arturo: **confirmar el formato exacto de `recinto`** con T-017/T-010).
- Los errores 422 no devuelven el valor recibido (solo `loc`, `msg`, `type`).

Respuesta: el contrato v1 completo (mismas claves de primer nivel obligatorias que `contract.schema.json`), **siempre
válido contra el esquema**. Cada bloque (`parcela, historia, ndvi, clima, suelo, rotaciones`) o bien está relleno
(`_status: "simulado"`) o es un hueco `{"_status": "cargando"}` (`rotaciones: []`). `_meta.bloques_pendientes` lista los
huecos. El cliente sustituye en su estado los bloques `cargando` por los que reciba después.

`?bloques=clima,suelo` rellena solo esos y deja los demás en `cargando` (simula la carga progresiva: pide `parcela`
primero, luego `clima,suelo`, luego `rotaciones`). Sin parámetro = todos los que el stub sabe servir. `?bloques=` vacío
o con un nombre desconocido: 422. `ndvi` (Enrique, T-013) aún no existe: sale siempre `cargando`. `escenarios_meta` viaja
con `rotaciones`; `variantes` y `sensores` (P2) no se emiten.

Campos añadidos en `_meta` (el esquema deja abiertos los campos extra): `stub: true`, `consulta {lat, lon, recinto}`,
`consulta_id` (`q-<lat 5 dec>_<lon 5 dec>`), `generado_en`, `avisos[]`, `cobertura {nivel, ambito}`.

**Cobertura:** dentro de la bbox aproximada del Campo de Cartagena (lon -1.35..-0.65, lat 37.45..37.95, bordes incluidos)
`cobertura.nivel = "completo"`; fuera, `"basico"` más un aviso en `_meta.avisos` (y otro si el punto cae fuera de España
peninsular). El stub devuelve igualmente los datos demo en ambos casos; el semáforo legal en gris del nivel básico
(D-009) está sin implementar. La bbox se sustituirá por la consulta por municipio del propio SIGPAC.

### `GET /parcel/{id}`
Devuelve el contrato guardado de la última petición. `id` puede ser `parcela.id` (p. ej. el demo
`30-0-0-0-0-0-demo (SIGPAC 18/426/1)`, URL-codificado) o `_meta.consulta_id`. **404** si no está. Varias peticiones
`/analyze?bloques=...` del mismo punto **se fusionan**: lo ya cargado no se pierde.

La caché es un diccionario en memoria del proceso (máx. `CACHE_MAX` entradas, la más antigua sale primero): se pierde al
reiniciar y **no se comparte entre instancias de Cloud Run**. Para el stub basta; con `--max-instances 3` el frontend no
debe depender de que `/parcel/{id}` caiga en la misma instancia (guardar en `localStorage`, como acordado en D-009).

### Ejemplo rápido
```bash
curl -s localhost:8080/health
curl -s -X POST localhost:8080/analyze -H 'content-type: application/json' \
     -d '{"lat":37.7383,"lon":-0.98838}'                                    # parcela demo, cobertura completo
curl -s -X POST 'localhost:8080/analyze?bloques=clima' -H 'content-type: application/json' \
     -d '{"lat":41.65,"lon":-4.72}'                                         # Valladolid: cobertura basico + aviso
curl -s localhost:8080/parcel/q-37.73830_-0.98838
```

## Variables de entorno

| Variable | Por defecto | Uso |
|---|---|---|
| `PORT` | `8080` | Puerto de uvicorn (lo inyecta Cloud Run) |
| `FRONTEND_ORIGIN` | vacío | Origen(es) extra permitidos por CORS, separados por comas (sin `/` final; se ignora `*`). Siempre se permite `http://localhost:5173` |
| `GIT_SHA` | `dev` | Versión que devuelve `/health` |
| `CONTRACT_PATH` | `data/torre-pacheco.contract-v1.draft.json` | JSON del borrador a servir |
| `CACHE_MAX` | `256` | Entradas máximas de la caché en memoria |

CORS: solo `GET` y `POST`, cabecera `Content-Type`, **sin credenciales** (no hay cookies ni cuentas).

## Despliegue en Cloud Run (SOLO documentado, no ejecutado)

Lo hace un humano con el proyecto GCP creado y la facturación activa. Con `Dockerfile` en la carpeta, `--source .` construye con él:

```bash
gcloud run deploy agrockham-api --source . --project agrockham-nasa-2026 --region europe-west1 \
  --max-instances 3 --min-instances 0 --allow-unauthenticated
```
Opcional, para que `/health` muestre la versión y se acepte el frontend publicado:
`--set-env-vars GIT_SHA=$(git rev-parse --short HEAD),FRONTEND_ORIGIN=https://TU-FRONTEND` (con `--source` no se pasa el
`--build-arg`). `min-instances 0` implica arranque en frío de un par de segundos en la primera petición. `--allow-unauthenticated`
deja la API pública: el stub no tiene datos sensibles, pero la versión real debería limitar peticiones (ver abajo).

## Seguridad

- **Sin cuentas, sin secretos en la imagen.** El `Dockerfile` no copia `.env` (ni `.dockerignore` lo deja pasar), no hay `ARG`
  con claves y la imagen corre con un usuario sin privilegios (uid 10001).
- El token de Earthdata (cuando haga falta, T-013) irá por **Secret Manager** montado como variable de entorno en Cloud Run
  (`--set-secrets`), nunca en el repositorio, la imagen, `LOG.md` ni el bus.
- Los 422 no repiten el valor recibido; `lat`/`lon` rechazan NaN/Infinity; la caché está acotada.
- Pendiente para la versión real: límite de peticiones (el `--max-instances 3` ya acota el coste), registro sin coordenadas
  de usuarios si se considera dato personal, y revisar la **licencia/condiciones del FEGA** para llamar a SIGPAC desde código
  (riesgo abierto en D-009).

## Dependencias y licencias

Versiones fijadas, comprobadas en PyPI el 2026-11-14 (licencia leída de los metadatos instalados). Todas permisivas; la API
no distribuye nada de esto salvo la imagen del servicio. Anotar en `submission/data-citations.md` si el equipo lo exige.

| Paquete | Versión | Licencia | Uso |
|---|---|---|---|
| fastapi | 0.162.7 | MIT | framework |
| starlette | 1.10.0 | BSD-3-Clause | base de FastAPI |
| uvicorn | 0.54.0 | BSD-3-Clause | servidor ASGI |
| pydantic | 2.14.3 | MIT | validación |
| pydantic_core | 2.50.4 | MIT | núcleo de pydantic |
| annotated-types | 0.8.0 | MIT | transitiva |
| annotated-doc | 0.0.6 | MIT | transitiva |
| anyio | 4.16.0 | MIT | transitiva |
| click | 8.5.1 | BSD-3-Clause | transitiva (uvicorn) |
| h11 | 0.16.0 | MIT | transitiva (uvicorn) |
| idna | 3.20 | BSD-3-Clause | transitiva |
| opentelemetry-api | 1.45.2 | Apache-2.0 | transitiva (la trae fastapi 0.162) |
| typing-inspection | 0.4.5 | MIT | transitiva |
| typing_extensions | 4.16.0 | PSF-2.0 | transitiva |
| pytest | 9.2.0 | MIT | solo pruebas |
| httpx | 0.28.1 | BSD-3-Clause | solo pruebas (cliente de TestClient) |
| jsonschema | 4.26.0 | MIT | solo pruebas (esquema del contrato) |

Imagen base `python:3.12-slim` (Docker Official Image; Python bajo PSF-2.0, Debian con sus licencias propias).
Nota: starlette 1.x avisa de que `TestClient` prefiere el paquete `httpx2`; se mantiene `httpx` (conocido) y el aviso se
silencia en `pytest.ini`. Los datos del JSON son ilustrativos y propios del equipo (no hay datos de terceros en el stub).

## Qué faltaría para pasarlo a `app/backend/api/`

1. **Ownership:** `.claude/ownership.json` no incluye `app/backend/api/` (gonzalo tiene `app/backend/pipeline/` y `rules/`).
   Hay que añadirlo a la lista de gonzalo (decisión del equipo/jaime) y, con ello, reclamar la tarea (T-011 u otra) y
   quitar de `research/` este prototipo.
2. Mover la carpeta (sin `tests/` duplicados) y decidir de dónde lee el contrato: hoy hay una copia en `data/`; en `app/` debería
   leer `app/data/contract.schema.json` / el JSON de `app/data/` en vez de duplicarlo (o copiarlo en el build).
3. Sustituir cada bloque stub por su implementación real, conservando el formato `_status` (`real | precalculado`): parcela e
   historia (SIGPAC, tras aclarar licencia FEGA), clima (POWER, caché por celda 0,5°), suelo (SoilGrids, 5 llamadas/min),
   rotaciones (`run(parcela)` de Enrique, T-020), semáforo legal (T-019), NDVI (T-013). La caché pasaría a algo compartido
   si hay varias instancias (o se asume que cada una calienta la suya).
4. Cobertura por municipio en vez de bbox; semáforo legal en gris en nivel básico.
5. Confirmar con Arturo (T-017) el formato de `recinto` y si el frontend quiere `bloques=` por separado o un solo `/analyze`.
6. Construir y probar la imagen con Docker (aquí solo se pasó `docker build --check`, sin construir), y crear el proyecto GCP
   con facturación (acción humana).
