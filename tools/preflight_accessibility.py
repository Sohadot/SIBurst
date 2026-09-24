#!/usr/bin/env python3
"""Automated accessibility preflight for the generated SIBurst site.

ACCESSIBILITY PREFLIGHT ONLY — does not satisfy Interface Acceptance Test 17.

Test 17 is a human screen-reader traversal (INTERFACE_ACCEPTANCE.md). This
tool catches structural regressions before a human test: scope statement,
stage structure and descriptions, live region, hidden decorative graphics,
the transition record text, the reference list, IDs, ARIA references, and
focus targets. Standard library only. Fails closed.

Usage:
    python tools/preflight_accessibility.py [--docs DIR]
"""

import argparse
import os
import re
import sys
from collections import namedtuple
from html.parser import HTMLParser

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(REPO_ROOT, "docs")
BANNER = "ACCESSIBILITY PREFLIGHT ONLY — does not satisfy Interface Acceptance Test 17"
STAGES = ["s0", "s1", "s2", "s3", "s4", "s5", "s6"]
SCOPE = "SYSTEM DEMONSTRATION — a model of the SIBurst concept, not a measurement."
FOCUSABLE = {"a", "button", "input", "select", "textarea", "summary", "iframe"}

Finding = namedtuple("Finding", "check page detail")


