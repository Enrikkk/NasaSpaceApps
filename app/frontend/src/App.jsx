import Logo from './components/Logo.jsx'
import RegionsBar from './components/RegionsBar.jsx'
import FiltersPanel from './components/FiltersPanel.jsx'
import ViewSwitcher from './components/ViewSwitcher.jsx'
import MapView from './components/MapView.jsx'
import ParcelPanel from './components/parcel/ParcelPanel.jsx'
import { useAppState } from './state/AppState.jsx'
import styles from './App.module.css'

/**
 * One real map behind everything.
 *  - home: tilted satellite globe, the big logo and two buttons (Ver el mapa, Ir a mis parcelas).
 *  - map:  zoomed into Spain; regions, filters and the view switcher appear.
 */
export default function App() {
  const { screen, setScreen, setEntry, view } = useAppState()
  const onMap = screen === 'map'
  // Both zoom in from the globe: onto the farmer's parcel, or into Campo de Cartagena.
  const goToMyParcels = () => { setEntry('parcel'); setScreen('map') }
  const seeMap = () => { setEntry('cartagena'); setScreen('map') }

  return (
    <div className={`${styles.app} ${onMap ? styles.onMap : ''}`}>
      <MapView />

      <header className={styles.brand}>
        <Logo size={onMap ? 'sm' : 'lg'} onLight={onMap && view === 'mono'} onClick={() => setScreen('home')} />
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
          </div>
          <ViewSwitcher className={styles.views} />
          <ParcelPanel />
        </>
      )}
    </div>
  )
}
