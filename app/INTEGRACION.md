# Agrockham integrada: cómo ejecutarla en local

Rama `integracion`. Une la API (Gonzalo), el motor por parcela (Enrique, con la tabla de idoneidad de Arturo) y el
frontend (Jaime). No está fusionada en `main`. El panel del frontend que muestra el resultado está en construcción:
esta guía dice qué hay hoy y qué no.

## Arrancar en pocos comandos

Desde la raíz del repo, en dos terminales.

```bash
# Terminal 1: API con el motor en vivo, en http://127.0.0.1:8080
bash scripts/dev_app.sh

# Terminal 2: frontend, en http://127.0.0.1:5173
cd app/frontend && npm install && npm run dev
```

Antes de la primera vez, el script pide un entorno de Python. Si falta, escribe el comando para crearlo:

```bash
python3 -m venv ~/.venvs/agrockham-api && ~/.venvs/agrockham-api/bin/pip install -r app/backend/api/requirements-dev.txt
```

Qué hace `scripts/dev_app.sh`:

- Usa el Python de `~/.venvs/agrockham-api/bin/python`. Se cambia con `AGROCKHAM_PY`.
- Si no hay recintos completos (`ATOM_BUILD_DIR` sin definir y sin `app/backend/api/atom_build`), crea una muestra de
  66 recintos alrededor de la parcela demo, la misma que usan los tests. Avisa de ello. Fuera de esa zona,
  `/analyze` no encuentra parcela.
- Pone `ENGINE_MODE=vivo` y `FRONTEND_ORIGIN=http://127.0.0.1:5173` si no los has definido.
- Lanza `uvicorn app.backend.api.main:app` en `127.0.0.1`, puerto `8080` (o `PORT`).

Variantes que trae el propio script:

```bash
ENGINE_PRECIOS=carm bash scripts/dev_app.sh        # solo en local: precios CARM (permiso pendiente, no publicar)
OLLAMA_URL=http://127.0.0.1:11434 OLLAMA_MODEL=gpt-oss:20b NARRATIVA_GUARDAR=1 bash scripts/dev_app.sh   # textos del LLM en vivo
```

Documentación interactiva de la API: `http://127.0.0.1:8080/docs`.

Cómo sabe el frontend dónde está la API: lee `VITE_API_BASE` (por defecto `http://127.0.0.1:8080`) en
`app/frontend/src/api/client.js`. La ficha de la parcela vive en `app/frontend/src/components/parcel/`.

## Variables de entorno

| Variable | Por defecto | Qué hace |
|---|---|---|
| `ENGINE_MODE` | vacío en la API; `vivo` si arrancas con `scripts/dev_app.sh` | `vivo` usa `LiveEngine`: calcula el motor para cada parcela. Vacío = motor anterior (JSON de `ENGINE_JSON` o contrato de ejemplo simulado) |
| `ENGINE_PRECIOS` | `abierto` | `abierto` = precio medio nacional del MAPA como proxy, más Eurostat. `carm` = precios del anuario de la CARM, solo en local mientras el permiso siga pendiente |
| `OLLAMA_URL` | vacío | Dirección del Ollama local (por ejemplo `http://127.0.0.1:11434`). Sin ella, `POST /narrativa` no genera texto: solo sirve los ya guardados |
| `OLLAMA_MODEL` | `gpt-oss:20b` | Modelo que usa el reescritor. Lo lee `llm_rewrite.py` |
| `OLLAMA_TIMEOUT_S` | `300` | Tiempo máximo por llamada al modelo |
| `OLLAMA_THINK` | `low` para modelos `gpt-oss`; vacío para el resto | Nivel de razonamiento que se pide a Ollama. Se descarta lo que el modelo "piensa" y se usa solo la respuesta |
| `NARRATIVA_DIR` | `app/data/cache/narrativa` | Carpeta de textos ya generados |
| `NARRATIVA_GUARDAR` | sin definir | Con `1`, cada texto generado en vivo y válido se guarda en `NARRATIVA_DIR` |
| `AGROCKHAM_PY` | `~/.venvs/agrockham-api/bin/python` | Python que usa `dev_app.sh` |
| `PORT` | `8080` | Puerto de la API |
| `FRONTEND_ORIGIN` | `http://127.0.0.1:5173` con `dev_app.sh` | Origen extra permitido por CORS. La API solo acepta siempre `http://localhost:5173`; `http://127.0.0.1:5173` (donde arranca Vite) entra porque `dev_app.sh` lo pone aquí |
| `ATOM_BUILD_DIR` | `app/backend/api/atom_build` | Recintos SIGPAC completos. Ver `app/backend/api/README.md` |
| `ENGINE_JSON` | vacío | JSON del motor precalculado. Sirve de respaldo si el motor en vivo falla |

