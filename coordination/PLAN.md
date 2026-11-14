# Plan de desarrollo de Agrockham

v1 · sáb 14-nov-2026 13:15 · escrito por el agente de jaime a partir de todo el repo (pizarra, `field-shift-plan.md`,
`research/predictive-model-research.md`, `app/README.md`, tareas T-009..T-017, mesh D-004).
**Lo que ata al equipo va a `DECISIONS.md`** (D-006 nombre, D-007 PROPOSED arquitectura). Este fichero se puede
editar; cada cambio de fondo, una línea en `LOG.md`.

> **Agrockham** = Agro + la navaja de Ockham. Para el agricultor sin perfil técnico: *"Los datos de tu campo están
> dispersos. Los ordenamos y te decimos qué rotación te deja más dinero, con qué probabilidad y sin saltarte la ley."*
> Regla de producto y de ingeniería: **la solución más simple que funcione**. El motor calcula, la IA solo explica.

---

## 1. Qué entregamos (y qué no)

Reto 06 Field Shift. Los jueces puntúan: datos NASA + suelo + cultivo + **prioridades del agricultor**, **≥ 3 rotaciones
incluida la actual** con *por qué / evidencia / beneficios / huecos / riesgos*, **cuándo está el campo desnudo** y
cuándo es vulnerable, y que **no sustituye** al técnico.

Demo: **una parcela real de punta a punta**, Torre-Pacheco SIGPAC 18/426/1 (4,1 ha, regadío, zona vulnerable a
nitratos, 2025 melón → barbecho). El resto, simulado o hoja de ruta **y etiquetado** (tabla de `app/README.md`, D-005).

| Prioridad | Qué | Si falta el domingo 12:00 |
|---|---|---|
| **P0 (sin esto no hay demo)** | Mapa → ficha de parcela · línea temporal con meses desnudos · comparador de 3 rotaciones (actual + 2) con % éxito con horquilla, €/ha P10–P90, m³/ha, semáforo legal con artículo, "por qué · evidencia · lo que no sabemos · consulta a tu técnico" · clima real POWER/IMERG · todo cacheado · página de envío con datasets citados y uso de IA | no se envía |
| **P1 (lo que nos diferencia)** | Sliders de prioridades que reordenan en vivo · "la rotación B gana en el X % de escenarios" · NDVI real HLS/Sentinel-2 · heladas con SIAM TP91 · sobreoferta como riesgo · deploy estático + offline | se enseña con datos precalculados etiquetados |
| **P2 (si sobra tiempo)** | Slider "¿y si…?" lluvia/temperatura · botón clima 2050 · nodo ESP32 en vivo · narrador LLM con validador de cifras · 5–8 parcelas más · consulta inversa | diapositiva de hoja de ruta |

**Orden de recorte** si vamos tarde (primero lo de arriba): LLM narrador → 2050 → nodo ESP32 en vivo (queda la
reproducción SIAM) → parcelas extra → Monte Carlo (queda P10/P50/P90) → NDVI real (queda muestra precalculada etiquetada).

## 2. Arquitectura (navaja de Ockham)

```
 [T-011 pipeline Python]        [T-014 SIAM]        [T-013 NDVI]        [T-021 tablas a mano]
 SIGPAC·FEGA·HRL·POWER·IMERG    TP91 horario        HLS/S2 → SG →       crops.csv · precios ·
 SoilGrids·Open-Meteo ET0       → SQLite → JSON     meses desnudos      costes · reglas Ley 3/2020
        │ app/data/cache/*.json        │                   │                   │ app/data/*.csv
        └──────────────┬───────────────┴───────────────────┴───────────────────┘
                       ▼
        [T-012 + T-018 + T-019 + T-020 motor Python, offline]
        submodelos A–G por cultivo × fecha → escenarios por año (20) → DP de rotaciones (≥3) →
        valores por criterio + muestras de escenarios + paquete de evidencias
                       ▼
        app/data/torre-pacheco.json   ← EL CONTRATO (T-009). Un JSON por parcela.
                       ▼
        [T-010 React + Vite + MapLibre, estático]  ← pondera en el navegador (suma ponderada +
        "B gana X %" sobre las muestras), así los sliders van al instante y sin servidor
                       ▼
        [T-017] build estático (GitHub Pages/Netlify) + el mismo build en local sin red
```

