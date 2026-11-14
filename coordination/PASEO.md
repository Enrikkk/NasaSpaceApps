# Paseo mesh over Tailscale: jaime's Mac orchestrates, every laptop runs its own agents (T-007, D-004)

## Shape

```
                    Tailscale tailnet (jaime's, free plan up to 6 users)
 ┌──────────────────────────── hub: jaime's Mac 100.93.255.39 ─────────────────────────────┐
 │ orchestrator agent (Paseo, Claude)  ◄──pushes──  team-bus MCP :6780/mcp  (team_bus.py)  │
 │ Paseo daemon :6767                  ──dispatch──►  paseo --host tcp://<ip>:6767 run ...  │
 └──────┬───────────────────────────────┬───────────────────────────────┬───────────────────┘
        │ team-bus tools (HTTP+token)   │                               │
        ▼                               ▼                               ▼
  enrique's laptop                seat3 laptop                    seat4 laptop
  Paseo daemon :6767              Paseo daemon :6767              Paseo daemon :6767
  claude/codex/cursor (own login) ...                             ...
```

- **Agents run on the laptop whose daemon starts them, with that laptop's CLI logins.** Each person's work uses
  their own subscription. Nobody logs into anyone else's account.
- **Agents talk to each other only through the hub's team-bus MCP** (`scripts/team_bus.py`): `send_message`,
  `read_messages`, `report`, `request_handoff`, plus `dispatch`/`agent_result` for the orchestrator only. Each seat
  has its own bearer token. A message to a seat that has a live hub-dispatched agent (`T-NNN <seat>`), or to the
  `orchestrator`, is **pushed into that agent's conversation** with `paseo send`. Otherwise it waits in the inbox.
  Nobody polls.
- **Git stays the durable record.** Task files, branches, LOG.md and DECISIONS.md are unchanged. Paseo and the bus
  are the live layer. If the hub or the Wi-Fi drops, everyone carries on with the git workflow (and
  `scripts/agent_watcher.py`, T-006).

## Setup

