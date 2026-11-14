# H-001 — Encargo de Enrique (kike) al Cursor de Jaime

Autor: enrique (agente Claude). Rama de partida: `t012-motor-nucleo` (leer el último commit, `git log -1`).
**Trabaja en una rama nueva `t020-jaime` creada desde ella. NO unas a `main`: solo los humanos unen.**

Este fichero es autosuficiente: no tienes la conversación. Si algo no está claro, pregunta por el bus (seat `enrique`) en vez de suponer.

## Reglas de trabajo (valen para los tres pasos)

- Haz los pasos **en orden A → B → C**, un commit por paso, y avisa por el bus al terminar cada uno (hash + salida de tests).
- Prueba siempre con: `python3 -m pytest -q app/backend/engine app/backend/ndvi` (en la rama de partida pasan 99).
  **Mira el código de salida real** (`echo $?`), no encadenes `&&` detrás de `pytest | tail`: ya se coló un test roto por eso.
- No cambies pesos de estrategias, el DP ni las reglas agronómicas (`rules.allowed`), salvo lo que pida un paso.
- No hagas descargas de la red ni pongas claves o tokens en ningún fichero. No publiques nada fuera del repo.
- No ejecutes `validate_v1_1.py` de Gonzalo (Enrique no lo ha autorizado). Copiar ficheros de `origin/main` con `git show` sí está permitido.
- Mantén el rigor: números sin fuente se etiquetan «supuesto»; nada de afirmar cumplimiento legal ("herramienta de apoyo, no asesoría").
- Si un test falla o un número cambia mucho, **no lo arregles tapándolo**: descríbelo en el informe.

## Paso A — Revisar el trabajo de los subagentes y regenerar JSON

Contexto: dos piezas las escribieron subagentes Sonnet y nadie las ha revisado.
1. `app/backend/engine/decision/texts.py` (+ `tests/test_texts.py`): genera `texto{por_que, evidencia_resumen, no_sabemos, riesgos_texto, consulta}` por rotación, con plantillas. Hay un validador (`check`) que exige que cada número del texto salga del JSON de esa rotación; se le escapan los números escritos en letra («tres»).
2. `app/backend/ndvi/` (`bare_soil.py`, `appeears_request.py`, `appeears_csv.py`, `README.md`, tests con 50 casos sintéticos): prepara el cálculo de suelo desnudo con NDVI.

Qué hacer:
- Lee `texts.py` y muestrea el `texto` de **todas** las rotaciones de `app/data/torre-pacheco.json` tras regenerar (paso siguiente). Busca: afirmaciones que el JSON no respalda, tono de promesa («garantiza», «seguro»), falta de «no sabemos», números en letra que el validador no ve (mejora el validador para detectarlos si es sencillo), texto en castellano llano.
- Revisa `ndvi/`: productos `HLSL30.020` / `HLSS30.020`; los umbrales NDVI 0,20 y 0,35 son **supuestos** (0,35 sin fuente) y deben estar etiquetados como tales en código y README; que los tests no hagan red.
- Regenera ambos JSON: `python3 -m app.backend.engine.build torre-pacheco` y `python3 -m app.backend.engine.build torre-pacheco --abierto`. Comprueba que `torre-pacheco.abierto.json` **no contiene** las cadenas `CARM-ANUARIO` ni `anuarios`.
- Corrige lo mínimo necesario; commit «A: revisión textos+ndvi, JSON regenerados».

## Paso B — Dos cambios de método que pide Gonzalo (#133)

Archivos: `app/backend/engine/decision/strategies.py` (`simulate`, `draws`) y `app/backend/engine/build.py` (`rotation()`, bloque `exito_pct` y `escenarios*`). Léelos antes.

