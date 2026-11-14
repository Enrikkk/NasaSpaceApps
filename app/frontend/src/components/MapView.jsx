import { useEffect, useRef, useState } from 'react'
import * as maplibregl from 'maplibre-gl'
import {
  SOURCES, SPAIN_BOUNDS, REGIONS, FIRST_SCROLL_REGION, ENTRY_VIEW, DEMO_PARCEL, NARROW_MAX,
} from '../config/map.js'
import { homeCamera, refineHome } from './homeGlobe.js'
import { COARSE_LAND, loadWorldFine } from '../config/worldData.js'
import { useAppState } from '../state/AppState.jsx'
import styles from './MapView.module.css'
import Starfield from './Starfield.jsx'
import { sigpacUseLabel } from '../config/sigpacUses.js'
import { haFromSquareMetres } from './parcel/helpers.js'
import { addIgnOverlay, IGN_OVERLAY_IDS } from './ignOverlay.js'
import { recintoFromProps } from '../api/client.js'
import { useMyParcels, myParcels } from '../state/useMyParcels.js'
import { mapFilter, boundsOf, NO_MATCH } from '../state/myParcels.js'

// Map colours come from the design tokens so DESIGN.md stays the single source.
const token = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim()

const PARCEL_MIN_ZOOM = 13
const ENTER_GRACE_MS = 900
const NO_PADDING = { top: 0, bottom: 0, left: 0, right: 0 }

// Keep fly-to targets out from under the panels: on the right on desktop, at the bottom on phones (App.module.css).
const panelPadding = () => (window.innerWidth <= NARROW_MAX
  ? { ...NO_PADDING, top: 110, bottom: 120 }
  : { ...NO_PADDING, right: Math.max(300, window.innerWidth * 0.26) })

const mercY = (lat) => Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI) / 360)) / (2 * Math.PI)

/**
 * Camera that fits a region box on screen, leaving room for the panels (passed as map padding).
 * Computed in Mercator rather than with map.cameraForBounds, which would add the home globe's padding.
 */
function regionCamera(map, r) {
  const [[w, s], [e, n]] = r.bounds
  const pad = panelPadding()
  const m = 24
  const width = window.innerWidth - pad.left - pad.right - 2 * m
  const height = window.innerHeight - pad.top - pad.bottom - 2 * m
  const zoom = Math.log2(Math.min(width / (((e - w) / 360) * 512), height / ((mercY(n) - mercY(s)) * 512)))
  return { center: [(w + e) / 2, (s + n) / 2], zoom, padding: pad, bearing: 0, pitch: 0, roll: 0 }
}

// "Ir a mis parcelas": onto the farmer's saved parcels (all of them in view), or the demo parcel when none is saved yet.
function parcelCamera() {
  const saved = myParcels.getSnapshot().list
  const flat = { padding: panelPadding(), bearing: 0, pitch: 0, roll: 0 }
  if (!saved.length) return { center: [DEMO_PARCEL.lon, DEMO_PARCEL.lat], zoom: 15.5, ...flat }
  const b = boundsOf(saved)
  const cam = regionCamera(null, { bounds: b })
  const zoom = Number.isFinite(cam.zoom) ? Math.min(16, cam.zoom) : 16
  return { ...cam, zoom: saved.length === 1 ? 16 : zoom }
}

// Last refined home camera, so flying back home lands exactly (no correction jump).
let savedHome = null

/** Put the camera on the home globe for the current screen size. */
function placeHome(map) {
  map.jumpTo(homeCamera())
  refineHome(map)
  savedHome = { ...homeCamera(), center: map.getCenter(), size: `${window.innerWidth}x${window.innerHeight}` }
}

const regionById = (id) => REGIONS.find((r) => r.id === id)

