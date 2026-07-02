"""Leg-E AC#1/#2/#7 — GammaDocsProvider unit tests (RED-first).

Mirrors `tests/test_retrieval_scite_provider.py` (location + discipline):
per-test `responses.RequestsMock()` (anti-pattern #8 guard — no module-level
leaks), recorded real-page fixtures under `tests/fixtures/retrieval/gamma_docs/`
(provenance in that directory's README.md / `_provenance.json`), and a
no-stateful-mock self-guard.

The adapter is a PURE FETCH/NORMALIZE LEAF (Winston W-1): zero `app.*` imports,
zero writes, no LLM, no retry. Its three intentional degeneracies (pass-through
`formulate_query`; `refine()` → None; cross-validate N/A) are declared in
PROVIDER_INFO.notes per anti-pattern #3 (Texas T-1) and pinned here.
"""

from __future__ import annotations

import hashlib
import unicodedata
from pathlib import Path

import pytest
import responses
from retrieval import ProviderHint, RetrievalIntent
from retrieval.gamma_docs_provider import (
    GAMMA_DOCS_EXTRACTION_PATTERN,
    GAMMA_DOCS_FETCH_INTERVAL_S,
    GAMMA_DOCS_USER_AGENT,
    GammaDocsProvider,
    GammaDocsTransportError,
    canonical_doc_url,
    normalize_doc_text,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "retrieval" / "gamma_docs"

IMAGE_MODELS_URL = "https://developers.gamma.app/reference/image-model-accepted-values.md"
PARAMS_URL = "https://developers.gamma.app/guides/generate-api-parameters-explained.md"


def _fixture_bytes(name: str) -> bytes:
    return (FIXTURE_DIR / name).read_bytes()


def _intent(pages: list[str]) -> RetrievalIntent:
    return RetrievalIntent(
        intent="gamma live-doc audit fetch",
        provider_hints=[ProviderHint(provider="gamma_docs", params={"pages": pages})],
        kind="direct_ref",
        iteration_budget=1,
    )


# ---------------------------------------------------------------------------
# PROVIDER_INFO discipline (AC#1, Texas T-1/T-4/T-5, Winston W-2)
# ---------------------------------------------------------------------------


def test_gamma_docs_provider_info_identity_and_status_stub() -> None:
    """id/shape/status/auth per AC#1 + T-4 (status flips to ready ONLY with live proof)."""
    info = GammaDocsProvider.PROVIDER_INFO
    assert info.id == "gamma_docs"
    assert info.shape == "retrieval"
    assert info.status == "stub", (
        "T-4 status discipline: landed-unproven = 'stub'; 'ready' flips only in "
        "the change-set carrying the live fetch proof (AC#12)"
    )
    assert info.auth_env_vars == [], (
        "T-5 auth seam: the adapter NEVER holds GAMMA_API_KEY"
    )


def test_gamma_docs_provider_info_notes_declare_purpose_and_degeneracies() -> None:
    """W-2 registry fence + T-1 degeneracy declaration (anti-pattern #3)."""
    notes = GammaDocsProvider.PROVIDER_INFO.notes
    assert "doc-audit tooling" in notes
    assert "not a course-content retrieval source" in notes
    # The three intentional degeneracies, declared so no future dev "fixes" them.
    assert "pass-through" in notes
    assert "refine" in notes and "None" in notes
    assert "cross-validate" in notes.lower() or "cross_validate" in notes


def test_gamma_docs_module_is_a_pure_leaf_no_app_imports() -> None:
    """W-1: zero `app.*` imports in the adapter source (import-linter can't police skills)."""
    import retrieval.gamma_docs_provider as mod

    source = Path(mod.__file__).read_text(encoding="utf-8")
    assert "from app" not in source and "import app" not in source, (
        "adapter must be a pure leaf: an app.* import would execute inside every "
        "production Texas retrieval dispatch (Winston W-1)"
    )


# ---------------------------------------------------------------------------
# formulate_query — pass-through + params purity (AC#1, Texas T-2)
# ---------------------------------------------------------------------------


def test_gamma_docs_formulate_query_canonicalizes_strips_and_dedupes() -> None:
    provider = GammaDocsProvider()
    intent = _intent(
        [
            IMAGE_MODELS_URL + "#standard-models",
            IMAGE_MODELS_URL + "?ask=whatever",
            PARAMS_URL,
        ]
    )
    query = provider.formulate_query(intent)
    assert query == {"pages": [IMAGE_MODELS_URL, PARAMS_URL]}, (
        "identity is the canonical URL: fragment/query stripped; duplicates collapse"
    )


def test_gamma_docs_formulate_query_deterministic() -> None:
    import json as _json

    provider = GammaDocsProvider()
    intent = _intent([IMAGE_MODELS_URL, PARAMS_URL])
    serialized = {
        _json.dumps(provider.formulate_query(intent), sort_keys=True) for _ in range(50)
    }
    assert len(serialized) == 1


def test_gamma_docs_formulate_query_rejects_unknown_params_keys() -> None:
    """T-2 params purity: `params: {pages: [...]}` ONLY."""
    provider = GammaDocsProvider()
    intent = RetrievalIntent(
        intent="x",
        provider_hints=[
            ProviderHint(
                provider="gamma_docs",
                params={"pages": [IMAGE_MODELS_URL], "audit_facts": ["nope"]},
            )
        ],
        kind="direct_ref",
    )
    with pytest.raises(ValueError, match="pages"):
        provider.formulate_query(intent)


def test_gamma_docs_formulate_query_rejects_missing_or_empty_pages() -> None:
    provider = GammaDocsProvider()
    for params in ({}, {"pages": []}, {"pages": "not-a-list"}):
        intent = RetrievalIntent(
            intent="x",
            provider_hints=[ProviderHint(provider="gamma_docs", params=params)],
            kind="direct_ref",
        )
        with pytest.raises(ValueError):
            provider.formulate_query(intent)


def test_gamma_docs_canonical_doc_url_helper() -> None:
    assert canonical_doc_url(IMAGE_MODELS_URL + "#frag?x=1") == IMAGE_MODELS_URL
    assert canonical_doc_url(IMAGE_MODELS_URL + "?ask=q&goal=g") == IMAGE_MODELS_URL
    assert canonical_doc_url("  " + IMAGE_MODELS_URL + "  ") == IMAGE_MODELS_URL


def test_gamma_docs_canonical_doc_url_case_slash_and_rejects() -> None:
    """N7: scheme+host lowercased (path case preserved), trailing slash
    stripped, empty/relative URLs fail loud."""
    assert (
        canonical_doc_url("HTTPS://Developers.Gamma.App/Guides/X.md")
        == "https://developers.gamma.app/Guides/X.md"
    )
    assert (
        canonical_doc_url("https://developers.gamma.app/guides/x/")
        == "https://developers.gamma.app/guides/x"
    )
    for bad in ("", "   ", "guides/x.md", "/absolute/path.md", "developers.gamma.app/x"):
        with pytest.raises(ValueError):
            canonical_doc_url(bad)


# ---------------------------------------------------------------------------
# execute — polite UA, explicit UTF-8, no retry, transport typing (AC#1)
# ---------------------------------------------------------------------------


def test_gamma_docs_execute_fetches_raw_markdown_with_polite_ua() -> None:
    provider = GammaDocsProvider()
    query = provider.formulate_query(_intent([IMAGE_MODELS_URL]))
    with responses.RequestsMock() as rsps:
        rsps.get(IMAGE_MODELS_URL, body=_fixture_bytes("image_model_accepted_values.md"))
        rows = provider.execute(query)
        assert len(rsps.calls) == 1, "one fetch per page per run — no retry"
        assert rsps.calls[0].request.headers["User-Agent"] == GAMMA_DOCS_USER_AGENT
    assert len(rows) == 1
    raw = rows[0]
    assert raw["doc_url"] == IMAGE_MODELS_URL
    assert raw["http_status"] == 200
    assert "# Image models" in raw["text"]
    assert raw["fetched_at"].endswith("Z")


def test_gamma_docs_execute_decodes_utf8_explicitly() -> None:
    """AC#1/A-8: decode response.content as UTF-8 explicitly (never charset-guess)."""
    provider = GammaDocsProvider()
    query = provider.formulate_query(_intent([PARAMS_URL]))
    body = "# Café ✓ — em-dash\n".encode()
    with responses.RequestsMock() as rsps:
        # No charset in content-type: requests' apparent-encoding guess would
        # mojibake; the adapter must decode .content as UTF-8 itself.
        rsps.get(PARAMS_URL, body=body, content_type="text/plain")
        rows = provider.execute(query)
    assert "Café ✓ — em-dash" in rows[0]["text"]


def test_gamma_docs_execute_non_200_returns_row_not_exception() -> None:
    """HTTP-level failures surface as data (driver classifies indeterminate)."""
    provider = GammaDocsProvider()
    query = provider.formulate_query(_intent([IMAGE_MODELS_URL]))
    with responses.RequestsMock() as rsps:
        rsps.get(IMAGE_MODELS_URL, status=500, body="server error")
        rows = provider.execute(query)
    assert rows[0]["http_status"] == 500


def test_gamma_docs_execute_transport_error_raises_retrieval_local_type() -> None:
    """DNS/timeout-class failures raise a retrieval.* exception (no requests leak)."""
    import requests as _requests

    provider = GammaDocsProvider()
    query = provider.formulate_query(_intent([IMAGE_MODELS_URL]))
    with responses.RequestsMock() as rsps:
        rsps.get(IMAGE_MODELS_URL, body=_requests.exceptions.ConnectionError("boom"))
        with pytest.raises(GammaDocsTransportError) as excinfo:
            provider.execute(query)
    module = type(excinfo.value).__module__
    assert module.startswith("retrieval.")
    assert "requests" not in module and "urllib3" not in module


def test_gamma_docs_strict_utf8_decode_fallback_is_flagged() -> None:
    """P9: strict UTF-8 decode first; a byte stream that is NOT valid UTF-8
    falls back to errors='replace' AND carries a decode_replacement
    known_losses sentinel (T-7 floor -> the driver can never mint confirmed)."""
    provider = GammaDocsProvider()
    query = provider.formulate_query(_intent([PARAMS_URL]))
    with responses.RequestsMock() as rsps:
        rsps.get(PARAMS_URL, body=b"# ok \xff\xfe broken bytes\n")
        raw = provider.execute(query)
    assert "�" in raw[0]["text"], "replacement fallback must still yield text"
    row = provider.normalize(raw)[0]
    assert "decode_replacement" in row.provider_metadata["gamma_docs"]["known_losses"]


def test_gamma_docs_clean_utf8_carries_no_decode_sentinel() -> None:
    provider = GammaDocsProvider()
    query = provider.formulate_query(_intent([PARAMS_URL]))
    with responses.RequestsMock() as rsps:
        rsps.get(PARAMS_URL, body="# Café clean\n".encode())
        raw = provider.execute(query)
    row = provider.normalize(raw)[0]
    assert "decode_replacement" not in row.provider_metadata["gamma_docs"]["known_losses"]


def test_gamma_docs_non_markdown_content_type_is_a_known_loss() -> None:
    """P8: a 200 whose Content-Type is outside the text/markdown family
    (text/markdown, text/plain, or missing) gets a content_type_not_markdown
    sentinel — a 200 HTML page can no longer read as clean markdown."""
    provider = GammaDocsProvider()

    def _row(content_type: str | None):
        query = provider.formulate_query(_intent([PARAMS_URL]))
        with responses.RequestsMock() as rsps:
            rsps.get(PARAMS_URL, body=b"<html># not markdown</html>", content_type=content_type)
            return provider.normalize(provider.execute(query))[0]

    html_losses = _row("text/html").provider_metadata["gamma_docs"]["known_losses"]
    assert "content_type_not_markdown" in html_losses

    for ok_type in ("text/markdown; charset=utf-8", "text/plain", None):
        losses = _row(ok_type).provider_metadata["gamma_docs"]["known_losses"]
        assert "content_type_not_markdown" not in losses, ok_type


def test_gamma_docs_redirect_records_final_url_and_sentinel() -> None:
    """N2: response.url lands as the receipt's final_url; a redirect away from
    the requested URL is a `redirected` known_losses sentinel."""
    provider = GammaDocsProvider()
    moved = "https://developers.gamma.app/reference/image-models-moved.md"
    query = provider.formulate_query(_intent([IMAGE_MODELS_URL]))
    with responses.RequestsMock() as rsps:
        rsps.get(IMAGE_MODELS_URL, status=301, headers={"Location": moved})
        rsps.get(moved, body=_fixture_bytes("image_model_accepted_values.md"))
        rows = provider.normalize(provider.execute(query))
    meta = rows[0].provider_metadata["gamma_docs"]
    assert meta["final_url"] == moved
    assert "redirected" in meta["known_losses"]


def test_gamma_docs_no_redirect_final_url_matches_and_no_sentinel() -> None:
    provider = GammaDocsProvider()
    query = provider.formulate_query(_intent([IMAGE_MODELS_URL]))
    with responses.RequestsMock() as rsps:
        rsps.get(IMAGE_MODELS_URL, body=_fixture_bytes("image_model_accepted_values.md"))
        rows = provider.normalize(provider.execute(query))
    meta = rows[0].provider_metadata["gamma_docs"]
    assert meta["final_url"] == IMAGE_MODELS_URL
    assert "redirected" not in meta["known_losses"]


def test_gamma_docs_execute_paces_multi_page_fetches(monkeypatch: pytest.MonkeyPatch) -> None:
    """<=1 req/s: a sleep of the configured interval between consecutive pages."""
    import retrieval.gamma_docs_provider as mod

    sleeps: list[float] = []
    monkeypatch.setattr(mod.time, "sleep", lambda s: sleeps.append(s))
    provider = GammaDocsProvider()
    query = provider.formulate_query(_intent([IMAGE_MODELS_URL, PARAMS_URL]))
    with responses.RequestsMock() as rsps:
        rsps.get(IMAGE_MODELS_URL, body=b"# A\n")
        rsps.get(PARAMS_URL, body=b"# B\n")
        provider.execute(query)
    assert sleeps == [GAMMA_DOCS_FETCH_INTERVAL_S]


# ---------------------------------------------------------------------------
# normalize — TexasRow honesty + digest recipe (AC#1, Texas T-3/T-9, Murat M-6)
# ---------------------------------------------------------------------------


def _execute_fixture(name: str, url: str) -> list[dict]:
    provider = GammaDocsProvider()
    query = provider.formulate_query(_intent([url]))
    with responses.RequestsMock() as rsps:
        rsps.get(url, body=_fixture_bytes(name))
        return provider.execute(query)


def test_gamma_docs_normalize_row_shape_and_provider_metadata() -> None:
    provider = GammaDocsProvider()
    raw = _execute_fixture("image_model_accepted_values.md", IMAGE_MODELS_URL)
    rows = provider.normalize(raw)
    assert len(rows) == 1
    row = rows[0]
    assert row.source_id == IMAGE_MODELS_URL
    assert row.provider == "gamma_docs"
    assert row.source_origin == "operator-named"
    assert "# Image models" in row.body
    assert row.completeness_ratio == 1.0
    assert row.structural_fidelity == 1.0
    meta = row.provider_metadata["gamma_docs"]
    for key in (
        "doc_url",
        "fetched_at",
        "http_status",
        "content_sha256",
        "extraction_pattern",
        "known_losses",
        "page_title",
        "content_length_chars",
        "etag",
        "last_modified",
    ):
        assert key in meta, f"provider_metadata.gamma_docs missing {key!r} (AC#1)"
    assert meta["doc_url"] == IMAGE_MODELS_URL
    assert meta["page_title"] == "Image models"
    assert meta["extraction_pattern"] == GAMMA_DOCS_EXTRACTION_PATTERN
    assert meta["known_losses"] == []
    # Digest matches the recorded provenance stamp for this fixture (README table).
    normalized = normalize_doc_text(
        _fixture_bytes("image_model_accepted_values.md").decode("utf-8")
    )
    expected = "sha256:" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    assert meta["content_sha256"] == expected
    assert meta["content_length_chars"] == len(normalized)


def test_gamma_docs_digest_is_over_normalized_text_not_raw_bytes() -> None:
    """M-6: CRLF/NFD byte-variants of the same text digest identically."""
    provider = GammaDocsProvider()
    text_nfc_lf = "# Café\n\nline two\n"
    text_nfd_crlf = unicodedata.normalize("NFD", "# Café\r\n\r\nline two\r\n")
    assert text_nfc_lf.encode() != text_nfd_crlf.encode()

    def _row_for(body: str) -> dict:
        with responses.RequestsMock() as rsps:
            rsps.get(PARAMS_URL, body=body.encode("utf-8"))
            return provider.execute(
                provider.formulate_query(_intent([PARAMS_URL]))
            )[0]

    row_a = provider.normalize([_row_for(text_nfc_lf)])[0]
    row_b = provider.normalize([_row_for(text_nfd_crlf)])[0]
    meta_a = row_a.provider_metadata["gamma_docs"]
    meta_b = row_b.provider_metadata["gamma_docs"]
    assert meta_a["content_sha256"] == meta_b["content_sha256"], (
        "digest must be over NORMALIZED text (CRLF->LF + unicode NFC), or CDN "
        "byte-churn reads as false drift"
    )
    assert row_a.body == row_b.body


def test_gamma_docs_normalize_non_200_row_is_honest() -> None:
    """Failed fetch: completeness/fidelity None + known_losses sentinel (T-9)."""
    provider = GammaDocsProvider()
    query = provider.formulate_query(_intent([IMAGE_MODELS_URL]))
    with responses.RequestsMock() as rsps:
        rsps.get(IMAGE_MODELS_URL, status=503, body="upstream sad")
        raw = provider.execute(query)
    row = provider.normalize(raw)[0]
    assert row.completeness_ratio is None
    assert row.structural_fidelity is None
    assert row.body == ""
    losses = row.provider_metadata["gamma_docs"]["known_losses"]
    assert losses and any("503" in loss for loss in losses)


# ---------------------------------------------------------------------------
# identity_key + degenerate methods (AC#1, Amelia A-3)
# ---------------------------------------------------------------------------


def test_gamma_docs_identity_key_is_canonical_doc_url() -> None:
    from retrieval import TexasRow

    provider = GammaDocsProvider()
    row = TexasRow(
        source_id="fallback",
        provider="gamma_docs",
        provider_metadata={"gamma_docs": {"doc_url": IMAGE_MODELS_URL}},
    )
    assert provider.identity_key(row) == IMAGE_MODELS_URL


def test_gamma_docs_identity_key_falls_back_to_source_id() -> None:
    from retrieval import TexasRow

    provider = GammaDocsProvider()
    row = TexasRow(source_id=PARAMS_URL, provider="gamma_docs")
    assert provider.identity_key(row) == PARAMS_URL


def test_gamma_docs_identity_key_raises_when_both_missing() -> None:
    from retrieval import TexasRow

    provider = GammaDocsProvider()
    row = TexasRow.model_construct(source_id="", provider="gamma_docs", provider_metadata={})
    with pytest.raises(NotImplementedError):
        provider.identity_key(row)


def test_gamma_docs_refine_always_returns_none() -> None:
    """Declared degeneracy: refinement cannot help a direct-ref doc fetch."""
    provider = GammaDocsProvider()
    from retrieval import AcceptanceCriteria

    assert provider.refine({"pages": [IMAGE_MODELS_URL]}, [], AcceptanceCriteria()) is None


def test_gamma_docs_apply_filters_are_declared_passthroughs() -> None:
    provider = GammaDocsProvider()
    sample = [{"doc_url": IMAGE_MODELS_URL, "http_status": 200, "text": "# x\n"}]
    assert provider.apply_mechanical(sample, {"min_results": 1}) == sample
    assert provider.apply_provider_scored(sample, {"anything": True}) == sample


def test_gamma_docs_normalize_doc_text_helper() -> None:
    assert normalize_doc_text("a\r\nb\rc\n") == "a\nb\nc\n"
    assert normalize_doc_text(unicodedata.normalize("NFD", "Café")) == "Café"
    # P9: a leading BOM is stripped (a BOM'd byte-twin must digest identically).
    assert normalize_doc_text("\ufeff# Title\n") == "# Title\n"
    # P10: trailing whitespace per line is normalization noise, not content.
    assert normalize_doc_text("a  \nb\t\nc \n") == "a\nb\nc\n"


# ---------------------------------------------------------------------------
# AC#7 — no-stateful-mock anti-pattern self-guard (mirror scite exactly)
# ---------------------------------------------------------------------------


def test_gamma_docs_provider_test_module_has_no_stateful_mocks() -> None:
    """Tokens assembled at runtime so this self-test does not trip on its own source."""
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = (
        "Magic" + "Mock",
        "Async" + "Mock",
        "unittest" + ".mock",
    )
    for token in forbidden:
        assert token not in source, (
            f"GammaDocsProvider tests must not use {token!r} — "
            f"use `responses.RequestsMock()` + recorded fixtures instead."
        )
