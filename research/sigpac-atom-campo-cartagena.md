# SIGPAC: ATOM oficial del FEGA para el Campo de Cartagena (Plan B), condiciones de uso y borrador de correo

Investigado el 14-11-2026 para gonzalo (backend, D-009). Complementa, sin repetirla, `research/sigpac-viability-2026-11-14.md`
(rama `origin/research-sigpac-viability`, Arturo). Solo lectura: no se ha editado nada más del repo ni enviado ningún correo.

## Resumen ejecutivo

1. **El ATOM oficial existe, es público, sin login ni clave, y funciona.** Índice: https://www.fega.gob.es/atom/es.fega.sigpac.xml
   (feed INSPIRE; `<updated>` 2026-01-26). Los ZIP por municipio cuelgan de
   `https://www.fega.gob.es/atom/2026/rec_2026/30%20-%20MURCIA/` (campaña 2026, validez 2025-12-15, publicados el 2026-02-10).
2. **Los códigos de municipio del ATOM NO son los del INE en tres casos del encargo.** Los ficheros usan el código SIGPAC
   (`30` + municipio SIGPAC de 3 cifras). Comprobado con `recinfobypoint` en un punto de cada municipio y con el diccionario
   oficial del INE 2026: Fuente Álamo es INE 30021 (30019 es Cieza), La Unión es INE 30041 (30032 es Pliego), y Los Alcázares es
   INE 30902 pero su fichero ATOM es **30045**. Ver tabla.
3. **Condiciones: la prohibición de 2023 parece superada por documentos oficiales posteriores.** Los "Términos de uso de la
   información de alto valor del SIGC" (PDF del FEGA, metadatos de 11-02-2026) citan expresamente la OGC API de SIGPAC como
   servicio gratuito y dicen que no hace falta autorización. Falta confirmar por escrito el servicio `recinfobypoint` y el límite de
   peticiones (no figuran). Recomendación: enviar el correo (borrador abajo) y, mientras, construir el pipeline ATOM -> GeoJSON/PMTiles
   como respaldo de demo.
4. **Campo de Cartagena (sin Murcia): unos 160-170 mil recintos, ~75 MB de ZIP GPKG, ~130 MB descomprimido, ~145 MB de GeoJSON
   (~30 MB gzip).** Con el municipio de Murcia entero serían ~360 mil recintos y ~167 MB de ZIP. Estimaciones, no medidas (ver
   huecos).

## 1. Servicio ATOM del FEGA: estructura y comprobaciones

Pruebas hechas con `curl` (HEAD/GET), sin autenticación, el 14-11-2026 sobre las 15:20 hora local.

| Qué | URL | Observado |
|---|---|---|
| Feed raíz del servicio | https://www.fega.gob.es/atom/es.fega.sigpac.xml | 200. Entradas: Recintos 2026, Elementos del paisaje 2026, Recintos 2025, Elementos 2025, Cultivo declarado SIGC 2025 |
| Feed de recintos 2026 | https://www.fega.gob.es/atom/es.fega.sigpac.rec.2026.xml | 200. "Descargas ... con formatos GeoPackage y Shapefile comprimidos como ZIP". CRS EPSG:4258 (ETRS89) |
| Descripción OpenSearch | https://www.fega.gob.es/atom/osd.xml | 200 |
| Directorio de ZIP, Murcia, recintos 2026 | https://www.fega.gob.es/atom/2026/rec_2026/30%20-%20MURCIA/ | 200, listado Apache (45 municipios, `30001` a `30045`, cada uno en `_gpkg.zip` y `_shp.zip`) |
| Idem recintos 2025 | https://www.fega.gob.es/atom/2025/rec_2025/30%20-%20MURCIA/ | 200 (validez 2025-01-10) |
| Cultivo declarado 2025 | https://www.fega.gob.es/atom/2025/cd_2025/30%20-%20MURCIA/ | 200 (validez 2025-01-10; solo campaña anterior) |
| Tablas de códigos 2026 | https://www.fega.gob.es/atom/2026/sigpac_codes_2026.zip | 24 KB, descargado y abierto: `cod_usosigpac.csv`, `cod_producto.csv`, `cod_region_2023.csv`, `cod_incidencia.csv`, etc. |
| Página legacy del servicio | https://www.fega.gob.es/orig/ | 200. Pide aceptar condiciones en el navegador; dice "actualización anual" y "Se recomienda realizar la descarga fuera del horario comprendido entre las 8:00 y las 18:00" |

