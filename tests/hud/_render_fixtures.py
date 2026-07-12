"""Projection + panel-state fixtures for the flight-deck render goldens (35.5).

Plain projection *dicts* (the render layer consumes lenient-parsed dicts, never
strict models — AD-4/12), built deterministically so the golden matrix is a
stable byte pin. ``NOW`` and the section ``as_of`` values are fixed so age
stamps ("… · 5s ago") and the staleness veil are reproducible.

The v1 golden matrix (party greenlight amendment 10, BINDING):
7 envelope statuses + 4 panel states (no-active-run / unrecognized /
refuse-to-render / stale-veil) + the narrowed-component-selection fixture
(amendment 11) + a legacy-shaped-dir → UNRECOGNIZED case (rendered via the
server route in the goldens test).
"""

from __future__ import annotations

from typing import Any

TRIAL = "22b27500-6e67-4dd7-8308-fd89defe3d99"
OTHER = "33333333-3333-4333-8333-333333333333"

NOW = "2026-07-11T12:00:00+00:00"
_T5 = "2026-07-11T11:59:55+00:00"  # 5s before NOW
_T_STALE = "2026-07-11T11:58:00+00:00"  # 120s before NOW (past 60s tile budget)

GATE_CMD = (
    "gate decide --trial-id 22b27500-6e67-4dd7-8308-fd89defe3d99 "
    "--gate-id G4A --verb approve --card-id 131e70a2 "
    "--decision-card-digest 3f8ac21 --operator-id juanl"
)
RECOVER_CMD = (
    "trial recover --trial-id 22b27500-6e67-4dd7-8308-fd89defe3d99 --reenter-at 08"
)
BATCH_CMD = (
    "trial resume-batch --trial-id 22b27500-6e67-4dd7-8308-fd89defe3d99 "
    "--batch-id batch_abc123"
)


def _identity(lesson: str = "tejal-part-4") -> dict[str, Any]:
    return {
        "as_of": _T5,
        "trial_id": TRIAL,
        "lesson": lesson,
        "preset": "production",
        "operator_id": "juanleon",
    }


def _notifications_echo(parse_status: str = "ok") -> dict[str, Any]:
    return {"as_of": _T5, "parse_status": parse_status, "config": {}}


def _base(status: str, **env: Any) -> dict[str, Any]:
    envelope = {"as_of": _T5, "status": status}
    envelope.update(env)
    return {
        "schema_version": "v1",
        "seq": 10,
        "progress_seq": 5,
        "last_progress_at": _T5,
        "envelope_digest": "deadbeef",
        "as_of": _T5,
        "identity": _identity(),
        "envelope": envelope,
        "notifications_echo": _notifications_echo(),
        "modalities": {
            "as_of": _T5,
            "llm_execution_mode": "batch",
            "detective_disposition": "on",
            "styleguide": "hil-2026-apc-crossroads-classic-preserve",
            "styleguide_provenance": "directive.yaml",
        },
    }


def _stage1(done: bool = True) -> list[dict[str, Any]]:
    st = "done" if done else "pending"
    labels = [
        ("directive-composer", "Directive Composer"),
        ("corpus-mount", "Corpus Mount + Verify"),
        ("g0-ratify-gate", "Lesson-Plan + Workflow Ratify"),
    ]
    return [
        {
            "step_id": sid,
            "label": lab,
            "stage": "stage-1",
            "status": st,
            "conditions": [],
            "blockers": [],
            "locked_artifact_summary": None,
        }
        for sid, lab in labels
    ]


def _stage2(active_id: str, active_status: str = "active") -> list[dict[str, Any]]:
    rows = [
        ("07", "Gary Dispatch + Export"),
        ("08", "Irene Pass 2 — Narration"),
        ("11", "Voice Selection"),
        ("12", "ElevenLabs Audio Generation"),
        ("15", "Package + Land"),
    ]
    out = []
    for sid, lab in rows:
        if sid == active_id:
            status = active_status
        elif int(sid) < int(active_id):
            status = "done"
        else:
            status = "pending"
        out.append(
            {
                "step_id": sid,
                "label": lab,
                "stage": "stage-2",
                "status": status,
                "conditions": ["irene cache warm"] if sid == active_id else [],
                "blockers": [],
                "locked_artifact_summary": (
                    "07-gary-dispatch/locked-summary.json" if sid == active_id else None
                ),
            }
        )
    return out


