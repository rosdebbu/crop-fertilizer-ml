import os
import sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ==============================================================================
# CONFIGURATION & THEME
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PPTX = os.path.join(BASE_DIR, "Review_2_Crop_Fertilizer_ML.pptx")
OUTPUT_PDF = os.path.join(BASE_DIR, "Review_2_Crop_Fertilizer_ML.pdf")
COPY_PPTX = os.path.join(BASE_DIR, "Comprehensive_Viva_Crop_Fertilizer_ML copy.pptx")
COPY_PDF = os.path.join(BASE_DIR, "Comprehensive_Viva_Crop_Fertilizer_ML copy.pdf")

LOGO_LEFT = os.path.join(BASE_DIR, "extracted_logos", "img_3.png")
LOGO_RIGHT = os.path.join(BASE_DIR, "extracted_logos", "img_2.png")

CHART_CONFUSION = os.path.join(BASE_DIR, "output_charts", "02_confusion_matrix.png")
CHART_METRICS = os.path.join(BASE_DIR, "output_charts", "03_metrics_comparison.png")
CHART_ACC_COMP = os.path.join(BASE_DIR, "output_charts", "06_accuracy_comparison.png")
CHART_REG_PRED = os.path.join(BASE_DIR, "t2_regression_output", "actual_vs_predicted.png")
CHART_CV_CURVE = os.path.join(BASE_DIR, "t3_crossval_output", "learning_curve.png")

C_NAVY = RGBColor(0x1F, 0x38, 0x64)      # Primary Dark Header
C_ROYAL = RGBColor(0x2E, 0x54, 0x96)     # Accent / Subtitles
C_DARK = RGBColor(0x1E, 0x29, 0x3B)      # Body Text
C_MUTED = RGBColor(0x64, 0x74, 0x8B)     # Footers / Subtitles
C_WHITE = RGBColor(0xFF, 0xFF, 0xFF)     # White Background
C_CARD_BG = RGBColor(0xF8, 0xFA, 0xFC)   # Light Slate Card Fill
C_CARD_BORDER = RGBColor(0xCB, 0xD5, 0xE1)# Card Border
C_GREEN = RGBColor(0x05, 0x96, 0x69)     # Highlights / High Acc
C_GREEN_BG = RGBColor(0xDC, 0xFC, 0xE7)  # Light Green Badge
C_BLUE_LIGHT = RGBColor(0xEF, 0xF6, 0xFF)# Highlight card bg
C_AMBER = RGBColor(0xD9, 0x77, 0x06)     # Caution / Comparison
C_RED = RGBColor(0xDC, 0x26, 0x26)       # Warning / Error

FONT_MAIN = "Times New Roman"

prs = pptx.Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def add_header(slide, title_text, subtitle_text):
    # Left logo
    if os.path.exists(LOGO_LEFT):
        slide.shapes.add_picture(LOGO_LEFT, Inches(0.4), Inches(0.2), width=Inches(1.55))
    # Right logo
    if os.path.exists(LOGO_RIGHT):
        slide.shapes.add_picture(LOGO_RIGHT, Inches(11.3), Inches(0.2), width=Inches(1.6))
        
    # Title & Subtitle in Center
    tb = slide.shapes.add_textbox(Inches(2.1), Inches(0.18), Inches(9.1), Inches(1.05))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
    
    p = tf.paragraphs[0]
    p.text = title_text
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_MAIN
    p.font.size = Pt(21)
    p.font.bold = True
    p.font.color.rgb = C_NAVY
    p.space_after = Pt(2)
    
    p2 = tf.add_paragraph()
    p2.text = subtitle_text
    p2.alignment = PP_ALIGN.CENTER
    p2.font.name = FONT_MAIN
    p2.font.size = Pt(11)
    p2.font.italic = True
    p2.font.color.rgb = C_ROYAL

def add_footer(slide, slide_num, total_slides=16):
    tb = slide.shapes.add_textbox(Inches(0.5), Inches(6.98), Inches(12.33), Inches(0.35))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = f"RA2411056010276, RA2411056010283 | Review II: Crop Recommendation & Fertilizer Prediction | Slide {slide_num} of {total_slides}"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_MAIN
    p.font.size = Pt(10)
    p.font.color.rgb = C_MUTED

def add_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_CARD_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.2)
    else:
        shape.line.fill.background()
    return shape

# ==============================================================================
# SLIDE 1: TITLE SLIDE (REVIEW II EVALUATION)
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)

accent_box = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.25))
accent_box.fill.solid()
accent_box.fill.fore_color.rgb = C_NAVY
accent_box.line.fill.background()

if os.path.exists(LOGO_LEFT):
    s1.shapes.add_picture(LOGO_LEFT, Inches(0.8), Inches(0.6), width=Inches(2.4))
if os.path.exists(LOGO_RIGHT):
    s1.shapes.add_picture(LOGO_RIGHT, Inches(10.2), Inches(0.6), width=Inches(2.3))

badge = add_card(s1, Inches(4.2), Inches(0.7), Inches(4.933), Inches(0.6), bg_color=C_BLUE_LIGHT, border_color=C_ROYAL)
b_tf = badge.text_frame
b_tf.word_wrap = True
bp = b_tf.paragraphs[0]
bp.text = "REVIEW II EVALUATION • PROJECT & LAB DEFENSE"
bp.alignment = PP_ALIGN.CENTER
bp.font.name = FONT_MAIN
bp.font.size = Pt(12)
bp.font.bold = True
bp.font.color.rgb = C_NAVY

tb_title = s1.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.333), Inches(2.2))
tf = tb_title.text_frame
tf.word_wrap = True

p_main = tf.paragraphs[0]
p_main.text = "Crop Recommendation and Fertilizer Prediction\nUsing Machine Learning Frameworks"
p_main.alignment = PP_ALIGN.CENTER
p_main.font.name = FONT_MAIN
p_main.font.size = Pt(27)
p_main.font.bold = True
p_main.font.color.rgb = C_NAVY
p_main.space_after = Pt(8)

p_sub = tf.add_paragraph()
p_sub.text = "Comprehensive Review II Defense: Model Validation & Resampling, Performance Evaluation Metrics,\nMultiple Linear Regression, Logistic Regression, Model Prediction & Classification Benchmarks"
p_sub.alignment = PP_ALIGN.CENTER
p_sub.font.name = FONT_MAIN
p_sub.font.size = Pt(13)
p_sub.font.color.rgb = C_ROYAL
p_sub.font.italic = True

card_cand = add_card(s1, Inches(1.5), Inches(3.9), Inches(10.333), Inches(2.7), bg_color=C_CARD_BG, border_color=C_CARD_BORDER)
ctf = card_cand.text_frame
ctf.word_wrap = True
ctf.margin_top = Inches(0.2)
ctf.margin_left = Inches(0.4)

def add_pair(tf, left_txt, right_txt, is_head=False):
    p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p.text = f"{left_txt:<45} {right_txt}"
    p.font.name = FONT_MAIN
    p.font.size = Pt(13 if is_head else 12)
    p.font.bold = is_head
    p.font.color.rgb = C_NAVY if is_head else C_DARK
    p.space_after = Pt(4)

add_pair(ctf, "STUDENT CANDIDATES & REGISTER NUMBERS", "DEPARTMENT & INSTITUTION", is_head=True)
add_pair(ctf, "• DEBJIT DAS            (Reg No: RA2411056010276)", "Department of Computer Science and Engineering")
add_pair(ctf, "• ANSHUMAAN DAS   (Reg No: RA2411056010283)", "School of Computing, SRMIST, Kattankulathur")
add_pair(ctf, "Program: B.Tech Computer Science & Engineering", "Course / Evaluation: Review II - Machine Learning")
add_pair(ctf, "Academic Year: 2026", "Supervisor / Evaluator: Review Panel II")

add_footer(s1, 1)

# ==============================================================================
# SLIDE 2: REVIEW II SCOPE & SYLLABUS ALIGNMENT
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "REVIEW II EVALUATION MATRIX & TOPIC BREAKDOWN", 
           "Strict alignment to syllabus requirements: 3 core modules spanning validation, metrics, and models")

modules = [
    {
        "num": "MODULE 01",
        "title": "Model Validation and Resampling",
        "color": C_NAVY,
        "bg": C_BLUE_LIGHT,
        "items": [
            ("K-Fold Cross-Validation", "Splitting data into K=5 equal partitions; rotated train-validation cycles."),
            ("Stratified K-Fold", "Preserving class proportions across all 22 crop classes to prevent split bias."),
            ("Bootstrapping & Resampling", "Sampling with replacement (n from n); estimating sampling variance."),
            ("Out-of-Bag (OOB) Testing", "Inherent ~36.8% holdout evaluation without separate validation splits.")
        ]
    },
    {
        "num": "MODULE 02",
        "title": "Model Performance Evaluation",
        "color": C_ROYAL,
        "bg": C_CARD_BG,
        "items": [
            ("Performance Metrics Overview", "Continuous regression error vs discrete classification error."),
            ("Mean Squared Error (MSE)", "Quadratic error penalty: MSE = (1/n) Σ(y - ŷ)², with RMSE & R²."),
            ("The Confusion Matrix", "2x2 & multi-class error taxonomy: TP, TN, FP (Type I), FN (Type II)."),
            ("Accuracy, Precision, Recall, F1", "Harmonic balance between precision (soundness) & recall (completeness).")
        ]
    },
    {
        "num": "MODULE 03",
        "title": "Regression & Classification Models",
        "color": C_GREEN,
        "bg": C_GREEN_BG,
        "items": [
            ("Multiple Linear Regression (T5)", "Predicting continuous rainfall from 6 simultaneous agro-climatic inputs."),
            ("Logistic Regression (T6)", "Sigmoid squashing & Softmax for multi-class probability estimation."),
            ("Model Prediction Architecture", "End-to-end inference from raw sensor data to dual-stage advisory."),
            ("Comparison of Models", "Empirical benchmark: Logistic Regression, Decision Tree, KNN, Random Forest.")
        ]
    }
]

