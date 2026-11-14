---
id: T-014
title: Ground truth: SIAM collector + ESP32 soil-moisture node (optional wow)
status: todo
owner:
branch: t014-iot-siam-node
paths: app/iot/, app/data/cache/siam/
depends: T-009
---
SIAM hourly collector -> SQLite -> `sensores` block. ESP32 capacitive probe over MQTT if time allows; otherwise replay a
real SIAM series labelled 'historical replay'. Purpose: correct SMAP bias, local frost/heat alert, detect irrigation.

- 2026-11-14 13:20 | plan v1 (coordination/PLAN.md): Seat (plan): arturo. Priority 1: SIAM TP91 hourly/daily 20-year series -> app/data/cache/siam/ (feeds frost risk in T-012). Priority 2 (P2): ESP32 node over MQTT; else labelled 'historical replay'.
