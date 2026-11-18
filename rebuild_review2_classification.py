"""Rebuild the Review II deck for a classification-only project.

All numbers are computed here from the CSVs (default: ./data). If you get the
full 2,200-row dataset, run:  python rebuild_review2_classification.py path/to/crop.csv
"""
import copy, sys, os, time
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from pptx import Presentation
from pptx.util import Emu
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (accuracy_score, precision_recall_fscore_support, confusion_matrix,
                             ConfusionMatrixDisplay)

HERE = os.path.dirname(os.path.abspath(__file__))
CROP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "data", "Crop_recommendation.csv")
FERT = os.path.join(HERE, "data", "Fertilizer_Prediction.csv")
SRC, OUT = os.path.join(HERE, "Review_2_FIXED.pptx"), os.path.join(HERE, "Review_2_Classification.pptx")
CH = os.path.join(HERE, "output_charts"); os.makedirs(CH, exist_ok=True)
MODELS = {"Random Forest": lambda: RandomForestClassifier(n_estimators=100, random_state=42, oob_score=True),
          "Decision Tree": lambda: DecisionTreeClassifier(random_state=42),
          "KNN (k=5)": lambda: KNeighborsClassifier(5)}

# ------------------------------------------------------------------ metrics
def evaluate(X, y):
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, random_state=42, stratify=y)
    sc = StandardScaler().fit(Xtr); a, b = sc.transform(Xtr), sc.transform(Xte)
    res = {"n": len(X), "ntr": len(Xtr), "nte": len(Xte), "k": y.nunique(), "m": {}}
    for name, mk in MODELS.items():
        m = mk().fit(a, ytr); p = m.predict(b)
        pr, rc, f1, _ = precision_recall_fscore_support(yte, p, average="weighted", zero_division=0)
        onehot = (np.array(m.classes_)[None, :] == np.array(yte)[:, None]).astype(float)
        cv = cross_val_score(make_pipeline(StandardScaler(), mk()), X, y,
                             cv=StratifiedKFold(5, shuffle=True, random_state=42))
        d = dict(acc=accuracy_score(yte, p) * 100, prec=pr * 100, rec=rc * 100, f1=f1 * 100,
                 brier=float(((m.predict_proba(b) - onehot) ** 2).sum(1).mean()),
                 cv=cv * 100, cvm=cv.mean() * 100, cvs=cv.std() * 100)
        if name == "Random Forest":
            d["oob"] = m.oob_score_ * 100
            t = time.perf_counter()
            for _ in range(30): m.predict(b[:1])
            d["ms"] = (time.perf_counter() - t) / 30 * 1000
            d["cm"] = confusion_matrix(yte, p, labels=m.classes_); d["classes"] = list(m.classes_)
            d["x0"], d["y0"], d["p0"] = Xte.iloc[0], yte.iloc[0], p[0]
            d["conf0"] = m.predict_proba(b[:1]).max() * 100
        res["m"][name] = d
    return res

crop = pd.read_csv(CROP); fert = pd.read_csv(FERT)
assert crop.isna().sum().sum() == 0 and fert.isna().sum().sum() == 0
for c in ("Soil Type", "Crop Type"): fert[c] = LabelEncoder().fit_transform(fert[c])
RC = evaluate(crop.drop(columns="label"), crop["label"])
RF_ = evaluate(fert.drop(columns="Fertilizer Name"), fert["Fertilizer Name"])
rf, rff = RC["m"]["Random Forest"], RF_["m"]["Random Forest"]
chance = 100 / RC["k"]

# ------------------------------------------------------------------ charts
fig, ax = plt.subplots(figsize=(4.6, 4.2), dpi=200)
ConfusionMatrixDisplay(rf["cm"], display_labels=rf["classes"]).plot(ax=ax, cmap="Blues", colorbar=False,
                                                                    xticks_rotation=90, include_values=RC["k"] <= 12)
ax.set_title("Random Forest confusion matrix\n(crop, holdout n=%d)" % RC["nte"], fontsize=9)
ax.tick_params(labelsize=5 if RC["k"] > 12 else 6); [t.set_fontsize(6) for t in ax.texts]
fig.tight_layout(); fig.savefig(os.path.join(CH, "review2_confusion_crop.png")); plt.close(fig)

