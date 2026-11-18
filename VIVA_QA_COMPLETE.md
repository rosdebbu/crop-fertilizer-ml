# Complete Viva Question Bank — Crop Recommendation & Fertilizer Prediction

Numbers below match this repo (`outputs/results.json`). Where a common textbook answer would be wrong for **this** project, it is marked ⚠.

---
## Category 1: Overview and motivation

**Q1. What is the objective of your project?**
"To support precision agriculture by recommending the most suitable crop and fertilizer from soil nutrients (N, P, K), pH, moisture and climate (temperature, humidity, rainfall). We train supervised classifiers and serve them through a web app so a farmer can cut input cost and avoid a poor crop choice."

**Q2. Give a high-level overview of the tech stack and architecture.**
- ML: pandas, numpy, scikit-learn. Models: Random Forest, Decision Tree, KNN.
- Backend: FastAPI + Pydantic (validation) + Uvicorn (ASGI server). Models train at start-up and are kept in memory.
- Frontend: single-page HTML/JS in `static/`, served by FastAPI.
- Extras: multi-model comparison, climate-stress simulation, profit and dosage calculators, crop rotation, location profiles.
- ⚠ An MLP/ANN exists only in the tutorial notebook (Tutorial 15, `hidden_layer_sizes=(64, 32)`), not in the web app. Do not say the app uses a neural network.

**Q3. Why is this problem important?**
Wrong crop choice and over-fertilizing waste money, degrade soil (acidification, salinity) and pollute water. Data-driven recommendations are cheap and scalable compared with soil-lab visits for every field.

**Q4. Who are the users and what are the inputs and outputs?**
Farmers or extension officers. Input: 7 values for crop (N, P, K, temperature, humidity, pH, rainfall); 7 for fertilizer (temperature, humidity, moisture, soil type, N, P, K). Output: predicted class, per-class probabilities, all three models' answers, and an explanation.

**Q5. Is this a classification or regression problem? Why?**
Classification: the target is a category (22 crops, 7 fertilizers), not a number.

---
## Category 2: Datasets and preprocessing

**Q6. Describe the datasets.**
- Crop: Kaggle "Crop Recommendation Dataset" (atharvaingle). 2,200 rows, 22 classes × 100 (perfectly balanced), 7 numeric features.
- Fertilizer: Kaggle "Fertilizer Prediction" (irakozekelly). 100,000 rows, 7 classes (roughly balanced, 14-15% each), features: temperature, humidity, moisture, soil type, N, P, K (crop type is not used as a feature).
- No missing values and no duplicate rows in either file.

**Q7. How did you check data quality?**
`isna().sum()` and `duplicated().sum()` (both 0), `describe()` for ranges, class counts for balance, correlation heatmap, boxplots for outliers, and mutual information between features and label.

**Q8. Why StandardScaler, and which models does it matter for?**
z = (x − μ) / σ. It matters for KNN (Euclidean distance: rainfall 20-300 would swamp pH 3.5-9) and for ANNs/logistic regression (gradient-based). It has no effect on Decision Tree and Random Forest because splits are threshold comparisons that don't change under monotonic scaling. We scale once so all three models share one pipeline.

**Q9. Why fit the scaler only on the training set?**
To prevent data leakage: fitting on all data lets test-set mean and variance influence training, giving over-optimistic scores. Rule: `fit_transform` on train, `transform` on test and on every API request.

**Q10. How did you encode categorical variables?**
`LabelEncoder` on Soil Type → integers (Crop Type was dropped from the fertilizer model so it matches the 22-crop recommender). Caveat: label encoding implies an order that doesn't exist; harmless for tree models, slightly distorting for KNN. One-hot encoding would be cleaner for KNN.

**Q11. Why `stratify=y` and `random_state=42`?**
Stratify keeps class proportions identical in train and test (important with 22 classes). A fixed seed makes results reproducible.

**Q12. Why an 80/20 split?**
Common compromise: enough data to train, enough (440 crop rows) to test. Cross-validation backs it up so the result doesn't depend on one split.

**Q13. Did you handle outliers?**
Boxplots showed a few extreme rainfall/pH values, but they are real agronomic values (e.g. rice in high rain), and tree models are robust to outliers, so we kept them. Pydantic limits (`ge/le`) reject impossible API input.

**Q14. Why is the crop dataset easy to classify?**
Each crop was sampled around a distinct N-P-K/climate profile, so classes form well-separated clusters (rice: high rain and humidity; chickpea/kidney beans: specific P-K and low rain).

---
## Category 3: Algorithms and model selection

**Q15. How does Random Forest work and why is it best here?**
Bagging: 100 trees, each trained on a bootstrap sample with a random subset of features at each split; prediction is the majority vote. Averaging cuts the variance of a single tree, handles non-linear interactions, needs no scaling, gives feature importance. Result: 99.55% on crop.

