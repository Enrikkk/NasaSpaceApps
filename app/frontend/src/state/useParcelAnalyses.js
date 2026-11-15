import { useEffect, useSyncExternalStore } from 'react'
import { analyze } from '../api/client.js'
import { createAnalysesStore } from './parcelAnalyses.js'
import { recintoOfParcel } from './myParcels.js'
import { useMyParcels } from './useMyParcels.js'

// One store for the whole app: the full analysis of every saved parcel, preloaded in the background.
export const analyses = createAnalysesStore(
  (p) => analyze({ lat: p.lat, lon: p.lon, recinto: recintoOfParcel(p) }),
  { concurrency: 2 },
)

/** Mounted once (App): keeps the preload in step with the saved list, from the home screen on. */
export function usePreloadMyParcels() {
  const { list } = useMyParcels()
  useEffect(() => { analyses.sync(list) }, [list])
}

/** { [ref]: { status, data } }; re-renders when any analysis arrives. */
export function useParcelAnalyses() {
  return useSyncExternalStore(analyses.subscribe, analyses.getSnapshot)
}
