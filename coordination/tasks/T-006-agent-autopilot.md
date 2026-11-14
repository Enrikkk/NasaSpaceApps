---
id: T-006
title: Autopilot watcher: agents pick up tasks assigned to them via git, no API, no MCP server
status: review
owner: jaime
branch: main
paths: scripts/agent_watcher.py, coordination/AUTOPILOT.md, coordination/DECISIONS.md (PROPOSED only)
depends: T-001
---
Goal: a teammate's Claude Code / Codex CLI / Cursor agent wakes up on its own when another agent hands it a task,
without spending tokens on polling and without new infrastructure (Tailscale + central MCP server were considered).

Design: the task board in git stays the single source of truth (D-001). A small Python watcher per laptop does
`git fetch` every N seconds (0 tokens) and only launches `claude -p` / `codex exec` / `cursor-agent -p` when a task
file has `owner: <SEAT>`, `status: todo`, `auto: yes`. The watcher does the git work (claim, branch, commit, push,
status -> review/blocked, log line); the agent only codes.

Acceptance: `python3 scripts/agent_watcher.py --once --dry-run` lists what it would run; docs in coordination/AUTOPILOT.md.

- 2026-11-14 10:10 | jaime | done (needs team OK, D-003 PROPOSED): scripts/agent_watcher.py + coordination/AUTOPILOT.md. Tested end-to-end on a scratch clone with a fake origin: claim -> branch -> push -> review, hand-over T-099 -> T-100 (renumbered on collision, chain 1), base-branch merge, failing agent -> blocked, depends gating. Not yet tested with real claude/codex/cursor CLIs.
