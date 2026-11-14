import styles from './Panel.module.css'

/** Raised surface. variant: 'card' (rounded) | 'bar' (square, for headers). */
export default function Panel({ as: Tag = 'div', variant = 'card', className = '', children, ...rest }) {
  return (
    <Tag className={`${styles.panel} ${styles[variant]} ${className}`} {...rest}>
      {children}
    </Tag>
  )
}
