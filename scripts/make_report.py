"""Two-pass report build: builds the docx, exports a PDF with Word, reads the real page numbers,
rebuilds so the contents / list pages show them. Run from the repo root: python scripts/make_report.py"""
import json, os, re, subprocess, sys
import fitz

def roman(n):
    out = ""
    for v, s in ((10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")):
        while n >= v: out += s; n -= v
    return out

def norm(t): return re.sub(r"\s+", " ", t).strip()

def build(): subprocess.run([sys.executable, "scripts/build_report.py"], check=True)

def to_pdf():
    src, dst = os.path.abspath("report/Project_Report.docx"), os.path.abspath("report/Project_Report.pdf")
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts/word_to_pdf.ps1", src, dst], check=True, timeout=240)
    for f in os.listdir("report"):
        if f.startswith("~$"): os.remove(os.path.join("report", f))

def pagemap():
    doc = fitz.open("report/Project_Report.pdf"); pages = [norm(p.get_text()) for p in doc]
    ch1 = next(i for i, t in enumerate(pages) if re.match(r"^(\d+ )?CHAPTER 1 INTRODUCTION", t))
    out = {}
    for name in ("ABSTRACT", "TABLE OF CONTENTS", "LIST OF TABLES", "LIST OF FIGURES", "LIST OF SYMBOLS AND ABBREVIATIONS"):
        i = next(i for i, t in enumerate(pages) if i < ch1 and re.match(r"^([ivx]+ )?" + name, t)); out[f"front:{name}"] = roman(i + 1)
    for r in json.load(open("report/records.json")):
        key = norm(r["key"]); hit = next((i for i in range(ch1, len(pages)) if key in pages[i]), None)
        out[r["key"]] = str(hit - ch1 + 1) if hit is not None else "?"
    return out, len(pages), ch1

os.makedirs("report", exist_ok=True)
for f in ("report/pagemap.json", "report/labels.json"):
    if os.path.exists(f): os.remove(f)
last = None
for it in range(5):
    build(); to_pdf(); pm, n, ch1 = pagemap()
    print(f"pass {it + 1}: {n} pdf pages, chapter 1 starts at pdf page {ch1 + 1}, missing: {[k for k, v in pm.items() if v == '?']}")
    lab = open("report/labels.json").read()
    if (pm, lab) == last: break
    last = (pm, lab); json.dump(pm, open("report/pagemap.json", "w"), indent=1)
print("done")
