// Crop filter. The ids are the engine's crop ids (`ciclos_detalle[].cultivo`) and the list is its rotation catalogue
// (app/backend/engine/decision/rotations.py CATALOG): only crops that can appear in an option. Lemon is perennial and
// never enters a rotation, so it is not offered. `match` is the fallback when an option has no ciclos_detalle.
export const CROPS = [
  { id: 'todos', label: 'Todos los cultivos' },
  { id: 'lechuga', label: 'Lechuga', match: /lechuga/i },
  { id: 'brocoli', label: 'Brócoli', match: /br[oó]coli/i },
  { id: 'melon', label: 'Melón', match: /mel[oó]n/i },
  { id: 'alcachofa', label: 'Alcachofa', match: /alcachofa/i },
]

export const PRIORITIES = [
  { id: 'beneficio', label: 'Beneficio' },
  { id: 'agua', label: 'Ahorro de agua' },
  { id: 'suelo', label: 'Salud del suelo' },
  { id: 'riesgo', label: 'Menos riesgo' },
]

export const DEFAULT_PRIORITIES = { beneficio: 50, agua: 50, suelo: 50, riesgo: 50 }
