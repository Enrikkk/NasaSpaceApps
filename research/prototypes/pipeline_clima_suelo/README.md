# Prototipo: clima, ET0 y suelo con cache (preparación de T-011, sin reclamar)

Preparado por el agente de gonzalo. **No está en `app/` ni en `coordination/`**; no hay commit. Solo librería estándar
(Python 3.11); `jsonschema` solo para validar (venv, no en el sistema). Produce los bloques `clima` y `suelo` del
contrato v1 borrador (`research/contract-v1-draft/`) con `_status: "real"` y comprueba que validan.

## Cómo ejecutar

```bash
cd research/prototypes/pipeline_clima_suelo
python3 build_blocks.py 37.7383 -0.98838          # resumen + out/37.7383_-0.98838.blocks.json (+ contador de red)
python3 build_blocks.py 37.7383 -0.98838 --json   # solo el JSON {clima, suelo, fuentes_nuevas}
python3 -m unittest -v                            # 24 tests, sin red (usan cache/)
/ruta/venv/bin/python validate_blocks.py          # esquema + 12 invariantes + cordura (venv con jsonschema)
AGROCKHAM_OFFLINE=1 python3 build_blocks.py ...   # prohíbe la red: falla si falta algo en la cache
AGROCKHAM_CACHE_DIR=/otra/ruta python3 ...        # otra carpeta de cache
```

| Fichero | Qué es |
|---|---|
| `pipeline.py` | red con contador y reintentos, cache por celda, derivados de clima y suelo |
| `build_blocks.py` | CLI `lat lon` |
| `validate_blocks.py` | valida los bloques contra `contract.schema.json`, los mezcla en una copia del borrador y pasa `validate.py`; cordura |
| `test_pipeline.py` | tests unitarios (celdas, relleno -999, texturas, conversiones, reintentos, límite de SoilGrids, bloques desde cache, esquema) |
| `cache/` | cache de la parcela demo (224 KB, 4 ficheros JSON; <1 MB, por eso está dentro del prototipo) |
| `out/` | salida generada (12 KB) |

## Qué hace

| Dato | Fuente y llamada | Celda de cache (clave) |
|---|---|---|
| T2M_MAX, T2M_MIN, PRECTOTCORR 2005-2024 diario | NASA POWER, `community=AG`, `&time-standard=UTC`, 1 llamada | nodo MERRA-2 de 0,5° lat x 0,625° lon (`75_-2`, se consulta en el nodo 37.5, -1.25) |
| IMERG_PRECTOT 2005-2024 diario | NASA POWER (IMERG vía POWER), 1 llamada | píxel IMERG de 0,1° (`377_-10`, centro 37.75, -0.95) |
| Lluvia ERA5 + ET0 FAO-56 diarios | Open-Meteo archive API, `models=era5`, 1 llamada | celda de 0,1° (`377_-10`) |
| clay, sand, silt, soc, phh2o, nitrogen en 0-5, 5-15, 15-30 cm | SoilGrids v2 REST, 1 llamada (6 propiedades x 3 profundidades) | celda de 0,0025° (~220 x 280 m, `15095_-396`) |

Decisión de diseño sobre la celda de POWER: MERRA-2 (T2M, PRECTOTCORR) es de 0,5° x 0,625°, pero IMERG es de 0,1°.
Medido: dos puntos a 25 km dan el mismo T2M/PRECTOTCORR pero IMERG distinto (0,26 frente a 0,07 mm el 1-ene-2024).
Por eso hay **dos** llamadas a POWER con claves distintas; con una sola celda de 0,5° se mezclarían ~25 píxeles de IMERG.
Se consulta siempre en el **centro de la celda**, así lo cacheado no depende de quién llegue primero.

Cache: `cache/<fuente>_<celda>.json`; series diarias compactas (inicio + lista de 7305 valores; `-999` de POWER y huecos
guardados como `null` y contados en `relleno_descartado`), URL, fecha de descarga, unidades, resolución, licencia.
Un año se descarta de una serie si tiene menos de 360 días válidos. `AGROCKHAM_OFFLINE=1` impide cualquier llamada.

### Bloque `clima`
- `lluvia_anual_mm`: `valor` = media 2005-2024 de las tres fuentes; `horquilla` = [mín, máx] entre fuentes (no es un intervalo de confianza);
  `fuentes` = ids de `fuentes[]` (`power`, `imerg`, `open-meteo`, este último **nuevo**: la salida trae `fuentes_nuevas` para añadirlo al contrato); `por_fuente_mm`.
- `serie_anual[]`: 20 años; `lluvia_mm` = media de las fuentes ese año; **`lluvia_por_fuente_mm {power, imerg, era5}`**; `tmin_min_c`, `tmax_max_c`, `dias_calor_gt_38`.
- `dias_calor_gt_38`: días/año con T2M_MAX > 38 °C, tendencia OLS por década, más `dias_calor_gt_35`, `tmax_max_20_anios_c` y un aviso.
- `dias_helada`: **`fuente: "pendiente SIAM"`, `provisional: true`**. El contrato exige `valor` numérico, así que lleva el cómputo provisional
  de días con T2M_MIN < 0 °C en la celda MERRA-2 (ver trampas). La cifra real vendrá de SIAM (T-014). En `serie_anual` no se incluye `dias_helada`.
