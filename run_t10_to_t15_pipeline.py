import os
import sys
import io
import json
import base64
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import (
    silhouette_score, silhouette_samples,
    davies_bouldin_score, calinski_harabasz_score,
    adjusted_rand_score, normalized_mutual_info_score,
    homogeneity_score, completeness_score, v_measure_score,
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from scipy.cluster.hierarchy import dendrogram, linkage

# Setup paths and styling
OUT_DIR = "output_t10_t15"
os.makedirs(OUT_DIR, exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['figure.autolayout'] = True

print("=== STARTING T10-T15 PIPELINE EXECUTION ===")

# -------------------------------------------------------------
# 1. LOAD AND PREPARE DATASET
# -------------------------------------------------------------
df = pd.read_csv("data/Crop_recommendation.csv")
print(f"[DATASET] Loaded Crop_recommendation.csv with shape {df.shape}")
feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
X_raw = df[feature_cols].values
y_raw = df['label'].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_raw)

le = LabelEncoder()
y_encoded = le.fit_transform(y_raw)
classes = le.classes_

# PCA for 2D visual projections
pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_scaled)
print(f"[PCA] Explained Variance Ratio: {pca.explained_variance_ratio_} (Total: {sum(pca.explained_variance_ratio_):.2%})")

results = {}

# -------------------------------------------------------------
# T10: HIERARCHICAL CLUSTERING
# -------------------------------------------------------------
print("\n--- Running T10: Hierarchical Clustering ---")
linkage_matrix = linkage(X_scaled, method='ward')

plt.figure(figsize=(10, 5), dpi=300)
dendrogram(linkage_matrix, truncate_mode='lastp', p=25, leaf_rotation=45, leaf_font_size=9, show_contracted=True)
plt.title("T10: Hierarchical Agglomerative Dendrogram (Ward Linkage)", fontsize=13, fontweight='bold', pad=12)
plt.xlabel("Cluster Samples / Index", fontsize=11)
plt.ylabel("Ward Euclidean Distance Threshold", fontsize=11)
plt.axhline(y=15, color='crimson', linestyle='--', linewidth=1.8, label='Optimal Cut Threshold (y=15, k=4)')
plt.legend(loc='upper right')
plt.tight_layout()
t10_dendro_path = os.path.join(OUT_DIR, "t10_dendrogram.png")
plt.savefig(t10_dendro_path, dpi=300)
plt.close()

# Fit Agglomerative with k=4
k_hier = 4
agg_model = AgglomerativeClustering(n_clusters=k_hier, linkage='ward')
agg_labels = agg_model.fit_predict(X_scaled)

plt.figure(figsize=(8, 6), dpi=300)
palette = sns.color_palette("deep", k_hier)
for c in range(k_hier):
    idx = (agg_labels == c)
    plt.scatter(X_pca[idx, 0], X_pca[idx, 1], label=f"Cluster {c+1} (n={idx.sum()})", color=palette[c], alpha=0.8, s=60, edgecolors='k', linewidth=0.5)
plt.title(f"T10: Hierarchical Clustering (k={k_hier}) in PCA Space", fontsize=13, fontweight='bold', pad=12)
plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)", fontsize=11)
plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)", fontsize=11)
plt.legend(loc='best', frameon=True)
plt.tight_layout()
t10_pca_path = os.path.join(OUT_DIR, "t10_clusters_pca.png")
plt.savefig(t10_pca_path, dpi=300)
plt.close()

df_t10_profile = pd.DataFrame(X_raw, columns=feature_cols)
df_t10_profile['Cluster'] = agg_labels + 1
t10_profile_summary = df_t10_profile.groupby('Cluster').mean().round(2)
print("[T10] Cluster Mean Profiles:")
print(t10_profile_summary)
t10_sil = silhouette_score(X_scaled, agg_labels)
print(f"[T10] Silhouette Score: {t10_sil:.4f}")

# -------------------------------------------------------------
# T11: K-MEANS CLUSTERING
# -------------------------------------------------------------
print("\n--- Running T11: K-Means Clustering ---")
k_range = range(1, 11)
inertias = []
for k in k_range:
    km = KMeans(n_clusters=k, init='k-means++', n_init=10, random_state=42)
    km.fit(X_scaled)
    inertias.append(km.inertia_)

