# Fuentes revisadas y huecos pendientes

## Familia botánica

Completadas las ocho familias. Seis se verificaron en la tabla de familias del manual de UC Cooperative Extension (página impresa 13 / página PDF 12, índice desde cero). Limón y veza se contrastaron con FAO Ecocrop. En veza se normaliza Leguminosae a Fabaceae y se explicita la especie asumida `Vicia sativa`; no implica que cualquier veza tenga idénticos parámetros agronómicos. Los hechos taxonómicos se atribuyen; no se copian las tablas ni el contenido editorial de esas publicaciones.

## Costes de haba y veza

Descargado el PDF completo y revisadas las tablas relevantes mediante extracción de texto de MAPA **ECREA 2.0 Cultivos proteaginosos y forrajeros 2020**, publicación febrero 2022:

https://www.mapa.gob.es/dam/mapa/contenido/ministerio/servicios/servicios-de-informacion/analisis-y-prospectiva/ecrea/estudios-de-costes-explotaciones-agricolas/2020/cultivos_proteaginosos_y_forrajeros.pdf

La tabla nacional agrupa **guisantes y habas**; otra tabla agrupa **lentejas, garbanzos y vezas**. No son observaciones específicas de haba ni costes de veza como cubierta sin cosecha. Por ello no se trasladan como costes `sourced` de nuestros cultivos. El documento puede servir para un escenario proxy explícito, previa decisión del equipo; no cierra los huecos por sí solo. Cebada sigue pendiente de lectura de su estudio específico.

El acceso se comprobó sin desactivar TLS, usando el certificado público FNMT G2R compartido por Enrique. El PDF (28 MB) no se añade a Git; el repositorio conserva la URL y el resultado de revisión.

## Resto de huecos

- `legal_group`: solicitado a Gonzalo, responsable de las reglas legales; sin asignación por inferencia.
- `frost_threshold` / `heat_threshold`: no se codifica un único número sin cultivar, fase sensible y duración de exposición. La Tmin observada de TP91 es una entrada meteorológica, no un umbral de daño del cultivo.
- `n_need` / `n_credit`: requieren condiciones de cultivo y una fuente agronómica; permanecen vacíos/P.
- Profundidad de raíces y agotamiento: ya incorporados desde Enrique, revisión `6cd6d8e`, como `zr_min`, `zr_max`, `p_depletion`. Se elimina el nombre alternativo `root_depth`.
- Salinidad de alcachofa, sustitutos y parámetros secundarios: se conservan tal como vienen, con su confianza y estado.
- Derechos de reutilización: los textos de copyright del registro de Enrique no se convierten en permisos abiertos. Revisión pública pendiente.

El motor debe detectar vacíos antes de puntuar; no debe emitir resultados completos aparentando que estos datos están verificados.
