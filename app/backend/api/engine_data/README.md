# engine_data: contrato de montaje del JSON del motor

La API NO lleva el codigo del motor (enrique): solo lee su JSON publicado y lo convierte con `app/data/contract/adapt_enrique.py`.

- Para activar el motor en la imagen/arranque local, copia el JSON publicado (`app/data/torre-pacheco.json` o `torre-pacheco.abierto.json`, de la rama de enrique cuando este en main) a `app/backend/api/engine_data/engine.json` ANTES de construir.
- Si existe, la API lo usa por defecto (`ENGINE_JSON` explicito manda). Si no existe, usa el borrador simulado (`DraftEngine`).
- `engine.json` esta ignorado por git a proposito: puede incluir precios CARM (D-010, permiso pendiente) y no debe subirse al repo por accidente.
- El mismo mecanismo vale para montar un volumen en `/app/app/backend/api/engine_data` o fijar `ENGINE_JSON=/ruta`.
- `escenarios_meta.alineados` viene del JSON (false hasta que enrique lo arregle); la UI debe respetarlo.
