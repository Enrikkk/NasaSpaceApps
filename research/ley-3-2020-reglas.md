# Ley 3/2020 del Mar Menor y PAC: tabla de reglas para verificar en el BOE

> **No es asesoría legal.** Es una transcripción de trabajo, hecha por un agente, para que una persona
> (gonzalo) la contraste con el BOE antes de que el motor de reglas (T-019) la use. Los textos consolidados del BOE
> "son de carácter informativo y no tienen valor jurídico" (aviso del propio BOE). La salida del producto debe decir
> "consulta a tu técnico / a la Consejería".
>
> - Preparado: 2026-11-14 (seat gonzalo, agente de investigación; no reclama T-019).
> - Leído en primario hoy: texto consolidado de la Ley 3/2020 (BOE-A-2020-9793, "Última actualización publicada el 06/09/2023"),
>   su página de Análisis (referencias posteriores), RD 1049/2022 (BCAM 7), RD 1048/2022 (ecorrégimen), fichas y notas del FEGA.
> - Convención: **NO CONFIRMADO** = no está en el texto leído o no se pudo verificar. **INFERIDO** = lectura razonable que el texto no dice expresamente.
> - Las citas literales son cortas (máx. 25 palabras) y sirven solo para localizar el pasaje en el BOE.
>
> URLs base:
> - Ley (texto consolidado): <https://www.boe.es/eli/es-mc/l/2020/07/27/3/con> (ficha: <https://www.boe.es/buscar/act.php?id=BOE-A-2020-9793>)
> - Ley (análisis, referencias posteriores): <https://www.boe.es/buscar/doc.php?id=BOE-A-2020-9793>
> - RD 1049/2022 (condicionalidad, BCAM 7): <https://www.boe.es/eli/es/rd/2022/12/27/1049/con> (BOE-A-2022-23049)
> - RD 1048/2022 (ecorregímenes): <https://www.boe.es/eli/es/rd/2022/12/27/1048/con> (BOE-A-2022-23048)

## Resumen para quien tenga prisa

1. **La parcela de demo está en Zona 2** según las dos capas oficiales de la CARM (IDERM) consultadas hoy (sección 3). No se ha podido
   contrastar con la imagen del Anexo I del BOE (es un mapa sin leyenda ni coordenadas), así que queda "muy probable", no "confirmado".
2. Consecuencia: **los arts. 50-54 (Zona 1) no le son exigibles**. En particular el art. 51 (grupo 1, ciclos, cobertera) **no es una restricción legal en Zona 2**.
   El JSON de demo (`app/data/torre-pacheco.mock.json`, `semaforo_legal`) dice "Hoja repetida en zona 2 y suelo desnudo > 2 meses en invierno":
   esa combinación solo sería infracción en Zona 1 (art. 51.3 y 51.6). En Zona 2 aplican los arts. 37, 39 y 40 (y 29 si hubiera franja de 1.500 m, que no es el caso).
3. Los grupos legales del art. 51.1 **sí están en el texto**: melón, alcachofa y haba son **Grupo 2**; brócoli (Brassica) y lechuga (hojas, INFERIDO) son **Grupo 1**.
   Cebada, veza/cubierta y limón **no están clasificados** (NO CONFIRMADO).
4. Enmiendas: el BOE no registra ninguna posterior a 06/09/2023. Hay una reforma del régimen sancionador **solo en trámite** (toma en consideración 09/09/2026), que no toca las reglas agronómicas según lo que se ha podido leer (sección 4).
5. BCAM 7 **no obliga a explotaciones con ≤ 10 ha de tierra de cultivo** (RD 1049/2022, anexo II). Con 4,09 ha de la parcela demo, depende de la superficie total de la explotación (dato que no tenemos).

---

## 1. Tabla de reglas

Leyenda de tipo: **DURA** = restricción dura (incumplimiento = infracción o prohibición); **AVISO** = el motor avisa/penaliza pero no es prohibición directa o depende de un dato que no tenemos; **INFO** = informativo.
Zona: Z1 = solo Zona 1; Z2 = Zona 2 (y la 1 también, salvo que se diga lo contrario); "Z1+Z2" = ambas; "franja" = áreas a menos de 1.500 m de la ribera (art. 29).

Aplicabilidad por zona, base legal: art. 2.2 ("se diferencian dos zonas, Zona 1 y Zona 2, cuya delimitación se lleva a cabo en el Anexo I") y art. 26.1-2.
La Sección 1.ª del Cap. V (arts. 27-49) aplica a **Zonas 1 y 2**; la Sección 2.ª (arts. 50-54) solo a **Zona 1** (encabezados de sección en el texto consolidado).

### 1.1 Ley 3/2020

