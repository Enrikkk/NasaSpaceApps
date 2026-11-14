# Presentación de Agrockham (1:30, 6 diapositivas)

`agrockham-presentacion.pptx` va justo después del vídeo de apertura. Abre con la idea con la que acaba el vídeo («Así nace Agrockham») y cierra con «Haciendo fácil lo difícil».

El guion de cada diapositiva, con sus tiempos, está en las **notas del orador**. Son unas 215 palabras, unos 1:26 a ritmo normal.

| # | Tiempo | Diapositiva | Visual |
|---|---|---|---|
| 1 | 0:00–0:06 | Portada: «Qué sembrar, cuándo y con qué riesgo» | Globo de la app y logo |
| 2 | 0:06–0:23 | Todas las parcelas de España, en un mapa | **GIF 1**: zoom del globo a la parcela |
| 3 | 0:23–0:43 | Lo que sabemos de cada parcela | Ficha real de la app, las seis fuentes de datos y el aviso «~40 %» de la lluvia |
| 4 | 0:43–0:55 | 20 años de precios y clima, año a año | Flujo en 4 pasos |
| 5 | 0:55–1:14 | Tú decides qué te importa | **GIF 2**: mover las prioridades y ver cómo cambia la rotación |
| 6 | 1:14–1:30 | Haciendo fácil lo difícil | «Ya funciona» frente a «Lo siguiente» |

## Los dos GIF

Ahora mismo hay **capturas reales de la app**: las capturamos el 14 de noviembre de 2026 de la versión desplegada (v9). Si no da tiempo a grabar los GIF, la presentación funciona igual con ellas.

| GIF | Qué grabar |
|---|---|
| **GIF 1** (diapositiva 2) | Inicio → «Ir a mis parcelas» → el globo hace zoom → clic en un recinto → se abre la ficha |
| **GIF 2** (diapositiva 5) | Con la ficha abierta, abrir FILTROS → mover «Ahorro de agua» o «Beneficio» → cambia «La que mejor encaja con tus prioridades» |

Recomendaciones para grabarlos:

- **Programa:** ScreenToGif (Windows), Kap (Mac) o Peek (Linux).
- **Duración y fluidez:** de 6 a 8 s, a 15 fps, en bucle.
- **Tamaño:** que el fichero pese menos de 10 MB.
- **Encuadre:** 16:9. Con otra proporción la imagen se deforma.
- **Créditos:** que se lean los créditos de la esquina del mapa (FEGA, IGN y NASA GIBS).

Para cambiar la captura por el GIF, haz clic derecho en la imagen → **Cambiar imagen → Desde un archivo**. Así conserva el tamaño y la posición. PowerPoint reproduce los GIF solo en el modo presentación.

## Lo que el guion NO dice, a propósito, porque todavía no está hecho

- **Registro de parcelas (añadir o quitar con un clic):** el botón «Ir a mis parcelas» solo hace zoom. Por eso va en «Lo siguiente».
- **Capacidad de inversión:** no está en el modelo. Las prioridades que hay son beneficio, agua, suelo y riesgo. También va en «Lo siguiente».
- **Riesgo por lluvias torrenciales:** el riesgo que calcula el modelo es el de un mal año (por clima y precio) y los días de helada y de calor.
- **Parcelas de la NASA:** las parcelas vienen del SIGPAC (FEGA). De la NASA salen el clima (POWER), la lluvia (IMERG) y la imagen del globo (GIBS).
- **Análisis en toda España:** en el mapa se ven los recintos de toda España, pero el análisis completo solo cubre 170.265 recintos de 7 municipios del Campo de Cartagena.

## Regenerarla

`build_deck.js` construye la presentación con pptxgenjs. Necesita los paquetes `pptxgenjs`, `react`, `react-dom`, `react-icons` y `sharp` en `NODE_PATH`, y el `apply_theme.js` del skill de pptx en `PPTX_SKILL_DIR`.

## Recursos y licencias (para el formulario)

| Recurso | Origen y licencia |
|---|---|
| Logo y paleta | `brand/` del equipo. ⚠️ La licencia de la fuente Brunson, con la que está dibujado el logo, sigue pendiente: ver `brand/README.md` |
| Texto | Inter (SIL OFL 1.1). Si el portátil de la presentación no tiene Inter, PowerPoint pone otra fuente. Instálala antes (es gratuita). |
| Iconos | Font Awesome Free vía react-icons (iconos CC BY 4.0) |
| Capturas | De nuestra app. Los mapas que se ven son: Blue Marble (NASA GIBS / NASA Earth Observatory), ortofoto PNOA y mapa base del IGN (CC BY 4.0 scne.es), y recintos SIGPAC © FEGA (CC BY 4.0). Los créditos están en cada diapositiva. |
| Uso de IA | Diseño, maquetación y redacción del guion con Claude (Anthropic), a partir del guion del equipo. Hay que declararlo en `submission/ai-use.md`. |

No se usan logos de la NASA ni nada que sugiera que la NASA respalda el proyecto.
