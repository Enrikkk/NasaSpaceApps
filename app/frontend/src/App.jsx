import Logo from './components/Logo.jsx'
import RegionsBar from './components/RegionsBar.jsx'
import FiltersPanel from './components/FiltersPanel.jsx'
import MyParcelsPanel from './components/MyParcelsPanel.jsx'
import MapView from './components/MapView.jsx'
import ParcelPanel from './components/parcel/ParcelPanel.jsx'
import { useAppState } from './state/AppState.jsx'
import { NARROW_MAX } from './config/map.js'
import { usePreloadMyParcels } from './state/useParcelAnalyses.js'
import styles from './App.module.css'

/**
 * One real map behind everything.
 *  - home: tilted satellite globe, the big logo and two buttons (Ver el mapa, Ir a mis parcelas).
 *  - map:  zoomed into Spain; regions, filters and the view switcher appear.
 */
export default function App() {
  const { screen, setScreen, setEntry, setMyParcelsOpen } = useAppState()
  usePreloadMyParcels() // the saved parcels are analysed in the background from the first screen on
  const onMap = screen === 'map'
  // Both zoom in from the globe onto the farmer's saved parcels (MapView: Campo de Cartagena when none is saved).
  // "Ir a mis parcelas" also opens the list, but only on desktop: on a phone the list would cover the map it flew to.
  const goToMyParcels = () => { setEntry('parcel'); setMyParcelsOpen(window.innerWidth > NARROW_MAX); setScreen('map') }
  const seeMap = () => { setEntry('cartagena'); setScreen('map') }

  return (
    <div className={`${styles.app} ${onMap ? styles.onMap : ''}`}>
      <MapView />

      <header className={styles.brand}>
        <Logo size={onMap ? 'sm' : 'lg'} onClick={() => setScreen('home')} />
      </header>

      {!onMap && (
        <div className={styles.homeActions}>
          <button type="button" className={styles.seeMap} onClick={seeMap}>Ver el mapa</button>
          <button type="button" className={styles.myParcels} onClick={goToMyParcels}>Ir a mis parcelas</button>
        </div>
      )}


      {onMap && (
        <>
          <div className={styles.side}>
            <RegionsBar />
            <FiltersPanel />
            <MyParcelsPanel />
          </div>
          <ParcelPanel />
        </>
      )}
    </div>
  )
}
