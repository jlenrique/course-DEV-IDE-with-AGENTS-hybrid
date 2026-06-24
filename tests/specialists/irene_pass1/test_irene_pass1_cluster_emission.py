"""Story 1.1 — cluster emission re-wired into LLM-first Pass-1.

RED-first tests for AC-1..AC-9 of
`_bmad-output/implementation-artifacts/spec-1.1-pass1-cluster-emission.md`.

These exercise prompt assembly, parse, the new pure `normalize_clusters`
backstop, the artifact write, the tolerance-of-absence path, and the
downstream Gary `_derive_clusters` round-trip. No network/LLM calls.
"""

from __future__ import annotations

import importlib.util
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.irene_pass1 import _act as pass1_act

REPO_ROOT = Path(__file__).resolve().parents[3]


# --------------------------------------------------------------------------- #
# Fakes / helpers (match the style in test_irene_pass1_lesson_plan_authoring)  #
# --------------------------------------------------------------------------- #
@dataclass
class _FakeChat:
    response_text: str

    def invoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
        assert messages[0]["role"] == "system"
        assert "plan_units" in messages[1]["content"]
        return SimpleNamespace(
            content=self.response_text,
            usage_metadata={"input_tokens": 1400},
        )


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
            cache_prefix=json.dumps(payload, sort_keys=True),
            entries_count=0,
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


# --------------------------------------------------------------------------- #
# AC-1 — emission contract carries cluster keys + decision guidance           #
# --------------------------------------------------------------------------- #
def test_ac1_emission_contract_requests_cluster_fields_and_guidance() -> None:
    _system, user = pass1_act.assemble_pass1_prompt(
        {"mode": "pass-1"}, extracted_source="Corpus."
    )
    for key in (
        "cluster_id",
        "cluster_role",
        "cluster_position",
        "narrative_arc",
        "cluster_interstitial_count",
        "parent_slide_id",
        "develop_type",
    ):
        assert key in user, f"missing cluster JSON key in prompt: {key}"
    # chunk-by-default + keep-dense-singleton guidance present
    assert "head + N interstitials" in user or "head + N interstitial" in user
    assert "KEEP DENSE" in user
    assert "singleton" in user.lower()


# --------------------------------------------------------------------------- #
# AC-2 — detailed references loaded (unique sentinel phrases)                  #
# --------------------------------------------------------------------------- #
def test_ac2_decision_and_arc_reference_bodies_present() -> None:
    _system, user = pass1_act.assemble_pass1_prompt(
        {"mode": "pass-1"}, extracted_source="Corpus."
    )
    # Verbatim sentinels confirmed in the reference files:
    assert "If a slide requires 3+ distinct explanatory beats" in user
    assert "From [start state] to [end state]" in user
    # The three references are named in the loaded set.
    assert "cluster-decision-criteria.md" in user
    assert "cluster-narrative-arc-schema.md" in user
    assert "cluster-density-controls.md" in user


def test_ac2_references_registered_in_pass1_references() -> None:
    for name in (
        "cluster-decision-criteria.md",
        "cluster-narrative-arc-schema.md",
        "cluster-density-controls.md",
    ):
        assert name in pass1_act.PASS_1_REFERENCES


# --------------------------------------------------------------------------- #
# AC-3 — parse preserves clusters; head + 2 interstitials -> 3 units           #
# --------------------------------------------------------------------------- #
def test_ac3_parse_preserves_cluster_fields() -> None:
    raw = json.dumps(
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
                    "narrative_arc": "From confusion to clarity through disclosure",
                    "cluster_interstitial_count": 2,
                },
                {
                    "unit_id": "u2",
                    "title": "Inter 1",
                    "learning_objective": "lo",
                    "scope_decision": "in-scope",
                    "rationale": "r",
                    "cluster_id": "c-u1",
                    "cluster_role": "interstitial",
                    "cluster_position": "tension",
                    "parent_slide_id": "u1",
                },
                {
                    "unit_id": "u3",
                    "title": "Inter 2",
                    "learning_objective": "lo",
                    "scope_decision": "in-scope",
                    "rationale": "r",
                    "cluster_id": "c-u1",
                    "cluster_role": "interstitial",
                    "cluster_position": "develop",
                    "parent_slide_id": "u1",
                },
            ],
        }
    )
    plan = pass1_act.parse_pass1_response(raw)
    units = plan["plan_units"]
    assert len(units) == 3
    assert {u["cluster_id"] for u in units} == {"c-u1"}
    head = next(u for u in units if u["cluster_role"] == "head")
    assert head["narrative_arc"] == "From confusion to clarity through disclosure"
    assert head["cluster_position"] == "establish"
    assert sum(1 for u in units if u["cluster_role"] == "interstitial") == 2


