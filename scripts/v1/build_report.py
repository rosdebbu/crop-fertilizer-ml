"""Builds report/Project_Report.docx (one pass). Use scripts/make_report.py for the full two-pass build with page numbers."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fitz
import report_engine as E
from report_engine import d, para, add_runs, set_font, AL, Inches, Pt, OxmlElement, qn, TW

if os.path.exists("report/pagemap.json"): E.PAGEMAP.update(json.load(open("report/pagemap.json")))
import report_content as C

TITLE = "CROP RECOMMENDATION AND FERTILIZER PREDICTION USING MACHINE LEARNING"
S1, S2 = "DEBJIT DAS", "ANSHUMAAN DAS"
R1, R2 = "RA2411056010276", "RA2411056010283"
GUIDE, DESIG = "Dr. Sasikala E", "Professor, DSBS"
LOGO, LOGO_H = "report/figures/srm_logo_cover.png", "report/figures/srm_logo_header.png"
E.setup_document()


def center(text, size=14, bold=False, italic=False, after=6, spacing=1.2, before=0):
    return para(text, size, bold, italic, align=AL.CENTER, spacing=spacing, after=after, before=before)


def picture(path, width):
    p = d.add_paragraph(); p.alignment = AL.CENTER; p.paragraph_format.space_after = Pt(6)
    p.add_run().add_picture(path, width=Inches(width)); return p


def no_borders(tbl):
    tblPr = tbl._tbl.tblPr; b = OxmlElement("w:tblBorders")
    for e in ("top", "left", "bottom", "right", "insideH", "insideV"):
        x = OxmlElement(f"w:{e}"); x.set(qn("w:val"), "nil"); b.append(x)
    tblPr.append(b)


# =========================== COVER (section 1) ===========================
E.page_border(d.sections[0])
center(TITLE, 18, True, after=10, before=10, spacing=1.3)
center("A PROJECT REPORT", 14, True, after=14)
center("Submitted by", 14, False, True, after=8)
center(f"{S1} [{R1}]", 16, after=2); center(f"{S2} [{R2}]", 16, after=14)
center("Under the Guidance of", 14, False, True, after=6)
center(f"({GUIDE.upper()})", 16, True, after=0); center(f"({DESIG})", 14, after=12)
center("in partial fulfillment of the requirements for the degree of", 12, False, True, after=8)
center("BACHELOR OF TECHNOLOGY", 14, after=0); center("in", 14, after=0)
center("COMPUTER SCIENCE ENGINEERING", 14, after=0); center("with specialization in (DATA SCIENCE)", 14, after=10)
picture(LOGO, 2.4)
for t in ("DEPARTMENT OF DATA SCIENCE AND BUSINESS SYSTEMS", "SCHOOL OF COMPUTING", "COLLEGE OF ENGINEERING AND TECHNOLOGY",
          "SRM INSTITUTE OF SCIENCE AND TECHNOLOGY", "KATTANKULATHUR - 603 203"):
    center(t, 16, after=0, spacing=1.3)
center("NOVEMBER 2026", 14, after=0, before=10)
# footer of section 1 stays empty

# =========================== FRONT MATTER (section 2, roman, starts at ii) ===========================
s2 = E.new_section(); E.footer_page_number(s2, "lowerRoman", 2)
page_border_removed = True

# ---- Bonafide certificate ----
t = d.add_table(rows=1, cols=2); no_borders(t)
t.rows[0].cells[0].width = Inches(1.5); t.rows[0].cells[1].width = Inches(5.2)
c0 = t.rows[0].cells[0].paragraphs[0]; c0.add_run().add_picture(LOGO_H, width=Inches(1.3))
c1 = t.rows[0].cells[1]; c1.text = ""
for i, line in enumerate(("Department of Data Science and Business Systems", "SRM Institute of Science & Technology", "Own Work* Declaration Form")):
    p = c1.paragraphs[0] if i == 0 else c1.add_paragraph()
    p.paragraph_format.space_after = Pt(0); p.alignment = AL.CENTER
    r = p.add_run(line); set_font(r, 11, bold=(i > 0))
center("SRM INSTITUTE OF SCIENCE AND TECHNOLOGY", 18, after=0, before=30)
center("KATTANKULATHUR – 603 203", 18, after=14)
center("BONAFIDE CERTIFICATE", 16, after=14)
para(f"Certified that the project report titled “**{TITLE}**” is the bonafide work of “**{S1} [{R1}], {S2} [{R2}]**” "
     "who carried out the project work under my supervision. Certified further, that to the best of my knowledge the work reported herein "
     "does not form any other project report or dissertation on the basis of which a degree or award was conferred on an earlier occasion "
     "on this or any other candidate.", 14, indent=0.4, spacing=1.5, after=60)
sig = d.add_table(rows=1, cols=2); no_borders(sig)
left = ["SIGNATURE", "", f"**{GUIDE.upper()}**", "SUPERVISOR", "Professor", "Department of Data Science", "and Business Systems"]
right = ["SIGNATURE", "", "[[HoD NAME]]", "PROFESSOR & HEAD", "DEPARTMENT OF DATA SCIENCE", "AND BUSINESS SYSTEMS"]
for cell, lines in zip(sig.rows[0].cells, (left, right)):
    cell.text = ""
    for i, line in enumerate(lines):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.2
        add_runs(p, line, 12, bold=(line == "SIGNATURE"))

# ---- Declaration ----
E.heading_center("DECLARATION", 16, page_break=True)
para(f"We, **{S1} [{R1}]** and **{S2} [{R2}]**, students of the Department of Data Science and Business Systems, School of Computing, "
     "College of Engineering and Technology, SRM Institute of Science and Technology, Kattankulathur, hereby declare that the project "
     f"report titled “**{TITLE}**” submitted in partial fulfillment of the requirements for the degree of Bachelor of Technology in "
     "Computer Science Engineering with specialization in Data Science is our own work, based on our own study and experiments.", 12, indent=0.4)
para("We have acknowledged all the material and sources used in its preparation, whether they are books, articles, reports, lecture notes, "
     "websites, datasets or any other kind of document, including electronic media. We have not copied from, or colluded with, any other "
     "person in preparing this work, and it has not been submitted to any other institution for the award of a degree or diploma.", 12, indent=0.4, after=40)
dt = d.add_table(rows=1, cols=2); no_borders(dt)
for cell, lines in zip(dt.rows[0].cells, ([f"**{S1}**", R1, "Signature: ____________", "Date: ____________"], [f"**{S2}**", R2, "Signature: ____________", "Place: Kattankulathur"])):
    cell.text = ""
    for i, line in enumerate(lines):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph(); p.paragraph_format.space_after = Pt(6); add_runs(p, line, 12)

# ---- Acknowledgement ----
E.heading_center("ACKNOWLEDGEMENT", 16, page_break=True)
for txt in (
    "We express our sincere thanks to the management of SRM Institute of Science and Technology for providing the facilities and the "
    "environment in which this project could be completed. We thank [[NAME]], Dean, College of Engineering and Technology, and [[NAME]], "
    "Chairperson, School of Computing, for their encouragement.",
    "We are grateful to [[HoD NAME]], Professor and Head, Department of Data Science and Business Systems, for the support given to the project, "
    "and to [[NAME]], Project Coordinator, for the guidance on the format and the schedule of the project reviews.",
    f"We are deeply indebted to our guide, **{GUIDE}**, {DESIG}, for the valuable guidance, the patient review of our work and the "
    "suggestions that helped us to evaluate our models more honestly and more rigorously.",
    "We also thank the faculty members of the department, the authors of the open-source libraries and public datasets on which this work "
    "is built, and our families and friends for their constant support."):
    para(txt, 12, indent=0.4)
para(f"{S1}\n{S2}", 12, align=AL.RIGHT, after=0)

# ---- Abstract ----
cvb = C.CV["Random Forest"]
E.heading_center("ABSTRACT", 16, page_break=True)
para("Choosing the right crop and the right fertilizer for a field is a decision that affects yield, cost and soil health, yet it is often "
     "made without data. This project builds a machine-learning system that recommends one of 22 crops from soil nitrogen, phosphorus, "
     "potassium, pH, temperature, humidity and rainfall, and one of 7 fertilizers from soil and nutrient information, and serves both "
     "through a FastAPI backend and a web interface with soil-health advice, profit and dosage estimates, climate-stress simulation and a "
     "regional satellite view.", 12, indent=0.4)
para(f"Seven classifiers were compared on the Kaggle crop dataset with repeated stratified cross-validation and paired Wilcoxon tests. "
     f"Random Forest was the most accurate ({cvb['acc_mean']} ± {cvb['acc_std']}%) and was selected. A noise-robustness experiment showed "
     f"that it loses accuracy faster than SVM and KNN when the inputs are noisy: at a noise level of 0.25 feature standard deviations it "
     f"scores {C.NZ['Random Forest'][2]}% against {C.NZ['SVM (RBF)'][2]}% for SVM. On the public fertilizer dataset of 100,000 rows every "
     f"model scored about 14%, which is the chance level. ANOVA, chi-square, mutual-information and shuffled-label tests showed that the "
     "labels are independent of the features, so the application reports a reliability warning for fertilizer predictions.", 12, indent=0.4)
para("The work contributes a tested end-to-end prototype, a dataset-audit and robustness protocol, and an honest account of what the "
     "public benchmarks can and cannot support. The findings are also presented as a research paper in Appendix B.", 12, indent=0.4, after=8)
para("**Keywords:** crop recommendation, fertilizer recommendation, random forest, precision agriculture, dataset audit, robustness", 12, align=AL.LEFT)

# ---- TOC / LoF / LoT markers ----
mk_toc = para("TABLE OF CONTENTS", 14, True, align=AL.CENTER, spacing=1.5, after=10, page_break=True)
mk_toc_end = para("", spacing=1.0, after=0)
mk_lof = para("LIST OF FIGURES", 14, True, align=AL.CENTER, spacing=1.5, after=10, page_break=True)
mk_lof_end = para("", spacing=1.0, after=0)
mk_lot = para("LIST OF TABLES", 14, True, align=AL.CENTER, spacing=1.5, after=10, page_break=True)
mk_lot_end = para("", spacing=1.0, after=0)

# ---- Abbreviations ----
para("ABBREVIATIONS", 14, True, align=AL.CENTER, spacing=1.5, after=10, page_break=True)
ABBR = [("ANOVA", "Analysis of Variance"), ("API", "Application Programming Interface"), ("ASGI", "Asynchronous Server Gateway Interface"),
        ("CART", "Classification and Regression Trees"), ("CORS", "Cross-Origin Resource Sharing"), ("CSV", "Comma-Separated Values"),
        ("CV", "Cross-Validation"), ("DAP", "Diammonium Phosphate"), ("DSBS", "Data Science and Business Systems"), ("DT", "Decision Tree"),
        ("EDA", "Exploratory Data Analysis"), ("EVI", "Enhanced Vegetation Index"), ("HGB", "Histogram Gradient Boosting"),
        ("HTTP", "Hyper Text Transfer Protocol"), ("JSON", "JavaScript Object Notation"), ("KNN", "K-Nearest Neighbours"),
        ("LR", "Logistic Regression"), ("ML", "Machine Learning"), ("MLP", "Multilayer Perceptron"), ("MSP", "Minimum Support Price"),
        ("NDVI", "Normalised Difference Vegetation Index"), ("NDWI", "Normalised Difference Water Index"), ("NIR", "Near-Infrared"),
        ("NPK", "Nitrogen, Phosphorus, Potassium"), ("OOB", "Out-of-Bag"), ("RBF", "Radial Basis Function"), ("REST", "Representational State Transfer"),
        ("RF", "Random Forest"), ("ROI", "Return on Investment"), ("SVM", "Support Vector Machine"), ("UI", "User Interface")]
at = d.add_table(rows=0, cols=2); no_borders(at)
for a, m in ABBR:
    cells = at.add_row().cells; cells[0].width = Inches(1.4); cells[1].width = Inches(5.3)
    for c, txt, b in ((cells[0], a, True), (cells[1], m, False)):
        c.text = ""; p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(5); add_runs(p, txt, 12, bold=b)

# =========================== MAIN MATTER (section 3, arabic from 1) ===========================
s3 = E.new_section(); E.footer_page_number(s3, "decimal", 1)
C.chapters()

# ---- References ----
E.RECS.append({"kind": "toc", "level": 0, "num": "", "title": "REFERENCES", "key": "REFERENCES"})
para("REFERENCES", 16, True, align=AL.CENTER, spacing=1.5, after=14, page_break=True)
for i, key in enumerate(E.CITES, 1):
    p = para("", 12, align=AL.JUSTIFY, spacing=1.15, after=8, left=0.5, indent=-0.5)
    p.paragraph_format.tab_stops.add_tab_stop(Inches(0.5))
    add_runs(p, f"[{i}]\t" + E.REFS[key], 12)
unused = [k for k in E.REFS if k not in E.CITES]
if unused: print("WARNING uncited references:", unused)
if len(E.CITES) < 15: print("WARNING fewer than 15 references")

# ---- Appendix A: coding ----
def grab(path, start, end=None, include_end=False):
    lines = open(path, encoding="utf-8").read().replace("\r\n", "\n").split("\n")
    i = next(k for k, l in enumerate(lines) if re.search(start, l))
    j = len(lines)
    if end:
        j = next((k for k in range(i + 1, len(lines)) if re.search(end, lines[k])), len(lines))
    return "\n".join(lines[i:j + (1 if include_end else 0)])

E.RECS.append({"kind": "toc", "level": 0, "num": "", "title": "APPENDIX A  CODING", "key": "APPENDIX A"})
para("APPENDIX A", 16, True, align=AL.CENTER, spacing=1.5, after=6, page_break=True)
para("CODING", 16, True, align=AL.CENTER, spacing=1.5, after=18)
para("Selected listings from the project source code are given below. The complete code is in the project repository. Code is shown in a "
     "monospaced font for readability.", 12, after=10)
CODE = E.CODE
CODE(grab("app.py", r"^def fit_and_score", r"^def train_crop_models"), "A.1  Training and evaluation of the models (app.py)")
CODE(grab("app.py", r"^# Train on first start", r"^load_or_train\(\)", True), "A.2  Model cache for fast start-up (app.py)")
CODE(grab("app.py", r'^@app\.post\("/api/predict/crop"\)', r'^@app\.post\("/api/predict/fertilizer"\)'), "A.3  Crop prediction endpoint (app.py)")
CODE(grab("app.py", r'^@app\.post\("/api/farmer/climate-stress"\)', r'^@app\.get\("/api/farmer/crop-rotation"\)'), "A.4  Climate-stress endpoint (app.py)")
CODE(grab("static/app.js", r"^// Shared field conditions", r"^function syncCropSlider"), "A.5  Shared field readings between tabs (static/app.js)")
CODE(grab("scripts/make_fertilizer_dataset.py", r"^LOW = 20", r"^rows = |^def build"), "A.6  Rule used for the synthetic fertilizer experiment")
CODE(grab("scripts/research_experiments.py", r"^# -+ D\. Crop: robustness", r"^# -+ A\. Fertilizer"), "A.7  Noise-robustness experiment (scripts/research_experiments.py)")

# ---- Appendix B: conference paper ----
E.RECS.append({"kind": "toc", "level": 0, "num": "", "title": "APPENDIX B  CONFERENCE PAPER", "key": "APPENDIX B"})
para("APPENDIX B", 16, True, align=AL.CENTER, spacing=1.5, after=6, page_break=True)
para("CONFERENCE PAPER", 16, True, align=AL.CENTER, spacing=1.5, after=18)
para("The research paper prepared from this work is reproduced below.", 12)
pdf = fitz.open("paper/Research_Paper.pdf")
os.makedirs("report/figures/paperpages", exist_ok=True)
for i, page in enumerate(pdf):
    path = f"report/figures/paperpages/p{i + 1}.png"; page.get_pixmap(dpi=140).save(path)
    pp = d.add_paragraph(); pp.alignment = AL.CENTER; pp.paragraph_format.page_break_before = True
    pp.add_run().add_picture(path, width=Inches(6.3))

# =========================== inject TOC / LoF / LoT ===========================
def inject(marker_end, entries):
    body = d.element.body
    for kind, args in entries:
        E.leader_line(**args)
        el = [e for e in body if e.tag != qn("w:sectPr")][-1]
        marker_end._p.addprevious(el)

front = [("ABSTRACT", "front:ABSTRACT"), ("TABLE OF CONTENTS", "front:TABLE OF CONTENTS"), ("LIST OF FIGURES", "front:LIST OF FIGURES"),
         ("LIST OF TABLES", "front:LIST OF TABLES"), ("ABBREVIATIONS", "front:ABBREVIATIONS")]
toc_entries = [("t", dict(left_text=n, page=E.pg(k), bold=True)) for n, k in front]
for r in E.RECS:
    if r["kind"] != "toc": continue
    if r["level"] == 0:
        if r["num"]: toc_entries.append(("t", dict(left_text=r["title"], page=E.pg(r["key"]), bold=True, num=r["num"], num_w=0.5)))
        else: toc_entries.append(("t", dict(left_text=r["title"], page=E.pg(r["key"]), bold=True)))
    else:
        toc_entries.append(("t", dict(left_text=r["title"], page=E.pg(r["key"]), indent=0.5, num=r["num"], num_w=0.55, size=11)))
inject(mk_toc_end, toc_entries)
inject(mk_lof_end, [("f", dict(left_text=r["title"], page=E.pg(r["key"]), num=r["num"], num_w=0.8, size=11)) for r in E.RECS if r["kind"] == "fig"])
inject(mk_lot_end, [("l", dict(left_text=r["title"], page=E.pg(r["key"]), num=r["num"], num_w=0.9, size=11)) for r in E.RECS if r["kind"] == "tab"])

os.makedirs("report", exist_ok=True)
json.dump(E.RECS, open("report/records.json", "w"), indent=1)
d.save("report/Project_Report.docx")
print("saved report/Project_Report.docx; citations:", len(E.CITES), "warnings:", E.WARN)