**B1. `exito_pct` sobre años históricos, no sobre 52 años-plan mezclados.**
Hoy `k_malos`/`n` cuentan cada (año-plan × año histórico) como una muestra: no son independientes y el intervalo de Wilson sale demasiado estrecho.
Nuevo cálculo: sea Y el conjunto de años históricos para los que **todos** los años-plan de la rotación tienen dinero (precio). Un año histórico y es «malo» si, evaluando bajo y el plan completo, algún año-plan tiene `clima_malo` **o** el margen medio del plan en y es < 0 (margen medio = media, sobre los años-plan, del margen de ese año-plan bajo y). Entonces `exito = 1 − k/n` con `n = |Y|`, `k` = nº de años malos, y el intervalo de Wilson con ese n.
En el JSON: `exito_pct.valor` y la horquilla salen de eso; añade `n_anios_historicos` (= |Y|; **dime el valor real: Gonzalo dice 20, el motor ha usado 19; averigua por qué y repórtalo, no lo fuerces**), `n_efectivo` (= |Y|) y conserva el actual 52 como `n_muestras` (informativo). Actualiza `exito_pct.definicion` para explicar el conteo. `peores_anios` se mantiene.

**B2. El índice i de `escenarios` debe ser la MISMA muestra en todas las rotaciones** (mismo año de clima, de precio y mismo factor de coste), porque «B gana al X %» se calcula comparando escenario a escenario.
Hoy solo se comparten los números aleatorios `u` y el multiplicador de coste; el año real lo elige cada rotación de su propia lista (`pools[t][int(u*len)]`), y esas listas difieren, así que i apunta a años distintos.
Nuevo: para cada variante (base, lluvia_-30, …, 2050), calcula el conjunto común C = intersección de los años con dinero de las rotaciones evaluables de esa variante; el escenario i usa en el año-plan t el año `C[int(u_t*len(C))]` en **todas** las rotaciones. Requiere calcular C antes de simular: reestructura `build()` en consecuencia. Las rotaciones no evaluables siguen con `escenarios: null`. Reporta |C| por variante (si C se encoge mucho, dilo).
Al terminar, el build debe exportar `escenarios_meta.alineados = true` (campo nuevo del contrato v1.1 de Gonzalo, en main 18e8275; `false` hasta que esto esté arreglado).
Test nuevo obligatorio: en el JSON construido, `escenarios_meta.anio_clima[i]` y `factor_coste[i]` son idénticos para todas las rotaciones evaluables, para todo i.

Informe obligatorio de este paso: tabla antes/después de `exito_pct.valor`, horquilla y P50 de margen para S0, S1, S2, S3 en `torre-pacheco.json`, y el |C| por variante. Commit «B: éxito sobre años históricos + escenarios emparejados».
(Gonzalo espera mi respuesta sobre B1 y B2 para congelar el contrato; no le contestes tú, dime los números.)

## Paso C — Reglas legales de Gonzalo en lugar de mis reglas provisionales

Hoy `app/backend/engine/decision/rules.py::semaforo()` es provisional. Gonzalo tiene `research/prototypes/legal_rules/{legal.py,rules.csv,grupos_cultivo.csv,test_legal.py}` y un puente `research/prototypes/integration/legal_blocks.py` en `origin/main` (léelos con `git show origin/main:<ruta>`; no están en nuestra rama).
- Copia `legal.py`, `rules.csv`, `grupos_cultivo.csv` a `app/backend/engine/decision/vendor/` (con una línea en un README: origen + commit de `origin/main`) y su test si funciona sin red.
- `semaforo()` pasa a llamar `legal.check(entrada, parcela, zona, contrato=True)` (mira `legal_blocks.entrada_legal` para construir la entrada; nombres de cultivo con su `canon_cultivo`). Conserva en la salida `_status: "simulado"`, `provisional: True`, y que las reglas siguen `por_verificar`.
- **No toques `rules.allowed`** (filtro agronómico del DP): los resultados del motor (márgenes, éxito, rotaciones elegidas) **no deben cambiar** por este paso; solo cambia `semaforo_legal`. Comprueba que el diff de los JSON fuera de `semaforo_legal` es vacío.
- La zona de la parcela (1 o 2 del Mar Menor) está **sin confirmar**: pásala como en `legal_blocks.aplicar` con `zona_2` o la que use Gonzalo por defecto, y deja visible en la salida que es un supuesto.
- Commit «C: semáforo legal con legal.py de Gonzalo».

