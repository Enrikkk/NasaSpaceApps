# Field Shift en Murcia: propuesta de producto y reparto (PROPOSED, sin decidir)

v2, 13-nov-2026. Región: **Región de Murcia y alrededores** (decisión de Jaime). Base:
`reports/Datos agrícolas Región de Murcia.md` (investigación) y `research/field-shift-datasets.md` (datasets filtrados).
Las decisiones las toma el equipo y van a `coordination/DECISIONS.md`.

---

## Lo que pide el reto (lo que puntúan los jueces)

- Herramienta de apoyo a la decisión: observaciones NASA + suelo + rasgos de cultivos + **prioridades del agricultor**.
- **Al menos 3 rotaciones, incluida la actual.** Para cada una: por qué, evidencia, beneficios, huecos de información
  y riesgos para revisión local.
- Señalar **cuándo está el campo desnudo** y cuándo es vulnerable el cultivo. La IA ("SI") debería ayudar justo ahí.
- Recordar que **no sustituye** al agricultor ni al técnico.

## El ángulo: lo que nadie más tiene

No hay ninguna herramienta en España (ni de las revisadas fuera) que compare rotaciones con sus pros y contras, su
incertidumbre y las normas locales. Los otros equipos de Murcia enseñarán mapas NDVI y chatbots. Nosotros:

1. **Radiografía de la parcela:** su historia real de cultivos (FEGA 2025–2026 + HRL Croplands 2017–2024) y los
   meses de suelo desnudo detectados con NDVI de NASA (HLS) y Sentinel-2.
2. **Semáforo legal:** cada rotación se comprueba contra la Ley 3/2020 del Mar Menor (máximo 2 ciclos al año, no
   repetir hoja/brásica en Zona 1, cubierta si queda desnudo >2 meses en otoño-invierno, 170 kg N/ha cerca de la
   costa) y contra la PAC (GAEC 7, ecorrégimen de rotación ~142 €/ha en regadío). Con el artículo citado.
3. **Tarjetas honestas:** cada número con su fuente, su escala y su horquilla. "B gana en el 78 % de los escenarios"
   en vez de una nota exacta. Un apartado "lo que no sabemos" en cada tarjeta.
4. **Clima 2050:** las mismas rotaciones reordenadas con el clima previsto (NEX-GDDP-CMIP6).
5. **Sensor en la parcela:** la ley ya obliga a medir humedad del suelo en regadíos de >0,5 ha en Zona 1, y Murcia no
   tiene ninguna red abierta de humedad del suelo. Nuestro nodo IoT tapa ese hueco y corrige al satélite.

Regla de oro: **el motor calcula, la IA solo explica**. Si quitamos el LLM, el ranking sigue funcionando.

## Parcela de demo

Torre-Pacheco, SIGPAC 18/426/1 (lat 37.73830, lon −0.98838): 4,1 ha de regadío en zona vulnerable a nitratos;
**2025 melón → ahora barbecho**. Es la historia completa del Mar Menor en una parcela. Confirmar el sábado con el NDVI.

---

## Reparto con los perfiles reales

### Jaime: interfaz + pitch
- **Pantallas:**
  1. *Mapa* (PNOA de fondo) → clic en la parcela → ficha (SIGPAC: ha, pendiente, regadío, zona legal).
  2. *El pasado de tu parcela:* línea temporal 2017–2026 (cultivos HRL/FEGA + NDVI) con los meses desnudos marcados.
  3. *Tus prioridades:* sliders (ahorrar agua, ingresos, mejorar el suelo, menos nitrato).
  4. *Comparador:* actual + 2 alternativas en tarjetas: semáforo legal, €/ha, agua (m³/ha), nitrógeno,
     confianza, "por qué · evidencia · lo que no sabemos · consulta a tu técnico".
  5. *¿Y si…?* Slider de lluvia y temperatura, y botón "clima 2050".
  6. *Tu sensor:* lectura en vivo del nodo IoT frente a SMAP y la estación SIAM.
- Trabaja desde el sábado a las 9:30 con el **JSON de mentira** del contrato (abajo), sin esperar a nadie.
- Stack sugerido: React + Vite + MapLibre + Recharts (o lo que domine).
- **Pitch:** guion de 3 min, vídeo, slides, página del proyecto, declaración de uso de IA y lista de datasets citados.

### ML: radiografía + ranking con incertidumbre
- **Detector de suelo desnudo y transiciones** (~4 h): NDVI por parcela (HLS-VI + Sentinel-2) → suavizado →
  umbrales y puntos de cambio. Validado contra las capas de suelo desnudo de HRL y las fechas de HR-VPP. Es lo que
  el reto pide literalmente a la IA.
- **Ranking ponderado con Monte Carlo** (~4 h): TOPSIS con los pesos del agricultor; se muestrean lluvia (3 fuentes),
  precios (mín/máx) y modelos de clima → "% de veces que gana cada rotación".