fig, ax = plt.subplots(figsize=(4.6, 4.2), dpi=200)
names = list(MODELS); w = .38; xs = np.arange(len(names))
ax.bar(xs - w / 2, [RC["m"][n]["acc"] for n in names], w, label="Crop", color="#1F3864")
ax.bar(xs + w / 2, [RF_["m"][n]["acc"] for n in names], w, label="Fertilizer", color="#C07A12")
fch = 100 / RF_["k"]; ax.axhline(fch, ls="--", c="grey", lw=1); ax.text(2.45, fch + 1.5, "fertilizer chance level", fontsize=6, ha="right")
ax.set_xticks(xs); ax.set_xticklabels(names, fontsize=7); ax.set_ylabel("Holdout accuracy (%)", fontsize=8)
ax.set_ylim(0, 100); ax.legend(fontsize=7); ax.set_title("Model comparison", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(CH, "review2_model_comparison.png")); plt.close(fig)

def box(ax, x, y, w, h, title, lines, fc, ec):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc=fc, ec=ec, lw=2))
    ax.text(x + w / 2, y + h - 3, title, ha="center", va="top", fontsize=13, fontweight="bold", color=ec)
    ax.text(x + 2, y + h - 9.5, "\n".join("• " + l for l in lines), ha="left", va="top", fontsize=11, linespacing=1.5)
def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", lw=2.5, color="#444"))

def diagram(path, boxes, arrows):
    fig, ax = plt.subplots(figsize=(13, 5.6), dpi=170); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    for b in boxes: box(ax, *b)
    for a in arrows: arrow(ax, *a)
    fig.savefig(path, bbox_inches="tight", facecolor="white"); plt.close(fig)

nF = crop.shape[1] - 1
diagram(os.path.join(CH, "review2_obj1_pipeline.png"), [
    (1, 52, 30, 42, "1. Raw Datasets", [f"Crop: {RC['n']} samples, {nF} features", f"{RC['k']} crop classes",
        f"Fertilizer: {RF_['n']} samples, 8 features", f"{RF_['k']} fertilizer classes", "No missing values"], "#EAF0FA", "#1F3864"),
    (35, 52, 30, 42, "2. Encoding", ["Soil Type: label encoded", "Crop Type: label encoded", "All inputs numeric",
        "Target = crop / fertilizer"], "#E8F5EC", "#1B7A43"),
    (69, 52, 30, 42, "3. Stratified Split", [f"80% train ({RC['ntr']} rows)", f"20% test ({RC['nte']} rows)",
        "random_state = 42", "Class ratios preserved"], "#F3ECF8", "#6B3A8C"),
    (69, 4, 30, 42, "4. Scaling", ["StandardScaler z = (x-mu)/sigma", "Fit on TRAIN only", "Applied to test set",
        "Prevents data leakage"], "#FDF6E3", "#9A6A00"),
    (35, 4, 30, 42, "5. Validation", ["5-fold Stratified CV", "Bootstrap sampling (RF bagging)",
        "Out-of-bag (OOB) estimate", "Holdout test evaluation"], "#FBEAEA", "#A12B2B"),
    (1, 4, 30, 42, "6. Ready for Models", ["Scaled train / test matrices", "Random Forest, Decision Tree, KNN",
        "Metrics + confusion matrix"], "#EAF0FA", "#1F3864")],
    [(31.5, 73, 34, 73), (65.5, 73, 68.5, 73), (84, 51, 84, 47), (68.5, 25, 65.5, 25), (34.5, 25, 31.5, 25)])
diagram(os.path.join(CH, "review2_obj2_architecture.png"), [
    (1, 58, 98, 38, "Input: soil and climate readings", ["Crop model: N, P, K, temperature, humidity, pH, rainfall",
        "Fertilizer model: temperature, humidity, moisture, soil type, crop type, N, P, K"], "#EAF0FA", "#1F3864"),
    (1, 6, 46, 44, "Stage 1: Crop Classifier", [f"Random Forest (100 trees), Decision Tree, KNN (k=5)",
        f"Predicts 1 of {RC['k']} crops", "Outputs class + probability"], "#E8F5EC", "#1B7A43"),
    (53, 6, 46, 44, "Stage 2: Fertilizer Classifier", ["Random Forest, Decision Tree, KNN (k=5)",
        f"Predicts 1 of {RF_['k']} fertilizers", "Crop type links the two stages"], "#F3ECF8", "#6B3A8C")],
    [(50, 57, 24, 51), (50, 57, 76, 51), (47.5, 28, 52.5, 28)])

# ------------------------------------------------------------------ deck
prs = Presentation(SRC)
S = lambda i: prs.slides[i - 1]
def shape(i, name): return next(s for s in S(i).shapes if s.name == name)

