from __future__ import annotations

from collections.abc import Callable

import pytest

pytestmark = [pytest.mark.live, pytest.mark.timeout(15)]


def test_elevenlabs_voices_smoke(
    env_value: Callable[..., str | dict[str, str]],
    timed_call: Callable,
) -> None:
    """One cheap voice-list call; proves auth reaches ElevenLabs."""

    env_value("ELEVENLABS_API_KEY")

    def _call() -> list[dict[str, object]]:
        from scripts.api_clients.elevenlabs_client import ElevenLabsClient

        return ElevenLabsClient().list_voices()

    voices, _elapsed = timed_call(_call)
    assert isinstance(voices, list)
    if voices:
        first = voices[0]
        assert isinstance(first, dict)
        assert first.get("voice_id") or first.get("name")
