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
