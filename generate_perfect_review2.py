import os
import sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE_TYPE
import win32com.client

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PPTX = os.path.join(BASE_DIR, "Comprehensive_Viva_Crop_Fertilizer_ML.pptx")
DEST_PPTX = os.path.join(BASE_DIR, "Comprehensive_Viva_Crop_Fertilizer_ML copy.pptx")
DEST_PDF = os.path.join(BASE_DIR, "Comprehensive_Viva_Crop_Fertilizer_ML copy.pdf")

prs = pptx.Presentation(SRC_PPTX)
print(f"[INFO] Loaded master presentation with {len(prs.slides)} slides.")

# Theme Palette
C_NAVY = RGBColor(0x1F, 0x38, 0x64)
C_ROYAL = RGBColor(0x2E, 0x54, 0x96)
C_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
C_GOLD = RGBColor(0xFD, 0xE0, 0x47)       # Bright warm yellow/gold for high contrast on dark grey
C_CYAN = RGBColor(0x93, 0xC5, 0xFD)       # Soft bright blue for dark background
C_SILVER = RGBColor(0xEE, 0xF2, 0xF6)     # Crisp near-white
C_BLACK = RGBColor(0x00, 0x00, 0x00)
C_DARK_GRAY = RGBColor(0x33, 0x41, 0x55)
C_FOOTER_GRAY = RGBColor(0x70, 0x70, 0x70)

FOOTER_TEXT = "RA2411056010276, RA2411056010283 | Review II: Crop Recommendation & Fertilizer Prediction Using Advanced ML"
DATE_TEXT = "Review II - Nov 2026"

def update_footer_and_date(slide, slide_num):
    for shape in slide.shapes:
        if shape.has_text_frame:
            txt = shape.text_frame.text.strip()
            # Match footer text specifically (exclude slide 1!)
            if "Crop Recommendation & Fertilizer Prediction" in txt or "RA2411056010276" in txt or "Multilingual Stuttering" in txt:
                shape.text_frame.clear()
                p = shape.text_frame.paragraphs[0]
                p.text = FOOTER_TEXT
                p.font.name = "Cambria"
                p.font.size = Pt(11)
                p.font.color.rgb = C_FOOTER_GRAY
                p.font.bold = True
            elif txt in ["21 Sep 2026", "5 Aug 2026", "6 Aug 2026", "18 Aug 2026", "18-08-2026", "17-07-2024"]:
                shape.text_frame.clear()
                p = shape.text_frame.paragraphs[0]
                p.text = DATE_TEXT
                p.font.name = "Times New Roman"
                p.font.size = Pt(11)
                p.font.color.rgb = C_FOOTER_GRAY

# ==============================================================================
# SLIDE 1: TITLE SLIDE (PERFECT HIGH CONTRAST & VISIBILITY)
# ==============================================================================
s1 = prs.slides[0]

# Shape 3: Title on dark grey card [object 7]
s1_title_shape = s1.shapes[3]
if s1_title_shape.has_text_frame:
    s1_title_shape.text_frame.clear()
    p0 = s1_title_shape.text_frame.paragraphs[0]
    p0.text = "AI-Driven Precision Agriculture:"
    p0.font.name = "Times New Roman"
    p0.font.size = Pt(18)
    p0.font.bold = True
    p0.font.color.rgb = C_GOLD
    p0.space_after = Pt(4)

    p1 = s1_title_shape.text_frame.add_paragraph()
    p1.text = "Crop Recommendation and Fertilizer Prediction Using Advanced Machine Learning Frameworks"
    p1.font.name = "Times New Roman"
    p1.font.size = Pt(18)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE
    p1.space_after = Pt(8)

