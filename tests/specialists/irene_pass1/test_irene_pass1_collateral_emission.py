"""Braid S1 — Irene Pass-1 additive collateral emission (AC-8, AC-9).

RED-first tests for the additive collateral-emission seam:
  - collateral-emission instructions appended in assemble_pass1_prompt
  - pure normalize_collateral(plan) backstop (mirror normalize_clusters)
  - parse_pass1_response yields a well-formed CollateralSpec-shaped dict on
    both the present-block and none paths AND the fallback-unit path
  - write_lesson_plan appends additive collateral lines; cluster lines byte-unchanged
  - no new CONSUMED_PAYLOAD_KEYS; emission additive on the output plan dict

No network/LLM calls.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

from app.marcus.lesson_plan.collateral_spec import CollateralSpec
from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.irene_pass1 import _act as pass1_act


# --------------------------------------------------------------------------- #
# Fakes                                                                        #
# --------------------------------------------------------------------------- #
@dataclass
class _FakeChat:
    response_text: str

    def invoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
        return SimpleNamespace(content=self.response_text, usage_metadata={"input_tokens": 1})


@dataclass
class _FakeHandle:
    response_text: str

    @property
    def chat(self) -> _FakeChat:
        return _FakeChat(self.response_text)


def _state(payload: dict[str, Any]) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True), entries_count=0
        ),
        model_resolution_trail=[
            ModelResolutionEntry(
                level="per_specialist",
                requested="gpt-5.4",
                resolved="gpt-5.4",
                reason="test",
                timestamp=datetime.now(UTC),
                cache_prefix_hash="a" * 64,
            )
        ],
    )


_PRESENT_BLOCK = {
    "declaration": "present",
    "workbook": {
        "sections": [
            {
                "section_id": "sec-1",
                "learning_objective_id": "u1",
                "title": "Trend depth",
                "depth_delta": {
                    "deferred_from_slide": "u1",
                    "deferred_depth": "the full derivation",
                },
                "exercises": [
                    {
                        "exercise_id": "ex-1",
                        "bloom_level": "apply",
                        "prompt_intent": "apply the trend",
                        "answer_key_source_ref": "src-u1",
                    }
                ],
                "narrative_intent": "fuller narrative",
            }
        ]
    },
    "research_goals": [
        {
            "goal_id": "rg-1",
            "pedagogical_intent": "learner needs the primary source for 23%",
        }
    ],
}


def _present_response() -> str:
    return json.dumps(
        {
            "lesson_summary": "x",
            "plan_units": [
                {
                    "unit_id": "u1",
                    "title": "Head",
                    "learning_objective": "lo",
                    "scope_decision": "in-scope",
                    "rationale": "r",
                    "cluster_id": "c-u1",
                    "cluster_role": "head",
                    "cluster_position": "establish",
                }
            ],
            "collateral": _PRESENT_BLOCK,
        }
    )


def _none_response() -> str:
    return json.dumps(
        {
            "lesson_summary": "x",
            "plan_units": [
                {
                    "unit_id": "u1",
                    "title": "Head",
                    "learning_objective": "lo",
                    "scope_decision": "in-scope",
                    "rationale": "r",
                }
            ],
            "collateral": {"declaration": "none"},
        }
    )


# --------------------------------------------------------------------------- #
# AC-8 — prompt instructions appended (sibling of cluster block)               #
# --------------------------------------------------------------------------- #
def test_ac8_prompt_requests_collateral_fields() -> None:
    _system, user = pass1_act.assemble_pass1_prompt(
        {"mode": "pass-1"}, extracted_source="Corpus."
    )
    for token in (
        "collateral",
        "declaration",
        "workbook",
        "learning_objective_id",
        "depth_delta",
        "bloom_level",
        "answer_key_source_ref",
        "research_goals",
        "pedagogical_intent",
    ):
        assert token in user, f"missing collateral token in prompt: {token}"
    # cluster block still present (additive sibling, not a replacement)
    assert "cluster_id" in user


# --------------------------------------------------------------------------- #
# AC-8 — normalize_collateral backstop: pure / idempotent / never-crash        #
# --------------------------------------------------------------------------- #
def test_ac8_normalize_present_block_yields_valid_collateral() -> None:
    plan = {"plan_units": [{"unit_id": "u1"}], "collateral": _PRESENT_BLOCK}
    out = pass1_act.normalize_collateral(plan)
    spec = CollateralSpec.model_validate(out["collateral"])
    assert spec.declaration == "present"
    assert spec.workbook is not None
    assert spec.workbook.sections[0].learning_objective_id == "u1"


def test_ac8_normalize_missing_collateral_defaults_to_none_declaration() -> None:
    plan = {"plan_units": [{"unit_id": "u1"}]}
    out = pass1_act.normalize_collateral(plan)
    spec = CollateralSpec.model_validate(out["collateral"])
    assert spec.declaration == "none"
    assert spec.workbook is None


def test_ac8_normalize_explicit_none_round_trips() -> None:
    plan = {"plan_units": [], "collateral": {"declaration": "none"}}
    out = pass1_act.normalize_collateral(plan)
    spec = CollateralSpec.model_validate(out["collateral"])
    assert spec.declaration == "none"


def test_ac8_normalize_malformed_collateral_degrades_to_none() -> None:
    # A garbage collateral block must never crash; backstop degrades to none.
    plan = {"plan_units": [], "collateral": {"declaration": "present"}}
    out = pass1_act.normalize_collateral(plan)
    spec = CollateralSpec.model_validate(out["collateral"])
    assert spec.declaration == "none"


def test_ac8_normalize_collateral_is_pure_no_mutation() -> None:
    plan = {"plan_units": [], "collateral": {"declaration": "none"}}
    snapshot = json.dumps(plan, sort_keys=True)
    pass1_act.normalize_collateral(plan)
    assert json.dumps(plan, sort_keys=True) == snapshot


def test_ac8_normalize_collateral_is_idempotent() -> None:
    plan = {"plan_units": [{"unit_id": "u1"}], "collateral": _PRESENT_BLOCK}
    once = pass1_act.normalize_collateral(plan)
    twice = pass1_act.normalize_collateral(once)
    assert once == twice


def test_ac8_normalize_collateral_handles_non_dict_plan() -> None:
    out = pass1_act.normalize_collateral(None)
    assert out["collateral"]["declaration"] == "none"


def test_ac8_normalize_collateral_in_all() -> None:
    assert "normalize_collateral" in pass1_act.__all__


# --------------------------------------------------------------------------- #
# FIX-1 — observable degrade: a present/workbook block that fails validation   #
# must emit exactly one logger.warning before degrading to "none".             #
# --------------------------------------------------------------------------- #
def test_fix1_present_with_stray_key_degrades_to_none_and_warns(caplog) -> None:
    # A near-valid present workbook with one stray key fails CollateralSpec
    # validation. Behavior must still degrade to none (decision-on-record) BUT
    # the degrade must be observable: exactly one warning.
    near_valid = json.loads(json.dumps(_PRESENT_BLOCK))
    near_valid["workbook"]["sections"][0]["stray_unexpected_key"] = "boom"
    plan = {"plan_units": [], "collateral": near_valid}
    with caplog.at_level(logging.WARNING, logger=pass1_act.__name__):
        out = pass1_act.normalize_collateral(plan)
    spec = CollateralSpec.model_validate(out["collateral"])
    assert spec.declaration == "none"
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1, f"expected exactly one warning, got {len(warnings)}"


def test_fix1_present_with_no_workbook_degrades_and_warns(caplog) -> None:
    # declaration=present but no usable workbook fails validation; must warn.
    plan = {"plan_units": [], "collateral": {"declaration": "present"}}
    with caplog.at_level(logging.WARNING, logger=pass1_act.__name__):
        out = pass1_act.normalize_collateral(plan)
    spec = CollateralSpec.model_validate(out["collateral"])
    assert spec.declaration == "none"
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1


def test_fix1_clean_none_does_not_warn(caplog) -> None:
    plan = {"plan_units": [], "collateral": {"declaration": "none"}}
    with caplog.at_level(logging.WARNING, logger=pass1_act.__name__):
        pass1_act.normalize_collateral(plan)
    assert [r for r in caplog.records if r.levelno == logging.WARNING] == []


def test_fix1_absent_collateral_does_not_warn(caplog) -> None:
    plan = {"plan_units": [{"unit_id": "u1"}]}
    with caplog.at_level(logging.WARNING, logger=pass1_act.__name__):
        pass1_act.normalize_collateral(plan)
    assert [r for r in caplog.records if r.levelno == logging.WARNING] == []


def test_fix1_non_dict_collateral_does_not_warn(caplog) -> None:
    plan = {"plan_units": [], "collateral": "not-a-dict"}
    with caplog.at_level(logging.WARNING, logger=pass1_act.__name__):
        pass1_act.normalize_collateral(plan)
    assert [r for r in caplog.records if r.levelno == logging.WARNING] == []


def test_fix1_observable_degrade_preserves_purity() -> None:
    near_valid = json.loads(json.dumps(_PRESENT_BLOCK))
    near_valid["workbook"]["sections"][0]["stray_unexpected_key"] = "boom"
    plan = {"plan_units": [], "collateral": near_valid}
    snapshot = json.dumps(plan, sort_keys=True)
    pass1_act.normalize_collateral(plan)
    assert json.dumps(plan, sort_keys=True) == snapshot


# --------------------------------------------------------------------------- #
# AC-8 — parse_pass1_response carries collateral on both paths + fallback      #
# --------------------------------------------------------------------------- #
def test_ac8_parse_present_block_yields_present_spec() -> None:
    plan = pass1_act.parse_pass1_response(_present_response())
    spec = CollateralSpec.model_validate(plan["collateral"])
    assert spec.declaration == "present"


def test_ac8_parse_none_block_yields_none_spec() -> None:
    plan = pass1_act.parse_pass1_response(_none_response())
    spec = CollateralSpec.model_validate(plan["collateral"])
    assert spec.declaration == "none"


def test_ac8_parse_fallback_unit_path_carries_none_collateral() -> None:
    plan = pass1_act.parse_pass1_response("this is not json")
    assert "collateral" in plan
    spec = CollateralSpec.model_validate(plan["collateral"])
    assert spec.declaration == "none"


def test_ac8_parse_absent_collateral_key_defaults_to_none() -> None:
    raw = json.dumps(
        {
            "lesson_summary": "x",
            "plan_units": [
                {"unit_id": "u1", "title": "T", "learning_objective": "lo",
                 "scope_decision": "in-scope", "rationale": "r"}
            ],
        }
    )
    plan = pass1_act.parse_pass1_response(raw)
    spec = CollateralSpec.model_validate(plan["collateral"])
    assert spec.declaration == "none"


# --------------------------------------------------------------------------- #
# AC-8 — write_lesson_plan: additive collateral lines, cluster lines unchanged #
# --------------------------------------------------------------------------- #
_COLLATERAL_HEADING = "## Workbook collateral"


def _cluster_section_of(text: str) -> str:
    """Extract only the lines the cluster-emission story owns (byte-stability).

    FIX-2: truncate the document at the ``## Workbook collateral`` heading
    BEFORE filtering. The old helper kept any ``"## "`` line, which let the
    collateral heading (and the additive section's own ``## ``-prefixed
    sub-headings) leak into the filtered "cluster section" — so the
    byte-stability assertion did not pin what it claimed (plan-unit / cluster
    lines identical with vs without collateral). Truncating first guarantees
    the compared region is exactly the plan-unit / cluster body.
    """
    head_index = text.find("\n" + _COLLATERAL_HEADING)
    if text.startswith(_COLLATERAL_HEADING):
        head_index = 0
    cluster_region = text if head_index < 0 else text[:head_index]
    keep_prefixes = (
        "# Irene Pass-1 Lesson Plan",
        "## ",
        "- Learning objective:",
        "- Scope decision:",
        "- Rationale:",
        "- Cluster id:",
        "- Cluster role:",
        "- Cluster position:",
        "- Narrative arc:",
        "- Parent slide id:",
        "- Cluster interstitial count:",
    )
    return "\n".join(
        line
        for line in cluster_region.splitlines()
        if line == "" or line.startswith(keep_prefixes)
    )


def test_ac8_write_collateral_lines_present(tmp_path) -> None:
    plan = pass1_act.parse_pass1_response(_present_response())
    path = pass1_act.write_lesson_plan(plan, run_id="run-collat", runs_root=tmp_path)
    text = path.read_text(encoding="utf-8")
    assert "Collateral" in text or "collateral" in text
    assert "present" in text
    # the workbook section objective + depth-delta show up in the witness
    assert "sec-1" in text
    assert "u1" in text


def test_ac8_write_collateral_none_line_present(tmp_path) -> None:
    plan = pass1_act.parse_pass1_response(_none_response())
    path = pass1_act.write_lesson_plan(plan, run_id="run-none", runs_root=tmp_path)
    text = path.read_text(encoding="utf-8")
    assert "none" in text.lower()


def test_ac8_cluster_lines_byte_unchanged_vs_no_collateral(tmp_path) -> None:
    # The cluster-section lines must be byte-identical whether or not a
    # collateral block is present (additive guarantee). We build the SAME
    # plan_units with and without collateral and compare the cluster section.
    units = [
        {
            "unit_id": "u1",
            "title": "Head",
            "learning_objective": "lo",
            "scope_decision": "in-scope",
            "rationale": "r",
            "cluster_id": "c-u1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "narrative_arc": "From A to B through C",
            "cluster_interstitial_count": 0,
        }
    ]
    plan_no = pass1_act.normalize_collateral(
        pass1_act.normalize_clusters({"lesson_summary": "s", "plan_units": units})
    )
    plan_yes = pass1_act.normalize_clusters(
        {"lesson_summary": "s", "plan_units": units, "collateral": _PRESENT_BLOCK}
    )
    plan_yes = pass1_act.normalize_collateral(plan_yes)
    p_no = pass1_act.write_lesson_plan(plan_no, run_id="r-no", runs_root=tmp_path)
    p_yes = pass1_act.write_lesson_plan(plan_yes, run_id="r-yes", runs_root=tmp_path)
    cluster_no = _cluster_section_of(p_no.read_text(encoding="utf-8"))
    cluster_yes = _cluster_section_of(p_yes.read_text(encoding="utf-8"))
    assert cluster_no == cluster_yes
    # FIX-2 guard: the collateral section must NOT leak into the extracted
    # cluster region (otherwise the assertion above pins the wrong thing).
    assert _COLLATERAL_HEADING not in cluster_yes
    # The region we pin must actually contain the cluster witness lines.
    assert "- Cluster id: c-u1" in cluster_yes
    assert "- Narrative arc: From A to B through C" in cluster_yes


def test_fix2_helper_excludes_collateral_and_catches_cluster_regression() -> None:
    # The helper must (a) drop the collateral section entirely and (b) be
    # sensitive to a displaced cluster line, so the byte-stability assertion
    # genuinely guards the cluster body.
    base = (
        "# Irene Pass-1 Lesson Plan\n"
        "\n"
        "## u1: Head\n"
        "- Learning objective: lo\n"
        "- Scope decision: in-scope\n"
        "- Rationale: r\n"
        "- Cluster id: c-u1\n"
        "- Cluster role: head\n"
        "- Cluster position: establish\n"
        "\n"
        "## Workbook collateral\n"
        "- Declaration: present\n"
        "### sec-1: Trend depth\n"
        "- Learning objective id: u1\n"
        "\n"
    )
    extracted = _cluster_section_of(base)
    # collateral heading + its ### sub-heading must be gone
    assert _COLLATERAL_HEADING not in extracted
    assert "### sec-1" not in extracted
    assert "- Learning objective id: u1" not in extracted
    # A regression that displaced a cluster line is caught: mutate the cluster
    # body and confirm the extracted section differs.
    mutated = base.replace("- Cluster id: c-u1", "- Cluster id: c-DISPLACED")
    assert _cluster_section_of(mutated) != extracted


# --------------------------------------------------------------------------- #
# FIX-3 — S1->S2 seam robustness: free-text fields with newlines must not       #
# inject fake markdown lines into irene-pass1.md (which S2 parses back).        #
# --------------------------------------------------------------------------- #
def test_fix3_section_title_newline_does_not_inject_artifact_line(tmp_path) -> None:
    block = json.loads(json.dumps(_PRESENT_BLOCK))
    block["workbook"]["sections"][0]["title"] = "Trend depth\nInjected: fake"
    plan = pass1_act.normalize_collateral(
        {"lesson_summary": "s", "plan_units": [{"unit_id": "u1"}], "collateral": block}
    )
    path = pass1_act.write_lesson_plan(plan, run_id="r-inject", runs_root=tmp_path)
    text = path.read_text(encoding="utf-8")
    # No artifact line may start with the injected fake-markdown content.
    for line in text.splitlines():
        assert not line.startswith("Injected: fake"), (
            f"newline-injected fake line leaked into artifact: {line!r}"
        )
    # The section heading carries the sanitized title on ONE line.
    heading_lines = [
        line for line in text.splitlines() if line.startswith("### sec-1:")
    ]
    assert len(heading_lines) == 1
    assert "Injected: fake" in heading_lines[0]


def test_fix3_research_goal_intent_newline_sanitized(tmp_path) -> None:
    block = json.loads(json.dumps(_PRESENT_BLOCK))
    block["research_goals"][0]["pedagogical_intent"] = "need source\nInjected: rg"
    plan = pass1_act.normalize_collateral(
        {"lesson_summary": "s", "plan_units": [{"unit_id": "u1"}], "collateral": block}
    )
    path = pass1_act.write_lesson_plan(plan, run_id="r-inject-rg", runs_root=tmp_path)
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        assert not line.startswith("Injected: rg")


# --------------------------------------------------------------------------- #
# AC-9 — no new consumed payload key; act() carries collateral in output       #
# --------------------------------------------------------------------------- #
def test_ac9_consumed_payload_keys_unchanged() -> None:
    from app.specialists.irene_pass1.payload_contract import CONSUMED_PAYLOAD_KEYS

    assert "collateral" not in CONSUMED_PAYLOAD_KEYS


def test_ac9_act_carries_collateral_into_output(tmp_path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "extracted.md").write_text("# Corpus\n\nSource.", encoding="utf-8")
    update = pass1_act.act(
        _state(
            {
                "mode": "pass-1",
                "run_id": "run-collat-act",
                "runs_root": str(tmp_path),
                "bundle_reference": str(bundle),
            }
        ),
        handle=_FakeHandle(_present_response()),
        model_id="gpt-5.4",
    )
    output = json.loads(update["cache_state"]["cache_prefix"])
    spec = CollateralSpec.model_validate(output["lesson_plan"]["collateral"])
    assert spec.declaration == "present"
