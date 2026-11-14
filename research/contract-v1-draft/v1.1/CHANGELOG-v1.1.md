# Contrato v1.1-draft: cambios respecto al borrador v1 (gonzalo, sáb 14-nov-2026)

Preparación, sin tocar `app/` ni `coordination/`. Base: `DIFERENCIAS-con-torre-pacheco-json.md` sección 1 ("donde sea lo mismo, cedo yo")
y el JSON real de enrique (`origin/t012-motor-nucleo` @ f3be98b, `app/data/torre-pacheco.json`, `generado: 2026-11-14`).

| Fichero | Qué es |
|---|---|
| `contract.schema.v1.1.json` | Schema 2020-12, `schema_version: "1.1.0-draft"`. P0 obligatorio, `additionalProperties` abierto |
| `adapt_enrique.py` | JSON de enrique -> contrato v1.1 (solo stdlib; no inventa datos). `--formato draft-v1` adapta mínimamente el borrador v1 antiguo |
| `validate_v1_1.py` | Schema + invariantes (FALLO / AVISO) + `--selftest` (15 mutaciones) + `--strict-licencia` |

```bash
cd research/contract-v1-draft/v1.1
git show origin/t012-motor-nucleo:app/data/torre-pacheco.json > /tmp/enrique.json
python3 adapt_enrique.py /tmp/enrique.json -o /tmp/tp.v1.1.json --origen "enrique @ t012-motor-nucleo <sha>"
/ruta/venv/bin/python validate_v1_1.py /tmp/tp.v1.1.json --selftest      # venv con jsonschema
```

## Qué cambia respecto al borrador v1 (y por qué)
| Tema | v1 (borrador) | v1.1 | Por qué |
|---|---|---|---|
| `comprobaciones[].resultado` | cumple / no_cumple / aviso / indeterminado | **ok / falla / no_aplica / no_evaluable** | Vocabulario de enrique y de `legal.py`. `estado` y `detalle` opcionales; `resultado_original` lo pone el adaptador |
| Rotaciones | 3 fijas (`actual`, `alt-a`, `alt-b`), alt-b = cebada/veza/cebada | **mínimo 3, ids libres**, una sola `es_actual`; se quita la regla "alt-b == cebada, veza, cebada" | enrique entrega 4 (`actual`, `s1`, `s2`, `s3`). Se mantiene "ninguna rotación con alcaparra" (D-008) |
| `historia` | objeto `{_status, cultivos_declarados[]}` | **lista** `[{anio, cultivo, fuente, declaraciones?[]}]` | Forma de enrique. `declaraciones` = 0..N declaraciones SIGPAC/FEGA del año (campaña explícita). `cultivo` puede ser null. Su estado va en `_meta.estado_bloques.historia` (una lista no lleva `_status`) |
| Muestras | `escenarios_margen_eur_ha` | **`escenarios`** | Nombre de enrique (cedo yo). Mismo contenido |
| `agua_detalle` | números sueltos | `bruto_m3_ha` = `{p10,p50,p90}`; todo admite `null` (`coste_eur_ha`, `perdida_sal_pct`...) | Forma de enrique |
| `margen_eur_ha` | sin unidad | **`unidad` obligatoria**; `media` y `cvar80` admitidos; `valor` puede ser `p50` (enrique) | Una cifra sin unidad no se puede mostrar |
| `exito_pct` | `valor/horquilla` obligatorios | admite `null` (incl. `k_malos`, `n` = 0/null, `metodo`), `definicion`, `peores_anios` como enteros u objetos | Rotaciones no evaluables |
| `null` | no permitido | `exito_pct`, `margen_eur_ha`, `criterios` o sus valores `null` **solo si** `huecos[]` no vacío o `exito_pct.definicion` lo explican (lo exige el schema) | Pedido en DIFERENCIAS 1 |
| Obligatorios de rotación | exito, margen, agua, semáforo, por_que, evidencia, huecos, **riesgos** | igual pero **`riesgos` pasa a opcional** | Solo P0 reales |
| `fuentes[].id` / `url` | id en minúsculas, url obligatoria | ids con mayúsculas (`SIAM-TP91`), `url` opcional | ids de enrique; fuentes deducidas sin url |
| `semaforo_legal` | `_status` enum | además `provisional: boolean` | `provisional` de enrique -> `simulado` + `provisional: true` |
| Campos de enrique documentados | no existían | `_estado_bloques`, `licencia`, `criterios_sentido`, `supuestos_decision`, `generado`, `rotaciones[].{estrategias, horizonte_anios, plan_anios, variantes}`, `evidencia[].{escala, confianza, aviso}`, `comprobaciones[].detalle` | Se admiten y se describen; el resto sigue abierto |
| Versión | `1.0.0-draft` | `1.1.0-draft` (patrón `^1\.x\.y(-draft)?$`) | |

