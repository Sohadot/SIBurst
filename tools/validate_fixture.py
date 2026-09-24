#!/usr/bin/env python3
"""Validate the canonical SIBurst demonstration fixture.

Every law in DEMONSTRATION_FIXTURE.md is recomputed here from the fixture's
primary data (arrival order, cluster membership, relationships, Field
coordinates). Stored derived values are checked against the recomputation,
never trusted.

Standard library only. Fails closed: exit status 0 only when every invariant
passes.

Usage:
    python tools/validate_fixture.py [path/to/fixture.json]
"""

import json
import math
import os
import re
import sys
from collections import namedtuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FIXTURE = os.path.join(REPO_ROOT, "data", "demonstration-fixture.json")

# --- Normative constants (DEMONSTRATION_FIXTURE.md; DEC-019, DEC-020) -------

SCHEMA_VERSION = "1.0.0"
FIXTURE_ID = "siburst-demonstration-fixture"

STAGES = ["S0", "S1", "S2", "S3", "S4", "S5", "S6"]
STAGE_ORDER = {s: i for i, s in enumerate(STAGES)}
ARRIVAL_STAGES = ["S0", "S1", "S2", "S3"]
ACTIVATION_STAGES = ["S0", "S1", "S2", "S3"]
CUMULATIVE_ENTITIES = {"S0": 3, "S1": 15, "S2": 22, "S3": 24}
FIRST_FIELD_STAGE = "S4"

ENTITY_COUNT = 24
ENTITY_IDS = ["N%02d" % i for i in range(1, ENTITY_COUNT + 1)]
CLUSTER_IDS = ["C1", "C2", "C3", "C4"]
CLUSTER_SIZE = 6
ANCHOR_COUNT = 4
RELATIONSHIP_RANGE = (36, 48)

LANES = 4
CELLS_PER_LANE = 6
SAME_LANE_MAX_CELL_DISTANCE = 2
ADJACENT_LANE_MAX_CELL_DISTANCE = 1

S2_MIN_STUBS = 4
OFFSET_STEP = 0.10
OFFSET_CAP = 0.40
HALF_CELL = 0.5
OFFSET_DECIMALS = 4

MIN_DEGREE = 2
MAX_DEGREE_TO_MEAN = 2.0

FIELD_MARGIN = 0.05
FIELD_MIN_SEPARATION = 0.05
FIELD_MAX_DECIMALS = 3
LINKED_TO_UNLINKED_MAX = 0.80
INTRA_TO_INTER_MAX = 0.80
CLUSTER_MIN_SPREAD = 0.05
CLUSTER_CENTROID_MIN_DISTANCE = 0.25
ASPECTS = [(1.0, 1.0), (1.0, 9.0 / 16.0), (9.0 / 16.0, 1.0)]
ASPECT_MIN_SEPARATION = 0.035

ANCHOR_SEPARATION_MIN_RATIO = 2.0
ANCHOR_CONVERGENCE_MAX_RATIO = 0.5

FORBIDDEN_TOKENS = {
    "score", "scores", "agi", "si", "level", "telemetry", "live", "realtime",
    "timestamp", "time", "date", "prediction", "predicted", "forecast",
    "probability", "random", "seed", "generated", "capability", "intelligence",
    "status", "measurement",
}
LABEL_KEYS = {"id", "name", "state_label", "fixture_id"}

TOP_LEVEL_KEYS = [
    "schema_version", "fixture_id", "description", "scope", "lattice",
    "stages", "clusters", "entities", "relationships", "field", "anchors",
    "derived",
]

Failure = namedtuple("Failure", "invariant subject expected actual")


class FixtureError(Exception):
    """Raised when structural failures prevent semantic validation."""


# Structural failures after which semantic checks cannot run meaningfully.
# Other failures (ordering, counts, duplicates) are reported and validation
# continues, so every broken invariant is visible in one run.
FATAL_INVARIANTS = {
    "structure.top_level", "structure.entities", "structure.entity_count", "structure.entity_ids",
    "structure.entity_fields", "structure.relationships", "structure.relationship_fields",
    "structure.endpoints", "structure.stages", "structure.clusters",
}


# --- Geometry and graph helpers ---------------------------------------------

def lattice_position(arrival_index):
    """The placement law: position is determined by arrival order alone."""
    return arrival_index // CELLS_PER_LANE, arrival_index % CELLS_PER_LANE


def lattice_routable(a, b):
    """The routing law (DEC-020). a and b are (lane, cell) pairs."""
    lane_distance = abs(a[0] - b[0])
    cell_distance = abs(a[1] - b[1])
    if lane_distance == 0:
        return cell_distance <= SAME_LANE_MAX_CELL_DISTANCE
    if lane_distance == 1:
        return cell_distance <= ADJACENT_LANE_MAX_CELL_DISTANCE
    return False


def lattice_normalized(lane, cell):
    """Cell centre in the normalized unit square used for comparisons."""
    return (cell + 0.5) / CELLS_PER_LANE, (lane + 0.5) / LANES


