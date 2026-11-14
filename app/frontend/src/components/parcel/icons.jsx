// Small line icons for the parcel panel (20x20, stroke = currentColor), same style as ui/Icon.jsx.
const PATHS = {
  close: <path d="M5 5l10 10M15 5L5 15" />,
  chevron: <path d="M5 8l5 5 5-5" />,
  ok: <><circle cx="10" cy="10" r="7.5" /><path d="M6.5 10.2l2.4 2.4 4.6-5" /></>,
  warn: <><path d="M10 2.8l8 14H2z" /><path d="M10 8v4M10 14.4v.2" /></>,
  stop: <><circle cx="10" cy="10" r="7.5" /><path d="M5.5 5.5l9 9" /></>,
  unknown: <><circle cx="10" cy="10" r="7.5" /><path d="M7.6 7.8a2.5 2.5 0 1 1 3.4 2.3c-.7.3-1 .8-1 1.5M10 14.2v.2" /></>,
  down: <path d="M4 6l5 5 3-3 4 4M16 8v4h-4" />,
  star: <path d="M10 2.8l2.1 4.5 4.9.6-3.6 3.4.9 4.9L10 13.8l-4.3 2.4.9-4.9L3 7.9l4.9-.6z" />,
  leaf: <><path d="M4 16C4 8 9 4 16 4c0 7-4 12-12 12z" /><path d="M4 16l7-7" /></>,
  pencil: <><path d="M13 4l3 3L7.5 15.5 4 16l.5-3.5z" /><path d="M11.5 5.5l3 3" /></>,
  bookmark: <path d="M6 3.5h8V17l-4-3.2L6 17z" />,
  retry: <><path d="M16 10a6 6 0 1 1-2-4.5" /><path d="M16 3v3.5h-3.5" /></>,
}

export default function GlyphIcon({ name, size = 20, filled = false }) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill={filled ? 'currentColor' : 'none'} stroke="currentColor"
      strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round" aria-hidden="true" focusable="false">
      {PATHS[name]}
    </svg>
  )
}
