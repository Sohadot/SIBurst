# Motion Semantics

Every animation must carry meaning. This document defines the only kinds of
motion the SIBurst interface may use, what each one means, and how the
experience works when motion is reduced. It is governed by
`INTERFACE_CONTRACT.md`.

## 1. Principles

1. **Motion is state change made visible.** Every movement corresponds to a
   change in the demonstration system's state or relationships, as defined in
   the contract.
2. **Motion is driven by progress, not by time.** Movement inside the
   demonstration is a function of `p` (see `INTERFACE_CONTRACT.md` §6). When the
   visitor stops, the system stops.
3. **Stillness invariant.** If the visitor does not scroll or navigate, nothing
   inside the demonstration moves. There are no idle loops, ambient drift,
   pulsing, or "breathing".
4. **Monotonic easing only.** Interpolations may ease in or out, but they never
   overshoot, bounce, spring, or oscillate.
5. **Removable test.** If an animation could be removed without losing
   information about accumulation, threshold, or regime, it must not exist
   (from `SITE_ARCHITECTURE.md`).

## 2. Motion taxonomy

Six motion classes are allowed. Any motion that does not belong to one of them
is prohibited.

### M1 — Appearance

- **Meaning:** an entity or relationship now exists in the model.
- **Allowed stages:** S0–S3 (nodes and links); S5 (the name and the transition
  record); S6 (reference items).
- **Form:** the element enters at its final position. Opacity or a short
  stroke draw-on is acceptable.
- **Prohibited misuse:** elements flying in from outside, scaling up from zero
  with overshoot, or appearing in a burst. Appearance used only to "reveal"
  content on scroll.

### M2 — Relationship formation

- **Meaning:** a relationship between two existing entities now exists.
- **Allowed stages:** S0–S3.
- **Form:** the link is drawn from one entity to the other along its route.
  Before S4 the route is orthogonal. If the Lattice cannot route it, it is drawn
  as a stub.
- **Prohibited misuse:** lines that travel, float, or animate continuously once
  formed; data-flow "pulses" moving along links; links that appear without a
  relationship in the graph.

### M3 — Constraint pressure

- **Meaning:** the structure is approaching or exceeding its capacity.
- **Allowed stages:** S2–S3.
- **Form:** stubs accumulate; routed links crowd shared rail segments; the
  threshold-warning role appears on affected elements. All changes are tied to
  `p`.
- **Prohibited misuse:** shaking, vibration, flicker, flashing, alarm-style
  blinking, pulsing boundaries.

### M4 — Local misalignment

- **Meaning:** the old description fails in specific places.
- **Allowed stages:** S3 only.
- **Form:** individual nodes slip off their cell centers by a deterministic
  offset of at most half a cell, proportional to their unrouted relationships.
  Links to them detour. Rails stay straight.
- **Prohibited misuse:** random jitter; global warping; glitch, tearing, or
  channel-split effects; any misalignment outside the boundary.

### M5 — Topology reconfiguration

- **Meaning:** the rules of organization change; the same entities are now
  related differently.
- **Allowed stages:** S4 only.
- **Form:** in this order, all tied to `p`:
  1. **Rails retire:** they withdraw or fade as a whole. They do not break,
     shatter, or fragment.
  2. **Nodes reposition:** each node moves along a smooth, direct path from its
     Lattice position to its Field position. Movement may be staggered by
     cluster, never by random order.
  3. **Links resolve:** orthogonal routes straighten into direct paths; stubs
     extend to complete their relationships.
- **Prohibited misuse:** explosion, particle blast, screen shake, flash, speed
  ramp, random scattering, vortex or spiral paths, zooming "through" the
  system, cross-fading one scene into another.

### M6 — Stabilization

- **Meaning:** the new regime holds.
- **Allowed stages:** S5–S6.
- **Form:** active-signal emphasis settles to dormant; the system becomes still.
  In S6, the demonstration recedes in contrast so the reference layer is readable.
- **Prohibited misuse:** celebratory effects, confetti, glow-ups, or any motion
  implying achievement.

### Interface feedback (outside the taxonomy)

Focus indicators, hover states, and pressed states on controls and links are
interface feedback, not demonstration motion. They change immediately or with a
very short transition, and never move the demonstration system.

## 3. Allowed and prohibited: reference pairs

| Allowed | Not allowed |
|---|---|
| A line appears because a relationship now exists. | A line floats continuously because it looks technological. |
| A node changes position because its relationship topology changed. | Nodes drift randomly. |
| The interface reorganizes under a new rule. | The screen shakes or explodes. |
| A stub appears because the Lattice cannot route a relationship. | A node flickers to show "instability". |
| Rails fade as their rule is lifted. | Rails shatter into fragments. |
| The system becomes still after S5. | The system idles with ambient motion. |

## 4. Reduced motion

When the visitor has set `prefers-reduced-motion: reduce`, the thesis must
survive intact. **No essential meaning may depend on animation alone.** This is
mandatory.

In reduced-motion mode:

- **Discrete states.** Each stage is shown as its canonical state. Changes
  happen at stage boundaries, not continuously with `p`.
- **No interpolated movement.** Nodes never travel. At S4, the Lattice layout is
  replaced by the Field layout in one step. Anchors keep their identifiers, so
  continuity of identity is carried by labels, not by motion.
- **S4 as two frames.** The transition is presented as two explicit states:
  *Lattice (rules in force)* and then *Field (rules changed)*. Each has its
  state label and description.
- **Transition record.** The S5 side-by-side record (Lattice beside Field, anchors
  marked in both) is always shown. It carries the comparison that motion would
  otherwise carry.
- **Opacity only where appropriate.** A short opacity change (about 200 ms or
  less) may soften a step change in appearance or stabilization. It is never
  used to cross-fade the whole system between regimes.
- **Explicit stage navigation.** The stage navigation is the primary way through
  the sequence, and every stage is reachable in one action.

Reduced-motion users must be able to answer the same question as everyone else:
*was the change from S1 to S4 more of the same, or different?*

## 5. Motion and performance

If a device cannot animate the demonstration smoothly, the implementation uses
the reduced-motion path. Motion is always the first thing sacrificed. Meaning is
never sacrificed.
