// Small hand-made line icons (original, no icon library). 20x20, stroke = currentColor.
const PATHS = {
  map: <><path d="M2 5l5-2 6 2 5-2v12l-5 2-6-2-5 2z" /><path d="M7 3v12M13 5v12" /></>,
  satellite: <><path d="M7.5 7.5l5 5" /><path d="M5 3l4 4-2 2-4-4zM15 11l4 4-2 2-4-4z" /><path d="M3 17a4 4 0 0 0 4-4" /></>,
  mono:<><circle cx="10" cy="10" r="7" /><path d="M10 3a7 7 0 0 1 0 14z" fill="currentColor" /></>,
  parcel: <><path d="M3 4h6v5H3zM11 4h6v8h-6zM3 11h6v5H3zM11 14h6v2h-6z" /></>,
  back: <path d="M12 4l-6 6 6 6" />,
  pin: <><path d="M10 18s6-5.5 6-10a6 6 0 0 0-12 0c0 4.5 6 10 6 10z" /><circle cx="10" cy="8" r="2" /></>,
}

export default function Icon({ name, size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none" stroke="currentColor"
      strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round" aria-hidden="true">
      {PATHS[name]}
    </svg>
  )
}
