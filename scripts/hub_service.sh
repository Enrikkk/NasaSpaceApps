#!/usr/bin/env bash
# HUB ONLY (jaime's Mac): run the team-bus as a macOS LaunchAgent so it survives closed terminals and reboots.
#   bash scripts/hub_service.sh install | uninstall | status | logs
set -euo pipefail
LABEL=es.umu.nasaspaceapps.teambus
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$HOME/.paseo-team/bus/serve.log"
# launchd jobs can't read ~/Documents (macOS privacy/TCC), so the service runs its own clone outside it,
# fast-forwarded from GitHub at every start. The orchestrator still works in the real repo (TEAM_BUS_REPO).
APP="$HOME/.paseo-team/app"

case "${1:-status}" in
  install)
    mkdir -p "$HOME/Library/LaunchAgents" "$(dirname "$LOG")"
    if [ -d "$APP/.git" ]; then git -C "$APP" pull -q --ff-only
    else git clone -q "$(git -C "$ROOT" remote get-url origin)" "$APP"; fi
    echo "service code: $APP ($(git -C "$APP" log --oneline -1))"
    cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>-c</string>
    <string>cd "$APP" &amp;&amp; { git pull -q --ff-only || true; } &amp;&amp; exec /usr/bin/python3 scripts/team_bus.py serve</string></array>
  <key>WorkingDirectory</key><string>$APP</string>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>$HOME/.local/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>TEAM_BUS_REPO</key><string>$ROOT</string>
    <key>GIT_TERMINAL_PROMPT</key><string>0</string>
    <key>GIT_SSH_COMMAND</key><string>ssh -o BatchMode=yes -o ConnectTimeout=5</string>
  </dict>
  <key>RunAtLoad</key><true/><key>KeepAlive</key><true/><key>ThrottleInterval</key><integer>15</integer>
  <key>StandardOutPath</key><string>$LOG</string><key>StandardErrorPath</key><string>$LOG</string>
</dict></plist>
EOF
    launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$PLIST"
    for _ in $(seq 1 15); do curl -s -m 1 "http://$(tailscale ip -4 | head -1):6780/health" | grep -q ok && break; sleep 1; done
    tail -2 "$LOG"
    curl -s -m 2 "http://$(tailscale ip -4 | head -1):6780/health" | grep -q ok && echo "installed: team-bus is up (survives reboots)" \
      || echo "installed, but the bus is not answering yet: is another copy (a terminal tab) holding port 6780? bash scripts/hub_service.sh logs" ;;
  uninstall)
    launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true; rm -f "$PLIST"; echo "removed" ;;
  status)
    launchctl print "gui/$(id -u)/$LABEL" 2>/dev/null | grep -E "state|pid" || echo "not installed"
    curl -s -m 3 "http://$(tailscale ip -4 | head -1):6780/health" || echo "bus not answering" ;;
  logs) tail -f "$LOG" ;;
esac
