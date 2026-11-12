# Four people, four coding agents, one repo: coordination options for NASA Space Apps Murcia (13-15 Nov 2026)

Research date: 2026-11-10. Sources: official Claude Code docs (fetched today, docs reflect Claude Code ~v2.1.3xx), repo READMEs fetched today, a handful of blog write-ups. Anything I could not confirm is tagged **[UNVERIFIED]**.

---

## (a) Recommendation for this weekend

**Use plain GitHub as the coordination layer, and make it enforceable with two small hooks. Do not build a live agent-to-agent network.** Concretely: one shared repo; a single `AGENTS.md` (with `CLAUDE.md` importing it) that holds the rules, an ownership map (one human + their agent owns each directory) and the workflow; GitHub Issues + a Project board as the task queue, claimed with assignee + `in-progress` label; one short-lived branch per task named `<person>/<task>`, rebased and pushed small and often; one `status/<name>.md` file per person as the "who is doing what" view (each file has exactly one writer, so it never conflicts); a `SessionStart` hook that does `git pull --rebase` and prints open issues + everyone's status into the agent's context; and a `PreToolUse` hook that blocks an agent from editing files owned by someone else (script below, tested). Agents "message" each other through issue comments and status files; humans use a group chat. The reason: every Claude Code feature that does live messaging or shared task lists today (agent teams, cross-session messaging, Remote Control) works only inside one machine or one claude.ai account, so it cannot link four different people's laptops. The third-party mesh tools that claim to do so are young, mostly localhost-only or LAN-only, and each costs 30-60 minutes of setup with real risk on venue Wi-Fi. Keep one optional stretch goal: MCP Agent Mail on one laptop over a phone hotspot, only if you have a spare hour before Friday and accept it is untested by us.

---

## What the evidence says (short)

1. **Claude Code native multi-agent features are single-machine or single-account.** Agent teams: mailbox and task list live in `~/.claude/teams/...` and `~/.claude/tasks/...` on the lead's disk; "one team per session ... can't share a team across sessions"; experimental, off by default (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`); no worktree isolation, so you must partition files by hand. Cross-session messaging (v2.1.224+, on by default) reaches "your" sessions: same machine over a Unix socket, other machines/cloud only "your" sessions via Remote Control under the same claude.ai login. It cannot message a teammate's session under a different account. Remote Control and cloud sessions are per-account, and a shared cloud session link is a read-only snapshot, not live ("their view doesn't update in real time").
2. **Anthropic's own large parallel-agent experiment used git as the coordination layer.** In the C-compiler project, agents claimed a task by writing a lock file into `current_tasks/`; if two chose the same task, git sync forced the second to pick another. Each agent had its own clone and pushed to a shared upstream. Merge conflicts were frequent but Claude resolved them. There was no orchestrator and no messaging. It worked for many independent problems and failed on one big coupled task (16 agents hit the same bug and overwrote each other).
3. **Community hackathon-style write-ups agree on the same three rules:** each session owns a file or folder (a team that placed 2nd in a 6-hour hackathon: "if two sessions edit the same file, merge conflicts erase the speedup"); put constraints in a file every agent loads (CLAUDE.md/AGENTS.md); parallelism pays on independent tasks and hurts on tightly coupled ones. Review/merge speed becomes the bottleneck, not generation speed.
4. **The "agent mesh" MCP tools are immature for cross-person use** (details in the table). Notably, Repowire's README says agents on different machines do **not** message each other; its relay only gives remote dashboard/MCP access. claude-peers-mcp is localhost-only.

---

## (b) Comparison table

"Cross-machine?" means: can agents run on **different people's laptops** and still see each other, live.

