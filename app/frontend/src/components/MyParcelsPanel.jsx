import { useCallback, useId, useState } from 'react'
import Panel from './ui/Panel.jsx'
import DisplayText from './DisplayText.jsx'
import EditableName from './ui/EditableName.jsx'
import ScoreRing from './ui/ScoreRing.jsx'
import MyParcelsReport from './MyParcelsReport.jsx'
import { useAppState } from '../state/AppState.jsx'
import { useMyParcels } from '../state/useMyParcels.js'
import { useParcelAnalyses } from '../state/useParcelAnalyses.js'
import { recintoOfParcel } from '../state/myParcels.js'
import { successOf } from '../state/report.js'
import { riskLevel } from './parcel/ranking.js'
import { fmtHa, fmtInt } from './parcel/helpers.js'
import styles from './MyParcelsPanel.module.css'

const TONE = { bajo: 'good', medio: 'mid', alto: 'bad' }

/** Ring of one saved parcel: spinning while its analysis is preloaded, then the success % of its recommended option. */
function ParcelRing({ entry, priorities }) {
  if (!entry || entry.status === 'pending' || entry.status === 'loading') {
    return <ScoreRing status="loading" title="Calculando esta parcela…" />
  }
  if (entry.status === 'error') return <ScoreRing status="error" title="No se ha podido calcular esta parcela" />
  const v = successOf(entry.data, priorities)
  if (v === null) return <ScoreRing status="none" title="Sin recomendación con porcentaje para esta parcela" />
  return (
    <ScoreRing value={v} tone={TONE[riskLevel({ valor: v })] ?? 'good'}
      title={`La opción recomendada sale bien en ${fmtInt(v)} de cada 100 años simulados`} />
  )
}

/**
 * "Tus parcelas": the recintos the farmer saved (button in the parcel sheet), outlined in red on the map. Each one is
 * analysed in the background (preload), shows a ring with its result, and the report joins them all into one result.
 */
export default function MyParcelsPanel() {
  const { myParcelsOpen, setMyParcelsOpen, setSelectedParcel, setFlyTarget, priorities } = useAppState()
  const { list, guarda, remove, rename } = useMyParcels()
  const all = useParcelAnalyses()
  const [report, setReport] = useState(false)
  const closeReport = useCallback(() => setReport(false), [])
  const bodyId = useId()
  const go = (p) => {
    setSelectedParcel({ lat: p.lat, lon: p.lon, recinto: recintoOfParcel(p) })
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
          <span><DisplayText name="tus-parcelas" alt="Tus parcelas" />{list.length > 0 && <span className={styles.count}>{list.length}</span>}</span>
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
                  <ParcelRing entry={all[p.ref]} priorities={priorities} />
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
        {list.length > 0 && (
          <button type="button" className={styles.report} onClick={() => setReport(true)}>
            Informe de todas tus parcelas
          </button>
        )}
        {!guarda && <p className={styles.fine}>Tu navegador no deja guardar: se perderán al recargar.</p>}
      </div>
      {report && <MyParcelsReport onClose={closeReport} />}
    </Panel>
  )
}
