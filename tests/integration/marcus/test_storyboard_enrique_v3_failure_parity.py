"""Story enhanced-vo.2 (D1, Winston) — display<->dispatch parity ON FAILURE.

A single failing v3 input is fed to BOTH call sites and they MUST AGREE:
  (i) the Storyboard-B resolver (`_resolve_v3_provider_text`) returns the "fail"
      status that renders the operator-facing "WILL FAIL AT DISPATCH" marker; AND
  (ii) Enrique pre-flight (`build_assembly_bundle` -> `_resolve_directed_plan`)
      raises ``EnriqueActError`` with a MATCHING reason.

This proves the two sites cannot silently drift — the operator never approves a
clean-looking panel for a segment that then crashes the PAID run. Offline; no API.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from app.marcus.orchestrator import storyboard_publisher
from app.specialists.enrique import _act as enrique_act
from tests.specialists.enrique._fake_elevenlabs import FakeElevenLabsClient

MODULE = storyboard_publisher._load_generator_module()
FLAG = "MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE"


def _storyboard_status(vd: dict[str, Any], narration: str) -> dict[str, Any] | None:
    return MODULE._resolve_v3_provider_text(vd, narration)


def _enrique_raises(
    tmp_path: Path, vd: dict[str, Any], narration: str
) -> enrique_act.EnriqueActError:
    client = FakeElevenLabsClient()
    seg = {"segment_id": "seg-01", "slide_id": "slide-01", "text": narration, "voice_direction": vd}
    payload = {"bundle_path": str(tmp_path), "segments": [seg]}
    with pytest.raises(enrique_act.EnriqueActError) as ei:
        enrique_act.build_assembly_bundle(
            payload, selection={"selected_voice_id": "narrator"}, client=client  # type: ignore[arg-type]
        )
    # Pre-flight refused before any synthesis spend.
    assert len(client.calls) == 0
    return ei.value


@pytest.mark.parametrize(
    ("vd", "narration", "expected_tag", "shared_token"),
    [
        # Deferred (compiler-unpopulated) rhetorical_role on the v3 model.
        (
            {"elevenlabs": {"model_id": "eleven_v3"}, "rhetorical_role": "curious_pivot"},
            "Remember access. The next decision changes the patient's path.",
            "elevenlabs.v3.role.unpopulated",
            "curious_pivot",
        ),
        # Pathological canonical that already carries a literal v3 tag.
        (
            {"elevenlabs": {"model_id": "eleven_v3"}, "rhetorical_role": "warm_callback"},
            "[warm] already tagged narration body",
            "elevenlabs.v3.canonical.contains-tag",
            "warm",
        ),
    ],
)
def test_storyboard_and_enrique_agree_on_the_same_failing_v3_input(
    tmp_path: Path,
    monkeypatch,
    vd: dict[str, Any],
    narration: str,
    expected_tag: str,
    shared_token: str,
) -> None:
    monkeypatch.setenv(FLAG, "1")

    # (i) Storyboard resolver -> fail status (renders "WILL FAIL AT DISPATCH").
    status = _storyboard_status(vd, narration)
    assert status is not None and status.get("status") == "fail"
    reason = str(status.get("reason", ""))
    assert shared_token in reason
    # The fail status is exactly what the panel turns into the operator marker.
    marker = MODULE._render_v3_failure_markup(reason)
    assert "WILL FAIL AT DISPATCH" in marker

    # (ii) Enrique pre-flight -> raises with a MATCHING reason on the IDENTICAL input.
    err = _enrique_raises(tmp_path, vd, narration)
    assert err.tag == expected_tag
    assert shared_token in str(err)
