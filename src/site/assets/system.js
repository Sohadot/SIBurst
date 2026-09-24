// SIBurst demonstration system.
//
// Progressive enhancement over a complete static document. The graph, arrival
// order, clusters, anchors, S3 offsets and Field coordinates all come from
// data/demonstration-fixture.json. This file contains no graph data. It holds
// only the presentation rules already governed by INTERFACE_CONTRACT.md,
// MOTION_SEMANTICS.md and DEMONSTRATION_FIXTURE.md.
//
// Pure functions are exported so they can be tested without a browser.

export const STAGES = ["S0", "S1", "S2", "S3", "S4", "S5", "S6"];

// Indicative progress ranges (INTERFACE_CONTRACT.md §6.2), used unchanged.
export const P_RANGES = [
  [0.0, 0.12], [0.12, 0.3], [0.3, 0.45], [0.45, 0.58], [0.58, 0.74], [0.74, 0.88], [0.88, 1.0],
];

const S4 = 4;
const FIRST_FIELD = 4;
const LAST_ARRIVAL = 3;

// S4 phases (MOTION_SEMANTICS.md M5): rails retire, nodes reposition, links resolve.
export const PHASES = { rails: [0, 0.25], nodes: [0.25, 0.7], links: [0.7, 1] };

// Layout in SVG user units. Portrait rotates lanes onto the x axis
// (DEMONSTRATION_FIXTURE.md §13); the Field is scaled, never recomputed.
export const LAYOUTS = {
  landscape: { name: "landscape", width: 640, height: 440, pad: 40 },
  portrait: { name: "portrait", width: 440, height: 640, pad: 40 },
};

export const clamp = (v, lo = 0, hi = 1) => Math.min(hi, Math.max(lo, v));
const round2 = (v) => Math.round(v * 100) / 100;
const lerp = (a, b, k) => a + (b - a) * k;
const lerpPoint = (a, b, k) => ({ x: lerp(a.x, b.x, k), y: lerp(a.y, b.y, k) });

// Monotonic ease in-out: no overshoot, no bounce.
export const ease = (k) => (k <= 0 ? 0 : k >= 1 ? 1 : k * k * (3 - 2 * k));

export function phase(t, [start, end]) {
  return ease(clamp((t - start) / (end - start)));
}

// --- Progress --------------------------------------------------------------

export function stageIndexAt(p) {
  const q = clamp(p);
  for (let i = 0; i < P_RANGES.length; i += 1) {
    if (q < P_RANGES[i][1]) return i;
  }
  return P_RANGES.length - 1;
}

// Local S4 progress t in [0, 1]. Internal only; never displayed.
export function transitionT(p) {
  const [start, end] = P_RANGES[S4];
  return clamp((p - start) / (end - start));
}

export function progressFromStage(stageIndex, fraction) {
  const [start, end] = P_RANGES[stageIndex];
  return start + clamp(fraction) * (end - start);
}

export function stageIndexFromHash(hash) {
  const match = /^#s([0-6])$/.exec(hash || "");
  return match ? Number(match[1]) : null;
}

// --- Fixture ---------------------------------------------------------------

export function indexFixture(fixture) {
  const fail = (why) => { throw new Error(`fixture not usable: ${why}`); };
  if (!fixture || !Array.isArray(fixture.entities) || !Array.isArray(fixture.relationships)) fail("shape");
  if (!Array.isArray(fixture.stages) || fixture.stages.map((s) => s.id).join() !== STAGES.join()) fail("stages");
  const lattice = fixture.lattice || {};
  const lanes = lattice.lanes;
  const cells = lattice.cells_per_lane;
  if (!(lanes > 0 && cells > 0) || fixture.entities.length !== lanes * cells) fail("lattice");
  const order = Object.fromEntries(STAGES.map((s, i) => [s, i]));
  const byId = new Map();
  for (const e of fixture.entities) {
    const ok = typeof e.id === "string" && e.arrival_stage in order && e.lattice && e.field && e.s3
      && Number.isFinite(e.field.x) && Number.isFinite(e.field.y);
    if (!ok) fail(`entity ${e.id}`);
    byId.set(e.id, {
      id: e.id,
      arrival: order[e.arrival_stage],
      lane: e.lattice.lane,
      cell: e.lattice.cell,
      offsetCell: e.s3.offset_cell,
      offsetLane: e.s3.offset_lane,
      fx: e.field.x,
      fy: e.field.y,
      anchor: e.anchor === true,
    });
  }
  const relationships = fixture.relationships.map((r) => {
    if (!byId.has(r.source) || !byId.has(r.target) || !(r.activation_stage in order)) fail(`relationship ${r.id}`);
    return { id: r.id, source: r.source, target: r.target, activation: order[r.activation_stage] };
  });
  return {
    lanes,
    cells,
    sameLaneMax: lattice.same_lane_max_cell_distance,
    adjacentLaneMax: lattice.adjacent_lane_max_cell_distance,
    entities: [...byId.values()],
    byId,
    relationships,
    labels: fixture.stages.map((s) => s.state_label),
  };
}

