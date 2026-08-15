"""Regression tests for the craft-skill deterministic checks (journalism-writing ·
encyclopedia-writing).

The scholarly-citation checks have their own home in test_lint_regressions.py
(_cit_checks); this file covers the other two lint-measured craft skills. Each
module is loaded the same way tools/_lint loads it — importlib.util with a
per-test module name so sibling loads never collide.
"""
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _load_skill_checks(skill: str, tag: str):
    path = REPO / ".claude" / "skills" / skill / "checks.py"
    spec = importlib.util.spec_from_file_location(f"{tag}_checks_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _jrn_checks():
    return _load_skill_checks("journalism-writing", "jrn")


def _enc_checks():
    return _load_skill_checks("encyclopedia-writing", "enc")


# ── journalism-writing ────────────────────────────────────────────────────────

def test_d6_bulleted_c_region_matches_prose_c():
    """D6 regression (GG8a-1) — a bulleted C position ('**C — Mediation**:\n-
    internal contradiction …') was truncated at its own first bullet, so the
    meta-critique keywords inside its bullets never registered. The C region must
    be bounded by the next dialectic label / H2, not the next bullet — bulleted
    and prose C must yield identical counts."""
    jrn = _jrn_checks()

    def body_for(c_block):
        return (
            "## Opposing Positions\n\n"
            "**Position A**:\nThesis body.\n\n"
            "**Position B**:\nAntithesis body.\n\n"
            + c_block
        )

    prose_c = (
        "**C — Mediation**:\n"
        "Both camps err — an internal contradiction sits at the core of A's "
        "self-serving framing, and interest bias runs through both sides at once.\n"
    )
    bulleted_c = (
        "**C — Mediation**:\n"
        "- internal contradiction sits at the core of A's framing\n"
        "- self-serving framing; interest bias runs through both sides at once\n"
    )

    m_prose = jrn.evaluate_contradiction_dialectic(
        body_for(prose_c), conflict_section=body_for(prose_c)
    )
    m_bulleted = jrn.evaluate_contradiction_dialectic(
        body_for(bulleted_c), conflict_section=body_for(bulleted_c)
    )

    assert m_bulleted["D6_c_meta_count"] > 0, "bulleted C must register its keywords"
    assert m_bulleted["D6_c_meta_count"] == m_prose["D6_c_meta_count"]
    assert set(m_bulleted["D6_c_meta_hits"]) == set(m_prose["D6_c_meta_hits"])


def test_d6_c_region_stops_at_next_label_and_h2():
    """D6 bound (GG8a-1) — the C region must not bleed into the next dialectic
    label, nor past the end of the opposing-positions section into the next H2."""
    jrn = _jrn_checks()
    section = (
        "## Opposing Positions\n\n"
        "**Position A**:\nA body.\n\n"
        "**Position B**:\nB body.\n\n"
        "**C — Mediation**:\n"
        "- internal contradiction in A\n"
        "\n**Position A**:\nA2 body.\n\n"
        "## Monitoring Points\n"
        "- internal contradiction also mentioned in the next section\n"
    )
    m = jrn.evaluate_contradiction_dialectic(section, conflict_section=section)
    # the second '**Position A**' bounds the C region, so only the first hit counts
    assert m["D6_c_meta_hits"] == ["internal contradiction"]


def test_qualifier_near_term_flagged():
    """T4/jrn.qualifier regression (GG8a-2) — 'in the near term' is a scope
    qualifier in the same family as 'in the short term' but was missing from
    QUALIFIER_PATTERNS, so a body that only qualified with it under-reported."""
    jrn = _jrn_checks()
    m = jrn.evaluate_contradiction_dialectic(
        "The forecast holds in the near term, on this metric.", conflict_section=""
    )
    assert m["T4_qualifiers"] == 2
    # hyphenated variant covered by the same pattern
    m2 = jrn.evaluate_contradiction_dialectic(
        "The forecast holds in the near-term.", conflict_section=""
    )
    assert m2["T4_qualifiers"] == 1


# ── encyclopedia-writing ──────────────────────────────────────────────────────

def test_abbr_gloss_exempts_product_license_names():
    """enc.abbr-gloss regression (GG8a-3) — product/license names (MIT·GPL·AGPL…)
    are proper names, not abbreviations needing a parenthetical gloss; real
    abbreviations are still flagged."""
    enc = _enc_checks()
    assert enc.find_abbr_violations(
        "The project ships under MIT and GPL; AGPL is reserved for the server "
        "component, and the SDK itself is BSD-licensed.\n"
    ) == []
    assert enc.find_abbr_violations("The report is licensed under the MIT License.\n") == []
    # a real abbreviation with no gloss is still flagged
    assert enc.find_abbr_violations("The OSDI board met on Friday.\n") == ["OSDI"]
