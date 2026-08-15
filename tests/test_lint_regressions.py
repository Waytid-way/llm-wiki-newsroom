"""Audit regression target tests — catches recurrences of the "copy then edit only
one side" class, such as divergent lint verdicts and F4 lint-ification."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_w2_unmeasurable_is_pass_in_both_paths():
    """A2/F5 regression — an unmeasurable body is PASS (displayed as n/a) identically for L2-3 and L2-4.

    Previously: L2-3 serialized inf→None→⚠️, while L2-4 gave inf→✅, opposite verdicts for the same state.
    """
    import overview  # tools/_lint/ — includes manifest/skill loading (assumes the repo)

    m = {
        "total": 200, "lead_density": 1.0, "body_density": 0.0,
        "lead_body_ratio": None,  # serialized representation of inf = unmeasurable
        "dup_total": 0, "contradiction_refs": 1,
        "r1_hot": [], "r2_violations": [], "b1_hits": [],
        "l1_violations": [], "l2_violations": [], "l3_violations": [],
        "s6_long": [], "s6_para_anti": [],
        "g1_grade_meta": 99, "g2_cite_type_meta": 99,
        "duplicates": [],
    }
    lines = overview._format_metrics_line(m)
    w2_segment = next(seg for seg in lines[0].split("  ") if seg.startswith("W2"))
    assert "ratio=n/a" in w2_segment and "✅" in w2_segment


def test_paragraph_count_is_module_level_single_definition():
    """F5 regression — prevent recurrence of nested duplication (2 copies) of _paragraph_count."""
    import overview

    src = (ROOT / "tools" / "_lint" / "overview.py").read_text(encoding="utf-8")
    assert src.count("def _paragraph_count") == 1
    assert overview._paragraph_count("a\n\nb\n\nc") == 3
    assert overview._paragraph_count("") == 1  # minimum 1 (denominator protection)


def test_skeleton_overview_single_source_of_truth():
    """C29 — `_skeleton_overview` was byte-identical copies in the builder
    (`_build/clusters.py`, which writes the skeleton) and the lint SoT
    (`_lint/overview.py`, which checks it). Hoisted into _lib: both modules
    must consume the shared copy and neither may re-inline it, or a future
    edit to one side diverges and the lint flags the builder's own product."""
    from _build import clusters as C
    from _lib import _skeleton_overview
    import overview

    assert C._skeleton_overview is _skeleton_overview
    assert overview._skeleton_overview is _skeleton_overview

    for rel in ("tools/_build/clusters.py", "tools/_lint/overview.py"):
        src = (ROOT / rel).read_text(encoding="utf-8")
        assert "def _skeleton_overview" not in src, (
            f"{rel} re-inlined the shared skeleton (import it from _lib)"
        )

    # The shared copy still emits a schema-complete skeleton.
    skel = _skeleton_overview({"name": "Test Cluster", "slug": "test-cluster"})
    assert "## Recent Changes" in skel and "## Adjacent Domains & Scope" in skel
    assert skel.startswith("---\n")


def test_demotion_excludes_prose_embedded_hub(tmp_path):
    """measurement-root regression — a hub embedded only in overview/synthesis/timeline/trail
    must be treated as nav-inbound and excluded from demotion candidates even when it rides on no graph edge.

    Previously (2026-06): the graph build did not emit prose-layer origin edges, so a hub embedded
    only in an overview (Appier, Similarweb, etc.) never saw its nav in the demotion lint and
    recurred as a false-strong demotion candidate every sweep. Fixed by scanning `_prose_nav_stems` directly.
    """
    import hub_demotion

    d = tmp_path / "entities"
    d.mkdir()
    hub = d / "테스트오펀.md"
    hub.write_text(
        '---\ntitle: "테스트오펀"\ntype: entity\nkind: org\n'
        "sources: [single-src]\n---\n## Overview\n짧은 본문.\n",
        encoding="utf-8",
    )
    empty_graph = {"inbound": {}, "cluster": {}}

    # no prose embed → detected as an isolated demotion candidate (strong)
    iss, _ = hub_demotion._check_directory(d, "entities", empty_graph, set(), set())
    assert any("테스트오펀" in i for i in iss)

    # the same hub embedded in the prose layer → excluded as nav-inbound (0 omissions)
    iss2, _ = hub_demotion._check_directory(
        d, "entities", empty_graph, set(), {"테스트오펀"}
    )
    assert not any("테스트오펀" in i for i in iss2)


