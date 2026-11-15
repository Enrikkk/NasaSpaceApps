import { createContext, useContext, useMemo, useState } from 'react'
import { DEFAULT_PRIORITIES } from '../config/filters.js'

const AppStateContext = createContext(null)

/**
 * Global UI state.
 * screen:     'home' (globe) | 'map'
 * view:       base map, see VIEWS in config/map.js
 * entry:      where entering the map flies to ('cartagena' | 'parcel'); SIGPAC parcels are always shown
 * regionId:   region the map is focused on, see REGIONS in config/map.js
 * priorities: weights 0-100 the farmer sets in the filters panel
 * selectedParcel: clicked SIGPAC recinto, null or { lat, lon, recinto, tile }; opens the parcel panel
 */
export function AppStateProvider({ children }) {
  const [screen, setScreen] = useState('home')
  const [view, setView] = useState('satelite')
  const [regionId, setRegionId] = useState('espana')
  const [priorities, setPriorities] = useState(DEFAULT_PRIORITIES)
  const [crop, setCrop] = useState('todos')
  // Where the zoom from the globe lands: 'cartagena' (Ver el mapa, click, scroll) or 'parcel' (Ir a mis parcelas).
  const [entry, setEntry] = useState('cartagena')
  const [selectedParcel, setSelectedParcel] = useState(null)
  // "Tus parcelas" list: open or folded; flyTarget = { lat, lon, n } asks the map to go to one of them.
  const [myParcelsOpen, setMyParcelsOpen] = useState(false)
  const [flyTarget, setFlyTarget] = useState(null)

  const value = useMemo(() => ({
    screen, setScreen,
    view, setView,
    regionId, setRegionId,
    priorities,
    setPriority: (key, v) => setPriorities((p) => ({ ...p, [key]: v })),
    crop, setCrop,
    entry, setEntry,
    selectedParcel, setSelectedParcel,
    myParcelsOpen, setMyParcelsOpen,
    flyTarget, setFlyTarget,
  }), [screen, view, regionId, priorities, crop, entry, selectedParcel, myParcelsOpen, flyTarget])

  return <AppStateContext.Provider value={value}>{children}</AppStateContext.Provider>
}

export function useAppState() {
  const ctx = useContext(AppStateContext)
  if (!ctx) throw new Error('useAppState must be used inside <AppStateProvider>')
  return ctx
}
