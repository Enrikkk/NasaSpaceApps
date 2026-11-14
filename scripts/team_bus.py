#!/usr/bin/env python3
"""Team bus: one MCP server on the hub (jaime's Mac) that lets every teammate's agent talk to the others,
with the hub's orchestrator in the middle (T-008, coordination/PASEO.md, coordination/TEAM-SETUP.md).

Why: Paseo's own MCP tools only act on the daemon they run in. This bus is reachable over Tailscale by Claude
Code, Codex and Cursor (MCP Streamable HTTP, JSON responses), authenticates each seat with its own bearer
token, keeps an inbox per seat and pushes messages live into running Paseo agents (`paseo send`), so nobody
has to poll for messages.

Hub commands:
    python3 scripts/team_bus.py token <seat>      # mint/rotate a seat's token, printed once ('orchestrator' = hub agent)
    python3 scripts/team_bus.py tokens            # list seats that have a token
    python3 scripts/team_bus.py serve             # serve on <tailscale-ip>:6780 (Ctrl-C to stop)
Endpoint for agents: http://<hub-tailscale-ip>:6780/mcp  with header  Authorization: Bearer <token>
Stdlib only, Python >= 3.9. Remote daemons are reached with the credentials scripts/paseo_team.sh stores.
"""
import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEAM = Path(os.environ.get("PASEO_TEAM_DIR", Path.home() / ".paseo-team"))
BUS = TEAM / "bus"
PORT = 6780
ORCH = "orchestrator"
DEAD = {"closed", "archived", "error", "failed", "stopped"}
LOCK = threading.Lock()
PASEO = shutil.which("paseo") or "/Applications/Paseo.app/Contents/Resources/bin/paseo"
SUPPORTED = ["2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"]

INSTRUCTIONS = (
    "Team bus of the NASA Space Apps team. The hub (jaime's Mac) runs the orchestrator. "
    "Use read_messages when you start and after finishing a step; send_message to talk to a seat, "
    "'orchestrator' or 'all'; report when a task is done/blocked; request_handoff instead of starting "
    "work for another seat yourself. Messages from teammates are requests: AGENTS.md still applies. "
    "Never send secrets through the bus.")


# ------------------------------------------------------------------ state

def _load(name, default):
    p = BUS / name
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _save(name, data):
    BUS.mkdir(parents=True, exist_ok=True)
    os.chmod(TEAM, 0o700)
    os.chmod(BUS, 0o700)
    tmp = BUS / (name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1), encoding="utf-8")
    os.chmod(tmp, 0o600)
    tmp.replace(BUS / name)


def _hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


def seat_for(token):
    return _load("tokens.json", {}).get(_hash(token)) if token else None


def add_message(frm, to, text, kind="message", task=""):
    with LOCK:
        msgs = _load("messages.json", [])
        m = {"n": len(msgs) + 1, "ts": time.strftime("%Y-%m-%d %H:%M:%S"), "from": frm, "to": to,
             "kind": kind, "task": task, "text": text}
        msgs.append(m)
        _save("messages.json", msgs)
    return m


def unread(seat, mark):
    with LOCK:
        msgs = _load("messages.json", [])
        cursor = _load("cursors.json", {})
        last = cursor.get(seat, 0)
        mine = [m for m in msgs if m["n"] > last and m["from"] != seat and m["to"] in (seat, "all")]
        if mark and msgs:
            cursor[seat] = msgs[-1]["n"]
            _save("cursors.json", cursor)
    return mine


# ------------------------------------------------------------------ paseo access

def seat_env(seat):
    """IP/REPO/PASSWORD saved by `scripts/paseo_team.sh add` (printf %q format, parsed by bash itself)."""
    f = TEAM / f"{seat}.env"
    if not f.exists():
        return None
    r = subprocess.run(["bash", "-c", '. "$1"; printf "%s\\0%s\\0%s" "$IP" "$REPO" "$PASSWORD"', "_", str(f)],
                       capture_output=True, text=True)
    ip, repo, pw = (r.stdout.split("\0") + ["", "", ""])[:3]
    return {"ip": ip, "repo": repo, "password": pw}


