"""C71 — the always-empty INTRINSICALLY_UNFIXABLE_SOURCES whitelist and its
enforcement machinery (per-file escape branch, corpus whitelist/unwhitelisted
split, [Whitelist] summary blocks) were removed as YAGNI. The corpus gate is
now purely ACCEPTABLE_FAILS against the raw failing set; the per-file path has
no whitelist escape hatch. Re-introduce only when a real entry is whitelisted.
"""
import source as src
from pathlib import Path


def _write_failing_source(path):
    # Missing `## Summary` → S1 FAIL (a REQUIRED_KEYS member). The T1 tags /
    # Sc1 scraped hard gates and the kebab-case filename gate all pass, so S1
    # is the only failing key.
    path.write_text(
        "---\ntitle: X\ntype: source\ntags: [t]\nscraped: 2026-01-01\n---\n\n"
        "## Key Claims\n\n- [fact] Someone — said something\n\n"
        "## Connections\n\n- cites: [[f0]]\n",
        encoding="utf-8",
    )


def test_whitelist_constant_and_machinery_removed():
    assert not hasattr(src, "INTRINSICALLY_UNFIXABLE_SOURCES")
    assert "INTRINSICALLY_UNFIXABLE_SOURCES" not in (
        Path(__file__).resolve().parent.parent / "tools" / "_lint" / "source.py"
    ).read_text(encoding="utf-8")


def test_corpus_gate_is_pure_acceptance_margin(tmp_path, monkeypatch):
    wiki = tmp_path / "wiki"
    (wiki / "sources").mkdir(parents=True)
    files = []
    for i in range(3):
        p = wiki / "sources" / f"f{i}.md"
        _write_failing_source(p)
        files.append(p)
    monkeypatch.setattr(src, "WIKI", wiki)
    monkeypatch.setattr(src, "real_source_files", lambda: files)
    monkeypatch.setattr(src, "_PAGE_INDEX_CACHE", None)
    monkeypatch.setattr(src, "ACCEPTABLE_FAILS", 5)
    assert src.run() == 0  # 3 failing ≤ margin → advisory, exit 0
    monkeypatch.setattr(src, "ACCEPTABLE_FAILS", 2)
    assert src.run() == 1  # 3 failing > margin → hard fail


def test_per_file_path_has_no_whitelist_escape(tmp_path, monkeypatch):
    wiki = tmp_path / "wiki"
    (wiki / "sources").mkdir(parents=True)
    p = wiki / "sources" / "f0.md"
    _write_failing_source(p)
    monkeypatch.setattr(src, "SOURCES_DIR", wiki / "sources")
    monkeypatch.setattr(src, "real_source_files", lambda: [p])
    monkeypatch.setattr(src, "_PAGE_INDEX_CACHE", None)
    # A failing source hard-fails — previously the (always-empty) whitelist
    # branch existed as an escape hatch.
    assert src.run(target="f0") == 1
