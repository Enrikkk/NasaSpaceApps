# H-002 — Motor por parcela («A completo»): idoneidad, regadío/secano, pendiente, suelo, etiqueta ambiental

Autor: enrique (agente Claude), 14 nov ~18:00. Decisión de Enrique tras la petición de Gonzalo (#197): el motor debe devolver rotaciones propias para **cualquier** parcela, no solo Torre-Pacheco.
Base: rama `origin/t020-jaime` @ 91ba395 (o más nueva). Nada se une a `main`: lo hace Enrique.

## Decisiones ya tomadas (no reabrir)
1. **Idoneidad = excluir lo imposible + % de puntuación.** Lo que no puede darse (hortalizas de regadío en secano) sale del catálogo. Lo que va peor pero es posible baja su **puntuación** (no el margen en euros ni el rendimiento) un % tomado de una tabla con fuente. Cada tarjeta debe decir qué factores se aplicaron y que los % sin fuente son **supuestos**.
2. **Opción ambiental = etiqueta**, no interruptor: cada rotación lleva `ambiente: {nivel: "alto"|"medio"|"bajo", motivos: [...]}` (alto = más amigable con el medio ambiente), calculada de forma determinista con agua (m³/ha), cobertura/suelo desnudo (días), crédito de nitrógeno de leguminosas/cubierta y, cuando exista, el semáforo legal. Umbrales = supuestos etiquetados.
3. **Datos que faltan:** si falta pendiente, regadío, suelo… no se inventan: factor 1, y la tarjeta lo dice en «no sabemos» («sin dato de pendiente: no aplicado»).
4. El margen en euros **no cambia** por la idoneidad. Un cultivo penalizado se muestra «recomendada menos», no con otro dinero.

## Entradas del motor por parcela (`ParcelInput`) — contrato propuesto
`parcel_id`, `lat`, `lon`, `area_ha`, `regadio` (true/false/null), `pendiente_pct` (número o null), `suelo{textura, ph, materia_organica_pct, salinidad_ce_dsm, profundidad_cm, drenaje}` (cada uno puede ser null), `zona_legal` ("zona_1"/"zona_2"/null), `cultivos_declarados` (ids del catálogo, o null), `estacion_clima` (por defecto la SIAM de Torre-Pacheco; una sola estación hoy).
Salida: el mismo JSON de rotaciones de hoy + `ambiente` + `idoneidad{factores_aplicados, excluidos, sin_dato}` por rotación.

## ARTURO (rama `arturo-idoneidad`, rutas nuevas `app/backend/engine/suitability/`; no toques el resto del motor)
1. `tables/idoneidad.csv`: por cultivo × factor (pendiente por tramos, regadío/secano, textura, salinidad CE, pH, drenaje, profundidad): `factor` 0-1 o `excluir`, `source_id`, URL, licencia, `conf` (A/B/C), `estado` (`con_fuente`/`supuesto`). Fuentes abiertas candidatas a revisar (licencia incluida): FAO EcoCrop y guías FAO de idoneidad; documentos de la CARM/IMIDA si son reutilizables. **Un % sin fuente se marca `supuesto`, nunca se presenta como dato.**
2. `suitability.py`, función pura sin red: `evaluar(parcela_input, catalogo) -> {excluidos[], factores{cultivo: {factor, motivos[], estado}}, sin_dato[]}`. Y `etiqueta_ambiental(metricas) -> {nivel, motivos[]}` con los umbrales como constantes `supuesto`.
3. Pruebas: ≥ 15 casos (pendiente alta penaliza solo a los cultivos de la lista; secano excluye lechuga, brócoli, melón y alcachofa de regadío; datos nulos → factor 1 y `sin_dato`; etiqueta alto/medio/bajo en casos límite). Código de salida real.
4. Avisa por el bus con hash, tabla de fuentes/licencias y qué cultivos secano (cebada, haba…) tiene el motor con datos de rendimiento y coste: **si no los hay, dilo; en secano la parcela quedaría «no evaluable» y eso es lo honesto.**

## JAIME (Cursor) — después de J1, J2 y J3 (H-001)
1. Rama `t020-parcela`: función `run_parcel(parcel_input) -> dict` en `app/backend/engine/` que reutiliza `build()`, aplica `suitability.evaluar` (exclusiones antes del DP; % sobre la puntuación del DP), añade `ambiente` e `idoneidad` al JSON y funciona con campos nulos.
2. El caso Torre-Pacheco con la entrada actual debe dar **las mismas cifras de dinero** que hoy (prueba de regresión). Otra parcela de prueba debe dar rotaciones distintas cuando cambian pendiente/regadío.
3. Protocolo para Gonzalo: `Engine.run(parcel_input)` según su `app/backend/api/engine_adapter.py` (léelo, no lo edites).
