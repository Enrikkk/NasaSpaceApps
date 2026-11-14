#!/usr/bin/env bash
# Hub side of the team's Paseo mesh (T-007, coordination/PASEO.md). Runs on the orchestrator laptop (jaime).
# Secrets stay outside the repo in ~/.paseo-team/<seat>.env (chmod 600).
#
#   scripts/paseo_team.sh add <seat> <tailscale-ip> [repo-path-on-their-laptop]   # asks the password (hidden)
#   scripts/paseo_team.sh ls                                        # who is online, which providers
#   scripts/paseo_team.sh on <seat> <paseo args...>                 # any paseo command on that laptop
#   scripts/paseo_team.sh dispatch <seat> <T-NNN> [provider[/model]] # start the task there (token-lean prompt)
#   scripts/paseo_team.sh orchestrator [provider]                  # start the hub's orchestrator agent
#   scripts/paseo_team.sh rm <seat>
set -euo pipefail
DIR="$HOME/.paseo-team"
PORT="${PASEO_PORT:-6767}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

load() {
  [ -f "$DIR/$1.env" ] || { echo "unknown seat '$1' (scripts/paseo_team.sh add $1 <ip>)"; exit 1; }
  # shellcheck disable=SC1090
  . "$DIR/$1.env"
}
remote() { PASEO_PASSWORD="$PASSWORD" paseo --host "tcp://$IP:$PORT" "$@"; }
# --env flags so agents started by the hub can use the team-bus MCP (tokens minted by scripts/team_bus.py token)
bus_env() {
  local tok="$DIR/bus/tokens/$1.token" hub
  hub="$(tailscale ip -4 2>/dev/null | head -1)"
  [ -f "$tok" ] && [ -n "$hub" ] && printf '%s\n' --env "TEAM_BUS_TOKEN=$(cat "$tok")" --env "TEAM_BUS_URL=http://$hub:6780/mcp"
  return 0
}

cmd="${1:-ls}"; shift || true
case "$cmd" in
  add)
    seat="${1:?seat}"; ip="${2:?tailscale ip}"
    repo="${3:?absolute repo path on their laptop (paseo_join.sh prints it)}"
    mkdir -p "$DIR"; chmod 700 "$DIR"
    printf 'Daemon password for %s: ' "$seat"; read -r -s pw; echo
    PASEO_PASSWORD="$pw" paseo --host "tcp://$ip:$PORT" provider ls >/dev/null || {
      echo "cannot reach $seat at $ip:$PORT with that password"; exit 1; }
    umask 077
    { printf 'IP=%q\nREPO=%q\nPASSWORD=%q\n' "$ip" "$repo" "$pw"; } > "$DIR/$seat.env"
    # also show their laptop in the hub's Paseo app (sidebar host list)
    paseo host add "tcp://$ip:$PORT?password=$pw" --label "$seat" >/dev/null 2>&1 || true
    echo "added $seat ($ip). Try: scripts/paseo_team.sh on $seat ls"
    ;;
  rm)
    rm -f "$DIR/$1.env"; echo "removed $1 (also remove it in Paseo: paseo host ls / paseo host rm <id>)" ;;
  ls)
    for f in "$DIR"/*.env; do
      [ -e "$f" ] || { echo "no seats yet: scripts/paseo_team.sh add <seat> <ip>"; exit 0; }
      seat="$(basename "$f" .env)"; load "$seat"
      if provs="$(remote provider ls 2>/dev/null)"; then
        avail="$(echo "$provs" | awk 'NR>1 && $3=="available" {printf "%s ", $1}')"
        busy="$(remote ls -q 2>/dev/null | wc -l | tr -d ' ')"
        echo "$seat  $IP  online  agents=$busy  providers: ${avail:-none}"
      else
        echo "$seat  $IP  OFFLINE"
      fi
    done ;;
  on)
    seat="$1"; shift; load "$seat"; remote "$@" ;;
  dispatch)
    seat="$1"; tid="$2"; prov="${3:-}"; load "$seat"
    git -C "$ROOT" fetch -q origin
    file="$(git -C "$ROOT" ls-tree --name-only origin/main coordination/tasks/ | grep "/$tid-" | head -1)"
    [ -n "$file" ] || { echo "$tid is not on origin/main. Write the task file and push it first."; exit 1; }
    slug="$(basename "$file" .md)"; branch="t${slug#T-}"; branch="${branch:0:60}"
    prompt="Seat $seat, task $tid. First: git fetch origin && git rebase origin/main. \
Read AGENTS.md sections 3-6 and $file, nothing else unless the task needs it. Stay inside the task's paths. \
Work on this branch ($branch), small commits prefixed '$tid:', push the branch. Do not merge into main. \
Team-bus MCP tools (if available): read_messages now; send_message to ask a seat or the orchestrator; \
request_handoff if another seat must do part of it (don't do it yourself); report when done or blocked. \
End with exactly one line: RESULT: done|blocked | <1-2 line result, how to run it, branch>."
    args=(run --no-wait --quiet --title "$tid $seat" --label "task=$tid" --cwd "$REPO"
          --new-workspace worktree --worktree-mode branch-off --new-branch "$branch" --base origin/main)
    [ -n "$prov" ] && args+=(--provider "$prov")
    args+=($(bus_env "$seat"))
    out="$(remote "${args[@]}" "$prompt" 2>/dev/null)"
    id="$(printf '%s\n' "$out" | grep -E -o '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | tail -1)"
    [ -n "$id" ] || { echo "dispatch failed:"; printf '%s\n' "$out"; exit 1; }
    echo "$tid -> $seat agent $id on branch $branch"
    echo "wait (0 tokens): scripts/paseo_team.sh on $seat wait $id"
    echo "result:          scripts/paseo_team.sh on $seat logs $id --tail 5"
    ;;
  orchestrator)
    prov="${1:-claude}"
    [ -f "$DIR/bus/tokens/orchestrator.token" ] || { echo "first: python3 scripts/team_bus.py token orchestrator"; exit 1; }
    out="$(paseo run --no-wait --quiet --title orchestrator --provider "$prov" --cwd "$ROOT" $(bus_env orchestrator) \
      "You are the team ORCHESTRATOR on the hub. Read coordination/ORCHESTRATOR.md and follow it. Start with team_status." 2>/dev/null)"
    id="$(printf '%s\n' "$out" | grep -E -o '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | tail -1)"
    [ -n "$id" ] || { echo "could not start the orchestrator:"; printf '%s\n' "$out"; exit 1; }
    echo "orchestrator agent $id (open it in the Paseo app, or: paseo attach $id)" ;;
  *) sed -n '2,11p' "$0"; exit 1 ;;
esac
