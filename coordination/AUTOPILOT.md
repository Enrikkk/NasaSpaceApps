# Autopilot: agents that hand tasks to each other across laptops (T-006)

> **Since D-004 (2026-11-14) this is the FALLBACK.** The primary live layer is Paseo over Tailscale, with jaime's
> Mac as the hub: see `coordination/PASEO.md`. Use this watcher when the hub or Tailscale is down.

**What it is.** `scripts/agent_watcher.py` runs on each laptop that wants an unattended agent. Every 60 s it does
`git fetch` (costs 0 tokens) and looks at the task board on `origin/main`. Only when a task is handed to its
seat does it launch that laptop's agent CLI headless, on the person's flat subscription (Claude Pro, ChatGPT
Plus, Cursor Pro). No API keys, no Tailscale, no central MCP server: **git is the message bus** (D-001), so it
works across any network, including the venue Wi-Fi with client isolation, and nothing breaks if one laptop dies.

## The contract (one extra field)

A task is picked up automatically when its front matter has all three:

```
owner: <seat>     # who should do it
status: todo
auto: yes         # opt-in. Without it, the task is for the human.
```

Optional fields the watcher understands:

| field | meaning |
|---|---|
| `base: <branch>` | start the work from that branch (for example, the backend branch the frontend needs). Main is merged in on top. |
| `depends: T-003, T-004` | wait until those are `review` or `done` |
| `chain: N` | set by the watcher. Each agent-to-agent hand-over adds 1; above 5 it stops and waits for a human (ping-pong guard) |

## What happens when a task is picked up

1. **Claim on main**: `status: doing` plus `branch`, pushed. The push is the lock (AGENTS.md §3).
2. Branch `tNNN-slug` in a **private worktree** `../NasaSpaceApps-autopilot`. Your own checkout is never touched.
3. Agent runs headless with a fixed prompt: read AGENTS.md and the task, stay inside `paths`, don't run git,
   hand over follow-up work by creating task files for other seats, and end with
   `AUTOPILOT: done | ...` or `AUTOPILOT: blocked | ...` in the task file.
4. The watcher commits and pushes the branch, then on main sets the task to `review` or `blocked`, publishes the
   new tasks for other seats (renumbering on collision), and appends a LOG line. You get a desktop notification.
5. **Humans review and merge `review` branches into main.** The watcher never merges into main.

## Run it (each person, in a spare terminal)

```bash
export SEAT=jaime                                     # your seat from context/team.md
python3 scripts/agent_watcher.py --once --dry-run     # shows what it would run, changes nothing
python3 scripts/agent_watcher.py --agent claude       # Claude Code (needs `claude` CLI on PATH, logged in)
python3 scripts/agent_watcher.py --agent codex        # Codex CLI (`codex exec --full-auto`)
python3 scripts/agent_watcher.py --agent cursor       # Cursor CLI (`cursor-agent -p --force`)
python3 scripts/agent_watcher.py --agent-cmd 'claude -p {prompt} --model sonnet --permission-mode acceptEdits'
```

Agent output goes to `.git/autopilot-logs/T-NNN-<time>.log`. Follow it with `tail -f`.

**Quota guards (defaults):** at most 3 agent runs per hour (`--max-runs-per-hour`), each killed after 40 min
(`--timeout-min`). Polling never calls the agent. Only one watcher per seat per laptop (lock file).

## Handing work to a teammate's agent

Ask your own agent (or write by hand) a task file such as:

```
---
id: T-012
title: Map view shows the parcel rotation from /api/rotation
status: todo
owner: ana
auto: yes
branch:
base: t011-rotation-endpoint
paths: app/frontend/
depends: T-011
---
Acceptance: `npm run dev`, open /parcel/demo, see 2017-2024 crops as a timeline. API shape in app/backend/README.md.
```

Push it to main. Ana's watcher starts within a minute.

## Safety notes (read before enabling)

- The agent runs **without asking you**. Claude gets `acceptEdits` plus an allow-list (python/node/npm, read-only
  git) and the ownership hook (`$SEAT`) still applies. Codex runs in its `workspace-write` sandbox. Cursor `--force`
  allows any shell command, so give Cursor seats tight `paths`.
- Task text written by teammates becomes the agent's instructions. Only teammates can push to this private
  repo. Keep it that way.
- Only set `auto: yes` for tasks whose acceptance criteria are concrete. Vague tasks burn quota and come back `blocked`.
- Stop: Ctrl-C. Pause without stopping: set your tasks to `auto: no`.

## Why not Tailscale and a central MCP task server?

That was considered (2026-11-14). It would have been a second task board next to `coordination/tasks/` (two
sources of truth), a single point of failure on the laptop hosting it, and an hour of setup on hackathon Saturday.
The part that saves quota, an external watcher that only wakes the CLI when there is work, is the same in both
designs, and git already gives us the queue, the lock (push rejection), the history and offline tolerance.
If we later want live chat between agents, add an MCP server then. The watcher doesn't need to change.
