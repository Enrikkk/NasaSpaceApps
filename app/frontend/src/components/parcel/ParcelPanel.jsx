import { useEffect, useRef, useState } from 'react'
import GlyphIcon from './icons.jsx'
import { Summary, YourParcel, Influence, Rotations, Footer } from './sections.jsx'
import { useAnalysis } from './hooks.js'
import { refFromRecinto } from './helpers.js'
import { useAppState } from '../../state/AppState.jsx'
import styles from './ParcelPanel.module.css'

const SLOW_AFTER_MS = 8000

function errorText(err) {
  if (err?.timeout) return 'El cálculo está tardando demasiado.'
  if (err?.status === 422) return 'No hemos podido leer esta parcela.'
  if (err?.status >= 500) return 'El servidor ha tenido un problema al calcular esta parcela.'
  return 'No hemos podido conectar con el servidor.'
}

function Loading() {
  const [slow, setSlow] = useState(false)
  useEffect(() => {
    const t = setTimeout(() => setSlow(true), SLOW_AFTER_MS)
    return () => clearTimeout(t)
  }, [])
  return (
    <div className={styles.loading} role="status">
      <span className={styles.spinner} aria-hidden="true" />
      <div>
        <p>Calculando las rotaciones para esta parcela…</p>
        {slow && <p className={styles.fine}>Si es la primera vez que miramos esta zona puede tardar hasta un minuto.</p>}
      </div>
    </div>
  )
}

function Body({ parcel, onClose }) {
  const { priorities } = useAppState()
  const { quick, full, error, loading, retry } = useAnalysis(parcel)
  const scrollRef = useRef(null)
  const reference = refFromRecinto(parcel.recinto)
  const data = full
  const parcela = data?.parcela ?? quick?.parcela ?? null
  const coverage = data?._meta?.cobertura

  useEffect(() => { scrollRef.current?.scrollTo({ top: 0 }) }, [parcel])

  return (
    <aside
      className={styles.root}
      aria-label="Ficha de la parcela"
      onKeyDown={(e) => { if (e.key === 'Escape') onClose() }}
    >
      <header className={styles.top}>
        <div className={styles.titles}>
          <p className={styles.eyebrow}>Recinto SIGPAC</p>
          <h2 className={styles.ref}>{reference || 'Sin referencia SIGPAC'}</h2>
        </div>
        <button type="button" className={styles.close} onClick={onClose} aria-label="Cerrar la ficha de la parcela">
          <GlyphIcon name="close" />
        </button>
      </header>

      <div className={styles.scroll} ref={scrollRef}>
        <Summary parcela={parcela} loading={loading && !error} />

        {loading && !error && <Loading />}

        {error && (
          <div className={styles.error} role="alert">
            <p>{errorText(error)} Los datos de la parcela de arriba sí los tenemos; las rotaciones no.</p>
            <button type="button" className={styles.retry} onClick={retry}>
              <GlyphIcon name="retry" size={16} />Reintentar
            </button>
          </div>
        )}

        {data && coverage && coverage.nivel && coverage.nivel !== 'completo' && (
          <p className={styles.coverage}>
            <b>Resultado orientativo.</b> {coverage.ambito || 'Cobertura básica: sin datos de parcela SIGPAC.'}
          </p>
        )}

        {data && (
          <>
            <YourParcel data={data} />
            <Influence data={data} />
            <Rotations key={data._meta?.consulta_id ?? 'x'} data={data} priorities={priorities} />
          </>
        )}

        <Footer data={data} />
      </div>
    </aside>
  )
}

/**
 * Parcel sheet: opens when a recinto is clicked on the map (AppState.selectedParcel). Mounted only on the map
 * screen; leaving the map unmounts it and clears the selection.
 */
export default function ParcelPanel() {
  const { selectedParcel, setSelectedParcel } = useAppState()
  useEffect(() => () => setSelectedParcel(null), [setSelectedParcel])
  if (!selectedParcel) return null
  return <Body parcel={selectedParcel} onClose={() => setSelectedParcel(null)} />
}