- `et0_mm_mes {valores[12], anual_mm, ...}`: media 2005-2024 de la suma mensual de ET0 FAO-56 (ene..dic, mm/mes).
- `metadatos`: fechas de descarga, URL de cada llamada, unidades, resolución, celda consultada, rellenos descartados, licencias, trampas.

### Bloque `suelo`
- Media ponderada por espesor (5, 10, 15 cm) de 0-30 cm. `textura` USDA en español (triángulo con arena+limo+arcilla normalizados a 100).
- Conversiones explícitas (`metadatos.conversiones`): clay/sand/silt g/kg ÷ 10 = %; `soc` dg/kg ÷ 10 = g/kg de **carbono** orgánico;
  `materia_organica_pct` = SOC (g/kg) ÷ 10 × 1,724 (van Bemmelen); `phh2o` ÷ 10; `nitrogen` cg/kg ÷ 100 = g/kg. El `d_factor` de la respuesta se comprueba contra lo esperado.
- `agua_disponible_mm`: Saxton y Rawls 2006 (CC 33 kPa − PMP 1500 kPa) por capa x espesor. Es la reserva **de 0-30 cm** (≈150 mm/m), no de toda
  la zona radicular; el mock usaba 120 mm (profundidad no definida). Sin corrección por gravas. Decisión pendiente: ¿enrique la quiere a 1 m?
- Además de lo exigido: `arena_pct`, `limo_pct`, `arcilla_pct`, `soc_g_kg`, `ph_h2o`, `nitrogeno_g_kg`, `capas[]` por profundidad.

## Resultados medidos (parcela demo 37.7383, -0.98838)

**Tiempos** (portátil de gonzalo):

| Ejecución | Tiempo | Llamadas de red |
|---|---|---|
| 1.ª (cache vacía) | 9,4 s (9,3 s en red) | 4: POWER x2, Open-Meteo x1, SoilGrids x1; 0 s de espera por límite |
| 2.ª y siguientes | 0,09 s | **0** (contador `RED: 0 llamadas`; también con `AGROCKHAM_OFFLINE=1`) |

Con una sola celda nueva SoilGrids no espera; la espera de 12,5 s (5 llamadas/min) solo se nota con 2+ celdas de suelo seguidas.
La hora de la última llamada se guarda en `cache/.state/` para respetar el límite entre procesos. Reintentos con espera 15/30/60 s en 429/5xx/timeout.

**Cifras** (20 años 2005-2024):

| | |
|---|---|
| Lluvia anual | **308 mm**, horquilla 262-366: POWER 297, IMERG 366, ERA5 262 mm |
| 2024 | ERA5 184,7 / POWER 210,9 / IMERG 263,4 mm: **coincide** con la investigación (185 / 211 / 263) |
| ET0 anual | 1422 mm (máx. jul 186, mín. dic 58 mm); déficit medio ≈ 1114 mm |
| Días > 38 °C | 0 en 20 años (MERRA-2; máx. 37,6 °C). Ver trampas |
| T2M_MIN mínima 20 años | +1,4 °C; **0** días T2M_MIN < 0 (provisional) |
| Suelo 0-30 cm | franco-arcillo-limoso (arena 18,7 / limo 43,8 / arcilla 37,4 %), pH 7,97, N 1,1-1,9 g/kg |
| MO | 2,14 % media 0-30 cm (SOC 12,4 g/kg); **superficie 0-5 cm: 3,72 % (SOC 21,6)**; 15-30 cm: 1,59 % |
| Agua disponible 0-30 cm | 44,9 mm |

**Validación**: `validate_blocks.py` → bloque `clima` OK, bloque `suelo` OK, esquema completo del borrador con los bloques reales OK,
12/12 invariantes OK, 10/10 comprobaciones de cordura OK (lluvia 250-350 mm, fuentes difieren 104 mm, 2024 coincide, ET0 estacional, etc.).
Tests: 24/24 sin red. El validador detecta una mutación (test que borra `lluvia_mm`).

## Trampas y avisos (también en `metadatos.trampas`)
1. **`FROST_DAYS` de POWER no es Tmin < 0**; no se usa. Las heladas reales vendrán de SIAM. El provisional (T2M_MIN < 0) tampoco sirve como cifra final:
   MERRA-2 promedia ~50 km (incluye mar) y da +1,4 °C de mínima en 20 años.
2. **`EVLAND` de POWER no ve el riego** (evaporación del modelo de superficie): inútil en regadío. La ET0 sale de Open-Meteo.
3. **El mismo suavizado hace 0 días > 38 °C**: el `dias_calor_gt_38` de POWER es una cota inferior. Conviene sacar calor y helada de SIAM TP91 (T-014).
   El mock tenía ~4 días/año y 1 helada: la realidad local no está en POWER.
