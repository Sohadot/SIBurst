#!/usr/bin/env python3
"""Build the SIBurst static site into docs/ (DEC-017, DEC-022).

One-way and deterministic:

    canonical Markdown + canonical fixture + src/site templates and assets
        -> tools/build_site.py -> docs/

Usage:
    python tools/build_site.py            # write docs/
    python tools/build_site.py --check    # rebuild to a temporary directory and
                                          # fail if docs/ differs in any byte

Build-time dependency: markdown-it-py (requirements-build.txt). Nothing from
it ships to the public site.
"""

import argparse
import filecmp
import html
import json
import math
import os
import re
import shutil
import sys
import tempfile
from string import Template

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO_ROOT, "src", "site")
OUT = os.path.join(REPO_ROOT, "docs")
FIXTURE = os.path.join(REPO_ROOT, "data", "demonstration-fixture.json")
GITHUB_BLOB = "https://github.com/Sohadot/SIBurst/blob/main/"
SITE_URL = "https://siburst.com/"
SITE_DOMAIN = "siburst.com"
# Metadata description (not announced by screen readers; the page body is unchanged).
META_DESCRIPTION = ("SIBurst names the transition from incremental capability growth into a "
                    "materially different operating regime — a governed conceptual system, "
                    "not a measurement or prediction.")

# Reference pages, in reading order: (group, source file).
REFERENCE_DOCS = [
    ("Conceptual foundation", "FOUNDATION_THESIS.md"),
    ("Conceptual foundation", "NAME_ARCHITECTURE.md"),
    ("Conceptual foundation", "CATEGORY_BOUNDARY.md"),
    ("Conceptual foundation", "COMMERCIAL_TERRITORY.md"),
    ("Conceptual foundation", "GLOSSARY.md"),
    ("Conceptual foundation", "PUBLIC_CLAIM_POLICY.md"),
    ("Conceptual foundation", "SITE_ARCHITECTURE.md"),
    ("Conceptual foundation", "DECISION_LOG.md"),
    ("Implementation doctrine", "INTERFACE_CONTRACT.md"),
    ("Implementation doctrine", "VISUAL_SYSTEM.md"),
    ("Implementation doctrine", "MOTION_SEMANTICS.md"),
    ("Implementation doctrine", "RESPONSIVE_ACCESSIBILITY.md"),
    ("Implementation doctrine", "INTERFACE_ACCEPTANCE.md"),
    ("Implementation doctrine", "DEMONSTRATION_FIXTURE.md"),
    ("Implementation doctrine", "SITE_BUILD.md"),
]
REFERENCE_FILES = [name for _, name in REFERENCE_DOCS]
STAGES = ["S0", "S1", "S2", "S3", "S4", "S5", "S6"]
STAGE_NAMES = {}  # filled from the fixture


class BuildError(Exception):
    pass


# --- Deterministic text helpers ---------------------------------------------

def read_text(path):
    with open(path, "rb") as handle:
        return handle.read().decode("utf-8")


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    with open(path, "wb") as handle:
        handle.write(text.encode("utf-8"))


def copy_bytes(source, target):
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(source, "rb") as src, open(target, "wb") as dst:
        dst.write(src.read())


def slug_for(filename):
    return filename[:-3].lower().replace("_", "-") + ".html"


def heading_slug(text):
    slug = re.sub(r"[^\w\s-]", "", text.lower(), flags=re.UNICODE)
    return re.sub(r"[\s_]+", "-", slug).strip("-") or "section"


def esc(text):
    return html.escape(text, quote=True)


# --- Governed copy extraction (never paraphrased) ----------------------------

def extract_thesis():
    text = read_text(os.path.join(REPO_ROOT, "FOUNDATION_THESIS.md"))
    match = re.search(r"^## Thesis\n\n(.+?)\n\n", text, re.M | re.S)
    if not match:
        raise BuildError("FOUNDATION_THESIS.md: thesis paragraph not found")
    return " ".join(match.group(1).split())


def extract_claim_boundary():
    text = read_text(os.path.join(REPO_ROOT, "README.md"))
    match = re.search(r"^(SIBurst does not assert .+?)\n\n", text, re.M | re.S)
    if not match:
        raise BuildError("README.md: claim boundary sentence not found")
    return " ".join(match.group(1).split())