function buildStyle() {
  return {
    version: 8,
    projection: { type: 'globe' },
    // Blue halo around the globe, fading out as we zoom into Spain.
    sky: {
      'sky-color': token('--space'),
      'horizon-color': token('--atmosphere'),
      'fog-color': token('--atmosphere'),
      'atmosphere-blend': ['interpolate', ['linear'], ['zoom'], 0, 1, 5, 1, 7, 0],
    },
    sources: {
      ...SOURCES,
      land: { type: 'geojson', data: COARSE_LAND, attribution: 'Natural Earth' },
      borders: { type: 'geojson', data: { type: 'FeatureCollection', features: [] } },
    },
    layers: [
      // On a globe the background paints the sphere: it is the water of the mono view.
      { id: 'water', type: 'background', paint: { 'background-color': token('--ocean') } },
      // Satellite: NASA Blue Marble for the whole world...
      { id: 'blue-marble', type: 'raster', source: 'blueMarble', paint: { 'raster-fade-duration': 0 } },
      // ...mono: land and borders (Natural Earth)...
      { id: 'land', type: 'fill', source: 'land', layout: { visibility: 'none' }, paint: { 'fill-color': token('--land') } },
      {
        id: 'borders', type: 'line', source: 'borders', layout: { visibility: 'none' },
        paint: { 'line-color': token('--water'), 'line-opacity': 0.45, 'line-width': ['interpolate', ['linear'], ['zoom'], 2, 0.4, 8, 1.2] },
      },
      // ...and the Spanish maps on top (tiles only requested inside Spain).
      {
        id: 'ign-base', type: 'raster', source: 'ignBase', minzoom: 4, layout: { visibility: 'none' },
        paint: { 'raster-saturation': -1, 'raster-contrast': -0.1, 'raster-opacity': 0.75 },
      },
      { id: 'pnoa', type: 'raster', source: 'pnoa', minzoom: 5, layout: { visibility: 'none' } },
      {
        id: 'recintos-fill', type: 'fill', source: 'sigpac', 'source-layer': 'recinto',
        layout: { visibility: 'none' },
        paint: { 'fill-color': token('--green-light'), 'fill-opacity': ['case', ['boolean', ['feature-state', 'hover'], false], 0.35, 0.06] },
      },
      {
        id: 'recintos-line', type: 'line', source: 'sigpac', 'source-layer': 'recinto',
        layout: { visibility: 'none' },
        paint: { 'line-color': token('--cream'), 'line-width': ['interpolate', ['linear'], ['zoom'], 13, 0.4, 17, 1.6], 'line-opacity': 0.8 },
      },
      // The farmer's own parcels ("Tus parcelas"): red outline over a thin white halo so it reads on any base map.
      // The filter is set from the saved list (see the effect below); until then it matches nothing.
      {
        id: 'mis-parcelas-fill', type: 'fill', source: 'sigpac', 'source-layer': 'recinto', filter: NO_MATCH,
        layout: { visibility: 'none' },
        paint: { 'fill-color': token('--own-parcel'), 'fill-opacity': 0.28 },
      },
      {
        id: 'mis-parcelas-halo', type: 'line', source: 'sigpac', 'source-layer': 'recinto', filter: NO_MATCH,
        layout: { visibility: 'none', 'line-join': 'round' },
        paint: { 'line-color': token('--cream'), 'line-opacity': 0.95, 'line-width': ['interpolate', ['linear'], ['zoom'], 13, 3.2, 17, 7.5] },
      },
      {
        id: 'mis-parcelas-line', type: 'line', source: 'sigpac', 'source-layer': 'recinto', filter: NO_MATCH,
        layout: { visibility: 'none', 'line-join': 'round' },
        paint: { 'line-color': token('--own-parcel'), 'line-width': ['interpolate', ['linear'], ['zoom'], 13, 1.8, 17, 4.5] },
      },
    ],
  }
}


// In the satellite view PNOA fades in over Blue Marble while zooming into Spain, then Blue Marble fades out so the
// sea beyond PNOA coverage is the flat --ocean colour (= PNOA's own sea) instead of a stepped edge.
const PNOA_FADE_IN = ['interpolate', ['linear'], ['zoom'], 5.5, 0, 7.5, 1]
const BLUE_MARBLE_FADE_OUT = ['interpolate', ['linear'], ['zoom'], 7.5, 1, 9, 0]

