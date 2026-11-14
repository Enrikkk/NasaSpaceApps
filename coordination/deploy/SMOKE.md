# T-017 — smoke API + JSON del motor, handoff #166

Objetivo: arrancar el candidato API con la red del pipeline desactivada, cargar el JSON precalculado correcto y comprobar respuestas HTTP con el validador del productor. No prueba navegador, motor por punto, exactitud agronómica ni publicación.

## Ejecución local reproducible

Entradas usadas: API `main@2ec59e1`, JSON de `origin/t012-motor-nucleo@473f2c2`, caché de la parcela demo del candidato, muestra FEGA versionada de 66 recintos. Se extraen copias a `/tmp`: no se edita `app/backend/api` ni las tablas T-021. El venv temporal instala las versiones ya fijadas por Gonzalo en `app/backend/api/requirements-dev.txt`; no son nuevas dependencias del producto.

Ejecutar con ese Python:

```sh
/ruta/venv/bin/python scripts/t017_smoke.py \
  --root /ruta/candidato-api \
  --engine-json /ruta/torre-pacheco.abierto.json \
  --sample-atom --api-sha 2ec59e1 --engine-sha 473f2c2
```

La muestra se reencoda en un directorio temporal al formato gzip que espera el loader: no se descargan ni alteran atributos, y quedan registrados hash, atribución y tamaño. No demuestra cobertura de los cinco municipios. Para un paquete real usar `--atom-dir /ruta/paquete-gonzalo` en lugar de `--sample-atom`.

El proceso usa `AGROCKHAM_OFFLINE=1`, `ENGINE_JSON` explícito, una caché temporal y un puerto efímero en `127.0.0.1`. Se detiene al terminar, incluso si falla. El script no acepta URL remota y no llama al Cloud Run desplegado por Gonzalo.

Resultados y respuestas JSON permanecen en un directorio temporal fuera de los checkouts: `report.json`, logs y respuestas/validación. No publicar automáticamente esos artefactos; pueden contener datos sujetos a condiciones de reutilización. `--output /ruta/nueva-fuera-del-repo` permite fijar el destino.

Comprueba:

- `/health` 200, versión esperada y ATOM cargado con datos.
- `POST /analyze` de la parcela demo; validador `app/data/contract/validate_contract.py` y sus invariantes, ejecutados sobre la respuesta.
- `_meta.motor` indica JSON de Enrique; no se acepta fallback silencioso a `DraftEngine`. IDs de rotaciones coinciden con el fichero de entrada.
- CORS para `http://localhost:5173`.
- `GET /parcel/{consulta_id}` 200 y validación del contrato.
- `/recintos` devuelve GeoJSON no vacío y atribución. Health/GeoJSON se comprueban con su estructura específica, no con el esquema del contrato `/analyze`.

El esquema puede emitir avisos blandos de fuentes/licencias; pasar el validador no autoriza publicación. La marca `_status=real` de rotaciones viene del JSON precalculado, no acredita que se haya ejecutado el motor para otro punto.

## Pasada con Docker sin red

Usar una imagen **ya construida localmente** por Gonzalo, con el mismo candidato API:

```sh
/ruta/venv/bin/python scripts/t017_smoke.py \
  --root /ruta/candidato-api \
  --engine-json /ruta/torre-pacheco.abierto.json \
  --atom-dir /ruta/paquete-atom \
  --mode docker --image agrockham-api:etiqueta-local \
  --api-sha 2ec59e1 --engine-sha 473f2c2
```

El runner usa `--pull=never --network none`, montajes de solo lectura para JSON/ATOM, `AGROCKHAM_OFFLINE=1` y llamadas desde `docker exec` al loopback interno. No publica puertos ni imágenes, no construye ni descarga. Comprueba por `docker inspect` que la red sea `none`; detiene únicamente su contenedor con nombre único. La máquina ejecutora necesita Docker; Arturo no lo tiene instalado. La validación de esquema se ejecuta en el host con el Python de desarrollo, sin añadir paquetes a la imagen.

El modo local solo desactiva la red del pipeline mediante su configuración. **No equivale al aislamiento de red del modo Docker.**

## Evidencia y trabajo pendiente

- Pasada local inicial con el JSON publicado de Enrique: trece checks pasan, con muestra 66; artefactos internos en `/tmp/agrockham-t017-local-2`. Ese JSON declaraba CARM y no se copia al handoff ni al repo.
- Tras #169, el candidato de handoff es el JSON **abierto** (`incluye_precios_carm=false`). Su pasada independiente y resumen están en `local-smoke-summary.json`, sin copiar las respuestas de precios.
- #169 comunica prueba de Gonzalo sobre Docker `2ec59e1`, `--network none` y `AGROCKHAM_OFFLINE=1`: health versión correcta, 50.368 recintos, analyze demo y fuera de cobertura, recintos 203; imagen/contenedor borrados. Es evidencia reportada por Gonzalo, no ejecución de Arturo. Se pidió confirmar carga del JSON del motor y validación de su respuesta (#172): no se asumen del health o del 200.
- Frontend versionado, API base, origen de producción y fallback del navegador siguen esperando paquete/commit de Jaime. No se declara la demo terminada.
- Cloud Run ya fue desplegado por Gonzalo según #163/#165; esta tarea no lo consulta ni cambia recursos. GCP sigue a cargo de Gonzalo y no existe autorización de despliegue por Arturo.

## Cierre de integración #166, evidencia #176

Gonzalo aclaró que su primera imagen usaba DraftEngine. Repitió con API `02e4b89` y JSON abierto `473f2c2` dentro de `engine_data/engine.json` (`ENGINE_JSON` vacío), `--network none` y `AGROCKHAM_OFFLINE=1`. Conservó la respuesta en main `c281ac1`, `research/evidence/analyze-docker-abierto-02e4b89.json`. Arturo comprobó SHA-256 `6a6f934bc1b2cbbdfa5356bd93ee800184c5651e057dbf5bc6b92a772ed540d5` y ejecutó el validador de `c281ac1`: cero errores de esquema, cero invariantes fallidas y tres avisos. Está seleccionado JSON de Enrique, con cuatro rotaciones, `actual` sin margen y `alineados=false`.

Avisos conservados: medias de margen difieren de las muestras Monte Carlo; `peores_anios` supera `k_malos` en s1/s3; dos menciones CARM en metadatos SIAM (no equivalen a precios CARM). Remitidos a Enrique (#178). No se cambió el motor ni la política del validador. #166 queda cerrado para integración API + JSON + Docker; T-017 sigue abierto por frontend/fallback. La ejecución Docker fue de Gonzalo; Arturo verificó el artefacto, sin instalar Docker.
