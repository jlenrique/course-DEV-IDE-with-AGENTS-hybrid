"""P2 Texas pass-0 — offline unit specs (DD1/DD3/DD5/DD6/DD8).

RED-first behavioral specs for the citation resolver, the universal-md front
matter, and the A4 groundedness gate. All OFFLINE: the live Texas dispatcher is
replaced by an INJECTED fake (legit DI, not a mock of the SUT) so the resolver's
branch logic is exercised without network. The live leg (real scite) is the
operator-gated validation run, separate from this suite.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from pass0.citation_resolver import (
    extract_doi,
    resolve_citations,
)
from pass0.universal_markdown_preamble import (
    CLEAN_BODY_MARKER,
    PROVENANCE_ANNOTATION_MARKER,
    emit_front_matter,
    parse_front_matter,
)
from pass0.universal_md import (
    build_component_record,
    content_fingerprint,
    is_excerpt_grounded,
)
from retrieval.contracts import ProviderResult, TexasRow

# The canonical markdown normalizer — REUSED via injection (DD6), proving the A4
# gate uses the same blockquote/`\$`/whitespace normalization as P1.
from app.marcus.orchestrator.g0_enrichment_wiring import _normalize_for_groundedness

# --------------------------------------------------------------------------- #
# Fakes (injected dispatch seam — DI, not a mock of the resolver)             #
# --------------------------------------------------------------------------- #


def _hit_dispatch(*, doi: str, title: str, venue: str = "JAMA", year: int = 2019):
    def _dispatch(_intent):
        row = TexasRow(
            source_id=doi,
            provider="scite",
            title=title,
            authors=["Shrank WH", "Rogstad TL"],
            provider_metadata={"scite": {"doi": doi, "venue": venue, "year": year}},
        )
        return ProviderResult(provider="scite", rows=[row], acceptance_met=True, iterations_used=1)

    return _dispatch


def _empty_dispatch(_intent):
    # scite total:0 — DOI not in the index.
    return ProviderResult(provider="scite", rows=[], acceptance_met=False, iterations_used=1)


def _raising_dispatch(_intent):
    raise RuntimeError("simulated scite transport failure")


def _component(
    component_id: str,
    excerpt: str,
    *,
    source_type: str = "reference_citation",
    parent: str = "src-001",
) -> SimpleNamespace:
    return SimpleNamespace(
        component_id=component_id,
        parent_source_id=parent,
        source_type=source_type,
        excerpt=excerpt,
    )


JAMA_EXCERPT = (
    "estimated cost of waste ... (Shrank WH, Rogstad TL, Parekh N. Waste in the US "
    "Health Care System. JAMA. 2019;322(15):1501-1509. doi:10.1001/jama.2019.13978) - MISUSE"
)
PROBE_EXCERPT = (
    'Phantom Determinants ... "... doi:10.9999/jihs.2099.deadbeef" '
    "(https://pubmed.ncbi.nlm.nih.gov/99999999/)"
)


# --------------------------------------------------------------------------- #
# DOI extraction                                                              #
# --------------------------------------------------------------------------- #


def test_extract_doi_strips_trailing_paren_and_quote() -> None:
    assert extract_doi(JAMA_EXCERPT) == "10.1001/jama.2019.13978"
    assert extract_doi(PROBE_EXCERPT) == "10.9999/jihs.2099.deadbeef"
    assert extract_doi("no doi present here") is None


def test_extract_doi_preserves_embedded_balanced_parens() -> None:
    # FIX 1: biomedical DOIs embed balanced parens (e.g. Lancet). The suffix must
    # NOT be truncated at the first inner ')'.
    text = "Murray CJL et al. doi:10.1016/S0140-6736(09)60401-3 blah blah"
    assert extract_doi(text) == "10.1016/S0140-6736(09)60401-3"


def test_extract_doi_strips_unbalanced_wrapping_paren() -> None:
    # FIX 1: the WRAPPING case still strips the trailing unbalanced ')'.
    assert extract_doi("(doi:10.1001/jama.2019.13978)") == "10.1001/jama.2019.13978"
    # Wrapped AND embedded-balanced: strip only the outer unbalanced ')'.
    assert (
        extract_doi("(doi:10.1016/S0140-6736(09)60401-3)")
        == "10.1016/S0140-6736(09)60401-3"
    )


def test_extract_doi_strips_trailing_sentence_punctuation() -> None:
    # FIX 1: a trailing '.'/',' (and an interleaved wrap like ').') is stripped.
    assert extract_doi("see 10.1001/jama.2019.13978.") == "10.1001/jama.2019.13978"
    assert extract_doi("see 10.1001/jama.2019.13978, and") == "10.1001/jama.2019.13978"
    assert extract_doi("(doi:10.1001/jama.2019.13978).") == "10.1001/jama.2019.13978"


# --------------------------------------------------------------------------- #
# Resolver — the four offline branches (DD3)                                  #
# --------------------------------------------------------------------------- #


def test_resolve_resolved_branch_echoes_doi_into_resolved_ref() -> None:
    source = {"src-001": JAMA_EXCERPT}
    comps = [_component("c1", JAMA_EXCERPT)]
    out = resolve_citations(
        comps,
        source,
        dispatch=_hit_dispatch(
            doi="10.1001/jama.2019.13978", title="Waste in the US Health Care System"
        ),
        normalize_fn=_normalize_for_groundedness,
    )
    assert len(out) == 1
    row = out[0]
    assert row["resolution_status"] == "resolved"
    assert row["doi"] == "10.1001/jama.2019.13978"
    assert row["reason"] is None
    assert row["resolver_provider"] == "scite"
    assert row["normalization_version"] == "tex-norm-v1"
    ref = row["resolved_ref"]
    assert ref["title"] == "Waste in the US Health Care System"
    assert ref["doi"] == "10.1001/jama.2019.13978"
    assert ref["access_url"] == "https://doi.org/10.1001/jama.2019.13978"
    assert ref["journal"] == "JAMA"


def test_resolve_failed_not_in_index_when_dispatch_empty() -> None:
    source = {"src-001": PROBE_EXCERPT}
    comps = [_component("c1", PROBE_EXCERPT)]
    out = resolve_citations(
        comps, source, dispatch=_empty_dispatch, normalize_fn=_normalize_for_groundedness
    )
    assert out[0]["resolution_status"] == "failed"
    assert out[0]["reason"] == "not_in_index"
    assert out[0]["resolved_ref"] is None
    assert out[0]["doi"] == "10.9999/jihs.2099.deadbeef"  # DOI captured even on fail


def test_resolve_no_doi_in_excerpt_skips_dispatch() -> None:
    source = {"src-001": "A reference with no identifier."}
    comps = [_component("c1", "A reference with no identifier.")]

    def _must_not_call(_intent):  # pragma: no cover - asserts it is never reached
        raise AssertionError("dispatch must not run when there is no DOI")

    out = resolve_citations(
        comps, source, dispatch=_must_not_call, normalize_fn=_normalize_for_groundedness
    )
    assert out[0]["resolution_status"] == "failed"
    assert out[0]["reason"] == "no_doi_in_excerpt"
    assert out[0]["doi"] is None
    assert out[0]["resolved_ref"] is None


def test_resolve_dispatch_error_branch() -> None:
    source = {"src-001": JAMA_EXCERPT}
    comps = [_component("c1", JAMA_EXCERPT)]
    out = resolve_citations(
        comps, source, dispatch=_raising_dispatch, normalize_fn=_normalize_for_groundedness
    )
    assert out[0]["resolution_status"] == "failed"
    assert out[0]["reason"] == "dispatch_error"
    assert out[0]["resolved_ref"] is None
    assert out[0]["doi"] == "10.1001/jama.2019.13978"


# --------------------------------------------------------------------------- #
# DD6 — A4 RED groundedness (HARD)                                            #
# --------------------------------------------------------------------------- #


def test_a4_fabricated_excerpt_is_ungrounded_and_not_resolved() -> None:
    # The excerpt is NOT a substring of the parent source — fabricated span.
    source = {"src-001": "The real parent source talks only about apples and oranges."}
    fabricated = "Totally invented citation doi:10.1001/jama.2019.13978 never in source"
    comps = [_component("c1", fabricated)]

    def _must_not_call(_intent):  # pragma: no cover
        raise AssertionError("ungrounded excerpt must not be DOI-resolved")

    out = resolve_citations(
        comps, source, dispatch=_must_not_call, normalize_fn=_normalize_for_groundedness
    )
    assert out[0]["resolution_status"] == "ungrounded"
    assert out[0]["reason"] is None
    assert out[0]["resolved_ref"] is None


def test_a4_benign_markdown_artifact_is_grounded() -> None:
    # Source has the markdown-escaped `\$760` + a blockquote `> ` prefix; the
    # excerpt un-escapes them. tex-norm-v1 normalizes BOTH sides -> grounded.
    source = {"src-001": "> Healthcare waste was \\$760 billion. doi:10.1001/jama.2019.13978"}
    excerpt = "Healthcare waste was $760 billion. doi:10.1001/jama.2019.13978"
    comps = [_component("c1", excerpt)]
    out = resolve_citations(
        comps,
        source,
        dispatch=_hit_dispatch(doi="10.1001/jama.2019.13978", title="Waste"),
        normalize_fn=_normalize_for_groundedness,
    )
    # NOT ungrounded — the benign `\$`/`> ` artifacts are normalized away.
    assert out[0]["resolution_status"] == "resolved"


def test_is_excerpt_grounded_helper_directly() -> None:
    assert is_excerpt_grounded("$760", "cost was \\$760 total", _normalize_for_groundedness)
    assert not is_excerpt_grounded("not here", "only this text", _normalize_for_groundedness)
    assert is_excerpt_grounded("", "anything", _normalize_for_groundedness)  # empty -> grounded


# --------------------------------------------------------------------------- #
# Component selection — reference_citation OR DOI-bearing excerpt             #
# --------------------------------------------------------------------------- #


def test_selection_includes_doi_bearing_non_reference_components() -> None:
    source = {"src-001": JAMA_EXCERPT, "src-002": "plain slide text, no doi"}
    comps = [
        _component("c1", JAMA_EXCERPT, source_type="narration"),  # DOI-bearing narration
        _component("c2", "plain slide text, no doi", source_type="slide", parent="src-002"),
    ]
    out = resolve_citations(
        comps,
        source,
        dispatch=_hit_dispatch(doi="10.1001/jama.2019.13978", title="Waste"),
        normalize_fn=_normalize_for_groundedness,
    )
    # Only the DOI-bearing narration is selected; the plain slide is skipped.
    assert [r["component_id"] for r in out] == ["c1"]
    assert out[0]["resolution_status"] == "resolved"


# --------------------------------------------------------------------------- #
# DD5 — emit_front_matter determinism + round-trip + demarcation             #
# --------------------------------------------------------------------------- #


def test_emit_front_matter_is_deterministic_and_round_trips() -> None:
    fields = {
        "component_id": "src-001-c003",
        "type": "reference_citation",
        "locator": "Course > Module > Part 1 > Page 3",
        "verbatim_excerpt": "waste was $760 billion (doi:10.1001/jama.2019.13978)",
        "content_fingerprint": content_fingerprint("waste was $760 billion"),
        "resolution_status": "resolved",
        "doc_ordinal": 7,
        "normalization_version": "tex-norm-v1",
    }
    a = emit_front_matter(fields)
    b = emit_front_matter(fields)
    assert a == b  # byte-deterministic
    rt = parse_front_matter(a)
    for key, value in fields.items():
        assert rt[key] == value
    # every declared key present (missing -> null)
    assert "part" in rt and rt["part"] is None


def test_emit_front_matter_rejects_unknown_key() -> None:
    with pytest.raises(ValueError, match="unknown front-matter key"):
        emit_front_matter({"component_id": "c1", "bogus": 1})


def test_emit_front_matter_carries_provisional_los_when_provided() -> None:
    # FIX 4: provisional_los is an accepted, round-trippable, list-valued key so
    # P3 can validate lo_refs ⊆ provisional_los.
    fields = {
        "component_id": "src-001-c003",
        "type": "reference_citation",
        "provisional_los": ["lo-1", "lo-2"],
    }
    out = emit_front_matter(fields)
    assert emit_front_matter(fields) == out  # byte-deterministic
    rt = parse_front_matter(out)
    assert rt["provisional_los"] == ["lo-1", "lo-2"]


def test_emit_front_matter_provisional_los_defaults_to_empty_list() -> None:
    # FIX 4: absent → empty list (NOT null) so P3 subset-checks need no null-guard.
    rt = parse_front_matter(emit_front_matter({"component_id": "c1"}))
    assert rt["provisional_los"] == []


def test_emit_front_matter_key_ordering_is_deterministic_with_provisional_los() -> None:
    # FIX 4: provisional_los is appended after doc_ordinal; declared order preserved.
    from pass0.universal_markdown_preamble import FRONT_MATTER_KEYS

    assert FRONT_MATTER_KEYS[-1] == "provisional_los"
    assert FRONT_MATTER_KEYS.index("doc_ordinal") < FRONT_MATTER_KEYS.index(
        "provisional_los"
    )


def test_build_component_record_has_demarcated_body() -> None:
    rec = build_component_record(
        component_id="src-001-c003",
        component_type="reference_citation",
        locator="Course > Part 1",
        verbatim_excerpt="waste was $760 billion",
        source_ref={
            "source_id": "src-001",
            "locator": "Part 1",
            "quoted_span": "waste was $760 billion",
        },
        extraction_provenance={"connector": "local_file"},
        doc_ordinal=7,
        source_text="the parent says waste was $760 billion overall",
        normalize_fn=_normalize_for_groundedness,
        resolution_status="resolved",
    )
    assert CLEAN_BODY_MARKER in rec["markdown"]
    assert PROVENANCE_ANNOTATION_MARKER in rec["markdown"]
    assert "waste was $760 billion" in rec["markdown"]  # verbatim, no paraphrase
    assert rec["grounded"] is True
    assert rec["fields"]["resolution_status"] == "resolved"


def test_build_component_record_forces_ungrounded_at_freeze() -> None:
    # A4 HARD (DD6): a fabricated excerpt forces resolution_status=ungrounded at
    # content_fingerprint freeze — never a silent sha over un-grounded text.
    rec = build_component_record(
        component_id="c1",
        component_type="reference_citation",
        locator="L",
        verbatim_excerpt="this span is not in the parent at all",
        source_ref=None,
        extraction_provenance=None,
        doc_ordinal=1,
        source_text="the parent talks about something else entirely",
        normalize_fn=_normalize_for_groundedness,
        resolution_status="resolved",  # caller said resolved...
    )
    assert rec["grounded"] is False
    assert rec["fields"]["resolution_status"] == "ungrounded"  # ...freeze overrides
