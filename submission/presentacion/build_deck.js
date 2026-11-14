// Builds agrockham-presentacion.pptx (6 slides, ~1:30). Brand: brand/README.md (palette, logo, Inter).
// Run: NODE_PATH=<dir with pptxgenjs, react, react-dom, react-icons, sharp> node build_deck.js
// Screenshots in assets/ are of the live app (v9); the two marked GIF are meant to be swapped for recordings.
const path = require('path');
const pptxgen = require('pptxgenjs');
const React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');
const sharp = require('sharp');
const fa = require('react-icons/fa6');
const { applyTheme } = require(process.env.PPTX_SKILL_DIR
  ? path.join(process.env.PPTX_SKILL_DIR, 'scripts/apply_theme.js') : './apply_theme.js');

const A = f => path.join(__dirname, 'assets', f);
const OUT = path.join(__dirname, 'agrockham-presentacion.pptx');

const THEME = {
  name: 'Agrockham', headFontFace: 'Inter', bodyFontFace: 'Inter',
  colors: {
    dk1: '2B2F2B', lt1: 'F0EDE4', dk2: '1E3626', lt2: 'B9BDB2',
    accent1: '6BB383', accent2: '297847', accent3: 'E0B04A', accent4: 'E07A5F', accent5: '8EC5FF', accent6: '373C36',
    hlink: '6BB383', folHlink: 'B9BDB2',
  },
};
const HEX = { bg: '2B2F2B', brandDark: '1E3626', space: '05070A' };

async function icon(Icon, color = '#F0EDE4') {
  const svg = renderToStaticMarkup(React.createElement(Icon, { size: 256, color }));
  const buf = await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer();
  return 'image/png;base64,' + buf.toString('base64');
}

