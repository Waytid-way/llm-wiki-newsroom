"""Pure-Python Leiden community detection (RBConfiguration quality).

Fallback backend for `tools/_build/clusters.py` and `tools/_lint/cluster_drift.py`
when `leidenalg`/`python-igraph` are not installed (e.g. Android/Termux where the
C extensions are painful to build). Implements Traag, Waltman & van Eck (2019),
"From Louvain to Leiden: guaranteeing well-connected communities", restricted to
the RBConfiguration quality function (modularity with resolution parameter — the
same function the repo's `_run_leiden` docstring calls "Louvain-equivalent", so
`resolution` values stay directly comparable to prior Leiden/Louvain runs).

Deterministic by construction: node order = sorted node ids (matching the igraph
conversion in `to_igraph`), RNG seeded. Mirrors the API surface the two modules
use from leidenalg:

    from _leiden_py import find_partition
    communities, quality = find_partition(G_nx, resolution=1.0, seed=0,
                                          initial_membership=None)

`initial_membership` (warm start) is a length-N list of community indices in
sorted-node order, exactly like `leidenalg`'s. `communities` is a list of sets
of node NAMES (the same shape `_run_leiden` returns).

RBConfiguration quality (undirected, weighted, resolution gamma):

    Q = sum_c [ inc_c / m - gamma * (deg_c / (2m))^2 ]

  inc_c = internal edge weight of community c (self-loops counted once)
  deg_c = sum of weighted degrees in c (self-loops counted twice)
  m     = total edge weight (each edge once, self-loops once)

Single-node move delta (i from c to d; k_id = weight of i's edges into d,
k_ic likewise into c, k_i = weighted degree of i, self-loop w_ii):

    dQ = (k_id - k_ic + 2*w_ii)/m
         - gamma * k_i * (k_i - deg_c + deg_d) / (2 m^2)

Implementation: flat multi-pass — local moving (never decreases Q), then
Leiden refinement (splits each community into connected sub-communities via
the same local-moving restricted to same-community neighbors), repeated until
stable. No graph aggregation needed: each pass works on the original
adjacency, so self-loops never arise and the delta stays exact.
"""

from __future__ import annotations

import random
from collections import defaultdict


def _quality(m: float, deg: list[float], comm: list[int], self_w: list[float],
             adj: list[dict[int, float]], resolution: float) -> float:
    c_deg: dict[int, float] = defaultdict(float)
    c_inc: dict[int, float] = defaultdict(float)
    for i in range(len(comm)):
        c_deg[comm[i]] += deg[i]
    for i in range(len(comm)):
        c_inc[comm[i]] += self_w[i]  # self-loop counted once
        for j, w in adj[i].items():
            if j > i and comm[j] == comm[i]:
                c_inc[comm[i]] += w  # each undirected edge once
    return sum(
        inc / m - resolution * (c_deg[c] / (2 * m)) ** 2
        for c, inc in c_inc.items()
    )


def _local_moving(adj, self_w, deg, comm, m, resolution, rng) -> bool:
    """One pass of local moving (RBConfiguration). Returns True if any node moved."""
    n = len(adj)
    c_deg: dict[int, float] = defaultdict(float)
    c_inc: dict[int, float] = defaultdict(float)
    for i in range(n):
        c_deg[comm[i]] += deg[i]
    for i in range(n):
        c_inc[comm[i]] += self_w[i]
        for j, w in adj[i].items():
            if j > i and comm[j] == comm[i]:
                c_inc[comm[i]] += w

    moved = False
    order = list(range(n))
    rng.shuffle(order)
    for i in order:
        c = comm[i]
        k_i = deg[i]
        w_ii = self_w[i]
        k_into: dict[int, float] = defaultdict(float)
        for j, w in adj[i].items():
            k_into[comm[j]] += w
        k_ic = k_into.get(c, 0.0) + 2 * w_ii  # self-loop counts twice in k
        best_d, best_gain = c, 0.0
        for d, k_id in k_into.items():
            if d == c:
                continue
            deg_d = c_deg[d]
            deg_c = c_deg[c]  # current (with i still inside)
            gain = (k_id - k_ic + 2 * w_ii) / m \
                - resolution * k_i * (k_i - deg_c + deg_d) / (2 * m * m)
            if gain > best_gain:
                best_d, best_gain = d, gain
        if best_d != c and best_gain > 0:
            c_inc[c] -= k_ic - w_ii   # edges lost to c (self stays with i, once)
            c_inc[best_d] += k_into.get(best_d, 0.0) + w_ii
            c_deg[c] -= k_i
            c_deg[best_d] += k_i
            comm[i] = best_d
            moved = True
    return moved


