# Deep analysis of the 14 challenges (Space Apps 2026, Murcia)

Written 2026-11-10 by Claude for the team. Inputs: the verbatim challenge texts in `context/challenges/`, the rules
in `context/official-rules.md`, the 2025 winners in `context/past-winners-2025.md`, the Murcia team list in
`context/event-murcia.md`, and a few data-access checks (sources at the bottom).
**Each challenge's official data list comes out Fri 13 Nov.** Everything below about data is my best knowledge
plus spot checks, so re-check it on Friday (task T-004).

The short version is in `shortlist.md`. This file is the long version: what each challenge is really asking,
what most teams will build, where the opening is, and concrete ideas.

---

## 0. The game we're playing

### Who judges, in what order
1. **Murcia local judges** pick Global Nominees from the Murcia submissions. This is the gate. Their criteria and
   any local prizes are unpublished until Friday (Judging & Awards Guide, 13 Nov). In past editions the criteria
   were roughly *impact, creativity, validity, relevance, presentation*. That's my recollection, **unverified for 2026**.
2. NASA and partner experts pick Global Finalists, then an executive committee picks **10 Global Winners**, one per
   award: Best Use of Science · Best Use of Data · Best Use of Technology · Galactic Impact · Best Mission Concept ·
   Most Inspirational · Best Use of Storytelling · Global Connection · Art & Technology · Local Impact.

### What the 2025 winners had in common (from `past-winners-2025.md`)
- **A real, named NASA dataset at the centre of the story** (DONKI live feed, GeneLab OSD-288, NASA POWER,
  Kepler/TESS). Not "space-themed", but *data-driven*.
- **A working, clickable link** (deployed site), a demo video, and a long, honest "Project Details" text.
- **A candid AI-use section.** In 2026 this is mandatory: "SI" is NASA's 2026 word for AI.
- **Explained limits and validation.** The science-flavoured winners showed what the data can't say.
- Winners came from small cities and the virtual event too. A Murcia team is not at a disadvantage.

### Our edge as a team
Four CS students who are strong with AI agents and software. No geologist, astronomer or combustion scientist.
So we should pick a challenge where:
- **the hard part is software/algorithms/AI** (where we beat domain-heavy teams), not domain interpretation,
- **the data is reachable in under an hour** (otherwise we lose day 1),
- **the demo has a "wow" moment** a non-expert judge gets in 10 seconds,
- **we can show validation** (our numbers match a published reference). That neutralises our lack of domain cred.

### The local competition (snapshot 10 Nov, `event-murcia.md`)
| Challenge | Murcia teams already on it |
|---|---|
| Interplanetary Survival Guide: Martian Map | **4** |
| Field Shift: Adapting Farms | **4** |
| MODIS/VIIRS hot spots · Dancing with the SARs · Health Monitoring | 2 each |
| Trend Detective · Discarded Equipment · Moon/Mars analogs · Junior Astronaut · SPHEREx · Flame in Freefall | 1 each |
| **Lunar Landing Site Navigator · Space Mission Design Game · Earth Information Jukebox** | **0** |

Local judges compare everything, not per challenge, so an empty challenge doesn't guarantee anything. But it
does mean nobody will build a similar project next to ours and dilute the "wow", and our project stands out.
Avoid Martian Map and Field Shift unless we have a radically different angle.

### Rule that shapes our prep
"Participants should NOT begin working on their project until … November 14, 2026 (9:00 a.m. local time)."
Until Saturday 09:00 we only do **research, learning, accounts and team logistics**: no project code, no UI
mockups. Reading this analysis, learning a library and testing that an API answers are fine; writing the app is not.

---

## Scoring legend

Scores 1–5, 5 = best for us. **Fit** = how well a 4-CS/AI team matches it · **Data** = how easy the data is to get
and use (5 = trivial) · **Wow** = demo impact for non-experts · **AI** = how central AI can legitimately be ·
**Scope** = how well it fits ~39 hours · **Room** = local competition (5 = nobody else).

---

