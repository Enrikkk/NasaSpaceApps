# Satellite + weather ML for yield prediction, crop-type mapping, domain transfer and uncertainty (Field Shift, Campo de Cartagena)

Research date: 2026-11-14. Method: web search + fetch of primary papers/model cards. Where only a secondary summary was available, this is stated. Anything without a source is in "Gaps" or "Inferences", not in "Cited Findings".

---

## 1. Yield prediction: gradient boosting / RF vs deep models (CNN-RNN, LSTM, Deep GP); typical accuracy, data needs, field vs county scale

### Takeaway
At county scale, tree ensembles (XGBoost/RF) on tabular weather+soil(+NDVI) features usually match or beat LSTM/DNN, especially with little data; deep models win mainly when long histories (decades x ~1,000 counties) and sequential weather are available (Khaki CNN-RNN: ~8-9% relative RMSE). Field-level satellite-only yield mapping is far weaker (r2 ~0.4-0.45) and county aggregation raises it (r2 ~0.69). Every strong number in the literature rests on US NASS/yield-monitor labels that do not exist for Murcia horticulture.

### Cited Findings
- County-level soybean study over 959 Midwest counties: XGBoost test R2 = 0.82, RMSE = 0.246 t/ha, and it outperformed LSTM and DNN on identical inputs (secondary search summary of the IJAEOG 2023 paper; verify before quoting) — [DOAJ record](https://doaj.org/article/0d75730d9ecb42849b4ca95fdc397df1); a separate Bonn study (Extreme Gradient Boosting for Yield Estimation compared with Deep Learning) also reports XGBoost beating DL on RMSE and R2 for US soybean — [arXiv 2208.12633](https://arxiv.org/abs/2208.12633v1)
- US Corn Belt county forecasting with only 5 training years (2012-2016): RF had the lowest RMSE, 0.342 t/ha, then XGBoost 0.373 t/ha; the 1D-CNN was best in only one year (2018, RMSE 0.280 t/ha) (secondary summary; paper not opened) — [Springer, s11540-024-09753-w](https://link.springer.com/article/10.1007/s11540-024-09753-w)
- Khaki, Wang & Archontoulis CNN-RNN (13 Corn Belt states): trained on 1980 up to the year before each validation year, 1,176 corn counties and 1,115 soybean counties; test years 2016-2018. Corn RMSE 16.48 / 15.74 / 17.64 bu/ac vs RF 25.48 / 29.40 / 26.02, DFNN 27.23 / 23.88 / 21.37, LASSO 32.58 / 27.06 / 31.30. Soybean RMSE 4.15 / 4.32 / 4.91 vs RF 8.69 / 8.61 / 12.78. CNN-RNN RMSE about 9% (corn) and 8% (soybean) of mean yield. Inputs: 6 weekly-averaged daily weather variables (Daymet), gSSURGO soil, weekly planting progress, historical mean yield. **No remote sensing and no uncertainty estimates.** 5-fold CV on unseen locations (2018): corn RMSE 24.10, soybean 6.35 — [Khaki et al., Front. Plant Sci. (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6993602/)
- Note on the above: in Khaki's own comparison, RF is the weak baseline (RMSE ~1.5-2x CNN-RNN), which contradicts the "trees beat deep" results above; the difference is training-set size (about 39 years x >1,000 counties) and the feature set. Treat "which is better" as data-volume dependent — [Khaki et al. (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6993602/) vs [Springer 2024](https://link.springer.com/article/10.1007/s11540-024-09753-w)
- You et al. 2017 Deep Gaussian Process: county-level US soybean yield from MODIS spectral-band/temperature **histograms** (CNN/LSTM feature learners + GP layer for spatio-temporal correlation); abstract-level claim of 30% RMSE reduction vs traditional remote-sensing methods and 15% MAPE improvement over USDA national-level estimates — [AAAI 2017](https://ojs.aaai.org/index.php/AAAI/article/view/11172). Reimplementation notes the original MODIS data for the top-11 soybean states needs just over 110 GB — [pycrop-yield-prediction](https://github.com/gabrieltseng/pycrop-yield-prediction)
- European regional yield forecasting (Paudel et al. 2023): LSTM / 1D-CNN statistically better than GBDT for German soft wheat, similar to GBDT in all other case studies; the 2021 Paudel baseline paper built an explainable-feature ML baseline without information leakage, early-season accuracy comparable with the EU MARS system, end-of-season worse than MARS for DE and FR — [AGRIS record (2023)](https://agris.fao.org/search/fr/records/669f6fe200eb85b7d72ced4a); [IDEAS (2021)](https://ideas.repec.org/a/eee/agisys/v187y2021ics0308521x20308775.html)
- Field/pixel scale from satellite alone (SCYM, crop-model-trained, no ground labels): original SCYM captured 14-58% (mean 35%) of maize yield variation in US state-years; improved versions explain 41-83% of multi-year variation across nine Midwest states, RMSE typically <1 t/ha. Deines et al. 2021 (over 1 million yield-monitor maize observations): r2 = 0.31 -> 0.40 at 30 m pixel after harmonic smoothing, 0.45 at field, 0.69 at county — [Lobell lab summary / Jin et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC5338538) ; [X-MOL abstract of Deines et al. RSE 2021](https://www.x-mol.com/paper/1328096325776089088)

### Inferences
- With 30 h and no yield labels for Murcia, a trained yield regressor for Murcia is not credible. What is defensible: (a) tree-ensemble model trained on US county/field data with climate-normalised features, shown as a methodological demo; or (b) SCYM-style approach (crop-model simulation -> regression on satellite+weather, no ground labels) described as the route to Spain.
- Tree models + 30-40 years x ~1,000 counties is a laptop-hours problem (seconds-minutes per fit); the CNN-RNN needs that data volume and GPU-hours, so it is not a sensible first choice for the team.
- Field-level r2 ~0.4-0.45 even in the best-labelled place on Earth is an honest number to quote when explaining "satellite vs ground" differences.

### Gaps
- No peer-reviewed yield benchmark for irrigated Mediterranean horticulture (lettuce, broccoli, melon etc.) was found; I did not search Spanish literature (IMIDA, CEBAS-CSIC) in depth.
- You et al. per-model RMSE table could not be read (AAAI PDF blocked). A secondary review quoted CNN 6.27 -> 5.77 with GP and LSTM 5.83 -> 5.55 but I could not trace its URL; do not quote it.
- Springer s11540-024-09753-w and DOAJ IJAEOG 2023 were read only via search summaries.

---

## 2. Crop-type mapping from Sentinel-2/HLS time series: RF, TempCNN, PSE-TAE, foundation models (Prithvi, Presto, Galileo); what runs on a laptop

### Takeaway
Within a region with local labels, RF/TempCNN/PSE-TAE all reach >91% OA on parcel classification; the real differences appear in per-class mIoU (RF 32.5 vs PSE-TAE 50.9). Prithvi's published crop model is US-CDL-only and gets mIoU ~0.43-0.51 on 13 classes, which does not include Murcia's vegetable crops. For a laptop demo in hours, a pixel-time-series classifier (RF/LightGBM, or Presto features) is realistic; fine-tuning Prithvi needs a GPU and labels the team does not have for Murcia.

### Cited Findings
- PSE-TAE benchmark (Sentinel-2 parcels, Garnot et al. CVPR 2020), OA / mIoU: PSE+TAE 94.2 / 50.9; CNN+GRU 93.8 / 48.1; CNN+TempCNN 93.3 / 47.5; Transformer 93.0 / 46.3; ConvLSTM 92.5 / 42.1; Random Forest on handcrafted features 91.6 / 32.5. Training time per epoch: PSE+TAE 158 s, RF 2,932 s (handcrafted preprocessing is the cost). PSE-TAE is lightweight: the dataset on disk is 28.6 GB raw vs 98.1 GB for CNN-based pipelines — [Garnot et al., arXiv 1911.07757 (PDF, table read locally)](https://arxiv.org/pdf/1911.07757)
- Prithvi-EO-1.0-100M multi-temporal crop classification fine-tune: HLS 224x224 chips, 18 channels (6 bands x 3 dates), 13 CDL-derived classes (Natural Vegetation, Forest, Corn, Soybeans, Wetlands, Developed/Barren, Open Water, Winter Wheat, Alfalfa, Fallow/Idle, Cotton, Sorghum, Other); aAcc 60.64%, mIoU 0.4269, mAcc 64.06%; best classes Open Water 0.68, Corn 0.55, Soybeans 0.53; worst Alfalfa 0.31, Cotton 0.32, Sorghum 0.33. Card says CDL labels are noisy. Apache-2.0. Inference script in NASA-IMPACT/hls-foundation-os — [HF model card](https://huggingface.co/ibm-nasa-geospatial/Prithvi-EO-1.0-100M-multi-temporal-crop-classification)
- Prithvi-EO-2.0 paper, same US crop task (3 timestamps, 5,000 samples): U-Net 42.6 mIoU, Prithvi-1.0-100M 42.7, Prithvi-2.0-300M 48.6, Prithvi-2.0-600M 50.7 (mAcc 68.8). Pretrained on 4.2 M global HLS time-series samples; 6 HLS bands at 30 m. Sizes 300M (ViT-L) and 600M (ViT-H); pretraining cost about 21,000 and 58,000 GPU-hours. On PASTIS (France) 600M gets 37.4 / 53.4 mIoU at 10% / 100% training data vs U-TAE 36.9 / 52.9 — [Prithvi-EO-2.0 arXiv 2412.02732](https://arxiv.org/html/2412.02732v3); [search summary of same paper](https://arxiv.org/pdf/2412.02732)
- Prithvi-EO-2.0-300M-TL card: Apache-2.0, 300M parameters, takes lat/lon + date-of-year embeddings (optional, drop mechanism), inputs HLS V2 reflectance in 6 bands in chronological order; load via TerraTorch `BACKBONE_REGISTRY.build(...)`; example notebooks (multitemporal crop segmentation, landslide, carbon flux) run on a Colab T4. The card names no fine-tuned crop-classification checkpoint for 2.0 — [HF Prithvi-EO-2.0-300M-TL](https://huggingface.co/ibm-nasa-geospatial/Prithvi-EO-2.0-300M-TL)
- TerraTorch: `pip install terratorch`, Apache-2.0, supports Prithvi, TerraMind, SatMAE, DOFA, Clay, timm backbones; README does not state CPU support or Python/PyTorch versions — [IBM/terratorch](https://github.com/IBM/terratorch)
- Presto (NASA Harvest) works on per-pixel time series (10 m pixel), is small (about 38.4 M MACs for a 12-step series vs 89.4 M for Galileo-Nano, 890 M for AnySat), and was fine-tuned inside WorldCereal. Macro-F1 crop type: CatBoost 0.728 random split vs Presto fine-tuned 0.809 / SSL+Presto 0.820; geographic split CatBoost 0.563 vs Presto 0.650; temporal split 0.649 vs 0.686. Binary cropland F1 geographic split 0.810 (deployed CatBoost) vs 0.829 Presto. Inputs: Sentinel-1, Sentinel-2, Copernicus DEM, AgERA5 weather, 18-month series. Cropland labels ~1.3 M points in 176 countries (USA, Spain, Belgium = 40%); crop-type ~255,000 points — [Butsko et al., WorldCereal lessons, arXiv 2508.00858](https://arxiv.org/html/2508.00858); [NASA Harvest Presto page](https://www.nasaharvest.org/news/presto-a-smarter-way-to-use-satellite-data-to-help-farmers)
- Galileo (multimodal transformer): its preprint reports Galileo-Base ranking above Presto-type pixel-time-series models; I found no independent head-to-head under domain shift — [Galileo arXiv 2502.09356](https://arxiv.org/pdf/2502.09356v3.pdf)
- Mediterranean parcels: a Valencia orchard study (RF pixel-level then plot-level) reached OA 84.18%, kappa 0.71; Sentinel-2 12-band models were 1.96% more accurate than NDVI-only models, but NDVI-only trains much faster (secondary summaries) — [RiuNet UPV](https://riunet.upv.es/handle/10251/236545); [Sensors 2023 / PMC10459796](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10459796/)

### Inferences
- PSE-TAE/TempCNN need parcel labels; Murcia has no CDL equivalent here (SIGPAC land-use polygons exist in Spain but were not researched), so the team's practical options are: unsupervised/rule-based (phenology, section 3) or a classifier trained on a handful of manually labelled parcels.
- "Pixel RF/LightGBM on smoothed NDVI+SWIR time series" runs in minutes on a laptop for a ~20 x 20 km area (174 HLS scenes), fits the 30-h budget; Prithvi inference at 224x224 chips with 300M parameters is feasible on CPU but slow, and fine-tuning is not.
- Prithvi 100M crop model should not be advertised as a Murcia crop classifier: its class list has corn/soy/cotton/sorghum/winter wheat, no lettuce, brassica, melon, citrus.

### Gaps
- No Spain/Mediterranean horticulture result for Prithvi, TempCNN or PSE-TAE was found; searches for Campo de Cartagena specifically returned nothing relevant.
- CPU inference timings for Prithvi were not found. TerraTorch Python/PyTorch compatibility not found.
- PSE-TAE dataset region/number of parcels not extracted (France Sentinel-2 dataset; check paper if quoting).

---

## 3. Phenology and bare-soil detection from NDVI time series (smoothing, number of seasons per year)

### Takeaway
Standard toolchain: smooth with Savitzky-Golay (or TIMESAT's adaptive SG / double-logistic / asymmetric Gaussian fits), count seasons as complete amplitude-passing peaks, and mark bare windows where smoothed NDVI is below a locally calibrated threshold. HLS 30 m phenology exists (Bolton et al. 2020), but double/multiple cropping is a known weak spot for all tools, and I found no published bare-soil NDVI cut-off specific to Mediterranean greenhouse/irrigated vegetables.

### Cited Findings
- TIMESAT 3.3 offers adaptive Savitzky-Golay filtering and upper-envelope weighted fits to asymmetric Gaussian and double-logistic functions, extracts season start/end/length/integrals, and has a section on determining the number of seasons — [TIMESAT 3.3 manual](https://web.nateko.lu.se/timesat/docs/TIMESAT33_SoftwareManual.pdf)
- Cropping-frequency approach in Nile Delta (Sentinel-2/Landsat-8): count growing seasons as the number of peaks corresponding to a complete growth cycle; seasonal or relative-amplitude thresholds used; up to two successive seasons detected — [Nile Delta multi-season phenology (PMC7613390)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7613390/)
- Intercomparison of TIMESAT and other tools: double cropping is an added challenge and no method identified it adequately — [Big Earth Data and ML for Sustainable and Resilient Agriculture, arXiv 2211.12584](https://arxiv.org/pdf/2211.12584)
- A smallholder study using Sentinel-2 + Savitzky-Golay mapped single/double cropping, intercropping, multiple harvest and fallow with decision tree and k-means; 10-day compositing performed better for phenology curves — [Taylor & Francis GIScience & RS 2024](https://informahealthcare.com/doi/abs/10.1080/15481603.2024.2309843)
- Bolton et al. 2020 produce 30 m phenophase transition dates from HLS (Landsat 8 + Sentinel-2) vegetation-index series; best where leaf area changes strongly with season, less interpretable in evergreen systems — [Bolton et al., RSE 240:111685](https://modarch.gsfc.nasa.gov/sci_team/pubs/abstract_new.php?id=39393)
- A generic NDVI reading guide: healthy dense canopy above ~0.5; interpret by season, plant type and region — [Univ. Valencia vegetation-index tool](https://www.uv.es/777Dxw6NiQtJw==/includes/productos/apps/indices_veg.html)
- Prithvi OOD paper: accuracy held for observation windows of 45-90 days (peak ~75 days) and fell ~0.11 for windows under 30 days, i.e. the window must match the local crop calendar — [Kolluru et al., arXiv 2610.08810](https://www.alphaxiv.org/abs/2610.08810)

### Inferences
- Concrete laptop recipe: per pixel (or per field mean), build NDVI from HLS, mask by Fmask, interpolate to 5-10 day grid, Savitzky-Golay (e.g. window ~5 samples, order 2, to be tuned), mark "bare" as NDVI below a threshold calibrated from the team's own known bare fields (NDVI ~0.15-0.25 is typical for bare soil but that figure is not sourced here), count peaks with prominence >= amplitude threshold -> seasons/year and gaps between seasons = "bare-field windows".
- Murcia caveat: plastic mulch, greenhouses and short (60-90 day) vegetable cycles produce 2-3 short peaks per year; with 174 scenes/year (~1 per 2 days overall, fewer cloud-free) the time resolution is adequate, but the validation threshold should be set with field photos/SIGPAC, not copied from cereal studies.

### Gaps
- No peer-reviewed bare-soil threshold or validation for irrigated Mediterranean vegetable systems found.
- TIMESAT's "number of seasons" section content not read (index text truncated). The TIMESAT Python wrappers/pip availability was not checked.

---

## 4. Can a "pairs" model (previous crop + season conditions -> outcome) be built from CDL rotations + NASS yields + weather?

### Takeaway
Yes in the US, and the closest published work does exactly this with causal ML: Kluger, Di Tommaso & Lobell ("Precrop Payoffs", ERL 2025) estimate the yield effect of the previous crop from crop-type maps + satellite yield proxies, conditional on weather. CDL-sequence models also predict the *next crop* (pre-season crop-type prediction). Neither is available as a ready Murcia model, and sequence/effect sizes found are modest and US-specific.

### Cited Findings
- Kluger, Di Tommaso, Lobell: combine crop type maps, satellite data and causal ML to estimate how precrop effects depend on the crop sequence and on weather; findings: most common rotations among rotators are among the most beneficial; more diverse than two-crop rotations usually gives small, sometimes negative, effects; precrop benefits larger under rainier conditions; soybean benefits larger when warmer; legume precrop benefits smaller when warmer — [arXiv 2506.02384](https://arxiv.org/abs/2506.02384)
- Effect sizes reported by NASA Earth Observatory summary: corn after soybean or soybean after spring wheat ~+8% (significant); corn after soybean alone ~+2.5%; corn after winter wheat ~+0.9%; soybean after winter wheat ~-12%. Data: Landsat and the CDL — [NASA Earth Observatory](https://science.nasa.gov/earth/earth-observatory/how-to-rotate-crops-154601) (note: the 8% vs 2.5% apparently overlapping categories come from the news article; check the paper before quoting)
- NASS: historical CDL rotations can be used by ML to predict next-year crop type; "crop sequence boundaries" introduced to cut data volume — [NASS, Preseason crop type prediction using crop sequence boundaries](https://nass.usda.gov/Education_and_Outreach/Reports,_Presentations_and_Conferences/Journal_Articles/Preseason%20crop%20type%20prediction%20using%20crop%20sequence%20boundaries.pdf)
- A neural net learns crop-sequence information from the CDL time series to correct misclassified pixels — [ISPRS Archives XLII-3/W11, 2020](https://isprs-archives.copernicus.org/articles/XLII-3-W11/161/2020/isprs-archives-XLII-3-W11-161-2020.pdf)
- The CDL-derived labels are noisy (stated on the Prithvi card), which propagates into any rotation model — [HF model card](https://huggingface.co/ibm-nasa-geospatial/Prithvi-EO-1.0-100M-multi-temporal-crop-classification)

### Inferences
- A feasible "pairs" demo: tabular table of (field-year: previous crop, two-years-ago crop, season GDD/rain/temperature from POWER, outcome = satellite yield proxy or county NASS yield) -> LightGBM with quantile objective. This is a few hours' work for California or Midwest data but the outcome label is weak (satellite proxy r2 ~0.45) and previous-crop effects are only a few % to ~10%, easily swamped by weather noise; interval widths will be bigger than the rotation signal.
- For Murcia, previous-crop effects should be presented as rule-based agronomic knowledge (e.g. avoid same family repeats) rather than a learned parameter, unless an equivalent labelled sequence dataset is found.
- CropRotViz was named in the brief; I did not find it in searches, so it is not cited.

### Gaps
- No peer-reviewed rotation-effect model for Mediterranean horticulture; no Spanish crop-sequence dataset checked (SIGPAC/ESYRCE not researched).
- CropRotViz not located. Kluger et al.'s sample sizes, uncertainty intervals and the number of countries not read (abstract page only).

---

## 5. Domain shift California -> Murcia/Spain: evidence on cross-region transfer; which features transfer

### Takeaway
Evidence is consistently negative for naive transfer: source-only crop classifiers lose roughly half their F1 across European regions, and Prithvi's crop model lost ~25 accuracy points US -> Europe, mostly due to phenology/observation-window mismatch while still reporting high confidence. Methods that align phenology (TimeMatch, climate-based adaptation), fine-tune a pretrained pixel model with local labels, and use window-matched inputs recover a large part. A California-trained model should be framed as methodology, with Murcia outputs labelled "unvalidated".

### Cited Findings
- Prithvi-EO-2.0 crop FM across 37 events in 12 countries: mean OA fell from 0.65 (US) to 0.40 (Europe); deterministic confidence stayed high while accuracy collapsed; expected calibration error rose in 7 of 8 paired events; in affected scenes 12-51% of pixels were confidently mislabeled at near-zero precision; Monte-Carlo-dropout entropy flagged the shift in all 8 paired events; merging 13 classes into 10 added 8.4 points OA with no retraining; accuracy collapses when the observation window misaligns with local phenology — [Kolluru et al., arXiv 2610.08810 (Sept 2026 preprint, not peer reviewed)](https://www.alphaxiv.org/abs/2610.08810)
- TimeMatch (four Sentinel-2 tiles in Austria, Denmark, France; >300,000 parcels): source-only macro-F1 averaged 39.2%, with temporal-shift correction 58.2%; individual tasks 28.3 -> 57.4 (DK->FR1), 24.9 -> 52.1 (FR1->DK); closest regions (FR1->FR2) transferred well (70.3 -> 73.0). Shift between regions was up to ~35 days, tracking climate (warmer regions mature earlier). Spectral differences from soil/topography noted but not addressed — [TimeMatch, arXiv 2111.02682](https://ar5iv.labs.arxiv.org/html/2111.02682)
- WorldCereal/Presto: crop-type macro-F1 fell from 0.809 (random split) to 0.650 (geographic split) and 0.686 (temporal); pretrained Presto beat CatBoost under geographic split (0.650 vs 0.563) and random-init Presto was weaker, so pretraining helps shift robustness; SSL on target-like data did not help further for cropland; some regions (Tanzania, Ethiopia) remained hard — [Butsko et al., arXiv 2508.00858](https://arxiv.org/html/2508.00858)
- Other cross-region adaptation work, found via search, not read in depth: Phenology Alignment Network (CVPRW 2021), ClimID-UDA (climate-indicator correction, >11% accuracy gain across China/Europe regions, J. Remote Sensing 2025), EuroCropsML (Estonia, Latvia, Portugal) — [PAN CVPRW 2021](https://openaccess.thecvf.com/content/CVPR2021W/AgriVision/papers/Wang_Phenology_Alignment_Network_A_Novel_Framework_for_Cross-Regional_Time_Series_CVPRW_2021_paper.pdf); [DOAJ ClimID-UDA](https://doaj.org/article/6187f2bcd2a041d5abda596f436cc09b); [EuroCropsML arXiv 2504.11022](https://export.arxiv.org/pdf/2504.11022)
- California-specific temporal shift example: an L-band SAR study in San Joaquin Valley saw cross-year accuracy drop from 89.1% to 78.0% (SAR, not optical, and a temporal not geographic shift; secondary summary) — [Remote Sensing 2023 record](https://doaj.org/article/93f5b47882b64d6f9e4c30a649a0f865)
- Yield models: the "climate-normalised" idea has support in the form of weather-conditioned precrop effects (rain-dependent) and in Khaki's feature-importance finding that solar radiation and temperature dominate, but I found no paper testing US-trained yield models on Spanish horticulture — [Kluger et al.](https://arxiv.org/abs/2506.02384); [Khaki et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC6993602/)

### Inferences
- Features likely to transfer: phenology-relative quantities (days since green-up/peak, NDVI amplitude, integrated NDVI over the season), GDD-normalised weather anomalies, and spectral-index shapes. Features likely not to transfer: calendar-date inputs, absolute temperature/rain levels, soil-class codes, class labels (CA vs Murcia crop sets differ), and anything tied to management (irrigation, plastic mulch, greenhouse) that California field crops lack.
- California Central Valley (irrigated, Mediterranean climate) is a better analogue for Murcia than the Midwest, but crop mix differs (almonds, tomatoes, lettuce, rice, cotton): lettuce/tomato/broccoli/melon overlap exists, which is a concrete reason to use CDL California classes (CDL has lettuce, broccoli etc. in California) rather than the 13-class Prithvi set (CDL class availability is from background knowledge, not verified in this research).
- Deterministic softmax confidence is not a valid transfer-safety indicator; use ensemble/MC-dropout disagreement or distance-to-training-distribution checks.

### Gaps
- No direct "California -> Spain" experiment found. Phenology Alignment Network paper returned 403 so its numbers were not read.
- Whether the Prithvi OOD preprint used CDL or other references was not stated on the page read.

---

## 6. Uncertainty quantification: quantile regression, conformal (MAPIE, CQR), ensembles, MC dropout, weather-scenario Monte Carlo, resolution mismatch, farmer communication

### Takeaway
LightGBM quantile objective + split/conformalized calibration (MAPIE's ConformalizedQuantileRegressor) is the cheapest honest interval method for tabular yield models and runs in seconds. Conformal coverage is marginal and assumes exchangeability, so under region/year shift it will under-cover; MC-dropout/ensemble disagreement is the better shift flag. Weather-scenario resampling and resolution-propagation are standard ideas but I found no crop-specific literature to cite for them.

### Cited Findings
- CQR (Romano et al. 2019): conformal methods reached the nominal 90% coverage in experiments, whereas uncalibrated quantile forests/neural nets carry no finite-sample guarantee and were sensitive to tuning; separately fitted lower/upper quantile models can cross, rare when quantiles are far apart (5%/95%) — [Romano et al., arXiv 1905.03222](https://arxiv.org/pdf/1905.03222)
- MAPIE: scikit-learn-compatible; `ConformalizedQuantileRegressor` corrects lower/upper quantile predictions by a constant and supports `lightgbm.LGBMRegressor` as the quantile estimator; `symmetric_correction` option; time-series intervals via `TimeSeriesRegressor` with EnbPI or ACI; MAPIE v1 introduced exchangeability tests; `regression_coverage_score` in `mapie.metrics`. Class names changed between v0.x and v1.x — [MAPIE docs (latest)](https://mapie.readthedocs.io/en/latest/); [CQR class docs](https://mapie.readthedocs.io/en/latest/generated/mapie.regression.ConformalizedQuantileRegressor.html); [TimeSeriesRegressor](https://mapie.readthedocs.io/en/stable/generated/mapie.regression.TimeSeriesRegressor.html); [CQR tutorial](https://mapie.readthedocs.io/en/v0.8.6/examples_regression/4-tutorials/plot_cqr_tutorial.html)
- Conformal applied to crop yield (single-study results, not independently verified): split conformal on a mixture-of-experts reached ~0.90 coverage at 90% with widths ~1.66 t/ha (plot-level) and 8.88 t/ha (country-level); HSE-GNN-CP's CQR gave 80.72% empirical coverage at 80% nominal vs 40.03% for uncalibrated bootstrap intervals; Ugandan maize out-of-fold conformal 91.7% at 90%, widths varied by agro-ecological zone — [J. Computing & Information Sciences](https://journals.iub.edu.pk/index.php/JCIS/article/view/4398); [MDPI Information 17(2):141](https://www.mdpi.com/2078-2489/17/2/141); [Discover AI (Uganda), via search](https://nru.uncst.go.ug/bitstreams/313c1654-0dc3-4ea3-984d-4393bb4bacbc/download)
- Quantile random forest for crop yield probability density forecasting reported good prediction-interval coverage (non-conformal) — [arXiv 1904.10959](https://ar5iv.arxiv.org/html/1904.10959)
- Deep ensembles vs MC dropout (general, not crop-specific): ensembles usually calibrate better under OOD, MC dropout can be overconfident, but results are not uniform; raw MC-dropout ECE ~0.10-0.13 reduced to ~0.005-0.022 by post-hoc conformal adjustment in one time-series setting — [BatchEnsemble evaluation, arXiv 2601.21581](https://arxiv.org/html/2601.21581); [Bumper-beam UQ comparison, arXiv 2607.18294](https://arxiv.org/pdf/2607.18294)
- In the Prithvi crop FM transfer study, MC-dropout entropy flagged shift in 8/8 paired events while softmax confidence did not — [Kolluru et al.](https://www.alphaxiv.org/abs/2610.08810)
- Khaki CNN-RNN and You et al. predate/ignore interval output (Khaki reports none; You's GP layer gives a predictive variance in principle) — [Khaki et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC6993602/); [You et al. AAAI 2017](https://ojs.aaai.org/index.php/AAAI/article/view/11172)
- Satellite vs ground accuracy for the "satellite vs ground differences" requirement: field-level satellite yield r2 0.45 vs county 0.69 shows aggregation reduces error but ground-truth (yield monitor) vs proxy mismatch remains — [X-MOL Deines et al. 2021](https://www.x-mol.com/paper/1328096325776089088)

### Inferences
- Recommended stack for the hackathon: LightGBM (objective="quantile", alpha=0.1 / 0.5 / 0.9) -> MAPIE ConformalizedQuantileRegressor with a calibration split taken by *year* (leave-years-out) so the calibration set mimics temporal shift; report empirical coverage per held-out year, and say plainly that coverage on Murcia is not guaranteed.
- Weather-scenario Monte Carlo: for each target field-season, sample N (e.g. 30) historical POWER weather years for the not-yet-observed rest of season, run the trained model, and report the 10/50/90th percentile of outcomes; combine with CQR width for model error (total spread ~ sqrt(weather var^2 + model var^2) is an assumption, not sourced).
- Resolution mismatch: SMAP (9 km), IMERG (10 km) values are single numbers per cell; the honest treatment is to include a "within-cell heterogeneity" term (e.g. spread of HLS NDVI within the SMAP cell) as an additional uncertainty badge rather than claiming field-level soil moisture. No source found for formal propagation; label as a design choice.
- Farmer-facing communication (inference, no sources found): show an 80% range ("most likely between X and Y") and a 3-level confidence badge driven by (a) interval width relative to median, (b) ensemble/MC-dropout disagreement, (c) whether the field's features lie inside the training range; avoid showing a single point value, and show "not validated for this region" explicitly for Murcia.

### Gaps
- No crop-specific literature found on historical-weather resampling (analog-year) for yield ensembles or on propagating SMAP/IMERG coarse-resolution error to field level.
- No source found on farmer comprehension of uncertainty displays (confidence badges, ranges); search returned nothing relevant.
- MAPIE exact v1 signature of ConformalizedQuantileRegressor (fit / conformalize / predict_interval) could not be read (stable-URL 404); check the live docs before coding.

---

## 7. Python libraries and what actually runs on a laptop in hours (summary table of sourced facts)

### Takeaway
Core stack (scikit-learn, LightGBM, MAPIE) is light; Prithvi via TerraTorch is installable by pip but inference/fine-tuning realistically wants a GPU (the official examples target a Colab T4). I could verify fewer library facts than I wanted (eo-learn, sktime, torchgeo, earthaccess were not researched here).

### Cited Findings
- TerraTorch: pip-installable, Apache-2.0, unified backbone registry including Prithvi (HF IDs like `ibm-nasa-geospatial/Prithvi-EO-2.0-300M-TL`) — [IBM/terratorch](https://github.com/IBM/terratorch); [HF Prithvi-EO-2.0-300M-TL](https://huggingface.co/ibm-nasa-geospatial/Prithvi-EO-2.0-300M-TL)
- Prithvi crop-classification demo code: NASA-IMPACT hls-foundation-os; demo Space exists — [HF card](https://huggingface.co/ibm-nasa-geospatial/Prithvi-EO-1.0-100M-multi-temporal-crop-classification)
- WorldCereal classification code is open-source on GitHub (Presto-based) — [worldcereal-classification](https://github.com/WorldCereal/worldcereal-classification)
- PSE-TAE / lightweight temporal attention reference implementation in PyTorch — [VSainteuf/lightweight-temporal-attention-pytorch](https://github.com/VSainteuf/lightweight-temporal-attention-pytorch)
- Presto compute cost is ~38.4 M MACs per 12-step pixel series, i.e. CPU-feasible; Paper states CPU-only retraining was a requirement but gives no measured latencies — [Butsko et al.](https://arxiv.org/html/2508.00858)
- TIMESAT is a standalone (MATLAB/Fortran) package with manual — [TIMESAT 3.3 manual](https://web.nateko.lu.se/timesat/docs/TIMESAT33_SoftwareManual.pdf)

### Inferences
- Realistic timeline in the 30 h: (1) earthaccess download + NDVI/phenology (3-4 h); (2) LightGBM quantile + MAPIE CQR on a US tabular dataset (3-4 h); (3) weather-scenario Monte Carlo (1-2 h); (4) optional Prithvi inference on a few Murcia chips on a GPU/Colab as a "foundation-model sanity check" with the OOD caveat.
- Pure-Python phenology: `scipy.signal.savgol_filter` and `scipy.signal.find_peaks` replace TIMESAT for this scope (standard SciPy functions; not sourced here).

### Gaps
- eo-learn, sktime, torchgeo, earthaccess not researched. Prithvi CPU speed unknown.
- ECOSTRESS/SMAP/IMERG-specific ML uses not researched (out of tool budget).

---

## Source-quality notes
- Primary and read: Khaki CNN-RNN (PMC), PSE-TAE (PDF table extracted locally), Presto/WorldCereal paper, TimeMatch, Prithvi-EO-2.0 paper, HF model cards, Kluger abstract, Prithvi OOD preprint abstract (arXiv 2610.08810, Sept 2026, unreviewed).
- Search-summary only (not opened): IJAEOG 2023 XGBoost soybean, Springer s11540-024-09753-w, conformal-yield papers, Deines 2021 numbers, ClimID-UDA, EuroCropsML, Valencia RF OA.
- Blocked/failed: AAAI You et al. PDF (access denied), Stanford mirror (certificate error), PAN CVPRW (403), MAPIE CQR stable page (404).
- Conflict to flag: Khaki's RF baseline is much worse than CNN-RNN, whereas 2023-24 county studies find RF/XGBoost best; different data volumes explain it, not a contradiction of quality.