## Entrega

Al acabar cada paso: mensaje por el bus a `enrique` con (1) hash del commit, (2) salida de pytest con su código de salida, (3) lo que cambió y lo que NO pudiste verificar. Empuja `t020-jaime` a origin. Enrique revisa el diff antes de que nadie una nada.

## Paso D — Reescritor LLM de las tarjetas (T-022), experimental, tras A, B y C

Decisión de Enrique: el LLM solo **reformula** lo que ya está en `texto{...}`; un comprobador determinista impide inventar números; si falla se le dice al modelo qué y dónde falló y reformula; **tras 3 fallos se queda el texto de plantilla**. La tarjeta muestra el texto del LLM si es válido y, si no, la plantilla.
Regla del proyecto: el motor calcula, el LLM no. El LLM nunca ve ni toca cifras que no estén en su lista cerrada.

Crea `app/backend/engine/decision/llm_rewrite.py` (stdlib, sin dependencias nuevas) con:
- Interfaz de modelo intercambiable: `class Backend: complete(system:str, user:str) -> str`. Dos implementaciones: `OpenAICompatible` (para Ollama u otro servidor local: `base_url`, `model`) y `Anthropic` (clave solo desde la variable de entorno `LLM_API_KEY`; **nunca** en ficheros ni por el bus). Selección por variables de entorno. Una `FakeBackend` para tests.
- `rewrite_rotation(rot, backend, max_attempts=3)`: para cada campo de `rot["texto"]`, prompt = plantilla + lista cerrada de números permitidos (`texts.numbers_in`) + reglas («solo reformula; no añadas hechos; conserva toda salvedad y todo «no sabemos»; castellano llano; sin promesas»).
- Comprobación determinista tras cada intento: (1) todo número del texto nuevo ∈ lista permitida, **incluidos los escritos en letra** («tres», «cuarenta por ciento»); (2) todos los números de la plantilla siguen apareciendo; (3) lista de palabras prohibidas («garantizado», «seguro que», «sin riesgo», «asegura»...); (4) longitud ≤ 1,5× la plantilla. Si falla, el siguiente intento recibe un mensaje exacto con lo que falló («número 55 no permitido», «falta 41 %»).
- Salida añadida al JSON, sin tocar `texto`: `texto_llm{campo: {texto, modelo, intentos, valido}}`; si 3 fallos, `valido:false` y la tarjeta usa `texto`. Registrar en `_meta.uso_ia` qué modelo, para qué y la fecha (se declara en el envío). Guardar los prompts y respuestas en `app/data/cache/llm_log/` (sin claves) como evidencia.
- Tests con `FakeBackend`: acepta una reformulación válida; rechaza y reintenta ante un número inventado y ante un número en letra; tras 3 fallos deja la plantilla; no cambia ningún número del JSON fuera de `texto_llm`.
- **No descargues ningún modelo ni nada de red sin avisar a Enrique con nombre, origen y tamaño.** Dime qué runtime/modelo tienes en tu portátil (Ollama, clave de API, otro) y probamos con ese.

## Paso E — Precios abiertos MAPA como proxy (después de B; antes o después de C, tú eliges)

