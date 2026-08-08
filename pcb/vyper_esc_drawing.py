"""Render the VYPER-55A EVT two-face floorplan from vyper_esc_layout.py."""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

sys.path.insert(0, str(Path(__file__).parent))
import vyper_esc_layout as L

COLORS = {
    "Q_": "#d9a441",
    "U_DRV": "#922f37",
    "U_MCU": "#355c9a",
    "RN_": "#7a6a9d",
    "TH_": "#35a56b",
}


def color_for(name):
    return next((c for prefix, c in COLORS.items() if name.startswith(prefix)),
                "#777777")


fig, axes = plt.subplots(1, 2, figsize=(13, 7), dpi=180)
for ax, side, title in zip(axes, ("F", "B"), ("TOP / F.Cu", "BOTTOM / B.Cu")):
    ax.add_patch(FancyBboxPatch((-18, -18), 36, 36,
                                boxstyle="round,pad=0,rounding_size=5",
                                fc="#153b2b", ec="#111111", lw=1.2))
    ax.add_patch(Circle((0, 0), L.FUSE_CAVITY_R, fill=False,
                        ec="#2b6fd6", lw=0.9, ls="--"))
    for hx, hy in L.HOLES:
        ax.add_patch(Circle((hx, hy), L.HARDWARE_KEEPOUT_D / 2,
                            fill=False, ec="#ffcf57", lw=0.7, ls=":"))
        ax.add_patch(Circle((hx, hy), L.HOLE_D / 2,
                            fc="white", ec="black", lw=0.6))

    for name, spec in L.PARTS.items():
        if spec["side"] != side:
            continue
        x, y = spec["pos"]
        w, h = spec["courtyard"]
        ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h,
                               fc=color_for(name), ec="white", lw=0.45))
        label = name.replace("Q_", "").replace("U_", "").replace("RN_", "")
        ax.text(x, y, label, color="white", fontsize=4.4,
                ha="center", va="center", rotation=90 if h > w else 0)

    for channel, pads in L.MOTOR_PADS.items():
        for phase, (x, y) in zip("ABC", pads):
            w, h = L.MOTOR_PAD_SIZE
            ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h,
                                   fc="#d8d8d8", ec="black", lw=0.35))
            ax.text(x, y, phase, fontsize=4.3, ha="center", va="center")

    for label, (x, y) in L.BATTERY_PADS.items():
        w, h = L.BATTERY_PAD_SIZE
        ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h,
                               fc="#e64b40" if "+" in label else "#222222",
                               ec="white", lw=0.4))
        ax.text(x, y, label, color="white", fontsize=4.5,
                ha="center", va="center", rotation=90)

    ax.text(0, 22.2, title, fontsize=12, fontweight="bold", ha="center")
    ax.text(0, -22.0, "36×36 R5 | 30.5×30.5 M3 | 6-layer / 2 oz outer",
            fontsize=7.5, ha="center")
    ax.set_xlim(-28, 28)
    ax.set_ylim(-25, 26)
    ax.set_aspect("equal")
    ax.axis("off")

fig.suptitle("VYPER-55A 4-in-1 ESC — EVT MECHANICAL FLOORPLAN\n"
             "55 A / 2 s is a design target, not a tested rating",
             fontsize=13, fontweight="bold")
fig.tight_layout()
out = Path(__file__).parent / "vyper_esc_floorplan.png"
fig.savefig(out, facecolor="white", bbox_inches="tight")
print("wrote", out)