export function visibleEntities(model, stageIndex) {
  const s = Math.min(stageIndex, LAST_ARRIVAL);
  return model.entities.filter((e) => e.arrival <= s);
}

export function activeRelationships(model, stageIndex) {
  const s = Math.min(stageIndex, LAST_ARRIVAL);
  return model.relationships.filter((r) => r.activation <= s);
}

// DEC-020 routing law, read from the fixture's lattice parameters.
export function routable(model, a, b) {
  const laneDistance = Math.abs(a.lane - b.lane);
  const cellDistance = Math.abs(a.cell - b.cell);
  if (laneDistance === 0) return cellDistance <= model.sameLaneMax;
  if (laneDistance === 1) return cellDistance <= model.adjacentLaneMax;
  return false;
}

export function stubIds(model, stageIndex) {
  if (stageIndex >= FIRST_FIELD) return [];
  return activeRelationships(model, stageIndex)
    .filter((r) => !routable(model, model.byId.get(r.source), model.byId.get(r.target)))
    .map((r) => r.id);
}

// --- Geometry --------------------------------------------------------------

export function geometry(model, layout) {
  const inner = { w: layout.width - 2 * layout.pad, h: layout.height - 2 * layout.pad };
  const portrait = layout.name === "portrait";
  const cellSpan = (portrait ? inner.h : inner.w) / model.cells;
  const laneSpan = (portrait ? inner.w : inner.h) / model.lanes;
  return { ...layout, inner, portrait, cellSpan, laneSpan };
}

// Map (lane, cell) coordinates, possibly fractional, to user units.
function latticeXY(g, lane, cell) {
  const along = g.pad + cell * g.cellSpan;
  const across = g.pad + lane * g.laneSpan;
  return g.portrait ? { x: across, y: along } : { x: along, y: across };
}

export function latticePoint(g, e, withOffset) {
  const dl = withOffset ? e.offsetLane : 0;
  const dc = withOffset ? e.offsetCell : 0;
  const p = latticeXY(g, e.lane + 0.5 + dl, e.cell + 0.5 + dc);
  return { x: round2(p.x), y: round2(p.y) };
}

export function fieldPoint(g, e) {
  return { x: round2(g.pad + e.fx * g.inner.w), y: round2(g.pad + e.fy * g.inner.h) };
}

export function cellRect(g, e) {
  const a = latticeXY(g, e.lane, e.cell);
  const b = latticeXY(g, e.lane + 1, e.cell + 1);
  return { x0: Math.min(a.x, b.x), y0: Math.min(a.y, b.y), x1: Math.max(a.x, b.x), y1: Math.max(a.y, b.y) };
}

export function rails(g, model) {
  const lines = [];
  for (let lane = 0; lane <= model.lanes; lane += 1) {
    lines.push([latticeXY(g, lane, 0), latticeXY(g, lane, model.cells)]);
  }
  for (let cell = 0; cell <= model.cells; cell += 1) {
    lines.push([latticeXY(g, 0, cell), latticeXY(g, model.lanes, cell)]);
  }
  return lines.map(([a, b]) => ({ x1: round2(a.x), y1: round2(a.y), x2: round2(b.x), y2: round2(b.y) }));
}

