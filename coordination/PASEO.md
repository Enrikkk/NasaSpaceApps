# Paseo mesh over Tailscale: jaime's Mac orchestrates, every laptop runs its own agents (T-007, D-004)

## Shape

```
              Tailscale tailnet (jaime's, free plan up to 6 users)
   ┌───────────────────────── hub: jaime's Mac 100.93.255.39 ─────────────────────────┐
   │ Paseo daemon + orchestrator agent (Claude)                                       │
   │ scripts/paseo_team.sh dispatch <seat> T-NNN  ──►  paseo --host tcp://<ip>:6767   │
   └───────┬──────────────────────────┬──────────────────────────┬────────────────────┘
           ▼                          ▼                          ▼
   enrique's laptop            seat3 laptop               seat4 laptop
   Paseo daemon :6767          Paseo daemon :6767         Paseo daemon :6767
   claude / codex / cursor     (own login)                (own login)
```

- **Agents run on the laptop whose daemon starts them, with that laptop's CLI logins.** Each person's work uses
  their own subscription. Nobody logs into anyone else's account.
- **Git stays the durable record.** Task files, branches, LOG.md and DECISIONS.md are unchanged. Paseo is the
  live layer: it starts agents, follows them and stops duplicate work. If the hub or the Wi-Fi drops, everyone
  carries on with the git workflow (and `scripts/agent_watcher.py`, T-006).

## Setup

**Hub (jaime), once:**
1. Tailscale admin console → Users → Invite the 3 teammates (free Personal plan: 6 users).
2. `bash scripts/paseo_join.sh`, so the hub's daemon also listens on Tailscale with a password and teammates can
   watch it from their Paseo app.

**Each teammate, ~10 min:**
1. Install Tailscale, accept jaime's invite, connect.
2. Install Paseo Desktop (https://paseo.sh/download) or `npm install -g @getpaseo/cli`.
3. Install and log in your agent CLI: `claude` (run it once), `codex login`, or `cursor-agent login`.
4. `git clone` the repo, `export SEAT=<you>`, then `bash scripts/paseo_join.sh`. It sets a password, listens on
   your Tailscale IP, and prints one line to send to jaime **privately**, with your password.

**Hub registers each teammate:** `scripts/paseo_team.sh add <seat> <ip> <repo-path>` (asks for the password,
hidden). Secrets stay in `~/.paseo-team/` (chmod 600), never in the repo. `scripts/paseo_team.sh ls` shows who
is online and which providers they have.

## Daily flow (no duplicate work)

1. The orchestrator writes or updates `coordination/tasks/T-NNN-*.md` (owner, status `doing`, branch, paths) and
   pushes. The board is still the lock.
2. `scripts/paseo_team.sh dispatch <seat> T-NNN [provider/model]` starts an agent on that laptop, in a new
   worktree on branch `tNNN-slug` from `origin/main`.
3. `scripts/paseo_team.sh on <seat> wait <id>`, then `... logs <id> --tail 5` to read the `RESULT:` line.
4. The orchestrator sets the task to `review`/`blocked` with the result and appends to LOG. A human merges
   into main.
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

- A daemon password gives **full control of that laptop as its owner** (agents run shell commands). Share it only
  with the hub, privately. Rotate it with `paseo daemon set-password` after the event.
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
- Not tested yet: a second physical laptop.
