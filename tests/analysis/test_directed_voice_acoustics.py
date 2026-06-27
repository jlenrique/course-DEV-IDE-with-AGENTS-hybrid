"""RED-first tests for the P5 directed-voice acoustic harness + judge (Step 5).

Three layers, all deterministic + offline (no live API):

1. Analyzer on synthetic numpy-generated WAVs (known duration/amplitude/silence)
   -> proves :func:`analyze_clip` reports correct duration/rms/peak.
2. Judge unit tests -> a control floor + a treatment delta > 3F PASSES; a
   treatment delta < 3F FAILS (no false pass). k is fixed at 3.
3. Integration via the REAL ``build_assembly_bundle`` + the settings-sensitive
   ``FakeElevenLabsClient`` on 3 treatments -> the analyzer+judge detect the
   intended duration ordering (slower > faster), proving the WHOLE directed
   pipeline moves the targeted scalar deterministically, offline.
"""

from __future__ import annotations

import math
import wave
from pathlib import Path

import numpy as np
import pytest

from app.specialists.enrique import _act as enrique_act
from scripts.analysis.directed_voice_acoustics import (
    DEFAULT_K,
    analyze_clip,
    materially_different,
)
from tests.specialists.enrique._fake_elevenlabs import (
    FakeElevenLabsClient,
    parse_fake_audio,
)

_SR = 44100


def _write_tone_wav(
    path: Path, *, seconds: float, amplitude: float, freq: float = 440.0
) -> Path:
    """Write a mono 16-bit PCM sine tone of known duration + amplitude."""
    n = int(round(seconds * _SR))
    t = np.arange(n, dtype=np.float64) / _SR
    wave_data = amplitude * np.sin(2.0 * math.pi * freq * t)
    pcm = np.clip(wave_data * 32767.0, -32768, 32767).astype("<i2")
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(_SR)
        wf.writeframes(pcm.tobytes())
    return path


# --------------------------------------------------------------------------- #
# 1. Analyzer on synthetic WAVs.
# --------------------------------------------------------------------------- #
def test_analyzer_reports_correct_durations(tmp_path: Path) -> None:
    short = _write_tone_wav(tmp_path / "short.wav", seconds=1.0, amplitude=0.5)
    longer = _write_tone_wav(tmp_path / "long.wav", seconds=1.5, amplitude=0.5)
    a_short = analyze_clip(short)
    a_long = analyze_clip(longer)
    assert a_short.duration_s == pytest.approx(1.0, abs=0.02)
    assert a_long.duration_s == pytest.approx(1.5, abs=0.02)
    assert a_long.duration_s > a_short.duration_s


def test_analyzer_rms_orders_loud_above_quiet(tmp_path: Path) -> None:
    loud = _write_tone_wav(tmp_path / "loud.wav", seconds=1.0, amplitude=0.8)
    quiet = _write_tone_wav(tmp_path / "quiet.wav", seconds=1.0, amplitude=0.05)
    a_loud = analyze_clip(loud)
    a_quiet = analyze_clip(quiet)
    assert a_loud.rms > a_quiet.rms
    # A 0.8-amplitude sine has rms ~= 0.8/sqrt(2) ~= 0.566.
    assert a_loud.rms == pytest.approx(0.8 / math.sqrt(2), abs=0.02)
    assert a_loud.peak == pytest.approx(0.8, abs=0.02)


def test_analyzer_silence_is_near_zero_rms(tmp_path: Path) -> None:
    silence = _write_tone_wav(tmp_path / "silence.wav", seconds=1.0, amplitude=0.0)
    a = analyze_clip(silence)
    assert a.rms == pytest.approx(0.0, abs=1e-4)
    assert a.peak == pytest.approx(0.0, abs=1e-4)
    assert a.duration_s == pytest.approx(1.0, abs=0.02)


