"""Enrique Class-C ElevenLabs API act implementation."""

from __future__ import annotations

import hashlib
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
from app.specialists._shared.voice_direction_map import (
    SUPPORTED_RENDER_STRATEGIES,
    VoiceDirectionMapError,
    clean_default_tier,
    load_style_guide_tts_defaults,
    map_voice_direction_to_tts,
    normalize_optional_str,
    resolve_voice_id_with_source,
    voice_direction_active,
    voice_selection_default_tier,
)
from app.specialists._shared.voice_provider_text import (
    COMPILER_VERSION as PROVIDER_TEXT_COMPILER_VERSION,
)
from app.specialists._shared.voice_provider_text import (
    POPULATED_RHETORICAL_ROLES,
    VoiceProviderTextError,
    build_text_channels,
    compile_provider_text,
    extract_tags,
)
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.enrique.elevenlabs_dispatch import dispatch_to_elevenlabs
from app.specialists.irene.authoring.pass_2_template import VoiceDirection
from app.specialists.narration_join import join_narration_segments, phantom_segment_ids
from scripts.api_clients.elevenlabs_client import (
    DEFAULT_DIALOGUE_MODEL,
    DEFAULT_TTS_MODEL,
    ElevenLabsClient,
)

# Story enhanced-vo.2 (Slice 1): a FIXED seed graduated into the directed v3 call
# (AC-B10 test-hygiene) so a blind strip-vs-tag A/B differs by direction, not render
# noise. v2/non-v3 path is unchanged (no seed).
DIRECTED_V3_SEED = 73219

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-enrique"
CONFIG_PATH = REPO_ROOT / "app" / "specialists" / "enrique" / "config.yaml"


class EnriqueActError(SpecialistDispatchError):
    """Raised when Enrique cannot produce a valid narration envelope.

    Audio-arc taxonomy re-base (2026-06-12): Enrique is the REAL-spend
    node — a mid-batch TTS failure must error-pause recoverably, never
    crash away paid audio.
    """


def _require_bundle_path(payload: dict[str, Any]) -> Path:
    """dp-v1.2 rider (Winston R2): the repo-root DEFAULT_BUNDLE_PATH is
    retired — every write lands in a run-scoped bundle. act() injects the
    path on the production walk; a direct caller without one fails loud."""
    raw = str(payload.get("bundle_path") or "").strip()
    if not raw:
        raise EnriqueActError(
            "payload carries no bundle_path; refusing to write to an "
            "implicit default location",
            tag="elevenlabs.bundle.path-missing",
        )
    return Path(raw)


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


def _recommended_voice_id(voices: list[dict[str, Any]], config: dict[str, Any]) -> str:
    configured = normalize_optional_str(config.get("default_recommended_voice_id"))
    voice_ids = {str(voice.get("voice_id") or "") for voice in voices}
    if configured and configured in voice_ids:
        return configured
    return str(voices[0]["voice_id"])


def build_voice_selection_contract(
    payload: dict[str, Any], *, client: ElevenLabsClient | None = None
) -> dict[str, Any]:
    client_was_supplied = client is not None
    client = client or ElevenLabsClient()
    config = _load_config()
    bundle_path = _require_bundle_path(payload)
    selection_dir = bundle_path / "voice-selection"
    count = int(
        payload.get("voice_preview_candidate_count")
        or config.get("voice_preview_candidate_count")
        or 3
    )
    raw_voices = payload.get("candidate_voices")
    if not isinstance(raw_voices, list):
        configured_voices = config.get("default_candidate_voices")
        if not client_was_supplied and isinstance(configured_voices, list):
            raw_voices = configured_voices
        else:
            raw_voices = client.list_voices()
    cost = float(config.get("default_cost_per_1k_chars_usd", 0.30))
    voices = [_candidate_voice(v, i, cost=cost) for i, v in enumerate(raw_voices[:count], start=1)]
    if not voices:
        raise EnriqueActError(
            "voice preview requires at least one candidate", tag="elevenlabs.voice-preview.empty"
        )
    recommended_voice_id = (
        _recommended_voice_id(voices, config)
        if not client_was_supplied and not isinstance(payload.get("candidate_voices"), list)
        else str(voices[0]["voice_id"])
    )
    preview = {"voices": voices, "recommended_voice_id": recommended_voice_id}
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


