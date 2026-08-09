# LinkedIn project draft

**VYPER — a code-generated, high-speed rocket-body FPV drone concept**

I designed VYPER to explore how a tightly packaged, 3D-printable quadcopter
could reduce drag without becoming a conventional flat FPV frame. The current
design uses a hollow Ø57 mm Von Kármán-ogive fuselage, a removable cosine
boat-tail, four swept true-X blade arms and aft-facing pusher propellers.

The full airframe is generated in Python/CadQuery and exports Neptune-4-sized
STL and STEP parts. A separate fit-check assembly includes the selected 6S
battery, motors, 5-inch prop discs, electronics envelopes, wire bores and exact
ISO M3 motor fasteners.

Current analytical screening results:

- 705 g slicer-based estimated all-up mass and 8.9:1 static thrust-to-weight;
- 40 cm² component drag area estimate;
- 241 km/h ideal prop-pitch speed; 200 km/h would require 83% pitch efficiency;
- 28.6 mm adjacent prop-tip clearance and 18.0 mm body clearance;
- all current geometry, tolerance, packaging and first-order ESC checks pass.

The most important part of the project is the boundary between modeling and
proof. VYPER has not flown, the 200 km/h target is not a claim, and the custom
flight controller/ESC are not orderable yet. The repository labels those
boards as EVT, documents every remaining ERC/DRC, thermal, structural and dyno
gate, and separates the under-$200 purchased-stack prototype from the custom-
electronics development cost.

The custom 22×64 mm FC now has a 59-net, 74-component authored electrical
design, while the custom 30×72 mm four-channel ESC has 159 nets and 195
components. Every footprint is packed inside its vertical board outline and
the placement-level KiCad checks report no shorts, clearance, courtyard, edge
or footprint errors. Both boards remain explicitly unrouted: 183 FC and 499
ESC connections, independent review and hardware bring-up are still open.

Building the tests changed the design repeatedly: the 6S battery forced a
larger honest body diameter; a friction-only tail became a three-screw
heat-set-insert joint; a full arm cavity became a Ø5.5 mm bore so the printed
arm retained sidewalls; and the custom ESC changed to 60 V MOSFETs plus 65 V
smart gate drivers after transient-margin review.

Stack: Python, CadQuery, OpenCascade, KiCad 9, Betaflight, AM32.

Repository: https://github.com/rishith-c/vyper

#AerospaceEngineering #CAD #3DPrinting #Python #KiCad #FPV #Aerodynamics
