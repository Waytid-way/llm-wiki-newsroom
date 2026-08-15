"""Regression tests for two export fixes (issue #8):

- C98: main() validates the graph assets stage_site needs BEFORE touching the
  export dir, so a fresh clone (gitignored graph/_pages.json) aborts with a
  friendly build-first message instead of a half-rewritten wiki-export/ + raw
  FileNotFoundError traceback.
- C99: _clean_body strips YAML frontmatter, so the merged export files carry
  prose only (per-page '---' stays a clean separator instead of being doubled
  by raw frontmatter text).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import export  # noqa: E402


def test_clean_body_strips_frontmatter():
    """Raw YAML frontmatter must not land as visible body text in the RAG
    export — prose only. No-op when the page has no frontmatter."""
    src = '---\ntitle: "Foom"\ntype: concept\n---\n## Body\n\nprose here\n'
    out = export._clean_body(src)
    assert "title:" not in out
    assert "type: concept" not in out
    assert out.lstrip().startswith("## Body"), out
    # Plain body without frontmatter passes through unchanged.
    assert export._clean_body("## Body\n\nprose here\n").lstrip().startswith("## Body")


def test_merge_folder_omits_frontmatter(monkeypatch, tmp_path):
    """The merged file (all-overviews.md etc.) must carry page prose only — no
    raw frontmatter blocks between the per-page '---' separators."""
    folder = tmp_path / "wiki" / "overviews"
    folder.mkdir(parents=True)
    (folder / "A.md").write_text(
        '---\ntitle: "Alpha"\ntype: overview\n---\n## Alpha body\n', encoding="utf-8"
    )
    out = tmp_path / "out"
    out.mkdir()  # main() does OUT.mkdir(exist_ok=True) before merging
    monkeypatch.setattr(export, "WIKI", tmp_path / "wiki")
    monkeypatch.setattr(export, "OUT", out)

    name, count = export._merge_folder("overviews", "all-overviews.md")

    assert count == 1
    merged = (out / name).read_text(encoding="utf-8")
    assert 'title: "Alpha"' not in merged
    assert "type: overview" not in merged
    assert "## Alpha body" in merged
    # Per-page separator survives exactly once — not doubled by frontmatter.
    assert merged.count("---") == 1


def test_main_aborts_before_mutation_when_assets_missing(monkeypatch, tmp_path, capsys):
    """Fresh-clone regression: graph/_pages.json is gitignored until build.py
    runs, and main() used to crash AFTER rewriting wiki-export/. It must now
    return 1 with the friendly build-first message and touch nothing."""
    monkeypatch.setattr(export, "GRAPH", tmp_path / "graph")  # empty → all 4 JSONs absent
    out = tmp_path / "wiki-export"
    monkeypatch.setattr(export, "OUT", out)

    assert export.main() == 1
    assert not out.exists(), "export dir must not be created on missing assets"
    printed = capsys.readouterr().out
    assert "tools/build.py" in printed
    assert "_pages.json" in printed
