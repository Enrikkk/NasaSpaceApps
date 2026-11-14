---
id: T-013
title: NDVI series and bare-soil months detector for the demo parcel
status: todo
owner:
branch: t013-bare-soil-ndvi
paths: app/backend/ndvi/, app/data/cache/ndvi/
depends: T-009
---
Kick off the slow downloads Sat 09:00 (AppEEARS HLS-VI/MODIS, or Sentinel-2 via CDSE). Smooth the series, threshold NDVI
to flag bare months and crop-vulnerable periods; output the `ndvi` block. Pre-compute offline; the demo reads the result.

- 2026-11-14 13:20 | plan v1 (coordination/PLAN.md): Seat (plan): enrique. Human launches AppEEARS/CDSE NOW. Fallback MODIS 250 m or labelled precomputed sample.
