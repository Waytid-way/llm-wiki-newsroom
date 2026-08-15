"""Regression tests for the three issues found by the Codex review of the
quick-wins batch (issue #11) — case-insensitive frontmatter URL lookup,
malformed cluster-labels structure, and inline-code-only headings.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "_lint"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "_build"))

from _build import clusters as C  # noqa: E402
from _build.index import _extract_raw_url  # noqa: E402
from _lib import strip_code, strip_fences  # noqa: E402
from structure import _extract_headings  # noqa: E402


def test_strip_fences_keeps_inline_code():
    """Fence-only stripping preserves inline code spans (strip_code removes
    both — the two helpers must stay distinct)."""
    t = "## `foo` heading\n\n```py\n## Fake\n```\nplain `inline` text"
    assert strip_fences(t) == "## `foo` heading\n\nplain `inline` text"
    assert strip_code(t) == "##  heading\n\nplain  text"


def test_extract_headings_keeps_inline_code_heading():
    """A heading that is (or contains) inline code must still register —
    anchor validation depends on it. Fenced headings stay ignored."""
    heads = _extract_headings("## `foo`\n\n```md\n## Fake inside fence\n```\n")
    assert "`foo`" in heads, heads
    assert "Fake inside fence" not in heads, heads


def test_extract_raw_url_case_insensitive():
    """URL:/Source: frontmatter keys (any case) must still resolve — the old
    hand-rolled regex matched case-insensitively."""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "x.md"
        p.write_text('---\nURL: "https://example.com/UPPER"\n---\n', encoding="utf-8")
        assert _extract_raw_url(str(p)) == "https://example.com/UPPER"
        p.write_text("---\nSource: https://example.com/s\n---\n", encoding="utf-8")
        assert _extract_raw_url(str(p)) == "https://example.com/s"


def test_load_labels_malformed_shapes():
    """Syntactically valid JSON with a wrong top-level shape (list, or
    labels: null) must degrade to [] — same as corrupt files."""
    orig = C.LABELS_PATH
    try:
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            for content in ("[]", '{"labels": null}', '{"labels": {"a": 1}}'):
                p = d / "labels.json"
                p.write_text(content, encoding="utf-8")
                C.LABELS_PATH = p
                assert C._load_labels() == [], f"shape {content!r} must yield []"
    finally:
        C.LABELS_PATH = orig
    assert isinstance(C._load_labels(), list)  # healthy path intact
