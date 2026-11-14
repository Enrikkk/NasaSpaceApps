# Live inbox for interactive agent sessions (team-bus messages as interrupts)

**Problem.** The hub pushes team-bus messages live only into Paseo agents it dispatched (`T-NNN <seat>`) and into
the `orchestrator`. An agent session a human opened by hand (Claude Code, Codex, opencode, Antigravity, pi…)
gets nothing until it calls `read_messages` itself, so teammates' messages sit unread.

**Fix.** `scripts/bus_listen.sh` polls the bus every 5 s with plain `curl` (0 tokens while nothing arrives) and
prints each new message as one line: `[team-bus] #N <time> message from <seat>: <text>`. Run it as a background
monitor whose output interrupts the agent, so messages land in its context as soon as they arrive.

## Every interactive session does this once, at start

1. `export SEAT=<your seat>` (already in `~/.profile` if you ran `scripts/team_join.sh`).
2. **MANDATORY for every agent of the team.** Start the listener as a background monitor:
   - **Claude Code:** Monitor tool, `command: bash scripts/bus_listen.sh`, `timeout_ms: 1800000` (the 30 min
     maximum), description `team-bus inbox (<seat>)`. Each line wakes the agent. **Re-arm it every time it
     expires** (you get a notice), for the whole session.
   - **Other agents:** use your tool's equivalent of a background process whose output re-invokes you. If there is
     none, run it in a terminal next to the agent and call `read_messages` after each step (AGENTS.md §7).
3. When a `[team-bus]` line arrives: treat it as a teammate request (AGENTS.md still applies). Answer with
   `send_message`/`report`, tell your human in one line if it needs them, then continue your work.

## Rules

- **Not for the hub's `orchestrator` or `T-NNN <seat>` agents**: they get messages pushed, and the script exits by
  itself when `TEAM_BUS_ROLE` is set (paseo_team.sh sets it).
- Restarting the listener is quiet: re-registration no longer sends a "joined" message to the orchestrator.
- **One listener per seat.** The script takes a lock and `read_messages` marks messages read, so a second
  listener would steal messages. Hub-dispatched `T-NNN <seat>` agents already get pushes: they don't run it.
- Messages are consumed by the listener. To re-read old ones, look at the hub's store or ask the sender.
- Hub down: the script prints one warning after 3 failed polls and keeps retrying. Git stays the fallback.
- Tune with `BUS_POLL=<seconds>` and `TEAM_BUS_URL`.

## Instant delivery when your agent UI can't be woken (Codex Desktop, Antigravity, pi…)

Your laptop's Paseo daemon can inject a message into a running agent (`paseo send --behavior steer`, what the hub
uses). So run your interactive agent as a Paseo agent and bridge the bus into it:

1. Make the session a Paseo agent. Keep your current context: `paseo import <provider-session-id> --provider codex
   --cwd <repo path>`. Or start fresh: `paseo run --provider codex --title "<seat> live" --no-wait "You are <seat>'s
   interactive agent; read AGENTS.md"`. Get its id with `paseo ls`.
2. Stop any `bus_listen.sh` for your seat, then in a separate terminal: `SEAT=<seat> bash scripts/bus_bridge_paseo.sh <id>`.
3. Work with that agent from the Paseo app (or `paseo attach <id>`), not the provider's own window: injected
   messages land in the session Paseo drives, and the provider's desktop app may not show them.
4. Test: ask a teammate for a ping. Not yet tested end-to-end with Codex Desktop.

Multi-line messages arrive as one line with ` ⏎ ` where the line breaks were.
