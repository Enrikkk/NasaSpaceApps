import { HOME_VIEW, NARROW_MAX } from '../config/map.js'

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
