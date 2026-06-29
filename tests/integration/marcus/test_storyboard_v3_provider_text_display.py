"""Story enhanced-vo.2 (AC-B9) — Storyboard B shows literal v3 provider bytes.

Before any live spend, the operator-facing review must show, side by side: the
canonical narration, the literal ``provider_text`` (tags inline), the
rhetorical_role, AND the captions channel PROVING zero tag-leak. Computed via the
SAME compiler Enrique drives (display<->dispatch parity), fed from manifest-B.

Drives the REAL legacy ``generate-storyboard.py`` panel routine (loaded the same
way the publisher loads it). Offline; no live API.
"""

from __future__ import annotations

from app.marcus.orchestrator import storyboard_publisher
from app.specialists._shared import voice_provider_text as vpt

MODULE = storyboard_publisher._load_generator_module()

CANONICAL = "Remember access. The next decision changes the patient's path."

V3_DIRECTED_VD = {
    "schema_version": "voice-direction.v1",
    "render_strategy": "tts",
    "emotional_tone": "warm",
    "rhetorical_role": "warm_callback",
    "elevenlabs": {"model_id": "eleven_v3"},
    "source": "cd-authored",
}


def _render(vd: dict, narration_text: str) -> str:
    return MODULE._render_voice_direction_section(
        [{"segment_id": "seg-01", "voice_direction": vd, "narration_text": narration_text}]
    )


def test_storyboard_b_shows_provider_text_and_captions_zero_leak() -> None:
    html = _render(V3_DIRECTED_VD, CANONICAL)
    provider = vpt.compile_provider_text(CANONICAL, rhetorical_role="warm_callback")
    # The literal provider bytes (tag inline) are shown to the operator.
    assert "[warm]" in html
    assert "warm_callback" in html
    # The captions channel is shown and is the CANONICAL narration (no tag leak).
    # The provider markup carries the tag; the captions markup must not.
    assert "data-role=\"provider-text\"" in html or "provider-text" in html
    assert "data-role=\"captions-text\"" in html or "captions" in html
    # Display<->dispatch parity: the shown provider equals the compiler output.
    import html as _html

    assert _html.escape(provider) in html


def test_storyboard_b_non_v3_shows_no_block() -> None:
    # A populated role but NON-v3 model -> no provider block AND no failure marker
    # (dispatch is plain v2 — nothing to preview, nothing fails).
    non_v3 = {
        "schema_version": "voice-direction.v1",
        "render_strategy": "tts",
        "rhetorical_role": "warm_callback",
    }
    html2 = _render(non_v3, CANONICAL)
    assert "[warm]" not in html2
    assert "WILL FAIL AT DISPATCH" not in html2


def test_storyboard_b_deferred_role_shows_will_fail_at_dispatch() -> None:
    # S2: a v3 model + DEFERRED role will FAIL LOUD at Enrique dispatch (S1). The
    # panel must SHOW that failure (not a clean/blank panel the operator approves
    # before the paid run crashes).
    deferred = dict(V3_DIRECTED_VD, rhetorical_role="curious_pivot")
    html = _render(deferred, CANONICAL)
    assert "WILL FAIL AT DISPATCH" in html
    assert "curious_pivot" in html


def test_storyboard_b_pathological_canonical_shows_failure_not_blank() -> None:
    # S2: a populated role but a canonical that already carries a literal [warm] tag
    # fails compile -> the panel surfaces the failure rather than swallowing it.
    html = _render(V3_DIRECTED_VD, "[warm] already tagged narration body")
    assert "WILL FAIL AT DISPATCH" in html
