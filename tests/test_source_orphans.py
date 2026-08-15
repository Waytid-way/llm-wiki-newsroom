"""Regression coverage for the hub `sources:` sync — the rewrite must leave
`last_updated` alone — plus the source_orphans detector/fixer consistency
fixes (C67: backfill iterates HUB_SUBDIRS; C70: the corpus wikilink walk
strips code before extracting links).

A hub's `last_updated` is its narrative date (`.claude/layers/hub.md`). Bumping
it on a pure `sources:` sync re-dates the hub as freshly authored, which makes
`upstream_max_date > last_updated` structurally impossible and hides a lagging
narrative from the staleness lint. New-source arrival reaches downstream pages
through the composite propagation date in `tools/_build/dependencies.py`.
"""
import json

import source_orphans


def test_sources_sync_does_not_bump_last_updated():
    text = "---\ntitle: X\nsources: [a]\nlast_updated: 2026-06-26\n---\n\n## Overview\n\nBody.\n"
    out = source_orphans._rewrite_sources(text, ["a", "b"])
    assert "sources: [a, b]" in out
    assert "last_updated: 2026-06-26" in out


def test_block_style_sources_normalized_without_touching_date():
    text = "---\ntitle: X\nsources:\n  - a\n  - b\nlast_updated: 2026-06-26\n---\n\nBody.\n"
    out = source_orphans._rewrite_sources(text, ["a", "b", "c"])
    assert "sources: [a, b, c]" in out
    assert "  - a" not in out  # block items consumed, not left orphaned
    assert "last_updated: 2026-06-26" in out


def test_backfill_covers_all_hub_subdirs(tmp_path, monkeypatch):
    """C67 — _apply_backfill must iterate HUB_SUBDIRS, not a hardcoded
    entities/concepts subset: a `## Connections` link to a syntheses/trails/
    timelines hub must be backfilled into that hub's frontmatter, matching the
    hub set the detector scans (the two had silently diverged)."""
    wiki = tmp_path / "wiki"
    (wiki / "sources").mkdir(parents=True)
    pages = {
        "entities": ["EntityOne"],
        "syntheses": ["SynthOne"],
        "trails": ["TrailOne"],
    }
    for sub, stems in pages.items():
        (wiki / sub).mkdir()
        for stem in stems:
            (wiki / sub / f"{stem}.md").write_text(
                f"---\ntitle: {stem}\ntype: hub\n---\n\nBody.\n", encoding="utf-8"
            )
    src = wiki / "sources" / "alpha.md"
    src.write_text(
        "---\ntitle: Alpha\ntype: source\n---\n\n## Summary\n\nBody.\n\n"
        "## Connections\n\n- [[EntityOne]]\n- [[SynthOne]]\n- [[TrailOne]]\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(source_orphans, "WIKI", wiki)
    monkeypatch.setattr(source_orphans, "real_source_files", lambda: [src])

    assert source_orphans._apply_backfill() == 3
    for sub, stems in pages.items():
        for stem in stems:
            text = (wiki / sub / f"{stem}.md").read_text(encoding="utf-8")
            assert "sources: [alpha]" in text


def test_corpus_walk_ignores_fenced_wikilinks(tmp_path, monkeypatch, capsys):
    """C70 — the corpus wikilink walk must strip code before extracting links
    (mirrors _lint/structure.py): a `[[link]]` inside a code fence is example
    text, not a reference, and must not de-orphan the source."""
    wiki = tmp_path / "wiki"
    (wiki / "sources").mkdir(parents=True)
    (wiki / "concepts").mkdir()
    src = wiki / "sources" / "fenced-only.md"
    src.write_text(
        "---\ntitle: Fenced Only\ntype: source\n---\n\n## Summary\n\nBody.\n",
        encoding="utf-8",
    )
    (wiki / "concepts" / "Example.md").write_text(
        "---\ntitle: Example\ntype: concept\n---\n\n## Overview\n\nUsage example:\n\n"
        "```md\n[[fenced-only]]\n```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(source_orphans, "WIKI", wiki)
    monkeypatch.setattr(source_orphans, "SRC", wiki / "sources")
    monkeypatch.setattr(source_orphans, "real_source_files", lambda: [src])

    rc = source_orphans.run(json_out=True)
    payload = json.loads(capsys.readouterr().out)
    assert rc == 1  # the fenced link must NOT rescue the orphan
    assert payload["orphans"] == 1
    assert payload["dead_end"] == ["fenced-only"]


def test_corpus_walk_counts_real_wikilinks(tmp_path, monkeypatch, capsys):
    """C70 control — a genuine link outside any fence still de-orphans."""
    wiki = tmp_path / "wiki"
    (wiki / "sources").mkdir(parents=True)
    (wiki / "concepts").mkdir()
    src = wiki / "sources" / "linked.md"
    src.write_text(
        "---\ntitle: Linked\ntype: source\n---\n\n## Summary\n\nBody.\n",
        encoding="utf-8",
    )
    (wiki / "concepts" / "Example.md").write_text(
        "---\ntitle: Example\ntype: concept\n---\n\n## Overview\n\nSee [[linked]] for details.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(source_orphans, "WIKI", wiki)
    monkeypatch.setattr(source_orphans, "SRC", wiki / "sources")
    monkeypatch.setattr(source_orphans, "real_source_files", lambda: [src])

    rc = source_orphans.run(json_out=True)
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["orphans"] == 0