plt.figure(figsize=(8, 5), dpi=300)
plt.plot(list(k_range), inertias, marker='o', color='#1f77b4', linewidth=2.5, markersize=8)
plt.title("T11: K-Means Elbow Curve (Inertia vs Number of Clusters)", fontsize=13, fontweight='bold', pad=12)
plt.xlabel("Number of Clusters (k)", fontsize=11)
plt.ylabel("WCSS / Inertia", fontsize=11)
plt.xticks(list(k_range))
plt.axvline(x=4, color='crimson', linestyle='--', linewidth=1.5, label='Elbow Point (k=4)')
plt.annotate('Elbow Inflection (k=4)', xy=(4, inertias[3]), xytext=(5.2, inertias[3] + 150),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=7),
             fontweight='bold', fontsize=10)
plt.legend(loc='upper right')
plt.tight_layout()
t11_elbow_path = os.path.join(OUT_DIR, "t11_elbow_curve.png")
plt.savefig(t11_elbow_path, dpi=300)
plt.close()

# Fit K-Means with k=4
k_kmeans = 4
kmeans_model = KMeans(n_clusters=k_kmeans, init='k-means++', n_init=10, random_state=42)
kmeans_labels = kmeans_model.fit_predict(X_scaled)
kmeans_centers_scaled = kmeans_model.cluster_centers_
kmeans_centers_pca = pca.transform(kmeans_centers_scaled)

plt.figure(figsize=(8, 6), dpi=300)
palette = sns.color_palette("Set2", k_kmeans)
for c in range(k_kmeans):
    idx = (kmeans_labels == c)
    plt.scatter(X_pca[idx, 0], X_pca[idx, 1], label=f"Cluster {c+1} (n={idx.sum()})", color=palette[c], alpha=0.8, s=60, edgecolors='k', linewidth=0.5)
plt.scatter(kmeans_centers_pca[:, 0], kmeans_centers_pca[:, 1], s=250, c='red', marker='X', edgecolor='black', linewidth=1.5, label='Centroids', zorder=10)
plt.title(f"T11: K-Means Clusters & Centroids in PCA Space (k={k_kmeans})", fontsize=13, fontweight='bold', pad=12)
plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)", fontsize=11)
plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)", fontsize=11)
plt.legend(loc='best', frameon=True)
plt.tight_layout()
t11_kmeans_pca_path = os.path.join(OUT_DIR, "t11_kmeans_pca.png")
plt.savefig(t11_kmeans_pca_path, dpi=300)
plt.close()

kmeans_centers_orig = scaler.inverse_transform(kmeans_centers_scaled)
df_t11_centers = pd.DataFrame(kmeans_centers_orig, columns=feature_cols, index=[f"Cluster {i+1}" for i in range(k_kmeans)]).round(2)
print("[T11] K-Means Cluster Centroids (Original Feature Scale):")
print(df_t11_centers)
t11_sil = silhouette_score(X_scaled, kmeans_labels)
print(f"[T11] Silhouette Score: {t11_sil:.4f}, Inertia: {kmeans_model.inertia_:.2f}")

# -------------------------------------------------------------
# T12: CLUSTER EVALUATION
# -------------------------------------------------------------
print("\n--- Running T12: Cluster Evaluation ---")
k_eval_range = range(2, 9)
sil_scores = []
db_scores = []
ch_scores = []

for k in k_eval_range:
    km = KMeans(n_clusters=k, init='k-means++', n_init=10, random_state=42)
    lbls = km.fit_predict(X_scaled)
    sil_scores.append(silhouette_score(X_scaled, lbls))
    db_scores.append(davies_bouldin_score(X_scaled, lbls))
    ch_scores.append(calinski_harabasz_score(X_scaled, lbls))

# Multi-panel plot for internal evaluation
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4.5), dpi=300)
ax1.plot(list(k_eval_range), sil_scores, 'bo-', linewidth=2, markersize=7)
ax1.set_title("Silhouette Score (Higher is Better)", fontweight='bold')
ax1.set_xlabel("Number of Clusters (k)")
ax1.set_ylabel("Silhouette Score")
ax1.axvline(x=4, color='crimson', linestyle='--')

