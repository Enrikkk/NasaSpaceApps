"""Pipeline de datos por parcela de Agrockham (T-011).

Subpaquetes:
  atom         SIGPAC (recintos) desde el ATOM del FEGA -> bloque `parcela` del contrato.
  clima_suelo  NASA POWER / IMERG / Open-Meteo / SoilGrids -> bloques `clima` y `suelo` del contrato.

Ejecutar siempre desde la raiz del repo (`python -m app.backend.pipeline.<...>`). Ver README.md.
"""