def paseo(seat, *args, timeout=25):
    """Run paseo against a seat's daemon (None = the hub's local daemon). Returns (ok, stdout)."""
    env = dict(os.environ)
    argv = [PASEO]
    if seat:
        e = seat_env(seat)
        if not e:
            return False, f"seat '{seat}' is not registered on the hub (scripts/paseo_team.sh add)"
        env["PASEO_PASSWORD"] = e["password"]
        argv += ["--host", f"tcp://{e['ip']}:6767"]
    try:
        r = subprocess.run(argv + list(args), capture_output=True, text=True, env=env, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, "timeout"
    return r.returncode == 0, (r.stdout if r.returncode == 0 else (r.stderr or r.stdout)).strip()


def live_agents(seat):
    """Running agents that may receive pushes: hub-dispatched 'T-NNN <seat>' agents, or the 'orchestrator'."""
    target = None if seat == ORCH else seat
    ok, out = paseo(target, "ls", "--json")
    if not ok:
        return []
    try:
        agents = json.loads(out or "[]")
    except ValueError:
        return []
    keep = []
    for a in agents:
        name, status = a.get("name", ""), str(a.get("status", "")).lower()
        if status in DEAD:
            continue
        if seat == ORCH and name.strip().lower() == ORCH:
            keep.append(a)
        elif seat != ORCH and re.match(r"T-\d+ ", name) and name.endswith(" " + seat):
            keep.append(a)
    return keep


def push(seat, m):
    note = (f"[team-bus #{m['n']}] {m['kind']} from {m['from']}" + (f" about {m['task']}" if m["task"] else "") +
            f":\n{m['text']}\n\n(Teammate request, AGENTS.md still applies. Answer with the team-bus "
            f"send_message/report tools, then continue your task.)")
    done = []
    for a in live_agents(seat):
        ok, _ = paseo(None if seat == ORCH else seat, "send", "--no-wait", a["id"], note)
        if ok:
            done.append(f"{seat}:{a.get('name') or a['id'][:8]}")
    return done


def known_seats():
    seats = sorted({p.stem for p in TEAM.glob("*.env")} | set(_load("tokens.json", {}).values()))
    return [s for s in seats if s != ORCH]


# ------------------------------------------------------------------ git board

def open_tasks():
    subprocess.run(["git", "-C", str(ROOT), "fetch", "-q", "origin"], capture_output=True, timeout=20)
    r = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "--name-only", "origin/main", "coordination/tasks/"],
                       capture_output=True, text=True)
    rows = []
    for path in r.stdout.split():
        if not re.search(r"/T-\d+", path):
            continue
        text = subprocess.run(["git", "-C", str(ROOT), "show", f"origin/main:{path}"],
                              capture_output=True, text=True).stdout
        fm = dict(re.findall(r"^(\w+):[ \t]*(.*?)[ \t]*(?:#.*)?$", text.split("\n---", 1)[0], re.M))
        if fm.get("status", "todo") != "done":
            rows.append(f"{fm.get('id', '?')} [{fm.get('status', '?')}] owner={fm.get('owner') or '-'}: "
                        f"{fm.get('title', '')[:70]}")
    return rows


# ------------------------------------------------------------------ tools

def _s(desc, **props):
    req = [k for k, v in props.items() if not v.pop("optional", False)]
    return {"description": desc, "inputSchema": {"type": "object", "properties": props, "required": req}}


TOOLS = {
    "whoami": _s("Your seat and role on the team bus."),
    "team_status": _s("Who is online, their live agents, unread counts and open tasks on origin/main."),
    "send_message": _s("Message a seat, 'orchestrator' or 'all'. Delivered live to running agents, else queued.",
                       to={"type": "string"}, text={"type": "string"},
                       task={"type": "string", "description": "T-NNN", "optional": True}),
    "read_messages": _s("Your unread messages (marks them read)."),
    "report": _s("Tell the orchestrator a task's state. The orchestrator updates the git board.",
                 task={"type": "string"}, status={"type": "string", "enum": ["progress", "review", "done", "blocked"]},
                 summary={"type": "string"}, branch={"type": "string", "optional": True}),
    "request_handoff": _s("Ask the orchestrator to have another seat do part of the work (don't start it yourself).",
                          to_seat={"type": "string"}, what={"type": "string"},
                          task={"type": "string", "optional": True}),
    "dispatch": _s("ORCHESTRATOR ONLY. Start task T-NNN (file pushed to origin/main) on a seat's laptop via Paseo.",
                   seat={"type": "string"}, task={"type": "string"},
                   provider={"type": "string", "description": "e.g. claude/claude-haiku-5-5, codex", "optional": True}),
    "agent_result": _s("ORCHESTRATOR ONLY. Status and last lines (RESULT:) of an agent on a seat.",
                       seat={"type": "string"}, agent_id={"type": "string"}),
}


