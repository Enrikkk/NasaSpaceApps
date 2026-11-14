#!/usr/bin/env python3
"""Autopilot watcher: wake this seat's coding agent only when a task is handed to it. No API, no MCP server.

The task board in git (coordination/tasks/*.md) stays the single source of truth (D-001). This script polls
`git fetch` (0 tokens) and only launches the agent CLI (Claude Code / Codex / Cursor, on your flat subscription)
when a task on origin/main has:

    owner: <your seat>
    status: todo
    auto: yes

Then it: claims the task on main -> creates the task branch in a private worktree -> runs the agent headless ->
commits + pushes the branch -> sets the task to review/blocked on main, publishes any follow-up tasks the agent
created for other seats, appends a LOG line. The agent only writes code; git is done here. Your own checkout is
never touched (the bot works in ../<repo>-autopilot).

Usage (from the repo root):
    python3 scripts/agent_watcher.py --once --dry-run          # what would run? touches nothing
    SEAT=jaime python3 scripts/agent_watcher.py --agent claude  # loop forever (Ctrl-C to stop)
    python3 scripts/agent_watcher.py --agent codex  --seat ana
    python3 scripts/agent_watcher.py --agent cursor --seat luis
    python3 scripts/agent_watcher.py --agent-cmd 'mytool run {prompt}'   # any other CLI

See coordination/AUTOPILOT.md. Stdlib only, Python >= 3.9.
"""
import argparse
import datetime as dt
import fcntl
import os
import platform
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = "coordination/tasks"
LOG_FILE = "coordination/LOG.md"

# {prompt} is replaced by the task prompt. The watcher does all git work, so agents need no git/network rights.
PRESETS = {
    "claude": ["claude", "-p", "{prompt}", "--permission-mode", "acceptEdits", "--max-turns", "80",
               "--allowedTools",
               "Read,Edit,Write,Glob,Grep,Bash(python3:*),Bash(pip:*),Bash(node:*),Bash(npm:*),Bash(npx:*),"
               "Bash(ls:*),Bash(cat:*),Bash(head:*),Bash(tail:*),Bash(wc:*),Bash(mkdir:*),"
               "Bash(git status:*),Bash(git diff:*),Bash(git log:*),Bash(git show:*)"],
    "codex": ["codex", "exec", "--full-auto", "{prompt}"],
    "cursor": ["cursor-agent", "-p", "--force", "--output-format", "text", "{prompt}"],
}

PROMPT = """You are the AUTOPILOT coding agent for seat '{seat}' in this repo (NASA Space Apps 2026 team).
You run unattended: nobody will answer questions, so make reasonable choices and write them down.

1. Read AGENTS.md, then your task file {task_path} (task {id}: {title}).
2. You are on git branch '{branch}' in a dedicated worktree. Do the task. Keep it small, working, demo-able.

Rules:
- Only change files inside the task's paths ({paths}), your own task file, and new task files (see below).
- Do NOT run git commit / push / checkout / merge / rebase. The watcher commits and pushes when you exit.
- Do NOT edit coordination/LOG.md or coordination/DECISIONS.md. The watcher logs for you.
- Never write secrets (tokens, keys) into files. Run whatever quick check/test exists for what you touched.
- If part of the work belongs to another seat, hand it over: create coordination/tasks/T-NNN-short-slug.md
  (next free number) with front matter
      id: T-NNN / title: ... / status: todo / owner: <their seat> / auto: yes / branch: /
      base: {branch} / paths: <their folders> / depends: {id}
  and a precise description with acceptance criteria (what files, what interface, how to test).
  Known seats: {seats}. Use `auto: no` if a human should do it.
- FINAL STEP, mandatory: append exactly one line at the very end of {task_path}:
      AUTOPILOT: done | <1-2 line result + how to run it>
  or  AUTOPILOT: blocked | <what is missing and what a human must do>
"""


# ---------------------------------------------------------------- helpers

def now():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def say(msg):
    print(f"[autopilot {dt.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def git(cwd, *args, check=True):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip() or r.stdout.strip()}")
    return r


