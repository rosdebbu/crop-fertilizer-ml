"""Builds paper/Research_Paper.docx (two-column, IEEE-style) from outputs/research_results.json.
Run from repo root after scripts/research_experiments.py:  python scripts/build_paper.py"""
import json, os, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

R = json.load(open("outputs/research_results.json"))
cv, noise, lv = R["crop_cv"], R["crop_noise_accuracy"], R["noise_levels_fraction_of_std"]
wil, fa, mean, best = R["crop_wilcoxon_vs_best"], R["fert_anova_p"], R["fert_feature_means_by_label"], R["crop_best"]
ABBR = {"Random Forest": "RF", "Decision Tree": "DT", "KNN (k=5)": "KNN", "SVM (RBF)": "SVM",
        "Logistic Regression": "LR", "MLP (64,32)": "MLP", "Hist. Gradient Boosting": "HGB"}
FIGDIR = "paper/figures"; os.makedirs(FIGDIR, exist_ok=True)
plt.rcParams.update({"font.family": "serif", "font.size": 7, "axes.linewidth": .6})

# ---------- figures (sized for one 3.4 in column) ----------
fig, ax = plt.subplots(figsize=(3.4, 2.2))
names = list(cv)
ax.barh([ABBR[n] for n in names][::-1], [cv[n]["acc_mean"] for n in names][::-1],
        xerr=[cv[n]["acc_std"] for n in names][::-1], color="#2f5d50", capsize=2)
ax.set_xlim(95, 100); ax.set_xlabel("Cross-validated accuracy (%)"); ax.grid(axis="x", alpha=.3)
fig.tight_layout(); fig.savefig(f"{FIGDIR}/fig1_cv.png", dpi=300); plt.close(fig)

fig, ax = plt.subplots(figsize=(3.4, 2.4))
for n, v in noise.items(): ax.plot(lv, v, marker="o", ms=3, lw=1, label=ABBR[n])
ax.set_xlabel(r"Noise level $\lambda$ (noise std / feature std)"); ax.set_ylabel("Test accuracy (%)")
ax.grid(alpha=.3); ax.legend(fontsize=5.5, ncol=2, frameon=False)
fig.tight_layout(); fig.savefig(f"{FIGDIR}/fig2_noise.png", dpi=300); plt.close(fig)

fig, ax = plt.subplots(figsize=(3.4, 2.0))
labs = ["Crop\n(RF, CV)", "Fertilizer\n(RF, real labels)", "Fertilizer\n(RF, shuffled)", "Fertilizer\nchance"]
vals = [cv["Random Forest"]["acc_mean"], R["fert_rf_cv_real_pct"], R["fert_rf_cv_shuffled_labels_pct"], R["fert_chance_pct"]]
b = ax.bar(labs, vals, color=["#2f5d50", "#b5483a", "#8a8a8a", "#c9c9c9"])
for r_, v in zip(b, vals): ax.text(r_.get_x() + r_.get_width() / 2, v + 1.5, f"{v:.1f}", ha="center", fontsize=6.5)
ax.set_ylim(0, 112); ax.set_ylabel("Accuracy (%)"); ax.tick_params(axis="x", labelsize=5.8)
fig.tight_layout(); fig.savefig(f"{FIGDIR}/fig3_audit.png", dpi=300); plt.close(fig)

# ---------- document helpers ----------
d = Document()
sec = d.sections[0]
sec.page_width, sec.page_height = Inches(8.27), Inches(11.69)  # A4
for side in ("left_margin", "right_margin"): setattr(sec, side, Inches(0.75))
sec.top_margin, sec.bottom_margin = Inches(0.8), Inches(0.9)
normal = d.styles["Normal"]; normal.font.name = "Times New Roman"; normal.font.size = Pt(10)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
normal.paragraph_format.space_after = Pt(4); normal.paragraph_format.space_before = Pt(0)