**Q16. Decision Tree vs Random Forest?**
| | Decision Tree | Random Forest |
|---|---|---|
| Model | one tree | ensemble of 100 trees |
| Variance | high, overfits | low, averaged |
| Interpretability | easy to read | harder |
| Crop accuracy | 97.95% | 99.55% |

**Q17. How does KNN work and what is its limitation?**
Lazy learner: stores training data and labels a new point by the majority of its k=5 nearest neighbours (Euclidean). No training cost but prediction is O(N·d) per query, so it is slow on large data (100k rows) and sensitive to scaling and irrelevant features.

**Q18. How did you choose k=5, 100 trees?**
They are sensible defaults and were not tuned. Honest answer: next step is `GridSearchCV` over k, `n_estimators`, `max_depth`.

**Q19. What is Out-of-Bag (OOB) score?**
Each bootstrap sample leaves out about 36.8% of rows (1 − 1/e). Predicting those rows with the trees that never saw them gives a free validation estimate (`oob_score=True`). We used 5-fold CV instead.

**Q20. What is bagging vs boosting?**
Bagging trains models in parallel on resamples and averages (Random Forest, reduces variance). Boosting trains sequentially, each model fixing the previous errors (XGBoost, AdaBoost, reduces bias).

**Q21. Why not Logistic Regression, SVM or XGBoost?**
Not needed: RF already reaches ~99.5%. They could be added for comparison; XGBoost is the natural next candidate.

**Q22. Entropy vs Gini?**
Both measure node impurity. Gini = 1 − Σp²; entropy = −Σp log p. sklearn's default is Gini (cheaper); results are usually very similar.

**Q23. What does `max_depth` do and why do trees overfit?**
Depth limits tree complexity. An unlimited tree memorises training points (zero training error, high variance). Limiting depth or min samples per leaf, or using a forest, fixes it.

**Q24. What is the curse of dimensionality and does it affect you?**
In high dimensions distances become similar, hurting KNN. We have only 7-8 features, so it is not a problem here.

**Q25. How are probabilities / confidence produced?**
`predict_proba`: Random Forest = average of tree votes; Decision Tree = class fraction in the leaf (often 100%, so overconfident); KNN = fraction of the 5 neighbours (steps of 20%). These are not calibrated probabilities.

---
## Category 4: Evaluation and validation

**Q26. Is 99.5% accuracy overfitting? How do you know?**
"We ran 5-fold stratified cross-validation: 99.5% for Random Forest, matching the 99.55% hold-out score. A big gap would signal overfitting. The dataset is clean and separable; real farm data with sensor noise would score lower."

**Q27. Why weighted precision, recall and F1?**
Multi-class. Weighted averages per-class scores by support. Crop is balanced, so weighted ≈ macro.

**Q28. Define precision, recall, F1.**
Precision = TP/(TP+FP); recall = TP/(TP+FN); F1 = 2PR/(P+R), the harmonic mean.

**Q29. What is a confusion matrix?**
Rows = actual, columns = predicted. The diagonal is correct predictions; off-diagonal cells show which classes get mixed up (e.g. rice vs jute, maize vs others with similar climate).

**Q30. Why isn't accuracy enough?**
It hides class imbalance and the cost of different mistakes. Here classes are balanced, so accuracy is meaningful, but we still report P/R/F1.

**Q31. What is cross-validation and why use it?**
Split data into k folds, train on k−1, test on the held-out fold, rotate, average. It uses all data and shows score variance, so one lucky split can't fool you. sklearn uses stratified folds for classifiers.

**Q32. What is the baseline/chance accuracy?**
1/number of classes: 4.5% for 22 crops, 14.3% for 7 fertilizers. A model must clearly beat this. The app computes it in `data_quality`.

**Q33. Feature importance: what did you find?**
For crop, rainfall, humidity and potassium rank highest, then phosphorus, N, temperature, pH. Importance in RF = average impurity decrease from splits on that feature.

---
## Category 5: Unsupervised learning (tutorial notebooks T10-T12)

**Q34. Why cluster if you have labels?**
To discover natural agro-climatic groups, which helps crop rotation and intercropping, and to sanity-check that the labels match the data structure.

**Q35. How did you choose k in K-Means?**
Elbow method (inertia/WCSS vs k for k = 2..8) and silhouette score; the notebook uses k=4. Silhouette near +1 means dense, well-separated clusters.

**Q36. Ward vs single linkage?**
Single = minimum pair distance, causes "chaining". Ward = merges the pair that least increases within-cluster variance, giving compact, balanced clusters (used in the notebook: `linkage='ward'`).

**Q37. What is a dendrogram?**
A tree showing the order and distance at which clusters merge; cutting at a height gives a chosen number of clusters.

**Q38. K-Means weaknesses?**
Needs k in advance, assumes spherical clusters, sensitive to initial centroids (use k-means++) and to scaling.

**Q39. Supervised vs unsupervised?**
Supervised learns from labelled examples (our classifiers); unsupervised finds structure without labels (clustering).