| id | Regla en una frase | Artículo / apartado | Cita literal corta | Tipo | Zona | Cómo se comprueba con nuestros datos |
|---|---|---|---|---|---|---|
| L-01 | La zona (1 o 2) de la explotación decide qué medidas aplican; si está en ambas, cada parte con las suyas | art. 26.1 y 26.2; art. 2.2 | "en función de la zona en que se encuentren, según la delimitación del Anexo I" | INFO | Z1+Z2 | Campo `zona` de la parcela (sección 3). Demo: Zona 2 (casi seguro) |
| L-02 | Franja de 1.500 m desde la ribera: prohibido fertilizante químico, estiércol no compostado y abono en verde | art. 29.4.a (y 29.2) | "Queda prohibida la aplicación de todo tipo de fertilizantes, estiércoles o abonado en verde en las citadas áreas" (29.2) | DURA | franja (Z1 y Z2 si la parcela cae en la franja) | Distancia parcela-orilla ≤ 1.500 m. **No tenemos la distancia calculada**: demo ≥ ~9 km del borde de Zona 1 (sección 3), luego no aplica. Para otras parcelas, calcular contra la ribera de la capa oficial |
| L-03 | Franja: máximo 170 kg N/ha/año | art. 29.4.b | "La fertilización superior a 170 kg/N/ha/año." | DURA | franja | kg N/ha/año del plan de abonado de la rotación (campo de N aportado por cultivo) y distancia ≤ 1.500 m |
| L-04 | Franja: la reserva de retención sube al 20 % de la explotación (máx. 20 % aunque el POT lo amplíe, art. 29.6) | art. 29.3 | "la reserva de suelo prevista en el artículo 37 será del 20 por ciento de la superficie de cada explotación" | INFO | franja | No es de rotación; dato de explotación. Mostrar solo como nota |
| L-05 | Franja: nuevos invernaderos y regadío sin derechos consolidados en ciertos casos, prohibidos | art. 29.4.c y 29.4.d | NO se cita (texto largo; leer el apartado) | INFO | franja | No aplica al motor de rotación |
| L-06 | 5 % de la superficie de cada explotación en Zona 1 y 2 a sistemas de retención de nutrientes (exentas unidades de regadío ≤ 0,5 ha; agrupación posible si < 2 ha) | art. 37.1, 37.5, 37.6 | "destinar el 5 por 100 de la superficie de cada explotación agrícola situada en la Zona 1 y 2" | AVISO | Z1+Z2 | Nivel explotación, no rotación. Mostrar aviso fijo ("reserva el 5 %"). Cuenta como retención, entre otras, "cubiertas vegetales" (art. 37.2.i): un cubierto podría ayudar, INFERIDO, confirmar con técnico. Infracción grave si no se cumple: art. 81.3.f |
| L-07 | Máximo 2 ciclos de cultivo anuales por parcela; 3 solo si son hortícolas de hoja de ciclo < 45 días | art. 39.2 | "queda prohibido establecer más de dos ciclos de cultivo anuales en una misma parcela agrícola" y "cultivos hortícolas de hojas de ciclo inferior a 45 días, para los que solo se permitirán como máximo tres ciclos anuales" | DURA | Z1+Z2 | Contar ciclos por año natural en el calendario de la rotación; si 3, exigir que los 3 sean hoja con ciclo < 45 días (campo `ciclo_dias` por cultivo). Infracción grave: art. 81.3.h. "Año" no está definido (INFERIDO: año natural) |
| L-08 | Anotar fecha de siembra/trasplante e inicio de recolección en el cuaderno de explotación | art. 39.2 (último párrafo) y 51.5 | "La fecha de siembra o trasplante y el inicio de la recolección deben anotarse en el cuaderno de explotación." | INFO | Z1+Z2 | El calendario ya tiene siembra y cosecha; recordatorio en la ficha |
| L-09 | Prohibida la urea y los fertilizantes con N ureico | art. 40.2 | "Se prohíbe en todo caso el uso de urea y de todos aquellos fertilizantes que presenten nitrógeno en forma ureica." | DURA | Z1+Z2 | Si el plan de abonado del motor declara la forma de N, rechazar urea. Si no hay dato de forma de N: AVISO "no uses urea" |
| L-10 | Prohibido el abonado mineral de fondo que contenga nitrógeno (se repite para Zona 1 en el art. 52.3) | art. 40.4 (y 52.3) | "Queda prohibido en todo caso la aplicación de abonado mineral de fondo, que contenga nitrógeno." | DURA | Z1+Z2 | Igual que L-09: depende de que el plan de abonado distinga fondo/cobertera. Si no, AVISO |
| L-11 | Nitrato amónico (N > 32 %) solo bajo supervisión técnica y nunca en el último tercio del ciclo de hortícolas | art. 40.3 | "En ningún caso se permitirá su aplicación en cultivos hortícolas en el último tercio de su ciclo de cultivo." | DURA | Z1+Z2 | Solo si el plan de abonado usa nitrato amónico y da fechas |
| L-12 | Obligatorio el balance de nitrógeno y prescripción técnica de los N; coeficientes de extracción "más restrictivos del intervalo" | art. 40.1, 40.5, 40.6 | "Será obligatorio realizar el cálculo del balance de nitrógeno" (40.5, cita parcial) | INFO | Z1+Z2 | El motor puede mostrar el N de la rotación como orientativo, no como prescripción |
| L-13 | En Zona 1 solo se permite agricultura "sostenible y de precisión" (la que cumple las secciones 1.ª y 2.ª) | art. 50.1 y 50.2 | "En la Zona 1 solo se permite la agricultura sostenible, y de precisión." | INFO | Z1 | No es una comprobación aparte; resume que en Z1 se suman las reglas L-14 a L-18 |
| L-14 | **Zona 1:** máx. 2 ciclos anuales y, de ellos, máx. 1 ciclo de especies del Grupo 1 | art. 51.2 | "solo podrá realizarse como máximo un ciclo de cultivo anual de las especies del Grupo 1" | DURA | **Z1** | Contar ciclos del año y marcar grupo por cultivo (sección 2). Infracción grave: art. 81.3.q. **No exigible en Zona 2** |
| L-15 | **Zona 1:** prohibidos dos ciclos consecutivos del Grupo 1; hay que alternar con Grupo 2. Excepción: Grupo 1 de ciclo < 45 días (que además permite 2 ciclos anuales) | art. 51.3 | "Queda prohibido realizar dos ciclos de cultivo consecutivos de especies del Grupo 1" y "Se excluyen de esta prohibición las especies del Grupo 1 de ciclo inferior a 45 días" | DURA | **Z1** | Para `allowed(prev, cur)` en la DP: prohibir grupo(prev)=1 y grupo(cur)=1 salvo `ciclo_dias` < 45. Infracción grave: art. 81.3.q. **No exigible en Zona 2** |
| L-16 | **Zona 1:** especies no incluidas en la tabla se asignan al Grupo 1 o 2 por profundidad radicular y manejo; su cultivo en Zona 1 se comunica antes a la Consejería | art. 51.4 | "se adscribirán al Grupo 1 o 2 en función de su profundidad radicular y manejo del cultivo" | AVISO | **Z1** | Cebada, veza, limón y otros no listados: NO CONFIRMADO su grupo (sección 2). El motor usa un grupo provisional marcado "por verificar" |
| L-17 | **Zona 1, regadío:** si en otoño-invierno no hay cultivo principal y el suelo queda desnudo > 2 meses, cultivo de cobertera (gramíneas u otras captadoras) enterrado como abono verde, o estructuras de retención (acaballonados) con vegetación espontánea. No aplica en invernaderos | art. 51.6 | "La medida se aplicará cuando el periodo de tiempo de suelo desnudo sea superior a dos meses" | DURA | **Z1** (regadío, no invernadero) | Meses de suelo desnudo del detector NDVI / calendario (> 2 meses seguidos). "Meses de otoño e invierno" no se define (INFERIDO oct-mar; NO CONFIRMADO). Infracción leve: art. 81.2.l. **En Zona 2 no es obligación legal**: la cubierta se propone como mejora agronómica, no como cumplimiento |
| L-18 | **Zona 1:** prohibida aplicación directa de purín sin tratar; otros estiércoles solo compostados y según CBPA | art. 52.1 y 52.2 | NO se cita | INFO | **Z1** | No afecta a la rotación del demo |
| L-19 | **Zona 1:** obligatorios sensores de humedad/tensiómetros (salvo regadío < 0,5 ha) y goteros ≤ 2,2 L/h en hortícolas | art. 53.1 y 53.2 | "Queda prohibido el empleo de goteros, en cultivos hortícolas, con caudales unitarios superiores a 2,2 L/h." | INFO | **Z1** | Dato de explotación, no de rotación |
| L-20 | **Zona 1, temporal:** prohibidos fertilizantes con N inorgánico o de síntesis "durante dos años o hasta que" haya infraestructura de encauzamiento; no se aplica en la franja de 1.500 m (rige el art. 29.4) | disposición adicional decimotercera (añadida por Decreto-ley 5/2021, en vigor 31/08/2021) | "Se prohíbe en su totalidad el uso de fertilizantes que contengan nitrógeno inorgánico o de síntesis." | AVISO (vigencia dudosa) | **Z1** | **NO CONFIRMADO si sigue en vigor**: el plazo de dos años, contado desde 31/08/2021, habría vencido en 2023 salvo que el texto de "o hasta que" implique otra cosa; no se ha encontrado en el BOE una prórroga ni derogación (el Análisis del BOE solo lista la adición). Para el demo (Z2) no aplica |
| L-21 | Cumplir el programa de actuación de la zona vulnerable a nitratos (Campo de Cartagena) | art. 48; arts. 40.1, 40.5, 54 | NO se cita | INFO | Z1+Z2 | El programa (Orden de 16/06/2016 citada en el preámbulo, y sus revisiones) **no se ha leído**: NO CONFIRMADO su contenido actual (límites de N por cultivo, periodos sin fertilizar) |
| L-22 | Sanciones: leves 2.000-5.000 €, graves 5.001-50.000 €, muy graves 50.001-500.000 €; graves/muy graves "conllevarán" pérdida de ayudas autonómicas 2 años | art. 83.1 y 83.4 | NO se cita | INFO | Z1+Z2 | Solo para el texto explicativo. Ojo: el art. 83.4 es el que pretende reformar la proposición del PP en trámite (sección 4) |

