@AGENTS.md

## Claude Code specifics

- Project skills in `.claude/skills/`: `/sync` (start of session), `/claim` (take or create a task),
  `/handoff` (log, update task, push). Use them; they implement AGENTS.md §2–5.
- When you spawn subagents, give them the task file path and the relevant `context/challenges/NN-*.md` path
  rather than re-explaining the hackathon.
- Keep `context/` as the shared memory of this project: if you learn something every agent should know
  (a data quirk, an API limit, a venue detail), add it to the right `context/` or `research/` file and log it,
  rather than keeping it only in your private memory.