class Tree(HTMLParser):
    """A minimal element tree with ancestry, enough for structural checks."""

    VOID = {"meta", "link", "br", "hr", "img", "input", "source", "wbr", "area", "base", "col", "embed", "param", "track"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = {"tag": "#root", "attrs": {}, "children": [], "text": [], "parent": None}
        self.current = self.root
        self.elements = []

    def handle_starttag(self, tag, attrs):
        node = {"tag": tag, "attrs": dict(attrs), "children": [], "text": [], "parent": self.current}
        self.current["children"].append(node)
        self.elements.append(node)
        if tag not in self.VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        node = {"tag": tag, "attrs": dict(attrs), "children": [], "text": [], "parent": self.current}
        self.current["children"].append(node)
        self.elements.append(node)

    def handle_endtag(self, tag):
        node = self.current
        while node is not self.root and node["tag"] != tag:
            node = node["parent"]
        if node is not self.root:
            self.current = node["parent"]

    def handle_data(self, data):
        self.current["text"].append(data)


def parse(path):
    tree = Tree()
    with open(path, "rb") as handle:
        tree.feed(handle.read().decode("utf-8"))
    return tree


def text_of(node):
    parts = list(node["text"])
    for child in node["children"]:
        parts.append(text_of(child))
    return " ".join(" ".join(parts).split())


def ancestors(node):
    node = node["parent"]
    while node is not None:
        yield node
        node = node["parent"]


def hidden_from_at(node):
    """True when the node or an ancestor is removed from the accessibility tree."""
    for n in [node] + list(ancestors(node)):
        if n["attrs"].get("aria-hidden") == "true" or "hidden" in n["attrs"]:
            return True
    return False


def by_id(tree, element_id):
    return [e for e in tree.elements if e["attrs"].get("id") == element_id]


def html_pages(docs):
    pages = []
    for base, dirs, names in os.walk(docs):
        dirs.sort()
        for name in sorted(names):
            if name.endswith(".html"):
                pages.append(os.path.join(base, name))
    return pages


def check_page(tree, rel):
    findings = []
    ids = [e["attrs"]["id"] for e in tree.elements if "id" in e["attrs"]]
    for duplicate in sorted({i for i in ids if ids.count(i) > 1}):
        findings.append(Finding("ids.duplicate", rel, "id %r appears more than once" % duplicate))
    known = set(ids)
    for e in tree.elements:
        for attr in ("aria-labelledby", "aria-describedby", "aria-controls"):
            for ref in e["attrs"].get(attr, "").split():
                if ref not in known:
                    findings.append(Finding("aria.broken_reference", rel, "%s=%r on <%s> has no target" % (attr, ref, e["tag"])))
        tabindex = e["attrs"].get("tabindex")
        if tabindex is not None and re.fullmatch(r"-?\d+", tabindex) and int(tabindex) > 0:
            findings.append(Finding("focus.positive_tabindex", rel, "tabindex=%s on <%s>" % (tabindex, e["tag"])))
        # The panel is revealed by script at runtime, so the `hidden` attribute
        # does not count here: graphics must be aria-hidden themselves.
        aria_hidden = any(n["attrs"].get("aria-hidden") == "true" for n in [e] + list(ancestors(e)))
        if e["tag"] == "svg" and not aria_hidden:
            findings.append(Finding("svg.exposed", rel, "decorative <svg class=%r> is exposed to assistive technology" % e["attrs"].get("class")))
        if e["tag"] == "svg" and e["attrs"].get("focusable") != "false":
            findings.append(Finding("svg.focusable", rel, "<svg class=%r> should carry focusable=\"false\"" % e["attrs"].get("class")))
        in_svg = any(a["tag"] == "svg" for a in ancestors(e))
        if in_svg and (e["tag"] in FOCUSABLE or "tabindex" in e["attrs"] or "href" in e["attrs"]):
            findings.append(Finding("focus.inside_graphics", rel, "focus target <%s> inside decorative graphics" % e["tag"]))
    html = next((e for e in tree.elements if e["tag"] == "html"), None)
    if not html or not html["attrs"].get("lang"):
        findings.append(Finding("document.lang", rel, "<html> must declare a language"))
    if not any(e["tag"] == "title" and text_of(e) for e in tree.elements):
        findings.append(Finding("document.title", rel, "missing <title>"))
    if not any(e["tag"] == "main" for e in tree.elements):
        findings.append(Finding("document.main", rel, "missing <main> landmark"))
    if len([e for e in tree.elements if e["tag"] == "h1"]) != 1:
        findings.append(Finding("document.h1", rel, "exactly one <h1> expected"))
    return findings


def check_index(tree):
    rel = "index.html"
    findings = []
    visible = [e for e in tree.elements if not hidden_from_at(e)]
    if not any(SCOPE in text_of(e) for e in visible if e["tag"] == "p"):
        findings.append(Finding("scope.statement", rel, "demonstration scope statement missing from accessible text"))
    sections = [e for e in tree.elements if e["tag"] == "section" and "stage" in e["attrs"].get("class", "").split()]
    if [s["attrs"].get("id") for s in sections] != STAGES:
        findings.append(Finding("stages.structure", rel, "stage sections must be %s in order" % STAGES))
    for s in sections:
        sid = s["attrs"].get("id")
        heading = [c for c in s["children"] if c["tag"] == "h2"]
        if not heading or s["attrs"].get("aria-labelledby") != heading[0]["attrs"].get("id"):
            findings.append(Finding("stages.heading", rel, "%s needs an h2 that labels the section" % sid))
        description = by_id(tree, "%s-description" % sid)
        if not description or len(text_of(description[0])) < 40 or hidden_from_at(description[0]):
            findings.append(Finding("stages.description", rel, "%s needs an accessible state description" % sid))
        elif "demonstration" not in text_of(description[0]).lower():
            findings.append(Finding("stages.description", rel, "%s description must be scoped to the demonstration" % sid))
    live = [e for e in tree.elements if "aria-live" in e["attrs"] or e["attrs"].get("role") in ("status", "alert", "log")]
    if len(live) != 1:
        findings.append(Finding("live.count", rel, "exactly one live region expected, found %d" % len(live)))
    for e in live:
        if e["attrs"].get("aria-live") != "polite" or e["attrs"].get("role") == "alert":
            findings.append(Finding("live.assertive", rel, "stage announcements must be polite, not assertive"))
        if e["attrs"].get("id") != "stage-announcer" or hidden_from_at(e):
            findings.append(Finding("live.placement", rel, "the live region must be #stage-announcer and exposed"))
        if text_of(e):
            findings.append(Finding("live.initial", rel, "the live region must start empty so nothing is announced on load"))
    record = [e for e in tree.elements if e["tag"] == "figure" and "transition-record" in e["attrs"].get("class", "")]
    record_text = [c for r in record for c in r["children"] if c["tag"] == "figcaption"]
    if not record_text or len(text_of(record_text[0])) < 80 or hidden_from_at(record_text[0]):
        findings.append(Finding("record.text", rel, "the S5 transition record needs its text equivalent"))
    reference = by_id(tree, "reference")
    items = [e for e in tree.elements if e["tag"] == "a" and e["attrs"].get("href", "").startswith("reference/")
             and e["attrs"].get("href") != "reference/"]
    if not reference or len(items) < 1:
        findings.append(Finding("reference.list", rel, "reference list missing"))
    first_focus = next((e for e in tree.elements if e["tag"] in FOCUSABLE and (e["tag"] != "a" or "href" in e["attrs"])), None)
    if not first_focus or first_focus["attrs"].get("href") != "#reference":
        findings.append(Finding("focus.skip_link", rel, "the first focus target must be the skip-to-reference link"))
    return findings, len(items)


def check_reference_index(tree, expected_count):
    rel = "reference/index.html"
    items = [e for e in tree.elements if e["tag"] == "a" and e["attrs"].get("href", "").endswith(".html")]
    if len(items) != expected_count:
        return [Finding("reference.list", rel, "reference index lists %d documents, main page %d" % (len(items), expected_count))]
    return []


def run(docs=DOCS):
    findings = []
    index_path = os.path.join(docs, "index.html")
    if not os.path.exists(index_path):
        return [Finding("document.missing", "index.html", "not found")], 0
    pages = html_pages(docs)
    trees = {os.path.relpath(p, docs).replace(os.sep, "/"): parse(p) for p in pages}
    for rel, tree in trees.items():
        findings.extend(check_page(tree, rel))
    index_findings, reference_count = check_index(trees["index.html"])
    findings.extend(index_findings)
    if "reference/index.html" in trees:
        findings.extend(check_reference_index(trees["reference/index.html"], reference_count))
    else:
        findings.append(Finding("reference.list", "reference/index.html", "not found"))
    return findings, len(trees)


def main(argv):
    parser = argparse.ArgumentParser(description=BANNER)
    parser.add_argument("--docs", default=DOCS)
    args = parser.parse_args(argv[1:])
    print(BANNER)
    findings, pages = run(args.docs)
    if findings:
        print("PREFLIGHT FAILED: %d finding(s)" % len(findings))
        for f in findings:
            print("- [%s] %s: %s" % f)
        return 1
    print("PREFLIGHT PASSED: %d pages checked. Human screen-reader acceptance (Test 17) is recorded separately in ACCESSIBILITY_TEST_17.md." % pages)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