Notas operativas:

- Los ZIP se sirven con `Content-Type: application/zip` y **sin cabecera `Access-Control-Allow-Origin`** (comprobado con HEAD sobre
  `.../30016_rec_2026_20251215_gpkg.zip`): sirven para un pipeline en build, no para `fetch` desde el navegador. En cambio la OGC
  API de hubcloud sí devuelve `access-control-allow-origin: *` (https://sigpac-hubcloud.es/ogcapi/collections/recintos/items?f=json&limit=1&bbox=-0.99,37.73,-0.98,37.74)
  y no devolvió ninguna cabecera de límite de peticiones (`RateLimit`/`Retry-After`).
- La descarga de prueba (17 MB en total) se hizo dentro de la franja 8:00-18:00 que el FEGA desaconseja; para descargas mayores,
  hacerlo de noche.
- Convención de nombre: `{provincia 2 cifras}{municipio SIGPAC 3 cifras}_rec_{campaña}_{fecha validez}_{gpkg|shp}.zip`
  (https://sigpac-hubcloud.es/html/sdsigpac/descServicio.html describe el patrón; el servicio de descargas provincial de hubcloud es
  otro servicio distinto del ATOM).

## 2. Municipios del Campo de Cartagena: códigos y ficheros (recintos 2026, GPKG)

Base de URL: `https://www.fega.gob.es/atom/2026/rec_2026/30%20-%20MURCIA/` + nombre de fichero.
Códigos INE verificados contra https://www.ine.es/daco/daco42/codmun/diccionario26.xlsx ("a 1 de enero de 2026").
Código SIGPAC verificado con https://sigpac-hubcloud.es/servicioconsultassigpac/query/recinfobypoint/4258/{lon}/{lat}.json
sobre un punto de cada municipio (campo `municipio`).

| Municipio | INE (encargo -> real) | Municipio SIGPAC | Fichero ATOM GPKG | Tamaño ZIP | Recintos | Actualizado |
|---|---|---|---|---|---|---|
| Cartagena | 30016 -> **30016** | 16 | `30016_rec_2026_20251215_gpkg.zip` | 30 942 148 B (30 MB), HEAD, no descargado (>20 MB) | no medido (est. ~68 k) | Last-Modified 2026-02-10 |
| Torre-Pacheco | 30037 -> **30037** | 37 | `30037_rec_2026_20251215_gpkg.zip` | 13 586 044 B, descargado | **29 859** | 2026-02-10 |
| Fuente Álamo de Murcia | 30019 -> **30021** | 21 | `30021_rec_2026_20251215_gpkg.zip` | 21 607 054 B, HEAD, no descargado (>20 MB) | no medido (est. ~47 k) | 2026-02-10 |
| Los Alcázares | 30902 -> **30902** (INE) | **45** | `30045_rec_2026_20251215_gpkg.zip` | 825 344 B, descargado | **1 815** | 2026-02-10 |
| San Javier | 30035 -> **30035** | 35 | `30035_rec_2026_20251215_gpkg.zip` | ~5,6 MB (listado Apache, no descargado) | no medido (est. ~12 k) | 2026-02-10 |
| San Pedro del Pinatar | 30036 -> **30036** | 36 | `30036_rec_2026_20251215_gpkg.zip` | 1 263 576 B, descargado | **2 925** | 2026-02-10 |
| La Unión | 30032 -> **30041** | 41 | `30041_rec_2026_20251215_gpkg.zip` | 1 569 089 B, descargado | **2 515** | 2026-02-10 |
| Murcia (parcial: pedanías del sur) | 30030 -> **30030** | 30 | `30030_rec_2026_20251215_gpkg.zip` | 92 136 925 B (92 MB), HEAD, no descargado | no medido (est. ~200 k en todo el municipio) | 2026-02-10 |

Fuentes de la tabla: listado https://www.fega.gob.es/atom/2026/rec_2026/30%20-%20MURCIA/ (tamaños y fechas), HEAD de los ficheros
citados, apertura local de los GPKG descargados, diccionario INE y consultas `recinfobypoint`.

Otros datos para la tabla:

- Variante Shapefile de cada municipio (mismo nombre con `_shp.zip`), ~7 % más pequeña (Cartagena 27 MB, Torre-Pacheco 12 MB). Se
  recomienda GPKG (nombres de campo completos, tipos nativos).
- Los Alcázares (INE 30902) y Santomera (INE 30901) no tienen código 30xxx en INE, pero el SIGPAC los numera dentro de 1-45. Solo se
  ha verificado Los Alcázares = 45.
- Campaña 2025 equivalente: `.../atom/2025/rec_2025/30%20-%20MURCIA/{codigo}_rec_2025_20250110_gpkg.zip` (mismos tamaños casi idénticos;
  Cartagena 29 MB). Útil para detectar cambios de recinto entre campañas.

### Atributos del GPKG (comprobado abriendo los 4 GPKG descargados)

Una capa `recinto`, geometría `Polygon` en EPSG:4258, campos:

| Campo | Contenido observado |
|---|---|
| `provincia`, `municipio`, `agregado`, `zona`, `poligono`, `parcela`, `recinto` | Referencia SIGPAC completa (por ejemplo 30/37/0/0/18/426/1) |
| `dn_surface` | Superficie **en m²** (40 867,86 para 18/426/1; la REST da 4,0868 ha) |
| `pendiente_media` | **Entero en tanto por mil** (8 para 18/426/1; la REST da 0,8 %). Dividir entre 10 para obtener % |
| `altitud` | Metros (53 para 18/426/1, igual que la REST) |
| `coef_regadio` | Entero 0-100, puede ser nulo (100 para 18/426/1) |
| `uso_sigpac` | Código de 2 letras (TA, CI, IV, IM, ZU, MT, FO, AG, CA, ...) decodificable con `cod_usosigpac.csv` |
| `incidencias` | Lista de códigos de incidencia, texto (`cod_incidencia.csv`) |
| `region` | Código de región de producción (`cod_region_2023.csv`) |
| `csp`, `dn_oid` | Identificadores internos; `csp` nulo en todas las muestras |

El recinto de demo 30/37/0/0/18/426/1 está en el GPKG de Torre-Pacheco y coincide con la REST (uso TA, regadío 100, altitud 53,
superficie 4,0868 ha, pendiente 0,8 %). **No trae cultivo declarado**: ese vive en `cd_2025` (campaña anterior), un GPKG distinto por
municipio, con otro esquema.

Composición por uso en los municipios medidos (ha, GPKG 2026): Torre-Pacheco 18 960 ha totales, TA 8 822, CI 3 443, IM 1 918,
ZU 1 361, IV 983; con `coef_regadio` > 0 el 64 % de la superficie (12 193 ha) y 11 925 de 29 859 recintos.

## 3. Tamaño estimado del Campo de Cartagena

Medido en los 4 GPKG descargados (37 114 recintos, 17,2 MB de ZIP): ~463 B de ZIP por recinto; GPKG descomprimido ~1,73x el ZIP
(Torre-Pacheco: 23,5 MB); GeoJSON con 6 decimales y 9 propiedades cortas: **~884 B por recinto sin comprimir, ~180 B con gzip**
(Torre-Pacheco: 26,4 MB / 5,5 MB; San Pedro: 2,4 MB / 0,5 MB; se convirtió en el scratchpad solo para medir).

| Conjunto | ZIP GPKG | Recintos (est.) | GPKG | GeoJSON | GeoJSON gzip |
|---|---|---|---|---|---|
| Cartagena + Torre-Pacheco + Fuente Álamo + San Javier + San Pedro + La Unión + Los Alcázares | ~75 MB | ~160-170 mil | ~130 MB | ~145 MB | ~30 MB |
| Anterior + Murcia municipio completo | ~167 MB | ~360 mil | ~290 MB | ~320 MB | ~65 MB |

Son extrapolaciones por bytes/recinto; la densidad real varía (La Unión da 624 B/recinto, el resto ~430-455). El Campo de Cartagena
real es solo la parte sur de Murcia: recortar por bbox tras descargar. Mazarrón (SIGPAC 26, 18 MB ZIP) queda fuera salvo que
se quiera incluir el litoral.

## 4. Condiciones de uso: qué dice el texto oficial

### 4.1 Lo que prohíbe (2023) y lo que lo supera (2024-2026)

- **Respuesta MAPA, 26-06-2023** (https://datos.gob.es/es/catalogo/e05024401-sistema-de-informacion-geografica-de-parcelas-agricolas-sigpac,
  releída del HTML): "No está permitido el acceso desde código por parte de terceros a la información de la base de datos SIGPAC."
  Remite al visor, a la descarga municipal (ATOM) y al WMS. Hay otra respuesta MAPA del 28-05-2025 en la misma ficha que vuelve a
  remitir al ATOM sin repetir esa frase; tampoco menciona la OGC API.
- **Términos de uso de la información de alto valor del SIGC (FEGA, S.G. de Ayudas Directas, PDF de febrero de 2026)**:
  https://www.fega.gob.es/orig/pdfs/Terminos_de_uso_de_informacion_de_alto_valor_del_SIGC.pdf (leído íntegro en local).
  - Declara datos de alto valor (HVD, Reglamento UE 2023/138) las capas RECINTOS, ELEMENTOS DEL PAISAJE y CULTIVO DECLARADO (líneas de
    declaración), "datos de la Campaña en curso y datos de la Campaña previa".
  - Licencia CC BY 4.0, con uso comercial o no comercial y obras derivadas permitidos.
  - Cita literal clave: "No se requiere ningún requisito formal o autorización expresa por parte del FEGA para el acceso, descarga o copia".
  - Lista los servicios por los que el FEGA proporciona esos datos de forma gratuita: "Visor Sigpac, Servicio Atom y otros
    servicios en la nube, como el MVT de Sigpac, WMS de Sigpac, OGC API de Sigpac, Servicio Salidas gráficas de Sigpac y Servicio de
    descargas Sigpac a nivel provincia". **El servicio de consultas REST (`recinfobypoint`) no figura nombrado** (el "como" sugiere
    lista abierta, pero no lo dice).
  - Atribución obligatoria: "Fuente de los datos: FONDO ESPAÑOL DE GARANTÍA AGRARIA O.A." visible en toda copia redistribuida, indicando
    si hubo cambios y la fecha de extracción/actualización; prohibido sugerir respaldo o patrocinio del FEGA (no usar su logo).
  - Exención de garantías y de disponibilidad ("acceso continuo"); el FEGA puede suspender el acceso. Sin límite de peticiones indicado.
  - Contacto oficial para preguntas sobre estos datos: sg.ayudasdirectas@fega.es.
