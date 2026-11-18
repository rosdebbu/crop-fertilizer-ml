"""Report engine: SRM project-report format (Times New Roman, 12 pt, 1.5 spacing, L 1 in / R 0.5 in,
chapters on new pages, Fig n.m below figures, Table n.m above tables, numbered citations).
Content lives in report_content.py; build_report.py runs the two-pass build that fills TOC page numbers."""
import json, os, re
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH as AL, WD_COLOR_INDEX, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

TW = 6.67  # text width in inches (A4 8.27 - 1.0 left - 0.6 right)
BODY_SPACING, BODY_AFTER = 1.15, 6
FONT = "Times New Roman"

PAGEMAP = {}            # key -> printed page string (filled from report/pagemap.json on pass 2)
RECS = []               # ordered records of headings / figures / tables for TOC, LoF, LoT
CITES = []              # citation keys in order of first appearance
REFS = {}               # key -> reference text (set by content module)
WARN = []
LABELS = json.load(open("report/labels.json")) if os.path.exists("report/labels.json") else {}   # key -> "7.3" (from previous pass)
NEWLABELS = {}

d = Document()


# ---------------- low-level helpers ----------------
def set_font(run, size=None, bold=None, italic=None, name=FONT):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    if size: run.font.size = Pt(size)
    if bold is not None: run.bold = bold
    if italic is not None: run.italic = italic


def cite_text(m):
    keys = [k.strip() for k in m.group(1).split(",")]
    nums = []
    for k in keys:
        if k not in REFS: raise KeyError(f"unknown reference {k}")
        if k not in CITES: CITES.append(k)
        nums.append(CITES.index(k) + 1)
    nums = sorted(set(nums)); out, i = [], 0
    while i < len(nums):                       # compress runs of 3+ as a-b, else comma list
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1: j += 1
        out.append(f"{nums[i]}-{nums[j]}" if j - i >= 2 else ",".join(str(n) for n in nums[i:j + 1]))
        i = j + 1
    return "[" + ",".join(out) + "]"


MARK = re.compile(r"(\*\*.+?\*\*|\[\[.+?\]\])")


def add_runs(p, text, size=12, bold=False, italic=False):
    text = re.sub(r"\{\{?num:([^}]+)\}\}?", lambda m: LABELS.get(m.group(1), "?.?"), text)
    text = re.sub(r"\{c:([^}]+)\}", cite_text, text)
    for chunk in MARK.split(text):
        if not chunk: continue
        r_bold, hl = bold, False
        if chunk.startswith("**"): chunk, r_bold = chunk[2:-2], True
        elif chunk.startswith("[["): chunk, hl = chunk[2:-2], True
        r = p.add_run(chunk); set_font(r, size, r_bold, italic)
        if hl: r.font.highlight_color = WD_COLOR_INDEX.YELLOW


def para(text="", size=12, bold=False, italic=False, align=AL.JUSTIFY, spacing=BODY_SPACING, after=BODY_AFTER, before=0,
         keep=False, indent=None, left=None, page_break=False):
    p = d.add_paragraph(); pf = p.paragraph_format
    p.alignment = align; pf.line_spacing = spacing; pf.space_after = Pt(after); pf.space_before = Pt(before)
    if keep: pf.keep_with_next = True
    if indent is not None: pf.first_line_indent = Inches(indent)
    if left is not None: pf.left_indent = Inches(left)
    if page_break: pf.page_break_before = True
    add_runs(p, text, size, bold, italic)
    return p


def set_cell_shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), fill); tcPr.append(sh)


def pagebreak():
    d.add_paragraph().add_run().add_break(__import__("docx.enum.text", fromlist=["WD_BREAK"]).WD_BREAK.PAGE)


# ---------------- body-content API ----------------
state = {"ch": 0, "fig": 0, "tab": 0, "sec": 0}


def P(text):
    if len(re.sub(r"\{c:[^}]+\}", "[0]", text).split()) > 135: WARN.append("long paragraph: " + text[:50])
    return para(text)


def BUL(items):
    for t in items:
        p = para("", after=4, left=0.45, indent=-0.25)
        add_runs(p, "•  " + t)
    d.paragraphs[-1].paragraph_format.space_after = Pt(12)


def NUM(items):
    for i, t in enumerate(items, 1):
        p = para("", after=4, left=0.45, indent=-0.3)
        add_runs(p, f"({i})  " + t)
    d.paragraphs[-1].paragraph_format.space_after = Pt(12)


