#!/usr/bin/env bash
# ONE command, no questions: join THIS laptop to the team mesh (Tailscale + Paseo + team-bus MCP). Safe to re-run.
#   bash scripts/team_join.sh <seat>
# Exit 0 = ready. Exit 3 = a HUMAN step is needed (printed); do it, then re-run. Anything else = error (printed).
# What it does: checks Tailscale, puts ~/.local/bin on the login PATH, installs/links the Paseo CLI, starts the daemon,
# generates a random daemon password (kept in ~/.team-mesh/daemon-password, chmod 600), listens on the Tailscale IP
# only, and registers with the hub's team-bus, which stores that password so the orchestrator can start tasks here.
set -euo pipefail
SEAT="$(printf '%s' "${1:-${SEAT:-}}" | tr '[:upper:]' '[:lower:]')"
[ -n "$SEAT" ] || { echo "usage: bash scripts/team_join.sh <seat>   (seat names: context/team.md)"; exit 2; }
HUB_IP="${HUB_IP:-100.93.255.39}"
PORT=6767
BUS="http://$HUB_IP:6780/mcp"
REPO="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STATE="$HOME/.team-mesh"
OS="$(uname -s)"
mkdir -p "$STATE" "$HOME/.local/bin"; chmod 700 "$STATE"
export PATH="$HOME/.local/bin:$PATH"

ok()    { printf '  \033[32mok\033[0m  %s\n' "$*"; }
human() { printf '\n\033[1;33mHUMAN STEP NEEDED:\033[0m %s\nThen re-run: bash scripts/team_join.sh %s\n' "$*" "$SEAT"; exit 3; }
fail()  { printf '\n\033[1;31mERROR:\033[0m %s\n' "$*"; exit 1; }

echo "Joining seat '$SEAT' ($OS) to the team mesh, hub $HUB_IP"

# 1. Tailscale -------------------------------------------------------------------------------------------------
TS="$(command -v tailscale || true)"
[ -z "$TS" ] && [ -x /Applications/Tailscale.app/Contents/MacOS/Tailscale ] && TS=/Applications/Tailscale.app/Contents/MacOS/Tailscale
if [ -z "$TS" ]; then
  if [ "$OS" = Darwin ] && command -v brew >/dev/null 2>&1; then
    brew install --cask tailscale >/dev/null 2>&1 || true
    [ -x /Applications/Tailscale.app/Contents/MacOS/Tailscale ] && TS=/Applications/Tailscale.app/Contents/MacOS/Tailscale
  fi
  [ -n "$TS" ] || human "install Tailscale: https://tailscale.com/download (Linux: curl -fsSL https://tailscale.com/install.sh | sh)"
fi
MYIP="$("$TS" ip -4 2>/dev/null | head -1 || true)"
[ -n "$MYIP" ] || human "open Tailscale and sign in using the invite link jaime posted in the team chat (it must be HIS tailnet)."
curl -s -m 5 "http://$HUB_IP:6780/health" | grep -q ok \
  || human "this laptop ($MYIP) can't reach the hub $HUB_IP. Make sure you joined jaime's tailnet via his invite link (not your own), and that jaime's Mac is on."
ok "Tailscale $MYIP, hub reachable"
IS_HUB=""; [ "$MYIP" = "$HUB_IP" ] && IS_HUB=1

# 2. ~/.local/bin on the LOGIN shell PATH (the Paseo daemon only reads login profiles) ----------------------------
case "$OS:$(basename "${SHELL:-bash}")" in
  Darwin:zsh) PROF="$HOME/.zprofile" ;;
  Darwin:*)   PROF="$HOME/.bash_profile" ;;
  *)          PROF="$HOME/.profile" ;;
esac
PATH_CHANGED=""
if ! grep -qs 'HOME/.local/bin' "$PROF"; then
  printf '\n# agent CLIs + paseo (team mesh)\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$PROF"
  PATH_CHANGED=1
fi
ok "login PATH has ~/.local/bin ($PROF)"

# 3. Paseo CLI + daemon -----------------------------------------------------------------------------------------
if ! command -v paseo >/dev/null 2>&1; then
  if [ -x /Applications/Paseo.app/Contents/Resources/bin/paseo ]; then
    ln -sf /Applications/Paseo.app/Contents/Resources/bin/paseo "$HOME/.local/bin/paseo"
  elif command -v npm >/dev/null 2>&1; then
    npm install -g @getpaseo/cli >/dev/null 2>&1 || npm install -g --prefix "$HOME/.local" @getpaseo/cli >/dev/null
  else
    human "install Node.js (https://nodejs.org) or the Paseo Desktop app (https://paseo.sh/download)"
  fi
fi
command -v paseo >/dev/null 2>&1 || fail "paseo CLI not found after install"
paseo daemon status >/dev/null 2>&1 || paseo daemon start >/dev/null 2>&1 || true
if [ -n "$PATH_CHANGED" ] && [ "$OS" = Darwin ] && pgrep -f "Paseo.app/Contents/MacOS/Paseo" >/dev/null; then
  osascript -e 'quit app "Paseo"' >/dev/null 2>&1 || true; sleep 3; open -a Paseo; sleep 8   # re-read login PATH
