"""Leg-C R3 — floor consumption wired into the REAL dispatched act path.

Pins (hermetic recording handle, no network):

- a bound floor is honored on the act path at plan CREATION (04A shape:
  corpus present, anchors must resolve) AND at REFINEMENT (05/05B shape:
  prior-plan payload, carried-forward anchors trusted per A-4) — the LATEST
  pass honors, because refinement consolidates (baseline: 04A 10 -> 05/05B 7);
- an unhonorable floor error-pauses recoverably (SpecialistDispatchError);
- the anchor EMISSION carries no scripted value/hint (D-3): the instruction
  block requests source_refs + refinement carry-forward and never mentions the
  floor/scripted vocabulary.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.irene_pass1 import _act as pass1_act
from app.specialists.irene_pass1 import cluster_floor as cf

FIXTURE_PATH = (
    Path(__file__).resolve().parents[3]
    / "tests" / "fixtures" / "leg_c_cluster_floor"
    / "irene_pass1-05B-output-verbatim.json"
)


@dataclass
class _RecordingChat:
    response_text: str
    calls: list[list[dict[str, str]]] = field(default_factory=list)

    def invoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
        self.calls.append(messages)
        return SimpleNamespace(content=self.response_text, usage_metadata=None)


@dataclass
class _RecordingHandle:
    response_text: str
    chat: _RecordingChat = field(init=False)

    def __post_init__(self) -> None:
        self.chat = _RecordingChat(self.response_text)


def _state(payload: dict[str, Any]) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True), entries_count=0
        ),
    )


# Fixture-derived response: the verbatim-real 05B plan_units + synthetic
# anchors (clearly labelled; the live baseline predates the anchor emission).
_REFS_BY_UNIT: dict[str, list[str]] = {
    "u01": ["physicians already possess the core traits of innovation leaders"],
    "u02": ["the clinical method mirrors the design thinking process"],
    "u03": ["required reading before the intrapreneurship content"],
    "u04": ["intrapreneurship changes systems from within existing institutions"],
    "u05": [
        "Image Prompt: a blank canvas beside a load-bearing blueprint",
        "Narration: every wall you want to move is load-bearing",
    ],
    "u06": [
        "Image Prompt: an organizational web of resources and stakeholders",
        "Narration: the organization already holds what you need to scale",
    ],
    "u07": ["an idea has no intrinsic value until vetted into an opportunity"],
    "u08": ["the tablet idea jumps to technology before the workflow problem"],
    "u09": ["chief complaint, root cause, and desired workflow improvement"],
    "u10": ["first principles thinking breaks the workflow into fundamental truths"],
    "u11": ["part three closes by integrating the clinician innovator mindset"],
    "u12": ["which distinction separates an idea from an opportunity"],
}


def _response_with_refs() -> str:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    units = payload["lesson_plan"]["plan_units"]
    for unit in units:
        unit["source_refs"] = list(_REFS_BY_UNIT[unit["unit_id"]])
    return json.dumps(
        {
            "lesson_summary": payload["lesson_plan"]["lesson_summary"],
            "plan_units": units,
            "collateral": {"declaration": "none"},
        }
    )


def _corpus_with_anchors() -> str:
    lines = ["# Part 3 corpus (synthetic anchor host)\n"]
    for refs in _REFS_BY_UNIT.values():
        lines.extend(refs)
    return "\n".join(lines)


def _creation_payload(tmp_path: Path, floor: int | None) -> dict[str, Any]:
    bundle = tmp_path / "bundle"
    bundle.mkdir(exist_ok=True)
    (bundle / "extracted.md").write_text(_corpus_with_anchors(), encoding="utf-8")
    payload: dict[str, Any] = {
        "mode": "pass-1",
        "run_id": "run-floor-act",
        "runs_root": str(tmp_path),
        "bundle_reference": str(bundle),
    }
    if floor is not None:
        payload["min_cluster_floor"] = floor
    return payload


def test_creation_path_honors_bound_floor_and_strips_prompt(tmp_path: Path) -> None:
    handle = _RecordingHandle(_response_with_refs())
    update = pass1_act.act(
        _state(_creation_payload(tmp_path, floor=8)), handle=handle, model_id="gpt-5.4"
    )
    output = json.loads(update["cache_state"]["cache_prefix"])
    units = output["lesson_plan"]["plan_units"]
    assert cf.count_clusters(units) == 8  # honored: 7 -> 8
    assert [u["unit_id"] for u in units] == [f"u{i:02d}" for i in range(1, 13)]
    # locked_scope carries the SAME honored units (the arbiter surface)
    assert cf.count_clusters(output["locked_scope"]["plan_units"]) == 8
    # zero floor bytes reached the model (Murat-5 in unit form)
    for message in handle.chat.calls[-1]:
        assert "min_cluster_floor" not in message["content"]


def test_creation_path_without_floor_is_unchanged_control(tmp_path: Path) -> None:
    handle = _RecordingHandle(_response_with_refs())
    update = pass1_act.act(
        _state(_creation_payload(tmp_path, floor=None)), handle=handle, model_id="gpt-5.4"
    )
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert cf.count_clusters(output["lesson_plan"]["plan_units"]) == 7  # count_K


def test_refinement_path_honors_floor_via_carried_forward_refs(tmp_path: Path) -> None:
    """05/05B shape: prior plan in upstream_output, NO bundle_reference —
    extracted_source is None; carried-forward anchors are schema+role checked
    only (A-4). The LATEST pass must honor (refinement consolidates)."""
    handle = _RecordingHandle(_response_with_refs())
    payload = {
        "mode": "pass-1",
        "run_id": "run-floor-refine",
        "runs_root": str(tmp_path),
        "upstream_output": {"lesson_plan": {"plan_units": []}},
        "min_cluster_floor": 8,
    }
    update = pass1_act.act(_state(payload), handle=handle, model_id="gpt-5.4")
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert cf.count_clusters(output["lesson_plan"]["plan_units"]) == 8


def test_unhonorable_floor_error_pauses_recoverably(tmp_path: Path) -> None:
    from app.specialists.dispatch_errors import SpecialistDispatchError

    handle = _RecordingHandle(_response_with_refs())
    with pytest.raises(cf.ClusterFloorMismatchError) as excinfo:
        pass1_act.act(
            _state(_creation_payload(tmp_path, floor=20)),
            handle=handle,
            model_id="gpt-5.4",
        )
    assert isinstance(excinfo.value, SpecialistDispatchError)


def test_anchor_resolution_active_at_creation(tmp_path: Path) -> None:
    """At creation the corpus is present: anchors that do NOT resolve verbatim
    veto the split (unresolvable -> soft mismatch, never guess-and-split)."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "extracted.md").write_text(
        "A corpus that contains none of the synthetic anchors.", encoding="utf-8"
    )
    handle = _RecordingHandle(_response_with_refs())
    payload = {
        "mode": "pass-1",
        "run_id": "run-floor-unresolved",
        "runs_root": str(tmp_path),
        "bundle_reference": str(bundle),
        "min_cluster_floor": 8,
    }
    with pytest.raises(cf.ClusterFloorMismatchError):
        pass1_act.act(_state(payload), handle=handle, model_id="gpt-5.4")