// Orthogonal route along a rail: up or down to the rail, along it, then to the
// partner. Same lane: the rail above the lane. Adjacent lanes: the shared rail.
export function orthogonalRoute(g, a, b, pa, pb) {
  const railLane = a.lane === b.lane ? a.lane : Math.max(a.lane, b.lane);
  const rail = latticeXY(g, railLane, 0);
  if (g.portrait) {
    return [pa, { x: rail.x, y: pa.y }, { x: rail.x, y: pb.y }, pb];
  }
  return [pa, { x: pa.x, y: rail.y }, { x: pb.x, y: rail.y }, pb];
}

export function straightRoute(pa, pb) {
  return [pa, lerpPoint(pa, pb, 1 / 3), lerpPoint(pa, pb, 2 / 3), pb];
}

// A stub leaves its source toward the partner and ends at the source cell edge.
export function stubEnd(g, source, ps, pt) {
  const r = cellRect(g, source);
  const dx = pt.x - ps.x;
  const dy = pt.y - ps.y;
  const reach = [];
  if (dx > 0) reach.push((r.x1 - ps.x) / dx);
  if (dx < 0) reach.push((r.x0 - ps.x) / dx);
  if (dy > 0) reach.push((r.y1 - ps.y) / dy);
  if (dy < 0) reach.push((r.y0 - ps.y) / dy);
  const k = Math.min(...reach);
  return { x: round2(ps.x + dx * k), y: round2(ps.y + dy * k) };
}

export function tick(end, from, half = 6) {
  const dx = end.x - from.x;
  const dy = end.y - from.y;
  const len = Math.hypot(dx, dy) || 1;
  const nx = (-dy / len) * half;
  const ny = (dx / len) * half;
  return [{ x: round2(end.x + nx), y: round2(end.y + ny) }, { x: round2(end.x - nx), y: round2(end.y - ny) }];
}

export function pathData(points) {
  return points.map((p, i) => `${i ? "L" : "M"}${round2(p.x)} ${round2(p.y)}`).join(" ");
}

// --- State -----------------------------------------------------------------

// Discrete state for reduced motion: S4 is either "rules in force" or "rules changed".
export function reducedT(t) {
  return t < 0.5 ? 0 : 1;
}

// The complete render state for a given progress. Pure: same inputs, same output.
export function frame(model, g, p, { reduced = false } = {}) {
  const stage = stageIndexAt(p);
  let t = stage < S4 ? 0 : stage > S4 ? 1 : transitionT(p);
  if (reduced && stage === S4) t = reducedT(t);
  const kRails = stage < S4 ? 0 : phase(t, PHASES.rails);
  const kNodes = stage < S4 ? 0 : phase(t, PHASES.nodes);
  const kLinks = stage < S4 ? 0 : phase(t, PHASES.links);
  const offsets = stage >= LAST_ARRIVAL;
  const visible = new Set(visibleEntities(model, stage).map((e) => e.id));

  const pos = new Map();
  for (const e of model.entities) {
    const start = latticePoint(g, e, offsets);
    pos.set(e.id, kNodes > 0 ? lerpPoint(start, fieldPoint(g, e), kNodes) : start);
  }

  const nodes = model.entities.map((e) => ({
    id: e.id,
    x: round2(pos.get(e.id).x),
    y: round2(pos.get(e.id).y),
    visible: visible.has(e.id),
    anchor: e.anchor,
    active: stage <= LAST_ARRIVAL && e.arrival === stage,
  }));

  const active = new Set(activeRelationships(model, stage).map((r) => r.id));
  const links = model.relationships.map((r) => {
    const a = model.byId.get(r.source);
    const b = model.byId.get(r.target);
    const pa = pos.get(a.id);
    const pb = pos.get(b.id);
    const base = { id: r.id, visible: active.has(r.id), fresh: stage <= LAST_ARRIVAL && r.activation === stage };
    if (stage >= FIRST_FIELD && kLinks >= 1) {
      return { ...base, kind: "field", points: straightRoute(pa, pb), tick: null };
    }
    if (routable(model, a, b)) {
      const route = orthogonalRoute(g, a, b, pa, pb);
      const points = kLinks > 0 ? route.map((q, i) => lerpPoint(q, straightRoute(pa, pb)[i], kLinks)) : route;
      return { ...base, kind: stage >= FIRST_FIELD ? "resolving" : "route", points, tick: null };
    }
    // Unroutable: a stub before S4; it extends to its partner as links resolve.
    const s0 = latticePoint(g, a, offsets);
    const e0 = stubEnd(g, a, s0, latticePoint(g, b, offsets));
    const end = { x: pa.x + (e0.x - s0.x), y: pa.y + (e0.y - s0.y) };
    const reach = kLinks > 0 ? lerpPoint(end, pb, kLinks) : end;
    const points = straightRoute(pa, reach);
    return {
      ...base,
      kind: stage >= FIRST_FIELD ? "resolving" : "stub",
      points,
      tick: kLinks < 1 ? { points: tick(reach, pa), opacity: round2(1 - kLinks) } : null,
    };
  });

  return {
    stage,
    stageId: STAGES[stage],
    t,
    regime: stage < S4 ? "lattice" : stage === S4 && kLinks < 1 ? "transition" : stage === 6 ? "after" : "field",
    railOpacity: round2(1 - kRails),
    nodes,
    links,
  };
}

