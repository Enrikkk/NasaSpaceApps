# Precios agrarios con licencia abierta o reutilización explícita (gonzalo, 2026-11-14)

Alcance: precios percibidos / en origen de lechuga, melón, brócoli, alcachofa, haba verde, cebada y limón, series 2005-2024 o más, España o Murcia.
Método: búsqueda web más comprobación directa de cada fuente (HEAD o descarga pequeña, lectura de la licencia en la página oficial). Fecha de las comprobaciones: 2026-11-14. No se ha escrito nada fuera de este fichero.
Contexto: los precios CARM/ESAM (`esam.carm.es`) NO son abiertos (ver `submission/data-citations.md`, fila CARM/ESAM) y no se usan aquí.

## 1. Resultado en tres líneas

- Las tres fuentes con reutilización clara (MAPA, Eurostat, FAOSTAT) cubren los siete cultivos a escala **nacional (España)**. No he encontrado ninguna serie **de Murcia** con licencia abierta.
- MAPA "Índices y Precios Percibidos Agrarios" es la única con **serie mensual 2005-2026** de seis de los siete cultivos (brócoli solo 2005-2014). Eurostat y FAOSTAT dan el **valor anual** y coinciden con la columna "Anual" de MAPA en 2024 (comprobado, sección 4).
- La licencia de MAPA no es una CC: es la reutilización de la Ley 37/2007 con la condición de citar la fuente. Eurostat y FAOSTAT sí declaran CC BY 4.0 (FAOSTAT) o reutilización autorizada citando la fuente (Eurostat).

## 2. Tabla comparativa

Unidades: MAPA y Eurostat en €/100 kg (dividir entre 100 para €/kg); FAOSTAT en LCU/tonne (en España LCU = EUR; dividir entre 1000 para €/kg). Comprobado que los valores FAOSTAT son los de MAPA x10 (sección 4).

| Fuente | Cultivos (confirmados en el fichero) | Periodicidad y años | Formato / acceso | Licencia (frase oficial corta) | Atribución |
|---|---|---|---|---|---|
| **A. MAPA, Índices y Precios Percibidos Agrarios** (precio percibido nacional, € por 100 kg) | Lechuga, melón, alcachofa, haba verde, cebada, limón: sí, 2005-2026. Brócoli ("COL BROCOLI"): solo 2005-2014 | Mensual y media anual. 2005-jul 2026 (2026 parcial, provisional) | 5 Excel .xlsx, 140-212 KB, HEAD 200 y descargados. Hoja `PrePer1` cereales, `PrePer3` hortalizas, `PrePer4` cítricos | "puede ser utilizada sin necesidad de autorización expresa, siempre que se cite la fuente de los documentos objeto de reutilización" | Sí: citar fuente y mantener los metadatos de fecha y condiciones de reutilización |
| **B. MAPA, Precios Medios Nacionales** (semanal, precio en origen) | Lechuga romana (€/100 ud, no kg), melón piel de sapo (€/100 kg), alcachofa, haba verde, limón, cebada pienso y malta (€/t), brócoli (fila desde 2020, valores desde 2021) | Semanal. 2019-semana 36 de 2026 | 8 Excel .xlsx por año, 59-117 KB, descargados | Misma que A (aviso legal de MAPA) | Sí, igual que A |
| **C. Eurostat `apri_ap_crpouta`** (precios de venta absolutos, cultivos) | Lechuga al aire libre, melones, cebada (total, pienso, maltera), limón, haba **seca** ("dried broad beans"), coliflor. **No** hay brócoli, alcachofa ni haba verde | Anual, 2000-2024 (actualizado 2025-05-15). Para ES 2005-2024: 20 años por producto | API JSON, petición de prueba HTTP 200, 49 KB | "Reuse of statistical data ... for commercial or non-commercial purposes is authorised provided the source is acknowledged" | Sí: citar el dataset y la fecha de acceso; indicar si se modifican los datos |
| **D. FAOSTAT, Producer Prices (dominio PP)** | Los siete: Lettuce and chicory, Cantaloupes and other melons, **Cauliflowers and broccoli** (agrupado), Artichokes, Broad beans and horse beans green, Barley, Lemons and limes | Anual 1991-2024 (todos los años de 2005 a 2024; también mensual 2010-2024 con huecos) | ZIP bulk de 11,7 MB, descargado y leído. Valores marcados "A = Official value" | "licensed under the Creative Commons Attribution-4.0 International licence (CC BY 4.0)" | Sí, formato exacto de cita FAO en sección 5 |

