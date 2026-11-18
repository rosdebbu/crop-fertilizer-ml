# Viva Guide — Crop Recommendation & Fertilizer Prediction

## 1. What the project is (30-second answer)
A web app that takes soil + weather values and predicts (a) the best **crop** and (b) the best **fertilizer**. Three scikit-learn classifiers (Random Forest, Decision Tree, KNN) are trained at server start-up on two CSVs, exposed through a **FastAPI** REST backend, and used by a single-page HTML/JS UI in `static/`.

## 2. What is exactly used
| Layer | Tech | Where |
|---|---|---|
| Data | `data/Crop_recommendation.csv` (2,200 rows, 22 crops, 100 each — balanced), `data/Fertilizer_Prediction.csv` (100,000 rows, 7 fertilizers); both are the real Kaggle files | `data/` |
| ML | scikit-learn: `StandardScaler`, `LabelEncoder`, `RandomForestClassifier`, `DecisionTreeClassifier`, `KNeighborsClassifier`, `train_test_split`, `cross_val_score` | `app.py` → `fit_and_score()` |
| Backend | FastAPI + Pydantic (input validation) + Uvicorn (server) | `app.py` |
| Frontend | Plain HTML/JS/Tailwind-style UI served by FastAPI | `static/index.html`, `static/app.js` |
| Unused | `frontend/` (Next.js) has no `page.tsx`, so it is an unfinished alternative UI | — |
| Offline analysis | `crop_recommendation.py`, `fertilizer_prediction.py` produce the charts in `output_charts*/` (EDA, confusion matrices, feature importance) | root |
| Tutorials | `Tutorial_1…6` notebooks (preprocessing, regression, CV, metrics, …) | root |

## 3. How it works (pipeline)
1. **Load** CSV with pandas. No missing values, no duplicates (checked).
2. **Encode** (fertilizer only): `Soil Type` → integer (Crop Type is not used as a model feature) with `LabelEncoder`.
3. **Split**: 80/20, `stratify=y` (keeps class balance), `random_state=42` (reproducible).
4. **Scale**: `StandardScaler` fitted on *train only*, then applied to test (avoids data leakage). Needed for KNN (distance based); trees don't need it.
5. **Train** 3 models, **evaluate** with accuracy / precision / recall / F1 (weighted averages for multi-class) and, for crop, 5-fold cross-validation.
6. **Serve**: `POST /api/predict/crop` and `/api/predict/fertilizer` scale the request with the *same* fitted scaler, return the predicted class, per-class probabilities (`predict_proba`), and all three models' answers side by side.
7. **Extras**: `/api/farmer/*` (profit, fertilizer dosage, climate-stress what-if, rotation) and `/api/geo/analyze`.

## 4. Results to quote
- **Crop**: Random Forest ≈ **99.5 %** (CV 99.5 %), Decision Tree / KNN ≈ **98 %**. Chance = 4.5 % (22 classes). The data is clean, well separated → very high accuracy is plausible.
- **Fertilizer (real Kaggle data)**: all models ≈ **14.3 %** = chance for 7 classes. See §6.
- **Fertilizer (rule-based synthetic experiment)**: RF ≈ **94.8 %**, proving the pipeline learns when labels have signal.

## 5. Likely questions and answers
**Why Random Forest?** An ensemble of decision trees on bootstrap samples with random feature subsets; averaging reduces the variance of a single tree, handles non-linear feature interactions, needs no scaling, gives feature importance. It was best on crop.

**Why compare 3 models?** To show the trade-off: Decision Tree = interpretable but overfits; KNN = simple, no training, sensitive to scale and slow on 100k rows; RF = most accurate, less interpretable.

**Why StandardScaler, and why fit only on train?** KNN uses Euclidean distance, so rainfall (0–300) would dominate pH (3–10). Fitting on the full data would leak test statistics into training.

**Why stratify and random_state?** Stratify keeps every class's proportion in both splits; random_state makes results repeatable.

**Why weighted precision/recall/F1?** Multi-class; weighted averages by class support. (Crop is balanced so weighted ≈ macro.)

**Is 99 % accuracy overfitting?** Checked with 5-fold CV (99.5 %), which matches the hold-out score, so no. The dataset is simply easy and synthetic-like. Caveat: a real field has noisier data.

**How are probabilities / confidence produced?** `predict_proba`: for RF the fraction of trees voting for each class; for a Decision Tree it is the leaf class fraction (often 100 %, so overconfident); for KNN it is neighbour votes out of 5.

**What does the `/climate-stress` endpoint do?** Perturbs temperature/humidity/rainfall (drought, heatwave, flood), re-runs the RF and shows how the recommendation changes — a sensitivity analysis, not a forecast.

**How is bad input handled?** Pydantic `Field(ge=, le=)` returns HTTP 422 for out-of-range numbers; unknown soil/crop names return HTTP 400.

**How would you deploy / scale it?** Currently models are trained at import (≈30 s because of the 100k-row set). Better: train offline, save with `joblib`, load at start-up; run Uvicorn behind a reverse proxy/Docker.

## 6. Honest limitations (say these before the examiner finds them)
1. **The fertilizer model does not learn.** Accuracy ≈ chance on both the original 200-row file and the 100k-row file (mutual information between features and label ≈ 0.01). The labels are effectively random with respect to the features, so the fertilizer recommendation is **not reliable**. Proof: identical mean N/P/K for every label, CV accuracy 14.2 %. A synthetic rule-based set (`scripts/make_fertilizer_dataset.py`) reaches 94.8 %, so the code is fine and the data is the limit. A real fix needs a dataset where the fertilizer follows soil tests. The API now returns `model_reliability_warning` and `/api/status → data_quality` states this.
2. **Mandi prices, NDVI, weather, social feed are hard-coded sample data**, not live APIs. `/api/geo/analyze` now says so in `data_source`. Present them as a *prototype of the decision-support layer*.
3. **Profit / dosage numbers** use fixed average yields and MSP values — indicative only.
4. **Single hold-out split** for fertilizer; **no hyper-parameter tuning** (e.g. `GridSearchCV` on `n_estimators`, `max_depth`, `k`).
5. Feature importance and EDA charts are static images made offline, not regenerated by the app.
6. Dataset is a public Kaggle-style crop dataset: it does not model soil texture, season or region, so real-world generalisation is unproven.

## 7. What was improved in this pass
- `requirements.txt` was missing `fastapi`, `uvicorn`, `pydantic` — a fresh install could not run the app. Added (plus `httpx`, `pytest` for tests).
- Removed ~60 lines of duplicated training code (one `fit_and_score()` helper for both datasets); added 5-fold CV for crop.
- Real Kaggle data kept as the official data (synthetic set is an optional experiment). Added chance-level baseline + reliability warning so the fertilizer problem is visible, not hidden.
- CORS: `allow_origins="*"` combined with `allow_credentials=True` is invalid/unsafe → credentials disabled.
- Added `test_api.py` (4 tests: valid prediction, validation error, bad category, data-quality report). Run with `python -m pytest -q test_api.py`.

## 8. Run it
```bash
pip install -r requirements.txt
python app.py        # open the URL printed (default http://localhost:8000)
```
