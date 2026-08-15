"""Regression tests for graph-module findings C54 / C97.

C54 — `lint graph gaps --top N` must cap the stdout bridge table without
forcing a second full betweenness recompute. Previously `--top N` computed
the bridge ranking twice per run: once capped at N (Track B display) and
again for the fixed trail slice (Track D), i.e. two full
`_discover/surprising.compute()` runs on an unchanged wiki.

C97 — the hub-frontmatter loader is single-sourced in
`_lint/_hub_common.load_hub_frontmatter`; `graph_gaps` (reshaped) and
`_news/gap_queries` (raw) both resolve through it instead of carrying
their own duplicate copies.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT / "tools", ROOT / "tools" / "_lint"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def _write_graph_artifacts(tmp_path):
    """`graph/_graph.json` + `graph/_clusters.json` fixtures with the REAL
    shape the pipeline parses (empty corpus is enough — bridge is patched)."""
    graph = tmp_path / "_graph.json"
    clusters = tmp_path / "_clusters.json"
    graph.write_text(json.dumps({"nodes": [], "edges": []}), encoding="utf-8")
    clusters.write_text(
        json.dumps({"clusters": [], "hub_assignments": {}, "source_assignments": {}}),
        encoding="utf-8",
    )
    return graph, clusters


def test_top_caps_bridge_table_without_recompute(monkeypatch, tmp_path, capsys):
    """C54 — `--top 3` shows a 3-row bridge table from ONE computation.

    Previously the bridge ranking was computed twice (top=3 for the display,
    top=10 for the trail slice) — two full betweenness recomputes. Now it is
    computed once at the widest needed slice and the display is capped after.
    """
    import graph_gaps

    _write_graph_artifacts(tmp_path)
    monkeypatch.setattr(graph_gaps, "GRAPH_PATH", tmp_path / "_graph.json")
    monkeypatch.setattr(graph_gaps, "CLUSTERS_PATH", tmp_path / "_clusters.json")
    monkeypatch.setattr(graph_gaps, "THEMES_PATH", tmp_path / "_no_themes.json")
    monkeypatch.setattr(graph_gaps, "TRAILS_DIR", tmp_path / "trails")
    monkeypatch.setattr(graph_gaps, "_load_hub_frontmatter", lambda: {})

    calls: list[int] = []

    def fake_bridge(top: int = 10):
        calls.append(top)
        return [
            {"id": f"entities/H{i}.md", "title": f"H{i}", "cluster": "c1",
             "degree": 5, "cross_cluster_ratio": 0.5, "composite": 0.5 - i / 100}
            for i in range(12)
        ]

    monkeypatch.setattr(graph_gaps, "detect_bridge_nodes", fake_bridge)

    rc = graph_gaps.run(json_out=False, top=3)
    assert rc == 1  # trail gaps keep the exit code independent of the display cap
    out = capsys.readouterr().out
    # Full computed ranking is surfaced in the header; the TABLE is capped.
    assert "Bridge node — top 12" in out
    bridge_section = out.split("─── Track B", 1)[1].split("─── Track D", 1)[0]
    bridge_rows = [l for l in bridge_section.splitlines() if re.match(r"^  H\d", l)]
    assert len(bridge_rows) == 3  # display capped at --top 3

    # JSON mode emits the full list regardless of --top (run() docstring
    # contract), still from a single computation per invocation.
    rc_json = graph_gaps.run(json_out=True, top=3)
    body = json.loads(capsys.readouterr().out)
    assert rc_json == 1
    assert len(body["track_b"]["bridge"]) == 12
    assert len(body["track_d"]["trail"]) == 10  # fixed TRAIL_BRIDGE_TOP slice

    # ONE computation per run, at max(--top, TRAIL_BRIDGE_TOP) — never a
    # second recompute just to re-slice the same ranking.
    assert calls == [10, 10]


def test_hub_frontmatter_loader_is_shared(monkeypatch, tmp_path):
    """C97 — graph_gaps and gap_queries resolve hub frontmatter through the
    ONE shared loader in `_lint/_hub_common`; the duplicate local copies are
    gone and both modules see identical data for the same hub ids."""
    import graph_gaps
    from _lint import _hub_common
    from _news import gap_queries

    wiki = tmp_path / "wiki"
    (wiki / "entities").mkdir(parents=True)
    (wiki / "concepts").mkdir()
    (wiki / "entities" / "Alpha.md").write_text(
        "---\ntitle: \"Alpha Corp\"\ntags: [ai]\n"
        "sources: [raw/a.md]\nlast_updated: 2026-01-02\n---\n# Alpha\n",
        encoding="utf-8",
    )
    (wiki / "concepts" / "Beta.md").write_text(
        "---\ntitle: \"Beta idea\"\n---\n# Beta\n", encoding="utf-8")

    monkeypatch.setattr(_hub_common, "WIKI", wiki)
    _hub_common.load_hub_frontmatter.cache_clear()

    shared = _hub_common.load_hub_frontmatter()
    assert set(shared) == {"entities/Alpha.md", "concepts/Beta.md"}

    # gap_queries consumes the shared loader directly (its `_load_hub_fm`
    # name is kept for `crawl.py`, which imports it).
    assert gap_queries._load_hub_fm is _hub_common.load_hub_frontmatter
    assert gap_queries._load_hub_fm() is shared  # lru_cache: same object
    assert gap_queries._load_hub_fm()["entities/Alpha.md"]["tags"] == ["ai"]

    # graph_gaps reshapes the SAME loader's output, so both modules resolve
    # the same frontmatter for the same hub ids.
    reshaped = graph_gaps._load_hub_frontmatter()
    assert set(reshaped) == {"entities/Alpha.md", "concepts/Beta.md"}
    assert reshaped["entities/Alpha.md"]["sources"] == ["raw/a.md"]
    assert reshaped["entities/Alpha.md"]["last_updated"].isoformat() == "2026-01-02"
    assert reshaped["entities/Alpha.md"]["title"] == "Alpha Corp"
    assert reshaped["concepts/Beta.md"]["title"] == "Beta idea"


def test_hub_frontmatter_loader_defined_once_repo_wide():
    """C97 audit — the loader body exists exactly once (in _hub_common); the
    per-module copies are not allowed to regrow."""
    srcs = [
        (ROOT / "tools" / "_lint" / "_hub_common.py").read_text(encoding="utf-8"),
        (ROOT / "tools" / "_lint" / "graph_gaps.py").read_text(encoding="utf-8"),
        (ROOT / "tools" / "_news" / "gap_queries.py").read_text(encoding="utf-8"),
    ]
    assert sum(s.count("def load_hub_frontmatter") for s in srcs) == 1
    # graph_gaps only reshapes; gap_queries no longer owns a local loader.
    assert "def _load_hub_fm" not in srcs[2]
