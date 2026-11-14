# Motor de Agrockham (`app/backend/engine`)

Este README cubre las tres piezas añadidas en la rama `integracion`. Para el núcleo (submodelos A-D, precios,
productos) ver `core/README.md`. Para la tabla de idoneidad de Arturo ver `suitability/README.md`.
Cómo se enchufa todo en local: `app/INTEGRACION.md`.

## Motor por parcela (`run_parcel`)

Tarea H-002 (`coordination/handoffs/H-002-motor-por-parcela.md`). Antes, el motor calculaba solo la parcela demo.
Ahora calcula cualquier parcela:

```python
from app.backend.engine.build import run_parcel
doc = run_parcel({"lat": 37.7383, "lon": -0.98838, "area_ha": 4.0, "regadio": True, "pendiente_pct": 1.2,
                  "zona_legal": "zona_2", "cultivos_declarados": ["lechuga"]})
```

Código: `parcela.py` (capa por parcela) y `build.run_parcel` / `build.build(parcel_input=...)` en `build.py`. La tabla y el
módulo de idoneidad son de Arturo (`suitability/`).

### Entrada (`parcel_input`)

Un `dict`. Todos los campos son opcionales y pueden ser `None`: un dato que falta no se inventa, cuenta como "sin dato".

| Campo | Qué es |
|---|---|
| `parcel_id` | identificador de la parcela |
| `lat`, `lon` | posición; sirve para la distancia a la estación de referencia |
| `area_ha` | superficie en hectáreas (si falta o es 0, no hay totales) |
| `regadio` | `True`, `False` o `None`. Solo `False` excluye los cultivos del catálogo |
| `pendiente_pct` | pendiente en % |
| `zona_legal` | `zona_1`, `zona_2` u otro valor; entra en el semáforo legal |
| `suelo` | `textura`, `ph`, `materia_organica_pct`, `salinidad_ce_dsm`, `profundidad_cm`, `drenaje` |
| `cultivos_declarados` | lista de textos o de dicts con `cultivo`, `producto` o `cultivo_secundario` (declaración a FEGA) |

Si `parcel_input` no es un `dict`, lanza `TypeError`. `allow_restricted=True` usa precios CARM; el valor por defecto
es `False` (datos abiertos). `base_year` (por defecto 2025) fija el año de los euros.

### Qué cambia la parcela

- Quita del catálogo los cultivos que la parcela no puede cultivar (exclusiones de Arturo). Hoy: todos si `regadio` es `False`.
- Da a cada cultivo un factor de puntuación de 0 a 1. La rotación se puntúa con la media de los factores de sus ciclos.
  Un cultivo penalizado se recomienda menos.
- Elige la rotación de referencia (`actual`): la declarada a FEGA si algún cultivo declarado está en el catálogo y se
  puede cultivar; si no, la rotación típica de la zona, marcada como supuesto.
- Calcula la etiqueta ambiental y las frases que enseña la tarjeta.

**No cambia euros, kilos ni porcentajes de éxito** de una rotación. La idoneidad solo mueve la puntuación. Una
salvedad: los escenarios se alinean sobre los años comunes a todas las rotaciones mostradas (D-011). Si cambia la
rotación de referencia, las cifras de una rotación pueden moverse un poco.

### Qué añade a la salida

Por cada rotación de `rotaciones`:

| Campo | Contenido |
|---|---|
| `idoneidad` | `factor_puntuacion`, `factores_aplicados` (por cultivo: `variable`, `valor_entrada`, `factor`, `estado`, `conf`, `fuente_id`, `url`), `frases`, `_status: "supuesto"` |
| `ambiente` | etiqueta `nivel` (`alto`, `medio`, `bajo`), `motivos`, `estado`, `sin_dato`, `umbrales`, `metricas` (`agua_m3_ha`, `suelo_desnudo_dias`, `credito_n_kg_ha`, `color_legal`), `frase`, `nota` |
| `totales_parcela` | solo si se conoce `area_ha`: `area_ha`, `margen_eur` (`p10`, `p50`, `p90`), `agua_m3`, `unidad`, `nota` |
| `suelo_desnudo_dias` | días al año con el suelo desnudo (media del plan) |

