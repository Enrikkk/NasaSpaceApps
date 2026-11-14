# MAPA anual — handoff T-021 / bus #139

`mapa_prices.csv`: 60 filas, lechuga/melón/alcachofa genéricos nacionales, 2005–2024 inclusive. Mantiene las primeras columnas de `prices.csv` y añade trazabilidad por fila. No sustituye `prices.csv`, no cambia defaults ni genera JSON. Enrique selecciona el proxy compatible en el motor.

- Nominal original: columna **Anual** de `PrePer3`, **EUR/100 kg**. No se calcula una media simple de los meses. `code` vacío: los libros no proporcionan el código Eurostat usado por nuestra otra serie.
- `eur_kg = eur_100kg / 100`; `eur_100kg_real2015 = nominal × 100 / HICP_ES_año`, redondeado a seis decimales, y `eur_kg_real2015 = real2015 / 100`. Estas columnas reales son derivadas, no cifras reales publicadas por MAPA. Fuente del deflactor `EUR-HICP`, índice positivo y finito verificado.
- `conf=B,status=proxy`: uso como precio de un producto específico todavía es un proxy. Lechuga no acredita iceberg/romana; melón no acredita piel de sapo/galia. No se convierte €/pieza a €/kg ni se afirma precio de Murcia.
- Valores nominales con dos decimales: se respeta el formato Excel `numFmtId=2` (`0.00`). El texto numérico XML original se conserva en `source_raw_value`; evita presentar residuos binarios como precisión publicada.
- `mapa_inputs.json` fija URL y fecha de descarga (2026-11-14, Europe/Madrid; no se registró hora exacta). `mapa_manifest.json` conserva SHA-256 de cada XLSX, fechas originales del libro, hoja/notas, los quince solapamientos y la elección. Los nombres de archivo no determinan el año real de cobertura.
- Selección: modificación original del libro más reciente gana en años solapados. Libros 2005, 2015, 2020 y 2024, modificados respectivamente 2017-07-17, 2024-05-17, 2026-04-28 y 2026-10-27. No se promedian revisiones. La extracción requiere una cifra válida para cada cultivo/año; ningún hueco se rellena con cero.
- Se excluyen años posteriores a 2024, incluido 2026 parcial. Se preserva la nota original sobre provisionalidad del último año, sin extenderla automáticamente a nuestros veinte años.
- Nota fuente hortícolas: precio a granel sobre almacén comprador. No demuestra quién paga la recolección ni qué costes cubre; esa compatibilidad económica queda pendiente del motor. Son precios nacionales, no independientes de las series que MAPA remite a Eurostat/FAOSTAT.

## Procedencia, permisos y TLS

Fuente: Ministerio de Agricultura, Pesca y Alimentación, Índices y Precios Percibidos Agrarios, [página del conjunto](https://www.mapa.gob.es/es/estadistica/temas/estadisticas-agrarias/economia/precios-percibidos-pagados/precios-percibidos-por-los-agricultores-y-ganaderos). Las cuatro URLs exactas figuran en el catálogo y el manifiesto; IDs `MAPA-PER-2005`, `MAPA-PER-2015`, `MAPA-PER-2020`, `MAPA-PER-2024` en `sources.csv`.

Se leyó el [aviso legal primario](https://www.mapa.gob.es/es/atencion-al-ciudadano/aviso-legal) descargado por TLS el 2026-11-14: permite reutilizar citando la fuente, exceptúa derechos de terceros y exige conservar fechas de actualización y condiciones de reutilización. Reutilización conforme a Ley 37/2007, **no licencia CC ni SPDX inventado**. No se emplean logos ni material editorial. Se conserva el hash del HTML leído y las condiciones resumidas, sin redistribuir la página completa.

Descargas con `curl --fail --location --cacert /tmp/t021-mapa-fnmt.pem`, verificación activa. El certificado público se obtuvo byte a byte de `origin/t012-motor-nucleo:app/backend/engine/sources/certs/fnmt_g2r_root.pem`; no se desactivó TLS. Los XLSX binarios se mantienen fuera de Git; para reproducir, descargarlos a un directorio con nombres `2005.xlsx`, `2015.xlsx`, `2020.xlsx`, `2024.xlsx` y el aviso como `legal.html`, comprobar hashes del manifiesto y ejecutar:

```sh
python3 app/data/tables/build_mapa_snapshot.py --input /tmp/t021-mapa
python3 app/data/tables/test_mapa_snapshot.py
```

Comprobaciones de lectura de las celdas Anual de 2024: lechuga 31.42, melón 47.57, alcachofa 96.42 EUR/100 kg. No son tres validaciones externas independientes.