def rewrite(sh, lines):
    """lines = [(template_index, text)]; templates are paragraphs 0,1,2 of the original box."""
    tf = sh.text_frame; ps = list(tf.paragraphs)
    tm = [copy.deepcopy(p._p) for p in ps[:3]]
    for p in ps: p._p.getparent().remove(p._p)
    for k, text in lines:
        el = copy.deepcopy(tm[min(k, len(tm) - 1)]); tf._txBody.append(el)
        runs = el.findall("{http://schemas.openxmlformats.org/drawingml/2006/main}r")
        for r in runs[1:]: el.remove(r)
        runs[0].find("{http://schemas.openxmlformats.org/drawingml/2006/main}t").text = text

def set_para(slide_no, startswith, text):
    for sh in S(slide_no).shapes:
        if sh.has_text_frame:
            for para in sh.text_frame.paragraphs:
                if para.text.strip().startswith(startswith) and para.runs:
                    para.runs[0].text = text
                    for r in para.runs[1:]: r.text = ""

def add_pic(slide_no, path, left, top, width):
    S(slide_no).shapes.add_picture(path, Emu(left), Emu(top), width=Emu(width))

def replace_pic(slide_no, path):
    old = max((s for s in S(slide_no).shapes if s.shape_type == 13), key=lambda s: s.width * s.height)
    old._element.getparent().remove(old._element)
    add_pic(slide_no, path, 900000, 1250000, 10400000)

f1 = lambda d: f"{d:.2f}%"
# slide 2 agenda
rewrite(shape(2, "object 7"), [(0, t) for t in [
    "Course Work & Academic Foundation", "Project Overview & Problem Formulation",
    "Literature Survey Highlights (10 Studies)", "Review II Scope & Evaluation Parameters",
    "Model Validation & Resampling (K-Fold CV & Bootstrapping)",
    "Model Performance Evaluation (Accuracy, Precision, Recall, F1, MSE, Confusion Matrix)",
    "Classification Models (Random Forest, Decision Tree, KNN)",
    "Model Prediction Pipeline & Comparison of Classification Models",
    "Project Milestones, Publications & Future Scope", "References & Conclusion"]])

# slides 16-17 stale claims
set_para(16, "Agro-Climatic Generalization Gap", "Agro-Climatic Generalization Gap — Existing classifiers are tuned on one task and degrade across diverse multi-class crops and seasonal variation.")
set_para(16, "Feature Stoichiometry Gap", "Evaluation Rigor Gap — Many systems report a single train-test split instead of stratified cross-validation and per-class confusion-matrix analysis.")
set_para(17, "Design and engineer", "Build a reproducible data pipeline: encoding, stratified train-test split, leakage-free scaling and 5-fold stratified cross-validation for crop and fertilizer datasets.")
set_para(17, "Build a high-precision", "Build a two-stage classification pipeline: Stage 1 crop recommendation (RF, DT, KNN) feeding crop type into Stage 2 fertilizer prediction.")

# slide 18 Objective 1
rewrite(shape(18, "object 5"), [
    (0, "Data Preprocessing, Validation & Resampling — Objective 1"),
    (1, f"Two tabular datasets are cleaned, encoded and split with no data leakage: crop data ({RC['n']} samples, {nF} features, {RC['k']} crops) and fertilizer data ({RF_['n']} samples, 8 features, {RF_['k']} fertilizers)."),
    (2, "• Data Quality: No missing values; Soil Type and Crop Type are label-encoded so every input is numeric."),
    (2, f"• Stratified Split: 80/20 train-test split (random_state=42) gives {RC['ntr']} training and {RC['nte']} test rows with class proportions preserved."),
    (2, "• Leakage-Free Scaling: StandardScaler is fitted on the training set only and then applied to the test set."),
    (2, "• Resampling: 5-fold Stratified Cross-Validation plus bootstrap sampling inside Random Forest (out-of-bag estimate)."),
    (2, f"• Observed Result: Random Forest crop CV accuracy is {rf['cvm']:.2f}% ± {rf['cvs']:.2f}% (OOB {rf['oob']:.2f}%), stable across folds. Fertilizer CV accuracy is {rff['cvm']:.1f}%, about the {100/RF_['k']:.1f}% chance level for {RF_['k']} classes."),
])
replace_pic(19, os.path.join(CH, "review2_obj1_pipeline.png"))

