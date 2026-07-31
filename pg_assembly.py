"""Peregreen-X assembly: shell + hub + four arms, for review renders."""
import cadquery as cq
import peregreen_shell as M

asm = M.result
hub = M.hub
one = M.arm.translate((0, 0, M.ARM_Z))
for a in M.ARM_ANGLES:
    asm = asm.union(one.rotate((0, 0, 0), (0, 0, 1), a))
asm = asm.union(hub)
result = asm

if __name__ == "__main__":
    o = result.val()
    b = o.BoundingBox()
    print(f"assembly {b.xlen:.0f} x {b.ylen:.0f} x {b.zlen:.0f} mm, "
          f"{o.Volume():.0f} mm^3, solids={len(o.Solids())}")
