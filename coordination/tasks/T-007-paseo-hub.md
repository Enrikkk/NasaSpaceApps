---
id: T-007
title: Paseo orchestrator over Tailscale (jaime's Mac = hub, one daemon per laptop)
status: doing
owner: jaime
branch: main
paths: coordination/PASEO.md, scripts/paseo_join.sh, AGENTS.md (section 7), coordination/DECISIONS.md, coordination/AUTOPILOT.md
depends: T-006
---
Team wants Paseo (paseo.sh) as the live orchestrator so agents don't duplicate work, with jaime's Mac as the hub over
Tailscale. Agents run on the daemon's machine with that machine's CLI logins, so: one Paseo daemon per laptop (own
subscription), listening on its Tailscale IP with a password; the hub registers every laptop as a host and its
orchestrator agent launches work on them. Git (coordination/tasks, LOG) stays the durable record; T-006 watcher = fallback.

Acceptance: coordination/PASEO.md runbook; scripts/paseo_join.sh joins a laptop in one command; hub reaches itself via
its Tailscale IP; D-004 recorded.
