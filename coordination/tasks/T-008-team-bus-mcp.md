---
id: T-008
title: Team bus MCP on the hub: agent-to-agent messages across laptops, jaime = orchestrator
status: doing
owner: jaime
branch: main
paths: scripts/team_bus.py, .mcp.json, .cursor/mcp.json, coordination/TEAM-SETUP.md, coordination/ORCHESTRATOR.md, coordination/PASEO.md, AGENTS.md
depends: T-007
---
Paseo's own MCP tools only act on one host, so add a small MCP server on jaime's Mac (Tailscale IP, per-seat bearer
tokens) that every teammate's agent (Claude Code / Codex / Cursor) connects to. Tools: whoami, team_status,
send_message (to a seat, the orchestrator, or all), read_messages, report, request_handoff; hub-only: dispatch.
Messages are pushed live into running Paseo agents via `paseo send`, otherwise they wait in the inbox.
Plus an agent-executable setup guide (coordination/TEAM-SETUP.md) so each teammate tells their agent "set it all up".
