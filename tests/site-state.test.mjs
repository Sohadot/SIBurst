// State and geometry tests for src/site/assets/system.js.
// Standard library only: node --test tests/site-state.test.mjs

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const source = readFileSync(join(root, "src/site/assets/system.js"), "utf8");
const sys = await import(`data:text/javascript;base64,${Buffer.from(source).toString("base64")}`);
const fixture = JSON.parse(readFileSync(join(root, "data/demonstration-fixture.json"), "utf8"));
const model = sys.indexFixture(fixture);
const derived = Object.fromEntries(fixture.derived.map((row) => [row.stage, row]));
const landscape = sys.geometry(model, sys.LAYOUTS.landscape);
const portrait = sys.geometry(model, sys.LAYOUTS.portrait);
const mid = (i) => (sys.P_RANGES[i][0] + sys.P_RANGES[i][1]) / 2;

test("stage determination follows the contract ranges", () => {
  assert.equal(sys.stageIndexAt(0), 0);
  assert.equal(sys.stageIndexAt(0.12), 1);
  assert.equal(sys.stageIndexAt(0.5), 3);
  assert.equal(sys.stageIndexAt(0.6), 4);
  assert.equal(sys.stageIndexAt(1), 6);
  assert.equal(sys.stageIndexAt(-1), 0);
  assert.equal(sys.stageIndexAt(2), 6);
  for (let i = 0; i < 7; i += 1) assert.equal(sys.stageIndexAt(mid(i)), i);
});

test("entity visibility per stage matches the fixture arrival schedule", () => {
  for (const [i, s] of ["S0", "S1", "S2", "S3", "S4", "S5", "S6"].entries()) {
    assert.equal(sys.visibleEntities(model, i).length, derived[s].entity_count, s);
  }
});

test("relationship activation per stage matches the fixture", () => {
  for (const [i, s] of ["S0", "S1", "S2", "S3", "S4", "S5", "S6"].entries()) {
    assert.equal(sys.activeRelationships(model, i).length, derived[s].active_relationship_count, s);
  }
});

test("stub sets are derived by the routing law and match the fixture", () => {
  for (const [i, s] of ["S0", "S1", "S2", "S3", "S4", "S5", "S6"].entries()) {
    assert.deepEqual(sys.stubIds(model, i), derived[s].stub_relationship_ids, s);
  }
  const s2 = sys.frame(model, landscape, mid(2));
  assert.equal(s2.links.filter((l) => l.visible && l.kind === "stub").length, 7);
  assert.ok(s2.links.filter((l) => l.kind === "stub").every((l) => l.tick && l.tick.opacity === 1));
});

test("S4 and later create no entity and no relationship", () => {
  const s3 = sys.frame(model, landscape, mid(3));
  for (const p of [0.58, 0.6, 0.66, 0.7, 0.73, mid(5), mid(6)]) {
    const f = sys.frame(model, landscape, p);
    assert.equal(f.nodes.filter((n) => n.visible).length, 24);
    assert.equal(f.links.filter((l) => l.visible).length, s3.links.filter((l) => l.visible).length);
    assert.deepEqual(f.nodes.map((n) => n.id), s3.nodes.map((n) => n.id));
    assert.deepEqual(f.links.map((l) => l.id), s3.links.map((l) => l.id));
  }
});

test("Lattice positions come from lane and cell only, in both orientations", () => {
  for (const e of model.entities) {
    const l = sys.latticePoint(landscape, e, false);
    const cw = landscape.inner.w / model.cells;
    const lh = landscape.inner.h / model.lanes;
    assert.ok(Math.abs(l.x - (40 + (e.cell + 0.5) * cw)) < 0.01);
    assert.ok(Math.abs(l.y - (40 + (e.lane + 0.5) * lh)) < 0.01);
    const p = sys.latticePoint(portrait, e, false);
    assert.ok(Math.abs(p.x - (40 + (e.lane + 0.5) * (portrait.inner.w / model.lanes))) < 0.01, "portrait lanes on x");
    assert.ok(Math.abs(p.y - (40 + (e.cell + 0.5) * (portrait.inner.h / model.cells))) < 0.01, "portrait cells on y");
  }
});