URLs exactas:

- A. Página: https://www.mapa.gob.es/es/estadistica/temas/estadisticas-agrarias/economia/precios-percibidos-pagados/precios-percibidos-por-los-agricultores-y-ganaderos
  - 2005-2014: https://www.mapa.gob.es/dam/mapa/contenido/estadisticas/temas/estadisticas-agrarias/1.economicas/indices--precios-y-salarios-agrarios/indices-y-precios-percibidos-agrarios/indicesypreciospercibidosenero2005-diciembre2014.xlsx
  - 2015-2023: https://www.mapa.gob.es/dam/mapa/contenido/estadisticas/temas/estadisticas-agrarias/1.economicas/indices--precios-y-salarios-agrarios/indices-y-precios-percibidos-agrarios/indicesypreciospercibidosagrariosenero2015-diciembre2023.xlsx
  - 2020-2025: https://www.mapa.gob.es/dam/mapa/contenido/estadisticas/temas/estadisticas-agrarias/1.economicas/indices--precios-y-salarios-agrarios/indices-y-precios-percibidos-agrarios/indicesypreciospercibidosagrariosenero2020-diciembre2022.xlsx
  - 2024-2026: https://www.mapa.gob.es/dam/mapa/contenido/estadisticas/temas/estadisticas-agrarias/1.economicas/indices-y-precios-agrarios/indices-y-precios-percibidos-agrarios/indices-y-precios-percibidos-agrarios--enero-2023-septiembre-2025-.xlsx
  - Hay además uno de 2010-jun 2018 (no hace falta). Los rangos de años de cada fichero son los que contiene realmente, no los del nombre del fichero (el último se llama "enero 2023-septiembre 2025" pero contiene 2024-2026; el de 2020 contiene 2020-2025). Donde se solapan, usar el fichero más reciente.
  - Metodología (PDF base 2020): https://www.mapa.gob.es/dam/mapa/contenido/estadisticas/temas/estadisticas-agrarias/1.economicas/indices--precios-y-salarios-agrarios/indices-y-precios-percibidos-agrarios/metodologiadeindicesypreciospercibidosagrariosbase2020.pdf
- B. Página: https://www.mapa.gob.es/es/estadistica/temas/estadisticas-agrarias/economia/precios-medios-nacionales/default.aspx
  - Ejemplo (2024): https://www.mapa.gob.es/dam/mapa/contenido/estadisticas/temas/estadisticas-agrarias/1.economicas/precios-medios/precios_medios_nacionales_2024s52.xlsx
  - El resto son `precios_medios_nacionales_2019v2.xlsx`, `_2020v2`, `_2021s52`, `_2022`, `_2023s52`, `_2025-s52`, `_2026-s36` en la misma carpeta `.../precios-medios/`.
- Licencia de A y B (aviso legal de MAPA): https://www.mapa.gob.es/es/atencion-al-ciudadano/aviso-legal
- C. Metadatos: https://ec.europa.eu/eurostat/cache/metadata/en/apri_ap_esms.htm
  - Petición de prueba que funcionó: `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/apri_ap_crpouta?format=JSON&lang=EN&geo=ES&sinceTimePeriod=2005`
  - Códigos de producto (dimensión `prod_veg`): 04192100 lechuga al aire libre, 04199913 melones, 01300000 cebada, 06230000 limones, 02230000 haba seca, 04110000 coliflor. Dimensión `currency`: EUR y NAC. No he probado filtrar por `currency` ni `prod_veg` en la URL; filtrar al leer el JSON.
  - Licencia: https://ec.europa.eu/eurostat/help/copyright-notice
- D. Base: https://www.fao.org/faostat/en/#data/PP
  - Bulk usado: https://bulks-faostat.fao.org/production/Prices_E_All_Data_(Normalized).zip (columna `Element` = "Producer Price (LCU/tonne)", `Months` = "Annual value", `Area` = Spain)
  - Licencia: https://www.fao.org/contact-us/terms/db-terms-of-use/en/

