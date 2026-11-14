import styles from './SegmentedControl.module.css'

/** Single choice between a few options. options: [{ id, label, icon? }] */
export default function SegmentedControl({ label, options, value, onChange, renderIcon }) {
  return (
    <div className={styles.group} role="radiogroup" aria-label={label}>
      {options.map((opt) => {
        const active = opt.id === value
        return (
          <button
            key={opt.id}
            type="button"
            role="radio"
            aria-checked={active}
            className={`${styles.option} ${active ? styles.active : ''}`}
            onClick={() => onChange(opt.id)}
          >
            {renderIcon && <span className={styles.icon} aria-hidden="true">{renderIcon(opt)}</span>}
            <span>{opt.label}</span>
          </button>
        )
      })}
    </div>
  )
}