Arturo (T-021) entregó el snapshot: `app/data/tables/mapa_prices.csv` en `origin/arturo-inbox-followup` @ ebc79ee (cópialo con `git show origin/arturo-inbox-followup:app/data/tables/mapa_prices.csv`; léelo junto a `MAPA-SNAPSHOT.md` y `sources.csv` de esa rama). 60 filas: lechuga, melón y alcachofa, anual 2005-2024, nominal EUR/100 kg, `eur_kg` exacto y `eur_kg_real2015` derivado con HICP, `conf=B`, `status=proxy`: **precio nacional genérico, no Murcia, no variedad, sin conversión kg↔pieza, y sin verificar si incluye el coste de recolección**.
Decisión de Enrique: la rotación actual debe ser evaluable en el build abierto con un **proxy explícito «lechuga genérica por kg»**.
- Añade en la capa de precios (`core/price.py`, `build.py`) un nivel MAPA para lechuga, melón y alcachofa **solo en el build abierto** (`--abierto`): sustituye al Eurostat nacional en ese build. El build con CARM **no cambia** (sus precios CARM mandan; comprueba que su JSON no varía salvo `fuentes[]`).
- Lechuga iceberg: valorar los kilos netos (`kg_fallback=True` en `evaluate.py`, ya existe, hoy apagado por defecto) con el €/kg MAPA, **solo si** rendimiento y coste del cultivo están en kg compatibles; si no, la rotación sigue «no evaluable» y lo dices.
- Etiquetado visible en el JSON: `precio.tipo = "proxy"`, la nota de Arturo (nacional genérico, no Murcia, recolección sin verificar), `conf B`, y las `MAPA-PER-*` en `fuentes[]` con su aviso legal («reutilización citando la fuente, Ley 37/2007; no es CC»). Todo texto de tarjeta que use ese precio debe decir que es un proxy nacional.
- Reporta antes/después de la rotación actual y de S1/S3 en el build abierto (hoy S1 y S3 salen 100 % de éxito por el melón Eurostat 0,42 €/kg, optimista frente al de Murcia 0,29). Si MAPA cambia mucho esos números, no lo escondas: descríbelo.
- Tests: carga del CSV (60 claves, sin red), el build abierto no contiene precios CARM, el build con CARM no cambia.

## REPARTO EN 3 SUBTRABAJOS PARALELOS (decisión de Enrique, 14 nov ~17:30; sustituye al orden A→E de arriba)

Haz tres subtrabajos independientes, **cada uno en su rama y su `git worktree`** (si tu Cursor puede lanzar agentes en paralelo, uno por subtrabajo; si no, en este orden: J1, J2, J3). Todos parten de `origin/t020-jaime` @ 91ba395 (A+B hechos).
**Regla común:** no pongas los JSON de `app/data/` en conflicto a mano. Si al integrar chocan, **regénéralos** con `python3 -m app.backend.engine.build torre-pacheco` y `--abierto`. `pytest` con código de salida real. Nada se une a `main`: lo hace Enrique.

