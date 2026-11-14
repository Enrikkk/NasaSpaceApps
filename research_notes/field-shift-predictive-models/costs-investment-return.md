# Production costs, establishment investment, breakeven and time-to-return for Campo de Cartagena / Murcia crops (Field Shift / RotaSat)

Research date: 2026-11-14. Convention: **VERIFIED** = I downloaded and read the document on this machine. **SEARCH-ONLY** = seen only in a search-tool summary, not opened. **DERIVED** = my arithmetic on verified numbers (shown so it can be re-checked). **ESTIMATE** = my judgement, no source. All € figures are nominal for the year stated; do not mix years without the inflation step in Q6.

Bottom line up front: the only full, retrievable, per-hectare Murcia cost-and-NPV study is the IMIDA book on lemon (García García 2014, prices ~2012-13). The IMIDA/MAPA vegetable, almond and artichoke cost tables (García García 2018/2019/2020 books) exist but the MAPA PDFs could not be opened from this machine (TLS failure on mapa.gob.es; I did not bypass certificate checks). For vegetables I therefore have only indirect evidence (per-kg cost, an IMIDA-derived corrected-circulante proxy, price/yield context). A teammate with a normal browser should open the five MAPA PDFs listed in Q1 and transcribe the tables; that closes the biggest gap.

---

## Q1. Can the IMIDA / CARM / MAPA cost studies be retrieved, and what do they cover?

### Takeaway
The studies are a three-book series by José García García (IMIDA), 2018 (citrus + stone fruit), 2019 (nuts, pome fruit, vine, olive), 2020 (open-air and greenhouse horticulture), reprinted as MAPA Observatorio PDFs and a 2023 organic-crops book (Técnica 45). Only the older IMIDA lemon book (2014) and the CARM-hosted organic-premium justification could be read in full; the MAPA PDFs remain blocked here by TLS.

