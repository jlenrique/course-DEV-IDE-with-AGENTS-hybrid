"""Wanda Class-C Wondercraft API act implementation."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from scripts.api_clients.wondercraft_client import WondercraftClient

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-wanda"
DEFAULT_BUNDLE_PATH = REPO_ROOT / "runs" / "wanda"


class WandaActError(RuntimeError):
    """Raised when Wanda cannot produce a valid audio-bed envelope."""

    def __init__(self, message: str, *, tag: str) -> None:
        super().__init__(message)
        self.tag = tag


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), default=str)


def _trail_entry(last_entry: ModelResolutionEntry, *, tag: str) -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level=last_entry.level,
        requested=last_entry.requested,
        resolved=last_entry.resolved,
        reason=tag,
        timestamp=datetime.now(UTC),
        cache_prefix_hash=last_entry.cache_prefix_hash,
    )


def decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise WandaActError(
            "wanda envelope cache_prefix is not JSON",
            tag="wondercraft.malformed",
        ) from exc
    if not isinstance(decoded, dict):
        raise WandaActError(
            "wanda envelope cache_prefix must decode to an object",
            tag="wondercraft.wrong-type",
        )
    return decoded


def _audio_track(payload: dict[str, Any]) -> dict[str, Any]:
    storyboard = payload.get("storyboard") if isinstance(payload.get("storyboard"), dict) else {}
    track = payload.get("audio_track") or storyboard.get("audio_track") or {}
    return dict(track) if isinstance(track, dict) else {}


def _narration_text(payload: dict[str, Any]) -> str:
    manifest = payload.get("narration_manifest")
    if not isinstance(manifest, dict):
        manifest = payload.get("pass_2_narration_manifest")
    segments = manifest.get("segments") if isinstance(manifest, dict) else None
    if isinstance(segments, list):
        parts = [
            str(row.get("text") or row.get("narration_text") or "")
            for row in segments
            if isinstance(row, dict)
        ]
        return " ".join(part.strip() for part in parts if part.strip())
    return str(
        payload.get("prompt")
        or payload.get("script")
        or "Create a concise course audio bed."
    )


def _safe_bed_id(raw: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", raw.strip()).strip("-").lower()
    return cleaned or "bed-01"


def _bed_specs(payload: dict[str, Any]) -> list[dict[str, Any]]:
    track = _audio_track(payload)
    raw = track.get("beds") or track.get("audio_beds") or payload.get("audio_beds")
    if isinstance(raw, list) and all(isinstance(item, dict) for item in raw):
        specs = [dict(item) for item in raw]
    else:
        mood = str(track.get("mood") or payload.get("mood") or "focused")
        genre = str(track.get("genre") or payload.get("genre") or "ambient")
        specs = [{"bed_id": f"bed-{mood}-{genre}", "mood": mood, "genre": genre}]
    for index, spec in enumerate(specs, start=1):
        spec["bed_id"] = _safe_bed_id(str(spec.get("bed_id") or f"bed-{index:02d}"))
        spec.setdefault("mood", "focused")
        spec.setdefault("genre", "ambient")
        spec.setdefault("duration_seconds", 30)
    return specs


def _call_generate_audio_bed(
    client: WondercraftClient, spec: dict[str, Any], prompt: str
) -> dict[str, Any]:
    generate_audio_bed = getattr(client, "generate_audio_bed", None)
    if callable(generate_audio_bed):
        return generate_audio_bed(
            title=str(spec.get("title") or "Storyboard Audio Bed"),
            prompt=prompt,
            mood=str(spec.get("mood")),
            genre=str(spec.get("genre")),
            duration_seconds=int(spec.get("duration_seconds") or 30),
        )
    created = client.create_scripted_podcast(
        title=str(spec.get("title") or "Storyboard Audio Bed"),
        script_segments=[
            {
                "text": prompt,
                "voice_id": str(spec.get("voice_id") or "voice_a_narrator"),
            }
        ],
    )
    job_id = created.get("id") or created.get("job_id") or created.get("podcast_id")
    if job_id and hasattr(client, "wait_for_job"):
        terminal = client.wait_for_job(str(job_id), poll_interval=0, max_attempts=1)
        return {**created, **terminal}
    return created


def _extension(result: dict[str, Any], default: str = "mp3") -> str:
    raw = str(result.get("format") or result.get("audio_format") or default).lower().lstrip(".")
    url = str(result.get("url") or result.get("audio_url") or "")
    if url.endswith(".wav"):
        return "wav"
    return "wav" if raw == "wav" else "mp3"


def _audio_bytes(result: dict[str, Any]) -> bytes:
    for key in ("audio_bytes", "content", "bytes"):
        value = result.get(key)
        if isinstance(value, bytes):
            return value
        if isinstance(value, str) and value:
            return value.encode("utf-8")
    marker = (
        result.get("url")
        or result.get("audio_url")
        or result.get("id")
        or "wondercraft-audio-bed"
    )
    return f"wondercraft-audio-bed:{marker}".encode()


def build_compositor_invocation(audio_beds: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "specialist_id": "compositor",
        "gate_id": "G3",
        "audio_bed_paths": [row["audio_path"] for row in audio_beds],
    }


def generate_audio_beds(
    payload: dict[str, Any], *, client: WondercraftClient | None = None
) -> dict[str, Any]:
    client = client or WondercraftClient()
    bundle_path = Path(str(payload.get("bundle_path") or DEFAULT_BUNDLE_PATH))
    beds_dir = bundle_path / "assembly-bundle" / "audio" / "beds"
    beds_dir.mkdir(parents=True, exist_ok=True)
    prompt = _narration_text(payload)
    audio_beds: list[dict[str, Any]] = []
    # S0 fail-loud sweep extension (party review 2026-06-12, seventh seam):
    # the former per-bed "legacy_probe" dispatch existed only to stamp MB's
    # unconditionally-mocked receipt into production bed rows — same disease
    # as kira's legacy_receipt. The real path is _call_generate_audio_bed.
    for spec in _bed_specs(payload):
        result = _call_generate_audio_bed(client, spec, prompt)
        target = beds_dir / f"{spec['bed_id']}.{_extension(result)}"
        target.write_bytes(_audio_bytes(result))
        audio_beds.append(
            {
                "bed_id": spec["bed_id"],
                "audio_path": str(target),
                "mood": str(spec.get("mood")),
                "genre": str(spec.get("genre")),
                "provider_id": str(result.get("id") or result.get("job_id") or spec["bed_id"]),
                "provider_url": str(result.get("url") or result.get("audio_url") or ""),
                "cost_usd": float(result.get("cost_usd") or 0.0),
            }
        )
    track = _audio_track(payload)
    track["beds"] = audio_beds
    return {
        "specialist_id": "wanda",
        "gate_id": "G2",
        "bundle_path": str(bundle_path),
        "storyboard_audio_track": track,
        "audio_beds": audio_beds,
        "compositor_invocation": build_compositor_invocation(audio_beds),
    }


def act(state: RunState, *, client: WondercraftClient | None = None) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("wanda act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    try:
        verdict = generate_audio_beds(decode_envelope_payload(state), client=client)
    except WandaActError as exc:
        state.model_resolution_trail.append(_trail_entry(last_entry, tag=exc.tag))
        raise
    verdict["model_id"] = last_entry.resolved
    entries_count = state.cache_state.entries_count if state.cache_state is not None else 0
    return {
        "model_resolution_trail": [
            *state.model_resolution_trail,
            _trail_entry(last_entry, tag="wondercraft.audio-bed.ok"),
        ],
        "cache_state": CacheState(
            cache_prefix=_json_dumps(verdict), entries_count=entries_count + 1
        ).model_dump(mode="json"),
    }


__all__ = [
    "DEFAULT_BUNDLE_PATH",
    "SANCTUM_DIR",
    "WandaActError",
    "act",
    "build_compositor_invocation",
    "decode_envelope_payload",
    "generate_audio_beds",
]
