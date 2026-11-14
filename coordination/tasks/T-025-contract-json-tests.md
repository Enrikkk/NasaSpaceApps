---
id: T-025
title: Independent JSON contract checks for both demo outputs
status: doing
owner: arturo
branch: arturo-contract-tests
paths: app/backend/contract_tests/test_contract_json.py
depends: T-020, T-022
---

Requested by Enrique in bus #180/#181; compatible assistance authorized by Arturo.
Base: origin/t020-jaime @ 91ba395 (step B).

Use only stdlib + pytest. Do not modify app/backend/engine or either JSON; do not run Gonzalo's validate_v1_1.py.
Check both app/data/torre-pacheco.json and torre-pacheco.abierto.json:
source references; no CARM-ANUARIO/anuarios in open output; aligned climate-year/cost-factor scenarios;
effective n equals historical-year n; legal-result vocabulary; invalid text tokens and texts.check(out);
allowed block statuses. Finish with pytest exit 0 or an explicit rotation/field failure list, push and notify Enrique.

- 2026-11-14 | arturo: claimed before implementation. T-017 remains active independently, awaiting frontend package; no new agents, deploy or main merge.
