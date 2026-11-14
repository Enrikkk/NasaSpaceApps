// Filter options. Crops follow coordination/PLAN.md; they will come from the data contract (T-009) later.
export const CROPS = [
  { id: 'todos', label: 'Todos los cultivos' },
  { id: 'lechuga', label: 'Lechuga' },
  { id: 'brocoli', label: 'Brócoli' },
  { id: 'melon', label: 'Melón' },
  { id: 'limon', label: 'Limón' },
]

export const PRIORITIES = [
  { id: 'beneficio', label: 'Beneficio' },
  { id: 'agua', label: 'Ahorro de agua' },
  { id: 'suelo', label: 'Salud del suelo' },
  { id: 'riesgo', label: 'Menos riesgo' },
]

export const DEFAULT_PRIORITIES = { beneficio: 50, agua: 50, suelo: 50, riesgo: 50 }
