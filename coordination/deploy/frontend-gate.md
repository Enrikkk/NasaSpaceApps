# T-017: gate reutilizable del build de frontend

Propietario: Arturo. Complementa `t017_smoke.py`; no repite el análisis API/motor y no modifica componentes de Jaime.

## Uso sin red

```sh
python3 scripts/t017_frontend_gate.py --dist app/frontend/dist --worker-asset assets/<worker-emitido>.mjs > /tmp/frontend-gate.json
python3 scripts/test_t017_frontend_gate.py
```

Se usa **el nombre real del worker emitido por el build**, no el de un ejemplo. Comprueba index, entradas JS/CSS, existencia de archivos y hashes. El código de salida es 1 si falla cualquier comprobación solicitada. Si no se indica worker, lo deja pendiente: un informe sin errores no implica mapa validado.

## Configuración publicada o preview ya arrancado

```sh
python3 scripts/t017_frontend_gate.py \
  --dist app/frontend/dist \
  --worker-asset assets/<worker-emitido>.mjs \
  --site-url http://127.0.0.1:4173 \
  --api-base https://<api-confirmada> \
  --origin http://127.0.0.1:5173 > /tmp/frontend-gate.json
```

Solo hace GET al worker y a `/health` y OPTIONS a `/analyze`; no envía una parcela ni ejecuta cálculos/despliegues. Detecta el falso 200 HTML del fallback SPA que se observó en `393ef24`, y distingue `localhost` de `127.0.0.1` al comprobar CORS. No requiere dependencias de Python externas.

## Qué no demuestra

`passed` solo describe las comprobaciones ejecutadas. `demo_ready`, `browser_flow_verified` y `publication_authorized` quedan siempre en false. Sigue siendo necesario comprobar en navegador: seleccionar recinto -> consulta API -> estados carga/error/no evaluable -> comparador/prioridades y fallback etiquetado. Tampoco valida fuentes cartográficas remotas, todas las importaciones dinámicas ni el funcionamiento del worker; valida el recurso indicado y su respuesta HTTP.

El gate no instala ni compila nada, no arranca servicios, no lee `.env`, no escribe en el checkout y no cambia CORS. Guardar el informe fuera de Git; sus hashes permiten saber qué candidato se comprobó sin repetir la prueba sobre el mismo build. Si cambian los componentes o el contrato, verificar solo los checks afectados y conservar la referencia del candidato anterior.
