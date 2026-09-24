# Responsive and Accessibility Contract

How the SIBurst interface preserves the thesis across viewports, input methods,
and assistive technology. It is governed by `INTERFACE_CONTRACT.md`. Motion
reduction is specified in `MOTION_SEMANTICS.md` §4 and is not repeated here.

Target: **WCAG 2.2 Level AA.**

## 1. The invariant

On every viewport and with every input method, the visitor experiences the same
seven-stage state machine, the same rule change (Lattice → Field), and the same
continuity of identity. Geometry, proportions, orientation, and layout may
adapt. The entity set and anchor set may not: all 24 canonical entities and all
four anchors of `data/demonstration-fixture.json` appear on every viewport and
at every zoom level. Viewport adaptation changes representation, never fixture
membership. The semantics may not change.

## 2. Viewports

The widths below are indicative. The behavior is normative.

| Viewport | Indicative width | Behavior |
|---|---|---|
| **Wide desktop** | 1440 CSS px and above | The demonstration stays in view on one side; captions and stage navigation sit beside it. All 24 fixture entities. |
| **Laptop** | 1024–1439 | As wide desktop, with proportions reduced. |
| **Tablet** | 768–1023 | The demonstration stays in view in the upper part of the viewport; captions sit below it. Lanes run along the longer axis of the demonstration area. |
| **Mobile** | 360–767 | The demonstration stays in view and fills the width. Lanes run along the long axis of the viewport. Captions sit in a stable band that does not overlap the system. All 24 fixture entities. |
| **Very narrow** | below 360 | As mobile, with all 24 fixture entities and all four anchors. The state readout may wrap onto two lines but keeps its scope prefix. |

### 2.1 Mobile rule

Mobile must not become a simplified marketing landing page. It keeps:

- all seven stages, in order;
- the Lattice with visible rails before S4 and the Field after it;
- stubs in S2–S3 and slipped nodes in S3;
- anchors with identifiers across S4;
- the scoped state readout and the S5 transition record.

What may adapt: the orientation of lanes, the scale and aspect of the
demonstration (within the range validated in `DEMONSTRATION_FIXTURE.md` §13),
and the position of captions. The entities, relationships, and anchors are the
same canonical fixture on every viewport (DEC-018, DEC-019), so saturation
happens in S2 everywhere.

A mobile implementation that shows the stages as ordinary stacked content blocks
(heading, text, image) instead of one persistent system fails. The only
exception is the no-JavaScript fallback in `INTERFACE_CONTRACT.md` §8.1, where
the stacked figures all show the same system.

### 2.2 Orientation rule

S3 INSTABILITY must never make the interface genuinely unusable.
Representational instability is confined to the inside of the demonstration
boundary. Throughout every stage:

- navigation stays in the same place and works the same way;
- focus order is unchanged;
- captions and reference text never move, distort, or misalign;
- controls stay discoverable and visible.

"The system becomes unstable" must never mean "the website becomes inaccessible."

## 3. Accessibility requirements

### 3.1 Semantic structure

The future build uses semantic HTML:

- landmarks for the header, the stage navigation, the main content, and the
  reference layer;
- one heading per stage, in order, and a logical heading hierarchy overall;
- the stage navigation is a list of ordinary links to stage fragments;
- the reference index is a list of ordinary links;
- a "skip to reference" link is the first focusable element.

### 3.2 Keyboard equivalence

- The whole sequence can be traversed using only the keyboard: through the stage
  navigation, through ordinary page scrolling keys, and through fragment links.
- No keyboard trap anywhere.
- Native keyboard scrolling is not overridden.
- Moving to a stage by keyboard produces the same system state as scrolling to it.

### 3.3 Visible focus

- Every focusable element has a clearly visible focus indicator meeting WCAG 2.2
  focus-appearance guidance, with at least 3:1 contrast.
- Focused elements are never hidden behind the demonstration system or the
  caption band.

### 3.4 No color-only distinction

Every meaning carried by color is also carried by shape, weight, position, or
text, as specified in `VISUAL_SYSTEM.md` §2.

### 3.5 Readable text and zoom

- Reading text is never smaller than the user agent's default size.
- Text resizes to 200% without loss of content or function.
- At 400% zoom (a 320 CSS px wide viewport), text content reflows into a single
  column with no two-dimensional scrolling. The demonstration may reflow, scale,
  change orientation, or occupy more vertical space. It keeps all 24 entities
  and all four anchors: no entity or anchor is dropped. Accessibility is
  achieved through layout, never by removing parts of the system.
- Line length in the reference layer stays readable at all widths.

### 3.6 Descriptive state text

The demonstration's meaning is available as text:

- Each stage has a **state description** in the document: one or two
  sentences describing what the demonstration system shows at that stage, for
  example: "Demonstration stage 3 of 7: regime unstable. The lattice can no
  longer route every relationship; several nodes have slipped from their cells."
- When the stage changes, the new state label and description are announced
  once through a polite live region. They are announced only on stage change,
  never continuously.
- Every announced state includes the word "demonstration".

### 3.7 Decorative geometry

- The demonstration system's graphics are hidden from assistive technology
  (`aria-hidden="true"`). Its meaning is carried by the state descriptions,
  which are not hidden.
- Anchor identifiers are graphics and are hidden with the system. Descriptions
  refer to anchors by identifier where it helps, for example "nodes 03 and 11,
  once in the same lane, now sit in different clusters."
- The S5 transition record has a text equivalent describing the before and
  after layouts.

### 3.8 Motion and flashing

- The reduced-motion preference is honored as specified in
  `MOTION_SEMANTICS.md` §4.
- Nothing flashes more than three times per second, at any stage.
- No content moves, blinks, or scrolls automatically.

### 3.9 Screen readers

With a screen reader, the visitor meets, in order: the scope statement that
this is a demonstration, seven stages with headings, labels, captions, and
state descriptions, and then the reference layer. The rule change is stated in
the S4 and S5 descriptions. The sequence is complete without any visual access.

## 4. Without JavaScript

The no-JavaScript document described in `INTERFACE_CONTRACT.md` §8.1 must itself
meet these requirements. It is the baseline the enhanced experience is built on,
not a degraded afterthought.
