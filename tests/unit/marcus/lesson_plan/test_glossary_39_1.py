"""Story 39.1 — term-keyed glossary projection: the Package-A I/O matrix.

Every fixture derives from the two real runs (live-shape rule): the a940c5eb
skeleton + 1-row Ask-A pool ride the frozen 37-2b fixtures
(``tests/helpers/deep_dive_enrichment_37_2b``); the 8b275e5b W1 packet rows +
the REAL title-mangled headwords ride ``tests/fixtures/glossary_39_1``.

Matrix rows pinned here: a (covered), b (multi-row order), c (lean uncovered +
typed loss + coverage line), d (authority absent), d′ (degraded-with-skeleton
— deterministic-only this wave, declared in the story's witness-gap section),
e (pool empty/degraded), f (J-F3 mangle regression), g (J-F3 ``cite-003`` tier
verbatim + honesty sentence), k (row missing source_ref/provenance). Plus the
W3 post-writer headword invariant (mutant writer) and the AC-A9 reference-line
dedupe. Rows h/i/j (MD/DOCX association + resolvability) live in
``tests/specialists/workbook_producer/test_glossary_downstream_39_1.py``.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from types import SimpleNamespace

import pytest

from app.marcus.lesson_plan.deep_dive_enrichment import (
    DeepDiveEnrichmentExecutionReceiptV1,
    build_workbook_review_contribution,
    compose_deep_dive_enrichment,
)
from app.marcus.lesson_plan.glossary_projection import (
    BOLD_TERM_AUTHORITY_ABSENT_REASON,
    GLOSSARY_CAPABILITY_NOTE,
    GLOSSARY_REFERENCE_CONFLICT_LOSS_PREFIX,
    GLOSSARY_ROW_UNASSOCIATED_LOSS_PREFIX,
    GLOSSARY_TERM_UNCOVERED_DEGRADED_LOSS_PREFIX,
    GLOSSARY_TERM_UNCOVERED_LOSS_PREFIX,
    GLOSSARY_UNCOVERED_DEGRADED_ENTRY_LINE,
    GLOSSARY_UNCOVERED_ENTRY_LINE,
    GlossaryArticleBrief,
    GlossaryProjection,
    default_term_glossary_writer,
    glossary_projection_from_contribution,
    glossary_reference_lines,
    project_glossary_entries_for_terms,
    render_glossary_projection_markdown,
)
from tests.helpers.deep_dive_enrichment_37_2b import (
    degraded_candidate,
    enriched_candidate,
    live_pool_entry,
    live_skeleton_binding,
    make_request,
    mutated_pool_entry,
)
from tests.helpers.glossary_39_1 import (
    CITE_003_FIXTURE,
    FIXTURE_MANIFEST,
    W1_PACKET_ROWS_FIXTURE,
    cite_003_entry,
    cite_003_fixture_payload,
    mangled_headwords,
    w1_packet_entries,
    w1_packet_fixture_payload,
)

LIVE_TERMS = tuple(marker.term for marker in live_skeleton_binding().bold_terms)


def _receipt(request, *, mode: str = "live") -> DeepDiveEnrichmentExecutionReceiptV1:
    return DeepDiveEnrichmentExecutionReceiptV1(
        mode=mode,  # type: ignore[arg-type]
        calls=1 if mode == "live" else 0,
        idempotency_key="sha256:" + "2" * 64,
        request_digest=request.request_digest,
        pool_packet_digest=request.pool_packet_digest,
        model="gpt-5" if mode == "live" else None,
        model_config_digest="sha256:" + "3" * 64,
        cost_usd=0.05 if mode == "live" else None,
    )


def _enriched_contribution():
    request = make_request()
    result = compose_deep_dive_enrichment(request, lambda _: enriched_candidate(request))
    return build_workbook_review_contribution(result, _receipt(request))


def _degraded_contribution(loss: str = "deep_dive_enrichment_pool_unused", **request_kwargs):
    request = make_request(**request_kwargs)
    result = compose_deep_dive_enrichment(request, lambda _: degraded_candidate(loss))
    return build_workbook_review_contribution(
        result, _receipt(request, mode="offline_stub")
    )


# ---------------------------------------------------------------------------
# Rows a + b — covered terms, multi-row citation_id order
# ---------------------------------------------------------------------------


def test_row_a_covered_term_renders_verbatim_tier_citation_provenance() -> None:
    row = live_pool_entry()
    entries, losses = project_glossary_entries_for_terms(["AI"], [row])
    assert len(entries) == 1 and entries[0].covered
    article = entries[0].articles[0]
    assert article.term == "AI"
    assert article.citation_id == "ask-a-cite-001"
    assert article.evidence_hierarchy_tier == "T4_peer_other"
    assert article.source_ref == row.source_ref
    assert article.source_hash == row.source_hash
    assert not any(loss.startswith(GLOSSARY_TERM_UNCOVERED_LOSS_PREFIX) for loss in losses)
    rendered = render_glossary_projection_markdown(
        _projection_for(entries, losses, covered=1)
    )
    assert "### AI" in rendered
    assert GLOSSARY_CAPABILITY_NOTE in rendered
    assert "tier=T4_peer_other" in rendered
    assert "`ask-a-cite-001`" in rendered
    # The indexed work's title is cited support INSIDE the entry (AC-A2).
    assert "the indexed work" in rendered.lower()
    assert row.title in rendered


def _projection_for(entries, losses, *, covered):
    from app.marcus.lesson_plan.glossary_projection import GlossaryProjection

    return GlossaryProjection(
        authority="enriched",
        entries=entries,
        covered_count=covered,
        term_count=len(entries),
        empty_reason=None,
        degradation_reason=None,
        known_losses=losses,
        pool_packet_digest="a" * 64,
    )


def test_row_b_multi_row_coverage_orders_by_citation_id() -> None:
    """OFFLINE-ONLY this wave (M3 witness-gap declaration): the launch pool is
    1 row, so run A cannot exercise multi-row coverage — this deterministic
    pin is row b's only witness until a multi-row live pool exists."""
    first = live_pool_entry()
    zeroth = mutated_pool_entry(citation_id="ask-a-cite-000")
    entries, _ = project_glossary_entries_for_terms(["AI"], [first, zeroth])
    assert [a.citation_id for a in entries[0].articles] == [
        "ask-a-cite-000",
        "ask-a-cite-001",
    ]