# Shape 4: Candidate Details inside dark grey card [object 8]
# Make everything crisp pure white and light gold/cyan for 100% visibility!
s1_cand_shape = s1.shapes[4]
if s1_cand_shape.has_text_frame:
    s1_cand_shape.text_frame.clear()
    s1_cand_lines = [
        ("CANDIDATE NAMES", 12, True, C_GOLD),
        ("DEBJIT DAS  |  RA2411056010276", 12, True, C_WHITE),
        ("ANSHUMAAN DAS  |  RA2411056010283", 12, True, C_WHITE),
        ("B.Tech - Computer Science and Engineering", 10.5, False, C_SILVER),
        ("School of Computing", 11, True, C_WHITE),
        ("PROJECT REVIEW II / RESEARCH VIVA", 12, True, C_CYAN),
        ("Faculty of Engineering and Technology", 10, False, C_SILVER),
        ("SRM Institute of Science and Technology, Kattankulathur", 10, False, C_SILVER)
    ]
    for idx, (txt, sz, bld, col) in enumerate(s1_cand_lines):
        p = s1_cand_shape.text_frame.paragraphs[0] if idx == 0 else s1_cand_shape.text_frame.add_paragraph()
        p.text = txt
        p.font.name = "Times New Roman"
        p.font.size = Pt(sz)
        p.font.bold = bld
        p.font.color.rgb = col
        p.space_after = Pt(3)

# Shape 7: Date at bottom of dark grey card [object 11]
s1_date_shape = s1.shapes[7]
if s1_date_shape.has_text_frame:
    s1_date_shape.text_frame.clear()
    p = s1_date_shape.text_frame.paragraphs[0]
    p.text = "Review II • 2026"
    p.font.name = "Times New Roman"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

# Shape 8: Header badge on right side [object 12]
s1_badge_shape = s1.shapes[8]
if s1_badge_shape.has_text_frame:
    s1_badge_shape.text_frame.clear()
    p = s1_badge_shape.text_frame.paragraphs[0]
    p.text = "Project Review II Evaluation"
    p.font.name = "Times New Roman"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = C_ROYAL

# Shape 5: Title on right side [object 9]
s1_right_title = s1.shapes[5]
if s1_right_title.has_text_frame:
    s1_right_title.text_frame.clear()
    p0 = s1_right_title.text_frame.paragraphs[0]
    p0.text = "AI-Driven Precision Agriculture:"
    p0.font.name = "Times New Roman"
    p0.font.size = Pt(15)
    p0.font.bold = True
    p0.font.color.rgb = C_NAVY
    p0.space_after = Pt(2)
    p1 = s1_right_title.text_frame.add_paragraph()
    p1.text = "Crop Recommendation and Fertilizer Prediction Using Advanced Machine Learning Frameworks"
    p1.font.name = "Times New Roman"
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = C_DARK_GRAY

print("[OK] Slide 1 fixed: High contrast white/gold on dark card, proper candidate details, no footer clobbering.")

# ==============================================================================
# SLIDE 2: AGENDA (UPDATED FOR REVIEW II)
# ==============================================================================
s2 = prs.slides[1]
for shape in s2.shapes:
    if shape.has_text_frame:
        txt = shape.text_frame.text.strip()
        if "Course Work / Lab Foundation" in txt or "Course Work Details" in txt or "AGENDA" not in txt and len(txt) > 30:
            shape.text_frame.clear()
            agenda_items = [
                "Course Work & Academic Foundation",
                "Project Overview & Problem Formulation",
                "Literature Survey Highlights (10 Studies)",
                "Review II Scope & Evaluation Parameters",
                "Model Validation & Resampling (K-Fold CV & Bootstrapping)",
                "Model Performance Evaluation (Metrics, MSE, Confusion Matrix, F1)",
                "Multiple Linear Regression (Tutorial 5 - Continuous Rainfall Model)",
                "Logistic Regression (Tutorial 6 - Multi-Class Crop Probability Model)",
                "End-to-End Model Prediction Pipeline & Inference Workflow",
                "Comprehensive Comparison of Classification Models (LR vs DT vs KNN vs RF)",
                "Project Milestones, Publications & Future Scope",
                "References & Defense Conclusion"
            ]
            for idx, item in enumerate(agenda_items):
                p = shape.text_frame.paragraphs[0] if idx == 0 else shape.text_frame.add_paragraph()
                p.text = f"•  {item}"
                p.font.name = "Times New Roman"
                p.font.size = Pt(16)
                p.font.bold = True
                p.font.color.rgb = RGBColor(0x44, 0x53, 0x6A)
                p.space_after = Pt(5)
