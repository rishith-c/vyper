"""Render the dimensioned VYPER-F4 vertical FC floorplan."""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

sys.path.insert(0, str(Path(__file__).parent))
import vyper_f4_layout as L

DIM = "#c02020"
fig, ax = plt.subplots(figsize=(7, 12), dpi=180)
w2, h2 = L.BOARD_W / 2, L.BOARD_H / 2
ax.add_patch(FancyBboxPatch(
    (-w2, -h2), L.BOARD_W, L.BOARD_H,
    boxstyle=f"round,pad=0,rounding_size={L.CORNER_R}",
    fc="#15553a", ec="#111111", lw=1.3))

for hx, hy in L.HOLES:
    ax.add_patch(Circle((hx, hy), L.GROMMET_KEEPOUT_D / 2,
                        fill=False, ec="#ffcb55", ls=":", lw=1.0))
    ax.add_patch(Circle((hx, hy), L.HOLE_D / 2,
                        fc="white", ec="black", lw=0.7))

for name, spec in L.PARTS.items():
    x, y = spec["pos"]
    pw, ph = spec["courtyard"]
    back = spec["side"] == "B"
    ax.add_patch(Rectangle(
        (x - pw / 2, y - ph / 2), pw, ph,
        fc="#335f88" if back else "#c98f32", alpha=0.9,
        ec="white", lw=0.55, ls="--" if back else "-"))
    ax.text(x, y, name.split("_")[0] + (" B" if back else ""),
            color="white", fontsize=5.4, ha="center", va="center")

for pads in L.PAD_GROUPS.values():
    for x, y, label in pads:
        ax.add_patch(Rectangle((x - L.IO_PAD_SIZE[0] / 2,
                                y - L.IO_PAD_SIZE[1] / 2),
                               *L.IO_PAD_SIZE,
                               fc="#d8d8d8", ec="#222", lw=0.3))
        ax.add_patch(Circle((x, y), L.IO_PAD_DRILL / 2,
                            fc="#333333", ec="#111", lw=0.2))
        ax.text(x, y, label, fontsize=4.5, ha="center", va="center")


def hdim(y, x1, x2, label):
    ax.annotate("", xy=(x1, y), xytext=(x2, y),
                arrowprops=dict(arrowstyle="<->", color=DIM, lw=1.0))
    ax.text((x1 + x2) / 2, y + 0.7, label, color=DIM,
            ha="center", fontsize=8, fontweight="bold")


def vdim(x, y1, y2, label):
    ax.annotate("", xy=(x, y1), xytext=(x, y2),
                arrowprops=dict(arrowstyle="<->", color=DIM, lw=1.0))
    ax.text(x + 0.7, (y1 + y2) / 2, label, color=DIM,
            va="center", rotation=90, fontsize=8, fontweight="bold")


hdim(-35.0, -w2, w2, f"{L.BOARD_W:.0f} mm")
vdim(-18.0, -h2, h2, f"{L.BOARD_H:.0f} mm")
hdim(34.5, -L.HOLE_PITCH_X / 2, L.HOLE_PITCH_X / 2,
     f"{L.HOLE_PITCH_X:.0f} mm")
vdim(18.0, -L.HOLE_PITCH_Y / 2, L.HOLE_PITCH_Y / 2,
     f"{L.HOLE_PITCH_Y:.0f} mm")

gx, gy = L.PARTS["U2_gyro_ICM42688P"]["pos"]
ax.annotate("gyro", xy=(gx, gy), xytext=(-13.5, 8.5), fontsize=7,
            arrowprops=dict(arrowstyle="->", lw=0.8))
ax.text(0, 38.0, "VYPER-F4 VERTICAL FLIGHT CONTROLLER",
        fontsize=11, fontweight="bold", ha="center")
ax.text(0, 36.4,
        f"{L.BOARD_W:.0f}×{L.BOARD_H:.0f} R3 | "
        f"{L.HOLE_PITCH_X:.0f}×{L.HOLE_PITCH_Y:.0f} soft mount | "
        f"4× Ø{L.HOLE_D:.1f} | all mm",
        fontsize=7.5, ha="center")
ax.text(0, -38.0, "solid = F.Cu major parts   dashed = B.Cu major parts",
        fontsize=7, ha="center", color="#333")
ax.set_xlim(-21, 21)
ax.set_ylim(-40, 40)
ax.set_aspect("equal")
ax.axis("off")
fig.tight_layout()
out = Path(__file__).parent / "vyper_f4_dimensions.png"
fig.savefig(out, facecolor="white", bbox_inches="tight")
print("wrote", out)