# ---------------------------------------------------------------------------
# Row c — lean uncovered render (J-1) + typed loss + coverage line
# ---------------------------------------------------------------------------


def test_row_c_uncovered_term_is_lean_with_typed_loss() -> None:
    contribution = _enriched_contribution()
    projection = glossary_projection_from_contribution(contribution)
    assert projection.authority == "enriched"
    assert projection.term_count == len(LIVE_TERMS)
    assert projection.covered_count == 1  # only "AI" is association-covered
    uncovered = [e for e in projection.entries if not e.covered]
    assert len(uncovered) == len(LIVE_TERMS) - 1
    for entry in uncovered:
        assert entry.articles == ()
        assert (
            f"{GLOSSARY_TERM_UNCOVERED_LOSS_PREFIX}:{entry.term}"
            in projection.known_losses
        )
    rendered = render_glossary_projection_markdown(projection)
    # ONE section-lead coverage line (J-1).
    assert (
        f"Research coverage this run: 1 of {len(LIVE_TERMS)} terms." in rendered
    )
    assert rendered.count("Research coverage this run:") == 1
    # Per-term heading for EVERY bolded term, byte-exact.
    for term in LIVE_TERMS:
        assert f"### {term}" in rendered
    # Lean uncovered body: exactly ONE short line; no citation/tier/capability
    # note rides an uncovered entry.
    sections = rendered.split("### ")
    for chunk in sections[1:]:
        term = chunk.splitlines()[0]
        if term == "AI":
            continue
        body = "\n".join(chunk.splitlines()[1:])
        assert GLOSSARY_UNCOVERED_ENTRY_LINE in body
        assert "ask-a-cite-" not in body
        assert "tier=" not in body
        assert GLOSSARY_CAPABILITY_NOTE not in body
        assert [line for line in body.splitlines() if line.strip()] == [
            GLOSSARY_UNCOVERED_ENTRY_LINE
        ]


# ---------------------------------------------------------------------------
# Row d — bold-term authority absent (W1/A-2)
# ---------------------------------------------------------------------------


def test_row_d_no_contribution_renders_explicitly_empty() -> None:
    projection = glossary_projection_from_contribution(None)
    assert projection.authority == "absent"
    assert projection.entries == ()
    assert BOLD_TERM_AUTHORITY_ABSENT_REASON in (projection.empty_reason or "")
    rendered = render_glossary_projection_markdown(projection)
    assert BOLD_TERM_AUTHORITY_ABSENT_REASON in rendered
    assert "###" not in rendered
    assert "ask-a-cite-" not in rendered


