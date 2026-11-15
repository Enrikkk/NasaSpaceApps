import { useId } from 'react'
import Panel from './ui/Panel.jsx'
import EditableName from './ui/EditableName.jsx'
import { useAppState } from '../state/AppState.jsx'
import { useMyParcels } from '../state/useMyParcels.js'
import { RECINTO_KEYS } from '../state/myParcels.js'
import { fmtHa } from './parcel/helpers.js'
import styles from './MyParcelsPanel.module.css'

const recintoOf = (p) => Object.fromEntries(RECINTO_KEYS.filter((k) => Number.isInteger(p[k])).map((k) => [k, p[k]]))

/**
 * "Tus parcelas": the recintos the farmer saved (button in the parcel sheet). They are outlined in red on the map.
 * Everything lives in this browser only; the panel says so.
 */
export default function MyParcelsPanel() {
  const { myParcelsOpen, setMyParcelsOpen, setSelectedParcel, setFlyTarget } = useAppState()
  const { list, guarda, remove, rename } = useMyParcels()
  const bodyId = useId()
  const go = (p) => {
    setSelectedParcel({ lat: p.lat, lon: p.lon, recinto: recintoOf(p) })
    setFlyTarget({ lat: p.lat, lon: p.lon, n: Date.now() })
  }
  return (
    <Panel as="aside" className={`${styles.panel} ${myParcelsOpen ? styles.open : ''}`} aria-label="Tus parcelas">
      <h2 className={styles.heading}>
        <button
          type="button"
          className={`display ${styles.title}`}
          aria-expanded={myParcelsOpen}
          aria-controls={bodyId}
          onClick={() => setMyParcelsOpen(!myParcelsOpen)}
        >
          <span>Tus parcelas{list.length > 0 && <span className={styles.count}>{list.length}</span>}</span>
          <span className={styles.chevron} aria-hidden="true">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2"
              strokeLinecap="round" strokeLinejoin="round"><path d="M5 8l5 5 5-5" /></svg>
          </span>
        </button>
      </h2>
      <div id={bodyId} className={styles.body}>
        {list.length === 0 ? (
          <p className={styles.empty}>Aún no hay parcelas. Haz clic en un recinto y pulsa Guardar.</p>
        ) : (
          <ul className={styles.list}>
            {list.map((p) => (
              <li key={p.ref} className={styles.item}>
                <div className={styles.who}>
                  <span className={styles.swatch} aria-hidden="true" />
                  <div className={styles.names}>
                    <EditableName value={p.nombre} onSave={(n) => rename(p.ref, n)} className={styles.pname} />
                    <p className={styles.fine}>{[p.ref, p.ha ? `${fmtHa(p.ha)} ha` : null].filter(Boolean).join(' · ')}</p>
                  </div>
                </div>
                <div className={styles.actions}>
                  <button type="button" className={styles.see} onClick={() => go(p)} aria-label={`Ver ${p.nombre}`}>Ver</button>
                  <button type="button" className={styles.del} onClick={() => remove(p.ref)} aria-label={`Quitar ${p.nombre}`}>Quitar</button>
                </div>
              </li>
            ))}
          </ul>
        )}
        <p className={styles.fine}>
          {guarda
            ? 'Se guardan solo en este navegador.'
            : 'Tu navegador no deja guardar: se perderán al recargar.'}
        </p>
      </div>
    </Panel>
  )
}
