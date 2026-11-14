# API operations — handoff to Gonzalo

Arturo, bus #204, source: API README, engine_data/README and cloudbuild at main7760056.
These commands are documentation only: Arturo has not run build, deploy, IAM,
traffic, billing or resource changes. Gonzalo remains operator.

## Prepare an immutable candidate

Record API SHA, engine JSON SHA/hash, ATOM municipality/count manifest, cache
hashes, frontend origin, image digest/tag and previous verified Cloud Run revision.
Use a clean staging context with repository-root layout. Include API, pipeline,
rules, contract adapter, pinned dependencies, minimum app/data and cache seeds.
Generated ATOM GeoJSON belongs in app/backend/api/atom_build (not in git).
Copy the approved OPEN engine JSON to app/backend/api/engine_data/engine.json
before building. The API consumes that JSON, not engine code. If it is missing or
invalid the service may fall back to DraftEngine: HTTP200 alone proves little.

## Build and rollout — Gonzalo executes

From staging root, replace reviewed SHA/tag placeholders:

```sh
gcloud builds submit . --project agrockham-nasa-2026 \
 --config app/backend/api/cloudbuild.yaml \
 --substitutions _GIT_SHA=<api-sha>,_IMAGE=europe-west1-docker.pkg.dev/agrockham-nasa-2026/agrockham/agrockham-api:<tag>
```

Cloud Build uses app/backend/api/Dockerfile and root context; deploying source at
root is not the recorded build method. Gonzalo updates the existing service to
the resulting image digest. Preserve existing environment settings and set
FRONTEND_ORIGIN only to the frontend origin supplied by Jaime. Do not blindly
replace all environment variables or create another service.

Current cost protections from README: max instances2, min0, timeout120s,
concurrency80, 1vCPU/2GiB, CPU during requests. Earlier README v1 max3/1GiB values
are historical. Keep a known good image/revision for rollback.

Before traffic, test the candidate image with AGROCKHAM_OFFLINE=1 and Docker
--network none using the existing runner/arguments documented on branch
origin/t017-offline-deploy. No new suites needed unless the candidate or concern
changes. Check health SHA/ATOM count, JSON-engine marker, rotation IDs, actual
alignment declaration, schema/invariants and relevant warnings. v4 evidence
does not validate v5. Missing frontend/fallback prevents declaring demo ready.

After rollout: /health; demo /analyze; non-reference /analyze?bloques=parcela;
/recintos with bbox <=5km; CORS preflight for the actual frontend origin. v5 should
include _meta.rotaciones_referencia; v4 does not. Save report outside git with
candidate manifest, timestamp, request count and observed latencies.

## Rollback — Gonzalo executes

Select a previously verified revision, not merely the previous tag:

```sh
gcloud run revisions list --service agrockham-api --region europe-west1 --project agrockham-nasa-2026
gcloud run services update-traffic agrockham-api --to-revisions <verified-revision>=100 --region europe-west1 --project agrockham-nasa-2026
```

Recheck expected health SHA, engine/ATOM manifest and frontend CORS. Preserve failed
candidate evidence. Rollback restores its old payload and limitations too.

## Cost and incident handling

Budget50EUR emails are alerts, not a hard cutoff. Gonzalo monitors Run/Build/Registry
costs, retains serving/rollback images, removes verified unused images, and keeps
Cloud Build bucket one-day lifecycle and max2/min0 protections.
Emergency alternatives recorded by the producer (operator chooses impact):

```sh
# Stop unauthenticated public access while preserving the service.
gcloud run services remove-iam-policy-binding agrockham-api --project agrockham-nasa-2026 --region europe-west1 --member=allUsers --role=roles/run.invoker
# Destructive alternatives, not routine rollback:
gcloud run services delete agrockham-api --project agrockham-nasa-2026 --region europe-west1
gcloud billing projects unlink agrockham-nasa-2026
```

Record decision, impact and recovery owner. Do not enable extra paid services.
SoilGrids official notice reports instability; Gonzalo #211 observed slow live
responses. Seeded cache and honest cargando degradation remain important; neither
observation is an uptime guarantee. No email notifications were created here.
