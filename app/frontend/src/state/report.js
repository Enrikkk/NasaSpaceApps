// "Informe de tus parcelas": one result for all the saved parcels. Pure functions over the analyses (parcelAnalyses.js).
// Each parcel contributes its recommended option (the best one with the farmer's priorities, same ranking as the card).
// Money is added scenario by scenario: the engine's 200 scenarios are aligned (index i = same climate year, price and
// cost in every rotation), so farm[i] = sum of escenarios[i] x ha is the whole farm in that scenario. Never invented:
// if a parcel lacks a figure it is left out of that figure and the report says how many were counted.
import { isNum, rankRotations } from '../components/parcel/helpers.js'
import { cropsOf } from '../components/parcel/ranking.js'

/** The option the card ranks first with these priorities (null if the parcel has none with a score). */
export function bestOption(data, priorities) {
  if (!data || data.idoneidad?.no_evaluable) return null
  const top = rankRotations(data.rotaciones, priorities).find((x) => !x.rot.es_actual && x.score !== null)
  return top ? top.rot : null
}

/** Success % of the recommended option (the number in each parcel's ring), or null. */
export function successOf(data, priorities) {
  const v = bestOption(data, priorities)?.exito_pct?.valor
  return isNum(v) ? v : null
}

/** Linear-interpolated quantile of an already sorted array (q in 0..1). */
export function quantile(sorted, q) {
  if (!sorted.length) return null
  const pos = (sorted.length - 1) * q
  const lo = Math.floor(pos)
  const hi = Math.ceil(pos)
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo)
}

const LIGHT_ORDER = { verde: 0, amarillo: 1, rojo: 2 }

/**
 * list: saved parcels (myParcels), analyses: { [ref]: { status, data } }, priorities: filter weights.
 * Returns everything the report shows; figures are null when nothing could be counted.
 */
export function buildReport(list, analyses, priorities) {
  const rows = list.map((p) => {
    const entry = analyses?.[p.ref] ?? { status: 'pending' }
    const data = entry.status === 'done' ? entry.data : null
    const best = bestOption(data, priorities)
    const haApi = data?.parcela?.ha
    const ha = isNum(haApi) && haApi > 0 ? haApi : (isNum(p.ha) && p.ha > 0 ? p.ha : null)
    const margen = best?.margen_eur_ha?.p50
    return {
      ref: p.ref,
      nombre: p.nombre,
      status: entry.status,
      ha,
      best,
      crops: best ? cropsOf(best) : [],
      exito: isNum(best?.exito_pct?.valor) ? best.exito_pct.valor : null,
      margenTotalP50: isNum(margen) && ha ? margen * ha : null,
      noEvaluable: data?.idoneidad?.no_evaluable?.motivo ?? null,
      alineados: data?.escenarios_meta?.alineados === true,
    }
  })

  const done = rows.filter((r) => r.status === 'done')
  const pending = rows.filter((r) => r.status === 'pending' || r.status === 'loading').length
  const errors = rows.filter((r) => r.status === 'error')
  const counted = done.filter((r) => r.best && r.ha)

  const haTotal = counted.reduce((s, r) => s + r.ha, 0)
  const haSaved = rows.reduce((s, r) => s + (r.ha ?? 0), 0)

  // Money: scenario by scenario when every counted parcel has aligned scenarios of the same length.
  const withMoney = counted.filter((r) => Array.isArray(r.best.escenarios) && r.best.escenarios.length && r.best.escenarios.every(isNum))
  const n = withMoney[0]?.best.escenarios.length ?? 0
  const scenarioWise = withMoney.length > 0 && withMoney.every((r) => r.alineados && r.best.escenarios.length === n)
  let margen = null
  if (scenarioWise) {
    const farm = Array.from({ length: n }, (_, i) => withMoney.reduce((s, r) => s + r.best.escenarios[i] * r.ha, 0))
    const sorted = [...farm].sort((a, b) => a - b)
    margen = {
      p10: quantile(sorted, 0.1),
      p50: quantile(sorted, 0.5),
      p90: quantile(sorted, 0.9),
      positivos_pct: (farm.filter((v) => v > 0).length / n) * 100,
      n_escenarios: n,
      parcelas: withMoney.length,
      metodo: 'escenarios',
    }
  } else {
    const withP50 = counted.filter((r) => isNum(r.margenTotalP50))
    if (withP50.length) {
      margen = {
        p10: null, p50: withP50.reduce((s, r) => s + r.margenTotalP50, 0), p90: null,
        positivos_pct: null, n_escenarios: 0, parcelas: withP50.length, metodo: 'suma_medianas',
      }
    }
  }

  const sumOver = (get) => {
    const vals = counted.map((r) => ({ v: get(r.best), ha: r.ha })).filter((x) => isNum(x.v))
    return vals.length ? { total: vals.reduce((s, x) => s + x.v * x.ha, 0), ha: vals.reduce((s, x) => s + x.ha, 0), n: vals.length } : null
  }
  const agua = sumOver((b) => b.agua_m3_ha)
  const desnudo = sumOver((b) => b.suelo_desnudo_dias)
  const exito = sumOver((b) => b.exito_pct?.valor)

  // Hectares per crop in the recommended options (a parcel with two crops counts its hectares for both).
  const cropHa = new Map()
  for (const r of counted) for (const c of r.crops) cropHa.set(c, (cropHa.get(c) ?? 0) + r.ha)
  const cultivos = [...cropHa.entries()].map(([nombre, ha]) => ({ nombre, ha })).sort((a, b) => b.ha - a.ha)

  // Legal light: the worst one among the recommended options.
  let semaforo = null
  for (const r of counted) {
    const color = r.best.semaforo_legal?.color
    if (color in LIGHT_ORDER && (!semaforo || LIGHT_ORDER[color] > LIGHT_ORDER[semaforo])) semaforo = color
  }

  return {
    rows,
    total: rows.length,
    pending,
    errors: errors.length,
    noEvaluables: done.filter((r) => r.noEvaluable).length,
    contadas: counted.length,
    haTotal: counted.length ? haTotal : null,
    haGuardadas: haSaved || null,
    margen,
    agua_m3: agua ? agua.total : null,
    suelo_desnudo_dias: desnudo ? desnudo.total / desnudo.ha : null,
    exito_medio: exito ? exito.total / exito.ha : null,
    cultivos,
    semaforo,
  }
}
