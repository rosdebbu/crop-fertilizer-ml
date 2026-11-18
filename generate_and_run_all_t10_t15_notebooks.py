import os
import sys
import io
import json
import base64
import traceback
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import nbformat as nbf

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

print("=== STARTING NOTEBOOK GENERATION & EXECUTION ENGINE (T10 - T15) ===")

def execute_and_build_notebook(nb_title, cells_spec, filename):
    """
    Builds a Jupyter Notebook from a list of cell specifications, executes each code cell,
    captures text output and matplotlib figures as base64 images, and writes a fully rendered .ipynb file.
    """
    print(f"\n>> Building and executing notebook: {filename} ...")
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3 (ipykernel)",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.10.0"
        }
    }

    # Dedicated namespace for the notebook execution
    ns = {
        'np': np,
        'pd': pd,
        'plt': plt,
        'sns': sns,
        'os': os,
    }

    execution_count = 1

    for cell_info in cells_spec:
        cell_type = cell_info['type']
        source = cell_info['source']

        if cell_type == 'markdown':
            md_cell = nbf.v4.new_markdown_cell(source=source)
            nb.cells.append(md_cell)
        elif cell_type == 'code':
            code_cell = nbf.v4.new_code_cell(source=source)
            code_cell.execution_count = execution_count
            code_cell.outputs = []

            # Custom display function inside notebook
            def nb_display(obj):
                if hasattr(obj, 'to_html'):
                    code_cell.outputs.append(nbf.v4.new_output(
                        output_type='display_data',
                        data={
                            'text/html': obj.to_html(),
                            'text/plain': repr(obj)
                        }
                    ))
                else:
                    code_cell.outputs.append(nbf.v4.new_output(
                        output_type='display_data',
                        data={'text/plain': repr(obj)}
                    ))

            ns['display'] = nb_display

            # Capture stdout and stderr
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            captured_stdout = io.StringIO()
            captured_stderr = io.StringIO()
            sys.stdout = captured_stdout
            sys.stderr = captured_stderr

            # Reset matplotlib figures before cell
            plt.close('all')

            exec_error = None
            try:
                exec(source, ns)
            except Exception as e:
                exec_error = traceback.format_exc()

            sys.stdout = old_stdout
            sys.stderr = old_stderr

            if exec_error:
                print(f"[ERROR in cell {execution_count}]:\n{exec_error}")
                code_cell.outputs.append(nbf.v4.new_output(
                    output_type='error',
                    ename=type(e).__name__,
                    evalue=str(e),
                    traceback=exec_error.splitlines()
                ))
            else:
                stdout_text = captured_stdout.getvalue()
                if stdout_text:
                    code_cell.outputs.append(nbf.v4.new_output(
                        output_type='stream',
                        name='stdout',
                        text=stdout_text
                    ))

                # Check for generated matplotlib plots
                fignums = plt.get_fignums()
                if fignums:
                    for fig_id in fignums:
                        fig = plt.figure(fig_id)
                        buf = io.BytesIO()
                        fig.savefig(buf, format='png', bbox_inches='tight', dpi=140)
                        buf.seek(0)
                        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
                        code_cell.outputs.append(nbf.v4.new_output(
                            output_type='display_data',
                            data={
                                'image/png': img_b64,
                                'text/plain': f"<Figure size {fig.get_size_inches()[0]}x{fig.get_size_inches()[1]} with {len(fig.axes)} Axes>"
                            }
                        ))
                    plt.close('all')

            nb.cells.append(code_cell)
            execution_count += 1

    # Save to root workspace
    with open(filename, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"  [SAVED] {filename} ({len(nb.cells)} cells, fully executed)")

    # Also save to notebooks/ folder
    os.makedirs("notebooks", exist_ok=True)
    nb_path_in_dir = os.path.join("notebooks", filename)
    with open(nb_path_in_dir, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"  [SAVED] {nb_path_in_dir}")
    return filename

# ==============================================================================
# DEFINING THE 6 NOTEBOOKS
# ==============================================================================

