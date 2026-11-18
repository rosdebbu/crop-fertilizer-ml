import json
import os

def create_notebook(filename, cells):
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
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
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print(f"[CREATED] {filename}")

# ------------------------------------------------------------
# T7: PCA NOTEBOOK (Minimal Comments)
# ------------------------------------------------------------
t7_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Tutorial 7 (T7): Principal Component Analysis (PCA)\n",
            "**Goal:** Reduce 7 agricultural sensor features down to 2 principal components for visualization and dimensionality reduction."
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["### Step 1: Imports"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import os\n",
            "import numpy as np\n",
            "import pandas as pd\n",
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n",
            "from sklearn.preprocessing import StandardScaler\n",
            "from sklearn.decomposition import PCA\n",
            "\n",
            "sns.set_theme(style=\"whitegrid\")\n",
            "print(\"Libraries loaded.\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["### Step 2: Load Data"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "os.makedirs(\"data\", exist_ok=True)\n",
            "csv_path = os.path.join(\"data\", \"Crop_recommendation.csv\")\n",
            "if not os.path.exists(csv_path):\n",
            "    crops = [\"rice\", \"maize\", \"chickpea\", \"kidneybeans\", \"pigeonpeas\", \"mothbeans\", \"mungbean\", \"blackgram\", \"lentil\", \"pomegranate\"]\n",
            "    df = pd.DataFrame({\n",
            "        'N': np.random.randint(10, 140, 200),\n",
            "        'P': np.random.randint(5, 145, 200),\n",
            "        'K': np.random.randint(15, 205, 200),\n",
            "        'temperature': np.random.uniform(8.0, 43.0, 200),\n",
            "        'humidity': np.random.uniform(14.0, 100.0, 200),\n",
            "        'ph': np.random.uniform(3.5, 9.9, 200),\n",
            "        'rainfall': np.random.uniform(20.0, 300.0, 200),\n",
            "        'label': np.random.choice(crops, 200)\n",
            "    })\n",
            "    df.to_csv(csv_path, index=False)\n",
            "else:\n",
            "    df = pd.read_csv(csv_path)\n",
            "\n",
            "print(f\"Shape: {df.shape}\")\n",
            "display(df.head())"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["### Step 3: Standardize Features\n", "Standardization $z = (x - \\mu)/\\sigma$ is required because PCA maximizes variance."]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']\n",
            "X = df[features]\n",
            "y = df['label']\n",
            "\n",
            "scaler = StandardScaler()\n",
            "X_scaled = scaler.fit_transform(X)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["### Step 4: Full PCA & Scree Plot"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "pca_full = PCA(n_components=7)\n",
            "pca_full.fit(X_scaled)\n",
            "\n",
            "evr = pca_full.explained_variance_ratio_\n",
            "cum_evr = np.cumsum(evr)\n",
            "\n",
            "fig, ax1 = plt.subplots(figsize=(7, 4))\n",
            "comps = np.arange(1, 8)\n",
            "ax1.bar(comps, evr * 100, color='#3a86ff', alpha=0.7)\n",
            "ax1.set_xlabel('Principal Component')\n",
            "ax1.set_ylabel('Individual Variance (%)', color='#3a86ff')\n",
            "\n",
            "ax2 = ax1.twinx()\n",
            "ax2.plot(comps, cum_evr * 100, color='#e63946', marker='o', linewidth=2)\n",
            "ax2.axhline(80, color='grey', linestyle='--')\n",
            "ax2.set_ylabel('Cumulative Variance (%)', color='#e63946')\n",
            "\n",
            "plt.title('T7: Scree Plot')\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["### Step 5: 2D PCA Projection (7D -> 2D)"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "pca_2d = PCA(n_components=2)\n",
            "X_pca = pca_2d.fit_transform(X_scaled)\n",
            "df_pca = pd.DataFrame(X_pca, columns=['PC1', 'PC2'])\n",
            "df_pca['label'] = y.values\n",
            "\n",
            "plt.figure(figsize=(8, 5))\n",
            "top_crops = df['label'].value_counts().index[:6]\n",
            "sns.scatterplot(data=df_pca[df_pca['label'].isin(top_crops)], x='PC1', y='PC2', hue='label', palette='tab10', s=70)\n",
            "plt.title(f\"T7: 2D PCA (PC1: {pca_2d.explained_variance_ratio_[0]*100:.1f}%, PC2: {pca_2d.explained_variance_ratio_[1]*100:.1f}%)\")\n",
            "plt.legend(bbox_to_anchor=(1.05, 1))\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Viva Note (T7):\n",
            "- **Why reduce dimensions?** Avoid the curse of dimensionality, remove multicollinearity, and visualize data in 2D.\n",
            "- **Formula used:** Covariance matrix $\\Sigma = \\frac{1}{n-1} X^T X$ and Eigen decomposition $\\Sigma v = \\lambda v$."
        ]
    }
]
create_notebook("Tutorial_7_PCA.ipynb", t7_cells)