Nota de acceso a mapa.gob.es: el servidor presenta una cadena TLS que Node/WebFetch rechaza ("self signed certificate in certificate chain"). Con curl se verificó usando el certificado FNMT G2R que ya está en el repo (`app/backend/engine/sources/certs/fnmt_g2r_root.pem` en la rama `t012-motor-nucleo`), sin desactivar TLS. Los .xlsx se leyeron con un parser propio de zip+XML (no hay openpyxl instalado).

## 3. Cobertura por cultivo (qué fuente usar)

| Cultivo | Serie mensual 2005-2024 | Serie anual 2005-2024 | Observaciones |
|---|---|---|---|
| Lechuga | A (todos los meses, sin huecos) | A, C (al aire libre), D | A es lechuga genérica "100 kg". B da romana por 100 unidades. **Iceberg y romana por separado: NO CONFIRMADO con licencia abierta** |
| Melón | A (con meses sin dato fuera de temporada: 3 a 5 meses sin precio al año, p. ej. 2024 sin ene-mar ni nov-dic) | A, C ("Melons"), D | A no distingue piel de sapo; B sí ("Melón Piel de Sapo"), semanal 2019-2026 |
| Brócoli | A solo 2005-2014 (sin huecos). Después, solo B (semanal, desde 2021) | D: "Cauliflowers and broccoli" agrupado, 1991-2024. C: solo coliflor | **Hueco**: no hay serie mensual ni anual de brócoli puro 2015-2024 con licencia abierta |
| Alcachofa | A (2-3 meses al año sin precio, verano) | A, D | C no la tiene |
| Haba verde | A (4-5 meses sin precio, verano-otoño) | A, D ("green"), C solo haba seca | Cuidado: C "dried broad beans" es otro producto (30,39 €/100 kg en 2024 frente a 125,4 de la verde) |
| Cebada | A (1 mes sin dato al año desde 2015) | A, C, D | B da cebada pienso y malta en €/t |
| Limón | A (sin huecos) | A, C, D | A es precio **sobre árbol** (ver sección 6) |

## 4. Comprobación cruzada (calidad de los datos)

Precio anual 2024 en €/100 kg. A = columna "Anual" del Excel de MAPA; C = Eurostat; D = FAOSTAT dividido entre 10.

| Cultivo | A MAPA 2024 | C Eurostat 2024 | D FAO 2024 |
|---|---|---|---|
| Lechuga | 31,42 | 31,42 | 31,42 |
| Melón | 47,57 | 47,57 | 47,57 |
| Alcachofa | 96,42 | no existe | 96,42 |
| Haba verde | 125,40 | no existe (la seca: 30,39) | 125,40 |
| Cebada | 20,15 | 20,15 | 20,15 |
| Limón | 30,80 | 30,80 | 30,80 |
| Brócoli | no hay (A termina en 2014) | no hay (coliflor: 69,06) | 69,06 (coliflor+brócoli agrupado) |

Conclusión: en 2024 las tres fuentes dan **la misma cifra** (Eurostat y FAOSTAT redistribuyen el dato oficial de España, flag "A = Official value" en FAOSTAT). No son tres fuentes independientes.
Precaución en años antiguos: no son idénticas en todos los años. Ejemplos: lechuga 2005 MAPA (fichero 2005-2014) 54,47 frente a FAOSTAT 51,1; lechuga 2020 MAPA (fichero 2020-2025) 25,17 frente a FAOSTAT 24,73. Hay revisiones y cambios de ponderación entre bases (2005, 2015, 2020). No encadenar ficheros sin elegir uno por año y anotar la versión.

Fuentes de estas cifras: los .xlsx de A (columna `Anual`), la API de Eurostat y el ZIP de FAOSTAT citados en la sección 2.

## 5. Licencias y cita (texto para `submission/data-citations.md`)

