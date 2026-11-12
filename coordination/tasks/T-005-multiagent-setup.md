---
id: T-005
title: Set up the live multi-agent coordination add-on (if any) from research/
status: todo
owner:
branch: main
paths: AGENTS.md, .mcp.json, .claude/settings.json
depends: T-001
---
Already done locally (2026-11-10): SessionStart + ownership hooks in .claude/settings.json, AGENTS.md §7–8.
Left to do once the repo is on GitHub (T-001) and the challenge is picked (T-003):
1. Fill `.claude/ownership.json` with each seat's folders.
2. Each person: `export SEAT=<seat>` in ~/.bashrc, clone, run `claude`, approve project hooks.
3. Smoke test together (5 min): agent lists the board; then ask it to edit another seat's file, which must be BLOCKED.
4. Gemini CLI users: GEMINI.md symlinks AGENTS.md. Cursor users: add "read AGENTS.md first" to Cursor rules.
Optional stretch, only if everything else works by Thursday: MCP Agent Mail (see research file), untested.
