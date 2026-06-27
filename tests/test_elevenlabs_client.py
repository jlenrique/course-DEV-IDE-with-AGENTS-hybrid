"""Unit tests for the expanded ElevenLabs client."""

from __future__ import annotations

import base64
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.api_clients.elevenlabs_client import ElevenLabsClient, TtsResult


class TestElevenLabsClientTimestamps:
    def test_text_to_speech_with_timestamps_decodes_audio(self) -> None:
        client = ElevenLabsClient(api_key="test-key")
        response = MagicMock()
        response.json.return_value = {
            "audio_base64": base64.b64encode(b"audio-bytes").decode("utf-8"),
            "alignment": {
                "characters": list("Hi"),
                "character_start_times_seconds": [0.0, 0.1],
                "character_end_times_seconds": [0.1, 0.2],
            },
        }
        response.headers = {"request-id": "req-123"}

        with patch.object(client, "post_raw", return_value=response) as mocked:
            result = client.text_to_speech_with_timestamps("Hi", "voice-1")

        mocked.assert_called_once()
        assert result["audio_bytes"] == b"audio-bytes"
        assert result["request_id"] == "req-123"
        assert result["alignment"]["characters"] == ["H", "i"]

    def test_text_to_speech_passes_continuity_fields(self) -> None:
        client = ElevenLabsClient(api_key="test-key")
        response = MagicMock()
        response.content = b"speech"

        with patch.object(client, "post_raw", return_value=response) as mocked:
            result = client.text_to_speech(
                "segment 2",
                "voice-2",
                previous_request_ids=["req-1"],
                next_request_ids=["req-3"],
                pronunciation_dictionary_locators=[
                    {
                        "pronunciation_dictionary_id": "dict-1",
                        "version_id": "ver-1",
                    }
                ],
            )

        assert result == b"speech"
        _, kwargs = mocked.call_args
        assert kwargs["json"]["previous_request_ids"] == ["req-1"]
        assert kwargs["json"]["next_request_ids"] == ["req-3"]
        assert kwargs["json"]["pronunciation_dictionary_locators"][0][
            "pronunciation_dictionary_id"
        ] == "dict-1"


class TestTextToSpeechRequestId:
    """P5 Step 4 / ENRIQUE-A2 — surface the provider request-id."""

    def test_with_request_id_surfaces_header(self) -> None:
        client = ElevenLabsClient(api_key="test-key")
        response = MagicMock()
        response.content = b"directed-audio"
        response.headers = {"request-id": "req-abc-789"}

        with patch.object(client, "post_raw", return_value=response):
            result = client.text_to_speech_with_request_id(
                "Reflective line.",
                "voice-1",
                stability=0.62,
                style=0.22,
                speed=0.94,
            )

        assert isinstance(result, TtsResult)
        assert result.audio == b"directed-audio"
        assert result.request_id == "req-abc-789"

    def test_with_request_id_omits_unset_settings(self) -> None:
        client = ElevenLabsClient(api_key="test-key")
        response = MagicMock()
        response.content = b"x"
        response.headers = {}

        with patch.object(client, "post_raw", return_value=response) as mocked:
            client.text_to_speech_with_request_id("Hi", "voice-1", stability=0.3)

        _, kwargs = mocked.call_args
        # Only the explicitly-passed setting is sent; defaults are NOT injected.
        assert kwargs["json"]["voice_settings"] == {"stability": 0.3}

    def test_legacy_text_to_speech_preserves_default_settings(self) -> None:
        """Backward-compat: bytes-only path keeps its historic 0.5/0.75/0.0."""
        client = ElevenLabsClient(api_key="test-key")
        response = MagicMock()
        response.content = b"legacy"
        response.headers = {"request-id": "ignored"}

        with patch.object(client, "post_raw", return_value=response) as mocked:
            audio = client.text_to_speech("Hello", "voice-9")

        assert audio == b"legacy"  # still returns bytes only
        _, kwargs = mocked.call_args
        assert kwargs["json"]["voice_settings"] == {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
        }


