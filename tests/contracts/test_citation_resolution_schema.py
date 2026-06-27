"""DD4 — CitationResolution schema specs (closed-enum 3-surface + coherence).

The CitationResolution model is the additive G0EnrichmentResult field carrying
P2 Texas pass-0 verdicts. It must red-reject an out-of-set status at all three
surfaces (Literal validator, JSON-Schema enum, TypeAdapter round-trip), forbid
extra keys, and enforce the resolved/failed/ungrounded coherence invariants.
"""

from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from app.marcus.lesson_plan.g0_enrichment import (
    CITATION_RESOLUTION_REASONS,
    CITATION_RESOLUTION_STATUSES,
    CitationResolution,
    CitationResolutionStatus,
)


def _resolved(**over):
    base = dict(
        component_id="src-001-c003",
        doi="10.1001/jama.2019.13978",
        resolution_status="resolved",
        resolved_ref={"title": "Waste", "doi": "10.1001/jama.2019.13978",
                      "access_url": "https://doi.org/10.1001/jama.2019.13978"},
        reason=None,
    )
    base.update(over)
    return base


# --------------------------------------------------------------------------- #
# Closed-enum 3-surface red-rejection                                         #
# --------------------------------------------------------------------------- #


def test_status_surface1_literal_validator_rejects() -> None:
    with pytest.raises(ValidationError):
        CitationResolution(component_id="c1", resolution_status="bogus")


def test_status_surface2_json_schema_enum_is_exact() -> None:
    assert {"resolved", "failed", "ungrounded"} == CITATION_RESOLUTION_STATUSES
    assert {
        "no_doi_in_excerpt",
        "not_in_index",
        "dispatch_error",
    } == CITATION_RESOLUTION_REASONS


def test_status_surface3_type_adapter_round_trip_rejects() -> None:
    adapter = TypeAdapter(CitationResolutionStatus)
    assert adapter.validate_python("resolved") == "resolved"
    with pytest.raises(ValidationError):
        adapter.validate_python("maybe")


def test_extra_keys_forbidden() -> None:
    with pytest.raises(ValidationError):
        CitationResolution(**_resolved(), unexpected="x")


def test_defaults_provider_and_normalization_version() -> None:
    row = CitationResolution(**_resolved())
    assert row.resolver_provider == "scite"
    assert row.normalization_version == "tex-norm-v1"


def test_provider_is_closed_to_scite() -> None:
    with pytest.raises(ValidationError):
        CitationResolution(**_resolved(resolver_provider="pubmed"))


# --------------------------------------------------------------------------- #
# Coherence invariants                                                        #
# --------------------------------------------------------------------------- #


def test_resolved_requires_resolved_ref_and_no_reason() -> None:
    with pytest.raises(ValidationError, match="resolved_ref"):
        CitationResolution(component_id="c1", resolution_status="resolved", resolved_ref=None)
    with pytest.raises(ValidationError, match="failure reason"):
        CitationResolution(**_resolved(reason="not_in_index"))


def test_failed_requires_reason_and_no_resolved_ref() -> None:
    ok = CitationResolution(
        component_id="c1", resolution_status="failed", reason="not_in_index", resolved_ref=None
    )
    assert ok.resolution_status == "failed"
    with pytest.raises(ValidationError, match="name a reason"):
        CitationResolution(component_id="c1", resolution_status="failed", reason=None)
    with pytest.raises(ValidationError, match="resolved_ref"):
        CitationResolution(
            component_id="c1", resolution_status="failed", reason="not_in_index",
            resolved_ref={"title": "x"},
        )


def test_ungrounded_carries_no_ref_and_no_reason() -> None:
    ok = CitationResolution(component_id="c1", resolution_status="ungrounded")
    assert ok.resolved_ref is None and ok.reason is None
    with pytest.raises(ValidationError):
        CitationResolution(
            component_id="c1", resolution_status="ungrounded", resolved_ref={"title": "x"}
        )