El resto de variables de la API (`CONTRACT_PATH`, `PIPELINE_CACHE_DIR`, `LIVE_*`, `RECINTOS_*`, `CACHE_MAX`,
`AGROCKHAM_OFFLINE`) están en `app/backend/api/README.md`.

## Cómo se conectan las piezas

```
clic en un recinto (frontend)
   -> POST /analyze {lat, lon, recinto, zona}                  app/backend/api/main.py
   -> blocks.py: parcela (ATOM), clima y suelo (pipeline), semáforo legal
   -> engine_adapter.LiveEngine.run()
        parcel_input.construir()  ->  build.run_parcel(parcel_input)    app/backend/engine/
   -> contrato v1.1 por bloques: rotaciones + idoneidad, clima_origen, actual_origen, no_evaluable
   -> panel del frontend (en construcción)

después, por cada tarjeta que quiera un texto reescrito:
   -> POST /narrativa {id, rotacion, campos}                   app/backend/api/narrativa.py
   -> texto guardado y revalidado, o generado por el modelo local, o la plantilla de siempre
```

Puntos que conviene saber:

- `run_parcel` no usa red. Solo lee las tablas del repo. El clima y el suelo reales de la parcela los trae la API
  (pipeline), pero el motor usa su propia estación (ver "Límites").
- Si el motor en vivo falla, la API no se cae: sirve el motor de respaldo y lo dice en `_meta.avisos`.
- `POST /narrativa` va aparte de `/analyze` porque puede tardar. Necesita haber hecho antes un `/analyze`: busca la
  consulta por `_meta.consulta_id` o `parcela.id`.
- El motor está explicado en `app/backend/engine/README.md`. La API, en `app/backend/api/README.md`.

## Generar los textos del modelo antes de la demo

Hace falta una máquina con Ollama y el modelo instalado. No se descarga nada solo: si el modelo no está, el
reescritor se para y lo dice. El modelo previsto es gpt-oss-20b en cuantización Q4_K_M, en el portátil de Jaime.

1. Arranca la API con el modelo y con guardado:

   ```bash
   OLLAMA_URL=http://127.0.0.1:11434 OLLAMA_MODEL=gpt-oss:20b NARRATIVA_GUARDAR=1 bash scripts/dev_app.sh
   ```

   `OLLAMA_MODEL` puede llevar otro nombre si el modelo se importó de otra forma (por confirmar con Jaime).
2. Comprueba `GET /health`: el bloque `narrativa` dice si el modelo está en vivo y cuántos textos hay guardados.
3. Pide un `POST /analyze` y luego `POST /narrativa` con el `id` de la consulta y el `id` de cada rotación. Hazlo desde
   el frontend o a mano con `curl`. Cada texto válido se guarda en `app/data/cache/narrativa/<sha256 de la plantilla>.json`.
4. Con esos ficheros, la API sirve el texto sin modelo. Antes de servirlo vuelve a pasar el comprobador contra la
   plantilla actual. Si el motor cambia una cifra, el fichero viejo se rechaza y se muestra la plantilla.

Solo se guardan los textos que pasan el comprobador. La carpeta `app/data/cache/narrativa/` no está en `.gitignore`.
Si se versiona para que llegue a otro despliegue: por confirmar.

