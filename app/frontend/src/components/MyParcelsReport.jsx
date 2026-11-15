import { useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
import ScoreRing from './ui/ScoreRing.jsx'
import { useAppState } from '../state/AppState.jsx'
import { useMyParcels } from '../state/useMyParcels.js'
import { useParcelAnalyses, analyses } from '../state/useParcelAnalyses.js'
import { buildReport } from '../state/report.js'
import { riskLevel } from './parcel/ranking.js'
import { fmtEur, fmtInt, fmtHa, isNum } from './parcel/helpers.js'
import styles from './MyParcelsReport.module.css'

const TONE = { bajo: 'good', medio: 'mid', alto: 'bad' }
const toneOf = (v) => TONE[riskLevel({ valor: v })] ?? 'good'
const LIGHT = { verde: 'Verde', amarillo: 'Amarillo', rojo: 'Rojo' }

/**
 * "Informe de tus parcelas": one result for the whole farm, from the preloaded analyses, with the priorities set in
 * Filtros. It updates live while the last parcels are still being computed.
 */
export default function MyParcelsReport({ onClose }) {
  const { priorities } = useAppState()
  const { list } = useMyParcels()
  const all = useParcelAnalyses()
  const r = buildReport(list, all, priorities)
  const closeRef = useRef(null)

  useEffect(() => {
    closeRef.current?.focus()
    const onKey = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const m = r.margen
  const ready = r.total - r.pending
  return createPortal(
    <div className={styles.backdrop} onMouseDown={(e) => { if (e.target === e.currentTarget) onClose() }}>
      <section className={styles.dialog} role="dialog" aria-modal="true" aria-labelledby="informe-title">
        <header className={styles.top}>
          <div>
            <h2 id="informe-title" className={`display ${styles.title}`}>Informe de tus parcelas</h2>
            <p className={styles.sub}>
              {r.total} {r.total === 1 ? 'parcela' : 'parcelas'}
              {isNum(r.haGuardadas) ? ` · ${fmtHa(r.haGuardadas)} ha` : ''}
              {' · con tus prioridades de Filtros'}
            </p>
          </div>
          <button ref={closeRef} type="button" className={styles.close} onClick={onClose} aria-label="Cerrar el informe">×</button>
        </header>

        {r.pending > 0 && (
          <p className={styles.progress} role="status">
            <ScoreRing status="loading" size={20} title="Calculando" showText={false} />
            Calculando {ready} de {r.total}… el informe se completa solo.
          </p>
        )}

        <div className={styles.hero}>
          <ScoreRing
            value={m?.positivos_pct ?? r.exito_medio}
            status={m?.positivos_pct != null || r.exito_medio != null ? 'done' : r.pending ? 'loading' : 'none'}
            tone={toneOf(m?.positivos_pct ?? r.exito_medio)}
            size={64}
            textClassName={styles.heroPct}
            title="Escenarios en los que el conjunto de tus parcelas gana dinero"
          />
          <div className={styles.heroText}>
            <p className={styles.big}>
              {m && isNum(m.p50) ? <>{fmtEur(m.p50)} <span>al año</span></> : 'Sin cifra todavía'}
            </p>
            <p className={styles.line}>
              {m?.metodo === 'escenarios'
                ? `Margen esperado de todas tus parcelas juntas. En 8 de cada 10 años, entre ${fmtEur(m.p10)} y ${fmtEur(m.p90)}.`
                : m ? 'Margen esperado de todas tus parcelas juntas (suma de medianas: sin escenarios alineados no damos horquilla).'
                  : 'Aún no hay ninguna parcela calculada con margen.'}
            </p>
            {isNum(m?.positivos_pct) && (
              <p className={styles.line}>
                El conjunto gana dinero en {fmtInt(m.positivos_pct)} de cada 100 escenarios simulados con años reales de clima y precios.
              </p>
            )}
          </div>
        </div>

        <dl className={styles.facts}>
          <div><dt>Superficie calculada</dt><dd>{isNum(r.haTotal) ? `${fmtHa(r.haTotal)} ha` : '—'}</dd></div>
          <div><dt>Agua de riego</dt><dd>{isNum(r.agua_m3) ? `${fmtInt(r.agua_m3)} m³/año` : '—'}</dd></div>
          <div><dt>Éxito medio</dt><dd>{isNum(r.exito_medio) ? `${fmtInt(r.exito_medio)} %` : '—'}</dd></div>
          <div><dt>Suelo sin cultivo</dt><dd>{isNum(r.suelo_desnudo_dias) ? `${fmtInt(r.suelo_desnudo_dias)} días/año` : '—'}</dd></div>
          <div><dt>Semáforo legal</dt><dd>{LIGHT[r.semaforo] ?? '—'}</dd></div>
        </dl>

        {r.cultivos.length > 0 && (
          <div className={styles.block}>
            <h3 className={styles.h}>Qué sembrar</h3>
            <ul className={styles.crops}>
              {r.cultivos.map((c) => (
                <li key={c.nombre}><b>{c.nombre}</b> {fmtHa(c.ha)} ha</li>
              ))}
            </ul>
          </div>
        )}

        <div className={styles.block}>
          <h3 className={styles.h}>Parcela a parcela</h3>
          <ul className={styles.rows}>
            {r.rows.map((row) => {
              const status = row.status === 'done' ? (row.exito != null ? 'done' : 'none') : row.status === 'error' ? 'error' : 'loading'
              return (
                <li key={row.ref} className={styles.row}>
                  <ScoreRing value={row.exito} status={status} tone={toneOf(row.exito)} size={26} textClassName={styles.rowPct}
                    title={row.exito != null ? `Éxito de la opción recomendada: ${fmtInt(row.exito)} %` : undefined} />
                  <div className={styles.rowText}>
                    <p className={styles.rowName}>{row.nombre}{isNum(row.ha) ? <span> · {fmtHa(row.ha)} ha</span> : null}</p>
                    <p className={styles.rowFine}>
                      {row.status === 'error' ? 'No se ha podido calcular. '
                        : row.noEvaluable ? `Sin recomendación: ${row.noEvaluable}`
                          : row.crops.length ? row.crops.join(' · ')
                            : row.status === 'done' ? 'Sin opción con puntuación' : 'Calculando…'}
                      {row.status === 'error' && (
                        <button type="button" className={styles.retry} onClick={() => analyses.retry(row.ref)}>Reintentar</button>
                      )}
                    </p>
                  </div>
                  <span className={styles.rowMoney}>{isNum(row.margenTotalP50) ? fmtEur(row.margenTotalP50) : ''}</span>
                </li>
              )
            })}
          </ul>
        </div>

        <p className={styles.note}>
          Cada parcela aporta la opción que sale primera con tus prioridades. El dinero se suma escenario a escenario
          (mismo año de clima, precio y coste en todas). Herramienta de apoyo, no es una garantía: consulta a tu técnico.
        </p>
      </section>
    </div>,
    document.body,
  )
}
