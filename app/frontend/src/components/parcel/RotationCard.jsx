import { useEffect, useId, useState } from 'react'
import Panel from '../ui/Panel.jsx'
import GlyphIcon from './icons.jsx'
import {
  isNum, fmtInt, fmtPlain, fmtHa, splitName, legalOf, ENV_LEVELS,
} from './helpers.js'
import { cropsOf, subtitleOf, ecoInfo, riskInfo } from './ranking.js'
import styles from './RotationCard.module.css'

// "una pérdida de 1.041 €" / "1.041 €": losses are always said as losses.
const eurWord = (v) => (v < 0 ? `una pérdida de ${fmtPlain(Math.abs(v))} €` : `${fmtPlain(v)} €`)

function MoneyRange({ lo, hi }) {
  if (!isNum(lo) || !isNum(hi)) return <span className={styles.range}>Sin rango disponible</span>
  return <span className={styles.range}>Entre {eurWord(lo)} en un mal año y {eurWord(hi)} en un buen año</span>
}

function Money({ margen }) {
  const p50 = isNum(margen?.p50) ? margen.p50 : margen?.valor
  if (!isNum(p50)) {
    return (
      <div className={`${styles.metric} ${styles.wide}`}>
        <dt>En un año normal</dt>
        <dd><span className={styles.noData}>Sin precio: no se puede calcular</span></dd>
      </div>
    )
  }
  const loss = p50 < 0
  return (
    <div className={`${styles.metric} ${styles.wide}`}>
      <dt>En un año normal</dt>
      <dd>
        <span className={`${styles.big} ${loss ? styles.loss : ''}`}>
          {loss && <GlyphIcon name="down" size={20} />}
          {loss ? `Pérdida de ${fmtPlain(Math.abs(p50))} €` : `${fmtPlain(p50)} €`}
          <small> por hectárea y año</small>
        </span>
        <MoneyRange lo={margen.p10} hi={margen.p90} />
      </dd>
    </div>
  )
}

function GoodYears({ exito }) {
  const v = exito?.valor
  const [lo, hi] = Array.isArray(exito?.horquilla) ? exito.horquilla : []
  return (
    <div className={styles.metric}>
      <dt>Años buenos</dt>
      <dd>
        {isNum(v)
          ? <span className={styles.big}>{fmtInt(v)} %</span>
          : <span className={styles.noData}>No se puede calcular</span>}
        {isNum(v) && isNum(lo) && isNum(hi) && <span className={styles.range}>Entre {fmtInt(lo)} % y {fmtInt(hi)} %</span>}
        {isNum(v) && <span className={styles.range}>en años históricos simulados</span>}
      </dd>
    </div>
  )
}

function Water({ agua }) {
  return (
    <div className={styles.metric}>
      <dt>Agua</dt>
      <dd>
        {isNum(agua)
          ? <span className={styles.big}>{fmtInt(agua)}<small> m³/ha al año</small></span>
          : <span className={styles.noData}>No lo sabemos</span>}
      </dd>
    </div>
  )
}

export function LegalBadge({ semaforo }) {
  const l = legalOf(semaforo?.color)
  return (
    <span className={`${styles.legal} ${styles[`legal_${l.icon}`]}`}>
      <GlyphIcon name={l.icon} size={20} />
      <span>{l.word}</span>
    </span>
  )
}

function Legal({ semaforo }) {
  return (
    <div className={styles.metric}>
      <dt>Semáforo legal</dt>
      <dd><LegalBadge semaforo={semaforo} /></dd>
    </div>
  )
}

function Environment({ ambiente }) {
  const lvl = ENV_LEVELS[ambiente?.nivel]
  return (
    <div className={styles.metric}>
      <dt>Medio ambiente</dt>
      <dd>
        {lvl ? (
          <span className={styles.env}>
            <span className={styles.meter} aria-hidden="true">
              {[1, 2, 3].map((i) => <i key={i} className={i <= lvl.n ? styles.on : ''} />)}
            </span>
            {lvl.word}
          </span>
        ) : <span className={styles.noData}>Sin evaluar</span>}
      </dd>
    </div>
  )
}

