# app/: the product (working name: **RotaSat**)

Decision-support tool for **Field Shift: Adapting Farms with NASA Data**. A farmer without technical background
picks a parcel, sets priorities, and compares at least 3 crop rotations (the current one included), each with
success %, expected profit, water need, a legal traffic light and an honest "what we don't know".

Layout (created by the tasks, see `coordination/tasks/`):
`frontend/` (T-010) · `backend/pipeline/` (T-011) · `backend/engine/` (T-012) · `backend/ndvi/` (T-013) · `iot/` (T-014) · `data/` (T-009).

## Real vs simulated vs roadmap (keep this table true; the pitch and `submission/` copy it)

This is a 2-day hackathon. We may show a vision that is not built yet **if it is feasible and we label it as such**.

| Piece | Status for the demo | Notes |
|---|---|---|
| Parcel data (SIGPAC, declared crop FEGA, nitrate zone) | **Real**, demo parcel only | Torre-Pacheco 18/426/1, cached |
| Climate history (NASA POWER, IMERG rain, frost/heat days) | **Real**, demo parcel, cached | |
| Soil (SoilGrids) | **Real**, cached | |
| NDVI and bare-soil months (HLS / Sentinel-2) | **Real if T-013 lands**, else pre-computed sample labelled as such | |
| Success % per crop | **Real calculation, simple model** | share of 20 years where climate thresholds are not exceeded x price covers breakeven; no yield labels exist, we say so |
| Prices and breakeven | **Hand-entered** for 8-10 crops from MAPA/ESAM, with min/max | not live |
| Oversupply | **Proxy**: declared area per crop in the comarca | |
| Legal traffic light (Ley 3/2020 Mar Menor, PAC) | **Rules table**, articles cited | not legal advice |
| 2050 scenario | **Simulated**: climate deltas applied to thresholds; real NEX-GDDP-CMIP6 is roadmap | |
| IoT soil node | **Optional**: live pot demo or labelled historical SIAM replay | |
| Learning loop (farmer shares harvest results for a discount) | **Roadmap only** (business slide) | |
| Other parcels / other regions | **Roadmap**; the pipeline is parameterised by lat/lon | |

## Contract

One JSON per parcel: `app/data/<parcel>.json`. Example: `app/data/torre-pacheco.mock.json`
(**illustrative numbers, not measured**, replaced by real pipeline output as T-011/T-012/T-013 land).
