# Peregreen-X — LinkedIn project write-up

> Paste into the *Projects* section, or post as-is. Trim to taste.

---

**Peregreen-X — a fully 3D-printed high-speed FPV drone, designed parametrically and verified by test**

I built a complete rocket-style FPV quadcopter airframe in code — every part
generated from a parametric CAD script, and every design claim checked by an
automated test suite rather than by eye.

**The idea.** Inspired by the Peregreen V4, the fully 3D-printed quadcopter
that took the Guinness record at 657.59 km/h. I wanted to understand what
actually makes an airframe fast, on a $142 budget and a consumer printer.

**What I built**
• A parametric CadQuery model of the full airframe: Von Kármán minimum-drag
  ogive nose, 2 mm hollow fuselage, four swept blade arms, boat-tailed motor
  nacelles, internal flight-stack shelf.
• A 24-check automated test suite covering fit, printability, tolerances,
  aerodynamics and mass — run on every change.
• A component drag build-up, prop-pitch speed model, and full mass budget.
• Betaflight firmware configuration with every non-default value justified.

**Results**
• 567 g all-up, 8.1:1 thrust-to-weight
• CdA 39.4 cm² — roughly half a conventional open racer
• Fuselage fineness ratio 5.77, inside the low-drag optimum band
• $142 bill of materials

**What I actually learned — the useful part**

*Top speed was never limited by thrust.* The model showed 3.6 N of drag against
44 N of available thrust. The real ceiling is propeller pitch speed. Halving
drag doesn't raise the ceiling — it lowers the power needed to sit at it. That
reframed the whole project: the fairing buys efficiency and flight time, not
top speed.

*The tests caught what my eyes didn't.* An internal hub exported as four
disconnected wedges. An arm's frontal area computed against the wrong axis,
overstating its drag by 4.3×. A camera bay placed where the nose taper couldn't
hold it. A spline that self-intersected and produced a negative volume. Every
one of those looked fine in a render.

*Cheaper parts made the aircraft faster.* Re-specifying to a $150 budget meant a
smaller flight controller and battery — which let the fuselage shrink from 60 mm
to 52 mm and lose 25 % of its frontal area. The expensive component had been
setting the diameter all along.

**Stack:** Python, CadQuery, build123d, OpenCascade, Betaflight

Repo: github.com/rishith-c/peregreen-x

#Engineering #Aerospace #CAD #3DPrinting #Python #FPV #Drones #Aerodynamics