def test_row_d_contribution_without_result_renders_explicitly_empty() -> None:
    contribution = build_workbook_review_contribution(None, None)
    projection = glossary_projection_from_contribution(contribution)
    assert projection.authority == "absent"
    assert BOLD_TERM_AUTHORITY_ABSENT_REASON in (projection.empty_reason or "")
    # The contribution's own typed loss is surfaced in the reason detail.
    assert "deep_dive_enrichment_skeleton_unavailable" in (projection.empty_reason or "")


# ---------------------------------------------------------------------------
# Row d′ — degraded-with-skeleton (W1/A-2; deterministic-only this wave, M3)
# ---------------------------------------------------------------------------


def test_row_d_prime_degraded_uses_skeleton_authority_all_uncovered() -> None:
    contribution = _degraded_contribution("deep_dive_enrichment_pool_unused")
    projection = glossary_projection_from_contribution(contribution)
    assert projection.authority == "degraded_skeleton"
    assert tuple(e.term for e in projection.entries) == LIVE_TERMS
    assert projection.covered_count == 0
    assert all(not e.covered for e in projection.entries)
    assert projection.degradation_reason is not None
    assert "deep_dive_enrichment_pool_unused" in projection.degradation_reason
    # P10: pool honesty rides the one degradation reason (pool present here).
    assert "pool_status=ready" in projection.degradation_reason
    rendered = render_glossary_projection_markdown(projection)
    # Degradation reason surfaced ONCE at the section lead; entries stay lean.
    assert "deep_dive_enrichment_pool_unused" in rendered
    # P2 (row d′ truthfulness): the pool is PRESENT and its one row
    # association-covers "AI" — that term carries the state-accurate degraded
    # line + the DISTINCT typed loss; every other term keeps the plain line.
    assert rendered.count(GLOSSARY_UNCOVERED_DEGRADED_ENTRY_LINE) == 1
    assert rendered.count(GLOSSARY_UNCOVERED_ENTRY_LINE) == len(LIVE_TERMS) - 1
    assert (
        f"{GLOSSARY_TERM_UNCOVERED_DEGRADED_LOSS_PREFIX}:AI"
        in projection.known_losses
    )
    assert f"{GLOSSARY_TERM_UNCOVERED_LOSS_PREFIX}:AI" not in projection.known_losses
    ai_entry = next(e for e in projection.entries if e.term == "AI")
    assert ai_entry.degraded_association is True
    # One lean line either way (J-1): the AI body is exactly the degraded line.
    ai_chunk = rendered.split("### AI\n", 1)[1].split("### ", 1)[0]
    assert [line for line in ai_chunk.splitlines() if line.strip()] == [
        GLOSSARY_UNCOVERED_DEGRADED_ENTRY_LINE
    ]
    assert "ask-a-cite-" not in rendered


# ---------------------------------------------------------------------------
# Row e — pool packet empty/degraded: packet reason surfaced
# ---------------------------------------------------------------------------


def test_row_e_pool_empty_all_uncovered_with_packet_reason() -> None:
    contribution = _degraded_contribution(
        "deep_dive_enrichment_pool_empty",
        pool_rows=(),
        pool_scope_digest=None,
    )
    projection = glossary_projection_from_contribution(contribution)
    assert projection.covered_count == 0
    assert all(not e.covered for e in projection.entries)
    assert "deep_dive_enrichment_pool_empty" in (projection.degradation_reason or "")
    # P10: pool_status surfaces on the one degradation reason (empty pool).
    assert "pool_status=empty" in (projection.degradation_reason or "")
    rendered = render_glossary_projection_markdown(projection)
    assert "deep_dive_enrichment_pool_empty" in rendered
    # No pool row exists, so NO term is association-covered: every entry keeps
    # the plain genuinely-uncovered line (never the degraded-association one).
    assert rendered.count(GLOSSARY_UNCOVERED_ENTRY_LINE) == len(LIVE_TERMS)
    assert GLOSSARY_UNCOVERED_DEGRADED_ENTRY_LINE not in rendered


# ---------------------------------------------------------------------------
# P1 — zero-term honesty + malformed-contribution honesty (no deadlock)
# ---------------------------------------------------------------------------


