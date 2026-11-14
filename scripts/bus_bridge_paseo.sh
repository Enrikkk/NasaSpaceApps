#!/usr/bin/env bash
# Instant team-bus delivery for agent UIs that can't be woken by a background process (Codex Desktop, Antigravity, pi…).
# Pipes scripts/bus_listen.sh into a Paseo agent on THIS laptop with `paseo send --behavior steer`, so each message
# interrupts that agent right away (the same mechanism the hub uses for dispatched agents).
# Usage:  SEAT=<seat> bash scripts/bus_bridge_paseo.sh <paseo-agent-id>      (find the id with `paseo ls`)
# Work with that agent through the Paseo app or `paseo attach <id>`: messages land in the session Paseo drives.
# It replaces bus_listen.sh for the seat (one listener per seat). Details: coordination/BUS-LISTEN.md.
set -u
AGENT="${1:?usage: SEAT=<seat> bash scripts/bus_bridge_paseo.sh <paseo-agent-id>}"
cd "$(dirname "$0")/.." || exit 1
bash scripts/bus_listen.sh | while IFS= read -r l; do
  case "$l" in
    "[team-bus]"*)
      echo "$l"
      paseo send --no-wait --behavior steer "$AGENT" \
        "$l (Teammate request via team-bus; AGENTS.md still applies. Answer with team-bus send_message, then continue.)" \
        >/dev/null 2>&1 || echo "bus_bridge: paseo send to $AGENT failed (agent gone? check paseo ls)";;
    *) echo "$l";;
  esac
done