# --------------------------------------------------------------------------- #
# emission contract (D-3: anchors carry no scripted value/hint)                #
# --------------------------------------------------------------------------- #
def test_emission_requests_anchors_and_carry_forward() -> None:
    instructions = pass1_act._cluster_emission_instructions()
    assert "source_refs" in instructions
    assert "VERBATIM" in instructions
    assert "CARRY" in instructions and "FORWARD" in instructions and "UNCHANGED" in instructions


def test_emission_carries_no_scripted_hint() -> None:
    instructions = pass1_act._cluster_emission_instructions().lower()
    for forbidden in ("min_cluster_floor", "scripted", "floor", "styleguide"):
        assert forbidden not in instructions
    # and the assembled prompt with a bound floor names the floor NOWHERE
    _system, user = pass1_act.assemble_pass1_prompt(
        {"mode": "pass-1", "min_cluster_floor": 424242}, extracted_source="Corpus."
    )
    assert "min_cluster_floor" not in user
    assert "424242" not in user


def test_source_refs_survive_normalize_clusters() -> None:
    plan = {
        "plan_units": [
            {"unit_id": "h", "cluster_id": "c-h", "cluster_role": "head",
             "source_refs": ["a verbatim anchor"]},
        ]
    }
    out = pass1_act.normalize_clusters(plan)
    assert out["plan_units"][0]["source_refs"] == ["a verbatim anchor"]