// --- DOM -------------------------------------------------------------------

const SVG_NS = "http://www.w3.org/2000/svg";

function svgEl(name, attrs = {}) {
  const el = document.createElementNS(SVG_NS, name);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, String(v));
  return el;
}

function buildScene(svg, model, g) {
  svg.replaceChildren();
  svg.setAttribute("viewBox", `0 0 ${g.width} ${g.height}`);
  const b = 20;
  svg.append(svgEl("rect", { class: "boundary", x: b, y: b, width: g.width - 2 * b, height: g.height - 2 * b }));
  const railGroup = svgEl("g", { class: "rails" });
  for (const r of rails(g, model)) railGroup.append(svgEl("line", { class: "rail", ...r }));
  const linkGroup = svgEl("g", { class: "links" });
  const links = new Map();
  for (const r of model.relationships) {
    const group = svgEl("g", { class: "relationship", "data-relationship-id": r.id });
    const line = svgEl("path", { class: "link" });
    const mark = svgEl("path", { class: "tick" });
    group.append(line, mark);
    linkGroup.append(group);
    links.set(r.id, { group, line, mark });
  }
  const nodeGroup = svgEl("g", { class: "nodes" });
  const nodes = new Map();
  for (const e of model.entities) {
    const group = svgEl("g", { class: "entity", "data-node-id": e.id, "data-anchor": e.anchor ? "true" : "false" });
    const dot = svgEl("circle", { class: "node", r: 7 });
    group.append(dot);
    let label = null;
    if (e.anchor) {
      label = svgEl("text", { class: "identifier" });
      label.textContent = e.id;
      group.append(label);
    }
    nodeGroup.append(group);
    nodes.set(e.id, { group, dot, label });
  }
  svg.append(railGroup, linkGroup, nodeGroup);
  return { svg, railGroup, links, nodes };
}

function paint(scene, f, labelSize) {
  scene.svg.setAttribute("data-stage", f.stageId);
  scene.svg.setAttribute("data-regime", f.regime);
  scene.railGroup.setAttribute("opacity", f.railOpacity);
  scene.railGroup.setAttribute("display", f.railOpacity > 0 ? "inline" : "none");
  for (const n of f.nodes) {
    const el = scene.nodes.get(n.id);
    el.group.setAttribute("display", n.visible ? "inline" : "none");
    el.group.setAttribute("data-active", n.active ? "true" : "false");
    el.dot.setAttribute("cx", n.x);
    el.dot.setAttribute("cy", n.y);
    if (el.label) {
      el.label.setAttribute("x", round2(n.x + 10));
      el.label.setAttribute("y", round2(n.y - 10));
      el.label.setAttribute("font-size", labelSize);
    }
  }
  for (const l of f.links) {
    const el = scene.links.get(l.id);
    el.group.setAttribute("display", l.visible ? "inline" : "none");
    el.group.setAttribute("data-kind", l.kind);
    el.group.setAttribute("data-fresh", l.fresh ? "true" : "false");
    el.line.setAttribute("d", pathData(l.points));
    if (l.tick) {
      el.mark.setAttribute("d", pathData(l.tick.points));
      el.mark.setAttribute("opacity", l.tick.opacity);
      el.mark.setAttribute("display", "inline");
    } else {
      el.mark.setAttribute("display", "none");
    }
  }
}