Por qué así (D-007 PROPOSED):
- **Sin servidor en la demo.** Todo se precalcula offline; el navegador solo lee JSON y hace sumas. Nada depende
  del Wi-Fi del local. Si hay tiempo, FastAPI es una ampliación, no un requisito.
- **El motor exporta valores por criterio (margen, agua, suelo/N, riesgo) y ~200 muestras de escenario por
  rotación**; la UI aplica los pesos. Cambiar un slider no necesita recalcular nada en Python.
- **Escenarios ya calculados para los sliders P2** (lluvia −30/−15/0/+10 %, temperatura +0/+1/+2 °C, 2050): el motor
  los exporta como variantes del bloque `rotaciones`; la UI elige una.
- **El LLM, si entra, corre en el build** sobre el paquete de evidencias, con validador de cifras. Por defecto,
  plantillas de texto. Si se quita, nada se rompe.

### Contrato v1 (T-009, se congela hoy a las 14:30)
Base: `app/data/torre-pacheco.mock.json`. Se añade lo que pide la investigación (compatible hacia atrás):
`exito_pct{valor, horquilla, k_malos, n, metodo, peores_anios[]}` · `margen_eur_ha{valor, horquilla, p10, p50, p90,
breakeven_precio_eur_kg}` · `agua_detalle{etc_mm, bruto_m3_ha, coste_eur_ha, perdida_sal_pct}` ·
`criterios{margen, agua, suelo_n, riesgo}` normalizados 0–1 · `escenarios[]` (muestras de margen por rotación) ·
`semaforo_legal{color, motivo, articulo, comprobaciones[]}` · `sobreoferta_detalle{efecto_precio_pct, semaforo}` ·
`inversion{pico_caja_negativa_eur_ha, meses_hasta_primer_ingreso}` · `variantes{lluvia_-30, temp_+2, 2050…}` ·
`_status` por bloque: `real | precalculado | simulado` (la UI pinta la etiqueta).
**Regla:** después de las 14:30 solo se **añaden** campos. Cambiar o quitar uno = `send_message all` + acuerdo de
quien lo produce y quien lo lee.

## 3. Reparto (seats confirmados por jaime, 13:10)

| Seat | Rol | Tareas | Carpetas que posee (`.claude/ownership.json`) |
|---|---|---|---|
| **jaime** | Interfaz + pitch | T-010 (→ 10a/b/c/d), T-016, co-T-015 | `app/frontend/`, `submission/pitch.md`, `submission/slides/` |
| **gonzalo** | Backend | **T-009 contrato** (lo empezó), T-011, T-019 semáforo legal, co-T-015 | `app/data/` (contrato), `app/backend/pipeline/`, `app/backend/rules/`, `app/data/cache/pipeline/` |
| **enrique** | ML / motor | T-012 núcleo, T-018 precio·costes, T-020 decisión, T-013 NDVI, T-022 textos | `app/backend/engine/`, `app/backend/ndvi/`, `app/data/cache/ndvi/` |
| **arturo** | Redes / IoT | T-014 SIAM + ESP32, T-021 tablas (con ayuda humana), T-017 deploy/offline | `app/iot/`, `app/data/tables/`, `app/data/cache/siam/`, `scripts/deploy*` |

`submission/` (salvo pitch y slides) es compartido: T-015 lo llevan jaime y gonzalo.

### Tareas (las nuevas están en `coordination/tasks/`)