- Ampliación: análogos climáticos 2050 (k-NN sobre NEX-GDDP-CMIP6) y clasificador de cultivo con embeddings
  (Presto/TESSERA) para 2025–2026. **No** hacer predicción de rendimiento: no hay etiquetas abiertas.

### Redes e IoT: sensores en tierra
- **Colector SIAM:** tarea horaria que lee las estaciones SIAM del geoportal del IMIDA y guarda la serie (SQLite).
  Es la "red de sensores" real de la región.
- **Nodo ESP32:** sonda capacitiva de humedad + DS18B20, JSON por MQTT. Wi-Fi en la sala (móvil de respaldo);
  LoRaWAN/TTN solo en la diapositiva (hay ~23 pasarelas TTN cerca de Murcia).
- Tres usos que enseñar: corregir el sesgo de SMAP, alerta local de helada/calor, detectar riegos (sube la humedad
  sin lluvia).
- Demo: reproducir por MQTT series reales del SIAM (p. ej. la DANA de 2019) con la etiqueta "datos históricos
  reproducidos", y regar en directo una maceta con el nodo.
- Además: **caché offline** de toda la demo y comprobar que el Wi-Fi del local no bloquea MQTT.

### Backend: tubería de datos + motor de reglas
- Tubería por parcela: SIGPAC → cultivo declarado → zona nitratos/Mar Menor → suelos (SoilGrids, cacheado) →
  MDT05 → POWER/IMERG → Open-Meteo ET0 → caché JSON/Parquet. El punto de partida es `research/api_smoke_test.py`.
- Lanza el sábado a las 9:00 las tareas lentas (AppEEARS HLS-VI/MODIS/SRTM, descarga HRL).
- **Motor de reglas:** tabla de rasgos de 27 cultivos (Kc FAO-56, raíz, salinidad, N, precio; está en las notas de
  contexto), agua = Kc × ET0 − lluvia efectiva, reglas de la Ley 3/2020 y la PAC.
- Genera el **paquete de evidencias** (cada cifra con dataset, URL, escala y horquilla) y sirve la API a la interfaz.
- Ampliación: narrador LLM que solo redacta a partir del paquete, con un validador que comprueba cada número.

## Contrato de datos (se acuerda el sábado a las 9:30)

Un fichero por parcela, `app/data/<parcela>.json`, con estos bloques:
`parcela` (SIGPAC, polígono, ha, pendiente, regadío, zona legal) · `historia` (años → cultivo, fuente) ·
`ndvi` (serie + meses desnudos) · `clima` (12 meses + tendencias + escenario 2050, con horquillas) · `suelo` ·
`sensores` (SIAM + nodo) · `rotaciones[]` (cultivos por estación, puntuaciones, semáforo legal con artículo,
`evidencia[]` dataset+valor+URL+escala, `incertidumbre`, `huecos[]`, `riesgos[]`).
Backend e IoT rellenan, ML añade `ndvi` y el ranking, la interfaz solo lee.

## Calendario

| Cuándo | Qué |
|---|---|
| Vie 13 (hoy) | Cuentas Earthdata Login y Copernicus Data Space (cada humano). Leer el informe. **Nada de código del producto.** |
| Sáb 9:00 | Lanzar tareas lentas (AppEEARS, HRL). Confirmar parcela y ángulo. Registrar D-002/D-003. |
| Sáb 9:30 | Contrato JSON fijado. Cada uno arranca en lo suyo (Jaime con datos falsos). |
| Sáb 14:00 | Primer recorrido completo, feo, con datos reales parciales. |
| Sáb noche | Ranking + semáforo + nodo IoT conectados a la interfaz. Todo en caché. |
| Dom 12:00 | **Congelar funciones.** Solo arreglos y pulido. |
| Dom 12–17 | Vídeo, slides, página, uso de IA, datasets citados. |
| Dom 23:59 | Cierre global. Preguntar a la organización la hora del jurado local. |

## Notas para el pitch (Jaime)

- Gancho: "Esta parcela de Torre-Pacheco dio melón en 2025. Hoy está desnuda. Si llueve como el 2 de octubre
  (180 l/m² en San Javier), su nitrato acaba en el Mar Menor. Esto lo vemos desde el espacio."
- 3 minutos: problema (15 s) → la parcela vista desde el satélite (40 s) → 3 rotaciones con semáforo (50 s) →
  clima 2050 y sensor (30 s) → honestidad: lo que no sabemos (15 s) → cierre (10 s).
- Enseñar la incertidumbre como fortaleza ("tres satélites no se ponen de acuerdo en cuánto llovió; por eso te damos
  una horquilla").
- Sin logos de NASA. Declarar el uso de IA (asistentes de código y el LLM en la app). Subtítulos en inglés.
