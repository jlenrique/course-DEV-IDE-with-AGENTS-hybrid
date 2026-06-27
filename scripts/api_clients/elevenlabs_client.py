"""ElevenLabs API client for narration, timing, and audio generation.

API Docs: https://elevenlabs.io/docs/api-reference
Auth: xi-api-key header
Models: Eleven v3, Multilingual v2, Flash v2.5, Turbo v2.5, Music v1
Output: MP3, WAV, PCM, Opus
"""

from __future__ import annotations

import base64
import logging
import os
from pathlib import Path
from typing import Any, NamedTuple

from scripts.api_clients.base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class TtsResult(NamedTuple):
    """Audio bytes plus the surfaced ElevenLabs ``request-id`` (ENRIQUE-A2).

    The bare :meth:`ElevenLabsClient.text_to_speech` returns audio bytes only
    and discards the response headers. Directed-voice receipts (P5 Step 4) must
    record the REAL ``request_id`` the provider returned, so the synthesis seam
    Enrique drives returns this structurally-tiny result instead. Any test
    double Enrique injects only needs to expose ``audio`` and ``request_id``.
    """

    audio: bytes
    request_id: str | None

ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"
DEFAULT_TTS_MODEL = "eleven_multilingual_v2"
DEFAULT_DIALOGUE_MODEL = "eleven_v3"
DEFAULT_SOUND_MODEL = "eleven_text_to_sound_v2"
DEFAULT_MUSIC_MODEL = "music_v1"


