import { useEffect, useId, useState } from 'react'
import Panel from '../ui/Panel.jsx'
import GlyphIcon from './icons.jsx'
import { isNum, fmtInt, fmtPlain, fmtHa, splitName, legalOf } from './helpers.js'
import { cropsOf, subtitleOf, ecoInfo, riskInfo } from './ranking.js'
import styles from './RotationCard.module.css'

export function LegalBadge({ semaforo }) {
  const l = legalOf(semaforo?.color)
  return (
    <span className={`${styles.legal} ${styles[`legal_${l.icon}`]}`}>
      <GlyphIcon name={l.icon} size={18} />
      <span>{l.word}</span>
    </span>
  )
}

/** One big figure with its unit underneath. */
function Stat({ label, note, note2, bad, children }) {
  return (
    <div className={styles.stat}>
      <dt>{label}</dt>
      <dd>
        <span className={`${styles.statBig} ${bad ? styles.loss : ''}`}>{children}</span>
        {note && <small>{note}</small>}
        {note2 && <small>{note2}</small>}
      </dd>
    </div>
  )
}

/** The four figures that matter, big and short. Losses are said as losses (sign and colour). */
function Stats({ rot }) {
  const m = rot.margen_eur_ha
  const p50 = isNum(m?.p50) ? m.p50 : m?.valor
  const e = rot.exito_pct
  const [lo, hi] = Array.isArray(e?.horquilla) ? e.horquilla : []
  return (
    <dl className={styles.stats}>
      <Stat
        label="Beneficio"
        bad={isNum(p50) && p50 < 0}
        note={isNum(p50) ? 'por ha y año' : 'sin precio'}
        note2={isNum(m?.p10) && isNum(m?.p90) ? `de ${fmtPlain(m.p10)} a ${fmtPlain(m.p90)} €` : null}
      >
        {isNum(p50) ? `${p50 < 0 ? '−' : ''}${fmtPlain(Math.abs(p50))} €` : '—'}
      </Stat>
      <Stat
        label="Años buenos"
        note={isNum(e?.valor) ? 'en años simulados' : 'sin dato'}
        note2={isNum(e?.valor) && isNum(lo) && isNum(hi) ? `entre ${fmtInt(lo)} y ${fmtInt(hi)} %` : null}
      >
        {isNum(e?.valor) ? `${fmtInt(e.valor)} %` : '—'}
      </Stat>
      <Stat label="Agua" note={isNum(rot.agua_m3_ha) ? 'm³ por ha y año' : 'sin dato'}>
        {isNum(rot.agua_m3_ha) ? fmtInt(rot.agua_m3_ha) : '—'}
      </Stat>
      <Stat label="Legal"><LegalBadge semaforo={rot.semaforo_legal} /></Stat>
    </dl>
  )
}

function WholeParcel({ totales }) {
  const m = totales?.margen_eur
  if (!isNum(m?.p50)) return null
  const word = m.p50 < 0 ? `pérdida de ${fmtPlain(Math.abs(m.p50))} €` : `${fmtPlain(m.p50)} €`
  return <p className={styles.small}>Tu parcela entera{isNum(totales.area_ha) ? ` (${fmtHa(totales.area_ha)} ha)` : ''}: {word} al año</p>
}

function TextList({ title, items }) {
  const list = (Array.isArray(items) ? items : []).filter((s) => typeof s === 'string' && s.trim())
  if (!list.length) return null
  return (
    <section className={styles.block}>
      <h4>{title}</h4>
      <ul>{list.map((s, i) => <li key={i}>{s}</li>)}</ul>
    </section>
  )
}

/** The "por qué" paragraph: the template text, or the local model's version if it arrives and is valid. Three lines, then "más". */
function Why({ original, narr }) {
  const [showOriginal, setShowOriginal] = useState(false)
  const [more, setMore] = useState(false)
  const ai = narr?.status === 'done' ? narr.texto : null
  const shown = ai && !showOriginal ? ai : original
  if (!shown && narr?.status !== 'loading') return null
  const long = (shown ?? '').length > 170
  return (
    <section className={styles.why}>
      {shown && <p className={more || !long ? '' : styles.clamp}>{shown}</p>}
      {narr?.status === 'loading' && <p className={styles.wait} role="status">Preparando una explicación más sencilla…</p>}
      <p className={styles.aiTag}>
        {long && (
          <button type="button" className={styles.link} onClick={() => setMore((m) => !m)}>{more ? 'menos' : 'más'}</button>
        )}
        {ai && <span>{showOriginal ? 'Texto original' : 'IA local · cifras comprobadas'}</span>}
        {ai && original && (
          <button type="button" className={styles.link} onClick={() => setShowOriginal((s) => !s)}>
            {showOriginal ? 'ver la sencilla' : 'ver el original'}
          </button>
        )}
      </p>
    </section>
  )
}