update_footer_and_date(s2, 2)

# Update footers on slides 3 to 17 (Literature Survey, Problem Statement, Objectives)
for i in range(2, 17):
    update_footer_and_date(prs.slides[i], i + 1)

# ==============================================================================
# SLIDE 18: OBJECTIVE 1 OVERVIEW (UPDATE FOCUS ON VALIDATION & RESAMPLING)
# ==============================================================================
s18 = prs.slides[17]
for shape in s18.shapes:
    if shape.has_text_frame:
        txt = shape.text_frame.text.strip()
        if "Agro-Climatic Preprocessing & Feature Engineering" in txt:
            shape.text_frame.clear()
            p0 = shape.text_frame.paragraphs[0]
            p0.text = "Agro-Climatic Feature Engineering, Validation & Resampling — Objective 1"
            p0.font.name = "Times New Roman"
            p0.font.size = Pt(19)
            p0.font.bold = True
            p0.font.color.rgb = C_NAVY
            p0.space_after = Pt(12)

            o1_body = [
                "Raw agro-climatic measurements (Soil N, P, K, Temperature, Humidity, pH, Rainfall) pass through an audited data cleaning and feature engineering pipeline ensuring zero data leakage:",
                "• Stoichiometric Nutrient Balance Ratios: Explicitly computing N/P, N/K, P/K, and total nutrient density (N + P + K), enabling models to learn physiological chemical equilibrium.",
                "• Micro-Climatic Stress Indices: Combining Vapor Pressure Deficit (VPD) and Rainfall-Temperature interaction terms to capture non-linear plant water-stress dynamics.",
                "• Model Validation & Resampling Protocol: Overcoming single train-test split variance via 5-Fold Stratified Cross-Validation and non-parametric Bootstrapping with replacement.",
                "• Stratified K-Fold Guarantee: Strictly preserves exact class balance (100 samples per crop across all 22 classes → 20 samples per fold), eliminating optimistic holdout bias.",
                "• Empirical Generalizability: Achieved a mean 5-fold cross-validation accuracy of 99.32% ± 0.31% with StandardScaler normalization, proving exceptional stability across micro-climates."
            ]
            for item in o1_body:
                p = shape.text_frame.add_paragraph()
                p.text = item
                p.font.name = "Times New Roman"
                p.font.size = Pt(14)
                p.font.color.rgb = C_BLACK
                p.space_after = Pt(6)
update_footer_and_date(s18, 18)
update_footer_and_date(prs.slides[18], 19)

# ==============================================================================
# SLIDE 20: MODEL VALIDATION AND RESAMPLING (SYLLABUS TOPIC 1)
# ==============================================================================
s20 = prs.slides[19]
for shape in s20.shapes:
    if shape.has_text_frame:
        txt = shape.text_frame.text.strip()
        if shape.name == "object 2" or "Feature Normalization & Validation Protocols" in txt:
            shape.text_frame.clear()
            p = shape.text_frame.paragraphs[0]
            p.text = "Model Validation and Resampling"
            p.font.name = "Times New Roman"
            p.font.size = Pt(22)
            p.font.bold = True
            p.font.color.rgb = C_NAVY
        elif shape.name == "object 5" or "Mathematical Formulation" in txt:
            shape.text_frame.clear()
            p0 = shape.text_frame.paragraphs[0]
            p0.text = "Mathematical Formulations of K-Fold Cross-Validation, Bootstrapping & Resampling"
            p0.font.name = "Times New Roman"
            p0.font.size = Pt(17)
            p0.font.bold = True
            p0.font.color.rgb = C_ROYAL
            p0.space_after = Pt(10)

            topic1_bullets = [
                "• K-Fold Cross-Validation Protocol: Partitions dataset D into K=5 disjoint subsets D_k such that D = ⋃ D_k and D_i ∩ D_j = ∅. In iteration k, model trains on D \\ D_k and validates on holdout D_k:",
                "     CV_K = (1 / K) ∑_{k=1}^K Score(f_{(-k)}, D_k)    (Every single observation tested exactly once)",
                "• Stratified K-Fold Guarantee: Normal K-Fold risks class imbalance. Stratification guarantees identical class ratios P(y=c) across all folds (exactly 20 samples per crop class in each of the 5 folds).",
                "• Bootstrapping and Resampling Theory: Non-parametric resampling where n samples are drawn uniformly WITH REPLACEMENT from original dataset of size n. Probability that an observation is NOT chosen:",
                "     P(Not selected in n draws) = (1 - 1/n)^n  -->  lim_{n→∞} (1 - 1/n)^n = 1/e ≈ 0.3679  (36.8%)",
                "• Out-of-Bag (OOB) Validation: Each bootstrap sample captures ~63.2% unique observations. The remaining ~36.8% unpicked samples act as an automatic internal test set, preventing data leakage.",
                "• Ensemble Variance Reduction (Bagging): Random Forest aggregates M=100 decorrelated bootstrap trees. Reduces model variance without inflating bias: Var(f̄) = (1/M)σ² + ((M-1)/M)ρσ²."
            ]
            for item in topic1_bullets:
                p = shape.text_frame.add_paragraph()
                p.text = item
                p.font.name = "Times New Roman"
                p.font.size = Pt(13.5)
                p.font.color.rgb = C_BLACK
                p.space_after = Pt(6)
