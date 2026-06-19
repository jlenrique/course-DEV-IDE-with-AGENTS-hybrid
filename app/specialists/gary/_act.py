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
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.gary.gamma_dispatch import GammaDispatchError, dispatch_to_gamma
from scripts.api_clients.gamma_client import GammaClient
from skills.gamma_api_mastery.scripts.gamma_operations import (
    download_export,
    materialize_exported_slide_paths_by_title,
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


class GaryActError(SpecialistDispatchError):
    """Raised when Gary cannot produce a valid Gamma output envelope.

    Taxonomy re-base (live-path tranche, 2026-06-12): dispatch-family so a
    mid-walk failure error-pauses recoverably instead of killing the trial.
    """


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
        # Taxonomy re-base tranche (2026-06-12): the fabricated slide-01
        # roster was the slides-leg sibling of quinn_r's ninth seam —
        # absence of inputs is a contract violation, never a mode switch.
        raise GaryActError(
            "gary dispatched with no slides/per_slide_directives; refusing "
            "to fabricate a placeholder roster",
            tag="gamma.slides.starved",
        )
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


def _slide_title(slide: dict[str, Any], index: int) -> str:
    """The briefed card title — the SINGLE source for both the Gamma card
    heading (in `_input_text`) and the export title-match key (`expected_slots`).

    Storyboard-correctness follow-on (2026-06-19): Gamma free-titles and merges
    pages unless each input chunk leads with the exact briefed title under
    `cardSplit=inputTextBreaks`. Sharing one helper guarantees the heading we
    send and the key we match on cannot drift apart.
    """
    return str(
        slide.get("title")
        or slide.get("prompt")
        or slide.get("visual_description")
        or f"slide-{index:02d}"
    )


def _input_text(slides: list[dict[str, Any]], payload: dict[str, Any]) -> str:
    if payload.get("input_text"):
        return str(payload["input_text"])
    chunks = []
    for index, slide in enumerate(slides, start=1):
        title = _slide_title(slide, index)
        body = str(
            slide.get("prompt") or slide.get("brief") or slide.get("visual_description") or ""
        ).strip()
        # The `\n---\n` break is load-bearing under cardSplit=inputTextBreaks
        # (it delimits cards), so a body that embeds it would split a spurious
        # extra card and fail the bijective match. Neutralize any embedded
        # delimiter before it reaches the card splitter.
        body = body.replace("\n---\n", " ")
        # Lead every chunk with the exact briefed title as a heading so Gamma
        # adopts it as the card title verbatim under cardSplit=inputTextBreaks;
        # the export title-matcher (bijective containment) then resolves cleanly
        # instead of fail-louding on Gamma's invented page titles.
        chunk = f"# {title}" if not body or body == title else f"# {title}\n\n{body}"
        chunks.append(chunk)
    return "\n---\n".join(chunks)


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
    dropped_pages: list[dict[str, Any]] = []
    for variant in variants:
        generation = client.generate_deck(
            _input_text(slides, payload),
            num_cards=len(slides),
            theme_id=theme_id,
            # cardSplit=inputTextBreaks pins one card per `\n---\n` chunk, so
            # Gamma can no longer merge/split briefed slides (the 6->5 collapse
            # that orphaned slide-05/06). With the title-led chunks above, each
            # card is titled with the briefed title and binds bijectively.
            card_split="inputTextBreaks",
            additional_instructions=(
                f"{str(payload.get('additional_instructions') or '').strip()} "
                "Use each section's leading heading as that card's title "
                "verbatim; produce exactly one card per section; do not add a "
                "cover, agenda, divider, or summary card; do not merge or split "
                f"sections. Variant {variant}."
            ).strip(),
            export_as="png",
        )
        raw_generation_id = (
            generation.get("generation_id")
            or generation.get("id")
            or generation.get("generationId")
        )
        if not raw_generation_id:
            # Trial-3 cycle-2 root-cause hardening (2026-06-12): the old
            # fabricated per-variant fixture-id sentinel here was the EIGHTH
            # silent seam — it masked generate_deck returning a bare POST ack
            # and let untracked spend + empty slide rows flow to G2C.
            # Recoverable family: error-pause + `trial recover` retries.
            raise GammaDispatchError(
                f"gamma generation returned no id for variant {variant}; "
                f"keys={sorted(generation)}",
                tag="gamma.generation.id-missing",
            )
        generation_id = str(raw_generation_id)
        calls.append(generation_id)
        # Storyboard-correctness fix (party-ratified 2026-06-18): match the
        # exported pages to briefed slide_ids by TITLE (deterministic bijective
        # containment), NOT by position. Gamma injects a cover + merges/drops +
        # rephrases titles, so the page order does not correspond to the brief
        # order. The matcher surfaces the cover (dropped), a merged-away brief
        # (brief-unmatched), a stray page (page-unmatched), and collisions
        # (title-ambiguous) instead of silently shifting every slide.
        expected_slots = [
            (
                str(slide.get("slide_id") or f"slide-{index:02d}"),
                _slide_title(slide, index),
            )
            for index, slide in enumerate(slides, start=1)
        ]
        export_url = generation.get("exportUrl") or generation.get("export_url")
        if isinstance(export_url, str) and export_url.strip():
            downloaded_export = download_export(
                export_url, output_dir=export_dir, filename=f"gary_{variant}.png"
            )
            match = materialize_exported_slide_paths_by_title(
                Path(str(downloaded_export)),
                requested_format="png",
                expected_slots=expected_slots,
                module_lesson_part=variant,
                export_dir=export_dir,
                label=variant,
            )
            if match.ambiguous:
                raise GammaDispatchError(
                    f"gamma export title-ambiguous for variant {variant}: "
                    f"{match.ambiguous}",
                    tag="gamma.export.title-ambiguous",
                )
            if match.unmatched_keys:
                raise GammaDispatchError(
                    f"gamma export left briefed slide(s) unmatched for variant "
                    f"{variant}: {match.unmatched_keys}; unmatched pages: "
                    f"{[p.get('title') for p in match.unmatched_pages]}",
                    tag="gamma.export.brief-unmatched",
                )
            if match.unmatched_pages:
                raise GammaDispatchError(
                    f"gamma export produced non-leading unmatched page(s) for "
                    f"variant {variant}: {[p.get('title') for p in match.unmatched_pages]}",
                    tag="gamma.export.page-unmatched",
                )
            slide_paths = dict(match.matched)
            dropped_pages.extend({"variant": variant, **d} for d in match.dropped_pages)
        else:
            # Legacy fallback: generation already carries materialized rows
            # keyed by slide_id (no export to title-match).
            slide_paths = {}
            rows = generation.get("gary_slide_output")
            if isinstance(rows, list):
                for row in rows:
                    if isinstance(row, dict) and row.get("slide_id"):
                        slide_paths[str(row["slide_id"])] = str(row.get("file_path", ""))
        for index, slide in enumerate(slides, start=1):
            slide_id = str(slide.get("slide_id") or f"slide-{index:02d}")
            output.append(
                {
                    "slide_id": slide_id,
                    "card_number": index,
                    "dispatch_variant": variant,
                    "file_path": slide_paths.get(slide_id, ""),
                    "generation_id": generation_id,
                    # Observation A (folded in): the real slide title (original
                    # casing, objective-free), so the storyboard surface can
                    # stop showing the bare slide_id.
                    "display_title": str(slide.get("title") or "").strip() or slide_id,
                    "visual_description": str(
                        slide.get("visual_description") or slide.get("prompt") or ""
                    ),
                }
            )
    if output and not any(row.get("file_path") for row in output):
        # Twice-bitten guard (deferred this morning, bitten this evening):
        # slide rows with no materialized artifacts are quality theater —
        # downstream gates would review metadata, not slides. Recoverable.
        raise GammaDispatchError(
            f"no slide artifacts materialized for generation(s) {calls}; "
            "every gary_slide_output row has an empty file_path",
            tag="gamma.export.unmaterialized",
        )
    return {
        "generation_id": calls[0],
        "status": "complete",
        "theme_resolution": {"theme_id": theme_id, "handshake": "list_themes"},
        "generation_mode": "double-dispatch" if len(variants) == 2 else "single-dispatch",
        "calls_made": len(calls),
        "gary_slide_output": output,
        # Decision #1 provenance: engine cover pages dropped during title
        # matching are recorded here, never silently vanished.
        "dropped_pages": dropped_pages,
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