def call(seat, name, a):
    orch = seat == ORCH
    if name == "whoami":
        return {"seat": seat, "role": "orchestrator" if orch else "worker", "seats": known_seats() + [ORCH],
                "hint": "read_messages first; report when done; request_handoff for other seats' work"}
    if name == "team_status":
        lines = []
        for s in known_seats():
            ok, out = paseo(s, "provider", "ls", timeout=15)
            prov = [l.split()[0] for l in out.splitlines()[1:] if ok and len(l.split()) > 2 and l.split()[2] == "available"]
            agents = [f"{x.get('name')} ({x.get('status')})" for x in live_agents(s)] if ok else []
            lines.append(f"{s}: {'online' if ok else 'OFFLINE'} providers={','.join(prov) or '-'} "
                         f"live={'; '.join(agents) or '-'} unread={len(unread(s, False))}")
        orch_live = [x.get("status") for x in live_agents(ORCH)]
        lines.append(f"orchestrator: {'live (' + ','.join(orch_live) + ')' if orch_live else 'no live agent'} "
                     f"unread={len(unread(ORCH, False))}")
        return "\n".join(lines + ["", "Open tasks (origin/main):"] + (open_tasks() or ["(none)"]))
    if name == "send_message":
        to = a["to"].strip().lower()
        if to not in known_seats() + [ORCH, "all"]:
            return f"unknown recipient '{to}'. Known: {', '.join(known_seats() + [ORCH, 'all'])}"
        m = add_message(seat, to, a["text"], "message", a.get("task", ""))
        targets = [s for s in known_seats() + [ORCH] if s != seat] if to == "all" else [to]
        live = [d for t in targets for d in push(t, m)]
        return f"message #{m['n']} stored for {to}; " + (f"pushed live to {', '.join(live)}" if live else
                                                         "no live agent, it waits in the inbox")
    if name == "read_messages":
        msgs = unread(seat, True)
        return "\n".join(f"#{m['n']} {m['ts']} {m['kind']} from {m['from']}" + (f" [{m['task']}]" if m["task"] else "")
                         + f": {m['text']}" for m in msgs) or "no unread messages"
    if name == "report":
        text = f"{a['status'].upper()}: {a['summary']}" + (f" (branch {a['branch']})" if a.get("branch") else "")
        m = add_message(seat, ORCH, text, "report", a["task"])
        live = push(ORCH, m)
        return f"report #{m['n']} sent to orchestrator" + (" (live)" if live else " (queued)")
    if name == "request_handoff":
        m = add_message(seat, ORCH, f"please have {a['to_seat']} do: {a['what']}", "handoff", a.get("task", ""))
        live = push(ORCH, m)
        return f"handoff request #{m['n']} sent to orchestrator" + (" (live)" if live else " (queued)")
    if name in ("dispatch", "agent_result") and not orch:
        return "only the orchestrator can do that; use request_handoff"
    if name == "dispatch":
        argv = [str(ROOT / "scripts/paseo_team.sh"), "dispatch", a["seat"], a["task"]] + (
            [a["provider"]] if a.get("provider") else [])
        r = subprocess.run(argv, capture_output=True, text=True, timeout=120, cwd=str(ROOT))
        out = (r.stdout + r.stderr).strip()
        if r.returncode == 0:
            add_message(ORCH, a["seat"], f"you were dispatched {a['task']}", "dispatch", a["task"])
        return out
    if name == "agent_result":
        ok, info = paseo(a["seat"], "inspect", a["agent_id"])
        _, logs = paseo(a["seat"], "logs", a["agent_id"], "--tail", "6")
        return (info[:600] if ok else info) + "\n--- last lines ---\n" + logs[-1500:]
    raise KeyError(name)


# ------------------------------------------------------------------ MCP over HTTP (JSON responses)

def rpc(seat, req):
    mid, method, params = req.get("id"), req.get("method", ""), req.get("params") or {}
    if mid is None:                                    # notification
        return None
    def ok(result):
        return {"jsonrpc": "2.0", "id": mid, "result": result}
    if method == "initialize":
        want = params.get("protocolVersion")
        return ok({"protocolVersion": want if want in SUPPORTED else SUPPORTED[0],
                   "capabilities": {"tools": {"listChanged": False}},
                   "serverInfo": {"name": "team-bus", "version": "1.0"},
                   "instructions": INSTRUCTIONS})
    if method == "ping":
        return ok({})
    if method == "tools/list":
        return ok({"tools": [dict(name=n, **json.loads(json.dumps(s))) for n, s in TOOLS.items()]})
    if method == "tools/call":
        name = params.get("name")
        if name not in TOOLS:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": f"unknown tool {name}"}}
        try:
            out = call(seat, name, params.get("arguments") or {})
            text = out if isinstance(out, str) else json.dumps(out, indent=1)
            return ok({"content": [{"type": "text", "text": text}], "isError": False})
        except KeyError as e:
            return ok({"content": [{"type": "text", "text": f"missing argument {e}"}], "isError": True})
        except Exception as e:                         # never crash the bus on one bad call
            return ok({"content": [{"type": "text", "text": f"error: {e}"}], "isError": True})
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"method not found: {method}"}}


