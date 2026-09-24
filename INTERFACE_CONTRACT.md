# Interface Contract

The highest-level implementation contract for the SIBurst interface.

`SITE_ARCHITECTURE.md` defines what the interface must mean. This document
defines how that meaning may be implemented: as an explicit state machine,
over a governed geometry grammar, using a fixed set of semantic primitives.
It contains no code and no assets.

The governing rule is unchanged:

> The interface must embody the thesis, not illustrate it.

The defining implementation distinction:

> Before the transition, quantity changes while rules remain stable.
> At the transition, the rules themselves change.

A conforming implementation makes the difference between **MORE** and
**DIFFERENT** visible without depending on explanatory copy.

---

## 1. The demonstration system

The interface contains one **demonstration system**: a bounded, on-screen
model made of entities and relationships. It is the only thing that crosses
the transition. Everything else on the page — navigation, captions, reference
content — stays outside it and remains stable.

The demonstration system is a model of the SIBurst concept. It is not a
representation of any real AI system, dataset, or measurement.

Its threshold is a property of the model: the point at which the Lattice can no
longer represent the model's own relationships. It does not operationalize the
candidate threshold conditions in `FOUNDATION_THESIS.md`, which remain
illustrative, and it is not a method for detecting thresholds in real systems.

### 1.1 The relationship graph

The system is defined by a fixed, authored graph:

- a set of **entities** (nodes), each with a permanent identifier;
- a set of **relationships** (links) between pairs of entities, each with the
  stage at which it comes into existence.

The graph is authored in advance and ships with the page. It is not generated
randomly at runtime. The canonical graph is defined in
`data/demonstration-fixture.json` (§8.2). Its construction must satisfy three conditions:

1. **Arrival order is not relationship order.** Entities are placed in the
   pre-transition geometry by the order in which they appear. Relationships are
   authored so that strongly related entities are frequently placed far apart
   by that order.
2. **Non-local relationships grow.** The share of relationships connecting
   entities that are not adjacent in the pre-transition geometry rises through
   S1–S3.
3. **Latent structure exists.** The relationships form identifiable clusters
   that the pre-transition geometry cannot show, and that the post-transition
   geometry does show.

These conditions give the transition its meaning: **the new regime is
organized by the relationships the old regime could not represent.**

### 1.2 Entity conservation

The set of entities is **frozen at the end of S3**. From S4 onward no entity is
added, removed, merged, or split. Relationships that exist at the end of S3
all persist after S4. Relationships that could not be drawn under the old
rules (see §2.2) are completed, not invented.

---

## 2. Geometry grammar

### 2.1 Pre-transition law: the Lattice (S0–S3)

Before S4, the system obeys one spatial law, called **the Lattice**:

| Rule | Statement |
|---|---|
| **L1 — Lanes** | Space is divided into parallel, bounded **lanes**. Every entity belongs to exactly one lane. |
| **L2 — Cells** | Each lane is divided into equal **cells**. Every entity occupies exactly one cell, centered on it. |
| **L3 — Position by index** | An entity's position is determined by its arrival index: lanes fill in order, cells fill in order. Position carries no information about relationships. |
| **L4 — Orthogonal routing** | Relationships are drawn only along the rails between cells, with right-angled turns. |
| **L5 — Adjacency limit** | A relationship can be routed only between entities in the same lane or in adjacent lanes, within a bounded routing distance. |
| **L6 — Hierarchy** | Lanes contain cells; cells contain entities. Containment is the organizing hierarchy. |

A relationship that the Lattice cannot route under L4–L5 is still real in the
graph. Before S4 it is shown as an **unrouted stub**: a short segment leaving
the entity and ending at the edge of its cell, with a terminal mark. Stubs are
the visible record of relationships the structure cannot hold.

### 2.2 Post-transition law: the Field (S4–S6)

At S4, the Lattice is replaced by one new spatial law, called **the Field**:

