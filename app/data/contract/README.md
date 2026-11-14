# Contrato de datos Agrockham v1.1 (T-009)

Un documento JSON por parcela. Lo produce el backend (pipeline + motor + API) y lo lee el frontend. Es la unica
frontera entre ambos: nadie lee ficheros internos de otro.

| Fichero | Que es |
|---|---|
| `../contract.schema.json` | JSON Schema 2020-12 (`schema_version` 1.1.0). Obligatorio = P0; el resto opcional; `additionalProperties` abierto |
| `../torre-pacheco.contract.example.json` | Ejemplo conforme al contrato. **MOCK**: todo `simulado`, numeros ilustrativos, semilla fija. Para desarrollar la UI |
| `validate_contract.py` | Esquema + 15 invariantes (FALLO / AVISO) + `--selftest` (15 mutaciones que debe rechazar) + `--strict-licencia` |
| `adapt_enrique.py` | Convierte la salida del motor (`app/data/torre-pacheco.json`, rama de enrique) al contrato. No inventa datos: renombra, normaliza vocabulario, avisa de lo que falta |
| `generate_example.py` | Genera el borrador del ejemplo (stdlib, semilla 20261114, 19 anios 2006-2024) |

Historia y razones de cada cambio: `research/contract-v1-draft/` (README, `DIFERENCIAS-con-torre-pacheco-json.md`,
`v1.1/CHANGELOG-v1.1.md`). No se borra: es el registro.

## Validar

`jsonschema` va en un venv, nunca en el sistema (herramienta de desarrollo, MIT, no se distribuye):

```bash
python3 -m venv /tmp/venv-contract && /tmp/venv-contract/bin/pip install jsonschema
cd app/data/contract
/tmp/venv-contract/bin/python validate_contract.py ../torre-pacheco.contract.example.json --selftest
```

Salida: `RESUMEN: OK | errores de esquema: 0 | invariantes fallidas: 0 | avisos: N`. Codigo de salida 0 si no hay errores
de esquema ni FALLO. Los AVISO no hacen fallar (p. ej. la politica de licencia: el JSON publicable no debe nombrar
`CARM`/`esam` salvo decision D-010; `--strict-licencia` lo convierte en FALLO).

Validar la salida real del motor:

```bash
python3 adapt_enrique.py ../torre-pacheco.json -o /tmp/tp.v1.1.json --origen "enrique @ <rama> <sha>"
/tmp/venv-contract/bin/python validate_contract.py /tmp/tp.v1.1.json
```

## Regenerar el ejemplo

```bash
python3 generate_example.py /tmp/draft.json
python3 adapt_enrique.py /tmp/draft.json --formato draft-v1 --hoy 2026-11-14 \
    --origen "app/data/contract/generate_example.py (semilla 20261114), mock" -o ../torre-pacheco.contract.example.json
```

## Convenciones

- Claves y textos en espanol sin tildes; unidades en `_meta.unidades` (euros 2025; margen por ha y anio medio de la
  secuencia; agua en m3 brutos por ha y anio). Un `margen_eur_ha` sin `unidad` es invalido.
- Criterios 0-1 con **1 = mejor**. Mapa prioridad -> criterio: rentabilidad -> `margen`, agua -> `agua`, suelo -> `suelo_n`,
  riesgo -> `riesgo`.
- Rotaciones: minimo 3, una sola `es_actual`, ids libres (`actual`, `alt-a`, `alt-b` en el ejemplo; `s1..s3` en el motor).
  D-008: ninguna rotacion con alcaparra (sin fuente de coste, precio, agua ni salinidad).
- `semaforo_legal.comprobaciones[].resultado` = `ok | falla | no_aplica | no_evaluable`; `estado` = `verificado`
  (articulo leido en el BOE por una persona) o `por_verificar` (hoy todas). `parcela.zonas` no afirma zona 1/2 del Mar
  Menor mientras no se lea el Anexo I: usa `mar_menor_zona_por_verificar`.

## `_status` por bloque

`cargando | real | precalculado | simulado`. Un bloque `cargando` puede ir vacio y el esquema no le exige mas (asi sirve
para las respuestas por partes de `POST /analyze`, D-009). Las listas (`historia`, `rotaciones`) no llevan `_status`:
su estado va en `_meta.estado_bloques` y los bloques aun en carga se nombran en `_meta.bloques_pendientes`.
`mock` del motor se escribe `simulado`; `provisional` se escribe `simulado` + `provisional: true`. Si hay algun bloque
`simulado`, `_meta.aviso` debe empezar por MOCK y la UI lo muestra.