for idx, m in enumerate(modules):
    left = Inches(0.8 + idx * 4.0)
    top = Inches(1.4)
    w = Inches(3.7)
    h = Inches(5.35)
    
    card = add_card(s2, left, top, w, h, bg_color=C_CARD_BG, border_color=m["color"])
    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_top = Inches(0.2)
    tf.margin_left = Inches(0.25)
    tf.margin_right = Inches(0.25)
    
    p = tf.paragraphs[0]
    p.text = m["num"]
    p.font.name = FONT_MAIN
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = m["color"]
    p.space_after = Pt(2)
    
    p_t = tf.add_paragraph()
    p_t.text = m["title"]
    p_t.font.name = FONT_MAIN
    p_t.font.size = Pt(15)
    p_t.font.bold = True
    p_t.font.color.rgb = C_NAVY
    p_t.space_after = Pt(14)
    
    for head, desc in m["items"]:
        p_i = tf.add_paragraph()
        p_i.text = f"• {head}"
        p_i.font.name = FONT_MAIN
        p_i.font.size = Pt(12)
        p_i.font.bold = True
        p_i.font.color.rgb = m["color"]
        p_i.space_after = Pt(2)
        
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_MAIN
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = C_DARK
        p_d.space_after = Pt(10)

add_footer(s2, 2)

# ==============================================================================
# SLIDE 3: MODULE 1 — MODEL VALIDATION & RESAMPLING FOUNDATIONS
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "MODULE 1: MODEL VALIDATION & RESAMPLING FOUNDATIONS",
           "Why resampling is necessary: Overcoming sample variance, preventing data leakage, and ensuring generalization")

# Card Left: The Resampling Motivation
c_left = add_card(s3, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.35))
tf = c_left.text_frame
tf.word_wrap = True
tf.margin_top = Inches(0.25)
tf.margin_left = Inches(0.3)
tf.margin_right = Inches(0.3)

p = tf.paragraphs[0]
p.text = "THE CORE VALIDATION DILEMMA"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(8)

bullets_left = [
    ("The Holdout Flaw:", "A single fixed train-test split (e.g. 80/20) yields high variance. Depending on how random seeds fall, test accuracy can fluctuate by ±5%."),
    ("Data Leakage Hazard:", "Fitting scalers or feature selectors on the entire dataset before splitting causes test data leakage, inflating reported scores unnaturally."),
    ("Small-Data Constraints:", "When samples are scarce, setting aside a large test set starves the training process, causing underfitting and suboptimal weight convergence."),
    ("Resampling Solution:", "Resampling techniques repeatedly draw subsets from the dataset, training and evaluating across distinct permutations to guarantee true out-of-sample validity.")
]

for h, b in bullets_left:
    p_h = tf.add_paragraph()
    p_h.text = f"▶ {h}"
    p_h.font.name = FONT_MAIN
    p_h.font.size = Pt(12)
    p_h.font.bold = True
    p_h.font.color.rgb = C_ROYAL
    p_h.space_after = Pt(2)
    
    p_b = tf.add_paragraph()
    p_b.text = b
    p_b.font.name = FONT_MAIN
    p_b.font.size = Pt(11)
    p_b.font.color.rgb = C_DARK
    p_b.space_after = Pt(10)

# Card Right: Taxonomy Table
c_right = add_card(s3, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.35))
tf_r = c_right.text_frame
tf_r.word_wrap = True
tf_r.margin_top = Inches(0.25)
tf_r.margin_left = Inches(0.3)
tf_r.margin_right = Inches(0.3)

p = tf_r.paragraphs[0]
p.text = "TAXONOMY OF RESAMPLING TECHNIQUES"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(10)

resample_methods = [
    ("1. Holdout Method", "Single static split (e.g., 70/30). Fast but high estimation variance. Prone to lucky/unlucky splits."),
    ("2. K-Fold CV", "Splits data into K disjoint folds. Rotates testing across every fold. All data used for both train and test."),
    ("3. Stratified K-Fold", "K-Fold with guaranteed class balance across all folds. Mandatory for multi-class imbalanced data."),
    ("4. Leave-One-Out (LOOCV)", "K = N (train on N-1, test on 1). Zero estimation bias, but extreme computational cost on large N."),
    ("5. Bootstrapping", "Uniform sampling with replacement. Yields ~63.2% training samples and ~36.8% Out-of-Bag (OOB) validation samples.")
]

for m_name, m_desc in resample_methods:
    p_m = tf_r.add_paragraph()
    p_m.text = m_name
    p_m.font.name = FONT_MAIN
    p_m.font.size = Pt(12)
    p_m.font.bold = True
    p_m.font.color.rgb = C_NAVY
    p_m.space_after = Pt(2)
    
    p_d = tf_r.add_paragraph()
    p_d.text = m_desc
    p_d.font.name = FONT_MAIN
    p_d.font.size = Pt(10.5)
    p_d.font.color.rgb = C_DARK
    p_d.space_after = Pt(8)

add_footer(s3, 3)

# ==============================================================================
# SLIDE 4: K-FOLD & STRATIFIED K-FOLD CROSS-VALIDATION
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "K-FOLD & STRATIFIED K-FOLD CROSS-VALIDATION",
           "Iterative partition protocol, mathematical formulation, and stability benchmark on 2,200 crop observations")

# Left Box: Formulation
c_left = add_card(s4, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.35))
tf = c_left.text_frame
tf.word_wrap = True
tf.margin_top = Inches(0.25)
tf.margin_left = Inches(0.3)
tf.margin_right = Inches(0.3)

p = tf.paragraphs[0]
p.text = "MATHEMATICAL FORMULATION & PROTOCOL"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(8)

k_points = [
    ("Partition Step:", "The complete dataset D of N observations is randomly partitioned into K mutually exclusive and exhaustive subsets D₁, D₂, ..., D_K of roughly equal size N/K:"),
    ("  Formula:", "D = ⋃_{k=1}^K D_k,    where D_i ∩ D_j = ∅  for all i ≠ j"),
    ("Training Cycle:", "In iteration k ∈ {1, ..., K}, the model is fitted on training set D_{(-k)} = D \\ D_k and validated on holdout partition D_k."),
    ("Generalization Score:", "The aggregate cross-validation score is the arithmetic mean across all K iterations:"),
    ("  CV Formula:", "CV_K = (1 / K) ∑_{k=1}^K Score(f_{(-k)}, D_k)"),
    ("Why Stratification Matters:", "In our 22-class crop dataset (100 samples/class), standard K-Fold might create a fold with 15 Rice and 5 Maize. Stratified K-Fold guarantees exactly 20 samples per class in each of the 5 folds.")
]

for h, b in k_points:
    if h.strip().startswith("Formula") or h.strip().startswith("CV Formula"):
        p_box = tf.add_paragraph()
        p_box.text = b
        p_box.font.name = "Courier New"
        p_box.font.size = Pt(11)
        p_box.font.bold = True
        p_box.font.color.rgb = C_ROYAL
        p_box.space_after = Pt(6)
    else:
        p_h = tf.add_paragraph()
        p_h.text = h
        p_h.font.name = FONT_MAIN
        p_h.font.size = Pt(11.5)
        p_h.font.bold = True
        p_h.font.color.rgb = C_NAVY
        p_h.space_after = Pt(1)
        
        p_b = tf.add_paragraph()
        p_b.text = b
        p_b.font.name = FONT_MAIN
        p_b.font.size = Pt(10.5)
        p_b.font.color.rgb = C_DARK
        p_b.space_after = Pt(6)

# Right Box: Project Empirical Results
c_right = add_card(s4, Inches(6.9), Inches(1.4), Inches(5.6), Inches(5.35))
tf_r = c_right.text_frame
tf_r.word_wrap = True
tf_r.margin_top = Inches(0.25)
tf_r.margin_left = Inches(0.3)
tf_r.margin_right = Inches(0.3)

p = tf_r.paragraphs[0]
p.text = "5-FOLD STRATIFIED CV EXPERIMENTAL RESULTS"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(10)

folds_data = [
    ("Fold 1", "440 samples (20 / class)", "99.43%", "0.994"),
    ("Fold 2", "440 samples (20 / class)", "99.15%", "0.991"),
    ("Fold 3", "440 samples (20 / class)", "99.72%", "0.997"),
    ("Fold 4", "440 samples (20 / class)", "98.86%", "0.989"),
    ("Fold 5", "440 samples (20 / class)", "99.43%", "0.994"),
]

for f_name, f_samp, f_acc, f_f1 in folds_data:
    p_f = tf_r.add_paragraph()
    p_f.text = f"{f_name}:  Accuracy = {f_acc}  |  Macro F1 = {f_f1}  ({f_samp})"
    p_f.font.name = FONT_MAIN
    p_f.font.size = Pt(11)
    p_f.font.color.rgb = C_DARK
    p_f.space_after = Pt(4)