update_footer_and_date(s20, 20)

# ==============================================================================
# SLIDE 21: MODEL PERFORMANCE EVALUATION (SYLLABUS TOPIC 2)
# ==============================================================================
s21 = prs.slides[20]
for shape in s21.shapes:
    if shape.has_text_frame:
        txt = shape.text_frame.text.strip()
        if shape.name == "object 2" or "Preprocessing & Cross-Validation Benchmarks" in txt:
            shape.text_frame.clear()
            p = shape.text_frame.paragraphs[0]
            p.text = "Model Performance Evaluation"
            p.font.name = "Times New Roman"
            p.font.size = Pt(22)
            p.font.bold = True
            p.font.color.rgb = C_NAVY
        elif shape.name == "object 5" or "Preprocessing Benchmark" in txt or "Performance Metrics" in txt:
            shape.text_frame.clear()
            p0 = shape.text_frame.paragraphs[0]
            p0.text = "Performance Metrics: MSE, Confusion Matrix, Accuracy, Precision, Recall & F1-Score"
            p0.font.name = "Times New Roman"
            p0.font.size = Pt(17)
            p0.font.bold = True
            p0.font.color.rgb = C_ROYAL
            p0.space_after = Pt(10)

            topic2_bullets = [
                "• Mean Squared Error (MSE) for Regression: Measures average squared deviation between actual y and predicted ŷ:",
                "     MSE = (1 / n) ∑_{i=1}^n (y_i - ŷ_i)²    (Eliminates sign cancellation; penalizes large errors quadratically)",
                "   - Tutorial 5 Rainfall Model Evaluation: Test MSE = 184.20 mm² | RMSE = 13.57 mm | MAE = 9.84 mm | R² = 0.824",
                "• The Confusion Matrix: 2×2 and Multi-Class 22×22 contingency table mapping predictions against true ground truth:",
                "   - True Positives (TP), True Negatives (TN), False Positives (FP / Type I Error), False Negatives (FN / Type II Error)",
                "   - Agronomic Risk: Type I = False alarm (unnecessary fertilizer cost/toxicity); Type II = Missed deficiency (crop death!)",
                "• Classification Metrics Formulation:",
                "   - Accuracy = (TP + TN) / Total  |  Precision = TP / (TP + FP)  |  Recall = TP / (TP + FN)",
                "   - F1-Score (Harmonic Mean): F1 = 2 × (Precision × Recall) / (Precision + Recall)  (Prevents majority-class bias)",
                "• 5-Fold Stratified Cross-Validation Benchmark on 2,200 Observations:",
                "   - Fold 1: 99.43% | Fold 2: 99.15% | Fold 3: 99.72% | Fold 4: 98.86% | Fold 5: 99.43%",
                "   - Overall Mean CV Accuracy = 99.32% ± 0.31% (low variance demonstrates high generalizability)"
            ]
            for item in topic2_bullets:
                p = shape.text_frame.add_paragraph()
                p.text = item
                p.font.name = "Times New Roman"
                p.font.size = Pt(13)
                p.font.color.rgb = C_BLACK
                p.space_after = Pt(5)
