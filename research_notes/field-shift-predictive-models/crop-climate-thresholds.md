# Crop climate-risk thresholds and the "success %" method for Campo de Cartagena (RotaSat, D-005)

Research date 2026-11-14. Tools: web search plus a small-model page fetcher; several PDFs were decoded locally with `pdftotext`. Several primary pages returned 403/404/certificate errors (MDPI, UMass, ScienceDirect, FAO crop-info, ENESA). Where a number comes only from a search-engine summary of a page I could not open, it is marked "(via search summary)". Items without any source are NOT in Cited Findings; background-knowledge defaults are confined to the "Inferences" blocks and labelled LOW confidence.

Overall verdict: the sourced material is strong for **almond bloom frost, lemon frost, IMIDA's multi-duration frost criteria, Agroseguro loss structure, Wilson/Jeffreys intervals and quantile-mapping choices**. It is thin for **Spanish sowing calendars, GDD bases for lettuce/celery/artichoke/watermelon, and heat thresholds for barley/artichoke/faba**. No Spain-specific validation of NASA POWER Tmin extremes was found.

---

## Q1. Per-crop thresholds: windows, cycle, GDD, frost, heat, flowering sensitivities, almond chill

### Takeaway
Hard, citable frost numbers exist for almond (UC bloom-hardiness table, decoded below), lemon (UC critical temperatures) and a generic multi-duration frost criterion calibrated on SIAM-IMIDA stations. For vegetables I only found generic extension values (lettuce/celery start to freeze near -0.5 to -1 degC, broccoli head-initiation heat limit ~25.6 to 29 degC, pepper fruit-set limits 32 degC day / 24 degC night). Cycle lengths come from FAO-56 (already in `suitability-and-process-models.md`, not repeated). Treat the proposed table in "Inferences" as a starting encoding with explicit confidence, not as validated agronomy.

### Cited Findings