# slide 20 Validation & resampling
perclass = RC["nte"] // 5
rewrite(shape(20, "object 5"), [
    (0, "K-Fold Cross-Validation, Bootstrapping & Resampling"),
    (1, "• K-Fold Cross-Validation: Data D is split into K=5 disjoint folds D_k. In iteration k the model trains on D \\ D_k and is tested on D_k:"),
    (2, "     CV_K = (1 / K) ∑_{k=1}^K Score(f_(-k), D_k)    (every observation is tested exactly once)"),
    (1, f"• Stratified K-Fold: Each fold keeps the class ratio P(y=c) of the full data ({RC['n']//5} samples per fold for the crop data), avoiding class-imbalance bias."),
    (1, "• Bootstrapping: Draw n samples WITH REPLACEMENT from n. Probability an observation is never chosen:"),
    (2, "     (1 - 1/n)^n → 1/e ≈ 0.368, so each bootstrap sample holds about 63.2% unique observations"),
    (1, f"• Out-of-Bag (OOB) Validation: The ~36.8% unseen samples test each tree. Our Random Forest OOB accuracy: {rf['oob']:.1f}% (crop), {rff['oob']:.1f}% (fertilizer)."),
    (1, "• Bagging: Random Forest averages M=100 bootstrap trees, reducing variance: Var = ρσ² + (1-ρ)σ²/M."),
])

# slide 21 Performance evaluation
folds = " | ".join(f"Fold {i+1}: {v:.1f}%" for i, v in enumerate(rf["cv"]))
sh21 = shape(21, "object 5")
rewrite(sh21, [
    (0, "Performance Metrics: Confusion Matrix, Accuracy, Precision, Recall, F1 & MSE"),
    (1, f"• Confusion Matrix: {RC['k']}×{RC['k']} table of true vs predicted crops with TP, TN, FP (Type I) and FN (Type II)."),
    (2, "   - Agronomic risk: FP = wrong crop/fertilizer advice (cost); FN = missed correct recommendation"),
    (1, "• Accuracy = (TP + TN) / Total  |  Precision = TP / (TP + FP)  |  Recall = TP / (TP + FN)"),
    (1, "• F1-Score = 2 × (Precision × Recall) / (Precision + Recall), weighted over classes"),
    (1, "• MSE for classifiers (Brier score) on predicted class probabilities:"),
    (2, "     MSE = (1/n) ∑_i ∑_c (p̂_ic − y_ic)²   (lower is better)"),
    (1, f"• Random Forest (crop, holdout n={RC['nte']}): Accuracy {f1(rf['acc'])} | Precision {f1(rf['prec'])} | Recall {f1(rf['rec'])} | F1 {f1(rf['f1'])} | MSE {rf['brier']:.3f}"),
    (1, f"• 5-Fold Stratified CV (crop, n={RC['n']}): {folds}"),
    (1, f"• Mean CV accuracy = {rf['cvm']:.1f}% ± {rf['cvs']:.1f}% (chance level = {chance:.1f}%)"),
])
sh21.width = Emu(7300000)
add_pic(21, os.path.join(CH, "review2_confusion_crop.png"), 8000000, 1500000, 3700000)

# slide 22 Objective 2
rewrite(shape(22, "object 5"), [
    (0, "Classification Models — Objective 2"),
    (1, "The project solves two multi-class classification problems in sequence:"),
    (2, f"• Crop Recommendation: Random Forest (100 trees), Decision Tree (CART) and KNN (k=5) classify {RC['k']} crops from {nF} soil and climate features."),
    (2, f"• Fertilizer Prediction: the same three classifiers predict 1 of {RF_['k']} fertilizers from temperature, humidity, moisture, soil type, crop type, N, P and K."),
    (2, "• Two-Stage Link: the recommended crop becomes the crop-type input of the fertilizer stage."),
    (2, "• Deployment: FastAPI endpoints /api/predict/crop and /api/predict/fertilizer return the predicted class, class probabilities and all three models' predictions."),
    (2, "• Evaluation: holdout test, 5-fold stratified CV, confusion matrices and model comparison (next slides)."),
])
for s in S(23).shapes:
    if s.name in ("object 6", "object 7"):
        rs = [r for p in s.text_frame.paragraphs for r in p.runs]
        rs[0].text = "Objective 2: Two-Stage Classification" if s.name == "object 6" else ""
        if s.name == "object 6": s.top = Emu(300000); s.height = Emu(700000)
        for r in rs[1:]: r.text = ""
replace_pic(23, os.path.join(CH, "review2_obj2_architecture.png"))

