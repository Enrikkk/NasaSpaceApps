#!/usr/bin/env python3
"""Print the task board from coordination/tasks/*.md front matter. No dependencies.

Usage: python3 scripts/board.py [--mine SEAT] [--open]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS = ROOT / "coordination" / "tasks"
ORDER = {"doing": 0, "blocked": 1, "review": 2, "todo": 3, "done": 4}


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.split("#", 1)[0].strip()
    meta.setdefault("id", path.stem.split("-")[0] + "-" + path.stem.split("-")[1])
    meta["file"] = path.name
    return meta


def main():
    args = sys.argv[1:]
    mine = args[args.index("--mine") + 1] if "--mine" in args else None
    only_open = "--open" in args
    rows = [parse(p) for p in sorted(TASKS.glob("T-*.md"))]
    if mine:
        rows = [r for r in rows if r.get("owner") == mine]
    if only_open:
        rows = [r for r in rows if r.get("status") in ("todo", "") and not r.get("owner")]
    rows.sort(key=lambda r: (ORDER.get(r.get("status", "todo"), 9), r["id"]))
    if not rows:
        print("(no tasks)")
        return
    w_title = min(max(len(r.get("title", "")) for r in rows), 60)
    print(f"{'ID':6} {'STATUS':8} {'OWNER':10} {'TITLE':{w_title}}  PATHS")
    for r in rows:
        print(f"{r['id']:6} {r.get('status',''):8} {r.get('owner','') or '-':10} "
              f"{r.get('title','')[:w_title]:{w_title}}  {r.get('paths','')}")
    seat = os.environ.get("SEAT")
    if seat:
        n = sum(1 for r in rows if r.get("owner") == seat and r.get("status") == "doing")
        print(f"\nseat={seat}: {n} task(s) in progress")


if __name__ == "__main__":
    main()