- **MAPA (A y B)**. Aviso legal de mapa.gob.es: reutilización sin autorización expresa citando la fuente, salvo contenidos de terceros con derechos propios; hay que conservar "los metadatos sobre la fecha de actualización y las condiciones de reutilización". Cita sugerida: "Fuente: Ministerio de Agricultura, Pesca y Alimentación (MAPA), Índices y Precios Percibidos Agrarios / Precios Medios Nacionales, https://www.mapa.gob.es/es/estadistica/temas/estadisticas-agrarias/economia/ (consultado 2026-11-14). Reutilización conforme al aviso legal de MAPA (Ley 37/2007)." La licencia no es CC; no hay un identificador SPDX. URL: https://www.mapa.gob.es/es/atencion-al-ciudadano/aviso-legal
  - Reserva: el aviso excluye "contenidos sobre los que existan derechos de propiedad intelectual o industrial por parte de terceros". Los precios son estadística oficial del propio MAPA, pero el aviso es el del portal; no he encontrado un aviso específico de la estadística. Riesgo bajo, anotarlo.
- **Eurostat (C)**. "Reuse ... is authorised provided the source is acknowledged." Para datasets modificados la página de Eurostat pide la cita "Source: [Eurostat dataset datacode link], [access date]" y declarar que se han modificado los datos. Las excepciones (datos de terceros, países fuera de UE/EFTA/candidatos) no afectan a España. URL: https://ec.europa.eu/eurostat/help/copyright-notice
- **FAOSTAT (D)**. CC BY 4.0 más términos adicionales. Cita obligatoria: "FAO. [año de última actualización]. [Base: dataset]. [Accedido el DD Mes AAAA]. [URL] Licence: CC-BY-4.0." Ejemplo: "FAO. 2026. FAOSTAT: Producer Prices. Accedido el 14 de noviembre de 2026. https://www.fao.org/faostat/en/#data/PP Licence: CC-BY-4.0." (La fecha del bulk comprobado es 2026-10-09; confirmar el año de actualización en la página.)
  - **Términos adicionales que importan al equipo**: los datos "shall not be used for or in conjunction with the promotion of a commercial enterprise and/or its product(s) or services (s)" y no se puede sugerir respaldo de FAO. Si Agrockham se presenta como producto comercial, hay que decidirlo con el equipo; para una demo de hackathon como proyecto de investigación el riesgo es bajo, pero es un punto a decidir (humanos). También hay una cláusula de "third party exceptions" (el usuario debe comprobar si hay datos de terceros).
  - URL de los términos: https://www.fao.org/contact-us/terms/db-terms-of-use/en/

Estas tres entradas ya están en `submission/data-citations.md` (añadidas por gonzalo el 2026-11-14).

## 6. Precio percibido frente a precio en origen y qué usar para el margen

