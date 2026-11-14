---
id: T-014
title: Ground truth: SIAM collector + ESP32 soil-moisture node (optional wow)
status: todo
owner:
branch: t014-iot-siam-node
paths: app/iot/
depends: T-009
---
SIAM hourly collector -> SQLite -> `sensores` block. ESP32 capacitive probe over MQTT if time allows; otherwise replay a
real SIAM series labelled 'historical replay'. Purpose: correct SMAP bias, local frost/heat alert, detect irrigation.
