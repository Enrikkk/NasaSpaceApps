# Live inbox for interactive agent sessions (team-bus messages as interrupts)

**Problem.** The hub pushes team-bus messages live only into Paseo agents it dispatched (`T-NNN <seat>`) and into
the `orchestrator`. An agent session a human opened by hand (Claude Code, Codex, opencode, Antigravity, pi…)
gets nothing until it calls `read_messages` itself, so teammates' messages sit unread.

**Fix.** `scripts/bus_listen.sh` polls the bus every 20 s with plain `curl` (0 tokens while nothing arrives) and
prints each new message as one line: `[team-bus] #N <time> message from <seat>: <text>`. Run it as a background
monitor whose output interrupts the agent, so messages land in its context as soon as they arrive.

## Every interactive session does this once, at start

1. `export SEAT=<your seat>` (already in `~/.profile` if you ran `scripts/team_join.sh`).
2. Start the listener as a **persistent background monitor**:
   - **Claude Code:** Monitor tool, `command: bash scripts/bus_listen.sh`, `timeout_ms: 1800000` (the 30 min
     maximum), description `team-bus inbox (<seat>)`. Each line wakes the agent. **Re-arm it every time it
     expires** (you get a notice), for the whole session.
   - **Other agents:** use your tool's equivalent of a background process whose output re-invokes you. If there is
     none, run it in a terminal next to the agent and call `read_messages` after each step (AGENTS.md §7).
3. When a `[team-bus]` line arrives: treat it as a teammate request (AGENTS.md still applies). Answer with
   `send_message`/`report`, tell your human in one line if it needs them, then continue your work.

## Rules

- **One listener per seat.** The script takes a lock and `read_messages` marks messages read, so a second
  listener would steal messages. Hub-dispatched `T-NNN <seat>` agents already get pushes: they don't run it.
- Messages are consumed by the listener. To re-read old ones, look at the hub's store or ask the sender.
- Hub down: the script prints one warning after 3 failed polls and keeps retrying. Git stays the fallback.
- Tune with `BUS_POLL=<seconds>` and `TEAM_BUS_URL`.