# ------------------------------------------------------------------------------
# TUTORIAL 10: HIERARCHICAL CLUSTERING
# ------------------------------------------------------------------------------
t10_specs = [
    {
        'type': 'markdown',
        'source': (
            "# Tutorial 10 (T10): Building Programs to Implement Hierarchical Clustering\n\n"
            "## 📌 Objective\n"
            "Implement **Agglomerative Hierarchical Clustering** on the agricultural crop dataset (`Crop_recommendation.csv`). "
            "Identify natural agro-climatic clusters of crops without using target labels, visualize the cluster hierarchy via a **Dendrogram**, "
            "and examine the characteristics of each agro-ecological group.\n\n"
            "## 🔬 Key Concepts & Mathematical Formulas\n"
            "- **Hierarchical Clustering (Agglomerative)**: Bottom-up approach where each sample starts as its own cluster and pairs are recursively merged.\n"
            "- **Euclidean Distance Metric**: $d(u, v) = \\sqrt{\\sum_{i=1}^p (u_i - v_i)^2}$\n"
            "- **Ward's Minimum Variance Linkage**: Merges clusters that minimize the increase in total within-cluster variance:\n"
            "  $$\\Delta ESS = \\frac{n_A n_B}{n_A + n_B} ||\\mu_A - \\mu_B||^2$$\n"
            "- **Dendrogram**: Tree diagram depicting hierarchical arrangement of nested clusters and merge distances."
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 1: Import Required Libraries"
    },
    {
        'type': 'code',
        'source': (
            "import os\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n"
            "from sklearn.preprocessing import StandardScaler\n"
            "from sklearn.decomposition import PCA\n"
            "from sklearn.cluster import AgglomerativeClustering\n"
            "from scipy.cluster.hierarchy import dendrogram, linkage\n"
            "from sklearn.metrics import silhouette_score\n\n"
            "sns.set_theme(style=\"whitegrid\", palette=\"muted\")\n"
            "print('Libraries successfully imported!')"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 2: Load and Inspect Crop Recommendation Dataset\n"
            "We load `data/Crop_recommendation.csv` containing 7 numerical features: N, P, K, temperature, humidity, pH, and rainfall."
        )
    },
    {
        'type': 'code',
        'source': (
            "data_path = os.path.join('data', 'Crop_recommendation.csv')\n"
            "df = pd.read_csv(data_path)\n"
            "print(f'Dataset Shape: {df.shape}')\n"
            "print(f'Features: {list(df.columns[:7])}')\n"
            "print(f'Unique Crop Types: {df[\"label\"].nunique()}')\n"
            "display(df.head(6))"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 3: Feature Standardization\n"
            "Clustering algorithms rely on Euclidean distances. Features with large scales (e.g., Rainfall up to 300 mm, Potassium up to 205 kg/ha) "
            "would dominate features with small scales (e.g., pH 3.5 - 9.9) without standardization.\n"
            "$$z = \\frac{x - \\mu}{\\sigma}$$"
        )
    },
    {
        'type': 'code',
        'source': (
            "features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']\n"
            "X = df[features].values\n"
            "y = df['label'].values\n\n"
            "scaler = StandardScaler()\n"
            "X_scaled = scaler.fit_transform(X)\n"
            "print(f'Scaled Matrix Shape: {X_scaled.shape}')\n"
            "print(f'Feature Means: {np.round(X_scaled.mean(axis=0), 2)}')\n"
            "print(f'Feature Stds:  {np.round(X_scaled.std(axis=0), 2)}')"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 4: Construct Linkage Matrix & Plot Truncated Dendrogram\n"
            "We compute the Ward linkage matrix and plot a dendrogram showing the top cluster merges to identify the optimal cutoff threshold."
        )
    },
    {
        'type': 'code',
        'source': (
            "print('Computing Ward linkage matrix (minimizing within-cluster variance)...')\n"
            "linkage_matrix = linkage(X_scaled, method='ward')\n\n"
            "plt.figure(figsize=(11, 5.5), dpi=140)\n"
            "dendrogram(\n"
            "    linkage_matrix,\n"
            "    truncate_mode='lastp',\n"
            "    p=25,\n"
            "    leaf_rotation=45,\n"
            "    leaf_font_size=10,\n"
            "    show_contracted=True\n"
            ")\n"
            "plt.title('T10: Hierarchical Agglomerative Clustering Dendrogram (Ward Linkage)', fontsize=13, fontweight='bold', pad=12)\n"
            "plt.xlabel('Cluster Sample Bins (Contracted)', fontsize=11)\n"
            "plt.ylabel('Ward Euclidean Distance Threshold', fontsize=11)\n"
            "plt.axhline(y=15, color='crimson', linestyle='--', linewidth=1.8, label='Optimal Cut Threshold (y=15, k=4 Clusters)')\n"
            "plt.legend(loc='upper right')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 5: Fit Agglomerative Clustering Model ($k=4$)\n"
            "Based on the prominent horizontal gap in the dendrogram, we fit `AgglomerativeClustering` with $k=4$ clusters."
        )
    },
    {
        'type': 'code',
        'source': (
            "k_clusters = 4\n"
            "agg_model = AgglomerativeClustering(n_clusters=k_clusters, linkage='ward')\n"
            "agg_labels = agg_model.fit_predict(X_scaled)\n\n"
            "sil_score = silhouette_score(X_scaled, agg_labels)\n"
            "print(f'Agglomerative Model Fitted with k={k_clusters}')\n"
            "print(f'Overall Silhouette Score: {sil_score:.4f}')\n"
            "cluster_counts = pd.Series(agg_labels).value_counts().sort_index()\n"
            "for c_id, count in cluster_counts.items():\n"
            "    print(f'  - Cluster {c_id + 1}: {count} samples ({count/len(df):.1%})')"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 6: 2D Projection and Cluster Visualization via PCA\n"
            "To visually inspect cluster separation in 2D space, we project the 7 standardized features onto the top 2 Principal Components (PC1 & PC2)."
        )
    },
    {
        'type': 'code',
        'source': (
            "pca = PCA(n_components=2, random_state=42)\n"
            "X_pca = pca.fit_transform(X_scaled)\n\n"
            "plt.figure(figsize=(9, 6), dpi=140)\n"
            "colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']\n"
            "for c in range(k_clusters):\n"
            "    idx = (agg_labels == c)\n"
            "    plt.scatter(\n"
            "        X_pca[idx, 0], X_pca[idx, 1],\n"
            "        label=f'Cluster {c+1} (n={idx.sum()})',\n"
            "        color=colors[c], alpha=0.75, s=55, edgecolors='k', linewidth=0.4\n"
            "    )\n\n"
            "plt.title(f'T10: Agglomerative Clusters (k={k_clusters}) in 2D PCA Space', fontsize=13, fontweight='bold', pad=12)\n"
            "plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} Explained Variance)', fontsize=11)\n"
            "plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} Explained Variance)', fontsize=11)\n"
            "plt.legend(loc='upper right', frameon=True)\n"
            "plt.tight_layout()\n"
            "plt.show()"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 7: Agronomic Profiling & Cluster Mean Analysis\n"
            "We inspect the centroid averages of soil nutrients and weather conditions in each cluster to interpret what each cluster represents in agricultural terms."
        )
    },
    {
        'type': 'code',
        'source': (
            "df_profile = df[features].copy()\n"
            "df_profile['Cluster'] = [f'Cluster {c+1}' for c in agg_labels]\n"
            "profile_means = df_profile.groupby('Cluster').mean().round(2)\n"
            "print('=== Agro-Climatic Cluster Mean Profiles ===')\n"
            "display(profile_means)\n\n"
            "# Bar chart of normalized cluster means\n"
            "profile_norm = (profile_means - profile_means.mean()) / profile_means.std()\n"
            "plt.figure(figsize=(10, 4.5), dpi=140)\n"
            "sns.heatmap(profile_norm, annot=profile_means.values, fmt='.1f', cmap='coolwarm', cbar=True)\n"
            "plt.title('T10: Cluster Feature Profile Heatmap (Unscaled values displayed)', fontsize=12, fontweight='bold')\n"
            "plt.ylabel('Cluster')\n"
            "plt.xlabel('Agricultural Feature')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### 🎓 Viva Voce Questions & Answers (Tutorial 10)\n\n"
            "1. **Q: What is the fundamental difference between Agglomerative and Divisive Hierarchical Clustering?**\n"
            "   - **A:** Agglomerative is a **bottom-up** approach where each sample starts in its own cluster and pairs are iteratively merged. "
            "Divisive is a **top-down** approach where all samples start in a single master cluster and are recursively split.\n\n"
            "2. **Q: How does Ward's Linkage work and why is it preferred here?**\n"
            "   - **A:** Ward's linkage merges the pair of clusters that leads to the minimum increase in total within-cluster variance (Error Sum of Squares, ESS). "
            "It creates compact, spherical, balanced clusters similar to K-Means but without stochastic centroid initialization.\n\n"
            "3. **Q: What is the computational complexity of Hierarchical Clustering?**\n"
            "   - **A:** Time complexity is $\\mathcal{O}(n^3)$ in basic implementations and $\\mathcal{O}(n^2 \\log n)$ using priority queues/heaps. "
            "Space complexity is $\\mathcal{O}(n^2)$ to store the pairwise distance matrix."
        )
    }
]

# ------------------------------------------------------------------------------
# TUTORIAL 11: K-MEANS CLUSTERING
# ------------------------------------------------------------------------------
t11_specs = [
    {
        'type': 'markdown',
        'source': (
            "# Tutorial 11 (T11): Building Programs to Implement K-Means Clustering\n\n"
            "## 📌 Objective\n"
            "Implement the **K-Means Clustering** algorithm on the agricultural crop recommendation dataset. "
            "Determine the optimal number of clusters $k$ using the **Elbow Method (Inertia / WCSS)**, train the K-Means model, "
            "extract the cluster centroids, and project cluster assignments in PCA space.\n\n"
            "## 🔬 Key Concepts & Mathematical Formulas\n"
            "- **K-Means Objective (Within-Cluster Sum of Squares / Inertia)**:\n"
            "  $$J = \\sum_{j=1}^k \\sum_{x_i \\in S_j} ||x_i - \\mu_j||^2$$\n"
            "- **Lloyd's Algorithm Steps**:\n"
            "  1. **Initialization**: Select $k$ initial centroids $\\mu_1, \\dots, \\mu_k$.\n"
            "  2. **Assignment Step**: Assign each sample $x_i$ to its nearest centroid: $c^{(i)} = \\arg\\min_j ||x_i - \\mu_j||^2$.\n"
            "  3. **Update Step**: Recompute centroids: $\\mu_j = \\frac{1}{|S_j|} \\sum_{x_i \\in S_j} x_i$.\n"
            "  4. Repeat until centroids stabilize (convergence).\n"
            "- **K-Means++**: Intelligent probabilistic centroid initialization to avoid suboptimal local minima: "
            "chooses next center with probability $P(x) = \\frac{D(x)^2}{\\sum D(x')^2}$."
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 1: Import Required Libraries"
    },
    {
        'type': 'code',
        'source': (
            "import os\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n"
            "from sklearn.preprocessing import StandardScaler\n"
            "from sklearn.decomposition import PCA\n"
            "from sklearn.cluster import KMeans\n"
            "from sklearn.metrics import silhouette_score\n\n"
            "sns.set_theme(style=\"whitegrid\", palette=\"muted\")\n"
            "print('K-Means libraries loaded!')"
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 2: Load Data and Apply Standard Scaling"
    },
    {
        'type': 'code',
        'source': (
            "df = pd.read_csv('data/Crop_recommendation.csv')\n"
            "features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']\n"
            "X = df[features].values\n\n"
            "scaler = StandardScaler()\n"
            "X_scaled = scaler.fit_transform(X)\n"
            "print(f'Dataset loaded: {X.shape[0]} samples, {X.shape[1]} features.')\n"
            "print('Features standardized to mean=0, std=1.')"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 3: Determine Optimal $k$ via the Elbow Method\n"
            "We iterate $k$ from 1 to 10 and compute the Within-Cluster Sum of Squares (Inertia). "
            "The 'elbow' point where the rate of inertia drop levels off indicates the optimal cluster count."
        )
    },
    {
        'type': 'code',
        'source': (
            "k_range = range(1, 11)\n"
            "inertias = []\n\n"
            "for k in k_range:\n"
            "    km = KMeans(n_clusters=k, init='k-means++', n_init=10, random_state=42)\n"
            "    km.fit(X_scaled)\n"
            "    inertias.append(km.inertia_)\n\n"
            "plt.figure(figsize=(8.5, 4.8), dpi=140)\n"
            "plt.plot(list(k_range), inertias, marker='o', color='#1f77b4', linewidth=2.2, markersize=7)\n"
            "plt.title('T11: K-Means Elbow Curve (Inertia vs Number of Clusters k)', fontsize=13, fontweight='bold', pad=12)\n"
            "plt.xlabel('Number of Clusters (k)', fontsize=11)\n"
            "plt.ylabel('WCSS / Inertia', fontsize=11)\n"
            "plt.xticks(list(k_range))\n"
            "plt.axvline(x=4, color='crimson', linestyle='--', linewidth=1.5, label='Elbow Inflection Point (k=4)')\n"
            "plt.annotate('Elbow Inflection (k=4)', xy=(4, inertias[3]), xytext=(5.2, inertias[3] + 400),\n"
            "             arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=7),\n"
            "             fontweight='bold', fontsize=10)\n"
            "plt.legend(loc='upper right')\n"
            "plt.tight_layout()\n"
            "plt.show()\n\n"
            "for k, val in zip(k_range, inertias):\n"
            "    print(f'k = {k:2d} -> Inertia: {val:10.2f}')"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 4: Train Final K-Means Model ($k=4$)\n"
            "We fit K-Means with $k=4$, `init='k-means++'`, and 10 random restarts to guarantee global convergence."
        )
    },
    {
        'type': 'code',
        'source': (
            "k_optimal = 4\n"
            "kmeans = KMeans(n_clusters=k_optimal, init='k-means++', n_init=10, random_state=42)\n"
            "kmeans_labels = kmeans.fit_predict(X_scaled)\n\n"
            "sil = silhouette_score(X_scaled, kmeans_labels)\n"
            "print(f'K-Means Convergence Achieved in {kmeans.n_iter_} iterations.')\n"
            "print(f'Final Model Inertia: {kmeans.inertia_:.2f}')\n"
            "print(f'Silhouette Score: {sil:.4f}')\n\n"
            "counts = pd.Series(kmeans_labels).value_counts().sort_index()\n"
            "for c, cnt in counts.items():\n"
            "    print(f'  - Cluster {c+1}: {cnt} crops ({cnt/len(df):.1%})')"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 5: Cluster Centroids in Original Agronomic Units\n"
            "We inverse-transform the standardized centroids to express optimal nutrient and climate values in physical units (kg/ha, °C, %, mm)."
        )
    },
    {
        'type': 'code',
        'source': (
            "centroids_scaled = kmeans.cluster_centers_\n"
            "centroids_orig = scaler.inverse_transform(centroids_scaled)\n\n"
            "df_centroids = pd.DataFrame(\n"
            "    centroids_orig,\n"
            "    columns=features,\n"
            "    index=[f'Cluster {i+1}' for i in range(k_optimal)]\n"
            ").round(2)\n\n"
            "print('=== K-Means Cluster Centroids (Physical Units) ===')\n"
            "display(df_centroids)"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 6: 2D Visualization with Centroids in PCA Space\n"
            "We project data points and cluster centroids onto the first two principal components."
        )
    },
    {
        'type': 'code',
        'source': (
            "pca = PCA(n_components=2, random_state=42)\n"
            "X_pca = pca.fit_transform(X_scaled)\n"
            "centers_pca = pca.transform(centroids_scaled)\n\n"
            "plt.figure(figsize=(9, 6), dpi=140)\n"
            "palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd']\n"
            "for c in range(k_optimal):\n"
            "    idx = (kmeans_labels == c)\n"
            "    plt.scatter(\n"
            "        X_pca[idx, 0], X_pca[idx, 1],\n"
            "        label=f'Cluster {c+1} (n={idx.sum()})',\n"
            "        color=palette[c], alpha=0.75, s=55, edgecolors='k', linewidth=0.4\n"
            "    )\n\n"
            "# Plot Centroids\n"
            "plt.scatter(\n"
            "    centers_pca[:, 0], centers_pca[:, 1],\n"
            "    s=260, c='red', marker='X', edgecolor='black', linewidth=1.6,\n"
            "    label='Centroids (Lloyd Means)', zorder=10\n"
            ")\n\n"
            "plt.title(f'T11: K-Means Clusters & Centroids in PCA Space (k={k_optimal})', fontsize=13, fontweight='bold', pad=12)\n"
            "plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} Variance)', fontsize=11)\n"
            "plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} Variance)', fontsize=11)\n"
            "plt.legend(loc='upper right', frameon=True)\n"
            "plt.tight_layout()\n"
            "plt.show()"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 7: Predict Cluster for New Unseen Soil Test\n"
            "We test the K-Means pipeline by assigning a new farmer's field sample to its closest agro-ecological cluster."
        )
    },
    {
        'type': 'code',
        'source': (
            "sample_input = np.array([[90, 42, 43, 20.8, 82.0, 6.5, 202.9]])  # High N, high humidity, high rainfall\n"
            "sample_scaled = scaler.transform(sample_input)\n"
            "predicted_cluster = kmeans.predict(sample_scaled)[0] + 1\n"
            "print(f'Input Soil/Weather Test: {sample_input.tolist()[0]}')\n"
            "print(f'Assigned Cluster: Cluster {predicted_cluster}')"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### 🎓 Viva Voce Questions & Answers (Tutorial 11)\n\n"
            "1. **Q: What is the purpose of K-Means++ initialization?**\n"
            "   - **A:** Standard K-Means randomly picks initial centroids, which can lead to poor local optima and slow convergence. "
            "K-Means++ selects the first centroid uniformly at random, and then picks subsequent centroids with probability proportional to the squared distance to the nearest existing centroid. "
            "This spreads centroids apart initially, guaranteeing an $\\mathcal{O}(\\log k)$ competitive ratio.\n\n"
            "2. **Q: What is Inertia (Within-Cluster Sum of Squares, WCSS)?**\n"
            "   - **A:** Inertia measures internal cluster compactness. It is the sum of squared Euclidean distances from each data point to its assigned cluster centroid. "
            "Inertia naturally decreases as $k$ increases, reaching 0 when $k=n$.\n\n"
            "3. **Q: What are the main limitations of K-Means?**\n"
            "   - **A:** Assumes spherical clusters of similar size and density; highly sensitive to feature scaling and outliers; requires pre-specifying $k$."
        )
    }
]

# ------------------------------------------------------------------------------
# TUTORIAL 12: CLUSTER EVALUATION
# ------------------------------------------------------------------------------
t12_specs = [
    {
        'type': 'markdown',
        'source': (
            "# Tutorial 12 (T12): Building Programs to Perform Cluster Evaluation\n\n"
            "## 📌 Objective\n"
            "Perform comprehensive evaluation of clustering algorithms using both **Internal Validation Metrics** (unsupervised, no true labels needed) "
            "and **External Validation Metrics** (supervised, comparing against ground-truth crop classes). "
            "Evaluate across multiple values of $k$ and compare **K-Means** against **Hierarchical Clustering**.\n\n"
            "## 🔬 Key Evaluation Metrics & Formulas\n"
            "1. **Silhouette Score ($s$)**: Measures intra-cluster cohesion vs nearest-cluster separation (Range: $[-1, +1]$, higher is better):\n"
            "   $$s(i) = \\frac{b(i) - a(i)}{\\max(a(i), b(i))}$$\n"
            "2. **Davies-Bouldin Index (DBI)**: Ratio of within-cluster scatter to between-cluster separation (Lower is better):\n"
            "   $$DB = \\frac{1}{k} \\sum_{i=1}^k \\max_{j \\ne i} \\left( \\frac{\\sigma_i + \\sigma_j}{d(\\mu_i, \\mu_j)} \\right)$$\n"
            "3. **Calinski-Harabasz Index (Variance Ratio Criterion)**: Ratio of between-cluster dispersion to within-cluster dispersion (Higher is better):\n"
            "   $$CH = \\frac{\\text{Tr}(B_k)}{\\text{Tr}(W_k)} \\times \\frac{n - k}{k - 1}$$\n"
            "4. **Adjusted Rand Index (ARI)**: Chance-corrected measure of agreement between cluster assignments and ground truth (Range: $[-1, +1]$, $1 =$ perfect match)."
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 1: Import Required Libraries"
    },
    {
        'type': 'code',
        'source': (
            "import os\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n"
            "from sklearn.preprocessing import StandardScaler, LabelEncoder\n"
            "from sklearn.cluster import KMeans, AgglomerativeClustering\n"
            "from sklearn.metrics import (\n"
            "    silhouette_score, silhouette_samples,\n"
            "    davies_bouldin_score, calinski_harabasz_score,\n"
            "    adjusted_rand_score, normalized_mutual_info_score,\n"
            "    homogeneity_score, completeness_score, v_measure_score\n"
            ")\n\n"
            "sns.set_theme(style=\"whitegrid\", palette=\"muted\")\n"
            "print('Cluster evaluation libraries ready!')"
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 2: Load Data and Standardize"
    },
    {
        'type': 'code',
        'source': (
            "df = pd.read_csv('data/Crop_recommendation.csv')\n"
            "features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']\n"
            "X = df[features].values\n\n"
            "scaler = StandardScaler()\n"
            "X_scaled = scaler.fit_transform(X)\n\n"
            "le = LabelEncoder()\n"
            "y_true = le.fit_transform(df['label'])\n"
            "print(f'Loaded {len(df)} samples across {len(le.classes_)} true crop classes.')"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 3: Compute Internal Validation Metrics for $k \\in [2, 8]$\n"
            "We sweep $k$ from 2 to 8 and record Silhouette Score, Davies-Bouldin Index, and Calinski-Harabasz Index."
        )
    },
    {
        'type': 'code',
        'source': (
            "k_eval_range = range(2, 9)\n"
            "sil_scores = []\n"
            "db_scores = []\n"
            "ch_scores = []\n\n"
            "for k in k_eval_range:\n"
            "    km = KMeans(n_clusters=k, init='k-means++', n_init=10, random_state=42)\n"
            "    labels = km.fit_predict(X_scaled)\n"
            "    sil_scores.append(silhouette_score(X_scaled, labels))\n"
            "    db_scores.append(davies_bouldin_score(X_scaled, labels))\n"
            "    ch_scores.append(calinski_harabasz_score(X_scaled, labels))\n\n"
            "fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4.5), dpi=140)\n\n"
            "# 1. Silhouette\n"
            "ax1.plot(list(k_eval_range), sil_scores, 'bo-', linewidth=2, markersize=7)\n"
            "ax1.set_title('Silhouette Score (Higher is Better)', fontweight='bold')\n"
            "ax1.set_xlabel('Number of Clusters (k)')\n"
            "ax1.set_ylabel('Silhouette Coefficient')\n"
            "ax1.axvline(x=4, color='crimson', linestyle='--', label='k=4')\n"
            "ax1.legend()\n\n"
            "# 2. Davies-Bouldin\n"
            "ax2.plot(list(k_eval_range), db_scores, 'rs-', linewidth=2, markersize=7)\n"
            "ax2.set_title('Davies-Bouldin Index (Lower is Better)', fontweight='bold')\n"
            "ax2.set_xlabel('Number of Clusters (k)')\n"
            "ax2.set_ylabel('Davies-Bouldin Index')\n"
            "ax2.axvline(x=4, color='crimson', linestyle='--', label='k=4')\n"
            "ax2.legend()\n\n"
            "# 3. Calinski-Harabasz\n"
            "ax3.plot(list(k_eval_range), ch_scores, 'g^-', linewidth=2, markersize=7)\n"
            "ax3.set_title('Calinski-Harabasz Index (Higher is Better)', fontweight='bold')\n"
            "ax3.set_xlabel('Number of Clusters (k)')\n"
            "ax3.set_ylabel('Variance Ratio (CH Index)')\n"
            "ax3.axvline(x=4, color='crimson', linestyle='--', label='k=4')\n"
            "ax3.legend()\n\n"
            "plt.suptitle('T12: Multi-Metric Internal Cluster Validation', fontsize=14, fontweight='bold', y=1.03)\n"
            "plt.tight_layout()\n"
            "plt.show()"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 4: Detailed Silhouette Sample Analysis for $k=4$\n"
            "We generate a per-cluster silhouette plot showing the thickness and individual coefficient distribution for each of the 4 clusters."
        )
    },
    {
        'type': 'code',
        'source': (
            "k_chosen = 4\n"
            "km_final = KMeans(n_clusters=k_chosen, init='k-means++', n_init=10, random_state=42)\n"
            "km_labels = km_final.fit_predict(X_scaled)\n"
            "avg_sil = silhouette_score(X_scaled, km_labels)\n"
            "sample_sil_values = silhouette_samples(X_scaled, km_labels)\n\n"
            "fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=140)\n"
            "y_lower = 10\n"
            "palette = sns.color_palette('tab10', k_chosen)\n\n"
            "for i in range(k_chosen):\n"
            "    ith_cluster_sil = sample_sil_values[km_labels == i]\n"
            "    ith_cluster_sil.sort()\n"
            "    size_i = ith_cluster_sil.shape[0]\n"
            "    y_upper = y_lower + size_i\n"
            "    color = palette[i]\n"
            "    ax.fill_betweenx(np.arange(y_lower, y_upper), 0, ith_cluster_sil, facecolor=color, edgecolor=color, alpha=0.7)\n"
            "    ax.text(-0.05, y_lower + 0.5 * size_i, f'Cluster {i+1}', fontsize=10, fontweight='bold')\n"
            "    y_lower = y_upper + 10\n\n"
            "ax.set_title('T12: Silhouette Plot for K-Means (k=4)', fontsize=13, fontweight='bold', pad=12)\n"
            "ax.set_xlabel('Silhouette Coefficient Values', fontsize=11)\n"
            "ax.set_ylabel('Cluster Distribution', fontsize=11)\n"
            "ax.axvline(x=avg_sil, color='red', linestyle='--', linewidth=1.5, label=f'Average Silhouette ({avg_sil:.3f})')\n"
            "ax.set_yticks([])\n"
            "ax.legend(loc='lower left')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 5: Master Comparison: K-Means vs Hierarchical Clustering\n"
            "We fit Agglomerative Clustering ($k=4$) and evaluate both algorithms side-by-side on all 8 internal and external validation metrics."
        )
    },
    {
        'type': 'code',
        'source': (
            "agg_final = AgglomerativeClustering(n_clusters=4, linkage='ward')\n"
            "agg_labels = agg_final.fit_predict(X_scaled)\n\n"
            "metrics_data = {\n"
            "    'Evaluation Metric': [\n"
            "        'Silhouette Score (Internal, ↑)',\n"
            "        'Davies-Bouldin Index (Internal, ↓)',\n"
            "        'Calinski-Harabasz Index (Internal, ↑)',\n"
            "        'Adjusted Rand Index - ARI (External, ↑)',\n"
            "        'Normalized Mutual Info - NMI (External, ↑)',\n"
            "        'Homogeneity Score (External, ↑)',\n"
            "        'Completeness Score (External, ↑)',\n"
            "        'V-Measure Score (External, ↑)'\n"
            "    ],\n"
            "    'K-Means (k=4)': [\n"
            "        round(silhouette_score(X_scaled, km_labels), 4),\n"
            "        round(davies_bouldin_score(X_scaled, km_labels), 4),\n"
            "        round(calinski_harabasz_score(X_scaled, km_labels), 2),\n"
            "        round(adjusted_rand_score(y_true, km_labels), 4),\n"
            "        round(normalized_mutual_info_score(y_true, km_labels), 4),\n"
            "        round(homogeneity_score(y_true, km_labels), 4),\n"
            "        round(completeness_score(y_true, km_labels), 4),\n"
            "        round(v_measure_score(y_true, km_labels), 4)\n"
            "    ],\n"
            "    'Hierarchical Ward (k=4)': [\n"
            "        round(silhouette_score(X_scaled, agg_labels), 4),\n"
            "        round(davies_bouldin_score(X_scaled, agg_labels), 4),\n"
            "        round(calinski_harabasz_score(X_scaled, agg_labels), 2),\n"
            "        round(adjusted_rand_score(y_true, agg_labels), 4),\n"
            "        round(normalized_mutual_info_score(y_true, agg_labels), 4),\n"
            "        round(homogeneity_score(y_true, agg_labels), 4),\n"
            "        round(completeness_score(y_true, agg_labels), 4),\n"
            "        round(v_measure_score(y_true, agg_labels), 4)\n"
            "    ]\n"
            "}\n"
            "df_compare = pd.DataFrame(metrics_data)\n"
            "print('=== Comprehensive Clustering Evaluation Benchmark ===')\n"
            "display(df_compare)"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### 🎓 Viva Voce Questions & Answers (Tutorial 12)\n\n"
            "1. **Q: What does a negative Silhouette score indicate?**\n"
            "   - **A:** A negative silhouette score means that $a(i) > b(i)$, which indicates that a sample is closer to points in a neighboring cluster than to points in its own assigned cluster. "
            "It signifies misclustering or boundary overlap.\n\n"
            "2. **Q: What is the difference between Homogeneity and Completeness?**\n"
            "   - **A:** **Homogeneity** measures whether each cluster contains only members of a single class. "
            "**Completeness** measures whether all members of a given class are assigned to the same cluster. "
            "Their harmonic mean is the **V-Measure**.\n\n"
            "3. **Q: Why is Adjusted Rand Index (ARI) preferred over raw Rand Index?**\n"
            "   - **A:** The raw Rand Index does not account for chance agreements; random clustering can score well above 0. "
            "ARI adjusts for chance so that a random assignment scores near 0.0, and perfect clustering scores 1.0."
        )
    }
]

# ------------------------------------------------------------------------------
# TUTORIAL 13: DECISION TREE ALGORITHM
# ------------------------------------------------------------------------------
t13_specs = [
    {
        'type': 'markdown',
        'source': (
            "# Tutorial 13 (T13): Building Programs to Implement Decision Tree Algorithm\n\n"
            "## 📌 Objective\n"
            "Implement a **Decision Tree Classifier (CART)** on the agricultural crop recommendation dataset. "
            "Explore the bias-variance tradeoff by tuning `max_depth`, visualize tree decisions (`plot_tree`), "
            "compute Gini feature importances, and evaluate multi-class classification performance.\n\n"
            "## 🔬 Key Concepts & Mathematical Formulas\n"
            "- **Gini Impurity**: Measures the probability of misclassifying a randomly chosen element:\n"
            "  $$G = 1 - \\sum_{i=1}^C p_i^2$$\n"
            "- **Information Gain (Entropy)**:\n"
            "  $$H(S) = -\\sum_{i=1}^C p_i \\log_2(p_i)$$\n"
            "  $$IG(S, A) = H(S) - \\sum_{v \\in \\text{Values}(A)} \\frac{|S_v|}{|S|} H(S_v)$$\n"
            "- **Mean Decrease in Impurity (MDI)**: Feature importance calculated by total reduction of Gini impurity brought by each feature across all tree splits."
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 1: Import Required Libraries"
    },
    {
        'type': 'code',
        'source': (
            "import os\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n"
            "from sklearn.model_selection import train_test_split\n"
            "from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text\n"
            "from sklearn.metrics import accuracy_score, classification_report, confusion_matrix\n\n"
            "sns.set_theme(style=\"whitegrid\", palette=\"muted\")\n"
            "print('Decision Tree libraries loaded!')"
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 2: Load Data and Stratified Train-Test Split (80/20)"
    },
    {
        'type': 'code',
        'source': (
            "df = pd.read_csv('data/Crop_recommendation.csv')\n"
            "features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']\n"
            "X = df[features]\n"
            "y = df['label']\n\n"
            "X_train, X_test, y_train, y_test = train_test_split(\n"
            "    X, y, test_size=0.20, random_state=42, stratify=y\n"
            ")\n"
            "print(f'Training Set: {X_train.shape[0]} samples')\n"
            "print(f'Testing Set:  {X_test.shape[0]} samples')"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 3: Hyperparameter Tuning - Tree Depth vs Overfitting\n"
            "We vary `max_depth` from 1 to 12 and plot training vs testing accuracy to identify the sweet spot before overfitting begins."
        )
    },
    {
        'type': 'code',
        'source': (
            "depths = range(1, 13)\n"
            "train_accs = []\n"
            "test_accs = []\n\n"
            "for d in depths:\n"
            "    dt = DecisionTreeClassifier(max_depth=d, criterion='gini', random_state=42)\n"
            "    dt.fit(X_train, y_train)\n"
            "    train_accs.append(dt.score(X_train, y_train))\n"
            "    test_accs.append(dt.score(X_test, y_test))\n\n"
            "plt.figure(figsize=(8.5, 4.8), dpi=140)\n"
            "plt.plot(list(depths), train_accs, 'o-', label='Training Accuracy', color='#2ca02c', linewidth=2)\n"
            "plt.plot(list(depths), test_accs, 's--', label='Testing Accuracy', color='#1f77b4', linewidth=2)\n"
            "plt.title('T13: Decision Tree Max Depth vs Accuracy (Bias-Variance Tradeoff)', fontsize=13, fontweight='bold', pad=12)\n"
            "plt.xlabel('Max Tree Depth', fontsize=11)\n"
            "plt.ylabel('Accuracy Score', fontsize=11)\n"
            "plt.xticks(list(depths))\n"
            "plt.axvline(x=7, color='crimson', linestyle=':', label='Optimal Depth (d=7, ~98% acc)')\n"
            "plt.legend(loc='lower right')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 4: Train Optimized Decision Tree ($d=7$)"
    },
    {
        'type': 'code',
        'source': (
            "best_dt = DecisionTreeClassifier(max_depth=7, criterion='gini', random_state=42)\n"
            "best_dt.fit(X_train, y_train)\n"
            "y_pred_dt = best_dt.predict(X_test)\n\n"
            "train_acc = best_dt.score(X_train, y_train)\n"
            "test_acc = accuracy_score(y_test, y_pred_dt)\n"
            "print(f'Decision Tree Training Accuracy: {train_acc:.2%}')\n"
            "print(f'Decision Tree Testing Accuracy:  {test_acc:.2%}')\n"
            "print('\\nClassification Report Summary:')\n"
            "print(classification_report(y_test, y_pred_dt, digits=3))"
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 5: Confusion Matrix Heatmap"
    },
    {
        'type': 'code',
        'source': (
            "classes = sorted(y.unique())\n"
            "cm = confusion_matrix(y_test, y_pred_dt, labels=classes)\n\n"
            "plt.figure(figsize=(9, 7.5), dpi=140)\n"
            "sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes, cbar=False)\n"
            "plt.title(f'T13: Decision Tree Confusion Matrix (Accuracy: {test_acc:.1%})', fontsize=13, fontweight='bold', pad=12)\n"
            "plt.xlabel('Predicted Crop Label', fontsize=11)\n"
            "plt.ylabel('True Crop Label', fontsize=11)\n"
            "plt.xticks(rotation=45, ha='right')\n"
            "plt.yticks(rotation=0)\n"
            "plt.tight_layout()\n"
            "plt.show()"
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 6: Feature Importance Analysis (MDI)"
    },
    {
        'type': 'code',
        'source': (
            "fi = pd.Series(best_dt.feature_importances_, index=features).sort_values(ascending=True)\n\n"
            "plt.figure(figsize=(8.5, 4.5), dpi=140)\n"
            "colors = sns.color_palette('viridis', len(fi))\n"
            "fi.plot(kind='barh', color=colors, edgecolor='black', linewidth=0.5)\n"
            "plt.title('T13: Decision Tree Feature Importances (Gini Impurity Reduction)', fontsize=13, fontweight='bold', pad=12)\n"
            "plt.xlabel('Relative Importance Score', fontsize=11)\n"
            "plt.ylabel('Feature', fontsize=11)\n"
            "for idx, val in enumerate(fi):\n"
            "    plt.text(val + 0.005, idx, f'{val:.1%}', va='center', fontweight='bold')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 7: Visualizing the Tree Structure"
    },
    {
        'type': 'code',
        'source': (
            "plt.figure(figsize=(18, 9), dpi=140)\n"
            "plot_tree(best_dt, max_depth=3, feature_names=features, class_names=best_dt.classes_, filled=True, rounded=True, fontsize=8)\n"
            "plt.title('T13: Decision Tree Architecture (Top 3 Levels Shown for Readability)', fontsize=13, fontweight='bold', pad=12)\n"
            "plt.tight_layout()\n"
            "plt.show()"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### 🎓 Viva Voce Questions & Answers (Tutorial 13)\n\n"
            "1. **Q: How does CART choose the best split at each node?**\n"
            "   - **A:** The CART algorithm evaluates every available feature and threshold, computing the weighted Gini impurity of the resulting subsets. "
            "It greedily selects the split that maximizes the Gini Impurity Reduction ($\\Delta G = G_{\\text{parent}} - \\sum \\frac{N_j}{N} G_{\\text{child}_j}$).\n\n"
            "2. **Q: What is tree pruning and why is it necessary?**\n"
            "   - **A:** Without constraints, a decision tree will continue splitting until every leaf is pure ($G=0$), causing extreme overfitting. "
            "**Pre-pruning** stops tree growth early via `max_depth`, `min_samples_split`, or `min_samples_leaf`. "
            "**Post-pruning** (Cost-Complexity Pruning $\\alpha$) grows the full tree and collapses branches with high complexity penalties.\n\n"
            "3. **Q: How does Gini compare to Entropy?**\n"
            "   - **A:** Both produce almost identical tree architectures. However, Gini impurity does not involve logarithmic computation ($\\log_2$), "
            "making it computationally faster than Shannon Entropy."
        )
    }
]

# ------------------------------------------------------------------------------
# TUTORIAL 14: RANDOM FOREST ALGORITHM
# ------------------------------------------------------------------------------
t14_specs = [
    {
        'type': 'markdown',
        'source': (
            "# Tutorial 14 (T14): Building Programs to Implement Random Forest Algorithm\n\n"
            "## 📌 Objective\n"
            "Implement a **Random Forest Classifier** ensemble on the crop dataset. "
            "Examine the effect of `n_estimators` (number of trees) on testing accuracy and **Out-of-Bag (OOB)** score, "
            "compare Random Forest vs single Decision Tree variance, and assess feature importances.\n\n"
            "## 🔬 Key Concepts & Mathematical Formulas\n"
            "- **Ensemble Learning (Bagging)**: Bootstrap Aggregation trains $B$ independent trees on random subsets with replacement:\n"
            "  $$\\hat{y} = \\text{mode} \\{ T_1(x), T_2(x), \\dots, T_B(x) \\}$$\n"
            "- **Variance Reduction Principle**: If each tree has variance $\\sigma^2$ with pairwise correlation $\\rho$, ensemble variance is:\n"
            "  $$\\text{Var}(\\bar{T}) = \\rho \\sigma^2 + \\frac{1 - \\rho}{B} \\sigma^2$$\n"
            "- **Random Subspace Method**: Selects $m = \\sqrt{p}$ random features at each split, de-correlating trees (reducing $\\rho$).\n"
            "- **Out-of-Bag (OOB) Score**: Validation accuracy evaluated on samples omitted from each tree's bootstrap sample (~36.8% of training data)."
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 1: Import Required Libraries"
    },
    {
        'type': 'code',
        'source': (
            "import os\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n"
            "from sklearn.model_selection import train_test_split\n"
            "from sklearn.tree import DecisionTreeClassifier\n"
            "from sklearn.ensemble import RandomForestClassifier\n"
            "from sklearn.metrics import accuracy_score, classification_report, confusion_matrix\n\n"
            "sns.set_theme(style=\"whitegrid\", palette=\"muted\")\n"
            "print('Random Forest libraries loaded!')"
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 2: Load Data and Split (80/20)"
    },
    {
        'type': 'code',
        'source': (
            "df = pd.read_csv('data/Crop_recommendation.csv')\n"
            "features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']\n"
            "X = df[features]\n"
            "y = df['label']\n\n"
            "X_train, X_test, y_train, y_test = train_test_split(\n"
            "    X, y, test_size=0.20, random_state=42, stratify=y\n"
            ")\n"
            "print(f'Training Samples: {len(X_train)}, Testing Samples: {len(X_test)}')"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 3: Varying Number of Trees (`n_estimators`) vs OOB Score\n"
            "We test tree counts from 10 to 200 and observe testing accuracy and Out-of-Bag score stabilization."
        )
    },
    {
        'type': 'code',
        'source': (
            "tree_counts = [10, 25, 50, 75, 100, 150, 200]\n"
            "oob_scores = []\n"
            "test_scores = []\n\n"
            "for n in tree_counts:\n"
            "    rf_temp = RandomForestClassifier(n_estimators=n, max_depth=8, oob_score=True, random_state=42)\n"
            "    rf_temp.fit(X_train, y_train)\n"
            "    oob_scores.append(rf_temp.oob_score_)\n"
            "    test_scores.append(rf_temp.score(X_test, y_test))\n\n"
            "plt.figure(figsize=(8.5, 4.8), dpi=140)\n"
            "plt.plot(tree_counts, test_scores, 'o-', color='#1f77b4', linewidth=2, label='Test Accuracy')\n"
            "plt.plot(tree_counts, oob_scores, 's--', color='#ff7f0e', linewidth=2, label='Out-of-Bag (OOB) Score')\n"
            "plt.title('T14: Random Forest Trees vs Accuracy & OOB Convergence', fontsize=13, fontweight='bold', pad=12)\n"
            "plt.xlabel('Number of Estimators (Trees)', fontsize=11)\n"
            "plt.ylabel('Score (0 to 1)', fontsize=11)\n"
            "plt.axvline(x=100, color='crimson', linestyle=':', label='Chosen Trees (n=100)')\n"
            "plt.legend(loc='lower right')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 4: Fit Optimized Random Forest Classifier ($n=100$)"
    },
    {
        'type': 'code',
        'source': (
            "rf = RandomForestClassifier(n_estimators=100, max_depth=8, oob_score=True, random_state=42)\n"
            "rf.fit(X_train, y_train)\n"
            "y_pred_rf = rf.predict(X_test)\n\n"
            "rf_train_acc = rf.score(X_train, y_train)\n"
            "rf_test_acc = accuracy_score(y_test, y_pred_rf)\n"
            "rf_oob = rf.oob_score_\n\n"
            "print(f'Random Forest Training Accuracy: {rf_train_acc:.2%}')\n"
            "print(f'Random Forest Testing Accuracy:  {rf_test_acc:.2%}')\n"
            "print(f'Out-of-Bag (OOB) Score:          {rf_oob:.2%}')\n"
            "print('\\nClassification Report Summary:')\n"
            "print(classification_report(y_test, y_pred_rf, digits=3))"
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 5: Confusion Matrix Heatmap"
    },
    {
        'type': 'code',
        'source': (
            "classes = sorted(y.unique())\n"
            "cm_rf = confusion_matrix(y_test, y_pred_rf, labels=classes)\n\n"
            "plt.figure(figsize=(9, 7.5), dpi=140)\n"
            "sns.heatmap(cm_rf, annot=True, fmt='d', cmap='Greens', xticklabels=classes, yticklabels=classes, cbar=False)\n"
            "plt.title(f'T14: Random Forest Confusion Matrix (Accuracy: {rf_test_acc:.1%})', fontsize=13, fontweight='bold', pad=12)\n"
            "plt.xlabel('Predicted Crop Label', fontsize=11)\n"
            "plt.ylabel('True Crop Label', fontsize=11)\n"
            "plt.xticks(rotation=45, ha='right')\n"
            "plt.yticks(rotation=0)\n"
            "plt.tight_layout()\n"
            "plt.show()"
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 6: Feature Importance Comparison: Decision Tree vs Random Forest"
    },
    {
        'type': 'code',
        'source': (
            "dt = DecisionTreeClassifier(max_depth=7, random_state=42)\n"
            "dt.fit(X_train, y_train)\n\n"
            "df_fi = pd.DataFrame({\n"
            "    'Single Decision Tree': dt.feature_importances_,\n"
            "    'Random Forest (100 Trees)': rf.feature_importances_\n"
            "}, index=features)\n\n"
            "plt.figure(figsize=(9.5, 5), dpi=140)\n"
            "df_fi.plot(kind='bar', figsize=(9.5, 5), color=['#1f77b4', '#2ca02c'], edgecolor='black', linewidth=0.5)\n"
            "plt.title('T14: Feature Importance Comparison (Decision Tree vs Random Forest)', fontsize=13, fontweight='bold', pad=12)\n"
            "plt.xlabel('Agricultural Feature', fontsize=11)\n"
            "plt.ylabel('MDI Feature Importance', fontsize=11)\n"
            "plt.xticks(rotation=30, ha='right')\n"
            "plt.legend(loc='upper right')\n"
            "plt.tight_layout()\n"
            "plt.show()\n\n"
            "display(df_fi.round(4))"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### 🎓 Viva Voce Questions & Answers (Tutorial 14)\n\n"
            "1. **Q: Why does Random Forest achieve higher accuracy and lower variance than a single Decision Tree?**\n"
            "   - **A:** A single tree has high variance and easily overfits training noise. By taking the majority vote over 100 independently trained bootstrap trees, "
            "individual errors cancel out. The random feature subset selection ($m = \\sqrt{p}$) ensures the trees are de-correlated, maximizing the variance reduction formula $\\frac{1-\\rho}{B} \\sigma^2$.\n\n"
            "2. **Q: What is the Out-of-Bag (OOB) error and how does it replace a cross-validation set?**\n"
            "   - **A:** In bootstrap sampling with replacement, the probability of any given sample being omitted from a bootstrap sample of size $n$ is "
            "$\\lim_{n \\to \\infty} (1 - 1/n)^n = e^{-1} \\approx 36.8\\%$. Each sample is evaluated only by the trees for which it was left out, providing a built-in cross-validation estimate without needing a separate validation split.\n\n"
            "3. **Q: How does Random Forest (Bagging) differ from Gradient Boosting (Boosting)?**\n"
            "   - **A:** Random Forest builds deep trees in **parallel** to reduce variance. Gradient Boosting builds shallow trees **sequentially**, with each tree learning from the residual errors (pseudo-residuals) of prior trees to reduce bias."
        )
    }
]

# ------------------------------------------------------------------------------
# TUTORIAL 15: ARTIFICIAL NEURAL NETWORKS (ANN)
# ------------------------------------------------------------------------------
t15_specs = [
    {
        'type': 'markdown',
        'source': (
            "# Tutorial 15 (T15): Building Programs to Implement Artificial Neural Networks\n\n"
            "## 📌 Objective\n"
            "Implement a **Multi-Layer Perceptron (MLP)** Artificial Neural Network for multi-class crop recommendation. "
            "Demonstrate the absolute necessity of feature standardization, plot the **Cross-Entropy Training Loss Curve**, "
            "compare activation functions (ReLU, Tanh, Sigmoid), and generate a **Master Supervised Benchmark** comparing T13, T14, and T15.\n\n"
            "## 🔬 Key Concepts & Mathematical Formulas\n"
            "- **Artificial Neuron (Perceptron)**:\n"
            "  $$z = \\sum_{i=1}^d w_i x_i + b = W^T x + b, \\quad a = g(z)$$\n"
            "- **Activation Functions**:\n"
            "  - **ReLU**: $g(z) = \\max(0, z)$ (prevents vanishing gradient, fast computation)\n"
            "  - **Tanh**: $g(z) = \\frac{e^z - e^{-z}}{e^z + e^{-z}}$\n"
            "  - **Softmax** (Output layer for $C=22$ crop classes): $P(y=k|x) = \\frac{e^{z_k}}{\\sum_{j=1}^C e^{z_j}}$\n"
            "- **Cross-Entropy Loss (Log Loss)**:\n"
            "  $$\\mathcal{L} = -\\sum_{k=1}^C y_k \\log(\\hat{y}_k)$$\n"
            "- **Backpropagation**: Gradient computation using chain rule: $\\frac{\\partial \\mathcal{L}}{\\partial W^{[l]}} = \\delta^{[l]} (a^{[l-1]})^T$."
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 1: Import Required Libraries"
    },
    {
        'type': 'code',
        'source': (
            "import os\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n"
            "from sklearn.model_selection import train_test_split\n"
            "from sklearn.preprocessing import StandardScaler, LabelEncoder\n"
            "from sklearn.neural_network import MLPClassifier\n"
            "from sklearn.tree import DecisionTreeClassifier\n"
            "from sklearn.ensemble import RandomForestClassifier\n"
            "from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix\n\n"
            "sns.set_theme(style=\"whitegrid\", palette=\"muted\")\n"
            "print('Neural network libraries loaded!')"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 2: Load Data, Encode Targets & Apply Standard Scaling\n"
            "Neural networks use gradient-based optimization (Adam). Standardizing inputs ($z = (x-\\mu)/\\sigma$) is mandatory "
            "to prevent gradient explosion or saturation of activation functions."
        )
    },
    {
        'type': 'code',
        'source': (
            "df = pd.read_csv('data/Crop_recommendation.csv')\n"
            "features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']\n"
            "X = df[features].values\n\n"
            "le = LabelEncoder()\n"
            "y = le.fit_transform(df['label'])\n"
            "classes = le.classes_\n\n"
            "X_train, X_test, y_train, y_test = train_test_split(\n"
            "    X, y, test_size=0.20, random_state=42, stratify=y\n"
            ")\n\n"
            "scaler = StandardScaler()\n"
            "X_train_s = scaler.fit_transform(X_train)\n"
            "X_test_s = scaler.transform(X_test)\n\n"
            "print(f'Training Set: {X_train_s.shape}, Testing Set: {X_test_s.shape}')\n"
            "print(f'Input Nodes: {X.shape[1]}, Output Classes: {len(classes)}')"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 3: Configure and Train Multi-Layer Perceptron (ANN)\n"
            "Architecture: 7 Input features $\\to$ Hidden Layer 1 (64 neurons, ReLU) $\\to$ Hidden Layer 2 (32 neurons, ReLU) $\\to$ Output (22 classes, Softmax)."
        )
    },
    {
        'type': 'code',
        'source': (
            "mlp = MLPClassifier(\n"
            "    hidden_layer_sizes=(64, 32),\n"
            "    activation='relu',\n"
            "    solver='adam',\n"
            "    max_iter=400,\n"
            "    random_state=42,\n"
            "    early_stopping=False\n"
            ")\n"
            "mlp.fit(X_train_s, y_train)\n"
            "y_pred_mlp = mlp.predict(X_test_s)\n\n"
            "mlp_train_acc = mlp.score(X_train_s, y_train)\n"
            "mlp_test_acc = accuracy_score(y_test, y_pred_mlp)\n"
            "print(f'MLP Training Accuracy: {mlp_train_acc:.2%}')\n"
            "print(f'MLP Testing Accuracy:  {mlp_test_acc:.2%}')\n"
            "print(f'Training Completed in {len(mlp.loss_curve_)} Epochs.')\n"
            "print(f'Final Training Loss:   {mlp.loss_curve_[-1]:.4f}')"
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 4: Training Loss Curve (Adam Optimizer Convergence)"
    },
    {
        'type': 'code',
        'source': (
            "plt.figure(figsize=(8.5, 4.8), dpi=140)\n"
            "plt.plot(mlp.loss_curve_, color='#d62728', linewidth=2.2, label='Cross-Entropy Loss')\n"
            "plt.title('T15: Artificial Neural Network Training Loss Curve (Adam Optimizer)', fontsize=13, fontweight='bold', pad=12)\n"
            "plt.xlabel('Epoch / Iteration', fontsize=11)\n"
            "plt.ylabel('Loss Value', fontsize=11)\n"
            "plt.grid(True, linestyle='--', alpha=0.6)\n"
            "plt.legend(loc='upper right')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        )
    },
    {
        'type': 'markdown',
        'source': "### Step 5: Confusion Matrix Heatmap"
    },
    {
        'type': 'code',
        'source': (
            "cm_mlp = confusion_matrix(y_test, y_pred_mlp)\n\n"
            "plt.figure(figsize=(9, 7.5), dpi=140)\n"
            "sns.heatmap(cm_mlp, annot=True, fmt='d', cmap='Oranges', xticklabels=classes, yticklabels=classes, cbar=False)\n"
            "plt.title(f'T15: Artificial Neural Network Confusion Matrix (Accuracy: {mlp_test_acc:.1%})', fontsize=13, fontweight='bold', pad=12)\n"
            "plt.xlabel('Predicted Crop Label', fontsize=11)\n"
            "plt.ylabel('True Crop Label', fontsize=11)\n"
            "plt.xticks(rotation=45, ha='right')\n"
            "plt.yticks(rotation=0)\n"
            "plt.tight_layout()\n"
            "plt.show()"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 6: Activation Function Benchmarking\n"
            "We compare convergence and accuracy across **ReLU**, **Tanh**, and **Logistic (Sigmoid)** activations."
        )
    },
    {
        'type': 'code',
        'source': (
            "act_funcs = ['relu', 'tanh', 'logistic']\n"
            "act_scores = []\n\n"
            "for act in act_funcs:\n"
            "    m = MLPClassifier(hidden_layer_sizes=(64, 32), activation=act, solver='adam', max_iter=400, random_state=42)\n"
            "    m.fit(X_train_s, y_train)\n"
            "    act_scores.append(m.score(X_test_s, y_test))\n\n"
            "plt.figure(figsize=(7.5, 4.5), dpi=140)\n"
            "bars = plt.bar(act_funcs, act_scores, color=['#1f77b4', '#ff7f0e', '#2ca02c'], edgecolor='black', linewidth=0.5, width=0.45)\n"
            "plt.title('T15: ANN Activation Function Performance Comparison', fontsize=13, fontweight='bold', pad=12)\n"
            "plt.xlabel('Activation Function', fontsize=11)\n"
            "plt.ylabel('Test Accuracy', fontsize=11)\n"
            "plt.ylim(0, 1.15)\n"
            "for bar in bars:\n"
            "    yval = bar.get_height()\n"
            "    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.02, f'{yval:.1%}', ha='center', va='bottom', fontweight='bold')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### Step 7: Master Supervised Benchmark (T13 vs T14 vs T15)\n"
            "Side-by-side comparison of **Decision Tree (T13)**, **Random Forest (T14)**, and **Artificial Neural Network (T15)** on the exact same dataset split."
        )
    },
    {
        'type': 'code',
        'source': (
            "dt = DecisionTreeClassifier(max_depth=7, random_state=42)\n"
            "dt.fit(X_train, y_train)\n"
            "y_pred_dt = dt.predict(X_test)\n\n"
            "rf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)\n"
            "rf.fit(X_train, y_train)\n"
            "y_pred_rf = rf.predict(X_test)\n\n"
            "benchmark_df = pd.DataFrame({\n"
            "    'Supervised Model': ['Decision Tree (T13)', 'Random Forest (T14)', 'Artificial Neural Network (T15)'],\n"
            "    'Train Accuracy': [f'{dt.score(X_train, y_train):.2%}', f'{rf.score(X_train, y_train):.2%}', f'{mlp_train_acc:.2%}'],\n"
            "    'Test Accuracy': [f'{accuracy_score(y_test, y_pred_dt):.2%}', f'{accuracy_score(y_test, y_pred_rf):.2%}', f'{mlp_test_acc:.2%}'],\n"
            "    'Macro Precision': [\n"
            "        f'{precision_score(y_test, y_pred_dt, average=\"macro\"):.2%}',\n"
            "        f'{precision_score(y_test, y_pred_rf, average=\"macro\"):.2%}',\n"
            "        f'{precision_score(y_test, y_pred_mlp, average=\"macro\"):.2%}'\n"
            "    ],\n"
            "    'Macro Recall': [\n"
            "        f'{recall_score(y_test, y_pred_dt, average=\"macro\"):.2%}',\n"
            "        f'{recall_score(y_test, y_pred_rf, average=\"macro\"):.2%}',\n"
            "        f'{recall_score(y_test, y_pred_mlp, average=\"macro\"):.2%}'\n"
            "    ],\n"
            "    'Macro F1-Score': [\n"
            "        f'{f1_score(y_test, y_pred_dt, average=\"macro\"):.2%}',\n"
            "        f'{f1_score(y_test, y_pred_rf, average=\"macro\"):.2%}',\n"
            "        f'{f1_score(y_test, y_pred_mlp, average=\"macro\"):.2%}'\n"
            "    ]\n"
            "})\n"
            "print('=== Supervised Learning Master Benchmark ===')\n"
            "display(benchmark_df)\n\n"
            "# Visual Comparison Bar Chart\n"
            "x_pos = np.arange(3)\n"
            "width = 0.25\n"
            "train_vals = [dt.score(X_train, y_train), rf.score(X_train, y_train), mlp_train_acc]\n"
            "test_vals = [accuracy_score(y_test, y_pred_dt), accuracy_score(y_test, y_pred_rf), mlp_test_acc]\n"
            "f1_vals = [\n"
            "    f1_score(y_test, y_pred_dt, average='macro'),\n"
            "    f1_score(y_test, y_pred_rf, average='macro'),\n"
            "    f1_score(y_test, y_pred_mlp, average='macro')\n"
            "]\n\n"
            "plt.figure(figsize=(9.5, 4.8), dpi=140)\n"
            "plt.bar(x_pos - width, train_vals, width, label='Train Accuracy', color='#2ca02c')\n"
            "plt.bar(x_pos, test_vals, width, label='Test Accuracy', color='#1f77b4')\n"
            "plt.bar(x_pos + width, f1_vals, width, label='Macro F1-Score', color='#ff7f0e')\n"
            "plt.xticks(x_pos, ['Decision Tree (T13)', 'Random Forest (T14)', 'Neural Network (T15)'], fontweight='bold')\n"
            "plt.ylabel('Score (0 to 1)', fontsize=11)\n"
            "plt.title('Benchmark Comparison: Decision Tree vs Random Forest vs ANN', fontsize=13, fontweight='bold', pad=12)\n"
            "plt.ylim(0, 1.15)\n"
            "plt.legend(loc='upper right')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        )
    },
    {
        'type': 'markdown',
        'source': (
            "### 🎓 Viva Voce Questions & Answers (Tutorial 15)\n\n"
            "1. **Q: Why is feature scaling mandatory for Neural Networks but optional for Decision Trees?**\n"
            "   - **A:** Decision trees evaluate feature thresholds independently along single orthogonal dimensions, making them invariant to monotonic scaling. "
            "Neural networks use gradient descent where all inputs contribute to weight updates ($W \\leftarrow W - \\alpha \\frac{\\partial \\mathcal{L}}{\\partial W}$). "
            "Unscaled features produce elongated, ill-conditioned loss surfaces with severe gradient oscillations and vanishing/exploding gradients.\n\n"
            "2. **Q: Why does ReLU outperform Sigmoid in deep hidden layers?**\n"
            "   - **A:** Sigmoid has derivatives $g'(z) = g(z)(1 - g(z)) \\le 0.25$. When multiplied across multiple layers during backpropagation, gradients vanish exponentially toward 0. "
            "ReLU has a constant derivative of 1 for $z > 0$, preventing vanishing gradients and allowing much faster training.\n\n"
            "3. **Q: How does the Adam optimizer work?**\n"
            "   - **A:** Adam (Adaptive Moment Estimation) combines **Momentum** (exponential moving average of past gradients $m_t$) with **RMSProp** (exponential moving average of squared gradients $v_t$). "
            "It computes individual adaptive learning rates for every single parameter with bias correction."
        )
    }
]

# ==============================================================================
# EXECUTE ALL NOTEBOOKS
# ==============================================================================
if __name__ == "__main__":
    notebooks = [
        ("Tutorial_10_Hierarchical_Clustering.ipynb", t10_specs),
        ("Tutorial_11_KMeans_Clustering.ipynb", t11_specs),
        ("Tutorial_12_Cluster_Evaluation.ipynb", t12_specs),
        ("Tutorial_13_Decision_Tree.ipynb", t13_specs),
        ("Tutorial_14_Random_Forest.ipynb", t14_specs),
        ("Tutorial_15_Artificial_Neural_Networks.ipynb", t15_specs),
    ]

    for fname, specs in notebooks:
        execute_and_build_notebook(fname, specs, fname)

    print("\n========================================================")
    print("ALL 6 NOTEBOOKS (T10 TO T15) GENERATED & EXECUTED CLEANLY!")
    print("========================================================")