# --------------------------------------------------------------------------- #
# AC-4 — normalize_clusters backstop                                          #
# --------------------------------------------------------------------------- #
def test_ac4_normalize_singleton_gets_id_role_position_and_zero_count() -> None:
    plan = {"plan_units": [{"unit_id": "solo", "title": "T"}]}
    out = pass1_act.normalize_clusters(plan)
    unit = out["plan_units"][0]
    assert unit["cluster_id"]  # non-empty derived id
    assert unit["cluster_role"] == "head"
    assert unit["cluster_position"] == "establish"
    assert unit["cluster_interstitial_count"] == 0


def test_ac4_interstitial_inherits_head_narrative_arc() -> None:
    plan = {
        "plan_units": [
            {
                "unit_id": "h",
                "cluster_id": "c-h",
                "cluster_role": "head",
                "narrative_arc": "From A to B through C",
            },
            {
                "unit_id": "i",
                "cluster_id": "c-h",
                "cluster_role": "interstitial",
                "parent_slide_id": "h",
            },
        ]
    }
    out = pass1_act.normalize_clusters(plan)
    inter = next(u for u in out["plan_units"] if u["unit_id"] == "i")
    assert inter["narrative_arc"] == "From A to B through C"


def test_ac4_invalid_cluster_position_on_head_coerced_to_establish() -> None:
    plan = {
        "plan_units": [
            {
                "unit_id": "h",
                "cluster_id": "c-h",
                "cluster_role": "bogus-role",
                "cluster_position": "not-a-position",
            }
        ]
    }
    out = pass1_act.normalize_clusters(plan)
    unit = out["plan_units"][0]
    # invalid role -> head; a head anchors at establish (NOT left None).
    assert unit["cluster_role"] == "head"
    assert unit["cluster_position"] == "establish"


def test_ac4_invalid_cluster_position_on_interstitial_dropped_to_none() -> None:
    # An interstitial's invalid position must NOT be forced to establish.
    plan = {
        "plan_units": [
            {"unit_id": "h", "cluster_id": "c-h", "cluster_role": "head",
             "cluster_position": "establish"},
            {"unit_id": "i", "cluster_id": "c-h", "cluster_role": "interstitial",
             "parent_slide_id": "h", "cluster_position": "not-a-position"},
        ]
    }
    out = pass1_act.normalize_clusters(plan)
    inter = next(u for u in out["plan_units"] if u["unit_id"] == "i")
    assert inter["cluster_position"] is None


def test_ac4_interstitial_cluster_id_reconciled_to_parent_head() -> None:
    # MAJOR (T11): an interstitial with a VALID parent but a divergent
    # cluster_id must be reconciled to the parent head's cluster_id so count +
    # arc inheritance + Gary grouping stay mutually consistent.
    plan = {
        "plan_units": [
            {"unit_id": "h", "cluster_id": "c-h", "cluster_role": "head",
             "narrative_arc": "From A to B through C"},
            {"unit_id": "i", "cluster_id": "c-WRONG", "cluster_role": "interstitial",
             "parent_slide_id": "h"},
        ]
    }
    out = pass1_act.normalize_clusters(plan)
    inter = next(u for u in out["plan_units"] if u["unit_id"] == "i")
    head = next(u for u in out["plan_units"] if u["unit_id"] == "h")
    assert inter["cluster_id"] == "c-h"  # reconciled to the parent head
    assert inter["narrative_arc"] == "From A to B through C"
    assert head["cluster_interstitial_count"] == 1  # head now counts the member


def test_ac4_interstitial_linked_by_cluster_id_when_parent_missing() -> None:
    # Parent-fallback: model omitted parent_slide_id but gave a matching
    # cluster_id -> still resolved to the head (more forgiving of real output).
    plan = {
        "plan_units": [
            {"unit_id": "h", "cluster_id": "c-h", "cluster_role": "head"},
            {"unit_id": "i", "cluster_id": "c-h", "cluster_role": "interstitial"},
        ]
    }
    out = pass1_act.normalize_clusters(plan)
    inter = next(u for u in out["plan_units"] if u["unit_id"] == "i")
    head = next(u for u in out["plan_units"] if u["unit_id"] == "h")
    assert inter["cluster_role"] == "interstitial"  # NOT demoted
    assert inter["cluster_id"] == "c-h"
    assert head["cluster_interstitial_count"] == 1