### Cited Findings
- The series is documented in IMIDA's own bibliography: "Estructura de costes de las orientaciones productivas agrícolas de la Región de Murcia: frutales de hueso y cítricos" (García García 2018, 138 pp); "...frutos secos, frutales de pepita, vid y olivo" (2019, 128 pp); "...horticultura al aire libre y bajo invernadero" (2020, 138 pp). Data come from surveys of representative farms plus technicians; the accounting method follows MAGRAMA (2012). 42 production orientations were analysed (incl. limonero Fino, bróculi aire libre, melón piel de sapo). — [CARM, IMIDA "Justificación de primas a la agricultura ecológica", 20/12/2021](https://sede.carm.es/documentos/205/7.14-D.1%20Produccion%20ecologica%20generica%20(1).pdf) (VERIFIED)
- Table of contents (search summary) says the horticulture PDF has €/ha cost-structure tables for broccoli (p. 86), iceberg and Little Gem lettuce (pp. 88-89), piel de sapo and galia melon (pp. 90-91), artichoke, and establishment-investment tables; the citrus/stone-fruit PDF has "inversión y coste del inmovilizado" for lemon Fino/Verna; the nuts PDF has almond secano (7x7 m) and almond regadío 7x5.5 m RDC tables; the organic PDF (2023, Técnica 45) has rainfed almond p. 85 and broccoli p. 35. — SEARCH-ONLY, from [MAPA horticulture PDF](https://mapa.gob.es/es/alimentacion/temas/observatorio-cadena/estructuradecostesdelasorientacionesproductivasagricolasdelaregiondemurciahorticulturaalairelibreybajo_tcm30-690251.pdf), [citrus/stone fruit](https://mapa.gob.es/en/alimentacion/temas/observatorio-cadena/estructuradecostesdelasorientacionesproductivasagricolasdelaregiondemurciafrutalesdehuesoycitricos_tcm38-690249.pdf), [nuts/pome/vine](https://mapa.gob.es/en/alimentacion/temas/observatorio-cadena/estructuradecostesdelasorientacionesproductivasagricolasdelaregiondemurciafrutossecosfrutalesdepepitavi_tcm38-690250.pdf), [organic](https://mapa.gob.es/en/alimentacion/temas/observatorio-cadena/estructuradecostesdelosprincipalescultivosenagriculturaecologicadelaregiondemurcia_tcm38-690252.pdf)
- Fetch results on this machine: `mapa.gob.es` and `www.mapa.gob.es` fail TLS verification (curl ssl_verify_result=19; WebFetch "self signed certificate in certificate chain"); `servicio.mapa.gob.es` does verify, but the old `_tcm` URLs now 301-redirect to a new path that returns 404 on that host. Wayback Machine has no snapshot of the PDFs (availability API returned empty). core.ac.uk and MDPI return 403 to curl/WebFetch. — VERIFIED (own tests, 2026-11-14)
- New MAPA path revealed by the redirect (not openable here; try in a normal browser at `https://www.mapa.gob.es/` + this path): `dam/mapa/contenido/alimentacion/servicios/observatorio-de-precios-de-los-alimentos/nueva-estructura-oca-2024/estudios-de-costes-y-otros-estudios-de-interes/estudios-regionales/murcia/estructuradecostesdelasorientacionesproductivasagricolasdelaregiondemurciahorticulturaalairelibreybajo.pdf` (and the same folder with `...frutalesdehuesoycitricos.pdf`, `...frutossecosfrutalesdepepitavi.pdf`, `...estructuradecostesdelosprincipalescultivosenagriculturaecologicadelaregiondemurcia.pdf`). — VERIFIED redirect target, file itself unverified
- A 2025 IMIDA paper in MDPI Agriculture 15(23):2446 reports a cost structure for conventional broccoli in Murcia from a 2025 farmer survey, but I could not open it (403) — [MDPI](https://www.mdpi.com/2077-0472/15/23/2446) (SEARCH-ONLY). Also IMIDA 2025 "Economic and Environmental Assessment of Organic Lemon Cultivation" (DOI 10.3390/agronomy15061372, open access, not opened) — [IMIDA record](https://www.imida.es/-/garcia-castellanos-begona-et-l-economic-and-environmental-assessment-of-organic-lemon-cultivation-the-case-of-southeastern-spain-)
- Cajamar's "Análisis de la campaña hortofrutícola de la Región de Murcia" (2009/10 and 2010/11 editions, downloaded) discuss cost drivers (labour, inputs, water) qualitatively and contain no per-crop €/ha cost tables. — [2010/11](https://publicacionescajamar.es/wp-content/uploads/2023/03/analisis-de-la-campana-hortofruticola-12.pdf), [2009/10](https://publicacionescajamar.es/wp-content/uploads/2023/03/analisis-de-la-campana-hortofruticola-2.pdf) (VERIFIED, negative result)
- IMIDA uses "seguros" (insurance) as a named line in the working-capital (circulante) structure, treated as equal for conventional and organic. — [CARM/IMIDA 2021](https://sede.carm.es/documentos/205/7.14-D.1%20Produccion%20ecologica%20generica%20(1).pdf) (VERIFIED)

### Inferences
- The cost reference years of the 2018-2020 books are roughly 2017-2019 prices (surveys and the PDR 2014-2020 cost-simplification work cited 2016-17). Treat them as ~2018 € when inflating.
- The five MAPA PDFs are the single highest-value manual download for the team; everything in the vegetable rows below is a placeholder until they are transcribed.

### Gaps
- All €/ha tables for broccoli, lettuce, melon, artichoke, almond (regadío and secano), and the 2018 lemon update: files blocked. MDPI 2025 broccoli paper blocked (403).
- No Murcia COAG/ASAJA/UPA cost study with per-crop €/ha surfaced in searches.

---

## Q2. Lemon / citrus: establishment cost, years to production, annual costs, breakeven, payback

### Takeaway
IMIDA's lemon study (prices ~2012-13, 5 ha drip-fertigated farm) gives establishment of ~10,900 €/ha (of which only ~1,900 €/ha is the trees and planting; the rest is shed, irrigation head, network, reservoir), first sales in year 3, full production year 7 (Fino) or 8 (Verna), cash operating cost ~5,500 €/ha/yr excluding harvest, NPV-zero price 0.155 €/kg (Fino) and 0.215 €/kg (Verna), and payback 11-12 years with own funds (17 years if 100% financed). Lemon is a 10-12 year decision; it will never pass a "time to return < 3 years" filter.

### Cited Findings
All from [IMIDA, García García J. (2014), "Análisis del sector del limonero y evaluación económica de su cultivo", Serie Divulgación Técnica 06, CARM](https://conocimientoabierto.carm.es/jspui/bitstream/20.500.11914/862/1/LIBRO_Analisis_limonero.pdf) (VERIFIED, read in full; price/cost base: 1998-2012 prices, survey ~2012-13).

Farm model: 5 ha, 7x6 m (≈238 trees/ha), drip fertigation, ~190-64-137 kg N-P2O5-K2O/ha (Fino); irrigation 6,378 m³/ha (Fino) / 6,086 (Verna); full-production yield 48,000 kg/ha Fino, 36,000 kg/ha Verna; useful plantation life 22 years Fino, 25 Verna; discard 8% / 12.5%.

Establishment investment (Tables 9-10, 5 ha, €; per ha = /5):
- Shed + irrigation head building 12,000 (2,400 €/ha); irrigation head 11,810 (2,362); irrigation network 6,630 (1,326); **plantation (trees + planting) 9,390 (1,878 €/ha)**; auxiliary material 500 (100); regulating reservoir 14,335 (2,867). Total 54,665 € = **10,933 €/ha** (the Fino table prints 55,665, an apparent typo; 54,665/5 = 10,933 matches the printed per-ha figure).
- Equipment renewal 16,990 € in year 15 and 400 € auxiliary material every 5 years (Annex 5).

Annual cost structure at full production, Fino (Table 13, 5 ha, €; per ha = /5): fixed-fixed depreciation 2,560 (512 €/ha); pruning 2,617 (523); machinery 3,492 (698); phytosanitary 1,290 (258); fertiliser 3,558 (712); herbicide 305 (61); maintenance 463 (93); electricity 995 (199); permanent labour 7,917 (1,583); irrigation water 7,121 (1,424); circulante 27,758 (5,552); **total 30,318 = 6,064 €/ha, excluding harvest** (harvest is paid by the buyer). Water + electricity ≈ 27% of cost, permanent labour 26%. Verna total 29,694 (5,939 €/ha). Harvest ≈ 0.09 €/kg (Fino), 0.10 (Verna); cultivation + harvest "cost in origin" **10,431 €/ha Fino, 9,593 €/ha Verna**.
- Water price used: 0.22 €/m³ (literature 0.15-0.26 €/m³; Segura basin). Wage assumption 13,920 €/UTA-year incl. social security, 1,800 h/UTA (≈7.7 €/h). Harvest 600-700 kg per jornal (7-9 h).
- Production / revenue ramp (Annex 5, 5 ha): Fino sales 0, 0, 6,682, 13,363, 22,272, 33,408, 44,544 € in years 1-7 (i.e. 0%, 0%, 15%, 30%, 50%, 75%, 100% of full); Verna 0, 0, 4,613, 9,225, 18,450, 27,675, 36,900, 46,125 (full from year 8). Operating payments Fino years 1-7: 4,572; 6,455; 11,206; 16,682; 21,383; 27,326; 27,326 €. Prices assumed (mean 1998-2012 at origin): 0.20 €/kg all-lemon Fino, 0.29 €/kg Verna; discard 0.02 €/kg.
- Financial evaluation (real interest 1.5%; loans 8 yr, 1 yr grace, 5.5% nominal): own funds Fino NPV 139,200 €, IRR 9.93%, payback 11 yr; Verna NPV 188,356, IRR 10.26%, payback 12. 50% borrowed: IRR 7.44% / 8.14%, payback 13 / 14. 100% borrowed: IRR 5.29% / 6.33%, payback 17 / 17.
- Viability thresholds: NPV = 0 price **0.155 €/kg Fino, 0.215 €/kg Verna** (own funds); +0.01 €/kg per step of external financing (0.175 / 0.240 at 100% debt). Full-production average cost 0.14 €/kg Fino, 0.19 €/kg Verna (cultivation only). Minimum yield at mean price: ≈30,000 kg/ha Fino, ≈20,000 kg/ha Verna in a full-production year; lifetime-compensated 37,655 / 26,840 kg/ha. Minimum farm size 3.9 / 3.7 ha.
- Water efficiency (full production): 7.53 kg/m³ and 1.40 €/m³ gross, margin 0.45 €/m³ (Fino); 5.92 kg/m³, 1.52 €/m³, 0.54 €/m³ (Verna). Maximum water price compatible with NPV = 0: 0.50 (Fino) / 0.57 (Verna) €/m³ (so lemon survives the 0.33-0.38 subsidised price but only just survives unsubsidised desalination at 0.60-0.80).
- Labour: cultivation + harvest 0.48 UTA/ha (Fino), 0.43 (Verna); harvest alone 0.15 UTA/ha; CARM's own rural-development guideline gives 0.40 UTA/ha for drip lemon. With 1,800 h/UTA that is ≈ 860 h/ha/yr (Fino).
- Marketing (packing house) cost 0.415 €/kg (0.34 domestic): transport to warehouse 0.014, handling labour 0.093, packaging 0.096, international transport 0.15.
- Context: ~22,000 ha of the ~38,000 ha of Spanish lemon are in Murcia (57%). — [IMIDA 2014 book](https://conocimientoabierto.carm.es/jspui/bitstream/20.500.11914/862/1/LIBRO_Analisis_limonero.pdf) and search summary of [CARM](https://transparencia.carm.es/wres/transparencia/doc/Consejo_Gobierno/2024-09-26/punto_09_ayuda_ailimpo.pdf)
- 2018 IMIDA update (cross-check): the organic-premium document computes the "corrected circulante" overcost for citrus at 10% = 800 €/ha, implying a corrected working capital (circulante minus insurance, irrigation water+energy, maintenance) of ≈8,000 €/ha for conventional citrus (average of Fino, Verna, grapefruit; includes harvest). — [CARM/IMIDA 2021](https://sede.carm.es/documentos/205/7.14-D.1%20Produccion%20ecologica%20generica%20(1).pdf) (VERIFIED; the 8,000 is DERIVED = 800/0.10)

DERIVED from the IMIDA 2014 cash-flow tables (per ha, 2012-13 €; Fino; "cash" = operating payments excluding harvest and depreciation):
| Year | Op. payments €/ha | Sales €/ha | Net €/ha | Cumulative (excl. 10,933 €/ha investment) |
|---|---|---|---|---|
| 1 | 914 | 0 | -914 | -914 |
| 2 | 1,291 | 0 | -1,291 | -2,205 |
| 3 | 2,241 | 1,336 | -905 | -3,110 |
| 4 | 3,336 | 2,673 | -663 | -3,773 |
| 5 | 4,277 | 4,454 | +178 | -3,595 |
| 6 | 5,465 | 6,682 | +1,217 | -2,378 |
| 7+ | 5,465 | 8,909 | +3,444 | +1,066 at y7 |
Peak funding need ≈ 10,933 + 3,773 ≈ **14,700 €/ha** (2012-13 €), reached around year 4. Annual net at full production ≈ 3,440 €/ha before harvest cost (harvest is borne by the buyer at the stated prices, hence "price at tree").

### Inferences
- For a RotaSat "initial investment" filter: lemon ≈ 11,000 €/ha capex + ≈3,800 €/ha negative operating cash before it turns positive, in 2012-13 money. If inflated with the factor in Q6 (×1.25-1.35, ESTIMATE) that is roughly 14,000-15,000 €/ha capex and 18,000-20,000 €/ha peak funding in 2026 money. Plantation material itself (1,878 €/ha in 2012-13) is the minor part: a farmer who already has the irrigation infrastructure faces a much lower marginal capex (≈2,000-2,600 €/ha trees+planting, inflated) but the same 6-7 year wait.
- Time to first income: year 3 (small, 15% of full); year 5 operating break-even; year 7-8 full production; payback 11-12 yr. Lemon should be flagged "long-term, high liquidity need" (the IMIDA text says working capital ≈ 27,000 € per 5 ha per year, 11x the annual depreciation share).
- The 2012-13 price assumption (0.20 €/kg) and yield 48 t/ha are survey values for professional farms; regional average yield is likely lower and market prices have varied widely since. Use the NPV-zero price (0.155 €/kg) as the structural threshold and revalue it for 2026 inputs (Q6) before comparing with current farm-gate prices.
- Water: 6,000-6,400 m³/ha at 0.35 €/m³ (2026 subsidised) is ≈2,200 €/ha vs 1,424 €/ha in the book: water alone adds ≈ +800 €/ha/yr to the cost line.

### Gaps
- No 2018 or 2024 lemon €/ha table (MAPA PDF blocked). No sourced current (2025/26) farm-gate lemon price in this pass (existing notes in prices-and-decision-layer.md may have it).
- Orange/mandarin/grapefruit economics not retrieved.
- Adoption of the Mar Menor regional rules (nitrate zones) on citrus fertiliser costs not assessed.

---

## Q3. Almond (and rainfed alternatives): establishment cost, years to production, cost per ha, breakeven

### Takeaway
Rainfed almond in Murcia has a very low cost (~1,300 €/ha) and a very low, unstable yield (200-300 kg/ha marketable), so the cost per kg is 4.3-6.5 €/kg and cooperatives say prices are below cost; irrigated almond (RDC) is a different, mostly un-sourced economy (reported yields >2,500 kg kernel/ha with 5,000-6,000 m³/ha, production starting year 3). No sourced establishment cost per ha for almond in Murcia could be retrieved; it sits in the blocked MAPA "frutos secos" PDF.

### Cited Findings
- Rainfed ecological almond cost ≈ 1,300 €/ha (citing García García 2023, Publicación Técnica 45); effective cost per kg at best 4.33 €/kg at 300 kg/ha. Conventional yield 200-300 kg/ha marketable almond, ecological 120-150 kg/ha. Table: cost €/kg at yield kg/ha: 100→13.00; 150→8.67; 200→6.50; 250→5.20; 300→4.33. The cooperatives say offered prices are below effective cost; harvest forecast −36% vs last 3-campaign average. Article date 17 Sept 2023, figures from Fecoam. — [eComercio Agrario, 17/09/2023](https://ecomercioagrario.com/?p=121485) (VERIFIED, via WebFetch)
- The table is exactly 1,300 €/ha divided by yield (e.g. 1,300/200 = 6.50; 1,300/300 = 4.33), so it is a fixed-cost-per-ha view, not a variable-cost model. (DERIVED check of the above)
- Murcia has ≈76,400 ha of almond, ≈9% irrigated. The same search summary lists a "cost of ≈5 €/kg" for Murcia almond. — SEARCH-ONLY: [eComercio Agrario](https://ecomercioagrario.com/?p=139907), [Agronews](https://www.agronewscastillayleon.com/murcia-replanta-almendro/)
- Irrigated almond: full crop-water satisfaction needs 5,000-6,000 m³/ha with yields above 2,500 kg kernel/ha; another source gives production from year 3 (≈1,000-1,200 kg/ha) rising to 2,500-3,000 kg/ha from year 7, productive life ≥20 years; irrigation allows 300-400 trees/ha vs ≤200 rainfed. — SEARCH-ONLY, from the Cajamar technical presentation [Egea, diseño y manejo de plantaciones de almendro en secano duro y secanos con riegos de apoyo](https://www.cajamar.es/storage/documents/03-diseno-y-manejo-en-plantaciones-de-almendro-en-secano-duro-y-secanos-con-riegos-de-apoyo-j-egea-1472645474-547bd.pdf) (not opened by me)
- CARM aid for replacing drought-killed rainfed almond trees: 12 €/tree in the 2025 draft order (was 6 €/tree in 2014), budget 4.5 M€ over 3 years, ~1,200 beneficiaries; trees must be replanted at the same frame, secano only (irrigation coefficient 0). — [CARM Transparencia, MAIN 16/04/2025](https://transparencia.carm.es/wres/transparencia/doc/IniciativasNormativas/2025_AGRICULTURA_Almendro_secano/MAIN.pdf) (VERIFIED)
- Organic-premium overcost for "Frutos secos" (almond secano + almond regadío RDC with <1,200 m³/ha): 440 €/ha at 25% of corrected circulante → corrected working capital ≈1,760 €/ha for conventional nuts (DERIVED = 440/0.25; average of the two systems). — [CARM/IMIDA 2021](https://sede.carm.es/documentos/205/7.14-D.1%20Produccion%20ecologica%20generica%20(1).pdf) (VERIFIED)
- Existing team notes already give almond secano gross income ≈300 €/ha (0.2 t in shell × kernel ratio × 5.35 €/kg) — see murcia_agro_context.md (not re-verified here).

### Inferences
- Cross-checking the existing 300 €/ha gross income (secano almond) against ≈1,300 €/ha cost shows a structural loss; breakeven yield at 5.35 €/kg kernel is 1,300 / 5.35 ≈ 243 kg kernel/ha. The article's 200-300 kg/ha may be in-shell or marketable almond — the unit is not stated, so the yield unit must be confirmed before using it as kernel.
- Time to first income for irrigated almond is ~3 years but full ~7; with no sourced capex I cannot fill the investment column. ESTIMATE only: the irrigation infrastructure items in the lemon budget (head, network, shed ≈ 6,100 €/ha ex-reservoir, 2012-13) are broadly comparable, plus trees at 300-400/ha; confirm in the MAPA nuts PDF (table "inversión inicial en red de riego y plantación", almond regadío 7x5.5 m).
- In RotaSat, pistachio/olive-in-secano were not found in any retrieved source; do not include them in crops.csv without a source.

### Gaps
- Establishment €/ha (planting + irrigation) for irrigated almond, years to full production, irrigated costs/ha and NPV in Murcia: MAPA 2019 book blocked.
- Pistachio and olive-secano costs: no source found.
- The 2019 "Análisis socioeconómico del cultivo del almendro en la Región de Murcia" (García García & Payá, Fruticultura 70:40-49) is a probable NPV source but was not located.

---

## Q4. Annual vegetables and artichoke: variable costs, breakeven, months to first sale, labour

### Takeaway
No retrievable Murcia €/ha cost table for broccoli, lettuce, melon or artichoke was found; the only hard anchors are a per-kg broccoli cost (~0.39-0.40 €/kg, undated), an IMIDA-derived average non-water working-capital of ≈6,300 €/ha per horticultural cycle, a Canary lettuce structure (not transferable), and the water cost. The breakeven columns for vegetables should be built as cost = f(yield) once the MAPA horticulture PDF (tables 27-29 etc.) is transcribed.

### Cited Findings
- Organic-premium overcost for "Hortalizas" (average over artichoke, celery, iceberg lettuce, Little Gem lettuce, galia/cantaloupe melon) is 626 €/ha at 10% of corrected circulante → corrected circulante ≈ 6,260 €/ha per crop cycle, excluding insurance, irrigation (water + energy) and maintenance. — [CARM/IMIDA 2021](https://sede.carm.es/documentos/205/7.14-D.1%20Produccion%20ecologica%20generica%20(1).pdf) (VERIFIED; the 6,260 is DERIVED = 626/0.10, an average over those five crops, so individual crops will deviate)
- Broccoli production cost ≈ 0.39-0.40 €/kg against producer prices 0.90-1.20 €/kg in a good year; in a bad year (Lorca report) ≈ 0.20 €/kg price vs 0.39 €/kg cost. Neither article date was retrievable (likely 2016-2020). — SEARCH-ONLY via [HortiDaily](https://hortidaily.com/article/6000210/spain-vegetables-giving-murcia-s-economy-a-breather) and [Murcia Today 04/02/2020](https://murciatoday.com/murcia-crop-farmers-up-in-arms-over-low-market-prices_1302239-a.html)
- A large southeastern-Spain grower (350-400 ha of lettuce, broccoli, courgette, pepper, melon, watermelon) says that in a recent broccoli cycle the gap between profit and loss was "apenas tres céntimos" (unit unspecified). Article dated 10/03/2026. — [Interempresas 10/03/2026](https://www.interempresas.net/Horticola/624997-Horticultura-del-Sureste-organizar-para-crecer-digitalizar-para-decidir.html) (VERIFIED, via WebFetch)
- MAPA 2010 horticulture report: irrigated lettuce full production cost 37,848 €/ha and profit 10,620 €/ha for some case (≈2009-10); the same report gives net margins +667.55 and −586.09 €/ha for irrigated lettuce. The two are not reconcilable from the summaries, region and cycle count are unknown. — SEARCH-ONLY, [MAPA Hortícolas 2010](https://mapa.gob.es/es/ministerio/servicios/analisis-y-prospectiva/Hort%C3%ADcolas.2010_tcm30-88515.pdf); treat as unreliable.
- Canary Islands lettuce 2019/20 (not transferable): ≈0.33 €/kg total cost and ≈11,160 €/ha direct cost per cycle — [MAPA ficha](https://servicio.mapama.gob.es/en/alimentacion/temas/observatorio-cadena/ficha-costes-lechuga_tcm38-689119.pdf) (SEARCH-ONLY, per existing spanish-eu-data.md)
- Water at 0.35 €/m³: lettuce + melon at ≈11,500 m³/ha ≈ 4,000 €/ha/yr; lettuce + legume ≈7,600 m³/ha ≈ 2,660 €/ha/yr (existing team note, murcia_agro_context.md; not re-verified).
- Gross incomes already in the team notes: broccoli ≈9,600 €/ha (15 t × 650 €/t), melon ≈21,000 €/ha (33 t × 650 €/t, flagged suspect), artichoke ≈9,900 €/ha (17 t × 590 €/t). Artichoke yield context: Murcia official ≈13.2-14.1 t/ha (MAPA Anuario 2020 / 2023-avance, possibly mis-aligned table text) vs Vega Baja trial 27.8-36.4 t/ha (MAPA Horticultura 2002); farm-gate price cited 1.5 €/kg (domestic) and 0.90 €/kg (other) in a post-DANA 2019 article; artichoke area ~2,000 ha in the Vega Baja, 60% lost to the DANA. — SEARCH-ONLY: [MAPA Anuario 2023-avance](https://mapa.gob.es/estadistica/pags/anuario/2023-Avance/FORMATO%20PDF/AE23-C07/7.6.31.2.pdf), [Alicante Plaza](https://alicanteplaza.es/alicanteplaza/el-frio-provoca-la-bajada-de-categoria-en-algunos-cultivos-alcahofa-pero-duplica-el-precio-en-otros)
- Artichoke crop cycle in the IMIDA/CARM system: planting 15 Jul-15 Aug, first harvest Nov-Jan, shred, regrowth, second harvest Apr-May, then shred (so annual-cycle, two flushes, not a multi-year planting). Reference machinery prices in the same CARM document: tractor 100-110 CV + implement 39 €/h, 120 CV + implement 45 €/h (document undated, produced for PDR 2014-2020 extension, ≈2018-2022); shredding and rotavator passes 4.0 and 2.0 h/ha. — [CARM, IMIDA artichoke incorporation sheet](https://sede.carm.es/documentos/205/7.2.%20Incorporaci%C3%B3n%20alcachofa.pdf) (VERIFIED)
- Murcia horticulture is labour-intensive; the lemon study uses 7.7 €/h incl. social security (2012-13); Cajamar documents the 2012 agricultural social-security reform and a 67% foreign share in agrarian-regime workers (2011). — [Cajamar 2010/11](https://publicacionescajamar.es/wp-content/uploads/2023/03/analisis-de-la-campana-hortofruticola-12.pdf) (VERIFIED)

### Inferences
- Variable-cost placeholders for the engine until the MAPA tables are transcribed (all ESTIMATE, 2018-19 € basis, per cycle): non-water working capital ≈6,300 €/ha on average; add water (0.35 €/m³ × crop m³) and insurance. So broccoli total variable cost per cycle ≈ 6,300 + water 1,000-1,500 ≈ 7,500-8,000 €/ha (2018-19 €) → at 15 t/ha a breakeven price ≈ 0.50-0.55 €/kg, consistent in order of magnitude with the 0.39-0.40 €/kg report (which probably omits some items). Inflated ×1.26 (Q6) ≈ 0.63-0.69 €/kg.
- Breakeven yield = cost per ha / expected price; for broccoli at 650 €/t (existing note) and 8,000-9,500 €/ha, breakeven ≈ 12-15 t/ha, i.e. at or just below the 15 t/ha used for gross income, which fits "difference between profit and loss is 3 cents".
- Time from planting/sowing to first sale (general agronomic ranges, not from a retrieved source, ESTIMATE): lettuce 2-3 months from transplant; broccoli 3-4 months; melon 3.5-4.5 months from transplant; artichoke 3.5-5 months from planting (CARM calendar: mid-Jul/Aug planting → Nov first harvest). These are all < 6 months: they pass any "time to return < 1 year" filter, but price risk per cycle is high (see broccoli margin of "three cents").
- Establishment investment for annuals: no sourced capex. The farm-level irrigation infrastructure is the same type as the lemon budget (shed + head + network ≈ 6,100 €/ha ex-reservoir, 2012-13); marginal per-crop capex for an already-equipped farm is ≈0 (plastic mulch, tunnels are variable costs). RotaSat can treat annuals as capex ≈ 0 vs perennials 11,000 €/ha (lemon).
- Labour hours/ha for vegetables: not retrieved. The lemon figure (860 h/ha/yr) is far lower than horticulture, which I expect to be several times higher per cycle (ESTIMATE; confirm from MAPA tables).

### Gaps
- All Murcia horticulture €/ha line items (plants, fertiliser, plastic, harvest, labour) and labour hours/ha; the 2025 IMIDA/MDPI broccoli cost structure is the best candidate (blocked).
- Artichoke €/ha costs, and whether multi-year artichoke stands (5-6 years) exist in Murcia (CARM doc suggests annual replanting).
- Melon cost per ha and legume (faba/pea) cost per ha.
- Dates of the per-kg broccoli articles.

---

## Q5. Financing and insurance context (brief)

### Takeaway
Agroseguro is subsidised (~45% national average premium subsidy in 2025) and IMIDA lists insurance as a named cost line, but the per-hectare premiums for Murcia crops were not found. Credit assumptions in the IMIDA lemon study (5.5% nominal, 8 years, 1 year grace) and the IRR sensitivity are the only quantitative financing evidence.

### Cited Findings
- Agroseguro's citrus presentation (Valencia, 5 Mar 2026) shows the national average subsidy at 45% (2025); ENESA and regional governments together subsidise almost 50% of premiums; a 2026 CARM insurance-subsidy draft exists. — SEARCH-ONLY: [Agroseguro citrus Valencia 2026](https://agroseguro.es/wp-content/uploads/2026/03/PRESENTACION-CITRICOS-VALENCIA-05_03_2026.pdf), [CARM draft](https://transparencia.carm.es/wres/transparencia/doc/IniciativasNormativas/2026_INI_AGRICULTURA_seguros_agrarios/Borrador.pdf)
- 2025 Agroseguro indemnities: citrus 86.53 M€ and hortalizas 73.63 M€ nationally, damage concentrated in Andalucía, Valencia and Murcia. — SEARCH-ONLY: [Agroseguro 2025 evolution](https://agroseguro.es/wp-content/uploads/2026/04/NP_Agroseguro-presenta-la-evolucion-de-los-seguros-agrarios-en-2025.pdf)
- IMIDA financing assumptions and effect on lemon IRR/payback: see Q2 (own funds 9.93%/11 yr → 100% debt 5.29%/17 yr). — [IMIDA 2014](https://conocimientoabierto.carm.es/jspui/bitstream/20.500.11914/862/1/LIBRO_Analisis_limonero.pdf) (VERIFIED)
- Murcia PAC eco-scheme P3 ~142 €/ha (regadío) already in murcia_agro_context.md; rainfed almond tree-replacement aid 12 €/tree (Q3).

### Inferences
- For the engine, insurance can be a flat % line item (ESTIMATE, not sourced): entering premium €/ha as a configurable parameter defaulted to a small value, flagged "to calibrate from Agroseguro tariff".
- A "financed" toggle is cheap to add: the IMIDA result says debt financing raises the NPV-zero lemon price by ~0.01 €/kg per 50% tranche at 5.5% (2012-13 rates).

### Gaps
- Agroseguro premium €/ha by crop/module for Murcia; current agricultural credit rates (2026).

---

## Q6. Updating 2010-2019 costs to 2026: which index and what factor?

### Takeaway
Use the MAPA "Índices de precios pagados por los agricultores" (base 2020 = 100) for input items and a labour-specific update for wages. The index stood at 126.23 in January 2025 (base 2020); a press report quotes +29.5% since 2020; CPI compounding of the published average annual rates gives +22% 2020→2025. So roughly ×1.26-1.30 for 2020-based costs, and the IMIDA 2018-2020 books (2017-19 prices) similarly ×1.28-1.35 (ESTIMATE).

### Cited Findings
- MAPA publishes monthly "Índices y precios pagados agrarios" PDFs (base 2020 = 100); the general index was **126.23 in January 2025** (−4.83% y/y, mainly fuels; fertilisers and energy also fell). — [MAPA, Índices y precios pagados, enero 2025](https://servicio.mapa.gob.es/ca/estadistica/temas/estadisticas-agrarias/indicesypreciospagadosagrariospublicacion2025enero_tcm34-707242.pdf) (SEARCH-ONLY summary), index page [MAPA precios pagados](https://www.mapa.gob.es/en/estadistica/temas/estadisticas-agrarias/economia/precios-percibidos-pagados/precios-pagados-por-los-agricultores-y-ganaderos)
- Nov 2025: paid-prices index +1.82% y/y, fertilisers +11.37%, energy −8.37% (press replica of MAPA data); April 2026: +3.02% y/y, fuels ≈ +39.9%, phosphate fertilisers ≈ +36%; a newspaper says production costs rose 29.54% since 2020 per the ministry (not confirmed in the original). — SEARCH-ONLY: [Agronews, precios agrarios nov 2025](https://www.agronewscastillayleon.com/precios-agrarios-nov-2025), [Diario de León](https://www.diariodeleon.es/monograficos/agro/260815/2094070/precios-costes-siguen-alza.html)
- Spain CPI annual average: 3.1% (2021), 8.4% (2022), 3.5% (2023), 2.8% (2024), 2.7% (2025; INE confirms 2.7% for 2025 and 2.9% y/y December). INE moves the CPI to base 2025 from January 2026 (series splice needed). — [Focus Economics](https://www.focus-economics.com/es/country-indicator/espana/inflation/) (aggregator), [INE IPC Dec 2025](https://ine.es/dyngs/Prensa/IPC1225.htm?print=1) (SEARCH-ONLY)

### Inferences
- DERIVED: compounding 3.1%, 8.4%, 3.5%, 2.8%, 2.7% gives 1.031 × 1.084 × 1.035 × 1.028 × 1.027 ≈ 1.221, i.e. +22% general CPI from 2020 to 2025. The agri-input index (+26% if the Jan 2025 level of 126.23 holds; +29.5% per press) outran CPI, driven by fertiliser, energy and fuel in 2022.
- Practical rule for the engine: C2026 = C_year × index(2026)/index(year). For IMIDA 2018-2020 cost tables use the MAPA index with base year ≈ 2018-19 (index not retrieved; roughly 2019 ≈ 2020 level) ⇒ factor ≈ 1.26-1.30. For the 2012-13 lemon book add the 2012→2020 drift (not retrieved; general CPI was low, a few percent) ⇒ ≈ 1.27-1.35 (ESTIMATE). Update separately: water (use 0.33-0.38 €/m³ directly instead of 0.22), labour (agricultural wage agreements and the 2022-2025 SMI increases rose faster than CPI; not researched), and fertiliser (2022 spike, 2024 drop, 2025-26 rise: sensitive to the year chosen).
- Present all inflated numbers with a ±15% band and a "prices of 2018-19 inflated by X" label in the UI.

### Gaps
- The exact MAPA index values for 2012, 2018, 2019 and the latest month of 2026; the paid-prices PDFs were only seen as search summaries. Wage index for agricultural labour in Murcia.

---

## Q7. What can go into crops.csv / the engine now (summary of the above, mostly DERIVED)

### Takeaway
Only lemon has a complete sourced economic profile; almond has a sourced rainfed cost and an unsourced irrigated profile; vegetables need the MAPA table transcription. Provide the engine with two sets of fields: sourced values (flag `source=IMIDA2014`) and placeholders (`flag=estimate`).

### Cited Findings
- Table below. All lemon values come from [IMIDA 2014](https://conocimientoabierto.carm.es/jspui/bitstream/20.500.11914/862/1/LIBRO_Analisis_limonero.pdf); almond from [eComercio Agrario 2023](https://ecomercioagrario.com/?p=121485); the rest are DERIVED or ESTIMATE as marked.

| Crop | Capex €/ha (year €) | Time to first income | Time to full production | Payback | Variable/cash cost €/ha/yr (year €) | Breakeven price €/kg | Breakeven yield kg/ha | Labour h/ha/yr | Status |
|---|---|---|---|---|---|---|---|---|---|
| Lemon Fino (drip, 5 ha farm) | 10,933 (2012-13) | year 3 (15% of full) | year 7 | 11 yr own funds (17 yr 100% debt) | 5,465 cash excl. harvest; 6,064 incl. depreciation; 10,431 incl. harvest | 0.155 NPV-zero; 0.14 cultivation-only at 48 t/ha | ≈30,000 (full-yr) / 37,655 (lifetime) | ≈860 (0.48 UTA × 1,800 h) | VERIFIED source, 2012-13 prices |
| Lemon Verna | 10,933 (2012-13) | year 3 (10%) | year 8 | 12 yr (17 debt) | 5,352 cash; 5,939 incl. depreciation; 9,593 incl. harvest | 0.215 NPV-zero | ≈20,000 / 26,840 | ≈770 (0.43 UTA) | VERIFIED source |
| Almond secano (organic 2023 cost) | not retrieved | not retrieved | not retrieved | not retrieved | ≈1,300 (2023) | 4.33-6.50 €/kg at 300-200 kg/ha (unit unconfirmed) | ≈243 kg kernel/ha at 5.35 €/kg (DERIVED) | not retrieved | PARTIAL |
| Almond regadío RDC | not retrieved (ESTIMATE ≥ lemon infrastructure ≈6,000 + trees) | year 3 (~1,000-1,200 kg/ha, SEARCH-ONLY) | year 7 (2,500-3,000 kg/ha) | not retrieved | corrected circulante nuts avg ≈1,760 (DERIVED, 2018-19) | not retrieved | not retrieved | not retrieved | GAP |
| Broccoli | ≈0 marginal (ESTIMATE) | ~3-4 months (ESTIMATE) | single cycle | < 1 yr | ≈7,500-8,000 (ESTIMATE, 2018-19 €) | ≈0.50-0.55 (ESTIMATE) vs 0.39-0.40 reported | ≈12-15 t/ha at 650 €/t (DERIVED) | not retrieved | PLACEHOLDER |
| Lettuce | ≈0 marginal | ~2-3 months (ESTIMATE) | single cycle | < 1 yr | ≈6,300 non-water avg (DERIVED, 2018-19) + water | not retrieved | not retrieved | not retrieved | PLACEHOLDER |
| Melon | ≈0 marginal | ~3.5-4.5 months (ESTIMATE) | single cycle | < 1 yr | ≈6,300 non-water avg + water | not retrieved | not retrieved | not retrieved | PLACEHOLDER |
| Artichoke | ≈0 marginal | planting mid-Jul/Aug → first harvest Nov (CARM calendar), ≈3.5-5 months | second flush Apr-May | < 1 yr | ≈6,300 non-water avg + water | not retrieved | not retrieved | not retrieved | PLACEHOLDER |
| Faba/barley rainfed | ≈0 | one season | n/a | n/a | not retrieved | not retrieved | not retrieved | not retrieved | GAP |

### Inferences
- A "time to return" filter naturally partitions the crop set: annuals (<1 yr, price-risk high), lemon/citrus (payback 11-12 yr, working capital 14,700 €/ha peak), almond secano (never pays back at 2023 prices if the 1,300 €/ha cost and 200-300 kg/ha yield hold), almond regadío (unknown). For the demo, show lemon with its sourced cash-flow table and mark everything else "indicative".
- For T-012's `breakeven EUR/ha`: lemon 6,064 €/ha (2012-13, excluding harvest) or 10,431 €/ha including harvest; inflate (×1.27-1.35, ESTIMATE) ⇒ ≈7,700-8,200 and ≈13,200-14,100 €/ha (2026, indicative). Vegetables should use the placeholder above until transcription.

### Gaps
- Everything marked "not retrieved" or PLACEHOLDER; the single action that closes most of it is transcribing the MAPA/IMIDA horticulture, citrus and nuts tables (Q1).
