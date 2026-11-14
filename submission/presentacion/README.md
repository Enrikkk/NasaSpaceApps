# Presentación de Agrockham

`agrockham-presentacion.pptx`: 6 diapositivas, unos 1:30. Va después del vídeo de apertura. El guion está en [guion.md](guion.md) y también en las notas de cada diapositiva.

## GIF

Las diapositivas 2 y 5 llevan capturas de la app (versión desplegada, 14 de noviembre de 2026). Se pueden sustituir por GIF:

- **Diapositiva 2:** «Ir a mis parcelas» → zoom del globo → clic en un recinto → se abre la ficha.
- **Diapositiva 5:** abrir FILTROS → mover «Ahorro de agua» o «Beneficio» → cambia la rotación recomendada.

Grabadlos en 16:9, de 6 a 8 s y a 15 fps, de modo que pesen menos de 10 MB. Para sustituir la captura: clic derecho en la imagen → Cambiar imagen → Desde un archivo.

## Fuera del guion (aún no existe en la app)

- Registro de parcelas
- Capacidad de inversión
- Riesgo por lluvias torrenciales
- Análisis completo fuera del Campo de Cartagena

En la última diapositiva, las dos primeras aparecen como «Lo siguiente».

## Regenerar

`build_deck.js` (pptxgenjs). Necesita `pptxgenjs` en `NODE_PATH` y el `apply_theme.js` del skill de pptx en `PPTX_SKILL_DIR`.

## Recursos y licencias

- **Logo y paleta:** `brand/` del equipo. La licencia de la fuente Brunson del logo está pendiente (ver `brand/README.md`).
- **Texto:** Inter (SIL OFL 1.1). Hay que instalarla en el portátil de la presentación.
- **Gráfico de precios:** Eurostat `apri_ap_crpouta`, precio de venta en España, 2005-2024 (copia en `app/data/tables/source_snapshot/eurostat_prices_es.csv`, rama t020-jaime).
- **Capturas:** de nuestra app. Créditos de los mapas: Blue Marble (NASA GIBS / NASA Earth Observatory), IGN (CC BY 4.0 scne.es) y SIGPAC © FEGA (CC BY 4.0).
- **IA:** maquetación y redacción hechas con Claude (Anthropic) a partir del guion del equipo. Hay que declararlo en `submission/ai-use.md`.