def _refine(adj, self_w, deg, comm, m, resolution, rng) -> list[int]:
    """Leiden refinement: split each community into connected sub-communities
    by local moving restricted to nodes of the same base community (a node may
    only join a sub-community it shares an edge with — the well-connectedness
    guarantee). Returns new per-node community labels."""
    n = len(adj)
    sub = list(range(n))
    s_deg: dict[int, float] = defaultdict(float)
    s_inc: dict[int, float] = defaultdict(float)
    for i in range(n):
        s_deg[sub[i]] += deg[i]
    for i in range(n):
        s_inc[sub[i]] += self_w[i]
        for j, w in adj[i].items():
            if j > i and sub[j] == sub[i]:
                s_inc[sub[i]] += w

    order = list(range(n))
    rng.shuffle(order)
    for i in order:
        base = comm[i]
        k_i = deg[i]
        w_ii = self_w[i]
        cand: dict[int, float] = defaultdict(float)
        for j, w in adj[i].items():
            if comm[j] == base:
                cand[sub[j]] += w
        if not cand:
            continue
        cur = sub[i]
        k_ic = cand.get(cur, 0.0) + 2 * w_ii
        best_s, best_gain = cur, 0.0
        for s, k_is in cand.items():
            if s == cur:
                continue
            deg_s = s_deg[s]
            deg_c = s_deg[cur]
            gain = (k_is - k_ic + 2 * w_ii) / m \
                - resolution * k_i * (k_i - deg_c + deg_s) / (2 * m * m)
            if gain > best_gain:
                best_s, best_gain = s, gain
        if best_s != cur and best_gain > 0:
            s_inc[cur] -= k_ic - w_ii
            s_inc[best_s] += cand.get(best_s, 0.0) + w_ii
            s_deg[cur] -= k_i
            s_deg[best_s] += k_i
            sub[i] = best_s

    relabel: dict[int, int] = {}
    out = [0] * n
    for i in range(n):
        s = sub[i]
        if s not in relabel:
            relabel[s] = len(relabel)
        out[i] = relabel[s]
    return out


def find_partition(
    G,
    resolution: float = 1.0,
    seed: int | None = None,
    initial_membership: list[int] | None = None,
) -> tuple[list[set[str]], float]:
    """Leiden on a NetworkX weighted undirected graph.

    Returns (communities, quality): communities is a list of sets of node NAMES,
    quality is the RBConfiguration quality of the final partition.
    """
    nodes = sorted(G.nodes())
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    rng = random.Random(seed)

    adj, self_w, m = _build_structures(G, idx, n)
    if m <= 0:
        return [{x} for x in nodes], 0.0
    deg = [self_w[i] * 2 + sum(adj[i].values()) for i in range(n)]

    comm: list[int] = (
        list(initial_membership) if initial_membership is not None else list(range(n))
    )
    if len(comm) != n:
        raise ValueError(
            f"initial_membership length {len(comm)} != node count {n} (sorted order)"
        )

    for _pass in range(50):
        moved = _local_moving(adj, self_w, deg, comm, m, resolution, rng)
        refined = _refine(adj, self_w, deg, comm, m, resolution, rng)
        if refined == comm and not moved:
            break
        comm = refined

    quality = _quality(m, deg, comm, self_w, adj, resolution)
    groups: dict[int, list[str]] = defaultdict(list)
    for i, c in enumerate(comm):
        groups[c].append(nodes[i])
    return [set(v) for _, v in sorted(groups.items())], quality


def _build_structures(G, idx: dict, n: int):
    """(adj, self_w, m) — neighbor-weight maps, self-loop weights, total weight."""
    adj: list[dict[int, float]] = [{} for _ in range(n)]
    self_w = [0.0] * n
    m = 0.0
    for u, v, w in G.edges(data="weight", default=1.0):
        i, j = idx[u], idx[v]
        if i == j:
            self_w[i] += w
            m += w  # self-loop counted once
            continue
        adj[i][j] = adj[i].get(j, 0.0) + w
        adj[j][i] = adj[j].get(i, 0.0) + w
        m += w
    return adj, self_w, m


def quality_of(G, membership: list[int], resolution: float = 1.0) -> float:
    """RBConfiguration quality of an explicit membership (no optimization).

    Mirrors `leidenalg.RBConfigurationVertexPartition(graph,
    initial_membership=...).quality()` used by the drift check: evaluates the
    quality of the given partition as-is, without running local moving."""
    nodes = sorted(G.nodes())
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    adj, self_w, m = _build_structures(G, idx, n)
    if m <= 0:
        return 0.0
    if len(membership) != n:
        raise ValueError(
            f"membership length {len(membership)} != node count {n} (sorted order)"
        )
    deg = [self_w[i] * 2 + sum(adj[i].values()) for i in range(n)]
    return _quality(m, deg, list(membership), self_w, adj, resolution)