def parse_front(text):
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = re.split(r"\s+#", v, 1)[0].strip()
    return meta


def set_front(text, fields):
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return text
    lines = m.group(1).splitlines()
    for k, v in fields.items():
        for i, line in enumerate(lines):
            if re.match(rf"^{re.escape(k)}\s*:", line):
                lines[i] = f"{k}: {v}"
                break
        else:
            lines.append(f"{k}: {v}")
    return "---\n" + "\n".join(lines) + "\n---" + text[m.end():]


def is_yes(v):
    return str(v).strip().lower() in ("yes", "true", "1", "y", "si", "sí")


def deps_of(meta):
    return [d for d in re.findall(r"T-\d+", meta.get("depends", ""))]


def slug_branch(task_file, meta):
    b = meta.get("branch", "").strip()
    if b and b not in ("main", "-"):
        return b
    stem = Path(task_file).stem                      # T-007-nisar-endpoint
    num = re.match(r"T-(\d+)", stem)
    rest = stem.split("-", 2)[2] if stem.count("-") >= 2 else "task"
    return f"t{num.group(1) if num else '000'}-{rest}"[:60]


def read_tasks_at(repo, ref):
    """{path: (meta, text)} for every task file at a git ref, without checking anything out."""
    r = git(repo, "ls-tree", "--name-only", ref, TASKS_DIR + "/", check=False)
    out = {}
    for path in r.stdout.split():
        if not re.search(r"/T-\d+.*\.md$", path):
            continue
        text = git(repo, "show", f"{ref}:{path}").stdout
        meta = parse_front(text)
        meta.setdefault("id", re.search(r"T-\d+", Path(path).name).group(0))
        out[path] = (meta, text)
    return out


def seats_from_team(repo):
    try:
        text = (Path(repo) / "context/team.md").read_text(encoding="utf-8")
    except OSError:
        return []
    seats = []
    for line in text.splitlines():
        m = re.match(r"^\|\s*([a-z][a-z0-9_-]*)\s*\|", line)
        if m and m.group(1) not in ("seat",):
            seats.append(m.group(1))
    return seats


def notify(title, msg, enabled):
    say(f"{title}: {msg}")
    if enabled and platform.system() == "Darwin":
        esc = lambda s: s.replace("\\", "\\\\").replace('"', '\\"')
        subprocess.run(["osascript", "-e", f'display notification "{esc(msg)}" with title "{esc(title)}"'],
                       capture_output=True)
    elif enabled and shutil.which("notify-send"):
        subprocess.run(["notify-send", title, msg], capture_output=True)


# ---------------------------------------------------------------- the watcher