**J1 — «AB listo para main»** (rama `t020-ab`, la más urgente)
1. Bug que ha visto Gonzalo (#186): en `exito_pct.definicion` queda un texto sin formatear, `n_muestras = {sim['n_muestras']} conserva...` (f-string sin evaluar). Arréglalo y añade un test que impida cualquier `{` o `}` en los textos exportados.
2. `alineados` hoy solo está por rotación (`rotaciones[i].escenarios_meta.alineados`). Exporta además `escenarios_meta.alineados` en la **raíz**: `true` solo si es `true` en todas las rotaciones con escenarios; test.
3. Rebase sobre `origin/main` (hoy fe60c82 o más nuevo), pytest exit 0, JSON regenerados. Avísame con el hash. Sin push a `main`.

**J2 — «C y luego E»** (rama `t020-c`): paso C (legal.py de Gonzalo) y a continuación paso E (MAPA como proxy en el build abierto), en este orden y en la misma rama porque ambos tocan `build.py`. Un commit por paso y aviso a Enrique por paso.

**J3 — «D reescritor LLM»** (rama `t020-d`): paso D tal como está escrito, con `FakeBackend` y todos los tests. **No elijas modelo todavía**: Enrique te mandará cómo conectarlo. Los JSON solo se tocan al final, regenerando.

## J3 CONCRETO — pipeline de reescritura con Ollama (14 nov ~18:20; sustituye lo genérico del paso D)

Modelo decidido por Enrique: **gpt-oss-20b, cuantización Q4_K_M, servido por Ollama** en el portátil de Jaime (se está instalando). No lo descargues tú ni cambies de modelo: el nombre se lee de `OLLAMA_MODEL` (puede ser `gpt-oss:20b` o el de la importación GGUF; Jaime lo sabe) y la URL de `OLLAMA_URL` (por defecto `http://127.0.0.1:11434`).

1. **System prompt**: ya escrito en `app/backend/engine/decision/prompts/rewrite_system_es.md` (rama `t012-motor-nucleo`). Léelo y cárgalo desde ese fichero; no lo copies al código. Si ves que falta una regla, propónla por el bus, no la cambies sin avisar.
2. **`OllamaBackend`** (stdlib, `urllib`, sin dependencias): `POST {OLLAMA_URL}/api/chat` con `stream:false`, `messages:[system, user]`, `think:"low"` (gpt-oss es un modelo que razona: usa solo `message.content` y descarta `message.thinking`), `options:{temperature:0.2, seed:2026, num_ctx:4096}`, timeout 300 s. Si Ollama no responde: error claro, **no** reintentes en bucle.
3. **Entrada por llamada** (un campo de `texto` de una rotación cada vez): `Texto de plantilla: …` + `Cifras permitidas: …` (de `texts.numbers_in`) + el nombre del campo (`por_que`, `evidencia_resumen`, `no_sabemos`, `riesgos_texto`, `consulta`).
4. **Bucle de verificación** (decisión de Enrique): comprobador determinista tras cada respuesta → si falla, se le devuelve al modelo qué falló y dónde («la cifra 55 no está permitida», «falta la cifra 73 %», «aparece la palabra prohibida “seguro que”») y reescribe; **hasta 3 intentos**; tras el tercer fallo se queda la plantilla (`valido:false`). Comprobaciones: cifras ⊆ permitidas (también cantidades en letra), todas las cifras de la plantilla presentes, palabras prohibidas, longitud ≤ plantilla, y que conserve cada salvedad (palabras clave «provisional», «supuesto», «proxy», «orientativ», «no sabemos» si estaban en la plantilla). Frases de más de 25 palabras → aviso en el log, no fallo.
5. **Salida**: `texto_llm{campo:{texto, modelo, intentos, valido}}` junto a `texto` (que no se toca), `_meta.uso_ia{modelo, cuantizacion:"Q4_K_M", runtime:"ollama", fecha, finalidad:"reformular textos de tarjetas; no calcula"}`, y logs de prompts/respuestas en `app/data/cache/llm_log/` (sin claves; no hay claves). La tarjeta muestra `texto_llm` si `valido`, si no `texto`.
6. **CLI**: `python3 -m app.backend.engine.decision.llm_rewrite app/data/torre-pacheco.abierto.json [--dry-run]`; `--dry-run` usa `FakeBackend` y no necesita Ollama. Antes de llamar al modelo comprueba `GET /api/tags` y que `OLLAMA_MODEL` exista; si no, para y avisa (no hace `pull`).
7. **Pruebas** con `FakeBackend` (sin red): acepta una reescritura válida; reintenta con el mensaje de error ante cifra inventada, cifra en letra, salvedad perdida y palabra prohibida; tras 3 fallos deja la plantilla; el resto del JSON queda idéntico fuera de `texto_llm` y `_meta.uso_ia`.
8. **Prueba real** cuando Ollama esté listo: ejecútalo sobre el JSON abierto y mándame a `enrique`: cuántos campos pasaron a la 1.ª, 2.ª, 3.ª o fallaron, y 3 ejemplos antes/después **tal cual salieron**. No retoques a mano ninguna salida.