En la raíz del documento:

| Campo | Contenido |
|---|---|
| `idoneidad` | `excluidos`, `factores_puntuacion`, `sin_dato`, `reglas_pendientes`, `referencia_origen`, `declarados`, `declarados_en_catalogo`, `declarados_fuera_de_catalogo`, `frases`, `nota` |
| `clima_origen` | `estacion` (`SIAM-TP91`), `parcela_referencia`, `distancia_a_parcela_referencia_km`, `lejos` (más de 30 km), `frase` |
| `actual_origen` | de dónde sale la rotación de referencia: `habito_parcela_demo` (sin `parcel_input`), `declaracion_fega`, `supuesto_zona` o `sin_referencia` |
| `parcela_input` | la entrada tal cual la recibió el motor |
| `no_evaluable` | solo si no hay ninguna rotación evaluable (`rotaciones: []`): `motivo` y `_status`. Pasa, por ejemplo, con una parcela de secano |
| `escenarios_meta` | `alineados`, `n`, `semilla`, `n_anios_comunes`, `nota`. `alineados` es `true` solo si lo es en todas las rotaciones con escenarios (D-011) |

`idoneidad`, `clima_origen`, `parcela_input` y `no_evaluable` solo salen cuando se pasa `parcel_input`.

En el mismo commit se hicieron dos arreglos pequeños: se arregló una f-string sin formatear en `exito_pct.definicion`, y
`escenarios_meta.alineados` ahora está en la raíz del JSON.

### Límites

- **El clima es de una sola estación** (SIAM TP91, Torre-Pacheco) para cualquier parcela. `clima_origen` lo dice y
  avisa si la parcela está a más de 30 km (`LEJOS_KM`). Esos 30 km son un supuesto sin fuente.
- **Las penalizaciones por pendiente son iguales para las cuatro hortalizas** de la tabla. La pendiente cambia la
  puntuación, pero no qué rotación gana. Lo que sí cambia hoy entre parcelas: secano (sale "no evaluable", porque el
  catálogo solo tiene cultivos de regadío con coste y rendimiento), la zona legal, el cultivo declarado a FEGA como
  referencia, la etiqueta ambiental y los totales por superficie.
- **Los porcentajes de idoneidad y los umbrales de la etiqueta ambiental son supuestos del proyecto** (confianza C),
  no mediciones.
- Rendimiento medido (portátil del desarrollador, 2026-11-14): una ejecución de `run_parcel` tarda de 0,7 a 0,8 s, usa
  unos 18 MB de memoria máxima de Python, y ocho ejecuciones a la vez en hilos dieron resultados correctos. El motor no
  hace llamadas de red. Solo carga `numpy` como paquete externo; `scipy` se importa solo para el intervalo de Jeffreys opcional.

Pruebas: `python -m pytest app/backend/engine/decision/tests/test_parcela.py -q`.

## Precio MAPA como proxy

En la construcción con datos abiertos (`allow_restricted=False`, sin precios CARM), el motor usa la media nacional anual
del MAPA ("cultivo en general") como precio de proxy. Está marcado así, con la etiqueta `MAPA_LABEL` de `build.py`:
"MAPA, media nacional anual del cultivo en general (proxy)".

- Carga: `core/data.py`, función `load_mapa_prices()`. Lee `app/data/tables/mapa_prices.csv` (instantánea de Arturo, T-021;
  ver `app/data/tables/MAPA-SNAPSHOT.md`).
- La lechuga NO se valora con él (decisión del 14-nov-2026): el MAPA mezcla tipos y queda ~35 % bajo la iceberg de Murcia. En modo abierto las rotaciones con lechuga salen «sin precio». Se controla con `kg_fallback=False` en `build.py`.
- Las fuentes MAPA salen en `fuentes[]` con su licencia, su aviso legal y la nota "proxy nacional genérico (conf. X)".
- Con `allow_restricted=True` (precios CARM) no se usa.

