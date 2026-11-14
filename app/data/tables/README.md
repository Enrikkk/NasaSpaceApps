# T-021: tablas de Agrockham

Datos integrados desde `origin/t012-motor-nucleo`, commit `8b3a214`, preparados por Enrique. No se altera el formato largo original. `source_snapshot/` conserva las entradas y `manifest.json` sus SHA-256 y huecos.

Desde la raíz del repo:

```sh
python3 app/data/tables/build_tables.py --input app/data/tables/source_snapshot --output app/data/tables --revision 8b3a214 --supplement app/data/tables/supplement
python3 app/data/tables/test_build_tables.py
```

## Salidas

- `crop_params.csv`: formato largo canónico `crop_id,param,value,unit,source_id,conf,status,nota`. Conserva todas las filas de entrada y añade placeholders vacíos para parámetros ausentes.
- `crops.csv`: una fila por cultivo, con columnas de cada parámetro y `__unit`, `__source_id`, `__conf`, `__status`, `__note`. Leer como CSV, no separar a mano por comas.
- `costs.csv`: formato largo; costes nominales históricos. `price_base_year=2018` es la convención acordada con Enrique (bus #54), basada en encuestas 2017–19; no se ha aplicado inflación. `source_year` queda vacío: no confundir fecha de publicación y base monetaria.
- `prices.csv`: precios Eurostat originales EUR/100 kg, nominales por año y reales base 2015, más conversiones exactas EUR/kg. Brócoli usa coliflor y se marca `proxy`. No hay filas de precios para alcachofa ni veza: ausencia no equivale a cero.
- `area.csv`: superficie, producción y rendimiento Eurostat, con unidades en las cabeceras (kha/kt/t_ha); origen `EUR-AREA`.
- `sources.csv`: registro íntegro de fuentes de Enrique, sin convertir copyright en licencia abierta.
- `manifest.json`: origen, hashes, cobertura de cultivos, huecos y licencias pendientes de revisión.

## Integración y límites

La ausencia de un parámetro se representa por celda vacía, `conf=P`, `status=placeholder`; el consumidor debe comprobarla antes de calcular. No rellenar huecos con cero ni usar supuestos como mediciones. Familias botánicas documentadas en supplement/. Profundidad radicular: zr_min/zr_max; agotamiento: p_depletion (FAO-56 T22). Grupo legal, umbrales de helada/calor y N aún necesitan fuentes o una tabla explícita del motor. T-019 es de Gonzalo.

Alcachofa no es el topinambur (`Helianthus tuberosus`) de FAO-29. Veza se plantea como cubierta: un coste de veza forrajera cosechada no es automáticamente un coste de cubierta. No se añade el precio supuesto de alcachofa (~60 EUR/100 kg): no es una observación Eurostat.

Precios nacionales anuales no son precios de la parcela. No mezclar directamente precios reales base 2015 y costes nominales 2018: Enrique hará la armonización monetaria con HICP antes de calcular márgenes.

Costes de haba seca, cebada y veza: permanecen vacíos. Candidatos oficiales para revisión: MAPA ECREA 2021 Cereales y ECREA 2020 Cultivos proteaginosos y forrajeros. El PDF de proteaginosas ya se ha leído: agrupa cultivos y no permite asignar costes específicos sin un proxy explícito; véase REVIEWED-SOURCES.md. Cereales sigue pendiente. Los valores históricos de IMIDA, parámetros FAO y secundarios tienen licencia pendiente de verificación; su presencia en la tabla no acredita permiso de redistribución pública. Revisar antes de publicar la demo y declarar en `submission/data-citations.md`.

No se incorpora SIAM aquí: Enrique asume serie histórica y colector completo (bus #49). El borrador local de Arturo no se integra para evitar duplicación.

Los suplementos propios de Arturo viven en `supplement/`, separados del snapshot original; el generador rechaza parámetros duplicados y conserva el hash de ambas entradas.

## Revisión 8b3a214 (bus #77)

Incluye `sowing_month` (veza vacío/P), `stages_days_murcia` de alcachofa 34/34/211/25 (304 días, derivado B; no modela triturado) y `eurostat_hicp_es.csv` (1999–2025, EUR-HICP). La referencia compuesta F56-T11+CARM-ALC se valida por componentes. La conversión final a euros de 2025 pertenece al motor; estas tablas conservan sus bases nativas.

Se sustituyen los nombres antiguos por `frost_t0`, `frost_t100`, `heat_t0`, `heat_t100`, unidad `degC`. Todos siguen vacíos/P: las notas existentes no acreditan pares de inicio/100 % de daño aplicables a Tmin/Tmax diaria. `frost_window` y `heat_window` son opcionales: `ini`, `dev`, `mid`, `late` unidos por `+`, o `all`; vacío significa sin ventana documentada, no evidencia para asumir una. REQUIRED y manifest enumeran huecos obligatorios. No se deduce letalidad de temperaturas óptimas, germinación o conservación poscosecha.

`cost_candidates.csv` contiene proxies B de coste completo ECREA: haba seca = grupo guisantes/habas regadío nacional 2020 (1095.8 EUR/ha); cebada nacional 2021 secano (631.5) y regadío (1165.2), en filas distintas. Son candidatos separados: no entran en `crop_params.csv` ni sustituyen costes canónicos porque el motor 8b3a214 impone base 2018. El consumidor debe elegir régimen y convertir desde `price_base_year` antes de activar cada proxy. Incluyen cosecha y costes de oportunidad; nunca son costes de cubierta. Veza cubierta sigue vacía/P al no disponer de semilla+siembra desglosadas y verificadas.
