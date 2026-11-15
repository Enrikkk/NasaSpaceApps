import assert from 'node:assert/strict'
import test from 'node:test'
import {
  STORAGE_KEY, MAX_PARCELS, MAX_NAME, NO_MATCH, cleanName, defaultName, renameIn, refOf, isRegistrable, makeParcel, parseStored, addTo, removeFrom, mapFilter, boundsOf, createStore,
} from './myParcels.js'

const R = { provincia: 30, municipio: 37, agregado: 0, zona: 0, poligono: 18, parcela: 426, recinto: 1 }
const input = (over = {}) => ({ recinto: R, lat: 37.7383, lon: -0.98838, ha: 4.09, ...over })
const fakeStorage = (init = {}) => {
  const data = { ...init }
  return { data, getItem: (k) => (k in data ? data[k] : null), setItem: (k, v) => { data[k] = String(v) } }
}

test('reference follows the SIGPAC order and skips missing parts', () => {
  assert.equal(refOf(R), '30/37/0/0/18/426/1')
  assert.equal(refOf({ poligono: 18, parcela: 4, recinto: 2 }), '18/4/2')
})

test('only recintos SIGPAC identifies can be saved', () => {
  assert.equal(isRegistrable(R), true)
  assert.equal(isRegistrable({ poligono: 18, parcela: 4 }), false)
  assert.equal(isRegistrable({}), false)
  assert.equal(makeParcel(input({ recinto: {} })), null)
  assert.equal(makeParcel(input({ lat: undefined })), null)
})

test('the stored record has the reference, its parts, the place, the size and a date, nothing personal', () => {
  const p = makeParcel(input(), new Date('2026-11-14T10:00:00Z'))
  assert.deepEqual(Object.keys(p).sort(), ['agregado', 'fecha', 'ha', 'lat', 'lon', 'municipio', 'parcela', 'poligono', 'provincia', 'recinto', 'ref', 'zona'].sort())
  assert.equal(p.fecha, '2026-11-14')
  assert.equal('ha' in makeParcel(input({ ha: null })), false)
})

test('add, duplicate and remove', () => {
  const p = makeParcel(input())
  let r = addTo([], p)
  assert.equal(r.status, 'added')
  assert.equal(addTo(r.list, p).status, 'duplicate')
  assert.equal(addTo(r.list, null).status, 'invalid')
  assert.deepEqual(removeFrom(r.list, p.ref), [])
})

test('the list has a cap', () => {
  let list = []
  for (let i = 0; i < MAX_PARCELS; i++) list = addTo(list, makeParcel(input({ recinto: { ...R, recinto: i } }))).list
  assert.equal(list.length, MAX_PARCELS)
  assert.equal(addTo(list, makeParcel(input({ recinto: { ...R, recinto: 999 } }))).status, 'full')
})

test('corrupt or hand-edited storage never throws and keeps what is valid', () => {
  assert.deepEqual(parseStored(null), [])
  assert.deepEqual(parseStored('{no json'), [])
  assert.deepEqual(parseStored('{"a":1}'), [])
  const good = makeParcel(input())
  const raw = JSON.stringify([good, good, { ref: 'x' }, null, 5, { ...good, poligono: 'a' }, { ...good, recinto: 2, ref: 'zz' }])
  const out = parseStored(raw)
  assert.deepEqual(out.map((p) => p.ref), ['30/37/0/0/18/426/1', '30/37/0/0/18/426/2'])
})

test('map filter matches nothing when empty and one clause per saved recinto otherwise', () => {
  assert.deepEqual(mapFilter([]), NO_MATCH)
  const f = mapFilter([makeParcel(input()), makeParcel(input({ recinto: { ...R, recinto: 2 } }))])
  assert.equal(f[0], 'any')
  assert.equal(f.length, 3)
  assert.equal(f[1][0], 'all')
  assert.equal(f[1].length, 1 + 7)
  assert.deepEqual(f[1][1], ['==', ['to-number', ['get', 'provincia'], -1], 30])
})

test('bounds wrap the saved parcels', () => {
  assert.equal(boundsOf([]), null)
  const a = makeParcel(input())
  const b = makeParcel(input({ recinto: { ...R, recinto: 2 }, lat: 37.8, lon: -1.0 }))
  assert.deepEqual(boundsOf([a, b]), [[-1.0, 37.7383], [-0.98838, 37.8]])
})

test('store: saves to storage, notifies, reloads, survives a storage that throws', () => {
  const st = fakeStorage()
  const store = createStore(() => st)
  let calls = 0
  store.subscribe(() => { calls += 1 })
  assert.equal(store.add(input()), 'added')
  assert.equal(store.add(input()), 'duplicate')
  assert.equal(calls, 1)
  assert.equal(JSON.parse(st.data[STORAGE_KEY]).length, 1)
  assert.equal(createStore(() => st).getSnapshot().list.length, 1)         // survives a "reload"
  store.remove('30/37/0/0/18/426/1')
  assert.equal(store.getSnapshot().list.length, 0)
  st.data[STORAGE_KEY] = JSON.stringify([makeParcel(input())])              // another tab wrote
  store.reload()
  assert.equal(store.getSnapshot().list.length, 1)

  const blocked = createStore(() => { throw new Error('blocked') })
  assert.equal(blocked.getSnapshot().guarda, false)
  assert.equal(blocked.add(input()), 'added')                               // works in memory
  assert.equal(blocked.getSnapshot().list.length, 1)
  assert.equal(blocked.getSnapshot().guarda, false)                         // and says it is not saved
})

test('names: cleaned, capped, default "Parcela N" reuses the smallest free number', () => {
  assert.equal(cleanName('  Huerta   del  abuelo '), 'Huerta del abuelo')
  assert.equal(cleanName('   '), null)
  assert.equal(cleanName(5), null)
  assert.equal(cleanName('x'.repeat(100)).length, MAX_NAME)
  assert.equal(defaultName([]), 'Parcela 1')
  assert.equal(defaultName([{ nombre: 'Parcela 1' }, { nombre: 'Parcela 3' }]), 'Parcela 2')
})

test('store gives each new parcel a default name, can rename it, and keeps it after a reload', () => {
  const st = fakeStorage()
  const store = createStore(() => st)
  store.add(input())
  store.add(input({ recinto: { ...R, recinto: 2 } }))
  assert.deepEqual(store.getSnapshot().list.map((p) => p.nombre), ['Parcela 1', 'Parcela 2'])
  assert.equal(store.rename('30/37/0/0/18/426/1', '  La huerta  '), true)
  assert.equal(store.rename('30/37/0/0/18/426/1', '   '), false)       // empty: unchanged
  assert.equal(store.rename('no/existe', 'X'), false)
  assert.equal(createStore(() => st).getSnapshot().list[0].nombre, 'La huerta')
  store.remove('30/37/0/0/18/426/2')
  store.add(input({ recinto: { ...R, recinto: 3 } }))
  assert.equal(store.getSnapshot().list[1].nombre, 'Parcela 1')        // the first one was renamed, so "Parcela 1" is free again
})

test('parcels saved before names existed get one when read', () => {
  const old = JSON.stringify([makeParcel(input()), makeParcel(input({ recinto: { ...R, recinto: 2 } }))])
  assert.deepEqual(parseStored(old).map((p) => p.nombre), ['Parcela 1', 'Parcela 2'])
  assert.equal(renameIn([{ ref: 'a', nombre: 'x' }], 'a', 'y')[0].nombre, 'y')
})
