"""Extra measured results for the report: feature ablation (RF) and timing of the 7 classifiers on the crop data."""
import json, time, warnings
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
warnings.filterwarnings("ignore")
d = pd.read_csv("data/Crop_recommendation.csv"); X, y = d.drop(columns="label"), d["label"]
cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=42)
rf = lambda: make_pipeline(StandardScaler(), RandomForestClassifier(100, random_state=42))
base = cross_val_score(rf(), X, y, cv=cv, n_jobs=-1)
out = {"ablation": {"all features": [round(base.mean() * 100, 2), round(base.std() * 100, 2)]}}
for c in X.columns:
    s = cross_val_score(rf(), X.drop(columns=c), y, cv=cv, n_jobs=-1)
    out["ablation"][f"without {c}"] = [round(s.mean() * 100, 2), round(s.std() * 100, 2)]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, stratify=y, random_state=42)
M = {"Random Forest": RandomForestClassifier(100, random_state=42), "Decision Tree": DecisionTreeClassifier(random_state=42),
     "KNN (k=5)": KNeighborsClassifier(5), "SVM (RBF)": SVC(), "Logistic Regression": LogisticRegression(max_iter=2000),
     "MLP (64,32)": MLPClassifier((64, 32), max_iter=800, random_state=42), "Hist. Gradient Boosting": HistGradientBoostingClassifier(random_state=42)}
out["timing"] = {}
for n, m in M.items():
    p = make_pipeline(StandardScaler(), m)
    ft, pt = [], []
    for _ in range(3):
        t = time.perf_counter(); p.fit(Xtr, ytr); ft.append(time.perf_counter() - t)
        t = time.perf_counter(); p.predict(Xte); pt.append(time.perf_counter() - t)
    out["timing"][n] = [round(float(np.mean(ft)) * 1000, 1), round(float(np.mean(pt)) * 1000, 1)]
json.dump(out, open("outputs/report_extra.json", "w"), indent=1); print(json.dumps(out, indent=1))