| Rule | Statement |
|---|---|
| **F1 — No lanes** | Lanes and cells are retired. There is one shared space inside the boundary. |
| **F2 — Position by relationship** | An entity's position is determined by the relationship graph: entities that share more relationships are placed closer together; clusters become visible as spatial groupings. |
| **F3 — Direct routing** | Relationships are drawn as direct paths between the two entities, regardless of distance. |
| **F4 — No adjacency limit** | Any relationship in the graph can be drawn. Every stub from S2–S3 is completed into a full relationship. |
| **F5 — Network adjacency** | Containment no longer organizes the system. The relationship graph does. |

Field positions are **precomputed** from the authored graph and ship with the
page. They are not produced by a live, randomly seeded simulation, so every
visitor and every reviewer sees the same layout.

### 2.3 The rule change

The transformation chosen for SIBurst is:

> **Grid → relational field.** Position stops being assigned by index and
> starts being derived from relationships.

Stated as a testable change:

- **Before S4**, knowing an entity's arrival index is enough to predict where
  it is. Its lane predicts its band of space. Its relationships predict nothing
  about its position.
- **After S4**, an entity's arrival index and former lane predict nothing about
  its position. Its relationships predict it.

The secondary changes follow from the primary one: orthogonal routing becomes
direct routing, the adjacency limit is lifted, and containment gives way to
network adjacency.

### 2.4 Prohibited transition devices

The rule change must not be conveyed or accompanied by: explosion, particle
blast, screen shake, flash, speed ramp, random scattering, generic glitch
effects, vortex or spiral motion, or singularity imagery. The phase change
occurs through rule transformation, not spectacle.

---

## 3. Semantic primitives

The system uses exactly six primitives. No other visual element may appear
inside the demonstration system. Every element has a semantic role.

| Primitive | Meaning | Appears | Survives S4? | May change | Must remain invariant |
|---|---|---|---|---|---|
| **Node** | An entity: a unit of accumulated capability in the model. | S0, growing in number through S3. | Yes. | Position; routing of its links; post-transition emphasis. | Its existence, its identifier, its basic mark shape. Count is frozen from the end of S3. |
| **Link** | A relationship between two nodes. | When its relationship comes into existence (S0–S3); stubs from S2. | Yes. | Route (orthogonal → direct); stubs become complete links. | Which two nodes it connects. No link is created or removed at S4. |
| **Rail** | The Lattice itself: lane boundaries and cell divisions. It *is* the pre-transition spatial law made visible. | S0. | **No.** Retired during S4. | Visibility during S4 only, as it retires. | Straight and regular while it exists. It never bends, breaks, or shatters; the rule is lifted, not destroyed. |
| **Boundary** | The outer edge of the demonstration system. It scopes the model and carries the demonstration label (§5). | S0. | Yes. | Proportions, to suit the viewport. | Always present around the whole system. Never removed, never broken. |
| **Identifier** | A permanent label for an **anchor** node (for example `07`). | S0 onward, on a small fixed subset of nodes. | Yes. | Position, which follows its node. | Text, and the node it belongs to. |
| **State readout** | The current interface state, scoped to the demonstration. | S0 onward. | Yes. | The stage it reports. | Its scope prefix and position relative to the boundary. |

### 3.1 Anchors

A small, fixed subset of nodes (at least three, at most seven) are **anchors**.
They carry visible identifiers throughout. Anchors are chosen so that:

- at least two anchors sit in the **same lane** in the Lattice but in
  **different clusters** in the Field;
- at least two anchors sit in **different lanes** in the Lattice but in the
  **same cluster** in the Field.

Anchors are how the visitor sees continuity of identity. They make the rule
change legible: things that were side by side separate, and things that were
apart come together.

---

## 4. The state machine

### 4.1 Stages

The seven canonical stages correspond one-to-one to the stages in
`SITE_ARCHITECTURE.md` (S0 = 00, … S6 = 06).