def extract_contract_copy():
    text = read_text(os.path.join(REPO_ROOT, "INTERFACE_CONTRACT.md"))
    captions = dict(re.findall(r"^\| (S[0-6]) \| (.+?) \| (?:METAPHOR|DEFINITION) \|$", text, re.M))
    if sorted(captions) != STAGES:
        raise BuildError("INTERFACE_CONTRACT.md: reference captions table incomplete")
    scope = re.search(r"`(SYSTEM DEMONSTRATION — [^`]+)`", text)
    if not scope:
        raise BuildError("INTERFACE_CONTRACT.md: boundary caption not found")
    return captions, scope.group(1)


def extract_roles():
    """Document roles come from the README maps, not from new prose."""
    text = read_text(os.path.join(REPO_ROOT, "README.md"))
    roles = {}
    for name, role in re.findall(r"^\| \[([A-Z_]+\.md)\]\([A-Z_]+\.md\) \| (.+?) \|$", text, re.M):
        roles[name] = role
    missing = [name for name in REFERENCE_FILES if name not in roles]
    if missing:
        raise BuildError("README.md: no role listed for %s" % missing)
    return roles


# --- Markdown rendering ------------------------------------------------------

def markdown_renderer():
    try:
        from markdown_it import MarkdownIt
    except ImportError as error:  # pragma: no cover - environment guard
        raise BuildError("markdown-it-py is required: pip install -r requirements-build.txt") from error
    # CommonMark with tables. Raw HTML is disabled: Markdown cannot inject markup.
    return MarkdownIt("commonmark", {"html": False, "linkify": False, "typographer": False}).enable("table")


def rewrite_href(href):
    if re.match(r"^[a-z]+:", href) or href.startswith("#"):
        return href
    path, _, fragment = href.partition("#")
    path = path.lstrip("./")
    if path in REFERENCE_FILES:
        target = slug_for(path)
    elif path:
        target = GITHUB_BLOB + path
    else:
        target = ""
    return target + ("#" + fragment if fragment else "")


def render_markdown(md, text):
    tokens = md.parse(text)
    seen = {}
    title = None
    for i, token in enumerate(tokens):
        if token.type == "heading_open":
            content = tokens[i + 1].content
            if token.tag == "h1" and title is None:
                title = content
            slug = heading_slug(content)
            count = seen.get(slug, 0)
            seen[slug] = count + 1
            token.attrSet("id", slug if count == 0 else "%s-%d" % (slug, count))
        if token.type == "inline" and token.children:
            for child in token.children:
                if child.type == "link_open":
                    child.attrSet("href", rewrite_href(child.attrGet("href") or ""))
    if title is None:
        raise BuildError("document has no H1 title")
    body = md.renderer.render(tokens, md.options, {})
    return title, body


# --- Demonstration geometry (mirrors src/site/assets/system.js) --------------

LAYOUTS = {
    "landscape": {"name": "landscape", "width": 640, "height": 440, "pad": 40},
    "portrait": {"name": "portrait", "width": 440, "height": 640, "pad": 40},
}
PHASES = {"rails": (0.0, 0.25), "nodes": (0.25, 0.7), "links": (0.7, 1.0)}


def round2(v):
    # Matches JavaScript Math.round(v * 100) / 100.
    return math.floor(v * 100 + 0.5) / 100


def fmt(v):
    v = round2(v)
    return ("%.2f" % v).rstrip("0").rstrip(".") if v != int(v) else str(int(v))


def load_model():
    with open(FIXTURE, "rb") as handle:
        fixture = json.loads(handle.read().decode("utf-8"))
    order = {s: i for i, s in enumerate(STAGES)}
    lattice = fixture["lattice"]
    entities = []
    for e in fixture["entities"]:
        entities.append({
            "id": e["id"], "arrival": order[e["arrival_stage"]], "lane": e["lattice"]["lane"],
            "cell": e["lattice"]["cell"], "offset_cell": e["s3"]["offset_cell"],
            "offset_lane": e["s3"]["offset_lane"], "fx": e["field"]["x"], "fy": e["field"]["y"],
            "anchor": e["anchor"],
        })
    by_id = {e["id"]: e for e in entities}
    relationships = [{"id": r["id"], "source": r["source"], "target": r["target"],
                      "activation": order[r["activation_stage"]]} for r in fixture["relationships"]]
    for s in fixture["stages"]:
        STAGE_NAMES[s["id"]] = (s["name"], s["state_label"])
    return {"lanes": lattice["lanes"], "cells": lattice["cells_per_lane"],
            "same": lattice["same_lane_max_cell_distance"], "adjacent": lattice["adjacent_lane_max_cell_distance"],
            "entities": entities, "by_id": by_id, "relationships": relationships}


