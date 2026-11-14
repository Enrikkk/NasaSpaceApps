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

**AI inside the product:** at the time of writing, **no language model runs inside the app**. The scoring engine computes everything
with explicit rules and physics; card texts come from templates. If a language model is added to explain results, it will only receive
the engine's evidence package and its numbers will be checked **[confirm before submission]**.

**What AI did not do:** decide the product, accept licence risks, or validate legal rules as legal advice. The tool states that it does
not replace the farmer or the technician.
