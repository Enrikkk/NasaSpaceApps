// Pure logic of the parcel panel's ranked list: crops, 1-100 score and the two flags (Eco, Riesgo).
// Everything tolerates missing or null fields: no data means "sin evaluar", never an invented number.
import { isNum, fmtInt, fmtPlain, splitName } from './helpers.js'

/** 0-1 weighted score -> whole number 1-100 (never 0: the list always says "worst of the options", not "nothing"). */
export const score100 = (s) => (isNum(s) ? Math.min(100, Math.max(1, Math.round(s * 100))) : null)

const COVER = /cubierta|abono verde/i
const NOT_A_CROP = /barbecho|cubierta|abono verde/i

function cycleNames(rot) {
  const out = []
  for (const y of Array.isArray(rot?.plan_anios) ? rot.plan_anios : []) {
    for (const c of Array.isArray(y?.ciclos) ? y.ciclos : []) if (typeof c === 'string' && c.trim()) out.push(c.trim())
  }
  return out
}
const unique = (list) => list.filter((x, i) => list.indexOf(x) === i)

/** Crops of the rotation, in order of appearance, without fallow or cover crops. */
export const cropsOf = (rot) => unique(cycleNames(rot).filter((c) => !NOT_A_CROP.test(c)))
/** Cover crops ("cubierta de veza"): they help the soil, so the list says it. */
export const coversOf = (rot) => unique(cycleNames(rot).filter((c) => COVER.test(c)))

/** Subtitle: the strategy the engine used to build the option ("Máximo margen", "Suelo y agua"…) + cover crop. */
export function subtitleOf(rot) {
  const { label } = splitName(rot?.nombre)
  const covers = coversOf(rot)
  return covers.length ? `${label} · con ${covers.join(' y ')}` : label
}

/** Risk cut-offs on "% of good years" (ASSUMED by us; the flag text says so). >= bajo: low risk; >= medio: medium. */
export const RISK_CUTS = { bajo: 90, medio: 75 }

export function riskLevel(exito) {
  const v = exito?.valor
  if (!isNum(v)) return null
  return v >= RISK_CUTS.bajo ? 'bajo' : v >= RISK_CUTS.medio ? 'medio' : 'alto'
}

const money = (v) => (v < 0 ? `una pérdida de ${fmtPlain(Math.abs(v))} € por hectárea` : `${fmtPlain(v)} € por hectárea`)

/** { level, label, tone, text }; tone is good|mid|bad|none (the UI also writes the word, never colour alone). */
export function riskInfo(rot) {
  const e = rot?.exito_pct
  const level = riskLevel(e)
  if (!level) {
    return {
      level: null, label: 'Riesgo: sin evaluar', short: 'sin dato', tone: 'none',
      text: 'No podemos estimar el riesgo: a esta opción le falta el precio de algún cultivo, y sin precio no sabemos en cuántos años saldría bien.',
    }
  }
  const [lo, hi] = Array.isArray(e.horquilla) ? e.horquilla : []
  const range = isNum(lo) && isNum(hi) ? ` (entre ${fmtInt(lo)} y ${fmtInt(hi)} según la incertidumbre)` : ''
  const worst = Array.isArray(e.peores_anios) ? e.peores_anios[0] : null
  const worstText = worst && isNum(worst.margen_eur_ha)
    ? ` El peor año simulado${isNum(worst.anio) ? ` (${worst.anio})` : ''} dejó ${money(worst.margen_eur_ha)}.` : ''
  return {
    level, label: `Riesgo: ${level}`, short: level, tone: level === 'bajo' ? 'good' : level === 'medio' ? 'mid' : 'bad',
    text: `En ${fmtInt(e.valor)} de cada 100 años simulados del histórico, esta opción sale bien${range}.${worstText} `
      + `Los límites de la etiqueta (${RISK_CUTS.bajo} y ${RISK_CUTS.medio}) son supuestos nuestros. `
      + 'Solo cuenta clima y precios de años pasados: no es una garantía.',
  }
}

const ECO = { alto: ['good', 'alto'], medio: ['mid', 'medio'], bajo: ['bad', 'bajo'] }

/** Same shape as riskInfo, from the engine's environmental label (ambiente.nivel, an assumed heuristic). */
export function ecoInfo(rot) {
  const a = rot?.ambiente
  const hit = ECO[a?.nivel]
  if (!hit) {
    return { level: null, label: 'Eco: sin evaluar', short: 'sin dato', tone: 'none', text: 'No tenemos datos para valorar el trato al medio ambiente de esta opción.' }
  }
  const m = a.metricas ?? {}
  const facts = []
  if (isNum(m.agua_m3_ha)) facts.push(`agua: ${fmtInt(m.agua_m3_ha)} m³ por hectárea y año`)
  if (isNum(m.suelo_desnudo_dias)) facts.push(`suelo sin cultivo: ${fmtInt(m.suelo_desnudo_dias)} días al año`)
  const base = typeof a.frase === 'string' && a.frase.trim()
    ? a.frase.trim()
    : `Trato al medio ambiente: ${hit[1]}. Es una etiqueta orientativa nuestra, no una certificación.`
  return { level: a.nivel, label: `Eco: ${hit[1]}`, short: hit[1], tone: hit[0], text: facts.length ? `${base} (${facts.join('; ')}).` : base }
}
