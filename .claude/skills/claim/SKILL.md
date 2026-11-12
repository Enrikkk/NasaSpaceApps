---
name: claim
description: Claim an existing task or create-and-claim a new one on the Space Apps team board, pushing the claim before any work starts so other agents see it. Use when the user says claim T-NNN, take this task, I'll do X, or /claim new <title>.
---

# /claim T-NNN | /claim new <title>

Implements AGENTS.md §3. The claim is pushed **before** any code is written.

1. `git pull --rebase`.
2. Existing task: open `coordination/tasks/T-NNN-*.md`. If `owner` is another seat and status is `doing`, stop and tell the human who has it.
   New task: next free number from `ls coordination/tasks`; create `T-NNN-<slug>.md` with the front matter from AGENTS.md §3, a short description and acceptance criteria (ask the human for anything you can't infer). Fill `paths` honestly: the files/folders you expect to touch.
3. Check overlap: list other `doing` tasks whose `paths` overlap this one's. If any, warn the human and name the seat.
4. Set `owner: <seat>`, `status: doing`, `branch: tNNN-<slug>`. Commit only the task file: `git commit -m "claim T-NNN (<seat>)"`, then `git push`.
5. If the push is rejected: `git pull --rebase`; if the file now shows a different owner, the other seat won. Revert your claim and tell the human. If the number collided on a new task, renumber yours and push again.
6. Create/switch to the branch: `git switch -c tNNN-<slug>` (or `git switch` if it exists).
7. Append the claim line to `coordination/LOG.md`, commit, push.
