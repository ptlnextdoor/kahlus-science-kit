---
name: scientific-figures
description: Create publication-quality quantitative figures and ground the research claim behind them, for papers and ML venues (NeurIPS/ICML/Nature/Science). Routes internally to the right figure genre — law verification (predicted vs observed against an identity line), method sweep across a parameter, trend, comparison, distribution, relationship, matrix — so you never have to name the chart type. Use whenever generating any chart, plot, or figure for a paper, preprint, results doc, or formal report, or when checking whether a finding is novel and its baseline fair. Not for dashboards, slides, or architecture/schematic diagrams (hand-drawn in Illustrator/Figma/draw.io/TikZ, out of scope). Enforces a layout+label pipeline that cannot ship overlapping text or clipped labels.
license: Research and cited sources are public; this skill's own code is free to reuse.
---

# Scientific figures

Publication-grade **quantitative** figures, plus the research grounding that
decides whether the figure is worth making. One entry point — pick nothing, the
router below picks for you.

## The governing rule

**A figure must make its own falsification visible.** The reader should be able to
point at where a counterexample *would* appear — above the identity line, outside
the CI, in the empty region. A figure that could not have shown the claim failing
is decoration, not evidence.

This outranks every styling choice below. When a layout decision and this rule
conflict, this rule wins.

## Route first (do not skip)

Ask **what the figure has to prove**, not what the data looks like:

| The claim is… | Genre | Load |
|---|---|---|
| "this formula predicts that measurement" — a bound, scaling law, analytic truth | **law verification** | `references/genre-law-verification.md` |
| "these methods differ as parameter X varies" | **method sweep** | `references/genre-method-sweep.md` |
| "this quantity moves over time/training/epochs" | trend + uncertainty band | `references/common-patterns.md` |
| "these conditions differ" — and you care about effect size, not just stars | estimation plot, or points + CI | `references/common-patterns.md` |
| "here is the full distribution across units" | raincloud / KDE — never a bare bar hiding *n* | `references/common-patterns.md` |
| "these two variables relate" | scatter + regression band | `references/common-patterns.md` |
| "this matrix has structure" | heatmap (perceptually uniform cmap) | `references/common-patterns.md` |
| "is this finding new, and is the baseline fair?" | not a figure yet | `references/research-grounding.md` |

Two genres carry extra composition rules because they encode an argument, not
just data — load their file before writing code. The rest are chart-type choices
served by `common-patterns.md`.

If the answer is "I'm not sure what it has to prove", stop and settle that first.
That question is the whole design.

## The one styling rule that matters

**Manual label nudging is a bug, not a workflow.** If you call `ax.text(x, y, …)`
with hand-picked coordinates, or `ax.set_position()`, or eyeball a legend into an
empty corner — stop. Every documented collision (label-on-line, legend-on-peak,
clipped edge) traces back to a fixed coordinate that stopped being correct the
moment the data changed. The fix is always `constrained_layout`, an
outside/opaque legend, or a placement solver (`adjustText`/`textalloc`/
`labellines`). See `references/tool-stack.md`.

*Sanctioned exception:* the single provenance annotation in the law-verification
genre, anchored to one known point. Nothing else.

## Quick start

```python
import sys; sys.path.insert(0, "<this-skill-dir>/scripts")
import figure_style as fs

fs.use_paper_style()                       # SciencePlots + locked rcParams
fig, ax = fs.new_figure(cols=1)            # constrained_layout already on

ax.plot(x, y, color=fs.PALETTE[0])
texts = [ax.annotate(label, (xi, yi)) for xi, yi, label in points]
fs.place_labels(ax, texts)                 # adjustText, deterministic, seeded

fs.assert_no_clip(fig)                     # raises before you ship a clip
fs.save(fig, "out/my_figure")              # vector PDF + 300dpi PNG
```

`scripts/figure_style.py` is verified and importable; every dependency is
installed here (`references/tool-stack.md` for versions).

