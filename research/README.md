# research/

The retrieval stage this kit didn't have.

## Why a bridge and not a fork

Stanford STORM is a research pipeline: it searches, asks questions from multiple
perspectives, builds an outline, and writes a cited article. It does not make
figures and it does not typeset. Verified, not assumed — the package has zero
matplotlib imports.

This kit does figures and typesetting and had no retrieval stage. Bridging beats
forking: STORM stays a pip dependency, upgrades don't touch this repo, and the
MIT license stays clean because no STORM code is vendored here.

## Use

    pip install knowledge-storm
    # ... run STORM, producing ./results/<topic>/
    python research/storm_bridge.py --storm-output ./results/<topic> --figures

Emits to `output/storm/`:

| File | What |
|---|---|
| `<topic>.tex` | LaTeX body, `[n]` becomes a cite key, with a generated bibliography |
| `<topic>.md` | Markdown with a reference list |
| `<topic>_audit.json` | The evidence-base audit as data |
| `figures/fig_source_audit.png` | House-style domain breakdown |

## What it tells you that STORM won't

- **What fraction of the evidence is peer-reviewed.** Classified by domain
  (doi.org, arXiv, PubMed, IEEE, AIAA, ASME, Nature, Science, and so on).
- **Which sources were retrieved but never cited.** Usually means the draft is
  thinner than its reference list suggests.
- **A warning under 50% peer-reviewed**, because at that point it isn't a paper
  draft yet.

## What it cannot do

Check whether a citation actually supports the sentence it's attached to. STORM
retrieves; it does not vouch. That step is yours.

## Test

    python research/test_storm_bridge.py   # 16 checks, offline, no keys
