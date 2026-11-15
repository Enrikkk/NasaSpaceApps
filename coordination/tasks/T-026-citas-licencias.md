---
id: T-026
title: Verify submission data licences against official sources
status: done
owner: arturo
branch: t026-citas-licencias
paths: submission/data-citations.md, research/t026-license-review.md, coordination/deploy/OPS.md
depends: T-015
---
Gonzalo handoff bus #204. Main scope: official GIBS acknowledgement, product citations
POWER/IMERG/HLS/MODIS/SRTM, SoilGrids terms, PNOA year and SIAM licence.
Each item gets an official URL and concise evidence (<=25 words), or an explicit
unresolved reason. No invented licence or product version. No API edits/deploy.
Optional public smoke/runbook require separate recorded scope before implementation.

- 2026-11-14 Europe/Madrid: claimed before edits; base main 7760056.

- 2026-11-14 Europe/Madrid: principal delivered for review. Official source links and concise evidence for every enumerated item; POWER cache version/date recovered. Exact upstream IMERG collection and personalised daily SIAM permission remain unresolved with specific reasons. Candidate satellite product citations do not claim actual use. Table structure and <=25-word evidence checked; no suites repeated.

- 2026-11-14: optional #204 operational runbook scope claimed: coordination/deploy/OPS.md only, from API README/cloudbuild. Commands documented for Gonzalo, not executed. Public smoke artifacts stay outside git.

- 2026-11-14: #211 producer clarification incorporated (IMERG partial, SoilGrids observed slow). Optional OPS guide prepared, commands not executed. Public v4 smoke report outside git; no suites repeated. Main acceptance met including explicit unresolved source scope.
