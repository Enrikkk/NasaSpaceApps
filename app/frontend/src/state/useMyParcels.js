import { useSyncExternalStore } from 'react'
import { createStore, STORAGE_KEY } from './myParcels.js'

// One store for the whole app, over the browser's localStorage (accessing it can throw: the store copes).
export const myParcels = createStore(() => globalThis.localStorage)

// Another tab changed the list: pick it up.
if (typeof window !== 'undefined') {
  window.addEventListener('storage', (e) => { if (e.key === null || e.key === STORAGE_KEY) myParcels.reload() })
}

/** { list, guarda, add(input) -> status, remove(ref), rename(ref, nombre) -> bool }; re-renders when the list changes. */
export function useMyParcels() {
  const snap = useSyncExternalStore(myParcels.subscribe, myParcels.getSnapshot)
  return { list: snap.list, guarda: snap.guarda, add: myParcels.add, remove: myParcels.remove, rename: myParcels.rename }
}