/**
 * Layer visibility per base map, plus the SIGPAC parcels (always on in the map, off on the home globe).
 * satelite: Blue Marble + PNOA (fading in while zooming into Spain)
 * mono:     IGN Base with all its detail, greyed and laid at 75 % over cream land / light grey water (white-cream map)
 */
function applyView(map, view, parcels) {
  const show = (id, on) => map.getLayer(id) && map.setLayoutProperty(id, 'visibility', on ? 'visible' : 'none')
  const sat = view === 'satelite'
  show('blue-marble', sat)
  show('pnoa', sat)
  show('land', !sat)
  show('borders', !sat)
  show('ign-base', !sat)
  show('recintos-fill', parcels)
  show('recintos-line', parcels)
  show('mis-parcelas-fill', parcels)
  show('mis-parcelas-halo', parcels)
  show('mis-parcelas-line', parcels)
  // Satellite in the map (not the home globe): IGN towns, roads and names on top.
  for (const id of IGN_OVERLAY_IDS) show(id, sat && parcels)
  map.setPaintProperty('water', 'background-color', sat
    ? ['interpolate', ['linear'], ['zoom'], 7.5, token('--ocean'), 9, token('--ocean-deep')]
    : token('--water'))
  map.setPaintProperty('pnoa', 'raster-opacity', PNOA_FADE_IN)
  map.setPaintProperty('blue-marble', 'raster-opacity', BLUE_MARBLE_FADE_OUT)
  map.setPaintProperty('pnoa', 'raster-brightness-max', parcels ? 0.85 : 1)
  map.setPaintProperty('recintos-line', 'line-color', token(sat ? '--cream' : '--brand-dark'))
  map.setPaintProperty('recintos-fill', 'fill-color', token(sat ? '--green-light' : '--green'))
  // Mono: a faint fill shows each plot's extent; satellite: almost clear so the imagery shows.
  map.setPaintProperty('recintos-fill', 'fill-opacity',
    ['case', ['boolean', ['feature-state', 'hover'], false], 0.35, sat ? 0.06 : 0.12])
}

/**
 * One real map for the whole app.
 * home: big satellite globe, Spain in the lower-left part. Click or scroll on it -> zoom to Spain.
 * map:  Spain-only. First scroll flies to Región de Murcia, then the wheel zooms normally.
 */
