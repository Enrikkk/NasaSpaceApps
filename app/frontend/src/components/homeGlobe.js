import { HOME_VIEW, NARROW_MAX } from '../config/map.js'
import { homeSpinOffset, homeSpinEndMs } from './homeSpin.js'

/**
 * Home view: a close, tilted look at the planet that fills the page. The horizon runs diagonally from the top-left
 * to the bottom-right and Spain sits in the lower-left. Built from a fixed camera tilt (pitch, bearing, roll), a zoom
 * scaled to the screen, and a correction that puts Spain exactly at its target point.
 */
export function homeTarget(w = window.innerWidth, h = window.innerHeight) {
  const t = w <= NARROW_MAX ? HOME_VIEW.targetNarrow : HOME_VIEW.target
  return [t[0] * w, t[1] * h]
}

/** Camera guess for the current screen; refineHome() then moves Spain onto its target. */
export function homeCamera(w = window.innerWidth, h = window.innerHeight) {
  const scale = Math.sqrt((w * h) / (HOME_VIEW.refSize[0] * HOME_VIEW.refSize[1]))
  return {
    center: HOME_VIEW.center,
    zoom: HOME_VIEW.zoom + Math.max(-1.2, Math.log2(scale)),
    pitch: HOME_VIEW.pitch,
    bearing: HOME_VIEW.bearing,
    roll: HOME_VIEW.roll,
    padding: { top: 0, bottom: 0, left: 0, right: 0 },
  }
}

/** Slide the camera centre until Spain lands on its target point (a few pixel-sized jumps). */
export function refineHome(map, iterations = 4) {
  const [tx, ty] = homeTarget()
  for (let i = 0; i < iterations; i++) {
    const pc = map.project(map.getCenter())
    const pf = map.project(HOME_VIEW.focus)
    const next = map.unproject([pc.x - (tx - pf.x), pc.y - (ty - pf.y)])
    map.jumpTo({ center: next })
  }
}

// Intro spin state: it plays once per page load (module state also survives the dev double-mount).
const intro = { start: null, done: false }
const USER_EVENTS = ['pointerdown', 'wheel', 'keydown']

/**
 * Intro animation of the home globe (timeline in homeSpin.js): the camera turns east to the resting position,
 * driven by the clock (performance.now), not by frame counts. Any pointer, wheel or key press cancels it at once and
 * the globe settles on the resting position (unless the press opens the map, whose flight starts from where it is).
 * getFinal() gives the resting centre, isHome() whether the home screen is still showing. Returns dispose().
 */
export function playHomeIntro(map, getFinal, isHome) {
  const noMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  if (intro.done || noMotion) { intro.done = true; return () => {} }
  intro.start ??= performance.now()
  let raf = 0
  const dispose = () => {
    cancelAnimationFrame(raf)
    for (const ev of USER_EVENTS) window.removeEventListener(ev, onUser, true)
  }
  const finish = () => { dispose(); intro.done = true }
  const onUser = () => {
    finish()
    if (!isHome()) return
    map.easeTo({ center: getFinal(), duration: 700, essential: true })
    map.once('moveend', () => { if (isHome()) refineHome(map) })
  }
  const tick = () => {
    if (!isHome()) return finish()
    const t = performance.now() - intro.start
    const { lng, lat } = getFinal()
    map.jumpTo({ center: [lng + homeSpinOffset(t), lat] })
    if (t >= homeSpinEndMs()) { refineHome(map); return finish() } // same last correction as the resting globe gets
    raf = requestAnimationFrame(tick)
  }
  for (const ev of USER_EVENTS) window.addEventListener(ev, onUser, true)
  tick() // first frame now: no flash of the resting position before the globe jumps west
  return dispose
}