# ------------------------------------------------------------
# T8: NAIVE BAYES NOTEBOOK (Minimal Comments)
# ------------------------------------------------------------
t8_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Tutorial 8 (T8): Naïve Bayes Classification\n",
            "**Goal:** Build and compare Gaussian, Multinomial, and Bernoulli Naïve Bayes on crop classification."
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["### Step 1: Imports"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import os\n",
            "import numpy as np\n",
            "import pandas as pd\n",
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n",
            "from sklearn.model_selection import train_test_split\n",
            "from sklearn.preprocessing import StandardScaler, MinMaxScaler, Binarizer\n",
            "from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB\n",
            "from sklearn.metrics import accuracy_score, f1_score, confusion_matrix\n",
            "\n",
            "sns.set_theme(style=\"whitegrid\")\n",
            "print(\"Libraries loaded.\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["### Step 2: Load and Split Data"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "os.makedirs(\"data\", exist_ok=True)\n",
            "csv_path = os.path.join(\"data\", \"Crop_recommendation.csv\")\n",
            "if not os.path.exists(csv_path):\n",
            "    crops = [\"rice\", \"maize\", \"chickpea\", \"kidneybeans\", \"pigeonpeas\", \"mothbeans\", \"mungbean\", \"blackgram\", \"lentil\", \"pomegranate\"]\n",
            "    df = pd.DataFrame({\n",
            "        'N': np.random.randint(10, 140, 200),\n",
            "        'P': np.random.randint(5, 145, 200),\n",
            "        'K': np.random.randint(15, 205, 200),\n",
            "        'temperature': np.random.uniform(8.0, 43.0, 200),\n",
            "        'humidity': np.random.uniform(14.0, 100.0, 200),\n",
            "        'ph': np.random.uniform(3.5, 9.9, 200),\n",
            "        'rainfall': np.random.uniform(20.0, 300.0, 200),\n",
            "        'label': np.random.choice(crops, 200)\n",
            "    })\n",
            "    df.to_csv(csv_path, index=False)\n",
            "else:\n",
            "    df = pd.read_csv(csv_path)\n",
            "\n",
            "X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]\n",
            "y = df['label']\n",
            "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["### Step 3: Train 3 Naïve Bayes Models"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# 1. Gaussian NB (Continuous normal features)\n",
            "scaler_std = StandardScaler()\n",
            "X_tr_std = scaler_std.fit_transform(X_train)\n",
            "X_te_std = scaler_std.transform(X_test)\n",
            "gnb = GaussianNB()\n",
            "gnb.fit(X_tr_std, y_train)\n",
            "y_pred_gnb = gnb.predict(X_te_std)\n",
            "\n",
            "# 2. Multinomial NB (Non-negative counts/features)\n",
            "scaler_mm = MinMaxScaler()\n",
            "X_tr_mm = scaler_mm.fit_transform(X_train)\n",
            "X_te_mm = scaler_mm.transform(X_test)\n",
            "mnb = MultinomialNB(alpha=1.0)\n",
            "mnb.fit(X_tr_mm, y_train)\n",
            "y_pred_mnb = mnb.predict(X_te_mm)\n",
            "\n",
            "# 3. Bernoulli NB (Binary features)\n",
            "binarizer = Binarizer(threshold=0.5)\n",
            "X_tr_bin = binarizer.fit_transform(X_tr_mm)\n",
            "X_te_bin = binarizer.transform(X_te_mm)\n",
            "bnb = BernoulliNB(alpha=1.0)\n",
            "bnb.fit(X_tr_bin, y_train)\n",
            "y_pred_bnb = bnb.predict(X_te_bin)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["### Step 4: Comparison & Confusion Matrix"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "res_df = pd.DataFrame({\n",
            "    'Model': ['Gaussian NB', 'Multinomial NB', 'Bernoulli NB'],\n",
            "    'Accuracy (%)': [accuracy_score(y_test, y_pred_gnb)*100, accuracy_score(y_test, y_pred_mnb)*100, accuracy_score(y_test, y_pred_bnb)*100],\n",
            "    'F1-Score (%)': [f1_score(y_test, y_pred_gnb, average='weighted', zero_division=0)*100,\n",
            "                     f1_score(y_test, y_pred_mnb, average='weighted', zero_division=0)*100,\n",
            "                     f1_score(y_test, y_pred_bnb, average='weighted', zero_division=0)*100]\n",
            "})\n",
            "display(res_df)\n",
            "\n",
            "top_classes = sorted(list(set(y_test)))[:8]\n",
            "cm = confusion_matrix(y_test, y_pred_gnb, labels=top_classes)\n",
            "plt.figure(figsize=(7, 5))\n",
            "sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=top_classes, yticklabels=top_classes)\n",
            "plt.title('T8: Confusion Matrix (Gaussian NB)')\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Viva Note (T8):\n",
            "- **Why 'Naïve'?** Assumes all features are strictly conditionally independent given the class.\n",
            "- **Why Gaussian NB?** Ideal for real-world continuous sensor data (temperature, rainfall, pH)."
        ]
    }
]
create_notebook("Tutorial_8_Naive_Bayes.ipynb", t8_cells)