## 01 · Abandoned but not Forgotten: discarded equipment storytelling
**Ask:** an engaging, *accurate*, story-driven educational experience about hardware left on the Moon, on Mars and in deep space, for school-age kids.
**Data:** easy. NSSDCA mission catalog, NASA mission pages, LRO/LROC images of Apollo sites and landers, HiRISE images of
Mars landers (Viking, Pathfinder, Spirit, Opportunity, Phoenix, InSight, even crash sites), JPL Horizons for *live*
distances of Voyager 1/2, Pioneer 10/11 and New Horizons.
**What most teams build:** a clickable map with facts, or a comic.
**Opening:** make the machines *talk*, with accuracy as a feature.
- 💡 **"Ghost Fleet Radio"**: a 3D Moon + Mars + "deep space" view; click a dormant machine and it tells its story in
  first person (voice via TTS), then answers kids' questions. Every answer is grounded in a curated fact sheet, with
  sources shown (prevents the hallucination problem judges will worry about). Before/after: "here's me in 1971, here's
  LRO's photo of me in 2011". Voyager's live distance ticks up in real time.
- 💡 Variant: a "museum audio guide" for the Moon. Kids scan a QR on a printed Moon map at school.
**Hard part:** content curation and art, not code. **Awards:** Storytelling, Most Inspirational.
**Scores:** Fit 3 · Data 5 · Wow 4 · AI 4 · Scope 5 · Room 4 → **solid, but rewards content/art skills more than ours.**

## 02 · Be An Earth System Trend Detective! (Advanced)
**Ask:** a tool to *select* Earth-science variables, get them for a region, plot the time series, compute rate of
change and **significance** (t-test, Mann-Kendall, CIs). Doing both the visualization and the stats is "full scope". Explicitly suggests SI to
pick variables from a question or a region's character, and "a couple of demonstration examples".
**Data:** MERRA-2 and GLDAS monthly (GES DISC, Earthdata login, OPeNDAP/Giovanni), MODIS, OMI, AIRS, GPM.
The NASA POWER API (MERRA-2 based, no auth, point and regional monthly back to 1981) is a fast fallback. Gridded = heavier.
**What most teams build:** a dropdown → line chart → p-value.
**Opening:** this is an **agent problem**: question → variables → data → stats → map.
- 💡 **"Data Detective agent"**: ask "Is the Segura basin drying out?" The agent proposes variables (soil moisture,
  precipitation, evapotranspiration, LST), explains each in one line, fetches monthly series, deseasonalises, runs
  Mann-Kendall plus Sen's slope **per grid cell**, and shows a *map of significant trends*. That directly shows the
  challenge's key insight, "trends go opposite ways in different regions": e.g. drying in the southeast vs
  wetting in the north. Human-in-the-loop: the user can veto variables. Two guided demo cases (Murcia drought and
  something global, e.g. Arctic warming).
**Hard part:** gridded data plumbing and correct stats (autocorrelation, seasonality). **Awards:** Best Use of Data, Science.
**Scores:** Fit 4 · Data 3 · Wow 3 · AI 5 · Scope 3 · Room 4 → **strong AI fit, medium data risk, less visual wow.**

## 03 · Build a Junior Astronaut Mission Trainer (ages 7–12)
**Ask:** a game where kids run a lunar or Mars outpost, trading off life support, shielding, power, food and comms
delay. Every choice costs something. Use real data (DONKI solar events, OSDR, surface data). Browser, no account.
**Data:** easy. DONKI via api.nasa.gov (flares, CMEs, SEPs), OSDR, Mars weather.
**What most teams build:** a resource-bar survival game with invented numbers.
**Opening:** *real space weather drives the game*. Replay the actual solar storm of a real date. "Today's real Sun"
mode. Design must stay to 2–3 resources (the challenge warns against overload).
- 💡 **"Outpost: Real Sun"**: daily "sol" decisions; events are replayed DONKI events (e.g. the May 2024 Gannon storm);
  end-of-run "what really happened that day" card. Overlaps a lot with challenge 13, which has no local competition.
**Scores:** Fit 3 · Data 5 · Wow 3 · AI 2 · Scope 4 · Room 4 → **fine, but 13 is the better game challenge for us.**

## 04 · Create Health Monitoring Software for Astronauts
**Ask:** a visual tool for astronauts to self-assess health (BP, HR, glucose, sleep, mood…), with guidance, grounded
in NASA's Human Research Program (5 hazards). Body-map UI suggested.
**Data:** thin. HRP evidence reports and risk pages; OSDR is biology, not crew vitals. No real astronaut vitals dataset.
**What most teams build:** a dashboard with fake vitals and a clickable body (2 local teams already).
**Opening:** *measure something real, live*. Webcam remote photoplethysmography (rPPG) heart rate, voice/face mood
check-in, and an LLM "flight surgeon" that triages against HRP thresholds and knows the communication delay
("Earth is 22 min away: here's what to do now").
**Risk:** "medical advice" credibility, weak NASA-data story, crowded locally. **Awards:** Technology, Inspirational.
**Scores:** Fit 3 · Data 2 · Wow 4 · AI 4 · Scope 4 · Room 3 → **impressive demo possible, but weak on "use of NASA data".**

