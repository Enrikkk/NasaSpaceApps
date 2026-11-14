// "Tus parcelas": the farmer's own SIGPAC recintos, kept ONLY in this browser (localStorage). No account, no server,
// nothing about the parcels leaves the device. Pure logic + a tiny external store; the React hook is in useMyParcels.js.

export const STORAGE_KEY = 'agrockham.misParcelas.v1'
export const MAX_PARCELS = 50
export const RECINTO_KEYS = ['provincia', 'municipio', 'agregado', 'zona', 'poligono', 'parcela', 'recinto']
// Without these three there is no way to tell one recinto from another inside a municipality.
const REQUIRED = ['poligono', 'parcela', 'recinto']

const isInt = (v) => Number.isInteger(v) && v >= 0
const isCoord = (v) => typeof v === 'number' && Number.isFinite(v)

/** "30/37/0/0/18/426/1" from a recinto object (only the keys that exist, in SIGPAC order). */
export const refOf = (recinto) => RECINTO_KEYS.map((k) => recinto?.[k]).filter(isInt).join('/')

/** Only recintos that SIGPAC identifies can be saved (a click outside any recinto has no reference). */
export const isRegistrable = (recinto) => REQUIRED.every((k) => isInt(recinto?.[k]))

/** The record that is stored: reference, its parts, where it is and (if known) its size. No names, no personal data. */
export function makeParcel({ recinto, lat, lon, ha }, now = new Date()) {
  if (!isRegistrable(recinto) || !isCoord(lat) || !isCoord(lon)) return null
  const out = { ref: refOf(recinto) }
  for (const k of RECINTO_KEYS) if (isInt(recinto[k])) out[k] = recinto[k]
  out.lat = lat
  out.lon = lon
  if (typeof ha === 'number' && Number.isFinite(ha) && ha > 0) out.ha = ha
  out.fecha = now.toISOString().slice(0, 10)
  return out
}

/** Reads what localStorage holds; anything corrupt or hand-edited is dropped item by item, never thrown. */
export function parseStored(raw) {
  let data
  try { data = JSON.parse(raw) } catch { return [] }
  if (!Array.isArray(data)) return []
  const seen = new Set()
  const out = []
  for (const it of data) {
    const p = it && typeof it === 'object' ? makeParcel({ recinto: it, lat: it.lat, lon: it.lon, ha: it.ha }, new Date(0)) : null
    if (!p || seen.has(p.ref)) continue
    seen.add(p.ref)
    p.fecha = typeof it.fecha === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(it.fecha) ? it.fecha : p.fecha
    out.push(p)
    if (out.length >= MAX_PARCELS) break
  }
  return out
}

/** Pure list operations: they return a status instead of throwing. */
export function addTo(list, parcel) {
  if (!parcel) return { list, status: 'invalid' }
  if (list.some((p) => p.ref === parcel.ref)) return { list, status: 'duplicate' }
  if (list.length >= MAX_PARCELS) return { list, status: 'full' }
  return { list: [...list, parcel], status: 'added' }
}
export const removeFrom = (list, ref) => list.filter((p) => p.ref !== ref)
export const hasRef = (list, ref) => list.some((p) => p.ref === ref)

/** A filter that matches nothing. Written with a `literal` so MapLibre reads it as an EXPRESSION (a bare ['==', 1, 0]
 *  is taken for an old-style filter on a property called "1", is rejected, and takes the whole map style down). */
export const NO_MATCH = ['==', ['literal', 1], 0]

/**
 * MapLibre filter that matches exactly the saved recintos in the SIGPAC vector tiles (properties are numbers or
 * strings depending on the tile, hence to-number). Feature ids are NOT used: they are not stable between tiles.
 */
export function mapFilter(list) {
  if (!list.length) return NO_MATCH
  return ['any', ...list.map((p) => ['all', ...RECINTO_KEYS.filter((k) => isInt(p[k]))
    .map((k) => ['==', ['to-number', ['get', k], -1], p[k]])])]
}

/** [[west, south], [east, north]] around the saved parcels, or null. */
export function boundsOf(list) {
  if (!list.length) return null
  const lons = list.map((p) => p.lon)
  const lats = list.map((p) => p.lat)
  return [[Math.min(...lons), Math.min(...lats)], [Math.max(...lons), Math.max(...lats)]]
}

/**
 * External store over a storage object (injected so it is testable). Never throws: if the browser blocks storage
 * (private window, blocked site data) the list still works until the page is reloaded and `guarda` says false.
 */
export function createStore(getStorage) {
  const listeners = new Set()
  const load = () => {
    try { return { list: parseStored(getStorage().getItem(STORAGE_KEY)), guarda: true } } catch { return { list: [], guarda: false } }
  }
  let snap = load()
  const emit = () => listeners.forEach((l) => l())
  const persist = (list) => {
    let guarda = true
    try { getStorage().setItem(STORAGE_KEY, JSON.stringify(list)) } catch { guarda = false }
    snap = { list, guarda }
    emit()
  }
  return {
    getSnapshot: () => snap,
    subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn) },
    /** Re-read after another tab changed the list. */
    reload() { snap = load(); emit() },
    add(input) {
      const { list, status } = addTo(snap.list, makeParcel(input))
      if (status === 'added') persist(list)
      return status
    },
    remove(ref) {
      if (hasRef(snap.list, ref)) persist(removeFrom(snap.list, ref))
    },
  }
}
