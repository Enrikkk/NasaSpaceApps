import { HOME_SPIN } from '../config/map.js'

/**
 * Timeline of the intro spin of the home globe, as a pure function of time.
 *
 * Returns the longitude offset (degrees) to ADD to the resting camera longitude: it starts at -fromDeg (west of
 * the resting position) and ends at 0 (at rest).
 *   0 - 2 s   turn east, starting from rest (ease-in) and braking softly into the pause
 *   2 - 7 s   near-still pause: only a very slow drift of `driftDeg` degrees
 *   7 - 9 s   second turn east that eases out and lands exactly on the resting position
 *   9 s on    at rest (exactly 0)
 * Every piece uses a smootherstep curve, so position and speed are continuous (no jumps, speed 0 at each joint).
 */
const smoother = (u) => u * u * u * (u * (6 * u - 15) + 10)

export const homeSpinEndMs = (cfg = HOME_SPIN) => 2 * cfg.turnMs + cfg.pauseMs

export function homeSpinOffset(ms, cfg = HOME_SPIN) {
  const { fromDeg, driftDeg, turnMs, pauseMs } = cfg
  const turnDeg = (fromDeg - driftDeg) / 2
  if (!(ms > 0)) return -fromDeg // t <= 0 and NaN: start position
  if (ms >= homeSpinEndMs(cfg)) return 0
  if (ms < turnMs) return -fromDeg + turnDeg * smoother(ms / turnMs)
  if (ms < turnMs + pauseMs) return -fromDeg + turnDeg + driftDeg * smoother((ms - turnMs) / pauseMs)
  return -turnDeg + turnDeg * smoother((ms - turnMs - pauseMs) / turnMs)
}
