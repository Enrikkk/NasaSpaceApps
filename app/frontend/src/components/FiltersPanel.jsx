import { useId, useState } from 'react'
import Panel from './ui/Panel.jsx'
import DisplayText from './DisplayText.jsx'
import Select from './ui/Select.jsx'
import Slider from './ui/Slider.jsx'
import { CROPS, PRIORITIES } from '../config/filters.js'
import { useAppState } from '../state/AppState.jsx'
import styles from './FiltersPanel.module.css'

/**
 * Right panel: crop filter + priority weights. Values live in AppState; the engine data (T-009) will read them.
 * Always folded into its title; the chevron opens and closes the controls.
 */
export default function FiltersPanel() {
  const { crop, setCrop, priorities, setPriority } = useAppState()
  const [open, setOpen] = useState(false)
  const bodyId = useId()
  return (
    <Panel as="aside" className={`${styles.panel} ${open ? styles.open : ''}`} aria-label="Filtros">
      <h2 className={styles.heading}>
        <button
          type="button"
          className={`display ${styles.title}`}
          aria-expanded={open}
          aria-controls={bodyId}
          onClick={() => setOpen((o) => !o)}
        >
          <span><DisplayText name="filtros" alt="Filtros" /></span>
          <span className={styles.chevron} aria-hidden="true">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2"
              strokeLinecap="round" strokeLinejoin="round"><path d="M5 8l5 5 5-5" /></svg>
          </span>
        </button>
      </h2>
      <div id={bodyId} className={styles.body}>
        <Select label="Cultivo" options={CROPS} value={crop} onChange={setCrop} />
        <fieldset className={styles.group}>
          <legend className={styles.legend}>¿Qué te importa más?</legend>
          {PRIORITIES.map((p) => (
            <Slider key={p.id} label={p.label} value={priorities[p.id]} onChange={(v) => setPriority(p.id, v)} />
          ))}
        </fieldset>
      </div>
    </Panel>
  )
}
