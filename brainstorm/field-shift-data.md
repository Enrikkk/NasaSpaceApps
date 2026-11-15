# 🎯 RESUME HERE (written 2026-11-14 ~19:55 bus clock, before 5th /compact) — NEWEST, overrides older blocks
**Situation.** App integrada (frontend Jaime + motor por parcela Enrique + API Gonzalo + texto LLM) TERMINADA y subida en la rama `integracion` @ **f964717** (NO en main: merge = solo humanos). 356 tests backend pasan (7 skip) con `~/.venvs/agrockham-api/bin/python -m pytest app/backend -q -p no:cacheprovider --ignore=app/backend/pipeline/atom/tests/test_lookup.py`. Gonzalo ya desplegó API v7 (a082305, sin frontend). Falta: v8 = API+frontend en una URL (Gonzalo), 3ª pasada LLM de Jaime, y el mensaje "trabajo pendiente" de Gonzalo.
**Next action (literal).** 1) Re-armar el monitor del bus si caducó (`Monitor`: `cd "/home/enrikkk/Desktop/Computer Science/Hackathons/NasaSpaceApps" && SEAT=enrique bash scripts/bus_listen.sh`, 1.800.000 ms; id actual bqvg560sr, caduca ~20:20). Eventos truncados: `grep -a "#NNN" /tmp/claude-1000/-home-enrikkk-Desktop-Computer-Science-Hackathons/322a41e6-82ad-4143-9bf5-d372673838a1/tasks/<id>.output`. 2) Cuando llegue el mensaje de Gonzalo con trabajo pendiente: pasarlo por /mcq-explain + /drop-jargon al usuario (las decisiones se toman AQUI, no en el bus). Incluir en esa ronda la pregunta de Gonzalo #296: ¿se fusionan t012-motor-nucleo/t020 en main y en qué orden? (decisión humana; `integracion` ya los contiene todos: la cuestión real es si `integracion` entra entera en main). 3) Cuando Jaime mande la 3ª pasada LLM (esperable: s2 y actual necesitan 2 intentos, 0 caídas a plantilla): si OK, dar el LLM por cerrado. 4) Cuando Gonzalo dé URL+hash de v8: abrirla, 'Ir a mis parcelas', clic en recinto demo 18/426/1 (ficha con rotaciones; las de lechuga "Sin precio").
**In-flight.** Nada sin subir (git limpio salvo el PDF sin trackear: NUNCA commitearlo sin preguntar). Procesos locales: API uvicorn :8080 (arrancada con `scripts/dev_app.sh` con OLLAMA_URL=http://127.0.0.1:11435 falso -> el Ollama falso ya está parado, así que /narrativa cae a plantilla) y `vite preview` :5173 (build de producción de t010-cierre). Reiniciarlos con `setsid nohup bash scripts/dev_app.sh ... &` (NO usar `pkill -f` en el mismo comando: se mata a sí mismo, exit 144; matar por puerto: `ss -ltnp | grep :8080 | sed -E 's/.*pid=([0-9]+).*/\1/' | xargs kill`).
**Already verified — do not redo.** Navegador real (puppeteer) a 1440 y 390 px: clic en recinto -> POST /analyze -> ficha IZQUIERDA con Tu parcela/Cómo influye/rotaciones; sin recinto -> aviso "No hemos encontrado un recinto aquí"; tarjetas con lechuga -> "Sin precio: no se puede calcular"; ruta del texto LLM con Ollama falso ("Explicado por un modelo de IA local · cifras comprobadas" + "ver texto original"); build de PRODUCCIÓN carga el worker de MapLibre y abre la ficha. `npm run build` + `node --test` OK. LLM real (Jaime, Mac, gpt-oss-20b:latest Q4_K_M, `OLLAMA_MODEL=gpt-oss-20b:latest python3 -m app.backend.engine.decision.llm_rewrite app/data/torre-pacheco.abierto.json --campos por_que`): 12 s / 4 textos, 4/4 válidos al intento 1; s1 y s3 suenan naturales; s2 salió roto ("Sale probar") y actual casi igual -> arreglado en f964717 (check() rechaza «sale probar» y respuestas que solo borran 1–3 palabras).
**Settled decisions — do not re-litigate.**
- LECHUGA en modo abierto = SIN PRECIO (kg_fallback=False en build.py; rotaciones con lechuga "no se puede calcular", se mantienen agua/semáforo/ambiente; se omite la comparación en € con la referencia). Motivo: MAPA nacional "lechuga" mezcla tipos, ~35 % bajo iceberg Murcia (~0,43 €/kg CARM): lechuga x3 = −7.677 €/ha 0 % abierto vs +1.440 €/ha 38,9 % CARM. Búsqueda (subagente) NO halló fuente abierta de iceberg en origen: solo Mercamadrid mayorista CC BY 4.0 (2019-2025) y EC agridata farmgate sin verificar. RECHAZADO: factor de corrección derivado de datos CARM (sigue saliendo de datos no publicables); Mercamadrid con margen inventado. Melón/brócoli/alcachofa mantienen el proxy MAPA etiquetado. Supersede la decisión antigua "lechuga por kilo con MAPA".
- Modo abierto por defecto; CARM solo con ENGINE_PRECIOS=carm (permiso pendiente; el usuario manda el correo a la CARM él mismo).
- Aprobación de cifras: humana (Enrique); los agentes no la dan.
- Panel de parcela a la izquierda (el .side de Jaime a la derecha); Brunson fuera (licencia); worker MapLibre vía setWorkerUrl (Jaime t010-cierre ffdf168, ya fusionado).
**Hard-won facts.** Rama `integracion` incluye: t020-jaime, t012-motor-nucleo, arturo-idoneidad, arturo-contract-tests, arturo-inbox-followup, t026, t010-frontend-skeleton, t010-cierre, main (hasta 1f6838f). NO incluye (por qué): t015-submission-texts (Gonzalo: textos Devpost; interesa traer), t017-* (Arturo, solo QA/docs), research-sigpac-viability (docs), t020-ab (J1 duplica mis arreglos), t024-live-api (probablemente en main con otros hashes; sin verificar). Fixes de esta etapa: `texts.py` "que ahora"->"que la referencia" si origen supuesto_zona (6ba64dd); `blocks.py` por_parcela solo con recinto real (62746d4, hallazgo de Arturo); error del panel (a5e6489 + Jaime ffdf168); prompt LLM `engine/decision/prompts/rewrite_system_es.md` (margen 15 %, regla gramática, 2º ejemplo) y `MAX_LEN_RATIO=1.15`. Script `scripts/demo_local.sh` (API+vite+Ollama, autodetecta nombre gpt-oss) para el portátil de Jaime; docs en `app/INTEGRACION.md`. Bus: scripts en scratchpad `/tmp/claude-1000/-home-enrikkk-Desktop-Computer-Science-Hackathons/b25ffb0e-70c5-40de-897b-e3b8363b4439/scratchpad/send_bus22.py…29.py` (patrón: cabecera de send_bus22 + `msgs=[(to, task, text)]` + bucle `for to, task, text in msgs`). El bus corta a ratos (hub unreachable): reintentar tras ~20 s. Honest limits: una sola estación SIAM para todas las parcelas; la pendiente penaliza igual a los 4 cultivos; en abierto, referencia con lechuga sin dinero; la cifra de Gonzalo "−7.677" era la parcela declarando LECHUGA x3.
**Waiting on.** Jaime: 3ª prueba LLM (#323). Gonzalo: v8 (API+frontend, build con VITE_API_BASE=<URL Cloud Run>) y su mensaje de trabajo pendiente. Arturo: QA final sobre f964717 (fijó 3c45f63 antes; le avisé de f964717).
**Open for the user (only they can do).** Fusionar `integracion` en main; correo CARM; cuentas Earthdata/CDSE para NDVI; revisión agronómica de ventanas; confirmar licencia gpt-oss-20b en `submission/ai-use.md`; confirmar la descarga de gpt-oss:20b en la máquina de Jaime; decidir si se trae t015-submission-texts a integracion.


# (older) 🎯 RESUME HERE (written 2026-11-14 ~21:00, before 4th /compact) — NEWEST, overrides older blocks

**Situation.** Integrating Gonzalo's API + the prediction engine + Jaime's frontend into ONE app on branch `integracion` (pushed; NOT merged to main; only humans merge). Backend and frontend code are DONE and committed. The only thing left of the build is the **real browser test of the parcel panel**, which was interrupted halfway by the compaction.

**Immediate next action.** Finish the browser test with the puppeteer MCP tools (load with ToolSearch `select:mcp__puppeteer__puppeteer_navigate,mcp__puppeteer__puppeteer_screenshot,mcp__puppeteer__puppeteer_evaluate,mcp__puppeteer__puppeteer_click`):
1. Check both servers are up: `curl -s http://127.0.0.1:8080/health` (API) and `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5173/` (Vite). If down: `bash scripts/dev_app.sh` (repo root, background) and `cd app/frontend && npm run dev` (background).
2. Navigate to `http://127.0.0.1:5173/`, click the button whose text is "Ir a mis parcelas" (via evaluate), wait ~9 s. ALREADY SEEN WORKING: map lands at zoom 15.5 on 37.7383,-0.98838 with 167 recintos rendered (`window.__agroMap` exists in dev).
3. Click the demo parcel: `m.fire('click', {lngLat:{lng:-0.98838,lat:37.7383}, point: m.project([-0.98838,37.7383])})` or a real mouse click at the map centre; wait ~3 s; take a screenshot (1440x900) and read it: panel on the LEFT with header, "Tu parcela", "Cómo influye tu parcela", rotation cards, footer with FEGA attribution.
4. Also check what the subagent could NOT see: (a) a click with no recinto / outside the 66-recinto sample (`sin_cobertura` banner), (b) `no_evaluable` (rainfed; hard to trigger from the UI, the API test covers it), (c) mobile 390 px bottom sheet after the offset change to 84 px.
5. Fix what is wrong, `npm run build`, commit, push. Then report to Enrique and send Jaime + Gonzalo the hash on the bus.

**In-flight state.**
- Background processes left running from this session: API (uvicorn, port 8080, `ENGINE_MODE=vivo`, mini ATOM sample of 66 recintos, logs in scratchpad `api.log`) and Vite dev server (port 5173, `vite.log`). Kill with `pkill -f "uvicorn app.backend.api.main"` / `pkill -f vite` if stale.
- Bus monitor `b7xhlaocs` expires ~21:05: re-arm (Monitor, `cd <repo> && SEAT=enrique bash scripts/bus_listen.sh`, 1800000 ms).
- Working tree is clean except the untracked web-Claude PDF (never commit it without asking).
- Jaime's branch `t010-frontend-skeleton` keeps moving: re-merge it into `integracion` before the final hash (last merged: eddccab). Only conflict ever seen in any merge: `submission/data-citations.md` → keep both sides (remove the markers).

**Already verified — do not redo.**
- Backend: 352 passed, 7 skipped with `~/.venvs/agrockham-api/bin/python -m pytest app/backend -q -p no:cacheprovider --ignore=app/backend/pipeline/atom/tests/test_lookup.py` (that file needs `pyogrio`, not ours).
- Engine regression: demo parcel gives identical money/success/water/scenarios as before; `run_parcel` 0.7–0.8 s, ~18 MB peak, thread-safe with 8 threads, no network, only numpy (scipy lazy, Jeffreys only).
- API live: `POST /analyze` demo 1.1 s (HTTP 200, validates against Gonzalo's contract validator); point without recinto 7.3 s.
- LLM pipeline: 18 tests with FakeBackend; real run with `granite3.3:2b` here = 4/4 rejected by the checker → template, 7 min (too slow here: Enrique said run LLM tests on JAIME's machine).
- Frontend: `npm run build` passes; subagent saw the panel render in headless Chrome at 1440 and 390 px with a mocked `/narrativa`.

**Settled decisions — do not re-litigate.**
- Enrique: "Lo hago todo yo" → I did J1, E (MAPA), J3 (LLM rewriter), H-002 `run_parcel`; Jaime's Cursor only does frontend. Jaime's late J1 (`t020-ab` abc09fe) duplicates my fixes: NOT merged.
- Enrique: installing project deps is fine (npm in `app/frontend`, venv `~/.venvs/agrockham-api`).
- Enrique: use subagents, Sonnet unless complex (then Opus), effort high.
- Enrique: LLM tests on Jaime's machine, not here.
- Gonzalo's conditions (#246), all applied: open prices by default, CARM only with `ENGINE_PRECIOS=carm`; env-activated (`ENGINE_MODE=vivo`); fallback to previous engine + `_meta.avisos`; no endpoint/contract change; no network; rainfed = "no evaluable". LLM text outside `/analyze` in `POST /narrativa` (#247), precomputed files for the public deploy.
- Earlier ones still stand: ignore the "14 common years" issue; lettuce priced per kilo with the generic MAPA price (explicit proxy); environmental option is a label alto/medio/bajo; suitability = exclude the impossible + % on the DP score, never on euros.

**Hard-won facts.**
- Commits on `integracion`: 393ef24 merges · 41afdff engine per parcel + J1 + E · 02e7008 LLM rewriter · (API LiveEngine + /narrativa) · 136da2f · 3c225b7 dev script · 3c3abb4 docs · then the frontend panel commit (see `git log`).
- Files: `app/backend/engine/parcela.py`, `build.run_parcel`, `engine/decision/llm_rewrite.py`, `app/backend/api/{engine_adapter.py (LiveEngine), narrativa.py, main.py (/narrativa), settings.py, blocks.py}`, tests `engine/decision/tests/{test_parcela,test_llm_rewrite}.py`, `api/tests/test_live_engine.py`; frontend `app/frontend/src/api/client.js`, `src/components/parcel/*`; docs `app/INTEGRACION.md`, `app/backend/engine/README.md`; run script `scripts/dev_app.sh`.
- Frontend facts: API base `VITE_API_BASE` (default `http://127.0.0.1:8080`); CORS for `http://127.0.0.1:5173` only because `dev_app.sh` sets `FRONTEND_ORIGIN`; panel sits on the LEFT (Jaime's `.side` is on the right); priorities map beneficio→margen, agua→agua, suelo→suelo_n, riesgo→riesgo; `/analyze?bloques=parcela` and the full call run in parallel.
- Contract test trap: any key named `semaforo_legal` is treated as a full legal block → mine is `ambiente.metricas.color_legal`.
- Open-mode numbers (public default): reference −1.041 €/ha, 33.3 % good years; S1 7.746 €/ha, 100 %. CARM mode: reference 1.067, 41.2 %; S1 3.045, 81.2 %.
- Honest limits already told to Enrique: slope penalty equal for the 4 crops (score changes, winner does not); one climate station for every parcel (`clima_origen` warns beyond 30 km, unsourced threshold); a rotation's money shifts slightly when the reference rotation changes (D-011 common years).
- Bus: send via the scratchpad scripts `send_bus14..17.py` pattern (≤3 short messages). Last sent: #251–253 to Jaime (run LLM test with gpt-oss-20b, branch `integracion`), #261–263 to Gonzalo (hash 136da2f, Docker file list: exclude `engine/data/official/carm_precios_mensuales.csv` = restricted; SIAM series has no explicit open licence; asked for his 5-municipality ATOM build).

**Open / waiting.**
- Jaime's agent: result of the real LLM test (counts per attempt, time, 3 before/after examples). Not answered yet.
- Gonzalo: review + v6 image; how to get his full `atom_build`. Not answered yet.
- For Enrique to decide later: (1) demo price mode: open (publishable, reference loses money) vs CARM (more realistic, permission pending); (2) merge `integracion` into main (human only) once the browser test passes; (3) still pending from before: CARM permission email, Earthdata/CDSE accounts for NDVI, agronomist check of stage windows, gpt-oss-20b licence to confirm in `submission/ai-use.md`.


---

> # 🎯 RESUME HERE (written 2026-11-14 ~18:25, before 3rd /compact) — NEWEST, overrides older blocks
>
> **Situation.** Enrique (seat `enrique`) is now ORCHESTRATOR ONLY, to save tokens ("ahorra tokens", "deja de leer tanto y hacer tanto"): engine work is delegated over the team bus to **Jaime's Cursor agent** and **Arturo's agent**; I write briefs, review what comes back, answer teammates, give hashes. My branch `t012-motor-nucleo` @ **c1595a2** (pushed, NOT merged). Only humans merge to `main`.
>
> **Immediate next action.**
> 1. Re-arm the bus monitor (id `bdicniqd5` expires ~18:45): Monitor `cd "/home/enrikkk/Desktop/Computer Science/Hackathons/NasaSpaceApps" && SEAT=enrique bash scripts/bus_listen.sh`, timeout 1,800,000 ms. Truncated events: grep the Monitor `.output` under `/tmp/claude-1000/-home-enrikkk-Desktop-Computer-Science-Hackathons/322a41e6-82ad-4143-9bf5-d372673838a1/tasks/<id>.output`.
> 2. When Jaime delivers **J1** (branch `t020-ab`): review in a temp worktree (`git worktree add --detach <scratch>/wt origin/t020-ab`, `python3 -m pytest -q app/backend/engine app/backend/ndvi`, read the real exit code, remove the worktree), check the two fixes, then send **Gonzalo the hash** (he is waiting, redeploy held) and tell Enrique to merge (human). 
> 3. Ask Enrique one thing still unanswered: "accept Arturo's H-002 v1 (`bcda1bd`, `origin/arturo-idoneidad`, 46 tests pass, 14 active factors + 46 neutral, honest gaps) as is, to be integrated by Jaime later?" (my recommendation: yes).
> Do NOT start engine work myself unless Enrique asks.
>
> **In-flight state (nothing is applied to main).**
> - **Jaime's Cursor** (answers by bus, seat `jaime`; the bus always says "no live agent, waits in inbox": normal). Delivered on `origin/t020-jaime`: A (e7615d4: texts validator catches written-out numbers, NDVI thresholds labelled supuesto, JSON regenerated), B (91ba395), C (57561e9: `semaforo()` calls Gonzalo's `legal.check`, vendored in `decision/vendor/`, zone = `por_verificar`; actual rotation legal colour green→yellow with CARM). He said "sigo con E" (old order); I reminded him (#219/#220) to do **J1 first**. Sub-jobs (H-001 end, "REPARTO EN 3 SUBTRABAJOS"): **J1** `t020-ab` from 91ba395 (A+B only): fix the unformatted f-string `{sim['n_muestras']}` in `exito_pct.definicion`, add root `escenarios_meta.alineados` (true iff true in all evaluable rotations), test, rebase on `origin/main`, regenerate JSONs; **J2** `t020-c`: C then E (MAPA proxy in open build); **J3** `t020-d`: Ollama rewriter (spec "J3 CONCRETO" + prompt `app/backend/engine/decision/prompts/rewrite_system_es.md`, c1595a2). Then **H-002** `run_parcel` (after J1–J3).
> - **Jaime is installing gpt-oss-20b Q4_K_M under Ollama** (model name via `OLLAMA_MODEL`; he knows it; nobody downloads anything without asking Enrique).
> - **Arturo**: T-027 `arturo-idoneidad` bcda1bd (H-002 v1); T-025 `arturo-contract-tests` fa806a2 (14/14 contract tests pass on both JSONs, base 91ba395; NOT yet brought into our branch: do it after J1). He found NO missing `fuente_id` (Gonzalo's claim was wrong; Gonzalo told in #194). Arturo's MAPA snapshot: `app/data/tables/mapa_prices.csv` @ ebc79ee on `origin/arturo-inbox-followup` (lechuga/melón/alcachofa, 60 rows, proxy conf B).
> - **Gonzalo**: waits for my hash; holds redeploy; owns T-009, T-011, T-019, T-024 (API live on Cloud Run `https://agrockham-api-530791362085.europe-west1.run.app`, `/health`, `/analyze`). The public image uses the OPEN JSON (no CARM) by his decision. Asked (#197) for per-parcel engine → decided "A completo" (below). I told him to show the "reference parcel" notice meanwhile.
> - Handoff files (branch `t012-motor-nucleo`): `coordination/handoffs/H-001-jaime-cursor.md`, `H-002-motor-por-parcela.md`.
>
> **Already verified — do not redo.** pytest 101 passed on `origin/t020-jaime` at A (my temp worktree, exit 0). Jaime reports 102 passed at B and C (NOT rerun by me). I read A's diff and sampled the card texts. NOT reviewed deeply by me: B code, C code, Arturo's suitability code, Arturo's contract tests.
> B numbers (Jaime's report, CARM JSON, before→after): success actual 41.2 [28.8,54.8] → 41.2 [21.6,64.0]; s1 73.1 → 81.2 [57.0,93.4]; s2 62.0 → 53.3 [30.1,75.2]; s3 73.1 → 81.2. P50 €/ha: actual 328→1067, s1 3956→3045, s2 2025→1313, s3 3914→3004. Common years C = 14 (2006-2016, 2019, 2020, 2022; out: 2005, 2017, 2018, 2021, 2023); n_anios_historicos actual 17, s1 16, s2 15, s3 16; n_muestras 50-52; open JSON n=18, n_muestras 54 (Gonzalo). SIAM calendar 2005-2024; full years 2006-2024 = 19 (2005 has <360 days). Gonzalo's schema v1.1 admits `_status` with explanatory suffix and `mock`/`provisional` in legacy `_estado_bloques`.
>
> **Settled decisions — do not re-litigate.**
> - Delegate to Jaime's Cursor + Arturo; I orchestrate (token saving). No Grok bot: replaced by this (never explicitly confirmed; assumed).
> - CARM prices used in the CARM build even without permission; open JSON (public) has none. Lettuce: explicit generic €/kg MAPA proxy in the open build (step E), labelled proxy, not Murcia, harvest cost unverified.
> - Card texts = templates now; LLM rewriter: **gpt-oss-20b Q4_K_M via Ollama on Jaime's laptop**; check deterministic (numbers ⊆ allowed, no written-out numbers, template caveats kept, banned words, length); on failure feed the exact error back, up to 3 tries, then template; card shows LLM text if valid else template; must be declared as AI use.
> - B (14 common years): Enrique said "ignore, do nothing about it" → leave as is, declare it; do not ask again.
> - Merge plan: A+B first (J1), C and D as separate sub-jobs; E chained after C. Merging to main is Enrique's, never an agent's.
> - Per-parcel engine "A completo": hard-exclude the impossible (rainfed → no irrigated vegetables) + % penalty on the SCORE (not on margin/yield) from a sourced table (unsourced % = `supuesto`); missing data → factor 1 + "sin dato"; environmental option = a **label alto/medio/bajo** with reasons (not a toggle). Arturo: tables + pure module; Jaime: `run_parcel` + regression (Torre-Pacheco money figures unchanged).
> - No time limit today (Gonzalo's "20:00" was a joke); submission Sun 15 Nov 23:59.
> - Standing rules: ask before downloads/forms; only humans merge; never commit the untracked web-Claude PDF; no secrets on the bus; keep Enrique's email private; do not run teammates' scripts (e.g. `validate_v1_1.py`) without asking; Enrique sends the CARM email himself; use /mcq-explain + /drop-jargon for decisions.
>
> **Hard-won facts.**
> - Bus send: python urllib JSON-RPC to `http://100.93.255.39:6780/mcp`: `initialize` → `tools/call register {seat:"enrique"}` → `tools/call send_message {to,text,task}`. Scripts in scratchpad `send_bus*.py` (latest `send_bus13.py`). Keep messages SHORT (Gonzalo's #138 arrived truncated); he asked for ≤2 lines each, up to 3 in a row.
> - Secano caveat (Arturo): haba/cebada/veza lack canonical cost/yield in the engine → a rainfed parcel will be "no evaluable" (honest). Slope penalty only for 4 vegetables (×0.85 for 10-20 %, ×0.65 >20 %, supuestos C); haba pH 6.5-9 / poor drainage use a USDA source.
> - gpt-oss is a reasoning model: with Ollama use `message.content` only, `think:"low"`, temperature 0.2.
> - Last session pitfall: never chain `&&` after `pytest | tail`; read the real exit code.
> - Scratchpad: `/tmp/claude-1000/-home-enrikkk-Desktop-Computer-Science-Hackathons/b25ffb0e-70c5-40de-897b-e3b8363b4439/scratchpad/` (`esam/correo_carm.txt`, `send_bus*.py`, `resume_block2.md`).
>
> **Open items only Enrique can do/decide.** (a) answer #3 above (accept H-002 v1?); (b) merge `t020-ab` after my review; (c) send the CARM permission email (`scratchpad/esam/correo_carm.txt`, to agri-estadistica@carm.es); (d) Earthdata Login + AppEEARS + CDSE accounts for NDVI (`app/backend/ndvi/README.md`); (e) an agronomist must validate stage windows (limón, brócoli, haba, cebada) and alert thresholds before the pitch; (f) bare-soil rule 60 days vs monthly NDVI; (g) "decil inferior" wording in cards should become plain language (told Jaime in #154, J3 scope).

# 🎯 RESUME HERE (written 2026-11-14 ~16:25, before 2nd /compact) — NEWEST, overrides older blocks

**Situation.** Enrique (seat enrique, engine owner) on NASA Space Apps Murcia 2026, Agrockham. Engine T-012/T-018/T-020 done and pushed on branch `t012-motor-nucleo` @ bddecfd (NOT merged; only humans merge). 99 tests pass (engine + ndvi). Subagent work (T-022 texts, T-013 NDVI prep) is committed as WIP and has NOT been reviewed by me.
**Immediate next action (after user says "continue").** (1) Ask/handle the user's LAST request: he wants to "connect to a Grok bot that executes things so we only orchestrate and save tokens" — I asked which bot / how connected (xAI API key in a `.env` he creates, grok.com via Chrome extension, or an agent on a teammate's laptop via team-bus) / what to delegate / what data may leave (repo has CARM prices + IMIDA costs with unverified licences); he has NOT answered. Do not invent a connector (none exists in this session). Never print or paste keys. Anything Grok changes needs my review before commit. (2) Review subagent output: read `app/backend/engine/decision/texts.py` + sample `texto` of each rotation, run `python3 -m pytest -q app/backend/engine app/backend/ndvi`, regenerate JSONs (`python3 -m app.backend.engine.build torre-pacheco` and `--abierto`; the committed JSONs do NOT yet contain `texto`), commit, push. (3) Apply Gonzalo's method requests (#133) below. (4) Re-arm Monitor (`SEAT=enrique bash scripts/bus_listen.sh`, 30 min, id boz9q7w5w expires ~16:45).
**In-flight.** No background agents running (all 3 subagents finished). Working tree clean except the untracked web-Claude PDF (never commit it). JSONs in repo are from commit 3356c14 (no `texto`).
**User REJECTED my tool call** (downloading Gonzalo's `research/contract-v1-draft/v1.1/validate_v1_1.py` from origin/main into scratchpad and running it); reason unknown, he did not explain. Do NOT run teammates' scripts from main without asking first. Gonzalo says (unverified) my JSONs validate with 0 schema errors on v1.1 (2e1b93c on main).
**Gonzalo's pending requests (#133), all mine to do:** (a) add `_meta.estado_bloques` (copy of `_estado_bloques`) for list blocks (historia, rotaciones); he also says some `fuente_id` referenced are not in `fuentes[]` — my own check found none missing in torre-pacheco.json, ask which. (b) exito_pct on ~19 historical YEARS not 52 pooled plan-years: year y is bad if any plan-year option evaluated under year y has climate_bad OR the plan's mean margin<0; n = years valid for all plan-years; keep 52 as `n_muestras`; add `n_anios_historicos`, `n_efectivo`; update `definicion` (edit `simulate()` in decision/strategies.py + rotation() in build.py). (c) Scenario index i must be the SAME climate/price year and cost factor in every rotation: today only u and cost factor are shared, the year can differ when pools differ -> draw y from the COMMON years (intersection of money pools over all evaluable rotations, per variant) and confirm to him in the bus. (d) DECISIONS.md has D-010 (CARM) ACCEPTED by Enrique; Jaime/Arturo not yet confirmed.
**Settled decisions (do not re-ask).** CARM prices ARE used in the published `app/data/torre-pacheco.json` although permission is pending (Enrique chat; risk his; `torre-pacheco.abierto.json` = no-CARM twin via `--abierto`). Thermal risk = indicator PER GROWTH STAGE (`core/stage_risk.py`, ALERTS with source/conf/organ/days, frequency over 19 SIAM years, 'sin evidencia' per (stage, hazard), does NOT change success/margin). Texts = templates now, LLM later on Jaime's machine with number validator. No hard deadline ("la hora de las 20:00 era broma de Gonzalo"). Subagents (Sonnet) allowed. Sowing options only base date and +15 d (never earlier: frost unvalidated).
**Verified, do not redo.** 29 engine tests at 3356c14; 99 total at bddecfd. Validation of my JSON vs Gonzalo's DRAFT schema (d6b66cf): 90 errors -> 42/46, all remaining in his stale draft; fixed my side (semver 1.0.0, _meta.aviso, legal estado/provisional/_status 'simulado', sobreoferta 'cargando'/'gris', peores_anios objects, water p10/p50/p90 always, escenarios_margen_eur_ha alias + escenarios_meta, rotation-level anios/ciclo_dias/ciclos_por_anio, clima.serie_anual). Arturo's 5 corrections (#122) applied (6c272f2). Bus messages sent: #114, #121, #124, #129 (estimates to Arturo), #132 (to Gonzalo).
**Subagent reports (unverified by me).** Texts: `decision/texts.py` apply()/check()/numbers_in(); check raises AssertionError on any number not derivable from the rotation's JSON; words ("tres") escape the validator; open build shows S1/S3 100 % success from national Eurostat melon price (text hedges it). NDVI: `app/backend/ndvi/{bare_soil,appeears_request,appeears_csv}.py`, 50 synthetic tests; AppEEARS products are `HLSL30.020`/`HLSS30.020` (not .002), layers B04/B05(B8A)/Fmask, compute NDVI myself (the *_VI products have no quality layer); NDVI thresholds 0.20/0.35 are assumptions (0.35 has no source); monthly granularity: 2 bare months = 59-62 days vs `BARE_LIMIT_DAYS=60` in rules.py (decide >62 d or 3 months); unverified: CSV column names, token type, size/queue limits. HUMAN steps: create Earthdata Login (urs.earthdata.nasa.gov, ~5 min), accept AppEEARS terms, run task (README in app/backend/ndvi), drop CSVs in `app/data/cache/ndvi/`.
**Hard-won facts.** Commands: `python3 -m app.backend.engine.build torre-pacheco [--abierto]`; tests `python3 -m pytest -q app/backend/engine app/backend/ndvi`; bus send via python urllib (initialize -> register seat enrique -> send_message{to,text,task}) to http://100.93.255.39:6780/mcp. Open mode: lettuce has no open price (Eurostat 0.27 EUR/kg national vs Murcia iceberg ~0.43; kg_fallback flag exists, OFF) so the current rotation is "no evaluable" in money; Eurostat melon 0.42 vs Murcia 0.29 is optimistic. Gonzalo #135 / Arturo #136: MAPA open monthly national prices (research/precios-abiertos.md, bc7a021, EUR/100 kg, no variety/per-piece) do NOT solve iceberg per piece; not adopted. Results (CARM build): actual P50 +328 EUR/ha, success 41 %; S1 alcachofa->brocoli->alcachofa P50 +3956, 73 %; S2 brocoli+veza..., P50 +2025, 62 %. Variants temp +2 remove alcachofa frost episodes (3->0 of 19). Alerts to fix if Arturo sends values: `core/stage_risk.py` ALERTS + SOURCES. Rules.py is provisional until Gonzalo's `legal.py` replaces it (his `adapt_enrique.py` is in main v1.1). Gonzalo asked soil water to 1 m by layers (answered yes). Humans: send CARM email (draft scratchpad/esam/correo_carm.txt), Earthdata/CDSE accounts.
**Open questions.** Grok bot (see above). Phenology->stage windows (lemon, broccoli, haba, barley) are my assumptions: need an agronomist before the pitch. Bare-soil rule 60 vs monthly NDVI. Whether to adopt MAPA prices as an open fallback.

---

> ## 🎯 RESUME HERE (2026-11-14 ~15:45, Sat): enrique's engine (T-012 core + T-018 price/costs)
>
> **State.** Engine runs end-to-end on real data per crop TYPE, branch `t012-motor-nucleo` @ 27d51d9 (not merged; 15 tests:
> `python3 -m pytest app/backend/engine/core/tests -q`; demo table: `python3 -m app.backend.engine.core.evaluate`).
> Climate = SIAM TP91 station 2005-07..2024 (frost from station; POWER only fills gaps). Prices = CARM yearbook monthly quotes
> by variety 2002-2023 (`engine/data/official/carm_precios_mensuales.csv`, orientative), priced on each cycle's harvest months,
> tier CARM type → CARM crop → Eurostat national. Costs/kilos per type from IMIDA (net kg = coste_total/coste_unitario).
> Money in 2025 euros (HICP). Farmer can override the price in the UI (options in `precio.opciones_usuario`; per-year
> `cantidad_ha`, `coste_eur_ha`, `coste_recoleccion_eur_ha`, `clima_malo` exported for live recompute).
>
> **Next.** (1) Integrate arturo's tables `origin/arturo-inbox-followup` @ d3b1abf (frost_t0/t100, heat_t0/t100, ECREA proxies)
> — careful: when `app/data/tables/crop_params.csv` exists the engine reads only it, so it must carry the product rows too.
> (2) T-020 decision layer → `app/data/torre-pacheco.json` (contract v1). D-009 accepted: live backend later.
>
> **Decided by Enrique (don't reopen):** 2025 euros · artichoke on Murcia calendar · UI shows only FAO-calculated water ·
> no ML price/yield regressor (walk-forward backtest: loses to the median in 5/6 crops) · products per type + farmer's own price.
>
> **Money-only results (no climate thresholds yet):** limón fino 89 %, alcachofa 78 %, brócoli 62 %, melón piel de sapo 56 %,
> lechuga iceberg 39 % (0.21 €/pieza vs 0.24 cost), little gem 24 %; haba/cebada not evaluable.
> **Open:** does CARM "s/finca" include harvest? (default: farmer pays; UI toggle).
> **⚠️ Licence:** CARM yearbook prices = personal non-commercial use only, no modification (esam.carm.es/legal). Permission
> requested (Enrique emails agri-estadistica@carm.es). Engine uses them only with `--interno` / `allow_restricted=True`
> (branch @ 2f8b3b9, 16 tests); anything PUBLISHED uses open data only (Eurostat) until written permission.

# Field Shift (challenge 06): data brainstorm

Written 2026-11-14 by Claude (seat enrique). Sources:
- the official Resources tab, captured via Chrome on 2026-11-14
- live access checks against Murcia on the same day (commands at the bottom)

Read `context/challenges/06-adapting-farms-with-nasa-data.md` first.

## 1. What NASA published (Resources tab)

**Global (usable for Murcia):**

| Dataset | What the challenge says it's for |
|---|---|
| SMAP | soil moisture, freeze/thaw |
| GPM IMERG | rain, extremes, erosion |
| Landsat + MODIS/VIIRS | NDVI, bare ground, seasonal change |
| NASA POWER | temperature, radiation, frost, crop water use |
| SRTM | slope, runoff, erosion |
| ECOSTRESS | land-surface temperature and ET at about 70 m |
| GLDAS | continuous land-surface time series |
| GEDI | biomass, only weakly relevant to crops |
| FAO GAEZ | crop suitability, yield potential |
| ESA Sentinel-2 (partner) | 10–20 m |
| ECMWF ERA5 (partner) | hourly reanalysis |

GRACE/GRACE-FO is named in the challenge text but not in the Resources tab.

**US only, so not usable for Murcia:**
- USDA: Ag Data Commons, Web Soil Survey, SSURGO/STATSGO2, **Cropland Data Layer (CDL)**, AMS Market News, **NASS QuickStats**
- PRISM, NAIP, NLCD, CoCoRaHS, NWIS, **OpenET**, LANDFIRE, NLDAS

The ground truth the challenge suggests for training models (CDL rotations, NASS yields, OpenET) exists only in the US.

## 2. Access checks over Murcia (2026-11-14)

All checks used the huerta / Campo de Cartagena.

| Dataset | Resolution | Result | Verdict |
|---|---|---|---|
| NASA POWER API (AG) | ~0.5° (~50 km) | OK, no login. Monthly 2015–2024: T2M_MAX/MIN, PRECTOTCORR, FROST_DAYS, GWETROOT | climate context, ET0 input |
| POWER `EVLAND` | ~50 km | 0.2–1.8 mm/day in 2023 | **trap**: model ET of unirrigated land. It doesn't see irrigation. (`EVPTRNS` is in MJ/m²/day, not mm) |
| SoilGrids v2 (ISRIC, not NASA) | 250 m, modelled | Campo de Cartagena (−1.02, 37.78), 0–5 cm: clay 41.7 %, sand 16.6 %, pH 7.9, SOC 20 g/kg, N 1.79 g/kg. **Null over urban Murcia** | usable. SOC looks high for Murcia, so treat as modelled |
| HLS L30 + S30 (Landsat + Sentinel-2 harmonised) | 30 m | 79 + 95 = **174 granules in 2025** | **the workhorse**: per-field NDVI phenology |
| ECOSTRESS LSTE (L2T) | 70 m | 44 granules in 2025 | heat-stress snapshots |
| ECOSTRESS ET (L3T JET) | 70 m | **only 6 granules in 2025** | snapshots, not a time series |
| SMAP L3 enhanced (SPL3SMP_E) | 9 km | 364 granules in 2025 | sector-scale soil moisture |
| SMAP/Sentinel-1 (SPL2SMAP_S) | 1–3 km | 171 granules in 2025 | best SMAP resolution available |
| GPM IMERG daily final | 0.1° (~10 km) | 273 granules in 2025 (the final run lags by months) | rain and extremes. Use the Late run for recent dates |

Not checked yet:
- MODIS ET MOD16 (500 m, 8-day): possible ET time series
- GRACE (~300 km, basin scale only)
- SRTM, GAEZ, ERA5
- Earthdata login download of HLS (CMR search needs no login, download does)

## 3. Data insights (the brainstorm)

### a) Two honest scales
- **Field layer:** HLS/Sentinel-2 NDVI 30 m, ECOSTRESS 70 m, SRTM 30 m, SoilGrids 250 m.
- **Context layer:** SMAP 1–9 km, IMERG 10 km, POWER 50 km, ERA5, GRACE basin.

Never show a 9 km value as if it were "your field". The challenge explicitly asks to explain uncertainty and where
satellite data differs from ground data.

### b) Bare-field windows (literally asked)
Per-parcel HLS NDVI time series → months with NDVI below about 0.2 = bare soil. Those are the windows where a cover
crop or legume fits.

This is computable, visual and directly in the challenge text: "highlight times when fields are typically bare".

### c) Irrigation fingerprint
Model ET from POWER/GLDAS assumes no irrigation. Satellite ET (ECOSTRESS snapshots, maybe MOD16) shows the real
evapotranspiration. The gap approximates applied irrigation.

In Murcia water is *the* constraint, so this matters. **To verify**: ECOSTRESS has only 6 ET scenes a year, so check
MOD16 for a time series.

### d) Crop water demand per rotation (FAO-56)
Water demand per crop = Kc(stage) × ET0, with ET0 computed from POWER (Hargreaves or Penman-Monteith).

FAO-56 publishes Kc tables for lettuce, broccoli, melon, artichoke, faba bean, barley and so on. This is the bridge
from NASA climate data to "how much water does rotation X need", and it is defensible.

### e) The "model trained on pairs" (Enrique's idea)
Labelled pairs exist at scale only in the US: CDL gives the crop per 30 m pixel per year (2008→), NASS gives county
yields, OpenET gives field ET.

Pairs = (previous crop + this year's NASA conditions → this year's outcome), with the outcome being season-integrated
NDVI or yield. That gives millions of samples.

Options:
1. Murcia only: local hook, no labels, rules plus FAO-56 instead of ML. The 4 local teams will likely do this.
2. US only: rich labels, no local story.
3. **Train/validate on a US Mediterranean irrigated analog (California Central Valley: CDL + OpenET + SSURGO), apply
   to Murcia with explicit domain-shift caveats.** "Calibrated where ground truth exists, demonstrated at home."

### f) Spanish/EU equivalents (NOT verified, check before relying on them)
| Purpose | Candidate |
|---|---|
| Parcels | SIGPAC (MAPA) |
| Crop type | ESA WorldCereal (global 10 m), EuroCrops |
| Area and yield stats | ESYRCE (MAPA) |
| Weather ground truth to validate POWER/IMERG | SIAM-IMIDA stations (Murcia) |
| Water | Confederación Hidrográfica del Segura |
| Prices | MAPA prices |
| EU soil measurements to contrast SoilGrids | LUCAS soil |

### g) Local impact angle
In Campo de Cartagena, nitrates from intensive horticulture leaching into the Mar Menor are a major regional issue.
Cover crops in bare windows and legume rotations that reduce N fertiliser are a strong "why it matters" story.
Get facts and sources before claiming specifics.

## 4. How to reproduce the checks
- POWER: `https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=T2M_MAX,T2M_MIN,PRECTOTCORR,FROST_DAYS,GWETROOT,EVLAND&community=AG&longitude=-1.13&latitude=38.0&start=2015&end=2024&format=JSON`
- SoilGrids: `https://rest.isric.org/soilgrids/v2.0/properties/query?lon=-1.02&lat=37.78&property=clay&property=soc&depth=0-5cm&value=mean`
- CMR counts (no login): `https://cmr.earthdata.nasa.gov/search/granules.json?short_name=<SN>&bounding_box=-1.25,37.95,-1.0,38.1&temporal=2025-01-01T00:00:00Z,2025-12-31T23:59:59Z&page_size=0`
  → read the `CMR-Hits` header. SN = HLSL30, HLSS30, ECO_L2T_LSTE, ECO_L3T_JET, SPL3SMP_E, SPL2SMAP_S, GPM_3IMERGDF.
