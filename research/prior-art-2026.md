# Prior art: public 2026 Space Apps projects already on GitHub (checked 2026-11-13)

Why this matters: the "Room" score in `brainstorm/challenge-analysis.md` only counted **Murcia** teams. Globally,
every challenge already has several public 2026 repos, many created **weeks before 14 Nov**. Local judges pick
nominees first, but global judges will see these. Do **not** reuse their code (rules: work must be created during
the event); use them only to know the bar and to differentiate.

Method: `gh api repos/...` for the repos cited in the web-Claude report
(`NASA Space Apps Murcia 2026 análisis de retos e ideas de proyecto.pdf`, repo root) plus
`gh search repos "<terms>" --created ">2026-09-01"`. The search is keyword-based, so the counts below are a lower bound.

## The two that raise the bar most

### 11 Lunar Landing Site Navigator: `NetRunnerXD/lunar-horizon-wheel`
Created 2026-10-13, last push 2026-11-05, 12 commits, live on GitHub Pages. Covers almost all of our "Lumen" idea:
- LOLA horizon wheel with Sun and Earth tracks (10 min step, limb-darkened disk)
- operability swim-lanes (Sun ∧ Earth ∧ DSN ∧ battery)
- P10–P90 uncertainty, validation against NASA Goddard illumination maps
- traverse planner (slope < 20°, ≥50 % Sun and Earth, VIPER shadow rule): this was our "chase the light" idea
- DSN contact, X-band link budget, relay vs DTE
- both poles, ISRO Chandrayaan layers
- PDF/CSV/CZML/STAC export, EN/HI/BN interface, sonification

Matching it in 39 h is unrealistic.

### 07 Flame in Freefall: `eres0045/spica-firelab` ("The 34% Question")
Created 2026-11-11, 21 commits, 69 tests, live demo. A 3D ISS fire lab with O₂, pressure and flow sliders, and verdicts
computed from **2,012 cleaned PSI rows across 19 flight investigations**.

Key finding: **solids were never tested above 22.2 % O₂**, so the 34 % O₂ / 8.2 psi exploration atmosphere sits about
12 O₂ points outside the data. This confirms that PSI is public and tabular (our kill check passes), and it takes the
headline insight of our "Ignition Atlas".

## Other 2026 repos found per challenge (lower bound)
- 08 MODIS/VIIRS: ≥10, among them FireChronicle, ember-atlas, pyfire-watch, fire-harmony, kiln-watch-2026, Smokeshed
- 11 Lunar: ≥9
- 07 Flame: ≥9
- 14 Jukebox: ≥8
- 02 Trend Detective: TerraTrend (3D globe plus Mann-Kendall)
- 12 SPHEREx: spherex-planet-x
- 05 SARs: dancing-with-sars
- 04 Health: AstroByte-Health-Monitor
- 10 Martian Map: RISHI-1453/NASA_Space-Apps_Challenge_Martian_Map
- 09 Analogs: 1 found
- 13 Mission Design Game: 0 found with "mission design game space apps"; re-check with other terms

## Corrections to the web-Claude report (checked against the verbatim texts in `context/challenges/`)
- "CLPS Lunar Mission Browser" in the report = official **Lunar Landing Site Navigator** (11).
- 08 asks for a CSV download. Drawing the area of interest is a suggestion, and GeoJSON is not mentioned.
- 10 (Martian Map): the official text never mentions communications or relay. A connectivity layer has to be framed as
  safety or route planning to score on relevance.