Mapeos del adaptador (todos quedan en `_meta.adaptaciones`; lo que falta, en `_meta.avisos`): `_status` en prosa de enrique -> palabra de estado + `nota`;
`mock -> simulado`, `provisional -> simulado + provisional:true`, `real -> real`; `por_verificar`/`no_evaluado` -> `no_evaluable`; **`aviso -> no_evaluable`**
(regla 51.6 solo de Zona 1 con zona sin confirmar, igual que `legal.py`; el "77 días > 60" sigue en `detalle`); color y artículo del semáforo intactos;
`parcela.zonas` `mar_menor_zona_2 -> mar_menor_zona_por_verificar`; `fuentes[]` deducido de `evidencia[]` y `clima.lluvia_anual_mm.fuentes`
(`"SIAM TP91" -> SIAM-TP91`) con `licencia_estado: verify` (CARM-ANUARIO lleva el texto de licencia que ya trae enrique); `escenarios_meta {n, unidad}` deducido;
`sobreoferta_detalle` todo-null y `_status: pendiente` se omite. Rotación sin `escenarios`: queda sin la clave y con aviso, nunca se inventan muestras.

## Validación (venv-contract, jsonschema 4.26)
- (a) JSON de enrique adaptado: schema OK, 0 invariantes fallidas, 2 avisos (abajo); 15/15 mutaciones detectadas.
- (b) borrador v1 antiguo adaptado mínimamente: schema OK, 0 fallidas, 1 aviso (política de licencia: la `url` de la fuente `siam` del borrador es `datosabiertos.carm.es`); 15/15 detectadas.
- Versión anterior del JSON de enrique (copia con `actual` no evaluable, `escenarios: null`): schema OK, 0 fallidas, aviso de falta de `escenarios` en `actual`.

## Comprobación de política de licencia: ¿menciona el JSON de enrique "CARM" o "esam"?
**Sí: 33 apariciones (texto o clave) en 10 rutas. El JSON publicable debe tener 0.** Rutas: `_status` (1), `licencia.incluye_precios_carm` (clave),
`licencia.estado`, `licencia.fuentes_restringidas` (clave y valor), y por rotación (x4) `evidencia[].fuente_id` = `CARM-ANUARIO`, `evidencia[].url` (`esam.carm.es/...`),
`evidencia[].aviso`, y 8 textos en `huecos[]` y 8 en `riesgos[]`. El adaptador **no las borra** (no altera datos); `validate_v1_1.py` las lista como AVISO
(`--strict-licencia` las vuelve FALLO). Tras el adaptador son 37 (añade en `fuentes[]` el id, la url, la licencia y la nota de CARM-ANUARIO). Decidir con enrique cómo se
publica el dato de precios sin el nombre (o conseguir el permiso) antes de congelar.

