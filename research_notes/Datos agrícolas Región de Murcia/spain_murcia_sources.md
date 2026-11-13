# Fuentes de datos abiertos españolas y de la Región de Murcia para una herramienta de rotación de cultivos (Field Shift, Space Apps 2026)

Fecha de las pruebas: 13-nov-2026 (~20:05–20:20 UTC). Punto de prueba principal: lat 37.72, lon -0.97. **Ojo: ese punto cae en el término municipal de Cartagena (cód. 30016), no en Torre-Pacheco** (lo dice SIGPAC). Punto secundario: lat 38.47, lon -1.33 → cae en **suelo urbano de Jumilla** (uso SIGPAC `ZU`), conviene elegir otro punto rural para el Altiplano.
Todos los ficheros descargados están en `/private/tmp/claude-501/-Users-jaime-Documents-NasaSpaceApps/324b317c-8037-4e23-a8f2-fde635abe82e/scratchpad/api-tests/spain/`. Ninguno pasa de 7 MB. No se creó ninguna cuenta ni se usó ninguna clave.

Leyenda de veredictos: **KEEP** = usar en la demo; **OPTIONAL** = solo si sobra tiempo o como capa de contexto; **DROP** = no merece la pena en 36 h.

---

## 1. SIGPAC: ¿cómo obtengo el polígono de la parcela (recinto) y su uso en un punto?

### Takeaway
El FEGA tiene un servicio nuevo, abierto y rápido (`sigpac-hubcloud.es`): una llamada GET con lon/lat devuelve en ~0,2 s el recinto con su geometría WKT, superficie, pendiente, altitud, coeficiente de regadío y uso SIGPAC. También hay OGC API Features (GeoJSON por bbox), WMS y descargas ATOM por municipio. **KEEP (pieza central de la demo).** El IMIDA publica además las capas SIGPAC históricas de Murcia 2011–2024 como servicios ArcGIS consultables.

