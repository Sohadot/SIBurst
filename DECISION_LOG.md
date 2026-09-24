# Decision Log

A durable public record of foundational decisions. Entries are not deleted.
A decision that changes is marked **Superseded** and linked to the entry that
replaces it.

Status values: **Accepted**, **Superseded**, **Proposed**.

---

## DEC-001 — SIBurst names a transition, not a product class

- **Status:** Accepted
- **Decision:** SIBurst names the transition from incremental capability growth
  into a materially different operating regime. It does not name a model, tool,
  interface, or single product category.
- **Rationale:** Most AI names describe what a system is. A name for the
  transition itself describes something many different systems relate to, and
  remains meaningful as individual products change.
- **Consequences:** Every use of the name must relate to the transition
  (`CATEGORY_BOUNDARY.md`). Definitions of SIBurst in all documents must match
  `NAME_ARCHITECTURE.md`.

## DEC-002 — "Burst" denotes discontinuity, not a temporary spike

- **Status:** Accepted
- **Decision:** "Burst" denotes discontinuity, threshold crossing, or qualitative
  regime change after accumulated capability. It does not denote a temporary
  performance spike, benchmark burst, speed, or explosion.
- **Rationale:** A spike returns to baseline; a regime change does not. Reading
  "burst" as a spike would reduce the name to a performance claim.
- **Consequences:** Copy, interface, and imagery must avoid spike, speed, and
  explosion framings. The interface expresses the burst as a change of rules
  (`SITE_ARCHITECTURE.md`).

## DEC-003 — "SI" denotes Superintelligence within the naming architecture

- **Status:** Accepted
- **Decision:** Within SIBurst, "SI" denotes superintelligence. The project does
  not claim that "SI" is the exclusive, universal, or canonical abbreviation.
- **Rationale:** The meaning is a deliberate choice inside this identity. Claiming
  exclusivity would be inaccurate, since the letters have other established uses.
- **Consequences:** Documents describe SI as meaning superintelligence "within
  the SIBurst naming architecture" and make no broader claim.

## DEC-004 — No claim that superintelligence currently exists

- **Status:** Accepted
- **Decision:** The project makes no claim that superintelligence currently
  exists, and no claim that any named system is superintelligent.
- **Rationale:** The framework concerns a transition as a concept. Its
  credibility depends on not asserting what it has not shown.
- **Consequences:** Such a claim could only enter public materials as an
  OBSERVATION meeting the standard in `PUBLIC_CLAIM_POLICY.md`.

## DEC-005 — No unsupported dates, scores, or singularity rhetoric

- **Status:** Accepted
- **Decision:** No unsupported prediction dates, intelligence scores,
  multipliers, or singularity rhetoric are permitted.
- **Rationale:** These are the most common ways writing about advanced AI
  overstates its evidence. Excluding them is cheaper than correcting them.
- **Consequences:** Enforced through the prohibited-claims list in
  `PUBLIC_CLAIM_POLICY.md` and the category exclusions in `CATEGORY_BOUNDARY.md`.

## DEC-006 — "Phase change" is a framework, not a law

- **Status:** Accepted
- **Decision:** "Phase change" is the conceptual framework of SIBurst. It is not
  asserted as a universal scientific law of AI development.
- **Rationale:** The term is borrowed as a structural metaphor from physical
  systems. The borrowing clarifies the idea; it is not evidence for it.
- **Consequences:** Documents classify "phase change" as METAPHOR or DEFINITION,
  never OBSERVATION. The thesis states explicitly that not every capability
  trajectory must contain a threshold.

## DEC-007 — The interface represents the thesis, not generic AI themes

- **Status:** Accepted
- **Decision:** The interface must represent accumulation, threshold, and regime
  change, rather than decorate generic AI themes.
- **Rationale:** A site built from generic AI imagery would make SIBurst
  indistinguishable from any other AI project. An interface that enacts the
  transition demonstrates the concept.
- **Consequences:** `SITE_ARCHITECTURE.md` defines the progression, interface
  states, motion rule, and visual prohibitions that future work is reviewed
  against.

## DEC-008 — Commercial territories are natural areas, not limits

- **Status:** Accepted
- **Decision:** The territories in `COMMERCIAL_TERRITORY.md` and
  `CATEGORY_BOUNDARY.md` describe natural application areas, not limits on the
  identity.
- **Rationale:** The transition SIBurst names may matter to kinds of work that do
  not yet exist. Fixing the territory now would narrow the name prematurely.
- **Consequences:** New uses are judged by the boundary test, not by membership
  in a list.

## DEC-009 — The repository remains public-safe

- **Status:** Accepted
- **Decision:** All repository content must be safe for unrestricted public
  inspection. Pricing, buyers, negotiation, outreach, valuation, and private
  Sohadot strategy are prohibited from this repository.
- **Rationale:** The repository is public. It exists to define the concept, not
  to record commercial intentions.
- **Consequences:** Every change is reviewed against this rule before it is
  committed. Information that is not public-safe is never added, even
  temporarily.

## DEC-010 — No landing page before the foundation passes review

- **Status:** Accepted
- **Decision:** No landing page, site code, or visual production asset is
  produced until the conceptual foundation passes review.
- **Rationale:** An interface built before the concept is settled would fix
  unsettled ideas in visible form.
