"""raw_file_refs tokenization regression (issue #11, C69).

The module docstring promises the trailing `md`/`pdf` extension token is
dropped from the token set, so a source_file that differs from the raw
basename only by extension (foo.md vs foo.pdf) must still match. The
`_TOKEN_SPLIT_RE` previously lacked '.', so 'foo.md' stayed one token and
the extension-drop never fired (Jaccard 0.0 -> NO MATCH instead of an
auto-fixable match).
"""
from raw_file_refs import _jaccard, _tokens


def test_md_pdf_extension_tokens_match():
    """foo.md and foo.pdf (same basename, different source format) tokenize
    to the same set — the documented extension-drop behavior."""
    md = _tokens("Open Source AI.md")
    pdf = _tokens("Open Source AI.pdf")
    assert md == pdf, f"tokens differ: {md!r} vs {pdf!r}"
    assert md == {"Open", "Source", "AI"}, f"unexpected tokens: {md!r}"


def test_extension_mismatch_still_detected():
    """Different basenames must still mismatch — the fix must not collapse
    distinct files into one."""
    a = _tokens("Open Source AI.md")
    b = _tokens("Open Source Models.md")
    assert a != b
    assert _jaccard(a, b) < 1.0
