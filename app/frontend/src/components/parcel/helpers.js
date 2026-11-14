// Formatting and ranking helpers for the parcel panel. Everything tolerates missing or null fields.

const nf = (opts) => new Intl.NumberFormat('es-ES', { useGrouping: 'always', ...opts })
const int = nf({ maximumFractionDigits: 0 })
const one = nf({ maximumFractionDigits: 1, minimumFractionDigits: 1 })
const two = nf({ maximumFractionDigits: 2 })

export const isNum = (v) => typeof v === 'number' && Number.isFinite(v)

export const fmtInt = (v) => (isNum(v) ? int.format(Math.round(v)) : null)
export const fmtOne = (v) => (isNum(v) ? one.format(v) : null)
export const fmtHa = (v) => (isNum(v) ? two.format(v) : null)

/** "1.234 €" or "-1.234 €" */
export const fmtEur = (v) => (isNum(v) ? `${int.format(Math.round(v))} €` : null)

/** Number without unit for ranges: "-5.790" */
export const fmtPlain = (v) => (isNum(v) ? int.format(Math.round(v)) : null)

export const capitalize = (s) => (typeof s === 'string' && s ? s[0].toUpperCase() + s.slice(1) : s)

/** SIGPAC reference "30/37/0/0/18/426/1" from the recinto object; falls back to what exists. */
export function refFromRecinto(recinto) {
  if (!recinto) return ''
  return ['provincia', 'municipio', 'agregado', 'zona', 'poligono', 'parcela', 'recinto']
    .map((k) => recinto[k]).filter((v) => v !== undefined).join('/')
}

/** "Label: plan text" -> { label, plan, steps }. Steps split on the arrow the engine uses between years. */
export function splitName(nombre) {
  const text = typeof nombre === 'string' ? nombre : ''
  const i = text.indexOf(': ')
  const label = i > 0 ? text.slice(0, i) : text
  const plan = i > 0 ? text.slice(i + 2) : ''
  const steps = plan.split(' → ').map((s) => s.trim()).filter(Boolean)
  return { label: label || 'Rotación', plan, steps }
}

/** Farmer priorities (filters.js keys) -> criterios keys in the API. */
export const PRIORITY_TO_CRITERIO = { beneficio: 'margen', agua: 'agua', suelo: 'suelo_n', riesgo: 'riesgo' }

/**
 * Weighted mean of the criterios (all 0-1, 1 = best) with the farmer's weights. Null criteria are ignored.
 * If every weight is 0 (or none of the available criteria has weight) all available criteria weigh the same.
 * Returns null when the rotation has no criterion at all.
 */
export function priorityScore(criterios, priorities) {
  const items = []
  for (const [pKey, cKey] of Object.entries(PRIORITY_TO_CRITERIO)) {
    const c = criterios?.[cKey]
    if (isNum(c)) items.push({ c, w: Math.max(0, Number(priorities?.[pKey]) || 0) })
  }
  if (!items.length) return null
  let total = items.reduce((s, x) => s + x.w, 0)
  if (total <= 0) { items.forEach((x) => { x.w = 1 }); total = items.length }
  return items.reduce((s, x) => s + x.c * x.w, 0) / total
}

/**
 * Reference rotation first, then the rest by priority score (best first, unscored last, ties keep API order).
 * Returns [{ rot, score, best }], `best` marks the top-ranked non-reference rotation that has a score.
 */
export function rankRotations(rotaciones, priorities) {
  const list = Array.isArray(rotaciones) ? rotaciones : []
  const ref = list.filter((r) => r?.es_actual)
  const rest = list
    .filter((r) => r && !r.es_actual)
    .map((rot, i) => ({ rot, i, score: priorityScore(rot.criterios, priorities) }))
    .sort((a, b) => (b.score ?? -1) - (a.score ?? -1) || a.i - b.i)
  const out = [
    ...ref.map((rot) => ({ rot, score: priorityScore(rot.criterios, priorities), best: false })),
    ...rest.map(({ rot, score }) => ({ rot, score, best: false })),
  ]
  const top = out.find((x) => !x.rot.es_actual && x.score !== null)
  if (top) top.best = true
  return out
}

/** Readable names for the blocks in _meta.estado_bloques. */
export const BLOCK_LABELS = {
  parcela: 'los datos de la parcela',
  historia: 'el historial de cultivos',
  ndvi: 'la vegetación vista desde satélite',
  clima: 'el clima',
  suelo: 'el suelo',
  rotaciones: 'las rotaciones',
}

export const LEGAL = {
  verde: { word: 'Permitido', icon: 'ok' },
  amarillo: { word: 'Revisar', icon: 'warn' },
  rojo: { word: 'No permitido', icon: 'stop' },
  gris: { word: 'Sin evaluar', icon: 'unknown' },
}
export const legalOf = (color) => LEGAL[color] ?? LEGAL.gris

export const ENV_LEVELS = {
  alto: { word: 'Alto', n: 3 },
  medio: { word: 'Medio', n: 2 },
  bajo: { word: 'Bajo', n: 1 },
}
