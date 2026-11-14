# Engine core (T-012): submodels A-D over 19 real years

```sh
python3 -m app.backend.engine.core.evaluate [base_year]      # table for the demo crops, money in euros of base_year (default 2025)
python3 -m pytest app/backend/engine/core/tests -q           # 10 tests
```

- `data.py`: loads crop params (team table `app/data/tables/crop_params.csv` if present, else `engine/data/official/`),
  SIAM TP91 daily climate (POWER only fills station gaps, bias-corrected), Eurostat prices, Spain HICP.
- `submodels.py`: A aptitude, B graded frost/heat damage, C FAO-56 water and FAO-29 salt, D reference yield.
  `ASSUMPTIONS` lists every unsourced design value; each is exported as `supuestos`.
- `evaluate.py`: one scenario per historical cycle, paired with the price of its harvest year (D-008 PROPOSED).
  `exito_pct` = 1 - k/n, Wilson 95 %; `margen_eur_ha` P10/P50/P90/mean/CVaR80; `agua_m3_ha` P10/P50/P90.
- Missing parameter = hazard/margin not evaluated and listed in `huecos`; if nothing was tested, `exito_pct.valor` is null.

Climate-threshold params read from the tables (long format): `frost_t0`, `frost_t100`, `heat_t0`, `heat_t100` (degC:
damage starts at t0, total at t100, linear in between) and optional `frost_window` / `heat_window`
(`ini`, `dev`, `mid`, `late` joined with `+`, or `all`; default `all`). Frost uses the station's absolute daily minimum.
