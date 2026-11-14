# app/: the product (**Agrockham**, formerly the working name RotaSat, D-006)

Decision-support tool for **Field Shift: Adapting Farms with NASA Data**. A farmer without technical background
picks a parcel, sets priorities, and compares at least 3 crop rotations (the current one included), each with
success %, expected profit, water need, a legal traffic light and an honest "what we don't know".

Layout (created by the tasks, see `coordination/tasks/`):
`frontend/` (T-010) · `backend/pipeline/` (T-011) · `backend/engine/` (T-012) · `backend/ndvi/` (T-013) ·
`backend/rules/` (T-019) · `backend/api/` (T-024) · `iot/` (T-014) · `data/` (T-009).

Architecture (D-009, supersedes the static-only D-007): the browser (MapLibre globe) draws SIGPAC parcels; a click calls the
live API (`POST /analyze {lat, lon, recinto}`, FastAPI), which returns the contract block by block, each with its own
`_status`. The demo parcel (Torre-Pacheco 18/426/1) is preloaded as a fallback. Internet is required in the demo.

## Real vs simulated vs roadmap (keep this table true; the pitch and `submission/` copy it)

This is a 2-day hackathon. We may show a vision that is not built yet **if it is feasible and we label it as such**.
State as of Sat 14 Nov 2026, evening. Every block of the contract carries its own `_status`
(`cargando | real | precalculado | simulado`), and the UI shows the label.

| Piece | Status for the demo | Notes |
|---|---|---|
| Parcel (SIGPAC recinto, geometry, slope, area) | **Real** from the official SIGPAC download by municipality (ATOM); live OGC API access pending FEGA terms check (D-009) | FEGA's 2026 terms say no authorisation is needed; a 2023 MAPA reply says third-party access from code is not allowed, so ATOM is the safe route. Demo parcel Torre-Pacheco 18/426/1 |
| Declared crop history (FEGA) | **Real** where the pipeline reads it (T-011), else `simulado` | licence not confirmed separately |
| Climate history (NASA POWER, IMERG rain, SIAM TP91 frost) | **Real**, 19 observed years (2006-2024), cached per cell | POWER/ERA5 miss frost: frost days come from the SIAM TP91 station (not the exact field) |
| Soil (SoilGrids) | **Real**, cached per 250 m cell | |
| NDVI and bare-soil months (HLS / Sentinel-2) | **Real if T-013 lands**, else `simulado`, labelled | |
| Success % per crop | **Real calculation, simple model** (D-008, D-011) | share of the 19 historical years in which climate loss < 20 % AND margin >= 0 at that year's price, with a Wilson interval; no yield labels exist, we say so; never a yield prediction |
| Prices and breakeven | **CARM/ESAM yearbook prices under D-010**, written permission still **pending** (esam.carm.es/legal is personal, non-commercial, not open) | open twin `torre-pacheco.abierto.json` kept as fallback; re-review before the submission (Sun 21:00) |
| Costs, yields, irrigation | **Real tables** (IMIDA/MAPA, FAO-56, FAO-29), 8 crops | alcaparra is out (D-008) |
| Oversupply | **Proxy** (declared area per crop in the comarca), not emitted by the engine yet | |
| Legal traffic light (Ley 3/2020 Mar Menor, PAC) | **Rules table, articles cited, all `por_verificar`**; Mar Menor zone 1/2 **not verified** (Anexo I unread) | not legal advice; grey light outside the full-coverage area |
| "B wins X %" comparison | **Indicative** until `escenarios_meta.alineados = true` | the scenario index is not yet the same sample in every rotation (D-011) |
| 2050 scenario | **Simulated**: climate deltas applied to thresholds; real NEX-GDDP-CMIP6 is roadmap | |
| IoT soil node | **Optional**: live pot demo or labelled historical SIAM replay | |
| Saved parcels | **Real**, in the browser (`localStorage`), no accounts | |
| Learning loop / partner plan (farmer shares harvest results for a discount) | **Roadmap only**, may be shown as a labelled mock (business slide) | |
| Other regions | **Roadmap**: basic/indicative level (D-009), full coverage only in Campo de Cartagena | the pipeline is parameterised by lat/lon |

## Contract

One JSON per parcel, v1.1. Everything lives in `app/data/`; read `app/data/contract/README.md` first
(fields, who produces each block, freeze rules).

| File | What |
|---|---|
| `app/data/contract.schema.json` | JSON Schema 2020-12. Required = P0, the rest optional, open `additionalProperties` (after freezing, fields are only added) |
| `app/data/torre-pacheco.contract.example.json` | Example that conforms to the schema. **MOCK**: all `simulado`, illustrative numbers, fixed seed. Code the UI against it |
| `app/data/contract/validate_contract.py` | Schema + invariants + `--selftest`; run it before every contract change |
| `app/data/contract/adapt_enrique.py` | Engine output (`app/data/torre-pacheco.json`) -> contract v1.1 |

Run (jsonschema in a venv, never in the system Python):

```bash
python3 -m venv /tmp/venv-contract && /tmp/venv-contract/bin/pip install jsonschema
/tmp/venv-contract/bin/python app/data/contract/validate_contract.py app/data/torre-pacheco.contract.example.json --selftest
```

Live: the API (`app/backend/api/`, D-009) serves this same contract at `POST /analyze`, block by block with `_status`.
`app/data/torre-pacheco.mock.json` is the old illustrative mock (pre-v1.1) and `app/data/torre-pacheco.json` is the engine's
own output; both are being replaced by the contract format, and the example above is the reference until the API serves it.
