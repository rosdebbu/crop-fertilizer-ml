# Feature-by-Feature Guide: what is used, and viva questions

Tabs in the web app (`static/index.html`, logic in `static/app.js`, API in `app.py`).

| Tab | What it does | Algorithm / technique | Real or sample data |
|---|---|---|---|
| Crop Predictor | Recommends 1 of 22 crops from N, P, K, temperature, humidity, pH, rainfall | Random Forest (100 trees), Decision Tree, KNN (k=5); StandardScaler; `predict_proba` | Real (Kaggle crop data) |
| Fertilizer Advisor | Recommends 1 of 7 fertilizers from soil type, N, P, K, moisture, temperature, humidity (7 inputs; the crop shown is the Crop Predictor's result and is not a model input) | Same 3 models; LabelEncoder for soil and crop | Real Kaggle data, but labels have no signal (about 14%, chance), so the app shows a warning |
| Satellite & Climate | Map of a chosen region with NDVI / NDWI / EVI, weather, monsoon, mandi prices, sowing calendar | Leaflet map, Esri World Imagery tiles, band overlay colours, lookup of a location profile; "apply to predictor" feeds the region's N, P, K, weather into the Crop Predictor | Map imagery is real; NDVI, NDWI, EVI, weather, prices and feed are hard-coded sample values |
| Model Performance & Metrics | Accuracy, precision, recall, F1 per model, charts gallery | Hold-out 80/20 split, 5-fold cross-validation (crop), weighted metrics, confusion matrices, feature importance | Live from `/api/status`, charts from the offline scripts |
| Soil Health & Farm Report | Soil-health-card style report, profit estimate, fertilizer dosage, crop rotation, climate-stress | Threshold rules on N, P, K, pH, moisture; arithmetic (yield × MSP − cost); lookup tables; climate-stress = perturb inputs and re-predict with Random Forest | Rules and tables are fixed sample data |
| Dataset Explorer | Browse and search the CSV rows, summary stats | pandas `sample()`, `mean/min/max`, client-side filter | Real |
| Print / Export Report | Prints the current report | Browser `window.print()` | n/a |

## Formulas used in the farmer tools
- Profit: `yield/acre × acres = total yield`; `revenue = total yield × MSP`; `net profit = revenue − cost/acre × acres`; `ROI % = net profit / cost × 100`.
- Fertilizer dosage: `bags = bags per acre × acres`; `cost = bags × price per bag`; "savings" compares with an assumed 1.8× conventional over-use.
- Climate stress: drought (rainfall ×0.70, +1.5 °C, humidity ×0.75), heatwave (+3.5 °C, humidity ×0.85), cloudburst (rainfall ×1.5, −1.5 °C, humidity ×1.15), then Random Forest predicts the crop again.

---
## Viva questions by feature

### A. Crop Predictor
**Q. What happens when I click Predict?** The browser sends 7 numbers to `POST /api/predict/crop`. Pydantic validates ranges, the saved StandardScaler transforms them, the chosen model predicts, and the API returns the crop, probabilities, all three models' answers and a rule-based explanation.

**Q. Where does "confidence" come from?** `predict_proba` of the predicted class. Random Forest: share of trees voting for it. Decision Tree: leaf purity (often 100%, overconfident). KNN: share of the 5 neighbours. Not calibrated probabilities.

**Q. Why show three models?** To compare and to show consensus; if all three agree, the answer is more trustworthy.

**Q. What is the "scientific rationale" text?** Simple if-rules on the inputs (e.g. rainfall above 150 mm, N above 70, pH below 6), not model internals. It is an explanation aid, not the model's real reasoning.

**Q. Why does Random Forest win?** Ensemble averaging reduces variance; handles non-linear interactions; 99.55% test and 99.5% CV.

### B. Fertilizer Advisor
**Q. How is soil type handled, and what about the crop?** LabelEncoder turns soil type into integers; an unknown soil returns HTTP 400. Crop type was removed from the model: the fertilizer dataset has its own 11-crop list that does not match the 22-crop recommender and carries no signal. The tab instead shows the crop recommended by the Crop Predictor, used only for advice and dosage text.

**Q. Why is accuracy only about 14%?** The Kaggle labels are statistically independent of the features (equal mean N, P, K per fertilizer, mutual information about 0.01, CV 14.2%), so accuracy equals chance, 1/7. The app displays a reliability warning instead of pretending.

**Q. What would a correct fertilizer recommender do?** Compare soil-test nutrient levels with the crop's requirement, compute the deficit, and choose the fertilizer whose N-P-K ratio covers it (rule-based or trained on labelled agronomic data). Our synthetic rule-based experiment reached 94.8%, showing the pipeline works when labels carry signal.

**Q. What are the "diagnostics" shown?** Threshold rules, for example N, P or K below 15, or moisture below 30%.

### C. Satellite & Climate
**Q. Is the satellite data live?** The map imagery tiles are real (Esri World Imagery via Leaflet). NDVI, NDWI, EVI, weather, mandi prices and the social feed are hard-coded sample profiles for 6 regions; the band buttons change the overlay colour only. A production version would call Sentinel-2 / Google Earth Engine and a weather API.

**Q. What is NDVI?** (NIR − Red) / (NIR + Red). Values from −1 to 1; above about 0.6 means dense healthy vegetation.

**Q. What is NDWI?** (Green − NIR) / (Green + NIR) for water content; EVI is an NDVI variant that corrects for atmosphere and soil background.

**Q. What does "apply to predictor" do?** Copies the selected region's N, P, K, temperature, humidity, pH and rainfall into the Crop Predictor sliders and runs the model.

**Q. What is Leaflet?** An open-source JavaScript mapping library; it draws tile layers, markers and circles.

### D. Model Performance & Metrics
**Q. How were the metrics computed?** 80/20 stratified split (seed 42), scaler fit on train only, weighted precision/recall/F1, plus 5-fold CV for crop. The table reads `/api/status` live, so the UI cannot drift from the real numbers.

**Q. What do the charts show?** Class distribution, correlation heatmap, boxplots, confusion matrices, model accuracy comparison and feature importance, generated offline by `crop_recommendation.py` and `fertilizer_prediction.py`.

**Q. What is feature importance?** Mean decrease in Gini impurity from splits on a feature, averaged over trees; for crop: rainfall, humidity and potassium rank highest.

**Q. What is the chance-level baseline?** 1/classes: 4.5% for crop, 14.3% for fertilizer.

### E. Soil Health & Farm Report
**Q. How is the soil health card produced?** Rules compare N, P, K, pH and moisture with agronomic bands (low / medium / high); no ML model.

**Q. How is profit calculated and how reliable is it?** Revenue minus cost using fixed average yield, MSP and cost per acre. Indicative only; real values vary by region, season and market.

**Q. What is MSP?** Minimum Support Price set by the Government of India for crops.

**Q. What does climate-stress show and is it a forecast?** It is a sensitivity analysis: it perturbs weather inputs and shows whether the recommended crop changes. It is not a weather forecast.

**Q. What is crop rotation and why include it?** Growing different crops in sequence (for example rice, then a pulse that fixes nitrogen, then green manure) to restore soil nitrogen and break pest cycles. The API returns a rule-based plan by crop family.

### F. Dataset Explorer
**Q. How does it work?** `/api/data/crop/sample` and `/fertilizer/sample` return a random sample (seed 42) and per-column mean, min, max; the search box filters rows in the browser.

**Q. Why is exploring data important?** To check balance, ranges, missing values and outliers before modelling.

### G. Architecture and engineering
**Q. How do front end and back end communicate?** `fetch()` calls JSON REST endpoints on the same FastAPI server; CORS is enabled for development.

**Q. Why train at start-up and cache?** Models are small; training takes about 24 s on the 100k-row file, so a joblib cache cuts later starts to about 6 s and rebuilds if a CSV changes.

**Q. How is correctness tested?** 6 pytest tests with FastAPI's TestClient (valid prediction, validation errors, data-quality honesty, pipeline learns on signal).

**Q. What are the main limitations?** Fertilizer labels have no signal; satellite, price and weather values are sample data; no hyper-parameter tuning; economics use fixed averages.

**Q. What is your future scope?** Live Sentinel-2 / weather / mandi APIs, real labelled fertilizer data, soil sensors (IoT), tuned and calibrated models, regional language support.