def geometry(model, layout):
    g = dict(layout)
    g["inner_w"] = layout["width"] - 2 * layout["pad"]
    g["inner_h"] = layout["height"] - 2 * layout["pad"]
    g["portrait"] = layout["name"] == "portrait"
    g["cell_span"] = (g["inner_h"] if g["portrait"] else g["inner_w"]) / model["cells"]
    g["lane_span"] = (g["inner_w"] if g["portrait"] else g["inner_h"]) / model["lanes"]
    return g


def lattice_xy(g, lane, cell):
    along = g["pad"] + cell * g["cell_span"]
    across = g["pad"] + lane * g["lane_span"]
    return (across, along) if g["portrait"] else (along, across)


def lattice_point(g, e, with_offset):
    dl = e["offset_lane"] if with_offset else 0
    dc = e["offset_cell"] if with_offset else 0
    x, y = lattice_xy(g, e["lane"] + 0.5 + dl, e["cell"] + 0.5 + dc)
    return (round2(x), round2(y))


def field_point(g, e):
    return (round2(g["pad"] + e["fx"] * g["inner_w"]), round2(g["pad"] + e["fy"] * g["inner_h"]))


def routable(model, a, b):
    lane_distance, cell_distance = abs(a["lane"] - b["lane"]), abs(a["cell"] - b["cell"])
    if lane_distance == 0:
        return cell_distance <= model["same"]
    if lane_distance == 1:
        return cell_distance <= model["adjacent"]
    return False


def orthogonal_route(g, a, b, pa, pb):
    rail_lane = a["lane"] if a["lane"] == b["lane"] else max(a["lane"], b["lane"])
    rx, ry = lattice_xy(g, rail_lane, 0)
    if g["portrait"]:
        return [pa, (rx, pa[1]), (rx, pb[1]), pb]
    return [pa, (pa[0], ry), (pb[0], ry), pb]


def straight_route(pa, pb):
    return [pa, (pa[0] + (pb[0] - pa[0]) / 3, pa[1] + (pb[1] - pa[1]) / 3),
            (pa[0] + 2 * (pb[0] - pa[0]) / 3, pa[1] + 2 * (pb[1] - pa[1]) / 3), pb]


def stub_end(g, source, ps, pt):
    ax, ay = lattice_xy(g, source["lane"], source["cell"])
    bx, by = lattice_xy(g, source["lane"] + 1, source["cell"] + 1)
    x0, x1, y0, y1 = min(ax, bx), max(ax, bx), min(ay, by), max(ay, by)
    dx, dy = pt[0] - ps[0], pt[1] - ps[1]
    reach = []
    if dx > 0:
        reach.append((x1 - ps[0]) / dx)
    if dx < 0:
        reach.append((x0 - ps[0]) / dx)
    if dy > 0:
        reach.append((y1 - ps[1]) / dy)
    if dy < 0:
        reach.append((y0 - ps[1]) / dy)
    k = min(reach)
    return (round2(ps[0] + dx * k), round2(ps[1] + dy * k))


def tick(end, start, half=6):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy) or 1
    nx, ny = -dy / length * half, dx / length * half
    return [(round2(end[0] + nx), round2(end[1] + ny)), (round2(end[0] - nx), round2(end[1] - ny))]


def path_data(points):
    return " ".join("%s%s %s" % ("L" if i else "M", fmt(x), fmt(y)) for i, (x, y) in enumerate(points))


def static_frame(model, g, stage, field):
    """Canonical static state: a Lattice stage (S0-S3) or the Field (S4 after, S5, S6)."""
    s = min(stage, 3)
    offsets = stage >= 3 and not field
    pos = {e["id"]: (field_point(g, e) if field else lattice_point(g, e, offsets)) for e in model["entities"]}
    nodes = [e for e in model["entities"] if e["arrival"] <= s]
    links = []
    for r in model["relationships"]:
        if r["activation"] > s:
            continue
        a, b = model["by_id"][r["source"]], model["by_id"][r["target"]]
        pa, pb = pos[a["id"]], pos[b["id"]]
        if field:
            links.append((r, "field", [pa, pb], None))
        elif routable(model, a, b):
            links.append((r, "route", orthogonal_route(g, a, b, pa, pb), None))
        else:
            end = stub_end(g, a, pa, pb)
            links.append((r, "stub", [pa, end], tick(end, pa)))
    return pos, nodes, links


