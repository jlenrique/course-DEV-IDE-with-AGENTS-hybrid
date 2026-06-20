from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from app.specialists.quinn_r.graph import (
    ModeMismatchError,
    QRRParseError,
    _act,
    _parse_qrr,
)
from tests.specialists.quinn_r.conftest import make_state


def _payload(tmp_path: Path, *, gate_id: str = "G2C") -> str:
    return json.dumps(
        {
            "gate_id": gate_id,
            # dp-v1.1: every quinn_r manifest gate is pre-composition; the
            # post body is gate_phase-fallback only (no manifest gate maps it).
            "gate_phase": "pre-composition",
            "runs_root": str(tmp_path),
            "gary_slide_output": [{"slide_id": "s1", "file_path": "s1.png"}],
            "narration_script": [{"id": "seg-1", "narration_text": "Opening."}],
            "segment_manifest_deltas": [
                {"id": "seg-1", "visual_references": [{"perception_source": "s1"}]}
            ],
            "artifact_path": str(tmp_path / "assembled.mp4"),
            "modality": "video",
            "slides": [
                {
                    "slide_id": "s1",
                    "title": "Intro",
                    "narration_pointer": "narration/s1.vtt",
                    "motion_pointer": "motion/s1.mp4",
                    "evidence_block": "fixture",
                }
            ],
            "perception_artifacts": [
                {
                    "artifact_path": "fixtures/s1.png",
                    "card_number": 1,
                    "confidence": "HIGH",
                    "coverage": "perceived",
                    "extracted_text": "Opening.",
                    "layout_description": "Intro title slide.",
                    "slide_id": "s1",
                    "slide_title": "Intro",
                    "text_blocks": [{"text": "Opening"}],
                    "visual_elements": [{"kind": "title", "label": "intro title"}],
                }
            ],
            "narration_profile_controls": {"target_wpm": 120},
            "vtt_text": "WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nhello\n",
            "narration_segments": [
                {
                    "slide_id": "s1",
                    "text": "one two three four five six seven eight nine ten",
                    "duration_seconds": 5,
                    "motion_duration_seconds": 5.3,
                }
            ],
        }
    )


@pytest.mark.parametrize(
    "raw,expected",
    [
        (
            '{"status":"pass","severity":"low","summary":"ok","findings":[{"id":"1"}],"dimension_scores":{"accessibility":"PASS"}}',
            "pass",
        ),
        (
            '{"status":"warning","severity":"medium","summary":"ok","findings":[{"id":"1"}],"dimension_scores":{"accessibility":"WARN"}}',
            "warn",
        ),
        (
            '```json\n{"status":"failed","severity":"high","summary":"ok","findings":[{"id":"1"}],"dimension_scores":{"accessibility":"WARN"}}\n```',
            "fail",
        ),
    ],
)
def test_parse_qrr_ok(raw: str, expected: str) -> None:
    out = _parse_qrr(raw)
    assert out["status"] == expected


def test_parse_qrr_branch_error_tag() -> None:
    with pytest.raises(QRRParseError, match="parse failed") as exc_info:
        _parse_qrr("{bad")
    assert exc_info.value.tag == "qrr.parsed.malformed"


def test_quinn_r_act_g2c_writes_authorized_storyboard(tmp_path: Path) -> None:
    state = make_state(_payload(tmp_path, gate_id="G2C"))
    update = _act(state)
    payload = json.loads(update["cache_state"]["cache_prefix"])
    artifact = Path(payload["quinn_r_review"]["artifact_paths"][0])
    assert artifact.name == "authorized-storyboard.json"
    assert payload["quinn_r_review"]["mode"] == "pre-composition"
    assert update["model_resolution_trail"][-1].reason == "qrr.parsed.ok"


def test_quinn_r_act_g5_runs_structured_qa(tmp_path: Path) -> None:
    state = make_state(_payload(tmp_path, gate_id="G5"))
    update = _act(state)
    verdict = json.loads(update["cache_state"]["cache_prefix"])["quinn_r_review"]
    assert verdict["checks"] == ["wpm", "vtt", "coverage", "fidelity", "duration", "partition"]
    assert verdict["blocking"] == []
    assert verdict["advisory"] == []


def test_quinn_r_act_g3b_runs_storyboard_b_review(tmp_path: Path) -> None:
    # dp-v1.1: G3B no longer dispatches sensory bridges (the cycle-4 crash);
    # it reviews Pass-2 narration against Gary's real slide roster.
    state = make_state(_payload(tmp_path, gate_id="G3B"))
    update = _act(state)
    verdict = json.loads(update["cache_state"]["cache_prefix"])["quinn_r_review"]
    assert verdict["mode"] == "storyboard-b-review"
    assert verdict["status"] == "reviewed"


def test_quinn_r_act_mode_mismatch_fails_loudly(tmp_path: Path) -> None:
    bad = json.loads(_payload(tmp_path, gate_id="G2C"))
    bad["gate_phase"] = "post-composition"
    state = make_state(json.dumps(bad))
    with pytest.raises(ModeMismatchError):
        _act(state)


def test_quinn_r_act_body_loc_budget() -> None:
    import app.specialists.quinn_r._act as act_module

    source = inspect.getsource(act_module)
    logical_lines = [line for line in source.splitlines() if line.strip()]
    # Budget 150 -> 160 at Trial-3 finding #10 (2026-06-11): G2B variant-selection
    # + G2F motion-gate bodies added (manifest dispatches Quinn-R at 5 gates; only
    # 3 had bodies). 160 -> 168 at dp-v1.1 (2026-06-12): G3B storyboard_b body
    # replaces the post mapping that crashed cycle-4 live. 168 -> 180 at
    # dp-v1.2 audio-arc (2026-06-12): G5 grounding wire + fabricated-default
    # kill (raise replaces the slide-1 roster) + duration-aware WPM raise;
    # the heavy lifting lives in quality_control_dispatch. Bounded headroom,
    # not an open ceiling. 180 -> 186 at BETA S0.1 crash-taxonomy guard
    # (2026-06-19): ModeMismatchError dual-rebased onto SpecialistDispatchError
    # (+ keyword-only tag ctor) so a mode-miss error-pauses recoverably instead
    # of crashing the walk (the Trial-4 node-07B crash); +1 import line.
    # 186 -> 200 at P1 voice-agnostic WPM floor (2026-06-19; party-mode §2
    # green-light, beta-phase-1-closure-ratification §5): band constants +
    # break-glass branch (~6 logical lines) PLUS a party-mandated provenance
    # comment block (Amendment 1: n=1/INTERIM floor + re-validation trigger +
    # ceiling "no-natural-basis" disclosure). logical_lines counts comments,
    # so the mandated documentation consumes budget by design here. 200 -> 205
    # at P2-1 (2026-06-19): one G5 fidelity-detector hook + re-export, with
    # detector complexity isolated in fidelity_detector.py. 205 -> 220 at P2-1
    # T11 (Edge-1 ratified tripwire posture): the absent-perception dormant
    # branch + its party-ratified rationale comment (Winston B+tripwire).
    # 220 -> 222 at P2-2 T11 (2026-06-20; party-mode 5/5 D1 ratified the M3
    # remediation): FIDELITY_GATE=warn downgrade is now scoped to narration-only
    # failures (`or exc.scope != "narration"` guard), so structural FidelityErrors
    # still raise under warn. +2 logical lines = the honest cost of the M3 fix;
    # bump matches the documented-evolving-budget pattern (cf. 205->220 at P2-1 T11).
    assert len(logical_lines) <= 222