**Precio percibido (A)**: precio de mercado "que percibe el agricultor o ganadero por la venta de los productos agrarios, de calidad media, situados en la explotación agraria y sin I.V.A." (metodología MAPA base 2020, https://www.mapa.gob.es/dam/mapa/contenido/estadisticas/temas/estadisticas-agrarias/1.economicas/indices--precios-y-salarios-agrarios/indices-y-precios-percibidos-agrarios/metodologiadeindicesypreciospercibidosagrariosbase2020.pdf). Notas del propio Excel de MAPA (hoja `PrePer3`, `PrePer4` y `PrePer1` de los ficheros A):
- Hortalizas (lechuga, melón, alcachofa, haba verde): "precio a granel, sobre almacén comprador".
- Cítricos (limón): "precio sobre árbol sin recolectar".
- Cereales (cebada): "precio a granel, sobre almacén agricultor o cooperativa".
- Es un promedio nacional ponderado por una matriz provincial, no el precio de una finca ni de Murcia.

**Precio en origen (B)**: precios medios ponderados "obtenidos a partir de las cotizaciones registradas en los mercados de mayor representatividad a nivel nacional" con ponderaciones fijas por mercado (https://www.mapa.gob.es/es/estadistica/temas/estadisticas-agrarias/economia/precios-medios-nacionales/default.aspx). La "posición comercial" del Excel semanal, nota (13) para hortalizas: "Granel, s/finca, almacén agricultor, alhóndiga, lonja, etc."; nota (12) limón: "s/árbol"; nota (1) cereales: "Salida de almacén cargado o entregado al transformador después de intermediario". Es decir: cotización semanal en lonja o finca, mucho más volátil, con otra unidad en la lechuga (por 100 unidades) y sin ponderación por producción de la campaña.

**Precio mayorista/destino (Mercamurcia, Mercabarna)**: incluye embalaje, transporte y margen de intermediario. No sirve para el margen del agricultor y no he encontrado licencia (sección 7).

**Para el margen del motor**: usar el **percibido (A, o su anual en C/D)** en €/kg multiplicado por el rendimiento (kg/ha), porque es el ingreso que llega al agricultor y es la serie larga y mensual. Dos precauciones:
1. **Coherencia de costes**: el limón se percibe "sobre árbol sin recolectar", así que el precio no incluye la recolección, que paga el comprador. Si el coste de cultivo incluye recolección, el margen estaría infravalorado. En hortalizas "sobre almacén comprador" puede o no incluir la recolección pagada por el agricultor; esto NO está confirmado, hay que mirar el desglose de costes del IMIDA/ECREA que ya usa el motor para decidir qué costes de recolección y embalaje se restan.
2. **Unidad de la lechuga**: A está en €/100 kg, B en €/100 ud. No hay en estas fuentes el peso por unidad para convertir; no inventar una conversión.
3. **Estacionalidad**: A tiene meses sin precio (melón, alcachofa, haba verde). Si el motor pide precio mensual, usar solo los meses de campaña; para anual usar la columna "Anual" o C/D.

## 7. Descartadas o no confirmadas (explícito)

| Fuente | Estado | Motivo y URL |
|---|---|---|
| **CARM / ESAM** (precios de campo semanales, `esam.carm.es`) | DESCARTADA | Solo uso personal no comercial y sin modificación, según el aviso de esam.carm.es/legal que ya revisó Enrique (`submission/data-citations.md`). No re-revisada por mí. Ejemplo de boletín: https://esam.carm.es/wp-content/uploads/2025/06/PRECIOS-CAMPO-SEMANA-22.pdf |
| **Portal de datos abiertos de la Región de Murcia** | SIN PRECIOS AGRARIOS | Listados los 980 conjuntos del API CKAN (https://datosabiertos.regiondemurcia.es/api/3/action/package_search): hay bancos de germoplasma (incluye "Colección de LECHUGAS" y "de MELONES", no son precios), meteorología SIAM/IMIDA y precios de bienes urbanos, pero ningún conjunto de precios de cultivos ni de lonja. |
| **Mercamurcia (mercado mayorista)** | NO CONFIRMADO, sin licencia hallada | `https://www.mercamurcia.com/` respondió con 114 bytes al comprobarlo y la búsqueda no halló un aviso legal ni condiciones de reutilización. Los precios mayoristas son además precio de destino. |
| **Mercabarna** | NO CONFIRMADO | Publica libros estadísticos anuales en PDF (p. ej. https://www.mercabarna.es/media/upload/pdf/llibre-estadistic-mercat-central-fruites-hortalisses-mercabarna-2025_1777970972.pdf) pero no he localizado aviso legal ni licencia de reutilización (la web no respondió desde aquí). Mercado catalán, no murciano y de destino. |
| **datos.gob.es** | NO CONCLUYENTE | La búsqueda del catálogo está tras un WAF (devuelve una página Incapsula) y el API por título no devolvió nada para "precios percibidos", "precios medios nacionales" ni "Murcia". Lo único localizado fue el dataset de Asturias https://datos.gob.es/es/catalogo/a03002951-precios-sector-agrario (no sirve para Murcia). Existe una solicitud ciudadana de datos para un API de precios agrícolas: https://datos.gob.es/en/solicitud-de-datos/api-rest-o-csv-plano-con-el-historico-completo-de-precios-agricolas-y-ganaderos-del |
| **UE, API de precios de frutas y hortalizas (agridata.ec.europa.eu)** | NO CONFIRMADO el acceso | La documentación (https://agridata.ec.europa.eu/extensions/API_Documentation/fruitandvegetables.html) dice que el API histórico se retiró en octubre de 2025 y lo sustituye uno por etapas (ex-packaging, farmgate, retail) bajo `https://api.tech.ec.europa.eu/agrifood`. Mis peticiones a `/api/fruitAndVegetable/pricesSupplyChain/products` dieron HTTP 500 y tiempo agotado; no comprobé qué productos incluye ni la licencia de ese dataset (los contenidos de la UE se publican en CC BY 4.0 por defecto según https://ec.europa.eu/info/legal-notice_en, sin confirmar para este API). |
| **Precios regionales o provinciales de MAPA (Murcia)** | NO CONFIRMADO | No encontré una tabla de precios percibidos por provincia o comunidad descargable. Los Excel de A son nacionales. El Anuario de Estadística de MAPA podría tenerlos; no lo he revisado. |
| **econet.carm.es / CREM** | NO REVISADO | Hay tablas agrarias de la CARM (https://econet.carm.es/inicio/-/crem/sicrem/pu590/pdf/sec38.pdf), pero no he leído su aviso legal ni confirmado si traen precios por cultivo. |

## 8. Huecos NO CONFIRMADOS (resumen)

1. **Precio específico de Murcia / Campo de Cartagena**: ninguna serie abierta localizada. Los precios nacionales son una aproximación; el motor debe etiquetarlos "nacional".
2. **Brócoli 2015-2024**: solo hay el valor anual agrupado coliflor+brócoli de FAOSTAT y la semanal de MAPA B (desde 2021). Opción: usar FAOSTAT agrupado y declararlo, o semanal agregada a mensual (calcular y documentar).
3. **Lechuga iceberg frente a romana**: A es lechuga genérica; B es romana en €/100 ud. Iceberg abierta, no encontrada.
4. **Melón piel de sapo mensual 2005-2018**: A es "melón" genérico. B solo desde 2019 y con semanas sin precio.
5. **Haba verde en C (Eurostat)**: solo existe la seca. No mezclar.
6. **Conversión de lechuga €/ud a €/kg**: sin peso unitario abierto.
7. **Precio de barbecho**: no aplica (no hay venta); el motor no necesita precio.
8. **Acceso a la API de precios de frutas y hortalizas de la UE**: no verificado.
9. **Frase exacta de licencia de MAPA para la estadística concreta**: solo existe el aviso general del portal. Si el equipo quiere seguridad adicional, preguntar a MAPA (BG de Análisis, Coordinación y Estadística; es el firmante de los Excel). No he enviado ningún correo.

## 9. Recomendación

**Rotación actual (melón + lechuga + barbecho):**
1. **Primaria: MAPA A** (precio percibido). Melón y lechuga, mensual 2005-2026, un solo editor, licencia clara (cita de fuente), unidad €/100 kg para ambos. Para el margen anual usar la columna "Anual" (lechuga sin huecos; melón 2024 = 47,57 €/100 kg, lechuga 2024 = 31,42 €/100 kg).
2. **Comprobación y respaldo: FAOSTAT D** (CC BY 4.0, identificador explícito, valor anual, una sola descarga de 11,7 MB, mismo valor que MAPA en 2024) y **Eurostat C** (API JSON ligera, sin descarga). Para el contrato y la sumisión, si se quiere una licencia con nombre estándar, citar D; si se quiere el dato original, citar A.
3. **Detalle estacional reciente: MAPA B** (piel de sapo y romana semanal 2019-2026), solo como ilustración o validación, no para la serie larga.

**Alternativas (siguientes cultivos del motor):** cebada, limón, alcachofa y haba verde ya están cubiertos con A (2005-2026) y D (anual). Brócoli: A 2005-2014 + D agrupado coliflor y brócoli + B desde 2021; declarar el hueco.

**Para la sumisión**: añadir a `submission/data-citations.md` las tres citas de la sección 5 (humano decide la formulación final) y las dos reservas: aviso general de MAPA (no CC) y el término "no promoción comercial" de FAO.

RESULT: done | Con licencia abierta o reutilización explícita quedan cubiertos a escala NACIONAL lechuga, melón, alcachofa, haba verde, cebada y limón (MAPA percibidos mensual 2005-2026 + FAOSTAT CC BY 4.0 y Eurostat anual 2005-2024, mismos valores en 2024) y brócoli solo parcial (MAPA mensual 2005-2014, FAOSTAT anual agrupado con coliflor, MAPA semanal desde 2021); NO hay precios abiertos específicos de Murcia (CARM/ESAM descartado, portal regional sin precios, Mercamurcia y Mercabarna sin licencia hallada) ni lechuga iceberg separada ni API UE de F&V verificada.
