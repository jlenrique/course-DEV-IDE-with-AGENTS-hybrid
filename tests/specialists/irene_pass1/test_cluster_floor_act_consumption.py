"""Leg-C R3 — floor consumption wired into the REAL dispatched act path.

Pins (hermetic recording handle, no network):

- a bound floor is honored on the act path at plan CREATION (04A shape:
  corpus present, anchors must resolve) AND at REFINEMENT — the TRUE 05/05B
  shape carries BOTH ``upstream_output.lesson_plan`` AND ``bundle_reference``
  (nodes 05/05B declare the same ``dependency_projections.bundle_reference:
  {from: texas}`` corpus projection as 04A —
  ``state/config/pipeline-manifest.yaml:411-414`` and ``:429-435``), so
  carried-forward anchors resolve against the SAME extracted source; the
  LATEST pass honors, because refinement consolidates (baseline: 04A 10 ->
  05/05B 7). A bundle-less refinement payload is a DEGRADED defensive
  fallback (schema+role-only check), not the production shape;
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

from app.marcus.lesson_plan.pass1_source_span_catalog import (
    build_pass1_source_span_catalog,
)
from app.marcus.lesson_plan.slide_authority import canonical_source_content_digest
from app.models.pass1_source_section import (
    Pass1AuthenticatedSourceSection,
    canonical_extracted_content_digest,
)
from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.irene_pass1 import _act as pass1_act
from app.specialists.irene_pass1 import cluster_floor as cf
from app.specialists.source_bundle import (
    SourceBundleError,
    read_extracted_source_with_sections,
)
from tests._helpers.pass1_bundle import write_primary_slide_bundle
from tests._helpers.pass1_catalog_response import select_catalog_ids

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
        return SimpleNamespace(
            content=select_catalog_ids(self.response_text, messages),
            usage_metadata=None,
        )


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


def _install_empty_prior_authority(payload: dict[str, Any]) -> None:
    if "bundle_reference" in payload:
        _extracted, sections = read_extracted_source_with_sections(payload)
    else:
        placeholder = "Legacy-free empty prior authority."
        digest = canonical_source_content_digest(placeholder)
        sections = (
            Pass1AuthenticatedSourceSection(
                source_id=f"slides/slide-1-placeholder.md|{digest}",
                source_content_digest=digest,
                extracted_content_digest=canonical_extracted_content_digest(
                    placeholder
                ),
                body=placeholder,
            ),
        )
    catalog_digest = build_pass1_source_span_catalog(sections).catalog_digest
    prior_plan = {
        "source_span_catalog_digest": catalog_digest,
        "plan_units": [],
    }
    payload["upstream_output"] = {"lesson_plan": prior_plan}
    payload["prior_plan_authority_receipt"] = (
        pass1_act.validate_pass1_plan_authority(
            prior_plan,
            source_sections=sections,
        )
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


def _response_with_unknown_ids() -> str:
    payload = json.loads(_response_with_refs())
    for index, unit in enumerate(payload["plan_units"], start=1):
        unit.pop("source_refs", None)
        unit["source_ref_ids"] = [f"span:sha256:{index:064x}"]
    return json.dumps(payload)


def _corpus_with_anchors() -> str:
    lines = ["# Part 3 corpus (synthetic anchor host)\n"]
    for refs in _REFS_BY_UNIT.values():
        lines.extend(refs)
    return "\n".join(lines)


def _creation_payload(tmp_path: Path, floor: int | None) -> dict[str, Any]:
    bundle = tmp_path / "bundle"
    bundle.mkdir(exist_ok=True)
    write_primary_slide_bundle(bundle, _corpus_with_anchors())
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
    # zero floor bytes reached the model (Murat-5 in unit form) — EVERY call,
    # not just the last (R6)
    assert handle.chat.calls
    for call in handle.chat.calls:
        for message in call:
            assert "min_cluster_floor" not in message["content"]


def test_creation_path_without_floor_is_unchanged_control(tmp_path: Path) -> None:
    handle = _RecordingHandle(_response_with_refs())
    update = pass1_act.act(
        _state(_creation_payload(tmp_path, floor=None)), handle=handle, model_id="gpt-5.4"
    )
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert cf.count_clusters(output["lesson_plan"]["plan_units"]) == 7  # count_K


def test_refinement_true_shape_resolves_anchors_against_projected_corpus(
    tmp_path: Path,
) -> None:
    """R1 — the TRUE 05/05B refinement shape: the payload carries BOTH
    ``upstream_output.lesson_plan`` (prior plan) AND ``bundle_reference``
    (nodes 05/05B project the corpus exactly like 04A —
    ``state/config/pipeline-manifest.yaml:411-414``/``:429-435``). So
    ``read_extracted_source`` resolves, ``extracted_source`` is NON-None, and
    the carried-forward anchors must resolve verbatim against the SAME
    extracted source; the floor honors on that basis (the LATEST pass honors —
    refinement consolidates)."""
    handle = _RecordingHandle(_response_with_refs())
    payload = _creation_payload(tmp_path, floor=8)
    payload["run_id"] = "run-floor-refine-true"
    _install_empty_prior_authority(payload)
    update = pass1_act.act(_state(payload), handle=handle, model_id="gpt-5.4")
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert cf.count_clusters(output["lesson_plan"]["plan_units"]) == 8


def test_refinement_true_shape_unknown_catalog_ids_fail_first(tmp_path: Path) -> None:
    """A refinement cannot express non-resolving free-text authority anymore."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    write_primary_slide_bundle(
        bundle, "A corpus that contains none of the synthetic anchors."
    )
    handle = _RecordingHandle(_response_with_unknown_ids())
    payload = {
        "mode": "pass-1",
        "run_id": "run-floor-refine-veto",
        "runs_root": str(tmp_path),
        "bundle_reference": str(bundle),
        "min_cluster_floor": 8,
    }
    _install_empty_prior_authority(payload)
    with pytest.raises(pass1_act.Pass1AuthorityError, match="unknown or stale"):
        pass1_act.act(_state(payload), handle=handle, model_id="gpt-5.4")