| Stage | Name | Regime |
|---|---|---|
| S0 | QUIET ACCUMULATION | Lattice |
| S1 | SCALE | Lattice |
| S2 | THRESHOLD | Lattice, saturated |
| S3 | INSTABILITY | Lattice, failing locally |
| S4 | PHASE CHANGE | Lattice → Field |
| S5 | SIBURST | Field |
| S6 | THE AFTER | Field |

The stage is a pure function of progress: `stage = f(p)` (see §6). There are
no hidden timers, no random events, and no state that depends on how the
visitor arrived. The same `p` always produces the same system state.

### 4.2 Stage specifications

Occupancy means the share of Lattice cells holding a node.

#### S0 — QUIET ACCUMULATION

- **Semantic purpose:** establish a stable system and its rules before anything
  happens.
- **Visual condition:** a sparse Lattice inside its boundary; a few nodes,
  fewer links.
- **Geometry:** Lattice, rules L1–L6 fully visible through the rails.
- **Density:** low; occupancy at most about 15%.
- **Relationship behavior:** few links, all routable, all between near neighbors.
- **Navigation behavior:** stage navigation and the reference link are visible
  and usable from the first view.
- **Typography behavior:** state readout and identifiers are aligned to the
  rail rhythm, as grid-bound labels.
- **Permitted motion:** appearance of nodes and links as `p` advances (M1, M2 in
  `MOTION_SEMANTICS.md`).
- **Prohibited motion:** anything on load without progress; ambient drift,
  pulsing, breathing.
- **Orientation requirement:** the visitor can see the whole system and the
  stage index.
- **Exit condition:** `p` reaches the S1 boundary. By then the Lattice's rules
  must have been legible: lanes, cells, index order.

#### S1 — SCALE

- **Semantic purpose:** show "more of the same" explicitly.
- **Visual condition:** the same Lattice, visibly fuller and busier.
- **Geometry:** unchanged Lattice.
- **Density:** occupancy rises to roughly 60–75%.
- **Relationship behavior:** links multiply; all remain routable under L4–L5.
- **Navigation behavior:** unchanged.
- **Typography behavior:** unchanged; labels stay grid-bound.
- **Permitted motion:** M1, M2.
- **Prohibited motion:** any change of layout rule; acceleration used as meaning.
- **Orientation requirement:** anchors remain visible and in their cells.
- **Exit condition:** `p` reaches the S2 boundary. At exit, every relationship
  is still routable. S1 must end looking like S0 with more in it.

#### S2 — THRESHOLD

- **Semantic purpose:** show the structure approaching the limit of what it can
  represent.
- **Visual condition:** the Lattice is nearly full; relationships appear that
  it cannot route.
- **Geometry:** unchanged Lattice, at capacity.
- **Density:** occupancy 90% or more.
- **Relationship behavior:** unrouted stubs appear and accumulate; routed links
  crowd shared rail segments.
- **Navigation behavior:** unchanged.
- **Typography behavior:** unchanged. The state readout adopts the threshold
  role (see `VISUAL_SYSTEM.md`).
- **Permitted motion:** M1, M2, M3 (constraint pressure).
- **Prohibited motion:** anything breaking the Lattice; shaking, flicker,
  alarm-style flashing.
- **Orientation requirement:** nothing is broken yet. Every node is still in
  its cell.
- **Exit condition:** `p` reaches the S3 boundary, and stubs are clearly
  visible as a category distinct from routed links.

#### S3 — INSTABILITY

- **Semantic purpose:** show the old description failing locally.
- **Visual condition:** the Lattice still governs, but no longer represents the
  system faithfully.
- **Geometry:** Lattice rules still in force. Rails stay straight. Nodes under
  the most pressure slip off their cell centers.
- **Density:** occupancy 100%; stubs keep increasing.
- **Relationship behavior:** links detour and overlap; stubs outnumber newly
  routed links.
- **Navigation behavior:** unchanged and fully stable. Instability is confined
  to the demonstration system.
- **Typography behavior:** grid-bound labels may be pushed off alignment only
  where their node has slipped. Captions and navigation text are unaffected.
