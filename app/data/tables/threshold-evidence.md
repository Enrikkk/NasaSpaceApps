# Evidencia térmica T-021 — investigación primaria, 2026-11-14

Entrega incremental 1. Las notas históricas son índice, no validación. Hechos resumidos en palabras propias; no se redistribuyen artículos, tablas editoriales ni imágenes. Ninguna observación se activa automáticamente como curva de pérdida diaria. Las cuatro columnas canónicas permanecen P hasta acordar una parametrización que respete órgano, duración y métrica.

## Tres cultivos revisados primero

**Limón — UC ANR 8100, p.2, tabla 2 y nota**, [publicación de extensión](https://class.ucanr.edu/sites/default/files/2025-03/UC%20ANR%20Publication%208100.pdf), leída completa. Limón sin variedad: botones/flores −2.8 °C; fruto <13 mm −1.4 a −0.8; verde >13 mm −2.8 a −1.4; maduro en árbol −3.3 a −0.8. Son temperaturas críticas de daño por órgano, no porcentajes de mortalidad. La medición recomendada es aire con termómetro resguardado, no temperatura del fruto; duración/humedad alteran el límite. La cifra de 30 minutos para cítricos tiernos del texto no se asigna a cada fila de limón. No hay 100% de daño ni validación Fino/Verna en Murcia. Transferibilidad: alerta de exposición con intervalo y órgano, no pérdida de cosecha; `frost_t100` sigue P. Calor pendiente en esta entrega. Copyright UC 2003, todos los derechos reservados; solo síntesis factual atribuida.

**Brócoli — UMass Extension, apartado Growing**, [fuente leída](https://www.umass.edu/agriculture-food-environment/ht/vegetable/fact-sheets/broccoli-summer-heat). Resume ensayo Cornell en Galaxy: >35 °C durante más de cuatro días en iniciación floral produce cabezas deformes. Ventana aproximada de diez días antes de la pequeña cabeza visible; otra publicación UMass 2025 sitúa el inicio ligeramente distinto, por lo que no se identifica automáticamente con toda la fase FAO `mid`. Temperatura de exposición ambiental, no prueba de que un solo Tmax diario produzca igual efecto; no se da porcentaje de cabezas, rendimiento perdido ni 100%. Propuesta: indicador de episodio de calor en fase floral, con duración explícita; sin convertirlo en `heat_t100`. Es extensión institucional que remite al experimento, no nuevo ensayo de Murcia. Frío y artículo original pendientes. No licencia abierta identificada; síntesis propia, sin copiar material.

**Haba — Alharbi et al. 2021, Plants 10:1925**, [artículo original](https://www.mdpi.com/2223-7747/10/9/1925), §§2.2–2.3.2, 3.4.1. Dirab, 16 genotipos (incluye Giza Blanka): helada de aire −4.19 °C; abortaron todas las flores etiquetadas del grupo expuesto. No midieron rendimiento en Dirab; plantas sobrevivieron. Es 100% de ese grupo floral, no 100% de cosecha. Duración de esa helada no especificada allí; las fechas 4/5 febrero difieren entre secciones. Narrabri 2014 tuvo mínimo −3.9 °C y ocho horas de congelación: daño en tallos/vainas, escala visual, sin porcentaje directamente convertible. Propuesta: evidencia por órgano/episodio y recuperación, nunca `frost_t100=-4.19` de cultivo entero. Australia/Arabia no calibran automáticamente haba murciana. Artículo abierto; verificar licencia exacta antes de reproducir contenido.

**Haba calor — Bishop et al. 2016**, [original DOI 10.1111/jac.12172](https://onlinelibrary.wiley.com/doi/full/10.1111/jac.12172), Methods y Abstract, leído: Wizard, maceta, cinco días con 18/10, 22/14, 26/18, 30/22, 34/26 °C día/noche, fotoperiodo 16 h, aire medido en cámara. Floración/botón verde sensible; t50 aproximado 28 °C para rendimiento de flores preexistentes y 32 °C para germinación del polen. Son ajustes al 50%, no letalidad total; compensación de rendimiento en otros nudos. No trasladar a Tmax de un día ni a todos los cultivares; propuesta de modelo de exposición de cinco días y respuesta parcial, no rampa hasta 100%. Acceso abierto declarado; licencia concreta pendiente, sin reproducción editorial.

## Matriz inicial de búsqueda (los ocho)

| Cultivo | Frío | Calor | Motivo de no activar todavía |
|---|---|---|---|
| lechuga | ECOCROP 1313 leído: rest −1 / early growth 0 °C; contradice los −6 °C de notas previas | UC IPM y estudios específicos en revisión | ECOCROP no da duración, porcentaje u órgano; no aceptar antiguo −6 sin fuente |
| brocoli | búsqueda específica pendiente | episodio Galaxy descrito arriba | duración y daño de calidad, falta curva porcentual |
| melon | búsqueda específica en curso | ensayo Piel de Sapo 1988 localizado, pendiente lectura | polen in vitro/excised no es cosecha ni Tmax diario |
| alcachofa | ensayo UMH Orihuela 2023 localizado, acceso MDPI 429, pendiente alternativa | búsqueda específica en curso | no confundir Cynara con tubérculo Helianthus ni poscosecha |
| haba | campo −4.19 / −3.9 °C, arriba | cámara cinco días, arriba | daño de órgano y compensación; ninguna pérdida total de cultivo demostrada |
| cebada | fuentes de fase reproductiva localizadas, pendiente original | ensayo llenado de grano localizado, pendiente lectura | aire del dosel y estación no intercambiables |
| veza | ECOCROP 238003 leído: −1 °C rest/early | búsqueda de estrés específica en curso | Vicia sativa asumida; faltan exposición, % y efecto en biomasa de cubierta |
| limon | UC 8100 tabla 2 revisada | búsqueda específica en curso | intervalos por órgano sin % ni duración tabulada |

ECOCROP: [lechuga](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1313), [veza](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=238003). Los límites óptimos/absolutos de requerimiento térmico son idoneidad, no daño observado ni `heat_t100`.

## Propuesta al motor (pendiente Enrique)

Separar `observación térmica` de `parámetro de pérdida`: guardar temperatura, variable/órgano, etapa, duración y resultado/porcentaje con denominador. Admitir alertas por episodio o un punto de daño parcial sin obligar a inventar t100. Una alerta basada solo en extremos diarios es una aproximación declarada; horas bajo umbral requieren datos horarios. No acumular cada día como pérdidas independientes si el estudio midió un episodio completo. La correspondencia fenología experimental → ini/dev/mid/late debe ser un supuesto trazable. No se cambia el código de Enrique.