def svg_figure(model, layout_name, stage, field, label_size=16, node_r=7, css_class="system"):
    g = geometry(model, LAYOUTS[layout_name])
    pos, nodes, links = static_frame(model, g, stage, field)
    stage_id = STAGES[stage]
    regime = "field" if field else "lattice"
    if stage == 6:
        regime = "after"
    out = ['<svg class="%s" viewBox="0 0 %d %d" data-stage="%s" data-regime="%s" data-layout="%s" '
           'aria-hidden="true" focusable="false">' % (css_class, g["width"], g["height"], stage_id, regime, layout_name)]
    out.append('<rect class="boundary" x="20" y="20" width="%d" height="%d"/>' % (g["width"] - 40, g["height"] - 40))
    if not field:
        out.append('<g class="rails">')
        for lane in range(model["lanes"] + 1):
            (x1, y1), (x2, y2) = lattice_xy(g, lane, 0), lattice_xy(g, lane, model["cells"])
            out.append('<line class="rail" x1="%s" y1="%s" x2="%s" y2="%s"/>' % (fmt(x1), fmt(y1), fmt(x2), fmt(y2)))
        for cell in range(model["cells"] + 1):
            (x1, y1), (x2, y2) = lattice_xy(g, 0, cell), lattice_xy(g, model["lanes"], cell)
            out.append('<line class="rail" x1="%s" y1="%s" x2="%s" y2="%s"/>' % (fmt(x1), fmt(y1), fmt(x2), fmt(y2)))
        out.append("</g>")
    out.append('<g class="links">')
    for r, kind, points, mark in links:
        fresh = "true" if (not field and r["activation"] == stage) else "false"
        item = '<g class="relationship" data-relationship-id="%s" data-kind="%s" data-fresh="%s"><path class="link" d="%s"/>' % (
            r["id"], kind, fresh, path_data(points))
        if mark:
            item += '<path class="tick" d="%s"/>' % path_data(mark)
        out.append(item + "</g>")
    out.append("</g>")
    out.append('<g class="nodes">')
    for e in nodes:
        x, y = pos[e["id"]]
        active = "true" if (not field and e["arrival"] == stage) else "false"
        item = '<g class="entity" data-node-id="%s" data-anchor="%s" data-active="%s"><circle class="node" cx="%s" cy="%s" r="%d"/>' % (
            e["id"], "true" if e["anchor"] else "false", active, fmt(x), fmt(y), node_r)
        if e["anchor"]:
            item += '<text class="identifier" x="%s" y="%s" font-size="%d">%s</text>' % (
                fmt(x + 10), fmt(y - 10), label_size, e["id"])
        out.append(item + "</g>")
    out.append("</g></svg>")
    return "".join(out)


BOUNDARY_NAME = '<p class="boundary-name" aria-hidden="true">SIBurst</p>'


def stage_figure(model, stage, field, boundary_name=False):
    """Static figure in both orientations. At S5 the display name is attached
    to the demonstration boundary (INTERFACE_CONTRACT.md section 4.2)."""
    name = BOUNDARY_NAME if boundary_name else ""
    return ('<div class="orientation landscape" data-layout="landscape">%s%s</div>'
            '<div class="orientation portrait" data-layout="portrait">%s%s</div>' % (
                svg_figure(model, "landscape", stage, field), name,
                svg_figure(model, "portrait", stage, field, label_size=22, node_r=9), name))


# --- Reference Field (DEC-025) ------------------------------------------------
#
# A map of the canonical documents, separate from the demonstration fixture.
# An edge exists only where one canonical source names the other's exact file
# name outside fenced code blocks. Positions come from a deterministic stress
# majorization over shortest-path distances, using only IEEE arithmetic
# (+, -, *, /, sqrt) so every platform produces the same coordinates.

REFERENCE_FIELD_ITERATIONS = 400
REFERENCE_FIELD_LAYOUTS = {
    "landscape": {"width": 960, "height": 600, "pad": 90},
    "portrait": {"width": 440, "height": 760, "pad": 70},
}
FENCE = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.S | re.M)