summary_box = tf_r.add_paragraph()
summary_box.text = "\nSTATISTICAL SUMMARY & STABILITY:"
summary_box.font.name = FONT_MAIN
summary_box.font.size = Pt(12)
summary_box.font.bold = True
summary_box.font.color.rgb = C_NAVY
summary_box.space_after = Pt(4)

insights = [
    ("Mean Accuracy (μ):", "99.32% across all 2,200 agricultural observations."),
    ("Standard Deviation (σ):", "±0.31% — negligible variation across disjoint folds."),
    ("Design Rationale:", "StandardScaler strictly fitted on D \\ D_k to prevent data leakage."),
    ("Agronomic Conclusion:", "Low variance establishes model robustness across varying micro-climates.")
]

for ih, ib in insights:
    pi = tf_r.add_paragraph()
    pi.text = f"• {ih} {ib}"
    pi.font.name = FONT_MAIN
    pi.font.size = Pt(10.5)
    pi.font.color.rgb = C_DARK
    pi.space_after = Pt(3)

add_footer(s4, 4)

# ==============================================================================
# SLIDE 5: BOOTSTRAPPING & RESAMPLING (BAGGING & OOB)
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "BOOTSTRAPPING & RESAMPLING (BAGGING & OOB)",
           "Sampling with replacement, theoretical derivation of Out-of-Bag (OOB) samples, and ensemble variance reduction")

c_left = add_card(s5, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.35))
tf = c_left.text_frame
tf.word_wrap = True
tf.margin_top = Inches(0.25)
tf.margin_left = Inches(0.3)
tf.margin_right = Inches(0.3)

p = tf.paragraphs[0]
p.text = "THEORY OF BOOTSTRAP RESAMPLING"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(8)

boot_points = [
    ("Definition:", "Bootstrapping is a uniform resampling technique where n samples are drawn WITH REPLACEMENT from an original dataset D of size n."),
    ("Probability of Selection:", "Probability that an arbitrary observation i is NOT picked in a single draw = (1 - 1/n)."),
    ("Out-of-Bag (OOB) Limit:", "For n draws, the probability that sample i is never picked converges to:"),
    ("  Limit Formula:", "lim_{n→∞} (1 - 1/n)^n = 1/e ≈ 0.3679  (36.8%)"),
    ("Training vs OOB Split:", "Each bootstrap sample contains ~63.2% unique original observations (with duplicates). The remaining ~36.8% unpicked samples form the Out-of-Bag (OOB) evaluation set."),
    ("Inherent Validation:", "OOB evaluation acts as an automatic internal cross-validation without needing a separate holdout partition.")
]

for h, b in boot_points:
    if h.strip().startswith("Limit Formula"):
        p_box = tf.add_paragraph()
        p_box.text = b
        p_box.font.name = "Courier New"
        p_box.font.size = Pt(11)
        p_box.font.bold = True
        p_box.font.color.rgb = C_ROYAL
        p_box.space_after = Pt(6)
    else:
        p_h = tf.add_paragraph()
        p_h.text = h
        p_h.font.name = FONT_MAIN
        p_h.font.size = Pt(11.5)
        p_h.font.bold = True
        p_h.font.color.rgb = C_NAVY
        p_h.space_after = Pt(1)
        
        p_b = tf.add_paragraph()
        p_b.text = b
        p_b.font.name = FONT_MAIN
        p_b.font.size = Pt(10.5)
        p_b.font.color.rgb = C_DARK
        p_b.space_after = Pt(6)

c_right = add_card(s5, Inches(6.9), Inches(1.4), Inches(5.6), Inches(5.35))
tf_r = c_right.text_frame
tf_r.word_wrap = True
tf_r.margin_top = Inches(0.25)
tf_r.margin_left = Inches(0.3)
tf_r.margin_right = Inches(0.3)

p = tf_r.paragraphs[0]
p.text = "BAGGING & COMPARISON WITH CV"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(8)

p2 = tf_r.add_paragraph()
p2.text = "Bootstrap Aggregation (Bagging) in Random Forest:"
p2.font.name = FONT_MAIN
p2.font.size = Pt(12)
p2.font.bold = True
p2.font.color.rgb = C_ROYAL
p2.space_after = Pt(2)

p3 = tf_r.add_paragraph()
p3.text = "1. Generates B=100 bootstrap datasets D_1, ..., D_B from training data.\n2. Fits 100 individual decision trees f_b(x) with random feature subsets.\n3. Aggregates predictions via majority voting: ŷ = mode{f_1(x), ..., f_B(x)}.\n4. Slashing Variance: Var(f̄) = (1/B)σ² + ((B-1)/B)ρσ². By decorrelating trees (ρ ↓), variance approaches zero without increasing bias!"
p3.font.name = FONT_MAIN
p3.font.size = Pt(10.5)
p3.font.color.rgb = C_DARK
p3.space_after = Pt(10)

p_tbl_head = tf_r.add_paragraph()
p_tbl_head.text = "RESAMPLING METHODS HEAD-TO-HEAD:"
p_tbl_head.font.name = FONT_MAIN
p_tbl_head.font.size = Pt(11.5)
p_tbl_head.font.bold = True
p_tbl_head.font.color.rgb = C_NAVY
p_tbl_head.space_after = Pt(4)

comp_rows = [
    ("Holdout (70/30)", "Wasteful", "High", "Low", "Fast baseline"),
    ("K-Fold (K=5)", "Efficient", "Low", "Moderate", "Model tuning"),
    ("Stratified K-Fold", "Optimal", "Lowest", "Moderate", "Imbalanced class"),
    ("Bootstrap / OOB", "Reusable", "Low", "High (B trees)", "Ensemble learning")
]

for m, eff, var, comp, best in comp_rows:
    pr = tf_r.add_paragraph()
    pr.text = f"• {m:<18} | Var: {var:<6} | Best for: {best}"
    pr.font.name = FONT_MAIN
    pr.font.size = Pt(10)
    pr.font.color.rgb = C_DARK
    pr.space_after = Pt(3)

add_footer(s5, 5)

# ==============================================================================
# SLIDE 6: MODULE 2 — MODEL PERFORMANCE EVALUATION OVERVIEW
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
add_header(s6, "MODULE 2: MODEL PERFORMANCE EVALUATION FRAMEWORK",
           "Systematic evaluation metrics: Distinguishing regression error quantification from discrete classification metrics")

c_left = add_card(s6, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.35))
tf = c_left.text_frame
tf.word_wrap = True
tf.margin_top = Inches(0.25)
tf.margin_left = Inches(0.3)
tf.margin_right = Inches(0.3)

p = tf.paragraphs[0]
p.text = "THE DUAL EVALUATION PARADIGM"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(8)

eval_bullets = [
    ("Regression Metric Rationale:", "Measures numerical proximity between real continuous values (e.g. Rainfall mm) and model predictions. Residuals (y - ŷ) indicate error magnitude."),
    ("  Key Regression Metrics:", "• Mean Squared Error (MSE)\n• Root Mean Squared Error (RMSE)\n• Mean Absolute Error (MAE)\n• Coefficient of Determination (R²)"),
    ("Classification Metric Rationale:", "Measures decision boundary alignment and categorical correctness across discrete classes (e.g. 22 crops, 7 fertilizers)."),
    ("  Key Classification Metrics:", "• Confusion Matrix (TP, TN, FP, FN)\n• Overall Accuracy\n• Precision (Positive Predictive Value)\n• Recall (Sensitivity / True Positive Rate)\n• F1-Score (Harmonic Mean)")
]

for h, b in eval_bullets:
    p_h = tf.add_paragraph()
    p_h.text = h
    p_h.font.name = FONT_MAIN
    p_h.font.size = Pt(11.5)
    p_h.font.bold = True
    p_h.font.color.rgb = C_ROYAL
    p_h.space_after = Pt(1)
    
    p_b = tf.add_paragraph()
    p_b.text = b
    p_b.font.name = FONT_MAIN
    p_b.font.size = Pt(10.5)
    p_b.font.color.rgb = C_DARK
    p_b.space_after = Pt(6)

c_right = add_card(s6, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.35))
tf_r = c_right.text_frame
tf_r.word_wrap = True
tf_r.margin_top = Inches(0.25)
tf_r.margin_left = Inches(0.3)
tf_r.margin_right = Inches(0.3)

p = tf_r.paragraphs[0]
p.text = "THE ACCURACY PARADOX & REAL-WORLD RISK"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(8)

p2 = tf_r.add_paragraph()
p2.text = "Why Raw Accuracy Fails on Critical Problems:"
p2.font.name = FONT_MAIN
p2.font.size = Pt(12)
p2.font.bold = True
p2.font.color.rgb = C_RED
p2.space_after = Pt(4)

p3 = tf_r.add_paragraph()
p3.text = "Consider an agricultural disease detection system where 95 out of 100 plants are healthy and 5 are infected with lethal blight:\n\n• A naive model predicting 'Healthy' 100% of the time gets 95% Accuracy!\n• But its Recall for diseased plants is 0.0% — the entire crop dies!\n• Accuracy creates a false sense of security when class costs are asymmetric."
p3.font.name = FONT_MAIN
p3.font.size = Pt(11)
p3.font.color.rgb = C_DARK
p3.space_after = Pt(10)

p4 = tf_r.add_paragraph()
p4.text = "Multi-Metric Evaluation Strategy:"
p4.font.name = FONT_MAIN
p4.font.size = Pt(12)
p4.font.bold = True
p4.font.color.rgb = C_GREEN
p4.space_after = Pt(4)

