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
