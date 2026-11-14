# Prices, profit model and decision/optimisation layer for the Field Shift crop-recommendation app

Scope: design guide for (a) revenue = yield x price with price uncertainty, (b) costs/investment, (c) optimiser/ranker, (d) rotation planning. Demo region: Campo de Cartagena. About 30 h of hacking left, team of 4.

Convention: "Cited Findings" only carries things a fetched/searched source supports. Equations and design recommendations are my synthesis and live under "Inferences" (the underlying methods are textbook; where a source supports the method, it is cited in Cited Findings). Several PDFs were not machine-readable (see Gaps), so some papers are cited from abstracts/records only.

---

## Q1. Price forecasting: which model, how accurate, and is forecasting worth it versus seasonal historical distributions?

### Takeaway
Evidence on commodity/vegetable price series says simple baselines (naive persistence, SARIMA/ARIMA) are hard to beat, and Prophet is usually the worst; forecastability varies strongly by commodity. For a 30 h hackathon, a seasonal empirical distribution (median + P10/P90 by week-of-year, from MAPA/Mercamurcia weekly origin prices) is the defensible choice, with seasonal-naive/SARIMA as an optional backtested comparator.

### Cited Findings
- Italian wholesale food prices: ARIMA and LSTM performed similarly, a CNN-LSTM gave the best overall accuracy but needed more tuning, and Prophet was "quick and easy to use" but "considerably less accurate". — [Comparing Prophet and Deep Learning to ARIMA in Forecasting Wholesale Food Prices (arXiv 2107.12770)](https://arxiv.org/abs/2107.12770)
- Bangladesh agricultural retail prices (daily, 90-day input, 14-day horizon; naive persistence, SARIMA, Prophet, BiLSTM, Transformers): naive persistence had the best MAE on 3 of 5 commodities (garlic 4.66, chickpea 0.71, green chilli 3.95, sweet pumpkin 1.25 BDT/kg); SARIMA was best only on cucumber (8.97); Prophet had the worst MAE on every commodity (MAPE roughly 23-75%). Authors conclude forecastability varies by commodity and model complexity did not reliably help. No seasonal-naive baseline and no XGBoost/LightGBM in that paper. — [Benchmark ... Bangladeshi Market Price Dataset (arXiv 2604.06227, HTML)](https://arxiv.org/html/2604.06227)
- Korean onion study (12 models, five markets, source in Korean, summary via search tool): ARIMA/SARIMA performed well in Daegu and Busan, Prophet generally poor in all regions, and tree-based models (RF, GB, LightGBM) performed relatively poorly in Gwangju and Daejeon. — [KoreaScience PDF](https://koreascience.or.kr/article/CFKO202433161848561.pdf)
- Prophet's weakness on step-like price dynamics is attributed by the Bangladesh authors to its smooth-trend assumptions. — [arXiv 2604.06227](https://arxiv.org/html/2604.06227)
- Price data availability: MAPA weekly "informe semanal de coyuntura" bulletins list national average origin prices (e.g. artichoke 63.08 and 59.00 EUR/100 kg in consecutive weeks of one 2026 report; broccoli 44.11 -> 51.21 and 62.35 EUR/100 kg in others; romaine lettuce quoted per 100 units at 26.36 and 27.70 EUR/100 ud). The search tool noted file week numbers do not always match table dates, and the copies found were hosted by a third party (teseo.clal.it), so originals from MAPA should be used for citation. — [MAPA weekly report copy (2026 s20)](https://teseo.clal.it/upload/informe-semanal-de-coyuntura-2026-s-20.pdf)
- MAPA also publishes a weekly fruit and vegetable price bulletin (FyH) that covers regional markets, including Murcia, where in the 2025 campaign romaine lettuce, broccoli and cauliflower prices were above the previous campaign and above average. — [MAPA boletin semanal de precios FyH, 28 Apr-4 May 2025](https://servicio.mapa.gob.es/ca/ganaderia/estadisticas/182025boletinsemanaldepreciosdefyh28abril-4mayo_tcm34-707878.pdf)

### Inferences
- Recommended price layer (hackathon tier 1, ~3-4 h): for each crop c and week-of-year w, from >= 5-10 years of MAPA weekly origin prices, compute empirical quantiles P10/P50/P90 of the price at the expected harvest week. Harvest week = planting date + cycle length from upstream submodel. Convert to scenarios by sampling years (a "year" = one historical price path), which preserves cross-crop correlation for the risk model in Q3 for free. Deflate for inflation first (real EUR), otherwise a trend contaminates the distribution.
- Tier 2 (optional, ~3 h): rolling-origin backtest of seasonal-naive vs SARIMA vs the quantile table at 8-26 week horizons using MAE/pinball loss; report honestly "no forecast beats the seasonal distribution by more than X%" if that's what comes out. That is a defensible finding for judges and matches the literature above (simple wins). Skip Prophet and LightGBM: the cited evidence shows they underperform and add dependencies.
- Horizon matters: the app's decision is made months ahead of harvest (planting-to-harvest 2-3 months for lettuce, years for perennials). At those horizons, point forecasts add little over climatology; the distribution is the honest object. For perennials, use a long-run real-price assumption with a scenario band (low/base/high), not a forecast.
- Price-yield coupling: do not multiply independent P50s; a good year for yield (regional glut) tends to be a bad year for price. Sampling historical years jointly (if yield anomalies are available) or at least using the price scenarios while keeping yield uncertainty separate avoids overstating revenue spread or understating it. Flag this as an assumption in the UI.

### Gaps
- No peer-reviewed accuracy benchmark specifically on weekly Spanish horticultural (lettuce/broccoli/artichoke) prices was found; the evidence is from Italy, Korea and Bangladesh with different frequencies. Typical MAPE for volatile horticulture at 8-12 week horizons is therefore not established here.
- Seasonal-naive was not in either benchmark found, so "seasonal naive vs SARIMA" remains untested in the cited literature.
- The Mercamurcia/SIAM/MAPA open-data download route and history depth (how many years of weekly series per crop, unit conventions) were not verified; the search returned PDF bulletins, not an API/CSV endpoint.

---

## Q2. Profit model, costs and capital for annuals versus perennials (NPV, payback, IRR)

### Takeaway
Use a standard crop-enterprise gross margin per ha (yield x price - variable costs) for annuals, and a multi-year discounted cash flow (establishment cost, years to first income, NPV and payback) for perennials. This directly gives the "time to return" and "initial investment" filters the farmer asked for. MAPA's own cost framework defines gross margin and net margin explicitly and can be mirrored.

### Cited Findings
- MAPA's horticulture economic reports define margen bruto as gross product minus direct costs, machinery and hired labour, and margen neto as disposable income minus depreciation; indirect costs include an opportunity cost of land. — [MAPA, Horticolas 2010](https://mapa.gob.es/es/ministerio/servicios/analisis-y-prospectiva/Hort%C3%ADcolas.2010_tcm30-88515.pdf)
- In that 2010 report irrigated lettuce had a positive net margin (667.55 EUR/ha) but an operating loss (-586.09 EUR/ha) because of a fall in gross product; artichoke and irrigated lettuce losses were attributed mainly to a drop in gross product of 26.6% and 18.6%. This shows how thin and price/yield-driven annual horticulture margins are. — [MAPA, Horticolas 2010](https://mapa.gob.es/es/ministerio/servicios/analisis-y-prospectiva/Hort%C3%ADcolas.2010_tcm30-88515.pdf)
- Campo de Cartagena context: 15,420 ha of lettuce (46% of Spain) and broccoli as second crop by area (10,618 ha in 2011); a 2025 report quotes a potato grower saying cost per ha rose from about 8,000 to about 12,000 EUR in four years. — search results summarised from [MAPA Horticolas 2010](https://mapa.gob.es/es/ministerio/servicios/analisis-y-prospectiva/Hort%C3%ADcolas.2010_tcm30-88515.pdf) and [potatopro](https://www.potatopro.com/es/node/168511); the 15,420 / 10,618 ha figures come from the MAPA search snippets and are not independently confirmed on the page text.
- Perennial budgets: UC Davis publishes almond sample-cost studies with separate establishment-cost tables and cumulative net-return (payback) views; one UC Davis/Almond Board slide shows payback in year 8 at 2.10 USD/lb and year 6-7 at 3.00 USD/lb depending on whether cash overhead is included. A 2011 UC Davis summary quotes 3,974 USD/acre total production cost (annual, not establishment). — [Almond Board: economics of orchard establishment and almond production](https://live-br.almonds.com/sites/default/files/2020-04/economics_of_orchard_establishment_and_almond_production.pdf); [UC study helps farmers analyze costs to grow almonds](https://www.agalert.com/california-ag-news/archives/may-11-2011/uc-study-helps-farmers-analyze-costs-to-grow-almonds/)
- MAPA's Observatorio de la Cadena published a cost-structure document for the main organic crops of Murcia (candidate source for per-ha costs by crop), but the file could not be fetched (certificate error). — [MAPA estructura de costes cultivos ecologicos Murcia](https://mapa.gob.es/en/alimentacion/temas/observatorio-cadena/estructuradecostesdelosprincipalescultivosenagriculturaecologicadelaregiondemurcia_tcm38-690252.pdf)

### Inferences
Annual crop enterprise (per parcel p, crop c, one cycle):
- Revenue R = Y x P x (1 - loss) x area, with Y ~ yield model (mean, sd), P ~ price scenario at harvest week.
- Variable cost VC = seed/plants + fertiliser + plant protection + water (m3 x tariff, from FAO-56 demand) + hired labour (h/ha x wage) + machinery/fuel + harvest/packing (often per-unit, so scale with Y).
- Gross margin GM = R - VC. Return on cost = GM / VC. Gross margin per m3 of water = GM / water demand (this is the binding constraint in Campo de Cartagena, so rank by it too). Gross margin per month occupied = GM / cycle months (makes lettuce vs 12-month crops comparable).
- Time to first income t1 = planting-to-harvest months (plus lag to payment). Cash-flow exposure = max cumulative negative cash (peak working capital) = the "initial investment" number to compare against the farmer's capital slider.

Perennial (citrus, almond, artichoke multi-year, etc.), year t = 0..T:
- CF_t = Revenue_t - VC_t - Est_t (Est_t concentrated in t=0..2; Revenue_t follows a yield ramp-up curve).
- NPV = sum_t CF_t / (1 + r)^t; r = 4-8% real; show sensitivity.
- Payback = first t with cumulative sum of CF_t >= 0 (undiscounted) and discounted payback similarly.
- IRR = r such that NPV = 0 (numpy-financial or scipy brentq).
- Equivalent annual annuity EAA = NPV x r / (1 - (1+r)^-T) lets perennials and annuals be compared on a per-year basis; it is the cleanest way to put almond and lettuce on one axis.
- For the hackathon, hard-code cost tables per crop in a CSV with a source column; clearly mark placeholders. Use ranges, not point values, and show them as assumptions in the UI.

### Gaps
- No usable current per-hectare cost table for lettuce, broccoli, artichoke, citrus or almond in Campo de Cartagena was retrieved; the MAPA Murcia cost-structure PDF failed to load. Cost inputs will need to be taken from that MAPA/Observatorio document, Consejeria/IMIDA or RECAN (Red Contable Agraria Nacional) data, or labelled as team assumptions.
- No NPV/IRR numbers for Mediterranean citrus/almond orchards were found; the UC Davis (California) figures are not transferable to Murcia prices/labour.
- The percent figures quoted from MAPA 2010 are 15 years old and for national categories; do not present as current.

---

## Q3. Decision methods: ranking with filters, MCDA, LP farm planning, risk programming, multi-objective

### Takeaway
Best demo-ability and explainability: (1) hard-constraint filters + weighted-sum/TOPSIS score for the per-parcel ranker; (2) a small LP/MILP (HiGHS) for farm-level allocation under land/water/capital/labour; (3) risk via scenario-based CVaR or MOTAD as a single "risk aversion" slider; (4) optional Pareto view (profit vs water vs N-leaching, risk) by sweeping weights/epsilon-constraints in the LP, using pymoo NSGA-II only if time allows.

### Cited Findings
- MCDA in crop-land evaluation: a 2022 review in the Indian Journal of Agricultural Sciences of cropland-suitability studies reports AHP used by 53% of researchers, fuzzy AHP 16%, ANP 6%, TOPSIS 6%, ELECTRE 3%, others 16%; criteria are mostly soil, climate, topography, socio-economic, infrastructure, irrigation, land use and environment. — [Indian Journal of Agricultural Sciences (Jun 2022)](https://doaj.org/article/45aab46c92fd4b769f232e92fe540bd8)
- A wheat study under conservation agriculture used AHP-derived weights inside a TOPSIS ranking with agronomic, soil-health, crop-protection, energy and economic criteria; a 2021 paper used fuzzy AHP weights with TOPSIS and PROMETHEE to rank crop alternatives on economic, technical, social and environmental criteria. — search summaries of [AHP/TOPSIS crop selection results](https://dergipark.org.tr/en/download/article-file/1741046) and [Journal of Intelligent & Fuzzy Systems](https://content.iospress.com/articles/journal-of-intelligent-and-fuzzy-systems/ifs201701) (snippets only; details not read)
- Methodological review of AHP and TOPSIS covers rank reversal in AHP, normalization methods and distance functions for TOPSIS. — [Overview of MCDA and applications of AHP and TOPSIS](https://katalog.lib.cas.cz/KNAV/EdsRecord/edsdoj,edsdoj.7eca4aae69c549da9279217bc17f08d6)
- MOTAD (Hazell 1971) minimises total absolute deviation of income, can be solved by linear programming, and gives solutions close to quadratic E-V programming; it was proposed as a computationally cheaper alternative. Hardaker & Troncoso (1979) showed a MOTAD model built on a discrete distribution matching the elicited joint-normal moments can closely approximate the E-V frontier, whereas pseudo-random sampling of deviations risks solutions some distance from it. — [Hardaker & Troncoso 1979, Eur. Rev. Agric. Econ. 6(1):47-60](https://ideas.repec.org/a/oup/erevae/v6y1979i1p47-60..html); [Hazell/MOTAD discussion](https://vtechworks.lib.vt.edu/server/api/core/bitstreams/47606738-508d-4078-a9fd-c53e8c52b78e/content)
- Target-MOTAD (Tauer 1983) penalises only negative deviations below a target income; the complete efficient set can be traced by parametric programming over the target T and the expected-deviation limit lambda (McCamley & Kliebenstein 1987). — [IDEAS record, risk programming literature](https://ideas.repec.org/p/ags/aaea84/278966.html) (summary from search; full texts not read)
- Choosing one plan from the E-V efficient set needs a utility function, which is hard to establish reliably (Hazell & Norton 1986; Binswanger 1980); quadratic utility implies increasing absolute risk aversion; MOTAD approximates mean-standard-deviation and says nothing about risk-aversion type. — [Agrekon 28(1)](https://ageconsearch.umn.edu/record/267231/files/agrekon-28-01-006.pdf) (quotes Hazell & Norton 1986; Hazell 1982; Binswanger 1980)
- Hazell & Norton (1986), "Mathematical Programming for Economic Analysis in Agriculture", is the standard reference for these models. — cited throughout, e.g. [Agrekon 28(1)](https://ageconsearch.umn.edu/record/267231/files/agrekon-28-01-006.pdf)
- Filippi, Mansini & Stevanato (2017, Computers & Operations Research 81:26-39) propose two MILP models for crop selection on fixed land: maximise expected profit, and maximise CVaR; the CVaR model suits a risk-averse farmer. Keywords: market price variability, yield per hectare, Italian historical data. — [IRIS Unibs record](https://iris.unibs.it/handle/11379/487654); [Bohrium summary](https://www.bohrium.com/paper-details/mixed-integer-linear-programming-models-for-optimal-crop-selection/811103161539362816-3917)
- CVaR optimisation (Rockafellar & Uryasev) reduces to a linear program when uncertainty is a finite set of scenarios; practical caveat that LP solutions are sensitive to scenario estimation error. — [Rockafellar & Uryasev, Optimization of CVaR (PDF)](https://sites.math.washington.edu/~rtr/papers/rtr179-CVaR1.pdf); [Mansini, Ogryczak & Speranza overview](https://core.ac.uk/download/159146995.pdf)
- A multi-objective MILP for crop rotation with sustainability terms reports that with under 5% reduction in net income crop diversity could rise by 60% (snippet truncated). — [Multi-objective models for crop rotation planning problems](https://ersearch2.cvtisr.sk/vufind/SummonRecord/FETCH-LOGICAL-c333t-4559c202ac6cd1131b1ee7a6a991ccf97dfb23a09c14198b45881c70b49554443/Details)
- pymoo NSGA-II: survivors chosen front by front with crowding distance; defaults pop_size=100, SBX crossover, polynomial mutation; usage `minimize(problem, NSGA2(...), ('n_gen', 200))`; binary variants need custom sampling/crossover/mutation. — [pymoo NSGA-II docs](https://pymoo.org/algorithms/moo/nsga2.html). pymoo also ships MCDM helpers (pseudo-weights, compromise programming, knee point) and NSGA-III for 4+ objectives, per third-party skill listings (not the official page) — [pymoo skill listing](https://smithery.ai/skills/lifangda/pymoo).

### Inferences
Layer A, per-parcel ranker (explainable core, build first):
1. Hard filters (drop, with reason string): suitability < s_min; water demand > remaining allotment; capital need > capital limit; months to first income > max slider; labour hours > cap; crop banned by rotation rule (same family as previous).
2. Score for survivors: weighted sum of min-max normalised criteria, S_c = sum_k w_k x z_ck, criteria = expected GM/ha, GM per m3, P10 downside (or CVaR), time to income, suitability, N-leaching proxy. Show a per-criterion contribution bar for each recommendation (this is the explainability payoff). Offer TOPSIS as a toggle: closeness C_c = d-_c / (d+_c + d-_c) with d measured to the ideal/anti-ideal points over weighted normalised criteria; it is a ~20-line numpy function and gives a standard, citable "MCDA" label. AHP is not needed: pairwise comparisons add UI burden, and the sliders already produce weights (AHP also has the rank-reversal issue noted in the review above).
3. Inverse query ("which parcels maximise crop X"): same score matrix, fix crop c = X, rank parcels p by GM_pX (or by score), after filters. Trivial given a parcel x crop table.

Layer B, farm-level allocation (LP/MILP, the "classic farm planning LP" of Hazell & Norton):
- Decision: x_pc >= 0 area (ha) of crop c on parcel p (continuous; or binary y_pc if one crop per parcel per season).
- max sum_{p,c} g_pc x_pc  (g = expected GM/ha)
- s.t. sum_c x_pc <= A_p (land); sum_{p,c} w_pc x_pc <= W (water allotment, m3, optionally per month); sum_{p,c} k_pc x_pc <= K (capital); sum_{p,c} l_pcm x_pc <= L_m (labour per month); crop-share/market bounds x_c <= u_c; rotation constraints (Q4); months-to-income: x_pc = 0 if t1_c > T_max.
- Risk (Layer C) with S price/yield scenarios s (historical years), probability pi_s:
  - Scenario income I_s = sum g_pcs x_pc.
  - MOTAD: min sum_s pi_s d_s^- s.t. sum_pc (g_pcs - gbar_pc) x_pc + d_s^- >= 0, expected income >= Lambda; trace the frontier by varying Lambda.
  - CVaR (Rockafellar-Uryasev): max (1-lambda) E[I] + lambda (eta - 1/(1-alpha) sum_s pi_s u_s) s.t. u_s >= eta - I_s, u_s >= 0, eta free. alpha=0.9 or 0.95 (use 0.8 with ~10-15 scenarios, since the tail is otherwise one observation). lambda in [0,1] is the user's risk-aversion slider (0 = risk neutral).
  - Mean-variance E-V needs QP (scipy/cvxpy) and has the utility/risk-attitude caveats from the literature; MOTAD/CVaR keep it an LP, so HiGHS handles it.
- Explainability: duals (shadow prices) of the water and capital constraints give "one extra 100 m3 of allotment is worth X EUR" for free from the LP; show this in the demo.

Layer D, multi-objective: objectives f1 = -E[GM], f2 = water use or N-leaching proxy, f3 = -CVaR. Get a Pareto front cheaply with the epsilon-constraint method on the same LP (e.g. cap water at 100%, 90%, ... 60% and re-solve; solves in milliseconds) plotted as a front. Use pymoo NSGA-II only if the model becomes nonlinear/discrete enough that LP sweeps do not apply; it is slower, stochastic and harder to explain.

Ranking of options by demo-ability/explainability (my judgement): filters + weighted sum (best) > epsilon-constraint LP front and shadow prices > CVaR slider > TOPSIS > MOTAD/E-V (needs explanation) > NSGA-II (black box, seed-dependent).

### Gaps
- Primary texts of Hazell (1971), Tauer (1983), Hazell & Norton (1986) and Filippi et al. (2017) were not opened; details (e.g. Filippi's exact CVaR formulation, instance sizes) are from abstracts/secondary descriptions.
- No source found comparing AHP vs TOPSIS vs weighted-sum rankings on crop-selection outcomes with profitability as a primary criterion; the MCDA literature found is mostly land-suitability.
- Typical risk-aversion values in farm programming and how they are elicited were not retrieved; see Q6.

---

## Q4. Rotation planning: sequence rules, MILP/graph/DP formulations, cover crops and nitrate (Mar Menor)

### Takeaway
Rotation can be implemented in two complexity tiers: (1) per-parcel sequence rules as hard filters plus a small DP/shortest-path over a crop-state graph (Detlefsen & Jensen network-flow idea), which makes ">=3 strategies including current" simple to compute; (2) the full MILP of Santos et al. with family, set-aside and green-manure constraints, which is exact but heavy (branch-price-and-cut was needed for realistic size). For a hackathon, use tier 1 and enumerate strategies.

### Cited Findings
- Detlefsen & Jensen (2007), "Modelling optimal crop sequences using network flows", Agricultural Systems 94(2):566-572: finding the optimal rotation for a selection of crops on a given field is cast as a network modelling problem so specialised network algorithms can be used; later literature describes it as maximising gross margin for each crop sequence with constraints on crop shares in the year of interest. — [IDEAS/RePEc record via search](https://ageconsearch.umn.edu/record/152213) (abstract-level; full text not read)
- Dury, Schaller, Garcia, Reynaud & Bergez (2012), "Models to support cropping plan and crop rotation decisions: a review", Agronomy for Sustainable Development 32:567-580: reviews more than 120 references; critiques that most models treat the cropping plan as a fixed once-per-year or once-per-rotation choice rather than a dynamic series of annual and long-term decisions. — [HAL record hal-00930508](https://hal.archives-ouvertes.fr/hal-00930508) (abstract via search tool)
- Santos et al. rotation scheduling model (as reproduced in Aliano Filho et al., ICORES 2012): binary x_ijk = 1 if crop i is planted in period j on lot k. Maximise profitability sum area_k l_ij x_ijk. Constraints: no same-family crop on adjacent lots (2); no same-family crop consecutively on the same lot (3); no overlap in the same lot during the crop cycle t_i (4); each lot has at least one green-fertiliser (legume) application (5) and a set-aside period (6); demand satisfaction per crop (7). Exact solution is computationally heavy for real instances, so they used a genetic algorithm; the real instance: 16 lots, 29 crops of 10 botanical families, 2-year horizon, monthly periods (Sao Paulo, Brazil). — [Aliano Filho, Florentino & Vaz Pato, A genetic algorithm for crop rotation (ICORES 2012)](https://www.scitepress.org/Papers/2012/37619/37619.pdf)
- Santos, Munari, Costa & Santos (2015), EJOR 245(2):581-590: vegetable crop rotation scheduling with minimal plot sizes (multiples of a base area) and minimised cultivated area; integer program solved with a branch-price-and-cut algorithm (subadditive valid inequalities, primal heuristics, strong branching); efficient on instances from real-life data. Sustainable practices modelled: alternating plant families, fallow, green manure. — [EconPapers record](https://econpapers.repec.org/RePEc:eee:ejores:v:245:y:2015:i:2:p:581-590)
- Earlier (2010 book chapter) dos Santos, Arenales, Costa & Santos "crop rotation scheduling model" encodes ecological criteria such as not planting the same botanical family in sequence; Costa et al. (2014, Ann. Oper. Res.) had to use column generation because of a very large number of variables. — [branch-price-and-cut record](https://portal.mardi4nfdi.de/wiki/Publication:319637); [Unimelb listing](https://findanexpert.unimelb.edu.au/scholarlywork/900115-sustainable-vegetable-crop-supply-problem-with-perishable-stocks)
- Akplogan, de Givry et al., crop allocation problem (CAP): assign crops to plots over a horizon H with hard constraints (minimum return time rt between same crop on a plot, spatial compatibility, resource capacity such as one irrigated plot) and soft constraints (crop-sequence quality of successive pairs, spatial balance of acreage, topology), modelled as a weighted CSP solved with toulbar2 or as an ILP (NumberJack/SCIP); example farm 180 ha, 4 blocks, 15 plots, four crops. — [Akplogan et al., Solving the crop allocation problem using hard and soft constraints (RAIRO-OR)](https://miat.inrae.fr/degivry/Akplogan13.pdf)
- A 2024-era CEUR paper proposes a MILP for rotation planning with 8 crops and 2-, 3- and 4-year rotations; a multi-objective MILP for rotation shows large diversity gains for a small income loss (snippet). — [CEUR Vol-3944 paper5](https://ceur-ws.org/Vol-3944/paper5.pdf) (PDF text not extractable; only the search summary was used)
- Mar Menor context: nitrate in the Campo de Cartagena Quaternary aquifer reported around 200 mg NO3/l and about 456 t of nitrate entering the lagoon from the aquifer and dams in 2022; land abandoned for years still shows significant nitrate from organic-matter mineralisation, and leaching risk rises with intense rainfall. — [Noticias Ambientales](https://noticiasambientales.com/?p=158116); [ecoticias](https://www.ecoticias.com/medio-ambiente/por-que-abandonar-los-cultivos-puede-empeorar-la-contaminacion-del-mar-menor)
- A Puertes et al. (2021, Agricultural Systems) scenario analysis of best management practices for the Mar Menor found improved fertiliser management reduced nitrate export and leaching with minimal impact on crop yield (abstract snippet; cover crops not confirmed). — [IDEAS record, Agricultural Systems 188](https://ideas.repec.org/a/eee/agisys/v188y2021ics0308521x20308908.html)
- A UMU presentation reports fertigation as the main recovery measure, lowering nitrogen losses from 44% to 31%; it notes some leaching data still in preparation. — [Fernandez Molina, UMU](https://um.es/documents/3456781/9489754/6pedro-fernandez.pdf/1520e426-2ba0-4426-bebb-edb7a29e005d)

### Inferences
Tier 1 (build this): 
- Data: crop table with family (Asteraceae lettuce/artichoke, Brassicaceae broccoli/cauliflower, Solanaceae, Cucurbitaceae, Fabaceae, Poaceae, Amaryllidaceae), min return interval r_c (years or cycles), is_legume, cycle months, N-uptake/residue estimate.
- Per parcel, dynamic programming over seasons: state = crop (or family) grown in the previous season(s); value V_t(s) = max_c [GM_{c,t} + V_{t+1}(c)] subject to allowed(s, c) (different family; return interval via a small history window). With ~10 crops, 6-8 seasons, this is milliseconds. It is equivalent to the Detlefsen-Jensen network formulation (nodes = (season, crop), arcs = allowed transitions, arc weight = GM; longest path).
- Strategies to compare (>=3, including current): (S0) current practice, i.e. continue the parcel's observed last crops (repeat/monoculture-ish, penalised if it breaks family rule, flagged rather than forbidden so the baseline remains realistic); (S1) max expected GM subject to rotation rules; (S2) risk-averse (CVaR lambda high) or low-water; (S3) soil/N-friendly: must include a legume or cover crop in bare windows; (S4) quick-cash (cap months-to-income). Show a table: cumulative 3-5 year GM (P50 and P10), water, N-balance proxy, capital peak.
- Farm-level coupling: after per-parcel DP, apply farm-level LP (Q3 Layer B) per season only if shared water/capital must be allocated across parcels; the simplest honest approach is a parcel-level DP with farm constraints enforced by a greedy repair or by the LP over per-parcel pre-computed "strategy columns" (choose one strategy per parcel; a small MILP with binary z_{p,s}; this is a column-selection MILP with P x S binaries, trivially fast).
Tier 2 (only if time): full Santos-style x_{ijk} MILP including adjacency and set-aside; do not attempt, since the literature needed branch-price-and-cut or GA for realistic instances.
Cover crops: model as a zero-/low-revenue "crop" with small cost (seed, termination), short cycle placed in windows when the parcel is otherwise bare (e.g. between a summer and winter crop); benefits encoded as (a) N-leaching proxy reduction, (b) legume N credit to the next crop (cut fertiliser cost), (c) soft score term. State loudly that the nitrate reduction magnitude is an assumption, because no Campo de Cartagena cover-crop trial figure was found.

### Gaps
- No field-trial quantification of cover-crop nitrate reduction for Campo de Cartagena horticulture was found (searches in English and Spanish returned general Mar Menor nitrate context only). The N-leaching benefit has to be a clearly labelled assumption or taken from IMIDA/UMU reports not retrieved here.
- Detlefsen & Jensen (2007), Dury et al. (2012), Filippi et al. (2017) and Akplogan et al. were read at abstract/record level or partly; the Akplogan PDF text was only skimmed (constraint taxonomy), solve times not extracted.
- The CEUR 2024 paper's formulation and runtimes could not be extracted (PDF text empty).
- Minimum return intervals per family for Spanish horticulture were not sourced; the numbers must come from an agronomist or extension guide.

---

## Q5. Tools: PuLP, Pyomo, OR-Tools CP-SAT, pymoo, scipy.optimize for an interactive web app

### Takeaway
For LP/MILP of this size (tens of parcels x ~10-20 crops, <= a few thousand variables), scipy.optimize.milp (HiGHS) or PuLP (modelling layer) is enough and solves in well under a second. Use pymoo only for the optional Pareto/nonlinear part, and CP-SAT only if rotation becomes a large combinatorial assignment.

### Cited Findings
- scipy.optimize.milp wraps HiGHS; deterministic; typically finds the global optimum of moderately challenging MILPs; takes c, LinearConstraint, Bounds and an integrality vector (0 continuous, 1 integer, 2 semi-continuous, 3 semi-integer); matrices become sparse CSC; maximise by negating c; rounding a relaxed solution does not reliably give the integer optimum. — [SciPy docs: scipy.optimize.milp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html)
- pymoo NSGA-II defaults and usage as in Q3; pymoo constraint handling defaults to feasibility-first and supports penalty approaches (third-party listing). — [pymoo NSGA-II docs](https://pymoo.org/algorithms/moo/nsga2.html); [pymoo skill listing](https://smithery.ai/skills/lifangda/pymoo)
- Akplogan et al. solved their crop-allocation problem with either toulbar2 (weighted CSP) or an ILP solver through NumberJack/SCIP, indicating constraint-programming and ILP are both viable for rotation assignment. — [Akplogan et al.](https://miat.inrae.fr/degivry/Akplogan13.pdf)

### Inferences
- scipy.optimize.milp / linprog (HiGHS): no extra dependency if scipy is present, fast, sparse; downside is matrix-form modelling, which is error-prone with many constraint families and gives duals only via `linprog` (not `milp`). Good for a small hand-built model; use `linprog` for the continuous LP to get shadow prices.
- PuLP: readable algebraic modelling, ships a CBC binary by default and can call HiGHS if installed (not verified in this session: the PuLP doc page redirected and was not read); good for code the whole team can read in a demo. Pyomo: more powerful (nonlinear, stochastic extensions), but heavier syntax and needs an external solver install; overkill for 30 h.
- OR-Tools CP-SAT: integer-only (scale coefficients), strong for assignment/scheduling with logical constraints (e.g. rotation rules, adjacency); not natural for continuous areas and water balances. Use only if rotation is modelled as discrete assignment with many logical rules.
- Speed expectation (unmeasured, my estimate): LP/MILP with a few thousand variables solves in milliseconds to a couple of seconds with HiGHS; NSGA-II with pop 100 x 200 generations on a vectorised objective takes seconds to tens of seconds; so for slider-driven interaction precompute (profit tables, DP values) and keep the solve to LP/DP, and run NSGA-II only on a "compute Pareto" button.
- Recommended stack: pandas for tables -> numpy DP + scipy `linprog`/`milp` (or PuLP+HiGHS) -> FastAPI endpoint returning JSON (ranking, strategy table, shadow prices, Pareto points) -> web front end.

### Gaps
- No benchmark timings for PuLP/Pyomo/OR-Tools/pymoo on a farm-sized model were found; speed statements are estimates and should be measured on the real instance.
- PuLP default-solver packaging and HiGHS interface, Pyomo and CP-SAT docs were not successfully fetched (redirect/time budget), so claims about them are from general knowledge, not citations.

---

## Q6. Eliciting and encoding farmer preferences in a UI

### Takeaway
Map each preference to either a hard constraint (a number the farmer states) or a normalised weight/risk parameter; keep risk elicitation to one slider that maps to lambda in a CVaR/MOTAD objective, because eliciting full utility functions is known to be unreliable.

### Cited Findings
- Establishing reliable and stable decision-maker utility functions is difficult in practice (Binswanger 1980; Hazell & Norton 1986), which is why E-V and MOTAD frontiers are often reported as efficient sets rather than a single plan. — [Agrekon 28(1)](https://ageconsearch.umn.edu/record/267231/files/agrekon-28-01-006.pdf)
- Target-MOTAD parameterises risk by a target income T and an allowed expected shortfall lambda, and the full solution set can be generated by parametric programming over those two parameters. — [Target MOTAD literature record](https://ideas.repec.org/p/ags/aaea84/278966.html) (search-level)
- CVaR models are described as better suited to a risk-averse farmer. — [Filippi et al. 2017 record](https://iris.unibs.it/handle/11379/487654)
- Hardaker & Troncoso (1979) address MOTAD with subjectively elicited net-revenue distributions, i.e. eliciting beliefs about outcomes rather than utilities. — [IDEAS](https://ideas.repec.org/a/oup/erevae/v6y1979i1p47-60..html)

### Inferences
UI to model mapping (all editable, stored with the scenario so a result is reproducible):
| Control | Encoding |
|---|---|
| "Max months to first income" (slider/number) | hard filter t1_c <= T_max (also drops perennials when small) |
| "Money I can invest up front" (EUR/ha or EUR total) | hard constraint on peak cumulative negative cash (K) |
| "Water allotment" (m3/ha or m3/yr, per month if known) | LP capacity constraint W (and filter on per-crop demand) |
| "Labour available" (hours/month or no hired labour) | monthly capacity L_m |
| "Risk tolerance" (1-5 or "stable income" - "chase upside") | lambda in (1-lambda)E + lambda CVaR_alpha; map 1..5 -> lambda in {0,0.25,0.5,0.75,0.9}; also show the P10 income so the farmer sees what the slider means |
| "What matters to me" (profit / water saving / soil-N / low effort sliders) | weights in the weighted-sum/TOPSIS score, normalised to sum to 1; the same weights drive the epsilon-constraint Pareto selection |
| "Crops I will not grow / must grow" | bans / lower bounds on x_c |
| "Time horizon" (this season / 3 yr / 10 yr) | decides annuals-only vs including perennials NPV, discount rate r |
Good practice: preset personas (e.g. "cautious smallholder", "growth-oriented") as one-click slider settings for the demo; show a live "why was crop X excluded" list; show sensitivity (changing risk from 1 to 5 re-ranks).

### Gaps
- No empirical study on UI elicitation of risk attitudes for farmers (e.g. Holt-Laury lotteries for farmers, or sliders) was retrieved; the slider-to-lambda mapping is a design proposal, not a validated instrument.

---

## Research-process notes and caveats for the report writer
- Roughly 17 tool calls were used; several PDFs (CEUR 2024, arXiv 2604.06227 PDF, Akplogan, MAPA Murcia cost doc) were binary/unreadable or failed TLS, so those sources are cited at abstract/summary level. The HAL record for Dury et al. returned an access-denied page; its abstract came from a search summary.
- One factual correction from search: the Detlefsen & Jensen paper is in Agricultural Systems (2007) and uses network flows, not dynamic programming in the European Journal of Agronomy. A network longest-path is nonetheless computationally equivalent to the DP suggested above (my inference).
- Authorship of Dury et al. varies across records (Bergez, Dury, Reynaud, Schaller; one lists Garcia too). The "Therond/Navarrete" authors in the brief were not confirmed.
- Not verified at all: Hazell & Norton text contents, Hazell (1971) and Tauer (1983) primary papers, and any hard accuracy numbers for Spanish horticulture price forecasts.
