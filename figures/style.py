"""
figures/style.py
Shared matplotlib house style for Kahlus-science-kit.
Import this at the top of any figure script.

Usage:
    from style import apply_style, ACCENT, GRAY_FILL, savefig, box, arrow
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrow, Rectangle
import os

# ── palette ──────────────────────────────────────────────────────────────────
ACCENT    = "#8c1515"   # Stanford cardinal — the one accent color
GRAY_FILL = "#e8e8e8"   # light fill for neutral boxes
GRAY_MID  = "#bdbdbd"   # mid-gray for secondary bars


def apply_style():
    """Apply the Kahlus house rcParams. Call once at module level."""
    plt.rcParams.update({
        "font.family":      "serif",
        "font.serif":       ["Times New Roman", "STIXGeneral", "DejaVu Serif"],
        "font.size":        9,
        "xtick.direction":  "in",
        "ytick.direction":  "in",
        "axes.linewidth":   0.8,
        "figure.dpi":       200,
    })


def savefig(fig, output_dir, name, dpi=200):
    """Save fig to output_dir/name. Creates output_dir if needed."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, name)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", path)
    return path


# ── diagram primitives ────────────────────────────────────────────────────────

def box(ax, x, y, w, h, text, fill=None, fs=8, accent=False):
    """Draw a labeled rectangle. accent=True uses the ACCENT edge color."""
    if fill is None:
        fill = GRAY_FILL
    ec = ACCENT if accent else "black"
    lw = 1.1 if accent else 0.8
    r = Rectangle((x, y), w, h, facecolor=fill, edgecolor=ec, linewidth=lw)
    ax.add_patch(r)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(ax, x1, y1, x2, y2, accent=False):
    """Draw an annotate arrow between two points."""
    c = ACCENT if accent else "black"
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", color=c, lw=1.0),
    )


def clean_spines(ax, keep=("bottom", "left")):
    """Remove all spines except those in `keep`."""
    for spine in ax.spines:
        ax.spines[spine].set_visible(spine in keep)


# ── visual-standards checklist (runtime) ──────────────────────────────────────

def check_figure(fig, name=""):
    """
    Warn if a figure likely fails the visual standards.
    Not exhaustive — just catches the most common mistakes.
    """
    issues = []
    for ax in fig.axes:
        if not ax.get_xlabel() and ax.get_lines():
            issues.append("x-axis has no label")
        if not ax.get_ylabel() and ax.get_lines():
            issues.append("y-axis has no label")
    if issues:
        label = f"[{name}] " if name else ""
        for i in issues:
            print(f"WARNING {label}{i}")


# Apply style on import
apply_style()
