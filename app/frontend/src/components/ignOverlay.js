// Towns, municipalities and main roads from the IGN vector base map (CC BY 4.0 scne.es), drawn over the satellite
// view. Vector text is sharp at any screen resolution. We load IGN's own published style and keep only what we need.
const IGN_STYLE = 'https://vt-mapabase.idee.es/files/styles/mapaBase_scn_color1_CNIG.json'
const SOURCE = 'ignVector'
const ATTRIBUTION = 'Mapa base vectorial: CC BY 4.0 <a href="https://www.scne.es/" target="_blank" rel="noreferrer">scne.es</a>'

const ROADS = ['autopista_lin', 'autovia_lin', 'carretera_general_lin',
  'carretera_autonomica_1er_nivel_lin', 'carretera_autonomica_2do_nivel_lin']
const LABEL_LAYERS = ['nombre_poblacion_construccion_pto', 'nombre_division_administrativa_pto', 'contexto_nombre_poblacion_pto']
const LABEL_KINDS = /nucleo_poblacion|capital|municipio|provincia|simbolo-nucleo/

export const IGN_OVERLAY_IDS = []

/** Fetch IGN's style and add the road + label layers (hidden until a view shows them). */
export async function addIgnOverlay(map, beforeLabels) {
  const style = await (await fetch(IGN_STYLE)).json()
  const src = Object.values(style.sources).find((s) => s.type === 'vector')
  map.setGlyphs(style.glyphs)
  map.setSprite(style.sprite)
  // Spain only (incl. Canary Islands) and from zoom 6: outside that the IGN server answers 403.
  map.addSource(SOURCE, { ...src, bounds: [-18.4, 27.4, 4.6, 44.0], minzoom: Math.max(src.minzoom || 0, 6), attribution: ATTRIBUTION })

  for (const l of style.layers) {
    if (l.source && style.sources[l.source] !== src) continue
    const sl = l['source-layer'] || ''
    const road = l.type === 'line' && ROADS.includes(sl) && !/contorno|construccion|tnl_/.test(l.id)
    const shield = l.type === 'symbol' && ROADS.includes(sl) && /simbolo/.test(l.id)
    const label = l.type === 'symbol' && LABEL_LAYERS.includes(sl) && LABEL_KINDS.test(l.id)
    if (!road && !shield && !label) continue

    const layer = { ...l, id: `ign-${l.id}`, source: SOURCE, layout: { ...l.layout, visibility: 'none' }, paint: { ...l.paint } }
    if (road) {
      layer.paint['line-color'] = 'rgba(255, 246, 225, 0.7)'
    } else if (label) {
      layer.paint['text-color'] = '#ffffff'
      layer.paint['text-halo-color'] = 'rgba(0, 0, 0, 0.75)'
      layer.paint['text-halo-width'] = 1.4
      layer.paint['icon-opacity'] = 0.9
    }
    map.addLayer(layer, road ? beforeLabels : undefined)
    IGN_OVERLAY_IDS.push(layer.id)
  }
}
