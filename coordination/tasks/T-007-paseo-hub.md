---
id: T-007
title: Paseo orchestrator over Tailscale (jaime's Mac = hub, one daemon per laptop)
status: review
owner: jaime
branch: main
paths: coordination/PASEO.md, scripts/paseo_join.sh, AGENTS.md (section 7), coordination/DECISIONS.md, coordination/AUTOPILOT.md
depends: T-006
---
Team wants Paseo (paseo.sh) as the live orchestrator so agents don't duplicate work, with jaime's Mac as the hub over
Tailscale. Agents run on the daemon's machine with that machine's CLI logins, so: one Paseo daemon per laptop (own
subscription), listening on its Tailscale IP with a password; the hub registers every laptop as a host and its
orchestrator agent launches work on them. Git (coordination/tasks, LOG) stays the durable record; T-006 watcher = fallback.

Acceptance: coordination/PASEO.md runbook; scripts/paseo_join.sh joins a laptop in one command; hub reaches itself via
its Tailscale IP; D-004 recorded.

- 2026-11-14 10:35 | jaime | done on the hub side; waiting for teammates. Claude Code CLI 2.1.325 installed on jaime's Mac
  (~/.local/bin, PATH added to ~/.bash_profile so the Paseo daemon finds claude and cursor-agent). Paseo 0.15.4 Desktop
  already installed; `paseo` CLI linked into ~/.local/bin. Verified with throwaway daemons: Tailscale listen + set-password
  auth (missing/wrong password rejected), host add -> online, dispatch run flags (worktree, branch, wait, logs).
  Left: jaime runs `bash scripts/paseo_join.sh` (password prompt), invites 3 teammates to the tailnet, each runs
  paseo_join.sh, hub runs `paseo_team.sh add` per seat. Cursor on jaime's Mac needs `cursor-agent login`.
- 2026-11-14 10:45 | jaime | hub live: paseo_join.sh run on jaime's Mac, daemon on 100.93.255.39:6767 with password; auth verified from a credential-less client (Password required / 401). Left: tailnet invites + teammates join + `paseo_team.sh add` per seat.