Notas de lectura:
- Art. 28 (prohibida la transformación de secano a regadío sin derecho de aguas anterior, Zonas 1 y 2) y art. 31 (derecho de aprovechamiento de aguas) pueden ser relevantes si el motor propone cambiar secano por regadío. No se han transcrito.
- Art. 36 (estructuras vegetales de conservación) y art. 38 (curvas de nivel; en Zona 2 se permite apartarse en ciertos casos) son de manejo, no de rotación.
- Art. 43, 44 y 42 (restos de cultivo, abandono, materia orgánica) no se han analizado a fondo.

### 1.2 PAC (condicionalidad y ecorrégimen)

| id | Regla en una frase | Fuente exacta | Cita literal corta | Tipo | Aplica a | Cómo se comprueba con nuestros datos |
|---|---|---|---|---|---|---|
| P-01 | **BCAM 7, práctica 1 (rotación):** cada año, al menos el 33 % de la tierra de cultivo de la explotación lleva un cultivo principal distinto del año anterior | RD 1049/2022, anexo II, BCAM 7 (BOE-A-2022-23049). Ficha FEGA: <https://www.fega.gob.es/sites/default/files/files/document/250210_FICHA_Capa_Cultivos_Reiterados_%20BCAM_7.pdf> | "Realizar una rotación anual de al menos el 33% de la superficie de las tierras de cultivo de la explotación" (ficha FEGA) | DURA (condicionalidad: condiciona el cobro de ayudas, no es infracción de la Ley del Mar Menor) | Explotación, no parcela suelta | A nivel de explotación: % de superficie cuyo cultivo principal cambia. "Cultivo principal" = el que está en la parcela de mayo a julio (anexo II, ajustable por CCAA). Para una sola parcela de demo, el motor solo puede mostrar "esta parcela rota" |
| P-02 | **BCAM 7:** todas las parcelas cambian de cultivo al menos una vez cada tres años | RD 1049/2022, anexo II (misma fuente) y ficha FEGA | "Realizar una rotación de cultivos en todas las parcelas de la explotación al menos una vez cada tres años" (ficha FEGA) | DURA | Parcela | `cultivo(t) != cultivo(t-1)` en alguna campaña de cada ventana de 3 años. Definición de "cultivo" abajo (P-03) |
| P-03 | Qué cuenta como "cultivo distinto": género botánico; **especie** en Brassicaceae, Solanaceae, Cucurbitaceae y género Vicia; más barbecho y hierba/forraje | Ficha FEGA, sección "Cultivos considerados y excepciones"; RD 1049/2022, anexo II ("Otros aspectos relativos a la BCAM 7") | NO se cita | INFO | Parcela | Brócoli y lechuga distintos (género Brassica vs Lactuca). Melón (Cucurbitaceae) distingue especie. Haba y veza son ambas Vicia pero **especies distintas** (se cuentan como distintos). Cebada vs. otro cereal: género distinto |
| P-04 | BCAM 7: exentos cultivos plurianuales, barbechos, hierbas/forrajes y cultivos bajo agua en el cómputo; exentas explotaciones con > 75 % de esos usos, **con ≤ 10 ha de tierra de cultivable** y las ecológicas certificadas (Reglamento UE 2018/848) | RD 1049/2022, anexo II, BCAM 7; ficha FEGA | "En las que la superficie de tierra cultivable es inferior o igual a 10 hectáreas" (RD 1049/2022) | AVISO | Explotación | Superficie total de la explotación (**no la tenemos**, solo la parcela 4,09 ha). Preguntar al usuario. Además, el sistema de control se dirige a explotaciones > 10 ha de superficie agraria declarada (RD 1049/2022, art. 5) y no se aplican penalizaciones a explotaciones ≤ 10 ha (art. 14) |
| P-05 | BCAM 7 (nota): la campaña 2023 tuvo excepción (no se aplicó la BCAM 7); desde la solicitud única 2025 se elige entre rotación y diversificación | RD 1049/2022, disposición transitoria primera ("Excepciones para la campaña 2023") y anexo II; ficha FEGA ("a partir de la solicitud única de 2025") | NO se cita | INFO | Explotación | Solo texto |
| P-06 | **Ecorrégimen P3 (rotación con especies mejorantes), regadío:** al menos el 50 % de la tierra acogida cambia de cultivo cada año (25 % si > 25 % de la tierra es plurianual) | RD 1048/2022, art. 35 y art. 36.1.a (BOE-A-2022-23048). FAQ FEGA: <https://www.fega.gob.es/sites/default/files/files/document/230306_pmf4-ecorregimenes_v4.pdf> (P.4.5 a P.4.7) | "al menos, el 50 % de la superficie de tierra de cultivo correspondiente presente cada año un cultivo diferente al cultivo previo" (art. 36.1.a) | AVISO (es una ayuda voluntaria, no una obligación) | Explotación acogida | Cultivo distinto del año anterior en ≥ 50 % de la superficie acogida. Barbecho tras leguminosa no cuenta como rotación |
| P-07 | P3: al menos el 10 % de la superficie con especies mejorantes (anexo XV), de las cuales leguminosas ≥ 5 % de la superficie acogida. Hay además un límite de barbecho (FAQ FEGA: 5 ha sobre 25 ha acogidas de regadío) | RD 1048/2022, art. 36.1.b y anexo XV; FAQ FEGA P.4.5 y P.4.7 | "como mínimo, el 10 % de la superficie de tierra de cultivo correspondiente, esté ocupada por especies mejorantes" (art. 36.1.b) | AVISO | Explotación acogida | % de la superficie con especie mejorante (lista del anexo XV, **no transcrita aquí**: NO CONFIRMADO qué especies concretas cuentan: leer anexo XV) |
| P-08 | P3: explotaciones con ≤ 10 ha de tierra de cultivo pueden elegir diversificación (≥ 2 cultivos, el principal ≤ 75 %) y no necesitan especies mejorantes | RD 1048/2022, art. 36.2 | NO se cita | AVISO | Explotación ≤ 10 ha | Superficie de explotación (no disponible) |
| P-09 | Ecorrégimen de regadío: exige plan de abonado y registro de aportes de nutrientes y agua en el cuaderno; en zona vulnerable las autoridades pueden añadir requisitos | RD 1048/2022, art. 35.2 y 35.3 | NO se cita | INFO | Explotación acogida | El demo está en zona vulnerable a nitratos (ES62_1): mencionar |
| P-10 | Importe P3 regadío peninsular 2025: 141,98 €/ha hasta 25 ha y 99,386 €/ha por encima (sin plurianualidad); con plurianualidad 166,98 / 124,386 €/ha | Nota web FEGA, "Ecorregímenes. Importes unitarios definitivos. Campaña 2025" (19/05/2026): <https://www.fega.gob.es/sites/default/files/files/document/260519_NOTA_WEB_EERR_SEGUNDO_SALDO_C2025.pdf>; página: <https://www.fega.gob.es/es/pepac-2023-2027/ayudas-directas/ecorregimenes/iu-definitivos-ecorregimenes-2025> | NO se cita | INFO | Explotación acogida | Línea de ingreso opcional en el motor ("si se acoge"). El ≈ 142 €/ha de `predictive-model-research.md` queda **confirmado** con la fuente oficial. El importe de 2026 es provisional: <https://www.fega.gob.es/es/pepac-2023-2027/ayudas-directas/ecorregimenes/ecorregimenes-importes-unitarios-provisionales-para-la-campana-2026> (no leído) |