## Quien produce cada bloque

| Bloque | Produce | Lee |
|---|---|---|
| `schema_version`, `_meta`, `fuentes[]`, `no_sustituye` | gonzalo (API / adaptador) | todos |
| `parcela` (SIGPAC desde ATOM), `historia` (FEGA), `clima`, `suelo`, `prioridades_defecto` | gonzalo (T-011, T-024) | jaime, enrique |
| `rotaciones[].semaforo_legal` | gonzalo (T-019, reglas con articulos) | jaime |
| `ndvi` (`meses_desnudo`, `meses_vulnerable`) | enrique (T-013) | jaime |
| `escenarios_meta`, `rotaciones[]` (`exito_pct`, `margen_eur_ha`, `agua_*`, `criterios`, `sobreoferta*`, `inversion`, `escenarios`), `variantes` | enrique (T-012 / T-018 / T-020) | jaime |
| `sensores` | arturo (T-014), lo empaqueta gonzalo | jaime |

jaime (T-010) lee el contrato y calcula en el navegador "B gana en el X %" y la ponderacion por prioridades.

## Reglas de congelacion

1. Tras congelar el contrato solo se **anaden campos**: no se renombra, no se quita, no se cambia el tipo ni el sentido
   de uno existente. Un cambio rompedor es una version mayor y pasa por el bus (`to: all`) y `DECISIONS.md`.
2. El esquema es abierto (`additionalProperties`), asi que anadir un campo nunca rompe a quien lee. Quien produce un campo
   nuevo lo documenta en el esquema (`description`) en el mismo commit.
3. `validate_contract.py` debe pasar antes de cada cambio de contrato y sobre la salida del motor.
4. Un `null` en `exito_pct`, `margen_eur_ha` o `criterios` solo vale si `huecos[]` (o `exito_pct.definicion`) explica por que.
   Nunca se inventan muestras ni valores.

## Decisiones que el contrato recoge

- **D-008** (exito conjunto): el exito de una rotacion es la parte de los anios en que la perdida climatica es < 20 % **y** el
  margen es >= 0 con el precio de ese mismo anio; se muestra con intervalo de Wilson, nunca como prediccion de rendimiento.
  Alcaparra fuera de las rotaciones.
- **D-009** (backend vivo): `POST /analyze {lat, lon, recinto}` devuelve este mismo contrato por bloques, cada uno con su
  `_status`; la parcela demo precargada es el respaldo. `_meta.cobertura{nivel, ambito}` distingue `completo` (Campo de
  Cartagena, por municipio) de `basico` (resto de Espana, indicativo).
- **D-011** (exito sobre anios historicos): `exito_pct.valor` y `horquilla` se calculan sobre `n_anios_historicos` (hoy **19**,
  clima observado 2006-2024; el contrato no fija el numero, lo da el motor), no sobre anios-plan x anios. Los anios-plan
  se guardan en `n_muestras` (informativo: no son independientes, no entran en el intervalo) y `n_efectivo` es el n
  que usa el intervalo (normalmente = `n_anios_historicos`). `valor = 100 (n - k_malos) / n`.
- **`escenarios_meta.alineados`**: `true` solo si el indice `i` de `escenarios` es la **misma muestra** (mismo anio de clima, precio y coste)
  en todas las rotaciones. Hoy el motor real **no** lo cumple, asi que es `false` y la UI no debe presentar "B gana en el X %"
  como resultado firme (orientativo u oculto). Lo pone a `true` enrique cuando lo confirme (D-011).
- **D-010** (precios CARM): el JSON del motor usa precios CARM/ESAM con permiso escrito pendiente; riesgo asumido por enrique,
  pendiente de revisar antes del envio. El validador lo marca como AVISO de licencia. Alternativa abierta: `torre-pacheco.abierto.json`.

## Campos del esquema que el motor aun no emite (huecos conocidos)

`sobreoferta` y `sobreoferta_detalle`, `agua_detalle.coste_eur_ha` y `perdida_sal_pct`, `ciclos_por_anio` verificado,
`escenarios_meta.{semilla, anio_clima, beta_sobreoferta, factor_coste}`, `exito_pct.{n_anios_historicos, n_muestras, n_efectivo}`
(hasta que enrique aplique D-011), y que `margen_eur_ha.media` coincida con la media de `escenarios` (hoy no coincide: el
validador lo avisa). El ejemplo `simulado` los trae todos para que la UI pueda dibujarlos.