- **Consequences:** Sprint 0 contains only the nine foundation documents. No
  `index.html` and no site publishing configuration exist.

## DEC-011 — Phase change is represented by a rule change

- **Status:** Accepted
- **Decision:** The visual transition must alter geometry, topology, hierarchy,
  or another structural rule. Increased intensity alone is not enough. The chosen
  rule change is grid → relational field: before S4, position is assigned by
  index within lanes and cells; after S4, position is derived from relationships.
- **Rationale:** The thesis separates "more capability" from "a different
  operating regime". An interface that shows the transition only as more
  density, brightness, or speed would show more of the same, which is the
  opposite of the thesis.
- **Consequences:** `INTERFACE_CONTRACT.md` §2 defines the Lattice and Field
  rules. Acceptance Tests 1 and 2 fail any implementation whose S4 differs from
  S1 only in intensity or quantity.

## DEC-012 — Identity persists across the transition

- **Status:** Accepted
- **Decision:** The interface represents one system crossing regimes, not one
  scene being replaced by another. The entity set is frozen at the end of S3;
  entities, anchors, relationships, and the boundary all persist through S4.
- **Rationale:** The transition SIBurst names happens to a system. If the system
  were replaced, the interface would show substitution, not transition.
- **Consequences:** Cross-fading between independent compositions is prohibited.
  Anchors carry permanent identifiers. Acceptance Test 3 enforces the invariant.

## DEC-013 — Interface states are scoped to the demonstration

- **Status:** Accepted
- **Decision:** Labels such as `TRANSITION DETECTED` describe the on-screen model
  state and must not imply real-world AI telemetry. Every state label carries a
  scope prefix and stage index, the boundary identifies the system as a
  demonstration, and telemetry vocabulary and devices are prohibited.
- **Rationale:** An interface that looked like a live instrument would make an
  implicit claim that a real transition is being observed, which
  `PUBLIC_CLAIM_POLICY.md` forbids.
- **Consequences:** `INTERFACE_CONTRACT.md` §5 defines the labels, framing rule,
  and prohibited vocabulary. The progress variable `p` is never displayed as a
  number. Acceptance Tests 5 and 15 enforce the boundary. This resolves the
  Sprint 0 open question on interface-state framing.

## DEC-014 — Motion must carry semantic information

- **Status:** Accepted
- **Decision:** Every animation must correspond to a defined state or
  relationship change, within the six motion classes in `MOTION_SEMANTICS.md`.
  Demonstration motion is driven by progress, and the system is still when the
  visitor is idle.
- **Rationale:** Ornamental motion is the most common route to generic AI imagery,
  and it competes with the one change that matters.
- **Consequences:** Ambient, looping, and decorative motion are prohibited.
  Acceptance Test 9 fails any animation that cannot be mapped to a class and stage.

## DEC-015 — Accessibility preserves the thesis

- **Status:** Accepted
- **Decision:** Reduced-motion, keyboard, mobile, zoomed, and assistive-technology
  experiences must preserve the distinction between accumulation and regime
  change. The target is WCAG 2.2 AA.
- **Rationale:** A thesis that survives only under ideal viewing conditions is an
  effect, not a concept. Every visitor should be able to see the difference
  between more and different.
- **Consequences:** `MOTION_SEMANTICS.md` §4 and `RESPONSIVE_ACCESSIBILITY.md`
  define equivalent paths. Instability is confined to the demonstration.
  Acceptance Tests 6, 7, 8, 13, and 17 enforce the requirement.

## DEC-016 — Implementation remains static-first and dependency-minimal

- **Status:** Accepted
- **Decision:** The future site should prefer semantic HTML, CSS, SVG, and
  minimal vanilla JavaScript. Frameworks, external script or font sources,
  analytics, and heavy rendering need explicit justification through a recorded
  decision.
- **Rationale:** The concept should be understandable on modest hardware and
  without scripting. Every dependency is a liability for durability,
  performance, and accessibility.
- **Consequences:** `INTERFACE_CONTRACT.md` §8 defines the constraints, budgets,
  and progressive-enhancement baseline. Acceptance Tests 11 and 18 enforce them.

## DEC-017 — Reference HTML is generated from canonical Markdown

- **Status:** Accepted
- **Decision:** Canonical Markdown remains the single source of truth. Public
  HTML reference pages are generated derivatives and are never edited as
  independent content.
  - The canonical `.md` documents in this repository remain authoritative.
  - Reference HTML may be generated for the public site. It is not a second
    editorial source and is never edited by hand.
  - Generation is one-way, from Markdown to HTML, and is deterministic.
  - Validation fails whenever committed or published reference output does not
    match what the canonical Markdown regenerates.
  - The public site presents the documents inside its own reference layer.
    GitHub-rendered Markdown may remain an auxiliary source link, not the
    primary reading experience.
  - Generation introduces no runtime dependency into the public site.
  - Renderer and tool selection is an implementation detail for a later sprint.
    Once selected, the tooling is pinned and reproducible.
- **Rationale:** The doctrine must be readable on the site without creating a
  second version of it. A single canonical source, with derivatives that are
  checked mechanically, keeps what the site says identical to what the
  repository governs.
- **Consequences:** `INTERFACE_CONTRACT.md` §7.4 defines the invariants.
  Acceptance Test 12 fails any reference content that diverges from the
  canonical Markdown. No renderer or dependency is introduced in Sprint 1.
