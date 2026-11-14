# T017: next-candidate LiveEngine gate (preparation only)

Read-only sources: integracion3c3abb4 (API/engine/dev_app.sh), main1e046b3
(Dockerfile.engine). No producer suites/builds/requests repeated here. Earlier
JSON-precomputed smoke and frontend gate are not LiveEngine evidence.

## Confirmed inputs

- Repository-root context containing engine, API/narrativa, parcel_input,
  contract adapter, products/official snapshots, mapa_prices and mock/reference
  inputs; generated ATOM package and pipeline cache seed with hashes.
- ENGINE_MODE=vivo and ENGINE_PRECIOS=abierto. For offline test explicitly
  AGROCKHAM_OFFLINE=1 and container --network none; do not infer network isolation
  from LiveEngine itself. ENGINE_JSON is optional fallback, never proof of live.
- scripts/dev_app.sh defaults to API127.0.0.1:8080 and frontend origin127.0.0.1:5173.
  It can generate a66-recinto sample when full ATOM is missing, which must be
  labelled sample, not170265municipal coverage. Do not launch it just for review.
- ParcelInput: ATOM area/regadio/pendiente, SoilGrids texture/pH and real known
  fields; salinity/depth/drainage are null, never invented. Climate remains one
  SIAM Torre-Pacheco station, not per-parcel weather. Open-price proxy limits apply.

## Assertions for a newly assigned candidate

Record candidate API+engine SHA, image digest, input hashes, env mode, sample/full
ATOM scope and producer evidence identity. Require all of:

1. /health expected version and recorded ATOM count/municipalities.
2. POST/analyze result has `_meta.rotaciones_referencia.por_parcela=true` and
   applies to the requested parcel; expected live motor name is supplemental.
   `_meta.motor` uses the configured class name and alone does NOT detect a run
   falling back to JSON. Inspect fallback warnings and reference metadata.
3. Source-backed ParcelInput fields, per-parcel idoneidad and explicit unknowns;
   no substitution of missing salinity/depth/drainage or dryland economics.
4. Representative differing parcel inputs exercise live selection when needed;
   do not demand arbitrary different margins when evidence/data cannot support it.
   Dryland with no evaluable crop must remain no_evaluable, not a fake success.
5. Contract schema/invariants and recorded alignment as declared by this candidate.
6. Open-price/no-restricted-file image manifest checked independently of flags:
   an environment flag does not remove embedded data or make SIAM licensed.
7. /narrativa is optional and separate from /analyze. Without Ollama/valid cache,
   deterministic template fallback is acceptable and accurately labelled. Do not
   install/run an LLM or contact a backend for a packaging check.

Existing scripts/t017_smoke.py explicitly requires JSON and checks the JSON motor;
it is not to be relabelled as LiveEngine smoke. A future extension/new runner needs
an agreed candidate and gap not already covered by Gonzalo's producer evidence.
Desktop's frontend gate remains unchanged and its tests are not repeated.

## Exact dependencies / pending confirmation

- Gonzalo provides tested candidate SHA/context manifest and artifact showing
  actual live marker/no fallback, open-mode figures approved by Enrique, and
  absence of restricted CSV in final image. His existing green no-network run is
  producer evidence, not receiver execution. main Dockerfile alone cannot supply
  a buildable combined API/engine tree; use the confirmed integration source.
- Read-only concern sent to Gonzalo: Dockerfile.engine comment claims CARM CSV
  exclusion, but main1e046b3 ignore file includes engine broadly and no explicit
  restricted-file exclusion was observed. Was the actual staging context cleaned?
  Confirm from the image/manifest; do not infer absence from ENGINE_PRECIOS.
- Jaime supplies API client ownership/env/base, corrected worker asset and exact
  frontend origin/fallback; current visual-only changes do not provide UI→API.
- Desktop supplies nonduplicated new-candidate build/browser evidence. Only a new
  assigned candidate or concrete doubt justifies repeating affected checks.
- Gonzalo owns any image build/deploy/GCP; no cloud changes by this receiver.

## Follow-up #270/#281/#285/#289 — candidate7403fe6

Gonzalo fixed the restricted-CSV packaging issue in mainb74ed52: exclusions after
the allowlist plus RUN cleanup/assertion. Read-only diff checked by Arturo;
producer reports image built from a context containing CSV has zero restricted
files/test directories. No duplicate image build here. Public v6d2eb748 remains
JSON; Arturo's bounded7-request smoke passed10checks (historyFEGA real0..N,
endpoints, attribution,CORSlocalhost/127 and rejection of another origin).
Artifacts outsidegit: /tmp/agrockham-t017-v6-smoke/report.json.

