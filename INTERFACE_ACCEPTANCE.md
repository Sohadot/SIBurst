# Interface Acceptance

The pass/fail gate for any implementation of the SIBurst interface. The tests
operationalize `SITE_ARCHITECTURE.md` and the Sprint 1 contracts:
`INTERFACE_CONTRACT.md`, `VISUAL_SYSTEM.md`, `MOTION_SEMANTICS.md`, and
`RESPONSIVE_ACCESSIBILITY.md`.

## Gate 0 — Fixture integrity

**Precondition.** The implementation cannot enter the 18-test interface gate
unless the canonical demonstration fixture passes its fixture validator.

**Procedure.** From the repository root, run:

```
python tools/validate_fixture.py
python -m unittest discover -s tests
```

Also confirm that the implementation's demonstration data is exactly
`data/demonstration-fixture.json`, or is derived mechanically from it
(`INTERFACE_CONTRACT.md` §8.2).

**PASS** if both commands exit with status 0 and the implementation contains no
independent graph or geometry.

**FAIL** otherwise. Tests 1–18 are not run until Gate 0 passes.

Gate 0 is machine-verifiable and checks data and geometry integrity. It is not
a nineteenth interface test. Tests 1–18 judge interface behavior and presentation.

---

## How to run the gate

- Every test is either **PASS** or **FAIL**. There is no partial pass.
- An implementation is accepted only if **Gate 0 passes and all 18 tests pass**.
- Each test is run on at least one wide viewport and one mobile viewport, unless
  it names its own conditions.
- Where a test asks a reviewer to judge without reading, the reviewer covers or
  ignores all captions, headings, and labels other than anchor identifiers.
- Results are recorded with the implementation, including the viewports,
  browsers, and settings used.
- If a test cannot be run, it is recorded as FAIL until it can be.

---

## Test 1 — More vs Different

**Question.** Without reading explanatory prose, can a reviewer tell S1 SCALE
apart from S4 PHASE CHANGE (as completed at the start of S5)?

**Procedure.** Capture the system at the end of S1 and at the start of S5. Show
both to a reviewer with captions hidden. Ask what distinguishes them.

**PASS** if the reviewer names a difference in organization, such as "the grid
is gone", "things are grouped differently", or "lines go directly now".

**FAIL** if the only differences named are intensity, density, brightness,
speed, or quantity.

*Source: INTERFACE_CONTRACT §2.3; DEC-011.*

## Test 2 — Structural transition

**Question.** Does S4 change a genuine rule of organization?

**Procedure.** At the end of S3 and at the start of S5, check the positioning rule:

- At the end of S3, arrival index and lane predict each node's position.
- At the start of S5, check whether they still do. Check whether the anchors
  required by INTERFACE_CONTRACT §3.1 have separated or converged as specified.
  Confirm that no rail remains.

**PASS** if position is governed by index and lane before S4, and by
relationships after it, with the anchor conditions met.

**FAIL** if the same positioning rule holds on both sides, or if the only change
is visual styling.

*Source: INTERFACE_CONTRACT §2.1–2.3; DEC-011.*

## Test 3 — Identity continuity

**Question.** Is the post-transition system recognizably the same system,
reorganized?

**Procedure.** Count the nodes at the end of S3 and at the start of S5. Compare
the anchor identifiers. Watch S4 (and the reduced-motion S4 frames) and check
that anchors stay visible throughout.

**PASS** if the node counts are equal, every anchor persists with the same
identifier, no relationship is lost, and the boundary persists.

**FAIL** if any entity is added or removed at S4, any anchor disappears or is
relabeled, or the transition looks like one scene replacing another, including
a cross-fade between independent compositions.

*Source: INTERFACE_CONTRACT §1.2, §4.3; DEC-012.*

## Test 4 — No spectacle substitution

**Question.** Does the transition depend on spectacle?

**Procedure.** Watch S3–S5 at normal and at slow scroll speed.

**PASS** if none of the following occurs: explosion, flash, glitch, shake,
vortex or spiral motion, particle blast, random scattering, speed ramp, or
dramatic acceleration.

**FAIL** if any one occurs.

*Source: INTERFACE_CONTRACT §2.4; MOTION_SEMANTICS M5; DEC-002.*

## Test 5 — Claim integrity

**Question.** Could a reasonable visitor read an interface state as a factual
claim that AGI, superintelligence, or a real-world intelligence transition has
occurred?

