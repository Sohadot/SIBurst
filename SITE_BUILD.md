# Site Build

How the SIBurst static interface is built, checked, and validated. The site is
built for review only. **It is not published** (DEC-024).

## 1. Architecture

```
canonical Markdown (*.md)
canonical fixture (data/demonstration-fixture.json)
site sources (src/site/)
        ↓
tools/build_site.py
        ↓
docs/   (generated; never edited by hand — DEC-022)
```

| Source | Role |
|---|---|
| `src/site/index.template.html` | The main page: seven stage sections, the persistent demonstration panel, and the reference entry. |
| `src/site/reference.template.html` | The shell for each generated reference page. |
| `src/site/reference-index.template.html` | The reference index shell. |
| `src/site/assets/system.css` | The only stylesheet. |
| `src/site/assets/system.js` | The only script: a vanilla JavaScript module. |

| Output in `docs/` | Produced from |
|---|---|
| `index.html` | The template, the canonical fixture (static figures, counts, labels, anchors), and governed copy extracted from the Markdown. |
| `assets/system.css`, `assets/system.js` | Byte copies of `src/site/assets/`. |
| `data/demonstration-fixture.json` | A byte copy of `data/demonstration-fixture.json`. |
| `reference/*.html`, `reference/index.html` | Canonical Markdown rendered by the pinned renderer. |

Flow is one-way. Nothing in `docs/` is ever an input.

## 2. Commands

```
python -m pip install --require-hashes -r requirements-build.txt
python tools/build_site.py                       # build docs/
python tools/build_site.py --check               # fail if docs/ differs from a fresh build
python tools/validate_site.py                    # validate the generated site
python -m http.server 8000 --directory docs      # local preview at http://localhost:8000/
```

Local preview needs no build step and no application server. Opening
`docs/index.html` directly from disk shows the complete static document. The
enhanced demonstration needs HTTP, because browsers block `fetch` on `file:`
URLs, and the static document stays in place when that happens.

## 3. Deterministic build

- Output is UTF-8 with LF line endings and a trailing newline.
- Files and pages are produced in a fixed order.
- No timestamps, machine paths, user names, run identifiers, or random values
  are written.
- The same inputs produce byte-identical output. `--check` rebuilds into a
  temporary directory and reports any missing, extra, or differing file.

## 4. Governed copy

The page does not restate doctrine. The build extracts these exact strings
from the canonical sources, and fails if one cannot be found:

| Copy | Source |
|---|---|
| Tagline and claim-boundary sentence | `README.md` |
| Thesis paragraph | `FOUNDATION_THESIS.md`, "Thesis" |
| Stage captions | `INTERFACE_CONTRACT.md` §5.4 reference captions |
| Scope statement (`SYSTEM DEMONSTRATION — …`) | `INTERFACE_CONTRACT.md` §5.2 |
| Stage names and state labels | `data/demonstration-fixture.json` |
| Entity, relationship, and stub counts; anchor pairs | `data/demonstration-fixture.json` (`derived`, `anchors`) |
| Reference document roles | The document tables in `README.md` |

The accessible state descriptions in the template are implementation copy.
Their counts and anchor names are filled from the fixture.

## 5. Reference generation (DEC-017)

| Item | Value |
|---|---|
| Renderer | `markdown-it-py` |
| Version | 3.0.0, hash-pinned in `requirements-build.txt` |
| Transitive dependency | `mdurl` 0.1.2, hash-pinned |
| License | MIT (both packages) |
| Mode | CommonMark with tables; raw HTML **disabled**; no linkify or typographic replacement |

`markdown-it-py` was selected because:
- it implements CommonMark faithfully;
- it has a single small dependency;
- raw HTML can be switched off completely;
- it is widely used and permissively licensed.

It runs only inside `tools/build_site.py`. **It does not ship to the public
site**, which performs no Markdown conversion at runtime.

Generation rules:

- Wording is never changed. Presentation is: headings get stable `id`
  attributes, and pages share the site header.
- Links to other reference documents are rewritten to their generated pages.
  Links to other repository files point to their canonical source on GitHub.
- Each page names its canonical source file and links to it on GitHub.
- Markdown cannot inject markup or scripts: raw HTML is escaped, and unsafe
  link schemes are refused by the renderer.

## 6. Runtime

**Runtime dependency count: 0.** The public runtime consists of static HTML,
one stylesheet, inline SVG, one vanilla JavaScript module, and the local
fixture.
- There is no framework, library, CDN, font service, analytics, cookie, or
  storage.
- There is no canvas, WebGL, or media.
- The only network request is `data/demonstration-fixture.json`, from the same
  origin.

### Content Security Policy

Set with a `<meta http-equiv>` on every page:

```
default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self';
connect-src 'self'; font-src 'none'; object-src 'none'; frame-src 'none';
base-uri 'none'; form-action 'none'
```

Reference pages use `script-src 'none'` and omit `connect-src`. The pages
contain no inline scripts, `<style>` elements, or `style` attributes. The
script sets geometry through SVG attributes and one CSS custom property through
the CSSOM, both of which the policy allows. `frame-ancestors` cannot be set
through a `<meta>` element; it belongs to the server headers when publishing is
authorized.

### JavaScript architecture (`system.js`)

The script is an ES module (`<script type="module">`). It has two parts.

**Pure functions**, exported and tested in Node without a browser:
- progress to stage, following the §6.2 ranges of `INTERFACE_CONTRACT.md` unchanged;
- the local S4 progress `t`;
- fixture indexing and minimal validation;
- entity visibility and relationship activation;
- stub derivation by the DEC-020 law, read from the fixture's lattice parameters;
- Lattice and Field coordinate transforms;
- route and stub geometry;
- the complete frame for a given progress.