class Watcher:
    def __init__(self, a):
        self.a = a
        self.repo = str(ROOT)
        self.seat = a.seat
        self.common = Path(git(self.repo, "rev-parse", "--git-common-dir").stdout.strip())
        if not self.common.is_absolute():
            self.common = (ROOT / self.common).resolve()
        self.wt = str(Path(a.worktree).resolve()) if a.worktree else str(ROOT.parent / f"{ROOT.name}-autopilot")
        self.logdir = self.common / "autopilot-logs"
        self.runs = []                                # timestamps of recent agent runs (quota guard)
        self.seats = a.seats.split(",") if a.seats else seats_from_team(self.repo)
        if self.seat not in self.seats:
            self.seats.append(self.seat)
        if a.agent_cmd:
            self.cmd = shlex.split(a.agent_cmd)
        else:
            self.cmd = list(PRESETS[a.agent])
        if "{prompt}" not in self.cmd:
            self.cmd.append("{prompt}")

    # --- selection ------------------------------------------------------------------------------
    def candidates(self, repo):
        tasks = read_tasks_at(repo, "origin/main")
        status_by_id = {m["id"]: m.get("status", "") for m, _ in tasks.values()}
        picks = []
        for path, (m, _) in sorted(tasks.items()):
            if m.get("owner") != self.seat or m.get("status") != "todo" or not is_yes(m.get("auto", "")):
                continue
            missing = [d for d in deps_of(m) if status_by_id.get(d) not in ("done", "review")]
            if missing:
                say(f"skip {m['id']}: waiting on {', '.join(missing)}")
                continue
            if int(m.get("chain") or 0) > self.a.max_chain:
                say(f"skip {m['id']}: chain={m.get('chain')} > {self.a.max_chain} (agent ping-pong guard), "
                    f"a human must set chain: 0 to allow it")
                continue
            picks.append((path, m))
        return picks

    # --- worktree -------------------------------------------------------------------------------
    def ensure_worktree(self):
        if not Path(self.wt).exists():
            say(f"creating private worktree {self.wt}")
            git(self.repo, "worktree", "add", "--detach", self.wt, "origin/main")
        if git(self.wt, "status", "--porcelain").stdout.strip():
            say("worktree had leftovers from a crashed run: stashing them (git -C <worktree> stash list)")
            git(self.wt, "stash", "push", "-u", "-m", f"autopilot-leftover {now()}", check=False)

    def to_main(self):
        git(self.wt, "fetch", "-q", "origin")
        git(self.wt, "checkout", "-q", "--detach", "origin/main")

    def push_main(self, build, what):
        """build() edits files on a fresh origin/main and returns True if something must be committed."""
        for attempt in range(5):
            self.to_main()
            if not build():
                return True
            git(self.wt, "add", "-A", TASKS_DIR, LOG_FILE)
            git(self.wt, "commit", "-q", "-m", what)
            if git(self.wt, "push", "-q", "origin", "HEAD:main", check=False).returncode == 0:
                return True
            say(f"push to main rejected (someone pushed first), retry {attempt + 1}/5")
            time.sleep(2 + attempt * 3)
        return False

    # --- one task -------------------------------------------------------------------------------
    def run_task(self, path, meta):
        tid, branch = meta["id"], slug_branch(path, meta)
        full = Path(self.wt) / path

        # 1. claim on main (the git push is the lock, AGENTS.md section 3)
        def claim():
            m = parse_front(full.read_text(encoding="utf-8")) if full.exists() else {}
            if m.get("owner") != self.seat or m.get("status") != "todo":
                raise LookupError("task changed on main before we could claim it")
            full.write_text(set_front(full.read_text(encoding="utf-8"),
                                      {"status": "doing", "branch": branch}), encoding="utf-8")
            with open(Path(self.wt) / LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"- {now()} | seat={self.seat} | {tid} | autopilot({self.agent_name()}) claimed, "
                        f"branch {branch} | next: agent running\n")
            return True
        try:
            if not self.push_main(claim, f"claim {tid} ({self.seat}, autopilot)"):
                say(f"could not claim {tid}, will retry next cycle")
                return
        except LookupError as e:
            say(f"{tid}: {e}")
            return
        claim_sha = git(self.wt, "rev-parse", "HEAD").stdout.strip()

        # 2. task branch: from base: <branch> (handed-over work), else existing remote branch, else main
        base = meta.get("base", "").strip()
        remote_has = lambda b: git(self.wt, "rev-parse", "--verify", "-q", f"origin/{b}", check=False).returncode == 0
        start = f"origin/{base}" if base and remote_has(base) else (
            f"origin/{branch}" if remote_has(branch) else claim_sha)
        git(self.wt, "checkout", "-q", "-B", branch, start)
        if start != claim_sha:                         # bring main's board + latest code into the branch
            if git(self.wt, "merge", "-q", "--no-edit", claim_sha, check=False).returncode != 0:
                git(self.wt, "merge", "--abort", check=False)
                git(self.wt, "checkout", claim_sha, "--", "coordination/")
                git(self.wt, "commit", "-q", "-m", f"{tid}: sync coordination/ from main", check=False)
        before = git(self.wt, "rev-parse", "HEAD").stdout.strip()

        # 3. run the agent
        prompt = PROMPT.format(seat=self.seat, task_path=path, id=tid, title=meta.get("title", ""),
                               branch=branch, paths=meta.get("paths", "?"), seats=", ".join(self.seats))
        argv = [prompt if x == "{prompt}" else x.replace("{prompt}", prompt) for x in self.cmd]
        self.logdir.mkdir(parents=True, exist_ok=True)
        log_path = self.logdir / f"{tid}-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
        notify("Autopilot", f"{tid} started ({self.agent_name()})", self.a.notify)
        say(f"agent output -> tail -f {log_path}")
        self.runs.append(time.time())
        code = self.exec_agent(argv, log_path)

        # 4. outcome: last 'AUTOPILOT:' line in the task file
        text = full.read_text(encoding="utf-8") if full.exists() else ""
        lines = [l for l in text.splitlines() if l.startswith("AUTOPILOT:")]
        verdict, summary = "review", "agent exited without the AUTOPILOT line; check the branch"
        if lines:
            parts = lines[-1][len("AUTOPILOT:"):].split("|", 1)
            verdict = "blocked" if "block" in parts[0].lower() else "review"
            summary = (parts[1] if len(parts) > 1 else parts[0]).strip()[:200]
        if code != 0:
            verdict, summary = "blocked", f"agent exit code {code} ({'timeout' if code == -9 else 'error'}); " \
                                          f"log: .git/autopilot-logs/{log_path.name} on {self.seat}'s laptop"

        # 5. commit + push the branch
        git(self.wt, "add", "-A")
        git(self.wt, "commit", "-q", "-m", f"{tid}: autopilot ({self.agent_name()}) {verdict}: {summary[:60]}\n\n"
            f"Run by scripts/agent_watcher.py for seat {self.seat}.", check=False)
        if git(self.wt, "push", "-q", "-u", "origin", branch, check=False).returncode != 0:
            say(f"could not push {branch}; it stays local in {self.wt}")
        after = git(self.wt, "rev-parse", "HEAD").stdout.strip()
        changed = git(self.wt, "diff", "--name-status", before, after, "--", TASKS_DIR + "/").stdout.splitlines()

        # 6. publish board changes to main: own task -> review/blocked, new tasks for other seats, LOG line
        own_text = git(self.wt, "show", f"{after}:{path}", check=False).stdout or text
        new_files = {}
        for row in changed:
            st, p = row.split("\t", 1)[0], row.split("\t")[-1]
            if p != path and st.startswith("A"):
                new_files[p] = git(self.wt, "show", f"{after}:{p}").stdout
            elif p != path:
                say(f"ignoring agent edit to someone else's task {p}")
        chain = int(meta.get("chain") or 0) + 1
        published = []

        def publish():
            published.clear()
            full.write_text(set_front(own_text, {"status": verdict, "branch": branch}), encoding="utf-8")
            taken = {re.search(r"T-\d+", f.name).group(0) for f in (Path(self.wt) / TASKS_DIR).glob("T-*.md")}
            for p, body in new_files.items():
                m = parse_front(body)
                tid_new = m.get("id") or re.search(r"T-\d+", p).group(0)
                if tid_new in taken:                   # number collision: second to push renames (AGENTS.md)
                    n = max(int(t[2:]) for t in taken) + 1
                    tid_new = f"T-{n:03d}"
                    p = re.sub(r"T-\d+", tid_new, p, 1)
                body = set_front(body, {"id": tid_new, "chain": chain})
                (Path(self.wt) / p).write_text(body, encoding="utf-8")
                taken.add(tid_new)
                published.append(f"{tid_new}->{m.get('owner', '?')}")
            handed = f" | handed over: {', '.join(published)}" if published else ""
            with open(Path(self.wt) / LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"- {now()} | seat={self.seat} | {tid} | autopilot({self.agent_name()}) {verdict}: "
                        f"{summary} | branch {branch}{handed}\n")
            return True
        ok = self.push_main(publish, f"{tid}: autopilot -> {verdict}")
        notify("Autopilot", f"{tid} -> {verdict}: {summary[:90]}" + ("" if ok else " (board NOT updated, push failed)"),
               self.a.notify)
        self.to_main()

    def exec_agent(self, argv, log_path):
        env = dict(os.environ, SEAT=self.seat, AUTOPILOT="1")
        with open(log_path, "w", encoding="utf-8") as log:
            shown = " ".join("<prompt>" if "AUTOPILOT coding agent" in x else shlex.quote(x) for x in argv)
            log.write(f"$ {shown}\n\n")
            log.flush()
            p = subprocess.Popen(argv, cwd=self.wt, env=env, stdout=log, stderr=subprocess.STDOUT,
                                 stdin=subprocess.DEVNULL, start_new_session=True)
            try:
                return p.wait(timeout=self.a.timeout_min * 60)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL)
                p.wait()
                return -9

    def agent_name(self):
        return self.a.agent if not self.a.agent_cmd else Path(self.cmd[0]).name

    # --- loop -----------------------------------------------------------------------------------
    def cycle(self):
        if git(self.repo, "fetch", "-q", "origin", check=False).returncode != 0:
            say("git fetch failed (Wi-Fi?), retrying next cycle")
            return
        picks = self.candidates(self.repo)
        if self.a.dry_run:
            if not picks:
                say(f"nothing for seat={self.seat} (needs owner: {self.seat}, status: todo, auto: yes)")
            for path, m in picks:
                say(f"WOULD RUN {m['id']} '{m.get('title', '')}' on branch {slug_branch(path, m)} with: "
                    f"{' '.join(self.cmd[:2])} ...")
            return
        if not picks:
            return
        self.runs = [t for t in self.runs if time.time() - t < 3600]
        if len(self.runs) >= self.a.max_runs_per_hour:
            say(f"quota guard: {len(self.runs)} runs in the last hour (max {self.a.max_runs_per_hour}), waiting")
            return
        self.ensure_worktree()
        self.to_main()
        path, m = picks[0]
        say(f"picked {m['id']} '{m.get('title', '')}'")
        self.run_task(path, m)

    def loop(self):
        say(f"seat={self.seat} agent={self.agent_name()} worktree={self.wt} every {self.a.interval}s "
            f"(Ctrl-C to stop)")
        while True:
            try:
                self.cycle()
            except Exception as e:                    # keep watching; never die on one bad task
                say(f"error: {e}")
            if self.a.once:
                return
            time.sleep(self.a.interval)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seat", default=os.environ.get("SEAT") or None, help="your seat (default $SEAT)")
    ap.add_argument("--agent", choices=sorted(PRESETS), default=os.environ.get("AUTOPILOT_AGENT", "claude"))
    ap.add_argument("--agent-cmd", default=os.environ.get("AUTOPILOT_CMD"),
                    help="custom command, {prompt} is replaced, e.g. 'claude -p {prompt} --model sonnet'")
    ap.add_argument("--interval", type=int, default=60, help="seconds between git fetches (default 60)")
    ap.add_argument("--max-runs-per-hour", type=int, default=3, help="quota guard (default 3)")
    ap.add_argument("--timeout-min", type=int, default=40, help="kill the agent after N minutes (default 40)")
    ap.add_argument("--max-chain", type=int, default=5, help="max agent-to-agent hand-overs in a row (default 5)")
    ap.add_argument("--worktree", help="bot worktree path (default ../<repo>-autopilot)")
    ap.add_argument("--seats", help="comma list of seats for hand-overs (default: from context/team.md)")
    ap.add_argument("--once", action="store_true", help="one cycle, then exit")
    ap.add_argument("--dry-run", action="store_true", help="only print what would run")
    ap.add_argument("--no-notify", dest="notify", action="store_false", help="no desktop notifications")
    a = ap.parse_args()
    if not a.seat:
        sys.exit("No seat. export SEAT=<your seat> (see context/team.md) or pass --seat.")
    w = Watcher(a)
    if not a.dry_run and not shutil.which(w.cmd[0]):
        sys.exit(f"'{w.cmd[0]}' not found on PATH. Install it or pass --agent-cmd.")
    lock = open(w.common / f"autopilot-{a.seat}.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        sys.exit("another autopilot watcher for this seat is already running on this machine")
    try:
        w.loop()
    except KeyboardInterrupt:
        say("stopped")


if __name__ == "__main__":
    main()