def test_meta_lint_regex_hoisting_check_active():
    """F4 regression — the shared-regex redefinition detection check is alive in the meta lint,
    and there is currently no redefinition in tools/."""
    proc = subprocess.run(
        [sys.executable, "tools/lint.py", "meta"],
        capture_output=True, text=True, encoding="utf-8", cwd=ROOT, timeout=300,
    )
    assert proc.returncode in (0, 1)  # 1 = clone-environment artifacts (.claude/memory/, etc.) allowed
    assert "OK - shared FRONTMATTER*/WIKILINK*/AUTO* regexes defined only in _lib" in proc.stdout


def test_overview_sources_total_matches_catalog_membership():
    """Reground regression — the overview AUTO:SOURCES "N total" and the source
    catalog must apply ONE membership rule.

    Previously `_group_sources_by_cluster` fell back to the primary cluster for a
    source below threshold in every cluster, while `_render_sources_block` counted
    only `weight >= threshold` — so an orphan source appeared in the catalog but
    was missing from the overview total. Both numbers are generated, so no author
    could reconcile them by editing a page; the fix belongs to the build. This
    pins the two rules together, because a membership rule duplicated across two
    functions diverges again (copyeditor.md § Risk Mitigation Design)."""
    from _build import clusters as C

    clusters_data = {
        "source_weight_threshold": 0.3,
        "clusters": [{"slug": "c1", "name": "Cluster One"},
                     {"slug": "c2", "name": "Cluster Two"}],
        "source_assignments": {
            "sources/strong.md": {"primary": "c1", "weights": {"c1": 0.9, "c2": 0.4}},
            # below threshold everywhere → catalog falls back to its primary (c1)
            "sources/orphan.md": {"primary": "c1", "weights": {"c1": 0.2, "c2": 0.1}},
        },
    }
    sources = [
        ("Strong", "sources/strong.md", "", "", "2026-01-01", ""),
        ("Orphan", "sources/orphan.md", "", "", "2026-01-02", ""),
    ]

    cluster_files, _ = C._group_sources_by_cluster(sources, clusters_data)
    for cluster in clusters_data["clusters"]:
        slug = cluster["slug"]
        m = re.search(r"(\d+) total", C._render_sources_block(cluster, clusters_data))
        assert m, f"cluster {slug}: rendered block has no total"
        assert int(m.group(1)) == len(cluster_files.get(slug, [])), (
            f"cluster {slug}: overview total {m.group(1)} != "
            f"catalog membership {len(cluster_files.get(slug, []))}"
        )

    # The orphan is exactly what the divergence used to hide.
    assert len(cluster_files["c1"]) == 2


def test_f2_claim_stat_checked_at_every_occurrence(tmp_path, monkeypatch):
    """Reground regression — a stale restatement of the canonical claim total
    mid-body must fail F2, not only a stale head sentence.

    A delta-only re-ground edits the head and leaves earlier copies behind; the
    previous head-only `.search()` passed such a document."""
    import contradiction as CT

    md = tmp_path / "contradiction.md"

    def _write(head_n, body_n):
        md.write_text(
            f"# Contradictions\n\n"
            f"**{head_n} source-to-source contradictions** across the corpus.\n\n"
            f"## Synopsis\n\n"
            f"Restated later: **{body_n} source-to-source contradictions**.\n",
            encoding="utf-8",
        )

    monkeypatch.setattr(CT, "CONTRADICTIONS_MD_PATH", md)

    # Assert on the claim-stat drift specifically: this fixture is a minimal
    # document, so unrelated criteria (S1 sections, the theme stat) fail anyway.
    _write(7, 7)  # every occurrence agrees with the SoT
    issues, _ = CT._check_contradictions_md(set(), set(), 7, 0)
    assert not any("claims declared" in i for i in issues), issues

    _write(7, 5)  # head correct, mid-body stale — the case head-only checking missed
    issues, _ = CT._check_contradictions_md(set(), set(), 7, 0)
    assert any("claims declared=5 actual=7" in i for i in issues), issues


