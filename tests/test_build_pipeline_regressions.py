"""Regression tests for the C27/C28/C30/C32/C33 build-pipeline findings.

All five touch `tools/_build/` and the shared `_lib` helpers. The changes
verified here are the findable behavior deltas (extraction semantics are
pinned to the shared helpers, so they cannot drift again):

  C27 — the contradictions collector and source-metadata cache extract
        `## Connections` / `## Key Claims` via the shared
        `_lib.section_body`, not hand-rolled section regexes.
  C28 — the dependency builder's trail upstream extracts `## Path` via the
        shared `_lib.section_body`.
  C30 — `_hub_type` resolves prefixed wikilink targets (`[[entities/X]]`),
        which previously silently resolved to "missing".
  C32 — trail upstream counts only REAL path-item links (`N. [[Hub]]` at the
        start of the line, matching the trail lint's PATH_ITEM_LINKED_RE),
        not the first link anywhere on a numbered line.
  C33 — pages' ROOT_META guard is root-scoped: a subdir page whose filename
        collides with a root meta name (entities/overview.md) is kept.
"""
import json
from datetime import date

import pytest


# ---------- C27: section bodies via shared _lib.section_body ----------


def test_c27_connections_section_via_shared_section_body(tmp_path, monkeypatch):
    from _build import contradictions as CT

    src_dir = tmp_path / "sources"
    src_dir.mkdir(parents=True)
    (src_dir / "a.md").write_text(
        "---\ntitle: A\ntype: source\n---\n\n"
        "## Key Claims\n"
        "- [fact] claim one\n\n"
        "## Connections\n"
        "- contradicts: [[HubA]] — says X\n"
        "- contradicts: none\n\n"
        "## Contradictions\n"
        "- contradicts: [[Outside]] — outside the Connections section\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(CT, "wiki", tmp_path)

    items = CT._collect()
    assert len(items) == 1
    assert items[0]["source"] == "sources/a.md"
    assert items[0]["claim"] == "[[HubA]] — says X"


def test_c27_key_claims_primary_ratio_via_shared_section_body(tmp_path, monkeypatch):
    from _build import contradictions as CT

    src_dir = tmp_path / "sources"
    src_dir.mkdir(parents=True)
    (src_dir / "a.md").write_text(
        "---\ntitle: A\ntype: source\npublished: 2026-01-01\n---\n\n"
        "## Key Claims\n"
        "- [fact] fact one\n"
        "- [analysis] analysis one\n\n"
        "## Connections\n"
        "- contradicts: [[Hub]] — says X\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(CT, "wiki", tmp_path)

    meta = CT._build_source_metadata_cache()
    assert meta["a"]["date"] == "2026-01-01"
    assert meta["a"]["primary_ratio"] == 0.5


# ---------- C28: `## Path` via shared _lib.section_body ----------


def test_c28_trail_path_section_via_shared_section_body():
    from _build import dependencies as D

    stem_to_rel = {"HubA": "entities/HubA.md", "OtherHub": "entities/OtherHub.md"}
    body = (
        "## Path\n"
        "1. [[HubA]] — start here\n\n"
        "## Commentary\n"
        "1. [[OtherHub]] — numbered line in the commentary is not a path hop\n"
    )
    assert D._trail_path_upstream(body, stem_to_rel) == ["entities/HubA.md"]


def test_c28_trail_path_absent_returns_empty():
    from _build import dependencies as D

    assert D._trail_path_upstream("## Commentary\n1. [[HubA]]\n", {"HubA": "entities/HubA.md"}) == []


# ---------- C30: prefixed wikilink target resolution ----------


def test_c30_hub_type_resolves_prefixed_wikilink_targets(tmp_path, monkeypatch):
    from _build import contradictions as CT

    (tmp_path / "entities").mkdir()
    (tmp_path / "entities" / "OpenAI.md").write_text("---\ntype: entity\n---\n", encoding="utf-8")
    (tmp_path / "concepts").mkdir()
    (tmp_path / "concepts" / "RAG.md").write_text("---\ntype: concept\n---\n", encoding="utf-8")
    (tmp_path / "sources").mkdir()
    (tmp_path / "sources" / "paper.md").write_text("---\ntype: source\n---\n", encoding="utf-8")
    monkeypatch.setattr(CT, "wiki", tmp_path)

    # plain stems (pre-existing behavior)
    assert CT._hub_type("OpenAI") == "entity"
    assert CT._hub_type("RAG") == "concept"
    assert CT._hub_type("paper") == "source"
    assert CT._hub_type("Nope") == "missing"
    # C30: prefixed / suffixed forms now resolve too
    assert CT._hub_type("entities/OpenAI") == "entity"
    assert CT._hub_type("entities/OpenAI.md") == "entity"
    assert CT._hub_type("concepts/RAG") == "concept"
    assert CT._hub_type("sources/paper.md") == "source"
    assert CT._hub_type("entities/Nope") == "missing"


def test_c30_evidence_strength_credits_prefixed_entity_target(tmp_path, monkeypatch):
    """Pre-C30 a `[[entities/X]]` claim target resolved to "missing" (0.0 hub
    weight); the entity weight (0.15) must now be credited."""
    from _build import contradictions as CT

    (tmp_path / "entities").mkdir(parents=True)
    (tmp_path / "entities" / "OpenAI.md").write_text("---\ntype: entity\n---\n", encoding="utf-8")
    monkeypatch.setattr(CT, "wiki", tmp_path)

    item = {
        "id": "x", "source": "sources/a.md",
        "claim": "- contradicts: [[entities/OpenAI]] — says X",
    }
    ev = CT._evidence_strength(
        item, {"a": {"date": None, "primary_ratio": 0.0}}, date.today()
    )
    # 0.30*anchor(0) + 0.15*recency(0.2) + 0.40*primary(0) + 0.15*hub_type(1.0)
    assert ev == 0.18


# ---------- C32: only real path-item links are hops ----------


def test_c32_trail_upstream_only_counts_real_path_item_links():
    from _build import dependencies as D

    stem_to_rel = {"HubA": "entities/HubA.md", "HubB": "entities/HubB.md"}
    body = (
        "## Path\n"
        "1. [[HubA]] — the hop starts with a link\n"
        "2. See [[HubB]] for context — link not at item start: not a hop\n"
        "3. **[[HubA]]** — bold-prefixed hop still counts\n\n"
        "## Commentary\n"
        "fine\n"
    )
    upstream = D._trail_path_upstream(body, stem_to_rel)
    # HubB must be excluded (pre-C32 it was included as the first link of a
    # numbered line); bold-prefixed item 3 still hops (deduped against item 1).
    assert upstream == ["entities/HubA.md"]


def test_c32_path_item_regexes_shared_with_trail_lint():
    """The dependency builder and the trail lint must consume the SAME regex
    objects — no drifting copies of the path-item / path-item-linked rule."""
    from _lib import PATH_ITEM_LINKED_RE, PATH_ITEM_RE
    from _lint import trail as T

    assert T.PATH_ITEM_RE is PATH_ITEM_RE
    assert T.PATH_ITEM_LINKED_RE is PATH_ITEM_LINKED_RE


# ---------- C33: pages ROOT_META guard is root-scoped ----------


def test_c33_root_meta_guard_is_root_scoped(tmp_path, monkeypatch):
    from _build import pages as P

    wiki = tmp_path / "wiki"
    graph = tmp_path / "graph"
    (wiki / "entities").mkdir(parents=True)
    (wiki / "overviews").mkdir()
    (wiki / "overview.md").write_text("# ROOT\n", encoding="utf-8")
    (wiki / "entities" / "overview.md").write_text("# ENTITY NAMED OVERVIEW\n", encoding="utf-8")
    (wiki / "entities" / "Real.md").write_text("# REAL\n", encoding="utf-8")
    graph.mkdir()
    graph_json = graph / "_graph.json"
    graph_json.write_text(
        json.dumps({
            "nodes": [
                {"id": "overview.md", "label": "Overview", "type": "overview"},
                {"id": "entities/overview.md", "label": "Entity Overview", "type": "entity"},
                {"id": "entities/Real.md", "label": "Real", "type": "entity"},
            ]
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(P, "GRAPH_JSON", graph_json)
    monkeypatch.setattr(P, "WIKI", wiki)
    monkeypatch.setattr(P, "GRAPH", graph)

    P.run()

    pages = json.loads((graph / "_pages.json").read_text(encoding="utf-8"))["pages"]
    assert "overview.md" not in pages  # root meta file excluded
    assert "entities/overview.md" in pages  # C33: subdir name collision kept
    assert "entities/Real.md" in pages


@pytest.mark.parametrize(
    "nid,expected_excluded",
    [
        ("overview.md", True),
        ("contradiction.md", True),
        ("index.md", True),
        ("entities/overview.md", False),
        ("overviews/contradiction.md", False),
        ("sources/index.md", False),
    ],
)
def test_c33_root_meta_guard_scopes_by_parent(nid, expected_excluded):
    """The guard predicate itself: only wiki-ROOT files named in ROOT_META
    are excluded, subdir pages never are."""
    from pathlib import Path

    from _build import pages as P
    from _build.graph import ROOT_META

    excluded = Path(nid).parent == Path(".") and Path(nid).name in ROOT_META
    assert excluded is expected_excluded
    assert P.ROOT_META is ROOT_META  # pages uses the graph node-set definition
