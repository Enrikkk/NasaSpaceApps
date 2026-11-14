import { useCallback, useEffect, useRef, useState } from 'react'
import { analyze, narrativa, isAbort } from '../../api/client.js'

/**
 * Loads a parcel in two steps, in parallel: the instant parcel block (header) and the full analysis.
 * A new parcel (or retry) aborts the previous requests; their answers are ignored.
 */
export function useAnalysis(parcel) {
  const [attempt, setAttempt] = useState(0)
  const [res, setRes] = useState({ parcel: null, attempt: 0, quick: null, full: null, error: null })

  useEffect(() => {
    if (!parcel) return undefined
    const ac = new AbortController()
    let retryTimer = null
    const mine = (patch) => { if (!ac.signal.aborted) setRes((r) => ({ ...r, ...patch })) }
    setRes({ parcel, attempt, quick: null, full: null, error: null })
    analyze(parcel, { bloques: 'parcela', signal: ac.signal })
      .then((d) => {
        mine({ quick: d })
        // The server may still be loading the SIGPAC recintos (first request after a cold start): ask once more shortly.
        const p = d?.parcela
        if (attempt === 0 && p?.sin_cobertura && p._status === 'cargando' && parcel?.recinto && Object.keys(parcel.recinto).length) {
          retryTimer = setTimeout(() => { if (!ac.signal.aborted) setAttempt((n) => n + 1) }, 4000)
        }
      })
      .catch(() => { /* the header is optional: the full call reports real errors */ })
    analyze(parcel, { signal: ac.signal })
      .then((d) => mine({ full: d }))
      .catch((err) => { if (!isAbort(err)) mine({ error: err }) })
    return () => { ac.abort(); clearTimeout(retryTimer) }
  }, [parcel, attempt])

  const retry = useCallback(() => setAttempt((n) => n + 1), [])
  const current = res.parcel === parcel && res.attempt === attempt
  return {
    quick: current ? res.quick : null,
    full: current ? res.full : null,
    error: current ? res.error : null,
    loading: !current || (!res.full && !res.error),
    retry,
  }
}

/**
 * Plain-language rewrite of each rotation's "por_que" by the local model, at most once per rotation per analysis.
 * items[rotationId] = { status: 'loading' | 'done' | 'none', texto? }. Never throws, never blocks.
 */
export function useNarrativas(consultaId) {
  const [store, setStore] = useState({ id: null, items: {} })
  const ref = useRef({ id: null, asked: new Set(), ac: null })

  // Also runs on unmount (and twice in dev StrictMode): abort and forget, so a re-run asks again.
  useEffect(() => () => {
    ref.current.ac?.abort()
    ref.current = { id: null, asked: new Set(), ac: null }
  }, [consultaId])

  const request = useCallback((rotationId) => {
    if (!consultaId || !rotationId) return
    if (ref.current.id !== consultaId) {
      ref.current.ac?.abort()
      ref.current = { id: consultaId, asked: new Set(), ac: new AbortController() }
    }
    const cur = ref.current
    if (cur.asked.has(rotationId)) return
    cur.asked.add(rotationId)
    const put = (item) => {
      if (cur.ac.signal.aborted) return
      setStore((s) => ({ id: consultaId, items: { ...(s.id === consultaId ? s.items : {}), [rotationId]: item } }))
    }
    put({ status: 'loading' })
    narrativa({ id: consultaId, rotacion: rotationId }, { signal: cur.ac.signal })
      .then((r) => {
        const c = r?.campos?.por_que
        const ok = c?.valido === true && typeof c.texto === 'string' && c.texto.trim() !== ''
        put(ok ? { status: 'done', texto: c.texto } : { status: 'none' })
      })
      .catch((err) => { if (!isAbort(err)) put({ status: 'none' }) })
  }, [consultaId])

  return { items: store.id === consultaId ? store.items : {}, request }
}
