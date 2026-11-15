import { useCallback, useState } from 'react'
import Panel from '../ui/Panel.jsx'
import { sigpacUseLabel } from '../../config/sigpacUses.js'
import RotationCard from './RotationCard.jsx'
import { useNarrativas } from './hooks.js'
import { score100 } from './ranking.js'
import {
  isNum, fmtHa, fmtOne, fmtInt, capitalize, rankRotations, BLOCK_LABELS,
} from './helpers.js'
import styles from './sections.module.css'

/**
 * A small quiet line (never a big box) when the server has no data for the recinto, or the click was outside any recinto.
 * The numbers still come from the zone; the title and the header line already show what the click itself knew.
 */
export function Notice({ parcela, parcel }) {
  if (!parcela?.sin_cobertura) return null
  const known = parcel?.recinto && Object.keys(parcel.recinto).length > 0
  return (
    <p className={styles.hint} role="status" title={parcela.aviso || undefined}>
      {known ? 'Estimación de la zona: aún no tenemos los datos de este recinto.' : 'Aquí no hay un recinto: estimación de la zona.'}
    </p>
  )
}

/** The full facts grid (surface, irrigation, slope, region, SIGPAC use), for the folded section. */
function FactsGrid({ parcela }) {
  if (!parcela || parcela.sin_cobertura) return null
  const irrigation = parcela.regadio === true ? 'Regadío' : parcela.regadio === false ? 'Secano' : 'Regadío: no lo sabemos'
  const use = parcela.uso_sigpac ? sigpacUseLabel(parcela.uso_sigpac) : null
  const facts = [
    ['Superficie', isNum(parcela.ha) ? `${fmtHa(parcela.ha)} ha` : 'No lo sabemos'],
    ['Riego', irrigation],
    ['Pendiente', isNum(parcela.pendiente_pct) ? `${fmtOne(parcela.pendiente_pct)} %` : 'No lo sabemos'],
    parcela.comarca && ['Comarca', parcela.comarca],
    use && ['Uso SIGPAC', use],
  ].filter(Boolean)
  return (
    <Panel as="section" className={styles.card} aria-label="Datos de la parcela">
      <dl className={styles.facts}>
        {facts.map(([k, v]) => <div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}
      </dl>
    </Panel>
  )
}

function cropsDeclared(historia) {
  const seen = new Set()
  return (Array.isArray(historia) ? historia : [])
    .filter((h) => h && h.cultivo && h.cultivo !== 'sin producto')
    .sort((a, b) => (b.anio ?? 0) - (a.anio ?? 0))
    .filter((h) => { const k = `${h.anio}|${h.cultivo}`; if (seen.has(k)) return false; seen.add(k); return true })
    .slice(0, 6)
}

/** "Tu parcela": soil, yearly rain and the crops declared to FEGA. */
export function YourParcel({ data }) {
  const suelo = data.suelo ?? {}
  const lluvia = data.clima?.lluvia_anual_mm
  const crops = cropsDeclared(data.historia)
  const rows = []
  if (suelo.textura) rows.push(['Tipo de suelo', capitalize(suelo.textura)])
  if (isNum(suelo.ph_h2o)) rows.push(['Acidez (pH)', fmtOne(suelo.ph_h2o)])
  if (isNum(suelo.materia_organica_pct)) rows.push(['Materia orgánica', `${fmtOne(suelo.materia_organica_pct)} %`])
  if (isNum(lluvia?.valor)) {
    const h = Array.isArray(lluvia.horquilla) ? lluvia.horquilla : []
    rows.push(['Lluvia al año', `${fmtInt(lluvia.valor)} mm${isNum(h[0]) && isNum(h[1]) ? ` (entre ${fmtInt(h[0])} y ${fmtInt(h[1])} según la fuente)` : ''}`])
  }
  const simulated = [suelo, data.clima].some((b) => b?._status === 'simulado')
  return (
    <Panel as="section" className={styles.card} aria-labelledby="sec-tu-parcela">
      <h3 id="sec-tu-parcela" className={styles.h}>Tu parcela</h3>
      {rows.length > 0 ? (
        <dl className={styles.facts}>{rows.map(([k, v]) => <div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}</dl>
      ) : <p className={styles.muted}>No tenemos datos del suelo ni de la lluvia para este punto.</p>}
      {suelo.fuente && <p className={styles.fine}>Suelo: {suelo.fuente}. Es un dato modelado de la zona, no una medida en tu parcela.</p>}
      <div>
        <h4 className={styles.sub}>Cultivos declarados a FEGA</h4>
        {crops.length
          ? <ul className={styles.list}>{crops.map((h) => <li key={`${h.anio}${h.cultivo}`}><b>{h.anio ?? '—'}</b> {capitalize(h.cultivo)}</li>)}</ul>
          : <p className={styles.muted}>No sabemos qué cultivas ahora: no hay declaraciones para esta parcela.</p>}
      </div>
      {simulated && <p className={styles.fine}>Parte de estos datos son simulados, no medidos en tu parcela.</p>}
    </Panel>
  )
}

/** "Cómo influye tu parcela": plain sentences from the suitability check and the climate origin. */
export function Influence({ data }) {
  const frases = [...(data.idoneidad?.frases ?? []), data.clima_origen?.frase]
    .filter((s) => typeof s === 'string' && s.trim())
  if (!frases.length) return null
  return (
    <Panel as="section" className={styles.card} aria-labelledby="sec-influye">
      <h3 id="sec-influye" className={styles.h}>Cómo influye tu parcela</h3>
      <ul className={styles.list}>{frases.map((s, i) => <li key={i}>{s}</li>)}</ul>
    </Panel>
  )
}

/** Everything that is not the answer itself, folded away: soil and rain, the crops declared, how the parcel shapes the result. */
export function MoreAboutParcel({ data }) {
  return (
    <details className={styles.more}>
      <summary>Más sobre tu parcela</summary>
      <div className={styles.moreBody}>
        <FactsGrid parcela={data.parcela} />
        <YourParcel data={data} />
        <Influence data={data} />
      </div>
    </details>
  )
}

/** The options as a ranked list (best first, score 1-100, Eco and Riesgo flags); the reference to compare goes last. */
export function Rotations({ data, priorities, orientativo = false }) {
  const rotaciones = data.rotaciones ?? []
  const noEval = data.idoneidad?.no_evaluable?.motivo
  const ranked = rankRotations(rotaciones, priorities)
  const consultaId = data._meta?.consulta_id
  const { items, request } = useNarrativas(consultaId)
  const [openId, setOpenId] = useState(null)       // the detail of a card opens only when asked for
  const need = useCallback((id) => request(id), [request])

  if (noEval || !rotaciones.length) {
    return (
      <p className={styles.hint} role="status">
        {noEval ? `No recomendamos cultivos aquí: ${noEval}` : 'No hemos podido calcular cultivos para esta parcela.'}
      </p>
    )
  }
  return (
    <section className={styles.rotations} aria-labelledby="sec-rot">
      <h3 id="sec-rot" className={styles.h}>
        Recomendado{orientativo && <span className={styles.chip} title="Cálculo con datos de la zona, no de esta parcela">orientativo</span>}
      </h3>
      {ranked.map(({ rot, best, rank, score }) => (
        <RotationCard
          key={rot.id}
          rot={rot}
          rank={rank}
          score={score100(score)}
          best={best}
          open={openId === rot.id}
          onToggle={() => setOpenId((cur) => (cur === rot.id ? null : rot.id))}
          narr={items[rot.id]}
          onNeedNarrative={need}
          globalFrases={data.idoneidad?.frases ?? []}
        />
      ))}
      <p className={styles.tiny}>Puntuación de 1 a 100, relativa entre estas opciones. No es una garantía.</p>
    </section>
  )
}

const FEGA_FALLBACK = 'Fuente de los datos de los recintos: Fondo Español de Garantía Agraria O.A. (FEGA), licencia CC BY 4.0. Sin respaldo ni patrocinio del FEGA.'

/** Warnings, attributions (licence requirement), simulated blocks: folded; one tiny line stays visible. */
export function Footer({ data }) {
  const meta = data?._meta ?? {}
  const avisos = (meta.avisos ?? []).filter((s) => typeof s === 'string' && s.trim())
  const atribs = (meta.atribuciones ?? []).filter((s) => typeof s === 'string' && s.trim())
  const simulated = Object.entries(meta.estado_bloques ?? {}).filter(([, st]) => st === 'simulado').map(([k]) => k)
  return (
    <footer className={styles.footer}>
      <p>Herramienta de apoyo: consulta a tu técnico antes de decidir.</p>
      <details className={styles.sources}>
        <summary>Fuentes y avisos</summary>
        <div className={styles.sourcesBody}>
          {avisos.map((s, i) => <p key={i}><b>Aviso:</b> {s}</p>)}
          {simulated.map((k) => (
            <p key={k}><b>Dato simulado:</b> {capitalize(BLOCK_LABELS[k] ?? k)} son datos de ejemplo, no medidos en tu parcela.</p>
          ))}
          {(atribs.length ? atribs : [FEGA_FALLBACK]).map((s, i) => <p key={i}>{s}</p>)}
          <p>No es asesoría legal ni agronómica.</p>
        </div>
      </details>
    </footer>
  )
}
