import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import * as maplibregl from 'maplibre-gl'
import maplibreWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?url'
import 'maplibre-gl/dist/maplibre-gl.css'

// Vite must emit the worker as a real asset. MapLibre's default new URL(..., import.meta.url)
// resolves to index.html in the production build, so the map worker never starts.
maplibregl.setWorkerUrl(maplibreWorkerUrl)
import '../design/tokens.css'
import './styles/global.css'
import { AppStateProvider } from './state/AppState.jsx'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AppStateProvider>
      <App />
    </AppStateProvider>
  </StrictMode>,
)