def _steps(active_id: str, active_status: str = "active", walk: int = 21) -> dict[str, Any]:
    return {
        "as_of": _T5,
        "manifest_digest": "abc123",
        "node_count": 47,
        "walk_index": walk,
        "walk_generation": 0,
        "reentered_from": None,
        "entries": _stage1() + _stage2(active_id, active_status),
    }


def _health(stale: bool = False) -> dict[str, Any]:
    tiles = [
        {
            "as_of": _T5,
            "label": "Tokens",
            "value": "1.28M",
            "unit": None,
            "confidence": "unknown",
            "threshold_state": "nominal",
            "history": [],
        },
        {
            "as_of": _T5,
            "label": "Cost",
            "value": "$0.31",
            "unit": None,
            "confidence": "proxy",
            "threshold_state": "nominal",
            "history": [],
        },
        {
            "as_of": _T_STALE if stale else _T5,
            "label": "Gamma",
            "value": "412",
            "unit": "credits",
            "confidence": "direct",
            "threshold_state": "warning" if not stale else "nominal",
            "history": [],
        },
    ]
    return {"as_of": _T5, "tiles": tiles}


def _specialists() -> dict[str, Any]:
    return {
        "as_of": _T5,
        "roster": [
            {
                "name": "Gary",
                "status": "active",
                "current_node": "07",
                "model": "gpt-5",
                "last_artifact": "07-gary-dispatch/deck-export.pptx",
                "cost_usd": 0.04,
            },
            {
                "name": "Texas",
                "status": "done",
                "current_node": "02",
                "model": None,
                "last_artifact": "02-texas/corpus.json",
                "cost_usd": 0.01,
            },
        ],
    }


def _trace() -> dict[str, Any]:
    return {
        "as_of": _T5,
        "events": [
            {"at": _T5, "event": "node 07 enter", "detail": "walk 21 · gary-dispatch"},
            {"at": _T5, "event": "cost tick", "detail": "+$0.04 · openai gpt-5"},
        ],
    }


def _next_action(command: str, pause_class: str) -> dict[str, Any]:
    return {"as_of": _T5, "command": command, "pause_class": pause_class}


def _decision_card_voice() -> dict[str, Any]:
    """G4A voice-selection shape: operator_prompt + pick_context, NO proposal."""
    return {
        "as_of": _T5,
        "gate_focus": "voice_selection",
        "operator_prompt": "Approve the proposed voice, or edit to select an alternate.",
        "drafted_proposal": None,
        "pick_context": [
            "production-runner (11-gate)",
            "runs/x/enrique.md",
            "voice options: Sarah, Shannon, Stark, Mark",
        ],
        "evidence": [],
    }


def _error_message() -> dict[str, Any]:
    return {
        "as_of": _T5,
        "message": (
            "scope=narration; slide slide-05 narration figures not present in "
            "perceived authority: ['percent:10', 'percent:90']"
        ),
        "node_index": 33,
        "tag": "irene.pass2.figure-contradiction",
    }


def _deliverables() -> dict[str, Any]:
    return {
        "as_of": _T5,
        "components": {"deck": True, "motion": True, "workbook": True},
        "total_cost_usd": 0.31,
        "export_paths": [
            "exports/deck-export.pptx",
            "exports/lesson-workbook.docx",
            "exports/motion-segment-01.mp4",
        ],
    }


# --------------------------------------------------------------------------
# Projection builders per status
# --------------------------------------------------------------------------


def registered() -> dict[str, Any]:
    return _base("registered")


def in_flight_preflight() -> dict[str, Any]:
    proj = _base("in-flight")
    proj["preflight"] = {
        "as_of": _T5,
        "items": [
            {
                "name": "environment",
                "state": "pass",
                "output": "python 3.12 venv · keys present",
                "latency_ms": 400,
                "quota_reading": None,
                "quota_confidence": "unknown",
            },
            {
                "name": "openai",
                "state": "pass",
                "output": "quota: ok",
                "latency_ms": 412,
                "quota_reading": "rate-limit headers",
                "quota_confidence": "proxy",
            },
            {
                "name": "litellm",
                "state": "fail",
                "output": "proxy failed to start on port 4000",
                "latency_ms": None,
                "quota_reading": None,
                "quota_confidence": "unknown",
            },
        ],
    }
    return proj


def in_flight_walking() -> dict[str, Any]:
    proj = _base("in-flight")
    proj["steps"] = _steps("07", "active", walk=21)
    proj["health"] = _health()
    proj["specialists"] = _specialists()
    proj["trace"] = _trace()
    return proj