def test_refinement_bundleless_shape_fails_before_persistence(tmp_path: Path) -> None:
    """DEGRADED defensive fallback (NOT the production 05/05B shape — see the
    module docstring): a refinement payload with a prior plan but NO resolvable
    bundle_reference. ``extracted_source`` is None and carried-forward anchors
    are schema+role checked only (A-4). Kept as a fallback so a corpus-delivery
    regression degrades to the weaker check instead of crashing."""
    handle = _RecordingHandle(_response_with_refs())
    payload = {
        "mode": "pass-1",
        "run_id": "run-floor-refine",
        "runs_root": str(tmp_path),
        "min_cluster_floor": 8,
    }
    _install_empty_prior_authority(payload)
    with pytest.raises(SourceBundleError) as excinfo:
        pass1_act.act(_state(payload), handle=handle, model_id="gpt-5.4")
    assert excinfo.value.tag == "source.bundle.reference-missing"
    assert handle.chat.calls == []
    assert not (tmp_path / "run-floor-refine" / "irene-pass1.md").exists()


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


def test_invalid_response_fails_before_bound_floor_evaluation(
    tmp_path: Path,
) -> None:
    """Invalid framing is a response-processing failure, not floor evidence."""
    handle = _RecordingHandle("this is not json at all")
    with pytest.raises(pass1_act.Pass1AuthorityError, match="structured JSON object"):
        pass1_act.act(
            _state(_creation_payload(tmp_path, floor=8)),
            handle=handle,
            model_id="gpt-5.4",
        )


def test_unknown_catalog_selection_fails_before_floor_at_creation(tmp_path: Path) -> None:
    """Unknown authority cannot reach the cluster-floor matching seam."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    write_primary_slide_bundle(
        bundle, "A corpus that contains none of the synthetic anchors."
    )
    handle = _RecordingHandle(_response_with_unknown_ids())
    payload = {
        "mode": "pass-1",
        "run_id": "run-floor-unresolved",
        "runs_root": str(tmp_path),
        "bundle_reference": str(bundle),
        "min_cluster_floor": 8,
    }
    with pytest.raises(pass1_act.Pass1AuthorityError, match="unknown or stale"):
        pass1_act.act(_state(payload), handle=handle, model_id="gpt-5.4")


# --------------------------------------------------------------------------- #
# emission contract (D-3: anchors carry no scripted value/hint)                #
# --------------------------------------------------------------------------- #
def test_emission_requests_anchors_and_carry_forward() -> None:
    instructions = pass1_act._cluster_emission_instructions(refinement=True)
    assert "source_ref_ids" in instructions
    assert "exact spans" in instructions
    assert "Never emit source_refs" in instructions
    assert "copy" in instructions and "EXACTLY unchanged" in instructions


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
