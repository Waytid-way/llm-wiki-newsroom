"""`tools/_ingest/fetch_inbox.py` redirect-dedup unit tests — no network or disk.

Inbox-time dedup only looks at the original URL. fetch_one re-checks the *final*
URL resolved after redirects (r.url for PDF-via-redirect, _final_url for HTML)
against dedup_index, so a different short URL pointing at the same target is not
saved twice. Network functions are monkeypatched — the PDF sniff lives in
fetch_article.sniff_and_save_pdf (shared with fetch_article.main), so its
network/save calls are patched in the fetch_article namespace."""
import sys
from pathlib import Path

import pytest

# conftest puts tools/ on sys.path, but fetch_inbox lives under _ingest/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from _ingest import fetch_article as A  # noqa: E402
from _ingest import fetch_inbox as F  # noqa: E402


class _FakeStream:
    """safe_get_stream(...) context manager + response stub."""

    def __init__(self, url, ctype=""):
        self.url = url
        self.headers = {"Content-Type": ctype}

    def raise_for_status(self):
        pass

    def iter_content(self, chunk_size=1):
        yield b"%PDF-fake-body"

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_html_final_url_dedup_skips(monkeypatch):
    monkeypatch.setattr(F, "unwrap_share_wrapper", lambda u: u)
    monkeypatch.setattr(A, "is_pdf_url", lambda *a, **k: False)
    monkeypatch.setattr(A, "safe_get_stream", lambda *a, **k: _FakeStream("https://x.com/a"))
    monkeypatch.setattr(
        F, "fetch_html",
        lambda url, timeout=15: ("https://final.com/article?utm_source=x", "T", "D", "x" * 200),
    )
    monkeypatch.setattr(F, "save_markdown", lambda *a, **k: _fail_on_save())
    idx = {F.canonicalize_url("https://final.com/article"): "existing-slug"}
    status, path = F.fetch_one("https://short.link/xyz", dedup_index=idx)
    assert status == "SKIPPED:duplicate-of-existing-slug"
    assert path is None


def test_pdf_redirect_dedup_skips(monkeypatch):
    monkeypatch.setattr(F, "unwrap_share_wrapper", lambda u: u)
    # The sniff path classifies the *redirect-resolved* response: is_pdf_url
    # runs in the fetch_article namespace on (r.url, Content-Type).
    monkeypatch.setattr(A, "is_pdf_url", lambda u, ctype="": ctype == "application/pdf")
    monkeypatch.setattr(
        A, "safe_get_stream",
        lambda *a, **k: _FakeStream("https://cdn.com/file.pdf", "application/pdf"),
    )
    monkeypatch.setattr(A, "save_pdf", lambda *a, **k: _fail_on_save())
    idx = {F.canonicalize_url("https://cdn.com/file.pdf"): "existing-pdf"}
    status, path = F.fetch_one("https://short.link/pdf", dedup_index=idx)
    assert status == "SKIPPED:duplicate-of-existing-pdf"
    assert path is None


def test_html_no_false_skip_when_final_url_novel(monkeypatch):
    saved = Path("raw/NewsScrap/new.md")
    monkeypatch.setattr(F, "unwrap_share_wrapper", lambda u: u)
    monkeypatch.setattr(A, "is_pdf_url", lambda *a, **k: False)
    monkeypatch.setattr(A, "safe_get_stream", lambda *a, **k: _FakeStream("https://x.com/a"))
    monkeypatch.setattr(
        F, "fetch_html",
        lambda url, timeout=15: ("https://final.com/novel", "T", "D", "x" * 200),
    )
    monkeypatch.setattr(F, "save_markdown", lambda *a, **k: saved)
    idx = {F.canonicalize_url("https://final.com/other"): "existing-slug"}
    status, path = F.fetch_one("https://short.link/xyz", dedup_index=idx)
    assert status == "OK"
    assert path == saved