## 05 · Dancing with the SARs (NISAR)
**Ask:** an interactive app using **NISAR** radar data to track one or more surface changes anywhere.
**Data:** calibrated NISAR L-band products public since 20 Jul 2026 (acquisitions from 17 Jun 2026) via ASF
(Vertex, asf_search). Large HDF5 files (GCOV backscatter, GUNW interferograms), with known georeferencing quirks.
Only ~5 months of time series.
**What most teams build:** a before/after slider of backscatter.
**Opening:** Murcia is a world-famous InSAR case: **Lorca's subsidence** from groundwater over-extraction (and the 2011
quake), the Mar Menor and DANA floods. A local-impact story writes itself.
**Hard part:** SAR processing is a real domain skill. Interferometry in 36 h with no SAR expert is risky.
**Scores:** Fit 2 · Data 2 · Wow 4 · AI 2 · Scope 2 · Room 3 → **great story, too risky for us unless a teammate knows SAR.**

## 06 · Field Shift: Adapting Farms with NASA Data
**Ask:** a decision-support tool comparing ≥3 crop-rotation strategies using SMAP, ECOSTRESS, GPM, Landsat/MODIS,
POWER, GRACE, SRTM, plus soil, crop traits and farmer priorities. Explain evidence, uncertainty, risks.
**Data:** medium (many products, different resolutions).
**Local reality:** **4 Murcia teams** already. Murcia agriculture (huerta, water scarcity, Tajo-Segura) is the obvious
pitch for all of them.
**Only go here with** a very different angle (e.g. an agent that interviews the farmer by voice in Spanish and
produces a rotation plan with an evidence trail). Even then, judges will see 4 similar pitches.
**Scores:** Fit 3 · Data 3 · Wow 3 · AI 4 · Scope 3 · Room 1 → **avoid.**

## 07 · Flame in Freefall: SI-powered fire-safety insights from microgravity combustion data
**Ask:** an **AI-powered web dashboard** that *summarizes, ranks and interprets* combustion investigations in NASA's
**Physical Sciences Informatics (PSI)** database for fire safety in spacecraft, Moon base and rovers. Audience: researchers and engineers.
Display objectives, fuels, O₂ concentration, airflow, variables, sensors; compare investigations; support
predictive flammability modelling; point to Earth spin-offs.
**Data:** PSI is open (also mirrored on the AWS Registry of Open Data). Whether login or registration is needed today is
unconfirmed, so check Friday. Content = investigation descriptions, test matrices, data files, papers (NTRS).
The challenge text itself hands us the domain map (ACME ×6, FLEX/FLEX-2, CFI, BASS/BASS-II, SPICE, SLICE, SAME/SAME-R,
DAFT, BRE, Saffire) and the key scenario: **Moon base at ≥30 % O₂ and ≤10.2 psi** ("40 % more oxygen, much more flammable").
**What most teams build:** a chatbot over PDFs.
**Opening:** this is the one challenge where **AI is the product**, and LLM-engineering is exactly our skill.
- 💡 **"Ignition Atlas"**: (1) an LLM **extraction pipeline** turns every investigation and test into a structured record
  (fuel, geometry, O₂ %, pressure, flow speed, gravity, diluent, outcome, metrics) with a citation to page and file;
  (2) a **scenario ranker**: describe a habitat ("pressurized rover, 34 % O₂, 8.2 psi, 0.05 m/s ventilation,
  Nomex") and get the most relevant tests ranked, with *why*; (3) a **flammability map** (O₂ vs flow speed, burn
  vs no-burn points from real tests) with *your habitat's operating point* plotted on it; (4) a **gap finder**:
  "no partial-gravity data exists; microgravity and 1 g results bound it" (the challenge literally says this);
  (5) side-by-side investigation compare; (6) an Earth spin-offs tab.
**Hard part:** data access and format; staying scientifically humble (show evidence, not verdicts).
**Competition:** 1 local team (UPCT NAVIER, likely aerospace engineers; they'll know combustion better, we'll beat
them on the AI system).
**Awards:** Best Use of Technology, Best Use of Data, Science.
**Scores:** Fit 5 · Data 3 · Wow 4 · AI 5 · Scope 4 · Room 4 → **top candidate if PSI data is reachable on Friday.**

