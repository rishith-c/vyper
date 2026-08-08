"""Render the real CadQuery fit-check assembly to PNG with Matplotlib."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import vyper_assembly as A

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "img"
OUT.mkdir(parents=True, exist_ok=True)


def mesh_parts(transparent_shell=False):
    parts = []
    limits = [1e9, -1e9, 1e9, -1e9, 1e9, -1e9]
    for name, node in A.assembly.traverse():
        if node.obj is None:
            continue
        if transparent_shell and name == "fuselage":
            continue
        shape = node.obj.val() if hasattr(node.obj, "val") else node.obj
        vertices, triangles = shape.tessellate(0.65, 0.35)
        xyz = [(p.x, p.y, p.z) for p in vertices]
        faces = [[xyz[a], xyz[b], xyz[c]] for a, b, c in triangles]
        rgba = list(node.color.toTuple())
        rgba[:3] = [min(1.0, 0.20 + 1.45 * channel) for channel in rgba[:3]]
        if not transparent_shell and name == "fuselage":
            rgba[:3] = [0.28, 0.40, 0.52]
            rgba[3] = 0.92
        parts.append((name, faces, rgba))
        for x, y, z in xyz:
            limits[0] = min(limits[0], x)
            limits[1] = max(limits[1], x)
            limits[2] = min(limits[2], y)
            limits[3] = max(limits[3], y)
            limits[4] = min(limits[4], z)
            limits[5] = max(limits[5], z)
    return parts, limits


def render(filename, elev, azim, transparent_shell=False):
    parts, lim = mesh_parts(transparent_shell)
    fig = plt.figure(figsize=(16, 12), dpi=100, facecolor="#070a10")
    ax = fig.add_subplot(111, projection="3d", facecolor="#070a10")
    ax.set_proj_type("ortho")
    for _name, faces, rgba in parts:
        collection = Poly3DCollection(
            faces, facecolors=[rgba], edgecolors=[rgba], linewidths=0,
            alpha=rgba[3], shade=True,
        )
        ax.add_collection3d(collection)

    cx, cy, cz = (lim[0] + lim[1]) / 2, (lim[2] + lim[3]) / 2, (lim[4] + lim[5]) / 2
    span = max(lim[1] - lim[0], lim[3] - lim[2], lim[5] - lim[4]) * 0.50
    ax.set_xlim(cx - span, cx + span)
    ax.set_ylim(cy - span, cy + span)
    ax.set_zlim(cz - span, cz + span)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    fig.text(0.035, 0.95, "VYPER", color="#e4ebf5", fontsize=32, fontweight="bold")
    fig.text(0.035, 0.918, "6S  •  5×5 PUSHER  •  200 km/h TARGET",
             color="#59bdec", fontsize=15)
    fig.text(0.035, 0.886,
             "OPEN-SHELL MECHANICAL FIT CHECK" if transparent_shell
             else "CADQUERY GEOMETRY RENDER",
             color="#aeb8c8", fontsize=11)
    ax.set_position([0.04, 0.02, 0.94, 0.91])
    fig.savefig(OUT / filename, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(OUT / filename)


if __name__ == "__main__":
    render("vyper_200kph_iso.png", elev=23, azim=-48)
    render("vyper_200kph_side.png", elev=5, azim=0)
    render("vyper_200kph_fitcheck.png", elev=20, azim=-42, transparent_shell=True)
