---
name: sync
description: Start-of-session catch-up for the Space Apps team hub. Pulls the repo, reads decisions, recent log, open questions and the task board, and briefs the human on what changed and what is theirs. Use at the start of every session, after a break, or when the user says sync / catch me up / what's going on.
---

# /sync

Implements AGENTS.md §2.

1. Run `git pull --rebase` (on local changes: `git stash && git pull --rebase && git stash pop`; report conflicts, don't resolve other seats' files silently).
2. Determine the seat: `$SEAT`, else `git config user.name`, matched against `context/team.md`. If unknown, ask the human once.
3. Read `coordination/DECISIONS.md` (all), the last 40 lines of `coordination/LOG.md`, `coordination/questions.md` (entries addressed to this seat or `all` without an answer), and run `python3 scripts/board.py`.
4. `git log --since="6 hours ago" --oneline --all | head -30` to see what others pushed.
5. Brief the human in at most ~8 lines:
   - what changed since their last log line (by whom),
   - their tasks in progress and anything blocking them,
   - unanswered questions addressed to them,
   - 1–3 unclaimed tasks that fit them (from `context/team.md` skills).
6. Don't claim or edit anything in this skill. Suggest `/claim` if they want something.