## Build order

1. **Route** (table above). Load the genre file if there is one.
2. **Ground the claim** if this is going in a paper —
   `references/research-grounding.md`. Novelty, comparators, baseline fairness.
   Cheaper to find the scoop now than after the figure.
3. **Style + layout.** `fs.use_paper_style()` + `constrained_layout=True`. Never
   `tight_layout()` with a suptitle or outside legend — it clips them.
4. **Labels through a solver**, never by hand. `loc="outside upper right"` for
   legends that must not steal axes space; opaque panel
   (`frameon=True, framealpha>0.9`) if it must sit inside.
5. **Colour** from `fs.PALETTE` / `fs.SEQUENTIAL` / `fs.DIVERGING` — perceptually
   uniform, colourblind-safe. Never jet/rainbow. Reserve exactly one saturated
   accent for the point that carries the story.
6. **Verify.** `fs.assert_no_clip(fig)` turns "no overlap" from an impression
   into a gate.
7. **Export both.** Vector PDF (`pdf.fonttype=42`, editable text — required by
   most venues) plus 300dpi PNG. `fs.save()` does both.
8. **Actually open the PNG.** The gate catches clipping, not bad judgment.

## Text that carries meaning

Applies to every genre:

- **Titles state the finding, not the axes.** `"286 configurations, 11 signals,
  0 violations"` beats `"observed vs predicted"`. Report the counterexample count
  even — especially — when it is zero.
- **Panel titles carry direction**: `"false-certify rate (lower is better)"`.
- **Axis labels carry the punchline in a parenthetical**: `"predicted bound $W/H$
  (from the methods section alone)"`.
- **A suptitle states the takeaway as a sentence**, so the conclusion lands before
  the axes are read.
- Real math in labels, not prose paraphrase.

## Guardrails

- **Regenerate from committed data**, never hand-place points. The figure must be
  reproducible from a named command.
- **Assert algebraic identities in the analysis code, not the plot.** Then
  machine-precision agreement is a check rather than a fit, and a wrong mask fails
  loudly instead of drawing a plausible curve.
- **Never clip axes to hide outliers.** The loose cases are usually where the
  explanation lives.
- **The headline metric gets its own panel.** Never fold it into another.
- Evidence a paper cites must live in a **tracked** path — `runs/` is typically
  gitignored, and a `.git/info/exclude` entry is invisible to `.gitignore`
  inspection and will silently swallow `git add -A`.

## Reference files (load only what you need)

| File | Load when |
|---|---|
| `references/genre-law-verification.md` | Predicted vs observed; verifying a bound or closed-form law |
| `references/genre-method-sweep.md` | Several methods across a swept parameter |
| `references/research-grounding.md` | Novelty check, comparators, baseline fairness, claim boundaries |
| `references/common-patterns.md` | Which chart type for a data shape; copy-paste patterns |
| `references/tool-stack.md` | Choosing a library; verified versions and what each does *not* solve |
| `references/design-theory.md` | The *why* — venue typography, colour theory, canonical literature |
| `references/checklist.md` | Pre-submission: DPI/format/font per venue, anti-pattern list |

Worked examples: `scripts/law_verification_example.py` →
`examples/law_verification.png` (the `inflation ≤ W/H` figure);
`scripts/sweep_figure.py` (the power-sweep helper).

## Out of scope

Architecture/method "hero" diagrams (nested modules, encoder-decoder schematics)
are **hand-composed in a vector editor** — Illustrator, Figma, draw.io, TikZ — by
essentially every top-venue paper. They are not plotted. If asked, say so and
offer to generate the *data thumbnails* (real depth maps, PCA-to-RGB feature
grids) for someone to compose, rather than faking a diagram in matplotlib.
Interactive dashboards (Plotly/Bokeh/Altair) are also out of scope; this skill
targets static paper figures.
