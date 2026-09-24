"""Mutation tests for the SIBurst demonstration fixture validator.

Each test loads the canonical fixture, breaks exactly one invariant, and
checks that the validator rejects it with the expected invariant code.
Standard library only: python -m unittest discover -s tests
"""

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

import validate_fixture as vf  # noqa: E402

FIXTURE_PATH = os.path.join(REPO_ROOT, "data", "demonstration-fixture.json")


def load_canonical():
    with open(FIXTURE_PATH, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


CANONICAL = load_canonical()
SCHEMA = vf.load_schema()


def entity(fixture, entity_id):
    return next(e for e in fixture["entities"] if e["id"] == entity_id)


def relationship(fixture, rel_id):
    return next(r for r in fixture["relationships"] if r["id"] == rel_id)


def position(fixture, entity_id):
    e = entity(fixture, entity_id)
    return e["lattice"]["lane"], e["lattice"]["cell"]


def routable(fixture, rel):
    return vf.lattice_routable(position(fixture, rel["source"]), position(fixture, rel["target"]))


class FixtureTestCase(unittest.TestCase):
    def mutated(self):
        return copy.deepcopy(CANONICAL)

    def codes(self, fixture):
        return {f.invariant for f in vf.validate(fixture, SCHEMA)}

    def assertRejected(self, fixture, invariant):
        codes = self.codes(fixture)
        self.assertIn(invariant, codes, "expected %s among failures, got %s" % (invariant, sorted(codes)))


class CanonicalFixtureTests(FixtureTestCase):
    def test_canonical_fixture_passes(self):
        failures, _ = vf.validate_file(FIXTURE_PATH)
        self.assertEqual(failures, [])

    def test_canonical_serialization_is_stable(self):
        with open(FIXTURE_PATH, "rb") as handle:
            raw = handle.read()
        self.assertEqual(raw, vf.canonical_serialization(CANONICAL))
        self.assertNotIn(b"\r", raw)

    def test_validation_is_repeatable(self):
        first = vf.Validator(copy.deepcopy(CANONICAL))
        second = vf.Validator(copy.deepcopy(CANONICAL))
        self.assertEqual(first.run(), second.run())
        self.assertEqual(first.derive_stage_table(), second.derive_stage_table())
        self.assertEqual(first.metrics, second.metrics)

    def test_command_line_exit_codes(self):
        ok = subprocess.run([sys.executable, os.path.join(REPO_ROOT, "tools", "validate_fixture.py")],
                            capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        broken = self.mutated()
        broken["entities"][1]["id"] = "N01"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "fixture.json")
            with open(path, "wb") as handle:
                handle.write(vf.canonical_serialization(broken))
            bad = subprocess.run([sys.executable, os.path.join(REPO_ROOT, "tools", "validate_fixture.py"), path],
                                 capture_output=True, text=True)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("structure.entity_ids", bad.stdout)

    def test_schema_matches_validator_top_level(self):
        self.assertEqual(SCHEMA["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(SCHEMA["required"], vf.TOP_LEVEL_KEYS)

    def test_canonical_counts(self):
        v = vf.Validator(copy.deepcopy(CANONICAL))
        self.assertEqual(v.run(), [])
        table = {row["stage"]: row for row in v.derive_stage_table()}
        self.assertEqual([table[s]["entity_count"] for s in vf.ARRIVAL_STAGES], [3, 15, 22, 24])
        self.assertEqual(len(table["S0"]["stub_relationship_ids"]), 0)
        self.assertEqual(len(table["S1"]["stub_relationship_ids"]), 0)
        self.assertGreaterEqual(len(table["S2"]["stub_relationship_ids"]), 4)
        self.assertGreater(len(table["S3"]["stub_relationship_ids"]), len(table["S2"]["stub_relationship_ids"]))
        for s in ("S4", "S5", "S6"):
            self.assertEqual(table[s]["stub_relationship_ids"], [])
            self.assertEqual(table[s]["active_relationship_count"], len(CANONICAL["relationships"]))


class LawTests(unittest.TestCase):
    def test_placement_law(self):
        self.assertEqual(vf.lattice_position(0), (0, 0))
        self.assertEqual(vf.lattice_position(7), (1, 1))
        self.assertEqual(vf.lattice_position(23), (3, 5))

    def test_routing_law(self):
        self.assertTrue(vf.lattice_routable((0, 0), (0, 2)))
        self.assertFalse(vf.lattice_routable((0, 0), (0, 3)))
        self.assertTrue(vf.lattice_routable((1, 3), (2, 2)))
        self.assertFalse(vf.lattice_routable((1, 3), (2, 1)))
        self.assertFalse(vf.lattice_routable((0, 0), (2, 0)))

    def test_offset_law_is_bounded_and_deterministic(self):
        far = [(3, 5)] * 9
        pressure, dc, dl = vf.s3_offset("N01", (0, 0), far)
        self.assertEqual(pressure, 9)
        self.assertLessEqual((dc ** 2 + dl ** 2) ** 0.5, vf.OFFSET_CAP + 1e-9)
        self.assertEqual(vf.s3_offset("N01", (0, 0), far), (pressure, dc, dl))
        self.assertEqual(vf.s3_offset("N07", (1, 1), []), (0, 0.0, 0.0))
        # Opposing partners cancel; direction falls back to the ID-derived axis.
        self.assertEqual(vf.s3_offset("N02", (1, 2), [(0, 2), (2, 2)]), (2, -0.2, 0.0))


class StructuralMutationTests(FixtureTestCase):
    def test_duplicate_entity_fails(self):
        f = self.mutated()
        f["entities"][1]["id"] = "N01"
        self.assertRejected(f, "structure.entity_ids")

    def test_wrong_entity_count_fails(self):
        f = self.mutated()
        f["entities"].pop()
        self.assertRejected(f, "structure.entity_count")

    def test_duplicate_relationship_fails(self):
        f = self.mutated()
        clone = copy.deepcopy(f["relationships"][-1])
        clone["id"] = "R%02d" % (len(f["relationships"]) + 1)
        f["relationships"].append(clone)
        self.assertRejected(f, "structure.duplicate_relationship")

    def test_duplicate_relationship_id_fails(self):
        f = self.mutated()
        f["relationships"][1]["id"] = f["relationships"][0]["id"]
        self.assertRejected(f, "structure.relationship_ids")

    def test_self_link_fails(self):
        f = self.mutated()
        f["relationships"][0]["target"] = f["relationships"][0]["source"]
        self.assertRejected(f, "structure.self_link")

    def test_unknown_endpoint_fails(self):
        f = self.mutated()
        f["relationships"][0]["target"] = "N25"
        self.assertRejected(f, "structure.endpoints")

    def test_wrong_cluster_size_fails(self):
        f = self.mutated()
        moved = f["clusters"][0]["members"].pop()
        f["clusters"][1]["members"].append(moved)
        entity(f, moved)["cluster_id"] = f["clusters"][1]["id"]
        self.assertRejected(f, "clusters.size")

    def test_schema_rejects_unexpected_property(self):
        f = self.mutated()
        f["entities"][0]["colour"] = "blue"
        self.assertRejected(f, "schema")


class ArrivalAndLatticeMutationTests(FixtureTestCase):
    def test_invalid_arrival_stage_fails(self):
        f = self.mutated()
        f["entities"][0]["arrival_stage"] = "S4"
        self.assertRejected(f, "arrival.stage")

    def test_arrival_schedule_change_fails(self):
        f = self.mutated()
        entity(f, "N04")["arrival_stage"] = "S0"
        self.assertRejected(f, "arrival.cumulative")

    def test_wrong_lattice_coordinate_fails(self):
        f = self.mutated()
        entity(f, "N06")["lattice"]["cell"] = 4
        self.assertRejected(f, "lattice.placement_law")

    def test_weakened_routing_parameter_fails(self):
        f = self.mutated()
        f["lattice"]["same_lane_max_cell_distance"] = 3
        self.assertRejected(f, "lattice.parameters")


class LifecycleMutationTests(FixtureTestCase):
    def test_relationship_before_endpoint_fails(self):
        f = self.mutated()
        late = next(r for r in f["relationships"]
                    if entity(f, r["target"])["arrival_stage"] == "S2" and r["activation_stage"] == "S2")
        late["activation_stage"] = "S1"
        self.assertRejected(f, "lifecycle.before_endpoint")

    def test_post_s3_activation_fails(self):
        f = self.mutated()
        f["relationships"][-1]["activation_stage"] = "S4"
        self.assertRejected(f, "lifecycle.post_s3")


class RoutabilityMutationTests(FixtureTestCase):
    def test_s1_unroutable_edge_fails(self):
        f = self.mutated()
        rel = next(r for r in f["relationships"] if r["activation_stage"] == "S1")
        rel["source"], rel["target"] = "N01", "N06"  # same lane, cell distance 5
        self.assertRejected(f, "routability.s1")

    def test_missing_s2_stubs_fails(self):
        f = self.mutated()
        for r in f["relationships"]:
            if r["activation_stage"] == "S2" and not routable(f, r):
                r["activation_stage"] = "S3"
        self.assertRejected(f, "routability.s2_minimum")

    def test_s3_stub_growth_failure_fails(self):
        f = self.mutated()
        f["relationships"] = [r for r in f["relationships"]
                              if not (r["activation_stage"] == "S3" and not routable(f, r))]
        self.assertRejected(f, "routability.s3_growth")

    def test_stored_stub_table_tampering_fails(self):
        f = self.mutated()
        s2 = next(row for row in f["derived"] if row["stage"] == "S2")
        s2["stub_relationship_ids"] = s2["stub_relationship_ids"][:-1]
        self.assertRejected(f, "derived.stage_table")


class GraphMutationTests(FixtureTestCase):
    def test_disconnected_graph_fails(self):
        f = self.mutated()
        cluster = {e["id"]: e["cluster_id"] for e in f["entities"]}
        f["relationships"] = [r for r in f["relationships"] if cluster[r["source"]] == cluster[r["target"]]]
        self.assertRejected(f, "connectivity.graph")

    def test_low_degree_fails(self):
        f = self.mutated()
        degree_two = next(n for n in vf.ENTITY_IDS
                          if sum(n in (r["source"], r["target"]) for r in f["relationships"]) == 2)
        drop = next(r for r in f["relationships"] if degree_two in (r["source"], r["target"]))
        f["relationships"].remove(drop)
        self.assertRejected(f, "connectivity.degree")


class InstabilityMutationTests(FixtureTestCase):
    def test_arbitrary_offset_fails(self):
        f = self.mutated()
        displaced = next(e for e in f["entities"] if e["s3"]["pressure"] > 0)
        displaced["s3"]["offset_cell"] = 0.3
        self.assertRejected(f, "instability.offset_law")

    def test_zero_pressure_node_must_stay_centred(self):
        f = self.mutated()
        centred = next(e for e in f["entities"] if e["s3"]["pressure"] == 0)
        centred["s3"]["offset_lane"] = 0.1
        self.assertRejected(f, "instability.centered")


class AnchorMutationTests(FixtureTestCase):
    def test_anchor_continuity_failure_fails(self):
        f = self.mutated()
        entity(f, f["anchors"]["ids"][0])["anchor"] = False
        self.assertRejected(f, "anchors.flag_mismatch")

    def test_unknown_anchor_fails(self):
        f = self.mutated()
        f["anchors"]["ids"][0] = "N25"
        self.assertRejected(f, "anchors.continuity")

    def test_anchor_convergence_failure_fails(self):
        f = self.mutated()
        a, b = f["anchors"]["convergence_pair"]
        pa, pb = entity(f, a)["field"], entity(f, b)["field"]
        # Keep b in its cluster region but push it to the far edge from a.
        pb["x"] = round(1 - pa["x"], 3)
        pb["y"] = 0.95 if pa["y"] < 0.5 else 0.05
        self.assertRejected(f, "anchors.convergence")

    def test_anchor_separation_failure_fails(self):
        f = self.mutated()
        a, b = f["anchors"]["separation_pair"]
        pa = entity(f, a)["field"]
        entity(f, b)["field"] = {"x": round(pa["x"] + 0.06, 3), "y": pa["y"]}
        self.assertRejected(f, "anchors.separation")

    def test_anchor_pair_in_same_cluster_fails_separation(self):
        f = self.mutated()
        f["anchors"]["separation_pair"] = list(f["anchors"]["convergence_pair"])
        self.assertRejected(f, "anchors.separation")


class FieldMutationTests(FixtureTestCase):
    def test_field_duplicate_coordinate_fails(self):
        f = self.mutated()
        f["entities"][1]["field"] = dict(f["entities"][0]["field"])
        self.assertRejected(f, "field.duplicate_coordinate")

    def test_field_topology_distance_failure_fails(self):
        f = self.mutated()
        coords = [e["field"] for e in f["entities"]]
        shift = 5  # reassign coordinates by a fixed rotation, ignoring relationships
        for i, e in enumerate(f["entities"]):
            e["field"] = coords[(i * shift) % len(coords)]
        codes = self.codes(f)
        self.assertTrue({"field.linked_vs_unlinked", "field.cluster_distance", "field.cluster_legibility"} & codes,
                        sorted(codes))

    def test_field_out_of_bounds_fails(self):
        f = self.mutated()
        f["entities"][0]["field"]["x"] = 0.99
        self.assertRejected(f, "field.bounds")

    def test_field_collapsed_cluster_fails(self):
        f = self.mutated()
        members = f["clusters"][0]["members"]
        for k, n in enumerate(members):
            entity(f, n)["field"] = {"x": round(0.5 + 0.001 * k, 3), "y": 0.5}
        codes = self.codes(f)
        self.assertTrue({"field.cluster_collapse", "field.min_separation"} <= codes, sorted(codes))


class SurfaceMutationTests(FixtureTestCase):
    def test_random_field_metadata_fails(self):
        f = self.mutated()
        f["field"]["layout_seed"] = 7
        self.assertRejected(f, "surface.forbidden_key")

    def test_generated_timestamp_fails(self):
        f = self.mutated()
        f["field"]["generated_at"] = "volatile"
        self.assertRejected(f, "surface.forbidden_key")

    def test_telemetry_style_field_fails(self):
        f = self.mutated()
        f["entities"][0]["intelligence_score"] = 0.9
        self.assertRejected(f, "surface.forbidden_key")

    def test_telemetry_style_label_fails(self):
        f = self.mutated()
        f["stages"][4]["state_label"] = "LIVE AGI STATUS"
        self.assertRejected(f, "surface.forbidden_label")


if __name__ == "__main__":
    unittest.main()