def H1(num, title):
    state.update(ch=num, fig=0, tab=0, sec=0, eq=0)
    para(f"CHAPTER {num} {title.upper()}", 16, True, align=AL.CENTER, spacing=1.2, after=14, page_break=True, keep=True)
    RECS.append({"kind": "toc", "level": 0, "num": str(num), "title": title.upper(), "key": f"CHAPTER {num} {title.upper()}"})


def H2(title):
    state["sec"] += 1; num = f"{state['ch']}.{state['sec']}"; state["sub"] = 0
    text = f"{num} {title.upper()}"
    para(text, 14, True, align=AL.LEFT, after=6, before=6, keep=True, spacing=1.2)
    RECS.append({"kind": "toc", "level": 1, "num": num, "title": title.upper(), "key": text})


def H3(title):
    state["sub"] = state.get("sub", 0) + 1
    para(f"{state['ch']}.{state['sec']}.{state['sub']} {title.upper()}", 12, True, align=AL.LEFT, after=4, before=2, keep=True, spacing=1.2)


def FIG(path, caption, width=5.6, key=None):
    if "@@" in caption: caption, key = caption.split("@@")
    width = width * 0.78
    state["fig"] += 1; label = f"Fig {state['ch']}.{state['fig']}"
    if key: NEWLABELS[key] = f"{state['ch']}.{state['fig']}"
    p = d.add_paragraph(); p.alignment = AL.CENTER; pf = p.paragraph_format
    pf.keep_with_next = True; pf.space_after = Pt(4); pf.space_before = Pt(6)
    p.add_run().add_picture(path, width=Inches(width))
    para(f"{label}: {caption}", 11, False, True, align=AL.CENTER, spacing=1.1, after=10)
    RECS.append({"kind": "fig", "num": label, "title": caption, "key": f"{label}:"})


def _borders(tbl):
    tblPr = tbl._tbl.tblPr; b = OxmlElement("w:tblBorders")
    for e in ("top", "left", "bottom", "right", "insideH", "insideV"):
        x = OxmlElement(f"w:{e}"); x.set(qn("w:val"), "single"); x.set(qn("w:sz"), "6"); x.set(qn("w:color"), "000000"); b.append(x)
    tblPr.append(b)


def TABLE(caption, header, rows, widths=None, size=10.5, align_first_left=True, key=None):
    if "@@" in caption: caption, key = caption.split("@@")
    state["tab"] += 1; label = f"Table {state['ch']}.{state['tab']}"
    if key: NEWLABELS[key] = f"{state['ch']}.{state['tab']}"
    para(f"{label}: {caption}", 11, False, True, align=AL.CENTER, spacing=1.1, after=4, before=4, keep=True)
    RECS.append({"kind": "tab", "num": label, "title": caption, "key": f"{label}:"})
    t = d.add_table(rows=1, cols=len(header)); t.alignment = WD_TABLE_ALIGNMENT.CENTER; _borders(t)

    def fill(cells, vals, head=False):
        for k, (c, v) in enumerate(zip(cells, vals)):
            c.text = ""; p = c.paragraphs[0]; pf = p.paragraph_format
            pf.space_after = Pt(2); pf.space_before = Pt(2); pf.line_spacing = 1.0
            p.alignment = AL.LEFT if (k == 0 and align_first_left) else AL.CENTER
            add_runs(p, str(v), size, bold=head)
            if head: set_cell_shade(c, "D9E2D5")
    fill(t.rows[0].cells, header, True)
    for r in rows: fill(t.add_row().cells, r)
    for row in t.rows:
        trPr = row._tr.get_or_add_trPr(); cs = OxmlElement("w:cantSplit"); trPr.append(cs)
    for row in t.rows[:-1]:                      # keep the whole table on one page
        for c in row.cells:
            for pp in c.paragraphs: pp.paragraph_format.keep_with_next = True
    if widths:
        for row in t.rows:
            for c, w in zip(row.cells, widths): c.width = Inches(w)
    para("", spacing=1.0, after=4)


def EQ(text, key=None):
    state["eq"] = state.get("eq", 0) + 1; label = f"{state['ch']}.{state['eq']}"
    if key: NEWLABELS[key] = label
    p = para(f"{text}", 12, False, True, align=AL.CENTER, spacing=1.2, after=8)
    r = p.add_run(f"\t({label})"); set_font(r, 12)
    p.paragraph_format.tab_stops.add_tab_stop(Inches(TW), WD_TAB_ALIGNMENT.RIGHT)


