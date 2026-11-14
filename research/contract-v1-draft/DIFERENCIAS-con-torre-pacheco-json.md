# Diferencias entre el contrato borrador (gonzalo) y `torre-pacheco.json` (enrique, rama t012-motor-nucleo @ 676980d)

Para kike (enrique) · de gonzalo · sáb 14-nov-2026 · objetivo: poder congelar el contrato esta noche (20:00).
Comparación hecha en solo lectura: el JSON de la rama validado contra `contract.schema.json` (88 errores, casi todos
estructurales, ninguno de contenido). El schema es un borrador mío: **donde sea lo mismo, cedo yo**.

## 1. Lo que cambiaría yo (mi schema se adapta a tu JSON)

| Tema | Mi borrador | Tu JSON | Decisión propuesta |
|---|---|---|---|
| Vocabulario de `resultado` en comprobaciones legales | `cumple\|no_cumple\|aviso\|indeterminado` | `ok`, … | Adopto `ok\|falla\|no_aplica\|no_evaluable` (también lo usa mi `legal.py`) |
| Nº e ids de rotaciones | 3 (`actual`, `alt-a`, `alt-b`) | 4 (`actual`, `s1`, `s2`, `s3`) | Acepto las tuyas: mínimo 3, ids libres |
| `historia` | objeto `{_status, cultivos_declarados[]}` | lista `[{anio, cultivo, fuente}]` | Adopto tu lista; la 0..N de SIGPAC irá en un campo opcional `declaraciones` |
| `agua_detalle` | números sueltos | `{bruto_m3_ha:{p10,p50,p90}, coste_eur_ha:null,...}` | Adopto tu forma (percentiles) y permito `null` |
| `margen_eur_ha.unidad` | sin definir | "€ de 2025 por hectárea y año (media del plan)" | Adopto tu unidad y el campo `unidad` |
| Campos extra tuyos (`criterios_sentido`, `supuestos_decision`, `licencia`, `generado`, `horizonte_anios`, `plan_anios`, `estrategias`, `exito_pct.definicion`) | no existían | existen | Se documentan; el schema ya admite campos extra |
| `null` en rotación no evaluable | no permitido | `exito_pct`/`criterios`/`margen` = `null` | Lo permito siempre que `definicion`/`huecos` expliquen por qué |

## 2. Lo que te pido a ti (pequeño, para que la UI y la API puedan leerlo)

1. **`schema_version` y `_meta`** en la raíz (versión, fecha, `generado`, semilla) y **`fuentes[]`** con
   `{id, nombre, url, licencia}` por cada dataset usado (lo necesita `submission/` para citar y la tarjeta para el
   "de dónde sale esto").
2. **`_status` dentro de cada bloque** (`real|precalculado|simulado|cargando`), además de tu `_estado_bloques` si quieres
   conservarlo. Motivo: con D-009 la API entrega los bloques por separado (`POST /analyze?bloques=...`) y cada uno debe
   llevar su estado. Mapeo: `mock` -> `simulado`; `provisional` -> `simulado` con `provisional: true`.
3. **Muestras de escenarios también en `actual`.** Ahora `actual.escenarios = null`, pero "B gana en X %" necesita la
   rotación actual como línea base con el mismo índice (misma muestra = mismo año de clima/precio/parámetros en todas
   las rotaciones).
4. **Para el semáforo legal** (mi `legal.py`, `research/prototypes/legal_rules/`): por rotación `ciclos_por_anio` y por
   ciclo `ciclo_dias` (y siembra/cosecha si las tienes); `meses_desnudo` ya sale de `ndvi`. Con eso llamo a
   `legal.check(rotacion, parcela, zona)` desde la API y sustituyo tu semáforo `provisional`.
5. **Bloques reales de entrada.** Tu `_estado_bloques` marca `parcela`, `historia`, `ndvi`, `suelo` como `mock`. Yo
   produzco `parcela` real (ATOM/SIGPAC), `clima` y `suelo` reales (POWER/IMERG/ERA5/SoilGrids) en
   `research/prototypes/pipeline_clima_suelo/` y `atom_pipeline/`. Propongo que tu motor lea esos bloques de
   `app/data/cache/pipeline/<parcela>.json` en vez de los del mock. Dime qué campos de `clima` necesitas (serie anual
   por año: lluvia, Tmax, Tmin; ET0 mensual; días >38 °C).
6. **`parcela.zonas`**: ahora afirma `mar_menor_zona_2`. Hasta que yo verifique el Anexo I debe ser
   `mar_menor_zona_por_verificar` (muy probable Zona 2 según el WMS de la CARM, sin confirmar).

## 3. Dudas sobre el contenido (tuyo, solo para que lo veas)

- **`actual` no es evaluable con datos abiertos** (`exito_pct = null`, `margen = null`: "falta el precio de algún
  cultivo con datos abiertos"). La rotación actual es la línea base de todo el comparador y de "B gana X %". Hace falta una
  fuente abierta de precio para lechuga y melón (o decidir cómo se muestra sin ella). Es el hueco más importante que veo.
- **`exito_pct.n = 54`** en `s1` (D-008 habla de n = 20 años). ¿Qué cuenta n (año x cultivo)? El intervalo de Wilson
  supone observaciones independientes; conviene decirlo en `definicion`.
- **Calor y heladas con POWER:** MERRA-2 (~50 km) da 0 días >38 °C y Tmin mínima +1,4 °C en la parcela demo; los extremos
  salen de SIAM (tu colector). Detalle en el README de `pipeline_clima_suelo/`.
- **Suelo:** SoilGrids da MO 2,14 % (0-30 cm) frente al 1,1 % del mock, y agua disponible solo 0-30 cm (~45 mm). ¿La
  quieres a 1 m?
- **Licencia CARM:** vi `licencia.solo_uso_interno = false` y tu nota de 0 menciones en el JSON publicable; lo anoto en
  `submission/data-citations.md` como "PENDING PERMISSION" para el resto.

## 4. Siguiente paso propuesto (para esta noche)

1. Tú: contestas lo de la sección 2 (puntos 1-4 y 6) y la duda de `actual`.
2. Yo: publico `contract.schema.json` v1.1 con la sección 1 y un adaptador `adapt_enrique.py` que convierte tu JSON al
   contrato (para que Jaime pueda leer ya tu salida sin esperar), y la API `POST /analyze` que sirve tu JSON + mis
   bloques reales.
3. Jaime: lee el contrato v1.1 y congelamos.
