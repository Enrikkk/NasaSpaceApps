#!/usr/bin/env bash
# HUB ONLY (jaime's Mac): run the team-bus as a macOS LaunchAgent so it survives closed terminals and reboots.
#   bash scripts/hub_service.sh install | uninstall | status | logs
set -euo pipefail
LABEL=es.umu.nasaspaceapps.teambus
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$HOME/.paseo-team/bus/serve.log"

case "${1:-status}" in
  install)
    mkdir -p "$HOME/Library/LaunchAgents" "$(dirname "$LOG")"
    cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>/usr/bin/python3</string><string>$ROOT/scripts/team_bus.py</string><string>serve</string></array>
  <key>WorkingDirectory</key><string>$ROOT</string>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>$HOME/.local/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>GIT_TERMINAL_PROMPT</key><string>0</string>
    <key>GIT_SSH_COMMAND</key><string>ssh -o BatchMode=yes -o ConnectTimeout=5</string>
  </dict>
  <key>RunAtLoad</key><true/><key>KeepAlive</key><true/><key>ThrottleInterval</key><integer>15</integer>
  <key>StandardOutPath</key><string>$LOG</string><key>StandardErrorPath</key><string>$LOG</string>
</dict></plist>
EOF
    launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$PLIST"
    sleep 3; tail -3 "$LOG"
    echo "installed. If the log says 'Operation not permitted', give /usr/bin/python3 Full Disk Access or move the repo out of ~/Documents." ;;
  uninstall)
    launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true; rm -f "$PLIST"; echo "removed" ;;
  status)
    launchctl print "gui/$(id -u)/$LABEL" 2>/dev/null | grep -E "state|pid" || echo "not installed"
    curl -s -m 3 "http://$(tailscale ip -4 | head -1):6780/health" || echo "bus not answering" ;;
  logs) tail -f "$LOG" ;;
esac