function init() {
  const root = document.documentElement;
  const panel = document.getElementById("demonstration");
  const area = panel && panel.querySelector(".figure-area");
  const svg = panel && panel.querySelector("svg.system");
  const readout = document.getElementById("readout");
  const live = document.getElementById("stage-announcer");
  const sections = STAGES.map((s) => document.getElementById(s.toLowerCase()));
  if (!panel || !svg || !readout || !live || sections.some((s) => !s)) return;
  const reducedQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  const portraitQuery = window.matchMedia("(max-width: 767px) and (orientation: portrait)");

  fetch("data/demonstration-fixture.json", { credentials: "same-origin" })
    .then((response) => {
      if (!response.ok) throw new Error(`fixture HTTP ${response.status}`);
      return response.json();
    })
    .then((fixture) => {
      const model = indexFixture(fixture);
      let g = null;
      let scene = null;
      let pending = false;
      let lastStage = -1;
      let lastKey = "";

      const layoutNow = () => {
        g = geometry(model, portraitQuery.matches ? LAYOUTS.portrait : LAYOUTS.landscape);
        if (area) area.setAttribute("data-layout", g.name);
        scene = buildScene(svg, model, g);
        lastKey = "";
      };

      const progress = () => {
        const panelBottom = panel.getBoundingClientRect().bottom;
        const stacked = portraitQuery.matches;
        const ref = stacked ? panelBottom + (window.innerHeight - panelBottom) * 0.4 : window.innerHeight * 0.5;
        let index = 0;
        sections.forEach((s, i) => { if (s.getBoundingClientRect().top <= ref) index = i; });
        const rect = sections[index].getBoundingClientRect();
        return progressFromStage(index, (ref - rect.top) / Math.max(rect.height, 1));
      };

      const render = () => {
        pending = false;
        const p = progress();
        const f = frame(model, g, p, { reduced: reducedQuery.matches });
        const key = `${f.stage}:${f.t.toFixed(4)}:${g.name}`;
        if (key === lastKey) return;
        lastKey = key;
        const scale = svg.getBoundingClientRect().width / g.width || 1;
        paint(scene, f, round2(Math.max(16, 13 / scale)));
        if (f.stage !== lastStage) {
          lastStage = f.stage;
          readout.textContent = `DEMONSTRATION STATE · ${f.stageId} / ${model.labels[f.stage]}`;
          panel.setAttribute("data-stage", f.stageId);
          sections.forEach((s, i) => s.classList.toggle("is-current", i === f.stage));
          document.querySelectorAll("[data-stage-link]").forEach((a) => {
            if (a.getAttribute("data-stage-link") === f.stageId) a.setAttribute("aria-current", "step");
            else a.removeAttribute("aria-current");
          });
          const description = document.getElementById(`${f.stageId.toLowerCase()}-description`);
          live.textContent = description ? description.textContent.trim() : "";
        }
      };

      const request = () => {
        if (!pending) {
          pending = true;
          window.requestAnimationFrame(render);
        }
      };

      const measurePanel = () => {
        root.style.setProperty("--panel-block-size", `${Math.round(panel.getBoundingClientRect().height)}px`);
      };

      layoutNow();
      panel.hidden = false;
      root.classList.add("js-ready");
      measurePanel();
      window.addEventListener("scroll", request, { passive: true });
      window.addEventListener("resize", () => { measurePanel(); request(); }, { passive: true });
      window.addEventListener("hashchange", request);
      portraitQuery.addEventListener("change", () => { layoutNow(); measurePanel(); request(); });
      reducedQuery.addEventListener("change", () => { lastKey = ""; request(); });
      request();
    })
    .catch(() => {
      // The complete static document stays in place.
      root.classList.remove("js-ready");
      panel.hidden = true;
    });
}

if (typeof window !== "undefined" && typeof document !== "undefined") {
  init();
}