def test_ac4_duplicate_head_cluster_ids_are_split() -> None:
    # Two heads claiming the same cluster_id must end up distinct (no merge).
    plan = {
        "plan_units": [
            {"unit_id": "h1", "cluster_id": "c-dup", "cluster_role": "head"},
            {"unit_id": "h2", "cluster_id": "c-dup", "cluster_role": "head"},
        ]
    }
    out = pass1_act.normalize_clusters(plan)
    cids = {u["cluster_id"] for u in out["plan_units"]}
    assert len(cids) == 2  # the collision was split


def test_ac4_missing_and_duplicate_unit_ids_do_not_collapse() -> None:
    # Distinct id-less / duplicate-id singletons must not collapse into one
    # cluster (index-stable synthetic keys).
    plan = {
        "plan_units": [
            {"title": "no id A"},
            {"title": "no id B"},
            {"unit_id": "dup"},
            {"unit_id": "dup"},
        ]
    }
    out = pass1_act.normalize_clusters(plan)
    cids = [u["cluster_id"] for u in out["plan_units"]]
    assert len(set(cids)) == 4  # all four are distinct clusters


def test_ac4_normalize_clusters_handles_non_dict_plan() -> None:
    assert pass1_act.normalize_clusters(None) == {"plan_units": []}
    assert pass1_act.normalize_clusters([1, 2]) == {"plan_units": []}


def test_ac4_orphan_interstitial_demoted_to_singleton_head() -> None:
    plan = {
        "plan_units": [
            {
                "unit_id": "i",
                "cluster_id": "c-x",
                "cluster_role": "interstitial",
                "parent_slide_id": "nonexistent",
            }
        ]
    }
    out = pass1_act.normalize_clusters(plan)
    unit = out["plan_units"][0]
    assert unit["cluster_role"] == "head"
    assert unit["cluster_position"] == "establish"
    # no orphan parent reference leaks downstream
    assert not unit.get("parent_slide_id")


def test_ac4_cluster_interstitial_count_recomputed_from_members() -> None:
    plan = {
        "plan_units": [
            {
                "unit_id": "h",
                "cluster_id": "c-h",
                "cluster_role": "head",
                "cluster_interstitial_count": 99,  # stale model count
            },
            {"unit_id": "i1", "cluster_id": "c-h", "cluster_role": "interstitial",
             "parent_slide_id": "h"},
            {"unit_id": "i2", "cluster_id": "c-h", "cluster_role": "interstitial",
             "parent_slide_id": "h"},
        ]
    }
    out = pass1_act.normalize_clusters(plan)
    head = next(u for u in out["plan_units"] if u["unit_id"] == "h")
    assert head["cluster_interstitial_count"] == 2


def test_ac4_normalize_is_idempotent() -> None:
    plan = {
        "plan_units": [
            {"unit_id": "h", "cluster_id": "c-h", "cluster_role": "head",
             "narrative_arc": "From A to B through C", "cluster_interstitial_count": 5},
            {"unit_id": "i", "cluster_id": "c-h", "cluster_role": "interstitial",
             "parent_slide_id": "h"},
            {"unit_id": "orphan", "cluster_id": "c-z", "cluster_role": "interstitial",
             "parent_slide_id": "ghost"},
            {"unit_id": "solo", "title": "S"},
        ]
    }
    once = pass1_act.normalize_clusters(plan)
    twice = pass1_act.normalize_clusters(once)
    assert once == twice


def test_ac4_normalize_clusters_is_pure_no_mutation() -> None:
    plan = {"plan_units": [{"unit_id": "solo"}]}
    snapshot = json.dumps(plan, sort_keys=True)
    pass1_act.normalize_clusters(plan)
    assert json.dumps(plan, sort_keys=True) == snapshot


def test_ac4_normalize_clusters_in_all() -> None:
    assert "normalize_clusters" in pass1_act.__all__