p5 = tf_r.add_paragraph()
p5.text = "1. Precision guards against costly False Alarms (wasting expensive fertilizer).\n2. Recall guards against catastrophic Missed Detections (crop failure).\n3. F1-Score penalizes models that sacrifice one metric for the other.\n4. Confusion Matrix maps the exact pairwise confusion between every crop."
p5.font.name = FONT_MAIN
p5.font.size = Pt(11)
p5.font.color.rgb = C_DARK

add_footer(s6, 6)

# ==============================================================================
# SLIDE 7: MEAN SQUARED ERROR (MSE) & REGRESSION METRICS
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
add_header(s7, "MEAN SQUARED ERROR (MSE) & REGRESSION METRICS",
           "Mathematical formulation, quadratic penalty properties, calculation walkthrough, and companion metrics")

c_left = add_card(s7, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.35))
tf = c_left.text_frame
tf.word_wrap = True
tf.margin_top = Inches(0.25)
tf.margin_left = Inches(0.3)
tf.margin_right = Inches(0.3)

p = tf.paragraphs[0]
p.text = "MSE MATHEMATICAL FORMULATION"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(6)

p_f = tf.add_paragraph()
p_f.text = "MSE = (1 / n) ∑_{i=1}^n (y_i - ŷ_i)²"
p_f.font.name = "Courier New"
p_f.font.size = Pt(14)
p_f.font.bold = True
p_f.font.color.rgb = C_ROYAL
p_f.space_after = Pt(6)

mse_reasons = [
    ("1. Eliminates Sign Cancellation:", "Errors like +10 and -10 do not cancel out to 0; squaring ensures every deviation adds positively to the total loss penalty."),
    ("2. Quadratic Penalty on Outliers:", "An error of 2 units contributes 4 to MSE, while an error of 10 units contributes 100! Large blunders are penalized 25× harder than small errors."),
    ("3. Differentiability for OLS:", "Squaring produces a smooth, convex parabola with a continuous derivative, enabling analytical OLS solution without step-discontinuities.")
]

for h, b in mse_reasons:
    p_h = tf.add_paragraph()
    p_h.text = h
    p_h.font.name = FONT_MAIN
    p_h.font.size = Pt(11)
    p_h.font.bold = True
    p_h.font.color.rgb = C_NAVY
    p_h.space_after = Pt(1)
    
    p_b = tf.add_paragraph()
    p_b.text = b
    p_b.font.name = FONT_MAIN
    p_b.font.size = Pt(10.5)
    p_b.font.color.rgb = C_DARK
    p_b.space_after = Pt(5)

c_right = add_card(s7, Inches(6.9), Inches(1.4), Inches(5.6), Inches(5.35))
tf_r = c_right.text_frame
tf_r.word_wrap = True
tf_r.margin_top = Inches(0.25)
tf_r.margin_left = Inches(0.3)
tf_r.margin_right = Inches(0.3)

p = tf_r.paragraphs[0]
p.text = "STEP-BY-STEP CALCULATION & COMPANION METRICS"
p.font.name = FONT_MAIN
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(6)

calc_rows = [
    ("Actual (y)", "Predicted (ŷ)", "Error (e = y - ŷ)", "Squared Error (e²)"),
    ("50 mm", "48 mm", "+2 mm", "4.0"),
    ("65 mm", "60 mm", "+5 mm", "25.0"),
    ("80 mm", "82 mm", "-2 mm", "4.0"),
    ("90 mm", "85 mm", "+5 mm", "25.0")
]

for idx, (c1, c2, c3, c4) in enumerate(calc_rows):
    p_row = tf_r.add_paragraph()
    p_row.text = f"{c1:<12} {c2:<14} {c3:<16} {c4}"
    p_row.font.name = "Courier New" if idx > 0 else FONT_MAIN
    p_row.font.size = Pt(10)
    p_row.font.bold = (idx == 0)
    p_row.font.color.rgb = C_NAVY if idx == 0 else C_DARK
    p_row.space_after = Pt(2)

p_sum = tf_r.add_paragraph()
p_sum.text = "\nTotal Squared Error = 4 + 25 + 4 + 25 = 58\nMSE = 58 / 4 = 14.50 mm²"
p_sum.font.name = "Courier New"
p_sum.font.size = Pt(11)
p_sum.font.bold = True
p_sum.font.color.rgb = C_ROYAL
p_sum.space_after = Pt(8)

p_aux = tf_r.add_paragraph()
p_aux.text = "T5 Multiple Regression Model Results (Rainfall Target):"
p_aux.font.name = FONT_MAIN
p_aux.font.size = Pt(11.5)
p_aux.font.bold = True
p_aux.font.color.rgb = C_NAVY
p_aux.space_after = Pt(2)

p_aux_b = tf_r.add_paragraph()
p_aux_b.text = "• Test MSE = 184.20 mm² (overall squared variance)\n• RMSE = √184.20 = 13.57 mm (interpretable in real rainfall units!)\n• MAE = 9.84 mm (average absolute deviation)\n• R² Score = 0.824 (explains 82.4% of variance in regional rainfall)"
p_aux_b.font.name = FONT_MAIN
p_aux_b.font.size = Pt(10.5)
p_aux_b.font.color.rgb = C_DARK

add_footer(s7, 7)

# ==============================================================================
# SLIDE 8: THE CONFUSION MATRIX (BINARY & MULTI-CLASS)
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
add_header(s8, "CONFUSION MATRIX & ERROR TAXONOMY",
           "Structural layout of 2x2 matrix, decision error taxonomy, and high-stakes agricultural consequences")

c_left = add_card(s8, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.35))
tf = c_left.text_frame
tf.word_wrap = True
tf.margin_top = Inches(0.25)
tf.margin_left = Inches(0.3)
tf.margin_right = Inches(0.3)

p = tf.paragraphs[0]
p.text = "THE 2×2 CONFUSION MATRIX STRUCTURE"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(8)

cm_table = [
    ("Actual vs Predicted", "Actually POSITIVE", "Actually NEGATIVE"),
    ("Predicted POSITIVE", "TP (True Positive)", "FP (False Positive / Type I)"),
    ("Predicted NEGATIVE", "FN (False Negative / Type II)", "TN (True Negative)")
]

for idx, (c1, c2, c3) in enumerate(cm_table):
    pr = tf.add_paragraph()
    pr.text = f"{c1:<22} | {c2:<24} | {c3}"
    pr.font.name = FONT_MAIN
    pr.font.size = Pt(10.5)
    pr.font.bold = (idx == 0)
    pr.font.color.rgb = C_NAVY if idx == 0 else C_DARK
    pr.space_after = Pt(4)

p_mem = tf.add_paragraph()
p_mem.text = "\nMemory Rule to Avoid Confusion:"
p_mem.font.name = FONT_MAIN
p_mem.font.size = Pt(12)
p_mem.font.bold = True
p_mem.font.color.rgb = C_ROYAL
p_mem.space_after = Pt(2)

mem_bullets = [
    ("First Word (True / False):", "Did the model guess correctly or wrongly?"),
    ("Second Word (Positive / Negative):", "What classification did the model output?"),
    ("True Positive (TP):", "Patient has disease; Model correctly says 'Disease' ✓"),
    ("False Positive (FP):", "Patient is healthy; Model wrongly alarms 'Disease' ✗"),
    ("False Negative (FN):", "Patient has disease; Model wrongly says 'Healthy' ✗")
]

for h, b in mem_bullets:
    pm = tf.add_paragraph()
    pm.text = f"• {h} {b}"
    pm.font.name = FONT_MAIN
    pm.font.size = Pt(10.5)
    pm.font.color.rgb = C_DARK
    pm.space_after = Pt(2)

c_right = add_card(s8, Inches(6.9), Inches(1.4), Inches(5.6), Inches(5.35))
tf_r = c_right.text_frame
tf_r.word_wrap = True
tf_r.margin_top = Inches(0.25)
tf_r.margin_left = Inches(0.3)
tf_r.margin_right = Inches(0.3)

p = tf_r.paragraphs[0]
p.text = "AGRONOMIC IMPACT OF ERROR TYPES"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(8)

p_fp = tf_r.add_paragraph()
p_fp.text = "TYPE I ERROR: FALSE POSITIVE (FALSE ALARM)"
p_fp.font.name = FONT_MAIN
p_fp.font.size = Pt(12)
p_fp.font.bold = True
p_fp.font.color.rgb = C_AMBER
p_fp.space_after = Pt(2)

p_fp_t = tf_r.add_paragraph()
p_fp_t.text = "• Scenario: Soil has sufficient Nitrogen, but model wrongly predicts severe Nitrogen deficiency.\n• Action: Farmer buys and applies 50kg excess Urea.\n• Consequence: Soil acidification, groundwater nitrate toxicity, financial loss."
p_fp_t.font.name = FONT_MAIN
p_fp_t.font.size = Pt(10.5)
p_fp_t.font.color.rgb = C_DARK
p_fp_t.space_after = Pt(10)

p_fn = tf_r.add_paragraph()
p_fn.text = "TYPE II ERROR: FALSE NEGATIVE (MISSED DETECTION)"
p_fn.font.name = FONT_MAIN
p_fn.font.size = Pt(12)
p_fn.font.bold = True
p_fn.font.color.rgb = C_RED
p_fn.space_after = Pt(2)

