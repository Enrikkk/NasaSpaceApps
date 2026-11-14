import { useEffect, useRef, useState } from 'react'
import GlyphIcon from './icons.jsx'
import EditableName from '../ui/EditableName.jsx'
import { Notice, MoreAboutParcel, Rotations, Footer } from './sections.jsx'
import { useAnalysis } from './hooks.js'
import { refFromRecinto, isNum, factsLine } from './helpers.js'
import { useAppState } from '../../state/AppState.jsx'
import { useMyParcels } from '../../state/useMyParcels.js'
import { isRegistrable, refOf, MAX_PARCELS } from '../../state/myParcels.js'
import styles from './ParcelPanel.module.css'

const SLOW_AFTER_MS = 8000

function errorText(err) {
  if (err?.timeout) return 'Está tardando demasiado.'
  if (err?.status === 422) return 'No hemos podido leer esta parcela.'
  if (err?.status >= 500) return 'El servidor ha fallado.'
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
      <span>Calculando{slow ? ' · la primera vez tarda un poco más' : ''}</span>
    </div>
  )
}

/** Save / remove this recinto in "Tus parcelas" (only in this browser; outlined and shaded in red on the map). */
function SaveButton({ parcel, saved, ha }) {
  const { guarda, add, remove } = useMyParcels()
  const [msg, setMsg] = useState('')
  if (!isRegistrable(parcel.recinto)) return null
  const ref = refOf(parcel.recinto)
  const toggle = () => {
    if (saved) { remove(ref); setMsg(''); return }
    const status = add({ recinto: parcel.recinto, lat: parcel.lat, lon: parcel.lon, ha })
    setMsg(status === 'full' ? `Máximo ${MAX_PARCELS} parcelas` : '')
  }
  return (
    <>
      <button
        type="button"
        className={`${styles.save} ${saved ? styles.saved : ''}`}
        aria-pressed={saved}
        title={saved ? 'Quitar de Tus parcelas' : 'Añadir a Tus parcelas (se guarda solo en este navegador)'}
        onClick={toggle}
      >
        <GlyphIcon name="bookmark" size={16} filled={saved} />
        {saved ? 'Guardada' : 'Guardar'}
      </button>
      {msg && <span className={styles.fine} role="status">{msg}</span>}
      {saved && !guarda && <span className={styles.fine} role="status">No se puede guardar en este navegador</span>}
    </>
  )
}

function Body({ parcel, onClose }) {
  const { priorities } = useAppState()
  const { list, rename } = useMyParcels()
  const { quick, full, error, loading, retry } = useAnalysis(parcel)
  const scrollRef = useRef(null)
  const reference = refFromRecinto(parcel.recinto)
  const data = full
  const parcela = data?.parcela ?? quick?.parcela ?? null
  const quickOk = Boolean(quick?.parcela && !quick.parcela.sin_cobertura
    && (isNum(quick.parcela.ha) || quick.parcela.referencia))
  const coverage = data?._meta?.cobertura
  const orientativo = Boolean(coverage?.nivel && coverage.nivel !== 'completo')
  const ref = isRegistrable(parcel.recinto) ? refOf(parcel.recinto) : null
  const saved = ref ? list.find((p) => p.ref === ref) : null
  const facts = factsLine(parcela, parcel)

  useEffect(() => { scrollRef.current?.scrollTo({ top: 0 }) }, [parcel])

  return (
    <aside
      className={styles.root}
      aria-label="Ficha de la parcela"
      onKeyDown={(e) => { if (e.key === 'Escape') onClose() }}
    >
      <header className={styles.top}>
        <div className={styles.titles}>
          {saved
            ? <EditableName as="h2" className={styles.ref} value={saved.nombre} onSave={(n) => rename(saved.ref, n)} />
            : <h2 className={styles.ref}>{reference || 'Sin referencia SIGPAC'}</h2>}
          <p className={styles.facts}>{[saved ? reference : null, facts].filter(Boolean).join(' · ') || ' '}</p>
        </div>
        <div className={styles.actions}>
          <SaveButton parcel={parcel} saved={Boolean(saved)} ha={isNum(parcela?.ha) ? parcela.ha : undefined} />
          <button type="button" className={styles.close} onClick={onClose} aria-label="Cerrar la ficha de la parcela">
            <GlyphIcon name="close" />
          </button>
        </div>
      </header>

      <div className={styles.scroll} ref={scrollRef}>
        <Notice parcela={parcela} parcel={parcel} />

        {loading && !error && <Loading />}

        {error && (
          <div className={styles.error} role="alert">
            <p>{errorText(error)}{quickOk ? ' Las rotaciones no se han podido calcular.' : ''}</p>
            <button type="button" className={styles.retry} onClick={retry}>
              <GlyphIcon name="retry" size={16} />Reintentar
            </button>
          </div>
        )}

        {data && (
          <>
            <Rotations key={data._meta?.consulta_id ?? 'x'} data={data} priorities={priorities} orientativo={orientativo} />
            <MoreAboutParcel data={data} />
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