ax2.plot(list(k_eval_range), db_scores, 'rs-', linewidth=2, markersize=7)
ax2.set_title("Davies-Bouldin Index (Lower is Better)", fontweight='bold')
ax2.set_xlabel("Number of Clusters (k)")
ax2.set_ylabel("Davies-Bouldin Index")
ax2.axvline(x=4, color='crimson', linestyle='--')

ax3.plot(list(k_eval_range), ch_scores, 'g^-', linewidth=2, markersize=7)
ax3.set_title("Calinski-Harabasz Index (Higher is Better)", fontweight='bold')
ax3.set_xlabel("Number of Clusters (k)")
ax3.set_ylabel("Variance Ratio (CH Index)")
ax3.axvline(x=4, color='crimson', linestyle='--')

plt.suptitle("T12: Multi-Metric Internal Cluster Validation", fontsize=14, fontweight='bold', y=1.03)
plt.tight_layout()
t12_metrics_path = os.path.join(OUT_DIR, "t12_evaluation_metrics.png")
plt.savefig(t12_metrics_path, dpi=300)
plt.close()

# Detailed Silhouette Sample Analysis for k=4
fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
sample_silhouette_values = silhouette_samples(X_scaled, kmeans_labels)
y_lower = 10
for i in range(k_kmeans):
    ith_cluster_silhouette_values = sample_silhouette_values[kmeans_labels == i]
    ith_cluster_silhouette_values.sort()
    size_cluster_i = ith_cluster_silhouette_values.shape[0]
    y_upper = y_lower + size_cluster_i
    color = palette[i]
    ax.fill_betweenx(np.arange(y_lower, y_upper), 0, ith_cluster_silhouette_values, facecolor=color, edgecolor=color, alpha=0.7)
    ax.text(-0.05, y_lower + 0.5 * size_cluster_i, f"Cluster {i+1}", fontsize=10, fontweight='bold')
    y_lower = y_upper + 10

