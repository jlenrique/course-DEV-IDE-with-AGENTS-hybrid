"""Per-slide variant selection — the binding permutation + fail-loud capture tests.

Murat's bar: an ASYMMETRIC per-slide map (A=1/3/5, B=2/4/6) drives the EXACT per-slide mix;
a deck-wide impl physically cannot. The mirror kills a position-keyed hardcode. Capture is
total-coverage / identity fail-loud (never silent-default).
"""

from __future__ import annotations

import json
from uuid import uuid4

import pytest

from app.marcus.orchestrator.production_runner import (
    VariantSelectionError,
    _apply_per_slide_variant_selection,
    _apply_variant_selection,
)
from app.marcus.orchestrator.slide_variant_selection import (
    SlideVariantSelectionError,
    parse_selection_code,
    run_tag_for_trial,
    validate_selections,
)
from app.models.runtime.production_envelope import ProductionEnvelope, SpecialistContribution
from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState


def _rows_ab(n: int = 6) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for i in range(1, n + 1):
        sid = f"slide-{i:02d}"
        for variant in ("A", "B"):
            rows.append(
                {"slide_id": sid, "dispatch_variant": variant, "file_path": f"{variant}_{sid}.png"}
            )
    return rows


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


def _state(selections: dict[str, str] | None = None, *, deckwide: str | None = None) -> RunState:
    payload: dict[str, object] = {}
    if selections is not None:
        payload["slide_variant_selections"] = selections
    if deckwide is not None:
        payload["selected_variant_id"] = deckwide
    return RunState(
        run_id=uuid4(),
        graph_version="v42",
        cache_state=CacheState(cache_prefix=json.dumps(payload), entries_count=1),
    )


_MIX = {f"slide-0{i}": ("A" if i % 2 else "B") for i in range(1, 7)}
_MIRROR = {sid: ("B" if v == "A" else "A") for sid, v in _MIX.items()}


def test_per_slide_permutation_drives_the_exact_mix() -> None:
    env = _apply_per_slide_variant_selection(_envelope(_rows_ab()), _state(_MIX))
    out = env.latest_for_specialist("gary").output["gary_slide_output"]
    assert {r["slide_id"]: r["dispatch_variant"] for r in out} == _MIX
    assert len(out) == 6  # exactly one row per slide


def test_per_slide_mirror_drives_the_inverse() -> None:
    env = _apply_per_slide_variant_selection(_envelope(_rows_ab()), _state(_MIRROR))
    out = env.latest_for_specialist("gary").output["gary_slide_output"]
    assert {r["slide_id"]: r["dispatch_variant"] for r in out} == _MIRROR
    # The mirror must NOT equal the mix — proves output follows the map, not slide index.
    assert {r["slide_id"]: r["dispatch_variant"] for r in out} != _MIX


def test_absent_map_is_noop() -> None:
    env = _envelope(_rows_ab())
    assert _apply_per_slide_variant_selection(env, _state(None)) is env


def test_missing_slide_fails_loud() -> None:
    partial = {k: v for k, v in _MIX.items() if k != "slide-06"}
    with pytest.raises(VariantSelectionError, match="slide-06"):
        _apply_per_slide_variant_selection(_envelope(_rows_ab()), _state(partial))


def test_unknown_variant_fails_loud() -> None:
    bad = dict(_MIX, **{"slide-03": "C"})
    with pytest.raises(VariantSelectionError, match="slide-03"):
        _apply_per_slide_variant_selection(_envelope(_rows_ab()), _state(bad))


def test_orphan_slide_fails_loud() -> None:
    orphan = dict(_MIX, **{"slide-99": "A"})
    with pytest.raises(VariantSelectionError, match="slide-99"):
        _apply_per_slide_variant_selection(_envelope(_rows_ab()), _state(orphan))


def test_dispatcher_prefers_per_slide_over_deckwide() -> None:
    # Both keys present: per-slide wins (deck-wide would collapse to a single B deck).
    env = _apply_variant_selection(_envelope(_rows_ab()), _state(_MIX, deckwide="B"))
    out = env.latest_for_specialist("gary").output["gary_slide_output"]
    assert {r["slide_id"]: r["dispatch_variant"] for r in out} == _MIX


# --- selection code parse/validate (the capture seam) ---


def test_parse_code_round_trip() -> None:
    order = [f"slide-0{i}" for i in range(1, 7)]
    code = "SBA-464c5b77-1:A 2:B 3:A 4:B 5:A 6:B"
    assert parse_selection_code(code, order) == _MIX


def test_parse_code_rejects_malformed() -> None:
    with pytest.raises(SlideVariantSelectionError):
        parse_selection_code("1:A 2:B", ["slide-01", "slide-02"])


def test_parse_code_rejects_out_of_range() -> None:
    with pytest.raises(SlideVariantSelectionError, match="out of range"):
        parse_selection_code("SBA-t-9:A", ["slide-01"])


def test_validate_missing_is_loud() -> None:
    with pytest.raises(SlideVariantSelectionError, match="missing"):
        validate_selections({"slide-01": "A"}, {"slide-01": {"A"}, "slide-02": {"A", "B"}})


def test_run_tag_is_short_and_stable() -> None:
    tid = "464c5b77-292c-462b-8253-706f0b07f981"
    assert run_tag_for_trial(tid) == "464c5b77"
