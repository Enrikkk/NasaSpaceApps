# Team decisions (append only)

Only humans decide. Agents may append entries marked `PROPOSED`; a human changes nothing above, they append
`ACCEPTED D-NNN` / `REJECTED D-NNN` as a new line.

Format:
```
## D-NNN | YYYY-MM-DD | <decision> | decided by: <seats>
Why: ...
Rejected alternatives: ...
```

## D-001 | 2026-11-10 | Use this repo as the single hub; git is the coordination layer (AGENTS.md) | decided by: enrique
Why: works offline / on bad venue Wi-Fi, every agent tool reads files, no extra accounts.
Rejected alternatives: none yet. See research/multi-agent-collaboration.md for live-coordination add-ons.

## D-002 | open | Which challenge we take | decided by: (team, before Sat 09:00)
See brainstorm/challenge-analysis.md and brainstorm/shortlist.md.

## D-003 | 2026-11-14 | PROPOSED: opt-in autopilot (`auto: yes` tasks run by scripts/agent_watcher.py), git as the bus, no Tailscale/MCP server | proposed by: jaime (agent)
Why: lets each laptop's agent (Claude Code / Codex / Cursor, flat subscriptions, 0 API spend) pick up tasks handed to its seat and hand follow-ups to others, without a second task board or a host laptop that can die. Polling is `git fetch`, 0 tokens; guards: 3 runs/h, 40 min timeout, chain <= 5. Humans still merge into main. Details: coordination/AUTOPILOT.md.
Rejected alternatives: Tailscale + central MCP task server (duplicate source of truth, single point of failure, ~1 h setup on Saturday).