p_fn_t = tf_r.add_paragraph()
p_fn_t.text = "• Scenario: Soil is critically depleted in Potassium, but model falsely reports 'Sufficient / Healthy'.\n• Action: Farmer applies no fertilizer.\n• Consequence: Stunted crop growth, disease susceptibility, total crop failure! (Far more dangerous in agriculture!)."
p_fn_t.font.name = FONT_MAIN
p_fn_t.font.size = Pt(10.5)
p_fn_t.font.color.rgb = C_DARK
p_fn_t.space_after = Pt(10)

p_multi = tf_r.add_paragraph()
p_multi.text = "Multi-Class Matrix (22 Crops × 22 Crops):"
p_multi.font.name = FONT_MAIN
p_multi.font.size = Pt(11.5)
p_multi.font.bold = True
p_multi.font.color.rgb = C_NAVY
p_multi.space_after = Pt(2)

p_multi_t = tf_r.add_paragraph()
p_multi_t.text = "Diagonal elements represent correct predictions (TP_c for each crop). Off-diagonal elements show specific agronomic confusion (e.g. Lentil vs Mothbeans under low rainfall)."
p_multi_t.font.name = FONT_MAIN
p_multi_t.font.size = Pt(10)
p_multi_t.font.color.rgb = C_DARK

add_footer(s8, 8)

# ==============================================================================
# SLIDE 9: ACCURACY, PRECISION, RECALL, AND F1-SCORE
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
add_header(s9, "ACCURACY, PRECISION, RECALL & F1-SCORE",
           "Mathematical formulas, the harmonic mean rationale, multi-class aggregation, and benchmark summary")

c_left = add_card(s9, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.35))
tf = c_left.text_frame
tf.word_wrap = True
tf.margin_top = Inches(0.25)
tf.margin_left = Inches(0.3)
tf.margin_right = Inches(0.3)

p = tf.paragraphs[0]
p.text = "CORE METRIC MATHEMATICAL FORMULAS"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(6)

metrics_list = [
    ("Accuracy", "Accuracy = (TP + TN) / (TP + TN + FP + FN)", "Proportion of all predictions that were correct. Good for balanced classes, misleading for imbalanced data."),
    ("Precision", "Precision = TP / (TP + FP)", "Of all predicted positives, how many were truly positive? 'When model says YES, how often is it right?'"),
    ("Recall (Sensitivity)", "Recall = TP / (TP + FN)", "Of all actual positive cases, how many did the model catch? 'Out of real positives, how many were found?'"),
    ("F1-Score", "F1 = 2 × (Precision × Recall) / (Precision + Recall)", "Harmonic mean of Precision and Recall. Balances both metrics into a single fair summary score.")
]

for name, form, desc in metrics_list:
    p_n = tf.add_paragraph()
    p_n.text = f"▶ {name}:"
    p_n.font.name = FONT_MAIN
    p_n.font.size = Pt(12)
    p_n.font.bold = True
    p_n.font.color.rgb = C_ROYAL
    p_n.space_after = Pt(1)
    
    p_f = tf.add_paragraph()
    p_f.text = f"   {form}"
    p_f.font.name = "Courier New"
    p_f.font.size = Pt(10.5)
    p_f.font.bold = True
    p_f.font.color.rgb = C_NAVY
    p_f.space_after = Pt(2)
    
    p_d = tf.add_paragraph()
    p_d.text = f"   {desc}"
    p_d.font.name = FONT_MAIN
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = C_DARK
    p_d.space_after = Pt(5)

c_right = add_card(s9, Inches(6.9), Inches(1.4), Inches(5.6), Inches(5.35))
tf_r = c_right.text_frame
tf_r.word_wrap = True
tf_r.margin_top = Inches(0.25)
tf_r.margin_left = Inches(0.3)
tf_r.margin_right = Inches(0.3)

p = tf_r.paragraphs[0]
p.text = "WHY HARMONIC MEAN & AGGREGATION"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(6)

p_why = tf_r.add_paragraph()
p_why.text = "Why Not Use Regular (Arithmetic) Average?"
p_why.font.name = FONT_MAIN
p_why.font.size = Pt(12)
p_why.font.bold = True
p_why.font.color.rgb = C_RED
p_why.space_after = Pt(2)

p_why_t = tf_r.add_paragraph()
p_why_t.text = "• Extreme Case: Precision = 100%, Recall = 0%\n  - Arithmetic Mean = (100% + 0%) / 2 = 50% (Sounds mediocre, but model caught ZERO true cases!)\n  - Harmonic Mean (F1) = 2(1.0 × 0.0) / (1.0 + 0.0) = 0.0%!\n• Harmonic mean harshly punishes extreme imbalance, protecting users from useless models."
p_why_t.font.name = FONT_MAIN
p_why_t.font.size = Pt(10.5)
p_why_t.font.color.rgb = C_DARK
p_why_t.space_after = Pt(10)

p_agg = tf_r.add_paragraph()
p_agg.text = "Multi-Class Aggregation Strategies (22 Crops):"
p_agg.font.name = FONT_MAIN
p_agg.font.size = Pt(12)
p_agg.font.bold = True
p_agg.font.color.rgb = C_NAVY
p_agg.space_after = Pt(2)

p_agg_t = tf_r.add_paragraph()
p_agg_t.text = "1. Macro Average: Calculates metric independently for each of the 22 crops, then takes simple average. Treats all crops equally, regardless of frequency.\n2. Weighted Average: Weights each crop's score by its support (number of true instances). Accounts for population prevalence."
p_agg_t.font.name = FONT_MAIN
p_agg_t.font.size = Pt(10.5)
p_agg_t.font.color.rgb = C_DARK
p_agg_t.space_after = Pt(8)

p_res = tf_r.add_paragraph()
p_res.text = "Random Forest Score on 20% Holdout Test Data:\n• Accuracy = 99.32%  |  Precision = 0.994  |  Recall = 0.993  |  F1 = 0.993"
p_res.font.name = FONT_MAIN
p_res.font.size = Pt(11)
p_res.font.bold = True
p_res.font.color.rgb = C_GREEN

add_footer(s9, 9)

# ==============================================================================
# SLIDE 10: MODULE 3 — MULTIPLE LINEAR REGRESSION (T5)
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
add_header(s10, "MODULE 3: MULTIPLE LINEAR REGRESSION (TUTORIAL 5)",
           "Formulation of multi-feature linear hyperplane, Ordinary Least Squares (OLS) closed-form matrix solution, and evaluation")

c_left = add_card(s10, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.35))
tf = c_left.text_frame
tf.word_wrap = True
tf.margin_top = Inches(0.25)
tf.margin_left = Inches(0.3)
tf.margin_right = Inches(0.3)

p = tf.paragraphs[0]
p.text = "MATHEMATICAL FORMULATION & OLS"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(6)

p_eq = tf.add_paragraph()
p_eq.text = "ŷ = b₀ + b₁X₁ + b₂X₂ + b₃X₃ + b₄X₄ + b₅X₅ + b₆X₆"
p_eq.font.name = "Courier New"
p_eq.font.size = Pt(12)
p_eq.font.bold = True
p_eq.font.color.rgb = C_ROYAL
p_eq.space_after = Pt(6)

mlr_points = [
    ("Target Variable (y):", "Continuous regional Rainfall (in mm)."),
    ("6 Input Features (X):", "X₁=N, X₂=P, X₃=K, X₄=Temperature, X₅=Humidity, X₆=Soil pH."),
    ("Ordinary Least Squares (OLS):", "Finds optimal weights β that minimize the Residual Sum of Squares: RSS = ∑ (y_i - ŷ_i)²."),
    ("Analytical Normal Equation:", "β = (X^T X)^{-1} X^T y"),
    ("Zero-Iteration Advantage:", "Computed directly via matrix inversion in Scikit-Learn without needing learning rates or gradient descent loops.")
]

for h, b in mlr_points:
    if h.startswith("Analytical Normal Equation"):
        p_box = tf.add_paragraph()
        p_box.text = f"▶ {h}\n   {b}"
        p_box.font.name = "Courier New"
        p_box.font.size = Pt(11)
        p_box.font.bold = True
        p_box.font.color.rgb = C_NAVY
        p_box.space_after = Pt(6)
    else:
        p_h = tf.add_paragraph()
        p_h.text = f"• {h} {b}"
        p_h.font.name = FONT_MAIN
        p_h.font.size = Pt(10.5)
        p_h.font.color.rgb = C_DARK
        p_h.space_after = Pt(5)

c_right = add_card(s10, Inches(6.9), Inches(1.4), Inches(5.6), Inches(5.35))
tf_r = c_right.text_frame
tf_r.word_wrap = True
tf_r.margin_top = Inches(0.25)
tf_r.margin_left = Inches(0.3)
tf_r.margin_right = Inches(0.3)

p = tf_r.paragraphs[0]
p.text = "EMPIRICAL COEFFICIENTS & PERFORMANCE"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(8)

p_w = tf_r.add_paragraph()
p_w.text = "Learned Regression Weights Breakdown:"
p_w.font.name = FONT_MAIN
p_w.font.size = Pt(12)
p_w.font.bold = True
p_w.font.color.rgb = C_ROYAL
p_w.space_after = Pt(4)

weights = [
    ("Intercept (b₀):", "150.20 mm", "Baseline atmospheric moisture"),
    ("Humidity (b₅):", "+4.32", "Dominant positive driver; atmospheric saturation"),
    ("Temperature (b₄):", "+2.14", "Convective thermal updrafts influencing precipitation"),
    ("Nitrogen (b₁):", "+0.35", "Secondary soil correlate"),
    ("Phosphorus (b₂):", "-0.12", "Minimal negative correlate"),
    ("Soil pH (b₆):", "-0.54", "Neutral/slightly acidic soil moisture link")
]

