# NASA Space Apps 2026: Murcia team hub

Our team's shared workspace for the NASA Space Apps Challenge (Murcia, **13–15 Nov 2026**). It's built so that each
of us can plug in our own AI agent (Claude Code, Codex, Cursor, Gemini CLI) and have all four agents work on the same
project without stepping on each other.

## Plug in (5 minutes, each person)
```bash
git clone <repo-url> nasa-space-apps && cd nasa-space-apps
echo 'export SEAT=<yourname>' >> ~/.bashrc && source ~/.bashrc   # your seat name from context/team.md
claude            # or codex / cursor / gemini, from this folder
```
- Claude Code: approve the project hooks when asked, then type `/sync`. Use `/claim T-00N` to take a task and `/handoff` when you stop.
- Other agents: tell them "read AGENTS.md first and follow it". Gemini reads `GEMINI.md` (a link to AGENTS.md).
- Then fill your row in `context/team.md` and do task T-002 (accounts).

## Read in this order
1. `brainstorm/shortlist.md`: the 4 project options and my recommendation (5 min)
2. `brainstorm/challenge-analysis.md`: all 14 challenges analysed, local competition, scoring (20 min)
3. `context/README.md`: the event facts on one screen
4. `AGENTS.md`: the rules our agents follow (claiming tasks, git, logging)
5. `research/multi-agent-collaboration.md`: why we coordinate through git and not a live agent network

## Timeline
| When | What |
|---|---|
| Tue–Thu | Accounts (T-002), GitHub repo (T-001), read the brainstorm, vote in `brainstorm/votes.md`, set up your agent (T-005). **No project code.** |
| Fri 13 Nov | Resources and judging guide published → kill checks → decide main + backup (D-002). 17:00 welcome at Puertas de Castilla: ask about judging time, pitch format, prizes, overnight. |
| Sat 14, 09:00 | Hacking starts. 09:00–10:00 architecture + ownership map + tasks. Thin end-to-end demo by **Sat 20:00**. |
| Sun 15 | Polish, validation slide, video, pitch rehearsal. Demo-ready by early afternoon; submit by 18:00 (hard deadline 23:59). |

## Layout
`AGENTS.md` rules · `context/` facts · `brainstorm/` ideas · `research/` side research · `coordination/` board, log, decisions ·
`app/` code (from Saturday) · `submission/` project page, pitch, video · `scripts/board.py` task board.