def test_reground_status_surfaces_superseded_but_open_claims():
    """Reground follow-up trigger — a claim whose own source reports the dispute
    settled (`type: superseded`) while it stays `status: open` is surfaced; every
    other type/status combination stays silent (the surface must be zero-FP)."""
    import contradiction as CT

    assert CT._reground_status_line([]) is None
    assert CT._reground_status_line([{"id": "a", "type": "soft", "status": "open"}]) is None
    assert CT._reground_status_line(
        [{"id": "b", "type": "superseded", "status": "resolved"}]
    ) is None

    line = CT._reground_status_line([
        {"id": "c1", "type": "superseded", "status": "open"},
        {"id": "c2", "type": "real", "status": "open"},
    ])
    assert line is not None
    assert "1 superseded claim(s) still open" in line
    assert "c1" in line and "c2" not in line


def test_valid_link_target_set_has_one_owner(monkeypatch):
    """The "valid wikilink target" set was implemented three times (graph
    structure · link_candidates · the write-time hook). When only one copy
    changed, one check called a link broken and another did not.

    A fake stem is injected rather than asserting the import binding — a test
    that only checks `module.helper is _lib.helper` still passes after someone
    re-inlines the glob at the call site, which is the recurrence this guards.
    """
    import link_candidates
    from pathlib import Path as _P

    sentinel = {"__ONLY_FROM_THE_SHARED_HELPER__": _P("x.md")}
    monkeypatch.setattr(link_candidates, "wiki_page_paths", lambda: sentinel)
    assert link_candidates._index_pages() == sentinel


def test_r1_english_token_boundary():
    """R1 counts a numeric token only where the body actually says it.

    The word units are closed by `\\b`, but `%` was not: the phrase `50%+1 rule`
    yielded a bare `50%` token, so one phrase repeated three times read as a hot
    figure. A percentage followed by a digit or `+` is part of a longer token,
    not a standalone figure.
    """
    from _lint.overview import _r1_hot_tokens

    def toks(t):
        return dict(_r1_hot_tokens(t))

    assert toks("The 50%+1 rule. Under the 50%+1 rule. Debating the 50%+1 rule.") == {}
    # genuine repetition still counts — trailing punctuation and prose both
    assert toks("Share of 94%. About 94% now. Reaching 94%.") == {"94%": 3}
    assert toks("7 billion params. 7 billion again. 7 billion more.") == {"7 billion": 3}


def test_r1_korean_token_boundary(monkeypatch):
    """The same boundary rule under WIKI_LANG=ko — a counter that swallows the
    following syllable invents tokens: `2분기`→`2분`, `2조 4,585억`→`2조`,
    `5대 시중은행`→`5대`. Particles (`94%에`) must still count, so the block is
    scoped to the counter, not to any trailing Hangul.
    """
    import _lint.overview as O

    monkeypatch.setattr(O, "korean_mode", lambda: True)

    def toks(t):
        return dict(O._r1_hot_tokens(t))

    assert toks("2분기 실적. 2분기 매출. 2분기 이익.") == {}
    assert toks("2조 4,585억 원. 2조 2,254억 원. 2조 6,381억 원.") == {}
    assert toks("50%+1 룰이다. 50%+1 룰 적용. 50%+1 룰 논의.") == {}
    assert toks("점유율 94%. 94% 수준. 94%에 달한다.") == {"94%": 3}
    assert toks("9시간 55분. 55분 중단. 55분 지연.") == {"55분": 3}


