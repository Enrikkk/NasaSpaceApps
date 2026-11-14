# Semáforo legal determinista (prototipo de T-019, sin reclamar)

Preparado por el agente de gonzalo. **No está en `app/`**: si T-019 se reclama, se mueve a `app/backend/rules/`.
**Herramienta de apoyo, no es asesoría legal. Consulta a tu técnico.** Regla del proyecto: el motor calcula, el LLM no.
Todo sale de `rules.csv` y `grupos_cultivo.csv`, y **todas las reglas están `por_verificar`** hasta que gonzalo las contraste en el BOE.
Fuente única de las reglas: `research/ley-3-2020-reglas.md` (no se ha añadido ningún artículo ni umbral que no esté ahí).

| Fichero | Qué es |
|---|---|
| `rules.csv` | 32 filas (L-01..L-22, P-01..P-10): id, nombre, descripción, norma, artículo, ámbito (`zona_1`/`ambas`/`PAC`), condición, tipo (`dura`→rojo, `aviso`→ámbar, `informativo`), fuente, URL, `estado`, `implementada` (si/parcial/no) y motivo si no |
| `grupos_cultivo.csv` | `legal_group` por cultivo (art. 51.1) con confianza (`confirmado`/`inferido`/`no_confirmado`) y fundamento; alias en `alias` (separados por `|`) |
| `legal.py` | Librería (solo stdlib): `check`, `allowed`, `to_contract`, `info_cultivo` |
| `test_legal.py` | 31 tests `unittest` (4 de ellos validan contra `contract.schema.json` si hay `jsonschema`) |

## Cómo ejecutar

```bash
cd research/prototypes/legal_rules
python3 -m unittest -v test_legal            # los tests de esquema se omiten si no hay jsonschema
# con jsonschema (venv, no en el sistema):
python3 -m venv /tmp/v && /tmp/v/bin/pip install jsonschema && /tmp/v/bin/python -m unittest -v test_legal
```

```python
import legal
legal.check(rotacion, parcela, "zona_2")        # dict semaforo_legal (vocabulario interno)
legal.check(rotacion, parcela, "zona_1", contrato=True)   # vocabulario del esquema (ver "Divergencias")
legal.allowed("brocoli", "lechuga", "zona_1")   # (False, "dos ciclos consecutivos de Grupo 1 ...", "Ley 3/2020 art. 51.3")
```

`zona`: `"zona_1"`, `"zona_2"`, `"por_verificar"` (cualquier otro valor, o `parcela.cobertura == "basico"`, o rotación sin ciclos → `gris`).
Salida de `check`: `{color, motivo, articulo, comprobaciones:[{id, regla, resultado ok|falla|no_aplica|no_evaluable, articulo, estado, nota?}], zona, version_reglas, nota}`.
`nota` = "Herramienta de apoyo, no es asesoría legal. Consulta a tu técnico."

### Entradas que lee (todas opcionales salvo `ciclos`)
`rotacion`: `ciclos` (lista de cultivos, la rotación se repite), **`ciclos_por_anio`** (int) o `anios` (lista de listas), `ciclo_dias` {cultivo: días},
`suelo_desnudo_meses` (si falta y `es_actual`, usa `parcela.ndvi.meses_desnudo`: máximo de meses **seguidos** en oct-mar), `cobertera_invierno`, `n_kg_ha_anio`, `abonado[{forma_n, fondo, ultimo_tercio}]`.
`parcela`: `regadio`, `invernadero`, `distancia_orilla_m`, `explotacion_ha`, `ndvi`, `cobertura`.

### Cómo se decide el color
- **rojo**: una regla dura aplicable falla y los datos son firmes. Una regla de Zona 1 solo puede dar rojo con `zona_1`. Si el fallo depende de un grupo **inferido** (lechuga), o de la exención ≤ 10 ha de BCAM 7, baja a ámbar.
- **amarillo**: reglas de Zona 1 con `zona = por_verificar` (se muestran como `no_evaluable` con "si fuese Zona 1: ok/falla"), cultivo de grupo desconocido (art. 51.4), falta el calendario (`ciclos_por_anio`) o la parcela está en la franja de 1.500 m.
- **verde**: ninguna regla evaluable falla. Las comprobaciones `no_evaluable` por falta de datos de abonado/ribera (L-02, L-03, L-09, L-10, L-11) **no** bajan el color pero se listan en el `motivo`.
- **gris**: sin cobertura (D-009 cobertura básica) o sin ciclos.

## Colores esperados (3 rotaciones del borrador de contrato)

Supuesto: se añade `ciclos_por_anio = 1` (cada elemento de `ciclos` es una campaña anual; el borrador no lo dice). **Sin ese campo, todas salen ámbar** por art. 39.2 no evaluable (test `test_sin_ciclos_por_anio_es_ambar`). Parcela demo: regadío, sin invernadero; `actual` con 5 meses de suelo desnudo, las otras 1.

