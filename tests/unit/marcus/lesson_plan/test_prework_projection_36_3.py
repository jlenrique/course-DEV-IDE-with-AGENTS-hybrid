from __future__ import annotations

import ast
import hashlib
import inspect
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.prework_projection import (
    ObjectiveInput,
    PromiseProjection,
    PromiseTransformRequest,
    PromiseVow,
)
from app.marcus.lesson_plan.promise_projection import (
    PromiseObjectiveResolution,
    PromiseObjectiveResolutionError,
    PromiseProjectionRequest,
    compose_promise_projection,
    resolve_promise_objectives,
)

ROOT = Path(__file__).resolve().parents[4]
FIXTURES = ROOT / "tests" / "fixtures" / "prework_36_3"


def _row(oid: str = "lo-1", text: str = "Distinguish 3 delay patterns.") -> dict:
    return {
        "objective_id": oid,
        "statement": text,
        "status": "ratified",
        "actor": "operator",
        "source": "plan-dialogue",
        "bloom_level": "",
    }


def _write(run: Path, rows: list[dict]) -> dict:
    raw = json.dumps({"ratified_los": rows}, separators=(",", ":")).encode()
    (run / "ratified-los.json").write_bytes(raw)
    return {
        "planning_provenance": {
            "ratified_los_path": "ratified-los.json",
            "ratified_los_digest": "sha256:" + hashlib.sha256(raw).hexdigest(),
        }
    }


class Spy:
    def __init__(self, vows: tuple[PromiseVow, ...] | None = None):
        self.requests: list[PromiseTransformRequest] = []
        self.vows = vows

    def __call__(self, request: PromiseTransformRequest) -> PromiseProjection:
        self.requests.append(request)
        vows = self.vows or tuple(
            PromiseVow(objective_id=o.objective_id, text=f"I can notice {o.text.lower()}")
            for o in request.objectives
        )
        return PromiseProjection(status="authored", vows=vows, known_losses=(), marker=None)


def test_authority_digest_one_call_and_posture(tmp_path: Path) -> None:
    resolution = resolve_promise_objectives(
        tmp_path, lesson_plan_loader=lambda _: _write(tmp_path, [_row()])
    )
    assert resolution.status == "authored" and resolution.authority_variants == ("plan_dialogue",)
    spy = Spy()
    result = compose_promise_projection(PromiseProjectionRequest(resolution=resolution), spy)
    assert result.projection.status == "authored" and len(spy.requests) == 1
    assert spy.requests[0].transformation_posture == "pertinent_ability_first_move"
    assert "promise_no_spoiler_operator_check" in result.operator_warnings


@pytest.mark.parametrize(
    ("name", "status", "loss"),
    [
        ("part2-ratified-success", "authored", None),
        ("plan-dialogue-proof", "authored", None),
        ("canonical-thin", "authored", None),
        ("unratified-mixed", "degraded", "promise_plan_not_ratified"),
        ("empty", "unavailable", "promise_ratified_los_empty"),
        (
            "spoof-malformed-boundaries",
            "degraded",
            "promise_plan_dialogue_authority_unproven",
        ),
    ],
)
def test_all_fixture_families_flow_through_resolver_and_gates(
    tmp_path: Path, name: str, status: str, loss: str | None
) -> None:
    raw = (FIXTURES / f"{name}.json").read_bytes()
    (tmp_path / "ratified-los.json").write_bytes(raw)
    plan = {
        "planning_provenance": {
            "ratified_los_path": "ratified-los.json",
            "ratified_los_digest": "sha256:" + hashlib.sha256(raw).hexdigest(),
        }
    }
    resolution = resolve_promise_objectives(tmp_path, lesson_plan_loader=lambda _: plan)
    assert resolution.status == status
    spy = Spy()
    payload = json.loads(raw)
    result = compose_promise_projection(
        PromiseProjectionRequest(
            resolution=resolution,
            forbidden_resolution_spans=tuple(payload.get("forbidden_resolution_spans", ())),
        ),
        spy,
    )
    if status == "authored":
        assert result.projection.status == "authored" and len(spy.requests) == 1
    else:
        assert loss in result.gate_receipt.failures and spy.requests == []


