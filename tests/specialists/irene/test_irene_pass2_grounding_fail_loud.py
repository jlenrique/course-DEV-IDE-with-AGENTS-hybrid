"""PIN-G2 — Pass 2 refuses to dispatch on hollow grounding (dp-v1.1, 2026-06-12).

Red twins of Trial-3 cycle-4 defect 1: node 08 received ``input keys:
cache_prefix`` only and Irene authored a sepsis narration from her L5
exemplars with ``provenance: real``. The "payload empty, proceed anyway"
branch must not exist: every missing grounding input raises a typed
SpecialistDispatchError BEFORE the chat model is invoked, and a parsed
response that does not join the real slide roster raises after.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from app.marcus.orchestrator.production_runner import _RETRYABLE_DISPATCH_TAGS
from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.irene.graph import (
    Pass2GroundingError,
    _act,
    _assert_join_id_integrity,
    _assert_narration_joins_roster,
    backfill_delta_ids,
)
from app.specialists.narration_join import join_narration_segments
from app.specialists.source_bundle import SourceBundleError
from tests.specialists.irene.conftest import (
    joined_pass2_response,
    make_grounded_pass2_payload,
)


class _RefusingChat:
    """A chat handle that fails the test if Pass 2 dispatches ungrounded."""

    def invoke(self, messages: Any) -> Any:
        raise AssertionError(
            "chat model invoked despite missing grounding — the "
            "proceed-anyway branch is the cycle-4 defect"
        )


def _entry() -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level="registry_default",
        requested=None,
        resolved="gpt-5",
        reason="test",
        timestamp=datetime.now(UTC),
        cache_prefix_hash="a" * 64,
    )


def _state(payload: dict[str, Any]) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True), entries_count=0
        ),
        model_resolution_trail=[_entry()],
    )


def _patch_refusing_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.specialists.irene.graph.make_chat_model",
        lambda *a, **k: SimpleNamespace(chat=_RefusingChat(), entry=_entry()),
    )


def test_empty_payload_raises_before_dispatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_refusing_model(monkeypatch)
    with pytest.raises(SourceBundleError):
        _act(_state({}))


def test_missing_roster_raises_before_dispatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _patch_refusing_model(monkeypatch)
    payload = make_grounded_pass2_payload(tmp_path)
    del payload["gary_slide_output"]
    with pytest.raises(Pass2GroundingError) as excinfo:
        _act(_state(payload))
    assert excinfo.value.tag == "irene.pass2.grounding-missing"


def test_missing_lesson_plan_raises_before_dispatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _patch_refusing_model(monkeypatch)
    payload = make_grounded_pass2_payload(tmp_path)
    del payload["lesson_plan"]
    with pytest.raises(Pass2GroundingError) as excinfo:
        _act(_state(payload))
    assert excinfo.value.tag == "irene.pass2.grounding-missing"


def test_grounding_errors_are_recoverable_dispatch_family() -> None:
    # The runner converts SpecialistDispatchError to error-pause + recover;
    # grounding failures must ride that family, not crash the cycle.
    assert issubclass(Pass2GroundingError, SpecialistDispatchError)
    assert issubclass(SourceBundleError, SpecialistDispatchError)


def test_unjoined_narration_raises_after_parse(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Residual-confabulation kill: a response referencing slides outside the
    real roster (exemplar bleed despite grounding) fails loud."""
    response = SimpleNamespace(
        content=json.dumps(
            {
                "narration_script": [{"id": "seg-1", "narration_text": "Sepsis..."}],
                "segment_manifest_deltas": [
                    {
                        "id": "seg-1",
                        "visual_references": [
                            {"perception_source": "slide-clu-sepsis-01-1"}
                        ],
                    }
                ],
            }
        ),
        usage_metadata={"input_tokens": 10},
    )

    class _Chat:
        def invoke(self, messages: Any) -> Any:
            return response

    monkeypatch.setattr(
        "app.specialists.irene.graph.make_chat_model",
        lambda *a, **k: SimpleNamespace(chat=_Chat(), entry=_entry()),
    )
    with pytest.raises(Pass2GroundingError) as excinfo:
        _act(_state(make_grounded_pass2_payload(tmp_path)))
    assert excinfo.value.tag == "irene.pass2.slide-join-failed"


# ---------------------------------------------------------------------------
# Defect fix — Irene Pass-2 slide-join id-integrity gate
# (irene-pass2-slidejoin-id-integrity-gate.md; AMENDED spec AC-1..AC-6).
#
# The gap: `_assert_narration_joins_roster` validates perception_source→roster
# grounding but NEVER id-join integrity. An id-less or non-bijective Pass-2
# emission (the frozen `40f3a90a` shape) passes the roster gate yet collapses
# in `join_narration_segments` (text keyed by id) into a degenerate storyboard
# — distinct slide_id, IDENTICAL narration on every row. The new
# `_assert_join_id_integrity` closes that hole AT the Pass-2 boundary, reusing
# the already-retryable `irene.pass2.slide-join-failed` tag so auto-retry
# self-heals an id-bearing re-roll. The frozen shared join is untouched.
# ---------------------------------------------------------------------------