def distance(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def stage_leq(a, b):
    return STAGE_ORDER[a] <= STAGE_ORDER[b]


def connected(nodes, edges):
    nodes = sorted(nodes)
    if not nodes:
        return True
    adjacency = {n: set() for n in nodes}
    for a, b in edges:
        if a in adjacency and b in adjacency:
            adjacency[a].add(b)
            adjacency[b].add(a)
    seen = {nodes[0]}
    queue = [nodes[0]]
    while queue:
        current = queue.pop()
        for neighbour in sorted(adjacency[current]):
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append(neighbour)
    return len(seen) == len(nodes)


def s3_offset(entity_id, own, partners):
    """The S3 pressure/offset law.

    own is the node's (lane, cell); partners are the (lane, cell) positions of
    the other endpoints of its active unroutable relationships at S3.
    Returns (pressure, offset_cell, offset_lane) in logical cell units.
    """
    pressure = len(partners)
    if pressure == 0:
        return 0, 0.0, 0.0
    v_cell = sum(p[1] - own[1] for p in partners) / pressure
    v_lane = sum(p[0] - own[0] for p in partners) / pressure
    length = math.hypot(v_cell, v_lane)
    if length == 0:
        axis = int(entity_id[1:]) % 4
        v_cell, v_lane = [(1, 0), (0, 1), (-1, 0), (0, -1)][axis]
        length = 1.0
    magnitude = min(OFFSET_CAP, OFFSET_STEP * pressure)
    return pressure, _truncate(magnitude * v_cell / length), _truncate(magnitude * v_lane / length)


def _truncate(value):
    """Truncate toward zero to OFFSET_DECIMALS places, so rounding never
    pushes an offset past the cap. The inner round removes float noise."""
    scale = 10 ** OFFSET_DECIMALS
    return math.trunc(round(value * scale, 6)) / scale + 0.0


# --- Loading ----------------------------------------------------------------

def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key in JSON object: %r" % key)
        result[key] = value
    return result


def canonical_serialization(fixture):
    """The canonical byte form: UTF-8, 2-space indent, LF, trailing newline."""
    return (json.dumps(fixture, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def load_fixture(path):
    with open(path, "rb") as handle:
        raw = handle.read()
    text = raw.decode("utf-8")
    fixture = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    return raw, fixture


# --- Validation -------------------------------------------------------------

class Validator:
    def __init__(self, fixture):
        self.fixture = fixture
        self.failures = []

    def fail(self, invariant, subject, expected, actual):
        self.failures.append(Failure(invariant, str(subject), str(expected), str(actual)))

    def check(self, condition, invariant, subject, expected, actual):
        if not condition:
            self.fail(invariant, subject, expected, actual)
        return condition

    # Structural ---------------------------------------------------------

    def structure(self):
        f = self.fixture
        if not isinstance(f, dict):
            self.fail("structure.top_level", "fixture", "JSON object", type(f).__name__)
            raise FixtureError
        missing = [k for k in TOP_LEVEL_KEYS if k not in f]
        extra = [k for k in f if k not in TOP_LEVEL_KEYS]
        self.check(not missing, "structure.top_level", "fixture", "keys present: %s" % TOP_LEVEL_KEYS, "missing %s" % missing)
        self.check(not extra, "structure.top_level", "fixture", "no unknown top-level keys", "unknown %s" % extra)
        if missing:
            raise FixtureError
        self.check(f["schema_version"] == SCHEMA_VERSION, "structure.schema_version", "schema_version", SCHEMA_VERSION, f["schema_version"])
        self.check(f["fixture_id"] == FIXTURE_ID, "structure.fixture_id", "fixture_id", FIXTURE_ID, f["fixture_id"])

        lattice = f["lattice"]
        expected_lattice = {
            "lanes": LANES,
            "cells_per_lane": CELLS_PER_LANE,
            "same_lane_max_cell_distance": SAME_LANE_MAX_CELL_DISTANCE,
            "adjacent_lane_max_cell_distance": ADJACENT_LANE_MAX_CELL_DISTANCE,
            "s3_offset_step": OFFSET_STEP,
            "s3_offset_cap": OFFSET_CAP,
        }
        for key, value in expected_lattice.items():
            self.check(isinstance(lattice, dict) and lattice.get(key) == value, "lattice.parameters", "lattice.%s" % key, value,
                       lattice.get(key) if isinstance(lattice, dict) else lattice)

        stages = f["stages"]
        ids = [s.get("id") for s in stages] if isinstance(stages, list) else None
        self.check(ids == STAGES, "structure.stages", "stages", STAGES, ids)

        clusters = f["clusters"]
        cluster_ids = [c.get("id") for c in clusters] if isinstance(clusters, list) else None
        self.check(cluster_ids == CLUSTER_IDS, "structure.clusters", "clusters", CLUSTER_IDS, cluster_ids)

        entities = f["entities"]
        if not isinstance(entities, list) or not all(isinstance(e, dict) for e in entities):
            self.fail("structure.entities", "entities", "list of objects", type(entities).__name__)
            raise FixtureError
        entity_ids = [e.get("id") for e in entities]
        self.check(len(entities) == ENTITY_COUNT, "structure.entity_count", "entities", ENTITY_COUNT, len(entities))
        duplicates = sorted({i for i in entity_ids if entity_ids.count(i) > 1}, key=str)
        self.check(not duplicates, "structure.entity_ids", "entities", "each of N01-N24 exactly once", "duplicates %s" % duplicates)
        self.check(sorted(entity_ids, key=str) == ENTITY_IDS, "structure.entity_ids", "entities", "ids N01-N24", sorted(entity_ids, key=str))
        required = ["id", "arrival_index", "arrival_stage", "cluster_id", "anchor", "lattice", "s3", "field"]
        for e in entities:
            missing = [k for k in required if k not in e]
            self.check(not missing, "structure.entity_fields", e.get("id"), "fields %s" % required, "missing %s" % missing)
            if missing:
                raise FixtureError
            ok = (isinstance(e["lattice"], dict) and isinstance(e["field"], dict) and isinstance(e["s3"], dict)
                  and isinstance(e["arrival_index"], int) and isinstance(e["anchor"], bool))
            self.check(ok, "structure.entity_fields", e["id"], "typed lattice/field/s3/arrival_index/anchor", "malformed")
            if not ok:
                raise FixtureError
        indices = [e["arrival_index"] for e in entities]
        self.check(indices == list(range(ENTITY_COUNT)), "structure.entity_order", "entities",
                   "ordered by arrival_index 0-23", indices)
        self.check(entity_ids == ENTITY_IDS, "structure.entity_order", "entities",
                   "entity N(k) has arrival_index k-1", entity_ids)

        relationships = f["relationships"]
        if not isinstance(relationships, list) or not all(isinstance(r, dict) for r in relationships):
            self.fail("structure.relationships", "relationships", "list of objects", type(relationships).__name__)
            raise FixtureError
        rel_ids = [r.get("id") for r in relationships]
        dup_rel = sorted({i for i in rel_ids if rel_ids.count(i) > 1}, key=str)
        self.check(not dup_rel, "structure.relationship_ids", "relationships", "unique relationship ids", "duplicates %s" % dup_rel)
        self.check(RELATIONSHIP_RANGE[0] <= len(relationships) <= RELATIONSHIP_RANGE[1], "structure.relationship_count",
                   "relationships", "%d-%d" % RELATIONSHIP_RANGE, len(relationships))
        known = set(ENTITY_IDS)
        pairs = {}
        for r in relationships:
            missing = [k for k in ("id", "source", "target", "activation_stage") if k not in r]
            if not self.check(not missing, "structure.relationship_fields", r.get("id"), "id/source/target/activation_stage",
                              "missing %s" % missing):
                raise FixtureError
            valid_endpoints = r["source"] in known and r["target"] in known
            self.check(valid_endpoints, "structure.endpoints", r["id"], "endpoints in N01-N24", (r["source"], r["target"]))
            self.check(r["source"] != r["target"], "structure.self_link", r["id"], "distinct endpoints", (r["source"], r["target"]))
            key = tuple(sorted((str(r["source"]), str(r["target"]))))
            if key in pairs:
                self.fail("structure.duplicate_relationship", r["id"], "one relationship per pair",
                          "duplicates %s %s" % (pairs[key], key))
            pairs[key] = r["id"]
        expected_ids = ["R%02d" % i for i in range(1, len(relationships) + 1)]
        self.check(rel_ids == expected_ids, "structure.relationship_order", "relationships",
                   "ids R01..R%02d in list order" % len(relationships), rel_ids)
        if any(f.invariant in FATAL_INVARIANTS for f in self.failures):
            raise FixtureError

    # Surface / claim boundary -------------------------------------------

    def surface(self):
        def tokens(text):
            spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", str(text))
            return {t for t in re.split(r"[^a-z0-9]+", spaced.lower()) if t}

        def walk(node, path):
            if isinstance(node, dict):
                for key, value in node.items():
                    hit = tokens(key) & FORBIDDEN_TOKENS
                    self.check(not hit, "surface.forbidden_key", "%s.%s" % (path, key),
                               "no score/telemetry/prediction/randomness/time keys", "forbidden token(s) %s" % sorted(hit))
                    if key in LABEL_KEYS and isinstance(value, str):
                        hit = tokens(value) & FORBIDDEN_TOKENS
                        self.check(not hit, "surface.forbidden_label", "%s.%s" % (path, key),
                                   "no telemetry-style labels", "%r contains %s" % (value, sorted(hit)))
                    walk(value, "%s.%s" % (path, key))
            elif isinstance(node, list):
                for i, item in enumerate(node):
                    walk(item, "%s[%d]" % (path, i))

        walk(self.fixture, "fixture")

    # Semantic -----------------------------------------------------------

    def semantic(self):
        f = self.fixture
        entities = f["entities"]
        by_id = {e["id"]: e for e in entities}
        self.by_id = by_id
        pos = {}

        # Arrival
        invalid = [e["id"] for e in entities if e["arrival_stage"] not in ARRIVAL_STAGES]
        for n in invalid:
            self.fail("arrival.stage", n, "arrival stage in %s" % ARRIVAL_STAGES, by_id[n]["arrival_stage"])
        if any(by_id[n]["arrival_stage"] not in STAGE_ORDER for n in invalid):
            raise FixtureError
        for stage in ARRIVAL_STAGES:
            count = sum(1 for e in entities if e["arrival_stage"] in STAGE_ORDER
                        and stage_leq(e["arrival_stage"], stage))
            self.check(count == CUMULATIVE_ENTITIES[stage], "arrival.cumulative", stage,
                       "%d entities by %s" % (CUMULATIVE_ENTITIES[stage], stage), count)
        for e in entities:
            i = e["arrival_index"]
            expected = next(s for s in ARRIVAL_STAGES if i < CUMULATIVE_ENTITIES[s])
            self.check(e["arrival_stage"] == expected, "arrival.schedule", e["id"],
                       "arrival index %d arrives at %s" % (i, expected), e["arrival_stage"])

        # Lattice placement law
        cells_seen = {}
        for e in entities:
            lane, cell = e["lattice"].get("lane"), e["lattice"].get("cell")
            expected = lattice_position(e["arrival_index"])
            self.check((lane, cell) == expected, "lattice.placement_law", e["id"],
                       "lane=floor(i/6), cell=i mod 6 -> %s" % (expected,), (lane, cell))
            valid = isinstance(lane, int) and isinstance(cell, int) and 0 <= lane < LANES and 0 <= cell < CELLS_PER_LANE
            self.check(valid, "lattice.bounds", e["id"], "lane 0-3, cell 0-5", (lane, cell))
            if (lane, cell) in cells_seen:
                self.fail("lattice.duplicate_cell", e["id"], "one entity per cell", "shares %s with %s" % ((lane, cell), cells_seen[(lane, cell)]))
            cells_seen[(lane, cell)] = e["id"]
            pos[e["id"]] = expected
        self.check(len(cells_seen) == LANES * CELLS_PER_LANE, "lattice.cells", "lattice",
                   "%d occupied cells at S3" % (LANES * CELLS_PER_LANE), len(cells_seen))
        self.pos = pos

        # Clusters
        membership = {}
        for c in f["clusters"]:
            members = c.get("members", [])
            self.check(len(members) == CLUSTER_SIZE, "clusters.size", c.get("id"), CLUSTER_SIZE, len(members))
            for m in members:
                if m in membership:
                    self.fail("clusters.membership", m, "exactly one cluster", "in %s and %s" % (membership[m], c.get("id")))
                membership[m] = c.get("id")
        for e in entities:
            self.check(membership.get(e["id"]) == e["cluster_id"], "clusters.membership", e["id"],
                       "cluster_id matches clusters list (%s)" % membership.get(e["id"]), e["cluster_id"])
        self.cluster = {e["id"]: e["cluster_id"] for e in entities}

        # Relationship lifecycle
        edges = []
        for r in f["relationships"]:
            stage = r["activation_stage"]
            if not self.check(stage in ACTIVATION_STAGES, "lifecycle.post_s3", r["id"],
                              "activation stage in S0-S3 (S4 creates no relationships)", stage):
                continue
            a, b = by_id[r["source"]], by_id[r["target"]]
            latest = max(a["arrival_stage"], b["arrival_stage"], key=lambda s: STAGE_ORDER.get(s, 99))
            if latest in STAGE_ORDER:
                self.check(stage_leq(latest, stage), "lifecycle.before_endpoint", r["id"],
                           "activation >= endpoint arrival (%s)" % latest, stage)
            self.check(a["arrival_index"] < b["arrival_index"], "structure.relationship_orientation", r["id"],
                       "source arrives before target", (r["source"], r["target"]))
            if r["source"] != r["target"]:
                edges.append((r["id"], r["source"], r["target"], stage))
        order_keys = [(STAGE_ORDER[s], by_id[x]["arrival_index"], by_id[y]["arrival_index"]) for _, x, y, s in edges]
        self.check(order_keys == sorted(order_keys), "structure.relationship_order", "relationships",
                   "sorted by (activation stage, source index, target index)", "unsorted")
        self.edges = edges

        self.routability()
        self.graph()
        self.instability()
        self.field()
        self.anchors()
        self.derived()

    def active(self, stage):
        s = min(STAGE_ORDER[stage], STAGE_ORDER["S3"])
        return [e for e in self.edges if STAGE_ORDER[e[3]] <= s]

    def stubs(self, stage):
        if not STAGE_ORDER[stage] < STAGE_ORDER[FIRST_FIELD_STAGE]:
            return []
        return [e for e in self.active(stage) if not lattice_routable(self.pos[e[1]], self.pos[e[2]])]

    def routability(self):
        counts = {s: len(self.stubs(s)) for s in ARRIVAL_STAGES}
        for s in ("S0", "S1"):
            offenders = [e[0] for e in self.stubs(s)]
            self.check(not offenders, "routability.%s" % s.lower(), s,
                       "every active relationship routable (more of the same)", "unroutable %s" % offenders)
        self.check(counts["S2"] >= S2_MIN_STUBS, "routability.s2_minimum", "S2",
                   ">= %d unroutable relationships" % S2_MIN_STUBS, counts["S2"])
        self.check(counts["S3"] > counts["S2"], "routability.s3_growth", "S3",
                   "more unroutable than S2 (%d)" % counts["S2"], counts["S3"])
        share = {s: (counts[s] / len(self.active(s)) if self.active(s) else 0.0) for s in ("S2", "S3")}
        self.check(share["S3"] > share["S2"], "routability.s3_share", "S3",
                   "unroutable share above S2 (%.3f)" % share["S2"], "%.3f" % share["S3"])
        for s in ("S1", "S2", "S3"):
            prev = STAGES[STAGE_ORDER[s] - 1]
            self.check(len(self.active(s)) > len(self.active(prev)), "routability.accumulation", s,
                       "more active relationships than %s" % prev, len(self.active(s)))

    def graph(self):
        pairs = [(a, b) for _, a, b, _ in self.edges]
        self.check(connected(ENTITY_IDS, pairs), "connectivity.graph", "S3", "graph connected", "disconnected")
        degree = {n: 0 for n in ENTITY_IDS}
        for a, b in pairs:
            degree[a] += 1
            degree[b] += 1
        for n in ENTITY_IDS:
            self.check(degree[n] >= MIN_DEGREE, "connectivity.degree", n, ">= %d" % MIN_DEGREE, degree[n])
        mean = sum(degree.values()) / len(degree)
        self.check(max(degree.values()) <= MAX_DEGREE_TO_MEAN * mean, "connectivity.hub", "graph",
                   "max degree <= %.1f x mean (%.2f)" % (MAX_DEGREE_TO_MEAN, mean), max(degree.values()))
        intra = [p for p in pairs if self.cluster[p[0]] == self.cluster[p[1]]]
        inter = [p for p in pairs if self.cluster[p[0]] != self.cluster[p[1]]]
        self.check(len(intra) > len(inter), "clusters.intra_vs_inter", "graph",
                   "intra-cluster edges > inter-cluster edges", "%d vs %d" % (len(intra), len(inter)))
        for c in CLUSTER_IDS:
            members = [n for n in ENTITY_IDS if self.cluster[n] == c]
            internal = [p for p in intra if self.cluster[p[0]] == c]
            self.check(connected(members, internal), "clusters.internal_connectivity", c,
                       "cluster connected by its own relationships", "disconnected")
            internal_degree = {m: 0 for m in members}
            for a, b in internal:
                internal_degree[a] += 1
                internal_degree[b] += 1
            low = [m for m in members if internal_degree[m] < MIN_DEGREE]
            self.check(not low, "clusters.internal_degree", c,
                       "every member has >= %d intra-cluster relationships" % MIN_DEGREE, "below: %s" % low)
        self.degree = degree
        self.intra, self.inter = intra, inter

    def instability(self):
        stubs = self.stubs("S3")
        partners = {n: [] for n in ENTITY_IDS}
        for _, a, b, _ in stubs:
            partners[a].append(self.pos[b])
            partners[b].append(self.pos[a])
        displaced = 0
        for n in ENTITY_IDS:
            stored = self.by_id[n]["s3"]
            pressure, dc, dl = s3_offset(n, self.pos[n], partners[n])
            expected = {"pressure": pressure, "offset_cell": dc, "offset_lane": dl}
            actual = {k: stored.get(k) for k in expected}
            self.check(actual == expected, "instability.offset_law", n, expected, actual)
            if pressure == 0:
                self.check(stored.get("offset_cell") == 0 and stored.get("offset_lane") == 0, "instability.centered", n,
                           "zero-pressure node centred", actual)
            else:
                displaced += 1
            oc, ol = stored.get("offset_cell", 0) or 0, stored.get("offset_lane", 0) or 0
            self.check(abs(oc) <= HALF_CELL and abs(ol) <= HALF_CELL and math.hypot(oc, ol) <= HALF_CELL,
                       "instability.half_cell", n, "offset within half a cell", (oc, ol))
        self.check(displaced >= S2_MIN_STUBS, "instability.pressure", "S3",
                   ">= %d displaced nodes" % S2_MIN_STUBS, displaced)

    def field(self):
        coords = {}
        for n in ENTITY_IDS:
            fxy = self.by_id[n]["field"]
            x, y = fxy.get("x"), fxy.get("y")
            ok = all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (x, y))
            if not self.check(ok, "field.coordinates", n, "numeric x and y", (x, y)):
                continue
            self.check(FIELD_MARGIN <= x <= 1 - FIELD_MARGIN and FIELD_MARGIN <= y <= 1 - FIELD_MARGIN,
                       "field.bounds", n, "x,y in [%.2f, %.2f]" % (FIELD_MARGIN, 1 - FIELD_MARGIN), (x, y))
            self.check(round(x, FIELD_MAX_DECIMALS) == x and round(y, FIELD_MAX_DECIMALS) == y, "field.precision", n,
                       "at most %d decimals" % FIELD_MAX_DECIMALS, (x, y))
            coords[n] = (x, y)
        if len(coords) != ENTITY_COUNT:
            return
        seen = {}
        for n, p in coords.items():
            if p in seen:
                self.fail("field.duplicate_coordinate", n, "unique coordinates", "same as %s %s" % (seen[p], p))
            seen[p] = n
        ids = ENTITY_IDS
        all_pairs = [(ids[i], ids[j]) for i in range(len(ids)) for j in range(i + 1, len(ids))]
        linked = {tuple(sorted((a, b))) for _, a, b, _ in self.edges}
        for w, h in ASPECTS:
            scaled = {n: (p[0] * w, p[1] * h) for n, p in coords.items()}
            d = {pair: distance(scaled[pair[0]], scaled[pair[1]]) for pair in all_pairs}
            minimum = min(d.values())
            limit = FIELD_MIN_SEPARATION if (w, h) == (1.0, 1.0) else ASPECT_MIN_SEPARATION
            self.check(minimum >= limit, "field.min_separation", "aspect %.3f:%.3f" % (w, h),
                       ">= %.3f" % limit, "%.4f" % minimum)
            link_mean = sum(d[p] for p in all_pairs if p in linked) / len(linked)
            unlinked = [d[p] for p in all_pairs if p not in linked]
            unlink_mean = sum(unlinked) / len(unlinked)
            ratio = link_mean / unlink_mean
            self.check(ratio <= LINKED_TO_UNLINKED_MAX, "field.linked_vs_unlinked", "aspect %.3f:%.3f" % (w, h),
                       "mean linked <= %.2f x mean unlinked" % LINKED_TO_UNLINKED_MAX,
                       "%.4f / %.4f = %.3f" % (link_mean, unlink_mean, ratio))
            if (w, h) == (1.0, 1.0):
                self.metrics = {"mean_linked": link_mean, "mean_unlinked": unlink_mean, "ratio": ratio,
                                "min_separation": minimum}
        d = {pair: distance(coords[pair[0]], coords[pair[1]]) for pair in all_pairs}
        intra = [d[p] for p in all_pairs if self.cluster[p[0]] == self.cluster[p[1]]]
        inter = [d[p] for p in all_pairs if self.cluster[p[0]] != self.cluster[p[1]]]
        intra_mean, inter_mean = sum(intra) / len(intra), sum(inter) / len(inter)
        self.check(intra_mean <= INTRA_TO_INTER_MAX * inter_mean, "field.cluster_distance", "field",
                   "mean intra-cluster <= %.2f x mean inter-cluster" % INTRA_TO_INTER_MAX,
                   "%.4f vs %.4f" % (intra_mean, inter_mean))
        centroid = {}
        for c in CLUSTER_IDS:
            members = [coords[n] for n in ids if self.cluster[n] == c]
            centroid[c] = (sum(p[0] for p in members) / len(members), sum(p[1] for p in members) / len(members))
            spread = sum(distance(p, centroid[c]) for p in members) / len(members)
            self.check(spread >= CLUSTER_MIN_SPREAD, "field.cluster_collapse", c,
                       "mean distance to centroid >= %.2f" % CLUSTER_MIN_SPREAD, "%.4f" % spread)
        for i, a in enumerate(CLUSTER_IDS):
            for b in CLUSTER_IDS[i + 1:]:
                gap = distance(centroid[a], centroid[b])
                self.check(gap >= CLUSTER_CENTROID_MIN_DISTANCE, "field.cluster_centroids", "%s-%s" % (a, b),
                           ">= %.2f apart" % CLUSTER_CENTROID_MIN_DISTANCE, "%.4f" % gap)
        for n in ids:
            nearest = min(CLUSTER_IDS, key=lambda c: (distance(coords[n], centroid[c]), c))
            self.check(nearest == self.cluster[n], "field.cluster_legibility", n,
                       "nearest centroid is own cluster %s" % self.cluster[n], nearest)
        self.coords = coords
        self.intra_inter_field = (intra_mean, inter_mean)

    def anchors(self):
        a = self.fixture["anchors"]
        ids = a.get("ids", [])
        flagged = [n for n in ENTITY_IDS if self.by_id[n]["anchor"]]
        self.check(len(ids) == ANCHOR_COUNT and len(set(ids)) == ANCHOR_COUNT, "anchors.count", "anchors",
                   "%d distinct anchors" % ANCHOR_COUNT, ids)
        self.check(sorted(ids) == flagged, "anchors.flag_mismatch", "anchors",
                   "anchors.ids equals entities flagged anchor", "ids %s, flagged %s" % (sorted(ids), flagged))
        for n in ids:
            if self.check(n in self.by_id, "anchors.continuity", n, "anchor is a fixture entity", "unknown"):
                self.check(STAGE_ORDER[self.by_id[n]["arrival_stage"]] < STAGE_ORDER[FIRST_FIELD_STAGE],
                           "anchors.continuity", n, "exists before S4", self.by_id[n]["arrival_stage"])
        if not hasattr(self, "coords"):
            return

        def lattice_d(p, q):
            return distance(lattice_normalized(*self.pos[p]), lattice_normalized(*self.pos[q]))

        sep = a.get("separation_pair", [])
        con = a.get("convergence_pair", [])
        if self.check(len(sep) == 2 and all(n in ids for n in sep), "anchors.separation", "separation_pair",
                      "two anchors", sep):
            p, q = sep
            ratio = distance(self.coords[p], self.coords[q]) / lattice_d(p, q)
            self.check(self.pos[p][0] == self.pos[q][0], "anchors.separation", sep, "same Lattice lane", (self.pos[p], self.pos[q]))
            self.check(self.cluster[p] != self.cluster[q], "anchors.separation", sep, "different clusters", (self.cluster[p], self.cluster[q]))
            self.check(ratio >= ANCHOR_SEPARATION_MIN_RATIO, "anchors.separation", sep,
                       "Field distance >= %.1f x Lattice distance" % ANCHOR_SEPARATION_MIN_RATIO, "%.3f" % ratio)
            self.separation_ratio = ratio
        if self.check(len(con) == 2 and all(n in ids for n in con), "anchors.convergence", "convergence_pair",
                      "two anchors", con):
            p, q = con
            ratio = distance(self.coords[p], self.coords[q]) / lattice_d(p, q)
            self.check(self.pos[p][0] != self.pos[q][0], "anchors.convergence", con, "different Lattice lanes", (self.pos[p], self.pos[q]))
            self.check(self.cluster[p] == self.cluster[q], "anchors.convergence", con, "same cluster", (self.cluster[p], self.cluster[q]))
            self.check(ratio <= ANCHOR_CONVERGENCE_MAX_RATIO, "anchors.convergence", con,
                       "Field distance <= %.1f x Lattice distance" % ANCHOR_CONVERGENCE_MAX_RATIO, "%.3f" % ratio)
            self.convergence_ratio = ratio
        self.check(set(sep).isdisjoint(con), "anchors.pairs", "anchors", "separation and convergence pairs disjoint", (sep, con))

    def derived(self):
        stored = self.fixture["derived"]
        expected = self.derive_stage_table()
        self.check(stored == expected, "derived.stage_table", "derived",
                   "recomputed stage table", "stored table differs from recomputation")

    def derive_stage_table(self):
        table = []
        for s in STAGES:
            arrived = sum(1 for n in ENTITY_IDS if STAGE_ORDER[self.by_id[n]["arrival_stage"]] <= STAGE_ORDER[s])
            table.append({
                "stage": s,
                "regime": "lattice" if STAGE_ORDER[s] < STAGE_ORDER[FIRST_FIELD_STAGE] else "field",
                "entity_count": arrived,
                "active_relationship_count": len(self.active(s)),
                "stub_relationship_ids": [e[0] for e in self.stubs(s)],
            })
        return table

    def run(self):
        try:
            self.structure()
            self.surface()
            self.semantic()
        except FixtureError:
            pass
        return self.failures


DEFAULT_SCHEMA = os.path.join(REPO_ROOT, "schemas", "demonstration-fixture.schema.json")
SUPPORTED_SCHEMA_KEYWORDS = {
    "$schema", "$id", "$defs", "$ref", "title", "description", "type", "required", "properties",
    "additionalProperties", "items", "enum", "const", "pattern", "minimum", "maximum",
    "minItems", "maxItems", "uniqueItems",
}


def schema_errors(instance, schema, root=None, path="fixture"):
    """Check an instance against the JSON Schema subset used by the fixture schema.

    A minimal standard-library interpreter, so no schema package is needed.
    Unsupported keywords are reported rather than silently ignored.
    """
    root = root if root is not None else schema
    errors = []
    unsupported = set(schema) - SUPPORTED_SCHEMA_KEYWORDS
    if unsupported:
        return ["%s: unsupported schema keyword(s) %s" % (path, sorted(unsupported))]
    if "$ref" in schema:
        target = root
        for part in schema["$ref"].lstrip("#/").split("/"):
            target = target[part]
        return schema_errors(instance, target, root, path)
    kind = schema.get("type")
    checks = {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "boolean": lambda v: isinstance(v, bool),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    }
    if kind and not checks[kind](instance):
        return ["%s: expected %s" % (path, kind)]
    if "const" in schema and instance != schema["const"]:
        errors.append("%s: expected %r" % (path, schema["const"]))
    if "enum" in schema and instance not in schema["enum"]:
        errors.append("%s: expected one of %r" % (path, schema["enum"]))
    if "pattern" in schema and isinstance(instance, str) and not re.search(schema["pattern"], instance):
        errors.append("%s: does not match %s" % (path, schema["pattern"]))
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append("%s: below minimum %s" % (path, schema["minimum"]))
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append("%s: above maximum %s" % (path, schema["maximum"]))
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append("%s: missing required %r" % (path, key))
        properties = schema.get("properties", {})
        for key, value in instance.items():
            if key in properties:
                errors.extend(schema_errors(value, properties[key], root, "%s.%s" % (path, key)))
            elif schema.get("additionalProperties") is False:
                errors.append("%s: unexpected property %r" % (path, key))
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append("%s: fewer than %d items" % (path, schema["minItems"]))
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append("%s: more than %d items" % (path, schema["maxItems"]))
        if schema.get("uniqueItems"):
            serialized = [json.dumps(item, sort_keys=True) for item in instance]
            if len(set(serialized)) != len(serialized):
                errors.append("%s: items not unique" % path)
        if "items" in schema:
            for i, item in enumerate(instance):
                errors.extend(schema_errors(item, schema["items"], root, "%s[%d]" % (path, i)))
    return errors


def load_schema(path=DEFAULT_SCHEMA):
    with open(path, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)


def validate(fixture, schema=None):
    """Return the list of failures for a fixture object (empty means valid)."""
    schema = schema if schema is not None else load_schema()
    failures = [Failure("schema", "fixture", "conforms to demonstration-fixture.schema.json", e)
                for e in schema_errors(fixture, schema)]
    return failures + Validator(fixture).run()


def validate_file(path):
    """Validate a fixture file, including its canonical serialization."""
    failures = []
    try:
        raw, fixture = load_fixture(path)
    except (OSError, UnicodeDecodeError, ValueError) as error:
        return [Failure("load", path, "readable UTF-8 JSON without duplicate keys", error)], None
    if b"\r" in raw:
        failures.append(Failure("serialization.line_endings", path, "LF only", "CR found"))
    if raw != canonical_serialization(fixture):
        failures.append(Failure("serialization.canonical", path,
                                "UTF-8, 2-space indent, LF, trailing newline, no trailing spaces",
                                "bytes differ from canonical serialization"))
    try:
        schema = load_schema()
    except (OSError, UnicodeDecodeError, ValueError) as error:
        return failures + [Failure("schema", DEFAULT_SCHEMA, "readable schema", error)], None
    failures.extend(Failure("schema", "fixture", "conforms to demonstration-fixture.schema.json", e)
                    for e in schema_errors(fixture, schema))
    validator = Validator(fixture)
    failures.extend(validator.run())
    return failures, validator


def summary(v):
    counts = {s: (len(v.active(s)), len(v.stubs(s))) for s in STAGES}
    lines = [
        "entities: %d  relationships: %d  clusters: %d  anchors: %s" % (
            ENTITY_COUNT, len(v.edges), len(CLUSTER_IDS), ", ".join(v.fixture["anchors"]["ids"])),
        "stage  entities  active  stubs",
    ]
    for row in v.derive_stage_table():
        lines.append("%-6s %8d %7d %6d" % (row["stage"], row["entity_count"], row["active_relationship_count"],
                                          len(row["stub_relationship_ids"])))
    lines += [
        "degree range: %d-%d  intra-cluster: %d  inter-cluster: %d" % (
            min(v.degree.values()), max(v.degree.values()), len(v.intra), len(v.inter)),
        "field mean linked: %.4f  mean unlinked: %.4f  ratio: %.3f  min separation: %.4f" % (
            v.metrics["mean_linked"], v.metrics["mean_unlinked"], v.metrics["ratio"], v.metrics["min_separation"]),
        "field mean intra-cluster: %.4f  mean inter-cluster: %.4f" % v.intra_inter_field,
        "anchor separation ratio: %.3f  anchor convergence ratio: %.3f" % (v.separation_ratio, v.convergence_ratio),
    ]
    return "\n".join(lines)


def main(argv):
    path = argv[1] if len(argv) > 1 else DEFAULT_FIXTURE
    failures, validator = validate_file(path)
    if failures:
        print("FIXTURE INVALID: %d failure(s)" % len(failures))
        for f in failures:
            print("- [%s] %s: expected %s; actual %s" % (f.invariant, f.subject, f.expected, f.actual))
        return 1
    print("FIXTURE VALID: all invariants pass")
    print(summary(validator))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
