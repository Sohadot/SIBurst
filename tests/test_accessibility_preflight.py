"""Mutation tests for the automated accessibility preflight.

The preflight is machine evidence only. It never satisfies Interface
Acceptance Test 17, which is a human screen-reader traversal.
Standard library only.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

import preflight_accessibility as pa  # noqa: E402

DOCS = os.path.join(REPO_ROOT, "docs")


def read(path):
    with open(path, "rb") as handle:
        return handle.read().decode("utf-8")


def write(path, text):
    with open(path, "wb") as handle:
        handle.write(text.encode("utf-8"))


class PreflightTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.docs = os.path.join(self.tmp, "docs")
        shutil.copytree(DOCS, self.docs)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def checks(self):
        findings, _ = pa.run(self.docs)
        return {f.check for f in findings}

    def mutate(self, old, new, page="index.html", count=1, regex=False):
        path = os.path.join(self.docs, page)
        text = read(path)
        if regex:
            changed = re.sub(old, new, text, count=count, flags=re.S)
            self.assertNotEqual(changed, text)
        else:
            self.assertIn(old, text)
            changed = text.replace(old, new, count)
        write(path, changed)

    def assertFlagged(self, check):
        found = self.checks()
        self.assertIn(check, found, "expected %s, got %s" % (check, sorted(found)))


class CanonicalTests(PreflightTestCase):
    def test_canonical_build_passes(self):
        findings, pages = pa.run(self.docs)
        self.assertEqual(findings, [])
        self.assertGreaterEqual(pages, 17)

    def test_banner_states_it_is_not_test_17(self):
        result = subprocess.run([sys.executable, os.path.join(REPO_ROOT, "tools", "preflight_accessibility.py")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(result.stdout.startswith(pa.BANNER))
        self.assertIn("does not satisfy Interface Acceptance Test 17", result.stdout)
        self.assertNotRegex(result.stdout, r"Test 17 (passed|PASS)")


class MutationTests(PreflightTestCase):
    def test_removed_scope_statement(self):
        path = os.path.join(self.docs, "index.html")
        write(path, read(path).replace(pa.SCOPE, "A model."))
        self.assertFlagged("scope.statement")

    def test_removed_stage_description(self):
        self.mutate(r'<p class="description" id="s3-description">.*?</p>', "", regex=True)
        self.assertFlagged("stages.description")

    def test_unscoped_stage_description(self):
        self.mutate(r'(<p class="description" id="s4-description">)Demonstration stage', r"\1Stage", regex=True)
        self.assertFlagged("stages.description")

    def test_duplicate_live_region(self):
        self.mutate("<main id=\"main\">", '<main id="main"><p aria-live="polite" id="second-announcer"></p>')
        self.assertFlagged("live.count")

    def test_assertive_live_region(self):
        self.mutate('id="stage-announcer" aria-live="polite"', 'id="stage-announcer" aria-live="assertive"')
        self.assertFlagged("live.assertive")

    def test_decorative_svg_exposed(self):
        self.mutate('<svg class="system" aria-hidden="true"', '<svg class="system"')
        self.assertFlagged("svg.exposed")

    def test_focus_target_inside_graphics(self):
        self.mutate(r'(<svg class="record"[^>]*>)', r'\1<a href="#s0">x</a>', regex=True)
        self.assertFlagged("focus.inside_graphics")

    def test_removed_transition_record_text(self):
        self.mutate(r'<figcaption class="record-text">.*?</figcaption>', "", regex=True)
        self.assertFlagged("record.text")

    def test_duplicate_id(self):
        self.mutate('id="s2-description"', 'id="s1-description"')
        self.assertFlagged("ids.duplicate")

    def test_broken_aria_reference(self):
        self.mutate('aria-labelledby="s5-title"', 'aria-labelledby="s5-missing"')
        self.assertFlagged("aria.broken_reference")

    def test_positive_tabindex(self):
        self.mutate('<a href="#reference">Enter the reference layer</a>', '<a href="#reference" tabindex="3">Enter the reference layer</a>')
        self.assertFlagged("focus.positive_tabindex")

    def test_missing_reference_item(self):
        self.mutate(r'<li><a href="glossary.html">.*?</li>', "", page="reference/index.html", regex=True)
        self.assertFlagged("reference.list")

    def test_skip_link_not_first(self):
        self.mutate('<a class="skip-link" href="#reference">Skip to reference</a>', "")
        self.assertFlagged("focus.skip_link")

    def test_stage_out_of_order(self):
        self.mutate('id="s1" data-stage="S1"', 'id="s9" data-stage="S1"')
        self.assertFlagged("stages.structure")

    def test_missing_lang(self):
        self.mutate('<html lang="en">', "<html>", page="reference/glossary.html")
        self.assertFlagged("document.lang")


if __name__ == "__main__":
    unittest.main()