PLACE = re.compile(r"(\[CITE[^\]]*\]|\[Author[^\]]*\]|\[Department[^\]]*\]|\[email[^\]]*\])")

def para(text="", bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=None, after=None, keep=False, indent=None):
    p = d.add_paragraph(); p.alignment = align
    if after is not None: p.paragraph_format.space_after = Pt(after)
    if keep: p.paragraph_format.keep_with_next = True
    if indent: p.paragraph_format.first_line_indent = Inches(indent)
    for chunk in PLACE.split(text):
        if not chunk: continue
        for k, piece in enumerate(re.split(r"_([a-z])(?![a-z])", chunk)):  # x_j -> x with subscript j
            if not piece: continue
            r = p.add_run(piece); r.bold = bold; r.italic = italic
            if k % 2: r.font.subscript = True
            if size: r.font.size = Pt(size)
            if PLACE.fullmatch(chunk): r.font.highlight_color = WD_COLOR_INDEX.YELLOW
    return p

def body(text): return para(text, indent=0.17)

def heading(num, title):
    p = para(f"{num}.  {title.upper()}" if num else title.upper(), size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER, keep=True, after=3)
    p.paragraph_format.space_before = Pt(8)
    for r in p.runs: r.bold = False

def sub(letter, title):
    p = para(f"{letter}. {title}", italic=True, align=WD_ALIGN_PARAGRAPH.LEFT, keep=True, after=2)
    p.paragraph_format.space_before = Pt(3)

def borders(el, **edges):
    pr = el.get_or_add_tcPr() if hasattr(el, "get_or_add_tcPr") else el
    b = OxmlElement("w:tcBorders")
    for edge, sz in edges.items():
        e = OxmlElement(f"w:{edge}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), str(sz)); e.set(qn("w:color"), "000000"); b.append(e)
    pr.append(b)

def table(num, title, header, rows, widths=None):
    para(f"TABLE {num}", size=8, align=WD_ALIGN_PARAGRAPH.CENTER, after=0, keep=True)
    para(title.upper(), size=8, align=WD_ALIGN_PARAGRAPH.CENTER, after=3, keep=True)
    t = d.add_table(rows=1, cols=len(header)); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = True
    def fill(cells, vals, bold=False):
        for c, v in zip(cells, vals):
            c.text = ""; p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(str(v)); r.font.size = Pt(7.5); r.bold = bold
    fill(t.rows[0].cells, header, bold=True)
    for row in rows: fill(t.add_row().cells, row)
    for row in t.rows[:-1]:
        for c in row.cells:
            for pp in c.paragraphs: pp.paragraph_format.keep_with_next = True
    for row in t.rows:
        trPr = row._tr.get_or_add_trPr(); cs = OxmlElement("w:cantSplit"); trPr.append(cs)
    for c in t.rows[0].cells: borders(c._tc, top=8, bottom=6)
    for c in t.rows[-1].cells: borders(c._tc, bottom=8)
    if widths:
        for row in t.rows:
            for c, w in zip(row.cells, widths): c.width = Inches(w)
    d.add_paragraph().paragraph_format.space_after = Pt(2)

def figure(path, caption, w=3.3):
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=Inches(w))
    para(caption, size=8, align=WD_ALIGN_PARAGRAPH.CENTER, after=6)

def eq(text, label):
    p = para(f"{text}\t({label})", align=WD_ALIGN_PARAGRAPH.CENTER, italic=True, after=4)
    p.paragraph_format.tab_stops.add_tab_stop(Inches(3.35), alignment=2)

# ---------- title block (single column) ----------
para("Benchmark Accuracy Is Not Field Reliability: Auditing Crop and Fertilizer Recommendation Datasets and Their Robustness to Sensor Noise",
     bold=True, size=17, align=WD_ALIGN_PARAGRAPH.CENTER, after=8)