## 08 · Harmonization of MODIS and VIIRS Hot Spots
**Ask:** (1) harmonize MODIS (2000→) and VIIRS (2012→) active-fire records so sensor no longer matters; (2) a web app:
pick an area and dates → **burning-activity calendar** (month × year heatmap), anomalies vs historical median, CSV download.
**Data:** very easy. FIRMS yearly per-country CSVs, archive tool, area API with a free MAP_KEY.
**What most teams build:** naive counts per sensor, calendar heatmap.
**Opening:** do the **harmonization properly and prove it**. In the 2012–present overlap, fit a per-region, per-month
(and confidence- and FRP-aware) transfer function, e.g. quantile mapping of daily cell counts, or aggregate to a
common grid plus FRP threshold so VIIRS's extra small fires don't inflate counts. Then show the before/after
"seam" vanish in a chart. Add an early-warning view ("this month is in the 95th percentile for this area").
Spain/Murcia fires for local relevance; CONAE (Argentina) is a partner.
**Scores:** Fit 4 · Data 5 · Wow 3 · AI 2 · Scope 5 · Room 3 → **the safest, most finishable choice; less AI, 2 local rivals.**

## 09 · Identify Earth Locations that Analog Moon-Base Locations and Mars
**Ask:** use open Earth + Moon + Mars data to find and characterise **new** terrestrial analogs: what matches, how much,
where the analogy breaks, how it helps exploration. Maps, similarity metrics and ML are welcome. "Surprise us."
"Look beyond Atacama, Antarctica, Iceland, Hawaii."
**Data:** medium. Earth: Copernicus DEM/SRTM (slope, roughness), MODIS albedo, MODIS LST day–night amplitude
(a proxy for thermal inertia), NDVI, precipitation/aridity, ASTER GED emissivity, **EMIT surface mineralogy** (clays,
carbonates, sulfates in arid regions), aerosols. Mars: MOLA, TES albedo, THEMIS/TES thermal inertia, CRISM minerals.
Moon: LOLA, Diviner temperatures. Google Earth Engine makes the Earth side fast (free non-commercial account).
**What most teams build:** a map of famous analog sites with photos.
**Opening:** build a **search engine for Mars on Earth**.
- 💡 **"Terra Analoga"**: pick a target (Jezero delta, Gale/Mount Sharp, a lunar south-pole ridge); build its feature
  vector from Mars/Moon data; compute a similarity map over Earth's arid belt with **per-dimension sliders**
  (geology, thermal, terrain, dust); click a hit and get an "analog card" (green = holds, red = breaks, with numbers).
  **Validate**: known analogs (Atacama, Río Tinto, Haughton) must rank high. Then show *new* candidates.
  Local hook: **does Murcia/Almería hide a Mars analog?** The Cartagena–La Unión and Mazarrón mining districts
  (acidic, iron-sulfate-rich), Tabernas desert, Cabo de Gata volcanics. Only claim what the data supports.
**Hard part:** making cross-planet features comparable (scientific defensibility). **Awards:** Science, Data, Local Impact.
**Scores:** Fit 4 · Data 3 · Wow 5 · AI 4 · Scope 3 · Room 4 → **highest ceiling, real science risk.**

## 10 · Interplanetary Survival Guide: Martian Map
**Ask:** a layered map/HUD for a Marswalk at one location (≥3 data types), route avoiding obstacles, safety and
radiation, rover POV images.
**Data:** Mars Trek, HiRISE DTMs, CTX, CRISM, MSL/M2020 rover images, RAD radiation.
**Local reality:** **4 Murcia teams** (incl. 2 from UPCT).
**Only if** we'd do something they won't: e.g. a real path planner (A* on HiRISE DTM slope plus rock-density cost
with suit-energy budget) shown as a helmet HUD in WebXR. Strong idea, crowded room.
**Scores:** Fit 3 · Data 3 · Wow 4 · AI 3 · Scope 3 · Room 1 → **avoid (crowded).**