def paused_at_gate() -> dict[str, Any]:
    proj = _base("paused-at-gate", paused_gate="G4A")
    proj["steps"] = _steps("11", "active", walk=35)
    proj["health"] = _health()
    proj["specialists"] = _specialists()
    proj["trace"] = _trace()
    proj["next_action"] = _next_action(GATE_CMD, "paused-at-gate")
    proj["decision_card"] = _decision_card_voice()
    return proj


def paused_at_gate_stale() -> dict[str, Any]:
    """Severity-ordering case: a stale tile AND a gate pause — gate must win."""
    proj = paused_at_gate()
    proj["health"] = _health(stale=True)
    return proj


def paused_at_error() -> dict[str, Any]:
    proj = _base("paused-at-error", paused_error_tag="irene.figure-contradiction")
    steps = _steps("08", "active", walk=33)
    steps["reentered_from"] = 8
    proj["steps"] = steps
    proj["health"] = _health()
    proj["next_action"] = _next_action(RECOVER_CMD, "paused-at-error")
    proj["error_message"] = _error_message()
    return proj


def waiting_for_provider_batch() -> dict[str, Any]:
    proj = _base("waiting_for_provider_batch", waiting_batch_id="batch_abc123")
    proj["steps"] = _steps("12", "active", walk=40)
    proj["health"] = _health()
    proj["next_action"] = _next_action(BATCH_CMD, "waiting_for_provider_batch")
    return proj


def completed() -> dict[str, Any]:
    proj = _base("completed", completed_at="2026-07-11T14:02:11+00:00")
    proj["steps"] = _steps("15", "done", walk=47)
    proj["health"] = _health()
    proj["specialists"] = _specialists()
    proj["deliverables"] = _deliverables()
    return proj


def failed() -> dict[str, Any]:
    proj = _base("failed", paused_error_tag="gary.export-timeout")
    proj["steps"] = _steps("07", "active", walk=21)
    proj["health"] = _health()
    return proj


def narrowed_component_selection() -> dict[str, Any]:
    """Amendment 11 — a small run: deck + motion + workbook only (reduced map)."""
    proj = _base("in-flight")
    entries = _stage1() + [
        {
            "step_id": "07",
            "label": "Gary Dispatch + Export (deck)",
            "stage": "stage-2",
            "status": "active",
            "conditions": [],
            "blockers": [],
            "locked_artifact_summary": None,
        },
        {
            "step_id": "07W",
            "label": "Workbook Export",
            "stage": "stage-2",
            "status": "pending",
            "conditions": [],
            "blockers": [],
            "locked_artifact_summary": None,
        },
        {
            "step_id": "13",
            "label": "Kling Motion Segments",
            "stage": "stage-2",
            "status": "pending",
            "conditions": [],
            "blockers": [],
            "locked_artifact_summary": None,
        },
    ]
    proj["steps"] = {
        "as_of": _T5,
        "manifest_digest": "small01",
        "node_count": 3,
        "walk_index": 1,
        "walk_generation": 0,
        "reentered_from": None,
        "entries": entries,
    }
    proj["health"] = _health()
    return proj


# --------------------------------------------------------------------------
# data-envelope wrappers (what render_page / render_zones consume)
# --------------------------------------------------------------------------


def ok_data(projection: dict[str, Any]) -> dict[str, Any]:
    return {
        "panel_state": "ok",
        "projection": projection,
        "bound_trial_id": TRIAL,
        "mode": "session",
        "now": NOW,
    }


def no_active_run_data() -> dict[str, Any]:
    return {
        "panel_state": "no-active-run",
        "projection": None,
        "bound_trial_id": TRIAL,
        "mode": "session",
    }


def unrecognized_data() -> dict[str, Any]:
    return {
        "panel_state": "unrecognized",
        "projection": None,
        "bound_trial_id": TRIAL,
        "mode": "session",
        "unrecognized": {
            "raw": '{"schema_version": "v99", "note": "archived legacy shape"}',
            "schema_version": "v99",
            "reason": "unknown schema_version 'v99' (expected 'v1')",
        },
    }


def refuse_to_render_data() -> dict[str, Any]:
    return {
        "panel_state": "refuse-to-render",
        "projection": None,
        "bound_trial_id": TRIAL,
        "mode": "session",
        "refuse": {"bound": TRIAL, "found": OTHER},
    }


def stale_veil_data() -> dict[str, Any]:
    return ok_data(
        {**in_flight_walking(), "health": _health(stale=True)}
    )
