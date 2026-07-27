"""Regression: every .claude/ file in a rostered folder stays enumerated.

`layers/` joined `operations/` and `policies/` in the check's scope. The gap it
closes is silent — an unlisted layer file works fine, it is simply invisible to
the CLAUDE.md index an agent reads to decide where a rule belongs.
"""
import meta_schema as M


def test_rostered_folders_are_currently_complete():
    assert M._check_roster_completeness((M.ROOT / "CLAUDE.md").read_text(encoding="utf-8")) == []


def test_layers_is_rostered():
    assert "layers" in dict(M.ROSTER_FOLDERS), "layers dropped from ROSTER_FOLDERS"


def test_unlisted_file_is_reported(monkeypatch):
    monkeypatch.setattr(M, "_disk_roster", lambda folder: {"ghost-runbook.md"})
    issues = M._check_roster_completeness((M.ROOT / "CLAUDE.md").read_text(encoding="utf-8"))
    assert any("ghost-runbook.md" in i for i in issues), issues