ax.set_title("T12: Silhouette Plot for K-Means (k=4)", fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel("Silhouette Coefficient Values", fontsize=11)
ax.set_ylabel("Cluster Label & Distribution", fontsize=11)
ax.axvline(x=t11_sil, color="red", linestyle="--", linewidth=1.5, label=f"Average Silhouette ({t11_sil:.3f})")
ax.set_yticks([])
ax.legend(loc='lower left')
plt.tight_layout()
t12_sil_samples_path = os.path.join(OUT_DIR, "t12_silhouette_samples.png")
plt.savefig(t12_sil_samples_path, dpi=300)
plt.close()

# External Validation (ARI, NMI, Homogeneity, Completeness, V-measure)
eval_dict = {
    'Metric': [
        'Silhouette Score (Internal)',
        'Davies-Bouldin Index (Internal)',
        'Calinski-Harabasz Index (Internal)',
        'Adjusted Rand Index - ARI (External)',
        'Normalized Mutual Information - NMI (External)',
        'Homogeneity Score (External)',
        'Completeness Score (External)',
        'V-Measure Score (External)'
    ],
    'K-Means (k=4)': [
        round(silhouette_score(X_scaled, kmeans_labels), 4),
        round(davies_bouldin_score(X_scaled, kmeans_labels), 4),
        round(calinski_harabasz_score(X_scaled, kmeans_labels), 2),
        round(adjusted_rand_score(y_encoded, kmeans_labels), 4),
        round(normalized_mutual_info_score(y_encoded, kmeans_labels), 4),
        round(homogeneity_score(y_encoded, kmeans_labels), 4),
        round(completeness_score(y_encoded, kmeans_labels), 4),
        round(v_measure_score(y_encoded, kmeans_labels), 4)
    ],
    'Hierarchical (k=4)': [
        round(silhouette_score(X_scaled, agg_labels), 4),
        round(davies_bouldin_score(X_scaled, agg_labels), 4),
        round(calinski_harabasz_score(X_scaled, agg_labels), 2),
        round(adjusted_rand_score(y_encoded, agg_labels), 4),
        round(normalized_mutual_info_score(y_encoded, agg_labels), 4),
        round(homogeneity_score(y_encoded, agg_labels), 4),
        round(completeness_score(y_encoded, agg_labels), 4),
        round(v_measure_score(y_encoded, agg_labels), 4)
    ]
}
df_eval = pd.DataFrame(eval_dict)
print("[T12] Comprehensive Cluster Evaluation Table:")
print(df_eval)

# -------------------------------------------------------------
# T13: DECISION TREE ALGORITHM
# -------------------------------------------------------------
print("\n--- Running T13: Decision Tree Algorithm ---")
X_train, X_test, y_train, y_test = train_test_split(
    X_raw, y_encoded, test_size=0.20, random_state=42, stratify=y_encoded
)
print(f"[SPLIT] Train Shape: {X_train.shape}, Test Shape: {X_test.shape}")

# Hyperparameter search: Max Depth vs Accuracy
depth_range = range(1, 11)
train_accs = []
test_accs = []
for d in depth_range:
    dt_temp = DecisionTreeClassifier(max_depth=d, criterion='gini', random_state=42)
    dt_temp.fit(X_train, y_train)
    train_accs.append(dt_temp.score(X_train, y_train))
    test_accs.append(dt_temp.score(X_test, y_test))

plt.figure(figsize=(8, 5), dpi=300)
plt.plot(list(depth_range), train_accs, 'o-', label="Training Accuracy", color='#2ca02c', linewidth=2)
plt.plot(list(depth_range), test_accs, 's--', label="Testing Accuracy", color='#1f77b4', linewidth=2)
plt.title("T13: Decision Tree Max Depth vs Accuracy (Bias-Variance Tradeoff)", fontsize=13, fontweight='bold', pad=12)
plt.xlabel("Max Tree Depth", fontsize=11)
plt.ylabel("Accuracy Score", fontsize=11)
plt.xticks(list(depth_range))
plt.axvline(x=5, color='crimson', linestyle=':', label='Chosen Depth (d=5)')
plt.legend(loc='lower right')
plt.tight_layout()
t13_depth_path = os.path.join(OUT_DIR, "t13_depth_vs_accuracy.png")
plt.savefig(t13_depth_path, dpi=300)
plt.close()

# Fit optimal Decision Tree
dt_model = DecisionTreeClassifier(max_depth=5, criterion='gini', random_state=42)
dt_model.fit(X_train, y_train)
y_pred_dt = dt_model.predict(X_test)
dt_train_acc = dt_model.score(X_train, y_train)
dt_test_acc = accuracy_score(y_test, y_pred_dt)
dt_report = classification_report(y_test, y_pred_dt, target_names=classes, output_dict=False)
dt_report_dict = classification_report(y_test, y_pred_dt, target_names=classes, output_dict=True)
print(f"[T13] Decision Tree Train Accuracy: {dt_train_acc:.4f}, Test Accuracy: {dt_test_acc:.4f}")
print("[T13] Classification Report:\n", dt_report)

# Confusion Matrix Heatmap
plt.figure(figsize=(8, 6.5), dpi=300)
cm_dt = confusion_matrix(y_test, y_pred_dt)
sns.heatmap(cm_dt, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes, cbar=False)
plt.title(f"T13: Decision Tree Confusion Matrix (Accuracy: {dt_test_acc:.1%})", fontsize=13, fontweight='bold', pad=12)
plt.xlabel("Predicted Crop Label", fontsize=11)
plt.ylabel("True Crop Label", fontsize=11)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
t13_cm_path = os.path.join(OUT_DIR, "t13_confusion_matrix.png")
plt.savefig(t13_cm_path, dpi=300)
plt.close()

# Feature Importance
plt.figure(figsize=(8, 4.5), dpi=300)
dt_fi = pd.Series(dt_model.feature_importances_, index=feature_cols).sort_values(ascending=True)
colors = sns.color_palette("viridis", len(dt_fi))
dt_fi.plot(kind='barh', color=colors, edgecolor='black', linewidth=0.5)
plt.title("T13: Decision Tree Feature Importances (Gini Impurity Reduction)", fontsize=13, fontweight='bold', pad=12)
plt.xlabel("Relative Importance Score", fontsize=11)
plt.tight_layout()
t13_fi_path = os.path.join(OUT_DIR, "t13_feature_importance.png")
plt.savefig(t13_fi_path, dpi=300)
plt.close()

# Visual Tree Plot
plt.figure(figsize=(18, 10), dpi=300)
plot_tree(dt_model, feature_names=feature_cols, class_names=classes, filled=True, rounded=True, fontsize=8)
plt.title("T13: Full Decision Tree Architecture (max_depth=5)", fontsize=14, fontweight='bold', pad=12)
plt.tight_layout()
t13_tree_path = os.path.join(OUT_DIR, "t13_decision_tree_viz.png")
plt.savefig(t13_tree_path, dpi=300)
plt.close()

# -------------------------------------------------------------
# T14: RANDOM FOREST ALGORITHM
# -------------------------------------------------------------
print("\n--- Running T14: Random Forest Algorithm ---")
n_est_range = [10, 25, 50, 75, 100, 150, 200]
rf_oob_scores = []
rf_test_accs = []

for n in n_est_range:
    rf_temp = RandomForestClassifier(n_estimators=n, max_depth=8, oob_score=True, random_state=42)
    rf_temp.fit(X_train, y_train)
    rf_oob_scores.append(rf_temp.oob_score_)
    rf_test_accs.append(rf_temp.score(X_test, y_test))

plt.figure(figsize=(8, 5), dpi=300)
plt.plot(n_est_range, rf_test_accs, 'o-', color='#1f77b4', linewidth=2, label="Test Accuracy")
plt.plot(n_est_range, rf_oob_scores, 's--', color='#ff7f0e', linewidth=2, label="Out-of-Bag (OOB) Score")
plt.title("T14: Random Forest n_estimators vs Accuracy & OOB Score", fontsize=13, fontweight='bold', pad=12)
plt.xlabel("Number of Estimators (Trees)", fontsize=11)
plt.ylabel("Score", fontsize=11)
plt.axvline(x=100, color='crimson', linestyle=':', label='Chosen Trees (n=100)')
plt.legend(loc='lower right')
plt.tight_layout()
t14_trees_path = os.path.join(OUT_DIR, "t14_trees_vs_accuracy.png")
plt.savefig(t14_trees_path, dpi=300)
plt.close()

# Fit final Random Forest
rf_model = RandomForestClassifier(n_estimators=100, max_depth=8, oob_score=True, random_state=42)
rf_model.fit(X_train, y_train)
y_pred_rf = rf_model.predict(X_test)
rf_train_acc = rf_model.score(X_train, y_train)
rf_test_acc = accuracy_score(y_test, y_pred_rf)
rf_oob = rf_model.oob_score_
rf_report = classification_report(y_test, y_pred_rf, target_names=classes, output_dict=False)
rf_report_dict = classification_report(y_test, y_pred_rf, target_names=classes, output_dict=True)
print(f"[T14] Random Forest Train Accuracy: {rf_train_acc:.4f}, Test Accuracy: {rf_test_acc:.4f}, OOB Score: {rf_oob:.4f}")
print("[T14] Classification Report:\n", rf_report)

# Confusion Matrix Heatmap
plt.figure(figsize=(8, 6.5), dpi=300)
cm_rf = confusion_matrix(y_test, y_pred_rf)
sns.heatmap(cm_rf, annot=True, fmt='d', cmap='Greens', xticklabels=classes, yticklabels=classes, cbar=False)
plt.title(f"T14: Random Forest Confusion Matrix (Accuracy: {rf_test_acc:.1%})", fontsize=13, fontweight='bold', pad=12)
plt.xlabel("Predicted Crop Label", fontsize=11)
plt.ylabel("True Crop Label", fontsize=11)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
t14_cm_path = os.path.join(OUT_DIR, "t14_confusion_matrix.png")
plt.savefig(t14_cm_path, dpi=300)
plt.close()

# Side-by-side Feature Importance Comparison: Decision Tree vs Random Forest
df_fi_compare = pd.DataFrame({
    'Decision Tree': dt_model.feature_importances_,
    'Random Forest': rf_model.feature_importances_
}, index=feature_cols)

plt.figure(figsize=(9, 5), dpi=300)
df_fi_compare.plot(kind='bar', figsize=(9, 5), color=['#1f77b4', '#2ca02c'], edgecolor='black', linewidth=0.5)
plt.title("T14: Feature Importance Comparison (Decision Tree vs Random Forest)", fontsize=13, fontweight='bold', pad=12)
plt.xlabel("Agricultural Feature", fontsize=11)
plt.ylabel("MDI Feature Importance", fontsize=11)
plt.xticks(rotation=30, ha='right')
plt.legend(loc='upper right')
plt.tight_layout()
t14_fi_compare_path = os.path.join(OUT_DIR, "t14_rf_dt_feature_comparison.png")
plt.savefig(t14_fi_compare_path, dpi=300)
plt.close()

# -------------------------------------------------------------
# T15: ARTIFICIAL NEURAL NETWORKS (ANN - MLP)
# -------------------------------------------------------------
print("\n--- Running T15: Artificial Neural Networks (MLP) ---")
# Use scaled inputs for neural network optimization
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

mlp_model = MLPClassifier(
    hidden_layer_sizes=(64, 32),
    activation='relu',
    solver='adam',
    max_iter=500,
    random_state=42,
    early_stopping=False
)
mlp_model.fit(X_train_s, y_train)
y_pred_mlp = mlp_model.predict(X_test_s)
mlp_train_acc = mlp_model.score(X_train_s, y_train)
mlp_test_acc = accuracy_score(y_test, y_pred_mlp)
mlp_report = classification_report(y_test, y_pred_mlp, target_names=classes, output_dict=False)
mlp_report_dict = classification_report(y_test, y_pred_mlp, target_names=classes, output_dict=True)
print(f"[T15] MLP Train Accuracy: {mlp_train_acc:.4f}, Test Accuracy: {mlp_test_acc:.4f}, Epochs: {len(mlp_model.loss_curve_)}")
print("[T15] Classification Report:\n", mlp_report)

# Training Loss Curve
plt.figure(figsize=(8, 4.8), dpi=300)
plt.plot(mlp_model.loss_curve_, color='#d62728', linewidth=2.2, label="Cross-Entropy Loss")
plt.title("T15: Artificial Neural Network Training Loss Curve (Adam Optimizer)", fontsize=13, fontweight='bold', pad=12)
plt.xlabel("Iteration / Epoch", fontsize=11)
plt.ylabel("Loss Value", fontsize=11)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper right')
plt.tight_layout()
t15_loss_path = os.path.join(OUT_DIR, "t15_loss_curve.png")
plt.savefig(t15_loss_path, dpi=300)
plt.close()

# Confusion Matrix Heatmap
plt.figure(figsize=(8, 6.5), dpi=300)
cm_mlp = confusion_matrix(y_test, y_pred_mlp)
sns.heatmap(cm_mlp, annot=True, fmt='d', cmap='Oranges', xticklabels=classes, yticklabels=classes, cbar=False)
plt.title(f"T15: ANN (MLP) Confusion Matrix (Accuracy: {mlp_test_acc:.1%})", fontsize=13, fontweight='bold', pad=12)
plt.xlabel("Predicted Crop Label", fontsize=11)
plt.ylabel("True Crop Label", fontsize=11)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
t15_cm_path = os.path.join(OUT_DIR, "t15_confusion_matrix.png")
plt.savefig(t15_cm_path, dpi=300)
plt.close()

# Activation function comparison
act_funcs = ['relu', 'tanh', 'logistic']
act_accs = []
for act in act_funcs:
    m = MLPClassifier(hidden_layer_sizes=(64, 32), activation=act, solver='adam', max_iter=500, random_state=42)
    m.fit(X_train_s, y_train)
    act_accs.append(m.score(X_test_s, y_test))

plt.figure(figsize=(7, 4.5), dpi=300)
bars = plt.bar(act_funcs, act_accs, color=['#1f77b4', '#ff7f0e', '#2ca02c'], edgecolor='black', linewidth=0.5, width=0.5)
plt.title("T15: ANN Activation Function Performance Comparison", fontsize=13, fontweight='bold', pad=12)
plt.xlabel("Activation Function", fontsize=11)
plt.ylabel("Test Accuracy", fontsize=11)
plt.ylim(0, 1.05)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.02, f"{yval:.1%}", ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
t15_act_path = os.path.join(OUT_DIR, "t15_activations_comparison.png")
plt.savefig(t15_act_path, dpi=300)
plt.close()

# -------------------------------------------------------------
# MASTER MODEL COMPARISON (T13 vs T14 vs T15)
# -------------------------------------------------------------
print("\n--- Generating Master Classification Model Comparison ---")
comp_df = pd.DataFrame({
    'Model': ['Decision Tree (T13)', 'Random Forest (T14)', 'Artificial Neural Network (T15)'],
    'Train Accuracy': [f"{dt_train_acc:.2%}", f"{rf_train_acc:.2%}", f"{mlp_train_acc:.2%}"],
    'Test Accuracy': [f"{dt_test_acc:.2%}", f"{rf_test_acc:.2%}", f"{mlp_test_acc:.2%}"],
    'Macro Precision': [
        f"{precision_score(y_test, y_pred_dt, average='macro'):.2%}",
        f"{precision_score(y_test, y_pred_rf, average='macro'):.2%}",
        f"{precision_score(y_test, y_pred_mlp, average='macro'):.2%}"
    ],
    'Macro Recall': [
        f"{recall_score(y_test, y_pred_dt, average='macro'):.2%}",
        f"{recall_score(y_test, y_pred_rf, average='macro'):.2%}",
        f"{recall_score(y_test, y_pred_mlp, average='macro'):.2%}"
    ],
    'Macro F1-Score': [
        f"{f1_score(y_test, y_pred_dt, average='macro'):.2%}",
        f"{f1_score(y_test, y_pred_rf, average='macro'):.2%}",
        f"{f1_score(y_test, y_pred_mlp, average='macro'):.2%}"
    ]
})
print("[SUMMARY] Supervised Learning Benchmark Table:")
print(comp_df)

# Plot comparison bar chart
plt.figure(figsize=(9, 5), dpi=300)
x_pos = np.arange(3)
width = 0.25
acc_train_vals = [dt_train_acc, rf_train_acc, mlp_train_acc]
acc_test_vals = [dt_test_acc, rf_test_acc, mlp_test_acc]
f1_vals = [
    f1_score(y_test, y_pred_dt, average='macro'),
    f1_score(y_test, y_pred_rf, average='macro'),
    f1_score(y_test, y_pred_mlp, average='macro')
]

plt.bar(x_pos - width, acc_train_vals, width, label='Train Accuracy', color='#2ca02c')
plt.bar(x_pos, acc_test_vals, width, label='Test Accuracy', color='#1f77b4')
plt.bar(x_pos + width, f1_vals, width, label='Macro F1-Score', color='#ff7f0e')

plt.xlabel('Supervised Algorithm', fontsize=11, fontweight='bold')
plt.ylabel('Score (0 to 1)', fontsize=11, fontweight='bold')
plt.title('Benchmark Comparison: Decision Tree vs Random Forest vs ANN', fontsize=13, fontweight='bold', pad=12)
plt.xticks(x_pos, ['Decision Tree (T13)', 'Random Forest (T14)', 'Neural Network (T15)'])
plt.ylim(0, 1.15)
plt.legend(loc='upper right')
plt.tight_layout()
t15_comp_path = os.path.join(OUT_DIR, "t15_model_comparison.png")
plt.savefig(t15_comp_path, dpi=300)
plt.close()

# Save all quantitative outputs to a JSON cache for report building
cache_data = {
    't10': {
        'silhouette': float(t10_sil),
        'k': k_hier,
        'profile': t10_profile_summary.to_dict()
    },
    't11': {
        'silhouette': float(t11_sil),
        'inertia': float(kmeans_model.inertia_),
        'k': k_kmeans,
        'centroids': df_t11_centers.to_dict()
    },
    't12': {
        'eval_table': df_eval.to_dict(orient='records')
    },
    't13': {
        'train_acc': float(dt_train_acc),
        'test_acc': float(dt_test_acc),
        'report': dt_report,
        'top_feature': str(dt_fi.index[-1]),
        'top_importance': float(dt_fi.iloc[-1])
    },
    't14': {
        'train_acc': float(rf_train_acc),
        'test_acc': float(rf_test_acc),
        'oob_score': float(rf_oob),
        'report': rf_report
    },
    't15': {
        'train_acc': float(mlp_train_acc),
        'test_acc': float(mlp_test_acc),
        'epochs': len(mlp_model.loss_curve_),
        'final_loss': float(mlp_model.loss_curve_[-1]),
        'report': mlp_report
    },
    'summary': comp_df.to_dict(orient='records')
}

with open(os.path.join(OUT_DIR, "execution_metrics.json"), "w") as f:
    json.dump(cache_data, f, indent=2)

print("\n=== PIPELINE EXECUTION COMPLETED SUCCESSFULLY! ===")