**Procedure.** For every stage, check that:

- the state readout carries its scope prefix and stage index;
- the boundary caption identifies the system as a demonstration;
- no prohibited vocabulary or telemetry device from INTERFACE_CONTRACT §5.3
  appears;
- no number other than the stage index is shown;
- every caption can be classified under `PUBLIC_CLAIM_POLICY.md`.

Then ask a reviewer who has not read the repository what the state labels refer to.

**PASS** if every check holds and the reviewer says the labels describe the
on-screen demonstration.

**FAIL** if any check fails, or the reviewer believes the site is reporting on
real AI systems.

*Source: INTERFACE_CONTRACT §5; DEC-004, DEC-005, DEC-013.*

## Test 6 — Reduced motion

**Question.** Does the reduced-motion path keep the conceptual distinction?

**Procedure.** Turn on `prefers-reduced-motion: reduce`. Traverse S0–S6 with the
stage navigation. Repeat Tests 1, 2, and 3 in this mode.

**PASS** if all seven stages are reachable, S4 appears as two explicit states,
the S5 transition record is shown, no node travels, and Tests 1–3 pass.

**FAIL** if any stage is missing or merged, or if the distinction between S1 and
S4 depends on motion.

*Source: MOTION_SEMANTICS §4; DEC-015.*

## Test 7 — Mobile

**Question.** Do mobile visitors experience the same semantic progression?

**Procedure.** On a viewport 360 CSS px wide, and again below 360, traverse the
full sequence. Repeat Tests 1–3.

**PASS** if all seven stages occur in one persistent system, with rails, stubs,
slipped nodes, anchors, the scoped readout, and the transition record, and
Tests 1–3 pass.

**FAIL** if mobile shows the stages as ordinary stacked marketing blocks, or
drops any stage, primitive, or the rule change.

*Source: RESPONSIVE_ACCESSIBILITY §2.1; DEC-015.*

## Test 8 — Keyboard accessibility

**Question.** Can the entire sequence be traversed by keyboard alone?

**Procedure.** Without a pointer, go from page load through S0–S6 and into every
reference item and back.

**PASS** if every stage and reference item is reachable, focus is always visible,
there is no keyboard trap, and each stage reached by keyboard shows the same
state as when reached by scrolling.

**FAIL** otherwise.

*Source: RESPONSIVE_ACCESSIBILITY §3.2–3.3; DEC-015.*

## Test 9 — Semantic motion

**Question.** Can every animation be mapped to an explicit state or relationship
change?

**Procedure.** List every animation in the implementation and assign each one a
motion class (M1–M6) and a stage. Then stop scrolling at a point in each stage
and watch the demonstration for ten seconds.

**PASS** if every animation maps to one class and stage allowed by
`MOTION_SEMANTICS.md`, and nothing inside the demonstration moves while the
visitor is idle.

**FAIL** if any animation cannot be mapped, is used outside its allowed stages,
or runs while the visitor is idle.

*Source: MOTION_SEMANTICS §1–2; DEC-014.*

## Test 10 — Generic AI appearance

**Question.** Could the interface be mistaken for a generic AI product landing
page if the name were removed?

**Procedure.** Remove the name and show screenshots of S0, S3, S5, and S6 to a
reviewer. Check them against the visual prohibitions in `SITE_ARCHITECTURE.md`,
the additions in `VISUAL_SYSTEM.md` §1, and the excluded sections in
INTERFACE_CONTRACT §7.3.

**PASS** if no prohibited image, pattern, or section is present and the reviewer
does not identify the page as a typical AI product landing page.

**FAIL** otherwise.

*Source: SITE_ARCHITECTURE visual prohibitions; DEC-007.*

## Test 11 — Static fallback

**Question.** Without JavaScript, can a visitor still understand accumulation,
threshold, regime change, and SIBurst as the transition?

**Procedure.** Disable JavaScript and load the page.

**PASS** if all seven stages appear in order with static figures of the same
system, state labels with scope prefixes, captions, and state descriptions; the
figures for S3 and S5 show the rule change with the same anchors; and stage
navigation and reference links work.

**FAIL** if content is missing, blank, or only understandable with scripting.

*Source: INTERFACE_CONTRACT §8.1; DEC-016.*

## Test 12 — Reference access

**Question.** Can a visitor reach the governed foundation documents without
fighting the visual experience?

