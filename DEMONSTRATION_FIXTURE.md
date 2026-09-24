# Demonstration Fixture

The canonical demonstration system for the SIBurst interface.

| File | Role |
|---|---|
| `data/demonstration-fixture.json` | The fixture: the implementation source of truth for the demonstration graph and geometry. |
| `schemas/demonstration-fixture.schema.json` | Structural schema (JSON Schema 2020-12). |
| `tools/validate_fixture.py` | Validator. Recomputes every law below and fails closed. |
| `tests/test_fixture.py` | Mutation tests: each breaks one invariant and proves the validator rejects it. |

This document explains the fixture's laws. Where a number is given here, the
JSON file is canonical and the validator is the judge.

## 1. What the fixture is

`INTERFACE_CONTRACT.md` requires one authored, deterministic demonstration
system that crosses from the Lattice to the Field (§1–§4, §8.2). The fixture
is that system, fixed as data: 24 entities, their arrival order, 41
relationships and the stages at which they become active, four anchors, Lattice
positions, S3 displacements, and Field coordinates.

Future interface code renders this data. It does not invent, randomize, or
recompute the graph, the geometry, the stubs, the clusters, or the anchors.

## 2. What the fixture is not

The fixture is demonstration data for the on-screen model. It is **not**:

- a model of any real AI system, organization, or dataset;
- a capability benchmark or an intelligence measure;
- a threshold detector, scientific or otherwise;
- a prediction, forecast, or simulation of real events;
- evidence that intelligence undergoes phase transitions.

Entities are abstract (`N01`–`N24`). Clusters (`C1`–`C4`) are authored
topology that makes the Field legible. They are not categories of
intelligence, capability classes, or scientific communities. Occupancy
percentages are layout facts about a 24-cell grid, not progress measures, and
must never appear as public readouts (`INTERFACE_CONTRACT.md` §5.3, §6.1).

## 3. Why 24 entities

24 is an **implementation choice with no scientific meaning.** It:

- fits both node budgets in `INTERFACE_CONTRACT.md` §8 (24–64 wide, 16–40
  narrow), so every viewport shows the same entities;
- fills a 4 × 6 Lattice exactly, so the stages reach exact states: sparse
  (3/24), scale (15/24), near capacity (22/24), and full (24/24);
- divides into four clusters of six.

## 4. The Lattice

One logical Lattice: 4 lanes × 6 cells = 24 cells.

**Placement law.** An entity with zero-based arrival index `i` occupies:

```
lane = floor(i / 6)
cell = i mod 6
```

No entity is positioned by hand. Entity `N(k)` has arrival index `k − 1`, so
`N01`–`N06` fill lane 0, `N07`–`N12` lane 1, `N13`–`N18` lane 2, and
`N19`–`N24` lane 3. Position before S4 carries no information about
relationships.

For comparisons with the Field, a cell centre is normalized as
`x = (cell + 0.5) / 6`, `y = (lane + 0.5) / 4`.

## 5. Arrival schedule

| Stage | Entities present (cumulative) | Arriving | Lattice occupancy |
|---|---|---|---|
| S0 QUIET ACCUMULATION | 3 | N01–N03 | 12.5% |
| S1 SCALE | 15 | N04–N15 | 62.5% |
| S2 THRESHOLD | 22 | N16–N22 | ≈ 91.7% |
| S3 INSTABILITY | 24 | N23–N24 | 100% |
| S4–S6 | 24 | none | not applicable |

From S4 onward no entity is created, removed, merged, or split.

## 6. Routing law

For entities A and B, with `lane_distance = |A.lane − B.lane|` and
`cell_distance = |A.cell − B.cell|`, a relationship is **Lattice-routable** only if:

- **same lane:** `lane_distance == 0` and `cell_distance <= 2`; or
- **adjacent lane:** `lane_distance == 1` and `cell_distance <= 1`.

Everything else is unroutable under the Lattice. Routability is always
computed from this law. The fixture never declares it.

## 7. Relationship lifecycle

Each relationship has an ID (`R01`–`R41`), a source, a target, and an
`activation_stage` in S0–S3.

- A relationship activates no earlier than the later arrival of its two endpoints.
- No relationship activates at S4, S5, or S6. S4 changes representation; it
  creates nothing.
