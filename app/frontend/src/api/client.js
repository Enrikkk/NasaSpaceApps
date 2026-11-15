// Agrockham backend client (app/backend/api). Base URL: VITE_API_BASE or the local API.
export const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8080'

const RECINTO_KEYS = ['provincia', 'municipio', 'agregado', 'zona', 'poligono', 'parcela', 'recinto']

/**
 * SIGPAC reference from vector-tile properties. Values may be strings or numbers; only keys that parse to a
 * whole number >= 0 are kept (the API rejects anything else with 422).
 */
export function recintoFromProps(props = {}) {
  const out = {}
  for (const k of RECINTO_KEYS) {
    const raw = props[k]
    if (raw === null || raw === undefined || (typeof raw === 'string' && raw.trim() === '')) continue
    const n = Number(raw)
    if (Number.isInteger(n) && n >= 0) out[k] = n
  }
  return out
}

export class ApiError extends Error {
  constructor(message, { status = 0, timeout = false } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.timeout = timeout
  }
}

/** POST JSON. `signal` aborts (the caller ignores the AbortError); `timeoutMs` turns into ApiError.timeout. */
async function post(path, body, { signal, timeoutMs = 0 } = {}) {
  const ctl = new AbortController()
  let timedOut = false
  const onAbort = () => ctl.abort()
  if (signal) {
    if (signal.aborted) ctl.abort()
    else signal.addEventListener('abort', onAbort, { once: true })
  }
  const timer = timeoutMs ? setTimeout(() => { timedOut = true; ctl.abort() }, timeoutMs) : null
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: ctl.signal,
    })
    if (!res.ok) throw new ApiError(`HTTP ${res.status}`, { status: res.status })
    return await res.json()
  } catch (err) {
    if (timedOut) throw new ApiError('timeout', { timeout: true })
    if (err instanceof ApiError || err?.name === 'AbortError') throw err
    throw new ApiError(err?.message || 'network')
  } finally {
    if (timer) clearTimeout(timer)
    signal?.removeEventListener('abort', onAbort)
  }
}

export const isAbort = (err) => err?.name === 'AbortError'

/**
 * POST /analyze. bloques: 'parcela' returns only the parcel block (~10 ms); omit it for the full analysis
 * (about 1 s, up to a minute when soil/climate for that spot are not cached yet).
 */
export function analyze({ lat, lon, recinto }, { bloques, signal } = {}) {
  const body = { lat, lon }
  if (recinto && Object.keys(recinto).length) body.recinto = recinto
  const query = bloques ? `?bloques=${encodeURIComponent(bloques)}` : ''
  return post(`/analyze${query}`, body, { signal, timeoutMs: bloques ? 20_000 : 150_000 })
}

/** POST /narrativa: the "por_que" text of one rotation, rewritten by a local language model. Can take minutes. */
export function narrativa({ id, rotacion }, { signal } = {}) {
  return post('/narrativa', { id, rotacion, campos: ['por_que'] }, { signal, timeoutMs: 300_000 })
}
