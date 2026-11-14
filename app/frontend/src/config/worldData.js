import { feature, mesh } from 'topojson-client'
import land110m from 'world-atlas/land-110m.json'

// Natural Earth 4.1 (public domain) via world-atlas (ISC). Works offline once built.

/** Coarse land (1:110m, ~55 KB), bundled so the globe is green on the very first frame. */
export const COARSE_LAND = feature(land110m, land110m.objects.land)

/** Detailed land (1:10m) and borders (1:50m), lazy chunks swapped in when ready: clean coast at region zoom. */
export async function loadWorldFine() {
  const [land, countries] = await Promise.all([
    import('world-atlas/land-10m.json'),
    import('world-atlas/countries-50m.json'),
  ])
  const l = land.default
  const c = countries.default
  return {
    land: feature(l, l.objects.land),
    borders: mesh(c, c.objects.countries, (a, b) => a !== b),
  }
}
