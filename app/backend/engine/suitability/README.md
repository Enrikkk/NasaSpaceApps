# H002 parcel suitability — Arturo handoff

Base t020-jaime57561e9; request #212–214/#221; H002 read at t01227f9430.
Only this new package and task coordination are changed. No engine integration,
API edit, JSON rebuild, network fetch at runtime, main merge or deployment.

```sh
python -m pytest app/backend/engine/suitability/tests/test_suitability.py -q
```

Public API (stdlib):

```python
from app.backend.engine.suitability import evaluar, etiqueta_ambiental
r = evaluar({'regadio': False, 'pendiente_pct': 12, 'suelo': None},
            ['lechuga_iceberg', 'haba', 'cebada'])
e = etiqueta_ambiental({'agua_m3_ha': 2800, 'suelo_desnudo_dias': 45,
                       'credito_n_kg_ha': 35, 'semaforo_legal': 'ok'})
```

`catalogo` accepts base/product IDs, dictionaries with product_id/crop_id, or an
ID->crop_id/dictionary mapping. Outputs retain original IDs. The module loads its
bundled CSV on import; evaluar and etiqueta_ambiental themselves perform no IO
and do not mutate inputs. Factor is for **score only**; do not multiply margin,
yield or success percentages. Apply exclusion before DP. Keep the engine's money
unchanged. No engine/money import is needed to run these tests.

## What is implemented, and what is deliberately unresolved

- Current irrigated lettuce/broccoli/melon/artichoke systems are excluded if and
  only if regadio is the boolean false. This is H002 catalogue policy, **not** a
  biological assertion that every possible cultivar/system needs irrigation.
- For those four crops, slope (10,20]% gives0.85, >20% gives0.65. Both cutoffs
  and score percentages are original **supuestos C**, not agronomic measurements,
  erosion modelling or legal prohibitions. Other crops have no slope penalty;
  explicit pending-rule notices prevent claiming suitability on extreme slopes.
- Haba pH6.5–9 is a published growth range from USDA Plant Guide p2. Applying
  score0.9 outside it is a separate **supuesto**. Poor-drainage evidence is
  qualitative; score0.85 and the accepted class names are **supuestos**. Neither
  fact proves impossibility outside the range. All applied rows expose
  `umbral_estado` separately from the percentage's `estado`.
- Remaining soil texture, salinity, depth, pH/drainage crop pairs remain neutral
  with a **specific missing-rule notice**, including when input exists. This is
  an evidence gap, not unlimited tolerance. We did not fabricate 8×soil response
  curves to fill the table. The CSV covers all eight crops and seven input
  dimensions (60 rows, including slope tiers); `pending` rows are not applied.
- Missing/invalid inputs (NaN/Infinity/boolean-as-number/negative values) receive
  factor1 for that component and explicit sin_dato. Unknown crops likewise stay
  neutral without implying agronomic or economic feasibility. Slope percentages
  above100 remain valid; they are not angles.
- A future salinity rule must require salinidad_metodo='ECe'; generic CE, ECw and
  EC1:5 cannot be silently equated to saturated-paste rootzone conductivity.
  Current salinity rows are all pending, so no salt factor is applied.

## Environmental label contract

Metrics are annual per hectare: agua_m3_ha, suelo_desnudo_dias (0–366),
credito_n_kg_ha, semaforo_legal (ok/falla/no_evaluable, or color equivalents).
All thresholds live in AMBIENTE_UMBRALES and are **supuestos**, not observed
impact estimates or lifecycle assessment. High (=more friendly under this
policy) requires water<=3000, bare days<=60, N credit>=30, and legal ok.
Water>=6000 or bare days>=180 or legal falla yields low. Otherwise medium.
Missing information cannot earn high; medium carries explicit missing-data
warnings and is not an assertion of moderate risk. Returned limits are copied.

## Source / rights register

| source_id | Source and verification | Rights / exact use |
|---|---|---|
| PROJECT-H002 | [Enrique H002 decision](https://github.com/Enrikkk/NasaSpaceApps/blob/27f9430/coordination/handoffs/H-002-motor-por-parcela.md), bus212–214/221 | Original project rules/percentages; no third-party text copied and no global project licence chosen. All unvalidated percentages/cutoffs marked supuesto. |
| USDA-VIFA+PROJECT-H002 | [USDA NRCS Fava Bean Plant Guide](https://plants.usda.gov/DocumentLibrary/plantguide/pdf/pg_vifa.pdf), p2 Adaptation; [USDA rights policy](https://www.usda.gov/about-usda/policies-and-links#digital-rights-and-copyright) | USDA public-domain policy permits copying most agency information with credit and exceptions for identified protected items. Only pH range and paraphrased drainage fact used, no images or copied prose; score mapping remains original supuesto. Credit: U.S. Department of Agriculture, NRCS. |
| FAO-ECOCROP (research only) | [Official service](https://www.fao.org/geospatial/data-and-tools/data-portals/ecocrop/en), [Vicia faba sheet](https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=2146) | Environmental descriptors available; service says original database discontinued around2015. Did not establish product-specific redistribution licence, so no numeric records imported. |
| FAO-SALT (research only) | [FAO drainage paper61 Annex1](https://www.fao.org/4/y4263e/y4263e0e.htm) | Distinguishes ECe, duration/crop-stage assumptions and cultivar/rootstock effects; annex reproduces third-party Maas/Grattan data. No table copied or fabricated score conversion. |
| FAO-TERMS (research only) | [Official database terms](https://www.fao.org/contact-us/terms/db-terms-of-use/en/) | CC BY4.0 default is specifically corporate statistical databases, with promotion/third-party exceptions; not assumed blanket permission for EcoCrop or old books. |

Submission owner must add the USDA credit if these rules are integrated/published;
this branch does not edit submission/ or select a licence on the team's behalf.

## Secano economics audit at 57561e9

| Crop | Canonical coste_total / rendimiento_kg_ha | Other data | Honest result |
|---|---|---|---|
| haba (dry grain) | No complete canonical cost; no canonical crop yield used by engine | ECREA2020 candidates separate secano/regadio, explicit proxy B; no automatic loader. CARM green haba is a different harvested product. | Not economically evaluable for a dryland parcel from these inputs. |
| cebada (grain) | No complete canonical cost; no canonical crop yield used by engine | ECREA2021 candidates separate secano/regadio; Eurostat national production/area/yield mixes systems, not parcel dryland yield. | Not economically evaluable without an explicit regime-compatible proxy/yield decision. |
| veza (cover) | No verified establishment cost; no cash crop yield | Seed+sowing gap remains; harvested grain/forage total cost cannot replace cover establishment. | No fabricated margin; cover benefit must not be represented as harvested revenue. |

Audited read-only: app/data/tables/crop_params.csv, cost_candidates.csv,
engine/data/official/imida_costs.csv, products.csv, eurostat_area_es.csv and
core/data.py. Loader uses crop_params, not cost_candidates. Current default
rotation CATALOG has four irrigated crops only; exclusions may leave no evaluable
economic rotation. Report no_evaluable; do not invent dryland earnings. Parcel
suitability is not a substitute for the missing economic data or local climate.