También se puede reescribir un JSON del motor entero desde la línea de órdenes (ver `app/backend/engine/README.md`).

## Pruebas

```bash
# API (sin red). Si pytest no encuentra los módulos, lanza desde la raíz con python -m pytest.
~/.venvs/agrockham-api/bin/python -m pytest app/backend/api -q

# Motor: parcela, reescritor, idoneidad
~/.venvs/agrockham-api/bin/python -m pytest app/backend/engine -q
```

Resultado medido en la rama `integracion` para todo `app/backend`, sin `app/backend/pipeline/atom/tests/test_lookup.py`
(necesita `pyogrio`, que no está instalado): **352 pasan, 7 se omiten**. El comando de la medición no se repitió al
escribir esta guía. Los dos de arriba son más acotados.

Tests nuevos de esta integración:

- `app/backend/engine/decision/tests/test_parcela.py`: motor por parcela.
- `app/backend/engine/decision/tests/test_llm_rewrite.py`: reescritor, con un modelo falso, sin red.
- `app/backend/api/tests/test_live_engine.py`: `LiveEngine` y `POST /narrativa`, sin red.

## Mediciones (portátil del desarrollador, 14-nov-2026)

- Una ejecución de `run_parcel`: de 0,7 a 0,8 s.
- Memoria máxima de Python: unos 18 MB por ejecución.
- Ocho ejecuciones a la vez en hilos: todas devolvieron resultados correctos.
- El motor solo carga `numpy` como paquete externo. `scipy` se importa solo si se pide el intervalo de Jeffreys.
- `POST /analyze` completo de la parcela demo con el motor en vivo: unos 1,1 s.
- `POST /analyze` de un punto cuyo suelo no está en caché: unos 7 s.

## Límites conocidos

Léelos antes de enseñar la app. No están suavizados.

1. **El clima es de una sola estación** (SIAM TP91, Torre-Pacheco) para cualquier parcela. La salida lo dice en
   `clima_origen` y avisa si la parcela está a más de 30 km. Esos 30 km son un supuesto sin fuente.
2. **La pendiente cambia la puntuación, pero no qué rotación gana.** En la tabla de Arturo, las penalizaciones por
   pendiente son iguales para las cuatro hortalizas. Lo que de verdad cambia hoy entre parcelas es:
   - secano: sale "no evaluable", porque el catálogo solo tiene cultivos de regadío con coste y rendimiento;
   - la zona legal;
   - el cultivo declarado a FEGA, que pasa a ser la rotación de referencia;
   - la etiqueta ambiental;
   - los totales para la superficie de la parcela.
3. **La idoneidad nunca cambia euros, kilos ni porcentajes de éxito.** Pero los escenarios se alinean sobre los años
   comunes a todas las rotaciones mostradas (decisión D-011, `coordination/DECISIONS.md`). Por eso las cifras de una
   rotación pueden moverse un poco cuando cambia la rotación de referencia.
4. **Con datos abiertos, la lechuga no tiene precio y sus rotaciones salen «sin precio: no se puede calcular».** Decisión de
   Enrique (14-nov-2026). Motivo: la única serie abierta de lechuga es la media nacional del MAPA, que mezcla todos los
   tipos y queda ~35 % por debajo de la iceberg de Murcia; con ella la misma parcela con lechuga tres años seguidos daba
   −7.677 €/ha y 0 % de años buenos (con precios CARM, +1.440 €/ha y 38,9 %). No encontramos ninguna fuente abierta de
   iceberg en origen. Esas rotaciones siguen mostrando agua, semáforo legal y medio ambiente, y no se compara su dinero
   con el de las demás. Melón, brócoli y alcachofa mantienen el precio nacional del MAPA como proxy etiquetado.
   Los precios CARM solo se usan con `ENGINE_PRECIOS=carm` explícito; el permiso de la CARM sigue pendiente.
5. **Todos los porcentajes de idoneidad y los umbrales de la etiqueta ambiental son supuestos del proyecto** (confianza
   C), no mediciones.
