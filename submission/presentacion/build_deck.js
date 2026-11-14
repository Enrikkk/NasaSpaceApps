// Builds agrockham-presentacion.pptx (6 slides, ~1:30). Brand: brand/README.md (palette, logo, Inter).
// Run: NODE_PATH=<dir with pptxgenjs> PPTX_SKILL_DIR=<pptx skill dir> node build_deck.js
const path = require('path');
const pptxgen = require('pptxgenjs');
const { applyTheme } = require(path.join(process.env.PPTX_SKILL_DIR || '.', 'scripts/apply_theme.js'));

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

// Eurostat apri_ap_crpouta, Spain, selling price EUR/100 kg (snapshot in app/data/tables/source_snapshot/eurostat_prices_es.csv)
const YEARS = Array.from({ length: 20 }, (_, i) => String(2005 + i));
const LECHUGA = [51.12, 39.4, 42.16, 49.0, 37.69, 46.84, 30.0, 43.9, 41.73, 30.23, 25.12, 32.02, 39.43, 22.55, 27.87, 24.73, 27.49, 27.41, 34.22, 31.42];
const MELON = [25.84, 31.01, 34.64, 42.06, 30.09, 37.02, 25.99, 27.35, 33.54, 27.57, 42.48, 33.91, 33.02, 33.13, 28.37, 33.69, 29.13, 45.5, 58.52, 47.57];

