# T-021: tablas de Agrockham

Datos integrados desde `origin/t012-datos-oficiales`, commit `519849b`, preparados por Enrique. No se altera el formato largo original. `source_snapshot/` conserva las entradas y `manifest.json` sus SHA-256 y huecos.

Desde la raíz del repo:

```sh
python3 app/data/tables/build_tables.py --input app/data/tables/source_snapshot --output app/data/tables --revision 519849b
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

La ausencia de un parámetro se representa por celda vacía, `conf=P`, `status=placeholder`; el consumidor debe comprobarla antes de calcular. No rellenar huecos con cero ni usar supuestos como mediciones. Las familias botánicas, grupo legal, profundidad radicular, umbrales de helada/calor y N aún necesitan fuentes o una tabla explícita del motor. T-019 es de Gonzalo.

Alcachofa no es el topinambur (`Helianthus tuberosus`) de FAO-29. Veza se plantea como cubierta: un coste de veza forrajera cosechada no es automáticamente un coste de cubierta. No se añade el precio supuesto de alcachofa (~60 EUR/100 kg): no es una observación Eurostat.

Precios nacionales anuales no son precios de la parcela. No mezclar directamente precios reales base 2015 y costes nominales 2018: Enrique hará la armonización monetaria con HICP antes de calcular márgenes.

Costes de haba seca, cebada y veza: permanecen vacíos. Candidatos oficiales para revisión: MAPA ECREA 2021 Cereales y ECREA 2020 Cultivos proteaginosos y forrajeros. Localizados, pero PDF no leído por fallo TLS; no se incorporan cifras de resultados de buscador. Los valores históricos de IMIDA, parámetros FAO y secundarios tienen licencia pendiente de verificación; su presencia en la tabla no acredita permiso de redistribución pública. Revisar antes de publicar la demo y declarar en `submission/data-citations.md`.

No se incorpora SIAM aquí: Enrique asume serie histórica y colector completo (bus #49). El borrador local de Arturo no se integra para evitar duplicación.
