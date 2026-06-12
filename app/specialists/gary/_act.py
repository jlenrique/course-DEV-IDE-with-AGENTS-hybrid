"""Gary Class-C Gamma API act implementation."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.gary.gamma_dispatch import GammaDispatchError, dispatch_to_gamma
from scripts.api_clients.gamma_client import GammaClient
from skills.gamma_api_mastery.scripts.gamma_operations import (
    _materialize_exported_slide_paths,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-gary"
REFERENCES_DIR = REPO_ROOT / "skills" / "bmad-agent-gamma" / "references"
GARY_REFERENCES = (
    "content-type-mapping.md",
    "context-envelope-schema.md",
    "theme-template-preview.md",
    "quality-assessment.md",
)


class GaryActError(RuntimeError):
    """Raised when Gary cannot produce a valid Gamma output envelope."""

    def __init__(self, message: str, *, tag: str) -> None:
        super().__init__(message)
        self.tag = tag


def _json_dumps(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), default=str
    )


def decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise GaryActError("gary envelope cache_prefix is not JSON", tag="gamma.malformed") from exc
    if not isinstance(decoded, dict):
        raise GaryActError(
            "gary envelope cache_prefix must decode to an object",
            tag="gamma.wrong-type",
        )
    return decoded


def read_sanctum_digest(sanctum_dir: Path = SANCTUM_DIR) -> str:
    if not sanctum_dir.is_dir():
        return ""
    rows: list[str] = []
    for path in sorted(sanctum_dir.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            rows.append(f"{path.relative_to(sanctum_dir).as_posix()}\t{digest}")
    return "\n".join(rows)


def read_references(references_dir: Path = REFERENCES_DIR) -> str:
    parts: list[str] = []
    for name in GARY_REFERENCES:
        path = references_dir / name
        body = path.read_text(encoding="utf-8") if path.is_file() else f"<missing: {name}>"
        parts.append(f"### Reference: {name}\n{body}")
    return "\n\n".join(parts)


def _trail_entry(last_entry: ModelResolutionEntry, *, tag: str) -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level=last_entry.level,
        requested=last_entry.requested,
        resolved=last_entry.resolved,
        reason=tag,
        timestamp=datetime.now(UTC),
        cache_prefix_hash=last_entry.cache_prefix_hash,
    )


def _slides(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw = payload.get("slides") or payload.get("per_slide_directives") or []
    if not raw:
        raw = [
            {
                "slide_id": "slide-01",
                "prompt": payload.get("prompt", "Generate one course slide."),
            }
        ]
    if not isinstance(raw, list) or not all(isinstance(item, dict) for item in raw):
        raise GaryActError("gary slides must be a list of objects", tag="gamma.slides.invalid")
    return raw


def _theme_id(client: GammaClient, payload: dict[str, Any]) -> str | None:
    themes = client.list_themes(limit=int(payload.get("theme_limit", 20)))
    requested = str(payload.get("theme_id") or "").strip()
    if requested:
        return requested
    for theme in themes:
        if isinstance(theme, dict):
            value = theme.get("id") or theme.get("themeId") or theme.get("gammaId")
            if value:
                return str(value)
    return None


def _input_text(slides: list[dict[str, Any]], payload: dict[str, Any]) -> str:
    if payload.get("input_text"):
        return str(payload["input_text"])
    chunks = []
    for index, slide in enumerate(slides, start=1):
        prompt = slide.get("prompt") or slide.get("brief") or slide.get("title") or f"Slide {index}"
        chunks.append(str(prompt))
    return "\n---\n".join(chunks)


def _paths_from_generation(
    generation: dict[str, Any],
    *,
    slides: list[dict[str, Any]],
    export_dir: Path,
    label: str,
) -> list[str]:
    if isinstance(generation.get("exported_slide_paths"), list):
        return [str(path) for path in generation["exported_slide_paths"]]
    downloaded = generation.get("downloaded_path") or generation.get("export_path")
    if downloaded:
        return _materialize_exported_slide_paths(
            Path(str(downloaded)),
            requested_format="png",
            expected_card_numbers=list(range(1, len(slides) + 1)),
            module_lesson_part="gary",
            export_dir=export_dir,
            label=label,
        )
    rows = generation.get("gary_slide_output")
    if isinstance(rows, list):
        return [str(row.get("file_path", "")) for row in rows if isinstance(row, dict)]
    return []


def build_vera_g3_invocation(slide_output: list[dict[str, Any]]) -> dict[str, Any]:
    paths = [row["file_path"] for row in slide_output if row.get("file_path")]
    return {"specialist_id": "vera", "gate_id": "G3", "artifact_paths": paths}


def generate_gamma_variants(
    payload: dict[str, Any], *, client: GammaClient | None = None
) -> dict[str, Any]:
    client = client or GammaClient()
    slides = _slides(payload)
    export_dir = Path(str(payload.get("export_dir") or REPO_ROOT / "runs" / "gary-gamma"))
    export_dir.mkdir(parents=True, exist_ok=True)
    theme_id = _theme_id(client, payload)
    variants = ("A", "B") if bool(payload.get("double_dispatch")) else ("A",)
    output: list[dict[str, Any]] = []
    calls: list[str] = []
    for variant in variants:
        generation = client.generate_deck(
            _input_text(slides, payload),
            num_cards=len(slides),
            theme_id=theme_id,
            additional_instructions=str(
                payload.get("additional_instructions") or f"Variant {variant}"
            ),
            export_as="png",
        )
        generation_id = str(
            generation.get("generation_id") or generation.get("id") or f"fixture-{variant}"
        )
        calls.append(generation_id)
        paths = _paths_from_generation(
            generation, slides=slides, export_dir=export_dir, label=variant
        )
        for index, slide in enumerate(slides, start=1):
            output.append(
                {
                    "slide_id": str(slide.get("slide_id") or f"slide-{index:02d}"),
                    "card_number": index,
                    "dispatch_variant": variant,
                    "file_path": paths[index - 1] if index - 1 < len(paths) else "",
                    "generation_id": generation_id,
                    "visual_description": str(
                        slide.get("visual_description") or slide.get("prompt") or ""
                    ),
                }
            )
    return {
        "generation_id": calls[0],
        "status": "complete",
        "theme_resolution": {"theme_id": theme_id, "handshake": "list_themes"},
        "generation_mode": "double-dispatch" if len(variants) == 2 else "single-dispatch",
        "calls_made": len(calls),
        "gary_slide_output": output,
        "vera_g3_invocation": build_vera_g3_invocation(output),
    }


def act(state: RunState, *, client: GammaClient | None = None) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("gary act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    payload = decode_envelope_payload(state)
    tag = "gamma.dispatch.ok"
    try:
        if payload.get("slides") or payload.get("per_slide_directives") or payload.get("prompt"):
            receipt = generate_gamma_variants(payload, client=client)
        else:
            receipt = dispatch_to_gamma(
                directive_path=payload.get("directive_path"),
                export_dir=payload.get("export_dir"),
            )
            tag = "receipt.parsed.ok"
    except GammaDispatchError as exc:
        state.model_resolution_trail.append(_trail_entry(last_entry, tag=exc.tag))
        raise
    except GaryActError as exc:
        state.model_resolution_trail.append(_trail_entry(last_entry, tag=exc.tag))
        raise
    if not isinstance(receipt.get("gary_slide_output"), list) or not receipt["gary_slide_output"]:
        raise GaryActError("gamma receipt missing slide output", tag="gamma.output.missing")
    output = {"specialist_id": "gary", **receipt, "model_id": last_entry.resolved}
    entries_count = state.cache_state.entries_count if state.cache_state is not None else 0
    return {
        "model_resolution_trail": [
            *state.model_resolution_trail,
            _trail_entry(last_entry, tag=tag),
        ],
        "cache_state": CacheState(
            cache_prefix=_json_dumps(output),
            entries_count=entries_count + 1,
        ).model_dump(mode="json"),
    }


# Amelia a.1 (party review 2026-06-12): the payload contract participates in
# the act's import graph so it cannot rot as an orphan module.
from app.specialists.gary.payload_contract import CONSUMED_PAYLOAD_KEYS  # noqa: E402

__all__ = [
    "CONSUMED_PAYLOAD_KEYS",
    "GARY_REFERENCES",
    "GaryActError",
    "SANCTUM_DIR",
    "act",
    "build_vera_g3_invocation",
    "decode_envelope_payload",
    "generate_gamma_variants",
    "read_references",
    "read_sanctum_digest",
]