4. **Tres lluvias distintas**: IMERG +19 % sobre la media y ERA5 -15 %. No hay "la" lluvia; por eso horquilla y lluvia por fuente. La media (308) cae en el rango esperado.
5. IMERG vía POWER exige `&time-standard=UTC`; `-999` es relleno (en esta parcela y periodo hubo 0 rellenos).
6. **SoilGrids es un modelo a 250 m**, no una medida en la parcela. El SOC superficial (21,6 g/kg a 0-5 cm) es alto para un regadío semiárido
   (en el mock el SOC parecía alto; aquí la media 0-30 cm da 2,14 % frente al 1,1 % del mock). Cruzar con análisis locales/IMIDA antes de fiarse.
7. Las elevaciones difieren entre fuentes (MERRA-2 124 m, DEM de POWER en el píxel IMERG 299 m, ERA5 40 m): las temperaturas son del nodo, no de la parcela.

## Licencias y atribuciones (para `submission/data-citations.md`; `licencia_estado: verify` hasta revisarlas)
- **NASA POWER** (MERRA-2 / CERES / GPM IMERG vía POWER): datos abiertos de NASA. Atribución: "NASA Prediction Of Worldwide Energy Resources (POWER)", https://power.larc.nasa.gov/. Citar también los DOI de MERRA-2 (GMAO) e IMERG (NASA GES DISC).
- **GPM IMERG** (NASA/JAXA): https://gpm.nasa.gov/data/imerg. Dato abierto de NASA, citar el DOI del producto.
- **Open-Meteo** (ERA5 y ET0): los datos se ofrecen bajo **CC BY 4.0** (atribución "Weather data by Open-Meteo.com", https://open-meteo.com/); **la API gratuita es solo para uso no comercial**.
  Vale para el hackathon; un producto comercial necesitaría plan de pago o autoalojar. El origen ERA5 es de Copernicus C3S (licencia C3S, citar "Generated using Copernicus Climate Change Service information").
  Hay que añadir `open-meteo` a `fuentes[]` del contrato (entrada lista en `fuentes_nuevas` de la salida).
- **SoilGrids 2.0** (ISRIC): **CC BY 4.0**. Poggio, L., et al. (2021), SOIL 7, 217-240, https://doi.org/10.5194/soil-7-217-2021. https://soilgrids.org/
- **Saxton y Rawls (2006)**, Soil Water Characteristic Estimates by Texture and Organic Matter, SSSAJ 70:1569-1578: ecuaciones publicadas implementadas aquí (código propio, no se copia código ajeno).
- Triángulo textural USDA: clasificación estándar escrita desde cero.
- No se usó el token de Earthdata ni `.env`; ninguna de las cuatro fuentes necesita clave.

## Huecos y qué falta para pasarlo a `app/backend/pipeline/` (T-011)
- Reclamar T-011 y mover el código (`paths: app/backend/pipeline/, app/data/cache/pipeline/`); la cache de demo iría a `app/data/cache/pipeline/`.
- **Heladas y calor reales de SIAM** (T-014): sustituir `dias_helada` provisional y contrastar `dias_calor_gt_38`; ver si SIAM da también lluvia como cuarta fuente (el contrato ya cita `siam`).
- Bloques `parcela` e `historia` (SIGPAC/FEGA) y `escenario_2050` (hoja de ruta) no están aquí.
- Decidir si `agua_disponible_mm` debe ser de 1 m de perfil (pedir 30-60 y 60-100 cm a SoilGrids o asumir la extrapolación por metro: `45 mm / 30 cm ≈ 150 mm/m`).
- Fuente `open-meteo` en el contrato y su `licencia_estado`; decidir qué lluvia usa el motor (media de fuentes, o cada fuente como escenario de incertidumbre).
- Uso en vivo (D-009, `POST /analyze`): llamadas en paralelo y respuesta por partes (`_status: cargando`), cola global para el límite de SoilGrids (5/min por IP: en Cloud Run
  la IP de salida es compartida; precalentar celdas del Campo de Cartagena), cache en un almacén compartido en vez de ficheros locales, y un fallback si Open-Meteo/POWER no responden.
- Cobertura básica fuera del Campo de Cartagena: aún funciona (las cuatro fuentes son globales), pero la comparación de lluvia/helada con SIAM no.
- Soporte de una parcela fuera de rangos (mar, urbano): `build_suelo` lanza `ValueError` si SoilGrids no devuelve datos.
- Tests con red (una llamada por fuente) en CI; hoy todos son offline a propósito.
- Los límites de POWER/Open-Meteo no se han estresado: solo se hizo la parcela demo, con las 4 llamadas del pipeline más 7 llamadas de sondeo a POWER de 4-5 días (para decidir la geometría de celdas).