| Rotación | `zona_2` | `por_verificar` | `zona_1` |
|---|---|---|---|
| actual: melón / barbecho / lechuga | **verde** (art. 39.2; nota: suelo desnudo no es obligación legal en Zona 2) | **amarillo** (art. 51.6: "si fuese Zona 1: falla") | **rojo** (art. 51.6, suelo desnudo 5 meses > 2) |
| alt-a: brócoli / haba / alcachofa | **verde** (art. 39.2, BCAM 7) | **amarillo** (art. 51.2; "si fuese Zona 1: ok") | **verde** (arts. 39.2, 51.2, 51.3, 51.6) |
| alt-b: cebada / veza / cebada | **verde** (art. 39.2, BCAM 7) | **amarillo** (art. 51.4, grupo NO CONFIRMADO) | **amarillo** (art. 51.4, grupo NO CONFIRMADO) |

Con `zona_2`, un grupo desconocido (cebada, veza) no importa: el art. 51 no obliga fuera de Zona 1.

## Reglas implementadas
`L-07` (art. 39.2, ciclos/año), `L-14` (51.2), `L-15` (51.3, consecutivos; el barbecho se salta y la rotación se repite: INFERIDO), `L-16` (51.4, grupo desconocido), `L-17` (51.6, suelo desnudo > 2 meses; parcial),
`L-03` (29.4.b, 170 kg N/ha/año en franja), `L-02` (29.4.a: solo detecta que la parcela está en la franja y avisa; parcial), `L-09` (40.2 urea), `L-10` (40.4 abonado de fondo con N), `L-11` (40.3 nitrato amónico último tercio),
`P-02` (BCAM 7: cambio de cultivo cada 3 años, nivel parcela). `L-01` es el propio parámetro `zona`.
`allowed(prev, cur, zona)` implementa solo L-15: Zona 2 siempre `True`; Zona 1 prohíbe Grupo 1 + Grupo 1 salvo `ciclo_dias` < 45 en ambos (sin `ciclo_dias` → `False`, por prudencia);
`por_verificar` → `True` con motivo "por verificar" (`conservador=True` lo trata como Zona 1); grupo desconocido → `True` con aviso (`conservador=True` → `False`).
Si `prev` es barbecho, la DP debe pasar el último cultivo real.

## Reglas NO implementadas (y por qué)
| Regla | Motivo |
|---|---|
| L-06 (5 % de retención, art. 37) | Nivel explotación, no rotación. Aviso fijo en la ficha |
| L-04, L-05 (resto del art. 29), L-08, L-12, L-13, L-18, L-19, L-22 | Informativas o de instalación/explotación, no de rotación |
| L-20 (DA 13: N inorgánico en Zona 1) | **Vigencia NO CONFIRMADA** (plazo de 2 años desde 31/08/2021); además exige plan de abonado |
| **L-21 programa de actuación, art. 48** | El programa (Orden 16/06/2016 y revisiones) **no se ha leído**: no se conocen sus límites de N por cultivo ni periodos |
| **Meses de otoño-invierno del art. 51.6** | El texto no los define. El prototipo usa oct-mar (constante `VENTANA_OTONO_INVIERNO`, INFERIDO) |
| Forma de la cobertera y estructuras de retención (51.6) | Solo existe el flag `cobertera_invierno`; no se comprueba especie ni enterrado |
| P-01 (33 % anual, BCAM 7) | Es de explotación; no tenemos la superficie ni los cultivos de toda la explotación |
| P-04 (exenciones BCAM 7) | Falta la superficie total de la explotación (solo 4,09 ha de la parcela) |
| **P-06, P-07, P-08 (ecorrégimen P3), Anexo XV del RD 1048/2022** | El anexo XV (especies mejorantes) **no está leído**: NO CONFIRMADO qué cultivos cuentan; el límite de barbecho solo consta en una FAQ de 2023 |
| P-03, P-05, P-09, P-10 | Definiciones, historia o importes (el importe lo usa el motor económico de Enrique) |
| Ciclo de cultivo de la cubierta (veza) | El texto no dice si una cobertera enterrada cuenta como "ciclo" para 39.2 y 51.2. Se trata la veza como grupo desconocido |
| "Año" de los ciclos (39.2) | No definido; se usa el agrupamiento que declara `ciclos_por_anio`/`anios` (INFERIDO año natural) |

## Divergencias con el contrato borrador y el mock (propuestas, no editado nada)