function Totals({ totales }) {
  if (!totales) return null
  const m = totales.margen_eur
  const p50 = isNum(m?.p50) ? m.p50 : null
  return (
    <div className={`${styles.metric} ${styles.wide} ${styles.totals}`}>
      <dt>En toda tu parcela{isNum(totales.area_ha) ? ` (${fmtHa(totales.area_ha)} ha)` : ''}, cada año</dt>
      <dd>
        {p50 !== null
          ? <span className={styles.medium}>{eurWord(p50)} en un año normal</span>
          : <span className={styles.noData}>Sin precio: no se puede calcular</span>}
        {p50 !== null && isNum(m.p10) && isNum(m.p90) && (
          <span className={styles.range}>Entre {eurWord(m.p10)} en un mal año y {eurWord(m.p90)} en un buen año</span>
        )}
        {isNum(totales.agua_m3) && <span className={styles.range}>Agua: {fmtInt(totales.agua_m3)} m³ al año</span>}
      </dd>
    </div>
  )
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

/** The "por qué" paragraph: original text now, replaced by the local model's version if one arrives and is valid. */
function Why({ original, narr }) {
  const [showOriginal, setShowOriginal] = useState(false)
  const ai = narr?.status === 'done' ? narr.texto : null
  const shown = ai && !showOriginal ? ai : original
  if (!shown && narr?.status !== 'loading') return null
  return (
    <section className={styles.block}>
      <h4>Por qué</h4>
      {shown && <p>{shown}</p>}
      {narr?.status === 'loading' && <p className={styles.wait} role="status">Preparando una explicación más sencilla…</p>}
      {ai && original && (
        <p className={styles.aiTag}>
          <span>{showOriginal ? 'Texto original' : 'Explicado por un modelo de IA local · cifras comprobadas'}</span>
          <button type="button" className={styles.link} onClick={() => setShowOriginal((s) => !s)}>
            {showOriginal ? 'ver la explicación sencilla' : 'ver texto original'}
          </button>
        </p>
      )}
    </section>
  )
}

/**
 * One rotation. Metrics are always visible; the details open on click (one card open at a time, the parent decides).
 * Opening a card asks for the plain-language "por qué" (once per rotation, cached by the parent).
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
          <p className={styles.sub}>{rot.es_actual ? label : subtitleOf(rot)}</p>
          {(rot.es_actual || best) && (
            <span className={styles.badges}>
              {rot.es_actual && <span className={`${styles.badge} ${styles.badgeRef}`}>Referencia para comparar</span>}
              {best && (
                <span className={`${styles.badge} ${styles.badgeBest}`}>
                  <GlyphIcon name="star" size={16} />La que mejor encaja con tus prioridades
                </span>
              )}
            </span>
          )}
          <dl className={styles.metrics}>
            <Money margen={rot.margen_eur_ha} />
            <GoodYears exito={rot.exito_pct} />
            <Water agua={rot.agua_m3_ha} />
            <Legal semaforo={legal} />
            <Environment ambiente={rot.ambiente} />
            <Totals totales={rot.totales_parcela} />
          </dl>
          {steps.length > 0 && (
            <section className={styles.block}>
              <h4>Plan año a año</h4>
              <ul>{steps.map((s, i) => <li key={i}>{s}</li>)}</ul>
            </section>
          )}
          <Why original={t.por_que} narr={narr} />
          {legal && (legal.motivo || legal.provisional) && (
            <section className={styles.block}>
              <h4>Semáforo legal: {legalOf(legal.color).word}</h4>
              {legal.motivo && <p className={styles.small}>{legal.motivo}</p>}
              {(legal.provisional || legal._status === 'simulado') && (
                <p className={styles.small}>Provisional: las reglas legales aún están por verificar.</p>
              )}
            </section>
          )}
          {rot.ambiente?.frase && (
            <section className={styles.block}>
              <h4>Medio ambiente</h4>
              <p className={styles.small}>{rot.ambiente.frase}</p>
            </section>
          )}
          <TextList title="Riesgos" items={t.riesgos_texto} />
          <TextList title="Lo que no sabemos" items={t.no_sabemos} />
          <TextList title="Cómo influye tu parcela" items={frases} />
          <TextList title="En qué nos basamos" items={t.evidencia_resumen} />
          {t.consulta && <p className={styles.small}>{t.consulta}</p>}
        </div>
      )}
    </Panel>
  )
}