def test_cluster_literal_tuples_match_pass2_canonical_sets() -> None:
    # Amelia/Winston T11 drift-guard: _act.py duplicates the canonical cluster
    # Literals as plain tuples (minimal import surface). Pin them to the Pass-2
    # source-of-truth so a future divergence fails CI instead of drifting silently.
    from typing import get_args

    from app.specialists.irene.authoring.pass_2_template import (
        ClusterPosition,
        ClusterRole,
    )

    assert set(pass1_act.CLUSTER_ROLES) == set(get_args(ClusterRole))
    assert set(pass1_act.CLUSTER_POSITIONS) == set(get_args(ClusterPosition))


# --------------------------------------------------------------------------- #
# AC-5 — fallback unit becomes a normalized size-1 cluster                     #
# --------------------------------------------------------------------------- #
def test_ac5_fallback_unit_is_size1_cluster() -> None:
    plan = pass1_act.parse_pass1_response("this is not json at all")
    units = plan["plan_units"]
    assert len(units) == 1
    unit = units[0]
    assert unit["cluster_role"] == "head"
    assert unit["cluster_position"] == "establish"
    assert unit["cluster_id"]
    assert unit["cluster_interstitial_count"] == 0


# --------------------------------------------------------------------------- #
# AC-6 — artifact witness carries cluster fields                              #
# --------------------------------------------------------------------------- #
def test_ac6_write_lesson_plan_emits_cluster_fields(tmp_path) -> None:
    plan = {
        "lesson_summary": "summary",
        "plan_units": [
            {
                "unit_id": "h",
                "title": "Head",
                "learning_objective": "lo",
                "scope_decision": "in-scope",
                "rationale": "r",
                "cluster_id": "c-h",
                "cluster_role": "head",
                "cluster_position": "establish",
                "narrative_arc": "From A to B through C",
                "cluster_interstitial_count": 1,
            },
            {
                "unit_id": "i",
                "title": "Inter",
                "learning_objective": "lo",
                "scope_decision": "in-scope",
                "rationale": "r",
                "cluster_id": "c-h",
                "cluster_role": "interstitial",
                "cluster_position": "tension",
                "narrative_arc": "From A to B through C",
                "parent_slide_id": "h",
            },
        ],
    }
    path = pass1_act.write_lesson_plan(plan, run_id="run-ac6", runs_root=tmp_path)
    text = path.read_text(encoding="utf-8")
    assert "c-h" in text
    assert "head" in text
    assert "establish" in text
    assert "From A to B through C" in text
    assert "parent_slide_id" in text.lower() or "Parent slide" in text
    # flat fields still present (additive)
    assert "Learning objective" in text
    assert "Scope decision" in text


# --------------------------------------------------------------------------- #
# AC-7 — tolerance of absence: no cluster fields anywhere                      #
# --------------------------------------------------------------------------- #
def test_ac7_cluster_absent_plan_parses_normalizes_writes(tmp_path) -> None:
    raw = json.dumps(
        {
            "lesson_summary": "flat",
            "plan_units": [
                {
                    "unit_id": "f1",
                    "title": "Flat",
                    "learning_objective": "lo",
                    "scope_decision": "in-scope",
                    "rationale": "r",
                }
            ],
        }
    )
    plan = pass1_act.parse_pass1_response(raw)
    unit = plan["plan_units"][0]
    # degrades to a singleton size-1 cluster, never crashes
    assert unit["cluster_role"] == "head"
    assert unit["cluster_position"] == "establish"
    assert unit["cluster_id"]
    # write works
    path = pass1_act.write_lesson_plan(plan, run_id="run-ac7", runs_root=tmp_path)
    assert path.is_file()


def test_ac7_cluster_absent_segments_validate_in_pass2_envelope() -> None:
    from app.specialists.irene.authoring.pass_2_template import (
        REQUIRED_PROCEDURAL_RULES,
        IrenePass2AuthoringEnvelope,
    )

    png = "runs/probe/slide_01.png"

    def seg(sid: str, slide: str, card: int) -> dict:
        return {
            "id": sid,
            "slide_id": slide,
            "card_number": card,
            "narration_text": "Probe narration line for the segment here.",
            "behavioral_intent": "credible",
            "visual_file": png,
            "visual_detail_load": "medium",
            "timing_role": "anchor",
            "content_density": "medium",
            "duration_rationale": "Probe rationale for timing.",
            "bridge_type": "none",
            "visual_references": [
                {
                    "element": "title",
                    "location_on_slide": "top",
                    "narration_cue": "Probe narration line for the segment here.",
                    "perception_source": slide,
                }
            ],
        }

    envelope = {
        "schema_version": "irene-pass-2-authoring.v1",
        "run_id": "ac7-run",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "composition_mode": "isolated",
        "gary_slide_output": [
            {"slide_id": "s1", "card_number": 1, "file_path": png, "source_ref": "src1"},
        ],
        "perception_artifacts": [
            {"slide_id": "s1", "source_image_path": png, "visual_elements": []},
        ],
        "segment_manifest": {"segments": [seg("seg1", "s1", 1)]},
        "narration_script_markers": ["seg1"],
        "procedural_rules": list(REQUIRED_PROCEDURAL_RULES),
    }
    model = IrenePass2AuthoringEnvelope.model_validate(envelope)
    assert model.segment_manifest.segments[0].cluster_id is None


