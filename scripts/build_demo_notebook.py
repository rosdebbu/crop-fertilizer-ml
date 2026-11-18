"""Builds notebooks/Project_Demo_EDA.ipynb (executed) and Project_Demo.pdf, in the style of the sample EDA notebook printout.
Run from the repo root:  python scripts/build_demo_notebook.py"""
import os
import nbformat as nbf
from nbclient import NotebookClient
from nbconvert import HTMLExporter

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = []

cells.append(md("""# Crop & Fertilizer Recommendation - Exploratory Data Analysis

**Datasets** (Kaggle): *Crop Recommendation Dataset* (atharvaingle) and *Fertilizer Prediction* (irakozekelly).
**Targets:** `label` (22 crops) and `Fertilizer Name` (7 fertilizers).
**Team:** Debjit Das (RA2411056010276), Anshumaan Das (RA2411056010283) - Guide: Dr. Sasikala E, DSBS, SRM Institute of Science and Technology.

Run the cells top to bottom. The notebook only reads the two CSV files in the `data/` folder of the project."""))

cells.append(code("""# Imports and project paths
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")

# Works whether the notebook is started from notebooks/ or from the project root
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
CROP_CSV = ROOT / "data" / "Crop_recommendation.csv"
FERT_CSV = ROOT / "data" / "Fertilizer_Prediction.csv"
CROP_TARGET, FERT_TARGET = "label", "Fertilizer Name"
print("Project root:", ROOT)
print("Crop file found:", CROP_CSV.exists(), "| Fertilizer file found:", FERT_CSV.exists())"""))

cells.append(md("## 1. Load datasets: shape, dtypes, head"))
cells.append(code("""crop = pd.read_csv(CROP_CSV)
fert = pd.read_csv(FERT_CSV)

for name, df in (("CROP", crop), ("FERTILIZER", fert)):
    print(f"=== {name} ===")
    print("Shape:", df.shape)
    print()
    print(df.dtypes)
    print()
crop.head()"""))
cells.append(code("fert.head()"))

cells.append(md("## 2. Missing value heatmap"))
cells.append(code("""fig, axes = plt.subplots(1, 2, figsize=(14, 4))
for ax, (name, df) in zip(axes, (("Crop", crop), ("Fertilizer (first 2,000 rows)", fert.head(2000)))):
    sns.heatmap(df.isnull(), cbar=False, yticklabels=False, cmap="viridis", ax=ax)
    ax.set_title(f"Missing values (yellow = missing) - {name}")
plt.tight_layout()
plt.show()

print("Missing values - crop:", int(crop.isnull().sum().sum()), "| fertilizer:", int(fert.isnull().sum().sum()))
print("Duplicate rows - crop:", int(crop.duplicated().sum()), "| fertilizer:", int(fert.duplicated().sum()))"""))

cells.append(md("## 3. Distribution of the targets"))
cells.append(code("""fig, axes = plt.subplots(1, 2, figsize=(15, 4.5))
crop[CROP_TARGET].value_counts().sort_index().plot(kind="bar", color=sns.color_palette("viridis", 22), ax=axes[0])
axes[0].set_title("Crop classes (22 x 100 samples)"); axes[0].set_ylabel("Count")
fert[FERT_TARGET].value_counts().sort_index().plot(kind="bar", color=sns.color_palette("viridis", 7), ax=axes[1])
axes[1].set_title("Fertilizer classes (about 14.3% each)"); axes[1].set_ylabel("Count")
plt.tight_layout()
plt.show()
print("Chance-level accuracy: crop = %.2f%%, fertilizer = %.2f%%" % (100 / crop[CROP_TARGET].nunique(), 100 / fert[FERT_TARGET].nunique()))"""))

cells.append(md("## 4. Statistical summary and correlation heatmap"))
cells.append(code("crop.describe().round(2)"))
cells.append(code("""fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
sns.heatmap(crop.select_dtypes(include="number").corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0, square=True, ax=axes[0])
axes[0].set_title("Correlation of crop features")
sns.heatmap(fert.select_dtypes(include="number").corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0, square=True, ax=axes[1])
axes[1].set_title("Correlation of fertilizer features")
plt.tight_layout()
plt.show()"""))

cells.append(md("## 5. Boxplots: crop features by crop, fertilizer nutrients by fertilizer"))
cells.append(code("""fig, axes = plt.subplots(2, 2, figsize=(15, 9))
order = crop.groupby(CROP_TARGET)["rainfall"].median().sort_values().index
sns.boxplot(data=crop, x=CROP_TARGET, y="rainfall", order=order, ax=axes[0, 0], color="#4c72b0")
axes[0, 0].set_title("Rainfall by crop"); axes[0, 0].tick_params(axis="x", rotation=90)
sns.boxplot(data=crop, x=CROP_TARGET, y="ph", order=order, ax=axes[0, 1], color="#55a868")
axes[0, 1].set_title("Soil pH by crop"); axes[0, 1].tick_params(axis="x", rotation=90)
sns.boxplot(data=fert, x=FERT_TARGET, y="Nitrogen", ax=axes[1, 0], color="#c44e52")
axes[1, 0].set_title("Nitrogen by fertilizer (no visible difference)")
sns.boxplot(data=fert, x=FERT_TARGET, y="Potassium", ax=axes[1, 1], color="#8172b2")
axes[1, 1].set_title("Potassium by fertilizer (no visible difference)")
plt.tight_layout()
plt.show()"""))