- **Acuerdo de la Mesa del SGC, firmado 01-08-2024** (https://www.fega.gob.es/orig/pdfs/240801_MESA_SGC_Acuerdo_Distribucion_Datos_SIGC_fdo.pdf,
  leído en local): para capas HVD exige distribución "mediante interfaces de programación de aplicaciones (API), como servicios OGCs,
  o servicios de descarga de acceso directo ... que permitan descargas masivas", y que la administración "designará un punto de
  contacto para las preguntas y cuestiones relacionadas con las API". Es el soporte normativo de que la OGC API es un canal previsto.

### 4.2 Otros textos oficiales

| Fuente | Dice | URL |
|---|---|---|
| Cabecera `<rights>` del propio feed ATOM | "libre y gratuito en cualquier caso, siempre que se mencione al ... (FEGA) como autor y propietario de la información" | https://www.fega.gob.es/atom/es.fega.sigpac.xml |
| Página del servicio hubcloud | Datos "publican bajo los términos de la licencia pública" CC BY 4.0; sin aviso legal propio, sin contacto, sin límites | https://sigpac-hubcloud.es/ |
| Descripción OGC API | Cinco capas, JSON "para sistemas externos", CC BY 4.0, límite por página y de peticiones **no especificados** | https://sigpac-hubcloud.es/html/ogc-api/descServicio.html |
| Descripción servicio de descargas (provincial) | Gratuito, CC BY 4.0, "Al acceder al servicio se dan por aceptadas las condiciones de uso" | https://sigpac-hubcloud.es/html/sdsigpac/descServicio.html |
| Ficha datos.gob.es del dataset de recintos | Licencia `CC_BY_4_0`; contacto FEGA S.G. Ayudas Directas; servicios ATOM, OGC API y WMS enlazados | https://datos.gob.es/es/catalogo/e0dat0002-recintos-del-sistema-de-informacion-geografica-de-parcelas-agricolas-sigpac-espana |
| Página SIGPAC del FEGA | Enlaza los Términos de uso y el Acuerdo; para capas no HVD aplica la licencia propia del Acuerdo (Anexo I) | https://www.fega.gob.es/es/pepac-2023-2027/sistemas-gestion-y-control/sigpac |
| Licencia | CC BY 4.0 | https://creativecommons.org/licenses/by/4.0/deed.es |