### Cited Findings
- **Consulta por punto (sin clave), probada en vivo**: `curl -sS --compressed --max-time 60 "https://sigpac-hubcloud.es/servicioconsultassigpac/query/recinfobypoint/4258/-0.97/37.72.json"` → HTTP 200, 0,22 s. Respuesta: `{"provincia":30,"municipio":16,"poligono":502,"parcela":142,"recinto":1,"superficie":4.924,"pendiente_media":1,"coef_regadio":0,"incidencias":"199","uso_sigpac":"FY","region":12,"altitud":42,"srid":4258,"wkt":"POLYGON((-0.9676 37.7186, ...))"}`. **Importante:** el servidor responde gzip, así que hay que usar `--compressed` (sin él la salida parece basura binaria). Orden de parámetros: `/4258/{lon}/{lat}.json` — [sigpac-hubcloud recinfobypoint](https://sigpac-hubcloud.es/servicioconsultassigpac/query/recinfobypoint/4258/-0.97/37.72.json)
- El endpoint antiguo `https://sigpac.mapa.gob.es/fega/ServiciosVisorSigpac/query/recinfobypoint/4258/-0.97/37.72.json` devuelve HTTP 400 "Bad Request" (abandonado) — [prueba en vivo](https://sigpac.mapa.gob.es/fega/ServiciosVisorSigpac/query/recinfobypoint/4258/-0.97/37.72.json)
- **OGC API Features**: raíz titulada "API de descarga de objetos geográficos (API-Features) de datos SIGPAC del Fondo Español de Garantía Agraria (FEGA)", con OpenAPI en `/ogcapi/openapi`, procesos (`/ogcapi/processes`) y teselas (`/ogcapi/TileMatrixSets`) — [sigpac-hubcloud OGC API](https://sigpac-hubcloud.es/ogcapi?f=json)
- Colecciones: `recintos` ("Recintos SIGPAC de la campaña en uso"), `cultivo_declarado` ("Cultivo declarado de la campaña en uso"), `elementos_paisaje_area/linea/punto` — [collections](https://sigpac-hubcloud.es/ogcapi/collections?f=json)
- Consulta por bbox probada: `curl -sS --compressed "https://sigpac-hubcloud.es/ogcapi/collections/recintos/items?f=json&bbox=-0.9702,37.7198,-0.9698,37.7202&limit=2"` → HTTP 200, 0,21 s, GeoJSON FeatureCollection con `provincia, municipio, poligono, parcela, recinto, pendiente_media, altitud` y geometría Polygon — [recintos items](https://sigpac-hubcloud.es/ogcapi/collections/recintos/items?f=json&bbox=-0.9702,37.7198,-0.9698,37.7202&limit=2)
- **WMS**: `https://sigpac-hubcloud.es/wms?request=GetCapabilities&service=WMS` → HTTP 200, 0,26 s; capas `recinto`, `cultivo_declarado`, `e_paisaje`, `e_paisaje_linea`, `e_paisaje_punto` (también con prefijo `AU.Sigpac:`) — [SIGPAC WMS](https://sigpac-hubcloud.es/wms?request=getcapabilities&service=wms)
- **ATOM (descarga masiva)**: recintos SIGPAC 2025 y 2026, elementos del paisaje 2025 y 2026, cultivo declarado 2025 — [feed ATOM FEGA](https://www.fega.gob.es/atom/es.fega.sigpac.xml). Directorio navegable por año: `https://www.fega.gob.es/atom/2025/` contiene `cd_2025/`, `ep_2025/`, `rec_2025/` y `sigpac_codes_2025.zip` — [índice atom/2025](https://www.fega.gob.es/atom/2025/)
- **Tablas de códigos** (23 KB, descargado): `cod_producto.csv` (888 productos), `cod_usosigpac.csv`, `cod_incidencia.csv`, `cod_aprovechamiento.csv`, `cod_lineasad.csv`, `cod_region_2023.csv`… Ej.: uso `FY` = FRUTALES, `TA` = TIERRAS ARABLES, `TH` = HUERTA, `IV` = INVERNADEROS Y CULTIVOS BAJO PLÁSTICO, `CI` = CÍTRICOS; incidencia `199` = "Recinto inactivo" — [sigpac_codes_2025.zip](https://www.fega.gob.es/atom/2025/sigpac_codes_2025.zip)
- Licencia CC BY 4.0, catalogado como Conjunto de Datos de Alto Valor (Reglamento UE 2023/138); visor oficial en `https://sigpac.mapa.gob.es/fega/visor/` — [datos.gob.es ficha](https://datos.gob.es/es/catalogo/e0dat0002-cultivo-declarado-del-sistema-integrado-de-gestion-y-control-espana)
- **SIGPAC histórico de Murcia (IMIDA, ArcGIS REST)**: servicios `SIGPAC_2011`, `SIGPAC_2014`…`SIGPAC_2022`, `SIGPAC_2024` en la carpeta `AGRICULTURA_Y_GANADERIA`, y `SIGPAC_2012`, `SIGPAC_2013` en `3_09_INSTALACIONES_AGRICOLAS_Y_ACUICULTURA` (no aparece 2023) — [IMIDA AGRICULTURA_Y_GANADERIA](https://geoportal.imida.es/gis/rest/services/AGRICULTURA_Y_GANADERIA?f=json)
- Consulta probada a SIGPAC 2024 (capa 1 "SIGPAC2024 Recintos") en el punto → HTTP 200, 0,16 s; campos útiles: `uso_sigpac: FY`, `coef_regadio: 0`, `pendiente_media: 6`, `factor_suelo_auto: 94`, `grupo_cultivo_2013: CP`, `zona_marmenor: 0`, `nitratos`, `ref_catastral: 51016A502001420000PT` — [IMIDA SIGPAC_2024 query](https://geoportal.imida.es/gis/rest/services/AGRICULTURA_Y_GANADERIA/SIGPAC_2024/MapServer/1/query?geometry=-0.97,37.72&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=false&f=json)
- Punto secundario Jumilla (38.47, -1.33): `recinfobypoint` → HTTP 200, 0,23 s, municipio 22 (Jumilla), polígono 41, parcela 9000, 330 ha, `uso_sigpac: ZU` (zona urbana) — [prueba](https://sigpac-hubcloud.es/servicioconsultassigpac/query/recinfobypoint/4258/-1.33/38.47.json)

### Inferences
- Para la demo basta una sola llamada (`recinfobypoint`) para dibujar la parcela al hacer clic en el mapa: devuelve geometría + pendiente + altitud + regadío + uso. Con el WKT se recortan después los datos satelitales (AppEEARS, Sentinel).
- Los servicios IMIDA SIGPAC 2011–2024 permiten mostrar **cómo cambió el uso SIGPAC del recinto en 13 años** (p. ej., de invernadero a frutal), aunque el uso SIGPAC es grueso (TA/TH/FY…) y no dice qué hortaliza se sembró.
- El punto de prueba tiene incidencia 199 ("recinto inactivo"), así que no es el mejor ejemplo para la demo: hay que elegir un recinto activo de `TA`/`TH` con cultivo declarado (ver sección 2).

### Gaps
- No se encontró documentación de límites de uso (rate limits) de `sigpac-hubcloud.es`; ningún test dio error, pero no se probó carga.
- No se probaron las teselas vectoriales (MVT) ni los procesos de la OGC API.
- No se revisó si existe un visor SIGPAC específico de la CARM distinto del nacional; los servicios IMIDA cubren esa necesidad.

---

## 2. Cultivos declarados: ¿hay datos abiertos de qué se sembró cada año en cada parcela (para derivar rotaciones reales)?

### Takeaway
**Sí, y es el hallazgo más importante.** El FEGA publica como dato abierto la capa "Cultivo declarado" del SIGC (declaraciones PAC) a nivel de recinto: la campaña en curso vía OGC API/WMS y la campaña 2025 como GeoPackage/Shapefile por municipio. Comparando ambas se ve una rotación real en la parcela de prueba (2025 lechuga → campaña en uso melón). Solo hay **2 campañas** abiertas; no hay histórico más largo de cultivos declarados. **KEEP.**

### Cited Findings
- Prueba en vivo: `curl -sS --compressed "https://sigpac-hubcloud.es/ogcapi/collections/cultivo_declarado/items?f=json&bbox=-0.9705,37.7195,-0.9695,37.7205&limit=5"` → HTTP 200, 0,22 s, 1 feature: polígono 502, parcela 141, recinto 1, `parc_producto: 153` (= MELÓN según `cod_producto.csv`), `parc_sistexp: "R"` (regadío), `parc_supcult: 10300` (m²), `parc_ayudasol: "18"`, `cultsecun_producto: null` — [cultivo_declarado items](https://sigpac-hubcloud.es/ogcapi/collections/cultivo_declarado/items?f=json&bbox=-0.9705,37.7195,-0.9695,37.7205&limit=5)
- Campos consultables (`queryables`): provincia, municipio, agregado, zona, polígono, parcela, recinto, `exp_ca`, `exp_provincia`, `exp_num` (nº de expediente), `parc_producto`, `parc_sistexp`, `parc_supcult`, `parc_ayudasol`, `pdr_rec`, `cultsecun_producto` (cultivo secundario), `cultsecun_ayudasol`, `parc_indcultapro`, `tipo_aprovecha` — [queryables](https://sigpac-hubcloud.es/ogcapi/collections/cultivo_declarado/queryables?f=json)
- El ATOM solo ofrece cultivo declarado de **2025** (no hay `cd.2026` ni años anteriores en el feed), en GPKG y SHP — [ATOM cd 2025](https://www.fega.gob.es/atom/es.fega.sigpac.cd.2025.xml)
- Descarga por municipio, carpeta Murcia: `https://www.fega.gob.es/atom/2025/cd_2025/30%20-%20MURCIA/`; ficheros `300NN_cd_2025_20250110_gpkg.zip`; tamaños: Cartagena (30016) 6,3 MB, Jumilla (30022) 28 MB, Torre-Pacheco (30037) 4,8 MB; existen también carpetas de Albacete (02), Alicante (03), Almería (04) — [índice cd_2025](https://www.fega.gob.es/atom/2025/cd_2025/) y [carpeta Murcia](https://www.fega.gob.es/atom/2025/cd_2025/30%20-%20MURCIA/)
- GPKG de Cartagena 2025 descargado y leído con `sqlite3` (sin GDAL): tabla `cultivo_declarado`, 13.936 filas, columnas incl. `exp_ano` (=2025), `parc_producto`, `parc_sistexp`, `parc_supcult`, `cultsecun_producto`, `dn_geom`. El mismo recinto 502/141/1 aparece en 2025 con `parc_producto 155` (LECHUGA, regadío, 10.300 m²) y una segunda fila con `207` (LIMONERO) — [30016_cd_2025_20250110_gpkg.zip](https://www.fega.gob.es/atom/2025/cd_2025/30%20-%20MURCIA/30016_cd_2025_20250110_gpkg.zip)
- Superficie declarada 2025 en Cartagena por producto (top): sin producto 3.768 ha (5.722 filas); patata (99) 1.623 ha; barbecho tradicional (20) 1.359 ha; limonero (207) 1.327 ha; melón (153) 1.249 ha; almendro (104) 1.133 ha; pastos permanentes (62) 553 ha; lechuga (155) 521 ha; naranjo (206) 402 ha; trigo blando (1) 315 ha. 1.358 filas tienen cultivo secundario — [mismo fichero](https://www.fega.gob.es/atom/2025/cd_2025/30%20-%20MURCIA/30016_cd_2025_20250110_gpkg.zip)
- El servicio "Cultivo declarado del SIGC (España)" es HVD con licencia CC BY 4.0; contacto FEGA, SG Ayudas Directas; no indica frecuencia de actualización ni campañas — [datos.gob.es](https://datos.gob.es/es/catalogo/e0dat0002-cultivo-declarado-del-sistema-integrado-de-gestion-y-control-espana)
- Mapa de cultivos regional de Murcia **2005** (IMIDA): "Mapa de cultivos de la región de Murcia del año 2005. Visible a partir de la escala 1:25.000", a nivel de recinto. Consulta en el punto → recinto 502/142/1 con `USO_SIGPAC: IV`, `GRUP_CULT: IV` (invernadero en 2005, frutal en 2024–2026) — [IMIDA Cultivos MapServer](https://geoportal.imida.es/gis/rest/services/2_02_CUBIERTA_TERRESTRE/Cultivos/MapServer/0/query?geometry=-0.97,37.72&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=false&f=json)
- Mapa de Cultivos y Aprovechamientos (MCA) del MAPA: solo ediciones 1980–1990 y 2000–2010, a 1:50.000, descarga nacional en ZIP (`MapaCultivos1980_90.zip`, `Mapa_Cultivos_2000_10.zip`) — [MAPA MCA descargas](https://www.mapa.gob.es/es/cartografia-y-sig/ide/descargas/agricultura/mca). La URL WMS `https://wms.mapama.gob.es/sig/Agricultura/MapaCultivos2000-2010/wms.aspx` devolvió una excepción del servidor (`NullReferenceException`) — [prueba](https://wms.mapama.gob.es/sig/Agricultura/MapaCultivos2000-2010/wms.aspx?SERVICE=WMS&REQUEST=GetCapabilities)

### Inferences
- Como la OGC API ("campaña en uso") da MELÓN para el mismo recinto que en el fichero 2025 tiene LECHUGA, la API sirve **una campaña distinta de 2025, casi seguro la 2026**. Así se obtienen **dos años consecutivos** por recinto: fichero ATOM 2025 + API 2026. Es la "rotación actual" que pide el reto (estrategia de referencia) con dato oficial. Conviene confirmarlo con más recintos antes de afirmarlo en el pitch.
- Con el GPKG de 2025 de los municipios del Campo de Cartagena (Cartagena, Torre-Pacheco, San Javier, Fuente Álamo…) se pueden calcular **transiciones típicas 2025→2026** (lechuga→melón, brócoli→…) cruzando con la API por bbox. Sirven como "rotaciones observadas en la zona" para el comparador. El cultivo secundario (`cultsecun_producto`) captura el doble cultivo anual típico de hortícolas.
- Para más de 2 años, la única vía abierta es el **uso SIGPAC** histórico del IMIDA (2011–2024) y el mapa de cultivos 2005: sirve para cambios estructurales (invernadero/frutal/arable), no para la secuencia de hortalizas. El NDVI satelital tendría que rellenar el resto.
- Privacidad: `exp_num` es un identificador de expediente de ayuda. No mostrarlo en la interfaz ni en el pitch.
- Calidad: hay recintos con varias filas (dos expedientes, productos distintos) y miles de filas sin producto, así que hay que agregar por recinto y tratar los nulos.

### Gaps
- No se encontró ninguna publicación tipo "DUN de Cataluña" con serie larga (2015–2024) de cultivos declarados para Murcia. No se buscó en otras CC. AA.
- No se confirmó oficialmente qué campaña sirve la OGC API ni cuándo cambia de campaña.
- No se comprobó el significado de `ld_recinto` negativo ni la causa de las filas duplicadas.

---

## 3. Estadística agraria, precios y mercados (MAPA, CREM/ESAM CARM)

### Takeaway
Para los ingresos de cada rotación, la mejor fuente local son los **informes semanales de precios en origen de la CARM** (PDF, hasta la semana 45/2026). A nivel nacional, el MAPA publica precios medios en origen semanales (PDF, con Excel/Power BI). Los rendimientos salen de ESYRCE y del Anuario de Estadística Agraria de Murcia (PDF). No existe una API: hay que **precalcular a mano una tabla pequeña** (precio y rendimiento por cultivo). Veredicto: precios CARM **KEEP (tabla manual)**, ESYRCE/Anuario **KEEP (tabla manual)**, MCA **DROP**.

### Cited Findings
- CARM (Estadística Agraria Región de Murcia): página "Informes Semanales de Precios Representativos de Campo" con 135 enlaces a PDF; el último es la semana 45 de 2026: `https://esam.carm.es/wp-content/uploads/2026/11/PRECIOS-CAMPO-SEMANA-45_2026.pdf` — [listado ESAM](https://esam.carm.es/informes-semanales-de-precios-campo/)
- Formato de esos PDF: tabla con producto, variedad, categoría, posición de mercado ("s/finca" o "s/merc origen R. de Murcia") y precio mínimo/máximo en €/kg o €/unidad; incluyen apio, brócoli, calabacín, cebolla, pimiento, tomate, además de fruta y ganado — [semana 22/2025](https://esam.carm.es/wp-content/uploads/2025/06/PRECIOS-CAMPO-SEMANA-22.pdf), [semana 38/2025](https://esam.carm.es/wp-content/uploads/2025/10/PRECIOS-CAMPO-SEMANA-38_2025.pdf)
- La página "Evolución de precios de campo semanales" tiene buscador por producto (lechuga, limón…; algunos "sin datos en los últimos 5 años"), pero los datos se cargan por JavaScript; el HTML no trae la serie (probado: `curl https://esam.carm.es/observatorio-precios/precios-productos/lechuga/` → HTTP 200 sin cifras) — [ESAM precios por producto](https://esam.carm.es/observatorio-precios/precios-productos/)
- Anuario de Estadística Agraria de la Región de Murcia 2023/24 (PDF, julio 2026), con producción de herbáceos y leñosos y mapas por municipio — [Anuario 23/24](https://esam.carm.es/wp-content/uploads/2026/07/ANUARIO-23_24_PAGINAS_FINAL-1_compressed-1.pdf). Aviso metodológico: hasta 2020 los herbáceos solo contaban la ocupación principal; desde 2021 suman cultivos asociados — [búsqueda sobre CREM/ESAM](https://econet.carm.es/inicio/-/crem/sicrem/PU590/pdf/sec15.pdf)
- CREM (econet.carm.es): tablas municipales de distribución de la tierra y series de cultivos por municipio en PDF (p. ej. sección 15 de "Región de Murcia en cifras") — [CREM sec15](https://econet.carm.es/inicio/-/crem/sicrem/PU590/pdf/sec15.pdf), [Anuario CREM 2019 tomo II M4](https://econet.carm.es/inicio/-/crem/anuario/a2019/TomoII/pdf/M4.pdf)
- MAPA ESYRCE: resultados provisionales 2025 (trabajo de campo de mayo a octubre de 2025), tablas en la web, informe Power BI de rendimientos y microdatos solo bajo solicitud con fines científicos; el detalle provincial está en la publicación de tendencias de rendimientos — [ESYRCE](https://www.mapa.gob.es/es/estadistica/temas/estadisticas-agrarias/agricultura/esyrce), [tendencias mensuales](https://www.mapa.gob.es/es/estadistica/temas/estadisticas-agrarias/agricultura/esyrce-tendencias-mensuales-rendimientos-cultivos), [Informe Tendencias junio 2026](https://servicio.mapa.gob.es/fr/dam/jcr:1e12ebba-6146-44fb-bdb8-48afc4149c15/Informe_Tendencias_ESYRCE_Junio_2026.pdf)
- MAPA, Informe Semanal de Coyuntura: incluye "Precios Medios Nacionales en Origen de Frutas y Hortalizas" en €/100 kg (ej. acelga 73,38 → 69,09) — [ISC 2026 S-37](https://www.mapa.gob.es/es/dam/jcr:e5135043-2f1c-470c-a047-20ab5befe5b9/Informe%20Semanal%20de%20Coyuntura%202026%20S-37.eb96f778053a35885949ed82ed93ef71.pdf). Hay referencia a versiones "Excel y PowerBI" de los precios medios nacionales, no verificadas — [MAPA, boletín semanal de precios F&H](https://www.mapa.gob.es/es/agricultura/temas/producciones-agricolas/frutas-y-hortalizas/boletin_semanal_precios.aspx)
- Catálogo nacional datos.gob.es tiene API (probada): `curl "https://datos.gob.es/apidata/catalog/dataset/title/cultivo.json?_pageSize=10"` → HTTP 200, 0,50 s; los resultados para "cultivo" son sobre todo de Canarias, nada específico de Murcia — [datos.gob.es apidata](https://datos.gob.es/apidata/catalog/dataset/title/cultivo.json?_pageSize=10)

### Inferences
- En 36 h lo práctico es: abrir 3–4 PDF de precios CARM (p. ej. una semana por trimestre de 2025–2026) y la tabla de rendimientos de Murcia del Anuario/ESYRCE, y escribir a mano un `crops.csv` (cultivo, €/kg mín–máx, kg/ha, ciclo, mes de siembra/cosecha, necesidades de agua). Citar las fuentes en `submission/`.
- Para que el comparador muestre margen bruto por rotación basta con precio × rendimiento − coste del agua; los precios CARM dan la variabilidad (mín/máx) como medida de riesgo de mercado.

### Gaps
- No se verificó si existe descarga Excel histórica de precios medios nacionales semanales ni su URL exacta.
- No se encontró Excel/CSV de la estadística agraria municipal de Murcia; todo lo encontrado es PDF.
- No se investigó la Red de Alerta e Información Fitosanitaria (es de Andalucía) ni los avisos fitosanitarios de la CARM.

---

## 4. Estaciones agroclimáticas: SIAM (IMIDA), SiAR (MAPA) y AEMET

### Takeaway
**SIAM es la mejor fuente para Murcia y no necesita clave**: 50–55 estaciones (incluye las del SiAR en la Región). Hay un servicio ArcGIS con el último dato diario (fecha de ayer, con ET0 Penman-Monteith) y CSV históricos diarios 2000–2018 por estación (2019–2020 en CSV anuales; 2021–2026 solo vía portal web). SiAR tiene API JSON, pero exige registro con NIF y contraseña (lo tiene que hacer un humano). AEMET necesita API key por email. Veredicto: **SIAM KEEP**, **SiAR OPTIONAL** (solo para Alicante/Almería/Albacete), **AEMET OPTIONAL**.

### Cited Findings
- **Lista de estaciones SIAM (CSV, sin clave)**: `curl -sS "https://datosabiertos.carm.es/odata/Agricultura/IMIDA_estaciones.csv"` → HTTP 200, 0,23 s, 4 KB, codificación Latin-1; columnas `CODEST, RED, PARAJE, MUNICIPIO, FECHA DE ALTA, LATITUD, LONGITUD, ALTITUD`; 50 estaciones (34 red SIAM + 16 red SIAR) — [IMIDA_estaciones.csv](https://datosabiertos.carm.es/odata/Agricultura/IMIDA_estaciones.csv)
- Estaciones cerca del punto de prueba: **CA12 La Palma (Cartagena) 37.6889, -0.9509, alta 25/06/05, 30 m** (~3,5 km); TP91 Torre Pacheco 37.7477, -0.9867 (2005); TP42 Torre Blanca 37.7739, -0.8985 (1997); CA52 La Aljorra (red SIAR, 1999); CA42 Balsapintada (SIAR); TP73, TP22, TP52, CA73, CA91. Altiplano: JU81 Román (Jumilla) 38.3198, -1.3243 (1998); JU71 Las Encebras (Jumilla) 38.3944, -1.2393 (1996); JU52 Pinillos y JU42 Las Moratillas (Yecla) — [mismo CSV](https://datosabiertos.carm.es/odata/Agricultura/IMIDA_estaciones.csv)
- **Serie diaria por estación**: `curl -sS "https://datosabiertos.carm.es/odata/Agricultura/IMIDA_Diario_TP42.csv"` → HTTP 200, 0,55 s, ~0,9 MB comprimido, 6.854 filas desde 01/01/2000 hasta **31/12/2018** (no se actualiza); columnas `fecha,tmed,tmax,tmin,hrmed,hrmax,hrmin,radmed,vvmed,vvmax,dvmed,prec,eto` — [IMIDA_Diario_TP42.csv](https://datosabiertos.carm.es/odata/Agricultura/IMIDA_Diario_TP42.csv). Hay un fichero igual para cada estación (patrón `IMIDA_Diario_{CODEST}.csv`) — [catálogo CKAN IMIDA](https://datosabiertos.regiondemurcia.es/api/3/action/package_search?fq=organization:imida&rows=200)
- CSV anual con todas las estaciones: `IMIDA_dia_2020.csv` → HTTP 200, 1,9 MB, separador `;` y coma decimal (`"FECHA";"EST";...;"ETO"`). `IMIDA_dia_2021/2023/2025.csv` → HTTP 404 — [IMIDA_dia_2020.csv](https://datosabiertos.carm.es/odata/Agricultura/IMIDA_dia_2020.csv)
- Los ficheros "tiempo real" del catálogo (`ImidaMeteoHora.json/.csv`, `ImidaMeteoAnnio.csv`) devuelven HTTP 500 "No se ha localizado un servicio con la clave url.getImidaMeteoHora" (rotos) — [ImidaMeteoHora.json](https://datosabiertos.carm.es/rest-services/services/restFile/ImidaMeteoHora.json). El JSON de estaciones `https://transparencia.carm.es/rest-services/services/restAPI/ImidaEstaciones` → HTTP 500 — [prueba](https://transparencia.carm.es/rest-services/services/restAPI/ImidaEstaciones)
- **Último dato diario en vivo (sin clave)**: `curl -sS --compressed "https://geoportal.imida.es/gis/rest/services/3_14_ASPECTOS_GEOGRAFICOS_DE_CARACTER_METEOROLOGICO/SIAM_DATOS/MapServer/0/query?where=1%3D1&outFields=*&returnGeometry=false&f=json"` → HTTP 200, 6,8 s, 55 estaciones; ej. CA12: `FECHA 1794441600000` (= 2026-11-12), `ETO_PM_FAO 2.87`, `PREC 0.0`, `TMAX 26.41`, `TMIN 17.04`, `HRMED 56.8`, `RADMED 155.67`. No acepta `resultRecordCount` ("Pagination is not supported"). La capa 1 es `SIAM_ULTIMO_DATO_HORARIO` — [SIAM_DATOS MapServer](https://geoportal.imida.es/gis/rest/services/3_14_ASPECTOS_GEOGRAFICOS_DE_CARACTER_METEOROLOGICO/SIAM_DATOS/MapServer?f=json)
- Portal SIAM (Oracle APEX, solo http): menús "Informe agrometeorológico personalizado" (`f?p=101:46`), "Datos en tiempo real de las estaciones" (`f?p=101:110`), "Informe sobre horas frío para fruticultura" (`f?p=101:159`), "Informe de bajas temperaturas" (`f?p=101:147`), "Ficha estaciones". Son formularios con sesión: el histórico 2019–2026 se descarga a mano — [SIAM](http://siam.imida.es/apex/f?p=101:1)
- Modelo de **horas frío (<7 °C)** como ráster IMIDA; `identify` en el punto → 360 h (Modelo2) / 221 h (Modelo1) — [Modelos_horas_frio identify](https://geoportal.imida.es/gis/rest/services/3_14_ASPECTOS_GEOGRAFICOS_DE_CARACTER_METEOROLOGICO/Modelos_horas_frio/MapServer/identify?geometry=-0.97,37.72&geometryType=esriGeometryPoint&sr=4326&layers=all&tolerance=1&mapExtent=-1.0,37.7,-0.9,37.8&imageDisplay=400,400,96&returnGeometry=false&f=json)
- **SiAR**: la web se ha movido; `www.siar.es` redirige a `https://servicio.mapa.gob.es/siarweb/`, y `https://servicio.mapa.gob.es/websiar/` da 404 (muchos tutoriales tienen la URL vieja) — [siarweb](https://servicio.mapa.gob.es/siarweb/)
- SiAR API (manual técnico): base `https://servicio.mapa.gob.es/siarapi/API/V1/`; JSON; endpoints `Info/ESTACIONES|PROVINCIAS|CCAA|ACCESOS|CODIGOSVALIDACION?token=…` y `Datos/{Horarios|Diarios|Diarios2|Semanales|Mensuales}/{ESTACION|CCAA|…}?token=…&Id=HU01&Id=HU02&FechaInicial=2025-01-01&FechaFinal=2025-05-01&DatosCalculados=true`; con `DatosCalculados=true` devuelve `EtPMon` (ET0 Penman-Monteith); `Diarios2` da horas por tramo de temperatura (integrales térmicas). Para el token, el usuario debe estar dado de alta en REGEUS del MAPA y pedir "Deseo darme de alta en API SiAR"; NIF y contraseña se cifran con `/Autenticacion/cifrarCadena` y luego `/Autenticacion/obtenerToken`. Ejemplo de límites del manual: 30 peticiones/min, 1.000/día — [Manual técnico Web API SiAR](https://servicio.mapa.gob.es/siarweb/documentos/manuales/ManualTecnico_WEB_API_SIAR.pdf)
- Una fuente de terceros cita límites distintos (15 accesos/min, 240/día, 100 registros/min, 10.000/día) y un dominio anterior `servicio.mapama.gob.es/apisiar`, que ya da 404; SiAR guarda datos desde 1999 y tiene >520 estaciones — [pgtec-vrain SiAR](https://pgtec-vrain.github.io/data_sources/metadata_datasources/siar_datasource)
- Prueba sin token: `curl "https://servicio.mapa.gob.es/siarapi/API/V1/Info/ESTACIONES?token=INVALID"` → `{"status":500,"error":"Internal Server Error"}`; sin `token` → HTTP 400 — [siarapi](https://servicio.mapa.gob.es/siarapi/API/V1/Info/ESTACIONES)
- **AEMET OpenData**: sin clave, `curl -i "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones"` → HTTP 200 con cuerpo vacío (0 bytes), así que hace falta clave — [endpoint](https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones)
- Alta de clave: formulario que solo pide email y un campo de comprobación; condición de uso: "Autorizado el uso de la información y su reproducción citando a Aemet como autora" — [altaUsuario](https://opendata.aemet.es/centrodedescargas/altaUsuario). La clave es gratuita, llega por email y se envía como parámetro `api_key` o como cabecera — [datos.gob.es blog HVD meteo](https://datos.gob.es/es/blog/los-conjuntos-de-datos-meteorologicos-de-alto-valor), [presentación AEMET](https://www.aemet.es/documentos/es/conocenos/congresos_y_conferencias/reuniones/jornada_AEMET_OpenData/presentaciones/JMG.pdf)
- Endpoint de valores diarios usado por librerías: `valores/climatologicos/diarios/datos/fechaini/{}/fechafin/{}/estacion/{idema}` (fuente de terceros) — [wetterdienst AEMET](https://wetterdienst.readthedocs.io/en/latest/data/provider/aemet/observation/index.html); librería Python [pyAEMET](https://github.com/Jaimedgp/pyAEMET)
- Estaciones AEMET: **7031 San Javier Aeropuerto** (4 m, normales 1981–2010) — [AEMET 7031](https://www.aemet.es/es/serviciosclimaticos/datosclimatologicos/valoresclimatologicos?l=7031); **7228 Alcantarilla Base Aérea** (75 m) — [AEMET 7228](https://www.aemet.es/gl/serviciosclimaticos/datosclimatologicos/valoresclimatologicos?l=7228); **7178I Murcia** (solo fuente no oficial) — [snowy.es 7178I](https://snowy.es/stations/7178I)

### Inferences
- Para la demo: `SIAM_DATOS` (último día, con ET0) + CSV histórico 2000–2018 de CA12/TP91 (o TP42) + NASA POWER para rellenar 2019–2026 y validar. Así la herramienta enseña "dato de satélite/reanálisis NASA vs estación en suelo", que es justo lo que pide combinar el reto.
- Tarea natural para el compañero de IoT/redes: un pequeño colector que lea cada hora la capa `SIAM_ULTIMO_DATO_HORARIO`, la guarde en una serie temporal propia (SQLite/InfluxDB) y la sirva a la app como "red de sensores en tierra". Con la misma estructura de datos podría añadir un nodo LoRa simulado.
- SiAR no aporta nada en Murcia que no dé ya SIAM (las 16 estaciones SIAR de la Región están en la lista del IMIDA). Solo compensa si se quieren estaciones de Alicante, Almería o Albacete, y exige registro personal con NIF: decisión humana.
- AEMET: la clave por email suele ser rápida, pero no se probó; no es imprescindible teniendo SIAM y POWER. Si se usa, que la pida un humano y la guarde en `.env`.

### Gaps
- No se encontró el límite oficial de peticiones de AEMET OpenData ni se confirmó oficialmente el indicativo de Cartagena (¿7012C?) ni el de Murcia (7178I).
- No se verificó la licencia de los datos SIAM en el catálogo CKAN (campo `license_title` vacío).
- No se sabe si el alta en SiAR/REGEUS es inmediata.
- No se probó la descarga del "informe personalizado" del portal SIAM (2019–2026).

---

## 5. Agua: CHS (SAIH, piezometría, nitratos) y Mar Menor

### Takeaway
La CHS no tiene API documentada: SAIH y piezometría están detrás de visores con AJAX y formularios. **Atajo:** el IMIDA republica las capas de la CHS (piezómetros, estaciones de nitratos, pluviómetros, SAICA…) y las del Mar Menor (boyas, zonas vulnerables) como servicios ArcGIS consultables en JSON. Veredicto: **zonas vulnerables a nitratos y zona Mar Menor KEEP** (restricción regulatoria clave en el Campo de Cartagena); **piezómetros y nitratos de la CHS vía IMIDA OPTIONAL**; **SAIH/iVisor directo DROP**; **Canal Mar Menor/SDC DROP**.

### Cited Findings
- SAIH iVisor: `https://saihweb.chsegura.es/apps/ivisor/inicial.php` → HTTP 200, 0,65 s, app PHP; las páginas de datos (`index.php?salto=1&subsalto=pluviometria1.php`) cargan por AJAX y enlazan a `protocolo.php?tipo=1` (aceptación de condiciones). Los datos son provisionales y la consulta o descarga exige aceptar un formulario — [SAIH iVisor](https://saihweb.chsegura.es/apps/ivisor/inicial.php), [CHS iVisor](https://chsegura.es/en/cuenca/redes-de-control/saih/ivisor)
- El informe horario de precipitaciones es una ArcGIS Web App — [visor](https://www.chsegura.es/descargas/enlacesvisoresportal/Visor-informe-horario-precipitaciones)
- Piezometría: página "Consulta de series de piezometría" con visor/tabla en JavaScript; el HTML estático no trae datos — [series piezometría](https://www.chsegura.es/es/cuenca/redes-de-control/piezometria/series-piezometria/)
- Calidad de aguas subterráneas: descarga por estación, masa, municipio o provincia, con máximo un año natural por consulta — [Guía acceso datos SUB01](https://www.chsegura.es/export/sites/chs/descargas/cuenca/redesdecontrol/calidadenaguassubterraneas/docsdescarga/Guia_acceso_datos_SUB01.pdf)
- Licencia de la web CHS: enlace a CC BY 3.0 ES — [CHS iVisor (pie de página)](https://www.chsegura.es/es/cuenca/redes-de-control/saih/ivisor/); el registro de la red piezométrica pide citar a la CHS — [RediAM](https://portalrediam.cica.es/geonetwork/srv/api/records/6be7b660-740b-421b-baea-367048469659)
- **Capas CHS en el IMIDA** (`PROYECTOS/CHS_DATOS`, "Capas visor web CHS"): 23 capas, entre ellas Pluviometria, Meteorologia, Aforos, Red_de_control_SAICA, Calidad_subterranea, Piezometria, Estaciones_nitratos_web2021, Sondeos_MarMenor — [CHS_DATOS MapServer](https://geoportal.imida.es/gis/rest/services/PROYECTOS/CHS_DATOS/MapServer?f=json)
- Consulta probada (bbox -1.05,37.65,-0.85,37.80): capa 11 Piezometria → 8 piezómetros del acuífero Campo de Cartagena (ej. PA12223 "Cortijo de la Palma", Cartagena, Z 36,61 m, con enlace directo a la serie `...series-piezometria/index.html?entidad=cota&idMasa=070.052&listaCodigo=PA12223`); capa 12 → 12 estaciones de nitratos (ej. CA07NI-49, "Afectada", "Estaciones afectadas por nitratos DENTRO de ZV") — [Piezometria query](https://geoportal.imida.es/gis/rest/services/PROYECTOS/CHS_DATOS/MapServer/11/query?geometry=-1.05,37.65,-0.85,37.80&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=false&f=json)
- **Zonas vulnerables a nitratos y zonas Mar Menor (IMIDA)**: capas ZVN 2019, "Zonas Decreto Ley MM 2019", "Franja 1500 m", CHS Zona0/A1/A2, ZonaB, DPMT. Consulta en el punto → `ZONEID ES62_1`, `NAME Campo de Cartagena`, `AREAKM 412.8` — [ZONAS_VULNERABLES_NITRATOS query](https://geoportal.imida.es/gis/rest/services/PROYECTOS/ZONAS_VULNERABLES_NITRATOS/MapServer/0/query?geometry=-0.97,37.72&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=false&f=json)
- Capa nacional MITECO de zonas vulnerables (versiones dic-2024 y jul-2025), designadas por las CC. AA. — [MITECO zonas vulnerables](https://www.miteco.gob.es/es/cartografia-y-sig/ide/descargas/agua/zonas-vulnerables.html), [ficha servicio 2024](https://sig.mapama.gob.es/Docs/PDFServicios/ZonasVulnerables2024.pdf). Programa de actuación vigente en Murcia: orden de 16/06/2016, en revisión en 2025 — [MAIN 2025 PAZV](https://transparencia.carm.es/wres/transparencia/doc/IniciativasNormativas/2025_INI_AGRICULTURA_PAZV_nitratos/MAIN_2025_INI_AGRICULTURA_PAZV_nitratos.pdf)
- **Boyas Mar Menor (IMIDA)** `PROYECTOS/MARMENOR_BOYAS`: oxígeno y temperatura del día actual, evolución de la última semana, "Datos Completos Boyas Día Actual", "Piezómetros Últimos Datos Medios" — [MARMENOR_BOYAS](https://geoportal.imida.es/gis/rest/services/PROYECTOS/MARMENOR_BOYAS/MapServer?f=json)
- Canal Mar Menor: informes en PDF; los datos CTD son "provisionales a espera de su consolidación por el Servidor de Datos Científicos (SDC)"; no se encontró API ni descarga directa — [informe monitorización](https://canalmarmenor.carm.es/wp-content/uploads/Informe_monitorizacion_30_revisado_Director-COPIA.pdf), [guía subida CTD al SDC (UPCT)](https://download.med.upct.es/SDP_CTD/Guia_subida_datos_CTD_a_SDC.pdf). Los informes del proyecto BELICH (IEO-CSIC) prohíben publicar sus datos sin consentimiento — [Informe IEO enero 2026](https://www.miteco.gob.es/content/dam/miteco/es/ministerio/planes-estrategias/mar-menor/Informe-IEO-ENERO-2026.pdf)
- Anuario de Aforos del MITECO: descarga CSV nacional de caudales, embalses y evaporímetros (no incluye piezometría) — [Anuario de Aforos](https://www.miteco.gob.es/es/agua/temas/evaluacion-de-los-recursos-hidricos/sistema-informacion-anuario-aforos.html)

### Inferences
- Para el Campo de Cartagena, la restricción de nitratos (ZVN + zonas de la Ley del Mar Menor + franja de 1.500 m) es **un criterio de decisión de primer nivel**: una rotación con más leguminosas, abonos verdes o menos nitrógeno puntúa mejor dentro de esas zonas. Una consulta por punto basta para poner una etiqueta "Parcela en zona vulnerable / zona A1 Mar Menor" en la ficha de la parcela.
- Los piezómetros cercanos (cota del agua y enlace a la serie) sirven como indicador de "estrés del acuífero"; GRACE (NASA) da la tendencia a escala de cuenca. Es un buen par NASA + dato local.

### Gaps
- No se encontró un endpoint JSON/CSV directo para descargar series piezométricas ni de nitratos de la CHS; habría que hacer scraping del formulario (sin probar).
- No se comprobó con qué frecuencia el IMIDA actualiza la copia de las capas CHS (`Estaciones_nitratos_web2021` sugiere 2021).
- No se investigó la red estatal de boyas del MITECO ni su portal de datos.

---

## 6. Portales regionales: catálogo de datos abiertos de Murcia (CKAN) y geoportal IMIDA/IDERM

### Takeaway
El catálogo regional es CKAN 2.10 con API estándar en `/api/3/action/...` (la ruta `/catalogo/api` da 404). En agricultura solo aporta de verdad los datos SIAM del IMIDA. **La joya es el geoportal ArcGIS del IMIDA** (`geoportal.imida.es/gis/rest/services`): suelos, SIGPAC histórico, cultivos 2005, horas frío, SIAM, zonas vulnerables, infraestructuras de regadío y **NDVI Sentinel-2 a 10 m de 2019 a 2026**, todo consultable por punto sin clave. Veredicto: **geoportal IMIDA KEEP**, **CKAN regional OPTIONAL** (solo para SIAM).

### Cited Findings
- CKAN: `curl "https://datosabiertos.regiondemurcia.es/api/3/action/package_search?q=cultivos&rows=5"` → HTTP 200, 0,23 s, 38 resultados (casi ninguno relevante: bancos de germoplasma, contratos); `q=agricultura` → 201 resultados, sobre todo contratos públicos. La ruta `https://datosabiertos.regiondemurcia.es/catalogo/api/3/...` → 404 (página de CKAN 2.10.1) — [package_search](https://datosabiertos.regiondemurcia.es/api/3/action/package_search?q=cultivos&rows=5)
- Organizaciones (n.º de datasets): carm 357, ayuntamiento-de-lorca 216, **imida 128**, fundacion-integra 85, ayuntamiento-de-molina-de-segura 56, ayuntamiento-de-cartagena 22… — [organization_list](https://datosabiertos.regiondemurcia.es/api/3/action/organization_list?all_fields=true)
- Datasets del IMIDA: estaciones SIAM; informe meteorológico diario por estación 2000–2018; diario por año 2000–2020; anual (año hidrológico) y "agrícola" 2000–2021; efemérides; colecciones del banco de germoplasma (melón, tomate, lechuga, calabaza, berenjena) — [IMIDA en CKAN](https://datosabiertos.regiondemurcia.es/api/3/action/package_search?fq=organization:imida&rows=200)
- Geoportal IMIDA, carpetas: `2_01_ELEVACION`, `2_02_CUBIERTA_TERRESTRE`, `2_03_ORTOIMAGENES`, `3_04_USO_DEL_SUELO`, `3_09_INSTALACIONES_AGRICOLAS_Y_ACUICULTURA`, `3_11_ZONAS_SUJETAS_A_ORDENACION…`, `3_12_ZONAS_DE_RIESGOS_NATURALES`, `3_14_ASPECTOS_GEOGRAFICOS_DE_CARACTER_METEOROLOGICO`, `AGRICULTURA_Y_GANADERIA`, `GEMELO`, `PROYECTOS`… — [IMIDA REST root](https://geoportal.imida.es/gis/rest/services?f=json)
- `2_02_CUBIERTA_TERRESTRE`: ImageServer `2019_S2_NDVI_MD` … `2026_S2_NDVI_MD` (píxel 10 m, 1 banda), `2025_S2_INDICES_VEGETACION` (12 fechas de NDVI de 2025: 14-01, 08-02, 30-03, 24-04, 29-05, 28-06, 28-07, 02-08, 11-09, 03-10, 22-11, 30-12), `Cultivos` (mapa 2005), `PASTOS`, `Montes` — [CUBIERTA_TERRESTRE](https://geoportal.imida.es/gis/rest/services/2_02_CUBIERTA_TERRESTRE?f=json), [NDVI 2026 ImageServer](https://geoportal.imida.es/gis/rest/services/2_02_CUBIERTA_TERRESTRE/2026_S2_NDVI_MD/ImageServer?f=json)
- `3_09_INSTALACIONES_AGRICOLAS_Y_ACUICULTURA`: `Balsas_de_riego_Murcia`, `Infraestructuras_regadio_UTM_ETRS89` (Conducciones, Colectivos de riego, CRCC, Sectores, Tuberías, Red drenaje agrícola) — [Infraestructuras regadío](https://geoportal.imida.es/gis/rest/services/3_09_INSTALACIONES_AGRICOLAS_Y_ACUICULTURA/Infraestructuras_regadio_UTM_ETRS89/MapServer?f=json)
- Otros: `3_12_ZONAS_DE_RIESGOS_NATURALES/SNCZI_Zonas_inundables`; `PROYECTOS/DANA_PRECIPITACIONES_MURCIA`, `AEMET_ATLAS_CLIMA`, `AEMET_RED_ESTACIONES`, `ATLAS_DEL_AGUA`, `EVC_PENDIENTE_MEDIA_PARCELA_GP` (GPServer) — [PROYECTOS](https://geoportal.imida.es/gis/rest/services/PROYECTOS?f=json)
- El catálogo de metadatos de la CARM (GeoNetwork) lista servicios WMS IDERM (planeamiento, cauces, litoral) — [CARM geonetwork](https://mapas-gis-inter.carm.es/geonetwork/srv/api/records/sit_hid_cauces_carm_wms_md)

### Inferences
- El geoportal IMIDA sustituye en la práctica a "IDERM/Cartomur" para este proyecto: es REST/JSON, contesta en menos de 1 s (SIAM_DATOS tarda ~7 s) y permite consultas por punto. Patrón general: `…/MapServer/{capa}/query?geometry={lon},{lat}&geometryType=esriGeometryPoint&inSR=4326&outFields=*&returnGeometry=false&f=json`.
- El NDVI Sentinel-2 anual del IMIDA (2019–2026, 10 m) podría dar la **firma fenológica de la parcela** sin cuenta de Copernicus. Ojo: el reto pide datos NASA, así que conviene presentarlo como validación frente a HLS/MODIS de NASA, no como fuente principal.
- Es un servidor de un instituto regional: hay que cachear las respuestas de la parcela demo para no depender de él durante la presentación.

### Gaps
- No se probó la consulta de píxeles (`identify`/`getSamples`) en los ImageServer de NDVI.
- No se encontró la URL viva de IDERM/Cartomur ni su GetCapabilities. No se comprobaron las condiciones de uso del geoportal IMIDA.

---

## 7. IGN/CNIG: relieve (MDT), ortofoto PNOA y usos del suelo

### Takeaway
El WCS del IGN entrega el MDT de 5 m recortado a la parcela en ~0,1 s y sin clave (comprobado: 42 m en el punto, igual que SIGPAC). El WMS del PNOA sirve como mapa base. **MDT05 WCS KEEP** (mejor que SRTM 30 m para pendiente y bolsas de frío en parcelas pequeñas), **PNOA WMS KEEP** (mapa base), **SIOSE OPTIONAL**.

### Cited Findings
- WCS MDT: `GetCapabilities` → HTTP 200, 0,15 s; coberturas `Elevacion4258_5`, `Elevacion4258_25`, `Elevacion4258_200`, `Elevacion4258_500`, `Elevacion4258_1000`, `Elevacion25830_*`… — [WCS MDT capabilities](https://servicios.idee.es/wcs-inspire/mdt?SERVICE=WCS&REQUEST=GetCapabilities)
- GetCoverage probado: `curl -sS -o ign_mdt5_tile.tif "https://servicios.idee.es/wcs-inspire/mdt?SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage&COVERAGEID=Elevacion4258_5&SUBSET=Lat(37.719,37.721)&SUBSET=Long(-0.971,-0.969)&FORMAT=image/tiff"` → HTTP 200, 0,13 s, GeoTIFF 44×44 px int16, 4,3 KB; valor central 42 m (mín 39, máx 44) — [GetCoverage MDT05](https://servicios.idee.es/wcs-inspire/mdt?SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage&COVERAGEID=Elevacion4258_5&SUBSET=Lat(37.719,37.721)&SUBSET=Long(-0.971,-0.969)&FORMAT=image/tiff)
- WMS PNOA máxima actualidad: `https://www.ign.es/wms-inspire/pnoa-ma?SERVICE=WMS&REQUEST=GetCapabilities` → HTTP 200, 0,07 s — [PNOA WMS](https://www.ign.es/wms-inspire/pnoa-ma?SERVICE=WMS&REQUEST=GetCapabilities)
- Un intento de `GetFeatureInfo` en `https://servicios.idee.es/wms-inspire/mdt` con capa `EL.GridCoverage` devolvió una página de otro servicio ("Servicio de Zonas Inundables"): nombre de capa incorrecto; mejor usar el WCS — [prueba](https://servicios.idee.es/wms-inspire/mdt?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities)
- SIOSE para Murcia (IMIDA): `3_04_USO_DEL_SUELO/SIOSE_Murcia_utm_etrs89` y `SIOSE_Murcia_detalle_utm_etrs89` — [SIOSE Murcia detalle](https://geoportal.imida.es/gis/rest/services/3_04_USO_DEL_SUELO/SIOSE_Murcia_detalle_utm_etrs89/MapServer); MDE regional 1999 en `2_01_ELEVACION/MDE_1999_MURCIA_UTM_ETRS89` — [IMIDA elevación](https://geoportal.imida.es/gis/rest/services/2_01_ELEVACION?f=json)

### Inferences
- Con un recorte de 5 m de la parcela se calculan pendiente, orientación y posición relativa (hondonada = bolsa de frío) en el navegador o en Python sin GDAL. Así el riesgo de erosión y de helada se ve a escala de parcela. Usar SRTM (NASA) como comparación y para justificar "dato NASA".

### Gaps
- No se verificó la licencia IGN/CNIG en esta sesión (habitualmente CC BY 4.0, sin comprobar aquí). No se probó el SIOSE del IGN ni la descarga del CNIG.

---

## 8. Suelos y erosión (mapa de suelos de Murcia, LUCDEME, INES, IGME)

### Takeaway
El IMIDA publica un mapa de suelos regional consultable (tipo FAO, p. ej. "Xerosoles cálcicos", y si es fase salina), con capas de puntos de perfiles y de capa arable. Es grueso (el polígono del punto mide 228 km²), pero vale como contexto. El INES (erosión) está en el IMIDA y en el MITECO. **Suelos IMIDA KEEP (como contexto)**; **INES OPTIONAL**; **IGME geología DROP**; **LUCDEME Murcia** no encontrado en digital.

### Cited Findings
- `3_04_USO_DEL_SUELO/Suelos`: capas 0 "Puntos de la capa arable", 1 "Puntos de los perfiles", 2 "Suelos"; fuente: Consejería de Agricultura, Agua y Medio Ambiente de la Región de Murcia (CIDA y DG Medio Ambiente) y Ministerio de Medio Ambiente — [Suelos MapServer](https://geoportal.imida.es/gis/rest/services/3_04_USO_DEL_SUELO/Suelos/MapServer?f=json)
- Consulta en el punto (capa 2) → `SUELO_1: "Xerosoles cálcicos"`, `F_SALINA: "NO"`, `REGIMEN: "Dominante"`, área del polígono ≈ 228 km² — [Suelos query](https://geoportal.imida.es/gis/rest/services/3_04_USO_DEL_SUELO/Suelos/MapServer/2/query?geometry=-0.97,37.72&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=false&f=json)
- INES en el IMIDA (`3_04_USO_DEL_SUELO/INES`, capa "Puntos INES"; fuente DG Conservación de la Naturaleza, Tragsatec) — [INES MapServer](https://geoportal.imida.es/gis/rest/services/3_04_USO_DEL_SUELO/INES/MapServer?f=json); descargas INES de la CA de Murcia en el MITECO — [MITECO INES Murcia](https://www.miteco.gob.es/es/biodiversidad/temas/inventarios-nacionales/inventario-nacional-erosion-suelos/descarga_ines_murcia.html); WMS INES 2002–2019 (erosión laminar y en regueros) — [ficha IDEE](https://www.idee.es/csw-codsi-idee/srv/api/records/9876d351-7476-4a39-b45d-cd41e98a4325)
- Mapa geológico IGME de Murcia 1:200.000 (ArcGIS REST) — [IGME GeologicoMurcia_200](https://mapas.igme.es/gis/rest/services/Cartografia_Geologica/IGME_GeologicoMurcia_200/MapServer)
- LUCDEME en digital solo encontrado para Almería y Granada (REDIAM; 132 hojas 1:100.000 del sureste) — [REDIAM LUCDEME](https://portalrediam.cica.es/geonetwork/srv/api/records/9840a0f6-c27e-4fe6-80e9-56a7ee65e996)

### Inferences
- El tipo de suelo y la salinidad sirven para avisos cualitativos ("suelo calizo: cuidado con cultivos sensibles a la clorosis"; "fase salina: penalizar lechuga/fresa"). Para propiedades numéricas (textura, materia orgánica, capacidad de agua) habrá que tirar de una fuente global (SoilGrids/ISRIC) o de los puntos de perfil del IMIDA, que no se han inspeccionado.

### Gaps
- No se inspeccionaron los atributos de las capas de puntos de perfil y de capa arable (¿pH, CE, textura?).
- No se encontró la versión digital del LUCDEME de Murcia.

---

## 9. Seguro agrario (Agroseguro/ENESA): ¿hay mapas abiertos de riesgo de helada o pedrisco por municipio?

### Takeaway
No se encontró ningún dataset abierto con riesgo o siniestralidad por municipio. Hay notas de prensa, folletos y guías del plan de seguros; los datos municipales se han cedido a investigadores bajo petición. **DROP.** Para el riesgo de helada es mejor calcularlo con SIAM (informe de bajas temperaturas, horas frío) + MDT05 + NASA POWER.

### Cited Findings
- Un TFM usó partes de siniestro de pedrisco en frutales 2001–2010 que Agroseguro facilitó en Excel (fecha, municipio, causa, superficie) — [TFM Univ. León](https://grupos.unileon.es/ingecart/files/2014/05/TFM_GuillermoMarques2012.pdf)
- Agroseguro publica notas de prensa con siniestros (p. ej. tormentas de pedrisco abril–mayo 2026) y jornadas regionales (frutales Murcia, diciembre 2025) — [NP pedrisco 2026](https://agroseguro.es/wp-content/uploads/2026/05/NP_Tormentas-pedrisco-abril-y-mayo-2026__.pdf), [Jornada frutales Murcia](https://agroseguro.es/wp-content/uploads/2025/12/Jornada-frutales_Murcia_Dic_11.pdf)
- ENESA publica guías del plan de seguros (PDF) — [Guía plan 2022](https://servicio.mapa.gob.es/eu/enesa/publicaciones/guia_plan2022_tcm35-615530.pdf)
- Alternativa local: el portal SIAM ofrece "Informe de bajas temperaturas" y "Informe sobre horas frío para fruticultura" — [SIAM](http://siam.imida.es/apex/f?p=101:1)

### Inferences
- Se puede citar el seguro en el pitch como motivación ("el pedrisco y las heladas cuestan X"), pero el indicador de riesgo de la herramienta debe salir de datos climáticos.

### Gaps
- No se consultó el catálogo de datos abiertos del MAPA/ENESA específicamente; podría haber estadísticas de contratación por provincia.

---

## 10. IoT y sensores abiertos en la agricultura de Murcia

### Takeaway
No hay una red pública de sensores agrícolas IoT con datos abiertos en tiempo real, aparte de las estaciones SIAM (cada hora vía ArcGIS), las boyas del Mar Menor (IMIDA) y el SAIH de la CHS (visor). TTN Murcia es una comunidad incipiente. Para el compañero de IoT, el valor está en **construir el colector/gateway de datos de estaciones** y, si hay tiempo, un nodo simulado. Veredicto: **SIAM horario KEEP (como "feed IoT")**; **TTN/pilotos universitarios DROP** (no hay datos abiertos).

### Cited Findings
- TTN Murcia: comunidad en fase "Campaign", 23 miembros, mapa de gateways colaborativo — [TTN Murcia](https://www.thethingsnetwork.org/community/murcia/)
- IMIDA: póster Interreg SUDOE sobre seguimiento del riesgo de heladas con 3 parcelas experimentales, las 55 estaciones y una plataforma IoT basada en FIWARE; no confirma acceso público — [Póster IMIDA SUDOE](https://interreg-sudoe.eu/wp-content/uploads/2024/05/Poster-IMIDA-An-Gel-Perifel-ES.pdf)
- UPCT: plataforma de código libre que descarga automáticamente los datos de sensores IoT de parcelas agrícolas (TFM) — [iAgua UPCT](https://www.iagua.es/noticias/universidad-politecnica-cartagena/utilizan-herramientas-industria-40-optimizar-ahorro-agua); UPCT también desarrolló lectura de contadores de agua en entornos rurales sin cobertura — [esmartcity 2019](https://www.esmartcity.es/2019/10/28/upct-desarrolla-tecnologia-leer-contadores-agua-entornos-rurales-cobertura)
- Plataforma digital regional para servicios municipales inteligentes que integra sensores y portales de datos abiertos — [esmartcity 2023](https://www.esmartcity.es/2023/03/16/plataforma-digital-facilita-despliegue-servicios-municipales-inteligentes-region-murcia)
- Red estatal de boyas y sensores del Mar Menor (MITECO) con transmisión GSM/GPRS en tiempo real — [esmartcity 2025](https://esmartcity.es/2025/01/27/en-marcha-red-sensores-boyas-monitorizar-estado-ambiental-mar-menor), [MITECO licitación 2023](https://www.miteco.gob.es/eu/prensa/ultimas-noticias/2023/03/el_gobierno_licitalaprimerareddeboyasysensoresparasuministrarinf.html)
- Feeds en vivo consultables: `SIAM_DATOS` capa 1 (`SIAM_ULTIMO_DATO_HORARIO`) y `MARMENOR_BOYAS` (datos del día actual) — [SIAM_DATOS](https://geoportal.imida.es/gis/rest/services/3_14_ASPECTOS_GEOGRAFICOS_DE_CARACTER_METEOROLOGICO/SIAM_DATOS/MapServer?f=json), [MARMENOR_BOYAS](https://geoportal.imida.es/gis/rest/services/PROYECTOS/MARMENOR_BOYAS/MapServer?f=json)

### Inferences
- Historia de demo para el especialista en redes: "La NASA ve la parcela desde el espacio; la red SIAM la mide desde el suelo cada hora; nuestro colector une las dos fuentes". Implementación: cron cada hora → consulta ArcGIS → base de datos de series temporales → la app calcula ET0 acumulada y grados-día y lo compara con NASA POWER/SMAP.
- No se encontró la cobertura real de gateways de TTN en el Campo de Cartagena; no conviene prometer un despliegue LoRa real.

### Gaps
- No se encontraron APIs públicas de sensores de los ayuntamientos (Murcia, Cartagena) ni de CEBAS-CSIC o UMU para agricultura.
- No se comprobó si la consulta a la capa horaria SIAM devuelve datos (solo se vio su estructura; la capa diaria sí devolvió 55 estaciones).

---

## 11. Registro de pruebas en vivo y veredictos resumidos

### Takeaway
De las fuentes sin clave, funcionan rápido y con JSON/GeoTIFF: SIGPAC hubcloud (punto, OGC API, WMS, ATOM), geoportal ArcGIS del IMIDA (SIAM, suelos, nitratos, CHS, SIGPAC histórico, horas frío), CSV SIAM del CKAN, IGN WCS/WMS y la API CKAN regional. Fallan o están rotos: el endpoint SIGPAC antiguo, los ficheros "tiempo real" SIAM del CKAN, el JSON de estaciones de transparencia.carm.es, la URL antigua de SiAR y el WMS del MCA. AEMET y SiAR necesitan credenciales (no se pidieron).

### Cited Findings
Tabla de pruebas (13-nov-2026, `curl -sS -L --compressed --max-time 60`):

| # | Fuente | URL probada | HTTP | Tiempo | Muestra / nota |
|---|---|---|---|---|---|
| 1 | SIGPAC punto | [recinfobypoint](https://sigpac-hubcloud.es/servicioconsultassigpac/query/recinfobypoint/4258/-0.97/37.72.json) | 200 | 0,22 s | `uso_sigpac FY`, 4,924 ha, `altitud 42`, WKT (gzip, usar `--compressed`) |
| 2 | SIGPAC OGC colecciones | [collections](https://sigpac-hubcloud.es/ogcapi/collections?f=json) | 200 | 0,22 s | recintos, cultivo_declarado, elementos_paisaje_* |
| 3 | SIGPAC cultivo declarado | [items bbox](https://sigpac-hubcloud.es/ogcapi/collections/cultivo_declarado/items?f=json&bbox=-0.9705,37.7195,-0.9695,37.7205&limit=5) | 200 | 0,22 s | `parc_producto 153` (melón), regadío, 10.300 m² |
| 4 | SIGPAC antiguo | [ServiciosVisorSigpac](https://sigpac.mapa.gob.es/fega/ServiciosVisorSigpac/query/recinfobypoint/4258/-0.97/37.72.json) | 400 | 0,14 s | "Bad Request" (abandonado) |
| 5 | SIGPAC WMS | [GetCapabilities](https://sigpac-hubcloud.es/wms?request=GetCapabilities&service=WMS) | 200 | 0,26 s | capas recinto, cultivo_declarado |
| 6 | FEGA ATOM | [es.fega.sigpac.xml](https://www.fega.gob.es/atom/es.fega.sigpac.xml) | 200 | 0,17 s | rec 2025/2026, ep 2025/2026, cd 2025 |
| 7 | Cultivo declarado 2025 Cartagena | [30016 gpkg.zip](https://www.fega.gob.es/atom/2025/cd_2025/30%20-%20MURCIA/30016_cd_2025_20250110_gpkg.zip) | 200 | 1,16 s | 6,65 MB; 13.936 filas; recinto 502/141/1 = lechuga (155) |
| 8 | Códigos SIGPAC | [sigpac_codes_2025.zip](https://www.fega.gob.es/atom/2025/sigpac_codes_2025.zip) | 200 | 0,08 s | 23 KB; cod_producto.csv 888 filas |
| 9 | CKAN Murcia | [package_search](https://datosabiertos.regiondemurcia.es/api/3/action/package_search?q=cultivos&rows=5) | 200 | 0,23 s | 38 resultados; `/catalogo/api/...` → 404 |
| 10 | SIAM estaciones CSV | [IMIDA_estaciones.csv](https://datosabiertos.carm.es/odata/Agricultura/IMIDA_estaciones.csv) | 200 | 0,23 s | 50 estaciones, Latin-1 |
| 11 | SIAM diario TP42 | [IMIDA_Diario_TP42.csv](https://datosabiertos.carm.es/odata/Agricultura/IMIDA_Diario_TP42.csv) | 200 | 0,55 s | 2000-01-01…2018-12-31, incluye `eto` |
| 12 | SIAM tiempo real CKAN | [ImidaMeteoHora.json](https://datosabiertos.carm.es/rest-services/services/restFile/ImidaMeteoHora.json) | 500 | 0,16 s | "No se ha localizado un servicio" (roto) |
| 13 | SIAM último día (ArcGIS) | [SIAM_DATOS/0/query](https://geoportal.imida.es/gis/rest/services/3_14_ASPECTOS_GEOGRAFICOS_DE_CARACTER_METEOROLOGICO/SIAM_DATOS/MapServer/0/query?where=1%3D1&outFields=*&returnGeometry=false&f=json) | 200 | 6,8 s | 55 estaciones, fecha 2026-11-12, `ETO_PM_FAO` |
| 14 | SIAM portal | [siam.imida.es](http://siam.imida.es/apex/f?p=101:1) | 200 | 0,31 s | Oracle APEX, formularios con sesión |
| 15 | SiAR web nueva | [siarweb](https://servicio.mapa.gob.es/siarweb/) | 200 | 0,19 s | `www.siar.es` redirige aquí; `/websiar/` → 404 |
| 16 | SiAR API sin token | [Info/ESTACIONES](https://servicio.mapa.gob.es/siarapi/API/V1/Info/ESTACIONES) | 400 / 500 | <0,2 s | requiere token REGEUS |
| 17 | AEMET sin clave | [inventario estaciones](https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones) | 200 | 0,08 s | cuerpo vacío: hace falta `api_key` |
| 18 | IGN WCS MDT05 | [GetCoverage](https://servicios.idee.es/wcs-inspire/mdt?SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage&COVERAGEID=Elevacion4258_5&SUBSET=Lat(37.719,37.721)&SUBSET=Long(-0.971,-0.969)&FORMAT=image/tiff) | 200 | 0,13 s | GeoTIFF 44×44, centro 42 m |
| 19 | IGN PNOA WMS | [GetCapabilities](https://www.ign.es/wms-inspire/pnoa-ma?SERVICE=WMS&REQUEST=GetCapabilities) | 200 | 0,07 s | mapa base |
| 20 | MAPA MCA WMS | [GetCapabilities](https://wms.mapama.gob.es/sig/Agricultura/MapaCultivos2000-2010/wms.aspx?SERVICE=WMS&REQUEST=GetCapabilities) | 200 (error) | 0,18 s | `ServiceExceptionReport` NullReferenceException |
| 21 | CHS SAIH iVisor | [inicial.php](https://saihweb.chsegura.es/apps/ivisor/inicial.php) | 200 | 0,65 s | HTML+AJAX, requiere aceptar protocolo |
| 22 | CHS piezómetros (IMIDA) | [CHS_DATOS/11/query](https://geoportal.imida.es/gis/rest/services/PROYECTOS/CHS_DATOS/MapServer/11/query?geometry=-1.05,37.65,-0.85,37.80&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=false&f=json) | 200 | 1,28 s | 8 piezómetros Campo de Cartagena |
| 23 | Zonas vulnerables (IMIDA) | [ZVN/0/query](https://geoportal.imida.es/gis/rest/services/PROYECTOS/ZONAS_VULNERABLES_NITRATOS/MapServer/0/query?geometry=-0.97,37.72&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=false&f=json) | 200 | 0,91 s | ES62_01 Campo de Cartagena |
| 24 | Suelos (IMIDA) | [Suelos/2/query](https://geoportal.imida.es/gis/rest/services/3_04_USO_DEL_SUELO/Suelos/MapServer/2/query?geometry=-0.97,37.72&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=false&f=json) | 200 | 0,19 s | Xerosoles cálcicos, no salino |
| 25 | Cultivos 2005 (IMIDA) | [Cultivos/0/query](https://geoportal.imida.es/gis/rest/services/2_02_CUBIERTA_TERRESTRE/Cultivos/MapServer/0/query?geometry=-0.97,37.72&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=false&f=json) | 200 | 0,63 s | `GRUP_CULT IV` (invernadero) |
| 26 | Horas frío (IMIDA) | [identify](https://geoportal.imida.es/gis/rest/services/3_14_ASPECTOS_GEOGRAFICOS_DE_CARACTER_METEOROLOGICO/Modelos_horas_frio/MapServer/identify?geometry=-0.97,37.72&geometryType=esriGeometryPoint&sr=4326&layers=all&tolerance=1&mapExtent=-1.0,37.7,-0.9,37.8&imageDisplay=400,400,96&returnGeometry=false&f=json) | 200 | 0,65 s | 360 h / 221 h <7 °C |
| 27 | datos.gob.es API | [apidata](https://datos.gob.es/apidata/catalog/dataset/title/cultivo.json?_pageSize=10) | 200 | 0,50 s | nada relevante para Murcia |
| 28 | CARM precios semanales | [listado ESAM](https://esam.carm.es/informes-semanales-de-precios-campo/) | 200 | — | 135 enlaces PDF, último semana 45/2026 |

Veredictos (cada fuente usable en menos de 30 min salvo indicación):

| Fuente | Aporta a la herramienta de rotación | Veredicto |
|---|---|---|
| SIGPAC hubcloud (punto/OGC/WMS) | Polígono, superficie, pendiente, altitud, regadío, uso | **KEEP** |
| Cultivo declarado FEGA (API 2026 + GPKG 2025) | Rotación actual real (2 campañas) + rotaciones típicas de la zona | **KEEP** |
| SIGPAC histórico IMIDA 2011–2024 + mapa cultivos 2005 | Cambios de uso en ~20 años | OPTIONAL |
| SIAM: ArcGIS último dato + CSV 2000–2018 | Clima en suelo, ET0, "feed IoT" | **KEEP** |
| SiAR API | ET0, integrales térmicas en provincias vecinas; registro NIF | OPTIONAL |
| AEMET OpenData | Series largas aeropuerto San Javier/Alcantarilla; clave por email | OPTIONAL |
| ZVN + zonas Mar Menor (IMIDA/MITECO) | Restricción de nitrógeno por parcela | **KEEP** |
| Piezómetros/nitratos CHS vía IMIDA | Estrés del acuífero, contexto | OPTIONAL |
| SAIH/iVisor CHS directo, Canal Mar Menor/SDC | Sin API, scraping | DROP |
| IGN WCS MDT05 + PNOA WMS | Pendiente/frío a 5 m; mapa base | **KEEP** |
| Suelos IMIDA | Tipo de suelo, salinidad (cualitativo) | **KEEP** (contexto) |
| INES erosión | Contexto de erosión | OPTIONAL |
| NDVI S2 IMIDA 2019–2026 | Fenología de la parcela (validación de NASA HLS) | OPTIONAL |
| Precios CARM (PDF semanal) + MAPA ISC | Ingresos por cultivo (tabla manual) | **KEEP** (manual) |
| ESYRCE / Anuario Murcia / CREM | Rendimientos (tabla manual) | **KEEP** (manual) |
| MCA 1980–2010 MAPA | Demasiado antiguo/grueso; WMS con error | DROP |
| CKAN regional / datos.gob.es | Solo para encontrar SIAM | OPTIONAL |
| Agroseguro/ENESA | Sin datos abiertos | DROP |
| TTN Murcia / pilotos IoT universitarios | Sin feeds públicos | DROP |

### Inferences
- Una "tubería mínima" para la demo cabe en ~6 llamadas sin clave: SIGPAC punto → cultivo declarado (API + GPKG 2025 del municipio, precargado) → ZVN/Mar Menor → suelos → MDT05 → SIAM último día + CSV histórico de la estación más cercana. Todo se puede cachear en JSON para la parcela demo.
- Recomendación de parcela demo: un recinto `TA`/`TH` de regadío en Torre-Pacheco o Cartagena con cultivo declarado en 2025 y 2026 distinto (como el 502/141/1, lechuga→melón), dentro de la ZVN ES62_01 y a menos de 5 km de CA12 o TP91.

### Gaps
- Ningún servicio documenta límites de uso (salvo SiAR); no se hicieron pruebas de carga.
- Las conclusiones de "campaña 2026" para la OGC API se basan en una sola comparación de recinto.
- Nada de esto se ha añadido aún a `context/` ni a `LOG.md` del repo; lo debe hacer el agente coordinador o un humano.
