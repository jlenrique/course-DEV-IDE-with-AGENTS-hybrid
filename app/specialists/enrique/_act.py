"""Enrique Class-C ElevenLabs API act implementation."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.runtime.economics import RUNS_ROOT
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.enrique.elevenlabs_dispatch import dispatch_to_elevenlabs
from app.specialists.narration_join import join_narration_segments, phantom_segment_ids
from scripts.api_clients.elevenlabs_client import ElevenLabsClient

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-enrique"
CONFIG_PATH = REPO_ROOT / "app" / "specialists" / "enrique" / "config.yaml"
DEFAULT_BUNDLE_PATH = REPO_ROOT / "runs" / "enrique-narration"


class EnriqueActError(SpecialistDispatchError):
    """Raised when Enrique cannot produce a valid narration envelope.

    Audio-arc taxonomy re-base (2026-06-12): Enrique is the REAL-spend
    node — a mid-batch TTS failure must error-pause recoverably, never
    crash away paid audio.
    """


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
        raise EnriqueActError(
            "enrique envelope cache_prefix is not JSON", tag="elevenlabs.malformed"
        ) from exc
    if not isinstance(decoded, dict):
        raise EnriqueActError(
            "enrique envelope cache_prefix must decode to an object", tag="elevenlabs.wrong-type"
        )
    return decoded


def _load_config(config_path: Path = CONFIG_PATH) -> dict[str, Any]:
    if not config_path.is_file():
        return {}
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json_dumps(data) + "\n", encoding="utf-8", newline="\n")


def _load_structured_file(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    raw = target.read_text(encoding="utf-8")
    data = json.loads(raw) if target.suffix.lower() == ".json" else yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise EnriqueActError(
            "locked package file must contain a mapping", tag="elevenlabs.locked-package.invalid"
        )
    return data


def _voice_id(voice: dict[str, Any], index: int) -> str:
    return str(voice.get("voice_id") or voice.get("id") or f"voice-{index:02d}")


def _voice_name(voice: dict[str, Any], voice_id: str) -> str:
    return str(voice.get("voice_name") or voice.get("name") or voice_id)


def _preview_url(voice: dict[str, Any]) -> str:
    return str(
        voice.get("sample_audio_url") or voice.get("preview_url") or voice.get("sample_url") or ""
    )


def _candidate_voice(voice: dict[str, Any], index: int, *, cost: float) -> dict[str, Any]:
    voice_id = _voice_id(voice, index)
    labels = voice.get("characteristics") or voice.get("labels") or {}
    return {
        "voice_id": voice_id,
        "voice_name": _voice_name(voice, voice_id),
        "sample_audio_url": _preview_url(voice),
        "characteristics": labels if isinstance(labels, dict) else {"labels": str(labels)},
        "eta_seconds": float(voice.get("eta_seconds", 30)),
        "cost_per_1k_chars": float(voice.get("cost_per_1k_chars", cost)),
    }


def build_voice_selection_contract(
    payload: dict[str, Any], *, client: ElevenLabsClient | None = None
) -> dict[str, Any]:
    client = client or ElevenLabsClient()
    config = _load_config()
    bundle_path = Path(str(payload.get("bundle_path") or DEFAULT_BUNDLE_PATH))
    selection_dir = bundle_path / "voice-selection"
    count = int(
        payload.get("voice_preview_candidate_count")
        or config.get("voice_preview_candidate_count")
        or 3
    )
    raw_voices = payload.get("candidate_voices")
    if not isinstance(raw_voices, list):
        raw_voices = client.list_voices()
    cost = float(config.get("default_cost_per_1k_chars_usd", 0.30))
    voices = [_candidate_voice(v, i, cost=cost) for i, v in enumerate(raw_voices[:count], start=1)]
    if not voices:
        raise EnriqueActError(
            "voice preview requires at least one candidate", tag="elevenlabs.voice-preview.empty"
        )
    preview = {"voices": voices, "recommended_voice_id": voices[0]["voice_id"]}
    _write_json(selection_dir / "voice-preview-options.json", preview)
    lines = ["# Voice Selection Review", ""]
    for voice in voices:
        marker = " [recommended]" if voice["voice_id"] == preview["recommended_voice_id"] else ""
        lines.append(
            f"- {voice['voice_id']} | {voice['voice_name']} | {voice['sample_audio_url']}{marker}"
        )
    (selection_dir / "voice-selection-review.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n"
    )
    selected = (
        payload.get("voice_selection") if isinstance(payload.get("voice_selection"), dict) else {}
    )
    selection = {
        "selected_voice_id": str(
            selected.get("selected_voice_id")
            or payload.get("selected_voice_id")
            or preview["recommended_voice_id"]
        ),
        "selected_at": str(
            selected.get("selected_at") or datetime.now(UTC).isoformat().replace("+00:00", "Z")
        ),
        "operator_id": str(
            selected.get("operator_id")
            or payload.get("operator_id")
            or "operator-defaulted-recommended"
        ),
        "rationale": str(
            selected.get("rationale")
            or payload.get("rationale")
            or "Defaulted to Enrique's recommended voice."
        ),
    }
    _write_json(selection_dir / "voice-selection.json", selection)
    return {"bundle_path": str(bundle_path), "voice_preview": preview, "voice_selection": selection}


def _segments(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(payload.get("segments"), list):
        raw = payload["segments"]
    elif payload.get("locked_manifest_path") or payload.get("manifest_path"):
        manifest = _load_structured_file(
            str(payload.get("locked_manifest_path") or payload["manifest_path"])
        )
        raw = manifest.get("segments") or manifest.get("narration_segments") or []
    elif payload.get("narration_script") or payload.get("segment_manifest_deltas"):
        # Audio-arc grounding (2026-06-12): node 12 projects Pass-2 narration
        # keys; the shared join (the SAME policy the published Storyboard B
        # used) produces the segments Enrique pays to synthesize. Pre-spend
        # guard (Amelia): a join that drops narration segments refuses
        # BEFORE the TTS loop — bad join must never become paid garbage.
        narration = payload.get("narration_script")
        deltas = payload.get("segment_manifest_deltas")
        if not narration or not deltas:
            raise EnriqueActError(
                "enrique grounding requires BOTH narration_script and "
                "segment_manifest_deltas projections",
                tag="elevenlabs.input.missing-narration",
            )
        raw = join_narration_segments(narration, deltas)
        joined_ids = {str(row.get("id") or "") for row in raw}
        dropped = sorted(
            str(seg.get("id") or "")
            for seg in narration
            if isinstance(seg, dict) and str(seg.get("id") or "") not in joined_ids
        )
        if not raw or dropped:
            raise EnriqueActError(
                f"narration join dropped segment(s) {dropped}; refusing "
                "pre-spend (paid audio must cover the approved narration)",
                tag="elevenlabs.join.dropped-segments",
            )
        # dp-v1.2 rider (Amelia R1): a delta with no matching narration
        # joins with empty text; the TTS loop would skip it silently while
        # G5 counted its slide as covered. Refuse BEFORE spend.
        phantom = phantom_segment_ids(raw)
        if phantom:
            raise EnriqueActError(
                f"narration join produced empty-text segment(s) {phantom}; "
                "refusing pre-spend (a phantom delta would skip TTS silently "
                "yet count toward G5 coverage)",
                tag="elevenlabs.join.empty-narration-text",
            )
    else:
        raw = []
    if not isinstance(raw, list) or not all(isinstance(item, dict) for item in raw):
        raise EnriqueActError(
            "locked manifest segments must be a list of objects", tag="elevenlabs.segments.invalid"
        )
    return raw


def _segment_text(segment: dict[str, Any]) -> str:
    return str(
        segment.get("narration_text") or segment.get("text") or segment.get("script") or ""
    ).strip()


def _segment_id(segment: dict[str, Any], index: int) -> str:
    return str(segment.get("segment_id") or segment.get("id") or f"segment-{index:02d}")


def _write_vtt(path: Path, text: str, duration: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    seconds = max(1, int(round(duration)))
    path.write_text(
        f"WEBVTT\n\n00:00:00.000 --> 00:00:{seconds:02d}.000\n{text}\n",
        encoding="utf-8",
        newline="\n",
    )


def build_assembly_bundle(
    payload: dict[str, Any], *, selection: dict[str, Any], client: ElevenLabsClient | None = None
) -> dict[str, Any]:
    client = client or ElevenLabsClient()
    bundle_path = Path(str(payload.get("bundle_path") or DEFAULT_BUNDLE_PATH))
    audio_dir = bundle_path / "assembly-bundle" / "audio"
    captions_dir = bundle_path / "assembly-bundle" / "captions"
    segments = _segments(payload)
    outputs: list[dict[str, Any]] = []
    cost_per_1k = float(
        payload.get("cost_per_1k_chars")
        or _load_config().get("default_cost_per_1k_chars_usd", 0.30)
    )
    for index, segment in enumerate(segments, start=1):
        sid = _segment_id(segment, index)
        text = _segment_text(segment)
        if not text:
            continue
        audio_path = audio_dir / f"{sid}.mp3"
        audio = client.text_to_speech(text, selection["selected_voice_id"])
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        audio_path.write_bytes(audio if isinstance(audio, bytes) else bytes(str(audio), "utf-8"))
        duration = float(segment.get("duration_seconds") or max(1.0, len(text) / 14.0))
        caption_path = captions_dir / f"{sid}.vtt"
        _write_vtt(caption_path, text, duration)
        cost = round((len(text) / 1000.0) * cost_per_1k, 4)
        progress = (
            f"Enrique segment {sid} [{index}/{len(segments)}] OK | "
            f"duration={duration:.1f}s | cost={cost:.4f}"
        )
        print(
            progress,
            file=sys.stderr,
            flush=True,
        )
        outputs.append(
            {
                "segment_id": sid,
                "slide_id": str(segment.get("slide_id") or ""),
                "audio_path": str(audio_path),
                "caption_path": str(caption_path),
                "duration_seconds": duration,
                # Winston (audio-arc + review MUST-FIX 2): "measured" is
                # RESERVED for a real mp3 probe (rider). Payload-supplied
                # durations are PLANNED numbers — labeling them measured
                # would arm G5's WPM raise against the plan itself.
                "duration_source": "provided"
                if segment.get("duration_seconds")
                else "estimated-chars",
                "cost_usd": cost,
            }
        )
    return {
        "bundle_path": str(bundle_path),
        "narration_outputs": outputs,
        "compositor_invocation": build_compositor_invocation(outputs),
    }


def build_compositor_invocation(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "specialist_id": "compositor",
        "gate_id": "G3",
        "audio_paths": [row["audio_path"] for row in outputs],
        "caption_paths": [row["caption_path"] for row in outputs],
    }


def generate_enrique_outputs(
    payload: dict[str, Any], *, client: ElevenLabsClient | None = None
) -> dict[str, Any]:
    contract = build_voice_selection_contract(payload, client=client)
    result = {"specialist_id": "enrique", "gate_id": "G2", **contract}
    if _segments(payload):
        result.update(
            build_assembly_bundle(payload, selection=contract["voice_selection"], client=client)
        )
    if payload.get("legacy_dispatch_probe"):
        result["legacy_dispatch_probe"] = dispatch_to_elevenlabs(
            mode="voice-preview", operation_payload={}
        )
    return result


def act(state: RunState, *, client: ElevenLabsClient | None = None) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("enrique act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    payload = decode_envelope_payload(state)
    if not payload.get("bundle_path"):
        # Audio-arc (Amelia): run-scoped bundle — a shared repo-root default
        # means cross-run mp3 contamination in the compositor's input.
        payload["bundle_path"] = str(RUNS_ROOT / str(state.run_id) / "enrique-narration")
    try:
        verdict = generate_enrique_outputs(payload, client=client)
    except EnriqueActError as exc:
        state.model_resolution_trail.append(_trail_entry(last_entry, tag=exc.tag))
        raise
    verdict["model_id"] = last_entry.resolved
    entries_count = state.cache_state.entries_count if state.cache_state is not None else 0
    return {
        "model_resolution_trail": [
            *state.model_resolution_trail,
            _trail_entry(last_entry, tag="elevenlabs.dispatch.ok"),
        ],
        "cache_state": CacheState(
            cache_prefix=_json_dumps(verdict), entries_count=entries_count + 1
        ).model_dump(mode="json"),
    }


from app.specialists.enrique.payload_contract import CONSUMED_PAYLOAD_KEYS  # noqa: E402

__all__ = [
    "CONFIG_PATH",
    "CONSUMED_PAYLOAD_KEYS",
    "EnriqueActError",
    "SANCTUM_DIR",
    "act",
    "build_assembly_bundle",
    "build_compositor_invocation",
    "build_voice_selection_contract",
    "decode_envelope_payload",
    "generate_enrique_outputs",
]