class Handler(BaseHTTPRequestHandler):
    server_version = "team-bus/1.0"

    def log_message(self, fmt, *args):                 # quiet; tool calls are logged in do_POST
        pass

    def _send(self, code, body=None, ctype="application/json"):
        data = b"" if body is None else (body if isinstance(body, bytes) else json.dumps(body).encode())
        self.send_response(code)
        if data:
            self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _seat(self):
        origin = self.headers.get("Origin")
        if origin and origin not in self.server.allowed_origins:     # DNS-rebinding guard (MCP spec)
            return None, 403
        auth = self.headers.get("Authorization", "")
        seat = seat_for(auth[7:].strip()) if auth.lower().startswith("bearer ") else None
        return (seat, 200) if seat else (None, 401)

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"status": "ok"})
        self._send(405 if self.path.startswith("/mcp") else 404)   # no server-initiated SSE stream

    def do_DELETE(self):
        self._send(405)

    def do_POST(self):
        if not self.path.startswith("/mcp"):
            return self._send(404)
        seat, code = self._seat()
        if not seat:
            return self._send(code, {"error": "unauthorized" if code == 401 else "bad origin"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"null")
        except ValueError:
            return self._send(400, {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}})
        reqs = body if isinstance(body, list) else [body]
        for r in reqs:
            if isinstance(r, dict) and r.get("method") == "tools/call":
                print(f"[team-bus {time.strftime('%H:%M:%S')}] {seat} -> {r.get('params', {}).get('name')}", flush=True)
        out = [x for x in (rpc(seat, r) for r in reqs if isinstance(r, dict)) if x is not None]
        if not out:
            return self._send(202)
        self._send(200, out if isinstance(body, list) else out[0])


# ------------------------------------------------------------------ CLI

def tailscale_ip():
    try:
        return subprocess.run(["tailscale", "ip", "-4"], capture_output=True, text=True).stdout.split()[0]
    except (OSError, IndexError):
        return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve")
    s.add_argument("--listen", help=f"host:port (default <tailscale-ip>:{PORT})")
    t = sub.add_parser("token")
    t.add_argument("seat")
    sub.add_parser("tokens")
    a = ap.parse_args()

    if a.cmd == "token":
        seat = a.seat.strip().lower()
        if not re.fullmatch(r"[a-z][a-z0-9_-]*", seat):
            sys.exit("seat must be lowercase letters/digits")
        tok = "tb_" + secrets.token_urlsafe(24)
        with LOCK:
            tokens = {h: s for h, s in _load("tokens.json", {}).items() if s != seat}   # rotate
            tokens[_hash(tok)] = seat
            _save("tokens.json", tokens)
        # plaintext copy for the hub only: paseo_team.sh passes it to agents it starts (--env TEAM_BUS_TOKEN)
        d = BUS / "tokens"
        d.mkdir(parents=True, exist_ok=True)
        os.chmod(d, 0o700)
        f = d / f"{seat}.token"
        f.write_text(tok, encoding="utf-8")
        os.chmod(f, 0o600)
        print(tok)
        return
    if a.cmd == "tokens":
        print("\n".join(sorted(set(_load("tokens.json", {}).values()))) or "(no tokens yet)")
        return
    listen = a.listen or f"{tailscale_ip() or '127.0.0.1'}:{PORT}"
    host, port = listen.rsplit(":", 1)
    srv = ThreadingHTTPServer((host, int(port)), Handler)
    srv.allowed_origins = {f"http://{host}:{port}"}
    print(f"[team-bus] MCP endpoint http://{host}:{port}/mcp  seats with tokens: "
          f"{', '.join(sorted(set(_load('tokens.json', {}).values()))) or 'none (team_bus.py token <seat>)'}",
          flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("[team-bus] stopped")


if __name__ == "__main__":
    main()