## D-004 | 2026-11-14 | Live orchestration with Paseo over Tailscale, jaime's Mac as hub; supersedes D-001 for live coordination (git remains the durable record and fallback) | decided by: jaime (for the team)
Why: avoid duplicate work by having one orchestrator start and follow every agent live, while each laptop runs its own daemon with its own subscription (0 API spend). Paseo agents run on the daemon's machine, so the hub dispatches to each laptop's daemon over Tailscale (`scripts/paseo_team.sh`) instead of running everyone's agents itself. Token rules (one planner, free `paseo wait`, right-sized models, one-line RESULT) in coordination/PASEO.md.
Rejected alternatives: git-only coordination (D-001, no live view); all agents on the hub (would bill only jaime's account or need shared logins); D-003 watcher as the primary path (kept as the offline fallback).
D-003: superseded by D-004 (scripts/agent_watcher.py stays as the fallback when the hub is down).

## D-002 | 2026-11-14 | PROPOSED: take Field Shift: Adapting Farms with NASA Data; product = rotation comparator that maximises parcel profitability for non-technical farmers, region Murcia, demo parcel Torre-Pacheco 18/426/1 | proposed by: gonzalo (agent)
Why: team whiteboard (brainstorm/pizarra-2026-11-14.md) and field-shift-plan.md already converge here; 4 Murcia teams share the challenge, so differentiation is profitability + legal traffic light + honest uncertainty.
Rejected alternatives: see brainstorm/shortlist.md.

## D-005 | 2026-11-14 | PROPOSED: hackathon scope: one real end-to-end parcel, rest simulated or roadmap, always labelled | proposed by: gonzalo (agent)
Why: 2 days. We may "sell a bit of vision" if it is feasible and honest. The table in app/README.md says what is real, simulated or roadmap; the pitch and submission copy it. "Success %" is defined as climate-threshold exceedance over 20 years x price >= breakeven, not a yield prediction (no open yield labels exist).
Rejected alternatives: building a general multi-region system; claiming predictive accuracy we cannot validate.

ACCEPTED D-002 | 2026-11-14 | jaime (instructed his agent in chat; the team chose Field Shift on 13 Nov, region Murcia)
ACCEPTED D-002 | 2026-11-14 | Challenge 06 Field Shift: Adapting Farms with NASA Data | decided by: enrique (for the team, in chat)
Why: team choice. Data brainstorm in brainstorm/field-shift-data.md; prior-art caveats in research/prior-art-2026.md (4 Murcia teams on this challenge as of 10 Nov).

## D-006 | 2026-11-14 | Product name: **Agrockham** (Agro + Ockham's razor); replaces the working name RotaSat. Roles: jaime UI+pitch, gonzalo backend, enrique ML/engine, arturo networks/IoT | decided by: jaime (in chat)
Why: the whiteboard's "navaja de Ockham" principle is the product's rhetoric: the simplest tool that works for a non-technical farmer. Roles mapped from each person's skills; folders in .claude/ownership.json.

## D-007 | 2026-11-14 | PROPOSED: architecture and plan in coordination/PLAN.md: offline Python pipeline + engine precompute one contract JSON per parcel; static React/Vite/MapLibre UI does the weighting and "B wins X %" in the browser; no server in the demo; contract v1 frozen Sat 14:30 (add-only after); P0/P1/P2 scope and cut order; Hito 1 Sat 19:00, freeze Sun 12:00, submit Sun 21:00 | proposed by: jaime (agent)
Why: nothing depends on venue Wi-Fi, sliders respond instantly, one fewer moving part to debug at 3 a.m. FastAPI and the LLM narrator stay optional.
Rejected alternatives: live FastAPI backend for the demo (extra failure point, needs hosting); LLM computing scores (breaks "the engine computes, AI only explains").

## D-008 | 2026-11-14 | PROPOSED (amends D-005's "success %"): success % = share of the 20 historical years in which BOTH climate loss < 20 % (graded damage in the crop's sensitive window) AND margin >= 0 at that same year's real price; shown with a Wilson/Jeffreys interval, never as a yield prediction. Demo rotation alt-b "cebada, vezas, alcaparra" becomes "cebada -> veza -> cebada" (alcaparra has no cost/price/water/salinity source) | proposed by: enrique (decided in chat, needs team ACCEPT)
Why: multiplying P(climate ok) x P(price >= breakeven) assumes independence, which is false (frost years tend to raise prices); counting jointly over the same paired climate+price years needs no assumption. With n = 20, 0 failures still leaves a 12-16 % upper bound, so the interval is mandatory. Details: research/predictive-model-research.md (section "La formula de la pizarra...").
Rejected alternatives: keep the D-005 product; climate-only success % (a crop could show 90 % and lose money); keep alcaparra as "illustrative" (unsourced numbers on screen).


## D-009 | 2026-11-14 | PROPOSED (amends D-007): backend vivo (FastAPI en Cloud Run, creditos GCP) en vez de demo 100 % estatica. El navegador (globo MapLibre) dibuja recintos SIGPAC y, al hacer clic, llama a POST /analyze {lat, lon, recinto} que devuelve el contrato por bloques (cada bloque con _status: cargando | real | precalculado | simulado). Cache por celda (POWER 0,5 grados, SoilGrids 250 m). Se exige internet en la demo. Parcelas guardadas en localStorage, sin cuentas. Parcela demo precargada como respaldo. Cobertura completa en el Campo de Cartagena (por municipio); resto de Espana en nivel basico/indicativo | decided by: gonzalo (en chat con su agente), needs team ACCEPT (Jaime, plan en espera)
Why: el flujo "busco mi parcela, hago clic, se calcula" no cabe en un JSON precalculado por parcela. Detalle, pruebas y reparto: coordination/briefs/gonzalo-2026-11-14-backend-vivo-globo.md.
Rejected alternatives: demo solo estatica (no permite clic libre); cuentas reales en SQLite (gonzalo: no hace falta); modo offline (gonzalo: se requiere internet).
Open risk: licencia SIGPAC, el FEGA podria no permitir acceso desde codigo a su API; alternativa: descarga oficial ATOM por municipio.
ACCEPTED D-009 | 2026-11-14 | jaime (in chat with his agent): live backend (FastAPI on Cloud Run) + SIGPAC globe; amends D-007. Verify FEGA terms for programmatic SIGPAC access before depending on it; demo parcel stays preloaded as fallback.

## D-010 | 2026-11-14 | ACCEPTED (enrique decided; gonzalo acknowledged in chat; jaime and arturo have not confirmed yet): the published `app/data/torre-pacheco.json` USES CARM/ESAM prices although written permission is still pending. The licence risk is assumed knowingly | decided by: enrique, acknowledged by: gonzalo
What the source allows: esam.carm.es/legal permits reproduction citing the origin, but only personal non-commercial use and no modification, so it is NOT an open licence.
Why: without CARM prices the current rotation (melon, barbecho, lechuga) is not evaluable with open data, so the comparator has no baseline ("B wins X %" needs it).
Conditions agreed: cite "CARM-ANUARIO" in the card and in submission/data-citations.md and state "permiso pendiente"; keep the open twin `torre-pacheco.abierto.json` so the team can switch back; research/precios-abiertos.md searches for open price sources.
Known conflict: AGENTS.md section 6 (the submission form attests that every external resource is listed and no copyrighted material is used without permission); this is a team-wide attestation, not only enrique's risk.
Open, NOT decided: before filing the submission (Sun 21:00) the team must re-review this. A fallback is available at any time (switch to the open twin or to an open price source). No permission request by email will be sent (decided by gonzalo: nobody answers on Saturday).