- **Permitted motion:** M3, M4 (local misalignment), deterministic and bounded.
  A node's offset is at most half a cell and proportional to its count of
  unrouted relationships.
- **Prohibited motion:** random jitter, global distortion, glitch effects,
  any instability outside the boundary.
- **Orientation requirement:** navigation, focus order, captions, and controls
  are exactly as stable as in S0.
- **Exit condition:** `p` reaches the S4 boundary. The entity set is frozen at
  this point.

#### S4 — PHASE CHANGE

- **Semantic purpose:** change the rules while keeping the system.
- **Visual condition:** rails retire; nodes move from Lattice positions to Field
  positions; stubs complete; links resolve into direct paths.
- **Geometry:** Lattice → Field, following §2.3.
- **Density:** entity count unchanged. Occupancy stops being a meaningful measure.
- **Relationship behavior:** every relationship is drawn. Clusters become visible.
- **Navigation behavior:** unchanged.
- **Typography behavior:** identifiers detach from the grid rhythm and travel
  with their nodes. From here on, labels are attached to entities, not to
  coordinates.
- **Permitted motion:** M5 (topology reconfiguration), in this order: rails
  retire → nodes reposition → links resolve.
- **Prohibited motion:** every device in §2.4; replacing the scene; fading out
  one composition and fading in another.
- **Orientation requirement:** anchors are visible and trackable throughout.
- **Exit condition:** `p` reaches the S5 boundary. At exit, every node is at its
  Field position and no rail remains.

#### S5 — SIBURST

- **Semantic purpose:** name the crossing.
- **Visual condition:** the Field is stable. The name **SIBurst** appears in the
  display voice, placed at the boundary, not on any node. A **transition
  record** shows a reduced Lattice view (the end of S3) next to the Field, with
  the same anchors marked in both.
- **Geometry:** Field.
- **Density:** unchanged.
- **Relationship behavior:** static.
- **Navigation behavior:** unchanged.
- **Typography behavior:** display voice for the name; the caption states that
  SIBurst names the crossing just shown.
- **Permitted motion:** M6 (stabilization); appearance of the name and the
  transition record.
- **Prohibited motion:** celebratory effects of any kind; motion that makes
  the name appear to emerge from a burst.
- **Orientation requirement:** the visitor can compare before and after
  directly.
- **Exit condition:** `p` reaches the S6 boundary.

#### S6 — THE AFTER

- **Semantic purpose:** operate in the new regime and open the reference layer.
- **Visual condition:** the Field remains, visually quieter. The reference
  index (§7) is organized by the Field's grammar.
- **Geometry:** Field.
- **Density:** the demonstration recedes in contrast so that text is readable.
- **Relationship behavior:** static. Links between reference items express real
  relationships between the documents.
- **Navigation behavior:** the reference layer is fully available.
- **Typography behavior:** reading voice dominates.
- **Permitted motion:** M6 only; focus and hover feedback on reference items.
- **Prohibited motion:** any return to accumulation; looping back to S0
  automatically.
- **Orientation requirement:** the visitor knows the demonstration has ended
  and where the doctrine is.
- **Exit condition:** none. S6 is terminal. The visitor may navigate to any
  stage or document.

### 4.3 Continuity-of-identity invariant

The same system must persist through the transition.

- Every entity present at the end of S3 is present, identifiable, and
  unchanged in identity at S5 and S6.
- Every anchor keeps its identifier and is visible throughout S4.
- Relationships may reorganize, topology may change, hierarchy may change, and
  spatial rules change. The entity set and the relationship graph do not.
- The boundary persists throughout.

The visitor must perceive **"same system — different regime"**, never
**"old scene disappeared — new scene appeared."** An implementation that
cross-fades between two independent compositions violates this invariant,
even if both compositions are individually correct.

---

## 5. Interface-state language

### 5.1 Canonical labels