Nota sobre P-07: la FAQ del FEGA (v4, 06/03/2023, P.4.7) da el ejemplo "25 ha de regadío acogidas: rotación en 12,5 ha, 2,5 ha de mejorantes (1,25 ha de leguminosas), barbecho no superior a 5 ha". Los porcentajes de mejorantes (10 %) y leguminosas (5 %) coinciden con el RD 1048/2022 art. 36.1.b. El **límite de barbecho (20 % en ese ejemplo) no aparece en el art. 36 leído**: NO CONFIRMADO en el RD; solo consta en la FAQ de 2023. No usarlo en el motor sin que gonzalo lo valide.

---

## 2. Grupos legales de cultivo (art. 51.1)

**Dónde se define:** art. 51.1 de la Ley 3/2020 ("Limitaciones adicionales relativas al ciclo de cultivo", Sección 2.ª del Cap. V). Es **una tabla de dos columnas** dentro del propio artículo; el criterio es "profundidad radicular y manejo del cultivo". **Solo vincula en Zona 1** (arts. 50-54).

**Grupo 1 (según el texto):** ajo, apio, hortalizas del género Brassica, hortalizas de hoja, hierbas aromáticas (perejil, hojas de apio, cilantro, eneldo, albahaca), maíz dulce, cebolla, puerro.