# --------------------------------------------------------------------------- #
# AC-8 — downstream round-trip through Gary _derive_clusters                   #
# --------------------------------------------------------------------------- #
def _load_rgd():
    spec = importlib.util.spec_from_file_location(
        "rgd_ac8", REPO_ROOT / "scripts" / "utilities" / "run_gary_dispatch.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ac8_cluster_bearing_units_round_trip_to_gary() -> None:
    rgd = _load_rgd()
    raw = json.dumps(
        {
            "lesson_summary": "x",
            "plan_units": [
                {"unit_id": "h1", "cluster_id": "c-h1", "cluster_role": "head",
                 "cluster_position": "establish",
                 "narrative_arc": "From overload to capacity through interventions",
                 "cluster_interstitial_count": 2},
                {"unit_id": "i1", "cluster_id": "c-h1", "cluster_role": "interstitial",
                 "parent_slide_id": "h1"},
                {"unit_id": "i2", "cluster_id": "c-h1", "cluster_role": "interstitial",
                 "parent_slide_id": "h1"},
                {"unit_id": "h2", "cluster_id": "c-h2", "cluster_role": "head",
                 "cluster_position": "establish",
                 "narrative_arc": "From skepticism to confidence through evidence"},
                {"unit_id": "i3", "cluster_id": "c-h2", "cluster_role": "interstitial",
                 "parent_slide_id": "h2"},
            ],
        }
    )
    plan = pass1_act.parse_pass1_response(raw)
    # Gary reads slide rows; the emitted plan_units carry the same cluster keys.
    derived = rgd._derive_clusters(plan["plan_units"], envelope={})
    assert len(derived) == 2
    by_id = {c["cluster_id"]: c for c in derived}
    assert by_id["c-h1"]["interstitial_count"] == 2
    assert by_id["c-h2"]["interstitial_count"] == 1  # recomputed/derived from members
    assert "overload" in (by_id["c-h1"]["narrative_arc"] or "")


# --------------------------------------------------------------------------- #
# AC-5/round-trip — act() carries cluster fields into locked_scope             #
# --------------------------------------------------------------------------- #
def test_act_locked_scope_carries_cluster_fields(tmp_path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "extracted.md").write_text("# Corpus\n\nSource.", encoding="utf-8")
    response = json.dumps(
        {
            "lesson_summary": "summary",
            "plan_units": [
                {
                    "unit_id": "h",
                    "title": "Head",
                    "learning_objective": "lo",
                    "scope_decision": "in-scope",
                    "rationale": "r",
                    "cluster_id": "c-h",
                    "cluster_role": "head",
                    "cluster_position": "establish",
                    "narrative_arc": "From A to B through C",
                    "cluster_interstitial_count": 1,
                },
                {
                    "unit_id": "i",
                    "title": "Inter",
                    "learning_objective": "lo",
                    "scope_decision": "in-scope",
                    "rationale": "r",
                    "cluster_id": "c-h",
                    "cluster_role": "interstitial",
                    "parent_slide_id": "h",
                },
            ],
        }
    )
    update = pass1_act.act(
        _state(
            {
                "mode": "pass-1",
                "run_id": "run-ls",
                "runs_root": str(tmp_path),
                "bundle_reference": str(bundle),
            }
        ),
        handle=_FakeHandle(response),
        model_id="gpt-5.4",
    )
    output = json.loads(update["cache_state"]["cache_prefix"])
    units = output["locked_scope"]["plan_units"]
    head = next(u for u in units if u["unit_id"] == "h")
    assert head["cluster_id"] == "c-h"
    assert head["cluster_role"] == "head"
    assert head["narrative_arc"] == "From A to B through C"