def test_html_saves_under_redirect_resolved_url(monkeypatch):
    """The save URL must be the same one dedup judged on — otherwise the stored
    key never matches and the article re-enters through its original URL."""
    seen = {}
    monkeypatch.setattr(F, "unwrap_share_wrapper", lambda u: u)
    monkeypatch.setattr(A, "is_pdf_url", lambda *a, **k: False)
    monkeypatch.setattr(A, "safe_get_stream", lambda *a, **k: _FakeStream("https://x.com/a"))
    monkeypatch.setattr(
        F, "fetch_html",
        lambda url, timeout=15: ("https://final.com/article", "T", "D", "x" * 200),
    )
    monkeypatch.setattr(
        F, "save_markdown",
        lambda url, *a, **k: seen.setdefault("url", url) and None or Path("raw/x.md"),
    )
    status, _ = F.fetch_one("https://short.link/xyz", dedup_index={})
    assert status == "OK"
    assert seen["url"] == "https://final.com/article"


def _fail_on_save():
    raise AssertionError("save_* must not be called when the final URL is a duplicate")


def test_direct_pdf_redirect_dedup_skips(monkeypatch):
    """C13 / issue #4: a direct .pdf URL that redirects must dedup on the
    *final* URL, like the sniff path — not on the pre-fetch URL. Two different
    shortlinks resolving to one PDF must not both download."""
    monkeypatch.setattr(F, "unwrap_share_wrapper", lambda u: u)
    # Direct-PDF URL (path ends .pdf) whose redirect resolves elsewhere.
    monkeypatch.setattr(
        A, "safe_get_stream",
        lambda *a, **k: _FakeStream("https://mirror.example.com/file.pdf", "application/pdf"),
    )
    monkeypatch.setattr(A, "save_pdf", lambda *a, **k: _fail_on_save())
    idx = {F.canonicalize_url("https://mirror.example.com/file.pdf"): "existing-pdf"}
    status, path = F.fetch_one("https://cdn.example.com/original.pdf", dedup_index=idx)
    assert status == "SKIPPED:duplicate-of-existing-pdf"
    assert path is None


def test_direct_pdf_saves_via_sniff_path(monkeypatch):
    """C13 / issue #4: a direct .pdf URL with a novel final URL still downloads
    and saves — routed through the same redirect-resolved sniff path as
    PDF-via-redirect URLs, and saved under the *final* URL (the same key the
    dedup judges on), not the pre-fetch URL."""
    seen = {}
    monkeypatch.setattr(F, "unwrap_share_wrapper", lambda u: u)
    monkeypatch.setattr(
        A, "safe_get_stream",
        lambda *a, **k: _FakeStream("https://mirror.example.com/file.pdf", "application/pdf"),
    )
    monkeypatch.setattr(
        A, "save_pdf",
        lambda url, body, title: seen.setdefault("url", url) and None or Path("raw/PDF/file.pdf"),
    )
    status, path = F.fetch_one("https://cdn.example.com/original.pdf", dedup_index={})
    assert status == "OK"
    assert path == Path("raw/PDF/file.pdf")
    assert seen["url"] == "https://mirror.example.com/file.pdf"


def test_main_archives_before_rewriting_inbox(tmp_path, monkeypatch):
    """C14 / issue #3: write_inbox must run *after* append_archive.

    If append_archive dies (crash / disk error), the just-processed OK'd URLs
    must still be queued in the inbox — otherwise they exist in neither file:
    the inbox was already rewritten without them and the archive never got
    them (irrecoverable loss)."""
    inbox = tmp_path / "_inbox.md"
    inbox.write_text("https://example.com/article-A  # source=test\n", encoding="utf-8")
    monkeypatch.setattr(F, "INBOX", inbox)
    monkeypatch.setattr(F, "ARCHIVE", tmp_path / "_archive.md")
    monkeypatch.setattr(F, "SOURCE_MAP", tmp_path / "_source_map.json")

    saved = F.REPO_ROOT / "raw" / "NewsScrap" / "ok.md"
    monkeypatch.setattr(F, "fetch_one", lambda url, meta=None, dedup_index=None: ("OK", saved))

    def _crash(entries):
        raise RuntimeError("simulated death before write_inbox")

    monkeypatch.setattr(F, "append_archive", _crash)
    with pytest.raises(RuntimeError):
        F.main()
    # write_inbox must not have run yet: the OK'd URL is still in the inbox.
    assert "https://example.com/article-A" in inbox.read_text(encoding="utf-8")