## 11 · Lunar Landing Site Navigator (no local team yet)
**Ask:** an intuitive tool to compare **landing sites and dates** at the lunar south pole: **Sun and Earth positions
vs the local horizon** → **power** (solar elevation, sunlight duration, time to sunset) and **direct-to-Earth
comms windows** (time to Earthset). Curated sites (Apollo, CLPS, Artemis, other countries) plus custom coordinates,
date flexibility, side-by-side compare, 2D/3D views, timelines. Real topography (LOLA) for horizons, libration,
no atmospheric refraction. Users: mission planners, educators, public. Existing tools (Quickmap, Moon Trek, Horizons) are too complex.
**Data:** good. Ephemeris via JPL SPICE kernels (spiceypy: DE440, lunar PA frame) or Horizons; LOLA south-pole DEMs
(20–80 m/px, 5 m for select sites) from PGDA/PDS. Validation reference: NASA SVS south-pole illumination
2023–2030 animations and the Mazarico/Barker illumination papers.
**What most teams would build:** a 2D map with Horizons numbers. But nobody locally has picked it.
**Opening:** it's a **computational-geometry plus visualisation** problem, our strength, with a natural AI layer.
- 💡 **"Lumen"**: (1) **horizon engine**: ray-march the LOLA DEM (with lunar curvature and far-field terrain, since
  mountains 100 km away matter when the Sun skims at ≤1.5°) → horizon mask per site; (2) **ephemeris engine**: Sun and
  Earth az/el (and the visible fraction of the solar disk) per hour for 2027–2030; (3) **views**: a polar
  "sky dome" with the horizon silhouette and Sun/Earth tracks (the instantly readable image), a 3D terrain view with
  real-time shadows, a calendar heatmap of power and comm per day, and side-by-side compare; (4) **slip analysis**:
  "launch slips 3 weeks → you lose X h of sunlight and Y h of DTE"; (5) **planner copilot**: natural language
  → tool calls → ranked alternatives ("find sites within 15 km of Mons Mouton with ≥4 days of sun+DTE after 1 Apr 2028").
**Hard part:** frames and sign conventions (testable), DEM sizes (precompute), horizon accuracy (validate vs SVS).
**Awards:** Best Mission Concept, Best Use of Technology, Best Use of Data.
**Scores:** Fit 5 · Data 4 · Wow 5 · AI 3 · Scope 4 · Room 5 → **my #1: hard-tech, verifiable, visual, uncontested locally.**

