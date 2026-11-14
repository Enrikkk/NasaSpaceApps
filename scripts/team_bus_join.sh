#!/usr/bin/env bash
# Connect THIS laptop's agents to the team-bus MCP on the hub (T-008, coordination/TEAM-SETUP.md).
# Run it yourself: it asks for the token jaime sent you privately (hidden input).
#   bash scripts/team_bus_join.sh
set -euo pipefail
HUB_IP="${HUB_IP:-100.93.255.39}"
URL="http://$HUB_IP:6780/mcp"
ENVF="$HOME/.team-bus.env"

if [ -n "${TEAM_BUS_TOKEN_FILE:-}" ]; then           # hub self-setup: token file minted by team_bus.py
  TOKEN="$(cat "$TEAM_BUS_TOKEN_FILE")"
else
  printf 'Team-bus token from jaime (input hidden): '; read -r -s TOKEN; echo
fi
[ -n "$TOKEN" ] || { echo "empty token"; exit 1; }

# 1. check the token against the hub
reply="$(curl -s -m 10 -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"whoami","arguments":{}}}' "$URL" || true)"
seat="$(printf '%s' "$reply" | python3 -c 'import json,sys
try: print(json.loads(json.loads(sys.stdin.read())["result"]["content"][0]["text"])["seat"])
except Exception: print("")')"
[ -n "$seat" ] || { echo "hub did not accept the token (is Tailscale up? is the bus running on $HUB_IP:6780?)"; exit 1; }
echo "token OK: you are seat '$seat'"

# 2. store it outside the repo and load it from every shell (login shells too, which Paseo uses)
umask 077
printf 'export TEAM_BUS_TOKEN=%q\nexport TEAM_BUS_URL=%q\n' "$TOKEN" "$URL" > "$ENVF"
line='[ -f "$HOME/.team-bus.env" ] && . "$HOME/.team-bus.env"'
for rc in "$HOME/.bash_profile" "$HOME/.bashrc" "$HOME/.zprofile" "$HOME/.zshrc" "$HOME/.profile"; do
  if [ -f "$rc" ] || [ "$rc" = "$HOME/.zprofile" ] || [ "$rc" = "$HOME/.bash_profile" ]; then
    grep -qF '.team-bus.env' "$rc" 2>/dev/null || printf '\n# team-bus MCP (NASA Space Apps)\n%s\n' "$line" >> "$rc"
  fi
done
echo "saved in $ENVF (chmod 600), loaded from your shell profiles"

# 3. per-tool config (Claude Code reads the repo's .mcp.json; Cursor reads .cursor/mcp.json)
if command -v codex >/dev/null 2>&1; then
  codex mcp add team-bus --url "$URL" --bearer-token-env-var TEAM_BUS_TOKEN >/dev/null 2>&1 \
    && echo "Codex: team-bus added (codex mcp list)" \
    || echo "Codex: add it by hand, see coordination/TEAM-SETUP.md"
fi
echo "Done. Open a NEW terminal (or restart Claude Code / Cursor / the Paseo app) so they see TEAM_BUS_TOKEN."
