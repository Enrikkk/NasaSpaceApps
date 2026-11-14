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
