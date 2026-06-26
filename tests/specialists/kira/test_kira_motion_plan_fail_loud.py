"""S1 motion-restore: kira fails LOUD on a starved/empty motion plan.

BUG-REPRO (RED on pre-S1 code): the migration starved kira 07E of any
motion-plan input and ``_load_motion_plan`` converted that starvation into a
silent ``{"slides": []}`` default -> zero Kling iterations -> ``motion_receipts:
[]`` while provenance reported "real" (investigations/motion-receipts-cycle-5-6
-investigation.md, Finding 3). S1 makes the absence a CONTRACT VIOLATION:
absence of inputs is never a mode switch (S0 doctrine).

These are pure-Python contract tests (no Kling call — the raise fires in
``_load_motion_plan`` / before any provider invocation), so no live API and no
mock provider is needed. The live .mp4 proof lives in
``tests/test_integration_kira_motion.py`` (outside the kira specialist dir so
the no-live-import guard stays green).
"""

from __future__ import annotations

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.kira import _act as kira_act
from app.specialists.kira.graph import _plan


class _UnusedClient:
    """A client that explodes if touched — proves the raise precedes dispatch."""

    def generate_motion(self, **kwargs: object) -> dict[str, object]:  # pragma: no cover
        raise AssertionError("Kling must not be invoked when the plan is starved")


def test_generate_motion_raises_on_missing_motion_plan() -> None:
    """No motion_plan key + no motion_plan_path + no slides -> raise (not silent)."""
    with pytest.raises(kira_act.KiraActError) as exc_info:
        kira_act.generate_motion_from_plan({}, client=_UnusedClient())  # type: ignore[arg-type]
    assert exc_info.value.tag == "kira.motion-plan.missing"


def test_generate_motion_raises_on_empty_slides() -> None:
    """An explicitly delivered plan with zero slides is still a starvation."""
    payload = {"motion_plan": {"slides": []}}
    with pytest.raises(kira_act.KiraActError) as exc_info:
        kira_act.generate_motion_from_plan(payload, client=_UnusedClient())  # type: ignore[arg-type]
    assert exc_info.value.tag == "kira.motion-plan.empty"


def test_kira_act_error_pauses_on_starved_envelope() -> None:
    """The act() seam converts starvation into a recoverable error-pause.

    KiraActError subclasses SpecialistDispatchError, so the production runner
    error-pauses (recoverable) instead of killing the trial; act() must also
    stamp the failure tag onto the resolution trail before re-raising.
    """
    state = RunState(graph_version="v0.1-stub", temperature=0.0)
    plan_update = _plan(state)
    state = state.model_copy(
        update={
            "model_resolution_trail": plan_update["model_resolution_trail"],
            "cache_state": CacheState(cache_prefix="{}", entries_count=1),
        }
    )
    trail_len_before = len(state.model_resolution_trail)

    with pytest.raises(kira_act.KiraActError) as exc_info:
        kira_act.act(state, client=_UnusedClient())  # type: ignore[arg-type]

    assert isinstance(exc_info.value, SpecialistDispatchError)
    assert exc_info.value.tag == "kira.motion-plan.missing"
    # The error-pause stamps the failing tag onto the trail (recoverable seam).
    assert len(state.model_resolution_trail) == trail_len_before + 1
    assert state.model_resolution_trail[-1].reason == "kira.motion-plan.missing"


def test_kira_real_plan_still_dispatches(tmp_path: object) -> None:
    """A real, non-empty plan is unaffected by the fail-loud change (GREEN guard)."""
    from pathlib import Path

    class _RecordingClient:
        def __init__(self) -> None:
            self.calls: list[dict[str, object]] = []

        def generate_motion(self, **kwargs: object) -> dict[str, object]:
            self.calls.append(kwargs)
            return {
                "data": {
                    "task_id": "task-001",
                    "task_status": "succeed",
                    "task_result": {"videos": [{"url": "https://cdn.test/s1.mp4"}]},
                }
            }

        def download_video(self, video_url: object, output_path: object) -> Path:
            p = Path(str(output_path))
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"\x00\x00\x00\x18ftypmp42moovmdat")
            return p

    client = _RecordingClient()
    payload = {
        "bundle_path": str(tmp_path),
        "motion_plan": {
            "slides": [
                {"slide_id": "slide-01", "kling_prompt": "slow push-in", "estimated_cost_usd": 0.0}
            ]
        },
    }
    verdict = kira_act.generate_motion_from_plan(payload, client=client)  # type: ignore[arg-type]
    assert len(client.calls) == 1
    receipt = verdict["motion_receipts"][0]
    assert receipt["status"] == "success"
    # The CDN url is recorded as the source; the asset is the materialized local file.
    assert receipt["motion_source_url"] == "https://cdn.test/s1.mp4"
    expected_asset = str((Path(str(tmp_path)) / "motion" / "slide-01.mp4").resolve())
    assert receipt["motion_asset_path"] == expected_asset