export default function MapView() {
  const { screen, setScreen, view, regionId, setRegionId, entry, setEntry, setSelectedParcel, flyTarget } = useAppState()
  const containerRef = useRef(null)
  const mapRef = useRef(null)
  const screenRef = useRef(screen)
  const selectParcelRef = useRef(setSelectedParcel)
  const firstScrollDone = useRef(false)
  const enteredAt = useRef(0)
  const [zoom, setZoom] = useState(0)
  const [ready, setReady] = useState(false)
  const [overlay, setOverlay] = useState(0)

  screenRef.current = screen
  selectParcelRef.current = setSelectedParcel

  // Create the map once, as the home globe.
  useEffect(() => {
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: buildStyle(),
      ...homeCamera(),
      maxZoom: 18,
      scrollZoom: false, // home: wheel enters the map; map: enabled after the first-scroll jump
      dragPan: false, // home: the globe does not move; any touch or press opens the map (enabled on the map screen)
      touchZoomRotate: false, // idem (pinch)
      attributionControl: false,
      dragRotate: false,
      pitchWithRotate: false,
      keyboard: false,
    })
    map.touchZoomRotate.disableRotation()
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-left')
    map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left')
    map.addControl(new maplibregl.AttributionControl({ compact: false }), 'bottom-left')


    const onWheel = (e) => {
      if (screenRef.current === 'home') {
        e.preventDefault()
        if (e.deltaY !== 0) setScreen('map')
        return
      }
      if (firstScrollDone.current) return
      e.preventDefault()
      // Ignore the tail of the gesture that opened the map, and anything while the entry zoom is running.
      if (e.deltaY === 0 || performance.now() - enteredAt.current < ENTER_GRACE_MS || map.isMoving()) return
      firstScrollDone.current = true
      setRegionId(FIRST_SCROLL_REGION)
      map.once('moveend', () => map.scrollZoom.enable())
    }
    map.getCanvasContainer().addEventListener('wheel', onWheel, { passive: false })

    map.on('click', () => { if (screenRef.current === 'home') setScreen('map') })
    // On the home globe ANY interaction (tap, press, swipe, pinch) opens the map; the globe itself never pans or scrolls.
    const openFromHome = () => { if (screenRef.current === 'home') setScreen('map') }
    map.getCanvasContainer().addEventListener('touchstart', openFromHome, { passive: true })
    map.getCanvasContainer().addEventListener('mousedown', openFromHome)

    // Hover highlight + card on SIGPAC parcels.
    let hoveredId = null
    const setHover = (id) => {
      if (hoveredId !== null) map.setFeatureState({ source: 'sigpac', sourceLayer: 'recinto', id: hoveredId }, { hover: false })
      hoveredId = id
      if (id !== null) map.setFeatureState({ source: 'sigpac', sourceLayer: 'recinto', id }, { hover: true })
    }
    map.on('mousemove', 'recintos-fill', (e) => {
      map.getCanvas().style.cursor = 'pointer'
      setHover(e.features?.[0]?.id ?? null)
    })
    map.on('mouseleave', 'recintos-fill', () => { map.getCanvas().style.cursor = ''; setHover(null) })
    map.on('click', 'recintos-fill', (e) => {
      const tile = e.features?.[0]?.properties ?? {}
      selectParcelRef.current({ lat: e.lngLat.lat, lon: e.lngLat.lng, recinto: recintoFromProps(tile), tile })
    })

    // After MapLibre has resized its canvas (not on window 'resize', which comes first).
    map.on('resize', () => { if (screenRef.current === 'home' && !map.isMoving()) placeHome(map) })

    map.on('zoom', () => setZoom(map.getZoom()))
    // The camera needs no tiles: set it at once instead of waiting for 'load' (which waits for tiles).
    placeHome(map)
    map.on('style.load', async () => {
      setReady(true)
      try {
        await addIgnOverlay(map, 'recintos-fill')
        setOverlay((n) => n + 1)
      } catch { /* offline: satellite without names */ }
    })
    map.on('load', async () => {
      const fine = await loadWorldFine()
      if (!mapRef.current) return
      map.getSource('land').setData(fine.land)
      map.getSource('borders').setData(fine.borders)
    })
    mapRef.current = map
    if (import.meta.env.DEV) window.__agroMap = map // debugging from the browser console
    return () => {
      map.getCanvasContainer().removeEventListener('wheel', onWheel)
      map.remove()
      mapRef.current = null
    }
  }, [setScreen, setRegionId])

  // Screen changes: zoom from the globe into Spain, or back out to the globe.
  useEffect(() => {
    const map = mapRef.current
    if (!map) return
    map.stop()
    if (screen === 'map') {
      map.dragPan.enable()
      map.touchZoomRotate.enable()
      enteredAt.current = performance.now()
      map.getCanvas().style.cursor = ''
      // Deep zoom from the globe: onto the farmer's parcel, or into Campo de Cartagena. Either way the wheel then
      // zooms normally (no first-scroll jump).
      firstScrollDone.current = true
      const cam = entry === 'parcel' ? parcelCamera() : { ...ENTRY_VIEW, padding: panelPadding(), bearing: 0, pitch: 0, roll: 0 }
      map.flyTo({ ...cam, duration: 4200, curve: 1.4, essential: true })
      map.once('moveend', () => {
        if (screenRef.current !== 'map') return
        map.setMinZoom(Math.min(4.6, regionCamera(map, regionById('espana')).zoom - 0.4))
        map.setMaxBounds(SPAIN_BOUNDS)
        map.scrollZoom.enable()
      })
    } else {
      firstScrollDone.current = false
      setRegionId('espana')
      setEntry('cartagena')
      map.scrollZoom.disable()
      map.dragPan.disable()
      map.touchZoomRotate.disable()
      map.setMaxBounds(null)
      map.setMinZoom(0)
      const same = savedHome?.size === `${window.innerWidth}x${window.innerHeight}`
      const { size: _size, ...cam } = same ? savedHome : homeCamera()
      map.flyTo({ ...cam, duration: 2400, essential: true })
      map.once('moveend', () => { if (screenRef.current === 'home') refineHome(map) })
    }
    // regionId is read once on entry; later region changes are handled below.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [screen])

  // Region picked while on the map -> fly there. Counts as the "first scroll".
  useEffect(() => {
    const map = mapRef.current
    const r = regionById(regionId)
    if (!map || !r || screenRef.current !== 'map' || performance.now() - enteredAt.current < 50) return
    if (regionId !== 'espana' && !firstScrollDone.current) {
      firstScrollDone.current = true
      map.once('moveend', () => map.scrollZoom.enable())
    }
    map.flyTo({ ...regionCamera(map, r), duration: 2200, essential: true })
  }, [regionId])

  // View / parcels changes -> restyle. Home always shows the plain satellite globe.
  useEffect(() => {
    const map = mapRef.current
    if (!map || !ready) return
    const home = screen === 'home'
    applyView(map, home ? 'satelite' : view, !home)
  }, [view, ready, screen, overlay])

  // The saved parcels drive the red outline (filter on the SIGPAC tile properties).
  const { list: savedParcels } = useMyParcels()
  useEffect(() => {
    const map = mapRef.current
    if (!map || !ready) return
    const f = mapFilter(savedParcels)
    for (const id of ['mis-parcelas-fill', 'mis-parcelas-halo', 'mis-parcelas-line']) if (map.getLayer(id)) map.setFilter(id, f)
  }, [savedParcels, ready, overlay])

  // "Ver" in Tus parcelas: fly to that parcel, leaving room for the parcel sheet (left on desktop, bottom on phones).
  useEffect(() => {
    const map = mapRef.current
    if (!map || !flyTarget || screenRef.current !== 'map') return
    const phone = window.innerWidth <= NARROW_MAX
    const padding = phone ? { ...NO_PADDING, bottom: Math.round(window.innerHeight * 0.45) } : { ...NO_PADDING, left: 460 }
    map.flyTo({ center: [flyTarget.lon, flyTarget.lat], zoom: Math.max(map.getZoom(), 16.5), padding, duration: 1800, essential: true })
  }, [flyTarget])

  return (
    <div className={`${styles.wrap} ${screen === 'home' ? styles.home : ''}`}>
      <Starfield visible />
      <div ref={containerRef} className={styles.map} aria-label="Mapa" role="region" />
      {screen === 'map' && zoom < PARCEL_MIN_ZOOM && (
        <p className={styles.notice}>Acércate para ver los recintos SIGPAC</p>
      )}
    </div>
  )
}

// SIGPAC attribute names (provincia, municipio, poligono, parcela, recinto, uso_sigpac, superficie...).
function parcelCard(p) {
  const ref = ['provincia', 'municipio', 'agregado', 'zona', 'poligono', 'parcela', 'recinto']
    .map((k) => p[k]).filter((v) => v !== undefined && v !== null).join(':')
  const ha = haFromSquareMetres(p.superficie)
  const div = document.createElement('div')
  const rows = [
    ['Referencia SIGPAC', ref || '—'],
    ['Uso', sigpacUseLabel(p.uso_sigpac)],
    ha && ['Superficie', ha],
    p.coef_regadio !== undefined && ['Regadío', `${p.coef_regadio} %`],
  ].filter(Boolean)
  const title = document.createElement('strong')
  title.textContent = 'Recinto'
  div.append(title)
  const dl = document.createElement('dl')
  for (const [k, v] of rows) {
    const dt = document.createElement('dt'); dt.textContent = k
    const dd = document.createElement('dd'); dd.textContent = String(v)
    dl.append(dt, dd)
  }
  div.append(dl)
  return div
}