## 12 · Planet X and SPHEREx
**Ask:** a public web tool: enter RA/Dec → show a series of SPHEREx images of that patch like a little video, to spot
movers. Test on Barnard's Star, Epsilon Indi B, WISE 0855, RW Aur, R Dra. Kudos for spectra on the fly, add/subtract
epochs, FOV choice, Gaia/WISE overlays, URL-addressable, contamination flags, Aladin.
**Data:** good. IRSA SIA2 (`COLLECTION=spherex_qr2`), cutouts by appending center and size to image URLs, astroquery
and pyvo, IRSA tutorials (incl. a "source discovery tool" demo), `spxquery` package. SPHEREx pixels are 6.2″; Barnard's
Star moves ~10″/yr, WISE 0855 ~8″/yr, so over ~1.5 yr of surveys that's 2–3 pixels: visible in a blink.
**What most teams build:** the blink viewer (that's the spec).
**Opening:** (a) **auto-mover detection**: difference images + source extraction + linking across epochs, flagging
movers *not in Gaia* (citizen-science queue → Global Connection); (b) **spectra on click** (the 102-band
LVF design gives per-pixel wavelength); (c) Gaia positions propagated with proper motion as overlay arrows, showing that
the dot really is the star moving. 1 local team (SkyShift).
**Scores:** Fit 4 · Data 4 · Wow 4 · AI 3 · Scope 4 · Room 4 → **strong; astro-specific learning curve.**

## 13 · Space Mission Design Game (no local team yet)
**Ask:** a game to design, manage and simulate a whole mission: objective → spacecraft → instruments → launcher →
orbit → budgets (mass, power, cost, data, comms, lifetime); **multiplayer up to 4 with roles**; consequences for every
decision; simulation, scoring, post-mission analysis; difficulty levels, random events, shareable designs.
**Data:** optional. Real launcher capacities, real instrument specs, solar flux vs distance, simple link budgets,
real failure stories.
**What most teams build:** a single-player form with sliders and a score.
**Opening:** real-time **4-seat multiplayer** where each player sits on a different subsystem, on their own phone.
That's exactly the challenge's ask, and it's a CS strength (websockets/state sync).
- 💡 **"Mission Control: 4 Seats"**: judges scan a QR, get a role (Science / Spacecraft & Power / Launch & Orbit /
  Comms & Budget), negotiate under a shared budget, launch, watch a simulated timeline with events grounded in
  real history (a DONKI solar storm, Mars Climate Orbiter's unit error), get a PDR-style review from an
  AI "review board" that explains *why*.
**Awards:** Most Inspirational, Art & Technology, Mission Concept. Live demo with the judges playing is unforgettable.
**Scores:** Fit 4 · Data 4 · Wow 5 · AI 3 · Scope 4 · Room 5 → **best "wildcard": fun, uncontested, low data risk; lighter on NASA science data.**

## 14 · The Earth Information Jukebox (no local team yet)
**Ask:** pair NASA Earth Information Center visual frames with **real-time sonification**; accessibility (blind and
low-vision users) is core; output can be an interactive app or a curated playlist.
**Data:** easy (EIC / NASA SVS visualization frames and videos).
**What most teams build:** pixel colour → pitch.
**Opening:** **"sonify the science, not the pixels"**. Invert each visualization's colour bar to recover the actual data
value per pixel (e.g. °C anomaly), then map *data* to musical parameters (Tone.js) with musical scales; a scanning
"playhead" across the globe; a vision-LLM narrator describes what's on screen for screen-reader users; stereo panning
by longitude. Demo in the room is memorable (sound!).
**Awards:** Art & Technology, Storytelling, Inspirational.
**Scores:** Fit 3 · Data 4 · Wow 4 · AI 3 · Scope 5 · Room 5 → **dark horse; easy to finish, but may read as "less serious" to local judges.**

---

## Summary table

| # | Challenge | Fit | Data | Wow | AI | Scope | Room | Σ | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 11 | Lunar Landing Site Navigator | 5 | 4 | 5 | 3 | 4 | 5 | **26** | **#1** |
| 07 | Flame in Freefall | 5 | 3 | 4 | 5 | 4 | 4 | **25** | **#2** (if PSI data OK) |
| 13 | Space Mission Design Game | 4 | 4 | 5 | 3 | 4 | 5 | **25** | wildcard |
| 09 | Moon/Mars analogs | 4 | 3 | 5 | 4 | 3 | 4 | **23** | #3, high ceiling |
| 12 | Planet X & SPHEREx | 4 | 4 | 4 | 3 | 4 | 4 | **23** | strong |
| 02 | Trend Detective | 4 | 3 | 3 | 5 | 3 | 4 | 22 | AI-agent option |
| 08 | MODIS/VIIRS | 4 | 5 | 3 | 2 | 5 | 3 | 22 | safest |
| 14 | Earth Jukebox | 3 | 4 | 4 | 3 | 5 | 5 | 24 | dark horse |
| 01 | Discarded equipment | 3 | 5 | 4 | 4 | 5 | 4 | 25 | content-heavy |
| 04 | Health monitoring | 3 | 2 | 4 | 4 | 4 | 3 | 20 | weak data story |
| 03 | Junior astronaut | 3 | 5 | 3 | 2 | 4 | 4 | 21 | 13 is better |
| 05 | SARs (NISAR) | 2 | 2 | 4 | 2 | 2 | 3 | 15 | too risky |
| 06 | Field Shift | 3 | 3 | 3 | 4 | 3 | 1 | 17 | crowded |
| 10 | Martian Map | 3 | 3 | 4 | 3 | 3 | 1 | 17 | crowded |

The raw sum ties several challenges. My ranking also weighs **validation possible** (11, 07, 09, 12 can show "our
numbers match NASA's") and **our edge** (11 and 07 reward exactly what we're good at). That's why 01 and 14 sit below
despite similar sums.

---

## Sources for the data checks (10 Nov 2026)
- PSI open access: https://science.nasa.gov/physical-sciences-informatics-psi/ · https://www.re3data.org/repository/r3d100014699
- SPHEREx access: https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access · https://irsa.ipac.caltech.edu/data/SPHEREx/docs/cutout_tool.html · https://caltech-ipac.github.io/irsa-tutorials/spherex-cutouts · https://caltech-ipac.github.io/irsa-tutorials/spherex-source-discovery-tool-demo
- NISAR availability: https://nisar-docs.asf.alaska.edu/availability-overview/ · https://forum.earthdata.nasa.gov/viewtopic.php?p=26356
- Lunar illumination references: https://svs.gsfc.nasa.gov/4930/ · https://svs.gsfc.nasa.gov/4893 · https://ntrs.nasa.gov/citations/20205009660
- FIRMS: https://firms.modaps.eosdis.nasa.gov/download/ · https://firms.modaps.eosdis.nasa.gov/api/area/csv
