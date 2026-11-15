import { useLayoutEffect, useRef, useState } from 'react'
import styles from './Logo.module.css'
import DisplayText from './DisplayText.jsx'

// Height the small (map) logo should have, in px. The word keeps one font size and is scaled with a CSS transform,
// so going big <-> small is one smooth animation instead of a jump.
const SMALL_PX = { desktop: 40, phone: 28 }

/**
 * AGRO (rough, green) + CKHAM (clean, cream), always a button back to the home globe.
 * size: 'lg' (home) | 'sm' (map). onLight: over a light map, CKHAM turns dark.
 */
export default function Logo({ size = 'lg', onClick, onLight = false }) {
  const ref = useRef(null)
  const [k, setK] = useState(0.3)

  useLayoutEffect(() => {
    const measure = () => {
      const fs = parseFloat(getComputedStyle(ref.current).fontSize)
      const target = window.innerWidth <= 760 ? SMALL_PX.phone : SMALL_PX.desktop
      setK(Math.min(1, target / fs))
    }
    measure()
    window.addEventListener('resize', measure)
    return () => window.removeEventListener('resize', measure)
  }, [])

  return (
    <div
      ref={ref}
      className={`${styles.logo} ${size === 'sm' ? styles.small : ''} ${onLight ? styles.onLight : ''}`}
      style={{ '--logo-k': k }}
    >
      <button type="button" onClick={onClick} className={styles.button} aria-label="Agrockham, volver al inicio">
        <span className={`display ${styles.word}`}>
          <DisplayText name="logo-agro" alt="" />
          <DisplayText name={onLight ? 'logo-ckham-dark' : 'logo-ckham-cream'} alt="" />
        </span>
      </button>
    </div>
  )
}
