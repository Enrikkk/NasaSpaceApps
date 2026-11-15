import Panel from './ui/Panel.jsx'
import DisplayText from './DisplayText.jsx'
import { REGIONS } from '../config/map.js'
import { useAppState } from '../state/AppState.jsx'
import styles from './RegionsBar.module.css'

/** Top-right: folded to its title; hover (or tap/focus) unfolds one chip per region. */
export default function RegionsBar() {
  const { screen, setScreen, regionId, setRegionId } = useAppState()

  const pick = (id) => {
    setRegionId(id)
    if (screen !== 'map') setScreen('map')
  }

  return (
    <Panel as="nav" variant="bar" className={styles.bar} aria-label="Regiones" tabIndex={0}>
      <h2 className={`display ${styles.title}`}><DisplayText name="regiones" alt="Regiones" /></h2>
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