def test_p1_zero_term_present_authority_renders_honest_zero_coverage() -> None:
    """Enriched/degraded authority with ZERO bolded terms renders the honest
    "0 of 0" coverage line — never the authority-absent literal."""
    for authority in ("enriched", "degraded_skeleton"):
        projection = GlossaryProjection(
            authority=authority,  # type: ignore[arg-type]
            entries=(),
            covered_count=0,
            term_count=0,
            empty_reason=None,
            degradation_reason=None,
            known_losses=(),
            pool_packet_digest="a" * 64,
        )
        rendered = render_glossary_projection_markdown(projection)
        assert "Research coverage this run: 0 of 0 terms." in rendered
        assert BOLD_TERM_AUTHORITY_ABSENT_REASON not in rendered


def test_p1_zero_term_degraded_projection_from_contribution() -> None:
    """Duck-typed degraded contribution whose skeleton carries ZERO bold terms:
    the projection stays a present authority and renders honestly."""
    contribution = SimpleNamespace(
        deep_dive_enrichment=SimpleNamespace(
            status="degraded",
            known_losses=("deep_dive_enrichment_pool_unused",),
            request=SimpleNamespace(
                skeleton=SimpleNamespace(bold_terms=()),
                pool_rows=(),
                pool_status="empty",
                pool_known_losses=(),
                pool_packet_digest="b" * 64,
            ),
        ),
        known_losses=(),
    )
    projection = glossary_projection_from_contribution(contribution)
    assert projection.authority == "degraded_skeleton"
    assert projection.term_count == 0
    rendered = render_glossary_projection_markdown(projection)
    assert "Research coverage this run: 0 of 0 terms." in rendered
    assert BOLD_TERM_AUTHORITY_ABSENT_REASON not in rendered


def test_p1_malformed_result_request_missing_projects_typed_absent() -> None:
    """Result present but request missing: typed authority-absent projection
    with the malformed reason — never an AttributeError."""
    contribution = SimpleNamespace(
        deep_dive_enrichment=SimpleNamespace(
            status="enriched", known_losses=(), request=None
        ),
        known_losses=(),
    )
    projection = glossary_projection_from_contribution(contribution)
    assert projection.authority == "absent"
    assert "enrichment result malformed" in (projection.empty_reason or "")
    assert BOLD_TERM_AUTHORITY_ABSENT_REASON in (projection.empty_reason or "")
    assert "glossary_enrichment_result_malformed" in projection.known_losses
    rendered = render_glossary_projection_markdown(projection)
    assert BOLD_TERM_AUTHORITY_ABSENT_REASON in rendered


def test_p1_malformed_result_skeleton_missing_projects_typed_absent() -> None:
    """Non-enriched result whose request carries no skeleton: same typed
    authority-absent projection (never an AttributeError)."""
    contribution = SimpleNamespace(
        deep_dive_enrichment=SimpleNamespace(
            status="degraded",
            known_losses=("deep_dive_enrichment_pool_unused",),
            request=SimpleNamespace(skeleton=None),
        ),
        known_losses=(),
    )
    projection = glossary_projection_from_contribution(contribution)
    assert projection.authority == "absent"
    assert "enrichment result malformed" in (projection.empty_reason or "")


# ---------------------------------------------------------------------------
# P11 — a pool row associating with NO bolded term is visibly recorded
# ---------------------------------------------------------------------------


def test_p11_unassociated_row_records_visible_loss() -> None:
    row = mutated_pool_entry(
        supports_bold_terms=["governance frameworks"],
        matched_bold_terms=["governance frameworks"],
    )
    entries, losses = project_glossary_entries_for_terms(["AI"], [row])
    assert (
        f"{GLOSSARY_ROW_UNASSOCIATED_LOSS_PREFIX}:ask-a-cite-001" in losses
    )
    assert not entries[0].covered


def test_p11_associated_row_records_no_unassociated_loss() -> None:
    entries, losses = project_glossary_entries_for_terms(
        ["AI"], [live_pool_entry()]
    )
    assert entries[0].covered
    assert not any(
        loss.startswith(GLOSSARY_ROW_UNASSOCIATED_LOSS_PREFIX) for loss in losses
    )


# ---------------------------------------------------------------------------
# P12 — reference-identity conflicts are visible; first kept deterministically
# ---------------------------------------------------------------------------


