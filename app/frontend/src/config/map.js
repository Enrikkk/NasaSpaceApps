// Map configuration: sources, regions, views. Every source and its licence is in submission/data-citations.md.

const IGN_WMTS = (service, layer) =>
  `https://www.ign.es/wmts/${service}?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=${layer}` +
  '&STYLE=default&FORMAT=image/jpeg&TILEMATRIXSET=GoogleMapsCompatible&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}'

// Spain incl. Canary Islands: IGN/PNOA tiles are only requested inside this box.
const SPAIN_TILE_BOUNDS = [-18.4, 27.4, 4.6, 44.0]

export const ATTRIBUTION = {
  gibs: 'Blue Marble: <a href="https://earthdata.nasa.gov/gibs" target="_blank" rel="noreferrer">NASA GIBS</a> / NASA Earth Observatory',
  // IGN licence asks for "CC-BY 4.0 scne.es" visible next to the data.
  ign: 'CC BY 4.0 <a href="https://www.scne.es/" target="_blank" rel="noreferrer">scne.es</a> · Instituto Geográfico Nacional',
  sigpac: 'Recintos SIGPAC © <a href="https://www.fega.gob.es/" target="_blank" rel="noreferrer">FEGA</a> (CC BY 4.0)',
}

export const SOURCES = {
  // NASA Blue Marble, shaded relief + bathymetry (max level 8): blue ocean with sea floor, relief on land.
  blueMarble: {
    type: 'raster',
    tiles: ['https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpeg'],
    // Declared as 128 px (they are 256) so MapLibre asks for two zoom levels more: sharp on large/retina screens.
    tileSize: 128,
    maxzoom: 8,
    attribution: ATTRIBUTION.gibs,
  },
  ignBase: {
    type: 'raster',
    tiles: [IGN_WMTS('ign-base', 'IGNBaseTodo')],
    tileSize: 256,
    bounds: SPAIN_TILE_BOUNDS,
    maxzoom: 17,
    attribution: ATTRIBUTION.ign,
  },
  pnoa: {
    type: 'raster',
    tiles: [IGN_WMTS('pnoa-ma', 'OI.OrthoimageCoverage')],
    tileSize: 128, // one zoom level more than the screen asks for: sharp on retina
    bounds: SPAIN_TILE_BOUNDS,
    maxzoom: 19,
    attribution: ATTRIBUTION.ign,
  },
  // Live SIGPAC vector tiles (hubcloud). Source layer: 'recinto'. The offline PMTiles copy is T-023/T-011 work.
  sigpac: {
    type: 'vector',
    tiles: ['https://sigpac-hubcloud.es/mvt/recinto@3857@pbf/{z}/{x}/{y}.pbf'],
    minzoom: 13,
    maxzoom: 15,
    attribution: ATTRIBUTION.sigpac,
  },
}

// Mainland Spain + Balearic Islands. The map cannot pan outside this box.
export const SPAIN_BOUNDS = [[-10.6, 34.8], [5.6, 44.4]]

// Each region is a box [[west, south], [east, north]]; the map fits it to the screen (desktop or phone).
export const REGIONS = [
  { id: 'espana', label: 'España', bounds: [[-9.4, 35.9], [3.4, 43.8]] },
  { id: 'campo-cartagena', label: 'Campo de Cartagena', bounds: [[-1.25, 37.55], [-0.7, 37.95]] },
  // Comarca del Noroeste: Caravaca, Cehegín, Moratalla, Calasparra, Bullas.
  { id: 'noroeste', label: 'Noroeste', bounds: [[-2.35, 37.85], [-1.55, 38.45]] },
  // Valle del Guadalentín: Lorca, Puerto Lumbreras, Totana, Alhama de Murcia.
  { id: 'guadalentin', label: 'Valle del Guadalentín', bounds: [[-1.95, 37.45], [-1.3, 37.95]] },
]

// Region the map jumps to on the first scroll.
export const FIRST_SCROLL_REGION = 'campo-cartagena'

// Demo parcel (app/data/torre-pacheco.mock.json).
export const DEMO_PARCEL = { label: 'Parcela demo · Torre-Pacheco', lon: -0.98838, lat: 37.7383 }

// Two base maps: 'satelite' (NASA Blue Marble, PNOA when zoomed into Spain; home globe and default) and 'mono'
// (IGN Base with all its detail, recoloured white/cream). SIGPAC parcels are a toggle on top of either.
export const VIEWS = [
  { id: 'satelite', label: 'Satélite', icon: 'satellite' },
  // 'mono' (IGN Base in white/cream) still works in MapView but has no button: satellite only for now.
]

// Home view: close, tilted, rotated look at the planet; the horizon stays below the logo (logo over space). Spain
// (focus) is big, centre-right, moved onto target (fractions of the viewport). Tuned at refSize; the zoom scales with screen area.
export const HOME_VIEW = {
  center: [-7.29, 42.06],
  zoom: 5.2,
  pitch: 52,
  bearing: 38,
  roll: -19,
  refSize: [1440, 900],
  focus: [-3.7, 40],
  target: [0.64, 0.59],
  targetNarrow: [0.5, 0.64],
}

// Where the zoom from the globe lands: deep inside Campo de Cartagena, close enough to see the parcels (zoom >= 13).
export const ENTRY_VIEW = { center: [-0.98, 37.74], zoom: 13.2 }

// Phone layout breakpoint (px). Keep in sync with the @media queries in the CSS modules.
export const NARROW_MAX = 760