La "Condiciones de distribución y utilización de datos en capas NO HVD" (Acuerdo 2024) cubre otras capas (por ejemplo parcela); no aplica
a recintos, que son HVD. Una copia del acuerdo alojada en `data.source.coop` (fiboa/es-md) no es fuente oficial y no se ha usado.

### 4.3 Lectura para el equipo (no es asesoría legal)

- Descargar el ATOM y reutilizar los datos con atribución: **claramente permitido** (feed `<rights>`, Términos de uso, CC BY 4.0).
- Usar la OGC API desde código: los Términos 2026 la citan como servicio gratuito y dicen que no hace falta autorización. La respuesta de 2023
  es anterior y no menciona ese servicio, pero ninguna fuente oficial posterior la deroga expresamente. Riesgo bajo, no nulo.
- `recinfobypoint`: sin texto específico. Mismo dominio y mismo régimen de licencia, pero sin confirmación nominal.
- Sin límite de peticiones publicado: seguir con caché, consultas acotadas, paginación de 250 y pocas peticiones concurrentes.

## 5. Recomendación

1. **Enviar el correo del apartado 6** (lo envía un humano del equipo) y guardar la respuesta en `submission/` si llega. No bloquear
   el trabajo por ella.
2. **Sin autorización explícita para el servicio en vivo, o si responden negativamente:** pipeline offline ATOM -> GeoJSON/PMTiles y
   la demo no depende de ninguna API:
   - Build (una vez, de noche): descargar los 7 ZIP del Campo de Cartagena (y Murcia si se quiere el sur de la pedanía), `unzip` en directorio
     limpio, `ogr2ogr -f GeoJSONSeq -t_srs EPSG:4326` (o directamente a MVT con `tippecanoe`) leyendo la capa `recinto`.
   - Transformar propiedades: `dn_surface / 10000` -> ha, `pendiente_media / 10` -> %, mantener `uso_sigpac`, `coef_regadio`, la
     referencia completa y la fecha de extracción (20251215) y campaña (2026). Decodificar uso con `cod_usosigpac.csv`.
   - Recortar por bbox del Campo de Cartagena antes de teselar (descarta casi toda la parte de Murcia).
   - Teselar con `tippecanoe` a un PMTiles por municipio (`-Z10 -z15`, sin simplificar a zoom máximo; `--drop-densest-as-needed` en zooms bajos)
     o uno solo con el bbox completo (decenas de MB, a medir). Servir `.pmtiles` estático por HTTP range (GitHub Pages, Cloudflare R2 o el
     propio backend) y dibujarlo en el globo/mapa; mantener un GeoJSON por municipio para consultas puntuales (point-in-polygon en el backend en lugar de
     `recinfobypoint`).
   - Cultivo declarado: bajar `cd_2025` del ATOM por los mismos municipios (campaña anterior) en lugar de la OGC API.
   - Licencias de `ogr2ogr` (GDAL), `tippecanoe` y `pmtiles` a comprobar y anotar en `submission/` según AGENTS.md §6.
