// Brunson words as images (scripts/render_display.py): every device shows the brand type, no font file is loaded.
// The <img> is sized in em (.display-img in global.css), so it follows the font-size rules each title already has.
import regiones from '../assets/display/regiones.png'
import filtros from '../assets/display/filtros.png'
import tusParcelas from '../assets/display/tus-parcelas.png'
import informe from '../assets/display/informe.png'
import logoAgro from '../assets/display/logo-agro.png'
import logoCkhamCream from '../assets/display/logo-ckham-cream.png'
import logoCkhamDark from '../assets/display/logo-ckham-dark.png'

const SRC = {
  regiones,
  filtros,
  'tus-parcelas': tusParcelas,
  informe,
  'logo-agro': logoAgro,
  'logo-ckham-cream': logoCkhamCream,
  'logo-ckham-dark': logoCkhamDark,
}

/** alt = the visible word (it is the accessible name); pass alt="" when a parent already labels it. */
export default function DisplayText({ name, alt, className = '' }) {
  return <img src={SRC[name]} alt={alt} className={`display-img ${className}`} draggable={false} decoding="async" />
}