**Grupo 2 (según el texto):** guisantes, habas, judías, melón, pepino, pimiento, tomate, zanahoria, remolacha, alcachofa, sandía, patata.

| Cultivo del producto | ¿Lo clasifica el texto? | Grupo | Fundamento y salvedades |
|---|---|---|---|
| Lechuga | **No por nombre**; cae en la fila genérica "Hortalizas de hoja" | **Grupo 1 (INFERIDO)** | La lechuga es una hortaliza de hoja; el texto no nombra la lechuga. Confirmar con técnico/Consejería |
| Brócoli | **Sí, por la fila "Hortalizas del género Brassica"** | **Grupo 1** | Brócoli es *Brassica oleracea*. Es pertenencia botánica directa, pero el texto no dice "brócoli" |
| Melón | **Sí, por nombre** | **Grupo 2** | Fila "Melón" en la columna Grupo 2 |
| Alcachofa | **Sí, por nombre** | **Grupo 2** | Fila "Alcachofa" en Grupo 2. Resuelve el hueco de `predictive-model-research.md` ("grupo legal de alcachofa y haba sin confirmar") |
| Haba | **Sí, por nombre** ("Habas") | **Grupo 2** | Resuelve el mismo hueco |
| Cebada | **No** | **NO CONFIRMADO** | No está en la tabla. Por art. 51.4 se adscribe por profundidad radicular y manejo, y en Zona 1 su cultivo debe comunicarse antes a la Consejería. Sin criterio oficial leído |
| Veza / cubierta vegetal | **No** | **NO CONFIRMADO** | No está en la tabla. Además, el texto **no define** si una cobertera enterrada como abono verde (art. 51.6) cuenta como "ciclo de cultivo" a efectos de los arts. 39.2 y 51.2. Hay una pista en el art. 42.3.d (las especies para abonado en verde "no computan como otro cultivo", pero solo a efectos de la periodicidad de estiércoles), que no resuelve el caso |
| Limón | **No** | **NO CONFIRMADO** | Cultivo leñoso perenne; los arts. 39.2 y 51.2-51.3 hablan de "ciclos de cultivo anuales" y la tabla solo lista herbáceas. Lectura probable: no es objeto del art. 51 (INFERIDO), pero el texto no lo dice. Art. 38.2 exime a "plantaciones leñosas en riego localizado" solo de las actuaciones de curvas de nivel, no del art. 51 |