# slide 24 formulas
sh24 = shape(24, "object 5")
rewrite(sh24, [
    (0, "Mathematical Formulations: Classification Models"),
    (1, "• Feature Standardisation (all models):   z = (x − μ_train) / σ_train"),
    (1, "• Decision Tree (CART) — Gini impurity and split gain:"),
    (2, "     I_G(t) = 1 − ∑_c p(c|t)² ,    ΔI_G = I_G(t) − (N_L/N_t) I_G(t_L) − (N_R/N_t) I_G(t_R)"),
    (1, "• Random Forest — majority vote of M=100 bootstrap trees:"),
    (2, "     ŷ_RF = argmax_c (1/M) ∑_{m=1}^M I(ŷ_m(x) = c) ,    P(c|x) = (1/M) ∑_m P_m(c|x)"),
    (1, "• K-Nearest Neighbours (k=5, Euclidean distance):"),
    (2, "     d(x, x') = √∑_j (x_j − x'_j)² ,    ŷ = majority class among the 5 nearest training points"),
    (1, "• Evaluation: Accuracy, Precision, Recall, F1 and MSE (Brier) as defined on the Performance Evaluation slide"),
])
sh24.width = Emu(11000000)
for s in S(24).shapes:
    if s.name == "object 2": s.text_frame.paragraphs[0].runs[0].text = "Classification Models"

# slide 25 prediction + comparison
x0 = rf["x0"]; xs_ = ", ".join(f"{k}={v:.1f}" for k, v in x0.items())
rows = [f"   - {n:<14}: Accuracy {f1(d['acc'])} | Precision {f1(d['prec'])} | Recall {f1(d['rec'])} | F1 {f1(d['f1'])} | CV {d['cvm']:.1f}%"
        for n, d in RC["m"].items()]
frows = " | ".join(f"{n} {f1(d['acc'])}" for n, d in RF_["m"].items())
sh25 = shape(25, "object 5")
rewrite(sh25, [
    (0, "Model Prediction & Comparison of Classification Models"),
    (1, f"• Prediction Pipeline (one test sample): input [{xs_}]"),
    (2, "   - Scale with the fitted StandardScaler → Random Forest → predicted crop"),
    (2, f"   - Predicted: {rf['p0']} ({rf['conf0']:.0f}% model confidence) | True label: {rf['y0']} | Latency: {rf['ms']:.0f} ms per call (measured)"),
    (1, f"• Crop Models (holdout n={RC['nte']}, stratified 80/20 split):"),
] + [(2, r) for r in rows] + [
    (1, f"• Fertilizer Models (holdout n={RF_['nte']}, accuracy): {frows}"),
    (1, f"• Observation: Random Forest is the best crop model ({f1(rf['acc'])}), ahead of Decision Tree and KNN. Fertilizer models stay near the {100/RF_['k']:.1f}% chance level, so its features do not yet separate the 7 fertilizers; richer soil-test features are future work."),
])
sh25.width = Emu(7400000)
add_pic(25, os.path.join(CH, "review2_model_comparison.png"), 8000000, 1500000, 3700000)


# slide 26 / 28: only claims the code supports
set_para(26, "Automated Soil Deficiency", "Agronomic Advisory Layer (in app.py):")
set_para(26, "Low Nitrogen", "Predicted fertilizer is mapped to application guidance: bags per acre, timing and over-application risk.")
set_para(26, "Low Phosphorus", "Each crop prediction includes plain-language reasons (e.g. nitrogen and pH levels) explaining the match.")
set_para(26, "Soil pH Imbalance", "Each prediction returns class probabilities and the outputs of all three models for comparison.")
set_para(26, "Field Validation", "Future Scope: validate recommendations against TNAU agronomic guidelines and richer fertilizer data.")
set_para(28, "Journal Manuscript", "Journal Manuscript (Planned, Q1 Agri-Tech Venue):")
set_para(28, "Debjit Das, Anshumaan Das, et al.", "Debjit Das, Anshumaan Das, et al., “Dual-Engine Precision Agronomy: Joint Multi-Class Crop Suitability and Soil Fertilizer Deficit Remediation Using Interpretable Tree Ensembles,” in preparation.")
set_para(28, "Complete reproducible", "Reproducible source code, FastAPI server, Next.js web dashboard and Jupyter tutorials on GitHub (models are trained at server start-up from the bundled CSV files):")

# slide 26: larger, evenly spaced text (was tiny and top-heavy)
from pptx.util import Pt
b26 = shape(26, "object 5"); b26.left, b26.top, b26.width = Emu(800000), Emu(1350000), Emu(10600000)
for k, para in enumerate(b26.text_frame.paragraphs):
    lvl = para._p.find("{http://schemas.openxmlformats.org/drawingml/2006/main}pPr").get("lvl")
    top = k == 0; sec = (lvl is None) and not top
    para.space_before = Pt(14 if (top or sec) else 6)
    for r in para.runs:
        r.font.size = Pt(20 if top else 17 if sec else 15); r.font.bold = True if (top or sec) else None
prs.save(OUT); print("saved", OUT)
print("crop:", {n: round(d["acc"], 1) for n, d in RC["m"].items()}, "fert:", {n: round(d["acc"], 1) for n, d in RF_["m"].items()})