def test_p12_reference_conflict_recorded_and_first_kept() -> None:
    first = live_pool_entry()
    conflicting = mutated_pool_entry(
        source_ref="retrieval:scite:10.9999/conflicting-ref",
        source_id="10.9999/conflicting-ref",
    )
    entries, losses = project_glossary_entries_for_terms(["AI"], [first, conflicting])
    assert (
        f"{GLOSSARY_REFERENCE_CONFLICT_LOSS_PREFIX}:ask-a-cite-001" in losses
    )
    projection = _projection_for(tuple(entries), losses, covered=1)
    lines = glossary_reference_lines(projection)
    # Deduped to ONE line; the FIRST article (deterministic order) wins.
    assert len(lines) == 1
    assert first.source_ref in lines[0]
    assert "10.9999/conflicting-ref" not in lines[0]


def test_p12_identical_duplicate_rows_record_no_conflict() -> None:
    row = live_pool_entry()
    _, losses = project_glossary_entries_for_terms(["AI"], [row, row])
    assert not any(
        loss.startswith(GLOSSARY_REFERENCE_CONFLICT_LOSS_PREFIX) for loss in losses
    )


# ---------------------------------------------------------------------------
# P13 — unsafe-term fail-loud guard (public-boundary MD/DOCX defense)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "unsafe",
    [
        "multi\nline term",
        "#leading-hash",
        " padded ",
        "trailing ",
        "star*term",
        "**bolded**",
        "",
    ],
)
def test_p13_unsafe_term_raises_value_error(unsafe: str) -> None:
    with pytest.raises(ValueError, match="unsafe"):
        project_glossary_entries_for_terms([unsafe], [live_pool_entry()])


# ---------------------------------------------------------------------------
# Row f — the J-F3 mangle regression (real 8b275e5b rows + real mangled strings)
# ---------------------------------------------------------------------------


def test_row_f_real_w1_rows_never_yield_title_derived_headwords() -> None:
    rows = w1_packet_entries()
    entries, _ = project_glossary_entries_for_terms(LIVE_TERMS, rows)
    headwords = [e.term for e in entries]
    assert headwords == list(LIVE_TERMS)
    rendered = render_glossary_projection_markdown(
        _projection_for(tuple(entries), (), covered=sum(e.covered for e in entries))
    )
    rendered_headings = {
        line[4:].strip() for line in rendered.splitlines() if line.startswith("### ")
    }
    for mangled in mangled_headwords():
        assert mangled not in headwords
        assert mangled not in rendered_headings
    # The paper titles appear INSIDE covered entries as cited support, never
    # as headwords (AC-A2).
    covered_titles = {a.title for e in entries for a in e.articles}
    assert covered_titles  # the synthesized association makes rows eligible
    for title in covered_titles:
        assert title not in rendered_headings


# ---------------------------------------------------------------------------
# Row g — J-F3 ``cite-003`` tier verbatim + upstream-label honesty sentence
# ---------------------------------------------------------------------------


def test_row_g_cite_003_tier_rendered_verbatim_with_honesty_sentence() -> None:
    row = cite_003_entry()
    assert row.evidence_hierarchy_tier == "T1_systematic"  # the upstream mislabel
    entries, _ = project_glossary_entries_for_terms(["AI"], [row])
    article = entries[0].articles[0]
    # Never re-derived, never upgraded, never suppressed.
    assert article.evidence_hierarchy_tier == "T1_systematic"
    rendered = render_glossary_projection_markdown(
        _projection_for(tuple(entries), (), covered=1)
    )
    assert "tier=T1_systematic" in rendered
    assert "`T1_systematic`" in rendered
    # The capability note's upstream-label honesty sentence renders (AC-A4).
    assert "upstream machine labels" in rendered
    assert "does not verify" in rendered


def test_row_g_fixture_declares_its_derivation_transform() -> None:
    """M2 MUST: the fixture file itself declares verbatim vs synthesized fields."""
    payload = cite_003_fixture_payload()
    derivation = payload["derivation"]
    assert "verbatim_fields" in derivation and "synthesized_fields" in derivation
    assert "evidence_hierarchy_tier" in derivation["verbatim_fields"]
    assert "citation_id" in derivation["synthesized_fields"]
    assert "tier_label_note" in derivation
    assert payload["schema_version_pin"] == payload["entry"]["schema_version"]


# ---------------------------------------------------------------------------
# Row k — row missing source_ref/provenance skips into known_losses
# ---------------------------------------------------------------------------


def test_row_k_missing_source_ref_skips_and_degrades_to_uncovered() -> None:
    payload = live_pool_entry().model_dump(mode="json")
    payload["source_ref"] = ""
    entries, losses = project_glossary_entries_for_terms(["AI"], [payload])
    assert "glossary_skip_missing_source_ref:0" in losses
    assert not entries[0].covered
    assert f"{GLOSSARY_TERM_UNCOVERED_LOSS_PREFIX}:AI" in losses