/**
 * One option as a single line (rank, crops, score, Eco and Riesgo flags); clicking the line opens its detail: four
 * figures, a short explanation and, folded, the notes and assumptions. The parent decides which one is open.
 * Opening asks for the plain-language "por qué" (once per rotation, cached by the parent).
 */
export default function RotationCard({ rot, rank, score, best, open, onToggle, narr, onNeedNarrative, globalFrases }) {
  const bodyId = useId()
  const { label, steps } = splitName(rot.nombre)
  const t = rot.texto ?? {}
  const frases = (rot.idoneidad?.frases ?? []).filter((f) => !globalFrases.includes(f))
  const legal = rot.semaforo_legal

  useEffect(() => { if (open) onNeedNarrative(rot.id) }, [open, rot.id, onNeedNarrative])

  const crops = cropsOf(rot)
  const eco = ecoInfo(rot)
  const risk = riskInfo(rot)
  const tips = { eco, riesgo: risk }
  const [tip, setTip] = useState(null)           // which flag explanation is open: 'eco' | 'riesgo' | null
  const tipId = `${bodyId}-tip`
  const flip = (k) => setTip((cur) => (cur === k ? null : k))

  return (
    <Panel as="article" className={`${styles.card} ${open ? styles.open : ''} ${rot.es_actual ? styles.ref : ''}`}>
      <div className={styles.line}>
        <button type="button" className={styles.main} aria-expanded={open} aria-controls={bodyId} onClick={onToggle}>
          <span className={`${styles.rank} ${best ? styles.rankBest : ''}`} aria-label={isNum(rank) ? `Puesto ${rank}` : 'Referencia'}>
            {isNum(rank) ? rank : '·'}
          </span>
          <span className={styles.title} title={crops.join(' · ')}>{crops.length ? crops.join(' · ') : label}</span>
          {isNum(score)
            ? <span className={styles.score} aria-label={`Puntuación ${score} sobre 100`}>{score}</span>
            : <span className={styles.noScore}>ref.</span>}
        </button>
        <span className={styles.flags}>
          {[['eco', eco, 'leaf'], ['riesgo', risk, 'warn']].map(([k, info, icon]) => (
            <button
              key={k}
              type="button"
              className={`${styles.flag} ${styles[`tone_${info.tone}`]} ${tip === k ? styles.flagOn : ''}`}
              aria-expanded={tip === k}
              aria-controls={tipId}
              aria-label={info.label}
              title={info.label}
              onClick={() => flip(k)}
            >
              <GlyphIcon name={icon} size={14} /><span>{info.short}</span>
            </button>
          ))}
        </span>
      </div>

      {tip && <p id={tipId} className={styles.tip} role="note"><b>{tips[tip].label}.</b> {tips[tip].text}</p>}

      {open && (
        <div id={bodyId} className={styles.details}>
          <p className={styles.sub}>
            {rot.es_actual ? `Referencia para comparar · ${label}` : subtitleOf(rot)}
            {best && <span className={styles.bestTag}><GlyphIcon name="star" size={14} filled /> la que mejor encaja</span>}
          </p>
          <Stats rot={rot} />
          <WholeParcel totales={rot.totales_parcela} />
          <Why original={t.por_que} narr={narr} />
          <details className={styles.notes}>
            <summary>Notas y supuestos</summary>
            <div className={styles.notesBody}>
              {steps.length > 0 && (
                <section className={styles.block}>
                  <h4>Plan año a año</h4>
                  <ul>{steps.map((s, i) => <li key={i}>{s}</li>)}</ul>
                </section>
              )}
              {legal && (legal.motivo || legal.provisional) && (
                <section className={styles.block}>
                  <h4>Semáforo legal: {legalOf(legal.color).word}</h4>
                  {legal.motivo && <p className={styles.small}>{legal.motivo}</p>}
                  {(legal.provisional || legal._status === 'simulado') && (
                    <p className={styles.small}>Provisional: las reglas legales aún están por verificar.</p>
                  )}
                </section>
              )}
              <TextList title="Riesgos" items={t.riesgos_texto} />
              <TextList title="Lo que no sabemos" items={t.no_sabemos} />
              <TextList title="Cómo influye tu parcela" items={frases} />
              <TextList title="En qué nos basamos" items={t.evidencia_resumen} />
              {t.consulta && <p className={styles.small}>{t.consulta}</p>}
            </div>
          </details>
        </div>
      )}
    </Panel>
  )
}
