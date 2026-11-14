# SIGPAC: viabilidad de integración en Agrockham

Revisado el 14-11-2026 por Arturo y su agente. Fuente señalada por Arturo: https://sigpac.mapa.gob.es/fega/visor/

**Conclusión: viable y relevante para el MVP.** La investigación del repo ya incluía esta familia de servicios; ahora se han vuelto a probar los accesos oficiales sobre la parcela de demo. Se recomienda reutilizar el pipeline de Gonzalo, no crear otro. Esta evaluación no modifica el contrato ni implica que la integración esté terminada.

## Qué aporta

- Delimitación del recinto para el mapa y para recortar observaciones satelitales.
- Identificación SIGPAC completa, superficie, pendiente, altitud, uso registrado y coeficiente de regadío.
- Cultivos declarados como registros administrativos separados del uso SIGPAC; pueden existir varios registros por recinto.
- Capas de elementos del paisaje y servicios cartográficos para futuras ampliaciones.

No aporta por sí solo textura/pH del suelo, meteorología, rendimiento real, costes ni volumen de agua disponible. El coeficiente de regadío no sustituye una dotación de agua ni su verificación legal. La información declarada no equivale a una observación satelital del cultivo presente.

## Prueba realizada

Punto de demo: longitud -0.98838, latitud 37.73830. Cuatro consultas, HTTP 200 sin cuenta/clave, entre 0,33 y 0,36 segundos en esta prueba; no es una garantía de disponibilidad. Cabecera observada `Access-Control-Allow-Origin: *` en las cuatro respuestas.

| Consulta | Resultado observado |
|---|---|
| REST por punto | Recinto 30/37/0/0/18/426/1; 4,0868 ha; pendiente 0,8; coeficiente regadío 100; altitud 53 m; uso TA; geometría WKT EPSG:4258 |
| Catálogo OGC | Recintos, cultivo declarado y elementos de paisaje de área/línea/punto |
| OGC recintos por bbox | Un polígono coincidente con el identificador de demo |
| OGC cultivo declarado por bbox | Dos registros devueltos para el recinto: uno con producto 20 y otro con producto vacío e indicador especial. No colapsarlos a ciegas en un único cultivo |

La prueba usó `limit=2`; el cliente definitivo debe seguir la paginación y comprobar geometría/identificador, no asumir que cualquier objeto del bbox es el seleccionado. Las respuestas de cultivo se inspeccionaron excluyendo `exp_*`.

Consulta reproducible sin dependencias:

```sh
curl --fail --compressed 'https://sigpac-hubcloud.es/servicioconsultassigpac/query/recinfobypoint/4258/-0.98838/37.73830.json'
```

También se puede pedir `.geojson` por punto o identificador según la documentación. Ese formato está documentado; la prueba de punto de esta revisión fue con `.json`.

## Cómo integrarlo

1. **Gonzalo/T-011:** resolver coordenadas o referencia completa mediante REST; conservar provincia, municipio, agregado, zona, polígono, parcela y recinto. Un identificador abreviado como 18/426/1 no es único a escala nacional.
2. Normalizar geometría, CRS y unidades en el pipeline. Guardar fecha de descarga, campaña confirmada, URL, licencia y datos originales relevantes. Distinguir campaña desconocida de campaña actual.
3. Consultar los registros de cultivo por OGC, paginar y filtrar por ID completo/intersección exacta. Decodificar productos con el catálogo correspondiente a esa campaña; conservar registros especiales o sin producto como tales. Excluir los campos de expediente de las salidas del producto.
4. Exportar el contrato común y cachearlo. **Jaime/T-010:** dibujar el recinto y mostrar sus atributos. **Enrique:** usar el polígono para estadísticas satelitales y contrastar la historia declarada, sin convertirla automáticamente en una rotación intraanual verificada.
5. El visor oficial queda como herramienta de comprobación manual y posible enlace de referencia. No hace falta automatizar clics ni extraer el HTML para obtener los datos.

## Precauciones técnicas confirmadas

- **Unidades distintas:** el servicio REST de consulta documenta superficie en hectáreas. La documentación MVT define superficie en m² y pendiente como entero en tanto por mil. No reutilizar el mismo conversor entre ambos servicios sin adaptarlo. OGC también requiere comprobar su esquema y sus unidades específicas.
- **Campañas distintas:** MVT documenta que la ruta vigente entrega recintos vigentes pero cultivo declarado de la campaña anterior. La descripción OGC habla de campaña en uso sin identificar un año numérico. No generalizar la campaña entre servicios ni etiquetar un cultivo como actual solo por la URL.
- WMS sirve para presentación cartográfica; para alimentar cálculos y conservar atributos se prefieren REST/OGC.
- Las pruebas pequeñas confirman acceso técnico. No se ha probado carga masiva ni verificado un límite de peticiones; usar consultas acotadas y caché.
- La cartografía administrativa es útil para delimitar recintos; no garantiza precisión de cada medición agronómica ni sustituye el contraste en campo.

## Reutilización y fuentes primarias

Los catálogos nacionales de **recintos** y **cultivo declarado** indican CC BY 4.0. Citar FEGA/MAPA, dataset, campaña/fecha y transformaciones. No extender automáticamente esa licencia a ortofotos u otras capas de terceros del visor.

- Recintos y licencia: https://datos.gob.es/es/catalogo/e0dat0002-recintos-del-sistema-de-informacion-geografica-de-parcelas-agricolas-sigpac-espana
- Cultivo declarado y licencia: https://datos.gob.es/es/catalogo/e0dat0002-cultivo-declarado-del-sistema-integrado-de-gestion-y-control-espana
- REST por punto, formatos y atributos: https://sigpac-hubcloud.es/html/csp/consultas/cooordenadas.html
- REST por código completo: https://sigpac-hubcloud.es/html/csp/consultas/codigoSigPac.html
- MVT, campañas y unidades: https://sigpac-hubcloud.es/html/mvt/descServicio.html
- Colección de recintos: https://sigpac-hubcloud.es/ogcapi/collections/recintos?f=json
- Colección de cultivo declarado: https://sigpac-hubcloud.es/ogcapi/collections/cultivo_declarado?f=json

## Estado de coordinación

Avisado todo el equipo por el bus (#67 y #68) y Gonzalo específicamente (#69). Gonzalo conserva la responsabilidad de integración en pipeline/contrato; esta nota aporta la comprobación y las precauciones. No se han cambiado sus carpetas ni la interfaz.
