"""Link-based page candidates — cross-cutting concept discovery.

Paired with text_candidates.py in the `suggestions` pipeline. Both surface
potential wiki pages that don't yet exist; this module scans LINKS
(broken wikilinks converging across hubs), the other scans TEXT
(frequent noun phrases in page bodies).

For each mid-popularity hub (5-25 backlinks), look at the broken
`[[wikilinks]]` inside its top backlink pages. A target that surfaces
across multiple seeds is a strong cross-cutting candidate.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from _lib import (  # noqa: E402
    read_text_cached,
    unresolved_wikilinks,
    WIKI,
    wiki_page_paths,
)
sys.path.insert(0, str(Path(__file__).parent))
from _hub_common import hub_stems  # noqa: E402

BACKLINKS_PATH = WIKI / "_backlinks.json"

DEFAULT_MIN_BL = 5
DEFAULT_MAX_BL = 25
DEFAULT_TOP_BL_PER_SEED = 8
DEFAULT_MIN_SEEDS = 2
DEFAULT_TOP_RESULTS = 30


def _index_pages() -> dict[str, Path]:
    """Delegates — this module held a second copy of the same construction
    (unified 2026-07-23). When only one copy changed, `graph structure` called a
    link broken while this check did not."""
    return wiki_page_paths()


def _find(
    min_seeds: int = DEFAULT_MIN_SEEDS,
) -> list[dict]:
    pages = _index_pages()
    hubs = hub_stems()
    backlinks: dict = (
        json.loads(BACKLINKS_PATH.read_text(encoding="utf-8"))
        if BACKLINKS_PATH.exists()
        else {}
    )

    page_broken: dict[str, list[str]] = {}
    for stem, path in pages.items():
        # C73 — broken-target detection flows through the _lib single SoT
        # (unresolved_wikilinks: strips code and applies identical target
        # normalization to `_lint/structure.py`). A hand-rolled copy here
        # diverged (missing code-strip / differing normalization) and the two
        # checks disagreed about what is broken.
        broken_here = unresolved_wikilinks(read_text_cached(path), set(pages))
        if broken_here:
            page_broken[f"{path.relative_to(WIKI).as_posix()}"] = broken_here

    target_seeds: dict[str, set[str]] = defaultdict(set)
    target_total: Counter = Counter()
    target_pages: dict[str, set[str]] = defaultdict(set)

    for hub in hubs:
        refs = backlinks.get(hub)
        if not isinstance(refs, list):
            continue
        if not (DEFAULT_MIN_BL <= len(refs) <= DEFAULT_MAX_BL):
            continue
        for ref in refs[:DEFAULT_TOP_BL_PER_SEED]:
            ref_path = ref.get("from") if isinstance(ref, dict) else None
            if not ref_path:
                continue
            for t in page_broken.get(ref_path, []):
                target_seeds[t].add(hub)
                target_total[t] += 1
                target_pages[t].add(ref_path)

    results = []
    for target, seeds in target_seeds.items():
        if len(seeds) < min_seeds:
            continue
        results.append({
            "target": target,
            "seed_count": len(seeds),
            "total_mentions": target_total[target],
            "seeds": sorted(seeds),
            "appears_in": sorted(target_pages[target])[:5],
        })
    results.sort(key=lambda x: (-x["seed_count"], -x["total_mentions"]))
    return results


def run(*, json_out: bool = False,
        min_seeds: int = DEFAULT_MIN_SEEDS,
        top: int = DEFAULT_TOP_RESULTS) -> int:
    results = _find(min_seeds=min_seeds)

    if json_out:
        print(json.dumps(
            {"min_seeds": min_seeds, "results": results},
            ensure_ascii=False,
            indent=2,
        ))
        return 0 if not results else 1

    print(
        f"Cross-cutting concept candidates "
        f"(broken targets across ≥{min_seeds} seeds): {len(results)}"
    )
    print(
        "(0 ≠ failure: it means broken-link targets do not currently "
        "cluster across multiple seeds — wiki is healthy.)"
    )
    for c in results[:top]:
        seeds_preview = ", ".join(c["seeds"][:5])
        more = f" (+{len(c['seeds'])-5} more)" if len(c["seeds"]) > 5 else ""
        print(f"  [[{c['target']}]]  seeds={c['seed_count']}  mentions={c['total_mentions']}")
        print(f"      via: {seeds_preview}{more}")

    return 0 if not results else 1