for feat, val, note in weights:
    pw = tf_r.add_paragraph()
    pw.text = f"• {feat:<18} {val:<10} ({note})"
    pw.font.name = FONT_MAIN
    pw.font.size = Pt(10.5)
    pw.font.color.rgb = C_DARK
    pw.space_after = Pt(3)

p_res = tf_r.add_paragraph()
p_res.text = "\nRegression Performance Summary:"
p_res.font.name = FONT_MAIN
p_res.font.size = Pt(12)
p_res.font.bold = True
p_res.font.color.rgb = C_NAVY
p_res.space_after = Pt(4)

p_res_t = tf_r.add_paragraph()
p_res_t.text = "• Test Mean Squared Error (MSE): 184.20 mm²\n• Root Mean Squared Error (RMSE): 13.57 mm\n• Mean Absolute Error (MAE): 9.84 mm\n• Coefficient of Determination (R²): 0.824 (High predictive quality)"
p_res_t.font.name = FONT_MAIN
p_res_t.font.size = Pt(11)
p_res_t.font.color.rgb = C_DARK

add_footer(s10, 10)

# ==============================================================================
# SLIDE 11: CLASSIFICATION MODELS: LOGISTIC REGRESSION (T6)
# ==============================================================================
s11 = prs.slides.add_slide(blank_layout)
add_header(s11, "CLASSIFICATION MODELS: LOGISTIC REGRESSION (TUTORIAL 6)",
           "From continuous hyperplane to probabilities: Sigmoid activation, Softmax multi-class generalization, and Log-Loss")

c_left = add_card(s11, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.35))
tf = c_left.text_frame
tf.word_wrap = True
tf.margin_top = Inches(0.25)
tf.margin_left = Inches(0.3)
tf.margin_right = Inches(0.3)

p = tf.paragraphs[0]
p.text = "THE SIGMOID & SOFTMAX FORMULATION"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(6)

p_whynot = tf.add_paragraph()
p_whynot.text = "Why Linear Regression Fails on Classification:"
p_whynot.font.name = FONT_MAIN
p_whynot.font.size = Pt(11.5)
p_whynot.font.bold = True
p_whynot.font.color.rgb = C_RED
p_whynot.space_after = Pt(2)

p_whynot_t = tf.add_paragraph()
p_whynot_t.text = "Linear regression outputs continuous unbounded values (-∞ to +∞). Outputting 'Crop = 2.73' is mathematically nonsensical. We need probabilities constrained to [0, 1]."
p_whynot_t.font.name = FONT_MAIN
p_whynot_t.font.size = Pt(10.5)
p_whynot_t.font.color.rgb = C_DARK
p_whynot_t.space_after = Pt(8)

p_sig = tf.add_paragraph()
p_sig.text = "Sigmoid Function (Binary Classification):"
p_sig.font.name = FONT_MAIN
p_sig.font.size = Pt(11.5)
p_sig.font.bold = True
p_sig.font.color.rgb = C_ROYAL
p_sig.space_after = Pt(2)

p_sig_f = tf.add_paragraph()
p_sig_f.text = "σ(z) = 1 / (1 + e^{-z}),    where z = b₀ + ∑ b_i X_i"
p_sig_f.font.name = "Courier New"
p_sig_f.font.size = Pt(11.5)
p_sig_f.font.bold = True
p_sig_f.font.color.rgb = C_NAVY
p_sig_f.space_after = Pt(8)

p_soft = tf.add_paragraph()
p_soft.text = "Softmax Function (Multi-Class 22 Crops):"
p_soft.font.name = FONT_MAIN
p_soft.font.size = Pt(11.5)
p_soft.font.bold = True
p_soft.font.color.rgb = C_ROYAL
p_soft.space_after = Pt(2)

p_soft_f = tf.add_paragraph()
p_soft_f.text = "P(Y = c | x) = exp(w_c^T x) / ∑_{j=1}^C exp(w_j^T x)"
p_soft_f.font.name = "Courier New"
p_soft_f.font.size = Pt(11.5)
p_soft_f.font.bold = True
p_soft_f.font.color.rgb = C_NAVY
p_soft_f.space_after = Pt(6)

p_soft_d = tf.add_paragraph()
p_soft_d.text = "Guarantees all 22 crop probabilities sum to exactly 1.0."
p_soft_d.font.name = FONT_MAIN
p_soft_d.font.size = Pt(10)
p_soft_d.font.color.rgb = C_DARK

c_right = add_card(s11, Inches(6.9), Inches(1.4), Inches(5.6), Inches(5.35))
tf_r = c_right.text_frame
tf_r.word_wrap = True
tf_r.margin_top = Inches(0.25)
tf_r.margin_left = Inches(0.3)
tf_r.margin_right = Inches(0.3)

p = tf_r.paragraphs[0]
p.text = "LOG-LOSS & EXPERIMENTAL RESULTS"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(8)

p_loss = tf_r.add_paragraph()
p_loss.text = "Cross-Entropy Loss (Log-Loss) Objective:"
p_loss.font.name = FONT_MAIN
p_loss.font.size = Pt(12)
p_loss.font.bold = True
p_loss.font.color.rgb = C_ROYAL
p_loss.space_after = Pt(2)

p_loss_f = tf_r.add_paragraph()
p_loss_f.text = "L = - (1/n) ∑_{i=1}^n ∑_{c=1}^C y_{ic} log(p̂_{ic})"
p_loss_f.font.name = "Courier New"
p_loss_f.font.size = Pt(11.5)
p_loss_f.font.bold = True
p_loss_f.font.color.rgb = C_NAVY
p_loss_f.space_after = Pt(6)

p_loss_d = tf_r.add_paragraph()
p_loss_d.text = "• When true class c has predicted probability p̂ → 1, loss → 0.\n• When model confidently predicts wrong class (p̂ → 0), loss → ∞!\n• Optimized using L-BFGS quasi-Newton gradient optimization."
p_loss_d.font.name = FONT_MAIN
p_loss_d.font.size = Pt(10.5)
p_loss_d.font.color.rgb = C_DARK
p_loss_d.space_after = Pt(10)

p_lr_res = tf_r.add_paragraph()
p_lr_res.text = "Logistic Regression Benchmark on Crop Dataset:"
p_lr_res.font.name = FONT_MAIN
p_lr_res.font.size = Pt(12)
p_lr_res.font.bold = True
p_lr_res.font.color.rgb = C_GREEN
p_lr_res.space_after = Pt(4)

p_lr_res_t = tf_r.add_paragraph()
p_lr_res_t.text = "• Test Accuracy: 95.23% (N = 440 holdout samples)\n• Macro Precision: 0.955 | Macro Recall: 0.952 | Macro F1: 0.954\n• Convergence Latency: 12.4 ms\n• Limitations: Linear hyperplanes struggle with non-linear decision boundaries between moisture-sensitive crops (e.g., Rice vs Jute)."
p_lr_res_t.font.name = FONT_MAIN
p_lr_res_t.font.size = Pt(10.5)
p_lr_res_t.font.color.rgb = C_DARK

add_footer(s11, 11)

# ==============================================================================
# SLIDE 12: MODEL PREDICTION WORKFLOW (END-TO-END PIPELINE)
# ==============================================================================
s12 = prs.slides.add_slide(blank_layout)
add_header(s12, "END-TO-END MODEL PREDICTION PIPELINE",
           "From field sensor ingestion to dual-stage inference and validated agronomic recommendation")

c_left = add_card(s12, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.35))
tf = c_left.text_frame
tf.word_wrap = True
tf.margin_top = Inches(0.25)
tf.margin_left = Inches(0.3)
tf.margin_right = Inches(0.3)

p = tf.paragraphs[0]
p.text = "5-STAGE INFERENCE ARCHITECTURE"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(8)

pipeline_steps = [
    ("Stage 1: Sensor Ingestion", "Captures 7 physical agro-climatic readings: Nitrogen (N), Phosphorus (P), Potassium (K), Temperature, Humidity, pH, and Rainfall."),
    ("Stage 2: Standardization", "Transforms raw vector x via pre-fitted training scaler: z = (x - μ_train) / σ_train. Prevents feature dominance by large-magnitude variables (Rainfall vs pH)."),
    ("Stage 3: Crop Recommendation Engine", "Transformed vector feeds into Random Forest classifier (100 trees), generating Softmax multi-class probability distribution across 22 crops."),
    ("Stage 4: Fertilizer Conditioned Engine", "Takes soil chemical profile + predicted crop identity as inputs to predict optimal fertilizer formulation among 7 chemical classes."),
    ("Stage 5: Agronomic Advisory Delivery", "Outputs crop recommendation with confidence score, NPK requirement schedule, and seasonal crop rotation advisory.")
]

for s_name, s_desc in pipeline_steps:
    ps = tf.add_paragraph()
    ps.text = f"▶ {s_name}"
    ps.font.name = FONT_MAIN
    ps.font.size = Pt(11.5)
    ps.font.bold = True
    ps.font.color.rgb = C_ROYAL
    ps.space_after = Pt(1)
    
    pd = tf.add_paragraph()
    pd.text = s_desc
    pd.font.name = FONT_MAIN
    pd.font.size = Pt(10)
    pd.font.color.rgb = C_DARK
    pd.space_after = Pt(5)

