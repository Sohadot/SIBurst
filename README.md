# SIBurst

**Naming the phase change in intelligence.**

SIBurst is a conceptual digital asset built around one distinction:

> intelligence may accumulate incrementally while the operating regime
> associated with that capability may change discontinuously.

SIBurst names that discontinuity.

## Canonical thesis

> SIBurst names a phase change in intelligence: the transition from
> incremental capability growth into a materially different operating regime.

Most AI names describe a model, tool, or interface.
SIBurst names the transition itself.

## The name

| Part | Meaning within the SIBurst naming architecture |
|---|---|
| **SI** | Superintelligence. Used deliberately inside this naming system; no claim is made that "SI" is the exclusive or universal abbreviation for the term. |
| **Burst** | Discontinuity, threshold crossing, or qualitative regime change after accumulated capability. Not an explosion, not a temporary performance spike, not a benchmark result. |
| **SIBurst** | The transition event at which intelligence can no longer be understood only as more incremental capability, but enters a materially different operating regime. |

## What SIBurst does not claim

SIBurst does not assert that superintelligence has been achieved,
nor does it predict when or whether a specific transition will occur.

"Phase change" is the conceptual lens of this project. It is not presented
as an established scientific law of AI development.

## Conceptual foundation

What SIBurst means, what it may claim, and what the interface must express.

| Document | Role |
|---|---|
| [FOUNDATION_THESIS.md](FOUNDATION_THESIS.md) | The intellectual core: accumulation, threshold, discontinuity, new operating regime. |
| [NAME_ARCHITECTURE.md](NAME_ARCHITECTURE.md) | Canonical semantics of SI, Burst, and SIBurst, in semantic, temporal, and commercial layers. |
| [CATEGORY_BOUNDARY.md](CATEGORY_BOUNDARY.md) | What SIBurst is not by default, its natural territory, and the boundary test. |
| [COMMERCIAL_TERRITORY.md](COMMERCIAL_TERRITORY.md) | Public map of application areas: Build, Act, Measure, Cross. |
| [GLOSSARY.md](GLOSSARY.md) | Governed definitions of the project's working vocabulary. |
| [PUBLIC_CLAIM_POLICY.md](PUBLIC_CLAIM_POLICY.md) | Claim classes, prohibited claims, and the standard every public statement must meet. |
| [SITE_ARCHITECTURE.md](SITE_ARCHITECTURE.md) | Conceptual design of the future interface: the seven-stage experience and its prohibitions. |
| [DECISION_LOG.md](DECISION_LOG.md) | Durable record of decisions and their consequences. |

## Implementation doctrine

How the conceptual interface may be built and how any build is judged. These
documents implement the foundation; they do not redefine it.

| Document | Role |
|---|---|
| [INTERFACE_CONTRACT.md](INTERFACE_CONTRACT.md) | The implementation contract: seven-stage state machine, Lattice-to-Field rule change, semantic primitives, scoped state language, progress, content and reference architecture, and implementation constraints. |
| [VISUAL_SYSTEM.md](VISUAL_SYSTEM.md) | Spatial character, semantic color and typography roles, and density progression. |
| [MOTION_SEMANTICS.md](MOTION_SEMANTICS.md) | The permitted motion classes and the reduced-motion path. |
| [RESPONSIVE_ACCESSIBILITY.md](RESPONSIVE_ACCESSIBILITY.md) | Behavior across viewports and input methods, and WCAG 2.2 AA requirements. |
| [INTERFACE_ACCEPTANCE.md](INTERFACE_ACCEPTANCE.md) | Gate 0 (fixture integrity) and the pass/fail tests every implementation must meet. |
| [DEMONSTRATION_FIXTURE.md](DEMONSTRATION_FIXTURE.md) | The laws of the canonical demonstration system: arrival, placement, routing, stubs, S3 offsets, clusters, anchors, Field geometry, viewports. |
| [`data/demonstration-fixture.json`](data/demonstration-fixture.json) | The canonical demonstration fixture: the implementation source of truth for the demonstration graph and geometry. |
| [`schemas/demonstration-fixture.schema.json`](schemas/demonstration-fixture.schema.json) | The fixture's structural schema. |
| [`tools/validate_fixture.py`](tools/validate_fixture.py), [`tests/`](tests/) | The fixture validator and its mutation tests (Python standard library only). |
| [SITE_BUILD.md](SITE_BUILD.md) | How the static interface is built, checked, and validated: sources, deterministic build, reference generation, runtime constraints. |
| [`src/site/`](src/site/) | Interface source: HTML templates, stylesheet, and the vanilla JavaScript module. |
| [`tools/build_site.py`](tools/build_site.py), [`tools/validate_site.py`](tools/validate_site.py) | The deterministic site build and the site validator. |
| [`docs/`](docs/) | The generated static site. Never edited by hand (DEC-022). |

## Order of authority

| Question | Governed by |
|---|---|
| What the terms mean | `NAME_ARCHITECTURE.md` |
| What may be claimed publicly | `PUBLIC_CLAIM_POLICY.md` |
| What the interface experience must express | `SITE_ARCHITECTURE.md` |
| How that experience may be implemented | `INTERFACE_CONTRACT.md`, with `VISUAL_SYSTEM.md`, `MOTION_SEMANTICS.md`, and `RESPONSIVE_ACCESSIBILITY.md` |
| What the demonstration system contains | `data/demonstration-fixture.json`, under the laws in `DEMONSTRATION_FIXTURE.md` |
| Whether an implementation is accepted | `INTERFACE_ACCEPTANCE.md` |

Each level is bound by the levels above it. `DECISION_LOG.md` records why. A
conflict between documents is treated as a defect in the lower document, to be
corrected, not as a second meaning.

## Status

- **Sprint 0 — conceptual foundation:** closed.
- **Sprint 1 — interface contract:** closed.
- **Sprint 2 — canonical demonstration fixture:** closed.
- **Sprint 3 — executable static interface:** built, pending review.

The static interface is built in `docs/` for review. **The site has not been
published.** Publishing is a separate gate (DEC-024).
