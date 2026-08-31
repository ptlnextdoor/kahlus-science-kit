# Scientific document workflow

How we build every research document for the Kahlus program — figures, DOCX, and PDF.

---

## The three-layer stack

```
Layer 1: Raw data / geometry
    ↓
Layer 2: Python scripts → PNG figures  (figures/make_figures.py)
    ↓
Layer 3: Document builder             (docx/make_docs.py  OR  latex/template.tex)
    ↓
Output: .docx  /  .pdf
```

Everything is code. Nothing is manually formatted. Re-running the scripts produces
identical output.

---

## Layer 1 — data

Figures are generated from one of:
- **Real data** (experimental results, cohort sizes, cost tables)
- **Accurate geometry** (block diagrams where boxes represent real components)
- **External CC-licensed images** — always cited in the caption with license

We never use AI-generated images. We never invent curves or numbers.

---

## Layer 2 — figures (`figures/make_figures.py`)

Each figure is one Python function. The function:
1. Creates a `fig, ax = plt.subplots(...)` with a specific `figsize`
2. Draws the data using matplotlib primitives (bar, barh, annotate, Rectangle, …)
3. Calls `savefig(fig, output_dir, name)` → PNG written to `output/figures/`

The shared `style.py` applies rcParams once on import:

```python
plt.rcParams.update({
    "font.family": "serif",
    "font.serif":  ["Times New Roman", "STIXGeneral", "DejaVu Serif"],
    "font.size":   9,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "axes.linewidth":  0.8,
})
```

Palette:
- `ACCENT = "#8c1515"` — Stanford cardinal, used ≤ 2× per figure for the key element
- `GRAY_FILL = "#e8e8e8"` — neutral boxes
- `GRAY_MID  = "#bdbdbd"` — secondary bars

Diagram helpers:

```python
box(ax, x, y, w, h, text, accent=False)   # labeled rectangle
arrow(ax, x1, y1, x2, y2, accent=False)   # annotate arrow
clean_spines(ax, keep=("bottom","left"))   # remove excess spines
```

---

## Layer 3A — DOCX (`docx/make_docs.py`)

Uses `python-docx`. Every document calls the same helpers from `docx/helpers.py`:

```python
doc = new_doc()                      # Times New Roman + Page X of Y footer
title_block(doc, dept, institution,
            title, subtitle, doc_type,
            prepared, submitted, date, builds_on)
abstract(doc, "...")
section(doc, "key", "Section title") # auto-numbered per document
body(doc, "...")
bullets(doc, ["item 1", "item 2"])
figure(doc, "path/to.png", 6.0, "Figure 1.", "Caption text.")
table(doc, "Table 1.", "Caption.", header=[...], rows=[...], widths=[...])
references(doc, ["[1] ...", "[2] ..."])
doc.save("output.docx")
```

The `title_block()` produces the standard ME department heading:
```
DEPARTMENT OF MECHANICAL ENGINEERING
Institution name
══════════════════════════════════════
Document Title (large bold)
Subtitle (italic, small)
══════════════════════════════════════
Submitted to: ...     Date: ...
Prepared by:  ...     Type: ...
Builds directly on: ...
```

---

## Layer 3B — LaTeX (`latex/template.tex`)

Documents `\input{preamble}` and call `\kahlustitle{lhead}{title}{subtitle}{type}{builds-on}`.
Then use normal LaTeX: `\section`, `\begin{itemize}`, `\begin{table}[H]`, `\includegraphics`.

Figures reference the PNG output from Layer 2:
```latex
\includegraphics[width=0.88\textwidth]{../output/figures/fig_example_pipeline.png}
```

Compile:
```bash
pdflatex template.tex
pdflatex template.tex   # second pass for page count
```

---

## Visual standards checklist

Before committing a figure, verify:

- [ ] Every axis has a label with units
- [ ] Accent color used ≤ 2× (on the most important element only)
- [ ] No text drawn over data
- [ ] No invented numbers — every value traces to a real source or real geometry
- [ ] Caption follows format: `Figure N.  Bold-label followed by a sentence.`
- [ ] Survives black-and-white printing (accent is darker, not just differently colored)
- [ ] `dpi=200`, `bbox_inches="tight"`, `facecolor="white"` in `savefig`

---

## Adding a new project

1. Add a new figure function to `figures/make_figures.py`, call it from `__main__`.
2. Add a new `build_pXX()` function to `docx/make_docs.py` (or a new `pXX.tex`).
3. Call `python figures/make_figures.py` first, then `python docx/make_docs.py`.
4. Commit both the scripts and the generated PNGs. (PNGs are committed so the
   document build works without re-running the science pipeline.)

---

## AI agent prompt

When delegating to an AI agent:

> "Build a Kahlus-style scientific document for [project].
> Read kahlus-science-kit/docs/workflow.md for the format.
> Generate figures with matplotlib using the style in figures/style.py.
> Build the DOCX with helpers in docx/helpers.py.
> Use only real data or real geometry — no invented numbers, no AI images.
> One accent color #8c1515. Times New Roman. Page X of Y footer. Bold-label captions."
