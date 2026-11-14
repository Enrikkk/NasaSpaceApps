import Panel from './ui/Panel.jsx'
import { REGIONS } from '../config/map.js'
import { useAppState } from '../state/AppState.jsx'
import styles from './RegionsBar.module.css'

/** Top-right bar: title + one chip per region. Picking a region opens the map focused on it. */
export default function RegionsBar() {
  const { screen, setScreen, regionId, setRegionId } = useAppState()

  const pick = (id) => {
    setRegionId(id)
    if (screen !== 'map') setScreen('map')
  }

  return (
    <Panel as="nav" variant="bar" className={styles.bar} aria-label="Regiones">
      <h2 className={`display ${styles.title}`}>Regiones</h2>
      <ul className={styles.list}>
        {REGIONS.map((r) => {
          const active = screen === 'map' && r.id === regionId
          return (
            <li key={r.id}>
              <button
                type="button"
                className={`${styles.chip} ${active ? styles.active : ''}`}
                aria-pressed={active}
                onClick={() => pick(r.id)}
              >
                {r.label}
              </button>
            </li>
          )
        })}
      </ul>
    </Panel>
  )
}