Consecuencias para T-019/T-020: en el motor, `grupo_legal` debe ser un campo con valor `1`, `2` o `desconocido`, y `desconocido` en Zona 1 produce ámbar "por verificar" (art. 51.4), nunca verde.

Nota de uso: la excepción "Grupo 1 de ciclo inferior a 45 días" (art. 51.3) y el máximo de 3 ciclos de hoja < 45 días (art. 39.2) son dos excepciones distintas con redacción distinta; no confundirlas. La excepción del art. 39.2 se refiere a "hortícolas de hojas"; la del art. 51.3 a "especies del Grupo 1".

---

## 3. ¿Zona 1 o Zona 2 para la parcela de demo?

Parcela: Torre-Pacheco, SIGPAC 18/426/1, lat 37,7383, lon -0,98838, municipio 30037.

**Resultado: Zona 2 (muy probable). Confirmado por servicio WMS oficial de la CARM, NO confirmado contra la imagen del Anexo I del BOE.**

Qué se hizo (reproducible):
1. El art. 2.2 remite el límite de zonas al Anexo I. En el texto consolidado del BOE el Anexo I es **una imagen** sin leyenda, topónimos ni coordenadas (`https://www.boe.es/datos/imagenes/disp/2020/221/09793_8507.png`, 2126x2587 px, versión vigente "06/09/2023"). Solo muestra el contorno de la cuenca y una línea interior; **no permite ubicar una parcela** por sí sola.
2. La CARM publica un servicio WMS con las zonas: <https://mapas-gis-inter.carm.es/geoserver/SIT_ZOR_SOST_MAR_MENOR_CARM/wms?SERVICE=WMS&version=1.3.0&REQUEST=GetCapabilities>
   - Capa `zonas_sost`: "Zonas Mar Menor Decreto-Ley 2-2019" (capa histórica, Decreto-ley 2/2019).
   - Capa `zonas_sost_mod_2023s`: "Zonas Mar Menor Decreto-Ley 3/2023" (Anexo I modificado por el Decreto-ley 3/2023, **derogado**; el Anexo I vigente en el BOE es el original de 2020).
3. `GetFeatureInfo` (CRS EPSG:4326, punto 37,7383 N / -0,98838 E) devuelve en las dos capas: **"Zona 2"** (Superficie ≈ 105.088 ha en `zonas_sost`; 105.079 ha en `zonas_sost_mod_2023s`).
4. Barrido a lo largo de la latitud 37,7383: Zona 2 desde lon -0,98838 hasta -0,88; **Zona 1 aparece en lon -0,86** (borde de Zona 1 ≈ 9,5-11 km al este del demo; hacia el norte y el sur, Zona 2 en 37,70-37,80). Por tanto el demo está **a ≥ ~9 km del borde de Zona 1**, y la ribera está aún más lejos: la **franja de 1.500 m del art. 29 no aplica** (dato calculado a ojo con distancia lineal, no con la geometría de la ribera).

Por qué sigue "no confirmado":
- Las dos capas son de normas **distintas** del Anexo I vigente de la Ley 3/2020 (Decreto-ley 2/2019 y Decreto-ley 3/2023). Coinciden entre sí para este punto (y difieren en solo ~9 ha), lo que sugiere que los límites relevantes son estables; pero la Ley 3/2020 asume el Anexo I original (imagen), y no se ha comprobado que la capa de 2019 sea idéntica a esa imagen.- Cómo cerrar la duda (para gonzalo, 5 min): abrir SITMurcia, capa de "Estrategia del paisaje / Zonas Mar Menor": <https://sitmurcia.carm.es/estrategia-campo-de-cartagena-y-mar-menor> (la Ley 3/2020 dice que el Anexo I se publica en el Sistema Territorial de Referencia), buscar Torre-Pacheco, polígono 18, parcela 426, recinto 1 (o las coordenadas) y mirar si cae dentro del polígono "Zona 2". Alternativa: cargar en QGIS el WMS anterior y la capa SIGPAC del recinto.
- Confirmar también con el Anexo I del BOE: ampliar la imagen y comprobar que la parcela queda del lado "no costero" (Zona 2) de la línea interior.

Respuesta a la hipótesis previa ("Zona 1/2 de una parcela depende del Anexo I, cuyo mapa no se ha recuperado"): el mapa se recuperó (imagen sin referencias), y el WMS oficial lo suple para el punto.

---

## 4. Enmiendas y estado vigente (a fecha 2026-11-14)