6. **El modelo de lenguaje previsto no se ha probado.** Sí se probó el reescritor con un modelo pequeño,
   `granite3.3:2b`, en el portátil del desarrollador: el comprobador rechazó 4 de 4 textos y se usó la plantilla en los
   4. Tardó 7 minutos. El modelo previsto (gpt-oss-20b Q4_K_M con Ollama, en el portátil de Jaime) todavía no se ha
   probado.
7. Las rotaciones y sus cifras son las del motor para esa parcela, pero `historia`, `ndvi` y el suelo siguen sus
   propios estados (`_status` de cada bloque). No es consejo agronómico ni legal.

## Todo en un portátil con un solo comando

`bash scripts/demo_local.sh` arranca la API (motor en vivo, precios abiertos) en :8080 y el frontend en :5173. Si detecta
Ollama en `http://127.0.0.1:11434`, activa los textos del modelo local (`OLLAMA_MODEL`, por defecto `gpt-oss:20b`) y guarda
en `app/data/cache/narrativa/` los textos que pasan el comprobador. Sin Ollama, la ficha muestra la plantilla de siempre.
Requisitos una sola vez: entorno de Python (`requirements-dev.txt` de la API), `npm install` (lo hace el script) y, para el
texto del modelo, `ollama pull gpt-oss:20b` (~13 GB). Con la muestra de 66 recintos solo se encuentran parcelas alrededor de
la demo de Torre-Pacheco; con `ATOM_BUILD_DIR` apuntando a los recintos completos se encuentran todas.

## Frontend nuevo (2026-11-14 noche, `integracion` @b9033df)

Hecho por Enrique a petición del usuario (aunque `app/frontend/` es de Jaime; avisado por el bus). Todo en `app/frontend/src` y `design/tokens.css`; la API no cambia.

- **Ficha de parcela** (`components/parcel/`): una línea por opción (puesto, cultivos, puntuación 1-100, flags Eco y Riesgo); clic en la línea abre cuatro cifras y una explicación de 3 líneas; supuestos y notas plegados. La unidad es la **rotación de 3 años** (el motor no puntúa cultivos sueltos). La puntuación es `priorityScore(criterios, sliders de Filtros)`, **relativa** entre las opciones calculadas, no una probabilidad. La referencia va última y sin puntuación. Riesgo = % de años buenos (≥90 bajo, 75-89 medio, <75 alto: umbrales **supuestos**, la frase lo dice). Lógica pura y tests en `ranking.js` / `ranking.test.js`.
- **Tus parcelas** (`state/myParcels.js`, `useMyParcels.js`, `components/MyParcelsPanel.jsx`): solo en el navegador (`localStorage`, clave `agrockham.misParcelas.v1`), sin cuentas ni servidor. Alta con el botón Guardar de la ficha; nombre por defecto «Parcela N», editable; contorno rojo y relleno translúcido en el mapa (capas `mis-parcelas-*`, filtro por propiedades de la tesela SIGPAC). Ojo: el filtro vacío debe ser `NO_MATCH` (`['==',['literal',1],0]`); un `['==',1,0]` tumba todo el mapa.
- **Portada**: animación inicial del globo (`homeSpin.js`, `config/map.js` → `HOME_SPIN`): 2 s de giro, 5 s casi quieta, 2 s de cierre, reposo en la posición de siempre; cualquier toque la cancela; respeta `prefers-reduced-motion`. Móvil: el globo no se arrastra, cualquier toque abre el mapa; `100dvh`; tipografía Brunson (solo si instalada) → Impact.
- **Sin cobertura**: el cuadro grande «no hemos encontrado un recinto» pasó a una línea pequeña, con un reintento automático a los 4 s (el servidor puede estar cargando los recintos).
- **Tests**: `cd app/frontend && node --test src/state/*.test.js src/components/*.test.js src/components/parcel/*.test.js` (26) y `npm run build`.
- **Sin comprobar**: móvil real (táctil, Android), fluidez de la animación en GPU real.
