"""
research/storm_bridge.py

Bridge Stanford STORM research output into the kahlus-science-kit document pipeline.

WHY THIS EXISTS
---------------
STORM (stanford-oval/storm, MIT) is a retrieval + multi-perspective outline engine.
It produces a researched, cited article. It has NO figure generation and NO document
typesetting -- verified by grepping the package: zero matplotlib imports.

kahlus-science-kit has the opposite shape: a house figure style, a LaTeX preamble, a
DOCX builder, and prose-quality skills. It has no research or retrieval stage.

They compose cleanly. STORM finds and structures the evidence; this kit renders it.

    STORM  ->  storm_bridge  ->  figures/ + latex/ + docx/
    (research)  (this file)      (publication artifact)

WHAT THIS DOES NOT DO
---------------------
It does not vendor STORM. STORM is installed separately (`pip install knowledge-storm`)
and this file only reads its output directory. That keeps licenses clean and means a
STORM upgrade does not require touching this repo.

Usage:
    python research/storm_bridge.py --storm-output ./storm_out/topic_name
    python research/storm_bridge.py --storm-output ./out --emit latex --figures
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "figures"))


# ─────────────────────────────────────────────────────────────────────────────
# STORM output model
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Citation:
    index: int
    url: str
    title: str = ""
    snippets: list = field(default_factory=list)

    @property
    def domain(self) -> str:
        m = re.search(r"https?://([^/]+)", self.url)
        return m.group(1).replace("www.", "") if m else "unknown"

    @property
    def is_primary(self) -> bool:
        """Peer-reviewed or preprint sources we'd actually cite in a paper."""
        d = self.domain
        return any(k in d for k in (
            "doi.org", "arxiv.org", "pubmed", "ncbi.nlm.nih.gov", "nature.com",
            "science.org", "sciencedirect", "springer", "wiley", "ieee.org",
            "acm.org", "aiaa.org", "asme.org", "iop.org", "plos", "biorxiv",
            "medrxiv", "jamanetwork", "nejm", "thelancet",
        ))


@dataclass
class StormArticle:
    topic: str
    sections: list           # [(level:int, heading:str, body:str)]
    citations: list          # [Citation]
    outline: str = ""

    @property
    def word_count(self) -> int:
        return sum(len(b.split()) for _, _, b in self.sections)


def load_storm_output(path: str) -> StormArticle:
    """Read a STORM run directory.

    STORM writes (names vary slightly by version):
        storm_gen_article_polished.txt | storm_gen_article.txt
        url_to_info.json
        storm_gen_outline.txt
    """
    def _first(*names):
        for n in names:
            p = os.path.join(path, n)
            if os.path.exists(p):
                return p
        return None

    art_path = _first("storm_gen_article_polished.txt", "storm_gen_article.txt")
    if art_path is None:
        raise FileNotFoundError(
            f"No STORM article found in {path}. Expected "
            "storm_gen_article_polished.txt or storm_gen_article.txt"
        )

    with open(art_path, encoding="utf-8") as f:
        raw = f.read()

    sections = []
    cur_level, cur_head, buf = 1, os.path.basename(path).replace("_", " "), []
    for line in raw.splitlines():
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            if buf:
                sections.append((cur_level, cur_head, "\n".join(buf).strip()))
                buf = []
            cur_level, cur_head = len(m.group(1)), m.group(2).strip()
        else:
            buf.append(line)
    if buf:
        sections.append((cur_level, cur_head, "\n".join(buf).strip()))

    citations = []
    url_path = _first("url_to_info.json")
    if url_path:
        with open(url_path, encoding="utf-8") as f:
            info = json.load(f)
        mapping = info.get("url_to_unified_index", {})
        meta = info.get("url_to_info", {})
        for url, idx in mapping.items():
            m = meta.get(url, {})
            citations.append(Citation(
                index=int(idx),
                url=url,
                title=m.get("title", ""),
                snippets=m.get("snippets", []),
            ))
        citations.sort(key=lambda c: c.index)

    outline = ""
    op = _first("storm_gen_outline.txt", "direct_gen_outline.txt")
    if op:
        with open(op, encoding="utf-8") as f:
            outline = f.read()

    topic = os.path.basename(os.path.normpath(path)).replace("_", " ")
    return StormArticle(topic=topic, sections=sections,
                        citations=citations, outline=outline)


# ─────────────────────────────────────────────────────────────────────────────
# Source audit — the part that matters
# ─────────────────────────────────────────────────────────────────────────────

def audit_sources(article: StormArticle) -> dict:
    """Grade the evidence base.

    STORM retrieves from the open web. A publication-quality document needs to
    know how much of its support is peer-reviewed versus a blog post. This makes
    that ratio explicit instead of leaving it buried in a reference list.
    """
    total = len(article.citations)
    primary = [c for c in article.citations if c.is_primary]
    by_domain: dict = {}
    for c in article.citations:
        by_domain[c.domain] = by_domain.get(c.domain, 0) + 1

    cited_idx = set()
    for _, _, body in article.sections:
        for m in re.finditer(r"\[(\d+)\]", body):
            cited_idx.add(int(m.group(1)))
    orphans = [c for c in article.citations if c.index not in cited_idx]

    return {
        "total_sources": total,
        "primary_sources": len(primary),
        "primary_fraction": (len(primary) / total) if total else 0.0,
        "unique_domains": len(by_domain),
        "top_domains": sorted(by_domain.items(), key=lambda kv: -kv[1])[:10],
        "uncited_sources": len(orphans),
        "sections": len(article.sections),
        "words": article.word_count,
    }