fi
for _ in $(seq 1 30); do paseo daemon status >/dev/null 2>&1 && break; sleep 1; done
paseo daemon status >/dev/null 2>&1 || fail "Paseo daemon does not start (paseo daemon status)"
ok "Paseo $(paseo --version 2>/dev/null) daemon running"

# 4. an agent CLI that the daemon can use ------------------------------------------------------------------------
for _ in $(seq 1 20); do paseo provider ls 2>/dev/null | grep -q ' loading ' || break; sleep 2; done
PROVS="$(paseo provider ls 2>/dev/null | awk 'NR>1 && $3=="available" {printf "%s ", $1}')"
if [ -z "$PROVS" ]; then
  for p in claude codex cursor; do paseo provider diagnostic "$p" 2>/dev/null | grep -E "Resolved path|Status" | sed "s/^/  $p: /"; done
  human "log in to your agent CLI so Paseo can use it: run 'claude' then /login, or 'codex login', or 'cursor-agent login'. (If it says 'not found': install it, see coordination/TEAM-SETUP.md step 2.)"
fi
TOOL="$(echo "$PROVS" | awk '{print $1}')"
ok "providers available: $PROVS"

# 5. daemon password + listen on Tailscale only (skipped on the hub, which keeps its own) --------------------------
PW=""
if [ -z "$IS_HUB" ]; then
  if [ -s "$STATE/daemon-password" ] && paseo daemon config get daemon.auth.password 2>/dev/null | grep -q '"set": true'; then
    PW="$(cat "$STATE/daemon-password")"
  else
    PW="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
    feed() { sleep 2; printf '%s\r' "$PW"; sleep 2; printf '%s\r' "$PW"; sleep 3; }
    if [ "$OS" = Darwin ]; then feed | script -q /dev/null paseo daemon set-password >/dev/null 2>&1 || true
    else feed | script -qec "paseo daemon set-password" /dev/null >/dev/null 2>&1 || true; fi
    paseo daemon config get daemon.auth.password 2>/dev/null | grep -q '"set": true' \
      || human "could not set the Paseo password automatically. Run 'paseo daemon set-password' yourself, then save the same password in $STATE/daemon-password (chmod 600)."
    (umask 077; printf '%s\n' "$PW" > "$STATE/daemon-password")
  fi
  paseo daemon config set daemon.listen "$MYIP:$PORT" >/dev/null
  paseo daemon restart >/dev/null 2>&1 || true
  up=""; for _ in $(seq 1 30); do curl -s -m 2 "http://$MYIP:$PORT/api/health" | grep -q '"ok"' && { up=1; break; }; sleep 1; done
  [ -n "$up" ] || { [ "$OS" = Darwin ] && { osascript -e 'quit app "Paseo"' >/dev/null 2>&1; sleep 3; open -a Paseo; sleep 10; }; }
  curl -s -m 3 "http://$MYIP:$PORT/api/health" | grep -q '"ok"' || fail "daemon not answering on $MYIP:$PORT"
  ok "daemon on $MYIP:$PORT with a generated password (in $STATE/daemon-password)"
else
  ok "this is the hub: daemon password and listen address left as they are"
fi

# 6. register with the team-bus (Tailscale identity = credential; hands over the daemon password for dispatch) ----
RESULT="$(SEAT="$SEAT" REPO="$REPO" PW="$PW" TOOL="$TOOL" BUS="$BUS" python3 - <<'EOF'
import json, os, urllib.request
args = {"seat": os.environ["SEAT"], "repo": os.environ["REPO"], "daemon_password": os.environ["PW"], "tool": os.environ["TOOL"]}
body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "register", "arguments": args}}).encode()
req = urllib.request.Request(os.environ["BUS"], body, {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
try:
    print(json.loads(urllib.request.urlopen(req, timeout=60).read())["result"]["content"][0]["text"])
except Exception as e:
    print(f"REGISTER FAILED: {e}")
EOF
)"
printf '%s\n' "$RESULT" | sed 's/^/  bus: /'
echo "$RESULT" | grep -q "REGISTER FAILED\|already registered\|must be" && fail "registration failed (see above)"

# 7. MCP clients: Claude Code + Cursor use the repo's .mcp.json / .cursor/mcp.json; Codex needs one command -------
if command -v codex >/dev/null 2>&1; then
  codex mcp remove team-bus >/dev/null 2>&1 || true
  codex mcp add team-bus --url "$BUS" >/dev/null 2>&1 && ok "Codex: team-bus MCP added" || echo "  Codex: add by hand: codex mcp add team-bus --url $BUS"
fi
grep -qs "export SEAT=" "$PROF" || printf 'export SEAT=%s\n' "$SEAT" >> "$PROF"

echo
echo "READY: seat=$SEAT ip=$MYIP providers=[$PROVS] bus=$BUS"
echo "Restart Claude Code / Cursor / Codex in this repo so they load the team-bus MCP tools."
