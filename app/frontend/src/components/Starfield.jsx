import { useMemo } from 'react'
import styles from './Starfield.module.css'

// Deterministic pseudo-random so the sky is the same on every load (original art, no assets).
function rng(seed) {
  let s = seed
  return () => {
    s = (s * 16807) % 2147483647
    return (s - 1) / 2147483646
  }
}

/** Static star field behind the home globe: three layers of box-shadow dots. */
export default function Starfield({ visible }) {
  const layers = useMemo(() => {
    const r = rng(42)
    const layer = (n, alpha) => Array.from({ length: n }, () =>
      `${Math.round(r() * 2000)}px ${Math.round(r() * 1400)}px rgb(255 255 255 / ${alpha})`).join(',')
    return [layer(160, 0.35), layer(70, 0.6), layer(25, 0.9)]
  }, [])
  return (
    <div className={`${styles.sky} ${visible ? styles.visible : ''}`} aria-hidden="true">
      {layers.map((shadow, i) => <span key={i} className={styles[`s${i}`]} style={{ boxShadow: shadow }} />)}
    </div>
  )
}