def CODE(text, title=None):
    if title: para(title, 12, True, align=AL.LEFT, spacing=1.15, after=4, before=6, keep=True)
    for line in text.rstrip("\n").split("\n"):
        p = d.add_paragraph(); pf = p.paragraph_format
        pf.line_spacing = 1.0; pf.space_after = Pt(0); pf.left_indent = Inches(0.1)
        r = p.add_run(line.replace("\t", "    ").encode("ascii", "ignore").decode() or " "); set_font(r, 7, name="Courier New")
    para("", size=4, spacing=1.0, after=0)


# ---------------- sections / page numbering ----------------
def _clear_sect(sectPr):
    for tag in ("w:pgBorders", "w:pgNumType", "w:titlePg"):
        for el in sectPr.findall(qn(tag)): sectPr.remove(el)


def _insert_after_pgmar(sectPr, el):
    pgMar = sectPr.find(qn("w:pgMar")); pgMar.addnext(el)


def footer_page_number(section, fmt=None, start=None):
    sectPr = section._sectPr; _clear_sect(sectPr)
    n = OxmlElement("w:pgNumType")
    if fmt: n.set(qn("w:fmt"), fmt)
    if start is not None: n.set(qn("w:start"), str(start))
    _insert_after_pgmar(sectPr, n)
    section.footer.is_linked_to_previous = False
    fp = section.footer.paragraphs[0]; fp.alignment = AL.CENTER
    for r in list(fp.runs): r._r.getparent().remove(r._r)
    for kind, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        run = fp.add_run(); set_font(run, 12)
        if kind:
            fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), kind); run._r.append(fc)
        else:
            it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = txt; run._r.append(it)


def new_section():
    s = d.add_section(WD_SECTION.NEW_PAGE)
    _clear_sect(s._sectPr)
    return s


def setup_document():
    s = d.sections[0]
    s.page_width, s.page_height = Inches(8.27), Inches(11.69)
    s.left_margin, s.right_margin = Inches(1), Inches(0.6)
    s.top_margin, s.bottom_margin = Inches(0.9), Inches(0.85)
    s.footer_distance = Inches(0.4)
    st = d.styles["Normal"]; st.font.name = FONT; st.font.size = Pt(12)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    cp = d.core_properties
    cp.author = ""; cp.last_modified_by = ""; cp.comments = ""
    cp.title = "Crop Recommendation and Fertilizer Prediction Using Machine Learning - Project Report"


def page_border(section):
    b = OxmlElement("w:pgBorders"); b.set(qn("w:offsetFrom"), "page")
    for side in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{side}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "12")
        e.set(qn("w:space"), "24"); e.set(qn("w:color"), "000000"); b.append(e)
    _insert_after_pgmar(section._sectPr, b)


# ---------------- TOC / list pages ----------------
def leader_line(left_text, page, indent=0.0, num_w=0.0, size=12, bold=False, num=None):
    p = d.add_paragraph(); pf = p.paragraph_format
    pf.line_spacing = 1.0; pf.space_after = Pt(1.5); pf.left_indent = Inches(indent + num_w); pf.first_line_indent = Inches(-num_w)
    pf.tab_stops.add_tab_stop(Inches(TW), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    txt = (f"{num}\t" if num is not None and num_w else "") + left_text
    if num_w: pf.tab_stops.add_tab_stop(Inches(indent + num_w))
    r = p.add_run(txt); set_font(r, size, bold)
    r = p.add_run("\t" + str(page)); set_font(r, size, bold)
    return p


def pg(key, default="0"): return PAGEMAP.get(key, default)


def heading_center(text, size=16, page_break=False):
    return para(text, size, True, align=AL.CENTER, spacing=1.5, after=12, page_break=page_break)


def REF_TABLE(rows):
    """rows: (authors, title, venue, year) in citation order -> table like the sample report"""
    t = d.add_table(rows=1, cols=5); _borders(t); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    widths = [0.45, 1.55, 2.6, 1.55, 0.5]

    def fill(cells, vals, head=False):
        for c, v, w in zip(cells, vals, widths):
            c.width = Inches(w); c.text = ""; p = c.paragraphs[0]; pf = p.paragraph_format
            pf.space_after = Pt(0.5); pf.space_before = Pt(0.5); pf.line_spacing = 1.0; p.alignment = AL.LEFT
            add_runs(p, str(v), 7.5, bold=head)
            if head: set_cell_shade(c, "D9E2D5")
    fill(t.rows[0].cells, ["S.No.", "Authors", "Title", "Journal / Conference", "Year"], True)
    for i, r in enumerate(rows, 1): fill(t.add_row().cells, [i] + list(r))
    for row in t.rows:
        trPr = row._tr.get_or_add_trPr(); cs = OxmlElement("w:cantSplit"); trPr.append(cs)
