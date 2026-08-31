"""
docx/helpers.py
Reusable python-docx helpers for the Kahlus ME-report house style.
Every document built with make_docs.py imports from here.
"""
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ACCENT_RGB = RGBColor(0x8C, 0x15, 0x15)


# ── document setup ────────────────────────────────────────────────────────────

def new_doc(margins=(0.9, 0.9, 1.0, 1.0)):
    """Create a new Document with Times New Roman Normal style and Page X of Y footer."""
    doc = Document()
    _set_style(doc, margins)
    _add_page_footer(doc)
    return doc


def _set_style(doc, margins):
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    st.paragraph_format.space_after = Pt(4)
    st.paragraph_format.space_before = Pt(0)
    top, bot, left, right = margins
    for sec in doc.sections:
        sec.top_margin    = Inches(top)
        sec.bottom_margin = Inches(bot)
        sec.left_margin   = Inches(left)
        sec.right_margin  = Inches(right)


def _add_page_footer(doc):
    """Footer: centered 'Page X of Y' using Word field codes."""
    footer = doc.sections[0].footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def fld(instr):
        r = OxmlElement("w:r")
        f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
        it = OxmlElement("w:instrText")
        it.set(qn("xml:space"), "preserve"); it.text = instr
        f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "end")
        r.append(f1); r.append(it); r.append(f2)
        return r

    p.add_run("Page ").font.size = Pt(9)
    p._p.append(fld("PAGE"))
    p.add_run(" of ").font.size = Pt(9)
    p._p.append(fld("NUMPAGES"))
    for r in p.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(9)


# ── structural blocks ─────────────────────────────────────────────────────────

def hrule(doc, size=12):
    """Horizontal rule (paragraph border)."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(2)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"),   "single")
    bottom.set(qn("w:sz"),    str(size))
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "000000")
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p


def center(doc, text, bold=False, italic=False, size=11, caps=False, space_after=2):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(space_after)
    r = p.add_run(text.upper() if caps else text)
    r.bold   = bold
    r.italic = italic
    r.font.size = Pt(size)
    return p


def title_block(doc, dept, institution, title, subtitle, doc_type,
                prepared="Author", submitted="Supervisor", date="", builds_on=None):
    """
    Standard ME-report title block:
      DEPT NAME (bold, centered)
      Institution line
      ══════════════════════
      Title (large, bold)
      Subtitle (italic, small)
      ══════════════════════
      Submitted to / Prepared by / Date / Doc type table
      Builds directly on: … (optional)
    """
    center(doc, dept, bold=True, size=13)
    center(doc, institution, italic=True, size=10)
    hrule(doc, 16)
    center(doc, title, bold=True, size=14, space_after=1)
    center(doc, subtitle, italic=True, size=10)
    hrule(doc, 16)

    tb = doc.add_table(rows=4, cols=2)
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    rows_data = [
        ("Submitted to:", submitted),
        ("Prepared by:", prepared),
        ("Date:", date),
        ("Document type:", doc_type),
    ]
    for i, (k, v) in enumerate(rows_data):
        c0, c1 = tb.rows[i].cells
        c0.paragraphs[0].add_run(k).bold = True
        c1.paragraphs[0].add_run(v)
        c0.width = Inches(1.6)
        c1.width = Inches(4.9)
        for c in (c0, c1):
            c.paragraphs[0].paragraph_format.space_after = Pt(1)
            for r in c.paragraphs[0].runs:
                r.font.size = Pt(10)

    if builds_on:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        r = p.add_run("Builds directly on: ")
        r.bold = True; r.font.size = Pt(10)
        r2 = p.add_run(builds_on)
        r2.font.size = Pt(10); r2.italic = True


def abstract(doc, text):
    """Bold 'Abstract.' lead-in followed by body text and a thin hrule."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.add_run("Abstract.  ").bold = True
    p.add_run(text)
    hrule(doc, 6)


_section_counters = {}

def section(doc, key, title):
    """Auto-numbered bold section heading. key scopes the counter to one document."""
    n = _section_counters.get(key, 0) + 1
    _section_counters[key] = n
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after  = Pt(3)
    r = p.add_run(f"{n}.  {title}")
    r.bold = True
    r.font.size = Pt(12)
    return p


def body(doc, text):
    p = doc.add_paragraph(text)
    p.paragraph_format.space_after = Pt(4)
    return p


def bullets(doc, items):
    for it in items:
        p = doc.add_paragraph(it, style="List Bullet")
        p.paragraph_format.space_after = Pt(1)
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)


def caption(doc, label, text):
    """Bold label + body text, centered, small."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(8)
    p.add_run(label + "  ").bold = True
    p.runs[0].font.size = Pt(9)
    r2 = p.add_run(text)
    r2.font.size = Pt(9)


def figure(doc, path, width_inches, label, cap):
    """Insert a figure from path with a caption. Warns if file missing."""
    if not os.path.exists(path):
        print("WARNING: missing figure", path)
        body(doc, f"[MISSING FIGURE: {path}]")
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(path, width=Inches(width_inches))
    caption(doc, label, cap)


def table(doc, label, cap, header, rows, widths=None, font=9.5):
    """Booktabs-style table (Table Grid style) with bold header and caption above."""
    caption(doc, label, cap)
    tb = doc.add_table(rows=1 + len(rows), cols=len(header))
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    tb.style = "Table Grid"
    for j, h in enumerate(header):
        tb.rows[0].cells[j].paragraphs[0].add_run(h).bold = True
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            tb.rows[i + 1].cells[j].paragraphs[0].add_run(str(v))
    for row in tb.rows:
        for j, c in enumerate(row.cells):
            if widths:
                c.width = Inches(widths[j])
            for para in c.paragraphs:
                para.paragraph_format.space_after = Pt(1)
                for r in para.runs:
                    r.font.size = Pt(font)
                    r.font.name = "Times New Roman"
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return tb


def references(doc, refs):
    """Numbered reference list at the document end."""
    hrule(doc, 6)
    p = doc.add_paragraph()
    p.add_run("Selected references.").bold = True
    p.runs[0].font.size = Pt(8.5)
    for i, ref in enumerate(refs, 1):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.add_run(f"[{i}] {ref}").font.size = Pt(8)
