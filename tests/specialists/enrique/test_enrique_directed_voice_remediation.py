"""P5 directed-voice Step 4 — bmad-code-review remediation (RED-first).

Edge/Blind-layer money/proof/robustness fixes: M1 tier-3 cleaning, M2 model_id
fidelity, S1 pre-flight validation, S2 skip-if-exists, S3 null-request_id proof,
S4 malformed style_guide taxonomy, S6 single-source voice source, S7 hoisted
lookup guard. Driven through the REAL ``build_assembly_bundle`` + MUR-5 fake.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pytest

from app.specialists.enrique import _act as enrique_act
from tests.specialists.enrique._fake_elevenlabs import FakeElevenLabsClient

FLAG = "MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE"
SELECTION = {"selected_voice_id": "narrator"}
DEFAULT_MODEL = "eleven_multilingual_v2"


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
    payload: dict[str, Any] = {"bundle_path": str(tmp_path), "segments": segments}
    if payload_extra:
        payload.update(payload_extra)
    return enrique_act.build_assembly_bundle(payload, selection=SELECTION, client=client)  # type: ignore[arg-type]


# M1 — tier-3 raw-string cleaning.
def test_m1_tier3_blank_voice_id_falls_through_to_tier4(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    segments = [
        _segment("seg-01", "Blank tier-3 voice.", voice_direction={"emotional_tone": "neutral"})
    ]
    result = _build(
        tmp_path,
        segments,
        client=client,
        payload_extra={"voice_direction_defaults": {"voice_id": "", "stability": ""}},
    )
    receipt = result["narration_receipts"][0]
    # "" tier-3 voice_id must NOT mask tier-4 voice-selection.json default.
    assert receipt["voice_id"] == "narrator"
    assert receipt["effective_voice_source"] == "voice-selection.json"


def test_m1_tier3_blank_stability_not_sent_to_api(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    # pace-only direction -> NO derived stability. The blank tier-3 "" must be
    # CLEANED (never forwarded as a blank string -> 422); resolution then falls
    # through to the tier-5 style_guide default (0.5), a valid float.
    segments = [_segment("seg-01", "No blank to API.", voice_direction={"pace": "neutral"})]
    _build(
        tmp_path,
        segments,
        client=client,
        payload_extra={"voice_direction_defaults": {"stability": ""}},
    )
    sent = client.calls[0].settings["stability"]
    assert sent != ""  # the blank string never reached the API (M1)
    assert sent == 0.5  # fell through to the tier-5 style_guide default
    assert isinstance(sent, float)


# M2 — model_id receipt fidelity.
def test_m2_default_model_recorded_not_null(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    segments = [_segment("seg-01", "Default model.", voice_direction={"emotional_tone": "warm"})]
    receipt = _build(tmp_path, segments, client=client)["narration_receipts"][0]
    assert receipt["model_id"] == DEFAULT_MODEL
    assert receipt["effective_elevenlabs_settings"]["model_id"] == DEFAULT_MODEL
    assert client.calls[0].settings["model_id"] == DEFAULT_MODEL  # SENT matches recorded


def test_m2_explicit_model_override_preserved(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    segments = [
        _segment(
            "seg-01",
            "Explicit model.",
            voice_direction={"elevenlabs": {"model_id": "eleven_turbo_v2"}},
        )
    ]
    receipt = _build(tmp_path, segments, client=client)["narration_receipts"][0]
    assert receipt["model_id"] == "eleven_turbo_v2"


# S1 — pre-flight validation before ANY spend.
def test_s1_bad_segment3_bills_nothing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    segments = [
        _segment("seg-01", "First.", voice_direction={"emotional_tone": "neutral"}),
        _segment("seg-02", "Second.", voice_direction={"emotional_tone": "warm"}),
        _segment("seg-03", "Third bad.", voice_direction={"render_strategy": "dialogue"}),
    ]
    with pytest.raises(enrique_act.EnriqueActError) as exc:
        _build(tmp_path, segments, client=client)
    assert exc.value.tag == "elevenlabs.render-strategy.unsupported"
    # NOTHING billed — bad segment-3 caught in the pre-flight pass.
    assert client.calls == []
    assert not (tmp_path / "assembly-bundle" / "audio").exists()


# S2 — resume idempotency / skip-if-exists.
def test_s2_rerun_with_existing_segment_skips_api(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    direction = {"emotional_tone": "reflective", "pace": "slower", "energy": "low"}
    segments = [_segment("seg-01", "Already paid for.", voice_direction=direction)]

    first = FakeElevenLabsClient()
    _build(tmp_path, segments, client=first)
    assert len(first.calls) == 1

    second = FakeElevenLabsClient()
    result = _build(tmp_path, segments, client=second)
    assert second.calls == []  # no double-spend
    assert result["narration_outputs"][0]["duration_source"] == "reused"
    assert result["narration_outputs"][0]["cost_usd"] == 0.0
    assert len(result["narration_receipts"]) == 1


def test_s2_rerun_with_changed_settings_resynthesizes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    _build(
        tmp_path,
        [_segment("seg-01", "Same text.", voice_direction={"emotional_tone": "reflective"})],
        client=FakeElevenLabsClient(),
    )
    second = FakeElevenLabsClient()
    _build(
        tmp_path,
        [
            _segment(
                "seg-01",
                "Same text.",
                voice_direction={"emotional_tone": "urgent", "energy": "high"},
            )
        ],
        client=second,
    )
    assert len(second.calls) == 1  # changed settings -> re-synthesize


# S3 — null request_id proof integrity.
def test_s3_null_request_id_still_provable(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient(null_request_id=True)
    segments = [
        _segment("seg-01", "Billed but headerless.", voice_direction={"emotional_tone": "neutral"})
    ]
    receipt = _build(tmp_path, segments, client=client)["narration_receipts"][0]
    assert receipt["request_id"] is None
    assert receipt["request_id_present"] is False
    assert receipt["audio_sha256"] and len(receipt["audio_sha256"]) == 64
    audio = (tmp_path / "assembly-bundle" / "audio" / "seg-01.mp3").read_bytes()
    assert receipt["audio_sha256"] == hashlib.sha256(audio).hexdigest()


def test_s3_present_request_id_flag_true(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    segments = [_segment("seg-01", "Has id.", voice_direction={"emotional_tone": "neutral"})]
    receipt = _build(tmp_path, segments, client=client)["narration_receipts"][0]
    assert receipt["request_id_present"] is True
    assert receipt["request_id"]


# S4 — malformed style_guide.yaml taxonomy.
def test_s4_corrupt_style_guide_raises_tagged_error(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    bad = tmp_path / "style_guide.yaml"
    bad.write_text("tool_parameters: : : [unbalanced\n", encoding="utf-8")
    monkeypatch.setattr("app.specialists._shared.voice_direction_map._STYLE_GUIDE_PATH", bad)
    client = FakeElevenLabsClient()
    segments = [_segment("seg-01", "x", voice_direction={"emotional_tone": "neutral"})]
    with pytest.raises(enrique_act.EnriqueActError) as exc:
        _build(tmp_path / "b", segments, client=client)
    assert exc.value.tag == "elevenlabs.style-guide.malformed"
    assert client.calls == []  # failed before spend


# S6 — single-source voice_id / effective_voice_source agreement.
def test_s6_voice_id_and_source_agree_across_tiers(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    cases = [
        (
            {"elevenlabs": {"voice_id": "explicit-v"}},
            None,
            "explicit-v",
            "voice_direction.elevenlabs.voice_id",
        ),
        ({"emotional_tone": "warm"}, "seg-v", "seg-v", "segment voice_id"),
        ({"emotional_tone": "warm"}, None, "narrator", "voice-selection.json"),
    ]
    for i, (vd, seg_voice, exp_voice, exp_source) in enumerate(cases):
        client = FakeElevenLabsClient()
        seg = _segment("seg-01", "Agree.", voice_direction=vd)
        if seg_voice is not None:
            seg["voice_id"] = seg_voice
        receipt = _build(tmp_path / f"case{i}", [seg], client=client)["narration_receipts"][0]
        assert receipt["voice_id"] == exp_voice
        assert receipt["effective_voice_source"] == exp_source
        assert client.calls[0].voice_id == receipt["voice_id"]  # dispatched == recorded


# S7 — hoisted selected_voice_id guard (empty-segment payload, no KeyError).
def test_s7_empty_segment_payload_no_keyerror_flag_on(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    payload = {"bundle_path": str(tmp_path), "segments": []}
    result = enrique_act.build_assembly_bundle(payload, selection={}, client=client)  # type: ignore[arg-type]
    assert result["narration_outputs"] == []
    assert result["narration_receipts"] == []
    assert client.calls == []


def test_s7_empty_segment_payload_no_keyerror_flag_off(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(FLAG, raising=False)
    client = FakeElevenLabsClient()
    payload = {"bundle_path": str(tmp_path), "segments": [{"segment_id": "s", "text": ""}]}
    result = enrique_act.build_assembly_bundle(payload, selection={}, client=client)  # type: ignore[arg-type]
    assert result["narration_outputs"] == []
    assert "narration_receipts" not in result
    assert client.calls == []
