import SegmentedControl from './ui/SegmentedControl.jsx'
import Icon from './ui/Icon.jsx'
import { VIEWS } from '../config/map.js'
import { useAppState } from '../state/AppState.jsx'

/** Bottom-right: base map, satellite or monochrome. SIGPAC parcels are always drawn on top. */
export default function ViewSwitcher({ className = '' }) {
  const { view, setView } = useAppState()
  return (
    <div className={className}>
      <SegmentedControl
        label="Mapa base"
        options={VIEWS}
        value={view}
        onChange={setView}
        renderIcon={(opt) => <Icon name={opt.icon} />}
      />
    </div>
  )
}