def test_analyzer_raises_on_missing_clip(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        analyze_clip(tmp_path / "nope.wav")


# --------------------------------------------------------------------------- #
# 2. The deterministic judge (k fixed at 3).
# --------------------------------------------------------------------------- #
def test_k_default_is_three() -> None:
    assert DEFAULT_K == 3


def test_judge_passes_when_delta_exceeds_three_floor() -> None:
    # control floor F = |10.00 - 10.05| = 0.05; threshold = 3F = 0.15.
    control = ({"duration_s": 10.00}, {"duration_s": 10.05})
    # treatment delta = |9.0 - 12.0| = 3.0 >> 0.15 -> PASS.
    treatment = ({"duration_s": 12.0}, {"duration_s": 9.0})
    v = materially_different(control, treatment, "duration_s")
    assert v.floor == pytest.approx(0.05)
    assert v.threshold == pytest.approx(0.15)
    assert v.delta == pytest.approx(3.0)
    assert v.passed is True


def test_judge_fails_when_delta_below_three_floor_no_false_pass() -> None:
    # control floor F = 0.20; threshold = 3F = 0.60.
    control = ({"rms": 0.40}, {"rms": 0.60})
    # treatment delta = |0.50 - 0.55| = 0.05 < 0.60 -> FAIL (no false pass).
    treatment = ({"rms": 0.50}, {"rms": 0.55})
    v = materially_different(control, treatment, "rms")
    assert v.threshold == pytest.approx(0.60)
    assert v.delta == pytest.approx(0.05)
    assert v.passed is False


def test_judge_is_pure_and_deterministic() -> None:
    control = ({"duration_s": 1.0}, {"duration_s": 1.0})
    treatment = ({"duration_s": 2.0}, {"duration_s": 3.0})
    v1 = materially_different(control, treatment, "duration_s")
    v2 = materially_different(control, treatment, "duration_s")
    assert v1 == v2


def test_judge_accepts_clip_analysis_attribute_scalar(tmp_path: Path) -> None:
    a = _write_tone_wav(tmp_path / "a.wav", seconds=1.00, amplitude=0.5)
    a2 = _write_tone_wav(tmp_path / "a2.wav", seconds=1.01, amplitude=0.5)
    t_slow = _write_tone_wav(tmp_path / "slow.wav", seconds=1.6, amplitude=0.5)
    t_fast = _write_tone_wav(tmp_path / "fast.wav", seconds=1.0, amplitude=0.5)
    v = materially_different(
        (analyze_clip(a), analyze_clip(a2)),
        (analyze_clip(t_slow), analyze_clip(t_fast)),
        "duration_s",
    )
    # tiny control floor; ~0.6 s treatment delta -> PASS.
    assert v.passed is True
    assert v.delta > 3 * v.floor


# --------------------------------------------------------------------------- #
# 3. Integration: REAL build_assembly_bundle + settings-sensitive fake.
#    Proves the whole directed pipeline moves the targeted scalar (duration)
#    deterministically, offline. The fake's parseable `dur` field IS the scalar.
# --------------------------------------------------------------------------- #
_FLAG = "MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE"
_SELECTION = {"selected_voice_id": "narrator"}
# Same text for every treatment so ONLY the direction moves the scalar.
_TEXT = "The same exact words are spoken in every one of these treatments."


def _fake_dur(bundle: Path, sid: str) -> float:
    audio = (bundle / "assembly-bundle" / "audio" / f"{sid}.mp3").read_bytes()
    return float(parse_fake_audio(audio)["dur"])


def test_integration_directed_pipeline_moves_duration_ordering(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv(_FLAG, "1")
    client = FakeElevenLabsClient()
    segments = [
        # control pair: SAME text + SAME (neutral) direction twice -> floor.
        {"segment_id": "ctl-a", "text": _TEXT,
         "voice_direction": {"emotional_tone": "neutral", "pace": "neutral", "energy": "medium"}},
        {"segment_id": "ctl-b", "text": _TEXT,
         "voice_direction": {"emotional_tone": "neutral", "pace": "neutral", "energy": "medium"}},
        # 3 treatments (neutral / reflective-slower / urgent-faster).
        {"segment_id": "neutral", "text": _TEXT,
         "voice_direction": {"emotional_tone": "neutral", "pace": "neutral", "energy": "medium"}},
        {"segment_id": "reflective", "text": _TEXT,
         "voice_direction": {"emotional_tone": "reflective", "pace": "slower", "energy": "low"}},
        {"segment_id": "urgent", "text": _TEXT,
         "voice_direction": {"emotional_tone": "urgent", "pace": "faster", "energy": "high"}},
    ]
    enrique_act.build_assembly_bundle(
        {"bundle_path": str(tmp_path), "segments": segments},
        selection=_SELECTION,
        client=client,
    )

    dur_ctl_a = _fake_dur(tmp_path, "ctl-a")
    dur_ctl_b = _fake_dur(tmp_path, "ctl-b")
    dur_reflective = _fake_dur(tmp_path, "reflective")
    dur_urgent = _fake_dur(tmp_path, "urgent")

    # Intended ordering: slower (reflective) clip is LONGER than faster (urgent).
    assert dur_reflective > dur_urgent
    # Deterministic floor: identical inputs -> identical dur -> F == 0.
    verdict = materially_different(
        ({"dur": dur_ctl_a}, {"dur": dur_ctl_b}),
        ({"dur": dur_urgent}, {"dur": dur_reflective}),
        "dur",
    )
    assert verdict.floor == pytest.approx(0.0)
    assert verdict.delta > 0.0
    assert verdict.passed is True


def test_integration_dropped_direction_collapses_duration_delta(
    tmp_path: Path, monkeypatch
) -> None:
    """If direction were silently dropped, slower/faster would render identically
    -> the judge's treatment delta collapses to 0 and the proof FAILS RED."""
    monkeypatch.setenv(_FLAG, "1")
    client = FakeElevenLabsClient()
    # Two segments with NO direction (the 'dropped' counterfactual) -> identical
    # resolved speed -> identical fake dur -> delta 0.
    segments = [
        {"segment_id": "a", "text": _TEXT},
        {"segment_id": "b", "text": _TEXT},
    ]
    enrique_act.build_assembly_bundle(
        {"bundle_path": str(tmp_path), "segments": segments},
        selection=_SELECTION,
        client=client,
    )
    assert _fake_dur(tmp_path, "a") == _fake_dur(tmp_path, "b")
