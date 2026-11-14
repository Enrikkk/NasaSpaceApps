#!/usr/bin/env bash
# Join THIS laptop to the team's Paseo mesh over Tailscale (T-007, coordination/PASEO.md).
# Run it yourself in a terminal: it asks you to choose a daemon password.
#   bash scripts/paseo_join.sh
# Undo: paseo daemon config set daemon.listen 127.0.0.1:6767 && paseo daemon restart
set -euo pipefail
PORT="${PASEO_PORT:-6767}"
SEAT="${SEAT:-$(git config user.name 2>/dev/null || echo unknown)}"

say() { printf '\n\033[1m%s\033[0m\n' "$*"; }

# 1. Tailscale
command -v tailscale >/dev/null 2>&1 || {
  echo "Install Tailscale (https://tailscale.com/download), sign in with the invite jaime sent you, then re-run."; exit 1; }
IP="$(tailscale ip -4 2>/dev/null | head -1 || true)"
[ -n "$IP" ] || { echo "Tailscale is not connected. Open the Tailscale app (or run 'tailscale up') and re-run."; exit 1; }
say "Tailscale OK: $IP"

# 2. Paseo CLI (the Desktop app bundles it)
if ! command -v paseo >/dev/null 2>&1; then
  if [ -x /Applications/Paseo.app/Contents/Resources/bin/paseo ]; then
    mkdir -p "$HOME/.local/bin"
    ln -sf /Applications/Paseo.app/Contents/Resources/bin/paseo "$HOME/.local/bin/paseo"
    export PATH="$HOME/.local/bin:$PATH"
  else
    echo "Install Paseo: Desktop app from https://paseo.sh/download (recommended) or 'npm install -g @getpaseo/cli'."; exit 1
  fi
fi
paseo daemon status >/dev/null 2>&1 || paseo daemon start >/dev/null
say "Paseo $(paseo --version) daemon running"

# 3. Agent CLIs must be on the daemon's login-shell PATH and logged in with YOUR account
say "Providers on this laptop (you need at least one 'available'):"
paseo provider ls 2>/dev/null | awk 'NR>1 && $1 ~ /^(claude|codex|cursor|opencode|copilot)$/ {print "  " $1 ": " $3}'
cat <<'EOF'
  - unavailable = CLI not found by the daemon. If `claude`/`cursor-agent` live in ~/.local/bin, add
    export PATH="$HOME/.local/bin:$PATH"   to ~/.bash_profile (macOS) or ~/.profile (Linux), then restart Paseo.
  - error = not logged in: run `claude` once, `codex login`, or `cursor-agent login`.
EOF

# 4. Password (required before listening on the network)
if paseo daemon config get daemon.auth.password 2>/dev/null | grep -q '"set": true'; then
  say "Daemon password already set (keep using the one you shared with jaime)."
else
  say "Choose a daemon password. Anyone who has it can run agents on THIS laptop as you."
  echo "Share it with jaime in a private message only. Never put it in the repo or the LOG."
  paseo daemon set-password
fi
paseo daemon config get daemon.auth.password 2>/dev/null | grep -q '"set": true' || {
  echo "No password set; refusing to listen on the network."; exit 1; }

# 5. Listen on the Tailscale IP only (not on the venue Wi-Fi)
paseo daemon config set daemon.listen "$IP:$PORT" >/dev/null
paseo daemon restart >/dev/null 2>&1 || true
ok=""
for _ in $(seq 1 30); do
  if curl -s -m 2 "http://$IP:$PORT/api/health" | grep -q '"ok"'; then ok=1; break; fi
  sleep 1
done
if [ -z "$ok" ]; then
  echo "Daemon is not answering on $IP:$PORT yet. Quit and reopen the Paseo app (Desktop keeps the old address"
  echo "until it restarts), then check: curl http://$IP:$PORT/api/health"; exit 1
fi
say "Listening on $IP:$PORT with a password."

REPO="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
say "Send this to jaime (private chat), plus your password:"
echo "  bash scripts/paseo_team.sh add $SEAT $IP '$REPO'"