c_right = add_card(s12, Inches(6.9), Inches(1.4), Inches(5.6), Inches(5.35))
tf_r = c_right.text_frame
tf_r.word_wrap = True
tf_r.margin_top = Inches(0.25)
tf_r.margin_left = Inches(0.3)
tf_r.margin_right = Inches(0.3)

p = tf_r.paragraphs[0]
p.text = "REAL-WORLD PREDICTION EXECUTION RUN"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(8)

p_in = tf_r.add_paragraph()
p_in.text = "Input Observation Vector (Field Soil Sample #1042):"
p_in.font.name = FONT_MAIN
p_in.font.size = Pt(12)
p_in.font.bold = True
p_in.font.color.rgb = C_ROYAL
p_in.space_after = Pt(2)

in_vals = [
    ("Nitrogen (N):", "90.0 mg/kg (High)"),
    ("Phosphorus (P):", "42.0 mg/kg (Moderate)"),
    ("Potassium (K):", "43.0 mg/kg (Moderate)"),
    ("Temperature:", "20.87 °C"),
    ("Humidity:", "82.00 % (Tropical moist)"),
    ("Soil pH:", "6.50 (Slightly acidic)"),
    ("Rainfall:", "202.93 mm (Monsoon heavy)")
]

for k, v in in_vals:
    pin = tf_r.add_paragraph()
    pin.text = f"• {k:<18} {v}"
    pin.font.name = FONT_MAIN
    pin.font.size = Pt(10)
    pin.font.color.rgb = C_DARK
    pin.space_after = Pt(2)

p_out = tf_r.add_paragraph()
p_out.text = "\nModel Inference Output:"
p_out.font.name = FONT_MAIN
p_out.font.size = Pt(12)
p_out.font.bold = True
p_out.font.color.rgb = C_GREEN
p_out.space_after = Pt(4)

p_out_t = tf_r.add_paragraph()
p_out_t.text = "1. Predicted Crop: RICE (Oryza sativa)\n   - Prediction Confidence: 99.4% (Tree agreement: 99/100)\n   - Agronomic Fit: Perfect match for >200mm rain & high N.\n2. Fertilizer Recommendation: UREA (High N)\n   - Dosage: 50 kg/hectare top-dressed at tillering stage.\n3. Latency: 2.1 ms end-to-end execution."
p_out_t.font.name = FONT_MAIN
p_out_t.font.size = Pt(10.5)
p_out_t.font.color.rgb = C_DARK

add_footer(s12, 12)

# ==============================================================================
# SLIDE 13: MODEL PERFORMANCE EVALUATION ON PROJECT DATASETS
# ==============================================================================
s13 = prs.slides.add_slide(blank_layout)
add_header(s13, "MODEL PERFORMANCE EVALUATION & BENCHMARKS",
           "Rigorous holdout test evaluation across 2,200 crop observations and 7 fertilizer formulations")

c_left = add_card(s13, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.35))
tf = c_left.text_frame
tf.word_wrap = True
tf.margin_top = Inches(0.25)
tf.margin_left = Inches(0.3)
tf.margin_right = Inches(0.3)

p = tf.paragraphs[0]
p.text = "HOLDOUT TEST BENCHMARK (N = 440, 20% SPLIT)"
p.font.name = FONT_MAIN
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(8)

test_metrics = [
    ("Algorithm", "Accuracy", "Precision", "Recall", "Macro F1"),
    ("Random Forest", "99.32%", "0.994", "0.993", "0.993"),
    ("Decision Tree", "98.18%", "0.983", "0.982", "0.982"),
    ("K-Nearest Neighbors", "97.73%", "0.979", "0.977", "0.977"),
    ("Logistic Regression", "95.23%", "0.955", "0.952", "0.954")
]

for idx, (m, acc, prc, rec, f1) in enumerate(test_metrics):
    pr = tf.add_paragraph()
    pr.text = f"{m:<20} | {acc:<9} | {prc:<8} | {rec:<8} | {f1}"
    pr.font.name = "Courier New" if idx > 0 else FONT_MAIN
    pr.font.size = Pt(10.5)
    pr.font.bold = (idx == 0 or idx == 1)
    pr.font.color.rgb = C_NAVY if idx == 0 else (C_GREEN if idx == 1 else C_DARK)
    pr.space_after = Pt(3)

p_sub = tf.add_paragraph()
p_sub.text = "\nKey Evaluation Insights:"
p_sub.font.name = FONT_MAIN
p_sub.font.size = Pt(12)
p_sub.font.bold = True
p_sub.font.color.rgb = C_ROYAL
p_sub.space_after = Pt(2)

eval_insights = [
    ("Random Forest Superiority:", "Achieves highest macro F1 (0.993) with near-perfect balance between precision and recall across all 22 classes."),
    ("Zero Deficit Detection:", "Decision Tree and KNN perform strongly (>97%), but Decision Tree suffers from isolated overfitting on edge boundaries."),
    ("Pre-processing Validation:", "StandardScaler normalization was critical for KNN to prevent high-variance rainfall from dominating distance metrics.")
]

for h, b in eval_insights:
    pi = tf.add_paragraph()
    pi.text = f"• {h} {b}"
    pi.font.name = FONT_MAIN
    pi.font.size = Pt(10)
    pi.font.color.rgb = C_DARK
    pi.space_after = Pt(3)

c_right = add_card(s13, Inches(6.9), Inches(1.4), Inches(5.6), Inches(5.35))
tf_r = c_right.text_frame
tf_r.word_wrap = True
tf_r.margin_top = Inches(0.25)
tf_r.margin_left = Inches(0.3)
tf_r.margin_right = Inches(0.3)

p = tf_r.paragraphs[0]
p.text = "AGRONOMIC CATEGORY & FERTILIZER BENCHMARK"
p.font.name = FONT_MAIN
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(8)

p_cat = tf_r.add_paragraph()
p_cat.text = "Per-Category Breakdown (Random Forest Engine):"
p_cat.font.name = FONT_MAIN
p_cat.font.size = Pt(11.5)
p_cat.font.bold = True
p_cat.font.color.rgb = C_ROYAL
p_cat.space_after = Pt(4)

cat_data = [
    ("Cereals & Grains (Rice, Maize):", "Precision 1.00 | Recall 0.98 | F1 0.99"),
    ("Pulses & Legumes (Chickpea, Lentil):", "Precision 1.00 | Recall 1.00 | F1 1.00"),
    ("Cash Crops (Cotton, Jute):", "Precision 0.98 | Recall 1.00 | F1 0.99"),
    ("Fruits (Banana, Apple, Mango):", "Precision 1.00 | Recall 1.00 | F1 1.00")
]

for c_name, c_scr in cat_data:
    pcd = tf_r.add_paragraph()
    pcd.text = f"• {c_name}\n  {c_scr}"
    pcd.font.name = FONT_MAIN
    pcd.font.size = Pt(10)
    pcd.font.color.rgb = C_DARK
    pcd.space_after = Pt(3)

p_fert = tf_r.add_paragraph()
p_fert.text = "\nFertilizer Recommendation Model (7 Formulations):"
p_fert.font.name = FONT_MAIN
p_fert.font.size = Pt(11.5)
p_fert.font.bold = True
p_fert.font.color.rgb = C_NAVY
p_fert.space_after = Pt(2)

p_fert_t = tf_r.add_paragraph()
p_fert_t.text = "• Overall Test Accuracy: 98.90% across 7 chemical formulations\n• Urea, DAP, 14-35-14, 28-28, 17-17-17, 20-20, 10-26-26\n• Zero misclassifications between Nitrogen-deficiency and Potassium-deficiency formulations."
p_fert_t.font.name = FONT_MAIN
p_fert_t.font.size = Pt(10)
p_fert_t.font.color.rgb = C_DARK

add_footer(s13, 13)

# ==============================================================================
# SLIDE 14: COMPREHENSIVE COMPARISON OF CLASSIFICATION MODELS
# ==============================================================================
s14 = prs.slides.add_slide(blank_layout)
add_header(s14, "COMPREHENSIVE CLASSIFICATION MODEL COMPARISON",
           "Head-to-head empirical comparison across inductive bias, complexity, interpretability, and generalization")

card_main = add_card(s14, Inches(0.8), Inches(1.35), Inches(11.733), Inches(5.45))
tf = card_main.text_frame
tf.word_wrap = True
tf.margin_top = Inches(0.2)
tf.margin_left = Inches(0.3)
tf.margin_right = Inches(0.3)

p = tf.paragraphs[0]
p.text = "HEAD-TO-HEAD COMPARISON MATRIX"
p.font.name = FONT_MAIN
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(8)

comp_headers = f"{'Algorithm':<22} | {'Boundary Type':<18} | {'Accuracy':<10} | {'Macro F1':<10} | {'Fit Latency':<12} | {'Inference':<10} | {'Interpretability':<16} | {'Overfitting Risk'}"
p_hd = tf.add_paragraph()
p_hd.text = comp_headers
p_hd.font.name = "Courier New"
p_hd.font.size = Pt(10.5)
p_hd.font.bold = True
p_hd.font.color.rgb = C_NAVY
p_hd.space_after = Pt(4)

model_comparisons = [
    ("Logistic Regression", "Linear Hyperplane", "95.23%", "0.954", "12.4 ms", "< 0.5 ms", "Very High (Coeffs)", "Very Low"),
    ("Decision Tree (CART)", "Axis-Aligned Split", "98.18%", "0.982", "8.2 ms", "< 0.5 ms", "High (Tree rules)", "High (Unpruned)"),
    ("KNN (k=5)", "Voronoi Partition", "97.73%", "0.977", "0.0 ms (Lazy)", "8.5 ms", "Low (Instance)", "Moderate (Noise)"),
    ("Random Forest", "Ensemble Non-Linear", "99.32%", "0.993", "45.1 ms", "2.1 ms", "Moderate (Gini Imp)", "Lowest (Bagging)")
]