| # | Option | What it is | Cross-machine? | Setup | Cost | Maturity | Risk for this weekend |
|---|---|---|---|---|---|---|---|
| 1 | **GitHub repo + AGENTS.md/CLAUDE.md + Issues/Project board + branch-per-task + status files** (recommended) | Rules in a file every agent loads; queue = Issues; claim = assignee + label; one branch/PR per task | Yes (via GitHub) | 30-40 min | Free | Industry-standard pattern; Anthropic's C-compiler run used the same idea with lock files | Needs network to claim/push; assignee-claim is not atomic (two people can both be assigned) so keep area ownership as the real guard |
| 2 | **Git lock files** (`claims/<task>.txt`, push = claim) | Claim by pushing a file; non-fast-forward rejection means someone else got it first | Yes | 10 min on top of #1 | Free | Used by Anthropic's C compiler run | More ceremony than Issues; stale claims if an agent dies (add "claims older than 2 h are void") |
| 3 | **PreToolUse ownership hook** (script below) | Hard-blocks edits outside your owned paths. CLAUDE.md is only advice; hooks are enforced | n/a (per laptop, config shared via git) | 10 min | Free | Hooks are documented and stable; my script was tested locally on simulated hook input only, **not inside a live Claude Code session** | Env var `HACK_OWNER` must be set on each laptop; fails open on any error |
| 4 | **Claude Code agent teams** | One lead session spawns teammates with shared task list + SendMessage | **No** (one machine, one session) | 5 min (set env var) | Token cost multiplies per teammate | Experimental; documented limits (no resume of in-process teammates, task status lag, one team per session) | Fine *inside one person's laptop* for a research/review burst; useless for linking four people |
| 5 | **Cross-session messaging** (`ListAgents`, `SendMessage`) | Claude messages your other sessions, same machine or via Remote Control | Only across **your own** sessions/account | 0 (on by default v2.1.224+) | Free | Documented, current | Cannot reach a teammate's account. Messages arrive as untrusted peer text and cannot grant permissions |
| 6 | **Cloud sessions** (`claude --cloud "task"`) / Remote Control | Runs on Anthropic VM; clones from GitHub, pushes a branch | Per account, but each person can fire off long tasks that survive laptop sleep/Wi-Fi drops | 15 min (GitHub App or `/web-setup`) | Included in Pro/Max/Team limits, counts toward usage | Documented; needs claude.ai login (not API key) | Burns each person's rate limit; session must be able to push to repo; not shared between people |
| 7 | **Beads** (`bd`) <https://github.com/steveyegge/beads> | Git/Dolt-backed dependency-aware issue tracker for agents; `bd ready`, `bd update --claim` | Yes, via `bd dolt push/pull` to the git remote | 20-30 min | Free (MIT) | ~28.7k stars, ~11.6k commits (page did not show last commit date) | 1.1k open issues; Dolt sync/upgrade quirks documented; HTTP backend experimental. Overkill for 36 h unless someone already knows it |
| 8 | **MCP Agent Mail (Rust)** <https://github.com/Dicklesworthstone/mcp_agent_mail_rust> | MCP server: agent identities, inbox/outbox, advisory file reservations + git pre-commit guard, web UI | Yes in principle: run `am serve-http --host 0.0.0.0` on one machine, others connect to `/mcp/` with bearer token (README has no multi-laptop walkthrough) | 30-60 min **[UNVERIFIED, I did not run it]** | Free; license is MIT with an OpenAI/Anthropic rider (read it) | 244 stars, 6,154 commits (very active); Python original <https://github.com/Dicklesworthstone/mcp_agent_mail> ~2.2k stars is **superseded** | Installer is `curl | bash` and needs `minisign`; the host laptop is a single point of failure; reserved-file guard can block commits unexpectedly |
| 9 | **Repowire** <https://github.com/prassanna-ravishankar/repowire> | Local daemon + MCP; Claude Code/Codex/OpenCode/Pi peers `ask`/`notify` each other | **No** between laptops: README says relay only gives remote dashboard/MCP access | 15 min | Free (MIT) | 272 stars, 837 commits; requires tmux, Claude Code 2.1.224+; v0.14 "in progress" | Solves one-person-many-repos, not four people |
| 10 | **claude-peers-mcp** <https://github.com/louislva/claude-peers-mcp> | Broker on localhost:7899; sessions list peers and push messages | **No** ("everything is localhost-only") | 10 min | Free (MIT) | 2.2k stars but only 7 commits | Needs Bun, claude.ai login and the `--dangerously-load-development-channels` flag; README example also uses `--dangerously-skip-permissions` |
| 11 | **SLM Mesh** <https://github.com/qualixar/slm-mesh> | Peer messaging, shared KV, advisory locks; LAN WebSocket + shared secret | LAN only, same Wi-Fi/subnet | 20 min **[UNVERIFIED]** | Free; Elastic License 2.0 | 16 stars, 26 commits, no releases | README contradicts itself (says broker cannot bind 0.0.0.0, cross-machine setup needs exactly that); venue Wi-Fi often isolates clients, which would break LAN discovery |
| 12 | **GitHub MCP server** <https://github.com/github/github-mcp-server> | Official MCP for issues, PRs, projects (remote at `https://api.githubcopilot.com/mcp/`) | Yes (it is GitHub) | 5 min | Free (MIT) | 34.4k stars | Optional: `gh` CLI does the same with fewer moving parts; agents can use `gh` directly |
| 13 | **Notion / Linear MCP as the board** | Hosted board instead of Issues | Yes | 15 min | Free tiers **[UNVERIFIED]** | Not researched in detail | Second tool to keep in sync with git; issues in-repo are closer to the code |
| 14 | **Shared VPS + tmux, each person their own Unix user and clone** | All four agents run on one Linux box; humans SSH in | Yes (SSH) | 60-120 min (accounts, auth, toolchain, Claude login per person) **[UNVERIFIED]** | ~EUR 5-15 for the weekend **[UNVERIFIED]** | Old, solid technique | Wi-Fi drops hit typing latency (mosh/tmux help); one box is a single point of failure; never share one Claude login across people (check Anthropic's terms) |
| 15 | **GitHub Codespaces** | Per-person cloud dev box | Each person has their own; not a shared live box | 10 min | Free tier: 120 compute-hours/month (Free) or 180 (Pro); 2-core = $0.18/h beyond that | Mature | 4-core for 36 h = 144 core-hours, over the free quota; you still need GitHub-based coordination on top |
| 16 | **Tailscale (free Personal plan)** to reach a laptop/VPS across venue Wi-Fi | Private network so an Agent Mail server or SSH works despite client isolation | Yes | 15 min per person | Free: up to 6 users, unlimited devices, non-commercial **[check terms]** | Mature | Extra moving part; only needed if you adopt #8 or #14 |
| 17 | **VS Code Live Share / Coder / Ona (Gitpod)** | Real-time co-editing / managed dev environments | - | - | - | **Not researched** | Live co-editing of the same files is exactly what ownership rules are meant to prevent |

---

## (c) Setup recipe (target: 45 minutes, do it Thursday 12 Nov, before the clock starts)

Roles: one person is the "repo captain" for steps 1-5; everyone else does step 6 on their laptop. Replace `alice/bob/carol/dave` with real names and fill the ownership map from your project plan.

### 1. Create the repo and the skeleton (captain, 10 min)

```bash
gh repo create <org-or-you>/nasa-space-apps-2026 --private --clone && cd nasa-space-apps-2026
mkdir -p status .claude/hooks docs
```

Add all four as collaborators with write access (repo Settings > Collaborators). Give `main` light protection only: no force-push; do not require reviews (a 36 h event cannot wait for approvals) but do require pull requests if you want CI to gate, otherwise allow direct merges after rebase.

### 2. One rules file for every agent

`AGENTS.md` is read natively by Codex; Claude Code reads `AGENTS.md` only when there is no `CLAUDE.md`, so create a `CLAUDE.md` that imports it (the docs' "share one file with other coding tools" pattern). Gemini CLI does not read AGENTS.md by default; add `.gemini/settings.json` with `{"context":{"fileName":["AGENTS.md","GEMINI.md"]}}` **[from third-party docs mirror, verify]**. Cursor: AGENTS.md support **[UNVERIFIED]**; fallback is to paste "read AGENTS.md first" into Cursor's rules.

`CLAUDE.md`:
```markdown
@AGENTS.md
```

`AGENTS.md` (edit the bracketed parts; keep it under about 80 lines, agents lose rules in long files):
```markdown
# Project: <name> - NASA Space Apps 2026 Murcia (deadline: Sun 15 Nov, <time>)
Goal in one sentence: <...>. Stack: <...>. Run: `<cmd>`. Test: `<cmd>`.

## Ownership (HARD RULE)
Each directory has one owner. Only the owner's agent edits it. To change someone else's area,
open or comment on a GitHub issue assigned to them; do not edit their files.
- alice: backend/ data/
- bob: frontend/
- carol: ml/ notebooks/
- dave: docs/ demo/ deploy/   (also owns the pitch)
- shared (anyone, keep edits tiny, rebase first): README.md, AGENTS.md, package manifests

## Workflow
1. Start of session: the hook already pulled and listed open issues + status. Read `status/*.md`.
2. Pick work ONLY from GitHub Issues labelled `ready` that are in YOUR area. Claim it:
   `gh issue edit <n> --add-assignee @me --add-label in-progress --remove-label ready`
   Re-check the issue has no other assignee first. Never take an issue assigned to someone else.
3. Branch: `git switch -c <yourname>/<short-task>` from fresh `main`.
4. Commit small. Before every push: `git pull --rebase origin main`. Push at least every 30 min.
5. Merge to main yourself when tests pass: `gh pr create --fill && gh pr merge --squash --delete-branch`.
6. Update ONLY your own file `status/<yourname>.md` (3 lines: doing / done / blocked). Never edit others' status files.
7. Close the issue with a one-line comment saying what changed and where.
8. Need something from another area? Comment on their issue, label it `needs-<name>`, and move on to something else.

## Rules
- Never force-push. Never edit generated/lock files by hand. Never commit secrets (.env is gitignored).
- Do not start a task not in an issue. If you discover work, open an issue first.
- Interfaces between areas live in `docs/contracts.md` (API shapes, file formats). Change a contract only via an issue both owners comment on.
- Demo freeze: from Sun 09:00 only fixes labelled `demo-blocker`.
```

### 3. Task board (captain, 5 min)

```bash
gh label create ready --color 0E8A16; gh label create in-progress --color FBCA04
gh label create demo-blocker --color B60205
for n in alice bob carol dave; do gh label create needs-$n --color 1D76DB; done
```
Create the GitHub Project (Projects > New > Board) with columns Ready / In progress / Done, auto-add issues. Seed 12-20 issues, each small (1-3 hours), each with an owner area and acceptance criteria. Ask one agent to draft the issue list from the project brief, then a human prunes it. Rule of thumb from the C-compiler write-up and the agent-teams docs: tasks must be independent, self-contained, with a testable deliverable.

### 4. Shared project settings and hooks (captain, 10 min)

Commit `.claude/settings.json` (shared by everyone, per the docs project settings are checked in):

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command",
        "command": "git pull --rebase --autostash -q 2>&1 | tail -2; echo '--- OPEN ISSUES ---'; gh issue list --state open --limit 40 2>/dev/null; echo '--- STATUS FILES ---'; cat status/*.md 2>/dev/null" } ] }
    ],
    "PreToolUse": [
      { "matcher": "Edit|Write|MultiEdit",
        "hooks": [ { "type": "command",
          "command": "python3 -I \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/ownership.py" } ] }
    ]
  }
}
```
(The JSON shape for `PreToolUse` with `matcher: "Edit|Write"` and `$CLAUDE_PROJECT_DIR` is copied from the hooks guide; SessionStart stdout being added to Claude's context is documented there too.)

`.claude/ownership.json`:
```json
{ "alice": ["backend/", "data/"], "bob": ["frontend/"], "carol": ["ml/", "notebooks/"],
  "dave": ["docs/", "demo/", "deploy/", "status/dave.md"],
  "shared": ["README.md", "AGENTS.md", "CLAUDE.md", "status/"] }
```
(Putting `status/` in `shared` is intentional so each agent can write its own status file; the one-writer rule is a convention.)

`.claude/hooks/ownership.py` (tested locally against simulated hook JSON: allowed own path, blocked other owner's path, allowed unowned path, allowed when `HACK_OWNER` is unset):
```python
#!/usr/bin/env python3
"""PreToolUse hook: block Edit/Write/MultiEdit outside the paths owned by $HACK_OWNER.
Exit 2 = block, stderr is shown to Claude. Any parse problem -> allow (fail open)."""
import json, os, sys
try:
    ev = json.load(sys.stdin)
    path = (ev.get("tool_input") or {}).get("file_path")
    if not path:
        sys.exit(0)
    root = os.environ.get("CLAUDE_PROJECT_DIR") or ev.get("cwd") or os.getcwd()
    rel = os.path.relpath(os.path.realpath(path), os.path.realpath(root))
    me = os.environ.get("HACK_OWNER", "")
    own = json.load(open(os.path.join(root, ".claude", "ownership.json")))
except Exception:
    sys.exit(0)
if not me:
    sys.exit(0)
allowed = own.get(me, []) + own.get("shared", [])
if any(rel == a.rstrip("/") or rel.startswith(a if a.endswith("/") else a + "/") for a in allowed):
    sys.exit(0)
owner = next((k for k, v in own.items() if k != "shared" and any(rel.startswith(a) for a in v)), None)
if owner is None:
    sys.exit(0)  # unowned path: allow (claim it in ownership.json afterwards)
print(f"BLOCKED: {rel} belongs to '{owner}', you are '{me}'. Do not edit it. "
      f"Open a GitHub issue / comment for {owner} instead, or ask your human to change .claude/ownership.json.", file=sys.stderr)
sys.exit(2)
```
Caveat: this guards the Edit/Write tools only. An agent can still change files through Bash (`sed -i`, `echo >`). Say so in AGENTS.md ("do not use shell to edit files outside your area") and rely on the pull-request/diff glance for the rest. Also note that a `git pull --rebase` will rewrite other people's files on disk; that is fine, it is not an agent edit.

Also commit: `.gitignore` (include `.claude/settings.local.json`, `.env`), empty `status/<name>.md` for each person, and `docs/contracts.md`.

### 5. Push and verify (captain, 2 min)
`git add -A && git commit -m "coordination skeleton" && git push -u origin main`

### 6. Each teammate's laptop (10 min each, in parallel)

```bash
gh auth login                          # once; needed for gh issue/pr commands
git clone git@github.com:<org>/nasa-space-apps-2026.git && cd nasa-space-apps-2026
export HACK_OWNER=alice                # put in ~/.bashrc or ~/.zshrc; use YOUR name as in ownership.json
claude                                 # approve the project hooks/settings when prompted
```
Smoke test (do this together, 5 min): in Claude Code ask "list open issues and say which are yours", then ask it to edit a file in someone else's folder; it must be refused with the BLOCKED message. If the block does not fire, check `/hooks`, and whether `HACK_OWNER` is visible (`echo $HACK_OWNER` in the same shell you launched `claude` from). Using `HACK_OWNER` via a `settings.local.json` `env` block is another route but I did not test that the hook subprocess sees it, so prefer the shell export.

Codex CLI: it reads `AGENTS.md` natively; the ownership hook does not apply, so the rules are advice only for Codex/Cursor/Gemini agents. Give those agents a smaller, clearly separate area (e.g. `notebooks/` or `docs/`).

### 7. Rhythm during the hackathon
- Every 60-90 min: 2-minute standup in the human chat (what merged, what is blocked, anything the contracts need).
- Everyone `git pull --rebase` before starting a new task; the SessionStart hook handles it only at session start, so remind agents in AGENTS.md (done in step 4 of the workflow).
- Captain merges nothing special; everyone merges own PRs. The "integration check" is one human running the app from fresh `main` every few hours.
- Friday night: tag `v0-skeleton`. Saturday 18:00 and Sunday 08:00: tag `checkpoint-N`. A tag is your rollback if an agent breaks `main`.

### Optional stretch (only if the base works by Thursday evening): live messaging with MCP Agent Mail
Run `am serve-http --host 0.0.0.0` on one laptop (Rust build install: `curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/mcp_agent_mail_rust/main/install.sh" | bash`, needs `minisign`), put it behind a phone hotspot or Tailscale, and add it to a shared `.mcp.json`:
```json
{ "mcpServers": { "agent-mail": { "type": "http", "url": "http://<host-ip>:8765/mcp/",
    "headers": { "Authorization": "Bearer ${AGENT_MAIL_TOKEN}" } } } }
```
(The `${VAR}` expansion in `.mcp.json` `url` and `headers`, and the approval prompt for project-scoped servers, are per the Claude Code MCP docs. The Agent Mail URL path and token behaviour come from the README summary; **I did not run it, and its README has no multi-laptop walkthrough**, so budget an hour and decide at 18:00 Friday whether it is worth keeping.)

### Using Claude Code features that DO help
- **Within one laptop**: a person can let their Claude spawn subagents freely (cheap). Agent teams are fine for a one-off parallel research/review burst (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`), not for the main build; they add token cost and need file partitioning.
- **Flaky Wi-Fi**: `claude --cloud "<task>"` runs on Anthropic's VM against your pushed branch, keeps running if the laptop sleeps, and you can follow up with `claude -p "msg" --cloud <session-id>`. Requires a claude.ai login and GitHub access (Claude GitHub App or `/web-setup`). Push first; it clones the remote, not your working tree.
- **Several agents on one laptop** (e.g. a person runs a backend agent and a test agent): use `claude --worktree`/git worktrees so they do not share a checkout (Anthropic docs: worktrees isolate sessions you run yourself).
- Skills/commands: anything under `.claude/` committed to the repo is shared by `git pull`; no plugin marketplace needed. (Plugin marketplaces via git exist; I did not re-verify the syntax today.)

---

## Is one shared machine better than four laptops?

For this weekend, **no, with one exception.** Pros of one VPS/Codespace-style box: identical environment, shared dev server/ports/database, teammates can attach to each other's tmux to watch an agent live, work survives a laptop closing. Cons: setup is longer than your one-hour budget (four Unix accounts, four Claude logins, toolchain, SSH keys), every keystroke depends on venue Wi-Fi (mosh/tmux mitigate but do not remove it), one box is a single point of failure, and four agents in one checkout is the exact collision the write-ups warn about (give each person their own clone there too, which removes most of the benefit). GitHub Codespaces are per-person (not a shared live session) and 4-core for 36 h exceeds the free 120-hour quota. **Exception:** one cheap VPS as the *deploy/demo target* (shared database, public URL) is worth having; that is separate from where agents run.

---

## (d) Failure modes and how to avoid them

| Failure | Why it happens | Avoidance |
|---|---|---|
| Two agents edit the same file; one overwrites the other | No ownership; "agents don't know they're sharing a filesystem" (Intility/dev.to write-ups) | Ownership map + PreToolUse hook; shared files tiny and rebase-first; contracts in `docs/contracts.md` |
| Two agents build the same feature | Both read the same open issues; assignee is not exclusive on GitHub | Area ownership decides who may pick what; `in-progress` label + assignee; read issues fresh at task start |
| Stale claim (`in-progress` forever after an agent/laptop died) | Agents crash, humans forget | Whoever sees an `in-progress` issue with no commit in 2 h pings the assignee in chat, then reassigns |
| Big coupled task serialises everyone (the C-compiler "kernel" failure) | One monolithic goal | Split into independent issues with explicit interfaces; if the whole team is stuck on one bug, put ONE agent on it |
| Context drift: agent A's assumptions about an API differ from agent B's | Each agent has only its own context window; lead context does not carry (agent-teams docs) | Contracts file; agents must read it at start; changes to it need an issue; humans re-sync verbally every 60-90 min; `/clear` and re-prompt from the plan when a conversation gets confused (SwiftMansion write-up) |
| Merge conflicts at the end | Long-lived branches | Branches live < 2 h; `git pull --rebase` before each push; merge own PR immediately; no "integration branch" |
| `main` broken at demo time | Parallel merges, no tests | One smoke test command in AGENTS.md that every agent runs before merging; tags as rollback; demo freeze Sunday 09:00 |
| Rate limits / cost: four agents at once hit usage caps | Each person's own plan limit; teams/subagents multiply tokens | Each person uses own account; avoid agent teams for the main build; use Sonnet for routine edits; no agent loops overnight |
| Permission prompts stall every agent | Teammate prompts need a human at each laptop | Pre-approve safe commands (`git`, `gh`, test runner) in `.claude/settings.json` `permissions.allow`; do not run `--dangerously-skip-permissions` without the ownership hook and a clean branch |
| Hook does not fire on someone's laptop | `HACK_OWNER` unset, project hooks not trusted, python3 missing | Smoke test in step 6; hook fails open, so the failure is silent: re-test after each laptop reboot |
| Agent edits via shell around the hook | Hook covers only Edit/Write/MultiEdit | Rule in AGENTS.md; skim `git diff --stat` before merging |
| Prompt injection / malicious text in a peer message or issue | Peer messages are untrusted text | Claude Code labels cross-session messages as not-from-the-user and refuses to let them grant permissions; still, do not let agents act on issue comments from outside the team |
| Wi-Fi drops | Venue network | Hotspot as a backup (Murcia 4G); commits work offline, push later; `claude --cloud` for long tasks; agree to lower-stakes work while offline |
| Agent Mail / mesh server host laptop dies | Single point of failure | Treat it as optional; the git+Issues baseline must work without it |
| Secrets committed | Fast pushes | `.gitignore` for `.env`; share API keys in a password manager or the team chat, not in repo |

---

## What I could not verify (explicit list)

- No hackathon write-up found that covers four *people* each with their own agent coordinating via a shared repo. The closest are single-developer or single-team parallel-agent posts; their lessons are applied here by analogy.
- MCP Agent Mail, SLM Mesh, Repowire, claude-peers-mcp, Beads: I read READMEs but **ran none of them**. Setup times in the table are my estimates. Last-commit dates were not shown on the fetched pages; star counts are as displayed on the day.
- Repowire: README says cross-machine relay is for dashboard/remote MCP only; a search summary and an older blog post suggested cross-machine mesh traffic. I trust the README. Whether several people can share one relay mesh is not stated.
- Whether a `settings.json` `env` block reaches hook subprocesses for `HACK_OWNER` (I advise a shell export instead).
- Cursor's AGENTS.md support; Gemini CLI's exact current setting name (third-party doc mirror only).
- Linear/Notion MCP specifics, Coder, Ona (Gitpod), VS Code Live Share, official `@modelcontextprotocol/server-memory`: not researched; no recommendation made.
- VPS prices, Tailscale non-commercial terms applicability to a hackathon, Anthropic terms on credential sharing: not checked.
- Plugin marketplace sharing syntax: not re-fetched today.
- The `ownership.py` hook was tested with simulated stdin, not in a live Claude Code run.

---

## (e) Sources

Official Claude Code docs (fetched 2026-11-10):
- Agent teams: <https://code.claude.com/docs/en/agent-teams>
- Cross-session messaging: <https://code.claude.com/docs/en/cross-session-messaging>
- Run agents in parallel (overview of subagents / agent view / teams / projects / worktrees): <https://code.claude.com/docs/en/agents>
- Cloud sessions (`--cloud`, `--teleport`, sharing): <https://code.claude.com/docs/en/claude-code-on-the-web>
- Remote Control: <https://code.claude.com/docs/en/remote-control>
- Memory / CLAUDE.md / AGENTS.md: <https://code.claude.com/docs/en/memory>
- Hooks guide: <https://code.claude.com/docs/en/hooks-guide>
- MCP (`.mcp.json`, project scope, env expansion): <https://code.claude.com/docs/en/mcp>
- Docs index: <https://code.claude.com/docs/llms.txt>

Anthropic engineering:
- Building a C compiler with parallel Claudes (lock files in `current_tasks/`): <https://www.anthropic.com/engineering/building-c-compiler>

Repos and tools:
- Beads: <https://github.com/steveyegge/beads>
- MCP Agent Mail (Rust): <https://github.com/Dicklesworthstone/mcp_agent_mail_rust>
- MCP Agent Mail (Python, superseded): <https://github.com/Dicklesworthstone/mcp_agent_mail>
- Repowire: <https://github.com/prassanna-ravishankar/repowire> and <https://dev.to/prassannaravishankar/repowire-a-mesh-network-for-ai-coding-agents-3h2b>
- claude-peers-mcp: <https://github.com/louislva/claude-peers-mcp>
- SLM Mesh: <https://github.com/qualixar/slm-mesh>
- GitHub MCP server: <https://github.com/github/github-mcp-server>
- GitHub Codespaces billing: <https://docs.github.com/en/billing/concepts/product-billing/github-codespaces>
- Tailscale pricing: <https://tailscale.com/pricing>
- Gemini CLI GEMINI.md docs: <https://geminicli.com/docs/cli/gemini-md/>

Write-ups (experience reports, not controlled studies):
- Torq team, 2nd place in a 6-hour hackathon with parallel Claude sessions, one-owner-per-file rule: <https://inbarshirizly.substack.com/p/coming-soon>
- Running multiple Claude Code agents in parallel without collisions (worktrees): <https://dev.to/yureki_lab/how-i-run-multiple-claude-code-agents-in-parallel-without-collisions-3pbk>
- What I learned running 3 Claude agents in parallel for a week: <https://hackathon.swmansion.com/blog/what-i-learned-running-3-claude-agents-in-parallel-for-a-week/>
- Agent teams and git worktrees (Intility; page returned 403 to my fetcher, content known only from a search summary): <https://engineering.intility.com/article/agent-teams-or-how-i-learned-to-stop-worrying-about-merge-conflicts-and-love-git-worktrees>
- Agent teams setup guide with cost anecdote (secondary, unverified claims): <https://www.mejba.me/blog/claude-code-agent-teams-setup-guide>
- AGENTS.md coordination patterns (hypothetical templates, not a standard): <https://codex.danielvaughan.com/2026/09/22/agents-md-multi-agent-manifest-pattern-library-ten-coordination-patterns-codex-cli/>

---

## Addendum (2026-11-10): reconciliation with the repo's existing AGENTS.md

The NasaSpaceApps hub already contains an `AGENTS.md`, `CLAUDE.md` (imports it) and `/sync`, `/claim`, `/handoff` skills. They implement **option 2 (git task files as locks)** rather than GitHub Issues: claim = edit `coordination/tasks/T-NNN-*.md` and push before coding, so a rejected push means someone else got it first (the same compare-and-swap idea as Anthropic's `current_tasks/` lock files, and it is race-safe where GitHub assignees are not). Use that design as is. From this report, still worth adding on top of it:
1. The `PreToolUse` ownership hook (section c, step 4), driven by the `paths:` field of `doing` tasks or a small `.claude/ownership.json`. Not yet in the repo.
2. A `SessionStart` hook that runs `git pull --rebase --autostash` and `python3 scripts/board.py` (what `/sync` does manually).
3. The failure-mode table (section d), especially: stale `doing` claims older than 2 h, branches living under 2 h, one smoke-test command before merging, demo freeze, rollback tags.
Skip the GitHub Issues/Project steps unless the team prefers a visual board; two queues will drift.
