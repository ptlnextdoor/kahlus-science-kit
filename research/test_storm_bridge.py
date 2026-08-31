"""
research/test_storm_bridge.py

Assert-based self-check. No framework, no network, no API keys.
Builds a synthetic STORM output directory, runs the bridge over it, and checks
every claim the bridge makes about parsing, auditing, and emitting.

    python research/test_storm_bridge.py
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from storm_bridge import (  # noqa: E402
    Citation, load_storm_output, audit_sources, emit_latex, emit_markdown,
)

ARTICLE = """# Background

Cold plasma reduces bacterial load in chronic wounds [1]. A randomized trial
found significant wound area reduction [2].

## Mechanism

Reactive species drive the effect [3]. Standoff distance changes which species
reach the surface [1].

# Limitations

Study quality is heterogeneous [2].
"""

URL_INFO = {
    "url_to_unified_index": {
        "https://doi.org/10.1001/jamanetworkopen.2020.10411": 1,
        "https://pubmed.ncbi.nlm.nih.gov/32176094/": 2,
        "https://someblog.example.com/plasma-post": 3,
        "https://anotherblog.example.com/never-cited": 4,
    },
    "url_to_info": {
        "https://doi.org/10.1001/jamanetworkopen.2020.10411": {
            "title": "Cold Atmospheric Plasma vs Standard Therapy", "snippets": ["a"]},
        "https://pubmed.ncbi.nlm.nih.gov/32176094/": {
            "title": "Five year mortality DFU", "snippets": ["b"]},
        "https://someblog.example.com/plasma-post": {
            "title": "A blog about plasma", "snippets": ["c"]},
        "https://anotherblog.example.com/never-cited": {
            "title": "Orphan source", "snippets": ["d"]},
    },
}

OUTLINE = "# Background\n## Mechanism\n# Limitations\n"


def build_fixture(root: str) -> str:
    d = os.path.join(root, "cold_plasma_wounds")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "storm_gen_article_polished.txt"), "w") as f:
        f.write(ARTICLE)
    with open(os.path.join(d, "url_to_info.json"), "w") as f:
        json.dump(URL_INFO, f)
    with open(os.path.join(d, "storm_gen_outline.txt"), "w") as f:
        f.write(OUTLINE)
    return d


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="stormtest_")
    checks = 0
    try:
        d = build_fixture(tmp)

        # ── parsing ──────────────────────────────────────────────────────────
        art = load_storm_output(d)
        assert art.topic == "cold plasma wounds", art.topic
        checks += 1

        heads = [h for _, h, _ in art.sections]
        assert "Background" in heads and "Mechanism" in heads and "Limitations" in heads, heads
        checks += 1

        levels = {h: l for l, h, _ in art.sections}
        assert levels["Background"] == 1 and levels["Mechanism"] == 2, levels
        checks += 1

        assert len(art.citations) == 4, len(art.citations)
        assert art.citations[0].index == 1, "citations must sort by index"
        checks += 1

        assert art.word_count > 20, art.word_count
        checks += 1

        # ── domain + primary-source classification ───────────────────────────
        assert Citation(1, "https://doi.org/10.1/x").is_primary
        assert Citation(2, "https://pubmed.ncbi.nlm.nih.gov/1/").is_primary
        assert Citation(3, "https://arxiv.org/abs/2402.14207").is_primary
        assert not Citation(4, "https://someblog.example.com/p").is_primary
        checks += 1

        assert Citation(1, "https://www.nature.com/articles/x").domain == "nature.com"
        checks += 1

        # ── audit ────────────────────────────────────────────────────────────
        a = audit_sources(art)
        assert a["total_sources"] == 4, a
        assert a["primary_sources"] == 2, a          # doi + pubmed
        assert abs(a["primary_fraction"] - 0.5) < 1e-9, a
        checks += 1

        # source 4 appears in url_to_info but never as [4] in the body
        assert a["uncited_sources"] == 1, a
        checks += 1

        assert a["unique_domains"] == 4, a
        checks += 1

        # ── LaTeX emit ───────────────────────────────────────────────────────
        tex = emit_latex(art, os.path.join(tmp, "out", "a.tex"))
        body = open(tex).read()
        assert "\\cite{src1}" in body, "STORM [n] must become \\cite{srcN}"
        assert "[1]" not in body, "raw [n] markers must not survive"
        checks += 1

        assert "\\begin{thebibliography}" in body and "\\bibitem{src1}" in body
        checks += 1

        assert "\\subsection{Mechanism}" in body, "level 2 must map to subsection"
        checks += 1

        # ── markdown emit ────────────────────────────────────────────────────
        md = emit_markdown(art, os.path.join(tmp, "out", "a.md"))
        mbody = open(md).read()
        assert "## References" in mbody
        assert "50% peer-reviewed" in mbody, mbody[:400]
        checks += 1

        # ── failure mode ─────────────────────────────────────────────────────
        empty = os.path.join(tmp, "empty")
        os.makedirs(empty, exist_ok=True)
        try:
            load_storm_output(empty)
            raise AssertionError("must raise on a directory with no article")
        except FileNotFoundError:
            checks += 1

        # ── escaping ─────────────────────────────────────────────────────────
        art.sections = [(1, "Cost & Scope", "50% of cases cost $3 per unit_x")]
        tex2 = emit_latex(art, os.path.join(tmp, "out", "b.tex"))
        b = open(tex2).read()
        assert r"\&" in b and r"\%" in b and r"\$" in b and r"\_" in b, "LaTeX escaping failed"
        checks += 1

        print(f"\n  all {checks} checks passed")
        return 0
    except AssertionError as e:
        print(f"\n  FAILED after {checks} checks: {e}", file=sys.stderr)
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
