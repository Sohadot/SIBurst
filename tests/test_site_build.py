"""Build and mutation tests for the generated SIBurst site.

Each mutation test copies a fresh build, breaks one property, and checks that
the build check or the site validator rejects it with the expected code.
Requires the pinned build dependency (requirements-build.txt).
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

import build_site  # noqa: E402
import validate_site  # noqa: E402


def read(path):
    with open(path, "rb") as handle:
        return handle.read().decode("utf-8")


def write(path, text):
    with open(path, "wb") as handle:
        handle.write(text.encode("utf-8"))


class SiteTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.fresh = os.path.join(cls.tmp, "fresh")
        build_site.build(cls.fresh)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def copy(self):
        target = tempfile.mkdtemp(dir=self.tmp)
        docs = os.path.join(target, "docs")
        shutil.copytree(self.fresh, docs)
        return docs

    def codes(self, docs):
        return {f.invariant for f in validate_site.SiteValidator(docs, build_check=False).run()}

    def assertRejected(self, docs, code):
        codes = self.codes(docs)
        self.assertIn(code, codes, "expected %s, got %s" % (code, sorted(codes)))

    def edit(self, docs, name, old, new, count=1):
        path = os.path.join(docs, name)
        text = read(path)
        self.assertIn(old, text)
        write(path, text.replace(old, new, count))


class BuildTests(SiteTestCase):
    def test_canonical_build_matches_committed_docs(self):
        self.assertEqual(build_site.compare_trees(self.fresh, build_site.OUT), [])

    def test_check_passes_on_clean_output(self):
        result = subprocess.run([sys.executable, os.path.join(REPO_ROOT, "tools", "build_site.py"), "--check"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_build_is_deterministic(self):
        second = os.path.join(self.tmp, "second")
        build_site.build(second)
        self.assertEqual(build_site.compare_trees(self.fresh, second), [])

    def test_canonical_site_passes_validation(self):
        failures = validate_site.SiteValidator(self.copy(), build_check=False).run()
        self.assertEqual(failures, [])

    def test_modified_generated_html_fails_check(self):
        docs = self.copy()
        self.edit(docs, "index.html", "<main id=\"main\">", "<main id=\"main\"><p>edited by hand</p>")
        self.assertTrue(any("index.html" in p for p in build_site.check(docs)))

    def test_reference_drift_fails_check(self):
        docs = self.copy()
        self.edit(docs, "reference/foundation-thesis.html", "SIBurst names", "SIBurst proudly names")
        self.assertIn("differs from build output: reference/foundation-thesis.html", build_site.check(docs))

    def test_extra_file_fails_check(self):
        docs = self.copy()
        write(os.path.join(docs, "notes.html"), "<p>hand-written</p>")
        self.assertIn("not produced by the build: notes.html", build_site.check(docs))

    def test_reference_pages_render_without_raw_html(self):
        md = build_site.markdown_renderer()
        _, body = build_site.render_markdown(md, "# T\n\n<script>alert(1)</script>\n\n[x](javascript:alert(1))\n")
        self.assertNotIn("<script>", body)
        self.assertNotIn('href="javascript:', body)

    def test_internal_markdown_links_are_rewritten(self):
        self.assertEqual(build_site.rewrite_href("NAME_ARCHITECTURE.md#sibu"), "name-architecture.html#sibu")
        self.assertEqual(build_site.rewrite_href("README.md"), build_site.GITHUB_BLOB + "README.md")
        self.assertEqual(build_site.rewrite_href("#local"), "#local")


class FixtureCopyTests(SiteTestCase):
    def test_modified_public_fixture_fails(self):
        docs = self.copy()
        self.edit(docs, "data/demonstration-fixture.json", '"x": 0.411', '"x": 0.412')
        self.assertRejected(docs, "fixture.copy")

    def test_second_graph_in_source_fails(self):
        docs = self.copy()
        src = os.path.join(self.tmp, "src-copy")
        shutil.copytree(validate_site.SRC, src)
        with open(os.path.join(src, "assets", "system.js"), "a", encoding="utf-8") as handle:
            handle.write('\nconst extra = [["N01", "N02"]];\n')
        original = validate_site.SRC
        validate_site.SRC = src
        try:
            codes = {f.invariant for f in validate_site.SiteValidator(docs, build_check=False).run()}
        finally:
            validate_site.SRC = original
            shutil.rmtree(src)
        self.assertIn("fixture.second_graph", codes)


class StructureTests(SiteTestCase):
    def test_missing_reference_page_fails(self):
        docs = self.copy()
        os.remove(os.path.join(docs, "reference", "glossary.html"))
        self.assertRejected(docs, "structure.reference_page")

    def test_broken_internal_link_fails(self):
        docs = self.copy()
        self.edit(docs, "reference/index.html", "<h1>Reference</h1>", '<h1>Reference</h1><a href="missing-page.html">x</a>')
        self.assertRejected(docs, "links.broken")

    def test_broken_fragment_fails(self):
        docs = self.copy()
        self.edit(docs, "index.html", 'href="#reference">Reference</a>', 'href="#nowhere">Reference</a>')
        self.assertRejected(docs, "links.broken_fragment")

    def test_removed_stage_fails(self):
        docs = self.copy()
        path = os.path.join(docs, "index.html")
        write(path, re.sub(r'<section class="stage" id="s2".*?</section>', "", read(path), flags=re.S))
        self.assertRejected(docs, "structure.stages")

    def test_missing_skip_link_fails(self):
        docs = self.copy()
        self.edit(docs, "index.html", '<a class="skip-link" href="#reference">Skip to reference</a>', "")
        self.assertRejected(docs, "structure.skip_link")


class RuntimeSurfaceTests(SiteTestCase):
    def test_external_runtime_script_fails(self):
        docs = self.copy()
        self.edit(docs, "index.html", "</head>", '<script src="https://cdn.example.com/lib.js"></script></head>')
        self.assertRejected(docs, "runtime.external_script")

    def test_inline_script_fails(self):
        docs = self.copy()
        self.edit(docs, "index.html", "</head>", "<script>void 0</script></head>")
        self.assertRejected(docs, "runtime.inline_script")

    def test_external_stylesheet_fails(self):
        docs = self.copy()
        self.edit(docs, "index.html", "</head>", '<link rel="stylesheet" href="https://cdn.example.com/x.css"></head>')
        self.assertRejected(docs, "runtime.external_stylesheet")

    def test_external_font_fails(self):
        docs = self.copy()
        with open(os.path.join(docs, "assets", "system.css"), "a", encoding="utf-8") as handle:
            handle.write('\n@font-face { font-family: X; src: url("https://fonts.example.com/x.woff2"); }\n')
        self.assertRejected(docs, "runtime.external_font")

    def test_prohibited_runtime_dependency_fails(self):
        docs = self.copy()
        with open(os.path.join(docs, "assets", "system.js"), "a", encoding="utf-8") as handle:
            handle.write("\nconst jitter = Math.random();\n")
        self.assertRejected(docs, "runtime.dependency")

    def test_analytics_fails(self):
        docs = self.copy()
        with open(os.path.join(docs, "assets", "system.js"), "a", encoding="utf-8") as handle:
            handle.write("\ngtag('config', 'x');\n")
        self.assertRejected(docs, "runtime.dependency")

    def test_weakened_csp_fails(self):
        docs = self.copy()
        self.edit(docs, "index.html", "script-src 'self'", "script-src 'self' 'unsafe-inline'")
        self.assertRejected(docs, "runtime.csp")

    def test_iframe_fails(self):
        docs = self.copy()
        self.edit(docs, "index.html", "<main id=\"main\">", '<main id="main"><iframe src="x.html"></iframe>')
        self.assertRejected(docs, "runtime.forbidden_element")


class ClaimAndFallbackTests(SiteTestCase):
    def test_wrong_stage_label_fails(self):
        docs = self.copy()
        self.edit(docs, "index.html", "DEMONSTRATION STATE · S4 / TRANSITION DETECTED", "DEMONSTRATION STATE · S4 / LIVE AGI STATUS", count=1)
        self.assertRejected(docs, "claims.stage_label")

    def test_telemetry_wording_fails(self):
        docs = self.copy()
        self.edit(docs, "index.html", "<p class=\"caption\">", "<p class=\"caption\">REAL-TIME ", count=1)
        self.assertRejected(docs, "claims.wording")

    def test_missing_demonstration_scope_fails(self):
        docs = self.copy()
        path = os.path.join(docs, "index.html")
        write(path, read(path).replace(validate_site.SCOPE, "A model."))
        self.assertRejected(docs, "claims.scope")

    def test_visible_percentage_fails(self):
        docs = self.copy()
        self.edit(docs, "index.html", "<p class=\"caption\">", "<p class=\"caption\">62.5% ", count=1)
        self.assertRejected(docs, "claims.percentage")

    def test_missing_anchor_in_s5_record_fails(self):
        docs = self.copy()
        path = os.path.join(docs, "index.html")
        text = read(path)
        record = re.search(r'<figure class="transition-record".*?</figure>', text, re.S).group(0)
        broken = re.sub(r'<text class="identifier"[^>]*>N19</text>', "", record)
        write(path, text.replace(record, broken))
        self.assertRejected(docs, "fallback.record_anchors")

    def test_missing_entity_in_static_stage_fails(self):
        docs = self.copy()
        path = os.path.join(docs, "index.html")
        text = read(path)
        section = re.search(r'<section class="stage" id="s3".*?</section>', text, re.S).group(0)
        broken = re.sub(r'<g class="entity" data-node-id="N24".*?</g>', "", section, count=1, flags=re.S)
        write(path, text.replace(section, broken))
        self.assertRejected(docs, "fallback.entities")

    def test_low_contrast_fails(self):
        docs = self.copy()
        self.edit(docs, "assets/system.css", "--color-structure: #7A7F86;", "--color-structure: #D0D0D0;")
        self.assertRejected(docs, "contrast.ratio")

    def test_private_term_in_runtime_fails(self):
        docs = self.copy()
        self.edit(docs, "index.html", "<p class=\"caption\">", "<p class=\"caption\">Asking price available. ", count=1)
        self.assertRejected(docs, "safety.private_term")


if __name__ == "__main__":
    unittest.main()