cells.append(md("## 6. Scatter plots"))
cells.append(code("""top = ["rice", "jute", "chickpea", "apple", "coffee"]
sub = crop[crop[CROP_TARGET].isin(top)]
fig, axes = plt.subplots(1, 3, figsize=(17, 5))
sns.scatterplot(data=sub, x="rainfall", y="humidity", hue=CROP_TARGET, ax=axes[0], s=25)
axes[0].set_title("Crop: rainfall vs humidity (5 crops)")
sns.scatterplot(data=sub, x="K", y="P", hue=CROP_TARGET, ax=axes[1], s=25)
axes[1].set_title("Crop: potassium vs phosphorus (5 crops)")
samp = fert.sample(2000, random_state=42)
sns.scatterplot(data=samp, x="Nitrogen", y="Phosphorous", hue=FERT_TARGET, ax=axes[2], s=12, alpha=0.6)
axes[2].set_title("Fertilizer: N vs P (classes fully mixed)")
plt.tight_layout()
plt.show()"""))

cells.append(md("## 7. Feature importance (Random Forest)"))
cells.append(code("""from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

Xc, yc = crop.drop(columns=CROP_TARGET), crop[CROP_TARGET]
Xtr, Xte, ytr, yte = train_test_split(Xc, yc, test_size=0.2, stratify=yc, random_state=42)
rf = RandomForestClassifier(n_estimators=100, random_state=42).fit(Xtr, ytr)
print("Crop - Random Forest hold-out accuracy: %.2f%%" % (100 * rf.score(Xte, yte)))

imp = pd.Series(rf.feature_importances_, index=Xc.columns).sort_values()
imp.plot(kind="barh", color="#2f7d4f", figsize=(8, 4))
plt.title("Random Forest feature importance (crop)")
plt.xlabel("Importance")
plt.tight_layout()
plt.show()
imp.sort_values(ascending=False).round(4)"""))

cells.append(md("## 8. Model comparison and the fertilizer data audit"))
cells.append(code("""from scipy import stats
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

models = {"Random Forest": RandomForestClassifier(100, random_state=42), "Decision Tree": DecisionTreeClassifier(random_state=42),
          "KNN (k=5)": KNeighborsClassifier(5)}
fs = fert.sample(20000, random_state=42)
Xf = pd.get_dummies(fs.drop(columns=FERT_TARGET)).astype(float)
yf = fs[FERT_TARGET]
rows = []
for n, m in models.items():
    c = cross_val_score(make_pipeline(StandardScaler(), m), Xc, yc, cv=5).mean() * 100
    f = cross_val_score(make_pipeline(StandardScaler(), m), Xf, yf, cv=3).mean() * 100
    rows.append((n, round(c, 2), round(f, 2)))
res = pd.DataFrame(rows, columns=["Model", "Crop CV accuracy (%)", "Fertilizer CV accuracy (%)"]).set_index("Model")
print(res)

ax = res.plot(kind="bar", figsize=(8, 4), color=["#2f7d4f", "#c44e52"], rot=0)
ax.axhline(100 / 7, color="gray", ls="--", label="fertilizer chance (14.3%)")
ax.set_ylabel("Accuracy (%)"); ax.set_title("Cross-validated accuracy: crop vs fertilizer"); ax.legend(loc="center right")
plt.tight_layout(); plt.show()

print("\\nOne-way ANOVA of each nutrient across the 7 fertilizers (p > 0.05 means no difference):")
for col in ["Temperature", "Humidity", "Moisture", "Nitrogen", "Phosphorous", "Potassium"]:
    p = stats.f_oneway(*[g[col].values for _, g in fert.groupby(FERT_TARGET)]).pvalue
    print(f"  {col:12s} p = {p:.4f}")"""))

cells.append(md("""**Finding.** The crop data is clean and separable (about 99% accuracy). On the fertilizer data every model scores at chance (about 14%) and no feature differs between fertilizers, so the labels carry no learnable signal. The web application reports this with a reliability warning."""))

cells.append(md("## 9. Application demo (screenshots of the running web application)"))
for name, cap in (("crop", "Crop Predictor"), ("fertilizer", "Fertilizer Advisor (with reliability warning)"), ("satellite", "Satellite and Climate"),
                  ("report", "Soil Health and Farm Advisory Report"), ("dataset", "Dataset Explorer")):
    cells.append(md(f"**{cap}**"))
    cells.append(code(f"""from IPython.display import Image, display
display(Image(filename=str(ROOT / "report" / "figures" / "ui_{name}.png"), width=900))"""))

nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}})
os.makedirs("notebooks", exist_ok=True)
NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": "notebooks"}}).execute()
nbf.write(nb, "notebooks/Project_Demo_EDA.ipynb")
print("notebook executed and saved")

# ---- print-style PDF (like the Colab printout) ----
html, _ = HTMLExporter(template_name="classic").from_notebook_node(nb)
html = html.replace("</head>", "<style>@page{size:A4;margin:12mm} body{font-size:11px} div.input_area{border:1px solid #ccc} "
                    "div.output_area img{max-width:100%} .prompt{display:none}</style></head>", 1)
open("notebooks/Project_Demo_EDA.html", "w", encoding="utf-8").write(html)
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    pg = b.new_page(); pg.goto("file:///" + os.path.abspath("notebooks/Project_Demo_EDA.html").replace("\\", "/"))
    pg.wait_for_timeout(1500)
    pg.pdf(path="Project_Demo.pdf", format="A4", print_background=True, margin={"top": "12mm", "bottom": "12mm", "left": "10mm", "right": "10mm"})
    b.close()
print("saved Project_Demo.pdf")
