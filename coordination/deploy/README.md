# T-017 — preparación local, D-009

Esta entrega prepara comprobaciones y una ejecución reproducible. No despliega, no crea recursos GCP, no cambia facturación ni licencia. **La demo no está terminada.** T-021 permanece sin cambios en su rama.

## Referencias comprobadas

| Componente | Referencia leída | Estado observado |
|---|---|---|
| Base del worktree T-017 | `origin/main` `b48ebaee2697eee5c6d11a64581ee03fed96efea` | T-024 ya integrado; contrato, pipeline y reglas presentes |
| Candidato API actual | `origin/main` `2ec59e1` (Gonzalo #163–#166) | Dockerfile en `app/backend/api/`, contexto raíz; engine_data opcional y build-arg GIT_SHA corregidos |
| API previa, histórica | `origin/t024-live-api` `5d49ea0` | Sustituida como candidato por main2ec59e1; no construir desde esa rama antigua |
| Motor, solo referencia | `origin/t012-motor-nucleo` `473f2c25c9ab2efda970fc7d0de3644019de4b22` | Referencia con MAPA comunicada por Desktop; no se ejecutó build ni se copió JSON |
| Frontend en main | mismo `b48ebae` | Solo `DESIGN.md`, tokens y fuentes; faltan `package.json`, app construible y `dist/index.html` |

No se hace merge de ramas del equipo ni se sobrescriben sus carpetas. Claims/commits posteriores pueden cambiar el candidato: volver a fijar referencias y generar informe antes de construir.

## Una orden para inspeccionar

Desde la raíz de una copia del repo que contenga esta rama:

```sh
bash scripts/deploy.sh inspect
```

Solo lectura y biblioteca estándar de Python: sin red, instalaciones, imports del producto, llamadas cloud ni escrituras. Recorre los `COPY` del Dockerfile, verifica existencia y sintaxis Python, registra SHA-256 de entradas, lee JSON y comprueba presencia de semillas/ATOM/frontend/herramientas. No es un validador completo de Dockerignore ni reemplaza el esquema o las suites del productor.

```sh
bash scripts/deploy.sh check-image
bash scripts/deploy.sh check-demo
```

`inspect`: código 0 si terminó la inspección sin errores de formato, incluso con dependencias pendientes. `check-image` y `check-demo`: código 2 si faltan requisitos; código 1 ante JSON/sintaxis/contrato Docker no compatible. `demo_ready` permanece falso: este inspector no ejecuta navegador ni puede certificar el recorrido completo. `--root /ruta/candidato` inspecciona otro paquete sin editarlo. `--engine-json /ruta/candidato.json` inspecciona metadatos de un JSON existente, sin copiarlo ni publicarlo.

## Resultado real en el portátil de Arturo

- Inspección de fuentes sin errores; cuatro JSON de semilla clima/suelo presentes. Los perfiles de imagen y demo devuelven 2 como corresponde.
- Docker y gcloud no instalados. No se ejecutaron build, contenedores ni suites de Gonzalo/Enrique. Tras handoff #166 se creó un venv temporal con requirements-dev de la API para ejecutar un smoke HTTP de integración nuevo, detallado abajo.
- Falta `app/backend/api/atom_build/` con `*_recintos.geojson.gz` (e idealmente `index.json`). La muestra `torre-pacheco_demo_viewport.geojson` no es el formato de entrada del loader y no basta para construir el Dockerfile actual. Paquete completo solicitado a Gonzalo (#156/#161).
- Falta aplicación frontend versionada y su artefacto/fallback verificable. Solicitados por handoff al Cursor de Jaime (#157), sin crear otro agente.
- Sin `ENGINE_JSON`, la API utiliza `DraftEngine`: rotaciones de ejemplo. Con JSON precalculado sirve resultados de la parcela demo para cualquier punto; eso tampoco acredita motor por punto. El Dockerfile de main2ec59e1 copia engine_data: el productor documenta staging engine_data/engine.json o montaje/ENGINE_JSON (#164). No lleva código del motor ni implica evaluación por punto.

## Receta local para quien ya tenga Docker — NO ejecutada aquí

Entrada: paquete de Gonzalo con código fijado, cachés, ATOM en la ruta que espera el Dockerfile y un manifiesto de hashes. No preparar ese paquete editando sus áreas desde esta tarea. Inspeccionar el candidato antes de construir:

```sh
bash scripts/deploy.sh check-image --root /ruta/candidato
cd /ruta/candidato
TASK_SHA="$(git rev-parse --short=12 HEAD)"
TASK_IMAGE="agrockham-api:t017-${TASK_SHA}"
docker build -f app/backend/api/Dockerfile --build-arg GIT_SHA="$TASK_SHA" -t "$TASK_IMAGE" .
```

Si el paquete no tiene `.git`, el productor proporciona `TASK_SHA` desde su manifiesto; no usar `dev` como identidad de una versión revisada. La etiqueta local no es un despliegue ni una imagen publicada.

Para comprobar la API con red realmente aislada, sin prometer que el navegador funciona offline:

```sh
docker run --rm -d --name agrockham-t017-offline --network none \
  -e AGROCKHAM_OFFLINE=1 "$TASK_IMAGE"
docker exec agrockham-t017-offline python3 -c 'import json,urllib.request; h=json.load(urllib.request.urlopen("http://127.0.0.1:8080/health")); assert h["status"]=="ok"; assert h["recintos"]["cargado"]; print(h)'
docker exec agrockham-t017-offline python3 -c 'import json,urllib.request; q=urllib.request.Request("http://127.0.0.1:8080/analyze",data=json.dumps({"lat":37.7383,"lon":-0.98838}).encode(),headers={"Content-Type":"application/json"}); d=json.load(urllib.request.urlopen(q)); assert d.get("_meta"); print(d["_meta"].get("estado_bloques"),d["_meta"].get("motor"),d["_meta"].get("avisos"))'
docker stop agrockham-t017-offline
```

Esas dos peticiones son un smoke limitado: no sustituyen validación de esquema, exactitud de datos ni recorrido UI. Recoger versión, estados de bloques, atribuciones y cobertura; no convertir un 200 en éxito de la demo.

Para el smoke completo del productor, ejecutar su entorno de desarrollo con versiones fijadas y su API local arrancada **con `AGROCKHAM_OFFLINE=1`**. En main637c880, confirmado en2ec59e1 (#163), su smoke.py --sin-red ya limita el punto exterior al bloque parcela. Para cero red sigue siendo necesario el flag offline del servidor o aislamiento del contenedor. Si hay imagen con puerto publicado, limitarlo a `127.0.0.1:8080`; usar su smoke desde el host. No confundir ese modo con aislamiento de red del contenedor.

## Dependencias exactas y coordinación

| Responsable | Entrada que falta | Criterio de comprobación |
|---|---|---|
| Gonzalo, T-024/T-011 | Paquete ATOM reproducible con hashes, municipios/campaña/atribución e índice; confirmar si muestra reducida válida | Loader carga; `/health` informa número y municipios; `/recintos` y demo corresponden al paquete |
| Gonzalo + Enrique/Cursor | API enlazada al JSON/motor elegido, y forma de incluirlo en imagen | Sin default de ejemplo accidental; estados y límites por punto explícitos; JSON pasa contrato del productor |
| Jaime, T-010 | Commit/paquete frontend, comando build/preview, API base/env, origen previsto y fallback precargado | Compila; llamada local a API con CORS correcto; al cortar red muestra demo etiquetada, sin fingir consulta live |
| Gonzalo, GCP | Ruta de imagen/registro, configuración y manifiesto de carga para una ejecución futura por él | ATOM ignorado por Git llega al contexto; GIT_SHA trazable; origen exacto definido; recursos acotados según su configuración |
| Humanos | Aprobación concreta de publicación del artefacto seleccionado | No se infiere de D-009, de créditos disponibles ni de permiso para preparación local |

Hallazgos iniciales enviados a Gonzalo (#161/#162), corregidos por él en main2ec59e1 (#163/#164): `gcloud run deploy --source .` no encuentra este Dockerfile si solo está en `app/backend/api/`; su alternativa con cloudbuild.yaml ya pasa --build-arg GIT_SHA=${_GIT_SHA}; queda verificar el manifiesto subido (ATOM está ignorado) para cada paquete. No se modifica ese YAML desde Arturo. CORS permite localhost:5173 y `FRONTEND_ORIGIN`, sin credenciales; falta origen real de producción.

La autorización actual no incluye ejecutar comandos GCP ni elegir licencia global. No hay comando cloud en `scripts/deploy.sh`. Derechos/fuentes se revisan sobre el artefacto concreto; un JSON sin precios CARM no demuestra automáticamente que todas las demás fuentes sean abiertas.
