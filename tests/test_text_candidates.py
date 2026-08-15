"""Regression coverage for text_candidates.py — both subdir walks must derive
from _lib.WIKI_SUBDIRS so overviews/ and contradictions/ pages count as
existing pages (excluded from candidates) and are mined for candidates like
every other content directory (C68).

The old hand-rolled 6-subdir tuples silently omitted overviews/ and
contradictions/: a token that was an existing page there got re-proposed as a
new-page candidate, and mentions living only in those two directories were
never counted.
"""
import text_candidates


def _write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_existing_overview_and_contradiction_pages_not_proposed(tmp_path, monkeypatch):
    """C68 — an existing page in overviews/ or contradictions/ is excluded
    from the candidate set (its stem lands in the existing-page index)."""
    wiki = tmp_path / "wiki"
    _write(wiki / "overviews" / "FooBar.md",
           "---\ntitle: FooBar\ntype: overview\n---\n\nBody.\n")
    _write(wiki / "contradictions" / "ContraThing.md",
           "---\ntitle: ContraThing\ntype: contradiction\n---\n\nBody.\n")
    for name in ("one", "two", "three"):
        _write(
            wiki / "sources" / f"{name}.md",
            "---\ntitle: X\ntype: source\n---\n\n## Summary\n\n"
            "FooBar and ContraThing. FooBar again. ContraThing again. "
            "FooBar. ContraThing.\n",
        )
    monkeypatch.setattr(text_candidates, "WIKI", wiki)

    payload, _ = text_candidates._candidates(min_mentions=3, min_pages=2, top=50)
    tokens = {c["token"] for c in payload["candidates"]}
    # Without the fix both would be proposed (9 mentions / 3 pages each).
    assert "FooBar" not in tokens
    assert "ContraThing" not in tokens

    # The exclusion index itself covers the two subdirs.
    stems, norm_map = text_candidates._index_existing_pages()
    assert {"FooBar", "ContraThing"} <= stems
    assert text_candidates._normalise("FooBar") in norm_map
    assert text_candidates._normalise("ContraThing") in norm_map


def test_mining_covers_overviews_and_contradictions(tmp_path, monkeypatch):
    """C68 — the mining loop also walks WIKI_SUBDIRS: a token appearing only in
    overviews/ + contradictions/ pages is counted like any other content."""
    wiki = tmp_path / "wiki"
    _write(wiki / "overviews" / "Ov.md",
           "---\ntitle: Ov\ntype: overview\n---\n\n"
           "ZephyrToken one. ZephyrToken two. ZephyrToken three.\n")
    _write(wiki / "contradictions" / "Ct.md",
           "---\ntitle: Ct\ntype: contradiction\n---\n\n"
           "ZephyrToken four. ZephyrToken five. ZephyrToken six.\n")
    monkeypatch.setattr(text_candidates, "WIKI", wiki)

    payload, _ = text_candidates._candidates(min_mentions=6, min_pages=2, top=50)
    by_token = {c["token"]: c for c in payload["candidates"]}
    assert "ZephyrToken" in by_token
    assert by_token["ZephyrToken"]["mentions"] == 6
    assert by_token["ZephyrToken"]["page_count"] == 2
    assert set(by_token["ZephyrToken"]["sample_pages"]) == {
        "overviews/Ov", "contradictions/Ct",
    }