---
## Category 6: Web architecture and system design

**Q40. Why FastAPI over Flask or Django?**
ASGI/async performance, Pydantic validation returning clear 422 errors, automatic Swagger docs at `/docs`, type hints.

**Q41. What are the main endpoints?**
`GET /api/status`, `POST /api/predict/crop`, `POST /api/predict/fertilizer`, `GET /api/metrics`, `GET /api/data/*/sample`, `POST /api/farmer/profitability`, `/fertilizer-dosage`, `/climate-stress`, `GET /api/farmer/crop-rotation`, `GET /api/geo/analyze`.

**Q42. How is input validated?**
Pydantic `Field(ge=, le=)` (e.g. pH 0-14, humidity 0-100) → HTTP 422 on violation. Unknown soil or crop name → HTTP 400 with the list of valid values.

**Q43. What does the climate-stress feature do?**
It perturbs the input and re-predicts with Random Forest: drought (rainfall ×0.70, +1.5°C, humidity ×0.75), heatwave (+3.5°C, humidity ×0.85), cloudburst (rainfall ×1.5, −1.5°C, humidity ×1.15). It shows how the recommended crop changes. It is a sensitivity analysis, not a weather forecast. ⚠ Use these exact numbers, not "+4°C / −40%".

**Q44. How would you deploy it?**
Train offline, save with `joblib`, load at start-up (now it trains at import, which is slow); run Uvicorn in Docker behind Nginx; add logging and tests in CI.

**Q45. What is CORS and what did you change?**
Browsers block cross-origin calls unless the server allows them. We allow all origins for development but disabled `allow_credentials`, because a wildcard origin with credentials is invalid and unsafe.

**Q46. How is the model kept consistent between training and prediction?**
The same fitted `StandardScaler` and `LabelEncoder` objects live in memory (`crop_store`, `fert_store`) and are applied to each request.

**Q47. What testing did you do?**
`test_api.py`, 6 pytest tests: valid prediction, out-of-range input (422), bad category (400), data-quality report, honest quality flag, and a check that the pipeline learns when labels carry signal.

---
## Category 7: Trap questions and limitations

**Q48. (Big trap) What were the fertilizer results?**
"About 14.2-14.5% for all three models, which equals random guessing for 7 classes (14.3%). We investigated: mean N, P, K are the same for every fertilizer, mutual information is about 0.01, and cross-validated accuracy is 14.2%. So the public labels are statistically independent of the features. We did not hide it: the API returns `model_reliability_warning` and `/api/status` shows `data_quality`. To prove the code is correct we ran the same pipeline on a rule-based synthetic set and got 94.8%."

**Q49. Why not just fix the dataset?**
Changing real data to get good numbers would be dishonest. We kept the real data and documented the limit; the synthetic set is clearly labelled as an experiment.

**Q50. How should fertilizer be recommended properly?**
With agronomic rules: required nutrient (crop target) minus soil test level gives the deficit; choose the fertilizer whose N-P-K ratio covers it; confirm with a soil-health card or lab test.

**Q51. Are the mandi prices and weather real?**
No. `LOCATION_PROFILES`, mandi prices, NDVI and the social feed are hard-coded sample data, and `/api/geo/analyze` states this in `data_source`.

**Q52. Are profit and dosage figures reliable?**
They are indicative: fixed average yield, MSP and cost per acre. Real figures vary by region and season.

**Q53. Why is 99.5% unrealistic in the field?**
The dataset is clean and synthetic-like; real data has sensor noise, soil variability, seasons, pests and market effects that the 7 features ignore.

**Q54. Limitations and future scope?**
IoT soil probes and weather APIs; real fertilizer data; hyper-parameter tuning; saved models (joblib/ONNX); regional data and live mandi prices; multilingual UI; explainability (SHAP).

**Q55. What would you do differently?**
Collect real labelled fertilizer data, tune models, add a held-out test never touched during tuning, and add model monitoring.

**Q56. Did you tune hyper-parameters?**
No (defaults: 100 trees, k=5). The plan is `GridSearchCV` with cross-validation.

**Q57. How would you handle a class not seen in training?**
The model can only predict known classes; we reject unknown categorical values (HTTP 400) and would need new data and retraining to add a class.

---
## Category 8: Quick one-liners

| Term | One-line answer |
|---|---|
| Overfitting | Fits training noise, fails on new data |
| Underfitting | Too simple, poor on train and test |
| Bias-variance | Simple models: high bias; complex: high variance |
| Data leakage | Test information influencing training |
| Hyper-parameter | Setting chosen before training (k, trees, depth) |
| Ensemble | Combining several models for a better prediction |
| Normalisation vs standardisation | Min-max to [0,1] vs zero mean, unit variance |
| LabelEncoder vs OneHot | Integer codes vs one binary column per category |
| Pydantic | Python data validation via type hints |
| ASGI | Async server interface used by FastAPI/Uvicorn |
| joblib | Library to save and load trained models |
