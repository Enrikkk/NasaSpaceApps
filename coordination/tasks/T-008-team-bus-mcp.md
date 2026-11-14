---
id: T-008
title: Team bus MCP on the hub: agent-to-agent messages across laptops, jaime = orchestrator
status: review
owner: jaime
branch: main
paths: scripts/team_bus.py, scripts/team_bus_join.sh, scripts/paseo_team.sh, .claude/settings.json (enabledMcpjsonServers), .mcp.json, .cursor/mcp.json, coordination/TEAM-SETUP.md, coordination/ORCHESTRATOR.md, coordination/PASEO.md, AGENTS.md
depends: T-007
---
Paseo's own MCP tools only act on one host, so add a small MCP server on jaime's Mac (Tailscale IP, per-seat bearer
tokens) that every teammate's agent (Claude Code / Codex / Cursor) connects to. Tools: whoami, team_status,
send_message (to a seat, the orchestrator, or all), read_messages, report, request_handoff; hub-only: dispatch.
Messages are pushed live into running Paseo agents via `paseo send`, otherwise they wait in the inbox.
Plus an agent-executable setup guide (coordination/TEAM-SETUP.md) so each teammate tells their agent "set it all up".

- 2026-11-14 12:10 | jaime | team-bus live on the hub (100.93.255.39:6780/mcp, terminal tab 'team-bus'); tokens minted for jaime + orchestrator.
  Verified: 401 without token, 403 foreign Origin, worker dispatch refused; real Claude Code (-p, Haiku) used whoami/read/send
  via the repo-style .mcp.json with env expansion; a message was pushed live into a Paseo agent titled 'orchestrator'.
  Codex/Cursor configs written, untested. Left: jaime runs team_bus_join.sh for his own shell (the agent was not allowed to
  write the token into shell profiles), mints teammate tokens, teammates follow coordination/TEAM-SETUP.md.