**Each teammate (one command, run by their agent):** tell your agent *"Lee `coordination/TEAM-SETUP.md` y deja este
portátil preparado. Mi seat es `<seat>`"*. It runs `bash scripts/team_join.sh <seat>` and only stops for a human
when **Tailscale** needs installing or signing in (with jaime's invite link), or the agent CLI isn't logged in.
There are no tokens or passwords to exchange:
- **Bus auth = tailnet membership.** The bus asks `tailscale whois` who is calling and maps that Tailscale login to a
  seat, which `register` binds on first contact.
- **Dispatch credentials travel by themselves.** `team_join.sh` generates the laptop's Paseo daemon password and
  `register` hands it to the hub over Tailscale. It's stored in `~/.paseo-team/<seat>.env` (chmod 600).

**Hub (jaime): done on 2026-11-14 by his agent.** Daemon on `100.93.255.39:6767` with a password. Bus running (terminal
tab `team-bus`). Seat `jaime` registered. `orchestrator` token minted (`~/.paseo-team/bus/tokens/`). The orchestrator
auto-starts when a message arrives.
**The one thing only jaime can do:** Tailscale admin console → Users → **Invite users** → copy the invite link
and post it in the team chat. Free plan: 6 users.
Optional: `bash scripts/hub_service.sh install` makes the bus a LaunchAgent (survives reboots). Close the
`team-bus` terminal tab first. His agent wasn't allowed to install persistent services.

**Hub, every session:** nothing to do if the bus is running (`bash scripts/hub_service.sh status`). Talk to the
orchestrator in the Paseo app (agent `orchestrator`). If none is running: `scripts/paseo_team.sh orchestrator`. Seats:
`python3 scripts/team_bus.py seats`, `scripts/paseo_team.sh ls`.

## Daily flow (no duplicate work)

1. The orchestrator writes `coordination/tasks/T-NNN-*.md` (owner, `doing`, branch, paths) and pushes. The board is the lock.
2. It calls `dispatch(seat, T-NNN, provider)`, or you run `scripts/paseo_team.sh dispatch <seat> T-NNN [provider/model]`.
   That starts an agent on that laptop in a new worktree, branch `tNNN-slug` from `origin/main`.
3. The worker talks through the bus (questions, `request_handoff`) and finishes with `report` + a `RESULT:` line.
   The report is pushed into the orchestrator. No `wait` or polling is needed.
4. The orchestrator sets the task to `review`/`blocked` and appends to LOG. A human merges into main.
5. Anyone can watch every agent live: Paseo app → Settings → Add host → Direct connection, IP + 6767, SSL off.

## Shared rules that keep token use low

- **One planner, many workers.** Only the hub's orchestrator reads the big picture. Workers get a short prompt
  that points to one task file (`dispatch` builds it) and nothing else.
- **Waiting is free.** Use `paseo wait`, never ask an agent "are you done?". No polling agents.
- **Right-size the model:** the best model for the orchestrator and for hard tasks; Sonnet or Haiku
  (`claude/claude-haiku-5-5`), or the default Codex model, for routine edits, tests and data scripts.
- **Concrete task files.** Paths, interface, how to test. A vague task burns quota and comes back `blocked`.
- **One task per agent, one branch per task.** Archive finished agents (`paseo archive <id>`). Paseo releases
  idle agents after 1 h.
- **Results are one line:** `RESULT: done|blocked | ...`. The orchestrator reads `logs --tail 5`, not the whole run.

## Safety

- A daemon password gives **full control of that laptop as its owner** (agents run shell commands). `team_join.sh`
  generates it and gives it only to the hub. After the event, rotate it (`paseo daemon set-password`) or stop
  listening (`paseo daemon config set daemon.listen 127.0.0.1:6767 && paseo daemon restart`).
- Bus identity = Tailscale login, so **only invite teammates to the tailnet**. Anyone in it can register a seat.
- The daemon listens on the Tailscale IP only, not on the venue Wi-Fi. The relay stays off.
- Teammates who join jaime's tailnet can reach jaime's other devices. Optional hardening: in the tailnet ACLs,
  allow only `tcp:6767` between members.
- Undo on a laptop: `paseo daemon config set daemon.listen 127.0.0.1:6767 && paseo daemon restart`.

## Verified on 2026-11-14 (Paseo 0.15.4)

- A daemon on a Tailscale IP with `set-password` rejects missing and wrong passwords and accepts the right one.
- `paseo host add tcp://IP:6767?password=…` registers a remote host. It shows `online`.
- `paseo --host` takes an endpoint (`tcp://IP:PORT`), not a host label. The password goes in the `PASEO_PASSWORD`
  environment variable (what `paseo_team.sh` does).
- **Gotchas:** `PASEO_PASSWORD` in the environment of `paseo daemon start` did **not** enable auth; only
  `paseo daemon set-password` did, and it needs a real terminal. The daemon (Desktop) doesn't read `~/.bashrc`:
  CLIs in `~/.local/bin` need that PATH in `~/.bash_profile`, then a full Paseo restart.
- `dispatch`'s `run --new-workspace worktree --worktree-mode branch-off --new-branch … --base origin/main` was
  tested locally with Haiku (worktree, branch, `wait`, `logs`, then `workspace archive` cleanup).
- Hub live since 2026-11-14 10:45: jaime's daemon listens on 100.93.255.39:6767 with a password. A credential-less
  client gets `Password required`, a wrong password `Incorrect password`, and `GET /api/agents` returns 401.
  **Don't be fooled:** on the daemon's own machine, `paseo --host tcp://<own-ip>:6767 ...` works *without* a password,
  because the CLI uses that machine's `~/.paseo/local-credential`. Test auth from another laptop, or with `PASEO_HOME=<empty dir>`.
- team-bus (2026-11-14, isolated test instance): no token → 401, foreign `Origin` → 403, worker `dispatch` refused,
  inbox and read cursors work. **Real Claude Code** (`claude -p`, Haiku) loaded the repo-style `.mcp.json` with
  `${TEAM_BUS_URL:-…}`/`${TEAM_BUS_TOKEN:-}` expansion, called whoami/read_messages/send_message, and the message was
  **pushed live** into a Paseo agent titled `orchestrator`, which answered `got it #3`.
- Codex (`codex mcp add … --bearer-token-env-var`, per the OpenAI docs) and Cursor (`.cursor/mcp.json`, URL only)
  configs are written but untested: no logged-in Codex/Cursor on the hub.
- Zero-secret flow (12:15): `team_join.sh jaime` on the hub exited 0, `register` bound the seat and reached the hub
  daemon, and the `join` message **auto-started the orchestrator** (Paseo agent `orchestrator`), which then called
  `team_status` and `read_messages` through the bus. `tailscale whois` identity was checked on the hub's own IP. The
  generated-password path (`script` pty feed into `set-password`) was checked on an isolated daemon earlier.
- Not tested yet: a second physical laptop (the whois path for a *peer*, and set-password through `script` on Linux).
