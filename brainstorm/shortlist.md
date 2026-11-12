# Shortlist: the 4 projects worth deciding between

From `challenge-analysis.md`. Each is pitched at the level needed to decide, with a **kill check** to run
Friday 13 Nov when the official resources come out. Pick one main plus one backup on Friday night (D-002).
Remember: **no project code or mockups before Sat 09:00.**

**My recommendation:** **A (Lunar Navigator)** as main, **B (Flame in Freefall)** as backup, swapping them if the
team wants AI to be the core of the product and PSI data turns out clean on Friday.

---

## A · "Lumen": Lunar Landing Site Navigator (challenge 11) ★ recommended
**One line:** pick a south-pole site and a date, see in one glance whether you'll have power and a line to Earth, and
what you lose if the launch slips.

**The 10-second wow:** a polar "sky dome": the jagged real horizon of Shackleton's rim, the Sun skimming along it
over a lunar day, Earth bobbing above and below the horizon (libration). Drag the date: the shading of "power" and "comms"
hours changes. Then the 3D terrain with real shadows sweeping across the craters.

**Demo script (3 min):**
1. "Artemis wants the south pole for ice. But the Sun never rises more than ~1.5° there." Show the sky dome.
2. Compare 3 sites side by side: Connecting Ridge vs Mons Mouton (IM-2 target) vs a crater floor. Power % and DTE %.
3. "Your launch slipped 3 weeks." Slip slider: −38 h of sunlight, Earthset 2 days earlier.
4. Copilot: "Find me alternatives within 15 km with ≥4 days of sun + Earth after 1 Apr 2028" → ranked table, click → 3D.
5. Validation slide: our illumination % vs NASA's published maps for the same points.

**Architecture:**
- `engine/` (Python): spiceypy with DE440 + lunar PA frames → Sun and Earth topocentric az/el per hour; horizon masks
  by ray-marching LOLA DEM (20 m local + 80–120 m far field, lunar curvature); visible-disk fraction of the Sun;
  precomputed per curated site → JSON. FastAPI for custom points (horizon in seconds with numpy).
- `web/`: React (or Svelte) + D3 for sky dome and calendar heatmap; Three.js terrain (DEM → heightmap mesh,
  directional light at Sun vector) or CesiumJS Moon terrain if it saves time.
- `copilot/`: Claude API with tools `list_sites`, `evaluate(site, date_range)`, `search_near(lat, lon, radius, constraints)`.
**Split (4 seats):** ephemeris & metrics · DEM/horizon & 3D · web UI (dome, compare, calendar) · copilot + validation + story/submission.
**Kill check (Fri):** LOLA south-pole DEM download works and the size is sane; spiceypy kernels load; resources tab doesn't
redirect the challenge to something we can't do.
**Risks:** frame/sign bugs (unit-test against known cases: Sun elevation at the pole always within ±1.6°; Earth
below the horizon ~half of each month at the far-side-facing slopes); DEM size (precompute, cache); scope creep in 3D (2D dome first).
**Awards:** Best Mission Concept · Best Use of Technology · Best Use of Data.

---

## B · "Ignition Atlas": Flame in Freefall (challenge 07)
**One line:** an AI that has read every NASA microgravity-fire experiment and tells a habitat designer which results
apply to *their* oxygen, pressure, airflow and material, with citations.

**The 10-second wow:** type a Moon-base scenario → the flammability map lights up: real test points (burned / self-extinguished)
on O₂ vs flow speed, your habitat's red dot sitting *inside* the "burns" region, three cited experiments explaining why.

**Demo script (3 min):**
1. "Moon bases will run at ~34 % O₂. Things that don't burn on the ISS may burn there." Show the challenge's own numbers.
2. Scenario form → ranked investigations (BASS-II, Saffire, ACME BRE…) with 1-line "why relevant".
3. Flammability map with the operating point; click a point → the test record, the source PDF page.
4. Compare two investigations side by side (auto-generated similarities and differences).
5. Gap finder: "no partial-gravity data: here is the microgravity/1 g bound and the upcoming LUCI and FM2 experiments."