(async () => {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE'; // 13.333 x 7.5 in
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.author = 'Equipo Agrockham';
  pres.title = 'Agrockham';
  const C = pres.SchemeColor;

  pres.defineSlideMaster({ title: 'Portada', background: { color: '05070A' }, objects: [] });
  pres.defineSlideMaster({
    title: 'Contenido', background: { color: THEME.colors.dk1 },
    objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.7, y: 0.5, w: 11.93, h: 0.75,
      fontSize: 30, bold: true, color: C.background1, align: 'left', valign: 'middle', margin: 0 }, text: '' } }],
  });
  pres.defineSlideMaster({
    title: 'Cierre', background: { color: THEME.colors.dk2 },
    objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.7, y: 2.0, w: 11.93, h: 0.9,
      fontSize: 40, bold: true, color: C.background1, align: 'left', valign: 'middle', margin: 0 }, text: '' } }],
  });

  const text = (s, t, o) => s.addText(t, Object.assign({ isTextBox: true, margin: 0, color: C.background1, fontSize: 16, valign: 'top' }, o));
  const credit = (s, t, x, y, w) => text(s, t, { x, y, w, h: 0.25, fontSize: 10, color: C.background2, objectName: 'Créditos' });
  const MAP_CREDIT = 'Captura de la app · Recintos SIGPAC © FEGA (CC BY 4.0) · Ortofoto PNOA © IGN (CC BY 4.0 scne.es)';

  // 1. Portada
  pres.addSection({ title: 'Apertura' });
  let s = pres.addSlide({ masterName: 'Portada', sectionTitle: 'Apertura' });
  s.addImage({ path: A('globo.jpg'), x: 0, y: 0, w: 13.333, h: 7.5, objectName: 'Globo (app)' });
  s.addImage({ path: A('agrockham-logo-on-dark.png'), x: 0.7, y: 2.55, w: 6.0, h: 6.0 * 461 / 2400, objectName: 'Logo' });
  text(s, 'Qué sembrar, cuándo y con qué riesgo', { x: 0.7, y: 3.85, w: 7.5, h: 0.6, fontSize: 26, objectName: 'Lema' });
  text(s, 'NASA Space Apps Challenge 2026 · Murcia', { x: 0.7, y: 6.6, w: 7, h: 0.3, fontSize: 12, objectName: 'Evento' });
  credit(s, 'Imagen: Blue Marble, NASA GIBS / NASA Earth Observatory · IGN (CC BY 4.0 scne.es)', 0.7, 6.95, 9);
  s.addNotes('[0:00-0:06]\nGUION: «Esto es Agrockham: te ayuda a decidir qué sembrar, cuándo y con qué riesgo.»');

  // 2. Mapa
  pres.addSection({ title: 'Producto' });
  s = pres.addSlide({ masterName: 'Contenido', sectionTitle: 'Producto' });
  s.addText('Todas las parcelas de España, en un mapa', { placeholder: 'title' });
  s.addImage({ path: A('mapa-sigpac.jpg'), x: 0.7, y: 1.55, w: 8.4, h: 8.4 * 9 / 16, objectName: 'GIF 1: zoom del globo a la parcela' });
  credit(s, MAP_CREDIT, 0.7, 6.38, 8.4);
  text(s, '170.265', { x: 9.6, y: 1.5, w: 3.03, h: 0.75, fontSize: 40, bold: true, color: C.accent1, objectName: 'Cifra' });
  text(s, 'recintos con análisis completo en el Campo de Cartagena', { x: 9.6, y: 2.3, w: 3.03, h: 0.9, objectName: 'Cifra texto' });
  text(s, 'En el mapa se ven los recintos SIGPAC de toda España. Un clic abre la ficha de la parcela.',
    { x: 9.6, y: 3.5, w: 3.03, h: 1.2, fontSize: 14, color: C.background2, objectName: 'Detalle' });
  s.addNotes(`[0:06-0:23]
GUION: «Para ordenar tantos datos hemos creado un mapa con todas las parcelas oficiales de España. Haces clic en la tuya y ves su superficie, su riego y su pendiente. El análisis completo ya funciona en el Campo de Cartagena: más de ciento setenta mil parcelas.»

GIF 1 (opcional, sustituye a la captura): «Ir a mis parcelas» → zoom del globo → clic en un recinto → se abre la ficha. 16:9, 6-8 s, 15 fps.
Clic derecho en la imagen → Cambiar imagen → Desde un archivo.`);

  // 3. Datos
  s = pres.addSlide({ masterName: 'Contenido', sectionTitle: 'Producto' });
  s.addText('Lo que sabemos de cada parcela', { placeholder: 'title' });
  s.addImage({ path: A('panel-parcela.jpg'), x: 0.7, y: 1.55, w: 4.4, h: 4.4 / 0.921, objectName: 'Ficha de la parcela (app)' });
  credit(s, 'Ficha de un recinto en la app', 0.7, 6.4, 4.4);
  const rows = [['Clima diario, 20 años', 'NASA POWER'], ['Lluvia por satélite', 'GPM IMERG (NASA) y ERA5'], ['Suelo', 'ISRIC SoilGrids'],
                ['Parcela y cultivos declarados', 'SIGPAC, FEGA'], ['Heladas y calor', 'Estaciones SIAM-IMIDA'], ['Ley del Mar Menor', 'Ley 3/2020, BOE']];
  rows.forEach(([h, src], i) => {
    const x = 5.8 + (i % 2) * 3.55, y = 1.6 + Math.floor(i / 2) * 1.05;
    text(s, [{ text: h, options: { bold: true, breakLine: true } }, { text: src, options: { color: C.background2, fontSize: 14 } }],
      { x, y, w: 3.3, h: 0.8, objectName: h });
  });
  text(s, 'Las tres fuentes de lluvia difieren hasta un 40 % en la misma parcela. Por eso mostramos un rango.',
    { x: 5.8, y: 5.0, w: 6.8, h: 0.8, fontSize: 18, color: C.accent1, objectName: 'Lluvia' });
  s.addNotes(`[0:23-0:43]
GUION: «Con ese clic juntamos datos que antes estaban dispersos: veinte años de clima diario de NASA POWER, la lluvia del satélite GPM IMERG, el suelo y los cultivos que declaraste. Tres fuentes de lluvia difieren hasta un cuarenta por ciento en la misma parcela, así que mostramos un rango.»`);

  // 4. Precios
  s = pres.addSlide({ masterName: 'Contenido', sectionTitle: 'Producto' });
  s.addText('20 años de precios de venta', { placeholder: 'title' });
  s.addChart(pres.charts.LINE, [{ name: 'Lechuga', labels: YEARS, values: LECHUGA }, { name: 'Melón', labels: YEARS, values: MELON }], {
    x: 0.7, y: 1.45, w: 11.93, h: 4.45, objectName: 'Gráfico precios',
    chartColors: [THEME.colors.lt1, THEME.colors.accent1], lineSize: 2.5, lineDataSymbol: 'none',
    showLegend: true, legendPos: 't', legendFontSize: 14, legendColor: THEME.colors.lt1, legendFontFace: '+mn-lt',
    catAxisLabelColor: THEME.colors.lt2, valAxisLabelColor: THEME.colors.lt2, catAxisLabelFontSize: 12, valAxisLabelFontSize: 12,
    catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt', catAxisLineShow: false, valAxisLineShow: false,
    valGridLine: { color: '3D423C', size: 1 }, catGridLine: { style: 'none' }, valAxisMinVal: 0,
    showValAxisTitle: true, valAxisTitle: '€ por 100 kg', valAxisTitleColor: THEME.colors.lt2, valAxisTitleFontSize: 12, valAxisTitleFontFace: '+mn-lt',
  });
  text(s, 'Cada rotación se simula año a año con el clima y el precio de ese año.', { x: 0.7, y: 6.05, w: 11.93, h: 0.4, fontSize: 18, objectName: 'Explicación' });
  credit(s, 'Precio de venta en España, Eurostat (apri_ap_crpouta). Son precios nacionales; en Murcia pueden variar.', 0.7, 6.6, 11.93);
  s.addNotes(`[0:43-0:55]
GUION: «Además, hemos creado un sistema económico con veinte años de precios de mercado. Simulamos cada rotación año a año, con el clima y el precio de ese mismo año.»`);

  // 5. Decisión
  s = pres.addSlide({ masterName: 'Contenido', sectionTitle: 'Producto' });
  s.addText('Tú decides qué te importa', { placeholder: 'title' });
  s.addImage({ path: A('rotaciones-filtros.jpg'), x: 4.9, y: 1.55, w: 7.73, h: 7.73 * 9 / 16, objectName: 'GIF 2: prioridades y rotaciones' });
  credit(s, MAP_CREDIT, 4.9, 6.0, 7.73);
  text(s, ['Beneficio', 'Ahorro de agua', 'Salud del suelo', 'Menos riesgo'].map((t, i, a) => ({ text: t, options: { breakLine: i < a.length - 1 } })),
    { x: 0.7, y: 1.6, w: 3.8, h: 1.9, fontSize: 22, bold: true, color: C.accent1, paraSpaceAfter: 6, objectName: 'Prioridades' });
  text(s, 'Las rotaciones se ordenan según lo que eliges, con lo que ganarías en un año malo, normal y bueno, y el semáforo legal de la ley del Mar Menor.',
    { x: 0.7, y: 3.85, w: 3.8, h: 2.0, objectName: 'Explicación' });
  s.addNotes(`[0:55-1:14]
GUION: «Y aquí entra nuestro modelo de decisión. Tú eliges qué te importa: beneficio, agua, suelo o menos riesgo. El modelo ordena las rotaciones y te enseña cuánto ganarías en un año malo, normal y bueno, con un semáforo legal de la ley del Mar Menor.»

GIF 2 (opcional, sustituye a la captura): abrir FILTROS → mover «Ahorro de agua» o «Beneficio» → cambia la rotación recomendada. 16:9, 6-8 s, 15 fps.`);

  // 6. Cierre
  pres.addSection({ title: 'Cierre' });
  s = pres.addSlide({ masterName: 'Cierre', sectionTitle: 'Cierre' });
  s.addImage({ path: A('agrockham-logo-on-dark.png'), x: 0.7, y: 0.8, w: 4.0, h: 4.0 * 461 / 2400, objectName: 'Logo' });
  s.addText('Haciendo fácil lo difícil', { placeholder: 'title' });
  const col = (x, h, items) => text(s, [{ text: h, options: { bold: true, color: C.accent1, breakLine: true } }]
    .concat(items.map((t, i) => ({ text: t, options: { breakLine: i < items.length - 1 } }))),
    { x, y: 3.6, w: 5.6, h: 2.2, fontSize: 18, paraSpaceAfter: 8, objectName: h });
  col(0.7, 'Ya funciona', ['Mapa con los recintos SIGPAC de España', 'Clima, lluvia y suelo de cada parcela', 'Rotaciones con incertidumbre y semáforo legal']);
  col(7.0, 'Lo siguiente', ['Registro de parcelas', 'Capacidad de inversión en el modelo', 'Análisis completo en toda España']);
  s.addNotes(`[1:14-1:30]
GUION: «Lo siguiente: tu registro de parcelas y tu capacidad de inversión. Agrockham es una herramienta para ti y para tu técnico. Haciendo fácil lo difícil.»`);

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log('written', OUT);
})().catch(e => { console.error(e); process.exit(1); });
