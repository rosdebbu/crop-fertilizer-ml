"""Draws the three diagrams used in the project report -> report/figures/"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({"font.family": "serif", "font.size": 10})
OUT = "report/figures"
G, L, A = "#2f5d50", "#e6efdf", "#e0a526"

def box(ax, x, y, w, h, text, fc=L, tc="black", fs=9, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06", fc=fc, ec=G, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=tc, fontsize=fs, fontweight="bold" if bold else "normal", wrap=True)

def arrow(ax, x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12, color=G, lw=1.3))

# 1. System architecture
fig, ax = plt.subplots(figsize=(8, 4.2)); ax.set_xlim(0, 10); ax.set_ylim(0, 5.2); ax.axis("off")
box(ax, 0.2, 3.6, 2.2, 1.0, "Kaggle datasets\n(Crop, Fertilizer CSV)", fc=L)
box(ax, 3.0, 3.6, 2.2, 1.0, "Training module\nscikit-learn", fc=L)
box(ax, 5.8, 3.6, 2.0, 1.0, "Model cache\n(joblib)", fc=L)
box(ax, 8.2, 3.6, 1.6, 1.0, "Saved\nmodels", fc=L)
box(ax, 1.4, 1.9, 7.2, 1.0, "FastAPI REST backend\n(Pydantic validation, Uvicorn server)", fc=G, tc="white", bold=True)
box(ax, 0.2, 0.1, 9.6, 1.2, "Web interface (HTML / JavaScript / Leaflet)\nCrop Predictor | Fertilizer Advisor | Satellite & Climate\nSoil Health Report | Dataset Explorer", fc=A, fs=9)
arrow(ax, 2.4, 4.1, 3.0, 4.1); arrow(ax, 5.2, 4.1, 5.8, 4.1); arrow(ax, 7.8, 4.1, 8.2, 4.1)
arrow(ax, 6.8, 3.6, 6.2, 2.9); arrow(ax, 4.7, 1.9, 4.7, 1.3); arrow(ax, 5.3, 1.3, 5.3, 1.9)
fig.tight_layout(); fig.savefig(f"{OUT}/diag_architecture.png", dpi=250); plt.close(fig)

# 2. ML pipeline
fig, ax = plt.subplots(figsize=(8, 2.6)); ax.set_xlim(0, 12); ax.set_ylim(0, 3); ax.axis("off")
steps = ["Load CSV\n(pandas)", "Encode\ncategories", "Stratified\n80/20 split", "Scale\n(fit on train)", "Train RF, DT,\nKNN", "Evaluate\nmetrics + CV"]
for i, s in enumerate(steps):
    x = 0.15 + i * 1.95
    box(ax, x, 0.9, 1.65, 1.2, s, fc=G if i in (3,) else L, tc="white" if i == 3 else "black", fs=8.5)
    ax.text(x + 0.82, 2.35, str(i + 1), ha="center", fontsize=10, fontweight="bold", color=G)
    if i < 5: arrow(ax, x + 1.65, 1.5, x + 1.95, 1.5)
fig.tight_layout(); fig.savefig(f"{OUT}/diag_pipeline.png", dpi=250); plt.close(fig)

# 3. Random forest voting
fig, ax = plt.subplots(figsize=(7, 3.4)); ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
box(ax, 0.2, 2.0, 1.8, 1.0, "Input\nN, P, K, T, H,\npH, rainfall", fc=A, fs=8)
for i, (lab, y) in enumerate([("Tree 1\nRice", 3.9), ("Tree 2\nRice", 2.5), ("Tree 3\nJute", 1.1), ("Tree 100\nRice", -0.3)]):
    if y < 0: y = 0.05
    box(ax, 3.2, y, 1.7, 0.9, lab, fc=L, fs=8)
    arrow(ax, 2.0, 2.5, 3.2, y + 0.45); arrow(ax, 4.9, y + 0.45, 6.2, 2.5)
ax.text(4.05, 1.0, "...", fontsize=14, ha="center")
box(ax, 6.2, 2.0, 1.7, 1.0, "Majority\nvote", fc=G, tc="white", fs=9, bold=True)
arrow(ax, 7.9, 2.5, 8.4, 2.5); box(ax, 8.4, 2.0, 1.4, 1.0, "Rice", fc=A, bold=True)
fig.tight_layout(); fig.savefig(f"{OUT}/diag_random_forest.png", dpi=250); plt.close(fig)
print("ok")