**DOM code:**
- loads the fixture;
- builds one SVG scene with a stable element for every entity and every relationship;
- updates attributes when the visitor scrolls, resizes, follows a fragment
  link, or changes preferences;
- announces stage changes.

The script contains no entity, relationship, cluster, coordinate, or anchor
data. Rendering is event-driven: each event requests at most one
`requestAnimationFrame`. There is no loop, no interval, and no timer, so the
system is still whenever the visitor is.

### Progress

Native scrolling drives progress. The stage sections are sized in proportion to
the contract ranges:

| Stage | Height |
|---|---|
| S0 | 84vh |
| S1 | 126vh |
| S2 | 105vh |
| S3 | 91vh |
| S4 | 112vh |
| S5 | 98vh |
| S6 | 84vh |

The section under a reference line (mid-viewport, or mid-way down the reading
area on narrow screens) gives the stage. The position within it gives `p`
inside that stage's range. The ranges in use are exactly those of
`INTERFACE_CONTRACT.md` §6.2.

There is no scroll-jacking, no wheel handling, and no snapping. Fragments `#s0`
to `#s6` and `#reference` are ordinary anchors and work with and without
JavaScript.

## 7. Demonstration rendering

**Coordinates.** The landscape scene is 640 × 440 SVG units and the portrait
scene is 440 × 640, each with a 40-unit margin.

**Lattice.**
- Positions come only from `lane` and `cell`: cells run along x and lanes
  along y in landscape; in portrait, lanes run along x.
- S3 displacement adds the fixture's `offset_cell` and `offset_lane`, in cell
  units.

**Field.** Fixture coordinates are scaled into the inner area:
- landscape 560 × 360, an aspect ratio of about 1.56;
- portrait 360 × 560, about 0.64.

Both are inside the validated 9:16 to 16:9 range. Nothing is recomputed.

**Routes (routable relationships).** One deterministic orthogonal convention:
- from the source, the route goes perpendicular to the rail direction until it
  meets a rail;
- then along that rail to the partner's cell line;
- then to the partner.

The rail used is the one above the lane for same-lane relationships, and the
rail the two lanes share for adjacent-lane relationships. The same inputs
always give the same path, and nothing moves along a link.

**Stubs (unroutable relationships, S2–S3).**
- A straight segment from the source toward its partner, ending where it meets
  the source cell's edge.
- It ends in a perpendicular tick, so it is distinguishable without colour.
- At S4 the same element extends to the partner.

**S4 phases,** with internal `t` (never displayed):

| `t` range | Phase |
|---|---|
| 0–0.25 | Rails retire (opacity). |
| 0.25–0.70 | The same entity elements move from S3 positions to Field coordinates. |
| 0.70–1 | Routes straighten into direct paths, stubs extend to their partners, and ticks fade. |

Easing is monotonic smoothstep, with no overshoot.

**Reduced motion.**
- Every stage is discrete.
- S4 shows "rules in force" (the S3 state) for the first half of its range and
  "rules changed" (the Field) for the second, with no movement or path morphing
  in between.
- The S5 transition record is always present.

## 8. Progressive enhancement (DEC-023)

The HTML document is complete without JavaScript. It contains, in order, all
seven stages, each with:
- its state label and caption;
- an accessible state description;
- a static figure generated from the fixture (landscape and portrait
  variants). S4 has two explicit frames.

It also contains the S5 transition record with its text equivalent, and the
reference layer.

After the script has loaded and indexed the fixture and built the scene, it
adds `js-ready` to the root element and reveals the persistent panel. CSS then
hides the per-stage figures. If loading or initialization fails, nothing
changes and the static document remains.

When the viewport is shorter than about 30rem (including 400% zoom), the
persistent panel yields to the per-stage figures, so every entity and anchor
stays visible without leaving too little room to read.

## 9. Colour and budgets

The colour roles from `VISUAL_SYSTEM.md` §2, on background `#F3F2EE`. Contrast
is measured by `tools/validate_site.py`.

| Role | Value | Contrast | Minimum |
|---|---|---|---|
| Primary information | `#15171B` | 16.02:1 | 4.5 |
| Secondary information | `#4A4E55` | 7.46:1 | 4.5 |
| Structure (rails, boundary, receded Field) | `#7A7F86` | 3.60:1 | 3.0 |
| Dormant signal | `#545A63` | 6.21:1 | 3.0 |
| Active signal | `#1F4E8C` | 7.42:1 | 3.0 |
| Threshold warning (S2–S3 only) | `#A1420F` | 5.68:1 | 4.5 |
| Post-transition distinction (S4–S6 only) | `#0D6657` | 6.14:1 | 4.5 |
| Focus indicator | `#1F4E8C` | 7.42:1 | 3.0 |

Budgets (`INTERFACE_CONTRACT.md` §8):
- JavaScript at most about 30 KB compressed.
- The first view at most about 150 KB compressed.

`tools/validate_site.py` measures both and fails if either is exceeded.

## 10. Validation

| Command | What it proves |
|---|---|
| `python tools/validate_fixture.py` | Gate 0: the fixture passes every law. |
| `python tools/build_site.py --check` | `docs/` is exactly the build output. |
| `python tools/validate_site.py` | Generation integrity, runtime surface, CSP, structure and links, claim boundary, fixture integration, static fallback, contrast, budgets, and public safety. |
| `python -m unittest discover -s tests` | Fixture and site mutation tests. |
| `node --test tests/site-state.test.mjs` | State, geometry, and interpolation logic, and agreement between static figures and runtime geometry. |

`.github/workflows/site-validation.yml` runs all of these with read-only
permissions. It never deploys.

## 11. Not performed

Sprint 3 does not publish. It adds no GitHub Pages configuration, DNS, or
deployment workflow, and it does not launch the site. Those are a separate
gate (DEC-024).