| Stage | State label |
|---|---|
| S0 | `ACCUMULATING` |
| S1 | `DENSITY RISING` |
| S2 | `THRESHOLD APPROACHING` |
| S3 | `REGIME UNSTABLE` |
| S4 | `TRANSITION DETECTED` |
| S5 | `SIBURST` |
| S6 | `NEW OPERATING REGIME` |

This resolves the Sprint 0 open question on interface-state framing.

### 5.2 The framing rule

**Every state label is scoped to the demonstration system.**

- A state label is always rendered with a **scope prefix** and a **stage
  index**, in the same element, for example:
  `DEMONSTRATION STATE · S4 / TRANSITION DETECTED`.
- The scope prefix is never smaller than the label and is never shown without it.
- The boundary carries a persistent caption, visible in every stage, that
  identifies the system as a model, for example:
  `SYSTEM DEMONSTRATION — a model of the SIBurst concept, not a measurement.`
- Every label that assistive technology announces includes the word
  "demonstration".

"Detected" in `TRANSITION DETECTED` refers to the model's own state change. It
must never be paired with anything that suggests sensing of external systems.

### 5.3 Prohibited state vocabulary and devices

The following must not appear in state readouts, captions, or labels:

- `LIVE`, `REAL-TIME`, `CURRENT`, `NOW` (as a status), `GLOBAL`, `WORLD`;
- `AI STATUS`, `AGI STATUS`, `SI LEVEL`, `CURRENT AI STATE`,
  `GLOBAL INTELLIGENCE`, or any equivalent;
- percentages, scores, indices, levels, or continuously changing numbers
  (the stage index S0–S6 is the only number the readout shows);
- timestamps, dates, countdowns, or clocks;
- telemetry devices: blinking "recording" dots, status lights, feed tickers,
  signal-strength meters.

### 5.4 Captions

Each stage may carry one short caption (no more than two sentences). Captions
support orientation, assistive technology, and the no-JavaScript path. They
are not required for Test 1 in `INTERFACE_ACCEPTANCE.md`, which must pass
without them.

Every caption must be classifiable under `PUBLIC_CLAIM_POLICY.md`. Reference
captions:

| Stage | Reference caption | Claim class |
|---|---|---|
| S0 | A system accumulates inside fixed rules. | METAPHOR |
| S1 | More entities. More relationships. The same rules. | METAPHOR |
| S2 | Relationships begin to exceed the structure built to hold them. | METAPHOR |
| S3 | The old description fails in places. | METAPHOR |
| S4 | The rules change. The entities remain. | METAPHOR |
| S5 | SIBurst names this crossing: from more capability to a different operating regime. | DEFINITION |
| S6 | SIBurst names the transition, not the prediction. | DEFINITION |

Captions describe the demonstration. They never describe current real-world AI.

---

## 6. Progress contract

### 6.1 The progress variable

The experience is driven by one normalized variable:

`p ∈ [0, 1]`

`p` is **visitor progress through the demonstration** and nothing else. It is
not an intelligence score, a capability measure, a probability, or a time
estimate. It must never be displayed as a percentage or as a number of any kind.
Where progress is shown, it is shown as a stage position (for example `S3 / S6`).

### 6.2 Stage ranges

| Stage | Indicative range of `p` |
|---|---|
| S0 | 0.00 – 0.12 |
| S1 | 0.12 – 0.30 |
| S2 | 0.30 – 0.45 |
| S3 | 0.45 – 0.58 |
| S4 | 0.58 – 0.74 |
| S5 | 0.74 – 0.88 |
| S6 | 0.88 – 1.00 |

Implementations may move any boundary by up to ±0.03 to suit the layout,
provided that:

- stage order is preserved;
- S4 occupies at least 0.12 of the range, so the transition can be followed
  rather than flashed past;
- S1 is at least as long as S0, so "more of the same" is established;
- the ranges in use are recorded with the implementation.

### 6.3 Scroll behavior

- The experience may be scroll-driven. Scrolling advances `p`; it does not
  reveal a stack of unrelated sections. The demonstration system stays in view
  while `p` changes.