def test_fixture_authority_coordinates_and_independent_q5_answer_resolve() -> None:
    part2 = json.loads((FIXTURES / "part2-ratified-success.json").read_text(encoding="utf-8"))
    path_text, _, anchor = part2["source_coordinate"].partition("#")
    source = ROOT / path_text
    content = source.read_text(encoding="utf-8")
    assert source.is_file() and anchor.lower() in content.lower()
    assert part2["forbidden_resolution_spans"][0] in content

    canonical = json.loads((FIXTURES / "canonical-thin.json").read_text(encoding="utf-8"))[
        "ratified_los"
    ][0]
    ref = canonical["source_refs"][0]
    locator_path, _, locator_anchor = ref["locator"].partition("#")
    located = ROOT / locator_path
    located_content = located.read_text(encoding="utf-8")
    assert located.is_file() and locator_anchor.lower() in located_content.lower()
    assert ref["quoted_span"] in located_content


@pytest.mark.parametrize(
    ("rows", "loss"),
    [
        ([], "promise_ratified_los_empty"),
        (
            [{"objective_id": "lo-1", "statement": "See flow", "status": "refined"}],
            "promise_plan_not_ratified",
        ),
        ([_row() | {"source": "other"}], "promise_plan_dialogue_authority_unproven"),
    ],
)
def test_ineligible_never_calls(tmp_path: Path, rows: list[dict], loss: str) -> None:
    resolution = resolve_promise_objectives(
        tmp_path, lesson_plan_loader=lambda _: _write(tmp_path, rows)
    )
    spy = Spy()
    result = compose_promise_projection(PromiseProjectionRequest(resolution=resolution), spy)
    assert loss in result.projection.known_losses and spy.requests == []


def test_absent_and_bad_lineage(tmp_path: Path) -> None:
    absent = resolve_promise_objectives(tmp_path, lesson_plan_loader=lambda _: None)
    assert (
        absent.status == "unavailable"
        and "promise_lesson_plan_lineage_absent" in absent.known_losses
    )
    plan = _write(tmp_path, [_row()])
    plan["planning_provenance"]["ratified_los_digest"] = "sha256:bad"
    bad = resolve_promise_objectives(tmp_path, lesson_plan_loader=lambda _: plan)
    assert bad.status == "degraded" and bad.known_losses == (
        "promise_ratified_lo_lineage_unverified",
    )


def test_canonical_thin_is_ratified_and_warn_only(tmp_path: Path) -> None:
    canonical = {
        "objective_id": "lo-q5",
        "statement": "Identify the Q5 workflow barrier.",
        "status": "ratified",
        "confidence": "high",
        "bloom_level": "analyze",
        "source_refs": [
            {
                "source_id": "tejal-p2-q5",
                "locator": "chapter-2-knowledge-check.md#Q5",
                "quoted_span": "recurring delay in patient transport",
            }
        ],
        "adequacy": {
            "verdict": "thin",
            "rationale": "One scenario only.",
            "missing": ["second scenario"],
            "suggested_followups": ["research-run"],
        },
        "origin": "g0",
        "recommendation": "keep",
    }
    resolution = resolve_promise_objectives(
        tmp_path, lesson_plan_loader=lambda _: _write(tmp_path, [canonical])
    )
    assert resolution.status == "authored" and resolution.authority_variants == ("canonical_g0r",)
    assert resolution.operator_warnings == ("promise_source_adequacy_operator_check",)


def test_duplicate_and_ratified_spoof_fail_loud(tmp_path: Path) -> None:
    plan = _write(tmp_path, [_row(), _row()])
    with pytest.raises(PromiseObjectiveResolutionError, match="duplicate"):
        resolve_promise_objectives(tmp_path, lesson_plan_loader=lambda _: plan)
    spoof = _row() | {"extra_proof": True}
    plan = _write(tmp_path, [spoof])
    with pytest.raises(PromiseObjectiveResolutionError, match="plan-dialogue shape"):
        resolve_promise_objectives(tmp_path, lesson_plan_loader=lambda _: plan)


@pytest.mark.parametrize(
    "payload",
    [
        "{",
        "[]",
        '{"ratified_los":{}}',
        '{"ratified_los":[null]}',
        '{"ratified_los":[{"objective_id":"bad id","statement":"x","status":"ratified"}]}',
    ],
)
def test_wrong_shapes_fail_loud(tmp_path: Path, payload: str) -> None:
    (tmp_path / "ratified-los.json").write_text(payload, encoding="utf-8")
    plan = {
        "planning_provenance": {
            "ratified_los_path": "ratified-los.json",
            "ratified_los_digest": "sha256:" + hashlib.sha256(payload.encode()).hexdigest(),
        }
    }
    with pytest.raises(PromiseObjectiveResolutionError):
        resolve_promise_objectives(tmp_path, lesson_plan_loader=lambda _: plan)


