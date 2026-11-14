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

## Prices (T-018 part 1, `price.py`)
Decision 2026-11-14 (Enrique): no ML price regressor. Walk-forward backtest on Eurostat 2000-2024 (predict each year
from earlier years only): gradient boosting on 3 lags lost to the plain median in 5/6 crops (+18..+42 % MAE) and
tied on lettuce. The engine keeps the real years as scenarios and re-centres them on the trend line only when the
trend beats the median by >= 20 % (today: lettuce only, national real price 0.59 -> 0.32 EUR/kg from 2000-04 to 2020-24).

## Products by type and Murcia prices (`market.py`, decisions Enrique 2026-11-14)
- `data/official/products.csv`: sellable types (lechuga_iceberg / little_gem / romana, melon_piel_de_sapo / galia /
  cantaloup, brocoli, alcachofa, limon_fino / verna, haba, cebada). Agronomy from the base crop; economics from the
  type's own IMIDA rows (`crop_id` = product_id in imida_costs.csv), or a flagged fallback (`cost_product`).
- `data/official/carm_precios_mensuales.csv` (`sources/carm.py`): 4,261 monthly CARM yearbook quotes 2002-2023 by
  variety/quality, orientative. Default price tier: 1 CARM type -> 2 CARM crop -> 3 Eurostat national; the price of a
  cycle is the mean of the quotes in its harvest months, deflated with HICP. Quotes > 5x off the median are dropped.
- Quantities: net kg = coste_total / coste_unitario; pieces = coste_total / coste_unitario_ud (IMIDA).
- Farmer's own price: every year exports `cantidad_ha`, `coste_eur_ha`, `coste_recoleccion_eur_ha`, `clima_malo`,
  `canales{}`; the UI recomputes margin = cantidad x price - coste with the options in `precio.opciones_usuario`
  (oficial, canal, fijo, ajuste %, recolección, mis_anios). Years without a price are excluded from the success count.

## Decision layer (T-020, `app/backend/engine/decision/` + `build.py`)

```
python3 -m app.backend.engine.build torre-pacheco             # app/data/torre-pacheco.json (OPEN data only, publishable)
python3 -m app.backend.engine.build torre-pacheco --interno   # app/data/torre-pacheco.interno.json (CARM prices, git-ignored, never publish)
python3 -m pytest -q app/backend/engine
```
- Cycle = product at a sowing date (base date or +15 days; never earlier until frost thresholds are validated).
  Year option = non-overlapping cycles (14 days between), optional winter veza cover. Rotation = 3 year options (DP).
- DP: V_t(o) = score(o) + max V_{t+1}(o') with `rules.allowed(last(o), first(o'))` (different family, never two group-1 crops in a row).
  Strategies S1 max expected margin, S2 soil+water, S3 low risk (S2/S3 require margin >= 0); S0 = melon, fallow, lettuce.
- Criteria 0-1 across the exported rotations (1 = best in all four). 200 shared scenario draws (paired climate+price year per
  plan-year, cost x U(0.85,1.15)). Variants: lluvia -30/-15/+10, temp +1/+2, 2050 (deltas of the mock, simulated).
- `rules.py` is PROVISIONAL (T-019 will own the table). Open-data run: lettuce has no open price -> the current rotation is
  "no evaluable" in money (by design, see the lettuce note in `evaluate.py` `kg_fallback`).
