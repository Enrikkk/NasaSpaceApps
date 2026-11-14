# Agrockham frontend

React 19 + Vite 8 + MapLibre GL 6. Owner: jaime (T-010).

```bash
cd app/frontend && npm install && npm run dev     # http://127.0.0.1:5173
npm run build                                      # static build in dist/ (relative paths, works offline)
```

## What it does now

Un único mapa MapLibre (proyección globo) hace de globo en el inicio y de mapa después.

1. **Inicio:** logo y una vista cercana e inclinada del planeta que llena la página (NASA Blue Marble con relieve
   y fondo marino, halo de atmósfera, estrellas): horizonte en diagonal y España abajo a la izquierda. Cámara en
   `HOME_VIEW` (`src/config/map.js`), ajustada a cada pantalla por `src/components/homeGlobe.js`.
2. **Ir a mis parcelas** (botón bajo MUNDO): entra al mapa con Parcelas activado y vuela a la parcela demo.
3. **Entrar al mapa:** clic en el globo o en "Mundo", o cualquier scroll: zoom continuo hasta España.
   Entonces aparecen REGIONES, FILTROS y las vistas.
3. **Mapa de España** (no deja salir de la península + Baleares). El **primer scroll** vuela a la Región de
   Murcia; a partir de ahí la rueda hace zoom normal. Las regiones encajan su recuadro en la pantalla.
4. **Mapa base** (abajo a la derecha): Satélite (por defecto; Blue Marble y, al acercarse, ortofoto PNOA) o
   Monocromática (todo el detalle del IGN Base en blanco/crema). **Parcelas** es un interruptor aparte que dibuja
   los recintos SIGPAC sobre cualquiera de los dos (clic en un recinto = ficha; si estás lejos, vuela a la parcela
   demo de Torre-Pacheco).
5. Clic en el logo: vuelve al globo.
6. **Móvil (≤ 760 px):** regiones en una fila deslizable, filtros plegados en un botón, vistas a lo ancho abajo.

Los filtros (cultivo, prioridades) guardan su valor en `AppState` pero aún no filtran nada: esperan el contrato de
datos (T-009).

## Structure

```
design/            tokens.css (colours, type, spacing) + fonts. Rules in ../DESIGN.md
src/
  main.jsx         entry: global CSS + AppStateProvider
  App.jsx          layout shared by both screens (home / map)
  state/           AppState context: screen, view, region, filters
  config/          map.js (sources, regions, views, bounds) · filters.js (crops, priorities)
  components/
    ui/            design-system primitives: Panel, SegmentedControl, Slider, Select, Icon
    Logo, RegionsBar, FiltersPanel, ViewSwitcher, MapView (globe + map)
```

Styles are CSS Modules next to each component and only use tokens from `design/tokens.css`.
Map colours are read from the same tokens at runtime.

## Data sources

NASA Blue Marble via GIBS (live). Natural Earth land and borders (public domain, bundled, offline). IGN Base and PNOA (CC BY 4.0, IGN) and SIGPAC
recintos vector tiles (CC BY 4.0, FEGA), loaded live.
Offline copy of the parcels is T-023. All sources and licences: `submission/data-citations.md`.
