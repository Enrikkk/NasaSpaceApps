#!/usr/bin/env bash
# Live inbox for an INTERACTIVE agent session (a human-driven Claude Code / Codex / opencode window).
# Hub-dispatched Paseo agents ("T-NNN <seat>") already get messages pushed by the hub: they don't need this.
#
# Polls the team bus every $BUS_POLL seconds (default 20) with plain curl, so waiting costs 0 tokens. Each new
# message is printed as ONE stdout line and marked read. Run it as a background monitor whose every output
# line interrupts the agent:
#   Claude Code: Monitor tool, command `bash scripts/bus_listen.sh` (persistent).
#   Other tools: run it in a background terminal and have the agent read its output, or ask the human to.
# Only one listener per seat: two would race for the same messages. Details: coordination/BUS-LISTEN.md.
set -u
URL="${TEAM_BUS_URL:-http://100.93.255.39:6780/mcp}"
SEAT="${SEAT:?export SEAT=<your seat> first}"
POLL="${BUS_POLL:-20}"
LOCK="${TMPDIR:-/tmp}/bus_listen.${SEAT}.lock"

exec 9>"$LOCK"
if ! flock -n 9 2>/dev/null; then
  command -v flock >/dev/null && { echo "bus_listen: another listener for seat '$SEAT' is already running"; exit 1; }
fi

rpc() {  # rpc <id> <method> <params-json>
  curl -s -m 15 -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
       -H "Authorization: Bearer ${TEAM_BUS_TOKEN:-}" "$URL" \
       -d "{\"jsonrpc\":\"2.0\",\"id\":$1,\"method\":\"$2\",\"params\":$3}"
}

register() {
  rpc 1 initialize '{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"bus_listen","version":"1"}}' >/dev/null
  rpc 2 tools/call "{\"name\":\"register\",\"arguments\":{\"seat\":\"$SEAT\"}}" >/dev/null
}

register
echo "bus_listen: listening as seat '$SEAT' every ${POLL}s on $URL"
down=0
while :; do
  out=$(rpc 3 tools/call '{"name":"read_messages","arguments":{}}')
  if [ -z "$out" ]; then
    down=$((down + 1)); [ "$down" -eq 3 ] && echo "bus_listen: hub unreachable (3 tries); still retrying"
  else
    [ "$down" -ge 3 ] && echo "bus_listen: hub reachable again"
    down=0
    printf '%s' "$out" | python3 -I -c '
import json, sys
try:
    r = json.load(sys.stdin)
except ValueError:
    sys.exit()
res = r.get("result") or {}
txt = "\n".join(c.get("text", "") for c in res.get("content", []))
if res.get("isError") or "not registered" in txt:
    print("bus_listen: bus error: " + txt.replace("\n", " | ")[:300]); sys.exit(2)
for line in txt.splitlines():
    if line.startswith("#"):
        print("[team-bus] " + line, flush=True)
' || register
  fi
  sleep "$POLL"
done