def test_row_k_missing_provenance_skips_and_degrades_to_uncovered() -> None:
    payload = live_pool_entry().model_dump(mode="json")
    payload["provider_provenance"] = []
    entries, losses = project_glossary_entries_for_terms(["AI"], [payload])
    assert "glossary_skip_missing_provenance:0" in losses
    assert not entries[0].covered


# ---------------------------------------------------------------------------
# W3 — post-writer headword invariant (mutant writer)
# ---------------------------------------------------------------------------


def test_w3_mutant_writer_headword_overridden_byte_exact() -> None:
    def mangling_writer(term: str, entry: dict) -> GlossaryArticleBrief:
        brief = default_term_glossary_writer(term, entry)
        return replace(brief, term="Digital Health Healthcare Quality Primer")

    entries, _ = project_glossary_entries_for_terms(
        ["AI"], [live_pool_entry()], writer=mangling_writer
    )
    assert entries[0].articles[0].term == "AI"  # byte-exact, regardless of writer
    rendered = render_glossary_projection_markdown(
        _projection_for(tuple(entries), (), covered=1)
    )
    assert "### AI" in rendered
    assert "### Digital Health Healthcare Quality Primer" not in rendered


# ---------------------------------------------------------------------------
# AC-A9 — glossary reference lines: dedupe by citation_id
# ---------------------------------------------------------------------------


def test_reference_lines_dedupe_against_enrichment_and_within_glossary() -> None:
    contribution = _enriched_contribution()
    projection = glossary_projection_from_contribution(contribution)
    # The single covered row is ALSO the enrichment-used citation: excluded.
    assert glossary_reference_lines(
        projection, exclude_citation_ids=("ask-a-cite-001",)
    ) == ()
    # Without exclusion the covered row emits exactly one line in the
    # references idiom (citation_id + DOI-shape guard).
    lines = glossary_reference_lines(projection)
    assert len(lines) == 1
    assert "citation_id: `ask-a-cite-001`" in lines[0]
    assert "https://doi.org/10.5772/intechopen.94054" in lines[0]
    assert "tier=T4_peer_other" in lines[0]


def test_reference_lines_dedupe_two_terms_sharing_one_row() -> None:
    row = mutated_pool_entry(
        supports_bold_terms=["AI", "governance"],
        matched_bold_terms=["AI", "governance"],
    )
    entries, losses = project_glossary_entries_for_terms(["AI", "governance"], [row])
    projection = _projection_for(tuple(entries), losses, covered=2)
    lines = glossary_reference_lines(projection)
    assert len(lines) == 1  # a citation shared by two terms appears ONCE


# ---------------------------------------------------------------------------
# A5 re-point — packet digest witnessed on the projection
# ---------------------------------------------------------------------------


def test_projection_witnesses_pool_packet_digest() -> None:
    contribution = _enriched_contribution()
    projection = glossary_projection_from_contribution(contribution)
    assert (
        projection.pool_packet_digest
        == contribution.deep_dive_enrichment.request.pool_packet_digest
    )


# ---------------------------------------------------------------------------
# Fixture digest tripwire (drift-flags amendment; schema_version bump trips)
# ---------------------------------------------------------------------------


def test_fixture_manifest_digests_and_schema_versions_pinned() -> None:
    manifest = json.loads(FIXTURE_MANIFEST.read_text("utf-8"))
    for name, row in manifest["fixtures"].items():
        data = (FIXTURE_MANIFEST.parent / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == row["sha256"], (
            f"fixture {name} drifted from its frozen live shape — a "
            "schema_version bump must re-derive the fixture and update the "
            "manifest"
        )
    assert (
        cite_003_fixture_payload()["entry"]["schema_version"]
        == manifest["fixtures"]["cite-003-ask-a-entry.v1.json"]["pinned_schema_version"]
    )
    w1 = w1_packet_fixture_payload()
    assert all(
        row["schema_version"]
        == manifest["fixtures"]["w1-packet-rows-8b275e5b.json"]["pinned_schema_version"]
        for row in w1["entries"]
    )
    # The strict entry model itself is the bump tripwire: a bumped Literal
    # red-rejects these frozen payloads at validation time.
    assert len(w1_packet_entries()) == 5
    assert CITE_003_FIXTURE.is_file() and W1_PACKET_ROWS_FIXTURE.is_file()
