import assert from 'node:assert/strict'
import test from 'node:test'
import { homeSpinOffset, homeSpinEndMs } from './homeSpin.js'
import { HOME_SPIN } from '../config/map.js'

const { fromDeg, driftDeg } = HOME_SPIN

test('t = 0 is the start position, west of the resting one', () => {
  assert.equal(homeSpinOffset(0), -fromDeg)
})

test('t = 9 s is exactly the resting position, and it stays there', () => {
  assert.equal(homeSpinEndMs(), 9000)
  assert.equal(homeSpinOffset(9000), 0)
  for (const t of [9001, 10000, 60000, 1e9]) assert.equal(homeSpinOffset(t), 0)
})

test('never moves backwards (monotonic) and never overshoots', () => {
  let prev = homeSpinOffset(0)
  for (let t = 1; t <= 10000; t += 1) {
    const v = homeSpinOffset(t)
    assert.ok(v >= prev - 1e-12, `went back at ${t} ms`)
    assert.ok(v <= 0 && v >= -fromDeg)
    prev = v
  }
})

test('first turn covers most of the way, then the 2-7 s pause is almost still', () => {
  const turn = (fromDeg - driftDeg) / 2
  assert.ok(Math.abs(homeSpinOffset(2000) - (-fromDeg + turn)) < 1e-9)
  // During the pause the camera moves only driftDeg in total, and slowly (< 1.2 deg/s at any moment).
  assert.ok(Math.abs(homeSpinOffset(7000) - homeSpinOffset(2000) - driftDeg) < 1e-9)
  for (let t = 2000; t < 7000; t += 100) {
    const speed = (homeSpinOffset(t + 100) - homeSpinOffset(t)) / 0.1
    assert.ok(speed < 1.2, `too fast in the pause at ${t} ms: ${speed} deg/s`)
  }
})

test('the turns start and end at rest (soft joints, no jumps)', () => {
  const speed = (t) => (homeSpinOffset(t + 1) - homeSpinOffset(t)) / 0.001
  assert.ok(speed(0) < 0.01) // ease-in from rest
  assert.ok(speed(1999) < 0.01) // soft braking into the pause
  assert.ok(speed(6999) < 0.01 && speed(7000) < 0.01)
  assert.ok(speed(8999) < 0.01) // soft landing
  // continuous at the joints
  for (const t of [2000, 7000, 9000]) assert.ok(Math.abs(homeSpinOffset(t + 1e-6) - homeSpinOffset(t - 1e-6)) < 1e-6)
})

test('out-of-range values are clamped to the ends', () => {
  assert.equal(homeSpinOffset(-5), -fromDeg)
  assert.equal(homeSpinOffset(-Infinity), -fromDeg)
  assert.equal(homeSpinOffset(NaN), -fromDeg)
  assert.equal(homeSpinOffset(undefined), -fromDeg)
  assert.equal(homeSpinOffset(Infinity), 0)
})