- Native scrolling is never overridden: no scroll-jacking, no altered scroll
  speed, no forced snapping between stages. Proximity snapping is permitted.
- Progress is reversible. Scrolling back returns the system to earlier states
  exactly, because the state is a function of `p`.

### 6.4 Discrete traversal

Visitors must be able to traverse the full sequence without precise scrolling:

- A persistent **stage navigation** lists S0–S6 as ordinary links, each moving
  to that stage's canonical point (the start of its range, or the midpoint of
  S4 for the transition).
- Each stage has a stable fragment address (for example `#s4`), which works
  with and without JavaScript.
- Keyboard and reduced-motion traversal reach the same seven states in the same
  order (see `MOTION_SEMANTICS.md` and `RESPONSIVE_ACCESSIBILITY.md`).

---

## 7. Content architecture

The page has two layers.

### 7.1 Experiential layer (S0–S5)

The demonstration system, the state readout, the stage navigation, and the
captions. It carries the thesis in the smallest possible amount of text. It
never reproduces the foundation documents.

### 7.2 Reference layer (S6 and beyond)

The governed doctrine, reached from S6 and from the persistent reference link:

| Reference item | Source of truth |
|---|---|
| Thesis | `FOUNDATION_THESIS.md` |
| Name architecture | `NAME_ARCHITECTURE.md` |
| Category boundary | `CATEGORY_BOUNDARY.md` |
| Commercial territory | `COMMERCIAL_TERRITORY.md` |
| Glossary | `GLOSSARY.md` |
| Claim policy | `PUBLIC_CLAIM_POLICY.md` |
| Decision log | `DECISION_LOG.md` |
| Interface doctrine | `SITE_ARCHITECTURE.md` and the Sprint 1 contracts |

Rules:

- The Markdown documents in this repository are the **single source of truth**.
  Reference pages present them; they do not paraphrase or fork them. Reference
  pages are generated from the Markdown as specified in §7.4.
- In S6 the reference index is laid out in the Field grammar: items are nodes,
  and links show real relationships between documents (for example, the
  thesis relates to the name architecture and the claim policy). In the page
  structure, the same index is an ordinary list of links in reading order.
- A **reference link** is visible from the first view, so a visitor can reach
  the doctrine without passing through the demonstration.

### 7.3 Excluded sections

The following conventional sections are not part of the architecture: Features,
Benefits, Testimonials, Pricing, Customers, Integrations, and filler FAQs. Any
of them requires a recorded decision in `DECISION_LOG.md` before it can be admitted.

---

### 7.4 Reference generation

Canonical Markdown remains the single source of truth. Public HTML reference
pages are generated derivatives and are never edited as independent content
(DEC-017).

Invariants:

- **One-way flow.** `Markdown → generated reference HTML`. Generated HTML is
  never used as input to change the Markdown.
- **No manual edits.** Generated reference HTML is never edited by hand. Any
  change to reference content is made in the canonical Markdown and regenerated.
- **Deterministic regeneration.** The same Markdown and the same pinned
  generation process always produce the same reference HTML.
- **Zero unexplained drift.** Validation regenerates the reference pages and
  compares them with the published or committed output. Any difference that is
  not explained by a change to the canonical Markdown fails validation.
- **Integrated reading.** The reference index links to the generated pages
  inside the site's own reference layer. Visitors are not required to leave the
  site to read the doctrine.
- **Provenance links.** Each generated page may link to its canonical Markdown
  file as its source. GitHub-rendered Markdown is an auxiliary source link, not
  the primary reading experience.
- **No runtime dependency.** Generation happens before publication. The public
  site loads no renderer and needs no conversion at runtime.
- **Presentation, not meaning.** Generation may change presentation (layout,
  navigation, typography). It never changes wording, claim class, or meaning.

The renderer and generation tooling are selected in a later implementation
sprint. Once selected, they are pinned to exact versions so regeneration is
reproducible. No renderer is selected by this contract.

## 8. Implementation constraints

