import { useId } from 'react'
import styles from './Select.module.css'

/** Labelled native select. options: [{ id, label }] */
export default function Select({ label, options, value, onChange }) {
  const id = useId()
  return (
    <div className={styles.field}>
      <label htmlFor={id}>{label}</label>
      <select id={id} value={value} onChange={(e) => onChange(e.target.value)} className={styles.select}>
        {options.map((o) => <option key={o.id} value={o.id}>{o.label}</option>)}
      </select>
    </div>
  )
}
