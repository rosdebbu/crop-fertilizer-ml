"""Builds report/Project_Report.docx (one pass), laid out like the sample SRM report (10 chapters, references table, appendix,
paper publication status, plagiarism report). Use scripts/make_report.py for the multi-pass build that fills page numbers."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fitz
import report_engine as E
from report_engine import d, para, add_runs, set_font, AL, Inches, Pt, OxmlElement, qn

if os.path.exists("report/pagemap.json"): E.PAGEMAP.update(json.load(open("report/pagemap.json")))
import report_content as C

TITLE = "CROP RECOMMENDATION AND FERTILIZER PREDICTION USING MACHINE LEARNING"
S1, S2 = "DEBJIT DAS", "ANSHUMAAN DAS"
R1, R2 = "RA2411056010276", "RA2411056010283"
GUIDE, DESIG = "Dr. Sasikala E", "Professor"
LOGO, LOGO_H = "report/figures/srm_logo_cover.png", "report/figures/srm_logo_header.png"
E.setup_document()


def center(text, size=14, bold=False, italic=False, after=6, spacing=1.15, before=0):
    return para(text, size, bold, italic, align=AL.CENTER, spacing=spacing, after=after, before=before)


def no_borders(tbl):
    tblPr = tbl._tbl.tblPr; b = OxmlElement("w:tblBorders")
    for e in ("top", "left", "bottom", "right", "insideH", "insideV"):
        x = OxmlElement(f"w:{e}"); x.set(qn("w:val"), "nil"); b.append(x)
    tblPr.append(b)


def heading(text, size=14, page_break=True):
    return para(text, size, True, align=AL.CENTER, spacing=1.2, after=12, page_break=page_break)


# =========================== COVER (section 1) ===========================
center(TITLE, 18, True, after=22, before=20, spacing=1.2)
center("A PROJECT REPORT", 14, True, after=22)
center("Submitted by", 14, False, True, after=10)
center(f"{S1} [Reg No: {R1}]", 16, True, after=2); center(f"{S2} [Reg No: {R2}]", 16, True, after=24)
center("Under the Guidance of", 14, False, True, after=8)
center(GUIDE, 16, True, after=0); center(f"({DESIG}, Department of Data Science and Business Systems)", 12, after=18)
center("In partial fulfillment of the Requirements for the Degree of", 14, False, True, after=10)
center("BACHELOR OF TECHNOLOGY", 16, True, after=0); center("in COMPUTER SCIENCE ENGINEERING", 16, True, after=0)
center("with Specialization in DATA SCIENCE", 16, True, after=14)
p = d.add_paragraph(); p.alignment = AL.CENTER; p.paragraph_format.space_after = Pt(12)
p.add_run().add_picture(LOGO, width=Inches(2.6))
center("DEPARTMENT OF DATA SCIENCE AND BUSINESS SYSTEMS", 16, True, after=0, spacing=1.25)
center("COLLEGE OF ENGINEERING AND TECHNOLOGY", 16, True, after=0, spacing=1.25)
center("SRM INSTITUTE OF SCIENCE AND TECHNOLOGY", 16, True, after=0, spacing=1.25)
center("KATTANKULATHUR - 603 203", 16, True, after=10, spacing=1.25)
center("NOVEMBER 2026", 14, True, after=0)

# =========================== FRONT MATTER (roman, cover = i) ===========================
s2 = E.new_section(); E.footer_page_number(s2, "lowerRoman", 2)

# ---- Bonafide certificate ----
center("SRM INSTITUTE OF SCIENCE AND TECHNOLOGY", 18, True, after=2, before=10)
center("KATTANKULATHUR-603203", 18, True, after=26)
p = center("BONAFIDE CERTIFICATE", 16, True, after=22)
for r in p.runs: r.underline = True
para(f"Certified that this project report titled “**{TITLE}**” is the bonafide work of “**{S1} [Reg No: {R1}], {S2} [Reg No: {R2}]**” "
     "who carried out the project work under my supervision. Certified further, that to the best of my knowledge the work reported herein "
     "does not form part of any other thesis or dissertation on the basis of which a degree or award was conferred on an earlier occasion "
     "on this or any other candidate.", 12, spacing=1.5, after=60)
sig = d.add_table(rows=1, cols=2); no_borders(sig)
for cell, lines in zip(sig.rows[0].cells, ([f"**{GUIDE.upper()}**", DESIG, "Dept. of DSBS"], ["**DR. KAVITHA V**", "HEAD OF THE DEPARTMENT", "Dept. of DSBS"])):
    cell.text = ""
    for i, line in enumerate(lines):
        pp = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        pp.paragraph_format.space_after = Pt(0); add_runs(pp, line, 12)
para("", after=70)
ex = d.add_table(rows=1, cols=2); no_borders(ex)
for cell, txt in zip(ex.rows[0].cells, ("Signature of Internal Examiner", "Signature of External Examiner")):
    cell.text = ""; add_runs(cell.paragraphs[0], txt, 12)

# ---- Abstract (iii) ----
cvb = C.CV["Random Forest"]
heading("ABSTRACT")
for txt in (
    "Choosing the right crop and the right fertilizer for a field is a decision that affects yield, cost and soil health, yet it is often "
    "made without data. This project builds a machine-learning system that recommends one of 22 crops from soil nitrogen, phosphorus, "
    "potassium, pH, temperature, humidity and rainfall, and one of 7 fertilizers from soil and nutrient information, and serves both "
    "through a FastAPI backend and a web interface with soil-health advice, profit and dosage estimates, climate-stress simulation and a "
    "regional satellite view.",
    f"Seven classifiers were compared on the Kaggle crop dataset with repeated stratified cross-validation and paired Wilcoxon tests. "
    f"Random Forest was the most accurate ({cvb['acc_mean']} ± {cvb['acc_std']}%) and was selected. A noise-robustness experiment showed "
    f"that it loses accuracy faster than SVM and KNN when the inputs are noisy: at a noise level of 0.25 feature standard deviations it "
    f"scores {C.NZ['Random Forest'][2]}% against {C.NZ['SVM (RBF)'][2]}% for SVM. On the public fertilizer dataset of 100,000 rows every "
    f"model scored about 14%, which is the chance level. ANOVA, chi-square, mutual-information and shuffled-label tests showed that the "
    "labels are independent of the features, so the application reports a reliability warning for fertilizer predictions.",
    "The work contributes a tested end-to-end prototype, a dataset-audit and robustness protocol, and an honest account of what the "
    "public benchmarks can and cannot support. The findings are also presented as a research paper in the appendix."):
    para(txt, 12, spacing=1.4)
para("**Keywords:** crop recommendation, fertilizer recommendation, random forest, precision agriculture, dataset audit, robustness", 12, align=AL.LEFT)

# ---- Acknowledgement (iv) ----
heading("ACKNOWLEDGEMENT")
for txt in (
    "The success and the final outcome of this project required guidance and assistance from different sources and we feel extremely "
    "fortunate to have got this all along the completion of our project. Whatever we have done is largely due to such guidance and "
    "assistance and we would not forget to thank them.",
    "We express our sincere thanks to the Head of the Department, Department of Data Science and Business Systems, **Dr. KAVITHA V**, for "
    "all the help and infrastructure provided to us to complete this project successfully and her valuable guidance.",
    "We owe our profound gratitude to our project guide **Dr. SASIKALA E**, who took keen interest in our project work and guided us all "
    "along, till the completion of our project work by providing all the necessary information for developing a good system.",
    "We are thankful to and fortunate enough to get constant encouragement, support and guidance from all the Teaching staff of the "
    "Department of Data Science and Business Systems which helped us in successfully completing our minor project work. Also, we would "
    "like to extend our sincere regards to all the non-teaching staff of the department of Data Science and Business Systems for their "
    "timely support."):
    para(txt, 12, spacing=1.5, after=12)
para("", after=30)
para(f"**{S1} \u2013 {R1}**", 12, align=AL.RIGHT, after=0); para(f"**{S2} \u2013 {R2}**", 12, align=AL.RIGHT, after=0)

# ---- TOC / LoT / LoF markers (v, vi, vii) ----
mk_toc = heading("TABLE OF CONTENTS")
mk_toc_hdr = d.add_paragraph(); mk_toc_hdr.paragraph_format.space_after = Pt(4)
mk_toc_hdr.paragraph_format.tab_stops.add_tab_stop(Inches(3.6), E.WD_TAB_ALIGNMENT.CENTER); mk_toc_hdr.paragraph_format.tab_stops.add_tab_stop(Inches(6.67), E.WD_TAB_ALIGNMENT.RIGHT)
r = mk_toc_hdr.add_run("CHAPTER NO.\tTITLE\tPAGE NO."); set_font(r, 12, True)
mk_toc_end = para("", spacing=1.0, after=0)
mk_lot = heading("LIST OF TABLES"); mk_lot_end = para("", spacing=1.0, after=0)
mk_lof = heading("LIST OF FIGURES"); mk_lof_end = para("", spacing=1.0, after=0)

# ---- List of symbols and abbreviations (viii) ----
heading("LIST OF SYMBOLS AND ABBREVIATIONS")
ABBR = [("ANOVA", "Analysis of Variance"), ("API", "Application Programming Interface"), ("ASGI", "Asynchronous Server Gateway Interface"),
        ("CART", "Classification and Regression Trees"), ("CORS", "Cross-Origin Resource Sharing"), ("CSV", "Comma-Separated Values"),
        ("CV", "Cross-Validation"), ("DAP", "Diammonium Phosphate"), ("DSBS", "Data Science and Business Systems"), ("DT", "Decision Tree"),
        ("EDA", "Exploratory Data Analysis"), ("HGB", "Histogram Gradient Boosting"), ("HTTP", "Hyper Text Transfer Protocol"),
        ("JSON", "JavaScript Object Notation"), ("KNN", "K-Nearest Neighbours"), ("LR", "Logistic Regression"), ("ML", "Machine Learning"),
        ("MLP", "Multilayer Perceptron"), ("MSP", "Minimum Support Price"), ("NDVI", "Normalised Difference Vegetation Index"),
        ("NDWI", "Normalised Difference Water Index"), ("NIR", "Near-Infrared"), ("NPK", "Nitrogen, Phosphorus, Potassium"),
        ("OOB", "Out-of-Bag"), ("RBF", "Radial Basis Function"), ("REST", "Representational State Transfer"), ("RF", "Random Forest"),
        ("ROI", "Return on Investment"), ("SVM", "Support Vector Machine"), ("UI", "User Interface"),
        ("μ, σ", "Mean and standard deviation of a feature"), ("z", "Standardised value of a feature"),
        ("λ", "Noise level, as a fraction of the feature standard deviation"), ("γ", "Width parameter of the RBF kernel")]
at = d.add_table(rows=0, cols=2); no_borders(at)
for a, m in ABBR:
    cells = at.add_row().cells; cells[0].width = Inches(1.3); cells[1].width = Inches(5.3)
    for c, txt, b in ((cells[0], a, True), (cells[1], m, False)):
        c.text = ""; pp = c.paragraphs[0]; pp.paragraph_format.space_after = Pt(3); add_runs(pp, txt, 12, bold=b)

# =========================== MAIN MATTER (arabic from 1) ===========================
s3 = E.new_section(); E.footer_page_number(s3, "decimal", 1)
C.chapters()

# ---- Chapter 10: references (table, like the sample) ----
E.H1(10, "References")
E.REF_TABLE([E.REFS[key] for key in E.CITES])
unused = [k for k in E.REFS if k not in E.CITES]
if unused: print("WARNING uncited references:", unused)
if len(E.CITES) < 15: print("WARNING fewer than 15 references")


# ---- Appendix: code ----
def grab(path, start, end=None, include_end=False):
    lines = open(path, encoding="utf-8").read().replace("\r\n", "\n").split("\n")
    i = next(k for k, l in enumerate(lines) if re.search(start, l))
    j = len(lines)
    if end: j = next((k for k in range(i + 1, len(lines)) if re.search(end, lines[k])), len(lines))
    return "\n".join(lines[i:j + (1 if include_end else 0)])


E.RECS.append({"kind": "toc", "level": 0, "num": "", "title": "APPENDIX", "key": "APPENDIX CODE"})
para("APPENDIX CODE", 16, True, align=AL.CENTER, spacing=1.0, after=4, page_break=True)
para("Selected listings; the complete code is in the project repository.", 11, after=2)
CODE = E.CODE
CODE(grab("app.py", r"^def fit_and_score", r"^def train_crop_models"), "A.1  Training and evaluation of the models (app.py)")
CODE(grab("app.py", r"^# Train on first start", r"^load_or_train\(\)", True), "A.2  Model cache for fast start-up (app.py)")

# ---- Paper publication status ----
E.RECS.append({"kind": "toc", "level": 0, "num": "", "title": "PAPER PUBLICATION STATUS", "key": "PAPER PUBLICATION STATUS"})
para("PAPER PUBLICATION STATUS", 16, True, align=AL.CENTER, spacing=1.2, after=8, page_break=True)
para("A research paper was prepared from this project: “Benchmark Accuracy Is Not Field Reliability: Auditing Crop and Fertilizer "
     "Recommendation Datasets and Their Robustness to Sensor Noise”. Its status is given below and the paper follows.", 12, after=4)
for lab, val in (("Venue", "Zenodo (open-access research repository operated by CERN)"), ("Type", "Preprint (not peer reviewed)"), ("Status", "Published online"),
                 ("Publication date", "18-11-2026"), ("DOI", "10.5281/zenodo.24333948"), ("Link", "https://zenodo.org/records/24333948")):
    para(f"**{lab}:** {val}", 12, align=AL.LEFT, after=2)
para("", after=4)
pdf = fitz.open("paper/Research_Paper.pdf")
os.makedirs("report/figures/paperpages", exist_ok=True)
for i, page in enumerate(pdf):
    path = f"report/figures/paperpages/p{i + 1}.png"; page.get_pixmap(dpi=140).save(path)
    pp = d.add_paragraph(); pp.alignment = AL.CENTER
    if i: pp.paragraph_format.page_break_before = True
    pp.add_run().add_picture(path, width=Inches(4.9 if i == 0 else 6.2))

# ---- Plagiarism report ----
E.RECS.append({"kind": "toc", "level": 0, "num": "", "title": "PLAGIARISM REPORT", "key": "PLAGIARISM REPORT"})
para("PLAGIARISM REPORT", 16, True, align=AL.CENTER, spacing=1.2, after=14, page_break=True)
para("The SRM plagiarism check form follows on the next pages. It is completed and signed with the guide, and the similarity report generated "
     "with the help of the guide is attached after it. [[Attach the Turnitin similarity report here. The required similarity index is 10% or less.]]", 12)
pf = fitz.open("report/figures/plagiarism_form.pdf")
for i, page in enumerate(pf):
    path = f"report/figures/paperpages/plag{i + 1}.png"; page.get_pixmap(dpi=140).save(path)
    pp = d.add_paragraph(); pp.alignment = AL.CENTER; pp.paragraph_format.page_break_before = True
    pp.add_run().add_picture(path, width=Inches(6.3))


# =========================== inject TOC / LoT / LoF ===========================
def inject(marker_end, entries):
    body = d.element.body
    for args in entries:
        E.leader_line(**args)
        el = [e for e in body if e.tag != qn("w:sectPr")][-1]
        marker_end._p.addprevious(el)


toc = [dict(left_text=n, page=E.pg(f"front:{n}"), bold=True) for n in ("ABSTRACT", "LIST OF TABLES", "LIST OF FIGURES", "LIST OF SYMBOLS AND ABBREVIATIONS")]
for r_ in E.RECS:
    if r_["kind"] != "toc": continue
    if r_["level"] == 0:
        toc.append(dict(left_text=r_["title"], page=E.pg(r_["key"]), bold=True, num=r_["num"], num_w=1.0) if r_["num"] else dict(left_text=r_["title"], page=E.pg(r_["key"]), bold=True))
    # section-level entries are omitted so that the contents fit on one page
inject(mk_toc_end, toc)
inject(mk_lot_end, [dict(left_text=r_["title"], page=E.pg(r_["key"]), num=r_["num"].replace("Table ", ""), num_w=0.6, size=11) for r_ in E.RECS if r_["kind"] == "tab"])
inject(mk_lof_end, [dict(left_text=r_["title"], page=E.pg(r_["key"]), num=r_["num"].replace("Fig ", ""), num_w=0.6, size=11) for r_ in E.RECS if r_["kind"] == "fig"])

os.makedirs("report", exist_ok=True)
json.dump(E.RECS, open("report/records.json", "w"), indent=1)
json.dump(E.NEWLABELS, open("report/labels.json", "w"), indent=1)
d.save("report/Project_Report.docx")
print("saved report/Project_Report.docx; citations:", len(E.CITES), "warnings:", E.WARN)
