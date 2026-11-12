---
name: handoff
description: End-of-work-block handoff for the Space Apps team hub. Updates the task file with progress, appends to the shared LOG, records proposed decisions, commits and pushes so other agents and teammates see the state. Use when the user says handoff, wrap up, I'm taking a break, push my progress, or before sleeping/switching tasks.
---

# /handoff

Implements AGENTS.md §4–5.

1. Summarise what was done this block from the conversation and `git diff`/`git log` on the task branch.
2. Update the task file(s) owned by this seat: status (`doing` / `review` / `done` / `blocked`), and append a timestamped note: what works, how to run it (one command), what's left, known issues.
3. Append one line to `coordination/LOG.md` (format in that file). If something blocks someone else or they need to know it, say so explicitly with `@seat`.
4. If a team-level choice was made or is needed, append it to `coordination/DECISIONS.md` as `PROPOSED` (never mark it decided yourself).
5. If a new fact every agent should know came up (data quirk, API limit, venue info), add it to the right file in `context/` or `research/`.
6. Commit (`T-NNN: handoff …`) and push the task branch; push `main` changes to coordination files too (`git switch main && git pull --rebase && git checkout <branch> -- coordination/ && commit && push`, or commit coordination files directly on main).
7. If the work is ready and runs, offer to merge into `main` per AGENTS.md §4 (pull, run, merge, push), and ask the human first.