def _cit_checks():
    """Load the scholarly-citation skill detectors the same way source.py does."""
    import importlib.util

    path = ROOT / ".claude" / "skills" / "scholarly-citation" / "checks.py"
    spec = importlib.util.spec_from_file_location("cit_checks_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_g2_weasel_boundary_keeps_named_claimants():
    """G2 recalibration regression — a denylist without a case boundary drops the very
    names the guideline offers as correct examples (`Free Software Foundation` ends in
    `foundation`). In English the discriminator is the final word's case: a named source
    capitalizes it, a weasel does not.
    """
    w = _cit_checks()._is_weasel_head

    for named in (
        "Free Software Foundation", "Software Freedom Conservancy",
        "Open Source Initiative", "Government Accountability Office",
        "Electronic Frontier Foundation", "The Linux Foundation",
        "AMD", "Ai2", "Pleias", "Bradley Kuhn",
    ):
        assert not w(named), f"named claimant dropped as weasel: {named!r}"

    for weasel in (
        "the government", "the industry", "the foundation", "the community",
        "industry sources", "Government sources", "experts", "the media", "",
    ):
        assert w(weasel), f"weasel let through: {weasel!r}"


def test_g2_accepts_plain_name_rejects_evasion_and_bloat():
    """G2 measures whether the claimant is *named*, not whether it is linked (WP:ASF).
    Plain text passes when the speaker has no page; it fails when a page does exist
    (link evasion) or when content is pushed into the head slot.
    """
    cit = _cit_checks()
    page_index = {"Meta": ("entities/Meta.md", "entity")}

    def g2(line):
        body = f"## Key Claims\n{line}\n\n## Connections\n"
        return cit.evaluate_citation(
            body, page_index=page_index, section_titles_fn=lambda rel: set()
        )["g2"]

    # plain-text name, no page → PASS and counted as plain
    ok = g2("- [fact] Pleias — released a fully open multilingual dataset")
    assert ok[0] is True and ok[4] == 1

    # wikilink → PASS, not counted as plain
    linked = g2("- [fact] [[Meta]] — released Llama under a custom licence")
    assert linked[0] is True and linked[4] == 0

    # plain text naming an existing page → link evasion → FAIL
    assert g2("- [fact] Meta — released Llama under a custom licence")[0] is False

    # content pushed into the head slot → FAIL
    bloat = "x" * (cit.CLAIMANT_HEAD_MAX + 1)
    assert g2(f"- [fact] {bloat} — said something")[0] is False

    # anonymous subject → FAIL even in plain text
    assert g2("- [fact] the industry — expects consolidation")[0] is False


def test_a2_exempts_plain_speaker_and_fails_broken_link():
    """A2 judges whether a speaker is named and whether a link resolves — not whether
    a link is present. A plain-text speaker leaves the denominator (the page may be
    below the creation threshold); a link to a missing page fails.
    """
    cit = _cit_checks()
    page_index = {"Mozilla": ("entities/Mozilla.md", "entity")}

    def a2(quote):
        body = f"## Key Quotes\n{quote}\n\n## Connections\n"
        return cit.evaluate_citation(
            body, page_index=page_index, section_titles_fn=lambda rel: set()
        )["a2"]

    # (pass, linked-and-valid, judged) per input class. Every class below was surfaced by
    # review of this check; the separator rule (the first spaced dash between an
    # even-indexed quote mark and the next mark) is the only one of five candidates that
    # gets all of them right — the four it replaces are enumerated in checks.py.
    cases = [
        # linked speaker, plain speaker, and the two failure modes
        ('> "q" — [[Mozilla]]', (True, 1, 1)),
        ('> "q" — Bruce Perens, OSI co-founder', (True, 0, 0)),
        ('> "q" — [[Perens]]', (False, 0, 1)),          # broken link (pre-fix: passed)
        ('> "q" — Mozilla', (False, 0, 1)),             # evasion, as G2 reads the claimant slot
        # nobody named — none of these may exempt themselves
        ('> "an unattributed line"', (False, 0, 1)),
        ('> "an unattributed line" — ', (False, 0, 1)),
        ('> "the OSD — 26 years old — applies"', (False, 0, 1)),
        ('> "they call it "open source" — a stretch — at best"', (False, 0, 1)),
        ('> "q text here" 2024-10-28', (False, 0, 1)),  # unspaced hyphen is not a separator
        ('> "q text here" (op-ed)', (False, 0, 1)),
        ('> "q text unclosed — [[Mozilla]]', (False, 0, 1)),
        # a link inside the quotation body is never the speaker
        ('> "the OSD — 26 years — applies to [[Mozilla]]" — Perens, co-founder', (True, 0, 0)),
        ('> "— the OSD applies to [[Mozilla]]" — Perens, co-founder', (True, 0, 0)),
        # …nor may it launder a broken speaker link, or a trailing segment
        ('> "they call it "open source" — for [[Mozilla]]" — [[Perens]]', (False, 0, 1)),
        ('> "q" — [[Perens]] — via [[Mozilla]]', (False, 0, 1)),
        ('> "q" — [[Mozilla]] — 2024-10-28', (True, 1, 1)),
        # forms that must stay judged: anchor, alias, en dash, hyphen, nested body term
        ('> "q" — [[Mozilla#Key Quotes]]', (True, 1, 1)),
        ('> "q" — [[Mozilla|the Mozilla Foundation]]', (True, 1, 1)),
        ('> "q" – [[Mozilla]]', (True, 1, 1)),
        ('> "q" - [[Mozilla]]', (True, 1, 1)),
        ('> "q about "openness" here" — [[Mozilla]]', (True, 1, 1)),
        # a quoted work title inside the attribution does not swallow it
        ('> "q" — [[Mozilla]], author of "The OSD"', (True, 1, 1)),
        ('> "q" — Perens, author of "The OSD"', (True, 0, 0)),
        # text between the closing mark and the separator is not "naming nobody"
        ('> "q" (emphasis added) — [[Mozilla]]', (True, 1, 1)),
        ('> "q," she said — Perens, co-founder', (True, 0, 0)),
    ]
    for quote, expected in cases:
        assert a2(quote) == expected, quote

    # several quotes in one section are scored per line: of the first four classes,
    # three are judged (linked·broken·evasion) and one is exempt (plain speaker)
    assert a2("\n".join(q for q, _ in cases[:4])) == (False, 1, 3)


def test_hub_body_degrades_when_skill_unavailable(tmp_path):
    """C72 — an unguarded import-time manifest read + skill exec can crash ALL of
    lint.py (missing checks.py / manifest key / renamed fn → AttributeError). The
    load must be guarded: on failure print a warning to stderr and degrade to
    empty results so lint survives.

    The failure is injected into a fresh interpreter: the skill spec is pointed
    at a stub module WITHOUT the manifest-declared function name, which is the
    renamed-function variant of the crash. Import must succeed, the module must
    hold `enc_skill is None`, and `_check_body` must return no issues.
    """
    stub = tmp_path / "stub_checks.py"
    stub.write_text("def unrelated(): pass\n", encoding="utf-8")
    code = f"""
import importlib.util, sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "tools"))
sys.path.insert(0, str(Path.cwd() / "tools" / "_lint"))

_orig_spec = importlib.util.spec_from_file_location
def _sabotaged(name, location):
    if name == "enc_checks_hub":
        return _orig_spec(name, r"{stub}")
    return _orig_spec(name, location)
importlib.util.spec_from_file_location = _sabotaged

import hub_body
assert hub_body.enc_skill is None, hub_body.enc_skill
issues = hub_body._check_body("# h\\n\\nbody", Path("entities/Fake.md"), "entities")
assert issues == [], issues
print("DEGRADED_OK")
"""
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, encoding="utf-8", cwd=ROOT, timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    assert "DEGRADED_OK" in proc.stdout
    assert "WARNING" in proc.stderr


def test_link_candidates_broken_detection_uses_lib_unresolved_wikilinks(monkeypatch, tmp_path):
    """C73 — broken-target detection must flow through `_lib.unresolved_wikilinks`
    (single SoT: strips code, identical target normalization to structure.py).
    A hand-rolled `LINK_RE.findall` copy diverges: it counted links inside code
    fences and applied different target normalization.
    """
    import link_candidates

    wiki = tmp_path / "wiki"
    (wiki / "entities").mkdir(parents=True)
    page = wiki / "entities" / "Seed.md"
    page.write_text(
        "See [[Missing]] and [[Existing]] and `[[CodeBroken]]` and\n"
        "```\n[[FenceBroken]]\n```\n",
        encoding="utf-8",
    )
    existing = wiki / "entities" / "Existing.md"
    existing.write_text("x\n", encoding="utf-8")

    pages = {"Seed": page, "Existing": existing}
    bl = tmp_path / "backlinks.json"
    bl.write_text(
        json.dumps({"Seed": [{"from": "entities/Seed.md"} for _ in range(6)]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(link_candidates, "WIKI", wiki)
    monkeypatch.setattr(link_candidates, "BACKLINKS_PATH", bl)
    monkeypatch.setattr(link_candidates, "hub_stems", lambda: {"Seed"})
    monkeypatch.setattr(link_candidates, "_index_pages", lambda: pages)

    results = link_candidates._find(min_seeds=1)
    targets = {r["target"] for r in results}
    assert "Missing" in targets
    assert "Existing" not in targets          # resolves → not broken
    assert "CodeBroken" not in targets        # inline-code strip via the SoT helper
    assert "FenceBroken" not in targets       # fenced-code strip via the SoT helper


def test_suggestions_json_caps_link_candidates_without_top(monkeypatch, capsys):
    """C50 — the JSON branch must cap link_candidates at DEFAULT_TOP_RESULTS even
    when --top is absent, mirroring the text branch. Previously the JSON doc
    carried the full unbounded list while text mode capped at 30.
    """
    import suggestions

    fake = [
        {"target": f"T{i}", "seed_count": 2, "total_mentions": 2,
         "seeds": ["a", "b"], "appears_in": ["p"]}
        for i in range(50)
    ]
    monkeypatch.setattr(suggestions.link_candidates, "_find", lambda min_seeds=2: fake)
    monkeypatch.setattr(
        suggestions.text_candidates, "_candidates",
        lambda min_mentions=10, min_pages=5, top=50: ({"min_mentions": 10, "min_pages": 5, "candidates": []}, 0),
    )

    suggestions.run(json_out=True)
    doc = json.loads(capsys.readouterr().out)
    assert len(doc["link_candidates"]["results"]) == suggestions.link_candidates.DEFAULT_TOP_RESULTS

    suggestions.run(json_out=True, top=3)
    doc = json.loads(capsys.readouterr().out)
    assert len(doc["link_candidates"]["results"]) == 3


def test_aggregate_rewrite_block_uses_non_fragmentary_theme_count(capsys):
    """C52 — the aggregate rewrite block must hand Claude the NON-fragmentary
    theme count (the F2 gate's comparison basis) and state the `other-fragmentary`
    exclusion explicitly; previously it printed len(themes) including the
    fragmentary bucket, so Claude wrote a count the gate rejects.
    """
    import contradiction as CT

    CT._emit_rewrite_block_aggregate(claim_count=12, theme_count=5)
    out = capsys.readouterr().out
    assert "themes=5 (non-fragmentary" in out
    assert "other-fragmentary" in out
    assert "5 NON-fragmentary themes" in out


def test_staleness_signals_shared_owner():
    """C51 — the timestamp staleness comparisons (uncommitted edits +
    commit-date drift) must be defined exactly once, inside _staleness_signals,
    and consumed by both is_themes_json_stale and _check_freshness. A second
    inline copy drifts when only one side changes.
    """
    src = (ROOT / "tools" / "_lint" / "contradiction_theme.py").read_text(encoding="utf-8")
    assert src.count("def _staleness_signals") == 1
    # both consumers route through the helper — no inline `derived_at <` re-checks
    assert src.count("uncommitted, commit_date = _staleness_signals(") == 2


def test_staleness_signals_behavior(monkeypatch):
    """C51 — _staleness_signals returns the effective signals the consumers
    format: (uncommitted, commit_date) with the drift comparisons applied."""
    import contradiction_theme as CTh

    doc = {"derived_at": "2026-08-10"}
    today = "2026-08-16"

    monkeypatch.setattr(CTh, "_claims_has_uncommitted", lambda: True)
    monkeypatch.setattr(CTh, "_claims_last_change_date", lambda: "2026-08-15")
    assert CTh._staleness_signals(doc, today) == (True, "2026-08-15")

    monkeypatch.setattr(CTh, "_claims_has_uncommitted", lambda: False)
    assert CTh._staleness_signals(doc, today) == (False, "2026-08-15")

    monkeypatch.setattr(CTh, "_claims_last_change_date", lambda: "2026-08-01")
    assert CTh._staleness_signals(doc, today) == (False, None)


def test_check_freshness_consumes_shared_signals(monkeypatch):
    """C51 — _check_freshness formats its advisory from the shared signals and
    does not re-implement the comparisons."""
    import contradiction_theme as CTh

    doc = {"derived_at": "2026-08-10"}
    monkeypatch.setattr(CTh, "_staleness_signals", lambda d, today: (True, None))
    line = CTh._check_freshness(doc)
    assert line is not None and "uncommitted edits" in line

    monkeypatch.setattr(CTh, "_staleness_signals", lambda d, today: (False, "2026-08-15"))
    line = CTh._check_freshness(doc)
    assert line is not None and "last changed in commit on 2026-08-15" in line

    monkeypatch.setattr(CTh, "_staleness_signals", lambda d, today: (False, None))
    assert CTh._check_freshness(doc) is None


def test_is_themes_json_stale_consumes_shared_signals(monkeypatch, tmp_path):
    """C51 — is_themes_json_stale formats its gate message from the shared
    signals, so the hard gate and the advisory can never drift apart."""
    import contradiction_theme as CTh

    themes = tmp_path / "themes.json"
    themes.write_text(json.dumps({"derived_at": "2026-08-10", "source_count": 3}), encoding="utf-8")
    claims = tmp_path / "claims.json"
    claims.write_text(json.dumps([{"id": "a"}, {"id": "b"}, {"id": "c"}]), encoding="utf-8")
    monkeypatch.setattr(CTh, "THEMES_JSON", themes)
    monkeypatch.setattr(CTh, "CLAIMS_JSON", claims)

    monkeypatch.setattr(CTh, "_staleness_signals", lambda d, today: (True, None))
    stale, reason = CTh.is_themes_json_stale()
    assert stale and "uncommitted edits" in reason

    monkeypatch.setattr(CTh, "_staleness_signals", lambda d, today: (False, "2026-08-15"))
    stale, reason = CTh.is_themes_json_stale()
    assert stale and "last changed on 2026-08-15" in reason

    monkeypatch.setattr(CTh, "_staleness_signals", lambda d, today: (False, None))
    assert CTh.is_themes_json_stale() == (False, None)

def test_a2_name_role_attribution_is_not_evasion():
    """A2 (GG8b-1) — a 'Name, Role' attribution is exempt from the link-evasion
    flag even when the name has a page: the org in a role line is not the speaker
    ('Matt Garman, AWS CEO' is not AWS — cit.speaker-link note), so name-matching
    would manufacture misattribution. A bare name with a page stays evasion."""
    cit = _cit_checks()
    page_index = {"Matt Garman": ("entities/Matt Garman.md", "entity")}

    def a2(quote):
        body = f"## Key Quotes\n{quote}\n\n## Connections\n"
        return cit.evaluate_citation(
            body, page_index=page_index, section_titles_fn=lambda rel: set()
        )["a2"]

    # 'Name, Role' with a page for the name → exempt, not evasion
    assert a2('> "q" — Matt Garman, AWS CEO') == (True, 0, 0)
    # lowercase role keyword ('co-founder') is title-ish too
    assert a2('> "q" — Matt Garman, co-founder') == (True, 0, 0)
    # a bare name with a page → still evasion
    assert a2('> "q" — Matt Garman') == (False, 0, 1)


def test_g2_accepts_plain_claimant_without_em_dash():
    """G2 (GG8b-2) — a plain claimant needs no em dash separator: '[fact] Matt
    Garman, AWS CEO said …' names the claimant in the head position, so the slot
    is filled (cit.claimant-link: plain text with their role is the terminal form
    below the page-creation threshold). A dash right after the grade marker
    ('[fact] — Matt Garman said …') must not empty the slot either."""
    cit = _cit_checks()
    page_index = {"Matt Garman": ("entities/Matt Garman.md", "entity")}

    def g2(line):
        body = f"## Key Claims\n{line}\n\n## Connections\n"
        return cit.evaluate_citation(
            body, page_index=page_index, section_titles_fn=lambda rel: set()
        )["g2"]

    # plain claimant, no dash → PASS, counted as plain
    ok = g2("- [fact] Matt Garman, AWS CEO said the plan was dropped")
    assert ok[0] is True and ok[4] == 1
    # dash before the claimant → PASS, counted as plain
    ok2 = g2("- [fact] — Matt Garman said the plan was dropped")
    assert ok2[0] is True and ok2[4] == 1
    # the screening still applies: an existing page in the head slot is evasion
    assert g2("- [fact] Matt Garman — said the plan was dropped")[0] is False
