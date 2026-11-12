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