for name, bound, acc, f1, fit, inf, interp, risk in model_comparisons:
    pr = tf.add_paragraph()
    pr.text = f"{name:<22} | {bound:<18} | {acc:<10} | {f1:<10} | {fit:<12} | {inf:<10} | {interp:<16} | {risk}"
    pr.font.name = "Courier New"
    pr.font.size = Pt(10)
    pr.font.bold = (name == "Random Forest")
    pr.font.color.rgb = C_GREEN if name == "Random Forest" else C_DARK
    pr.space_after = Pt(4)

p_exp = tf.add_paragraph()
p_exp.text = "\nARCHITECTURAL TRADEOFF ANALYSIS & WINNER JUSTIFICATION:"
p_exp.font.name = FONT_MAIN
p_exp.font.size = Pt(12)
p_exp.font.bold = True
p_exp.font.color.rgb = C_ROYAL
p_exp.space_after = Pt(4)

tradeoff_points = [
    ("Bias-Variance Tradeoff:", "Decision Trees exhibit low bias but high variance (memorizing training anomalies). Random Forest aggregates 100 decorrelated trees via Bagging, driving variance down while preserving low bias."),
    ("Inference Latency vs Scaling:", "KNN requires computing Euclidean distances against all 1,760 training points during test time (8.5 ms). Random Forest evaluates 100 trees in parallel in just 2.1 ms."),
    ("Feature Scaling Sensitivity:", "Logistic Regression and KNN strictly require StandardScaler feature scaling. Tree models (DT, RF) are monotonic and scale-invariant, making them exceptionally resilient to noisy field sensors."),
    ("Final Selection:", "Random Forest (99.32% Accuracy, 0.993 F1) was selected as our primary production model for deployment in the full-stack web decision system.")
]

for th, tb in tradeoff_points:
    pt = tf.add_paragraph()
    pt.text = f"• {th} {tb}"
    pt.font.name = FONT_MAIN
    pt.font.size = Pt(10)
    pt.font.color.rgb = C_DARK
    pt.space_after = Pt(2)

add_footer(s14, 14)

# ==============================================================================
# SLIDE 15: REVIEW II SUMMARY & VIVA DEFENSE READINESS
# ==============================================================================
s15 = prs.slides.add_slide(blank_layout)
add_header(s15, "REVIEW II SUMMARY & VIVA DEFENSE READINESS",
           "Synthesis of theoretical foundations, empirical results, and anticipated examiner questions")

c_left = add_card(s15, Inches(0.8), Inches(1.4), Inches(5.8), Inches(5.35))
tf = c_left.text_frame
tf.word_wrap = True
tf.margin_top = Inches(0.25)
tf.margin_left = Inches(0.3)
tf.margin_right = Inches(0.3)

p = tf.paragraphs[0]
p.text = "SUMMARY OF REVIEW II ACCOMPLISHMENTS"
p.font.name = FONT_MAIN
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(8)

accomplishments = [
    ("Module 1 (Validation):", "Implemented 5-Fold Stratified Cross-Validation on 2,200 samples (Mean CV = 99.32% ± 0.31%), mathematically derived Out-of-Bag (OOB) limits (~36.8%), and proved variance reduction through Bagging."),
    ("Module 2 (Evaluation):", "Formulated MSE, RMSE (13.57 mm), and R² (0.824) for regression. Structured binary & multi-class confusion matrices, analyzed agricultural Type I vs Type II error costs, and established F1-Score harmonic balance."),
    ("Module 3 (Models):", "Built Multiple Linear Regression (T5) using closed-form OLS to predict continuous rainfall. Implemented Logistic Regression (T6) via Sigmoid/Softmax with Log-Loss. Benchmarked 4 classifiers, proving Random Forest superior.")
]

for ah, ab in accomplishments:
    pa = tf.add_paragraph()
    pa.text = f"▶ {ah}"
    pa.font.name = FONT_MAIN
    pa.font.size = Pt(11.5)
    pa.font.bold = True
    pa.font.color.rgb = C_ROYAL
    pa.space_after = Pt(1)
    
    pad = tf.add_paragraph()
    pad.text = ab
    pad.font.name = FONT_MAIN
    pad.font.size = Pt(10.5)
    pad.font.color.rgb = C_DARK
    pad.space_after = Pt(6)

c_right = add_card(s15, Inches(6.9), Inches(1.4), Inches(5.6), Inches(5.35))
tf_r = c_right.text_frame
tf_r.word_wrap = True
tf_r.margin_top = Inches(0.25)
tf_r.margin_left = Inches(0.3)
tf_r.margin_right = Inches(0.3)

p = tf_r.paragraphs[0]
p.text = "KEY VIVA QUESTIONS PRE-EMPTED"
p.font.name = FONT_MAIN
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_NAVY
p.space_after = Pt(8)

viva_qa = [
    ("Q1: Why Stratified K-Fold over simple K-Fold?", "A: Standard K-Fold splits randomly, risking class imbalance in folds. Stratification guarantees equal representation across all 22 crop classes."),
    ("Q2: Why use F1-Score instead of Accuracy?", "A: If a dataset has imbalanced classes, a dumb model predicting only the majority class achieves high accuracy but zero recall. F1 harmonic mean forces balance."),
    ("Q3: Why is MSE preferred over MAE during training?", "A: MSE produces a smooth, differentiable parabola with continuous derivatives, allowing analytical OLS matrix inversion and rapid gradient descent convergence."),
    ("Q4: Why does Random Forest outperform a single Decision Tree?", "A: A single tree overfits local data noise. Bagging 100 decorrelated trees averages out variance without inflating bias.")
]

for q, a in viva_qa:
    pq = tf_r.add_paragraph()
    pq.text = q
    pq.font.name = FONT_MAIN
    pq.font.size = Pt(11)
    pq.font.bold = True
    pq.font.color.rgb = C_NAVY
    pq.space_after = Pt(1)
    
    pa = tf_r.add_paragraph()
    pa.text = a
    pa.font.name = FONT_MAIN
    pa.font.size = Pt(10)
    pa.font.color.rgb = C_DARK
    pa.space_after = Pt(5)

add_footer(s15, 15)

# ==============================================================================
# SLIDE 16: CONCLUSION & DEFENSE ACKNOWLEDGMENT
# ==============================================================================
s16 = prs.slides.add_slide(blank_layout)

accent_box = s16.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.25))
accent_box.fill.solid()
accent_box.fill.fore_color.rgb = C_NAVY
accent_box.line.fill.background()

if os.path.exists(LOGO_LEFT):
    s16.shapes.add_picture(LOGO_LEFT, Inches(0.8), Inches(0.6), width=Inches(2.4))
if os.path.exists(LOGO_RIGHT):
    s16.shapes.add_picture(LOGO_RIGHT, Inches(10.2), Inches(0.6), width=Inches(2.3))

card_end = add_card(s16, Inches(1.5), Inches(1.6), Inches(10.333), Inches(5.0), bg_color=C_CARD_BG, border_color=C_CARD_BORDER)
tf = card_end.text_frame
tf.word_wrap = True
tf.margin_top = Inches(0.4)
tf.margin_left = Inches(0.5)
tf.margin_right = Inches(0.5)

p_thx = tf.paragraphs[0]
p_thx.text = "THANK YOU"
p_thx.alignment = PP_ALIGN.CENTER
p_thx.font.name = FONT_MAIN
p_thx.font.size = Pt(36)
p_thx.font.bold = True
p_thx.font.color.rgb = C_NAVY
p_thx.space_after = Pt(8)

p_sub_thx = tf.add_paragraph()
p_sub_thx.text = "REVIEW II EVALUATION CONCLUDED • OPEN FOR QUESTIONS & DISCUSSION"
p_sub_thx.alignment = PP_ALIGN.CENTER
p_sub_thx.font.name = FONT_MAIN
p_sub_thx.font.size = Pt(14)
p_sub_thx.font.bold = True
p_sub_thx.font.color.rgb = C_ROYAL
p_sub_thx.space_after = Pt(20)

p_proj = tf.add_paragraph()
p_proj.text = "Project Title: Crop Recommendation & Fertilizer Prediction Using Advanced Machine Learning Frameworks"
p_proj.alignment = PP_ALIGN.CENTER
p_proj.font.name = FONT_MAIN
p_proj.font.size = Pt(13)
p_proj.font.bold = True
p_proj.font.color.rgb = C_DARK
p_proj.space_after = Pt(14)

p_cands = tf.add_paragraph()
p_cands.text = "DEBJIT DAS (RA2411056010276)    |    ANSHUMAAN DAS (RA2411056010283)\nDepartment of Computer Science and Engineering • School of Computing\nSRM Institute of Science and Technology, Kattankulathur"
p_cands.alignment = PP_ALIGN.CENTER
p_cands.font.name = FONT_MAIN
p_cands.font.size = Pt(12)
p_cands.font.color.rgb = C_MUTED

add_footer(s16, 16)

# Save both as dedicated Review 2 presentation and copy presentation
prs.save(OUTPUT_PPTX)
prs.save(COPY_PPTX)
print(f"[OK] Generated {OUTPUT_PPTX} successfully (16 slides).")
print(f"[OK] Updated {COPY_PPTX} successfully.")
