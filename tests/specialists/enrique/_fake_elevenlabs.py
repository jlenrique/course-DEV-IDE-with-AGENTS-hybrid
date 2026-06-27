"""Deterministic, settings-SENSITIVE ElevenLabs test double (MUR-5 / ENRIQUE-A2).

This is the single injected seam used by the Enrique directed-voice unit tests.
It mirrors the REAL ``ElevenLabsClient`` synthesis surface
(``text_to_speech`` legacy bytes path + ``text_to_speech_with_request_id``
settings-bearing path + ``list_voices``) but emits **deterministic, parseable,
settings-sensitive** audio bytes so a dropped ``voice_direction`` fails RED:

- ``speed`` (pace) -> clip duration field,
- ``style`` + ``stability`` (energy) -> amplitude field,
- ``voice_id`` -> tone field.

Every request is recorded as ``FakeTtsCall`` and a synthetic, monotonically
distinct ``request_id`` is emitted per call. Explicit overrides flow verbatim.

GUARD (MUR-5 "non-substitutable for live legs"): :func:`assert_not_in_live_leg`
hard-fails if this double is ever wired where a REAL ElevenLabs call is required.
It is module-quarantined under ``_fake_*`` (not ``test_*``) so the live-API
import detector does not scan it, and it deliberately does NOT import the real
``elevenlabs_client`` module.
"""

from __future__ import annotations

from typing import Any, NamedTuple


class FakeTtsResult(NamedTuple):
    """Structurally compatible with ``elevenlabs_client.TtsResult``."""

    audio: bytes
    request_id: str | None


class FakeTtsCall(NamedTuple):
    """One recorded synthesis request."""

    text: str
    voice_id: str
    settings: dict[str, Any]
    request_id: str | None


_FAKE_GUARD_MARKER = "FAKE-ELEVENLABS-NON-SUBSTITUTABLE"


def _scaled(value: Any, *, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _voice_tone(voice_id: str) -> int:
    """Map a voice id to a deterministic integer 'tone' (so voice_id matters)."""
    return sum(ord(ch) for ch in voice_id) % 997


def render_fake_audio(
    text: str,
    voice_id: str,
    settings: dict[str, Any],
) -> bytes:
    """Settings-sensitive parseable bytes (NOT real mp3; for unit assertions).

    A change in pace/speed shifts ``dur``; a change in energy (style/stability)
    shifts ``amp``; a change in voice_id shifts ``tone``. Identical inputs ->
    identical bytes (deterministic).
    """
    speed = _scaled(settings.get("speed"), fallback=1.0)
    style = _scaled(settings.get("style"), fallback=0.0)
    stability = _scaled(settings.get("stability"), fallback=0.5)
    # Slower speed -> longer clip; lower stability + higher style -> louder.
    dur = round(max(0.1, len(text) / (14.0 * speed)), 4)
    amp = round(style + (1.0 - stability), 4)
    tone = _voice_tone(voice_id)
    model = str(settings.get("model_id") or "")
    sim = settings.get("similarity_boost")
    header = (
        f"{_FAKE_GUARD_MARKER}|voice={voice_id}|tone={tone}|speed={speed}"
        f"|stability={stability}|style={style}|similarity_boost={sim}"
        f"|model={model}|dur={dur}|amp={amp}|text={text}"
    )
    return header.encode("utf-8")


def parse_fake_audio(audio: bytes) -> dict[str, str]:
    """Parse :func:`render_fake_audio` bytes back into a field dict."""
    raw = audio.decode("utf-8")
    fields: dict[str, str] = {}
    parts = raw.split("|")
    if parts and parts[0] == _FAKE_GUARD_MARKER:
        parts = parts[1:]
    for part in parts:
        if "=" in part:
            key, _, value = part.partition("=")
            fields[key] = value
    return fields


class FakeElevenLabsClient:
    """Injected stand-in mirroring the real client's synthesis signature."""

    def __init__(
        self,
        *,
        voices: list[dict[str, Any]] | None = None,
        null_request_id: bool = False,
    ) -> None:
        self.calls: list[FakeTtsCall] = []
        self._voices = voices or [
            {"voice_id": "narrator", "name": "Narrator", "preview_url": "https://cdn.test/n.mp3"}
        ]
        self._counter = 0
        # S3: simulate a real billed call whose response carries NO request-id
        # header (so request_id is legitimately None and the audio_sha256 +
        # request_id_present fallback must still prove the spend).
        self._null_request_id = null_request_id

    # -- voice catalogue (parity with the real client) --
    def list_voices(self) -> list[dict[str, Any]]:
        return list(self._voices)

    # -- legacy bytes-only path (flag-OFF / backward compat) --
    def text_to_speech(self, text: str, voice_id: str, **kwargs: Any) -> bytes:
        return self._synthesize(text, voice_id, kwargs).audio

    # -- settings-bearing seam (directed path, surfaces request_id) --
    def text_to_speech_with_request_id(
        self, text: str, voice_id: str, **kwargs: Any
    ) -> FakeTtsResult:
        result = self._synthesize(text, voice_id, kwargs)
        return result

    def _synthesize(self, text: str, voice_id: str, kwargs: dict[str, Any]) -> FakeTtsResult:
        settings = {
            "model_id": kwargs.get("model_id"),
            "stability": kwargs.get("stability"),
            "similarity_boost": kwargs.get("similarity_boost"),
            "style": kwargs.get("style"),
            "speed": kwargs.get("speed"),
        }
        self._counter += 1
        request_id = (
            None
            if self._null_request_id
            else f"fake-req-{self._counter:04d}-{_voice_tone(voice_id):03d}"
        )
        audio = render_fake_audio(text, voice_id, settings)
        self.calls.append(
            FakeTtsCall(text=text, voice_id=voice_id, settings=settings, request_id=request_id)
        )
        return FakeTtsResult(audio=audio, request_id=request_id)


def assert_not_in_live_leg(client: Any) -> None:
    """Guard: a live leg must NEVER be satisfied by this double (MUR-5)."""
    if isinstance(client, FakeElevenLabsClient):
        raise AssertionError(
            "FakeElevenLabsClient is non-substitutable for a live ElevenLabs leg "
            "(MUR-5); a real ElevenLabsClient is required for live proof."
        )