**Efecto que hay que decir en voz alta.** Con datos abiertos, la rotación de referencia (melón + lechuga) sale con
pérdidas: mediana (p50) de −1.041 €/ha y 33,3 % de años buenos. Con precios CARM sale +1.067 €/ha y 41,2 %. Las
alternativas salen muy bien en modo abierto (S1: 100 % de años buenos), en parte porque el precio nacional del melón es
más alto que el de Murcia. El permiso de la CARM sigue pendiente. La API solo usa precios CARM con `ENGINE_PRECIOS=carm`
explícito.

## Reescritor LLM

Archivos: `decision/llm_rewrite.py`, `decision/prompts/rewrite_system_es.md`, `decision/tests/test_llm_rewrite.py`.

Un modelo de lenguaje **local** reescribe un texto que el motor ya calculó. **No calcula nada.** No hay proveedor
externo, ni clave, ni coste.

### Uso desde la línea de órdenes

```bash
python3 -m app.backend.engine.decision.llm_rewrite app/data/torre-pacheco.abierto.json [--dry-run] [--campos por_que,riesgos_texto]
```

- Escribe `<fichero>.llm.json` junto al original y muestra ANTES y DESPUÉS de cada texto.
- `--dry-run` usa un modelo falso que devuelve la plantilla: sin red y sin modelo.
- `--campos`: lista separada por comas. Valores válidos: `por_que`, `evidencia_resumen`, `no_sabemos`, `riesgos_texto`,
  `consulta`. Por defecto, `por_que`.
- Sin `--dry-run` usa Ollama (`OLLAMA_URL`, por defecto `http://127.0.0.1:11434`; `OLLAMA_MODEL`, por defecto
  `gpt-oss:20b`; `OLLAMA_TIMEOUT_S`, `OLLAMA_THINK`). No descarga nada: si el modelo no está instalado, se para y lo dice.
- Cada intento queda en `app/data/cache/llm_log/<fecha>.jsonl` (carpeta ignorada por git).

### Cómo funciona

1. Se envía al modelo el prompt de sistema, la plantilla y la lista cerrada de cifras permitidas.
2. Un **comprobador determinista** (`check`) revisa la respuesta. La rechaza si:
   - lleva una cifra que no está en la plantilla, o le falta alguna;
   - escribe una cantidad con letras o palabras («tres», «la mitad»...);
   - usa una expresión prohibida («garantizado», «seguro que», «sin riesgo», «asegura», «sin duda», «te hará ganar», «cumple la ley»);
   - pierde una salvedad de la plantilla («provisional», «supuesto», «proxy», «orientativ...», «no sabemos», «por verificar»...);
   - es más larga que la plantilla;
   - lleva listas, títulos o formato;
   - lleva palabras vacías como `None`, `null` o `nan`.
3. Si falla, se le dice al modelo exactamente qué falló y reescribe. Hasta **3 intentos** (`MAX_TRIES`).
4. Tras el tercer fallo se queda la **plantilla** determinista (`valido: false`). La tarjeta solo muestra el texto del
   modelo si `valido` es `true`.

### Forma de la salida

Por texto (`rewrite_text`): `{texto, modelo, intentos, valido, errores}`. `texto` es el del modelo si es válido; si no, la plantilla.

En el JSON del motor (`apply`): cada rotación recibe `texto_llm: {<campo>: {...}}`, y `_meta.uso_ia` queda con `modelo`,
`runtime`, `cuantizacion`, `fecha`, `finalidad` y `verificacion`. El campo `texto` (la plantilla) nunca se modifica.

### Estado de las pruebas

- Los tests (`test_llm_rewrite.py`) usan un modelo falso: sin red, sin modelo.
- Ejecución real con el modelo pequeño `granite3.3:2b` en el portátil del desarrollador: el comprobador rechazó 4 de 4
  textos y se usó la plantilla en los 4. Tardó 7 minutos.
- **El modelo previsto, gpt-oss-20b Q4_K_M con Ollama en el portátil de Jaime, todavía no se ha probado.**
- Licencia del modelo: por confirmar antes de entregar.
