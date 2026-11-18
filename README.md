# Crop Recommendation & Fertilizer Prediction (ML + FastAPI)

An end-to-end machine learning and precision-agriculture web application that recommends the optimal **crop** (22 classes) and **fertilizer** (7 classes) from soil nutrients (`N`, `P`, `K`, `pH`), weather (`temperature`, `humidity`, `rainfall`), soil type, and moisture using **Random Forest**, **Decision Tree**, and **K-Nearest Neighbors (KNN)**, served through a **FastAPI** backend and interactive web UI.

> **Datasets (Kaggle):**
> - [Crop Recommendation Dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) (2,200 rows, 22 crops)
> - [Fertilizer Prediction Dataset](https://www.kaggle.com/datasets/irakozekelly/fertilizer-prediction) (100,000 rows, 7 fertilizers)

---

## Features

- **Dual ML Prediction Pipelines:** Trains and compares Random Forest, Decision Tree, and KNN models for both crop recommendation and fertilizer prediction, with model caching (`.model_cache.joblib`).
- **Data Quality Audit & Honesty Guardrails:** Automatically computes chance-level baselines and flags unreliable datasets via `/api/status` (`data_quality`) and `model_reliability_warning` on fertilizer predictions.
- **Farmer Decision-Support Tools:**
  - **Crop Rotation Advisor** (`/api/farmer/crop-rotation`)
  - **Profitability Estimator** (`/api/farmer/profitability`)
  - **Fertilizer Dosage Calculator** (`/api/farmer/fertilizer-dosage`)
  - **Climate Stress Analysis** (`/api/farmer/climate-stress`)
  - **Geo Analysis** (`/api/geo/analyze`)
- **Interactive Web UI:** Served at `/` and `/studio` (`static/index.html`, `static/app.js`).
- **Research & Academic Deliverables:** Includes a complete IEEE-style research paper (`paper/`), full project report (`report/`), presentation decks (`Crop_Fertilizer_ML_Final.pptx`), EDA & ML tutorial notebooks (`notebooks/`), and Viva Q&A guides.

---

## Model Results

| Task | Random Forest | Decision Tree | KNN | Chance Baseline |
|---|---:|---:|---:|---:|
| **Crop Recommendation** (2,200 rows, 22 classes) | **99.55%** (CV 99.5%) | 97.95% (CV 98.68%) | 97.95% (CV 97.14%) | 4.55% |
| **Fertilizer, real Kaggle data** (100,000 rows, 7 classes) | 14.54% | 14.69% | 14.21% | 14.29% |
| **Fertilizer, rule-based synthetic** (5,000 rows, 7 classes) | **94.80%** (CV 95.84%) | 90.40% (CV 90.24%) | 80.20% (CV 80.08%) | 14.29% |

> **Why is the real fertilizer dataset at chance level?**
> In the Kaggle fertilizer file, labels are statistically independent of the input features (mean N, P, and K are nearly identical across all 7 fertilizer classes), so no classifier can outperform random guessing (~14.29%). The app surfaces this transparently through `/api/status` → `data_quality` and a `model_reliability_warning` on every fertilizer prediction. The optional rule-based synthetic dataset (`scripts/make_fertilizer_dataset.py`) demonstrates that the pipeline learns effectively (94.80% accuracy) when labels carry real signal.

---

## Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Web App & API Server
```bash
python app.py
```
Starts the FastAPI server at `http://localhost:8000` (or the next available port if `8000` is busy).

### 3. Run API Tests
```bash
python -m pytest -q test_api.py
```

### 4. (Optional) Use the Synthetic Fertilizer Dataset
```bash
python scripts/make_fertilizer_dataset.py
# PowerShell:
$env:FERTILIZER_CSV="data/synthetic/Fertilizer_rule_based.csv"
python app.py
```

### 5. Run Offline EDA & Evaluation Scripts
```bash
python crop_recommendation.py
python fertilizer_prediction.py
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/status` | Model readiness, dataset stats, and `data_quality` audit |
| `GET` | `/api/metrics` | Accuracy, precision, recall, F1, and CV scores for all models |
| `POST` | `/api/predict/crop` | Predict best crop with class probabilities |
| `POST` | `/api/predict/fertilizer` | Predict fertilizer with reliability warning if applicable |
| `GET` | `/api/data/crop/sample` | Sample rows from the crop dataset |
| `GET` | `/api/data/fertilizer/sample` | Sample rows from the fertilizer dataset |
| `GET` | `/api/geo/analyze` | Regional soil/climate suitability analysis |
| `POST` | `/api/farmer/profitability` | Estimated crop profitability breakdown |
| `POST` | `/api/farmer/fertilizer-dosage` | Recommended NPK / fertilizer dosage |
| `POST` | `/api/farmer/climate-stress` | Climate stress risk evaluation |
| `GET` | `/api/farmer/crop-rotation` | Crop rotation recommendations |

---

## Project Structure

| Path | Purpose |
|---|---|
| `app.py` | FastAPI backend, model training/caching, prediction & farmer-advisory endpoints |
| `static/` | Web UI (`index.html`, `app.js`) |
| `data/` | Kaggle CSV datasets; `data/synthetic/` holds the optional rule-based fertilizer dataset |
| `crop_recommendation.py`, `fertilizer_prediction.py` | Offline EDA, training, and evaluation scripts generating `output_charts*/` |
| `output_charts/`, `output_charts_fertilizer/` | Confusion matrices, correlation heatmaps, feature importance, and distribution plots |
| `outputs/` | Run logs and `results.json` (verified metrics and sample API outputs) |
| `scripts/` | Synthetic data generator, report/paper/deck builders, and experiment runners |
| `paper/` | Research paper (`Research_Paper.pdf`, `Research_Paper.docx`) and figures |
| `report/` | Full project report (`Project_Report.pdf`, `Project_Report.docx`) and figures |
| `notebooks/` | Project demo EDA notebook and ML tutorial notebooks (`Tutorial_10`–`Tutorial_15`) |
| `Crop_Fertilizer_ML_Final.pptx` | Final presentation deck (plus earlier `Review_2_*` decks & PDFs) |
| `VIVA_PROJECT_QA.md`, `VIVA_FEATURES_QA.md`, `VIVA_QA_COMPLETE.md` | Viva preparation Q&A documentation |
| `test_api.py` | Automated API test suite (`pytest`) |
