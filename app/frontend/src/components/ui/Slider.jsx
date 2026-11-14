import { useId } from 'react'
import styles from './Slider.module.css'

/** Labelled 0-100 range input. */
export default function Slider({ label, value, onChange, min = 0, max = 100, step = 1 }) {
  const id = useId()
  return (
    <div className={styles.field}>
      <div className={styles.row}>
        <label htmlFor={id}>{label}</label>
        <output htmlFor={id} className={styles.value}>{Math.round(value)}</output>
      </div>
      <input
        id={id}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className={styles.range}
        style={{ '--pct': `${((value - min) / (max - min)) * 100}%` }}
      />
    </div>
  )
}