# MP3 frame-duration parser (Arc 3, measured-durations 2026-06-18). Dep-free —
# no mutagen, no ffprobe subprocess (operator-CLI avoidance + shipped-deps
# rule). Sums per-frame durations from the MPEG audio frame headers, so it is
# correct for CBR and VBR alike. Returns None on anything that is not a valid
# MPEG-1/2/2.5 Layer III stream (e.g. test fixture bytes) so the caller falls
# back to the char-count estimate — folded/fixture behavior is unchanged.
_MP3_BITRATES = {
    1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0],  # MPEG1 L3
    2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0],  # MPEG2/2.5 L3
}
_MP3_SAMPLE_RATES = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}


def _mp3_duration_seconds(data: bytes) -> float | None:
    """Sum MPEG Layer III frame durations; None if not a parseable MP3."""
    i = 0
    n = len(data)
    if n >= 10 and data[:3] == b"ID3":  # skip ID3v2 tag (syncsafe size)
        tag = (data[6] & 0x7F) << 21 | (data[7] & 0x7F) << 14
        tag |= (data[8] & 0x7F) << 7 | (data[9] & 0x7F)
        i = 10 + tag
    total = 0.0
    frames = 0
    while i + 4 <= n:
        if data[i] != 0xFF or (data[i + 1] & 0xE0) != 0xE0:
            i += 1
            continue
        ver_bits = (data[i + 1] >> 3) & 0x03  # 3=MPEG1, 2=MPEG2, 0=MPEG2.5
        layer_bits = (data[i + 1] >> 1) & 0x03  # 1=Layer III
        if layer_bits != 1 or ver_bits == 1:
            i += 1
            continue
        br_idx = (data[i + 2] >> 4) & 0x0F
        sr_idx = (data[i + 2] >> 2) & 0x03
        padding = (data[i + 2] >> 1) & 0x01
        if br_idx in (0, 15) or sr_idx == 3 or ver_bits not in _MP3_SAMPLE_RATES:
            i += 1
            continue
        bitrate = _MP3_BITRATES[1 if ver_bits == 3 else 2][br_idx] * 1000
        sample_rate = _MP3_SAMPLE_RATES[ver_bits][sr_idx]
        samples = 1152 if ver_bits == 3 else 576
        frame_len = int((samples // 8 * bitrate) // sample_rate) + padding
        if frame_len <= 4:
            i += 1
            continue
        total += samples / sample_rate
        frames += 1
        i += frame_len
    return round(total, 3) if frames else None


def _write_vtt(path: Path, text: str, duration: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    seconds = max(1, int(round(duration)))
    path.write_text(
        f"WEBVTT\n\n00:00:00.000 --> 00:00:{seconds:02d}.000\n{text}\n",
        encoding="utf-8",
        newline="\n",
    )


# Settings keys the resolved TTS dict carries (mirrors the shared mapper output).
_TTS_SETTING_KEYS = ("model_id", "stability", "similarity_boost", "style", "speed")


class _DirectedPlan:
    """A fully-resolved-and-validated directed segment, computed in the PRE-FLIGHT
    pass BEFORE any synthesis call (S1) so a bad segment N never bills 1..N-1."""

    __slots__ = (
        "index",
        "sid",
        "segment",
        "text",
        "direction",
        "resolved",
        "voice_id",
        "effective_voice_source",
        "effective_model",
        "effective_settings",
        # Story enhanced-vo.2 (Slice 1): v3 provider-text channels (pre-flight,
        # offline). render_mode is "v3_provider_text" iff the compiler actually
        # ran (effective model == eleven_v3 AND a POPULATED rhetorical_role);
        # otherwise "v2_settings" and the provider channel == canonical (sent text
        # unchanged, receipt byte-identical to today — AC-B12).
        "render_mode",
        "rhetorical_role",
        "channels",
        "sent_text",
    )

    def __init__(
        self,
        *,
        index: int,
        sid: str,
        segment: dict[str, Any],
        text: str,
        direction: VoiceDirection | None,
        resolved: dict[str, Any],
        voice_id: str,
        effective_voice_source: str,
        effective_model: str,
        render_mode: str,
        rhetorical_role: str | None,
        channels: dict[str, str] | None,
        sent_text: str,
    ) -> None:
        self.index = index
        self.sid = sid
        self.segment = segment
        self.text = text
        self.direction = direction
        self.resolved = resolved
        self.voice_id = voice_id
        self.effective_voice_source = effective_voice_source
        self.effective_model = effective_model
        self.render_mode = render_mode
        self.rhetorical_role = rhetorical_role
        self.channels = channels
        self.sent_text = sent_text
        # effective_elevenlabs_settings records the EFFECTIVE model actually used
        # (M2): resolved model_id is None when no tier supplies one, but the real
        # call/receipt must show the concrete default the client applies.
        self.effective_settings = {
            "voice_id": voice_id,
            "model_id": effective_model,
            "stability": resolved.get("stability"),
            "similarity_boost": resolved.get("similarity_boost"),
            "style": resolved.get("style"),
            "speed": resolved.get("speed"),
        }


def _resolve_directed_plan(
    index: int,
    segment: dict[str, Any],
    text: str,
    *,
    pass2_defaults: dict[str, Any],
    voice_selection_default: dict[str, Any],
    style_guide_defaults: dict[str, Any],
) -> _DirectedPlan:
    """Validate + resolve ONE directed segment (PRE-FLIGHT; no synthesis here).

    FAILS LOUD (tagged, recoverable) on a non-mapping / contract-invalid direction
    (`elevenlabs.voice-direction.invalid`), an unsupported ``render_strategy``
    (`elevenlabs.render-strategy.unsupported` — Card 3), or an unresolvable
    voice_id (`elevenlabs.voice-id.unresolved`). The empty-string ``voice_id`` is
    normalized at this call site (empty-voice-id guard). The voice_id AND its
    provenance label come from the SAME shared resolver (S6) so they cannot
    diverge from ``resolved["voice_id"]``.
    """
    from pydantic import ValidationError

    sid = _segment_id(segment, index)
    segment_voice_id = normalize_optional_str(segment.get("voice_id"))
    raw_direction = segment.get("voice_direction")
    direction: VoiceDirection | None
    if raw_direction is None:
        direction = None
        mapper_input = VoiceDirection()
    else:
        if not isinstance(raw_direction, dict):
            raise EnriqueActError(
                f"segment {sid} voice_direction must be a mapping",
                tag="elevenlabs.voice-direction.invalid",
            )
        try:
            direction = VoiceDirection.model_validate(raw_direction)
        except ValidationError as exc:
            raise EnriqueActError(
                f"segment {sid} voice_direction failed contract validation: {exc}",
                tag="elevenlabs.voice-direction.invalid",
            ) from exc
        if direction.render_strategy not in SUPPORTED_RENDER_STRATEGIES:
            # `dialogue` is modeled-not-consumed in v1; consuming it as
            # single-voice TTS would be silently-wrong output.
            raise EnriqueActError(
                f"segment {sid} unsupported render_strategy "
                f"{direction.render_strategy!r} (supported: "
                f"{sorted(SUPPORTED_RENDER_STRATEGIES)}); refusing to silently "
                "render single-voice",
                tag="elevenlabs.render-strategy.unsupported",
            )
        mapper_input = direction

    resolved = map_voice_direction_to_tts(
        mapper_input,
        segment_voice_id=segment_voice_id,
        pass2_voice_direction_defaults=pass2_defaults,
        voice_selection_default=voice_selection_default,
        style_guide_defaults=style_guide_defaults,
    )
    # Single-source voice_id + provenance (S6): same walk that produced
    # resolved["voice_id"], so they can never disagree.
    voice_id_raw, effective_voice_source = resolve_voice_id_with_source(
        mapper_input,
        segment_voice_id=segment_voice_id,
        pass2_voice_direction_defaults=pass2_defaults,
        voice_selection_default=voice_selection_default,
        style_guide_defaults=style_guide_defaults,
    )
    voice_id = normalize_optional_str(voice_id_raw)
    if voice_id is None:
        raise EnriqueActError(
            f"segment {sid} resolved no voice_id across all 5 precedence tiers; "
            "refusing to dispatch an empty voice",
            tag="elevenlabs.voice-id.unresolved",
        )
    # M2: the EFFECTIVE model is the resolved one, or the client default the call
    # will actually apply when no tier supplies model_id.
    effective_model = normalize_optional_str(resolved.get("model_id")) or DEFAULT_TTS_MODEL

    # Story enhanced-vo.2 (Slice 1): MODEL-AWARE v3 branch (AC-B4). DESIGN DECISION:
    # branch on the EFFECTIVE MODEL (== eleven_v3), NOT on render_strategy. The
    # frozen `render_strategy: Literal["tts","dialogue"]` is the synthesis MODE, a
    # different axis from the MODEL; overloading it with "v3" would conflate the two
    # and break the existing fail-loud on unsupported render_strategy. The v2 numeric
    # mapper stays FROZEN; this is its sibling. The compiler runs ONLY when the model
    # is eleven_v3 AND the segment carries a POPULATED rhetorical_role; otherwise the
    # provider channel == canonical and the sent text / receipt are byte-identical to
    # today (AC-B12). The compile is pure/offline, so it belongs in PRE-FLIGHT (S1):
    # a tag/firewall failure refuses BEFORE any segment bills.
    rhetorical_role = getattr(direction, "rhetorical_role", None) if direction is not None else None
    is_v3 = effective_model == DEFAULT_DIALOGUE_MODEL
    channels: dict[str, str] | None = None
    if is_v3 and rhetorical_role is not None:
        # S1 fail-loud: a v3 segment whose rhetorical_role the compiler does NOT
        # populate must REFUSE, never silently downgrade to neutral v2 (a dropped
        # delivery the operator never sees). Pre-flight, so nothing bills.
        if rhetorical_role not in POPULATED_RHETORICAL_ROLES:
            raise EnriqueActError(
                f"segment {sid} rhetorical_role {rhetorical_role!r} is not populated by "
                f"the v3 compiler (populated: {sorted(POPULATED_RHETORICAL_ROLES)}); "
                "refusing to silently render neutral v2",
                tag="elevenlabs.v3.role.unpopulated",
            )
        # M1: channel construction + the captions tag-leak gate are a v3-ONLY concern.
        # On the v2/non-v3 path NO channels are built, so a canonical that legitimately
        # contains brackets ([1]/[Figure 2]/[CO2]/[Na+]) synthesizes BYTE-IDENTICAL to
        # today (AC-B12) — the gates never see arbitrary canonical brackets.
        try:
            provider_text = compile_provider_text(text, rhetorical_role=rhetorical_role)
            channels = build_text_channels(canonical_text=text, provider_text=provider_text)
        except VoiceProviderTextError as exc:
            raise EnriqueActError(
                f"segment {sid} v3 provider-text compile failed: {exc}", tag=exc.tag
            ) from exc
        render_mode = "v3_provider_text"
        sent_text = channels["provider_text"]
    else:
        render_mode = "v2_settings"
        sent_text = text

    return _DirectedPlan(
        index=index,
        sid=sid,
        segment=segment,
        text=text,
        direction=direction,
        resolved=resolved,
        voice_id=voice_id,
        effective_voice_source=effective_voice_source,
        effective_model=effective_model,
        render_mode=render_mode,
        rhetorical_role=rhetorical_role,
        channels=channels,
        sent_text=sent_text,
    )


def _measure_duration(
    audio_bytes: bytes, segment: dict[str, Any], text: str
) -> tuple[float, str]:
    # Arc 3 (measured-durations): probe the REAL synthesized mp3. A valid
    # probe is the only thing that earns the "measured" label that arms
    # G5's WPM raise; otherwise fall back to payload/estimate (unchanged).
    measured = _mp3_duration_seconds(audio_bytes)
    if measured is not None:
        return measured, "measured"
    if segment.get("duration_seconds"):
        return float(segment["duration_seconds"]), "provided"
    return max(1.0, len(text) / 14.0), "estimated-chars"


def _reusable_receipt(
    receipt_path: Path, audio_path: Path, plan: _DirectedPlan
) -> dict[str, Any] | None:
    """Skip-if-exists guard (S2): return a prior receipt to REUSE iff a matching
    paid mp3 already exists, so a mid-loop-error resume/re-run does not re-bill
    a segment already synthesized at the SAME resolved settings. Any mismatch
    (settings changed, mp3 missing, receipt unreadable) -> re-synthesize."""
    if not (receipt_path.is_file() and audio_path.is_file()):
        return None
    try:
        prior = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(prior, dict):
        return None
    if prior.get("effective_elevenlabs_settings") != plan.effective_settings:
        return None
    if prior.get("voice_id") != plan.voice_id:
        return None
    # S3: a v3 receipt's audio was rendered from [tag] PROVIDER text; a current
    # NON-v3 plan (or vice versa) must NEVER reuse it. The persisted render_mode is
    # present only on v3 receipts (None on v2 — byte-identical), so compare against
    # the current plan's persisted form. This is defense-in-depth over the settings
    # check (model_id differs between v2/v3), and catches any future case where the
    # other resolved settings happen to coincide across modes.
    current_persisted_mode = (
        "v3_provider_text" if plan.render_mode == "v3_provider_text" else None
    )
    if prior.get("render_mode") != current_persisted_mode:
        return None
    # Story enhanced-vo.2 (AC-B6): on the v3 branch, ALSO compare the canonical +
    # provider text shas so a provider-text change (e.g. a different rhetorical_role
    # / tag, or edited narration) FORCES re-synthesis instead of reusing stale audio.
    if plan.render_mode == "v3_provider_text" and plan.channels is not None:
        if prior.get("provider_text_sha256") != plan.channels["provider_text_sha256"]:
            return None
        if prior.get("canonical_text_sha256") != plan.channels["canonical_text_sha256"]:
            return None
    return prior


def build_assembly_bundle(
    payload: dict[str, Any], *, selection: dict[str, Any], client: ElevenLabsClient | None = None
) -> dict[str, Any]:
    client = client or ElevenLabsClient()
    bundle_path = _require_bundle_path(payload)
    audio_dir = bundle_path / "assembly-bundle" / "audio"
    captions_dir = bundle_path / "assembly-bundle" / "captions"
    receipts_dir = bundle_path / "assembly-bundle" / "receipts"
    segments = _segments(payload)
    outputs: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    cost_per_1k = float(
        payload.get("cost_per_1k_chars")
        or _load_config().get("default_cost_per_1k_chars_usd", 0.30)
    )

    # P5 directed-voice (Step 4). Flag OFF ⇒ byte-identical to legacy: global
    # voice, no per-segment settings, no receipts. Flag ON ⇒ per-segment
    # resolution via the SAME shared mapper Storyboard B displays (no drift), the
    # tier-4/5 file reads wired here, and per-segment receipts written.
    directed = voice_direction_active()

    # Only segments that carry narration text are synthesized (blank-text rows are
    # skipped exactly as legacy did via the in-loop `continue`).
    synth_segments = [
        (index, segment)
        for index, segment in enumerate(segments, start=1)
        if _segment_text(segment)
    ]

    # S7: a zero-segment / all-blank payload returns the empty bundle WITHOUT
    # touching selection["selected_voice_id"] (legacy never did when there was no
    # work — a `selection` lacking that key must not KeyError here).
    if not synth_segments:
        return {
            "bundle_path": str(bundle_path),
            "narration_outputs": outputs,
            "compositor_invocation": build_compositor_invocation(outputs),
            **({"narration_receipts": receipts} if directed else {}),
        }

    selected_voice_id = selection["selected_voice_id"]

    if not directed:
        for index, segment in synth_segments:
            sid = _segment_id(segment, index)
            text = _segment_text(segment)
            audio_path = audio_dir / f"{sid}.mp3"
            audio_path.parent.mkdir(parents=True, exist_ok=True)
            audio = client.text_to_speech(text, selected_voice_id)
            audio_bytes = audio if isinstance(audio, bytes) else bytes(str(audio), "utf-8")
            audio_path.write_bytes(audio_bytes)
            duration, duration_source = _measure_duration(audio_bytes, segment, text)
            caption_path = captions_dir / f"{sid}.vtt"
            _write_vtt(caption_path, text, duration)
            cost = round((len(text) / 1000.0) * cost_per_1k, 4)
            print(
                f"Enrique segment {sid} [{index}/{len(segments)}] OK | "
                f"duration={duration:.1f}s | cost={cost:.4f}",
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
                    # RESERVED for a real mp3 probe — now satisfied by Arc 3's
                    # frame-duration parser. "provided"/"estimated-chars" remain
                    # PLANNED numbers; only "measured" arms G5's WPM raise.
                    "duration_source": duration_source,
                    "cost_usd": cost,
                }
            )
        return {
            "bundle_path": str(bundle_path),
            "narration_outputs": outputs,
            "compositor_invocation": build_compositor_invocation(outputs),
        }

    # --- directed path (flag ON) ---
    voice_selection_default = voice_selection_default_tier(selected_voice_id)
    # M1: tier-3 (voice_direction_defaults) arrives RAW from the payload — clean
    # it the SAME way as tiers 4/5 so a blank "" cannot mask a lower tier or flow
    # to the API. S4: a corrupt tier-5 style_guide.yaml becomes a tagged,
    # recoverable error-pause instead of a bare YAMLError escaping act().
    pass2_defaults = clean_default_tier(
        payload.get("voice_direction_defaults")
        if isinstance(payload.get("voice_direction_defaults"), dict)
        else {}
    )
    try:
        style_guide_defaults = load_style_guide_tts_defaults()
    except VoiceDirectionMapError as exc:
        raise EnriqueActError(str(exc), tag=exc.tag) from exc

    # PRE-FLIGHT (S1): validate + resolve EVERY segment BEFORE the first
    # synthesis call, so a bad segment N never bills segments 1..N-1.
    plans = [
        _resolve_directed_plan(
            index,
            segment,
            _segment_text(segment),
            pass2_defaults=pass2_defaults,
            voice_selection_default=voice_selection_default,
            style_guide_defaults=style_guide_defaults,
        )
        for index, segment in synth_segments
    ]

    total = len(segments)
    for plan in plans:
        sid = plan.sid
        text = plan.text
        audio_path = audio_dir / f"{sid}.mp3"
        caption_path = captions_dir / f"{sid}.vtt"
        receipt_path = receipts_dir / f"{sid}.json"
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        # S2 skip-if-exists: reuse a prior paid mp3 at the SAME resolved settings
        # rather than re-billing on a resume/re-run.
        reusable = _reusable_receipt(receipt_path, audio_path, plan)
        if reusable is not None:
            print(
                f"Enrique segment {sid} [{plan.index}/{total}] REUSED (directed) | "
                f"voice={plan.voice_id} | req={reusable.get('request_id')} | "
                "skip-if-exists (no re-spend)",
                file=sys.stderr,
                flush=True,
            )
            receipts.append(reusable)
            outputs.append(
                {
                    "segment_id": sid,
                    "slide_id": str(plan.segment.get("slide_id") or ""),
                    "audio_path": str(audio_path),
                    "caption_path": str(caption_path),
                    "duration_seconds": reusable.get("narration_duration"),
                    "duration_source": "reused",
                    "cost_usd": 0.0,
                    "voice_id": plan.voice_id,
                    "request_id": reusable.get("request_id"),
                    "request_id_present": reusable.get("request_id_present"),
                    "audio_sha256": reusable.get("audio_sha256"),
                    "effective_elevenlabs_settings": plan.effective_settings,
                    "effective_voice_source": plan.effective_voice_source,
                    "pause_before_seconds": reusable.get("pause_before_seconds"),
                    "pause_after_seconds": reusable.get("pause_after_seconds"),
                    "assembled_duration_seconds": reusable.get("assembled_duration_seconds"),
                }
            )
            continue

        # ENRIQUE-A5 firewall: on the v2/non-v3 path the text sent to TTS is the
        # figure-gated narration verbatim (`delivery_tag` is NEVER injected — Card 3
        # conservative posture). On the v3 branch (Story enhanced-vo.2, AC-B7) the
        # SENT text is the compiler's PROVIDER text (canonical + allowlisted [tag]),
        # which the TAG-ONLY firewall guarantees strips byte-exact back to canonical;
        # a fixed seed is graduated in (AC-B10 test-hygiene). REUSES the same proven
        # `text_to_speech_with_request_id` call. model_id is passed explicitly (M2)
        # so the SENT model == the recorded effective model.
        call_kwargs: dict[str, Any] = {"model_id": plan.effective_model}
        for field in ("stability", "similarity_boost", "style", "speed"):
            value = plan.resolved.get(field)
            if value is not None:
                call_kwargs[field] = value
        if plan.render_mode == "v3_provider_text":
            call_kwargs["seed"] = DIRECTED_V3_SEED
        tts_result = client.text_to_speech_with_request_id(
            plan.sent_text, plan.voice_id, **call_kwargs
        )
        audio_bytes = (
            tts_result.audio
            if isinstance(tts_result.audio, bytes)
            else bytes(str(tts_result.audio), "utf-8")
        )
        audio_path.write_bytes(audio_bytes)
        # S3: an always-present content digest + explicit flag prove a billed
        # call even when the provider returns NO request-id header (None would
        # otherwise be indistinguishable from "no call ever happened").
        audio_sha256 = hashlib.sha256(audio_bytes).hexdigest()
        request_id_present = tts_result.request_id is not None
        duration, duration_source = _measure_duration(audio_bytes, plan.segment, text)
        # AC-B5 captions HARD gate: on the v3 branch the VTT receives the CANONICAL
        # captions channel (already passed the zero-tag-leak gate in pre-flight). On
        # the v2/non-v3 path there are no channels and the caption is the canonical
        # text VERBATIM — byte-identical to today, even when it contains brackets
        # ([1]/[Figure 2]/[CO2]) (AC-B12 / M1).
        caption_text = (
            plan.channels["captions_text"]
            if plan.render_mode == "v3_provider_text" and plan.channels is not None
            else text
        )
        _write_vtt(caption_path, caption_text, duration)
        # NIT: bill over the text actually SENT (provider on v3 is longer by the tag);
        # on v2 sent_text == text so the cost is byte-identical.
        cost = round((len(plan.sent_text) / 1000.0) * cost_per_1k, 4)

        # pause_before/after -> recorded silence-padding metadata (compositor
        # wiring pending — see follow-on; NOT yet applied to the played audio).
        pause_before = float(plan.direction.pause_before_seconds or 0.0) if plan.direction else 0.0
        pause_after = float(plan.direction.pause_after_seconds or 0.0) if plan.direction else 0.0
        assembled_duration = round(pause_before + duration + pause_after, 3)

        effective_voice_direction = (
            plan.direction.model_dump(mode="json") if plan.direction is not None else None
        )

        print(
            f"Enrique segment {sid} [{plan.index}/{total}] OK (directed) | "
            f"voice={plan.voice_id} | model={plan.effective_model} | "
            f"duration={duration:.1f}s | cost={cost:.4f} | "
            f"req={tts_result.request_id} | sha={audio_sha256[:12]}",
            file=sys.stderr,
            flush=True,
        )

        receipt = {
            "segment_id": sid,
            "voice_id": plan.voice_id,
            "render_strategy": (
                plan.direction.render_strategy if plan.direction is not None else "tts"
            ),
            "effective_voice_direction": effective_voice_direction,
            "effective_elevenlabs_settings": plan.effective_settings,
            "effective_voice_source": plan.effective_voice_source,
            "request_id": tts_result.request_id,
            "request_id_present": request_id_present,
            "audio_sha256": audio_sha256,
            "model_id": plan.effective_model,
            "char_count": len(text),
            "cost_usd": cost,
            "narration_file": str(audio_path),
            "narration_vtt": str(caption_path),
            "narration_duration": duration,
            "pause_before_seconds": pause_before,
            "pause_after_seconds": pause_after,
            "assembled_duration_seconds": assembled_duration,
        }
        # Story enhanced-vo.2 (AC-B7): the provider-text block is added ONLY on the
        # active v3 branch (render_mode == v3_provider_text). On the v2/non-v3 path
        # the receipt stays byte-identical to today (AC-B12) — these keys are absent.
        if plan.render_mode == "v3_provider_text":
            receipt.update(
                {
                    "render_mode": plan.render_mode,
                    "canonical_text_sha256": plan.channels["canonical_text_sha256"],
                    "provider_text": plan.channels["provider_text"],
                    "provider_text_sha256": plan.channels["provider_text_sha256"],
                    "provider_text_strategy": plan.rhetorical_role,
                    "provider_text_tags": extract_tags(plan.channels["provider_text"]),
                    "provider_text_compiler_version": PROVIDER_TEXT_COMPILER_VERSION,
                }
            )
        _write_json(receipt_path, receipt)
        receipts.append(receipt)

        outputs.append(
            {
                "segment_id": sid,
                "slide_id": str(plan.segment.get("slide_id") or ""),
                "audio_path": str(audio_path),
                "caption_path": str(caption_path),
                "duration_seconds": duration,
                "duration_source": duration_source,
                "cost_usd": cost,
                # additive directed keys (flag-ON only).
                "voice_id": plan.voice_id,
                "request_id": tts_result.request_id,
                "request_id_present": request_id_present,
                "audio_sha256": audio_sha256,
                "effective_elevenlabs_settings": plan.effective_settings,
                "effective_voice_source": plan.effective_voice_source,
                "pause_before_seconds": pause_before,
                "pause_after_seconds": pause_after,
                "assembled_duration_seconds": assembled_duration,
            }
        )

    return {
        "bundle_path": str(bundle_path),
        "narration_outputs": outputs,
        "compositor_invocation": build_compositor_invocation(outputs),
        "narration_receipts": receipts,
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