## Depende de enrique (DIFERENCIAS secciones 2 y 3), estado con el JSON actual
**Sección 2**
1. `schema_version`, `_meta`, `fuentes[]`: **siguen sin existir**; el adaptador los pone. Si enrique no los emite, el contrato real lo produce la API (mi `POST /analyze`) o el adaptador.
2. `_status` por bloque: no existe; lo derivo de `_estado_bloques`. Falta confirmar el mapeo (en especial `provisional -> simulado + provisional:true`).
3. Muestras en `actual`: **resuelto** en el JSON actual (200 muestras en las 4 rotaciones). Falta confirmar que el índice i es el mismo año/precio/coste en todas las rotaciones (no se puede comprobar con los datos; `escenarios_meta.alineado` no existe).
4. `ciclos_por_anio` y `ciclo_dias`: **siguen ausentes** (el semáforo de enrique sigue siendo el suyo, `provisional`; yo lo sustituiré con `legal.check` cuando los emita).
5. Bloques de entrada reales: `parcela`, `historia`, `ndvi`, `suelo` siguen `mock`; ¿lee `app/data/cache/pipeline/<parcela>.json`? Qué campos de `clima` necesita.
6. `parcela.zonas`: sigue afirmando `mar_menor_zona_2` (el adaptador lo cambia).

**Sección 3 y hallazgos nuevos al revisar el JSON actual**
- `actual` ya es evaluable (éxito 41,2 %, margen p50 328) con precios de CARM-ANUARIO: el hueco que señalé queda cubierto, pero con una fuente de licencia pendiente (ver arriba).
- `exito_pct.n` = 51/52/50/52 (no 20, D-008): ¿qué cuenta n? `definicion` ya avisa de que el intervalo es optimista por reutilizar años.
- `margen_eur_ha.valor` es el **p50**, y `media` **no coincide con la media de `escenarios`** (actual 1263 vs 997; s1 4123 vs 4185; s2 2107 vs 2066; s3 4083 vs 4145). ¿Qué promedia `media`? (AVISO del validador; p10/p50/p90 sí cuadran con las muestras ±1.)
- `aviso` en comprobaciones legales: confirmar que significa "regla de Zona 1 con zona sin confirmar" (mi mapeo a `no_evaluable`).
- `variantes`: enrique las entrega **dentro de cada rotación** (`rotaciones[].variantes{id:{exito_pct, margen_p50, agua_m3_ha, criterios, escenarios}}`), yo las tenía a nivel superior. Decidir cuál es el contrato (v1.1 admite ambas; hoy el adaptador mantiene la de enrique).
- `sobreoferta` / `sobreoferta_detalle` siguen `null`/`pendiente`; `agua_detalle.coste_eur_ha` y `perdida_sal_pct` son `null`.
- `RES-F29` apunta a un fichero del repo (`research/predictive-model-research.md`), no a una fuente citable: hay que citar la FAO-29 primaria.
- Fuentes de bloques mock (FEGA, SoilGrids, "HLS-VI (mock)") no tienen entrada en `fuentes[]` hasta que el dato sea real.
- SIAM/IMIDA/FAO: licencia sin verificar (`verify`); lo sigo en `submission/data-citations.md`.
- Pendientes míos, no de enrique: Zona 1/2 (Anexo I), SIGPAC desde código con el FEGA, `legal.check` en la API.


## Nota 2026-11-14 (gonzalo): 19 anios historicos, no 20; n del exito
- Enrique (#138, #144): el clima observado son **19 años (2006-2024)**, no 20. El contrato no fija el número: `exito_pct.n_anios_historicos` lo da el motor (hoy 19).
- Acordado (#138): el éxito y su horquilla se calculan sobre los años históricos (`n_anios_historicos`, `n_efectivo`); los 52 años-plan pasan a `n_muestras` (informativo, no independientes). Campos nuevos añadidos al schema (opcionales, add-only).
- El borrador v1 antiguo (`generate_draft.py`, serie 2005-2024 simulada) conserva 20 años solo como ejemplo; v1.1 manda.