def figure_source_audit(article: StormArticle, output_dir: str,
                        name: str = "fig_source_audit.png") -> Optional[str]:
    """House-style bar chart of the evidence base. Real data only."""
    try:
        from style import apply_style, savefig, ACCENT, GRAY_MID
        import matplotlib.pyplot as plt
    except ImportError:
        print("[skip] matplotlib/style not available", file=sys.stderr)
        return None

    a = audit_sources(article)
    if not a["top_domains"]:
        print("[skip] no citations to plot", file=sys.stderr)
        return None

    apply_style()
    labels = [d for d, _ in a["top_domains"]][::-1]
    counts = [n for _, n in a["top_domains"]][::-1]
    prim = [any(k in d for k in ("doi", "arxiv", "pubmed", "ncbi", "ieee",
                                 "nature", "science", "springer", "wiley"))
            for d in labels]

    fig, ax = plt.subplots(figsize=(5.2, 0.34 * len(labels) + 1.1))
    ax.barh(range(len(labels)), counts,
            color=[ACCENT if p else GRAY_MID for p in prim],
            edgecolor="black", linewidth=0.6, height=0.68)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_xlabel("sources retrieved")
    ax.set_title(
        f"Evidence base: {a['primary_sources']}/{a['total_sources']} peer-reviewed "
        f"({a['primary_fraction']:.0%})", fontsize=8, loc="left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, linewidth=0.4, alpha=0.4)
    # counts are integers; don't let matplotlib invent 0.5 of a source
    from matplotlib.ticker import MaxNLocator
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    return savefig(fig, output_dir, name)


# ─────────────────────────────────────────────────────────────────────────────
# Emitters
# ─────────────────────────────────────────────────────────────────────────────

def _tex_escape(s: str) -> str:
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                 ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
                 ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}")]:
        s = s.replace(a, b)
    return s


def emit_latex(article: StormArticle, out_path: str) -> str:
    """Write a .tex body that plugs into latex/preamble.tex.

    STORM's [n] markers become \\cite{srcN} against a generated bibliography.
    """
    lvl = {1: "section", 2: "subsection", 3: "subsubsection", 4: "paragraph"}
    lines = [
        "% Generated by research/storm_bridge.py from STORM output.",
        "% Prose is machine-drafted: run skills/humanize.md over it before use,",
        "% then skills/ai-check.md to score what survived.",
        "",
        f"\\section*{{{_tex_escape(article.topic.title())}}}",
        "",
    ]
    for level, head, body in article.sections:
        if head:
            lines.append(f"\\{lvl.get(level,'paragraph')}{{{_tex_escape(head)}}}")
        body = _tex_escape(body)
        body = re.sub(r"\\\[(\d+)\\\]", r"\\cite{src\1}", body)
        body = re.sub(r"\[(\d+)\]", r"\\cite{src\1}", body)
        lines += [body, ""]

    if article.citations:
        lines += ["\\begin{thebibliography}{99}"]
        for c in article.citations:
            t = _tex_escape(c.title or c.domain)
            lines.append(f"\\bibitem{{src{c.index}}} {t}. \\url{{{c.url}}}")
        lines += ["\\end{thebibliography}"]

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("wrote", out_path)
    return out_path


def emit_markdown(article: StormArticle, out_path: str) -> str:
    a = audit_sources(article)
    lines = [f"# {article.topic.title()}", "",
             "> Draft from STORM. Machine-generated prose — humanize before publishing.",
             "",
             f"**{a['words']} words · {a['sections']} sections · "
             f"{a['total_sources']} sources "
             f"({a['primary_fraction']:.0%} peer-reviewed)**", ""]
    for level, head, body in article.sections:
        if head:
            lines.append("#" * min(level + 1, 6) + f" {head}")
        lines += [body, ""]
    if article.citations:
        lines += ["## References", ""]
        for c in article.citations:
            lines.append(f"{c.index}. {c.title or c.domain} — <{c.url}>")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("wrote", out_path)
    return out_path


# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--storm-output", required=True,
                   help="A STORM run directory")
    p.add_argument("--emit", choices=["latex", "markdown", "both"], default="both")
    p.add_argument("--figures", action="store_true",
                   help="Render the source-audit figure")
    p.add_argument("--out-dir", default="output/storm")
    args = p.parse_args()

    article = load_storm_output(args.storm_output)
    a = audit_sources(article)

    print(f"\n  topic      {article.topic}")
    print(f"  sections   {a['sections']}")
    print(f"  words      {a['words']}")
    print(f"  sources    {a['total_sources']} "
          f"({a['primary_sources']} peer-reviewed, {a['primary_fraction']:.0%})")
    print(f"  domains    {a['unique_domains']}")
    if a["uncited_sources"]:
        print(f"  ⚠ {a['uncited_sources']} retrieved sources are never cited in the text")
    if a["primary_fraction"] < 0.5:
        print("  ⚠ under half the evidence base is peer-reviewed — "
              "tighten the retrieval before treating this as a paper draft")
    print()

    os.makedirs(args.out_dir, exist_ok=True)
    stem = re.sub(r"\W+", "_", article.topic).strip("_").lower() or "article"

    if args.emit in ("latex", "both"):
        emit_latex(article, os.path.join(args.out_dir, f"{stem}.tex"))
    if args.emit in ("markdown", "both"):
        emit_markdown(article, os.path.join(args.out_dir, f"{stem}.md"))
    if args.figures:
        figure_source_audit(article, os.path.join(args.out_dir, "figures"))

    with open(os.path.join(args.out_dir, f"{stem}_audit.json"), "w") as f:
        json.dump(a, f, indent=2)

    print("\nNext:")
    print("  1. Run skills/humanize.md over the draft prose.")
    print("  2. Run skills/ai-check.md to score what's left.")
    print("  3. Verify every [n] actually supports its sentence. STORM retrieves; it does not vouch.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
