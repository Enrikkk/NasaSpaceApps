import assert from 'node:assert/strict'
import test from 'node:test'
import { bestOption, successOf, quantile, buildReport } from './report.js'
import { createAnalysesStore } from './parcelAnalyses.js'

const W = { beneficio: 50, agua: 50, suelo: 50, riesgo: 50 }
const rot = (id, crit, extra = {}) => ({
  id, es_actual: false, nombre: `${id}: x`, criterios: crit,
  plan_anios: [{ ciclos: extra.ciclos ?? ['Melón piel de sapo', 'Brócoli'] }],
  ...extra,
})
const analysis = (rotaciones, ha = 2) => ({
  parcela: { ha }, escenarios_meta: { alineados: true }, idoneidad: {}, rotaciones,
})

const A = rot('s1', { margen: 1, agua: 0, suelo_n: 0, riesgo: 1 }, {
  exito_pct: { valor: 100 }, escenarios: [100, 200, -50, 300], agua_m3_ha: 8000, suelo_desnudo_dias: 100,
  semaforo_legal: { color: 'amarillo' },
})
const B = rot('s2', { margen: 0, agua: 1, suelo_n: 1, riesgo: 0 }, {
  exito_pct: { valor: 90 }, escenarios: [10, 20, 30, 40], agua_m3_ha: 3000, suelo_desnudo_dias: 40,
  ciclos: ['Brócoli', 'cubierta de veza'], semaforo_legal: { color: 'verde' },
})
const ref = { id: 'actual', es_actual: true, criterios: {}, plan_anios: [{ ciclos: ['Lechuga iceberg'] }] }

test('bestOption follows the priorities and never returns the reference', () => {
  const d = analysis([ref, A, B])
  assert.equal(bestOption(d, { beneficio: 100, agua: 0, suelo: 0, riesgo: 0 }).id, 's1')
  assert.equal(bestOption(d, { beneficio: 0, agua: 100, suelo: 0, riesgo: 0 }).id, 's2')
  assert.equal(bestOption(analysis([ref]), W), null)
  assert.equal(bestOption({ idoneidad: { no_evaluable: { motivo: 'secano' } }, rotaciones: [A] }, W), null)
  assert.equal(successOf(d, { beneficio: 100, agua: 0, suelo: 0, riesgo: 0 }), 100)
})

test('quantile interpolates', () => {
  assert.equal(quantile([0, 10], 0.5), 5)
  assert.equal(quantile([1, 2, 3], 0), 1)
  assert.equal(quantile([], 0.5), null)
})

test('buildReport adds parcels scenario by scenario and weighs by hectares', () => {
  const list = [{ ref: 'a', nombre: 'P1' }, { ref: 'b', nombre: 'P2' }, { ref: 'c', nombre: 'P3' }]
  const analyses = {
    a: { status: 'done', data: analysis([ref, A], 2) },     // farm a: [200, 400, -100, 600]
    b: { status: 'done', data: analysis([ref, B], 1) },     // farm b: [10, 20, 30, 40]
    c: { status: 'loading' },
  }
  const r = buildReport(list, analyses, W)
  assert.equal(r.total, 3)
  assert.equal(r.pending, 1)
  assert.equal(r.contadas, 2)
  assert.equal(r.haTotal, 3)
  assert.equal(r.margen.metodo, 'escenarios')
  // farm totals: [210, 420, -70, 640] -> sorted [-70, 210, 420, 640], median 315, 3 of 4 positive
  assert.equal(r.margen.p50, 315)
  assert.equal(r.margen.positivos_pct, 75)
  assert.equal(r.agua_m3, 8000 * 2 + 3000 * 1)
  assert.equal(r.suelo_desnudo_dias, (100 * 2 + 40 * 1) / 3)
  assert.equal(r.exito_medio, (100 * 2 + 90 * 1) / 3)
  assert.equal(r.semaforo, 'amarillo')
  assert.deepEqual(r.cultivos, [{ nombre: 'Brócoli', ha: 3 }, { nombre: 'Melón piel de sapo', ha: 2 }])
})

test('buildReport falls back to the sum of medians when scenarios are not aligned, and says so', () => {
  const d = analysis([{ ...A, margen_eur_ha: { p50: 1000 } }], 2)
  d.escenarios_meta.alineados = false
  const r = buildReport([{ ref: 'a' }], { a: { status: 'done', data: d } }, W)
  assert.equal(r.margen.metodo, 'suma_medianas')
  assert.equal(r.margen.p50, 2000)
  assert.equal(r.margen.positivos_pct, null)
})

test('buildReport with nothing computed yet has no figures, only counts', () => {
  const r = buildReport([{ ref: 'a' }, { ref: 'b' }], { b: { status: 'error' } }, W)
  assert.equal(r.pending, 1)
  assert.equal(r.errors, 1)
  assert.equal(r.margen, null)
  assert.equal(r.haTotal, null)
})

test('analyses store: list order, limited concurrency, seed and removal', async () => {
  const calls = []
  const resolvers = {}
  const store = createAnalysesStore((p) => { calls.push(p.ref); return new Promise((res) => { resolvers[p.ref] = res }) }, { concurrency: 2 })
  store.seed('c', { seeded: true })
  store.sync([{ ref: 'a' }, { ref: 'b' }, { ref: 'c' }, { ref: 'd' }])
  await Promise.resolve(); await Promise.resolve()
  assert.deepEqual(calls, ['a', 'b'])                       // first two, in order (c was seeded: never fetched)
  assert.equal(store.getSnapshot().d.status, 'pending')
  store.seed('d', { seeded: true })                         // d seeded while queued: never fetched either
  resolvers.a({ ok: 1 })
  await new Promise((r) => setTimeout(r, 0))
  assert.equal(store.getSnapshot().a.status, 'done')
  assert.deepEqual(calls, ['a', 'b'])
  store.sync([{ ref: 'a' }, { ref: 'd' }])                  // b and c removed: their late answers are dropped
  resolvers.b({ late: 1 })
  await new Promise((r) => setTimeout(r, 0))
  assert.equal(store.getSnapshot().b, undefined)
  assert.equal(store.getSnapshot().d.data.seeded, true)
})