test("Field positions scale the canonical coordinates and are never recomputed", () => {
  for (const g of [landscape, portrait]) {
    for (const e of model.entities) {
      const f = sys.fieldPoint(g, e);
      assert.ok(Math.abs(f.x - (g.pad + e.fx * g.inner.w)) < 0.01);
      assert.ok(Math.abs(f.y - (g.pad + e.fy * g.inner.h)) < 0.01);
    }
  }
});

test("S3 offsets are the fixture values, and only S3 onward uses them", () => {
  const s2 = sys.frame(model, landscape, mid(2));
  const s3 = sys.frame(model, landscape, mid(3));
  for (const e of fixture.entities) {
    const m = model.byId.get(e.id);
    const at3 = s3.nodes.find((n) => n.id === e.id);
    const expected = sys.latticePoint(landscape, { ...m, offsetCell: e.s3.offset_cell, offsetLane: e.s3.offset_lane }, true);
    assert.deepEqual({ x: at3.x, y: at3.y }, expected);
    const at2 = s2.nodes.find((n) => n.id === e.id);
    assert.deepEqual({ x: at2.x, y: at2.y }, sys.latticePoint(landscape, m, false), "S2 nodes stay centred");
  }
});

test("S4 interpolation endpoints: t=0 is the S3 state, t=1 is the Field", () => {
  const [start, end] = sys.P_RANGES[4];
  const s3 = sys.frame(model, landscape, mid(3));
  const t0 = sys.frame(model, landscape, start);
  const t1 = sys.frame(model, landscape, end - 1e-9);
  assert.equal(t0.railOpacity, 1);
  assert.deepEqual(t0.nodes.map((n) => [n.x, n.y]), s3.nodes.map((n) => [n.x, n.y]));
  assert.equal(t1.railOpacity, 0);
  for (const n of t1.nodes) {
    const f = sys.fieldPoint(landscape, model.byId.get(n.id));
    assert.ok(Math.abs(n.x - f.x) < 0.05 && Math.abs(n.y - f.y) < 0.05, n.id);
  }
  const s5 = sys.frame(model, landscape, mid(5));
  assert.ok(s5.links.every((l) => l.kind === "field" && l.tick === null));
});

test("S4 phases run in order: rails retire, entities move, links resolve", () => {
  const at = (t) => sys.frame(model, landscape, sys.progressFromStage(4, t));
  const s3 = sys.frame(model, landscape, mid(3));
  const f20 = at(0.2);
  assert.ok(f20.railOpacity < 1 && f20.railOpacity > 0);
  assert.deepEqual(f20.nodes.map((n) => [n.x, n.y]), s3.nodes.map((n) => [n.x, n.y]), "no movement while rails retire");
  const f50 = at(0.5);
  assert.equal(f50.railOpacity, 0);
  assert.notDeepEqual(f50.nodes.map((n) => [n.x, n.y]), s3.nodes.map((n) => [n.x, n.y]));
  assert.ok(f50.links.filter((l) => l.tick).every((l) => l.tick.opacity === 1), "links not yet resolving");
  const f85 = at(0.85);
  assert.ok(f85.links.some((l) => l.tick && l.tick.opacity < 1), "stubs resolving");
});

test("easing is monotonic and does not overshoot", () => {
  let previous = -1;
  for (let k = -0.2; k <= 1.2; k += 0.01) {
    const v = sys.ease(k);
    assert.ok(v >= 0 && v <= 1);
    assert.ok(v >= previous - 1e-12);
    previous = v;
  }
});

test("reverse traversal returns to exactly the same states", () => {
  const ps = Array.from({ length: 101 }, (_, i) => i / 100);
  const forward = ps.map((p) => JSON.stringify(sys.frame(model, landscape, p)));
  const backward = [...ps].reverse().map((p) => JSON.stringify(sys.frame(model, landscape, p))).reverse();
  assert.deepEqual(forward, backward);
});