New exact local candidate integracion7403fe6: dev_app.sh API running on18080,
66-feature sample, ENGINE_MODE=vivo, open prices, AGROCKHAM_OFFLINE=1; no assertion
of container network isolation. Three separate sampled recintos return live
por_parcela=true; dryland example honestly no_evaluable. Outside coverage returns
parcela cargando/noid but live metadata still applies=true and no_evaluable null;
semantic concern sent Enrique293, not silently repaired by this task.

New frontend build70modulesexit0 using matching-lock existing dependencies;
worker asset referenced by emitted bundle remains missing, gateexit1. Jaime288
owns the fix. Dev frontend5173 points to API18080 for Desktop's real-browserQA;
this receiver's CUA has no browser, Desktop's CUA does. Handoff283 toJaime was
cancelled287 to avoid duplicateQA. Local environment/coordinates handed toDesktop
in outputs/e2e-entorno.md; rawresponses/gate reports stay outsidegit.

Deployment sequence agreed289: Jaime/Enrique resolve frontend/App union;
Enrique approves open-price figures (lettuce currently under review, not tested
as correct); Gonzalo builds/deploys exact approved image and supplies digest,
revision and live-marker evidence; Arturo/Desktop validate published URL.
Gonzalo owns API/image/GCP, Arturo QA/scripts/deploydocs. Same-origin frontend
serving is available on mainf1b2ffa but is not proof of deployment/integration.
No main merge by agents; no new project/billing/spend expansion authorised.

## Desktop browser evidence7403fe6 — recovery completed

Desktop reports two covered parcels verified in real browser (18/429/1 and
18/426/1): selection, parcel panel and full rotations. Setting priorities to
100profit/0others moves Máximo margen first. Outside sample coverage (18/440/1)
shows a zone-estimate warning. These are two covered UI parcels, not three.
Receiver independently exercised three API parcels; do not conflate coverage.

Network-error test was coordinated on this exact candidate: receiver stopped only
its uvicorn PID108862, confirmed TCP18080 closed; Desktop saw visible error and
Reintentar. On explicit Desktop request the same API was restarted asPID110872,
health200/version7403fe6 confirmed. Desktop then verified Reintentar restores
429/1 panel and full rotations. Frontend remained running on5173 throughout.
This is recovery evidence, not proof of a complete offline preloaded fallback.

Desktop evidence files: outputs/e2e-integracion.md, e2e-error-red.jpg,
e2e-recuperacion.jpg in its workspace. Receiver records the supplied observations;
it has not executed browser automation or copied full screenshots into git.
Minor contradictory error copy sentJaime298 (claims parcel data exist when fast
parcel request also fails). Team notified byDesktop297.

Next QA targets an agreed combined candidate containing worker fix, the no-recinto
metadata correction62746d4, and Enrique's approved open-price figures. No duplicate
producer suite, no claim of three UI parcels or final demo, and no deployment of
the currently blocked candidate. Servers preserved for Desktop as requested.

## Public v7 / integration3c45f63 delta

Producer LOG1f6838f records API-only v7a082305, revision00009-pkq, live engine,
no frontend/fonts, open-price lettuce without a price (not evaluable), alignment
true, no-network image evidence and v6revision00008-vcv retained for rollback.
Desktop independently supplied health200/a082305/170265recintos7municipalities.
Neither observation means a frontend is deployed or figures have human approval.

Exact next combined source candidate fromEnrique309: integracion3c45f63.
Compared with7403fe6 frontend changes only error copy in ParcelPanel; no worker
fix. Root/local QA servers were not changed automatically. Worker emission and
Brunson permission/licensed fallback remain publication dependencies; Jaime311
asked for explicit ownership/solution, not assumed an edit authorisation.

Missing public no-recinto evidence was checked once byArturo: POST/analyze with
bloques=parcela,rotaciones at40.4168/-3.7038 returned200 in2.512s, parcela cargando,
sin_cobertura=true,idnull, reference.aplica=false, no true por_parcela and the
reference warning. Three affected assertions pass. Rawreport outsidegit:
/tmp/agrockham-t017-v7-sin-recinto/report.json. No producer smoke/suite repeated.
The configured class name still says LiveEngine; reference metadata correctly
prevents treating it as a calculation for an identified parcel.

Human review of proxy figures remains distinct from agent integration/build/test
results. Do not treat #309 as approval of economic accuracy or fonts. Next gate
and browser delta need an agreed corrected candidate, not another unchanged build.
