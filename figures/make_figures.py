"""
figures/make_figures.py
Example figure set demonstrating the Kahlus house style.
Run: python make_figures.py
Output: ../output/figures/
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from style import ACCENT, GRAY_FILL, GRAY_MID, savefig, box, arrow, clean_spines

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUTPUT = os.path.join(os.path.dirname(__file__), "..", "output", "figures")


# ─────────────────────────────────────────────────────── 1. bar chart example
def example_bar():
    """Cohort-size bar chart — monochrome + one accent bar."""
    fig, ax = plt.subplots(figsize=(3.5, 2.4))
    names  = ["Dataset A", "Dataset B (key)", "Dataset C"]
    values = [78, 2056, 5793]
    colors = [GRAY_MID, ACCENT, GRAY_FILL]
    bars = ax.bar(names, values, color=colors, edgecolor="black", linewidth=0.7)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v + 90, f"{v:,}",
                ha="center", fontsize=8)
    ax.set_ylabel("Subjects with full recording")
    ax.set_ylim(0, 6600)
    clean_spines(ax)
    savefig(fig, OUTPUT, "fig_example_bar.png")


# ─────────────────────────────────────────────── 2. pipeline / flow diagram
def example_pipeline():
    """Horizontal pipeline with accent gate at the end."""
    fig, ax = plt.subplots(figsize=(6.4, 2.2))
    ax.set_xlim(0, 10); ax.set_ylim(0, 3); ax.axis("off")

    box(ax, 0.1, 1.1, 1.7, 0.8, "Raw data\ningest")
    box(ax, 2.2, 1.1, 1.7, 0.8, "Integrity\ngate")
    box(ax, 4.3, 1.1, 1.7, 0.8, "Feature\nextraction")
    box(ax, 6.4, 1.1, 1.7, 0.8, "Model\nfit")
    box(ax, 8.5, 1.1, 1.4, 0.8, "Claim\ngate", accent=True)

    # negative-control annotation below main line
    box(ax, 4.3, 0.05, 1.7, 0.65, "Negative controls\n(shuffle / shift)",
        fill="white", fs=7)

    arrow(ax, 1.8, 1.5, 2.2, 1.5)
    arrow(ax, 3.9, 1.5, 4.3, 1.5)
    arrow(ax, 6.0, 1.5, 6.4, 1.5)
    arrow(ax, 8.1, 1.5, 8.5, 1.5, accent=True)
    arrow(ax, 5.15, 0.7, 5.15, 1.1)

    savefig(fig, OUTPUT, "fig_example_pipeline.png")


# ──────────────────────────────────────────── 3. horizontal Gantt timeline
def example_timeline():
    """Project timeline (Gantt) — standard format for program overviews."""
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    tracks = [
        ("Track E (regulatory)",  0.0, 4.0, False),
        ("Track D (hardware)",    0.5, 5.0, False),
        ("Track C (community)",   1.0, 6.0, False),
        ("Track B (compute) ★",   1.0, 7.0, True),   # ★ = critical path
        ("Track A (software)",    0.0, 6.0, False),
    ]
    for i, (name, s, e, acc) in enumerate(tracks):
        ax.barh(i, e - s, left=s, height=0.55,
                color=ACCENT if acc else GRAY_FILL,
                edgecolor="black", linewidth=0.7)
        ax.text(-0.15, i, name, ha="right", va="center", fontsize=8)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlim(-4.6, 8.2)
    ax.set_ylim(-0.6, len(tracks) - 0.4)
    ax.set_yticks([])
    ax.set_xticks(range(0, 9))
    ax.set_xlabel("Weeks from project start")
    for spine in ["left", "top", "right"]:
        ax.spines[spine].set_visible(False)
    savefig(fig, OUTPUT, "fig_example_timeline.png")


# ──────────────────────────────────────────────────────── 4. two-domain wall
def example_governance():
    """Data governance boundary diagram."""
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")

    # left domain
    ax.add_patch(Rectangle((0.2, 0.3), 4.4, 3.4,
                            facecolor="white", edgecolor="black", lw=1.0))
    ax.text(2.4, 3.45, "Research domain (approved DUA)",
            fontsize=8, ha="center", style="italic")
    box(ax, 0.5, 2.2, 1.7, 0.8, "Raw data\n(licensed)", fs=7.5)
    box(ax, 2.6, 2.2, 1.7, 0.8, "Benchmark +\npublication", fs=7.5)
    box(ax, 1.5, 0.7, 1.9, 0.8, "Methods, code,\nfindings (open)", fs=7.5)
    arrow(ax, 2.2, 2.6, 2.6, 2.6)
    arrow(ax, 2.7, 2.2, 2.6, 1.5)

    # wall
    ax.plot([5.0, 5.0], [0.3, 3.7], color=ACCENT, lw=2.2)
    ax.text(5.0, 3.85, "no raw data or trained-model transfer",
            fontsize=7.5, ha="center", color=ACCENT)

    # right domain
    ax.add_patch(Rectangle((5.4, 0.3), 4.4, 3.4,
                            facecolor="white", edgecolor="black", lw=1.0))
    ax.text(7.6, 3.45, "Product domain (own IRB)",
            fontsize=8, ha="center", style="italic")
    box(ax, 5.7, 2.2, 1.7, 0.8, "Own\nrecordings", fs=7.5)
    box(ax, 7.8, 2.2, 1.7, 0.8, "Device models\n(product)", fs=7.5)
    box(ax, 6.7, 0.7, 1.9, 0.8, "Consent +\nlocal storage", fs=7.5)
    arrow(ax, 7.4, 2.6, 7.8, 2.6)
    arrow(ax, 7.6, 1.5, 7.7, 2.2)

    savefig(fig, OUTPUT, "fig_example_governance.png")


if __name__ == "__main__":
    example_bar()
    example_pipeline()
    example_timeline()
    example_governance()
    print("all example figures written to", OUTPUT)
