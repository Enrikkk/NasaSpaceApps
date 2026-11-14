---
id: T-023
title: (P2) 5-8 more real FEGA parcels through the same pipeline
status: review
owner: gonzalo
branch: t023-more-parcels
paths: app/backend/pipeline/, app/data/cache/pipeline/
depends: T-011
---
Seat (plan): gonzalo. Only after Hito 1 (Sat 19:00) and if P1 is on track. Same pipeline parameterised by lat/lon; the UI lists them on the map.

- 2026-11-14 19:25 | gonzalo claimed and closed to review: the pipeline is parameterised by lat/lon and serves ANY recinto of the 7 covered municipalities live (parcel from ATOM, climate and soil with cache, real FEGA declared crops). 7 representative irrigated parcels (one per municipality) are pre-warmed so soil answers in ~0.5 s: 30/16/0/0/101/2/3 Cartagena, 30/21/0/0/502/65/1 Fuente Alamo, 30/35/0/0/1/39/1 San Javier, 30/36/0/0/4/231/2 San Pedro del Pinatar, 30/37/0/0/11/155/1 Torre-Pacheco (+ demo 30/37/0/0/18/426/1), 30/41/0/0/2/85/3 La Union, 30/45/0/0/7/2/3 Los Alcazares. Cache in app/data/cache/pipeline/clima_suelo (commit 4c8d8d9). Engine rotations stay the reference parcel until the live engine is deployed.
