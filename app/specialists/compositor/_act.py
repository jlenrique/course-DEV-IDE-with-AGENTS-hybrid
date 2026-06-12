"""Compositor Class-D2 deterministic assembly pipeline."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.dispatch_errors import SpecialistDispatchError

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-compositor"
FIELD_MASK_PATH = REPO_ROOT / "docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/field-mask.yaml"


class CompositorActError(SpecialistDispatchError):
    """Raised when Compositor cannot assemble deterministic outputs.

    Audio-arc taxonomy re-base (2026-06-12): a missing asset mid-copy must
    error-pause recoverably AFTER real audio spend, never crash the walk.
    """

    def __init__(self, message: str, *, tag: str = "compositor.assembly.failed") -> None:
        super().__init__(message, tag=tag)


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), default=str)


def decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise CompositorActError("compositor cache_prefix is not JSON") from exc
    if not isinstance(decoded, dict):
        raise CompositorActError("compositor cache_prefix must decode to an object")
    return decoded


def _bundle(payload: dict[str, Any]) -> Path:
    raw = payload.get("bundle_path") or payload.get("BUNDLE_PATH") or REPO_ROOT / "runs/compositor"
    return Path(str(raw))


def _slide_id(row: dict[str, Any], index: int, source: Path) -> str:
    return str(row.get("slide_id") or row.get("id") or source.stem or f"slide-{index:02d}")


def _copy_asset(source: str | Path, target: Path) -> str:
    src = Path(str(source))
    if not src.is_file():
        raise CompositorActError(f"missing compositor source asset: {src}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, target)
    return str(target)


def _visual_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw = payload.get("gary_slide_output") or payload.get("visuals") or []
    return [dict(row) for row in raw if isinstance(row, dict)]


def _motion_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw = payload.get("motion_receipts") or []
    rows = [dict(row) for row in raw if isinstance(row, dict)]
    rows.extend({"motion_asset_path": path} for path in payload.get("motion_asset_paths", []))
    return rows


def sync_visuals(payload: dict[str, Any]) -> dict[str, Any]:
    bundle = _bundle(payload)
    copied: dict[str, dict[str, str]] = {"visuals": {}, "motion": {}}
    for index, row in enumerate(_visual_rows(payload), start=1):
        source = Path(str(row.get("file_path") or row.get("visual_file") or ""))
        sid = _slide_id(row, index, source)
        target = bundle / "assembly-bundle" / "visuals" / f"{sid}.png"
        copied["visuals"][sid] = _copy_asset(source, target)
    for index, row in enumerate(_motion_rows(payload), start=1):
        source = Path(str(row.get("motion_asset_path") or row.get("file_path") or ""))
        sid = _slide_id(row, index, source)
        suffix = source.suffix.lower() if source.suffix.lower() in {".mp4", ".webm"} else ".mp4"
        target = bundle / "assembly-bundle" / "motion" / f"{sid}{suffix}"
        copied["motion"][sid] = _copy_asset(source, target)
    return copied


def _mask_fields() -> set[str]:
    data = yaml.safe_load(FIELD_MASK_PATH.read_text(encoding="utf-8")) or {}
    fields = set(data.get("defaults") or [])
    fields.update((data.get("specialist_extensions") or {}).get("compositor") or [])
    return {str(field).split(".")[-1] for field in fields}


def mask_assembly_guide(text: str) -> str:
    fields = _mask_fields()
    lines = []
    for line in text.replace("\r\n", "\n").splitlines():
        key = line.split(":", 1)[0].strip("- `").strip()
        lines.append(f"{key}: <masked>" if key in fields and ":" in line else line)
    return "\n".join(lines).strip() + "\n"


def field_masked_hash(path: Path) -> str:
    masked = mask_assembly_guide(path.read_text(encoding="utf-8")).encode()
    return hashlib.sha256(masked).hexdigest()


def regenerate_assembly_guide(payload: dict[str, Any], copied: dict[str, dict[str, str]]) -> Path:
    bundle = _bundle(payload)
    guide = Path(str(payload.get("assembly_guide_path") or bundle / "DESCRIPT-ASSEMBLY-GUIDE.md"))
    guide.parent.mkdir(parents=True, exist_ok=True)
    audio = [str(path) for path in payload.get("audio_paths", [])]
    beds = [str(path) for path in payload.get("audio_bed_paths", [])]
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    lines = [
        "# DESCRIPT ASSEMBLY GUIDE",
        "",
        f"- generated_at: {now}",
        f"- run_id: {payload.get('run_id') or now}",
        f"- build_timestamp: {now}",
        f"- bundle_path: {bundle.as_posix()}",
        "",
        "## Visuals",
        *[f"- {sid}: assembly-bundle/visuals/{sid}.png" for sid in sorted(copied["visuals"])],
        "",
        "## Motion",
        *[
            f"- {sid}: assembly-bundle/motion/{sid}{Path(path).suffix}"
            for sid, path in sorted(copied["motion"].items())
        ],
        "",
        "## Audio",
        *[f"- narration: {Path(path).as_posix()}" for path in sorted(audio)],
        *[f"- bed: {Path(path).as_posix()}" for path in sorted(beds)],
    ]
    guide.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return guide


def run_compositor_pipeline(payload: dict[str, Any]) -> dict[str, Any]:
    # Audio-arc grounding (2026-06-12): node 14 projects enrique's
    # compositor_invocation (top-level key); audio/caption paths ride nested
    # inside it, so the act derives them — dp-v1 projections are strictly
    # top-level-key (party consensus: derive in the act, don't grow the
    # projection substrate mid-arc).
    invocation = payload.get("compositor_invocation")
    if not payload.get("audio_paths") and isinstance(invocation, dict):
        payload = {
            **payload,
            "audio_paths": list(invocation.get("audio_paths") or []),
            "caption_paths": list(invocation.get("caption_paths") or []),
        }
    copied = sync_visuals(payload)
    guide = regenerate_assembly_guide(payload, copied)
    return {
        "specialist_id": "compositor",
        "gate_id": "G3",
        "bundle_path": str(_bundle(payload)),
        "synced_assets": copied,
        "assembly_guide_path": str(guide),
        "assembly_guide_field_masked_hash": field_masked_hash(guide),
    }


def act(state: RunState) -> dict[str, Any]:
    verdict = run_compositor_pipeline(decode_envelope_payload(state))
    entries = state.cache_state.entries_count if state.cache_state is not None else 0
    return {
        "cache_state": CacheState(
            cache_prefix=_json_dumps(verdict), entries_count=entries + 1
        ).model_dump(mode="json")
    }


from app.specialists.compositor.payload_contract import CONSUMED_PAYLOAD_KEYS  # noqa: E402

__all__ = [
    "CONSUMED_PAYLOAD_KEYS",
    "FIELD_MASK_PATH",
    "SANCTUM_DIR",
    "CompositorActError",
    "act",
    "decode_envelope_payload",
    "field_masked_hash",
    "mask_assembly_guide",
    "regenerate_assembly_guide",
    "run_compositor_pipeline",
    "sync_visuals",
]