- **Static-first.** The page is a static document. No server runtime is required.
- **Dependency-minimal.** Semantic HTML, CSS, inline SVG, and minimal vanilla
  JavaScript. No framework unless a later decision justifies one.
- **No external runtime sources.** No JavaScript CDNs and no external font
  services.
- **No analytics dependency** unless a later decision admits one.
- **No heavy rendering requirement.** The core experience does not require
  WebGL, large canvas rendering, high-end GPU effects, video backgrounds, or
  autoplay media. SVG is the default rendering surface, so that nodes,
  identifiers, and links remain document elements.
- **Deterministic data.** The graph, Lattice positions, and Field positions ship
  as static data with the page.
- **Modest hardware.** The complete sequence must be understandable on an
  ordinary mid-range phone. Where motion cannot run smoothly, the
  implementation falls back to the reduced-motion path rather than degrading
  meaning.
- **Indicative budgets:** 24–64 nodes on wide viewports and 16–40 on narrow
  ones; JavaScript no more than about 30 KB compressed; the complete first view
  no more than about 150 KB compressed, excluding reference pages.

### 8.1 Progressive enhancement

Without JavaScript, the document still presents the full sequence:

- seven stage sections in order, each with a static figure of the same
  demonstration system at that stage's canonical point, its state label with
  scope prefix, its caption, and its state description;
- the same entities and anchors in every stage figure, so the rule change
  and continuity of identity are visible by comparison;
- the stage navigation and the reference layer as ordinary links.

JavaScript enhances this document by combining the stage figures into one
persistent, progress-driven system. It does not create the content.

### 8.2 Demonstration fixture

The **deterministic demonstration fixture** exists before any animation logic
is written. It is established in `data/demonstration-fixture.json`, explained in
`DEMONSTRATION_FIXTURE.md`, and enforced by `tools/validate_fixture.py`. It is a
single, reviewable, static data source that governs:

- entity identifiers;
- arrival order;
- the relationship graph;
- the stage at which each relationship becomes active;
- anchors;
- Lattice placement (lane and cell for each entity);
- unroutable relationships (stubs) under rules L4–L5;
- Field placement;
- viewport variants, or deterministic rules for deriving them. There is one
  logical fixture for every viewport; only the transformations listed in
  `DEMONSTRATION_FIXTURE.md` §13 are permitted.

`data/demonstration-fixture.json` is the implementation source of truth for the
demonstration graph and geometry (DEC-018).

Rules:

- Rendering and animation code reads the fixture. It never invents, randomizes,
  or recomputes any of these values independently.
- Future HTML and JavaScript consume the fixture, or are compiled from it
  faithfully. Runtime interface code contains no independent duplicate of the
  graph or geometry. If fixture data is embedded in generated HTML, it is
  derived mechanically from the fixture file, in the same way DEC-017 governs
  reference pages.
- The fixture must pass its validator before any interface acceptance testing
  (`INTERFACE_ACCEPTANCE.md`, Gate 0).
- The fixture must satisfy §1.1, §1.2, and §3.1, and must allow acceptance
  Tests 2, 3, and 14 to be checked against it.
- The fixture is implementation data. It cannot redefine the thesis, the name,
  the stages, or the claim boundary. If a fixture conflicts with this contract,
  the fixture is defective.

This is an implementation integrity rule derived from DEC-011, DEC-012, and
DEC-016, not a new conceptual decision. The fixture was established in Sprint 2
(DEC-018 to DEC-021).

---

## 9. Authority

- `SITE_ARCHITECTURE.md` defines the conceptual experience and governs this
  contract.
- This contract governs `VISUAL_SYSTEM.md`, `MOTION_SEMANTICS.md`, and
  `RESPONSIVE_ACCESSIBILITY.md`.
- `INTERFACE_ACCEPTANCE.md` turns all of them into pass/fail tests.

If this contract contradicts the conceptual architecture, this contract is
defective. If an acceptance test contradicts a contract, the test is defective.
Defects are corrected and recorded in `DECISION_LOG.md`, never resolved silently
in the implementation.
