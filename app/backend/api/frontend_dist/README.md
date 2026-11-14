# frontend_dist: la app estatica servida por la API

Si existe `index.html` aqui (o en `FRONTEND_DIR`), la API la sirve en `/` (las rutas /health, /analyze, /parcel, /recintos y /docs mandan sobre ella). Un solo origen: no hace falta CORS ni un hosting aparte.
Construir (desde app/frontend de la rama integrada): `VITE_API_BASE=<URL publica de la API> npm run build` y copiar `dist/*` a esta carpeta ANTES de construir la imagen. El contenido esta ignorado por git (salvo este README y .gitkeep).