1. **El mock de la app contradice el informe.** `app/data/torre-pacheco.mock.json`, rotación `actual`: `"Hoja repetida en zona 2 y suelo desnudo > 2 meses en invierno"`, `amarillo`. Con la parcela en Zona 2 (WMS CARM, muy probable) los arts. 50-54 no obligan: ni la hoja repetida (51.3: solo Zona 1; y melón/barbecho/lechuga no repite hoja) ni el suelo desnudo (51.6: solo Zona 1) son infracción. **Propuesta**: con zona 2 → `verde`, `articulo: "Ley 3/2020 art. 39.2"`, motivo "Sin incumplimientos evaluables en Zona 2; 5 meses de suelo desnudo no es obligación legal en Zona 2, una cubierta sería mejora agronómica"; con zona sin confirmar → `amarillo`, art. 51.6 "por verificar". Además `articulo: "Ley 3/2020 (comprobar articulo exacto)"` debe pasar a un artículo concreto.
2. **El borrador `torre-pacheco.contract-v1.draft.json` ya no dice "hoja repetida", pero:** (a) `actual` afirma `art. 51.6 resultado: no_cumple` con la zona `por_verificar`: debería ser `indeterminado` (o `no_evaluable`) y el color ámbar solo por la zona; (b) `alt-a` y `alt-b` salen `verde` con la zona sin verificar, cuando con `por_verificar` las reglas de Zona 1 deberían dejar ámbar; (c) `alt-b` queda verde por "bajo consumo de agua", que no es criterio legal, y cebada/veza no tienen grupo legal confirmado; (d) `art. 39 cumple` se afirma sin que el contrato lleve ciclos por año.
3. **Vocabulario de `resultado`**: el esquema admite `cumple|no_cumple|aviso|indeterminado`; la tarea pide `ok|falla|no_aplica|no_evaluable`. `check()` devuelve el segundo; `to_contract()` (o `contrato=True`) traduce (`ok→cumple`, `falla→no_cumple`, `no_evaluable→indeterminado`) y **omite** `no_aplica`. **Propuesta**: añadir `no_aplica` al enum del esquema (la UI puede decir "no aplica en Zona 2") o fijar un solo vocabulario antes de congelar el contrato.
4. **Campos que el motor necesita y el contrato no tiene**: `rotaciones[].ciclos_por_anio` (o `anios`), `ciclo_dias` por cultivo, y opcionales `abonado`, `n_kg_ha_anio`, `cobertera_invierno`, `parcela.distancia_orilla_m`, `parcela.explotacion_ha`, `parcela.invernadero`. Los extra del semáforo (`id`, `nota`, `zona`, `version_reglas`) caben porque el esquema no cierra `additionalProperties`.

## Dudas que gonzalo debe cerrar en el BOE (en este orden)
1. **Zona de la parcela demo** (SITMurcia / WMS CARM / Anexo I): si es Zona 1, cambian los colores a la columna `zona_1` (actual rojo).
2. **Art. 2.2 y 26**: Sección 1.ª (arts. 27-49) en Zonas 1 y 2, Sección 2.ª (arts. 50-54) solo Zona 1. Es la base de todos los `no_aplica`.
3. **Art. 51.1, tabla de grupos**: melón, alcachofa, haba (2); "Hortalizas del género Brassica" y "Hortalizas de hoja" (1). Confirmar que la **lechuga** cae en "de hoja" (hoy `inferido`) y decidir **cebada, veza, limón y alcaparra** (hoy `no_confirmado`, art. 51.4).
4. **Art. 51.3**: redacción exacta y alcance de la excepción de "ciclo inferior a 45 días" (¿ambos ciclos? ¿solo el segundo?); ¿cuenta un barbecho entre dos Grupo 1 como alternancia?
5. **Art. 51.2 y 39.2**: máximos de ciclos (2 y 3 de hoja < 45 días), definición de "año" y si una cobertera/veza cuenta como ciclo. Necesitamos el dato `ciclos_por_anio` de Enrique.
6. **Art. 51.6**: meses de "otoño e invierno" (el prototipo usa oct-mar), exclusión de invernaderos y qué cuenta como cobertera suficiente.
7. **Art. 40.2, 40.3, 40.4** (urea, nitrato amónico, abonado de fondo): redacción exacta. **Art. 29.1, 29.2, 29.4.a/b**: 1.500 m, prohibición y 170 kg N/ha/año; el informe señala una posible tensión entre 29.2 (prohíbe todo fertilizante) y 29.4.b (170 kg).
8. **DA 13 (L-20)**: ¿sigue vigente? Solo importa en Zona 1.
9. **Art. 48 y programa de actuación de zona vulnerable**: ¿fija límites de N por cultivo? Si sí, hay una regla dura más.
10. **BCAM 7 (RD 1049/2022, anexo II)**: 33 %, cambio cada 3 años, exención ≤ 10 ha y definición de cultivo; con qué superficie de explotación se decide P-02.
11. **Análisis del BOE** el día de la entrega: ninguna modificación posterior a 06/09/2023 (reforma sancionadora solo en trámite).
12. Al contrastar cada regla, cambiar `estado` a `verificado` en `rules.csv`/`grupos_cultivo.csv` (el motor lo propaga a `comprobaciones[].estado`).
13. **Licencias** (AGENTS.md §6): el prototipo solo usa la librería estándar y citas de normas del BOE; `jsonschema` (MIT) se usa solo en el venv de desarrollo y no se distribuye.