**Procedure.** From the first view, reach the reference layer by the shortest
route. Then open each reference item.

**PASS** if a reference link is visible and usable from the first view, every
item in INTERFACE_CONTRACT §7.2 is reachable, and reference content matches the
repository's Markdown sources.

**FAIL** if the visitor must traverse the demonstration to reach the doctrine,
any item is missing, or reference content has been paraphrased or has diverged.

*Source: INTERFACE_CONTRACT §7.*

## Test 13 — Instability confinement

**Question.** Does S3 instability stay inside the demonstration?

**Procedure.** In S3, tab through the page, read the captions, and use the stage
navigation.

**PASS** if focus order, navigation position, caption layout, and control
visibility are identical to S0.

**FAIL** if anything outside the boundary moves, misaligns, or becomes harder to use.

*Source: RESPONSIVE_ACCESSIBILITY §2.2; DEC-015.*

## Test 14 — Determinism and reversibility

**Question.** Is the state a pure function of progress?

**Procedure.** Move to the middle of each stage by scrolling, by stage
navigation, and by loading its fragment address directly. Compare the results.
Scroll from S6 back to S0.

**PASS** if each method produces the same state at the same point, reloading
produces the same layout, and scrolling back reverses the sequence exactly.

**FAIL** if layout varies between loads or methods, or if any randomness is visible.

*Source: INTERFACE_CONTRACT §4.1, §6.3.*

## Test 15 — Progress is not a measurement

**Question.** Is `p` kept strictly as visitor progress?

**Procedure.** Inspect every visible label, the accessible text, and the page title.

**PASS** if progress appears only as a stage position (for example `S3 / S6`)
and is never shown as a percentage, score, level, or continuously changing number.

**FAIL** otherwise.

*Source: INTERFACE_CONTRACT §6.1; DEC-005, DEC-013.*

## Test 16 — Color and contrast

**Question.** Do color roles meet contrast requirements and never carry meaning alone?

**Procedure.** Measure contrast for each shipped scheme. View S2, S3, and S5 in
grayscale.

**PASS** if all text and essential graphics meet `VISUAL_SYSTEM.md` §2, the
threshold-warning and post-transition roles appear only in their allowed stages,
and every state is still distinguishable in grayscale.

**FAIL** otherwise.

*Source: VISUAL_SYSTEM §2; RESPONSIVE_ACCESSIBILITY §3.4.*

## Test 17 — Assistive-technology sequence

**Question.** Does a screen-reader user meet the complete thesis?

**Procedure.** Traverse the page with a screen reader.

**PASS** if the visitor hears the demonstration scope statement, seven stages in
order with scoped labels and state descriptions, a text equivalent of the
transition record, and then the reference layer. Stage changes are announced
once each, and decorative geometry is not announced.

**FAIL** otherwise.

*Source: RESPONSIVE_ACCESSIBILITY §3.6–3.9; DEC-015.*

## Test 18 — Implementation constraints

**Question.** Does the build respect the static-first, dependency-minimal constraints?

**Procedure.** Inspect network requests and source.

**PASS** if there are no external script or font sources, no framework or
analytics dependency without a recorded decision, no required WebGL, video, or
autoplay media, and the indicative size budgets in INTERFACE_CONTRACT §8 are met, or
any excess is recorded and justified.

**FAIL** otherwise.

*Source: INTERFACE_CONTRACT §8; DEC-016.*

---

## Summary

| # | Test | Guards |
|---|---|---|
| 1 | More vs Different | The thesis distinction |
| 2 | Structural transition | The rule change |
| 3 | Identity continuity | Same system, different regime |
| 4 | No spectacle substitution | The meaning of Burst |
| 5 | Claim integrity | The public claim boundary |
| 6 | Reduced motion | Meaning without animation |
| 7 | Mobile | Semantics on every viewport |
| 8 | Keyboard accessibility | Equal access to the sequence |
| 9 | Semantic motion | Motion as meaning |
| 10 | Generic AI appearance | Distinctiveness |
| 11 | Static fallback | Meaning without scripting |
| 12 | Reference access | Access to the doctrine |
| 13 | Instability confinement | Usability during S3 |
| 14 | Determinism and reversibility | Reproducible states |
| 15 | Progress is not a measurement | No implied scores |
| 16 | Color and contrast | Perceivable states |
| 17 | Assistive-technology sequence | The thesis without sight |
| 18 | Implementation constraints | Static-first build |
