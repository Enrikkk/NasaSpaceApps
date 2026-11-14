import assert from 'node:assert/strict'
import test from 'node:test'
import { haFromSquareMetres } from './helpers.js'

test('SIGPAC square metres become hectares, including small parcels', () => {
  assert.equal(haFromSquareMetres(500), '0,05 ha')
  assert.equal(haFromSquareMetres(1000), '0,10 ha')
  assert.equal(haFromSquareMetres(40900), '4,09 ha')
  assert.equal(haFromSquareMetres(undefined), null)
  assert.equal(haFromSquareMetres('no'), null)
})
