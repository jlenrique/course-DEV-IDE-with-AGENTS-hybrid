"""Direct Wondercraft dispatch seam for Wanda capabilities."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from scripts.api_clients.wondercraft_client import WondercraftClient

CAPABILITY_CODES: frozenset[str] = frozenset({"EP", "DP", "AS", "MB", "CM", "AH"})


class WondercraftDispatchError(RuntimeError):  # noqa: N818
    """Raised when Wanda dispatch cannot execute the requested capability."""

    def __init__(self, message: str, *, tag: str) -> None:
        super().__init__(message)
        self.tag = tag


def _ep_podcast_episode_produce(
    *,
    client: WondercraftClient,
    payload: dict[str, Any],
) -> dict[str, Any]:
    title = str(payload.get("title") or "Lesson Podcast")
    prompt = payload.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise WondercraftDispatchError(
            "EP requires non-empty prompt",
            tag="wanda_audio.parsed.missing-key",
        )
    voice_id = payload.get("voice_id")
    return client.create_podcast(title=title, prompt=prompt, voice_id=voice_id)


def _dp_podcast_dialogue_produce(
    *,
    client: WondercraftClient,
    payload: dict[str, Any],
) -> dict[str, Any]:
    title = str(payload.get("title") or "Dialogue Podcast")
    script = payload.get("script")
    if not isinstance(script, str) or not script.strip():
        raise WondercraftDispatchError(
            "DP requires non-empty script",
            tag="wanda_audio.parsed.missing-key",
        )
    return client.create_conversation_podcast(title=title, script=script)


def _as_audio_summary_produce(
    *,
    client: WondercraftClient,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """AS — Audio Summary capability. Wraps a single-voice script as a one-segment
    Wondercraft scripted-podcast. ``voice_id`` is required per Wondercraft API
    contract (verified live 2026-04-27); the previous tolerance of missing
    voice_id silently produced a malformed payload that the API rejected with
    403 (filed as anti-pattern A16 instance + remediated in
    `5a-2-wondercraft-client-payload-shape-defect`).
    """
    title = str(payload.get("title") or "Audio Summary")
    script = payload.get("script")
    if not isinstance(script, str) or not script.strip():
        raise WondercraftDispatchError(
            "AS requires non-empty script",
            tag="wanda_audio.parsed.missing-key",
        )
    voice_id = payload.get("voice_id")
    if not isinstance(voice_id, str) or not voice_id.strip():
        raise WondercraftDispatchError(
            "AS requires non-empty voice_id (Wondercraft scripted-podcast endpoint requires per-segment voice_id)",
            tag="wanda_audio.parsed.missing-key",
        )
    # Use the new list-of-segments form (preferred); the legacy string form
    # is supported for backward-compat in WondercraftClient itself but the
    # canonical AS shape is a single-segment list.
    return client.create_scripted_podcast(
        title=title,
        script_segments=[{"text": script, "voice_id": voice_id}],
    )


def _mb_music_bed_apply(
    *,
    client: WondercraftClient,
    payload: dict[str, Any],
) -> dict[str, Any]:
    connectivity = client.check_connectivity()
    return {
        "status": "mocked",
        "capability": "MB",
        "music_profile": payload.get("music_profile", "neutral-bed"),
        "ducking": payload.get("ducking", "moderate"),
        "api_connectivity": connectivity,
    }


def _cm_chapter_markers_emit(
    *,
    client: WondercraftClient,
    payload: dict[str, Any],
) -> dict[str, Any]:
    del client
    chapter_titles = payload.get("chapter_titles")
    if not isinstance(chapter_titles, list) or not chapter_titles:
        raise WondercraftDispatchError(
            "CM requires non-empty chapter_titles list",
            tag="wanda_audio.parsed.missing-key",
        )
    markers = []
    for index, title in enumerate(chapter_titles):
        markers.append(
            {
                "index": index + 1,
                "timestamp": f"00:{index:02d}:00",
                "title": str(title),
            }
        )
    return {
        "status": "success",
        "capability": "CM",
        "chapter_markers": markers,
    }


def _ah_audio_assembly_handoff(
    *,
    client: WondercraftClient,
    payload: dict[str, Any],
) -> dict[str, Any]:
    del client
    return {
        "status": "success",
        "capability": "AH",
        "assembly_handoff": {
            "title": str(payload.get("title") or "Audio Assembly Handoff"),
            "descript_ready": True,
            "operator_notes": str(payload.get("operator_notes") or ""),
            "generated_at": datetime.now(UTC).isoformat(),
        },
    }


def dispatch_to_wondercraft(
    *,
    capability: str,
    operation_payload: dict[str, Any] | None = None,
    client: WondercraftClient | None = None,
) -> dict[str, Any]:
    """Dispatch Wanda capability requests to Wondercraft client helpers."""
    normalized_capability = str(capability).strip().upper()
    if normalized_capability not in CAPABILITY_CODES:
        raise WondercraftDispatchError(
            f"unsupported wanda capability: {normalized_capability!r}",
            tag="wanda_audio.parsed.missing-key",
        )
    payload = dict(operation_payload or {})
    client = client or WondercraftClient()
    routes = {
        "EP": _ep_podcast_episode_produce,
        "DP": _dp_podcast_dialogue_produce,
        "AS": _as_audio_summary_produce,
        "MB": _mb_music_bed_apply,
        "CM": _cm_chapter_markers_emit,
        "AH": _ah_audio_assembly_handoff,
    }

    try:
        receipt = routes[normalized_capability](client=client, payload=payload)
    except WondercraftDispatchError:
        raise
    except Exception as exc:
        raise WondercraftDispatchError(
            "wanda dispatch failed",
            tag="wanda_audio.parsed.dispatch-failed",
        ) from exc

    if not isinstance(receipt, dict):
        raise WondercraftDispatchError(
            "wanda dispatch result must be a mapping",
            tag="wanda_audio.parsed.wrong-type",
        )

    return {
        "capability": normalized_capability,
        "receipt": receipt,
    }


__all__ = [
    "CAPABILITY_CODES",
    "WondercraftDispatchError",
    "dispatch_to_wondercraft",
]