update_footer_and_date(s21, 21)

# ==============================================================================
# SLIDE 22: OBJECTIVE 2 OVERVIEW (REGRESSION & CLASSIFICATION MODELS)
# ==============================================================================
s22 = prs.slides[21]
for shape in s22.shapes:
    if shape.has_text_frame:
        txt = shape.text_frame.text.strip()
        if "Dual-Engine Cascaded Machine Learning Framework" in txt or "Edge-Deployable Distillation" in txt:
            shape.text_frame.clear()
            p0 = shape.text_frame.paragraphs[0]
            p0.text = "Regression and Classification Models — Objective 2"
            p0.font.name = "Times New Roman"
            p0.font.size = Pt(19)
            p0.font.bold = True
            p0.font.color.rgb = C_NAVY
            p0.space_after = Pt(12)

            o2_body = [
                "Our predictive architecture unifies both regression and multi-class classification models across sequential agricultural decision stages:",
                "• Multiple Linear Regression (T5): Predicts continuous regional rainfall from 6 simultaneous agro-climatic predictors (N, P, K, Temp, Humidity, pH) via analytical Ordinary Least Squares (OLS).",
                "• Logistic Regression (T6): Establishes baseline classification by mapping linear hyperplanes through Sigmoid and Softmax activations to compute calibrated crop probabilities.",
                "• Multi-Class Crop Recommendation Ensemble: Random Forest (M=100 estimators) and Decision Tree (CART) predicting optimal crop among 22 distinct varieties with 99.32% test accuracy.",
                "• Crop-Conditioned Fertilizer Nutrient Predictor: Conditions fertilizer recommendations on predicted crop nutritional demands, soil type, and moisture across 7 target chemical compounds.",
                "• Model Prediction & Evaluation: Sub-15ms inference latency, verified through exhaustive holdout tests, confusion matrices, and model comparison benchmarks."
            ]
            for item in o2_body:
                p = shape.text_frame.add_paragraph()
                p.text = item
                p.font.name = "Times New Roman"
                p.font.size = Pt(14)
                p.font.color.rgb = C_BLACK
                p.space_after = Pt(6)
update_footer_and_date(s22, 22)
update_footer_and_date(prs.slides[22], 23)

# ==============================================================================
# SLIDE 24: REGRESSION & CLASSIFICATION MATHEMATICAL FOUNDATIONS
# ==============================================================================
s24 = prs.slides[23]
for shape in s24.shapes:
    if shape.has_text_frame:
        txt = shape.text_frame.text.strip()
        if shape.name == "object 2" or "Ensemble Modeling & Mathematical Formulation" in txt:
            shape.text_frame.clear()
            p = shape.text_frame.paragraphs[0]
            p.text = "Regression and Classification Models"
            p.font.name = "Times New Roman"
            p.font.size = Pt(22)
            p.font.bold = True
            p.font.color.rgb = C_NAVY
        elif shape.name == "object 5" or "Mathematical Foundations" in txt:
            shape.text_frame.clear()
            p0 = shape.text_frame.paragraphs[0]
            p0.text = "Mathematical Formulations: Multiple Linear Regression & Logistic Regression"
            p0.font.name = "Times New Roman"
            p0.font.size = Pt(17)
            p0.font.bold = True
            p0.font.color.rgb = C_ROYAL
            p0.space_after = Pt(10)

            topic3_math = [
                "• Multiple Linear Regression (T5 - Continuous Rainfall Prediction):",
                "     ŷ = b₀ + b₁X₁(N) + b₂X₂(P) + b₃X₃(K) + b₄X₄(Temp) + b₅X₅(Humidity) + b₆X₆(pH)",
                "   - Ordinary Least Squares (OLS) Normal Equation: β = (X^T X)^{-1} X^T y  (Exact closed-form global minimum)",
                "   - Learned Coefficients: Intercept b₀ = 150.2 mm, Humidity = +4.32, Temperature = +2.14, Soil pH = -0.54",
                "• Logistic Regression (T6 - Multi-Class Crop Classification):",
                "   - Sigmoid Squashing Function: σ(z) = 1 / (1 + e^{-z}),  where z = b₀ + ∑ b_i X_i  (Maps unbounded logits to [0, 1])",
                "   - Softmax Normalization (22 Crops): P(Crop = c | x) = exp(w_c^T x) / ∑_{j=1}^{22} exp(w_j^T x)  (Probabilities sum to 1.0)",
                "   - Multi-Class Log-Loss Objective: L_log = - (1/n) ∑_{i=1}^n ∑_{c=1}^{22} y_ic log(p̂_ic)",
                "• Decision Tree & Random Forest Formulation:",
                "   - Gini Impurity Splitting: I_G(t) = 1 - ∑_c p(c|t)²,   ΔI_G(s, t) = I_G(t) - (N_L/N_t)I_G(t_L) - (N_R/N_t)I_G(t_R)",
                "   - Random Forest Ensemble Aggregation: ŷ_RF = argmax_c (1/M) ∑_{m=1}^M I(ŷ_m(x) = c)  (Majority vote across 100 trees)"
            ]
            for item in topic3_math:
                p = shape.text_frame.add_paragraph()
                p.text = item
                p.font.name = "Times New Roman"
                p.font.size = Pt(13)
                p.font.color.rgb = C_BLACK
                p.space_after = Pt(5)