| ID | Qué | Seat | Depende | Modelo del agente | Horas |
|---|---|---|---|---|---|
| T-009 | Contrato v1 + mock ampliado | gonzalo | – | fuerte (diseño) | 1 |
| T-010 | UI: 4 pantallas sobre el mock (ver 10a–d en la tarea) | jaime | T-009 | fuerte para 10c, rápido para el resto | 8 |
| T-011 | Tubería real: `parcela`, `historia`, `clima`, `suelo` cacheados | gonzalo | T-009 | rápido (Haiku/Codex) | 5 |
| T-012 | Motor núcleo: aptitud (A), riesgo clima → % éxito Wilson (B), agua FAO-56 + sal FAO-29 (C), rendimiento ref. (D) | enrique | T-009, T-021 | fuerte | 5 |
| T-013 | NDVI HLS/S2 → meses desnudos y ventanas vulnerables | enrique | descarga lanzada YA | fuerte | 4 |
| T-014 | Colector SIAM TP91 → SQLite → `sensores` + serie de heladas para T-012; nodo ESP32 por MQTT (P2) | arturo | – | rápido | 4 |
| T-015 | Textos de envío, uso de IA, datasets citados | jaime + gonzalo | todo | rápido | 3 |
| T-016 | Pitch 3 min, slides, vídeo y vídeo de respaldo | jaime | T-010 | – (humano) | 4 |
| T-017 | Deploy estático + modo offline + licencia | arturo | T-010 | rápido | 2 |
| **T-018** | Motor: precio P10/P50/P90 (Eurostat), sobreoferta como desplazamiento incierto, costes y caja negativa (E, F) | enrique | T-021 | fuerte | 3 |
| **T-019** | Semáforo legal: tabla de reglas Ley 3/2020 + PAC con artículo, `allowed(prev, cur)` | gonzalo | T-009 | fuerte | 3 |
| **T-020** | Capa de decisión: DP de rotaciones (actual + ≥2), criterios normalizados, muestras de escenarios, variantes de sliders → escribe `torre-pacheco.json` | enrique | T-012, T-018, T-019 | fuerte | 4 |
| **T-021** | Tablas: `crops.csv` (8 cultivos), precios Eurostat, costes IMIDA/MAPA (transcripción humana ~2 h) | arturo | – | rápido + humano | 3 |
| **T-022** | Textos de tarjeta: plantillas desde el paquete de evidencias; LLM + validador solo si sobra tiempo (P2) | enrique | T-020 | rápido | 2 |
| **T-023** | (P2) 5–8 parcelas FEGA más con la misma tubería | gonzalo | T-011 | rápido | 2 |

Cultivos de la demo (8): lechuga, brócoli, melón, alcachofa, haba (leguminosa), cebada, cubierta (veza), limón
(perenne, solo horizonte 10 años). Rotaciones mínimas: **S0 actual** (melón → barbecho → lechuga), **S1 máximo
margen con reglas**, **S2 suelo/agua** (leguminosa o cubierta en cada ventana desnuda). S3 riesgo bajo, opcional.

## 4. Calendario (desde ahora, sáb 13:15)

| Cuándo | Hito | Qué tiene que estar |
|---|---|---|
| **Sáb 13:15–13:45** | Arranque | Plan aceptado, `ownership.json` cargado, `export SEAT` en cada portátil. **Humanos: lanzar YA las descargas lentas** (AppEEARS HLS-VI para la parcela; Sentinel-2 en CDSE; HRL Croplands). Cada uno, su listener `bus_listen.sh` |
| **14:30** | Contrato v1 congelado | T-009 en `main`. Todos programan contra él |
| **14:30–19:00** | Fase 1 en paralelo | UI 4 pantallas con el mock · tubería real de `parcela`/`clima`/`suelo` · motor A–D con el clima cacheado · `crops.csv` · colector SIAM · primera serie NDVI |
| **16:30** | Merge 1 | Cada rama a `main` (pull --rebase + que arranque) |
| **19:00** | **Hito 1: recorrido feo de punta a punta** | La UI enseña `torre-pacheco.json` generado por el motor con clima y suelo reales y 3 rotaciones. Sin pulir |
| **19:00–01:00** | Fase 2 | Precio y sobreoferta, semáforo con artículos, DP + escenarios, sliders en vivo, meses desnudos reales, heladas SIAM |
| **23:00** | Merge 2 | Igual que el merge 1. Dormir por turnos: al menos 5 h cada uno |
| **Dom 09:00** | Hito 2: todo real o etiquetado | Integración, test en un portátil **sin red** |
| **Dom 12:00** | **Congelar funciones** | Solo arreglos y pulido a partir de aquí |
| **Dom 12:00–14:00** | Vídeo de respaldo grabado | Si la demo en vivo falla, va el vídeo |
| **Dom 14:00–19:00** | Envío | Slides, página del proyecto, uso de IA, datasets (nombre + URL + licencia), deploy final |
| **Dom 21:00** | **Enviado** | Margen de 3 h sobre el cierre de las 23:59. Preguntar a la organización la hora del jurado local |