# Roster mirroring the conftest grounded payload (slide_ids s1/s2/s3).
_IDGATE_ROSTER = [
    {"slide_id": "s1"},
    {"slide_id": "s2"},
    {"slide_id": "s3"},
]


def test_ac1_id_less_after_backfill_fails_loud_non_vacuous() -> None:
    """AC-1: the true `40f3a90a` shape — valid roster-matching
    perception_sources but EVERY narration/delta id empty. Backfill cannot
    repair it (no segment_id alias; narration ids all None ⇒ no positional
    source). The roster gate stays SILENT (the gap) while the new id-integrity
    gate FIRES with its id-absence detail. Asserting BOTH is the anti-vacuity
    discriminator (a shared-tag assertion alone would be insufficient)."""
    parsed = {
        "narration_script": [
            {"id": None, "narration_text": "Opening."},
            {"id": None, "narration_text": "Middle."},
            {"id": None, "narration_text": "Closing."},
        ],
        "segment_manifest_deltas": [
            {"id": None, "visual_references": [{"perception_source": "s1"}]},
            {"id": None, "visual_references": [{"perception_source": "s2"}]},
            {"id": None, "visual_references": [{"perception_source": "s3"}]},
        ],
    }
    # Faithful to _act: run the boundary backfill first — it must NOT repair.
    parsed = backfill_delta_ids(parsed)

    # The pre-existing roster gate is SILENT on this fixture (the gap).
    assert _assert_narration_joins_roster(parsed, _IDGATE_ROSTER) is None

    # The new gate FIRES with its DISTINCT id-absence detail + shared tag.
    with pytest.raises(Pass2GroundingError) as excinfo:
        _assert_join_id_integrity(parsed)
    assert excinfo.value.tag == "irene.pass2.slide-join-failed"
    assert "id-less after backfill" in str(excinfo.value)
    # Distinct from the roster gate's grounding message.
    assert "does not join the real slide roster" not in str(excinfo.value)


def test_ac2_non_bijective_id_join_fails_loud() -> None:
    """AC-2: distinct segments sharing a non-empty join key (the text_by_id
    overwrite path). All ids are usable ⇒ the id-absence branch is silent;
    the non-bijective branch fires with its distinct detail. Roster gate stays
    silent (non-vacuous)."""
    parsed = {
        "narration_script": [
            {"id": "seg-1", "narration_text": "Opening."},
            {"id": "seg-1", "narration_text": "Closing."},  # duplicate id
        ],
        "segment_manifest_deltas": [
            {"id": "seg-1", "visual_references": [{"perception_source": "s1"}]},
            {"id": "seg-2", "visual_references": [{"perception_source": "s2"}]},
        ],
    }
    assert _assert_narration_joins_roster(parsed, _IDGATE_ROSTER) is None
    with pytest.raises(Pass2GroundingError) as excinfo:
        _assert_join_id_integrity(parsed)
    assert excinfo.value.tag == "irene.pass2.slide-join-failed"
    assert "id-join non-bijective" in str(excinfo.value)
    assert "id-less after backfill" not in str(excinfo.value)


def test_ac2c_duplicate_delta_ids_fails_loud() -> None:
    """MUST-FIX (bmad-code-review): the join builds one row per DELTA and keys
    each row's narration_text by the DELTA id (narration_join.py). A fixture
    with DISTINCT narration ids (passes narration-bijectivity (b)) and every
    delta id usable (passes id-absence (a)) but DUPLICATE non-empty DELTA ids
    floods every distinct slide with a single narration — the 40f3a90a collapse
    reached via duplicated delta ids. `phantom_segment_ids` misses it (the
    flooded text is non-empty). Condition (c) closes it with a DISTINCT detail.
    Roster gate stays silent (non-vacuous)."""
    parsed = {
        "narration_script": [
            {"id": "seg-1", "narration_text": "First."},
            {"id": "seg-2", "narration_text": "Second."},
            {"id": "seg-3", "narration_text": "Third."},
        ],
        "segment_manifest_deltas": [
            {"id": "seg-1", "visual_references": [{"perception_source": "s1"}]},
            {"id": "seg-1", "visual_references": [{"perception_source": "s2"}]},
            {"id": "seg-1", "visual_references": [{"perception_source": "s3"}]},
        ],
    }
    assert _assert_narration_joins_roster(parsed, _IDGATE_ROSTER) is None
    with pytest.raises(Pass2GroundingError) as excinfo:
        _assert_join_id_integrity(parsed)
    assert excinfo.value.tag == "irene.pass2.slide-join-failed"
    assert "delta id-join non-bijective" in str(excinfo.value)
    assert "id-less after backfill" not in str(excinfo.value)


