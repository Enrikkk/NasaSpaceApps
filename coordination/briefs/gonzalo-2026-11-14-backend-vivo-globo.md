# Brief de gonzalo (backend) · sáb 14-nov-2026 · PROPOSED, para Jaime, Enrique y Arturo

Origen: sesión interactiva de gonzalo revisando `coordination/PLAN.md` (plan en espera por Jaime, msg #41). Nada de esto
está implementado; no se han reclamado tareas T-009..T-023. Lo que es decisión de gonzalo va marcado **(gonzalo)**;
lo demás son propuestas del agente que necesitan ACCEPT del equipo.

## 1. Qué quiere gonzalo para el producto
- **Globo estilo Google Earth** donde se busca la parcela. Al hacer zoom aparecen los **recintos SIGPAC** (como el visor
  https://sigpac.mapa.es/fega/visor/) y, al hacer clic en uno, empiezan los cálculos con esas coordenadas.
- Layout: globo abajo a la izquierda tirando al centro; ajustes/filtros de navegación arriba a la izquierda y más
  controles a la derecha (a confirmar con Jaime si el globo es lienzo principal o minimapa).
- **Parcelas guardadas por navegador (`localStorage`), sin cuentas** (gonzalo).
- Lo pesado y complejo (drones, acuíferos/plantas de tratamiento, calidad/calibre) se **mockea y se anota** para slides y
  para el **vídeo de 30 s en inglés**. Suscripción y "plan socio" (descuento a cambio de datos de cosecha) se enseña
  **mockeado en la web**, etiquetado como demo. Todo lo demás, bien hecho.
- **Se requiere internet para funcionar** (gonzalo): no hace falta modo offline ni teselas precalculadas para la demo.
- **Backend vivo** (gonzalo). Hay **300 $ de créditos de GCP**: propuesta Cloud Run (FastAPI en contenedor, escala a
  cero). Crear proyecto/billing lo hace un humano.
- **Cobertura:** análisis completo en el **Campo de Cartagena** (gonzalo). Propuesta: resto de España en nivel
  "básico/indicativo" (ver 4).

## 2. Choque con el plan actual
D-007 (PROPOSED) dice estático y sin servidor; un backend vivo lo contradice. Texto propuesto para añadir (append) a
`coordination/DECISIONS.md` cuando Jaime dé el visto bueno:

```
## D-009 | 2026-11-14 | PROPOSED (amends D-007): backend vivo (FastAPI en Cloud Run, créditos GCP) en vez de demo 100 % estática. El navegador (globo MapLibre) dibuja recintos SIGPAC y, al hacer clic, llama a POST /analyze {lat, lon, recinto} que devuelve el contrato por bloques (cada bloque con _status: cargando | real | precalculado | simulado). Caché por celda (POWER 0,5°, SoilGrids 250 m). Se exige internet en la demo. Parcelas guardadas en localStorage, sin cuentas. Parcela demo precargada como respaldo | proposed by: gonzalo (decidido en chat con su agente), needs team ACCEPT
Why: el flujo "busco mi parcela, hago clic, se calcula" no cabe en un JSON precalculado por parcela. Rejected alternatives: demo solo estática (no permite clic libre); cuentas reales en SQLite (gonzalo: no hace falta).
```

## 3. Arquitectura propuesta
```
Navegador (React + MapLibre globo, Jaime)
 ├─ NASA GIBS (teselas WMTS)                       -> capas NDVI/lluvia, directo
 ├─ SIGPAC recintos por bbox + recinfobypoint      -> directo (CORS abierto)  [ver licencia, 5]
 └─ API Agrockham (FastAPI, gonzalo)  POST /analyze
      ├─ parcela/historia: SIGPAC + cultivo_declarado
      ├─ clima: POWER/IMERG 20 años, caché por celda 0,5°
      ├─ ET0: Open-Meteo, caché
      ├─ suelo: SoilGrids (5 llamadas/min), caché por celda; o raster regional descargado una vez
      ├─ reglas: tabla Ley 3/2020 + PAC (T-019)
      ├─ motor: run(parcela) -> rotaciones (Enrique, T-020: ha de ser función, no solo script offline)
      └─ NDVI: raster mensual precalculado del Campo de Cartagena -> estadística por polígono en el clic
```
La tarjeta se rellena por bloques (parcela ~0,2 s, clima ~2 s, suelo, luego rotaciones) con `_status` por bloque.

## 4. Cobertura en dos niveles (propuesta)
- **Completo (Campo de Cartagena):** reglas, precios, semáforo, rotaciones. Se delimita **por municipio**: la respuesta de
  SIGPAC trae provincia+municipio, así que es una consulta, sin geometría.
- **Básico (resto de España):** parcela, clima, suelo y reglas nacionales PAC. Rotaciones "indicativas, sin normativa
  autonómica ni precios locales"; semáforo legal en gris.
- Probado: el mismo endpoint SIGPAC responde en Valladolid y Valencia y devuelve el polígono en WKT.

## 5. Pruebas hechas hoy (solo lectura; scripts no incluidos en el repo)
- **SIGPAC OGC API** `sigpac-hubcloud.es/ogcapi/collections/recintos/items?bbox=`: 203 recintos en ~1,5x1 km en 0,65 s;
  **máx. 250 por página**; ~3 263 recintos en ~6x4 km (14 páginas); CORS abierto; **sin teselas vectoriales**. Atributos:
  referencia, pendiente media, altitud; uso y % regadío salen de `recinfobypoint`.
- **HLS con token de Earthdata:** CMR (sin login) encuentra 9 escenas HLSS30 en junio 2025 sobre la parcela demo. LP DAAC
  responde 303 a una URL firmada de CloudFront y admite lecturas por rango; la lectura por ventana (~1 km, B04+B8A+Fmask)
  de **una escena tardó 15,5 s** y dio NDVI medio 0,31. Nota técnica: GDAL no resolvió la redirección con
  `GDAL_HTTP_BEARER`; hay que pedir la URL firmada con `Authorization: Bearer` (`allow_redirects=False`) y pasarla a GDAL.
- Conclusión: ~170 escenas/año x 15 s en serie = ~45 min por ventana; con hilos, minutos. **No es viable en vivo por
  clic -> descargar una vez y precalcular compuestos mensuales de NDVI del Campo de Cartagena** (Enrique, T-013), y servir
  estadística por polígono. Sustituye a AppEEARS (colas) salvo como respaldo.

## 6. ⚠ Licencias (detalle en `submission/data-citations.md`, tabla nueva)
- **SIGPAC:** CC BY 4.0 (citar FEGA), **pero** una respuesta del FEGA en datos.gob.es dice que no se permite el acceso
  desde código de terceros a su base de datos. **Hay que resolverlo con el FEGA / sus condiciones de uso** antes de basar
  la demo en llamadas en vivo a `sigpac-hubcloud.es`. Alternativa limpia: descarga oficial por municipio (ATOM, CC BY) y
  servirlos nosotros (PMTiles/GeoJSON troceado).
- PNOA/IGN: CC BY 4.0, atribución visible "scne.es <año>". GIBS: crédito a NASA + reconocimiento de GIBS.
  SoilGrids: CC BY 4.0 (Poggio et al. 2021). Open-Meteo: datos CC BY, **API gratuita solo no comercial** (vale hoy).
- Revisión hecha solo con búsqueda web; lo marcado `verify` falta confirmarlo en la página oficial.

## 7. Reparto propuesto (sujeto al visto bueno de Jaime)
| Orden | Qué | Quién |
|---|---|---|
| 1 | Contrato v1 con `_status` por bloque (+`cargando`), `fuentes[]` con licencia, escenarios alineados entre rotaciones | gonzalo (T-009) |
| 2 | Capa de recintos SIGPAC en el globo (zoom >= ~14), clic = selecciona; parcelas guardadas en localStorage | Jaime (T-010) |
| 3 | `POST /analyze`: parcela, historia, clima, suelo reales con caché; despliegue en Cloud Run | gonzalo (T-011) |
| 4 | Semáforo legal como librería + endpoint | gonzalo (T-019) |
| 5 | Motor llamable `run(parcela)` | Enrique (T-020) |
| 6 | NDVI mensual del Campo de Cartagena a partir de HLS (lectura por ventanas) | Enrique (T-013) |
| 7 | Capas GIBS, mocks de visión, plan socio | Jaime |
Corte: si a las 19:00 (Hito 1) no hay recorrido completo con la parcela demo, se cortan 6 y 7.

## 8. Preguntas abiertas
1. @jaime: ¿visto bueno a D-009? ¿globo = lienzo principal o minimapa?
2. @enrique: ¿motor como función importable? ¿montas tú el compuesto mensual HLS (hay prueba de lectura funcionando)?
3. Quién crea el proyecto GCP con los 300 $ y quién hace el despliegue.
4. @gonzalo (humano): consulta al FEGA sobre acceso por código; BOE arts. 39/40/29/51 y Zona 1/2; T-002.

## 9. Seguridad
El token de Earthdata de gonzalo está solo en `.env` (git-ignorado). No se manda por el bus ni se escribe en LOG/commits.
