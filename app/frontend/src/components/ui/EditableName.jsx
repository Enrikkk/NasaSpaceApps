import { useEffect, useRef, useState } from 'react'
import GlyphIcon from '../parcel/icons.jsx'
import { MAX_NAME } from '../../state/myParcels.js'
import styles from './EditableName.module.css'

/**
 * A name you can click to rename: pencil icon, Enter or leaving the field saves, Esc cancels.
 * `as` is the heading level for the text. An empty name is ignored (the old one stays).
 */
export default function EditableName({ value, onSave, as: Tag = 'span', className = '' }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(value)
  const input = useRef(null)
  useEffect(() => { if (editing) { input.current?.focus(); input.current?.select() } }, [editing])
  useEffect(() => { if (!editing) setDraft(value) }, [value, editing])

  const done = (save) => {
    setEditing(false)
    if (save && draft.trim() && draft.trim() !== value) onSave(draft)
    else setDraft(value)
  }
  if (editing) {
    return (
      <input
        ref={input}
        className={`${styles.input} ${className}`}
        value={draft}
        maxLength={MAX_NAME}
        aria-label="Nombre de la parcela"
        onChange={(e) => setDraft(e.target.value)}
        onBlur={() => done(true)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') { e.preventDefault(); done(true) }
          if (e.key === 'Escape') { e.stopPropagation(); done(false) }
        }}
      />
    )
  }
  return (
    <Tag className={`${styles.name} ${className}`}>
      <button type="button" className={styles.btn} onClick={() => setEditing(true)} aria-label={`Cambiar el nombre «${value}»`} title="Cambiar el nombre">
        <span className={styles.text}>{value}</span>
        <GlyphIcon name="pencil" size={14} />
      </button>
    </Tag>
  )
}