(async () => {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE'; // 13.333 x 7.5 in
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.author = 'Equipo Agrockham';
  pres.title = 'Agrockham: presentación (1:30)';
  const C = pres.SchemeColor;

  const ICON = {
    map: await icon(fa.FaMap), pointer: await icon(fa.FaHandPointer), clima: await icon(fa.FaCloudSun),
    sat: await icon(fa.FaSatellite), suelo: await icon(fa.FaLayerGroup), parcela: await icon(fa.FaClipboardList),
    temp: await icon(fa.FaTemperatureHalf), ley: await icon(fa.FaScaleBalanced), euro: await icon(fa.FaEuroSign),
    gears: await icon(fa.FaGears), chart: await icon(fa.FaChartColumn), rotate: await icon(fa.FaRotate),
    traffic: await icon(fa.FaTrafficLight), check: await icon(fa.FaCheck), next: await icon(fa.FaArrowRight),
    rain: await icon(fa.FaCloudRain, '#2B2F2B'),
  };

  // ---------- layouts ----------
  const footer = () => ({ text: { text: 'Agrockham · NASA Space Apps Challenge 2026 · Murcia',
    options: { x: 0.6, y: 6.98, w: 8, h: 0.3, fontSize: 10, color: C.background2, margin: 0 } } });
  pres.defineSlideMaster({
    title: 'Portada', background: { color: HEX.space },
    objects: [{ placeholder: { options: { name: 'body', type: 'body', x: 0.7, y: 3.55, w: 6.6, h: 1.05,
      fontSize: 28, bold: true, color: C.background1, valign: 'top', margin: 0 }, text: '' } }],
  });
  pres.defineSlideMaster({
    title: 'Contenido', background: { color: HEX.bg },
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.4, w: 12.13, h: 0.8,
        fontSize: 34, bold: true, color: C.background1, align: 'left', valign: 'middle', margin: 0 }, text: '' } },
      footer(),
    ],
    slideNumber: { x: 12.23, y: 6.98, w: 0.5, h: 0.3, fontSize: 10, color: C.background2, align: 'right' },
  });
  pres.defineSlideMaster({
    title: 'Cierre', background: { color: HEX.brandDark },
    objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 1.75, w: 12.13, h: 0.9,
      fontSize: 40, bold: true, color: C.background1, align: 'left', valign: 'middle', margin: 0 }, text: '' } }],
  });

  // ---------- helpers ----------
  const card = (s, x, y, w, h, name, fill = C.accent6) =>
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { type: 'none' }, objectName: name });
  const dot = (s, x, y, d, img, name, fill = C.accent2) => {
    s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { type: 'none' }, objectName: name + ' círculo' });
    const p = d * 0.27;
    s.addImage({ data: img, x: x + p, y: y + p, w: d - 2 * p, h: d - 2 * p, objectName: name + ' icono' });
  };
  const text = (s, t, o) => s.addText(t, Object.assign({ isTextBox: true, margin: 0, color: C.background1, fontSize: 14, valign: 'top' }, o));
  const caption = (s, t, x, y, w) => text(s, t, { x, y, w, h: 0.28, fontSize: 10, color: C.background2, objectName: 'Créditos' });
  const shot = (s, file, x, y, w, h, name) => s.addImage({ path: A(file), x, y, w, h, objectName: name, altText: name,
    shadow: { type: 'outer', color: '000000', opacity: 0.45, blur: 10, offset: 3, angle: 90 } });

  // ======================= 1. PORTADA =======================
  pres.addSection({ title: 'Apertura' });
  let s = pres.addSlide({ masterName: 'Portada', sectionTitle: 'Apertura' });
  s.addImage({ path: A('globo.jpg'), x: 0, y: 0, w: 13.333, h: 7.5, objectName: 'Globo (app)' });
    s.addImage({ path: A('agrockham-logo-on-dark.png'), x: 0.7, y: 2.2, w: 6.2, h: 6.2 * 461 / 2400, objectName: 'Logo Agrockham' });
  s.addText('Qué sembrar, cuándo y con qué riesgo', { placeholder: 'body' });
  text(s, 'Clima de satélite, suelo, precios y la ley del Mar Menor, juntos en tu parcela.',
    { x: 0.7, y: 4.75, w: 6.4, h: 0.8, fontSize: 18, color: C.background1, objectName: 'Subtítulo' });
  text(s, 'NASA Space Apps Challenge 2026 · Reto «Field Shift: Adapting Farms with NASA Data» · Murcia',
    { x: 0.7, y: 6.45, w: 10.5, h: 0.3, fontSize: 12, color: C.background1, objectName: 'Evento' });
  caption(s, 'Imagen de la app: Blue Marble, NASA GIBS / NASA Earth Observatory · IGN (CC BY 4.0 scne.es)', 0.7, 6.85, 10.5);
  s.addNotes(`[0:00-0:06] Entra justo después del vídeo («Así nace Agrockham»).
GUION: «Esto es Agrockham: te ayuda a decidir qué sembrar, cuándo y con qué riesgo.»`);

  // ======================= 2. MAPA =======================
  pres.addSection({ title: 'Producto' });
  s = pres.addSlide({ masterName: 'Contenido', sectionTitle: 'Producto' });
  s.addText('Todas las parcelas de España, en un mapa', { placeholder: 'title' });
  shot(s, 'mapa-sigpac.jpg', 0.6, 1.5, 7.6, 7.6 * 9 / 16, 'GIF 1: zoom del globo a la parcela');
  caption(s, 'Captura de la app · Recintos SIGPAC © FEGA (CC BY 4.0) · Ortofoto PNOA © IGN (CC BY 4.0 scne.es)', 0.6, 5.88, 7.6);
  const rx = 8.65, rw = 4.08;
  [[ICON.map, 'Recintos oficiales SIGPAC', 'Toda España, sobre la ortofoto del IGN'],
   [ICON.pointer, 'Un clic en tu parcela', 'Superficie, riego, pendiente, uso y cultivos declarados']].forEach(([ic, h, b], i) => {
    const y = 1.55 + i * 1.3;
    dot(s, rx, y, 0.62, ic, h);
    text(s, h, { x: rx + 0.85, y: y - 0.02, w: rw - 0.85, h: 0.36, fontSize: 17, bold: true, objectName: h });
    text(s, b, { x: rx + 0.85, y: y + 0.38, w: rw - 0.85, h: 0.62, fontSize: 14, color: C.background2, objectName: h + ' detalle' });
  });
  card(s, rx, 4.2, rw, 1.95, 'Cifra Campo de Cartagena');
  text(s, '170.265', { x: rx + 0.3, y: 4.35, w: rw - 0.6, h: 0.8, fontSize: 48, bold: true, color: C.accent1, objectName: 'Cifra recintos' });
  text(s, 'recintos con análisis completo en 7 municipios del Campo de Cartagena',
    { x: rx + 0.3, y: 5.18, w: rw - 0.6, h: 0.75, fontSize: 14, objectName: 'Cifra detalle' });
  s.addNotes(`[0:06-0:23]
GUION: «Para ordenar tantos datos hemos creado un mapa con todas las parcelas oficiales de España. Haces clic en la tuya y ves su superficie, su riego y su pendiente. El análisis completo ya funciona en el Campo de Cartagena: más de ciento setenta mil parcelas.»

GIF 1 (sustituye a la captura): en la app, «Ir a mis parcelas» → el globo hace zoom hasta la parcela → clic en un recinto y se abre su ficha. 6-8 s, 15 fps, en bucle.
Cómo cambiarla sin perder tamaño ni posición: clic derecho en la imagen → Cambiar imagen → Desde un archivo.`);

  // ======================= 3. DATOS =======================
  s = pres.addSlide({ masterName: 'Contenido', sectionTitle: 'Producto' });
  s.addText('Lo que sabemos de cada parcela', { placeholder: 'title' });
  shot(s, 'panel-parcela.jpg', 0.6, 1.5, 4.75 * 0.92, 4.75, 'Ficha de la parcela (app)');
  caption(s, 'Ficha real de un recinto en la app', 0.6, 6.33, 4.4);
  const gx = 5.55, cw = 3.44, ch = 1.06, gap = 0.3;
  [[ICON.clima, 'Clima diario, 20 años', 'NASA POWER'],
   [ICON.sat, 'Lluvia por satélite', 'GPM IMERG (NASA) · ERA5'],
   [ICON.suelo, 'Suelo', 'ISRIC SoilGrids'],
   [ICON.parcela, 'Parcela y cultivos', 'SIGPAC · declaraciones a FEGA'],
   [ICON.temp, 'Heladas y calor', 'Estaciones SIAM-IMIDA'],
   [ICON.ley, 'Ley del Mar Menor', 'Ley 3/2020 (BOE)']].forEach(([ic, h, src], i) => {
    const x = gx + (i % 2) * (cw + gap), y = 1.5 + Math.floor(i / 2) * (ch + 0.22);
    card(s, x, y, cw, ch, 'Fuente: ' + h);
    dot(s, x + 0.22, y + 0.25, 0.56, ic, h);
    text(s, h, { x: x + 0.95, y: y + 0.2, w: cw - 1.1, h: 0.36, fontSize: 15, bold: true, objectName: h });
    text(s, src, { x: x + 0.95, y: y + 0.57, w: cw - 1.1, h: 0.3, fontSize: 12, color: C.background2, objectName: h + ' fuente' });
  });
  card(s, gx, 5.4, 2 * cw + gap, 1.0, 'Aviso lluvia', C.accent3);
  s.addImage({ data: ICON.rain, x: gx + 0.3, y: 5.62, w: 0.56, h: 0.56, objectName: 'Icono lluvia' });
  text(s, [{ text: '3 fuentes de lluvia, ~40 % de diferencia en la misma parcela. ', options: { bold: true } },
           { text: 'Te damos una horquilla, no un número inventado.' }],
    { x: gx + 1.1, y: 5.55, w: 2 * cw + gap - 1.35, h: 0.75, fontSize: 15, color: C.text1, valign: 'middle', objectName: 'Aviso lluvia texto' });
  s.addNotes(`[0:23-0:43]
GUION: «Con ese clic juntamos datos que antes estaban dispersos: veinte años de clima diario de NASA POWER, la lluvia del satélite GPM IMERG, el suelo y los cultivos que declaraste. Y somos honestos: tres fuentes de lluvia difieren hasta un cuarenta por ciento, así que te damos una horquilla, no un número inventado.»
Enlaza con el vídeo de apertura («Three rain sources. Same field. Forty percent apart.»).`);

  // ======================= 4. PRECIOS =======================
  s = pres.addSlide({ masterName: 'Contenido', sectionTitle: 'Producto' });
  s.addText('20 años de precios y clima, año a año', { placeholder: 'title' });
  const steps = [[ICON.euro, 'Precios de venta', '2005–2024 · MAPA, Eurostat, FAOSTAT (España)'],
                 [ICON.clima, 'Clima del mismo año', 'NASA POWER · estaciones SIAM'],
                 [ICON.gears, 'Simulamos cada rotación', '3 años, cultivo a cultivo, con su riego'],
                 [ICON.chart, 'Resultado', '€ por hectárea en un año malo, normal y bueno']];
  const sw = 2.65, sg = 0.5;
  steps.forEach(([ic, h, b], i) => {
    const x = 0.6 + i * (sw + sg);
    card(s, x, 1.6, sw, 2.85, 'Paso ' + (i + 1));
    dot(s, x + 0.3, 1.88, 0.7, ic, 'Paso ' + (i + 1));
    text(s, h, { x: x + 0.3, y: 2.78, w: sw - 0.6, h: 0.72, fontSize: 17, valign: 'bottom', bold: true, objectName: 'Paso ' + (i + 1) + ' título' });
    text(s, b, { x: x + 0.3, y: 3.6, w: sw - 0.6, h: 0.75, fontSize: 13, color: C.background2, objectName: 'Paso ' + (i + 1) + ' detalle' });
    if (i < 3) s.addImage({ data: ICON.next, x: x + sw + 0.11, y: 2.7, w: 0.28, h: 0.28, objectName: 'Flecha ' + (i + 1) });
  });
  text(s, '20', { x: 0.6, y: 4.85, w: 1.6, h: 1.3, fontSize: 80, bold: true, color: C.accent1, objectName: 'Cifra 20' });
  text(s, 'años', { x: 2.25, y: 5.33, w: 1.2, h: 0.6, fontSize: 26, bold: true, objectName: 'Cifra años' });
  text(s, [{ text: 'Cada año simulado usa el clima y el precio de ese mismo año.', options: { bold: true, breakLine: true } },
           { text: 'Así el riesgo sale de lo que pasó de verdad, no de una media. Los precios son nacionales: en Murcia pueden ser otros.', options: { color: C.background2 } }],
    { x: 3.75, y: 4.97, w: 8.95, h: 1.15, fontSize: 16, valign: 'middle', paraSpaceAfter: 6, objectName: 'Explicación' });
  s.addNotes(`[0:43-0:55]
GUION: «Además, hemos creado un sistema económico con veinte años de precios de mercado. Simulamos cada rotación año a año, con el clima y el precio de ese mismo año.»`);

  // ======================= 5. DECISIÓN =======================
  s = pres.addSlide({ masterName: 'Contenido', sectionTitle: 'Producto' });
  s.addText('Tú decides qué te importa', { placeholder: 'title' });
  shot(s, 'rotaciones-filtros.jpg', 5.2, 1.5, 7.53, 7.53 * 9 / 16, 'GIF 2: prioridades y rotaciones');
  caption(s, 'Captura de la app · Recintos SIGPAC © FEGA (CC BY 4.0) · Ortofoto PNOA © IGN (CC BY 4.0 scne.es)', 5.2, 5.83, 7.53);
  text(s, '¿Qué te importa más?', { x: 0.6, y: 1.5, w: 4.3, h: 0.36, fontSize: 15, bold: true, color: C.accent1, objectName: 'Prioridades título' });
  ['Beneficio', 'Ahorro de agua', 'Salud del suelo', 'Menos riesgo'].forEach((p, i) => {
    const x = 0.6 + (i % 2) * 2.2, y = 2.0 + Math.floor(i / 2) * 0.62;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 2.05, h: 0.48, rectRadius: 0.24, fill: { color: C.accent2 }, line: { type: 'none' }, objectName: 'Prioridad ' + p });
    text(s, p, { x, y, w: 2.05, h: 0.48, fontSize: 14, bold: true, align: 'center', valign: 'middle', objectName: 'Prioridad ' + p + ' texto' });
  });
  [[ICON.rotate, 'Rotaciones a 3 años, ordenadas por lo que tú eliges'],
   [ICON.chart, '€ por hectárea en un año malo, normal y bueno'],
   [ICON.traffic, 'Semáforo legal con la ley del Mar Menor']].forEach(([ic, t], i) => {
    const y = 3.5 + i * 0.85;
    dot(s, 0.6, y, 0.55, ic, t, i === 2 ? C.accent3 : C.accent2);
    text(s, t, { x: 1.35, y: y - 0.02, w: 3.55, h: 0.62, fontSize: 15, valign: 'middle', objectName: t });
  });
  s.addNotes(`[0:55-1:14]
GUION: «Y aquí entra nuestro modelo de decisión. Tú eliges qué te importa: beneficio, agua, suelo o menos riesgo. El modelo ordena las rotaciones y te enseña cuánto ganarías en un año malo, normal y bueno, con un semáforo legal de la ley del Mar Menor.»

GIF 2 (sustituye a la captura): ficha abierta → abrir FILTROS → mover «Ahorro de agua» o «Beneficio» → la tarjeta «La que mejor encaja con tus prioridades» cambia. 6-8 s, 15 fps, en bucle.
Nota: «menos riesgo» = riesgo de un mal año (clima y precio, más días de helada y calor). El modelo no calcula todavía el riesgo de lluvias torrenciales: no decirlo.`);

  // ======================= 6. CIERRE =======================
  pres.addSection({ title: 'Cierre' });
  s = pres.addSlide({ masterName: 'Cierre', sectionTitle: 'Cierre' });
  s.addImage({ path: A('agrockham-logo-on-dark.png'), x: 0.6, y: 0.6, w: 4.2, h: 4.2 * 461 / 2400, objectName: 'Logo Agrockham' });
  s.addText('Haciendo fácil lo difícil', { placeholder: 'title' });
  const col = (x, ic, h, items, name, fill) => {
    card(s, x, 3.0, 5.9, 3.1, name, C.text1);
    dot(s, x + 0.35, 3.3, 0.6, ic, name, fill);
    text(s, h, { x: x + 1.15, y: 3.3, w: 4.4, h: 0.6, fontSize: 20, bold: true, valign: 'middle', objectName: name + ' título' });
    text(s, items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
      { x: x + 0.4, y: 4.1, w: 5.2, h: 1.85, fontSize: 15, paraSpaceAfter: 6, objectName: name + ' lista' });
  };
  col(0.6, ICON.check, 'Ya funciona', ['Mapa con los recintos SIGPAC de toda España', 'Clima, lluvia y suelo de cada parcela',
    'Rotaciones con incertidumbre y semáforo legal'], 'Ya funciona', C.accent2);
  col(6.83, ICON.next, 'Lo siguiente', ['Registro «Mis parcelas»: añadir y quitar con un clic', 'Tu capacidad de inversión dentro del modelo',
    'Análisis completo en toda España y NDVI por satélite'], 'Lo siguiente', C.accent3);
  text(s, 'No sustituye a tu técnico: le da mejores datos.', { x: 0.6, y: 6.45, w: 12.13, h: 0.45, fontSize: 18, italic: true, color: C.accent1, objectName: 'Cierre frase' });
  s.addNotes(`[1:14-1:30]
GUION: «Lo siguiente: tu registro de parcelas y tu capacidad de inversión. Agrockham no sustituye a tu técnico: le da mejores datos. Haciendo fácil lo difícil.»
(Unos 5 s de margen hasta 1:30.)`);

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log('written', OUT);
})().catch(e => { console.error(e); process.exit(1); });