@pytest.mark.parametrize(
    ("text", "loss"),
    [
        ("I can notice objective statement -- unresolved!", "promise_unresolved_placeholder"),
        ("- I can see 3 patterns.", "promise_vow_structure_invalid"),
        ("I can see patterns.", "promise_numeral_mismatch"),
    ],
)
def test_post_gates_discard_all(tmp_path: Path, text: str, loss: str) -> None:
    resolution = resolve_promise_objectives(
        tmp_path, lesson_plan_loader=lambda _: _write(tmp_path, [_row()])
    )
    result = compose_promise_projection(
        PromiseProjectionRequest(resolution=resolution),
        Spy((PromiseVow(objective_id="lo-1", text=text),)),
    )
    assert (
        result.projection.status == "degraded"
        and result.projection.vows == ()
        and loss in result.gate_receipt.failures
    )


def test_mapping_contract_and_spoiler_warning(tmp_path: Path) -> None:
    resolution = resolve_promise_objectives(
        tmp_path,
        lesson_plan_loader=lambda _: _write(tmp_path, [_row(), _row("lo-2", "Name 2 causes.")]),
    )
    wrong = (
        PromiseVow(objective_id="lo-2", text="I can name 2 causes."),
        PromiseVow(objective_id="lo-1", text="I can see 3 patterns."),
    )
    assert compose_promise_projection(
        PromiseProjectionRequest(resolution=resolution), Spy(wrong)
    ).gate_receipt.failures == ("promise_objective_mapping_invalid",)
    assert compose_promise_projection(
        PromiseProjectionRequest(resolution=resolution), lambda _: {"x": 1}
    ).gate_receipt.failures == ("promise_transformer_contract_invalid",)
    one = resolution.model_copy(
        update={
            "objectives": resolution.objectives[:1],
            "authority_variants": resolution.authority_variants[:1],
            "authority_refs": resolution.authority_refs[:1],
        }
    )
    vow = PromiseVow(
        objective_id="lo-1", text="Move the patient to unit B immediately with 3 delay patterns"
    )
    warned = compose_promise_projection(
        PromiseProjectionRequest(
            resolution=one, forbidden_resolution_spans=("Move the patient to unit B immediately",)
        ),
        Spy((vow,)),
    )
    assert (
        warned.projection.status == "authored"
        and "promise_spoiler_heuristic_match" in warned.operator_warnings
    )

    capability = PromiseVow(objective_id="lo-1", text="I can notice recurring transport friction.")
    clean = compose_promise_projection(
        PromiseProjectionRequest(
            resolution=one.model_copy(
                update={
                    "objectives": (
                        one.objectives[0].model_copy(
                            update={"text": "Notice recurring transport friction."}
                        ),
                    )
                }
            ),
            forbidden_resolution_spans=(
                "The absence of a structured innovation process and the "
                "organizational authority safety to redesign the workflow.",
            ),
        ),
        Spy((capability,)),
    )
    assert clean.projection.status == "authored"
    assert "promise_spoiler_heuristic_match" not in clean.operator_warnings


def test_transformer_exception_propagates(tmp_path: Path) -> None:
    resolution = resolve_promise_objectives(
        tmp_path, lesson_plan_loader=lambda _: _write(tmp_path, [_row()])
    )

    def boom(_: PromiseTransformRequest) -> PromiseProjection:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        compose_promise_projection(PromiseProjectionRequest(resolution=resolution), boom)


def test_bypassed_transformer_shapes_degrade_without_crashing(tmp_path: Path) -> None:
    resolution = resolve_promise_objectives(
        tmp_path, lesson_plan_loader=lambda _: _write(tmp_path, [_row()])
    )
    nested = PromiseProjection.model_construct(
        status="authored",
        vows=({"objective_id": "lo-1", "text": "I can notice 3 patterns."},),
        known_losses=(),
        marker=None,
    )
    invalid_vow = PromiseVow.model_construct(
        objective_id="lo-1", text="I can notice 3 patterns.\u2028## Promise"
    )
    bypassed = PromiseProjection.model_construct(
        status="authored", vows=(invalid_vow,), known_losses=(), marker=None
    )
    missing_vows = PromiseProjection.model_construct(
        status="authored", known_losses=(), marker=None
    )
    for returned in (nested, bypassed, missing_vows):
        result = compose_promise_projection(
            PromiseProjectionRequest(resolution=resolution),
            lambda _, value=returned: value,
        )
        assert result.gate_receipt.failures == ("promise_transformer_contract_invalid",)