3. **Atribución en la app y en `submission/` (obligatoria en cualquier caso):** "Fuente de los datos: FONDO ESPAÑOL DE GARANTÍA AGRARIA O.A.",
   CC BY 4.0, indicar que los datos se han transformado (unidades, recorte, teselado) y la fecha de extracción. Sin logo ni nombre del FEGA/MAPA que
   sugiera respaldo.
4. **Híbrido recomendado para la demo:** capa de recintos desde PMTiles propio (siempre disponible, sin Wi-Fi), y llamadas
   puntuales a la OGC API/REST solo como enriquecimiento opcional con caché y degradación elegante.

## 6. Borrador de correo (NO ENVIADO)

**Para:** sg.ayudasdirectas@fega.es
(punto de contacto oficial para cuestiones sobre datos de alto valor del SIGC según los Términos de uso del FEGA; la web de contacto del FEGA no ofrece un
buzón específico de SIGPAC, https://www.fega.gob.es/es/contacta. Alternativa si rebotara: unidad-de-apoyo@fega.es, autor declarado en el feed ATOM)
**Asunto:** Consulta sobre uso de la OGC API y del servicio de consulta por punto de SIGPAC en un proyecto educativo de hackathon

Buenos días:

Somos un equipo de cuatro estudiantes de Ingeniería Informática de la Universidad de Murcia que participa en el NASA Space Apps Challenge
(sede de Murcia, 13-15 de noviembre de 2026), un hackathon educativo sin ánimo de lucro. Nuestro proyecto, Agrockham, es una aplicación web que muestra
recintos agrícolas del Campo de Cartagena junto con datos satelitales.

Hemos leído los "Términos de uso de la información de alto valor del SIGC" y el Acuerdo de la Mesa del SGC de 01-08-2024, que indican que no se
requiere autorización expresa para el acceso a los recintos bajo CC BY 4.0. También hemos visto una respuesta del MAPA de 26-06-2023 en datos.gob.es que no
permitía el acceso desde código de terceros, por lo que preferimos confirmar la situación actual antes de depender de ello. Nuestra consulta es:

1. ¿Está permitido que nuestra aplicación web use, desde código, la OGC API (https://sigpac-hubcloud.es/ogcapi, colecciones de recintos y cultivo declarado) y el servicio de
   consulta por punto (`recinfobypoint`, https://sigpac-hubcloud.es/servicioconsultassigpac/) con fines educativos y no comerciales? ¿Quedan cubiertos por los Términos de uso de alto valor?
2. ¿Existe un límite de peticiones recomendado (por segundo, minuto o día) o una franja horaria que debamos evitar? Nuestro plan es usar caché y consultas acotadas por bbox, con
   páginas de 250 elementos.
3. ¿Cómo prefieren que citemos la fuente? Pensamos usar "Fuente de los datos: FONDO ESPAÑOL DE GARANTÍA AGRARIA O.A.", licencia CC BY 4.0, indicando las transformaciones realizadas y
   la fecha de extracción, sin sugerir respaldo del FEGA.

Como alternativa, como respaldo ya descargamos los recintos de los municipios del Campo de Cartagena desde el servicio ATOM, así que si el uso de la API en vivo no fuera
adecuado, nos limitaríamos a eso.

Muchas gracias por su tiempo y por mantener estos datos abiertos.

Un saludo,
[Nombre y apellidos]
[Universidad de Murcia, equipo Agrockham, NASA Space Apps Challenge Murcia 2026]
[correo de contacto]

(Revisar antes de enviar: la frase "ya descargamos" solo es cierta cuando el pipeline ATOM esté ejecutado; hoy solo se han descargado 4 municipios pequeños para pruebas en el scratchpad.)

## 7. Huecos NO CONFIRMADOS

- **Número real de recintos y tamaño** de Cartagena, Fuente Álamo, San Javier y Murcia: extrapolados desde 4 municipios (463 B de ZIP por recinto); Cartagena y Fuente Álamo, Murcia (>20 MB)
  no se descargaron por la regla de tamaño.
- **Tamaño final de PMTiles** (no se ha ejecutado `tippecanoe`); las cifras de GeoJSON se midieron solo en Torre-Pacheco y San Pedro.
- **Código SIGPAC de Santomera** (supuesto 44) y mapeo exacto de los 45 ficheros a nombres de municipio: solo se verificaron los 8 pedidos más los resultados de Torre-Pacheco/Los Alcázares/La Unión/San Pedro con los GPKG.
- **Si `recinfobypoint` (servicio de consultas REST) está cubierto** por los Términos de uso HVD: no se nombra. Pendiente de respuesta del FEGA.
- **Límite de peticiones** de la OGC API y del REST: no publicado ni en cabeceras HTTP; no se probó carga.
- **Si la respuesta de 2023 sigue vigente para esos servicios:** ninguna fuente oficial posterior la deroga ni la confirma expresamente; es una inferencia de este informe.
- **Aviso legal MAPA** enlazado desde la ficha datos.gob.es (`http://www.magrama.gob.es/es/atencion-al-ciudadano/aviso-legal.aspx`, enlace antiguo): no se ha abierto.
- **Contenido exacto de los atributos `csp` y `region`:** `csp` siempre nulo en las muestras; `region` descrito solo por el nombre del catálogo `cod_region_2023.csv`.
- **Coincidencia de campaña** entre el GPKG 2026 (validez 15-12-2025) y lo que devuelve hoy la OGC API: no comparado.
- **Campo `pendiente_media` en tanto por mil:** inferido de un único recinto (8 en GPKG frente a 0,8 en REST) y de la documentación MVT citada por Arturo; no hay diccionario oficial del GPKG leído (existe un PDF de especificaciones técnicas enlazado desde https://www.fega.gob.es/orig/, no abierto).
- **Cultivo declarado 2026:** el ATOM solo ofrece la campaña previa (2025); la campaña en curso solo está en la OGC API.
- **Licencias de herramientas** (GDAL, tippecanoe, pmtiles) sin comprobar.
- El correo `sg.ayudasdirectas@fega.es` está en documentos oficiales como punto de contacto de datos de alto valor, pero no se ha verificado que responda a consultas de terceros.
