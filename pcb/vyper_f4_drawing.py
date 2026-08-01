"""Dimensioned drawing of the VYPER-F4, generated from the same layout module.

Produces vyper_f4_dimensions.png: board outline with the dimensions a fab or
a builder actually needs -- overall size, hole pattern, hole size, corner
radius, the fuselage-cavity circle the corners must clear, gyro offsets and
the gyro-to-inductor exclusion.

Run:  ../.venv/bin/python vyper_f4_drawing.py
"""

import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle

sys.path.insert(0, str(Path(__file__).parent))
import vyper_f4_layout as L

FIG_BG = "#ffffff"
BOARD_FC = "#1a5c38"
DIM = "#c02020"
NOTE = "#333333"

fig, ax = plt.subplots(figsize=(11, 11), dpi=160)
ax.set_facecolor(FIG_BG)

w2, h2, r = L.BOARD_W / 2, L.BOARD_H / 2, L.CORNER_R

# Board with true rounded corners
ax.add_patch(FancyBboxPatch((-w2, -h2), L.BOARD_W, L.BOARD_H,
                            boxstyle=f"round,pad=0,rounding_size={r}",
                            fc=BOARD_FC, ec="black", lw=1.2, alpha=0.92))

# Fuselage cavity circle the corners must clear
ax.add_patch(Circle((0, 0), L.FUSE_CAVITY_R, fill=False, ec="#2060c0",
                    lw=1.4, ls="--"))
ax.text(-L.FUSE_CAVITY_R * 0.02, L.FUSE_CAVITY_R + 0.7,
        f"fuselage cavity  Ø{2 * L.FUSE_CAVITY_R:.0f}",
        color="#2060c0", ha="center", fontsize=9)
reach = math.sqrt(2) * (w2 - r) + r
ax.annotate(f"corner reach {reach:.1f} < R{L.FUSE_CAVITY_R:.0f}  "
            f"(square board = 25.5, does not fit)",
            xy=(reach / math.sqrt(2), reach / math.sqrt(2)),
            xytext=(6.5, 27.5), color="#2060c0", fontsize=8.5,
            arrowprops=dict(arrowstyle="->", color="#2060c0", lw=0.9))

# Holes + grommet keepouts
for hx, hy in L.HOLES:
    ax.add_patch(Circle((hx, hy), L.HOLE_D / 2, fc="white", ec="black", lw=0.8))
    ax.add_patch(Circle((hx, hy), L.GROMMET_KEEPOUT_D / 2, fill=False,
                        ec="#c08020", lw=0.9, ls=":"))
ax.text(L.HOLE_PITCH / 2 + 3.4, L.HOLE_PITCH / 2 - 4.6,
        f"4x Ø{L.HOLE_D:.1f}\n(M3 grommet)\nkeepout Ø{L.GROMMET_KEEPOUT_D:.0f}",
        color="#c08020", fontsize=8, ha="left")

# Parts
for name, spec in L.PARTS.items():
    x, y = spec["pos"]
    w, h = spec["courtyard"]
    back = spec["side"] == "B"
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fill=back,
                           fc="#00000030" if back else "none",
                           ec="#dddddd" if not back else "#888888",
                           lw=1.0, ls="-" if not back else "--"))
    ax.text(x, y, name.split("_")[0] + ("\n(B)" if back else ""),
            color="white" if not back else "#dddddd",
            ha="center", va="center", fontsize=7.5)

for pads in L.PAD_GROUPS.values():
    for x, y, label in pads:
        ax.add_patch(Rectangle((x - 0.8, y - 0.8), 1.6, 1.6, fc="#c8c8c8",
                               ec="none"))

# Gyro-to-inductor exclusion
gx, gy = L.PARTS["U2_gyro_ICM42688P"]["pos"]
lx, ly = L.PARTS["L1_buck_inductor"]["pos"]
d = math.hypot(lx - gx, ly - gy)
ax.annotate("", xy=(lx, ly - 2.3), xytext=(gx, gy + 2.5),
            arrowprops=dict(arrowstyle="<->", color="#f0f0f0", lw=1.0))
ax.text(gx + 1.0, (gy + ly) / 2, f"{d:.1f}\n(≥10)", color="#f0f0f0",
        fontsize=8, ha="left")


def hdim(y, x1, x2, text, offset=1.6):
    ax.annotate("", xy=(x1, y), xytext=(x2, y),
                arrowprops=dict(arrowstyle="<->", color=DIM, lw=1.1))
    ax.text((x1 + x2) / 2, y + offset, text, color=DIM, ha="center",
            fontsize=10, fontweight="bold")


def vdim(x, y1, y2, text, offset=1.2):
    ax.annotate("", xy=(x, y1), xytext=(x, y2),
                arrowprops=dict(arrowstyle="<->", color=DIM, lw=1.1))
    ax.text(x + offset, (y1 + y2) / 2, text, color=DIM, va="center",
            rotation=90, fontsize=10, fontweight="bold")


hdim(-h2 - 4.6, -w2, w2, f"{L.BOARD_W:.0f}")
vdim(-w2 - 4.6, -h2, h2, f"{L.BOARD_H:.0f}")
hdim(-h2 - 8.6, -L.HOLE_PITCH / 2, L.HOLE_PITCH / 2, f"{L.HOLE_PITCH}")
vdim(-w2 - 8.6, -L.HOLE_PITCH / 2, L.HOLE_PITCH / 2, f"{L.HOLE_PITCH}")

ax.annotate(f"R{r:.0f}", xy=(w2 - r * 0.3, -h2 + r * 0.3), xytext=(24, -22),
            color=DIM, fontsize=10, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=DIM, lw=1.0))
ax.annotate(f"gyro ({gx:.0f}, {gy:+.1f})", xy=(gx, gy), xytext=(-27, 21),
            color=NOTE, fontsize=9,
            arrowprops=dict(arrowstyle="->", color=NOTE, lw=0.9))

ax.text(0, -h2 - 13.5,
        "VYPER-F4  36 x 36 / 30.5 x 30.5   |   dashed = B side   |   all mm",
        ha="center", fontsize=10, color=NOTE)

ax.set_xlim(-34, 34)
ax.set_ylim(-34, 32)
ax.set_aspect("equal")
ax.axis("off")
fig.tight_layout()
out = Path(__file__).parent / "vyper_f4_dimensions.png"
fig.savefig(out, facecolor=FIG_BG)
print("wrote", out)