- Relationships are listed in a stable order: by activation stage, then source
  arrival index, then target arrival index. The source always arrives first.

## 8. Stubs

A relationship is an **unrouted stub** at a stage exactly when:

1. both endpoints exist;
2. the relationship is active;
3. it is not Lattice-routable; and
4. the stage is before S4.

At S4, every stub resolves into its full relationship. No relationship is
invented.

| Stage | Active relationships | Stubs |
|---|---|---|
| S0 | 2 | 0 |
| S1 | 17 | 0 |
| S2 | 29 | 7 |
| S3 | 41 | 17 |
| S4–S6 | 41 | 0 |

S1 is pure "more of the same": more entities and relationships, all routable.
S2 introduces the first relationships the Lattice cannot hold. S3 raises both
the count and the share of stubs (7/29 → 17/41), without changing any rule.

The fixture stores this table in `derived` for inspection. The validator
recomputes it and rejects any difference.

## 9. S3 pressure and offset law

At S3, each entity has:

```
pressure = number of active S3 stubs incident to the entity
```

- **Pressure 0:** the entity stays centred in its cell.
- **Pressure > 0:** the entity is displaced within its cell by an offset
  `(offset_cell, offset_lane)`, measured in logical cell units:

```
v         = mean over the entity's stub partners of
            (partner.cell − cell, partner.lane − lane)
if v = (0, 0): v = axis[ id_number mod 4 ]
               where axis = [(1,0), (0,1), (−1,0), (0,−1)] and id_number is 1–24
magnitude = min(0.40, 0.10 × pressure)
offset    = magnitude × v / |v|, each component truncated toward zero
            to 4 decimal places
```

The magnitude is set by pressure. The direction is set by the entity's
relationships: each entity is drawn toward the relationships the Lattice cannot
route. Only when those pulls cancel exactly does the direction come from the
entity's identifier. The result is a pure function of the entity's identity in
the fixture. There is no randomness, and the offset never exceeds 0.40 of a
cell (below the half-cell bound in the contract). Lane and cell identity never
change.

Offsets apply only inside the demonstration boundary, and only at S3. In the
canonical fixture 23 of 24 entities carry pressure. Most offsets are 0.1 of a
cell, and the largest is about 0.30 (pressure 3).

## 10. Clusters

| Cluster | Members | Lanes spanned |
|---|---|---|
| C1 | N01, N02, N07, N08, N17, N23 | 0, 1, 2, 3 |
| C2 | N03, N04, N09, N16, N21, N22 | 0, 1, 2, 3 |
| C3 | N05, N06, N11, N12, N19, N20 | 0, 1, 3 |
| C4 | N10, N13, N14, N15, N18, N24 | 1, 2, 3 |

Each cluster begins as a compact core whose early relationships the Lattice can
route. Later arrivals land in distant cells because arrival order ignores
relationships. Their relationships to the core are the stubs. The Field
therefore reveals as clusters exactly the structure the Lattice could not
represent (`INTERFACE_CONTRACT.md` §1.1).

- 36 relationships are intra-cluster and 5 are inter-cluster: N01–N03,
  N04–N05, N08–N14, N12–N24, and N13–N21.
- Every cluster is connected by its own relationships, and every member has at
  least two intra-cluster relationships.
- The whole graph is connected. Degrees range from 2 to 4, so there is no
  dominant hub.

## 11. Anchors

Four anchors: **N05, N08, N09, N19.** They are chosen for topology and carry
no special relationships. The anchor flag affects no law.

- **Separation proof — N08 and N09.** They are Lattice neighbours in lane 1
  (cells 1 and 2), but they sit in different clusters (C1, C2), four
  relationships apart. In the Field they are 3.6 × farther apart than in the
  Lattice.
- **Convergence proof — N05 and N19.** They are at opposite corners of the
  Lattice (lane 0, cell 4 and lane 3, cell 0), in the same cluster (C3), and
  directly related. Their relationship is a stub through S2–S3 and completes at
  S4. In the Field they are 0.18 × their Lattice distance.

The validator requires a separation ratio of at least 2.0 and a convergence
ratio of at most 0.5, with the two pairs disjoint.

## 12. Field geometry

Every entity has canonical Field coordinates `x, y ∈ [0.05, 0.95]` in a
normalized unit square (origin at top-left, y downward), with at most three
decimals.