def strip_fenced_code(text):
    return FENCE.sub("", text)


def names_reference(text, filename):
    return re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(filename), text) is not None


def derive_reference_graph(texts):
    """texts: {filename: markdown}. Returns (directed references, undirected edges)."""
    names = [n for n in REFERENCE_FILES if n in texts]
    directed = []
    for source in names:
        body = strip_fenced_code(texts[source])
        for target in names:
            if target != source and names_reference(body, target):
                directed.append((source, target))
    order = {n: i for i, n in enumerate(names)}
    edges = sorted({tuple(sorted(pair, key=order.get)) for pair in directed}, key=lambda e: (order[e[0]], order[e[1]]))
    return directed, edges


def components(nodes, edges):
    adjacency = {n: [] for n in nodes}
    for a, b in edges:
        adjacency[a].append(b)
        adjacency[b].append(a)
    seen, groups = set(), []
    for n in nodes:
        if n in seen:
            continue
        group, queue = [], [n]
        seen.add(n)
        while queue:
            current = queue.pop(0)
            group.append(current)
            for m in adjacency[current]:
                if m not in seen:
                    seen.add(m)
                    queue.append(m)
        groups.append([x for x in nodes if x in group])
    return groups, adjacency


def stress_layout(nodes, adjacency):
    """Stress majorization on hop distances for one connected component."""
    count = len(nodes)
    if count == 1:
        return {nodes[0]: (0.0, 0.0)}
    index = {n: i for i, n in enumerate(nodes)}
    dist = [[0] * count for _ in range(count)]
    for i, n in enumerate(nodes):
        hops, queue = {n: 0}, [n]
        while queue:
            current = queue.pop(0)
            for m in adjacency[current]:
                if m not in hops:
                    hops[m] = hops[current] + 1
                    queue.append(m)
        for m, h in hops.items():
            dist[i][index[m]] = h
    columns = 4
    pos = [[float(i % columns), float(i // columns)] for i in range(count)]
    for _ in range(REFERENCE_FIELD_ITERATIONS):
        new = []
        for i in range(count):
            sx = sy = sw = 0.0
            for j in range(count):
                if i == j:
                    continue
                dx, dy = pos[i][0] - pos[j][0], pos[i][1] - pos[j][1]
                d = math.sqrt(dx * dx + dy * dy) or 1e-9
                w = 1.0 / (dist[i][j] * dist[i][j])
                sx += w * (pos[j][0] + dist[i][j] * dx / d)
                sy += w * (pos[j][1] + dist[i][j] * dy / d)
                sw += w
            new.append([sx / sw, sy / sw])
        pos = new
    return {n: (pos[i][0], pos[i][1]) for i, n in enumerate(nodes)}


def reference_field_layout(nodes, edges):
    """Normalized coordinates in [0.08, 0.92]. Components sit side by side and are
    never joined; isolated documents keep their own slot."""
    groups, adjacency = components(nodes, edges)
    placed = {}
    slot = 1.0 / len(groups)
    for k, group in enumerate(groups):
        local = stress_layout(group, adjacency)
        xs = [p[0] for p in local.values()]
        ys = [p[1] for p in local.values()]
        span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
        cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
        for n, (x, y) in local.items():
            placed[n] = ((k + 0.5) * slot + (x - cx) / span * 0.84 * slot, 0.5 + (y - cy) / span * 0.84)
    return {n: (round3(placed[n][0]), round3(placed[n][1])) for n in nodes}, groups


def round3(v):
    return math.floor(v * 1000 + 0.5) / 1000


def label_lines(title):
    """A title on one line, or split at the word boundary nearest its middle."""
    words = title.split()
    if len(words) < 2:
        return [[title]]
    best = min(range(1, len(words)), key=lambda k: (abs(len(" ".join(words[:k])) - len(" ".join(words[k:]))), k))
    return [[title], [" ".join(words[:best]), " ".join(words[best:])]]


def place_labels(points, titles, label_size, width, height):
    """Deterministic label placement. Each label, in document order, takes the
    first candidate (single line, then two lines) whose box stays inside the
    boundary and overlaps no placed label and no node; otherwise the candidate
    with the least overlap."""
    char_w = label_size * 0.56
    line_h = label_size * 1.15
    boxes, placed = [], {}
    node_boxes = {k: (x - 7, y - 7, x + 7, y + 7) for k, (x, y) in points.items()}

    def overlap(a, b):
        w = min(a[2], b[2]) - max(a[0], b[0])
        h = min(a[3], b[3]) - max(a[1], b[1])
        return w * h if w > 0 and h > 0 else 0.0

    for name, (x, y) in points.items():
        best = None
        for lines in label_lines(titles[name]):
            w = max(len(line) for line in lines) * char_w
            h = line_h * len(lines)
            candidates = [
                ("start", x + 10, y - h / 2), ("end", x - 10, y - h / 2),
                ("middle", x, y - 10 - h), ("middle", x, y + 10),
                ("start", x + 8, y - 8 - h), ("start", x + 8, y + 8),
                ("end", x - 8, y - 8 - h), ("end", x - 8, y + 8),
            ]
            for anchor, tx, top in candidates:
                left = tx if anchor == "start" else tx - w if anchor == "end" else tx - w / 2
                box = (left, top, left + w, top + h)
                inside = box[0] >= 24 and box[2] <= width - 24 and box[1] >= 24 and box[3] <= height - 24
                cost = sum(overlap(box, b) for b in boxes)
                cost += sum(overlap(box, nb) for k, nb in node_boxes.items() if k != name)
                cost += 0 if inside else 1e6
                if best is None or cost < best[0]:
                    best = (cost, anchor, tx, top, lines, box)
                if cost == 0:
                    break
            if best[0] == 0:
                break
        boxes.append(best[5])
        placed[name] = best[1:5]
    return placed


def reference_field_svg(nodes, edges, coords, titles, layout_name, label_size):
    layout = REFERENCE_FIELD_LAYOUTS[layout_name]
    w, h, pad = layout["width"], layout["height"], layout["pad"]
    iw, ih = w - 2 * pad, h - 2 * pad
    points = {n: (round2(pad + coords[n][0] * iw), round2(pad + coords[n][1] * ih)) for n in nodes}
    labels = place_labels(points, titles, label_size, w, h)
    out = ['<svg class="reference-field-map" viewBox="0 0 %d %d" data-layout="%s" aria-hidden="true" focusable="false">' % (w, h, layout_name)]
    out.append('<rect class="boundary" x="20" y="20" width="%d" height="%d"/>' % (w - 40, h - 40))
    out.append('<g class="reference-links">')
    for a, b in edges:
        (x1, y1), (x2, y2) = points[a], points[b]
        out.append('<path class="reference-link" data-source="%s" data-target="%s" d="M%s %s L%s %s"/>' % (
            a, b, fmt(x1), fmt(y1), fmt(x2), fmt(y2)))
    out.append('</g><g class="reference-nodes">')
    for n in nodes:
        x, y = points[n]
        anchor, tx, top, lines = labels[n]
        spans = "".join('<tspan x="%s" y="%s">%s</tspan>' % (
            fmt(tx), fmt(top + label_size * 0.9 + i * label_size * 1.15), esc(line)) for i, line in enumerate(lines))
        out.append('<g class="reference-node" data-document="%s"><circle cx="%s" cy="%s" r="6"/>'
                   '<text font-size="%d" text-anchor="%s" data-label="%s">%s</text></g>' % (
                       n, fmt(x), fmt(y), label_size, anchor, esc(titles[n]), spans))
    out.append("</g></svg>")
    return "".join(out)


def reference_field(titles):
    texts = {name: read_text(os.path.join(REPO_ROOT, name)) for name in REFERENCE_FILES}
    directed, edges = derive_reference_graph(texts)
    coords, groups = reference_field_layout(REFERENCE_FILES, edges)
    figure = ('<div class="orientation landscape">%s</div><div class="orientation portrait">%s</div>' % (
        reference_field_svg(REFERENCE_FILES, edges, coords, titles, "landscape", 15),
        reference_field_svg(REFERENCE_FILES, edges, coords, titles, "portrait", 15)))
    return figure, edges, groups


# --- Page assembly -----------------------------------------------------------

def stage_readout(stage_id):
    return "DEMONSTRATION STATE · %s / %s" % (stage_id, STAGE_NAMES[stage_id][1])


def reference_list(roles, prefix, edges):
    related = {name: [] for name in REFERENCE_FILES}
    for a, b in edges:
        related[a].append(b)
        related[b].append(a)
    groups = []
    for group in ("Conceptual foundation", "Implementation doctrine"):
        items = []
        for g, name in REFERENCE_DOCS:
            if g != group:
                continue
            linked = [n for n in REFERENCE_FILES if n in related[name]]
            items.append('<li><a href="%s%s">%s</a><span class="role">%s</span>'
                         '<span class="related">Explicit references: %s</span></li>' % (
                             prefix, slug_for(name), esc(name), esc(strip_md(roles[name])),
                             esc(", ".join(linked)) if linked else "none"))
        groups.append('<section class="reference-group" aria-labelledby="%s"><h3 id="%s">%s</h3><ul class="reference-list">%s</ul></section>' % (
            heading_slug(prefix + group), heading_slug(prefix + group), esc(group), "".join(items)))
    return "".join(groups)


def strip_md(text):
    return re.sub(r"`([^`]*)`", r"\1", text)


def anchors_text(model):
    return ", ".join(e["id"] for e in model["entities"] if e["anchor"])


def extract_tagline():
    match = re.search(r"^\*\*(.+?)\*\*$", read_text(os.path.join(REPO_ROOT, "README.md")), re.M)
    if not match:
        raise BuildError("README.md: tagline not found")
    return match.group(1)


def fixture_facts(model):
    """Counts and anchor pairs for the accessible descriptions, taken from the fixture."""
    with open(FIXTURE, "rb") as handle:
        fixture = json.loads(handle.read().decode("utf-8"))
    derived = {row["stage"]: row for row in fixture["derived"]}
    facts = {}
    for s in STAGES:
        facts["entities_" + s.lower()] = str(derived[s]["entity_count"])
        facts["relationships_" + s.lower()] = str(derived[s]["active_relationship_count"])
        facts["stubs_" + s.lower()] = str(len(derived[s]["stub_relationship_ids"]))
    facts["sep_a"], facts["sep_b"] = fixture["anchors"]["separation_pair"]
    facts["con_a"], facts["con_b"] = fixture["anchors"]["convergence_pair"]
    facts["lanes"] = str(model["lanes"])
    facts["cells"] = str(model["cells"])
    return facts


def reference_titles():
    md = markdown_renderer()
    return {name: render_markdown(md, read_text(os.path.join(REPO_ROOT, name)))[0] for name in REFERENCE_FILES}


def build_index(model, roles, target, titles):
    captions, scope = extract_contract_copy()
    field_figure, edges, groups = reference_field(titles)
    values = dict(fixture_facts(model))
    values.update({
        "tagline": esc(extract_tagline()),
        "meta_description": esc(META_DESCRIPTION),
        "site_url": SITE_URL,
        "thesis": esc(extract_thesis()),
        "claim_boundary": esc(extract_claim_boundary()),
        "scope": esc(scope),
        "anchors": esc(anchors_text(model)),
        "reference_list": reference_list(roles, "reference/", edges),
        "reference_field": field_figure,
        "reference_edge_count": str(len(edges)),
        "reference_node_count": str(len(REFERENCE_FILES)),
    })
    for s in STAGES:
        key = s.lower()
        values["caption_" + key] = esc(captions[s])
        values["readout_" + key] = esc(stage_readout(s))
        values["name_" + key] = esc(STAGE_NAMES[s][0])
    values["figure_s0"] = stage_figure(model, 0, False)
    values["figure_s1"] = stage_figure(model, 1, False)
    values["figure_s2"] = stage_figure(model, 2, False)
    values["figure_s3"] = stage_figure(model, 3, False)
    values["figure_s4_before"] = stage_figure(model, 4, False)
    values["figure_s4_after"] = stage_figure(model, 4, True)
    values["figure_s5"] = stage_figure(model, 5, True, boundary_name=True)
    values["figure_s6"] = stage_figure(model, 6, True)
    values["record_lattice"] = svg_figure(model, "landscape", 3, False, label_size=28, node_r=9, css_class="record")
    values["record_field"] = svg_figure(model, "landscape", 5, True, label_size=28, node_r=9, css_class="record")
    template = Template(read_text(os.path.join(SRC, "index.template.html")))
    write_text(os.path.join(target, "index.html"), template.substitute(values))


def build_reference(roles, target, titles):
    md = markdown_renderer()
    template = Template(read_text(os.path.join(SRC, "reference.template.html")))
    for group, name in REFERENCE_DOCS:
        title, body = render_markdown(md, read_text(os.path.join(REPO_ROOT, name)))
        page = template.substitute({
            "page_title": esc("%s · SIBurst reference" % title),
            "description": esc(strip_md(roles[name])),
            "canonical": SITE_URL + "reference/" + slug_for(name),
            "group": esc(group),
            "source_name": esc(name),
            "source_url": GITHUB_BLOB + name,
            "body": body.rstrip("\n"),
            "root": "../",
        })
        write_text(os.path.join(target, "reference", slug_for(name)), page)
    index_template = Template(read_text(os.path.join(SRC, "reference-index.template.html")))
    write_text(os.path.join(target, "reference", "index.html"), index_template.substitute({
        "canonical": SITE_URL + "reference/",
        "reference_list": reference_list(roles, "", reference_field(titles)[1]),
        "claim_boundary": esc(extract_claim_boundary()),
    }))


def build(target):
    if os.path.exists(target):
        shutil.rmtree(target)
    os.makedirs(target)
    model = load_model()
    roles = extract_roles()
    for asset in ("system.css", "system.js"):
        copy_bytes(os.path.join(SRC, "assets", asset), os.path.join(target, "assets", asset))
    copy_bytes(FIXTURE, os.path.join(target, "data", "demonstration-fixture.json"))
    titles = reference_titles()
    build_index(model, roles, target, titles)
    build_reference(roles, target, titles)
    build_publication(target)


def public_urls():
    """Canonical public URLs, in a fixed order. Every page declares the same URL
    as its canonical link; the 404 page is not a public URL."""
    return [SITE_URL, SITE_URL + "reference/"] + [SITE_URL + "reference/" + slug_for(n) for n in REFERENCE_FILES]


def build_publication(target):
    """Publication files for GitHub Pages at the custom domain (PUBLICATION.md)."""
    with open(os.path.join(target, "CNAME"), "wb") as handle:
        handle.write(SITE_DOMAIN.encode("ascii"))
    write_text(os.path.join(target, "robots.txt"),
               "User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n" % SITE_URL)
    entries = "".join("  <url><loc>%s</loc></url>\n" % esc(url) for url in public_urls())
    write_text(os.path.join(target, "sitemap.xml"),
               '<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % entries)
    copy_bytes(os.path.join(SRC, "404.template.html"), os.path.join(target, "404.html"))
    # Serve the validated artifact as built: no Jekyll processing on GitHub Pages.
    with open(os.path.join(target, ".nojekyll"), "wb"):
        pass


def tree_files(root):
    files = []
    for base, dirs, names in os.walk(root):
        dirs.sort()
        for name in sorted(names):
            files.append(os.path.relpath(os.path.join(base, name), root).replace(os.sep, "/"))
    return sorted(files)


def compare_trees(expected, actual):
    """Return human-readable differences between two directories."""
    problems = []
    e_files, a_files = tree_files(expected), tree_files(actual)
    for name in sorted(set(e_files) - set(a_files)):
        problems.append("missing from docs/: %s" % name)
    for name in sorted(set(a_files) - set(e_files)):
        problems.append("not produced by the build: %s" % name)
    for name in sorted(set(e_files) & set(a_files)):
        if not filecmp.cmp(os.path.join(expected, name), os.path.join(actual, name), shallow=False):
            problems.append("differs from build output: %s" % name)
    return problems


def check(target=OUT):
    with tempfile.TemporaryDirectory() as tmp:
        fresh = os.path.join(tmp, "docs")
        build(fresh)
        return compare_trees(fresh, target)


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if docs/ differs from a fresh build")
    parser.add_argument("--out", default=OUT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv[1:])
    try:
        if args.check:
            problems = check(args.out)
            if problems:
                print("BUILD CHECK FAILED: docs/ is not the output of the build")
                for p in problems:
                    print("- " + p)
                return 1
            print("BUILD CHECK PASSED: docs/ matches a fresh build byte for byte")
            return 0
        build(args.out)
        print("Built %d files into %s" % (len(tree_files(args.out)), os.path.relpath(args.out, REPO_ROOT)))
        return 0
    except BuildError as error:
        print("BUILD FAILED: %s" % error)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