# ------------------------------------------------------------
# T9: SVM NOTEBOOK (Clear Linear vs Non-Linear & Minimal Comments)
# ------------------------------------------------------------
t9_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Tutorial 9 (T9): Support Vector Machine (SVM)\n",
            "**Goal:** Understand Linear SVM vs Non-Linear SVM, implement different kernels, and tune hyperparameter $C$."
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 💡 What is Linear vs Non-Linear SVM?\n",
            "- **Linear SVM (`kernel='linear'`)**: Draws a **straight line** (or flat hyperplane in higher dimensions) to separate classes.\n",
            "- **Non-Linear SVM (`kernel='rbf'`, `kernel='poly'` etc.)**: When data cannot be separated by a straight line (e.g. one class surrounds another in a circle), it uses the **Kernel Trick** to bend/curve the boundary."
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["### Step 1: Imports"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import os\n",
            "import numpy as np\n",
            "import pandas as pd\n",
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n",
            "from sklearn.model_selection import train_test_split\n",
            "from sklearn.preprocessing import StandardScaler\n",
            "from sklearn.svm import SVC\n",
            "from sklearn.metrics import accuracy_score, f1_score, confusion_matrix\n",
            "\n",
            "sns.set_theme(style=\"whitegrid\")\n",
            "print(\"Libraries loaded.\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["### Step 2: Load Data & Standardize\n", "Feature scaling is mandatory for SVM to calculate correct geometric margins."]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "os.makedirs(\"data\", exist_ok=True)\n",
            "csv_path = os.path.join(\"data\", \"Crop_recommendation.csv\")\n",
            "if not os.path.exists(csv_path):\n",
            "    crops = [\"rice\", \"maize\", \"chickpea\", \"kidneybeans\", \"pigeonpeas\", \"mothbeans\", \"mungbean\", \"blackgram\", \"lentil\", \"pomegranate\"]\n",
            "    df = pd.DataFrame({\n",
            "        'N': np.random.randint(10, 140, 200),\n",
            "        'P': np.random.randint(5, 145, 200),\n",
            "        'K': np.random.randint(15, 205, 200),\n",
            "        'temperature': np.random.uniform(8.0, 43.0, 200),\n",
            "        'humidity': np.random.uniform(14.0, 100.0, 200),\n",
            "        'ph': np.random.uniform(3.5, 9.9, 200),\n",
            "        'rainfall': np.random.uniform(20.0, 300.0, 200),\n",
            "        'label': np.random.choice(crops, 200)\n",
            "    })\n",
            "    df.to_csv(csv_path, index=False)\n",
            "else:\n",
            "    df = pd.read_csv(csv_path)\n",
            "\n",
            "X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]\n",
            "y = df['label']\n",
            "\n",
            "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)\n",
            "\n",
            "scaler = StandardScaler()\n",
            "X_tr_sc = scaler.fit_transform(X_train)\n",
            "X_te_sc = scaler.transform(X_test)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["### Step 3: Compare Linear vs Non-Linear SVM Kernels"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "kernels = {\n",
            "    'Linear (Straight Boundary)': SVC(kernel='linear', C=1.0),\n",
            "    'Non-Linear RBF (Curved)': SVC(kernel='rbf', C=1.0, gamma='scale'),\n",
            "    'Non-Linear Poly (degree=3)': SVC(kernel='poly', degree=3, C=1.0),\n",
            "    'Non-Linear Sigmoid': SVC(kernel='sigmoid', C=1.0)\n",
            "}\n",
            "\n",
            "res = []\n",
            "for name, m in kernels.items():\n",
            "    m.fit(X_tr_sc, y_train)\n",
            "    pred = m.predict(X_te_sc)\n",
            "    res.append({\n",
            "        'Model': name,\n",
            "        'Accuracy (%)': accuracy_score(y_test, pred)*100,\n",
            "        'F1-Score (%)': f1_score(y_test, pred, average='weighted', zero_division=0)*100\n",
            "    })\n",
            "\n",
            "res_df = pd.DataFrame(res)\n",
            "display(res_df)\n",
            "\n",
            "plt.figure(figsize=(7, 4))\n",
            "plt.bar(res_df['Model'], res_df['Accuracy (%)'], color='#2b5c8f')\n",
            "plt.xticks(rotation=20, ha='right')\n",
            "plt.ylabel('Accuracy (%)')\n",
            "plt.title('T9: Linear vs Non-Linear SVM Kernels')\n",
            "plt.ylim(0, 105)\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["### Step 4: Hyperparameter $C$ Tuning\n", "Small $C$ = wider margin (soft margin, prevents overfitting). Large $C$ = narrow margin (hard margin, strictly penalizes errors)."]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "c_vals = [0.01, 0.1, 1, 10, 100]\n",
            "accs = []\n",
            "for c in c_vals:\n",
            "    m = SVC(kernel='rbf', C=c)\n",
            "    m.fit(X_tr_sc, y_train)\n",
            "    accs.append(accuracy_score(y_test, m.predict(X_te_sc))*100)\n",
            "\n",
            "plt.figure(figsize=(6, 3.5))\n",
            "plt.plot([str(c) for c in c_vals], accs, marker='o', color='#e76f51', linewidth=2)\n",
            "plt.title('T9: Effect of Regularization C (RBF)')\n",
            "plt.xlabel('C')\n",
            "plt.ylabel('Accuracy (%)')\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["### Step 5: Confusion Matrix"]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "best_svm = SVC(kernel='rbf', C=10.0)\n",
            "best_svm.fit(X_tr_sc, y_train)\n",
            "pred_best = best_svm.predict(X_te_sc)\n",
            "\n",
            "top_classes = sorted(list(set(y_test)))[:8]\n",
            "cm = confusion_matrix(y_test, pred_best, labels=top_classes)\n",
            "plt.figure(figsize=(7, 5))\n",
            "sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', xticklabels=top_classes, yticklabels=top_classes)\n",
            "plt.title('T9: Confusion Matrix (RBF Kernel)')\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Viva Note (T9):\n",
            "- **Linear vs Non-Linear:** Linear uses a straight flat hyperplane ($w^T x + b = 0$). Non-Linear uses the Kernel Trick ($K(x, x')$) to separate curved data in higher dimensions.\n",
            "- **What are Support Vectors?** Points on the edge of the margin that determine where the boundary is placed.\n",
            "- **Hyperparameters:** $C$ controls margin width vs misclassification tradeoff. $\\gamma$ (gamma) controls the influence radius of each point."
        ]
    }
]
create_notebook("Tutorial_9_SVM.ipynb", t9_cells)
