"""Reproducibility-invariant tests (Story 1.2 AC-1.2-D / NFR-X1–X5).

One test per invariant; each constructs a violating instance and confirms
validation rejection (or asserts the field is present with the right
constraints).
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models.state import (
    ALLOWED_GRAPH_VERSIONS,
    ModelResolutionEntry,
    RunState,
    SanctumFingerprint,
    StoryState,
)

# ---------------------------------------------------------------------------
# NFR-X1 — byte-for-byte replay (round-trip serialization is byte-stable)
# ---------------------------------------------------------------------------


def test_nfr_x1_run_state_round_trip_byte_stable() -> None:
    """RunState → dump → validate → dump must be a fixed point."""
    rs = RunState(graph_version="v0.1-stub")
    first = rs.model_dump(mode="json")
    second = RunState.model_validate(first).model_dump(mode="json")
    assert first == second, "RunState round-trip is not a fixed point — NFR-X1 violated"


def test_nfr_x1_story_state_round_trip_byte_stable() -> None:
    ss = StoryState(story_id="story-001")
    first = ss.model_dump(mode="json")
    second = StoryState.model_validate(first).model_dump(mode="json")
    assert first == second, "StoryState round-trip is not a fixed point — NFR-X1 violated"


# ---------------------------------------------------------------------------
# NFR-X2 — frozen graph version (closed-enum-style validation)
# ---------------------------------------------------------------------------


def test_nfr_x2_graph_version_field_present_on_run_state() -> None:
    assert "graph_version" in RunState.model_fields
    assert RunState.model_fields["graph_version"].is_required(), (
        "graph_version must be REQUIRED on RunState — NFR-X2 invariant"
    )


def test_nfr_x2_unknown_graph_version_rejected() -> None:
    with pytest.raises(ValidationError):
        RunState(graph_version="v99-future-not-frozen")


def test_nfr_x2_allowed_graph_versions_is_frozenset_stub() -> None:
    """Slab 4 Story 4.5 wires the real registry; until then the stub IS the SoT."""
    assert isinstance(ALLOWED_GRAPH_VERSIONS, frozenset)
    assert len(ALLOWED_GRAPH_VERSIONS) >= 1


# ---------------------------------------------------------------------------
# NFR-X3 — sanctum snapshot identity
# ---------------------------------------------------------------------------


def test_nfr_x3_sanctum_fingerprint_is_frozen_value_object() -> None:
    sf = SanctumFingerprint(content_sha256="a" * 64)
    with pytest.raises(ValidationError):
        sf.content_sha256 = "b" * 64  # frozen=True must forbid mutation


def test_nfr_x3_run_state_sanctum_fingerprint_field_present() -> None:
    assert "sanctum_fingerprint" in RunState.model_fields


def test_nfr_x3_sanctum_fingerprint_requires_content_sha256() -> None:
    with pytest.raises(ValidationError):
        SanctumFingerprint()  # content_sha256 is required


# ---------------------------------------------------------------------------
# NFR-X4 — model selection trail (append-only list of resolution entries)
# ---------------------------------------------------------------------------


def test_nfr_x4_run_state_model_resolution_trail_field_present() -> None:
    assert "model_resolution_trail" in RunState.model_fields


def test_nfr_x4_model_resolution_trail_default_empty_list() -> None:
    rs = RunState(graph_version="v0.1-stub")
    assert rs.model_resolution_trail == []


def test_nfr_x4_model_resolution_trail_holds_entries() -> None:
    """Updated 2026-04-23 per Story 1.3 AC-1.3-C: full ModelResolutionEntry shape."""
    entry = ModelResolutionEntry(
        level="registry_default",
        requested=None,
        resolved="gpt-5.4",
        reason="default fallthrough (NFR-X4 carrier test)",
        timestamp=datetime.now(UTC),
    )
    rs = RunState(graph_version="v0.1-stub", model_resolution_trail=[entry])
    assert len(rs.model_resolution_trail) == 1
    assert rs.model_resolution_trail[0].resolved == "gpt-5.4"
    assert rs.model_resolution_trail[0].reason  # full shape carries reason field


# ---------------------------------------------------------------------------
# NFR-X5 — documented temperature variance (constrained float)
# ---------------------------------------------------------------------------


def test_nfr_x5_temperature_default_zero() -> None:
    rs = RunState(graph_version="v0.1-stub")
    assert rs.temperature == 0.0


def test_nfr_x5_temperature_lower_bound_enforced() -> None:
    with pytest.raises(ValidationError):
        RunState(graph_version="v0.1-stub", temperature=-0.0001)


def test_nfr_x5_temperature_upper_bound_enforced() -> None:
    with pytest.raises(ValidationError):
        RunState(graph_version="v0.1-stub", temperature=2.0001)


@pytest.mark.parametrize("temp", [0.0, 0.5, 1.0, 1.5, 2.0])
def test_nfr_x5_temperature_in_range_accepted(temp: float) -> None:
    rs = RunState(graph_version="v0.1-stub", temperature=temp)
    assert rs.temperature == temp
