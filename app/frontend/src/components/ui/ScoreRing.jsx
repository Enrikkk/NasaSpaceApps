import styles from './ScoreRing.module.css'

const R = 15
const C = 2 * Math.PI * R

/**
 * Small ring + the percentage next to it. status: 'loading' (spinning arc), 'done' (arc filled to value),
 * 'none' (no figure: dashed ring and a dash), 'error' (dashed ring and "!"). tone colours the arc; the number is
 * always written, so colour is never the only signal.
 */
export default function ScoreRing({ value, status = 'done', tone = 'good', title, size = 34, showText = true, textClassName = '' }) {
  const has = status === 'done' && typeof value === 'number' && Number.isFinite(value)
  const pct = has ? Math.max(0, Math.min(100, value)) : 0
  const text = status === 'loading' ? '…' : status === 'error' ? '!' : has ? `${Math.round(pct)} %` : '—'
  return (
    <span className={styles.wrap} title={title} role="img" aria-label={title ?? text}>
      <svg width={size} height={size} viewBox="0 0 36 36" aria-hidden="true"
        className={`${styles.ring} ${status === 'loading' ? styles.spin : ''}`}>
        <circle cx="18" cy="18" r={R} className={`${styles.track} ${!has && status !== 'loading' ? styles.dashed : ''}`} />
        {status === 'loading' && <circle cx="18" cy="18" r={R} className={styles.arc} strokeDasharray={`${C * 0.25} ${C}`} />}
        {has && (
          <circle cx="18" cy="18" r={R} className={`${styles.arc} ${styles[tone]}`}
            strokeDasharray={`${(C * pct) / 100} ${C}`} transform="rotate(-90 18 18)" />
        )}
      </svg>
      {showText && <span className={`${styles.pct} ${textClassName}`}>{text}</span>}
    </span>
  )
}
