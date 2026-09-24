# Visual System

The visual language for the SIBurst interface. This document defines
principles and roles, not assets. It creates no colors, fonts, images, or
mockups. It is governed by `INTERFACE_CONTRACT.md`, whose primitives, stages,
and geometry grammar it styles.

## 1. Spatial character

The system should read as:

- **precise:** alignments are exact while the Lattice governs, so their later
  failure in S3 is visible;
- **infrastructural:** the demonstration resembles a structure or a schematic,
  not an illustration or a scene;
- **controlled:** nothing moves or appears without a state reason;
- **sparse at entry:** S0 leaves most of the boundary empty;
- **increasingly dense before threshold:** S1–S2 fill the Lattice toward capacity;
- **structurally altered after transition:** S5–S6 are visibly organized by a
  different rule, not a different decoration.

It must not read as generic "AI futurism". The visual prohibitions in
`SITE_ARCHITECTURE.md` apply in full. In addition:

- no glow, bloom, or light-trail effects on nodes or links;
- no depth effects (perspective, parallax, 3D rotation) in the demonstration;
- no decorative textures, noise, or scan lines;
- no gradients, except where a later decision gives one a semantic role.

## 2. Color roles

Color is assigned by **role**, never by mood. This document defines the roles;
it deliberately assigns no values. No color is claimed to carry scientific or
universal meaning.

| Role | Used for | Stages |
|---|---|---|
| **Background** | The page and the interior of the boundary. | All |
| **Primary information** | Captions, reference text, the SIBurst name, anchor identifiers. | All |
| **Secondary information** | Scope prefixes, stage index, supporting labels, the boundary caption. | All |
| **Structure** | Rails and the boundary. | Rails S0–S4; boundary all |
| **Dormant signal** | Nodes and links that exist but are not currently changing. | All |
| **Active signal** | Nodes and links appearing or changing in the current stage. | S0–S4 |
| **Threshold warning** | Unrouted stubs, slipped nodes, crowded rail segments, the state readout in S2–S3. | S2–S3 only |
| **Post-transition distinction** | Links and emphasis that exist only under the Field's rules. | S4–S6 only |

Rules:

- **Stage-bound roles.** Threshold warning never appears outside S2–S3.
  Post-transition distinction never appears before S4. Seeing either role
  therefore tells the visitor which regime they are in.
- **Never color alone.** Every color role that carries meaning is paired with a
  non-color cue:

  | Meaning | Non-color cue |
  |---|---|
  | Unrouted relationship | Open-ended stub with a terminal tick mark |
  | Slipped node | Visible offset from its cell center |
  | Active vs dormant | Stroke weight or fill state (filled vs outlined) |
  | Post-transition link | Direct path with no right angles, where every Lattice link had them |
  | Structure | Thin continuous rule, distinct from link weight |

- **Contrast.** Every shipped color scheme meets WCAG 2.2 AA:
  - text: at least 4.5:1 against its background, or 3:1 for large text;
  - graphical elements needed to understand a state (nodes, links, stubs,
    rails, boundary, focus indicators): at least 3:1 against adjacent colors.
- **Schemes.** An implementation may ship a light scheme, a dark scheme, or
  both. Every shipped scheme meets the contrast rules and keeps every role
  distinct.
- **Restraint.** No more than these eight roles. A ninth role requires a recorded
  decision.

## 3. Typography roles

| Role | Used for | Character |
|---|---|---|
| **Display voice** | The SIBurst name (S5), stage names. | Used rarely. It must never appear inside the demonstration system except for the name at S5. |
| **Reading voice** | Captions, state descriptions, reference documents. | Optimized for long-form legibility. |
| **System labels** | Scope prefixes, state labels, the boundary caption. | Uppercase, generously tracked, small but at least the minimum readable size. |
| **Numeric/index labels** | Stage index (S0–S6, 00–06), anchor identifiers. | Tabular figures, so labels do not shift width. |
| **Code/state labels** | File names and the stage index in the reference layer. | Monospace. |

### 3.1 Font strategy

- **System-first.** Every role is set with system font stacks, for example a
  system sans-serif stack for display, reading, and labels, and a system
  monospace stack (`ui-monospace` and equivalents) for code and index labels.
- **No external font services.** No font CDN is loaded.
- A self-hosted typeface may be introduced later only by a recorded decision.
  It must still fall back to the system stack without loss of meaning.

### 3.2 Typography obeys the rule change

Before S4, labels inside the demonstration are **coordinate-bound**: aligned to
the rail rhythm and positioned by the grid. From S4 onward, labels are
**entity-bound**: attached to their node and positioned relative to it. Text
outside the demonstration system (navigation, captions, reference) never
changes behavior between stages.

### 3.3 Minimum sizes

- Reading text is never smaller than the user agent's default size, and captions
  are no smaller than reading text.
- System labels and identifiers are never rendered below a legible minimum
  (about 12 CSS px at 100% zoom), and they scale with user font settings.
- If a viewport cannot fit identifiers at the minimum size, fewer anchors are
  shown (never below three). Labels are not shrunk.

## 4. Density progression

Density is how full the system is. It prepares the transition but never
constitutes it.

| Stage | Density principle |
|---|---|
| S0 | Sparse. Most of the Lattice is empty. Few links. |
| S1 | Entity count and link count rise. The Lattice fills, but everything still fits. |
| S2 | The system approaches the Lattice's representational capacity. Stubs appear. |
| S3 | The Lattice is full. Local failures of representation appear: slipped nodes, detours, overlaps, more stubs. |
| S4 | The representation system changes. Entity count is constant. |
| S5 | The Field grammar stabilizes. Clusters read clearly at the same entity count. |
| S6 | The demonstration recedes in contrast. Readable, navigable access to the doctrine takes priority. |

**Density alone must never represent the SIBurst event.** Increased density,
brightness, contrast, or count may accompany S1–S3. None of them may be the
signal of S4. The signal of S4 is the change of rule defined in
`INTERFACE_CONTRACT.md` §2.3.

## 5. Composition

- The boundary is the only frame. There are no cards, panels, or containers
  around parts of the demonstration.
- The stage navigation and state readout sit outside the boundary, in stable
  positions that do not change between stages.
- Captions sit outside the boundary and never overlap nodes or links.
- In S5, the transition record (a reduced Lattice beside the Field) uses the
  same primitives at a smaller scale. It introduces no new visual elements.