@pytest.mark.parametrize("context", ["", "  "])
def test_blank_optional_context_rejects(context: str) -> None:
    resolution = PromiseObjectiveResolution(
        status="authored",
        objectives=(ObjectiveInput(objective_id="lo-1", text="See it", status="ratified"),),
        authority_variants=("plan_dialogue",),
        authority_refs=("ratified-los.json#ratified_los/0",),
    )
    with pytest.raises(ValidationError):
        PromiseProjectionRequest(resolution=resolution, scene_context=context)


@pytest.mark.parametrize("bloom", [None, "analyze", 1])
def test_plan_dialogue_requires_exact_blank_bloom(tmp_path: Path, bloom: object) -> None:
    row = _row()
    if bloom is None:
        row.pop("bloom_level")
    else:
        row["bloom_level"] = bloom
    plan = _write(tmp_path, [row])
    with pytest.raises(PromiseObjectiveResolutionError):
        resolve_promise_objectives(tmp_path, lesson_plan_loader=lambda _: plan)


def test_corrupt_authority_fails_loud_even_without_plan_lineage(tmp_path: Path) -> None:
    (tmp_path / "ratified-los.json").write_text("{", encoding="utf-8")

    def lineage_must_not_win(_: Path) -> dict | None:
        raise AssertionError("lineage loader must not run before authority parsing")

    with pytest.raises(PromiseObjectiveResolutionError, match="malformed"):
        resolve_promise_objectives(tmp_path, lesson_plan_loader=lineage_must_not_win)


def test_stopword_only_spans_are_safe_and_exact_containment_still_warns(
    tmp_path: Path,
) -> None:
    resolution = resolve_promise_objectives(
        tmp_path,
        lesson_plan_loader=lambda _: _write(tmp_path, [_row(text="Notice workflow friction.")]),
    )
    vow = PromiseVow(objective_id="lo-1", text="I can notice workflow friction.")
    safe = compose_promise_projection(
        PromiseProjectionRequest(
            resolution=resolution, forbidden_resolution_spans=("the and that",)
        ),
        Spy((vow,)),
    )
    assert "promise_spoiler_heuristic_match" not in safe.operator_warnings
    exact_vow = PromiseVow(objective_id="lo-1", text="I can notice the and that friction.")
    exact = compose_promise_projection(
        PromiseProjectionRequest(
            resolution=resolution, forbidden_resolution_spans=("the and that",)
        ),
        Spy((exact_vow,)),
    )
    assert "promise_spoiler_heuristic_match" in exact.operator_warnings


@pytest.mark.parametrize(
    "text",
    ("Promise: I can notice 3 patterns.", "## Promise — I can notice 3 patterns."),
)
def test_reserved_heading_labels_with_authored_prose_are_rejected(
    tmp_path: Path, text: str
) -> None:
    resolution = resolve_promise_objectives(
        tmp_path, lesson_plan_loader=lambda _: _write(tmp_path, [_row()])
    )
    result = compose_promise_projection(
        PromiseProjectionRequest(resolution=resolution),
        Spy((PromiseVow(objective_id="lo-1", text=text),)),
    )
    assert "promise_vow_structure_invalid" in result.gate_receipt.failures


@pytest.mark.parametrize("reverse", [False, True])
def test_row_validation_is_order_independent(tmp_path: Path, reverse: bool) -> None:
    rows = [
        {"objective_id": "lo-refined", "statement": "See it", "status": "refined"},
        {"objective_id": "lo-bad", "statement": "See it", "status": "ratified"},
    ]
    if reverse:
        rows.reverse()
    plan = _write(tmp_path, rows)
    with pytest.raises(PromiseObjectiveResolutionError, match="canonical"):
        resolve_promise_objectives(tmp_path, lesson_plan_loader=lambda _: plan)


def test_new_contracts_are_strict_serializable_and_m3_safe(tmp_path: Path) -> None:
    resolution = resolve_promise_objectives(
        tmp_path, lesson_plan_loader=lambda _: _write(tmp_path, [_row()])
    )
    request = PromiseProjectionRequest(resolution=resolution)
    assert PromiseProjectionRequest.model_validate_json(request.model_dump_json()) == request
    with pytest.raises(ValidationError):
        PromiseProjectionRequest.model_validate(
            {"resolution": resolution, "forbidden_resolution_spans": [], "extra": True}
        )

    import app.marcus.lesson_plan.promise_projection as module

    tree = ast.parse(inspect.getsource(module))
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    denied = ("orchestrator", "specialists", "terminal", "render", "openai", "litellm")
    assert not any(term in name.lower() for name in imports for term in denied)