def test_ac4c_duplicate_delta_id_deterministic_collapse_proof() -> None:
    """Deterministic proof condition (c) closes a LIVE collapse, not a
    hypothetical: DISTINCT narration ids + DUPLICATE delta ids feed the frozen
    shared join a degenerate flood — distinct slide_ids, one narration_text on
    every row (all delta rows key on the shared id → the same narration).
    `join_narration_segments` is read only (byte-frozen); this observes it."""
    narration_script = [
        {"id": "seg-1", "narration_text": "First distinct narration."},
        {"id": "seg-2", "narration_text": "Second distinct narration."},
        {"id": "seg-3", "narration_text": "Third distinct narration."},
    ]
    deltas = [
        {"id": "seg-1", "visual_references": [{"perception_source": "s1"}]},
        {"id": "seg-1", "visual_references": [{"perception_source": "s2"}]},
        {"id": "seg-1", "visual_references": [{"perception_source": "s3"}]},
    ]
    rows = join_narration_segments(narration_script, deltas)
    assert [row["slide_id"] for row in rows] == ["s1", "s2", "s3"]  # distinct
    # Degenerate flood: one narration text on every row (shared delta id).
    assert {row["narration_text"] for row in rows} == {"First distinct narration."}


def test_ac3i_no_regression_known_good_passes() -> None:
    """AC-3 (i): the known-good tejal shape (distinct bijective ids) passes the
    new gate unchanged."""
    assert _assert_join_id_integrity(joined_pass2_response()) is None


def test_ac3ii_false_fire_guard_identical_text_distinct_ids_passes() -> None:
    """AC-3 (ii) FALSE-FIRE GUARD: two segments with IDENTICAL narration_text
    but DISTINCT ids are legitimate repeated prose ⇒ PASS. Bijectivity keys on
    id count, NEVER on narration_text."""
    parsed = {
        "narration_script": [
            {"id": "seg-1", "narration_text": "Same prose."},
            {"id": "seg-2", "narration_text": "Same prose."},  # identical text
        ],
        "segment_manifest_deltas": [
            {"id": "seg-1", "visual_references": [{"perception_source": "s1"}]},
            {"id": "seg-2", "visual_references": [{"perception_source": "s2"}]},
        ],
    }
    assert _assert_join_id_integrity(parsed) is None


def test_ac3ii_false_fire_guard_identical_text_shared_id_fires() -> None:
    """AC-3 (ii) mirror: IDENTICAL narration_text with a SHARED non-empty id
    FIRES — proving the discriminator is the id, not the text."""
    parsed = {
        "narration_script": [
            {"id": "seg-1", "narration_text": "Same prose."},
            {"id": "seg-1", "narration_text": "Same prose."},  # shared id
        ],
        "segment_manifest_deltas": [
            {"id": "seg-1", "visual_references": [{"perception_source": "s1"}]},
            {"id": "seg-2", "visual_references": [{"perception_source": "s2"}]},
        ],
    }
    with pytest.raises(Pass2GroundingError) as excinfo:
        _assert_join_id_integrity(parsed)
    assert "id-join non-bijective" in str(excinfo.value)


def test_ac4_pre_fix_deterministic_collapse_proof() -> None:
    """AC-4: proves the gate closes a LIVE collapse, not a hypothetical. The
    frozen shared join, fed the id-less fixture, floods every row with the
    SAME (last-write-wins) narration_text across DISTINCT slide_ids — exactly
    the `40f3a90a` degenerate storyboard. `join_narration_segments` is read
    only (byte-frozen); this test merely observes it."""
    narration_script = [
        {"id": None, "narration_text": "First distinct narration."},
        {"id": None, "narration_text": "Second distinct narration."},
        {"id": None, "narration_text": "Third distinct narration."},
    ]
    deltas = [
        {"id": None, "visual_references": [{"perception_source": "s1"}]},
        {"id": None, "visual_references": [{"perception_source": "s2"}]},
        {"id": None, "visual_references": [{"perception_source": "s3"}]},
    ]
    rows = join_narration_segments(narration_script, deltas)
    assert [row["slide_id"] for row in rows] == ["s1", "s2", "s3"]  # distinct
    # Degenerate flood: one narration text on every row (last-write-wins).
    assert {row["narration_text"] for row in rows} == {"Third distinct narration."}


def test_ac5_tag_is_retryable_dispatch_family() -> None:
    """AC-5: the raised tag rides the auto-retry family so an id-bearing
    re-roll self-heals within the bounded retries."""
    assert "irene.pass2.slide-join-failed" in _RETRYABLE_DISPATCH_TAGS
