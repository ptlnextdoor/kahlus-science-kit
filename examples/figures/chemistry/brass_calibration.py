"""
chemistry/brass_calibration.py
AP Chemistry: Beer's Law calibration curve for Cu²⁺ in brass.

Real lab data:
  Standards at 640 nm: [Cu²⁺] = 0.05, 0.10, 0.20, 0.40 M
                        A      = 0.126, 0.280, 0.582, 1.139
  Brass unknown absorbance: 0.301 → [Cu²⁺] = 0.105 M → 69% Cu by mass

House style: serif, one accent color (#8c1515), residual panel below.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import linregress
import os

# ── real data ────────────────────────────────────────────────────────────────
conc   = np.array([0.05, 0.10, 0.20, 0.40])   # M
absorp = np.array([0.126, 0.280, 0.582, 1.139])

brass_A   = 0.301   # measured absorbance of brass unknown
brass_pct = 69.0    # percent Cu by mass (from dilution math)

# ── linear regression (Beer's Law: A = ε·l·c, force through 0) ──────────────
# OLS with intercept = 0: slope = sum(x*y)/sum(x²)
slope = np.dot(conc, absorp) / np.dot(conc, conc)
fitted   = slope * conc
residuals = absorp - fitted
ss_res = np.sum(residuals**2)
ss_tot = np.sum((absorp - absorp.mean())**2)
r2 = 1 - ss_res / ss_tot
brass_conc = brass_A / slope   # 0.105 M

# ── rcParams ─────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":      "serif",
    "font.serif":       ["Times New Roman", "STIXGeneral", "DejaVu Serif"],
    "font.size":        10,
    "xtick.direction":  "in",
    "ytick.direction":  "in",
    "axes.linewidth":   0.9,
})

ACCENT = "#8c1515"
BLUE   = "#3a6ea5"

# ── figure ───────────────────────────────────────────────────────────────────
fig, (ax_main, ax_res) = plt.subplots(
    2, 1, figsize=(5.2, 5.2),
    gridspec_kw={"height_ratios": [3.5, 1], "hspace": 0.08},
    sharex=True,
)

# main: fit line
x_line = np.array([0, 0.45])
ax_main.plot(x_line, slope * x_line, color="gray", lw=1.4, zorder=1,
             label=rf"fit  $A = {slope:.3f}[\mathrm{{Cu}}^{{2+}}]$  ($R^2 = {r2:.3f}$)")

# standards
ax_main.scatter(conc, absorp, color=BLUE, s=55, zorder=3,
                label="standards (640 nm)")

# brass unknown with dashed drop-lines
ax_main.scatter([brass_conc], [brass_A], marker="D", color=ACCENT, s=80, zorder=4,
                label=rf"brass unknown $\rightarrow$ {brass_conc:.3f} M")
ax_main.plot([0, brass_conc], [brass_A, brass_A], color=ACCENT,
             lw=0.9, ls="--", zorder=2)
ax_main.plot([brass_conc, brass_conc], [0, brass_A], color=ACCENT,
             lw=0.9, ls="--", zorder=2)

ax_main.set_ylabel(r"absorbance $A$ (640 nm)")
ax_main.set_ylim(0, 1.25)
ax_main.set_xlim(0, 0.45)
ax_main.legend(fontsize=8.5, framealpha=0.9)
ax_main.set_title(f"Brass: {brass_pct:.0f}% Cu by mass", fontsize=11)
for sp in ["top", "right"]:
    ax_main.spines[sp].set_visible(False)

# residual panel
ax_res.axhline(0, color="gray", lw=0.9)
ax_res.scatter(conc, residuals, color=BLUE, s=55, zorder=3)
ax_res.set_ylabel("residual")
ax_res.set_xlabel(r"standard concentration $[\mathrm{Cu}^{2+}]$ (M)")
ax_res.set_ylim(-0.025, 0.025)
for sp in ["top", "right"]:
    ax_res.spines[sp].set_visible(False)

out = os.path.join(os.path.dirname(__file__), "brass_calibration.png")
fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
plt.close(fig)
print("wrote", out)