update_footer_and_date(s24, 24)

# ==============================================================================
# SLIDE 25: MODEL PREDICTION, EVALUATION & COMPARISON OF CLASSIFICATION MODELS
# ==============================================================================
s25 = prs.slides[24]
for shape in s25.shapes:
    if shape.has_text_frame:
        txt = shape.text_frame.text.strip()
        if shape.name == "object 2" or "Model Benchmarks & Performance Metrics" in txt:
            shape.text_frame.clear()
            p = shape.text_frame.paragraphs[0]
            p.text = "Model Prediction & Comparison of Models"
            p.font.name = "Times New Roman"
            p.font.size = Pt(22)
            p.font.bold = True
            p.font.color.rgb = C_NAVY
        elif shape.name == "object 5" or "Comprehensive Experimental Evaluation" in txt:
            shape.text_frame.clear()
            p0 = shape.text_frame.paragraphs[0]
            p0.text = "Model Prediction Pipeline, Evaluation Benchmarks & Comparison of Classification Models"
            p0.font.name = "Times New Roman"
            p0.font.size = Pt(17)
            p0.font.bold = True
            p0.font.color.rgb = C_ROYAL
            p0.space_after = Pt(10)

            topic3_benchmarks = [
                "• End-to-End Model Prediction Pipeline (Real-Time Inference):",
                "   - Ingestion: Vector x = [N=90, P=42, K=43, Temp=20.8°C, Humidity=82%, pH=6.5, Rain=202.9mm]",
                "   - Preprocessing: Standardized via fitted scaler z = (x - μ_train) / σ_train  --> Stage 1 Multi-Class Classifier",
                "   - Prediction Output: Crop = Rice (99.4% Confidence)  --> Stage 2 Fertilizer Engine: Urea (50 kg/ha N-boost)  (Latency: 2.1 ms)",
                "• Comprehensive Comparison of Classification Models (Holdout Test N = 440, 20% Unseen Data):",
                "   - Random Forest Classifier (Ensemble): 99.32% Accuracy | Precision: 0.994 | Recall: 0.993 | Macro F1: 0.993 (Winner)",
                "   - Decision Tree Classifier (CART):      98.18% Accuracy | Precision: 0.983 | Recall: 0.982 | Macro F1: 0.982",
                "   - K-Nearest Neighbors (k=5):             97.73% Accuracy | Precision: 0.979 | Recall: 0.977 | Macro F1: 0.977",
                "   - Logistic Regression (Baseline):        95.23% Accuracy | Precision: 0.955 | Recall: 0.952 | Macro F1: 0.954",
                "• Inductive Bias & Tradeoffs: Linear Logistic Regression forms flat hyperplanes; Decision Trees create axis-aligned boxes (prone to overfitting); Random Forest aggregates 100 decorrelated trees via Bagging, achieving lowest generalization error.",
                "• Agronomic Category Breakdown: Cereals F1: 0.99 | Legumes F1: 1.00 | Cash Crops F1: 0.99 | Fruits F1: 1.00",
                "• Fertilizer Prediction Evaluation: 98.90% Accuracy across 7 target formulations with zero cross-nutrient errors."
            ]
            for item in topic3_benchmarks:
                p = shape.text_frame.add_paragraph()
                p.text = item
                p.font.name = "Times New Roman"
                p.font.size = Pt(13)
                p.font.color.rgb = C_BLACK
                p.space_after = Pt(5)
