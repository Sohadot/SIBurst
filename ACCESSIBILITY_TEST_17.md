# Accessibility Test 17 Record

The acceptance record for Interface Acceptance Test 17, "Assistive-technology
sequence" (`INTERFACE_ACCEPTANCE.md`).

## Purpose

Test 17 asks whether a screen-reader user meets the complete thesis:
- the demonstration scope;
- the seven stages in order, with scoped labels and state descriptions;
- the S5 transition record text;
- the reference layer.

Stage changes must be announced once, and decorative geometry must not be
announced. This record documents the human traversal that closed the test.

## Human evidence and machine evidence

**Automated accessibility checks do not substitute for Interface Acceptance
Test 17.**

| Evidence | What it is | What it can establish |
|---|---|---|
| `tools/preflight_accessibility.py` | Automated structural check of the generated HTML. | Structure that could break a screen-reader traversal: scope text, stage structure and descriptions, a single polite live region, hidden decorative graphics, transition-record text, reference list, IDs, ARIA references, focus targets. |
| This record | A real screen-reader traversal by a person. | Whether the sequence is actually understandable when heard. |

**Test 17 was closed by a real screen-reader traversal.**

## Build under test

| Field | Value |
|---|---|
| Build | `main` at `28666032e438b40112ccb976be1d730cc7ea2482` (tree `543d55148877a64d79e36494e4ba77eb05517e6d`), the production-candidate baseline stated for the test |
| Build hash recorded on the device | not captured |

## Test environment

| Field | Value |
|---|---|
| Date | 2026-09-24 |
| Device | Redmi Note 13 Pro |
| Model | 23117RA68G |
| Operating system | Android 16 |
| OS build | 3.0.301.0.WNFEUXM.C08 |
| Browser | Google Chrome |
| Chrome version | not captured |
| Screen reader | Android TalkBack |
| TalkBack version | not captured |
| Tester identity | not retained |

## Observed checks

| # | Check | Result |
|---|---|---|
| 1 | The demonstration scope was conveyed: the visitor understood this is a model of the SIBurst concept, not a measurement. | PASS |
| 2 | The semantic sequence S0 → S1 → S2 → S3 → S4 → S5 → S6 was traversed successfully. | PASS |
| 3 | S4 / TRANSITION DETECTED remained understandable as a scoped demonstration state, not a real-world intelligence measurement. | PASS |
| 4 | Decorative geometry did not obstruct the experience with meaningless SVG, path, or node announcements. | PASS |
| 5 | S4 conveyed the semantic transition: the rules change while the entities remain. | PASS |
| 6 | S5 conveyed the meaning of the transition record. | PASS |
| 7 | S6 and the reference layer were traversable. | PASS |
| 8 | No navigation trap or materially disruptive repetition of announcements was encountered. | PASS |

**Interface Acceptance Test 17: PASS.**

## Announcements

Exact spoken announcement strings were not retained; the tester confirmed that
stage transitions were announced successfully and without materially disruptive
repetition.

Test 17 is a behavioral acceptance test, not a transcript collection.

## Limitations

- One screen reader, browser, and device were tested: Android TalkBack with
  Chrome on Android 16. No desktop screen reader (for example NVDA or
  VoiceOver) was tested.
- Browser and screen-reader versions were not captured.
- No verbatim transcript was retained.
- The build hash was not recorded on the device. The record relies on the
  stated production-candidate baseline.
- The result applies to the build under test. A later change to semantic
  markup, accessible text, focus order, live-region behavior, SVG
  accessibility, stage navigation, or the transition record requires Test 17
  to be repeated on the resulting commit.
- This record does not claim WCAG conformance, certification, or universal
  accessibility. WCAG 2.2 AA remains the target stated in
  `RESPONSIVE_ACCESSIBILITY.md`.

## Relationship to INTERFACE_ACCEPTANCE.md

`INTERFACE_ACCEPTANCE.md` defines Test 17 and is unchanged. This record is the
evidence that the test was executed and passed. With it, all 18 interface
acceptance tests have passed:
- Tests 1 to 16 and 18 by machine verification and browser review during
  Sprint 3;
- Test 17 by this human traversal.

Gate 0 passes independently (`python tools/validate_fixture.py`).
