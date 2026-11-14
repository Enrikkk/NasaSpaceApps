import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// base './' so the static build works from any folder (offline demo, GitHub Pages).
export default defineConfig({
  plugins: [react()],
  base: './',
  server: { port: 5173, host: '127.0.0.1' },
  // MapLibre 6 loads its worker with new URL(..., import.meta.url); pre-bundling breaks that path.
  optimizeDeps: { exclude: ['maplibre-gl'] },
})
