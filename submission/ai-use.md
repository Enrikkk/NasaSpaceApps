# Use of SI/AI (mandatory section)

> DRAFT written by gonzalo's agent on 2026-11-14 from what actually happened in the repo and the team logs. Every teammate should add or
> correct their own part before submitting. Claim nothing here that did not happen.

**AI tools used:** Claude Code (Anthropic) in several parallel sessions and sub-agents, one per teammate's laptop, coordinated through a
shared git repository and a message bus; other coding agents (Codex, Cursor) were used by some teammates **[each teammate: confirm]**.

**What the humans did:** the product idea and whiteboard session, the choice of challenge, region and demo parcel, the architecture and
scope decisions (D-002 to D-011, recorded in `coordination/DECISIONS.md`), the choice of data sources and the licence decisions
(for example accepting or rejecting a source), review of the numbers and of the legal rules, access to accounts (NASA Earthdata, Google
Cloud), the pitch, the video and the final decisions. Only humans decide; agents propose.

**What the AI did:** drafts of code (data pipelines, scoring engine, legal-rules table, API, tests, deployment), literature and
dataset research, transcription of whiteboard notes, documentation, and cross-checks of licences and of the Ley 3/2020 text against the
consolidated BOE. Every AI-written piece was kept in the repo with tests where possible and reviewed by a teammate **[confirm]**.

**AI inside the product:** the scoring engine computes everything (money, yields, water, success percentages, legal light, suitability)
with explicit rules and physics, and the card texts exist as deterministic templates. **The model never computes.** On top of that, the app
can show card texts **reworded by a local open-weights language model** (added on branch `integracion`, 2026-11-14). This is how it works:

- **Model:** gpt-oss-20b, quantisation Q4_K_M, served by Ollama on a team laptop (intended setup; the exact model name is read from
  `OLLAMA_MODEL`). **Licence of the model: por confirmar antes de entregar** (not recorded in the repo yet). Not yet tested at the time
  of writing; a small model (`granite3.3:2b`) was run only to test the checker.
- **No external provider, no API key, no cost.** The model runs on the team's own machine. Nothing is sent to a cloud service for this.
  Texts can be generated in advance and stored as files (`app/data/cache/narrativa/`), so the demo does not need the model to be running.
- **What it does:** takes a text the engine already produced and rewrites it in shorter, plainer Spanish for a farmer. It receives the
  template and a closed list of the figures that text contains.
- **What it does not do:** it does not compute, choose crops, change a figure, add facts or advice, give legal advice or promise results.
- **Verification (code: `app/backend/engine/decision/llm_rewrite.py`):** a deterministic checker reads every answer. It rejects any new
  figure, any missing figure, quantities written in words, forbidden promises, a lost caveat ("provisional", "supuesto", "proxy",
  "no sabemos"...), a text longer than the template, and markup. If it fails, the model is told exactly what failed and tries again, up to
  3 times. After the third failure the deterministic template is shown. A stored text is checked again against the current template before it
  is served, so an old or edited file cannot slip in a wrong figure. The card shows the model text only when it passed the checker.
- **Disclosure in the product:** the response says which texts were reworded by a model (`uso_ia`, `aviso` in `POST /narrativa`). Exact wording
  of the on-screen label: **[confirm with the frontend owner]**.
- **Log:** each attempt is kept locally in `app/data/cache/llm_log/` (ignored by git).

**What AI did not do:** decide the product, accept licence risks, or validate legal rules as legal advice. The tool states that it does
not replace the farmer or the technician.