class ElevenLabsClient(BaseAPIClient):
    """Client for ElevenLabs voice synthesis API.

    Args:
        api_key: ElevenLabs API key. Defaults to ``ELEVENLABS_API_KEY`` env var.
    """

    def __init__(self, api_key: str | None = None) -> None:
        api_key = api_key or os.environ.get("ELEVENLABS_API_KEY", "")
        super().__init__(
            base_url=ELEVENLABS_BASE_URL,
            auth_header="xi-api-key",
            auth_prefix="",
            api_key=api_key,
        )

    def list_voices(self) -> list[dict[str, Any]]:
        """List all available voices."""
        data = self.get("/voices")
        return data.get("voices", [])

    def get_voice(self, voice_id: str) -> dict[str, Any]:
        """Get details for a specific voice."""
        return self.get(f"/voices/{voice_id}")

    def list_models(self) -> list[dict[str, Any]]:
        """List available TTS models."""
        data = self.get("/models")
        return data if isinstance(data, list) else []

    def get_user(self) -> dict[str, Any]:
        """Get current user info including subscription details."""
        return self.get("/user")

    @staticmethod
    def _clean_payload(payload: dict[str, Any]) -> dict[str, Any]:
        """Remove null and empty values from request payloads."""
        return {
            key: value
            for key, value in payload.items()
            if value is not None and value != []
        }

    @staticmethod
    def _extract_request_id(response: Any) -> str | None:
        """Read the request identifier if the API returns one in headers."""
        headers = getattr(response, "headers", {}) or {}
        for key in ("request-id", "x-request-id", "request_id"):
            if headers.get(key):
                return headers[key]
        return None

    def _build_voice_settings(
        self,
        *,
        stability: float | None = None,
        similarity_boost: float | None = None,
        style: float | None = None,
        speed: float | None = None,
        use_speaker_boost: bool | None = None,
    ) -> dict[str, Any] | None:
        """Build request-scoped voice settings when values are provided."""
        settings = self._clean_payload(
            {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "speed": speed,
                "use_speaker_boost": use_speaker_boost,
            }
        )
        return settings or None

    def text_to_speech(
        self,
        text: str,
        voice_id: str,
        *,
        model_id: str = DEFAULT_TTS_MODEL,
        stability: float | None = 0.5,
        similarity_boost: float | None = 0.75,
        style: float | None = 0.0,
        speed: float | None = None,
        use_speaker_boost: bool | None = None,
        output_format: str = "mp3_44100_128",
        language_code: str | None = None,
        pronunciation_dictionary_locators: list[dict[str, str]] | None = None,
        seed: int | None = None,
        previous_text: str | None = None,
        next_text: str | None = None,
        previous_request_ids: list[str] | None = None,
        next_request_ids: list[str] | None = None,
        use_pvc_as_ivc: bool | None = None,
        apply_text_normalization: str | None = None,
        apply_language_text_normalization: bool | None = None,
    ) -> bytes:
        """Generate speech audio from text.

        Args:
            text: Text to convert to speech.
            voice_id: Voice ID from ``list_voices()``.
            model_id: TTS model to use.
            stability: Voice stability (0.0-1.0).
            similarity_boost: Voice clarity/similarity (0.0-1.0).
            style: Style exaggeration (0.0-1.0).
            speed: Playback speed multiplier (0.7-1.2).
            use_speaker_boost: Subtle speaker similarity boost when supported.
            output_format: Audio format string.
            language_code: Optional ISO-639-1 language code override.
            pronunciation_dictionary_locators: Optional dictionary ids/version ids.
            seed: Deterministic best-effort seed.
            previous_text: Text context preceding this generation.
            next_text: Text context following this generation.
            previous_request_ids: Prior request ids for continuity stitching.
            next_request_ids: Future request ids for continuity stitching.
            use_pvc_as_ivc: PVC/IVC compatibility switch.
            apply_text_normalization: ``auto``, ``on``, or ``off``.
            apply_language_text_normalization: Language-specific normalization.

        Returns:
            Raw audio bytes in the requested format.
        """
        return self.text_to_speech_with_request_id(
            text,
            voice_id,
            model_id=model_id,
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            speed=speed,
            use_speaker_boost=use_speaker_boost,
            output_format=output_format,
            language_code=language_code,
            pronunciation_dictionary_locators=pronunciation_dictionary_locators,
            seed=seed,
            previous_text=previous_text,
            next_text=next_text,
            previous_request_ids=previous_request_ids,
            next_request_ids=next_request_ids,
            use_pvc_as_ivc=use_pvc_as_ivc,
            apply_text_normalization=apply_text_normalization,
            apply_language_text_normalization=apply_language_text_normalization,
        ).audio

    def text_to_speech_with_request_id(
        self,
        text: str,
        voice_id: str,
        *,
        model_id: str = DEFAULT_TTS_MODEL,
        stability: float | None = None,
        similarity_boost: float | None = None,
        style: float | None = None,
        speed: float | None = None,
        use_speaker_boost: bool | None = None,
        output_format: str = "mp3_44100_128",
        language_code: str | None = None,
        pronunciation_dictionary_locators: list[dict[str, str]] | None = None,
        seed: int | None = None,
        previous_text: str | None = None,
        next_text: str | None = None,
        previous_request_ids: list[str] | None = None,
        next_request_ids: list[str] | None = None,
        use_pvc_as_ivc: bool | None = None,
        apply_text_normalization: str | None = None,
        apply_language_text_normalization: bool | None = None,
    ) -> TtsResult:
        """Generate speech and surface the provider ``request-id`` (ENRIQUE-A2).

        This is the settings-bearing synthesis seam the directed-voice path
        (P5 Step 4) drives so receipts can record the REAL request id. The
        settings default to ``None`` (omitted via ``_clean_payload``) rather
        than to the legacy ``text_to_speech`` defaults, so the per-segment
        resolved settings flow through verbatim. Existing ``text_to_speech``
        callers keep their old defaults by passing them explicitly.
        """
        payload = self._clean_payload(
            {
                "text": text,
                "model_id": model_id,
                "language_code": language_code,
                "voice_settings": self._build_voice_settings(
                    stability=stability,
                    similarity_boost=similarity_boost,
                    style=style,
                    speed=speed,
                    use_speaker_boost=use_speaker_boost,
                ),
                "pronunciation_dictionary_locators": pronunciation_dictionary_locators,
                "seed": seed,
                "previous_text": previous_text,
                "next_text": next_text,
                "previous_request_ids": previous_request_ids,
                "next_request_ids": next_request_ids,
                "use_pvc_as_ivc": use_pvc_as_ivc,
                "apply_text_normalization": apply_text_normalization,
                "apply_language_text_normalization": (
                    apply_language_text_normalization
                ),
            }
        )
        response = self.post_raw(
            f"/text-to-speech/{voice_id}",
            json=payload,
            params={"output_format": output_format},
        )
        return TtsResult(
            audio=response.content,
            request_id=self._extract_request_id(response),
        )

    def text_to_speech_with_timestamps(
        self,
        text: str,
        voice_id: str,
        *,
        model_id: str = DEFAULT_TTS_MODEL,
        stability: float | None = 0.5,
        similarity_boost: float | None = 0.75,
        style: float | None = 0.0,
        speed: float | None = None,
        use_speaker_boost: bool | None = None,
        output_format: str = "mp3_44100_128",
        language_code: str | None = None,
        pronunciation_dictionary_locators: list[dict[str, str]] | None = None,
        seed: int | None = None,
        previous_text: str | None = None,
        next_text: str | None = None,
        previous_request_ids: list[str] | None = None,
        next_request_ids: list[str] | None = None,
        use_pvc_as_ivc: bool | None = None,
        apply_text_normalization: str | None = None,
        apply_language_text_normalization: bool | None = None,
    ) -> dict[str, Any]:
        """Generate speech plus character-level timing metadata."""
        payload = self._clean_payload(
            {
                "text": text,
                "model_id": model_id,
                "language_code": language_code,
                "voice_settings": self._build_voice_settings(
                    stability=stability,
                    similarity_boost=similarity_boost,
                    style=style,
                    speed=speed,
                    use_speaker_boost=use_speaker_boost,
                ),
                "pronunciation_dictionary_locators": pronunciation_dictionary_locators,
                "seed": seed,
                "previous_text": previous_text,
                "next_text": next_text,
                "previous_request_ids": previous_request_ids,
                "next_request_ids": next_request_ids,
                "use_pvc_as_ivc": use_pvc_as_ivc,
                "apply_text_normalization": apply_text_normalization,
                "apply_language_text_normalization": (
                    apply_language_text_normalization
                ),
            }
        )
        response = self.post_raw(
            f"/text-to-speech/{voice_id}/with-timestamps",
            json=payload,
            params={"output_format": output_format},
        )
        data = response.json()
        audio_base64 = data.get("audio_base64", "")
        data["audio_bytes"] = base64.b64decode(audio_base64) if audio_base64 else b""
        data["request_id"] = self._extract_request_id(response)
        data["output_format"] = output_format
        return data

    def text_to_speech_file(
        self,
        text: str,
        voice_id: str,
        output_path: str | Path,
        **kwargs: Any,
    ) -> Path:
        """Generate speech and save to a file.

        Args:
            text: Text to convert.
            voice_id: Voice ID.
            output_path: File path to write audio.
            **kwargs: Additional args passed to ``text_to_speech()``.

        Returns:
            Path to the written audio file.
        """
        audio = self.text_to_speech(text, voice_id, **kwargs)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(audio)
        logger.info(
            "Audio saved: %s (%d bytes)", output_path, len(audio)
        )
        return output_path

    def text_to_speech_with_timestamps_file(
        self,
        text: str,
        voice_id: str,
        output_path: str | Path,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate timestamped speech and save the audio file.

        Returns the parsed timestamp payload augmented with ``audio_path``.
        """
        result = self.text_to_speech_with_timestamps(text, voice_id, **kwargs)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(result["audio_bytes"])
        result["audio_path"] = str(output_path)
        logger.info(
            "Timestamped audio saved: %s (%d bytes)",
            output_path,
            len(result["audio_bytes"]),
        )
        return result

    def create_pronunciation_dictionary_from_file(
        self,
        name: str,
        file_path: str | Path,
        *,
        description: str | None = None,
        workspace_access: str | None = None,
    ) -> dict[str, Any]:
        """Create a pronunciation dictionary from a `.pls` file."""
        file_path = Path(file_path)
        with file_path.open("rb") as handle:
            return self.post(
                "/pronunciation-dictionaries/add-from-file",
                data=self._clean_payload(
                    {
                        "name": name,
                        "description": description,
                        "workspace_access": workspace_access,
                    }
                ),
                files={"file": (file_path.name, handle, "application/octet-stream")},
            )

    def list_pronunciation_dictionaries(
        self,
        *,
        cursor: str | None = None,
        page_size: int = 30,
        sort: str | None = None,
        sort_direction: str | None = None,
    ) -> dict[str, Any]:
        """List pronunciation dictionaries and pagination metadata."""
        return self.get(
            "/pronunciation-dictionaries",
            params=self._clean_payload(
                {
                    "cursor": cursor,
                    "page_size": page_size,
                    "sort": sort,
                    "sort_direction": sort_direction,
                }
            ),
        )

    def get_pronunciation_dictionaries(
        self,
        *,
        cursor: str | None = None,
        page_size: int = 30,
        sort: str | None = None,
        sort_direction: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return only pronunciation dictionary metadata entries."""
        data = self.list_pronunciation_dictionaries(
            cursor=cursor,
            page_size=page_size,
            sort=sort,
            sort_direction=sort_direction,
        )
        return data.get("pronunciation_dictionaries", [])

    def download_pronunciation_dictionary_version(
        self,
        dictionary_id: str,
        version_id: str,
        output_path: str | Path,
    ) -> Path:
        """Download a pronunciation dictionary version as a `.pls` file."""
        response = self.get_raw(
            f"/pronunciation-dictionaries/{dictionary_id}/{version_id}/download"
        )
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)
        return output_path

    def text_to_sound_effect(
        self,
        text: str,
        *,
        output_format: str = "mp3_44100_128",
        loop: bool = False,
        duration_seconds: float | None = None,
        prompt_influence: float | None = None,
        model_id: str = DEFAULT_SOUND_MODEL,
    ) -> bytes:
        """Generate a sound effect clip from text."""
        response = self.post_raw(
            "/sound-generation",
            json=self._clean_payload(
                {
                    "text": text,
                    "loop": loop,
                    "duration_seconds": duration_seconds,
                    "prompt_influence": prompt_influence,
                    "model_id": model_id,
                }
            ),
            params={"output_format": output_format},
        )
        return response.content

    def text_to_sound_effect_file(
        self,
        text: str,
        output_path: str | Path,
        **kwargs: Any,
    ) -> Path:
        """Generate a sound effect and save it to disk."""
        audio = self.text_to_sound_effect(text, **kwargs)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(audio)
        return output_path

    def text_to_dialogue(
        self,
        inputs: list[dict[str, str]],
        *,
        model_id: str = DEFAULT_DIALOGUE_MODEL,
        language_code: str | None = None,
        settings: dict[str, Any] | None = None,
        pronunciation_dictionary_locators: list[dict[str, str]] | None = None,
        seed: int | None = None,
        apply_text_normalization: str | None = None,
        output_format: str = "mp3_44100_128",
    ) -> bytes:
        """Generate multi-speaker dialogue audio."""
        response = self.post_raw(
            "/text-to-dialogue",
            json=self._clean_payload(
                {
                    "inputs": inputs,
                    "model_id": model_id,
                    "language_code": language_code,
                    "settings": settings,
                    "pronunciation_dictionary_locators": pronunciation_dictionary_locators,
                    "seed": seed,
                    "apply_text_normalization": apply_text_normalization,
                }
            ),
            params={"output_format": output_format},
        )
        return response.content

    def text_to_dialogue_file(
        self,
        inputs: list[dict[str, str]],
        output_path: str | Path,
        **kwargs: Any,
    ) -> Path:
        """Generate dialogue audio and save it to disk."""
        audio = self.text_to_dialogue(inputs, **kwargs)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(audio)
        return output_path

    def generate_music(
        self,
        *,
        prompt: str | None = None,
        composition_plan: dict[str, Any] | None = None,
        music_length_ms: int | None = None,
        model_id: str = DEFAULT_MUSIC_MODEL,
        seed: int | None = None,
        force_instrumental: bool = False,
        store_for_inpainting: bool = False,
        output_format: str = "mp3_44100_128",
    ) -> bytes:
        """Generate instrumental or prompt-driven music via the music stream API."""
        response = self.post_raw(
            "/music/stream",
            json=self._clean_payload(
                {
                    "prompt": prompt,
                    "composition_plan": composition_plan,
                    "music_length_ms": music_length_ms,
                    "model_id": model_id,
                    "seed": seed,
                    "force_instrumental": force_instrumental,
                    "store_for_inpainting": store_for_inpainting,
                }
            ),
            params={"output_format": output_format},
        )
        return response.content

    def generate_music_file(
        self,
        output_path: str | Path,
        **kwargs: Any,
    ) -> Path:
        """Generate music and save it to disk."""
        audio = self.generate_music(**kwargs)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(audio)
        return output_path