## 5. Cómo usamos el mesh (Paseo + Tailscale + team-bus)

- **Un solo planificador:** el orquestador del hub (portátil de jaime). jaime le pasa este plan como objetivo; él
  despacha (`dispatch seat T-NNN`), sigue los `report` y avisa a cada humano cuando una rama está en `review`.
  Nadie despacha a otro portátil por su cuenta: se pide con `request_handoff`.
- **Por portátil, máximo 2 agentes vivos:** la sesión interactiva del humano + 1 despachado. Si hacen falta más
  manos dentro de una tarea, subagentes locales, no más despachos.
- **Modelo según la tarea** (columna "Modelo" arriba): Haiku/Codex para fetchers, componentes y scripts; modelo
  fuerte solo para contrato, motor de decisión y la pantalla del comparador. Respuesta final de una línea `RESULT:`.
- **Cada humano mantiene su listener** (`bash scripts/bus_listen.sh`, Monitor de 30 min) en su sesión interactiva.
- **Los cambios del contrato se anuncian por el bus a `all`** y se reflejan en `app/data/` en el mismo commit.
- **Git es la verdad:** rama por tarea (`t012-motor-nucleo`), commits `T-NNN: …`, push cada hora, merge a `main` en
  los merges 1 y 2 y al cerrar una tarea. Solo humanos mergean a `main`. Si el hub cae, seguimos con git solo
  (`scripts/agent_watcher.py` como respaldo, D-003).

## 6. Lo que solo pueden hacer los humanos

| Quién | Qué | Cuándo |
|---|---|---|
| enrique | Pedir AppEEARS HLS-VI (y MODIS NDVI de respaldo) para la parcela; cuenta CDSE para Sentinel-2 | **ahora** |
| arturo | Transcribir costes €/ha de IMIDA/MAPA (brócoli, lechuga, melón, alcachofa) a `app/data/tables/` desde el navegador; traer ESP32 + sonda capacitiva | sáb tarde |
| gonzalo | Verificar en el BOE los artículos de la Ley 3/2020 (39, 40, 29, 51) y si la parcela es Zona 1 o 2 (Anexo I) | sáb tarde |
| jaime | Guion y slides; preguntar a la organización hora y formato del jurado local; leer la Project Submission Guide | sáb tarde |
| todos | T-002: cuenta Space Apps unida al equipo + Earthdata Login; fila propia en `context/team.md` | hoy |
| todos | Revisar licencia de toda dependencia/dato/imagen y apuntarla en `submission/data-citations.md` (AGENTS.md §6) | siempre |

## 7. Riesgos y qué hacemos

| Riesgo | Plan |
|---|---|
| Las descargas NDVI tardan o fallan | Lanzarlas ya; respaldo MODIS 250 m o muestra precalculada etiquetada "precalculado" |
| Tmin de POWER no ve heladas en la parcela | SIAM TP91 (1,1 km) como fuente de frío; la tarjeta dice "estación X, no tu campo exacto" |
| No sabemos si la parcela es Zona 1 | Las reglas de Zona 1 salen en ámbar "por verificar" hasta que gonzalo lo confirme en el BOE |
| Costes de hortalizas sin fuente verificada | Banda ±15 % y etiqueta "precios 2018-19 actualizados"; solo limón tiene coste verificado |
| "% de éxito" suena a predicción | Siempre con horquilla Wilson y la frase "no predice tu cosecha: cuenta los años en que el clima no habría hecho daño" |
| Wi-Fi del local | Todo cacheado; el build corre en local sin red; vídeo de respaldo |
| 4 agentes pisándose | `ownership.json` + `paths` en cada tarea + el orquestador como único planificador |
| Querer hacerlo todo | Lista de recorte de la sección 1. A las 19:00 sin recorrido de punta a punta, cortamos P2 entero |

## 8. Pitch en una línea por bloque (para T-016)

Gancho (parcela desnuda de Torre-Pacheco vista desde el espacio) → datos dispersos → Agrockham los ordena →
3 rotaciones con semáforo y horquilla → "B gana en el X % de los escenarios" → lo que no sabemos y "consulta a tu
técnico" → cierre con la navaja de Ockham. Sin logos de NASA, subtítulos en inglés, uso de IA declarado.