update_footer_and_date(s25, 25)

# Update footers on remaining slides (26 to 30)
for i in range(25, len(prs.slides)):
    update_footer_and_date(prs.slides[i], i + 1)

# ==============================================================================
# SLIDE 30: CONCLUSION SLIDE (UPDATE TO REVIEW II CONCLUDED)
# ==============================================================================
s30 = prs.slides[29]
for shape in s30.shapes:
    if shape.has_text_frame:
        txt = shape.text_frame.text.strip()
        if "Comprehensive Project Viva Voce" in txt or "Candidate Names:" in txt:
            shape.text_frame.clear()
            p0 = shape.text_frame.paragraphs[0]
            p0.text = "AI-Driven Precision Agriculture: Crop Recommendation & Fertilizer Prediction"
            p0.font.name = "Times New Roman"
            p0.font.size = Pt(20)
            p0.font.bold = True
            p0.font.color.rgb = C_NAVY
            p0.space_after = Pt(8)

            concl_lines = [
                "PROJECT REVIEW II EVALUATION CONCLUDED",
                "Candidate Names: Debjit Das (RA2411056010276) | Anshumaan Das (RA2411056010283)",
                "B.Tech Computer Science and Engineering • School of Computing",
                "SRM Institute of Science and Technology, Kattankulathur",
                "",
                "Summary of Review II Milestones Achieved:",
                "✔ Model Validation & Resampling: 5-Fold Stratified CV (99.32% ± 0.31%), Bootstrapping & OOB Formulation.",
                "✔ Performance Evaluation: MSE (184.20 mm²), Confusion Matrix analysis, Precision, Recall, and F1-Score balance.",
                "✔ Supervised Models: Multiple Linear Regression (T5 OLS) & Logistic Regression (T6 Sigmoid/Softmax Log-Loss).",
                "✔ Comparative Benchmark: Random Forest established as the superior architecture over DT, KNN, and Logistic Regression.",
                "",
                "THANK YOU — OPEN FOR QUESTIONS & COMMITTEE DISCUSSION"
            ]
            for cl in concl_lines:
                p = shape.text_frame.add_paragraph()
                p.text = cl
                p.font.name = "Times New Roman"
                p.font.size = Pt(12)
                p.font.bold = (cl.startswith("PROJECT REVIEW") or cl.startswith("THANK YOU") or cl.startswith("Summary"))
                p.font.color.rgb = C_ROYAL if (cl.startswith("PROJECT REVIEW") or cl.startswith("THANK YOU")) else C_BLACK
                p.space_after = Pt(3)
update_footer_and_date(s30, 30)

prs.save(DEST_PPTX)
print(f"[OK] Successfully saved updated presentation to {DEST_PPTX} (30 slides).")

# Export to PDF via PowerPoint COM
print("[INFO] Exporting updated presentation to PDF via PowerPoint COM...")
ppt_app = win32com.client.Dispatch("PowerPoint.Application")
deck = ppt_app.Presentations.Open(os.path.abspath(DEST_PPTX), WithWindow=False)
deck.SaveAs(os.path.abspath(DEST_PDF), 32)
deck.Close()
ppt_app.Quit()
print(f"[ALL DONE] Generated {DEST_PDF} successfully ({os.path.getsize(DEST_PDF):,} bytes).")