class TestPronunciationDictionaryHelpers:
    def test_create_pronunciation_dictionary_uses_multipart(self, tmp_path: Path) -> None:
        client = ElevenLabsClient(api_key="test-key")
        dictionary_file = tmp_path / "medical.pls"
        dictionary_file.write_text("<lexicon />", encoding="utf-8")

        with patch.object(client, "post", return_value={"id": "dict-123"}) as mocked:
            result = client.create_pronunciation_dictionary_from_file(
                "medical-terms",
                dictionary_file,
                description="Medical terms",
            )

        assert result["id"] == "dict-123"
        _, kwargs = mocked.call_args
        assert kwargs["data"]["name"] == "medical-terms"
        assert kwargs["data"]["description"] == "Medical terms"
        assert "file" in kwargs["files"]

    def test_get_pronunciation_dictionaries_returns_entries(self) -> None:
        client = ElevenLabsClient(api_key="test-key")
        payload = {
            "pronunciation_dictionaries": [
                {"id": "dict-1", "latest_version_id": "ver-1", "name": "medical"}
            ],
            "has_more": False,
        }
        with patch.object(
            client, "list_pronunciation_dictionaries", return_value=payload
        ):
            result = client.get_pronunciation_dictionaries()
        assert result == payload["pronunciation_dictionaries"]


class TestBinaryGenerationHelpers:
    def test_text_to_sound_effect_returns_bytes(self) -> None:
        client = ElevenLabsClient(api_key="test-key")
        response = MagicMock()
        response.content = b"sfx"

        with patch.object(client, "post_raw", return_value=response) as mocked:
            result = client.text_to_sound_effect("subtle whoosh", duration_seconds=1.2)

        assert result == b"sfx"
        _, kwargs = mocked.call_args
        assert kwargs["json"]["text"] == "subtle whoosh"
        assert kwargs["json"]["duration_seconds"] == 1.2

    def test_text_to_dialogue_returns_bytes(self) -> None:
        client = ElevenLabsClient(api_key="test-key")
        response = MagicMock()
        response.content = b"dialogue"
        inputs = [
            {"text": "Hello", "voice_id": "voice-a"},
            {"text": "Hi", "voice_id": "voice-b"},
        ]

        with patch.object(client, "post_raw", return_value=response) as mocked:
            result = client.text_to_dialogue(inputs)

        assert result == b"dialogue"
        _, kwargs = mocked.call_args
        assert kwargs["json"]["inputs"] == inputs

    def test_generate_music_returns_bytes(self) -> None:
        client = ElevenLabsClient(api_key="test-key")
        response = MagicMock()
        response.content = b"music"

        with patch.object(client, "post_raw", return_value=response) as mocked:
            result = client.generate_music(
                prompt="Reflective medical underscore",
                music_length_ms=8000,
                force_instrumental=True,
            )

        assert result == b"music"
        _, kwargs = mocked.call_args
        assert kwargs["json"]["prompt"] == "Reflective medical underscore"
        assert kwargs["json"]["force_instrumental"] is True


class TestFileOutputs:
    def test_text_to_speech_with_timestamps_file_writes_audio(
        self, tmp_path: Path
    ) -> None:
        client = ElevenLabsClient(api_key="test-key")
        payload = {
            "audio_bytes": b"audio",
            "alignment": {},
            "normalized_alignment": {},
        }

        with patch.object(
            client, "text_to_speech_with_timestamps", return_value=payload
        ):
            result = client.text_to_speech_with_timestamps_file(
                "hello", "voice-1", tmp_path / "clip.mp3"
            )

        assert (tmp_path / "clip.mp3").read_bytes() == b"audio"
        assert result["audio_path"].endswith("clip.mp3")

    def test_download_pronunciation_dictionary_version_writes_file(
        self, tmp_path: Path
    ) -> None:
        client = ElevenLabsClient(api_key="test-key")
        response = MagicMock()
        response.content = b"<lexicon />"

        with patch.object(client, "get_raw", return_value=response):
            output = client.download_pronunciation_dictionary_version(
                "dict-1", "ver-1", tmp_path / "medical.pls"
            )

        assert output.read_bytes() == b"<lexicon />"