Fuente: pestaña "Análisis" del BOE (<https://www.boe.es/buscar/doc.php?id=BOE-A-2020-9793>) y cabecera de la ficha ("Última actualización publicada el 06/09/2023").

| Norma | Qué toca | Estado | Afecta a nuestras reglas |
|---|---|---|---|
| Decreto-ley 4/2021, de 17 jun (BORM-s-2021-90231) | Deroga arts. 64-66 (navegación) | En vigor/derogado luego reiteradamente por Ley 2/2022 | No |
| Decreto-ley 5/2021, de 27 ago (BORM-s-2021-90328; corrección BORM-s-2021-90332) | Modifica arts. 33, 34, 81.3, 84.2, 85.2; **añade la disposición adicional decimotercera** (N en Zona 1) | En vigor. Recurso de inconstitucionalidad desestimado: STC 126/2023, de 27 sep (BOE-A-2023-22421) | Sí: **DA 13 (L-20)**; art. 81.3 (infracciones graves) |
| Ley 4/2021, de 16 sep (BOE-A-2021-21316) | Modifica arts. 21, 22, 23 (vertidos) | En vigor | No |
| Ley 2/2022, de 19 may (BOE-A-2022-11316) | Deroga arts. 64-66 | En vigor | No |
| Decreto-ley 3/2023, de 3 ago (BORM-s-2023-90255) | Modificaba arts. 15, 16 y Anexos I y II | **Derogado** por Acuerdo publicado en Resolución de 1 sep 2023 (BORM-s-2023-90262); el consolidado "deja sin efecto" la modificación | Anexo I (zonas): vigente el original de 2020 (sección 3) |
| Sentencia TC 112/2021, de 13 may (BOE-A-2021-10025) | Recurso 5178/2020, desestimación respecto a determinados preceptos | Informativa | No concreto (no se leyó) |

**Posteriores a 06/09/2023: ninguna registrada en el BOE** (el consolidado no tiene versión posterior, y el Análisis no lista nada después de la STC de 27/09/2023 y el acuerdo de 01/09/2023). Esa es la verificación primaria hecha hoy.

Reforma anunciada **sin publicar** (búsqueda web, fuentes de prensa; no se ha encontrado el texto ni en el BOE ni en el BORM):
- Proposición de ley del PP para modificar el régimen sancionador (adaptarlo a la norma estatal de nutrición sostenible de suelos agrarios, y cambiar en el art. 83.4 "conllevará" por "podrá conllevar" la pérdida de ayudas): el Pleno de la Asamblea Regional aprobó solo la **toma en consideración el 9 de septiembre de 2026** (PP a favor, Vox abstención, PSOE y Podemos-IU-AV en contra) y está en fase de audiencias y comisión; no está aprobada ni publicada. Fuente: <https://www.la7tv.es/articulo/politica/asamblea-tramitara-reforma-que-decidira-infracciones-ley-mar-menor-implican-perder-ayudas/20260909083322073177.html> (también <https://www.moncloa.com/2026/09/10/lopez-miras-reforma-ley-mar-menor-3428937> y <https://www.cartagenaactualidad.com/articulo/region/asamblea-da-luz-verde-reforma-ley-mar-menor-pp-que-adapta-norma-estatal-sanciones-evita-duplicidades-mantiene-intacta-proteccion-ecosistema/20260909143302225525.html>, estos dos no leídos por completo). **No cita artículos agronómicos (29, 39, 40, 51)**, pero la fuente leída tampoco da el articulado completo: **NO CONFIRMADO** que no los toque.
- Propuestas de Vox y de Podemos-IU-AV (esta última sobre plantas solares en Zona 1 y 2) en el mismo trámite: contenido no verificado.
- Propuesta conjunta del sector agrario de 2022 (curvas de nivel, biosolarización, inhibidores) para modificar arts. 29, 38, 52 entre otros: sin evidencia de que se haya incorporado. Fuente: <https://agroinformacion.com/todo-el-sector-agrario-registra-una-propuesta-conjunta-de-actualizacion-de-la-ley-de-proteccion-del-mar-menor-porque-la-actual-esta-desactualizada/> (no leída por completo).
- Un resumen de búsqueda de la investigación previa dice que un decreto posterior "extendió la prohibición de N a toda la Zona 1". La explicación más probable es la **DA 13 del Decreto-ley 5/2021**, ya incluida en el texto (L-20); no se ha encontrado otro decreto. **NO CONFIRMADO** que no exista una prórroga de la DA 13 publicada solo en el BORM.

PAC:
- RD 1048/2022 consolidado figura "Última actualización publicada el 08/07/2026"; el RD 1049/2022, "09/10/2024". El texto leído hoy es el consolidado vigente a 2026-11-14, pero **no se ha comparado el contenido de las actualizaciones recientes del RD 1048/2022**: NO CONFIRMADO que la regla P3 de la FAQ de 2023 siga igual (el art. 36 leído hoy sí dice 50 %/10 %/5 %).

---

## 5. Checklist para gonzalo (en orden)

1. **Zona del demo (la más importante, 5 min).** Abre SITMurcia ( <https://sitmurcia.carm.es/estrategia-campo-de-cartagena-y-mar-menor> ) o el WMS en QGIS (sección 3) y confirma que SIGPAC 18/426/1 es "Zona 2". Si es Zona 1, los arts. 50-54 pasan a ser exigibles y hay que cambiar el demo y las reglas L-14 a L-17.
2. **Anexo I en el BOE:** abre <https://www.boe.es/buscar/act.php?id=BOE-A-2020-9793#ai> y confirma que la versión "Última actualización 06/09/2023" muestra el Anexo I original (el consolidado dice que la modificación por Decreto-ley 3/2023 "se deja sin efecto").
3. **Art. 2.2 y art. 26** (aplicabilidad por zona): confirma que Sección 1.ª (arts. 27-49) = Zonas 1 y 2, Sección 2.ª (arts. 50-54) = solo Zona 1.
4. **Art. 39.2** (L-07): confirma "más de dos ciclos anuales; tres solo hoja < 45 días".
5. **Art. 40.2, 40.3, 40.4** (L-09, L-10, L-11): confirma urea, nitrato amónico y abonado de fondo.
6. **Art. 37.1 y 37.6** (L-06): confirma 5 % y exenciones.
7. **Art. 29.1, 29.2, 29.4.a, 29.4.b** (L-02, L-03): confirma 1.500 m, prohibición y 170 kg N/ha/año.
8. **Art. 51.1** (tabla de grupos): contrasta la lista de la sección 2, sobre todo "Hortalizas de hoja", "Hortalizas del género Brassica", "Alcachofa", "Habas", "Melón".
9. **Art. 51.2, 51.3, 51.4, 51.6** (L-14 a L-17): confirma redacción, la excepción de 45 días y la exclusión de invernaderos. Decide qué meses son "otoño e invierno" para el detector de suelo desnudo (el texto no los define).
10. **Disposición adicional decimotercera** (L-20): comprueba en el BORM si sigue vigente o se prorrogó; solo importa si algún día se usa una parcela de Zona 1.
11. **Análisis del BOE:** revisa <https://www.boe.es/buscar/doc.php?id=BOE-A-2020-9793> (Referencias posteriores) por si el día de la entrega hay una modificación publicada después de 06/09/2023.
12. **BCAM 7:** lee el anexo II del RD 1049/2022 (apartado BCAM 7) y confirma 33 %, "una vez cada tres años", la exención ≤ 10 ha y la definición de cultivo; después mira la ficha FEGA citada.
13. **Ecorrégimen P3:** lee arts. 35 y 36 y el anexo XV (especies mejorantes) del RD 1048/2022, y los importes 2025 en la nota del FEGA; revisa el límite de barbecho (NO CONFIRMADO).
14. **Qué hacer con los NO CONFIRMADO**: decidir en el motor si cebada, veza y limón se marcan `grupo_legal = desconocido` (ámbar solo en Zona 1) y si la cubierta cuenta como ciclo (afecta a 39.2).
15. **Programa de actuación de la zona vulnerable** (art. 48): es posible que fije límites de N por cultivo; no leído. Búscalo en el BORM si el motor va a mostrar N por cultivo como "cumple la normativa".
16. **Actualiza el mock del demo:** el `semaforo_legal` actual ("Hoja repetida en zona 2...", `articulo: "Ley 3/2020 (comprobar articulo exacto)"`) no cuadra con Zona 2. Sustituir por la regla que sí aplica (p. ej. art. 39.2 con el número real de ciclos), cuando decidas.

---

## Anexo: fuentes y su estado de lectura

| Fuente | URL | Leído |
|---|---|---|
| Ley 3/2020, texto consolidado | <https://www.boe.es/eli/es-mc/l/2020/07/27/3/con> | Sí (arts. 1-86, DA 13, DT 3, anexos I y III en parte) |
| Ley 3/2020, Análisis | <https://www.boe.es/buscar/doc.php?id=BOE-A-2020-9793> | Sí |
| Anexo I, imagen | <https://www.boe.es/datos/imagenes/disp/2020/221/09793_8507.png> | Sí (solo contorno) |
| WMS zonas CARM | <https://mapas-gis-inter.carm.es/geoserver/SIT_ZOR_SOST_MAR_MENOR_CARM/wms> | Sí (GetCapabilities, GetFeatureInfo) |
| RD 1049/2022 | <https://www.boe.es/eli/es/rd/2022/12/27/1049/con> | Sí (BCAM 7) |
| RD 1048/2022 | <https://www.boe.es/eli/es/rd/2022/12/27/1048/con> | Sí (arts. 33-37); anexos X, XV, XVI **no leídos** |
| FEGA ficha BCAM 7 (capa cultivos reiterados) | <https://www.fega.gob.es/sites/default/files/files/document/250210_FICHA_Capa_Cultivos_Reiterados_%20BCAM_7.pdf> | Sí |
| FEGA FAQ nueva PAC (ecorregímenes) | <https://www.fega.gob.es/sites/default/files/files/document/230306_pmf4-ecorregimenes_v4.pdf> | Parcial (P.4.5-P.4.10, P.4.54) |
| FEGA nota importes 2025 | <https://www.fega.gob.es/sites/default/files/files/document/260519_NOTA_WEB_EERR_SEGUNDO_SALDO_C2025.pdf> | Sí (tabla de regadío) |
| STC 126/2023 | <https://www.boe.es/buscar/doc.php?id=BOE-A-2023-22421> | Resumen (no entra en el contenido de la DA 13) |
| Reforma 2026 (prensa) | La7TV, Moncloa, Cartagena Actualidad | La7TV leído; el resto solo en resultados de búsqueda |

Licencia/originalidad: este fichero contiene citas cortas y resúmenes propios; ningún texto extenso copiado. Las normas del BOE son documentos oficiales de acceso público; citar siempre BOE/BORM/FEGA en `submission/` (campo "Space Agency Partner & Other Data" / fuentes) cuando se usen.
