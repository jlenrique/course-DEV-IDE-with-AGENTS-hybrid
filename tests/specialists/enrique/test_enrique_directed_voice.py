"""P5 directed-voice Step 4 — Enrique per-segment consumption (RED-first).

Drives the REAL ``build_assembly_bundle`` through the injected MUR-5
``FakeElevenLabsClient`` (deterministic, settings-sensitive, parseable bytes) so
a dropped ``voice_direction`` fails RED. No live API; the live proof is a
separate cost-bounded leg (§L).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.specialists.enrique import _act as enrique_act
from tests.specialists.enrique._fake_elevenlabs import (
    FakeElevenLabsClient,
    parse_fake_audio,
)

FLAG = "MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE"
SELECTION = {"selected_voice_id": "narrator"}


def _segment(sid: str, text: str, **extra: Any) -> dict[str, Any]:
    seg: dict[str, Any] = {"segment_id": sid, "slide_id": f"slide-{sid}", "text": text}
    seg.update(extra)
    return seg


def _build(
    tmp_path: Path,
    segments: list[dict[str, Any]],
    *,
    client: FakeElevenLabsClient,
    payload_extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {"bundle_path": str(tmp_path), "segments": segments}
    if payload_extra:
        payload.update(payload_extra)
    return enrique_act.build_assembly_bundle(payload, selection=SELECTION, client=client)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# HEADLINE (Card 3 Complete-When): adjacent segments, distinct directions ->
# distinct resolved settings AND distinct receipts; dropping a direction is
# observable.
# --------------------------------------------------------------------------- #
def test_headline_adjacent_segments_get_distinct_settings_and_receipts(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    segments = [
        _segment(
            "seg-01",
            "We pause to reflect on what we just saw.",
            voice_direction={
                "emotional_tone": "reflective",
                "pace": "slower",
                "energy": "low",
            },
        ),
        _segment(
            "seg-02",
            "Act now — the window is closing fast.",
            voice_direction={
                "emotional_tone": "urgent",
                "pace": "faster",
                "energy": "high",
            },
        ),
    ]
    result = _build(tmp_path, segments, client=client)

    receipts = result["narration_receipts"]
    assert len(receipts) == 2
    s1 = receipts[0]["effective_elevenlabs_settings"]
    s2 = receipts[1]["effective_elevenlabs_settings"]
    # Distinct resolved settings (pace->speed, energy->stability/style).
    assert s1 != s2
    assert s1["speed"] == 0.94 and s2["speed"] == 1.1
    assert s1["stability"] == 0.75 and s2["stability"] == 0.30
    assert s1["style"] == 0.10 and s2["style"] == 0.65
    # Distinct REAL-shaped request ids.
    assert receipts[0]["request_id"] != receipts[1]["request_id"]
    assert all(r["request_id"] for r in receipts)
    # S8 anti-mis-threading: each receipt carries ITS OWN call's request_id (the
    # fake's monotonic counter would let a swapped/duplicated id slip past a mere
    # `[0] != [1]` check). Order-locked to client.calls.
    assert [r["request_id"] for r in receipts] == [c.request_id for c in client.calls]

    # The settings-sensitive asserts above are the REAL guard; this `audio1 !=
    # audio2` is decorative (the two texts already differ) but cheap to keep.
    audio1 = (tmp_path / "assembly-bundle" / "audio" / "seg-01.mp3").read_bytes()
    audio2 = (tmp_path / "assembly-bundle" / "audio" / "seg-02.mp3").read_bytes()
    assert audio1 != audio2
    assert parse_fake_audio(audio1)["speed"] == "0.94"
    assert parse_fake_audio(audio2)["speed"] == "1.1"


def test_dropping_a_voice_direction_is_observable_collapse(
    tmp_path: Path, monkeypatch
) -> None:
    """The RED guarantee: a segment WITHOUT direction resolves to defaults that
    differ from the directed values — so silently dropping direction is caught."""
    monkeypatch.setenv(FLAG, "1")
    directed = FakeElevenLabsClient()
    bare = FakeElevenLabsClient()
    direction = {"emotional_tone": "urgent", "pace": "faster", "energy": "high"}
    r_directed = _build(
        tmp_path / "a",
        [_segment("seg-01", "Same words here.", voice_direction=direction)],
        client=directed,
    )
    r_bare = _build(
        tmp_path / "b",
        [_segment("seg-01", "Same words here.")],
        client=bare,
    )
    sd = r_directed["narration_receipts"][0]["effective_elevenlabs_settings"]
    sb = r_bare["narration_receipts"][0]["effective_elevenlabs_settings"]
    assert sd != sb
    # Directed: pace=faster -> 1.1. Bare: no direction -> tier-5 style_guide
    # default speed (1.0). Either way the drop is OBSERVABLE in the receipt.
    assert sd["speed"] == 1.1 and sb["speed"] == 1.0
    assert sd["stability"] == 0.30 and sb["stability"] == 0.5  # energy=high vs tier-5
    assert directed.calls[0].settings["style"] != bare.calls[0].settings["style"]


# --------------------------------------------------------------------------- #
# 5-tier per-field precedence.
# --------------------------------------------------------------------------- #
def test_explicit_elevenlabs_override_beats_derived(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    # reflective derives stability 0.62, but the explicit override must win.
    segments = [
        _segment(
            "seg-01",
            "Override wins.",
            voice_direction={
                "emotional_tone": "reflective",
                "elevenlabs": {"stability": 0.123, "speed": 1.05},
            },
        )
    ]
    result = _build(tmp_path, segments, client=client)
    settings = result["narration_receipts"][0]["effective_elevenlabs_settings"]
    assert settings["stability"] == 0.123  # explicit (tier 1) over derived (tier 2)
    assert settings["speed"] == 1.05


def test_tier5_style_guide_fills_unset_similarity_boost(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    segments = [
        _segment("seg-01", "Filled from style guide.", voice_direction={"emotional_tone": "warm"})
    ]
    result = _build(tmp_path, segments, client=client)
    settings = result["narration_receipts"][0]["effective_elevenlabs_settings"]
    # similarity_boost has no derivation; tier-5 state/config/style_guide.yaml
    # supplies 0.75.
    assert settings["similarity_boost"] == 0.75


def test_empty_segment_voice_id_is_guarded(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    segments = [
        _segment(
            "seg-01",
            "Empty voice id must not mask lower tiers.",
            voice_id="",
            voice_direction={"emotional_tone": "neutral"},
        )
    ]
    result = _build(tmp_path, segments, client=client)
    receipt = result["narration_receipts"][0]
    # "" does NOT win; falls through to the voice-selection.json default.
    assert receipt["voice_id"] == "narrator"
    assert receipt["effective_voice_source"] == "voice-selection.json"
    assert client.calls[0].voice_id == "narrator"


def test_segment_voice_id_override_is_preserved(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    segments = [
        _segment(
            "seg-01",
            "Custom voice.",
            voice_id="custom-voice-123",
            voice_direction={"emotional_tone": "warm"},
        )
    ]
    result = _build(tmp_path, segments, client=client)
    receipt = result["narration_receipts"][0]
    assert receipt["voice_id"] == "custom-voice-123"
    assert receipt["effective_voice_source"] == "segment voice_id"
    assert client.calls[0].voice_id == "custom-voice-123"


def test_explicit_elevenlabs_voice_id_beats_segment_voice_id(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    segments = [
        _segment(
            "seg-01",
            "Highest priority voice.",
            voice_id="segment-voice",
            voice_direction={"elevenlabs": {"voice_id": "explicit-voice"}},
        )
    ]
    result = _build(tmp_path, segments, client=client)
    receipt = result["narration_receipts"][0]
    assert receipt["voice_id"] == "explicit-voice"
    assert receipt["effective_voice_source"] == "voice_direction.elevenlabs.voice_id"


# --------------------------------------------------------------------------- #
# Flag-OFF byte-identical.
# --------------------------------------------------------------------------- #
def test_flag_off_is_byte_identical_legacy_behaviour(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(FLAG, raising=False)
    client = FakeElevenLabsClient()
    segments = [
        _segment(
            "seg-01",
            "Legacy global voice.",
            duration_seconds=2.5,
            # A direction present in the payload must be IGNORED when flag is OFF.
            voice_direction={"emotional_tone": "urgent", "pace": "faster"},
        ),
        _segment("seg-02", "Second.", duration_seconds=3.0),
    ]
    result = _build(tmp_path, segments, client=client)

    assert "narration_receipts" not in result
    assert not (tmp_path / "assembly-bundle" / "receipts").exists()
    legacy_keys = {
        "segment_id",
        "slide_id",
        "audio_path",
        "caption_path",
        "duration_seconds",
        "duration_source",
        "cost_usd",
    }
    for row in result["narration_outputs"]:
        assert set(row) == legacy_keys
    # Global voice for every segment; legacy positional call path used.
    assert {call.voice_id for call in client.calls} == {"narrator"}


def test_flag_off_output_matches_pre_directed_baseline(tmp_path: Path, monkeypatch) -> None:
    """Same payload, flag OFF, must serialize byte-identically run to run."""
    monkeypatch.delenv(FLAG, raising=False)
    segments = [_segment("seg-01", "Stable.", duration_seconds=2.0)]
    out_a = _build(tmp_path / "a", segments, client=FakeElevenLabsClient())
    out_b = _build(tmp_path / "b", segments, client=FakeElevenLabsClient())

    def _normalize(result: dict[str, Any]) -> str:
        rows = [
            {k: v for k, v in row.items() if k not in ("audio_path", "caption_path")}
            for row in result["narration_outputs"]
        ]
        return json.dumps(rows, sort_keys=True)

    assert _normalize(out_a) == _normalize(out_b)


# --------------------------------------------------------------------------- #
# Fail-loud on unsupported render_strategy.
# --------------------------------------------------------------------------- #
def test_unsupported_render_strategy_fails_loud(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    segments = [
        _segment(
            "seg-01",
            "Should not render single-voice.",
            voice_direction={"render_strategy": "dialogue"},
        )
    ]
    with pytest.raises(enrique_act.EnriqueActError) as exc:
        _build(tmp_path, segments, client=client)
    assert exc.value.tag == "elevenlabs.render-strategy.unsupported"
    # Refused BEFORE spend: no audio synthesized.
    assert client.calls == []


def test_malformed_voice_direction_fails_loud(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    segments = [
        _segment(
            "seg-01",
            "Bad enum.",
            voice_direction={"emotional_tone": "skeptical"},  # not a v1 enum
        )
    ]
    with pytest.raises(enrique_act.EnriqueActError) as exc:
        _build(tmp_path, segments, client=client)
    assert exc.value.tag == "elevenlabs.voice-direction.invalid"


# --------------------------------------------------------------------------- #
# Request-id captured into receipts.
# --------------------------------------------------------------------------- #
def test_request_id_captured_into_receipt(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    segments = [_segment("seg-01", "Track me.", voice_direction={"emotional_tone": "neutral"})]
    result = _build(tmp_path, segments, client=client)
    receipt = result["narration_receipts"][0]
    assert receipt["request_id"] == client.calls[0].request_id
    # Receipt is also persisted to disk.
    on_disk = json.loads(
        (tmp_path / "assembly-bundle" / "receipts" / "seg-01.json").read_text(encoding="utf-8")
    )
    assert on_disk["request_id"] == receipt["request_id"]
    for field in (
        "segment_id",
        "voice_id",
        "render_strategy",
        "effective_voice_direction",
        "effective_elevenlabs_settings",
        "request_id",
        "model_id",
        "char_count",
        "cost_usd",
        "narration_file",
        "narration_vtt",
        "narration_duration",
    ):
        assert field in on_disk


# --------------------------------------------------------------------------- #
# pause -> RECORDED silence-padding metadata (compositor wiring is a filed
# follow-on `directed-voice-pause-padding-compositor-wiring`; NOT yet applied to
# the played audio — S5); delivery_tag never mutates narration text.
# --------------------------------------------------------------------------- #
def test_pause_seconds_recorded_as_silence_padding_metadata(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    segments = [
        _segment(
            "seg-01",
            "Padded.",
            duration_seconds=4.0,
            voice_direction={
                "emotional_tone": "neutral",
                "pause_before_seconds": 0.3,
                "pause_after_seconds": 0.6,
            },
        )
    ]
    result = _build(tmp_path, segments, client=client)
    receipt = result["narration_receipts"][0]
    assert receipt["pause_before_seconds"] == 0.3
    assert receipt["pause_after_seconds"] == 0.6
    # Padding is RECORDED into the assembled-duration metadata (NOT injected into
    # the spoken clip; the compositor must apply the silence — filed follow-on),
    # and surfaces on the assembly output row too.
    expected = round(0.3 + receipt["narration_duration"] + 0.6, 3)
    assert receipt["assembled_duration_seconds"] == expected
    assert result["narration_outputs"][0]["assembled_duration_seconds"] == expected


def test_delivery_tag_never_mutates_narration_text(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    narration = "This is the gated narration text."
    segments = [
        _segment(
            "seg-01",
            narration,
            voice_direction={"emotional_tone": "reflective", "delivery_tag": "[thoughtfully]"},
        )
    ]
    result = _build(tmp_path, segments, client=client)
    # The text sent to the synth seam is the figure-gated narration VERBATIM —
    # the tag is NOT injected (ENRIQUE-A5 firewall).
    assert client.calls[0].text == narration
    assert "[thoughtfully]" not in client.calls[0].text
    # The VTT (learner-facing captions) likewise carries only the narration.
    vtt = (tmp_path / "assembly-bundle" / "captions" / "seg-01.vtt").read_text(encoding="utf-8")
    assert "[thoughtfully]" not in vtt
    # The tag IS preserved in the receipt's effective direction (audit).
    assert result["narration_receipts"][0]["effective_voice_direction"]["delivery_tag"] == (
        "[thoughtfully]"
    )
