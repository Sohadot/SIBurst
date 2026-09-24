# Site Architecture

The conceptual design of the future SIBurst interface. This document contains
no code and no visual production assets. It defines what the interface must
*mean*, so that any later implementation can be judged against it.

## Principle

The interface must embody the thesis, not illustrate it.

The eventual site is **one continuous system**, not a sequence of conventional
page sections. The visitor does not scroll past panels about a phase change;
the visitor moves a single system through one.

The experience must make this distinction visible:

```
MORE OF THE SAME
        ↓
     THRESHOLD
        ↓
A DIFFERENT OPERATING REGIME
```

## Visual thesis

A system begins inside a stable geometry.

Capability accumulates.

At first, more capability produces more of the same: elements multiply,
connections strengthen, but the rules of the space are unchanged.

As the visitor progresses, signals increase, relationships densify, and the
system approaches a boundary.

At THRESHOLD, the interface must visibly show that continuity is becoming
insufficient to describe the state: the existing geometry strains to contain
what is inside it.

At PHASE CHANGE, there is **no explosion**. Instead, the interface changes its
geometry, its rules, its topology, its spatial relationships, or its
information architecture itself. What the visitor sees after the transition
cannot be produced by continuing what they saw before.

## Canonical progression

| Stage | Name | What changes | What must not change |
|---|---|---|---|
| **00** | QUIET ACCUMULATION | A sparse, stable system. Small additions, each unremarkable. | The rules of the space. |
| **01** | SCALE | Elements and connections increase. The system is visibly larger and busier. | The kind of thing the system is. This is "more of the same" made explicit. |
| **02** | THRESHOLD | Density reaches the limits of the geometry. Relationships begin to exceed the structure built to hold them. | Nothing breaks yet. The strain is the signal. |
| **03** | INSTABILITY | The old description visibly fails in places: alignments slip, the layout can no longer represent every relationship faithfully. | The visitor's orientation. Instability is shown, not inflicted on usability. |
| **04** | PHASE CHANGE | The rules change: a new geometry, topology, or organizing principle takes over. The same elements are now related differently. | Continuity of identity. The same system has crossed; it has not been replaced. |
| **05** | SIBURST | The transition is named. The interface identifies the crossing itself as the subject of the site. | The claim boundary. Naming the transition in the interface is not a claim that it has occurred in the world. |
| **06** | THE AFTER | The system operates in its new regime. Navigation, structure, and information follow the new rules, and the foundation documents are reachable from here. | Honesty about the after: it is a design state, not a forecast. |

## Interface states

Preliminary state labels for use in the interface:

- `ACCUMULATING`
- `DENSITY RISING`
- `THRESHOLD APPROACHING`
- `REGIME UNSTABLE`
- `TRANSITION DETECTED`
- `NEW OPERATING REGIME`

These are **interface language**, describing the state of the on-screen system.
They are not factual claims about current real-world AI and must never be wired
to, or presented as, live measurements of real systems (see
`PUBLIC_CLAIM_POLICY.md`).

## Motion rule

Every animation must correspond to a conceptual state change.

If an animation can be removed without losing information about accumulation,
threshold, or regime, it should not exist.

## Visual prohibitions

- AI brains
- humanoid robots
- glowing human heads
- generic neural-network imagery
- explosions
- singularity vortex clichés
- cyberpunk decoration
- floating SaaS cards
- stock dashboards
- gratuitous gradients
- animation without semantic meaning

## Acceptance questions for any future implementation

1. Can a visitor tell the difference between stage 01 (more) and stage 04
   (different) without reading any text?
2. Does the phase change alter the rules of the space, rather than its intensity?
3. Would any prohibited image or pattern be recognized in a screenshot?
4. Does every animation map to a stage in the progression?
5. Is any interface state readable as a claim about real-world AI? If so, it
   fails.

## Implementation contracts

Sprint 1 turns this conceptual architecture into implementation contracts:

| Document | Governs |
|---|---|
| `INTERFACE_CONTRACT.md` | The state machine (S0–S6 = stages 00–06), the geometry grammar and rule change, the semantic primitives, final interface-state language and framing, progress, content architecture, and implementation constraints. |
| `VISUAL_SYSTEM.md` | Spatial character, color roles, typography roles, and density progression. |
| `MOTION_SEMANTICS.md` | The motion taxonomy and reduced-motion behavior. |
| `RESPONSIVE_ACCESSIBILITY.md` | Viewport behavior, keyboard, zoom, and assistive-technology requirements. |
| `INTERFACE_ACCEPTANCE.md` | The pass/fail tests every implementation must meet. |

The preliminary interface states listed above are finalized, with their
framing rule, in `INTERFACE_CONTRACT.md` §5.

**Authority.** This document defines the conceptual experience. The Sprint 1
contracts define how that concept may be implemented. If an implementation
contract contradicts this document, the implementation contract is defective.

## Scope

No HTML, site code, or visual production assets are part of Sprint 0 or
Sprint 1. This document and the implementation contracts are the specification
against which that later work will be reviewed.
