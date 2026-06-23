from __future__ import annotations

import json
from uuid import uuid4

import pytest

from app.marcus.orchestrator.production_runner import (
    VariantSelectionError,
    _apply_deckwide_variant_selection,
)
from app.models.runtime.production_envelope import ProductionEnvelope, SpecialistContribution
from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState


def _state(selected_variant_id: str | None) -> RunState:
    payload = {"selected_variant_id": selected_variant_id} if selected_variant_id else {}
    return RunState(
        run_id=uuid4(),
        graph_version="v42",
        cache_state=CacheState(cache_prefix=json.dumps(payload), entries_count=1),
    )


def _raw_state(cache_prefix: str) -> RunState:
    return RunState(
        run_id=uuid4(),
        graph_version="v42",
        cache_state=CacheState(cache_prefix=cache_prefix, entries_count=1),
    )


def _envelope(rows: list[dict[str, object]]) -> ProductionEnvelope:
    envelope = ProductionEnvelope(trial_id=uuid4())
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="gary",
            node_id="07",
            output={"gary_slide_output": rows},
            model_used="test-model",
        )
    )
    return envelope


def test_deckwide_variant_selection_filters_doubled_roster_to_selected_variant() -> None:
    envelope = _envelope(
        [
            {"slide_id": "slide-01", "dispatch_variant": "A", "file_path": "a1.png"},
            {"slide_id": "slide-01", "dispatch_variant": "B", "file_path": "b1.png"},
            {"slide_id": "slide-02", "dispatch_variant": "A", "file_path": "a2.png"},
            {"slide_id": "slide-02", "dispatch_variant": "B", "file_path": "b2.png"},
        ]
    )

    filtered = _apply_deckwide_variant_selection(envelope, _state("B"))

    rows = filtered.latest_for_specialist("gary").output["gary_slide_output"]
    assert rows == [
        {"slide_id": "slide-01", "dispatch_variant": "B", "file_path": "b1.png"},
        {"slide_id": "slide-02", "dispatch_variant": "B", "file_path": "b2.png"},
    ]


def test_deckwide_variant_selection_absent_pick_is_noop() -> None:
    rows = [{"slide_id": "slide-01", "dispatch_variant": "A", "file_path": "a1.png"}]
    envelope = _envelope(rows)

    filtered = _apply_deckwide_variant_selection(envelope, _state(None))

    assert filtered is envelope
    assert filtered.latest_for_specialist("gary").output["gary_slide_output"] == rows


def test_deckwide_variant_selection_no_match_fails_loud() -> None:
    envelope = _envelope(
        [{"slide_id": "slide-01", "dispatch_variant": "A", "file_path": "a1.png"}]
    )

    with pytest.raises(VariantSelectionError, match="matched zero"):
        _apply_deckwide_variant_selection(envelope, _state("B"))


def test_deckwide_variant_selection_requires_exactly_one_row_per_slide() -> None:
    envelope = _envelope(
        [
            {"slide_id": "slide-01", "dispatch_variant": "B", "file_path": "b1.png"},
            {"slide_id": "slide-01", "dispatch_variant": "B", "file_path": "b1-dup.png"},
        ]
    )

    with pytest.raises(VariantSelectionError, match="exactly one row"):
        _apply_deckwide_variant_selection(envelope, _state("B"))


def test_deckwide_variant_selection_rejects_partial_selected_coverage() -> None:
    envelope = _envelope(
        [
            {"slide_id": "slide-01", "dispatch_variant": "A", "file_path": "a1.png"},
            {"slide_id": "slide-01", "dispatch_variant": "B", "file_path": "b1.png"},
            {"slide_id": "slide-02", "dispatch_variant": "A", "file_path": "a2.png"},
        ]
    )

    with pytest.raises(VariantSelectionError, match="slide-02"):
        _apply_deckwide_variant_selection(envelope, _state("B"))


def test_deckwide_variant_selection_rejects_parseable_non_dict_cache_prefix() -> None:
    envelope = _envelope(
        [{"slide_id": "slide-01", "dispatch_variant": "B", "file_path": "b1.png"}]
    )

    with pytest.raises(VariantSelectionError, match="cache_prefix"):
        _apply_deckwide_variant_selection(envelope, _raw_state("[]"))
