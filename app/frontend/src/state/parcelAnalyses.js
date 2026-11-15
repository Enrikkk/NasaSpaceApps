// Preload of "Tus parcelas": the full /analyze of every saved parcel, computed in the background as soon as the list
// is known (also on the home screen), in list order so the first parcels come first, a few at a time (the API runs at
// most 2 instances). Pure store: the fetch function is injected, the React side is in useParcelAnalyses.js.

/**
 * state[ref] = { status: 'pending' | 'loading' | 'done' | 'error', data?, error? }
 * fetchOne(parcel) -> Promise<analysis>. Errors are kept (no retry loop); retry(ref) asks again.
 */
export function createAnalysesStore(fetchOne, { concurrency = 2 } = {}) {
  let state = {}
  let queue = []              // parcels waiting, in list order
  let wanted = new Map()      // ref -> parcel, the current list
  let running = 0
  const listeners = new Set()
  const emit = () => { for (const fn of listeners) fn() }
  const put = (ref, entry) => { state = { ...state, [ref]: entry }; emit() }

  function pump() {
    while (running < concurrency && queue.length) {
      const p = queue.shift()
      running += 1
      put(p.ref, { status: 'loading' })
      Promise.resolve()
        .then(() => fetchOne(p))
        .then(
          (data) => { if (wanted.has(p.ref)) put(p.ref, { status: 'done', data }) },
          (error) => { if (wanted.has(p.ref)) put(p.ref, { status: 'error', error }) },
        )
        .finally(() => { running -= 1; pump() })
    }
  }

  function enqueue(p) {
    if (queue.some((q) => q.ref === p.ref)) return
    queue.push(p)
    const order = new Map([...wanted.keys()].map((ref, i) => [ref, i]))
    queue.sort((a, b) => (order.get(a.ref) ?? 0) - (order.get(b.ref) ?? 0))
  }

  return {
    getSnapshot: () => state,
    subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn) },

    /** The saved list changed: forget removed parcels, queue the new ones (errors stay until retry). */
    sync(list) {
      wanted = new Map(list.map((p) => [p.ref, p]))
      queue = queue.filter((p) => wanted.has(p.ref))
      const next = {}
      let changed = false
      for (const [ref, entry] of Object.entries(state)) {
        if (wanted.has(ref)) next[ref] = entry
        else changed = true
      }
      for (const p of list) {
        if (next[p.ref]) continue
        next[p.ref] = { status: 'pending' }
        changed = true
        enqueue(p)
      }
      if (changed) { state = next; emit() }
      pump()
    },

    /** An analysis the app already has (the parcel card that was just saved): no need to ask the server again. */
    seed(ref, data) {
      if (!data || state[ref]?.status === 'done') return
      queue = queue.filter((p) => p.ref !== ref)
      put(ref, { status: 'done', data })
    },

    retry(ref) {
      const p = wanted.get(ref)
      if (!p || state[ref]?.status !== 'error') return
      put(ref, { status: 'pending' })
      enqueue(p)
      pump()
    },
  }
}
