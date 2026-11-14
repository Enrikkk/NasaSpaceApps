# Contrato v1: BORRADOR de preparación (T-009, sin reclamar)

Preparado por el agente de gonzalo mientras el plan está en espera. **No está en `app/` ni en `coordination/`**: si el
equipo lo acepta, se mueve a `app/data/` en el mismo commit que reclame T-009. **Todos los números son ilustrativos**
(`_status: "simulado"`, aviso MOCK en `_meta.aviso`); el JSON lo genera `generate_draft.py` con semilla fija.

| Fichero | Qué es |
|---|---|
| `torre-pacheco.contract-v1.draft.json` | El mock ampliado (3 rotaciones x 200 muestras) |
| `contract.schema.json` | JSON Schema 2020-12. Obligatorio = P0; resto opcional; `additionalProperties` abierto (tras congelar solo se añaden campos) |
| `validate.py` | Esquema + 12 invariantes + `--selftest` (11 mutaciones que debe rechazar) |
| `generate_draft.py` | Genera el JSON (solo librería estándar, semilla 20261114). Dev-only |

Validar (jsonschema en un venv, MIT, solo herramienta de desarrollo, no se distribuye):
`python3 -m venv /tmp/v && /tmp/v/bin/pip install jsonschema && /tmp/v/bin/python validate.py --selftest`

## Convenciones
- Idioma y claves como el mock (español sin tildes). Unidades en `_meta.unidades`: euros 2025, margen por ha y año medio
  de la secuencia, agua en m³ brutos por ha y año.
- **`_status` por bloque**: `cargando | real | precalculado | simulado`. Un bloque `cargando` puede ir vacío y el
  esquema no le exige nada más (así sirve para las respuestas por partes de `POST /analyze`, D-009). Como una lista
  vacía no lleva `_status`, `_meta.bloques_pendientes` nombra los bloques aún en carga (p. ej. `["rotaciones"]`).
- Sub-bloques de rotación (`exito_pct`, `margen_eur_ha`, `agua_detalle`, `semaforo_legal`...) llevan `_status` opcional;
  si falta, hereda el de la rotación (así un `exito_pct{valor, horquilla}` del mock antiguo sigue siendo válido).
- Criterios: 0-1 con **1 = mejor**. Mapa con las prioridades: rentabilidad→`margen`, agua→`agua`, suelo→`suelo_n`, riesgo→`riesgo`.

