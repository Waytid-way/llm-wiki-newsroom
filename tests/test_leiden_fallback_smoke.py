"""Dependency-free Leiden smoke test (issue #2).

Regression guard for the pure-Python fallback path: with the native
igraph/leidenalg C extensions unavailable (the default Termux/Android
install), `build clusters` must still cluster the shipped corpus and
produce stable output matching the committed _clusters.json.

Fails if the fallback stops working — e.g. a future refactor makes
_run_leiden import native modules unconditionally, or the fallback's
partition drifts from the committed (native-produced) artifact.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _block_native(monkeypatch):
    """Simulate an install without the native Leiden C extensions."""
    for name in ("igraph", "leidenalg"):
        monkeypatch.setitem(sys.modules, name, None)


def _committed_clusters():
    return json.loads(
        (ROOT / "graph" / "_clusters.json").read_text(encoding="utf-8")
    ).get("clusters", [])


def test_dependency_free_cluster_build_matches_shipped_corpus(monkeypatch):
    """_run_leiden (the backend-selection seam) clusters via the pure-Python
    fallback when native modules are unavailable, reproducing the committed
    (native-produced) cluster membership exactly — splits AND merges fail."""
    _block_native(monkeypatch)

    from _build.clusters import RESOLUTION, SEED, build_hub_graph, _run_leiden

    G, *_ = build_hub_graph(verbose=False)
    expected = {frozenset(c["members"]) for c in _committed_clusters()}

    # Successful clustering: every hub is assigned, none dropped.
    communities = _run_leiden(G, resolution=RESOLUTION, seed=SEED)
    all_members = {node for c in communities for node in c}
    assert all_members == set(G.nodes()), "fallback dropped hubs"
    assert {frozenset(c) for c in communities} == expected, (
        "fallback partition differs from committed (native-produced) clusters"
    )

    # Warm path — what the workflow actually uses: seed from the committed
    # artifact, exactly like build.py clusters (warm-start from _clusters.json).
    hub_to_comm = {
        hub: i for i, c in enumerate(_committed_clusters()) for hub in c["members"]
    }
    warm = [hub_to_comm.get(n, len(hub_to_comm)) for n in sorted(G.nodes())]
    warm_comms = _run_leiden(
        G, resolution=RESOLUTION, seed=SEED, initial_membership=warm
    )
    assert {frozenset(c) for c in warm_comms} == expected, (
        "warm-start fallback partition differs from committed clusters"
    )


def test_dependency_free_cluster_build_is_deterministic(monkeypatch):
    """Same seed -> identical partition, so the dependency-free path keeps the
    pipeline's reproducibility guarantee (same as native Leiden)."""
    _block_native(monkeypatch)

    from _build.clusters import RESOLUTION, SEED, build_hub_graph, _run_leiden

    G, *_ = build_hub_graph(verbose=False)
    assert _run_leiden(G, resolution=RESOLUTION, seed=SEED) == _run_leiden(
        G, resolution=RESOLUTION, seed=SEED
    )
