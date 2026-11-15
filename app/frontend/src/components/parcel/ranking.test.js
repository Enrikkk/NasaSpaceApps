import assert from 'node:assert/strict'
import test from 'node:test'
import { score100, cropsOf, coversOf, subtitleOf, riskLevel, riskInfo, ecoInfo, cropIdsOf, hasCrop } from './ranking.js'
import { priorityScore, rankRotations } from './helpers.js'

const rot = (extra = {}) => ({
  id: 's2',
  nombre: 'Suelo y agua: año 1: Brócoli, cubierta de veza → año 2: Melón piel de sapo',
  plan_anios: [
    { anio_plan: 1, ciclos: ['Brócoli', 'cubierta de veza'] },
    { anio_plan: 2, ciclos: ['Melón piel de sapo', 'barbecho'] },
    { anio_plan: 3, ciclos: ['Brócoli', 'cubierta de veza'] },
  ],
  ...extra,
})

test('score is a whole number from 1 to 100 and null when there is no criterion', () => {
  assert.equal(score100(0.732), 73)
  assert.equal(score100(0), 1)
  assert.equal(score100(1), 100)
  assert.equal(score100(1.4), 100)
  assert.equal(score100(null), null)
  assert.equal(score100(undefined), null)
})

test('crops are unique, in order, without fallow or cover crops; covers are listed apart', () => {
  assert.deepEqual(cropsOf(rot()), ['Brócoli', 'Melón piel de sapo'])
  assert.deepEqual(coversOf(rot()), ['cubierta de veza'])
  assert.deepEqual(cropsOf({}), [])
  assert.deepEqual(cropsOf({ plan_anios: [{ ciclos: [null, 5, 'barbecho'] }] }), [])
  assert.equal(subtitleOf(rot()), 'Suelo y agua · con cubierta de veza')
})

test('risk label comes from the % of good years with assumed cut-offs', () => {
  assert.equal(riskLevel({ valor: 100 }), 'bajo')
  assert.equal(riskLevel({ valor: 90 }), 'bajo')
  assert.equal(riskLevel({ valor: 89.9 }), 'medio')
  assert.equal(riskLevel({ valor: 75 }), 'medio')
  assert.equal(riskLevel({ valor: 74 }), 'alto')
  assert.equal(riskLevel({ valor: null }), null)
  assert.equal(riskLevel(undefined), null)
})

test('risk text says the number, the range, the worst year, and that the cut-offs are assumed', () => {
  const r = riskInfo({ exito_pct: { valor: 94.4, horquilla: [74.2, 99], peores_anios: [{ anio: 2010, margen_eur_ha: -2322 }] } })
  assert.equal(r.label, 'Riesgo: bajo')
  assert.equal(r.tone, 'good')
  assert.match(r.text, /94 de cada 100 años/)
  assert.match(r.text, /entre 74 y 99/)
  assert.match(r.text, /una pérdida de 2\.322 € por hectárea/)
  assert.match(r.text, /supuestos nuestros/)
  assert.match(r.text, /no es una garantía/)
})

test('risk without data never invents a level', () => {
  const r = riskInfo({ exito_pct: { valor: null } })
  assert.equal(r.level, null)
  assert.equal(r.label, 'Riesgo: sin evaluar')
  assert.equal(r.tone, 'none')
  assert.equal(riskInfo({}).label, 'Riesgo: sin evaluar')
})

test('eco label uses the engine label and its sentence, plus water and bare-soil days', () => {
  const e = ecoInfo({ ambiente: { nivel: 'medio', frase: 'Trato al medio ambiente: medio.', metricas: { agua_m3_ha: 3352, suelo_desnudo_dias: 132 } } })
  assert.equal(e.label, 'Eco: medio')
  assert.equal(e.tone, 'mid')
  assert.match(e.text, /Trato al medio ambiente: medio/)
  assert.match(e.text, /3\.352 m³/)
  assert.match(e.text, /132 días/)
  assert.equal(ecoInfo({}).label, 'Eco: sin evaluar')
  assert.equal(ecoInfo({ ambiente: { nivel: 'raro' } }).level, null)
})

test('ranking: best score first, the reference rotation always last and without a rank', () => {
  const list = [
    { id: 'actual', es_actual: true, criterios: { margen: null, agua: 0.176, suelo_n: 0, riesgo: null } },
    { id: 's1', criterios: { margen: 1, agua: 0, suelo_n: 0.066, riesgo: 1 } },
    { id: 's2', criterios: { margen: 0, agua: 1, suelo_n: 0.814, riesgo: 0 } },
    { id: 's3', criterios: { margen: 0.975, agua: 0, suelo_n: 1, riesgo: 0.954 } },
  ]
  const p = { beneficio: 50, agua: 50, suelo: 50, riesgo: 50 }
  const ranked = rankRotations(list, p)
  assert.deepEqual(ranked.map((x) => x.rot.id), ['s3', 's1', 's2', 'actual'])
  assert.deepEqual(ranked.map((x) => x.rank), [1, 2, 3, null])
  assert.deepEqual(ranked.slice(0, 3).map((x) => score100(x.score)), [73, 52, 45])
  assert.equal(ranked[3].score, null)
  assert.equal(ranked[0].best, true)
  assert.equal(priorityScore(list[0].criterios, p) !== null, true)
})

// Crop filter: same shape as the API (plan_anios[].ciclos + ciclos_detalle[].cultivo).
const withDetail = {
  id: 's3',
  plan_anios: [{
    ciclos: ['Melón piel de sapo', 'Brócoli', 'cubierta de veza'],
    ciclos_detalle: [
      { producto: 'Melón piel de sapo', cultivo: 'melon' },
      { producto: 'Brócoli', cultivo: 'brocoli' },
      { producto: 'cubierta de veza', cultivo: 'veza' },
    ],
  }],
}
const namesOnly = { id: 'x', plan_anios: [{ ciclos: ['Lechuga iceberg', 'barbecho', 'Alcachofa'] }] }

test('cropIdsOf reads the engine crop ids and leaves cover crops out', () => {
  assert.deepEqual(cropIdsOf(withDetail), ['melon', 'brocoli'])
})

test('cropIdsOf falls back to the names when there is no ciclos_detalle', () => {
  assert.deepEqual(cropIdsOf(namesOnly), ['lechuga', 'alcachofa'])
  assert.deepEqual(cropIdsOf({}), [])
})

test('hasCrop: todos lets everything through; a crop only the options that grow it', () => {
  assert.equal(hasCrop(withDetail, 'todos'), true)
  assert.equal(hasCrop(withDetail, undefined), true)
  assert.equal(hasCrop(withDetail, 'melon'), true)
  assert.equal(hasCrop(withDetail, 'lechuga'), false)
  assert.equal(hasCrop(withDetail, 'veza'), false)
})