**Almond (best-sourced crop)**
- UC Cooperative Extension "Almond variety bloom hardiness" table (artificial freezing of branches, 30-minute exposures; durations beyond 30 min raise damage). I decoded the PDF column positions. For **Nonpareil**: full bloom 50% damage at 27 F (-2.8 degC), 70% at 26 F (-3.3 degC), 90% at 25 F (-3.9 degC); small nuts 1% at 30/29 F, 40% at 28 F (-2.2 degC), 90% at 27 F (-2.8 degC), 100% at 26 F (-3.3 degC); pink bud 20% at 25 F (-3.9 degC), 40% at 24-23 F (-4.4/-5 degC). **Peerless** full bloom: 0% at 29 F, 5% at 28 F (-2.2 degC), 90% at 27 F (-2.8 degC), 100% at 26 F. **Mission** full bloom: 1% at 28 F, 80% at 27 F, 100% at 26 F. Small nuts are the most fragile: Nonpareil 40% at -2.2 degC, Carmel 30% at 28 F, Butte 80% at 27 F. Table notes that "a couple of degrees can make the difference between no damage and severe damage" and that flower stage, duration, vigour and preceding weather matter. — [UC Orchard Facts, Almond variety bloom hardiness](https://www.ccfruitandnuts.ucanr.edu/sites/default/files/2010-08/44640.pdf) (my decoding of the PDF layout; California cultivars, not Spanish Guara/Marcona/Lauranne)
- A UC Cooperative Extension source gives "damage begins below about 28 F (-2.2 degC)", depending on variety — [thealmonddoctor.com](https://thealmonddoctor.com/tag/almond-frost/) (via search summary)
- Almond chill requirement: UC Davis-linked fit of 10 to 30 chill portions (Dynamic Model) for Ne Plus, Nonpareil, Mission, using first/10% bloom dates; a UC-linked table lists almond 22-32 CP with Nonpareil 23 CP. — [Pope & DeJong 2017, Acta Hort. 1160](https://dejong.ucdavis.edu/sites/g/files/dgvnsk8456/files/inline-files/II%2072%20Acta%20Hort%201160%20Pope%20and%20DeJong%202017%20Chill%20model.pdf), [thealmonddoctor, chill portions](https://thealmonddoctor.com/chill-portions-for-ca-crops/) (via search summary; numbers disagree between sources, 10-30 vs 22-32 CP, so cultivar-dependent)
- Murcia context: a spring 2026 frost episode caused significant almond damage in Murcia (no comarca figures) — [Agroseguro Informe de Siniestralidad 30/04/2026](https://agroseguro.es/wp-content/uploads/2026/05/Informe-de-Siniestralidad-2026_30-abril-2026.pdf) (via search summary, already in `murcia_agro_context.md`)

**IMIDA / SIAM generic frost-damage criteria (Murcia-calibrated, for fruit trees and vineyard)**
- IMIDA's "AnGel PERIFEL" poster defines three event types causing significant damage in the critical phenological period, from hourly SIAM-IMIDA station data (2000-2025, 55 agroclimatic stations): (a) 5 consecutive hours with mean T below -0.5 degC; (b) 2 consecutive hours below -1.5 degC; (c) 1 hour below -3.0 degC. They compute the probability of a -3 degC event per SIAM station. — [IMIDA AnGel Perifel poster (Interreg SUDOE)](https://interreg-sudoe.eu/wp-content/uploads/2024/05/Poster-IMIDA-An-Gel-Perifel-ES.pdf) (decoded locally with pdftotext)
- Same poster, grapevine critical temperatures by phenological state (grape, DO Bullas test plot): winter bud < -15 degC; swollen bud -3 to -5; green tip -1 to -3; leaf emergence -1 to -2; shoots -0.6 to -2.5; visible inflorescences -0.6 to -1.5; flowering -0.5 to -1; fruit set -0.5 to -1 degC. — same source
- Because the criteria are duration-based they cannot be applied to daily Tmin directly; see Q2/Q3.

**Lemon / citrus**
- UC critical temperatures (Publication 8100, as reported in a search summary): lemon buds and blossoms about -2.8 degC (27 F); green lemons >13 mm between -2.8 and -1.4 degC; tree-ripe lemons between -3.3 and -0.8 degC; threshold depends on duration and humidity. — [UC ANR citrus freeze guidelines](https://ucanr.edu/node/125932) (via search summary; page returned 403 when fetched)
- Orange: serious tree damage after 4 h at 24 F (-4.4 degC) — [UC ANR Real Dirt](https://ucanr.edu/node/106683) (via search summary)
- Murcia field evidence (2015 study): frost damage in orange and mandarin was scarce, more frequent in grapefruit and **severe in lemon trees**. — [Frost damage in lemon orchards in the province of Murcia (AMiner record)](https://aminer.org/pub/5f6455082bab2ead60da8a08/frost-damage-in-lemon-orchards-in-the-province-of-murcia) (via search summary; abstract not readable)

**Lettuce**
- ECOCROP (already in existing notes): killing temperature -1 degC for mature plants, -6 degC for seedlings; cycle 60-85 d (head), 35-70 d (leaf). — [ECOCROP 1313](https://ecocrop.apps.fao.org/ecocrop/srv/en/cropView?id=1313)
- UC iceberg lettuce production guide: optimum about 73 F (22.8 degC) day / 45 F (7 degC) night; high temperatures may cause bolting, bitterness, poor heading and tipburn; seed germination inhibited above 86 F (30 degC). No exact tipburn/bolting onset temperature found. — [UC IPM cultural tips for lettuce](https://ipm.ucanr.edu/home-and-landscape/cultural-tips-for-growing-lettuce/) (via search summary; the guide's own URL was not identified)
- Lettuce classed as very susceptible to freezing (light-frost range 28-32 F) — [MSU fall vegetable freeze damage](https://www.canr.msu.edu/news/identifying_and_preventing_freeze_damage_in_fall_vegetables_part_2) (via search summary)
- Murcia calendar: Campo de Cartagena iceberg cycle runs from end-September plantings through February; little gem transplants October to early February with the cultivars tested; romaine traditionally Huerta de Murcia, iceberg Campo de Cartagena. — MAPA Biblioteca Revistas, e.g. [Surcos/Horticultura 1993 (SH_1993_1_163_168)](https://www.mapa.gob.es/ministerio/pags/Biblioteca/Revistas/pdf%5FSH%2FSH%5F1993%5F1%5F163%5F168%2Epdf), [Vida Rural 2012 no. 344](https://www.mapa.gob.es/ministerio/pags/Biblioteca/Revistas/pdf_Vrural/Vrural_2012_344_15_18.pdf) (via search summary; which PDF holds which statement is uncertain, and they are 1993/2012)
- Dec 2010 frost (fourth consecutive night) in Guadalentin/Campo de Cartagena: artichoke worst hit (25-30% of the crop without value even for canning); broccoli and lettuce "less affected"; zucchini damaged in Lorca area; no minimum temperature or hectares reported. — [Interempresas, 28/12/2010](https://www.interempresas.net/Horticola/46531-heladas-arruinan-cosecha-de-alcachofa-del-Valle-del-Guadalentin-y-del-Campo-de-Cartagena.html)

**Broccoli**
- Heat at head initiation: an MDPI Horticulturae paper uses growing degree-days with T above 25.6 degC, described as the maximum tolerable for onset of head formation; the sensitive window is the differentiation to reproductive phase, about 3 weeks before harvest. — [MDPI Horticulturae 11(2):187](https://mdpi.com/2311-7524/11/2/187) (via search summary)
- UMass extension: temperatures above 85 F (29 degC) can cause heat injury; Cornell: critical heat-sensitive period only about 10 days. Symptoms: uneven bud development, brown bead, loose head; severity cultivar- and stage-dependent. — [UMass broccoli summer heat](https://www.umass.edu/agriculture-food-environment/vegetable/fact-sheets/broccoli-summer-heat), [Purdue SW broccoli evaluation 2025](https://vegcropshotline.org/article/2025-spring-broccoli-evaluation-at-the-southwest-purdue-agricultural-center/) (via search summary)
- Cold: buttoning after several days at 35-50 F (1.7-10 degC) in young plants; not only heat. — [Gardener's Path](https://gardenerspath.com/plants/vegetables/broccoli-buttoning/) (low-authority, via search summary)
- Base/optimum for broccoli development in one Queensland thesis: 0 and 20 degC. — [core.ac.uk 41229723](https://core.ac.uk/download/41229723.pdf) (via search summary; which of two core.ac.uk PDFs not certain; LOW confidence)
- Murcia/Mediterranean calendar: CIDA Murcia trials transplanted 11 Sep, 6 Oct, 23 Oct 1997; for Valencia littoral the last ideal transplant is 10-20 Sep; Mediterranean production calendar runs mid-September to early June, main export Dec-May; juvenile phase optimum 20-30 degC; temperature decisive for commercial head quality in Murcia. — [MAPA SH 2004](https://www.mapa.gob.es/ministerio/pags/biblioteca/revistas/pdf_SH%2FSH_2004_12_115_119.pdf) and related MAPA articles (via search summary, 1998-2004 vintage)
- FreshPlaza headline: heat reducing summer broccoli harvests by around 50% (content not read; location unconfirmed). — [FreshPlaza](https://www.freshplaza.com/europe/article/9553016/the-heat-is-reducing-summer-broccoli-harvests-by-around-50/)

**Celery**
- Freezing injury starts at about 31.1 F (-0.5 degC) in a desert-vegetable table; USDA-derived table about 31 F (-0.6 degC); cauliflower about 30.6 F. — [growables.org crop storage table](https://growables.org/informationVeg/CropStorage.htm) (via search summary; the 31.1 F text came from a second, unidentified desert-vegetable table)
- Optimum 16-18 degC, tolerates 7-24 degC; bolting after 10 days at 40-55 F (4-13 degC) (UC-linked) or after 12 h below 50 F; bulb celery 20-30 d at 4-6 degC induces maximum bolting. — [Sims, Celery production (archive.org)](https://archive.org/download/celeryproduction522sims/celeryproduction522sims.pdf), [ISHS](https://ishs.org/ishs-article/122_14/) (via search summary)

**Melon and watermelon**
- Arizona cantaloupe phenology model uses heat units with 86/55 F thresholds (30 / 12.8 degC); a commercial source uses base 50 F (10 degC). — [Univ. Arizona VIPM cantaloupe growth and development](https://vegetableipmupdates.arizona.edu/sites/default/files/2024-07/A_VIPM_JCS_Cantaloupes_Melons_Growth%20and%20Development_30apr24.pdf) (via search summary)
- Melon germination inhibited below 59 F (15 degC) — [Yara](https://www.yara.us/crop-nutrition/melon/agronomic-principles); soil at least 18 degC — [Wikifarmer](https://wikifarmer.com/es/cultivar-melones-al-aire-libre-con-fines-de-lucro-guia-de-cultivo-completa-de-principio-a-fin/) (low-authority). Field chilling threshold of 10-12 degC for melon: NOT found in a reliable source (UC Davis postharvest chilling injury is below 2 degC in storage, different issue).
- Watermelon: keep temperatures at or above 10 degC to avoid loss of colour/growth; soil at least 18 degC at planting. — [MAPA Vida Rural 1998 no. 77](https://mapa.gob.es/ministerio/pags/Biblioteca/Revistas/pdf%5Fvrural%2FVrural%5F1998%5F77%5F71%5F74%2Epdf), [EOS](https://eos.com/es/blog/cultivo-de-sandia/) (via search summary)
- Watermelon calendar: sowing/planting can move to March in Murcia and Almeria, May-June in colder interiors; harvest 80-100 d after transplant; Cajamar trial transplanted 8 Mar 2010 and finished 10 Jun 2010 (greenhouse). — [Cajamar boletin huerto 170](https://www.cajamar.es/storage/documents/boletin-huerto-170-1496659283-6c034.pdf), [Cajamar boletin 61](https://www.cajamar.es/storage/documents/boletin-huerto-61-1496052490-a717a.pdf), [Cajamar trial](https://cenca.chil.me/download-doc/92721/evaluacion-de-parametros-de-calidad-de-sandia-en-invernadero-2012) (via search summary)

**Pepper**
- Ontario OMAFRA: daytime highs above 32 degC cause pollen sterility/flower drop; night below 15.5 degC or above 24 degC give poor fruit set; blossom drop most likely above 30-32 degC or below 15 degC day and above 21 degC night. — [Ontario.ca extreme temperature effects on tomato and pepper](https://www.ontario.ca/page/effect-extreme-temperatures-tomato-and-pepper-crop), [OMAFRA blossom drop](https://www.omafra.gov.on.ca/IPM/english/peppers/diseases-and-disorders/blossom-drop.html)
- UC (Hartz et al. 2008, second-hand via a Queensland report): preferred day 24-30 degC, night 9-12 degC; plant tolerates 38 degC but pollination/fruit set suffer; nights above 21 degC increase flower abscission; days below 18 degC give malformed fruit. — [Queensland DCAP capsicum report](https://data.longpaddock.qld.gov.au/static/dcap/DCAP3/DCAP%203__3%20Capsicum%20CTT%20Final.pdf) (via search summary; LOW-MEDIUM)

**Artichoke**
- No numeric killing temperature found. Evidence of high frost vulnerability in Murcia: artichoke "the crop most affected" in several frost episodes; about 4,400 ha damaged in Guadalentin in one episode; plants themselves frozen in many cases. — [Interempresas 2010](https://www.interempresas.net/Horticola/46531-heladas-arruinan-cosecha-de-alcachofa-del-Valle-del-Guadalentin-y-del-Campo-de-Cartagena.html), [Agronews CyL / portalfruticola](https://www.portalfruticola.com/noticias/2010/12/21/espana-las-heladas-se-llevan-por-delante-la-cosecha-de-alcachofa/) (via search summary)
- Agroseguro treats artichoke frost specially: in some areas, from start of cover to 30 Nov frost covers only quantity damage; 1 Dec to 15 Feb only plant death; from 15 Feb quantity and quality; dead plant = lost more than 70% of productive structure; Murcia "area I" has a special quality table. — [Agroseguro CES line 307 plan 2023](https://agroseguro.es/wp-content/uploads/2023/06/CES-307-23-1.0.pdf) (decoded locally)

**Faba bean and barley**
- Faba bean tolerates mild spring frosts down to -2.0 degC in one cited study; flowering is the most frost-sensitive stage, pods are more tolerant than flowers (thick wall), indeterminate habit lets later pods compensate; early/mid sowing more frost-exposed, late sowing more exposed to heat/moisture stress at flowering. — [Frost damage and pod set in faba bean, PMC8467580](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8467580/), [GRDC GrowNote faba bean](https://grdc.com.au/__data/assets/pdf_file/0028/369532/GrowNote-Faba-Bean-North-14-Environmental.pdf) (via search summary)
- Cereals: frost injury risk at flowering about 30 F (-1 degC) for roughly 2 h (Kentucky extension, wheat table; barley is ranked the most frost-susceptible small grain). Spring barley at two-leaf stage given -5.6 degC: 49-68% leaf injury, heading delayed 1.4-2.4 d. — [Penn State extension](https://extension.psu.edu/will-late-spring-low-temperatures-affect-small-grains), [Influence of simulated spring frost on three barley cultivars](https://gender.cgiar.org/publications/influence-simulated-spring-frost-growth-and-yield-three-barley-cultivars) (via search summary)
- Barley GDD to maturity 1296 (Tbase 0, Tupp 15) in AquaCrop-OSPy — already in `suitability-and-process-models.md` ([crop_params.py](https://raw.githubusercontent.com/aquacropos/aquacrop/master/aquacrop/entities/crops/crop_params.py)).

**Generic physiology**
- Hatfield & Prueger 2015: pollination/reproductive stages are the most temperature-sensitive for all species; each species has min/optimum/max limits; water stress amplifies temperature effects. Numeric table not retrieved. — [Weather and Climate Extremes 10](https://doaj.org/article/9d77d63e327d459f958d5cdb59705941) (abstract via search summary; full text at [uoregon mirror](https://pages.uoregon.edu/chendon/coffee_literature/old_literature/2015%20Weather%20Clim.%20Extremes,%20Temperature%20extremes%20on%20plant%20growth.pdf))

### Inferences

**Proposed first-pass encoding (to be reviewed by an agronomist; "conf." = confidence).** "Frost kill" = Tmin below which a crop is lost; "Frost damage" = onset of economic loss. Values marked B are my background-knowledge defaults, NOT sourced in this session.

| Crop | Season windows (Campo de Cartagena) | Cycle | Frost damage / kill (degC, daily Tmin) | Heat flag (Tmax or Tmean) | Sensitive stage | Conf. |
|---|---|---|---|---|---|---|
| Lettuce (iceberg/romaine) | Autumn-winter: plant late Sep to early Feb (MAPA). Spring: Feb-Apr (B) | 75 d (Apr) to 105-140 d (Nov-Feb) (FAO-56) | Damage about -1 mature (ECOCROP kill), seedling -6; use graded ramp 0 to -3 (B) | Tmax over about 25-30 degC for heading-stage days (bolting, tipburn; UC gives optimum 23/7 and "high temperature" without a number) | last 3 weeks (heading) | Frost MED, heat LOW |
| Broccoli | Transplant Sep (ideal to 20 Sep) to Oct/Nov (Murcia trials); harvest Dec-May | 135 d (FAO-56 Sept) | Damage near -1 to -2, florets in curd most sensitive (B, extension) | Tmax above 25.6 (onset) to 29 degC (injury) in the ~10-day to 3-week head-initiation window | head initiation 3 weeks pre-harvest | Heat MED, frost LOW |
| Celery | autumn transplant (B) | 125 d (Apr) to 195 d (Oct/Nov) (FAO-56) | Freezing injury at about -0.5 to -0.6 | Tmean above 24 degC unfavourable (UC range 7-24 degC) ; bolting if about 10 d at 4-13 degC | whole canopy at harvest | MED |
| Melon | Spring-summer: Mar-May (B), transplant when soil at least 15-18 degC | 120 d (May), cantaloupe 90-100 (FAO-56) | Any Tmin below 0 kills; chilling-growth stop below 10-12 (GDD base 12.8 in AZ model) | upper heat unit cap 30 degC (AZ) | flowering | Frost LOW (B), GDD MED |
| Watermelon | Mar (Murcia/Almeria) to Apr-May | 70-90 d (FAO-56); harvest 80-100 d after transplant (Vida Rural) | Tmin below 0 kills; growth penalty below 10 degC | not found | flowering | LOW |
| Pepper | Spring: Mar-Jun planting (B) | 210 d (FAO-56, long) | Tmin below 0 kills (B); fruit-set loss when night below 15.5 degC | Tmax above 32 (pollen sterility), Tmin above 24 degC (poor set) | flowering/fruit set | Heat MED |
| Artichoke | Plant Jul-Sep, harvest Nov-Mar (B) | perennial; 150-360 d | Very frost-sensitive in Murcia (damage first at slightly below 0, plant death at harder frost; exact numbers NOT FOUND, flag) | not found | heads from Nov to Mar | LOW |
| Faba bean / legume cover | Autumn sow (Oct-Dec), cover or grain | 100 d (Mar/Apr) to 175-235 d (Nov) (FAO-56) | -2 mild-frost tolerated; flowering damage from about -1 to -3 | late sowing exposes flowering to heat (no number found) | flowering | LOW-MED |
| Barley | Nov sowing, 240 d (FAO) | 1296 GDD (Tb 0, Tupp 15), AquaCrop | Boot to flowering about -1 for 2 h; vegetative hardy to about -5 | grain-fill heat: no number found | boot to flowering | LOW-MED |
| Lemon | perennial | 365 d | Blossoms -2.8; green fruit -2.8 to -1.4; ripe -3.3 to -0.8 | n/a | fruit set and green fruit | MED-HIGH |
| Almond | perennial | bloom Feb-Mar (Murcia, B) | Nonpareil: full bloom 50% at -2.8, 90% at -3.9; small nuts 40% at -2.2, 90% at -2.8 (30-min) | n/a | bloom to small-nut | MED-HIGH (cultivar caveat) |

- Because the demo parcel is at Torre-Pacheco (about 50 m a.s.l., coastal plain), frost in the plan matters mainly for **winter vegetables (lettuce, broccoli, celery, artichoke) and almond/lemon bloom**; for melon/pepper/watermelon the binding risks are cold nights at transplant (Mar-Apr) and heat during flowering (Jun-Aug).
- A season-aware design avoids counting a frost in January against melon: evaluate each threshold only inside the crop's sensitive-stage window, derived from sowing date plus GDD (see Q3).
- Use at most 2-3 flags per crop for the demo (frost, heat-at-sensitive-stage, optionally chill), each with a source link and confidence tag shown to the farmer; that matches the "what we don't know" requirement.
- Almond: Murcia interior almond blooms in Feb-Mar, so the probability of Tmin at or below -2.2 degC inside the bloom window is the key flag; chill-hour sufficiency is rarely binding on the coastal plain (not sourced, LOW).

### Gaps
- No Murcian or Spanish sowing calendar newer than 2012 retrieved (IMIDA/SIAM, CARM "calendario de cultivos", InfoAgro blocked or not surfaced). Spring-summer windows for melon, watermelon, pepper and the artichoke planting date are background knowledge only.
- No source for GDD base/total for lettuce, celery, artichoke, watermelon; no GDD-to-harvest for broccoli from a Mediterranean source.
- No numeric frost kill for artichoke, watermelon or melon; no heat threshold for artichoke, barley, faba bean, watermelon.
- ECOCROP full records (Tmin, Tabs, killing temperature) for each crop not retrieved; running `Recocrop::ecocropPars()` would fill most frost-kill cells in minutes.
- Spanish almond cultivar bloom-hardiness (Guara, Marcona, Lauranne, Penta, Desmayo) not found; chill portions for those not found.
- UC iceberg/pepper/celery guides' own pages were not opened; their numbers arrive via secondary snippets.

---

## Q2. Graded versus binary: damage functions and degree-hour indices

### Takeaway
Everything sourced for frost points to **graded** damage (UC almond table goes 1% to 100% over about 3 degC; lemon thresholds are ranges) and to **duration-dependent** criteria (IMIDA's 5 h / 2 h / 1 h rule). Insurance (Agroseguro) is graded too: it defines frost as air at or below the critical minimum of each phenological phase and pays only above a minimum damage (10-30%) after a deductible (10-20%). I found no published, validated yield-loss-per-degree-hour function for Mediterranean vegetables, so any graded function we use must be labelled a modelling choice.

### Cited Findings
- Agroseguro defines the frost peril as "air temperature equal to or below the critical minimum temperature of each phase of vegetative development which, due to ice formation in tissues, causes loss..." (no number in the policy text; the critical temperatures live in the expert-assessment norms). — [Agroseguro CES line 307, plan 2023](https://agroseguro.es/wp-content/uploads/2023/06/CES-307-23-1.0.pdf)
- Agroseguro multi-crop vegetable line 324 (plan 2026): "minimo indemnizable" between 10% and 30% and deductibles ("franquicias") between 10% and 20% depending on risk, area, crop, module; 6-day waiting period; heat stroke ("golpe de calor") is a covered peril in modules 1-2 (Canary Islands only in module P). — [Agroseguro IDDP 2026 line 324](https://agroseguro.es/wp-content/uploads/2026/02/IDDP-2026-324-1.0.pdf) (decoded locally)
- Agroseguro's only numeric heat-stroke definition I found is from a vineyard talk (Canarias): warm-air invasion with Tmax above 35 degC together with RH minimum below 25%. Not an official vegetable definition. — [Charla seguro viñedo, La Palma](https://www.vinoslapalma.com/files/noticias/charla-seguro-vinedo.pdf) (via search summary)
- Heat-stress indicator literature lists (i) threshold-exceedance day counts and (ii) high degree-hours (degC h, Bristow & Albrecht 1991) as indices; thresholds still need to be set per crop. — [Boku ADA Drought Impacts](https://ada.boku.ac.at/documents/ADA_Drought_Impacts.pdf) (via search summary)
- Deryng et al. 2014 and Teixeira et al. 2013 build crop-specific "critical" and "limit" temperature thresholds on reproductive stages for staple crops (not vegetables). — [Deryng et al. 2014 ERL](https://ueaeprints.uea.ac.uk/49750/1/Deryng_etal_2014_EnvironResLett.pdf), [Teixeira et al. 2013 (WUR record)](https://research.wur.nl/en/publications/global-hot-spots-of-heat-stress-on-agricultural-crops-due-to-clim/) (via search summary; functional form not confirmed)
- NASA POWER FROST_DAYS and the 0-days-Tmin<0 finding are from the team's own earlier work (see task context), not re-sourced here.

### Inferences
- **Recommended graded form (a modelling choice, labelled as such):** per sensitive-stage day, damage fraction d(T) = clip((T_onset - T)/(T_onset - T_lethal), 0, 1) for cold, mirror for heat, using the table's onset and lethal values (e.g., almond bloom onset about -2.2, lethal about -3.9 degC). Season loss = 1 - product over stage days (1 - d) or max of d. Success year = season loss below the Agroseguro-like minimum-indemnity threshold (use 20% as default; sourced range 10-30%). This turns the binary "exceeded or not" into a share of years above a **meaningful loss**, and it mirrors how Agroseguro itself pays out.
- **Duration without hourly data:** reconstruct hourly T from daily Tmin/Tmax with a sine-exponential (Parton-Logan type) diurnal curve and apply IMIDA's three criteria; or, simpler, treat daily Tmin <= -3.0 as a one-hour event, Tmin <= -1.5 as two-hour, Tmin <= -0.5 as five-hour. The reconstruction method is standard but I did not source it here (LOW confidence). Better: take SIAM hourly data directly (IMIDA already did).
- Degree-hours above a heat threshold are cheap to compute from the same reconstruction (sum of (T_h - T_thr)+); use as an index for broccoli head-initiation and pepper flowering windows.
- Hail is the largest insured peril in Murcia (Q5) but cannot be derived from daily POWER/IMERG; do not pretend to model it.
- Agroseguro excludes damage from physiological disorders, bad pollination/set and pests, i.e., heat-induced tipburn, bolting and fruit-set failure are **uninsured**; these are exactly the heat flags worth showing to the farmer (inference from the exclusions list, see Q5).

### Gaps
- No published damage-per-degree-hour function for lettuce/broccoli/celery/pepper in Spain or the Mediterranean found.
- Agroseguro's "temperatura critica minima" per phase (peritacion norm annexes) not retrieved; those tables could replace several cells above.
- The official Agroseguro definition of "golpe de calor" for vegetables (line 324 special conditions) not retrieved.

---

## Q3. Method: exceedance probability per sowing date from N=20 years; handling coarse POWER cell

### Takeaway
Compute, for each candidate sowing date and each of the 20 historical years, whether (or how much) the crop loses in its season window, giving k "bad years" out of n=20; report p_hat = k/n with a **Wilson (or Jeffreys Beta) interval**, not Wald. For temperature extremes the POWER cell is the weak link: published validation in a comparable Mediterranean climate (Alentejo, Portugal) found a relatively large Tmin error, and your own cell shows 0 days below 0 degC while SIAM stations record frosts. Prefer SIAM-IMIDA station series (2000-2025, 55 stations) as the primary temperature source for frost; use POWER only for the other variables or as fallback, with a bias correction.

### Cited Findings
- Brown, Cai & DasGupta (2001, Statistical Science): Wald interval has erratic coverage (nominal 95% gives about 0.953 at n=17 for p=0.5 but about 0.919 at n=40 in their illustration); recommended Wilson or equal-tailed Jeffreys intervals for small n (for n up to about 40 they are very similar), Agresti-Coull for larger n; Wilson/Jeffreys coverage oscillates around nominal, Agresti-Coull is conservative. — [Brown, Cai, DasGupta 2001](https://projecteuclid.org/euclid.ss/1009213286)
- POWER validation, hot-summer Mediterranean (Alentejo, southern Portugal, 14 stations): good agreement for all variables except wind, **but "the Tmin error was relatively large"**; local bias correction improved Tmax/Tmin NRMSE and brought mean NMBE from 10.65% to 0.2% (the abstract's Tmin NRMSE numbers, "20.5 to 16.1 degC", look like a typo; verify in full text). — [Rodrigues & Braga 2021, Agronomy 11(6):1207](https://mdpi.com/2073-4395/11/6/1207) (via search summary; page returned 403)
- Sicily POWER vs ground stations: RMSE reported as 3.6, 5.0, 3.2 degC for Tmax, Tmin, Tmean respectively. — [Sensors 2023, 23(15):7007](https://doi.org/10.3390/s23157007) (via search summary; also cited in existing notes for ET0)
- No Spain-specific validation of POWER Tmin extremes found (searched POWER/ERA5-Land vs SIAM/AEMET). Related reanalysis evidence: ERA5-Land ran cold, mean bias -0.94 degC across 159 Alpine stations. — [EGU26-6475](https://meetingorganizer.copernicus.org/EGU26/EGU26-6475.html) (via search summary)
- Bias-correction method comparison: quantile delta mapping (QDM) preserves the climate-change signal, plain quantile mapping (QM) distorts trends when the distribution shifts; both remove systematic biases in a validation period. — [Climate Dynamics, s00382-020-05447-4](https://link.springer.com/10.1007/s00382-020-05447-4); an Austria comparison found QDM and PresRAT variants satisfied all three criteria (observed climatology, change signal, wet-day frequency). — [ASCMO 2023 via DOAJ](https://doaj.org/article/50eec7bb2c0e4488bad23f623ed63c9f) (via search summary)
- A Norwegian EURO-CORDEX report applied empirical QDM to daily Tmax/Tmin and noted Tmax must remain above Tmin after correction; defined frost-change days as Tmax above 0 and Tmin below 0. — [NVE report 2019:51](https://publikasjoner.nve.no/rapport/2019/rapport2019_51.pdf)
- SIAM-IMIDA: 55 agroclimatic stations with T, RH, P, wind, radiation; hourly mean temperatures 2000-2025 analysed by IMIDA; free data via siam.imida.es (existing notes). — [IMIDA poster](https://interreg-sudoe.eu/wp-content/uploads/2024/05/Poster-IMIDA-An-Gel-Perifel-ES.pdf)
- Regional frost evidence at AEMET stations: lowest absolute minimum Dec 2025 -2.0 degC at Caravaca (inland); Jan 2025 -6.7 degC at Jumilla (inland); neither is the Campo de Cartagena. — [AEMET Dec 2025](https://www.aemet.es/documentos/es/serviciosclimaticos/vigilancia_clima/resumenes_climat/ccaa/region-de-murcia/avance_climat_mur_dic_2025.pdf), [AEMET Jan 2025](https://web2.aemet.es/documentos/es/serviciosclimaticos/vigilancia_clima/resumenes_climat/ccaa/region-de-murcia/avance_climat_mur_ene_2025.pdf) (via search summary)
- Warming trend context: Murcia city summer Tmin +0.2 degC/decade, with most of the Tmin rise in the last 20 years — [Informe de Riesgos Climaticos RMU 2024](https://catedracambioclimaticoaguasalicante.ua.es/uploads/site/files/InformeRiesgos-RMU-2024-Online.pdf) (existing notes)

### Inferences
**Computed interval table (my calculation, n=20, 95%):** k bad years, p_hat, Wilson, Jeffreys:
| k | p_hat | Wilson 95% | Jeffreys 95% |
|---|---|---|---|
| 0 | 0.00 | 0.000-0.161 | 0.000-0.117 |
| 1 | 0.05 | 0.009-0.236 | 0.005-0.211 |
| 2 | 0.10 | 0.028-0.301 | 0.021-0.284 |
| 4 | 0.20 | 0.081-0.416 | 0.072-0.408 |
| 10 | 0.50 | 0.299-0.701 | 0.293-0.707 |
So "0 frosts in 20 years" is **not** "0% risk": the honest upper bound is about 12-16%. Display "success 95% (range 84-100%)" or a traffic light, never a bare 100%.

**Pipeline (pseudo-algorithm):**
1. For each crop c and sowing date s (step 7-10 d across the window): compute phenology per year y from daily Tmean with GDD (or FAO-56 days as fallback) to get stage windows [t_flower_start, t_flower_end, t_head_init...].
2. For each hazard h and stage window: loss_{c,s,y,h} in [0,1] via the graded function (Q2) from bias-corrected Tmin/Tmax (and, for water, rain/ET0).
3. year_bad = 1 if combined loss >= L* (default 20%, the Agroseguro-like threshold range 10-30%); k = sum over y; success_climate = 1 - k/n with Wilson interval; combine hazards with max or 1 - product (state which).
4. success = success_climate x P(price >= breakeven), the latter from the price scenarios. Multiply only if independence is plausible (inference), otherwise show the two factors separately.
5. Report as class (e.g., high/medium/low) plus interval; show the table of the 3 worst years.

**Statistical honesty points (inferences):**
- n=20 yearly samples are not stationary (warming 0.2 degC/decade); weight recent years or detrend (e.g., add the observed linear trend to Tmin), and state that the 2050 scenario is a delta shift of the thresholds/series, not new data.
- Adjacent sowing dates reuse the same years, so the effective sample size for a window is about 20, not 20 x (number of dates); do not narrow intervals by pooling dates.
- A Beta posterior with a weak prior (Jeffreys) is a good "explainable" variant: p ~ Beta(k+0.5, n-k+0.5); this is the same as the Jeffreys row above.

**Bias handling for Tmin (my recommendation, not a published result for this site):**
- Best: use the nearest SIAM station(s) (coastal-plain and inland) directly for Tmin/Tmax history; POWER is a gridded reanalysis whose smoothing hides cold-air pooling in the basin (background: POWER temperature is MERRA-2-based at about 0.5 x 0.625 deg, UNVERIFIED here; PCSE docs say 0.25 deg, see existing notes).
- If a gap-filling or generalisation to other parcels is needed: fit QM for Tmin/Tmax between POWER and a SIAM station over the overlap, but constrain the tails (fit only the cold-tail offset, e.g., a monthly Tmin shift/scale for the lowest 10% of days) because with about 20 years the extreme quantiles are noisy; verify that Tmax >= Tmin after correction (NVE report). Use QDM only for future-climate (2050) work. Simple delta (mean monthly offset) is acceptable as a baseline and as a sanity comparison.
- Validate by reporting number of days with Tmin below 0 and below -2 in station vs raw POWER vs corrected POWER; the target is matching frost-days frequency, not RMSE.
- Frost risk is local (basin cold pooling; "riesgo de heladas por inversion termica" papers for the Huerta de Murcia exist but numbers not retrieved), so label results "for the nearest station X, not your exact field".

### Gaps
- No Spain/Murcia POWER-vs-station Tmin extreme validation; Alentejo and Sicily are the nearest analogues (and the Sicily RMSE values come only from a search summary).
- Torre-Pacheco-area SIAM station ID(s) and their frost-days statistics not retrieved (SIAM data portal not queried); a SIAM pull is the single highest-value next step.
- Rodrigues & Braga full text not read (403); the exact correction method used there is unknown.
- No source tested QM vs delta specifically for frost-day frequency.

---

## Q4. Extreme rainfall / DANA as a crop and bare-soil risk

### Takeaway
Daily rainfall above 80-180 mm has occurred repeatedly in the Campo de Cartagena (2009, 2019, 2020, 2024, 2025, 2026), mostly in September-October; Agroseguro defines flood-torrential rain by its effects, not by a millimetre threshold. I found no published frequency for days above 40 mm per year at Torre-Pacheco/San Javier, so the frequency must be computed from station or IMERG data.

### Cited Findings
- 2 Oct 2026: San Javier 180.0 mm in one day (October record, previous 172.9 mm on 17/10/1972), 118.4 mm in one hour; Torre Pacheco 86.6 mm the same day; October totals San Javier 265.6, Torre Pacheco 170.2 mm. — [AEMET Oct 2026](https://www.aemet.es/documentos/es/serviciosclimaticos/vigilancia_clima/resumenes_climat/ccaa/region-de-murcia/avance_climat_mur_oct_2026.pdf) (existing notes)
- Sept 2019 DANA: about 300 mm in La Manga and parts of the Campo de Cartagena, 236 mm in 3 h near Playa Honda. — [Murcia Today](https://murciatoday.com/murcia-gota-fría-storm-and-flooding-september-2019_1106149-a.html) (existing notes)
- 27-28 Sept 2009 event mainly affected the Campo de Cartagena; March 2020: 113.8 mm in 24 h at Tentegorra (monthly daily maximum); Dec 2025: Campo de Cartagena points did not exceed 50 mm. — [AEMET March 2020](https://www.aemet.es/documentos/es/serviciosclimaticos/vigilancia_clima/resumenes_climat/ccaa/region-de-murcia/avance_climat_mur_mar_2020.pdf), [AEMET Dec 2025](https://www.aemet.es/documentos/es/serviciosclimaticos/vigilancia_clima/resumenes_climat/ccaa/region-de-murcia/avance_climat_mur_dic_2025.pdf), [study of 2009 events](https://digitum.um.es/digitum/bitstream/10201/2405/1/105448.pdf) (via search summary)
- Marco Ortega et al. studied 1980-2000 events above 100 mm in 24 h in the Region of Murcia; intense rainfall is more frequent in autumn with cold-air intrusions at upper levels. — [pub.ame-web.org TyC](https://pub.ame-web.org/index.php/TyC/article/download/1916/2147/7586) (via search summary; authors/venue as reported, not verified)
- Return period in the Levante (Valencian) zone: 150-200 mm in 24 h about every 50 years; this is not Cartagena. — [Finisterra](https://revistas.rcaap.pt/finisterra/article/view/18993/19743) (via search summary)
- Agroseguro "inundacion-lluvia torrencial" is assessed by effects (river/ramblas overflow, runoff, evident silting or drag of materials around the parcel), no mm threshold; "lluvia persistente" is a separate covered peril in vegetable lines; drought is excluded. — [Agroseguro CES line 307](https://agroseguro.es/wp-content/uploads/2023/06/CES-307-23-1.0.pdf), [IDDP line 324](https://agroseguro.es/wp-content/uploads/2026/02/IDDP-2026-324-1.0.pdf)
- Agroseguro 2025 Murcia: storm-related risks other than hail (torrential rain, flood, wind, installations) about 15 M EUR vs hail more than 63 M EUR. — [Agroseguro NP 2 Feb 2026](https://agroseguro.es/wp-content/uploads/2026/02/NP-Agroseguro_Siniestralidad-seguro-agrario-Murcia.pdf) (decoded locally)
- Emergency works cost for the Oct 2024 DANA: 10.2 M EUR; DANA "Alice" Oct 2025: 4.7 M EUR on canal damage. — [CHS 11/12/2025](https://chsegura.es/export/sites/chs/descargas/informaciongeneral/comunicacion/noticias/docsdescarga/Nota-de-prensa-JUNTA-DE-GOBIERNO.pdf) (existing notes)

### Inferences
- Thresholds for the tool (modelling choices, not sourced): daily rain at least 40 mm = "heavy" event flag (waterlogging, crust, nutrient/sediment export risk to the Mar Menor), at least 100 mm = "DANA-class". Report both as annual frequency and as probability of at least one event in the crop's own season window (autumn plantings are the exposed ones: Sep-Nov bare soil or seedlings).
- Compute from IMERG daily or, better, SIAM/AEMET station data; note that satellite precipitation tends to smooth peaks, so report the IMERG number as a lower bound (background statement, not sourced here).
- Use the same Wilson interval; extreme rain returns are sparse, so frequencies for 100 mm will be 0-2 events in 20 years and intervals will be wide.
- Link to bare-soil months: the key benefit is "rotation with winter cover or crop in Sep-Nov reduces exposure", consistent with existing notes.

### Gaps
- No published days/year above 40 mm or return periods (T=2, 5, 10, 25) for Torre-Pacheco or San Javier; AEMET or CHS IDF/max-precip studies (not retrieved) would give them.
- AEMET warning thresholds (Meteoalerta) per zone not retrieved.
- Crop-specific rain damage thresholds (e.g., romaine under heavy rain, fungal risk) not found.

---

## Q5. Agroseguro / ENESA: which climate perils dominate losses (to justify which risks to model)

### Takeaway
In Murcia in 2025, hail dominates insured losses by a wide margin (more than 63 M EUR of 92.2 M EUR), with other storm risks about 15 M EUR; horticultural indemnities were 10.3 M EUR (about 11%), doubling versus 2024. Frost is episodic but locally decisive for winter vegetables and almond (spring 2026 episode). I found no peril-by-crop breakdown for Murcian vegetables.

### Cited Findings
- Murcia 2025: indemnities 92.2 M EUR (+30% vs 70.3 M EUR in 2024); 45,800 ha with claims; hail storms more than 63 M EUR; torrential/persistent rain, flood, wind and installations about 15 M EUR; by production: fruit trees 49.5 M EUR (+33%), citrus 16.4 M, **vegetables 10.3 M (doubled)**, table grape 7.8 M, ornamentals 1.9 M, vineyard 1.6 M, livestock 1.7 M; 2021-2025 total above 430 M EUR; national 2025 claims 804 M EUR (second highest after the 2023 drought). — [Agroseguro press note 2 Feb 2026](https://agroseguro.es/wp-content/uploads/2026/02/NP-Agroseguro_Siniestralidad-seguro-agrario-Murcia.pdf) (decoded locally)
- 2026 monthly reports: March episode damage mostly fruit trees and occasionally vegetables; April 2026 frosts also affected winter-cycle vegetables in Murcia; July 2025 hail damaged herbaceous, wine grape, vegetables, nuts, citrus and fruit trees. — [Agroseguro Informe de Siniestralidad 2026](https://agroseguro.es/wp-content/uploads/2026/06/Informe-de-Siniestralidad-2026_31-de-mayo-2026.pdf) (via search summary)
- August 2026 hail affected 1,265 ha of almond in Murcia — existing notes ([AgroNews CyL](https://www.agronewscastillayleon.com/granizo-murcia-2613-hectareas-cultivos-afectados)).
- Perils in the multi-crop vegetable line 324 (outdoor and protected): hail, **heat stroke**, wind, exceptional risks (wildlife, fire, flood-torrential rain, persistent rain, snow, hollow watermelon), frost (by area/zone/crop/period), "resto de adversidades climaticas". Not insured: pests/diseases, **drought**, **physiological disorders**, over-ripening, **poor pollination or fruit set**. — [Agroseguro IDDP 2026 line 324](https://agroseguro.es/wp-content/uploads/2026/02/IDDP-2026-324-1.0.pdf)
- Leafy/brassica successive-cycle line (outdoor): cover for frost, hail, exceptional risks (wildlife, fire, flood-torrential rain, persistent rain, hurricane wind) and other climate adversities; crops include apio, brocoli, lechuga, escarola, col; subsidy up to 75% of net base premium via ENESA. — [Agroseguro leaflet Hortalizas aire libre ciclos sucesivos 2026](https://agroseguro.es/wp-content/uploads/2026/02/Generico-Hortalizas-ciclos.pdf) (decoded locally)
- Frost insurance is area-specific: in the area list for artichoke (line 307), Murcia zones 1-2 have frost cover; artichoke frost has a special mínimo indemnizable/franquicia in Murcia and Almeria (20% absolute). — [Agroseguro CES line 307](https://agroseguro.es/wp-content/uploads/2023/06/CES-307-23-1.0.pdf)

### Inferences
- Which risks to model with 20 years of POWER/IMERG: **frost (winter vegetables, artichoke, almond/lemon bloom), heat at sensitive stages (uninsured physiological damage), heavy rain/DANA (bare soil, seedlings, nitrate export)**. **Do not model hail** (cannot be inferred from daily reanalysis); say so on the card and point to insurance (hail is the dominant insured peril).
- Because frost is insured in Murcia only by area and period and physiological heat damage is excluded, the uninsured residual is precisely what a climate-threshold comparator can add.
- A statistic on "share of horticultural claims by peril in Murcia" would justify the choice more strongly; request it from Agroseguro/ENESA or use the national "Informe de siniestralidad" tables.

### Gaps
- No breakdown of vegetable indemnities in Murcia by peril (frost vs rain vs hail vs wind) found; Agroseguro press notes aggregate by crop group or by hail vs "storm" risks only.
- ENESA statistical yearbook (Estadistica del seguro agrario) per peril/province/line not retrieved.
- Agroseguro's own numeric critical frost temperatures per crop and phase (expert-assessment norms) not retrieved.

---

## Source reliability notes
- Pages I read in full: IMIDA poster, Agroseguro Murcia press note, Agroseguro CES 307 (2023), IDDP 324 (2026), leaflet "Hortalizas ciclos sucesivos 2026", UC almond bloom-hardiness table (all decoded locally from PDFs). Everything tagged "(via search summary)" should be spot-checked before going on a slide.
- Conflicts and caveats: almond chill requirement 10-30 CP (Pope & DeJong fit) vs 22-32 CP (UC-linked table); broccoli heat limit 25.6 degC (MDPI GDD cutoff) vs 29 degC (UMass); celery freezing -0.5 vs -0.6 degC across tables; the UC almond table is for California cultivars and 30-min artificial freezing; the Agroseguro frost definition has no numeric temperature; the Rodrigues & Braga abstract contains an evident typo.
- Uncertain URL mapping: the MAPA Biblioteca articles for lettuce and broccoli calendars came from a list of search hits whose snippets were not tied to exact PDFs; treat the year/source as indicative.
