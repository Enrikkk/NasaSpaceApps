#!/usr/bin/env python3
"""PreToolUse hook: block Edit/Write outside the paths owned by $SEAT (see .claude/ownership.json).
Exit 2 = block (stderr shown to Claude). Any problem, unset SEAT, or unowned path -> allow (fail open).
Adapted from research/multi-agent-collaboration.md. Guards edit tools only, not shell edits."""
import json, os, sys

def under(rel, p):
    return rel == p.rstrip("/") or rel.startswith(p if p.endswith("/") else p + "/")

try:
    ev = json.load(sys.stdin)
    path = (ev.get("tool_input") or {}).get("file_path") or (ev.get("tool_input") or {}).get("notebook_path")
    if not path:
        sys.exit(0)
    root = os.environ.get("CLAUDE_PROJECT_DIR") or ev.get("cwd") or os.getcwd()
    rel = os.path.relpath(os.path.realpath(path), os.path.realpath(root))
    me = os.environ.get("SEAT", "")
    with open(os.path.join(root, ".claude", "ownership.json")) as f:
        own = {k: v for k, v in json.load(f).items() if not k.startswith("_")}
except Exception:
    sys.exit(0)
if not me or rel.startswith(".."):
    sys.exit(0)
if any(under(rel, p) for p in own.get(me, []) + own.get("shared", [])):
    sys.exit(0)
owner = next((k for k, v in own.items() if k != "shared" and any(under(rel, p) for p in v)), None)
if owner is None:
    sys.exit(0)
print(f"BLOCKED by team ownership rule: {rel} belongs to seat '{owner}', you are '{me}'. "
      f"Don't edit it. Append a request to coordination/questions.md for @{owner}, or ask your human "
      f"to change .claude/ownership.json.", file=sys.stderr)
sys.exit(2)