The coordinates were produced **offline, once**, by stress majorization over
graph hop distances, from a fixed starting arrangement with no random input.
They were then scaled into [0.1, 0.9] and rounded. The committed numbers are
canonical. No runtime algorithm, random process, force simulation, or physics
simulation recomputes them.

Measured properties (validated):

| Property | Value | Requirement |
|---|---|---|
| Mean distance, linked pairs | 0.169 | — |
| Mean distance, unlinked pairs | 0.506 | — |
| Linked ÷ unlinked | 0.335 | ≤ 0.80 |
| Mean distance, intra-cluster pairs | 0.193 | ≤ 0.80 × inter-cluster |
| Mean distance, inter-cluster pairs | 0.528 | — |
| Minimum separation (1:1) | 0.068 | ≥ 0.05 |

The validator also requires the following:
- every entity is nearest to its own cluster's centroid;
- cluster centroids are at least 0.25 apart;
- no cluster collapses (its mean distance to centroid is at least 0.05);
- no two entities share a coordinate.

## 13. Viewports

There is one logical fixture, not one per viewport. Every viewport shows all 24
entities, the same relationships, the same clusters, and the same four anchors.

An implementation **may**:

- rotate lane orientation (lanes along the long axis);
- scale axes uniformly, or anisotropically within the validated aspect range
  of 9:16 to 16:9;
- change the boundary's aspect ratio and spacing within that range.

An implementation **may not** change arrival order, cluster membership, anchors,
relationships, Lattice lane/cell assignment, or Field topology.

The validator checks the Field at 1:1, 16:9, and 9:16. At every aspect ratio it
requires the linked ÷ unlinked ratio to stay at or below 0.80, and it requires
a minimum separation of 0.05 at 1:1 and 0.035 at the other two, in units of the
longer side. Any wider aspect ratio needs the fixture to be revalidated first.

## 14. Determinism and serialization

- UTF-8, LF line endings, 2-space indentation, and a trailing newline.
- Key order as written in the schema. Entities are ordered by arrival index.
  Relationships follow the order in §7.
- No volatile fields: no creation times, machine paths, user names, or
  run-time seeds.
- The validator rejects any file whose bytes differ from the canonical
  serialization of its content.
- No checksum is stored. Canonical serialization plus validation already makes
  every change visible.

## 15. Validator guarantees

`python tools/validate_fixture.py` exits `0` only if every check passes, and
prints each failure with its invariant, subject, expected condition, and actual
result. It checks:

| Group | Checks |
|---|---|
| Schema and structure | Conformance to the schema; version; entities `N01`–`N24` exactly once in arrival order; four clusters of six; four anchors; unique relationship IDs; no self-links or duplicate pairs; valid endpoints; stable ordering. |
| Arrival | Cumulative totals 3 / 15 / 22 / 24; no arrival after S3. |
| Lattice | Placement law; no duplicate cells; 24 cells filled; routing parameters equal the normative values. |
| Lifecycle | No activation before both endpoints exist; none after S3. |
| Routability | 0 stubs at S0 and S1; at least 4 at S2; more at S3 than S2, with a higher share. |
| Graph | Connected; every degree ≥ 2; no hub above 2 × mean degree; intra-cluster > inter-cluster; each cluster internally connected. |
| Instability | Offsets recomputed exactly; zero-pressure entities centred; half-cell bound. |
| Field | Bounds; precision; unique coordinates; minimum separation; linked vs unlinked; intra vs inter; centroids; legibility; no collapse; all three aspect ratios. |
| Anchors | Flags match the list; anchors exist before S4; separation and convergence proofs. |
| Derived | The stored stage table equals the recomputation. |
| Surface | No keys or labels suggesting scores, levels, telemetry, live or real-time state, times, dates, predictions, probabilities, randomness, or seeds. This defends the fixture's surface; it does not censor natural language. |
| Serialization | Canonical bytes and LF line endings. |

`python -m unittest discover -s tests` runs the mutation tests.

## 16. Claim boundary

Everything in the fixture is scoped to the SIBurst demonstration system
(`PUBLIC_CLAIM_POLICY.md`: DEFINITION within the framework). Field proximity is
an authored layout property, not empirical evidence. Stage labels are interface
states, not observations (`INTERFACE_CONTRACT.md` §5).
