"""Experiments for the paper. Run from repo root: python scripts/research_experiments.py
Writes outputs/research_results.json and outputs/research_figures/*.png"""
import json, os, warnings
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold, cross_validate, cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings("ignore")
SEED = 42
OUT = "outputs"; FIG = os.path.join(OUT, "research_figures"); os.makedirs(FIG, exist_ok=True)
res = {}

# ---------------- B. Crop: 7 models, repeated stratified CV ----------------
crop = pd.read_csv("data/Crop_recommendation.csv")
Xc, yc = crop.drop(columns="label"), crop["label"]
MODELS = {
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=SEED),
    "Decision Tree": DecisionTreeClassifier(random_state=SEED),
    "KNN (k=5)": KNeighborsClassifier(5),
    "SVM (RBF)": SVC(random_state=SEED),
    "Logistic Regression": LogisticRegression(max_iter=2000),
    "MLP (64,32)": MLPClassifier((64, 32), max_iter=800, random_state=SEED),
    "Hist. Gradient Boosting": HistGradientBoostingClassifier(random_state=SEED),
}
cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=SEED)  # 15 folds
scores, table = {}, {}
for name, m in MODELS.items():
    r = cross_validate(make_pipeline(StandardScaler(), m), Xc, yc, cv=cv,
                       scoring=["accuracy", "f1_macro"], n_jobs=-1)
    scores[name] = r["test_accuracy"]
    table[name] = {"acc_mean": round(r["test_accuracy"].mean() * 100, 2), "acc_std": round(r["test_accuracy"].std() * 100, 2),
                   "f1_macro_mean": round(r["test_f1_macro"].mean() * 100, 2), "f1_macro_std": round(r["test_f1_macro"].std() * 100, 2)}
    print(name, table[name])
res["crop_cv"] = table
# paired Wilcoxon: best model vs each other (same 15 folds)
best = max(scores, key=lambda k: scores[k].mean())
res["crop_best"] = best
res["crop_wilcoxon_vs_best"] = {}
for k, v in scores.items():
    if k == best: continue
    d = scores[best] - v
    p = 1.0 if np.all(d == 0) else float(stats.wilcoxon(scores[best], v).pvalue)
    res["crop_wilcoxon_vs_best"][k] = {"mean_diff_pp": round(d.mean() * 100, 2), "p_value": round(p, 4)}

# ---------------- D. Crop: robustness to sensor noise ----------------
Xtr, Xte, ytr, yte = train_test_split(Xc, yc, test_size=0.2, stratify=yc, random_state=SEED)
sd = Xtr.std().values
rng = np.random.default_rng(SEED)
levels = [0.0, 0.1, 0.25, 0.5, 1.0]            # noise std as a fraction of each feature's std
fitted = {n: make_pipeline(StandardScaler(), m).fit(Xtr, ytr) for n, m in MODELS.items()}
noise = {n: [] for n in MODELS}
for lv in levels:
    for n, mdl in fitted.items():
        accs = [mdl.score(Xte.values + rng.normal(0, lv * sd, Xte.shape), yte) for _ in range(10)]
        noise[n].append(round(float(np.mean(accs)) * 100, 2))
res["noise_levels_fraction_of_std"] = levels
res["crop_noise_accuracy"] = noise
fig, ax = plt.subplots(figsize=(6.5, 4))
for n, v in noise.items(): ax.plot(levels, v, marker="o", label=n)
ax.set_xlabel("Gaussian noise std (fraction of feature std)"); ax.set_ylabel("Test accuracy (%)")
ax.set_title("Crop model robustness to sensor noise"); ax.grid(alpha=.3); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "noise_robustness.png"), dpi=200); plt.close(fig)

# ---------------- A. Fertilizer: are the labels predictable at all? ----------------
fert = pd.read_csv("data/Fertilizer_Prediction.csv")
y = fert["Fertilizer Name"]; num = ["Temperature", "Humidity", "Moisture", "Nitrogen", "Phosphorous", "Potassium"]
res["fert_rows"] = len(fert); res["fert_chance_pct"] = round(100 / y.nunique(), 2)
res["fert_class_share_pct"] = (y.value_counts(normalize=True) * 100).round(2).to_dict()
res["fert_feature_means_by_label"] = fert.groupby(y)[num].mean().round(2).to_dict("index")
res["fert_anova_p"] = {c: round(float(stats.f_oneway(*[g[c].values for _, g in fert.groupby(y)]).pvalue), 4) for c in num}
res["fert_chi2_p_soil"] = round(float(stats.chi2_contingency(pd.crosstab(fert["Soil Type"], y))[1]), 4)
X = pd.get_dummies(fert[num + ["Soil Type"]]).astype(float)
sub = np.random.default_rng(SEED).choice(len(fert), 20000, replace=False)
Xs, ys = X.iloc[sub], y.iloc[sub]
res["fert_mutual_info_max"] = round(float(mutual_info_classif(Xs, ys, random_state=SEED).max()), 4)
rf = RandomForestClassifier(100, random_state=SEED, n_jobs=-1)
real = cross_val_score(rf, Xs, ys, cv=3).mean()
shuf = cross_val_score(rf, Xs, np.random.default_rng(SEED).permutation(ys.values), cv=3).mean()
res["fert_rf_cv_real_pct"] = round(real * 100, 2); res["fert_rf_cv_shuffled_labels_pct"] = round(shuf * 100, 2)

json.dump(res, open(os.path.join(OUT, "research_results.json"), "w"), indent=1)
print("\nbest crop model:", best, "\nfert RF CV real/shuffled:", res["fert_rf_cv_real_pct"], res["fert_rf_cv_shuffled_labels_pct"])