para("Debjit Das, Anshumaan Das and Dr. Sasikala E", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
para("Department of Data Science and Business Systems, School of Computing, SRM Institute of Science and Technology, Kattankulathur, Chennai 603 203, India", italic=True, size=10, align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
para("debjitdas90908@gmail.com, anshumaan.das@gmail.com", size=10, align=WD_ALIGN_PARAGRAPH.CENTER, after=8)

# ---------- two-column body ----------
body_sec = d.add_section(WD_SECTION.CONTINUOUS)
cols = OxmlElement("w:cols"); cols.set(qn("w:num"), "2"); cols.set(qn("w:space"), "360")
body_sec._sectPr.append(cols)

# footer page number
fp = d.sections[-1].footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
fld = OxmlElement("w:fldSimple"); fld.set(qn("w:instr"), "PAGE"); fp._p.append(fld)

abst = (f"Machine-learning crop and fertilizer recommenders are usually judged on clean public benchmarks, where accuracy above 95% "
        f"is routinely reported. This paper tests whether such scores reflect field reliability. On the Crop Recommendation dataset "
        f"(2,200 samples, 22 classes) seven classifiers reach {min(v['acc_mean'] for v in cv.values())}–{cv[best]['acc_mean']}% "
        f"under repeated stratified cross-validation, with {best} best ({cv[best]['acc_mean']} ± {cv[best]['acc_std']}%). "
        f"However, when Gaussian measurement noise of 0.25 feature standard deviations is added to the test inputs, {best} falls to "
        f"{noise[best][2]}% while SVM and KNN retain {noise['SVM (RBF)'][2]}% and {noise['KNN (k=5)'][2]}%: the best clean-data model is "
        f"not the most robust. On the Fertilizer Prediction dataset ({R['fert_rows']:,} samples, 7 classes) every model performs at chance "
        f"(about {R['fert_chance_pct']}%); ANOVA, chi-square, mutual-information and shuffled-label tests show that the labels are statistically "
        f"independent of the features. We contribute a short dataset-audit procedure, a noise-robustness protocol, and an open web prototype "
        f"that raises a reliability warning when a model performs at chance.")
p = para("", after=4)
r = p.add_run("Abstract—"); r.bold = True; r.italic = True
r = p.add_run(abst); r.bold = True
p = para("", after=6)
r = p.add_run("Index Terms—"); r.bold = True; r.italic = True
r = p.add_run("crop recommendation, fertilizer recommendation, precision agriculture, random forest, dataset audit, robustness to noise."); r.italic = True

heading("I", "Introduction")
body("Precision agriculture aims to match crop and fertilizer decisions to local soil and climate conditions. Machine-learning models "
     "trained on soil nutrient levels (nitrogen, phosphorus, potassium), pH and weather variables are an attractive, low-cost alternative "
     "to repeated laboratory analysis, and many studies train classifiers on two public Kaggle datasets and report accuracy above 95% [7], [8].")
body("Two questions are rarely asked. First, do the labels in the dataset actually depend on the features? A model cannot learn a "
     "relationship that does not exist, yet a high score is often taken as proof that one does. Second, do reported model rankings survive "
     "the measurement error of real soil and weather sensors, which is absent from clean benchmarks?")
body("This paper answers both questions for the crop and fertilizer datasets. Our contributions are: (1) a statistical audit showing that the "
     "public fertilizer labels carry no learnable signal; (2) a comparison of seven classifiers on the crop dataset using repeated "
     "cross-validation and paired significance tests; (3) a controlled noise-robustness experiment showing that the best clean-data model "
     "is among the least robust; and (4) an open prototype that exposes a reliability warning whenever a model is no better than chance.")

heading("II", "Related Work")
body("The classifiers compared in this paper are standard. Random forests [1] combine bootstrap sampling with random feature selection, "
     "nearest-neighbour rules [2] classify by proximity, and support vector machines [3] maximise the margin; all are available in "
     "scikit-learn [4]. Crop and fertilizer recommendation from soil and climate readings is a natural tabular classification task for "
     "these methods, and the two Kaggle datasets used here [7], [8] are public benchmarks on which high accuracy is easy to obtain. A "
     "survey of individual crop-recommendation applications is outside the scope of this short paper, which concentrates on how such "
     "benchmarks should be evaluated.")
body("Machine-learning methodology warns that benchmark datasets can contain label errors that destabilise model rankings [9], and that "
     "models may exploit shortcuts that do not reflect real ability [10]. Models should be compared with appropriate statistical tests "
     "[5], [6], and a shuffled-label control gives the accuracy expected by chance [11]. Robustness to input corruption is usually "
     "assessed by perturbing the inputs at several severities [12]. We apply these ideas to agricultural recommenders, where input "
     "noise from low-cost sensors is a practical concern.")

heading("III", "Data and Methodology")
sub("A", "Datasets")
body("The Crop Recommendation dataset [7] has 2,200 rows and 22 balanced crop classes (100 samples each) with seven features: N, P, K, "
     "temperature, humidity, pH and rainfall. The Fertilizer Prediction dataset [8] has 100,000 rows and seven fertilizer classes "
     "(Urea, DAP, 14-35-14, 28-28, 17-17-17, 20-20, 10-26-26) with temperature, humidity, moisture, soil type, N, P and K. Neither file has "
     "missing values or duplicate rows. The datasets use different crop lists and are therefore treated as separate problems.")
sub("B", "Classifiers")
body("We compare Random Forest (RF, 100 trees) [1], a single decision tree (DT), k-nearest neighbours (KNN, k = 5) [2], an RBF support "
     "vector machine (SVM) [3], logistic regression (LR), a multilayer perceptron (MLP, hidden layers 64 and 32) and histogram gradient "
     "boosting (HGB), all implemented in scikit-learn [4] with default settings and no tuning, so that differences reflect model "
     "families rather than tuning effort. Standardisation, z = (x − μ)/σ, is fitted inside each training fold to avoid leakage.")
sub("C", "Evaluation protocol")
body("We use repeated stratified 5-fold cross-validation with three repeats (15 folds) and report accuracy and macro-F1 as mean ± standard "
     "deviation. Differences between the best model and each other model are tested with the paired Wilcoxon signed-rank test [5], [6] "
     "over the 15 fold scores.")
sub("D", "Noise-robustness protocol")
body("Models are trained once on clean data (80/20 stratified split). At test time each feature x_j is replaced by")
eq("x′_j = x_j + ε,   ε ~ N(0, (λ·σ_j)²)", "1")
body("where σ_j is the training standard deviation of feature j and λ ∈ {0, 0.1, 0.25, 0.5, 1.0}. Accuracy is averaged over 10 noise "
     "draws per level.")
sub("E", "Dataset audit")
body("For the fertilizer data we apply four checks: one-way ANOVA of each numeric feature across fertilizer classes; a chi-square test of "
     "soil type against the label; the maximum mutual information between any feature and the label; and Random Forest cross-validated "
     "accuracy on real versus randomly shuffled labels (20,000-row subsample, 3 folds). If real-label accuracy equals shuffled-label "
     "accuracy, the labels are independent of the features.")

heading("IV", "Results and Discussion")
sub("A", "Crop dataset: clean-data performance")
table("I", "Crop dataset, repeated stratified 5-fold CV (3 repeats)",
      ["Model", "Accuracy (%)", "Macro-F1 (%)", f"Δ vs {ABBR[best]} (pp)", "p"],
      [[ABBR[k], f"{v['acc_mean']} ± {v['acc_std']}", f"{v['f1_macro_mean']} ± {v['f1_macro_std']}",
        "–" if k == best else wil[k]["mean_diff_pp"], "–" if k == best else wil[k]["p_value"]] for k, v in cv.items()])
body(f"{best} is the most accurate model ({cv[best]['acc_mean']}%, Table I, Fig. 1). Every other model is significantly worse at p < 0.05, "
     f"but the absolute gaps are small (0.5–2.4 percentage points). Even a linear model (LR) reaches {cv['Logistic Regression']['acc_mean']}%, "
     "which indicates that the crop classes are almost linearly separable and that the benchmark is easy.")
figure(f"{FIGDIR}/fig1_cv.png", "Fig. 1. Cross-validated accuracy of the seven classifiers (mean ± s.d., 15 folds).")

sub("B", "Crop dataset: robustness to sensor noise")
table("II", "Crop test accuracy (%) under added Gaussian noise",
      ["Model"] + [f"λ={x}" for x in lv], [[ABBR[k]] + [f"{x:.2f}" for x in v] for k, v in noise.items()])
body(f"Clean-data ranking does not carry over to noisy inputs (Table II, Fig. 2). At λ = 0.25, {ABBR[best]} drops from "
     f"{noise[best][0]}% to {noise[best][2]}%, whereas SVM keeps {noise['SVM (RBF)'][2]}% and KNN {noise['KNN (k=5)'][2]}%. HGB and DT degrade "
     f"fastest ({noise['Hist. Gradient Boosting'][2]}% and {noise['Decision Tree'][2]}%). A plausible explanation is that axis-aligned tree "
     "splits are sensitive to small shifts near thresholds, while distance- and margin-based models smooth over perturbations; we did not "
     "test this explanation directly. At λ = 1.0 all models fall below 45%, so the benchmark gives no assurance at high noise.")
figure(f"{FIGDIR}/fig2_noise.png", "Fig. 2. Test accuracy versus noise level λ (Eq. 1).")

sub("C", "Fertilizer dataset: label audit")
table("III", "Fertilizer dataset audit",
      ["Check", "Result"],
      [["Chance level (7 classes)", f"{R['fert_chance_pct']}%"],
       ["Class shares", f"{min(R['fert_class_share_pct'].values())}–{max(R['fert_class_share_pct'].values())}%"],
       ["ANOVA p (six numeric features)", f"{min(fa.values())}–{max(fa.values())}"],
       ["Chi-square p (soil vs label)", R["fert_chi2_p_soil"]],
       ["Max mutual information (nats)", R["fert_mutual_info_max"]],
       ["RF CV accuracy, real labels", f"{R['fert_rf_cv_real_pct']}%"],
       ["RF CV accuracy, shuffled labels", f"{R['fert_rf_cv_shuffled_labels_pct']}%"]], widths=[2.1, 1.2])
body(f"No feature differs significantly across fertilizer classes (all p > 0.05), and class means are practically identical "
     f"(Urea: N {mean['Urea']['Nitrogen']}, P {mean['Urea']['Phosphorous']}, K {mean['Urea']['Potassium']}; DAP: N {mean['DAP']['Nitrogen']}, "
     f"P {mean['DAP']['Phosphorous']}, K {mean['DAP']['Potassium']}). Random Forest scores {R['fert_rf_cv_real_pct']}% on the real labels and "
     f"{R['fert_rf_cv_shuffled_labels_pct']}% on shuffled labels (Fig. 3), so the labels are independent of the features and no model can exceed "
     "chance. Accuracy claims on this file should therefore be treated with caution. A recommender for this task needs data in which the "
     "fertilizer is determined by measured soil deficiency, for example from soil-test reports labelled by agronomists.")
figure(f"{FIGDIR}/fig3_audit.png", "Fig. 3. Crop versus fertilizer accuracy compared with chance and shuffled labels.")

sub("D", "Recommended audit checklist")
body("From these results we suggest that any agricultural recommender paper report: (i) chance-level accuracy; (ii) a shuffled-label control; "
     "(iii) per-feature tests of dependence on the label; (iv) repeated cross-validation with significance tests; and (v) accuracy under "
     "input noise at several levels.")

heading("V", "System Prototype")
body("A FastAPI backend serves the trained models and a single-page web interface provides crop prediction, fertilizer prediction, a "
     "rule-based soil-health audit, profit and dosage estimates, and a climate-stress simulation that perturbs temperature, humidity and "
     "rainfall and re-predicts the crop. The five shared field readings (N, P, K, temperature, humidity) feed both models, and the "
     "recommended crop is passed to the fertilizer view for advice and dosage only. The API returns a reliability warning whenever a "
     "model's best accuracy is within ten points of chance. Satellite, weather and market panels use stored sample values; they are an "
     "interface prototype and are not part of the evaluated results.")

heading("VI", "Threats to Validity and Limitations")
body("Both datasets are public benchmarks, not field measurements. Noise is simulated as independent Gaussian error and does not model "
     "sensor bias, drift or correlated errors. Models use default hyper-parameters; tuning could change absolute scores and may alter the "
     "ranking. Noise was applied at test time only; training with noise (augmentation) may reduce the gap and was not studied. The study "
     "shows no agronomic yield benefit, and results on other regions or crops may differ.")

heading("VII", "Conclusion and Future Work")
body("High benchmark accuracy does not imply a usable recommender. A short audit exposed a fertilizer dataset with no learnable signal, and "
     "a noise test changed the model ranking on the crop dataset. Future work will collect labelled field soil-test data, model realistic "
     "sensor errors, evaluate noise-aware training and calibrated probabilities, and add satellite vegetation indices as features.")

heading("", "References")
for ref in [
    "[1] L. Breiman, “Random forests,” Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.",
    "[2] T. Cover and P. Hart, “Nearest neighbor pattern classification,” IEEE Trans. Inf. Theory, vol. 13, no. 1, pp. 21–27, 1967.",
    "[3] C. Cortes and V. Vapnik, “Support-vector networks,” Machine Learning, vol. 20, no. 3, pp. 273–297, 1995.",
    "[4] F. Pedregosa et al., “Scikit-learn: Machine learning in Python,” J. Mach. Learn. Res., vol. 12, pp. 2825–2830, 2011.",
    "[5] F. Wilcoxon, “Individual comparisons by ranking methods,” Biometrics Bulletin, vol. 1, no. 6, pp. 80–83, 1945.",
    "[6] J. Demšar, “Statistical comparisons of classifiers over multiple data sets,” J. Mach. Learn. Res., vol. 7, pp. 1–30, 2006.",
    "[7] Kaggle user atharvaingle, “Crop Recommendation Dataset.” [Online]. Available: kaggle.com/datasets/atharvaingle/crop-recommendation-dataset",
    "[8] Kaggle user irakozekelly, “Fertilizer Prediction.” [Online]. Available: kaggle.com/datasets/irakozekelly/fertilizer-prediction",
    "[9] C. G. Northcutt, A. Athalye, and J. Mueller, “Pervasive label errors in test sets destabilize machine learning benchmarks,” in Proc. NeurIPS Datasets and Benchmarks Track, 2021.",
    "[10] R. Geirhos et al., “Shortcut learning in deep neural networks,” Nature Machine Intelligence, vol. 2, pp. 665–673, 2020.",
    "[11] M. Ojala and G. C. Garriga, “Permutation tests for studying classifier performance,” J. Mach. Learn. Res., vol. 11, pp. 1833–1863, 2010.",
    "[12] D. Hendrycks and T. Dietterich, “Benchmarking neural network robustness to common corruptions and perturbations,” in Proc. Int. Conf. Learning Representations (ICLR), 2019.",
]:
    para(ref, size=8, align=WD_ALIGN_PARAGRAPH.LEFT, after=1)

cp = d.core_properties  # clear tool metadata; set real details
cp.author = ""; cp.last_modified_by = ""; cp.comments = ""; cp.keywords = "crop recommendation, fertilizer recommendation, robustness"
cp.title = "Benchmark Accuracy Is Not Field Reliability: Auditing Crop and Fertilizer Recommendation Datasets"
os.makedirs("paper", exist_ok=True)
d.save("paper/Research_Paper.docx")
print("saved paper/Research_Paper.docx")