**Architecture:** ingestion (PSI files + NTRS papers) → LLM structured extraction (JSON schema per test, with
citation spans, validated by a second-pass checker) → SQLite/Postgres plus a vector index → FastAPI → React dashboard (Plotly).
**Split:** ingestion & extraction · retrieval/ranking & API · dashboard & plots · science QA + story/submission.
**Kill check (Fri):** PSI combustion datasets downloadable without days-long approval; at least ~6 investigations have
test-level tables (O₂, pressure, flow, outcome) we can extract. If only prose PDFs exist, the flammability map
weakens and A wins clearly.
**Risks:** extraction errors (show confidence and source for every number); the local UPCT team will have more combustion knowledge.
**Awards:** Best Use of Technology · Best Use of Data · Science.

---

## C · "Terra Analoga": a search engine for Mars on Earth (challenge 09)
**One line:** pick a spot on Mars or the Moon; we search the whole Earth for places that match it, dimension by
dimension, and say honestly where the match breaks.

**The 10-second wow:** a world map heating up where Earth "looks like Jezero" by the numbers; known analogs
(Atacama, Río Tinto) light up (proof it works) and so does an unexpected one, perhaps near home (Cartagena–La Unión /
Mazarrón mining districts, Tabernas). Sliders re-weight geology vs thermal vs terrain live.

**Architecture:** Google Earth Engine (or pre-downloaded coarse grids) for the Earth feature cube (DEM slope/roughness,
MODIS albedo, LST day–night amplitude, NDVI, aridity, ASTER GED / EMIT minerals, aerosol); target vectors from MOLA/TES/THEMIS/CRISM
(Mars) or LOLA/Diviner (Moon); normalized per-dimension similarity → map tiles; "analog card" with LLM text
generated *from the numbers*.
**Split:** Earth feature cube · Mars/Moon target features + science sanity · similarity engine + map UI · cards, validation, story.
**Kill check (Fri):** someone can get GEE (or equivalent coarse global grids) working in under 1 h; the resources list
includes usable Mars/Moon global maps.
**Risks:** cross-planet comparability is the scientific crux (thermal inertia vs LST amplitude is a proxy, not the same
quantity); judges with geology background may poke. Mitigate with explicit "proxy" labelling and validation on known analogs.
**Awards:** Science · Data · Local Impact (if the Murcia analog holds up).

---

## D · "Mission Control: 4 Seats": Space Mission Design Game (challenge 13), wildcard
**One line:** four players, four phones, one spacecraft: negotiate mass, power, money and science, launch, and find
out (with an AI review board) why it worked or exploded.

**The 10-second wow:** hand four judges our QR code; they're designing a mission together within 30 seconds.

**Architecture:** web game (React/Phaser) + websocket room server (Socket.IO or PartyKit); a catalog JSON of real launchers,
instruments and buses; simulation engine (deterministic, seeded random events from real mission history and a real DONKI storm);
Claude-powered review board (PDR critique, post-mission explanation).
**Split:** sim engine & catalog · multiplayer server & sync · game UI/art · AI review board + scenarios + story.
**Kill check:** none on data. The risk is game design: by Sat 12:00 we must have a paper prototype that's fun with 4 people.
**Risks:** "less NASA data" → mitigate with real catalogs and a "data sources" panel; polish takes time.
**Awards:** Most Inspirational · Art & Technology · Best Mission Concept.

---

## Honourable mentions (if the team's taste differs)
- **SPHEREx blink + auto-mover detection** (12): great if someone enjoys astronomy data; IRSA access is well documented.
- **Trend Detective agent** (02): the most "agentic" project; demo is less visual.
- **MODIS/VIIRS** (08): the safest to finish; win by rigorous harmonization with a visible "seam removed" chart.
- **Earth Jukebox** (14): an uncontested art + accessibility project; "sonify the science, not the pixels".

## How we decide (T-003)
1. Each person writes their ranking of A–D (plus any honourable mention) in `votes.md` with one sentence why.
2. Friday 13 Nov after 17:00: read the resources tabs of the top 2, run their kill checks, read the Judging Guide.
3. Decide main + backup; record D-002. Then we fill `.claude/ownership.json` and create the first tasks
   (but write no project code until Sat 09:00).