## Campos y quién los produce
| Bloque | Qué lleva | Produce | Lee |
|---|---|---|---|
| `schema_version`, `_meta` | versión, aviso MOCK, semilla, `bloques_pendientes`, `cobertura{nivel,ámbito}` (D-009 completo/básico), nota de normalización | gonzalo (T-011, endpoint) | todos |
| `parcela` | id, lat/lon, ha, pendiente, regadío, municipio, comarca, `sigpac{polígono,parcela,recinto}`, `zonas[]` | gonzalo (T-011) | jaime (T-010) |
| `historia.cultivos_declarados[]` | lista 0..N `{campana, anio, cultivo, fuente}`; `campana` explícita ("2025" o "2024-25") | gonzalo (T-011, FEGA) | jaime, enrique |
| `ndvi` | `meses_desnudo`, `meses_vulnerable`, `serie_mensual` opcional | enrique (T-013) | jaime |
| `clima` | `lluvia_anual_mm`, `dias_calor_gt_38`, `dias_helada`, `escenario_2050`, **`serie_anual[]`** (años históricos disponibles; hoy 19, 2006-2024, según enrique #144) | gonzalo (T-011; helada de SIAM) | enrique (motor), jaime |
| `suelo` | textura, MO, agua disponible | gonzalo (T-011) | enrique, jaime |
| `prioridades_defecto` | pesos que suman 1 | gonzalo/jaime | jaime |
| `escenarios_meta` | `n`, `semilla`, método, `anio_clima[]`, `beta_sobreoferta[]`, `factor_coste[]` alineados con las muestras | enrique (T-020) | jaime |
| `rotaciones[]` | ver abajo | enrique (T-020 + T-012/T-018) y gonzalo (`semaforo_legal`, T-019) | jaime (T-010) |
| `variantes` | esqueleto P2: `definiciones[]` (lluvia ±, temp +1/+2, 2050) y `resultados{id→{rotaciones[]}}` | enrique (T-020) | jaime |
| `sensores` | esqueleto del export SIAM TP91: `estacion`, `variables`, `periodo`, `lecturas[{t,tmin_c,...}]` | arturo (T-014) → gonzalo lo empaqueta | jaime |
| `fuentes[]` | `{id, nombre, url, licencia, licencia_estado}`; todo `fuente_id` del documento apunta aquí | gonzalo (T-015 las cita en `submission/`) | jaime |
| `no_sustituye` | frase fija "consulta a tu técnico" | gonzalo | jaime |

**`rotaciones[]`** (actual + 2; ids `actual`, `alt-a`, `alt-b`):
- `exito_pct{valor, horquilla, k_malos, n, metodo, desglose{clima, economico, conjunto}, peores_anios[]}` (T-012 núcleo, D-008:
  año malo = pérdida climática ≥ 20 % **o** margen < 0 con el precio de ese año; horquilla Wilson 95 %). `valor = 100(n-k)/n`.
- `margen_eur_ha{valor, horquilla, p10, p50, p90, breakeven_precio_eur_kg}` (T-018). `horquilla` es **siempre** `[p10, p90]`.
  `valor` = media de las muestras. `breakeven_precio_eur_kg` es un mapa `{cultivo: €/kg}` (los cultivos sin ingreso no figuran).
- `escenarios_margen_eur_ha[]`: 200 muestras; **el índice i es el mismo año/β/coste en todas las rotaciones** (T-020). La UI
  calcula "B gana en el X %" y pondera con `criterios` en el navegador.
- `agua_m3_ha` + `agua_detalle{etc_mm, bruto_m3_ha, coste_eur_ha, ecw_dSm, ece_dSm, perdida_sal_pct, ...}` (T-012 núcleo C).
- `criterios{margen, agua, suelo_n, riesgo}` 0-1 (T-020); `sobreoferta` 0-1 + `sobreoferta_detalle{indice_SI, beta, efecto_precio_pct, semaforo, escala}` (T-018).
- `inversion{pico_caja_negativa_eur_ha, meses_hasta_primer_ingreso, payback/VAN/TIR/EAA opcionales}` (T-018; los 4 últimos solo perennes).
- `semaforo_legal{color, motivo, articulo, comprobaciones[{regla, resultado, articulo, estado}]}` (gonzalo, T-019).
  `estado` = `verificado` (artículo leído en el BOE por una persona) o `por_verificar`. **En el borrador todas son `por_verificar`.**
- `suelo_desnudo_meses` (nuevo, útil para la línea temporal), `por_que`, `beneficios` (nuevo; el reto pide beneficios),
  `evidencia[]` (con `fuente_id`), `huecos`, `riesgos`. Opcionales definidos solo en el esquema: `filtros[]`, `rendimiento_t_ha`.

## Cambios respecto a `app/data/torre-pacheco.mock.json` (para el que lo lea)
1. `_status` de primer nivel (cadena con el aviso) pasa a `_meta.aviso`; `_status` ahora es el enum por bloque.
2. `historia` pasa de lista a objeto `{_status, cultivos_declarados[]}` (para poder marcarla `cargando`); `anio` se mantiene como alias.
3. `parcela.zonas`: `mar_menor_zona_2` → `mar_menor_zona_por_verificar` (la capa solo confirma zona vulnerable a nitratos ES62_1; el Anexo I no está leído).
4. `clima.lluvia_anual_mm.fuentes` pasa de nombres a ids de `fuentes[]`. `alt-b`: `cebada, veza, cebada` (D-008).
5. Todo lo demás del mock se conserva con los mismos nombres.

Estado de D-008 al escribir esto: **PROPOSED por enrique, sin ACCEPT en `DECISIONS.md`**; el borrador ya aplica el cambio de `alt-b`.

## Decisiones abiertas para el equipo
1. **Forma de `historia` y de las listas** (objeto con `_status` frente a lista + `_meta.bloques_pendientes`): jaime y gonzalo.
2. **Unidad de `margen_eur_ha` y escenarios**: ¿€/ha·año medio de la secuencia (borrador) o €/ha de la rotación completa? enrique y jaime.
3. **`breakeven_precio_eur_kg`**: mapa por cultivo (borrador) o un escalar del cultivo principal. enrique.
4. **Normalización de `criterios`**: escalas de referencia fijas (borrador) o min-max entre las rotaciones de la parcela (fuerza 0 y 1 aunque difieran poco). enrique y jaime.
5. **Nombres de prioridades vs criterios** (`suelo` frente a `suelo_n`, `rentabilidad` frente a `margen`): unificar ahora o dejar el mapa del README.
6. **`valor` del margen**: media (borrador) o P50; ¿añadimos `cvar80` desde el principio? enrique.
7. **`exito_pct`**: ¿se muestra con la horquilla Wilson y los años históricos disponibles (19) solamente, o también Jeffreys (research da ambos)? ¿D-008 aceptado? humanos.
8. **Zona 1/2 del Mar Menor**: gonzalo debe leer el Anexo I (o usar el campo `zona_marmenor` del SIGPAC de IMIDA que ya aparece en `research_notes/`); mientras, `mar_menor_zona_por_verificar` y las reglas solo de zona 1 salen `indeterminado`. Artículos 39/40/29/51/51.6 y BCAM 7 también `por_verificar`.
9. **Semáforo `gris`** para cobertura básica (resto de España, D-009): ¿mismo bloque con `color: gris`? gonzalo y jaime.
10. **Licencias**: `fuentes[].licencia_estado` es `verify` en casi todo (solo BOE y propias en `ok`); revisar antes del envío (`submission/data-citations.md`). SIGPAC: acceso desde código por confirmar con el FEGA.
11. **Variantes P2**: ¿se calcula cada variante con 200 muestras o solo `exito_pct`/`margen`/`criterios`? (el esquema admite lo segundo, más ligero).
12. **Tamaño**: ~35 kB por parcela con 3x200 muestras; con `variantes` completas crecería. ¿Muestras con 1 decimal menos o 100? jaime.
13. **Congelado**: ¿se congela con `schema_version: "1.0.0"` y el esquema añade solo campos desde entonces? El validador debe correr en CI/hook antes de cada cambio de contrato (propuesta).
