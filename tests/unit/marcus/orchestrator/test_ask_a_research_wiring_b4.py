"""B4 hardening: bold-term-lean, non-vacuous Ask-A packets on Tejal-like inputs.

Deterministic (replay-row) coverage for the Ask-A research seam fixes:

* B4a  ``build_scope`` derives a natural-language *topical* scite query from the
  bold-term deep-dive semantics instead of the pipe-delimited meta-string that
  returned no rows on the real corpus.
* B4b  A packet with strong bold-term associations but *zero* ability-token
  matches (boilerplate ratified LOs) is still valid and non-vacuous.
* B4c  Legitimately-indexed scite/consensus rows are not credibility-excluded
  purely for a missing venue string (PMID / scite_paper_id source ids).
* Scout MED #3 excerpt/match drift: association matching runs over the same
  stored evidence window, so a shown excerpt always contains the matched term.

No live dispatch: every scite row is a hand-built replay row.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from app.marcus.lesson_plan.ask_a_enrichment import (
    build_scope,
    canonical_digest,
    normalize_match_text,
)
from app.marcus.lesson_plan.deep_dive_projection import BoldTermMarker, DeepDiveAbilityInput
from app.marcus.lesson_plan.research_demand import AskAResearchDemandV1
from app.marcus.orchestrator import ask_a_research_wiring as wiring
from app.marcus.orchestrator.research_credibility import classify_evidence_hierarchy

# Boilerplate ratified-LO ability text, as produced for the Tejal corpus. Its
# tokens (material/introduced/src/q1/structural/shifts/remembering) deliberately
# do NOT appear in any scholarly abstract used below, so ability association is
# zero and the packet must lean on bold terms.
_BOILERPLATE_ABILITY = (
    "Understand the material introduced by src-001 "
    "(**Q1: Structural Shifts (Remembering)**)."
)
_BOILERPLATE_ABILITY_2 = (
    "Understand the material introduced by src-002 "
    "(**Q1: The Knowledge Explosion (Remembering)**)."
)


def _tejal_demand(
    *,
    bold_terms: tuple[str, ...] = ("burnout", "moral injury", "digital front door"),
) -> AskAResearchDemandV1:
    values = dict(
        status="ready",
        workbook_brief_payload_digest="sha256:" + "a" * 64,
        skeleton_authority_digest="sha256:" + "b" * 64,
        skeleton_candidate_digest="sha256:" + "c" * 64,
        abilities=(
            DeepDiveAbilityInput(ability_id="lo-g0-001", text=_BOILERPLATE_ABILITY),
            DeepDiveAbilityInput(ability_id="lo-g0-002", text=_BOILERPLATE_ABILITY_2),
        ),
        bold_terms=tuple(BoldTermMarker(term=term) for term in bold_terms),
        source_claim_refs=("src-001-claim", "src-002-claim"),
        known_losses=(),
    )
    raw = {
        "schema_version": "ask-a-research-demand.v1",
        "specialist_id": "workbook_brief",
        "node_id": "07W.1",
        **values,
    }
    raw["demand_digest"] = canonical_digest(raw)
    return AskAResearchDemandV1.model_validate(raw, strict=True)


def _provider_result(rows: list[SimpleNamespace]) -> SimpleNamespace:
    return SimpleNamespace(
        provider="scite",
        rows=rows,
        acceptance_met=True,
        iterations_used=1,
        refinement_log=[],
    )


# --------------------------------------------------------------------------- #
# B4a — topical query, not a pipe-delimited meta-string
# --------------------------------------------------------------------------- #
def test_build_scope_query_is_topical_not_pipe_meta() -> None:
    scope = build_scope(
        _tejal_demand(), provider_config_fingerprint="sha256:" + "d" * 64
    )
    # Topical bold-term deep-dive terms drive the provider intent.
    for term in ("burnout", "moral injury", "digital front door"):
        assert term in scope.query
    # None of the pipe-delimited meta-string scaffolding leaks into the query.
    assert "|" not in scope.query
    assert "ability[" not in scope.query
    assert "Ask-A cited enrichment" not in scope.query
    assert "claim_ref=" not in scope.query
    assert "bold_term=" not in scope.query
    # Boilerplate ability IDs / ratified-LO prose stay out of the search intent.
    assert "lo-g0-001" not in scope.query
    assert "Understand the material" not in scope.query
    assert scope.query_digest == canonical_digest(scope.query)


# --------------------------------------------------------------------------- #
# B4c — indexed scite/consensus rows survive a missing venue string
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "source_id",
    ["39876543", "8fba3910b73754f0b192c1ba93562d5a", "10.1080/01443410.2023"],
)
def test_indexed_scite_row_without_venue_is_not_credibility_excluded(source_id: str) -> None:
    row = SimpleNamespace(
        provider="scite",
        source_id=source_id,
        title="Clinician burnout and moral injury among physicians",
        body="A study of burnout in the clinical workforce.",
        authority_tier=None,
        provider_metadata={"scite": {}},
    )
    tier, peer = classify_evidence_hierarchy(row)
    assert tier == "T4_peer_other"
    assert peer is True
    assert tier not in {"T7_secondary_media", "T8_unknown"}


def test_unknown_provider_row_still_low_credibility() -> None:
    # Genuine low-credibility exclusion must remain intact.
    row = SimpleNamespace(
        provider="some_blog_scraper",
        source_id="post-42",
        title="Opinion piece",
        body="",
        authority_tier=None,
        provider_metadata={},
    )
    assert classify_evidence_hierarchy(row) == ("T8_unknown", False)


# --------------------------------------------------------------------------- #
# B4b + B4c — non-vacuous, bold-term-only packet on Tejal-like inputs
# --------------------------------------------------------------------------- #
def test_tejal_bold_term_packet_is_non_vacuous(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_enrichment_demand", lambda _: _tejal_demand())
    # A PMID row with no venue — old credibility tiering dropped this to T8 and
    # emptied the packet; the abstract carries the bold terms but none of the
    # boilerplate ability tokens.
    row = SimpleNamespace(
        provider="scite",
        source_id="39876543",
        title="Clinician burnout and workforce trends",
        body=(
            "Clinician burnout and moral injury are rising, and the "
            "digital front door reshapes patient access."
        ),
        provider_metadata={"scite": {}},
        authority_tier=None,
    )

    output = wiring.run_ask_a_research(
        run_dir=tmp_path,
        trial_id="tejal",
        dispatch_live=True,
        dispatch=lambda _: _provider_result([row]),
    )

    assert output.disposition != "completed_empty"
    assert output.disposition.startswith("completed")
    assert output.research_entries, "expected a non-vacuous bold-term-associated packet"
    entry = output.research_entries[0]
    # Bold-term association is load-bearing; ability association is absent.
    assert entry.supports_bold_terms == ("burnout", "moral injury", "digital front door")
    assert entry.supports_ability_ids == ()
    assert entry.matched_ability_tokens == {}
    assert entry.evidence_hierarchy_tier == "T4_peer_other"
    # Intake exposes covered bold terms while ability coverage stays empty.
    intake = output.research_intake
    assert intake is not None
    assert set(intake.covered_bold_terms) == {
        "burnout",
        "moral injury",
        "digital front door",
    }
    assert intake.covered_ability_ids == ()
    # Shown evidence actually contains every matched bold term.
    shown = normalize_match_text(f"{entry.title}\n{entry.evidence_excerpt}")
    for term in entry.supports_bold_terms:
        assert normalize_match_text(term) in shown


# --------------------------------------------------------------------------- #
# Scout MED #3 — association matches only within the stored excerpt window
# --------------------------------------------------------------------------- #
def test_bold_term_beyond_excerpt_window_is_not_associated(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        wiring,
        "resolve_enrichment_demand",
        lambda _: _tejal_demand(bold_terms=("burnout",)),
    )
    # DOI keeps the row credibility-admissible under both old and new tiering,
    # so the *only* discriminator is the matching window. "burnout" appears only
    # after the 2000-char evidence window; the stored excerpt (body[:2000]) would
    # NOT contain it, so it must not be recorded as an association.
    row = SimpleNamespace(
        provider="scite",
        source_id="10.1000/workforce",
        title="Workforce trends report",
        body=("x " * 1100) + " burnout appears only past the excerpt window.",
        provider_metadata={"scite": {}},
        authority_tier=None,
    )

    output = wiring.run_ask_a_research(
        run_dir=tmp_path,
        trial_id="drift",
        dispatch_live=True,
        dispatch=lambda _: _provider_result([row]),
    )

    assert output.disposition == "completed_empty"
    assert output.research_entries == ()


def test_bold_term_within_excerpt_window_is_shown_in_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        wiring,
        "resolve_enrichment_demand",
        lambda _: _tejal_demand(bold_terms=("burnout",)),
    )
    row = SimpleNamespace(
        provider="scite",
        source_id="10.1000/workforce",
        title="Workforce trends report",
        body="Clinician burnout is discussed early. " + ("x " * 1100),
        provider_metadata={"scite": {}},
        authority_tier=None,
    )

    output = wiring.run_ask_a_research(
        run_dir=tmp_path,
        trial_id="within",
        dispatch_live=True,
        dispatch=lambda _: _provider_result([row]),
    )

    assert output.research_entries
    entry = output.research_entries[0]
    assert entry.supports_bold_terms == ("burnout",)
    shown = normalize_match_text(f"{entry.title}\n{entry.evidence_excerpt}")
    assert "burnout" in shown