test("reduced motion makes S4 discrete: before or after, nothing in between", () => {
  const seen = new Set();
  for (let i = 0; i <= 40; i += 1) {
    const f = sys.frame(model, landscape, sys.progressFromStage(4, i / 40), { reduced: true });
    seen.add(JSON.stringify(f.nodes.map((n) => [n.x, n.y])));
    assert.ok(f.railOpacity === 0 || f.railOpacity === 1);
  }
  assert.equal(seen.size, 2);
  const before = sys.frame(model, landscape, sys.progressFromStage(4, 0.1), { reduced: true });
  const after = sys.frame(model, landscape, sys.progressFromStage(4, 0.9), { reduced: true });
  assert.equal(before.regime, "transition");
  assert.equal(after.regime, "field");
});

test("the same progress always produces the same state", () => {
  for (const p of [0, 0.3, 0.61, 0.66, 0.72, 0.9]) {
    assert.deepEqual(sys.frame(model, landscape, p), sys.frame(model, landscape, p));
  }
});

test("anchors persist, with the same identities, through every stage", () => {
  const anchors = fixture.entities.filter((e) => e.anchor).map((e) => e.id);
  for (let i = 3; i < 7; i += 1) {
    const f = sys.frame(model, landscape, mid(i));
    assert.deepEqual(f.nodes.filter((n) => n.anchor && n.visible).map((n) => n.id), anchors);
  }
});

test("direct fragment loads map to stage indices", () => {
  assert.equal(sys.stageIndexFromHash("#s4"), 4);
  assert.equal(sys.stageIndexFromHash("#s0"), 0);
  assert.equal(sys.stageIndexFromHash("#reference"), null);
  assert.equal(sys.stageIndexFromHash(""), null);
  assert.equal(sys.stageIndexAt(sys.progressFromStage(4, 0.45)), 4);
  assert.equal(sys.stageIndexAt(sys.progressFromStage(6, 1)), 6);
});

test("stubs end on the source cell boundary", () => {
  const f = sys.frame(model, landscape, mid(3));
  for (const l of f.links.filter((x) => x.kind === "stub")) {
    const rel = model.relationships.find((r) => r.id === l.id);
    const rect = sys.cellRect(landscape, model.byId.get(rel.source));
    const end = l.points[3];
    const onEdge = [Math.abs(end.x - rect.x0), Math.abs(end.x - rect.x1), Math.abs(end.y - rect.y0), Math.abs(end.y - rect.y1)]
      .some((d) => d < 0.02);
    assert.ok(onEdge, l.id);
  }
});

test("an unusable fixture is rejected, so the static document stays", () => {
  assert.throws(() => sys.indexFixture({}));
  assert.throws(() => sys.indexFixture({ ...fixture, entities: fixture.entities.slice(1) }));
  assert.throws(() => sys.indexFixture({ ...fixture, stages: fixture.stages.slice(1) }));
});

test("static figures in docs/index.html match the runtime geometry exactly", () => {
  const html = readFileSync(join(root, "docs/index.html"), "utf8");
  const check = (stageIndex, layout, g) => {
    const section = html.match(new RegExp(`<section class="stage" id="s${stageIndex}"[\\s\\S]*?</section>`))[0];
    const svg = section.match(new RegExp(`<svg class="system"[^>]*data-layout="${layout}"[\\s\\S]*?</svg>`))[0];
    const f = sys.frame(model, g, mid(stageIndex));
    for (const n of f.nodes.filter((x) => x.visible)) {
      const m = svg.match(new RegExp(`data-node-id="${n.id}"[^>]*><circle class="node" cx="([\\d.]+)" cy="([\\d.]+)"`));
      assert.ok(m, `${n.id} in static S${stageIndex} ${layout}`);
      assert.ok(Math.abs(Number(m[1]) - n.x) < 0.011 && Math.abs(Number(m[2]) - n.y) < 0.011, `${n.id} S${stageIndex} ${layout}`);
    }
  };
  for (const s of [0, 1, 2, 3, 5]) {
    check(s, "landscape", landscape);
    check(s, "portrait", portrait);
  }
});

test("system.js carries no graph data of its own", () => {
  assert.ok(!/\bN(0[1-9]|1\d|2[0-4])\b/.test(source));
  assert.ok(!/\bR\d{2}\b/.test(source));
  assert.ok(!/Math\.random|setInterval/.test(source));
});
