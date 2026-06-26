"""motion_planner act — deterministic ADAPTER over the Epic-14 motion engine.

The 07D.5 producer is a thin, deterministic adapter (spec-07d5 §2):

1. read the authorized winner deck (quinn_r ``upstream_output`` payload);
2. build the Epic-14 per-slide recommendation plan via
   ``build_motion_plan_from_authorized_storyboard`` (NO LLM) and apply the 07D
   designation — or AUTO-designate the engine's recommended video/animation
   slides for a no-HIL segment run (a provided designation overrides);
3. project the video/animation-designated rows into kira's ``motion_plan`` shape,
   sourcing the ``motion_prompt`` from the Epic-14 ``motion_brief`` /
   ``guidance_notes`` fused with a proven ``video-style-catalog.yaml``
   ``prompt_template``, the ``model_name`` from ``model-capabilities.yaml`` as a
   CURRENTLY-VALID id, and ``estimated_cost_usd`` from ``motion_budgeting``.

Binding amendment A (party 2026-06-26): NO model client is touched here — this is
pinned as a test invariant, not a comment. The library under
``skills/kling-video/references/`` is the SSOT for prompt templates and valid
model ids (absorbed fix 3).
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.motion_planner.payload_contract import CONSUMED_PAYLOAD_KEYS
from scripts.utilities.motion_budgeting import estimate_motion_credits

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-motion-planner"
CONFIG_PATH = REPO_ROOT / "app" / "specialists" / "motion_planner" / "config.yaml"
KLING_REFERENCES_DIR = REPO_ROOT / "skills" / "kling-video" / "references"
VIDEO_STYLE_CATALOG_PATH = KLING_REFERENCES_DIR / "video-style-catalog.yaml"
MODEL_CAPABILITIES_PATH = KLING_REFERENCES_DIR / "model-capabilities.yaml"
_MOTION_PLAN_ENGINE_PATH = (
    REPO_ROOT / "skills" / "production-coordination" / "scripts" / "motion_plan.py"
)

# Deterministic per-clip USD derived from motion_budgeting credits. Kling std 5s
# = 4 credits -> $0.12 (matches the proven kira fixture cost and stays under the
# 0.40 per-invocation cap). Documented rate so the projection is reproducible.
USD_PER_CREDIT = 0.03

# Production-safe default model: kling-v1-6 is the live-proven native id
# (2026-06-26). The stale kling-v2-6 default is "model is not supported" on the
# account (absorbed fix 2/3); the producer always emits an explicit valid id.
PREFERRED_MODEL_ID = "kling-v1-6"

_DEFAULT_DURATION = "5"
_DEFAULT_ASPECT_RATIO = "16:9"
_DEFAULT_MODE = "std"
_DEFAULT_DURATION_SECONDS = 5.0

# Deterministic style selection by operation (stable default acceptable per
# spec §10): a slide-preserving image2video style for approved-slide animation,
# a clean text2video atmosphere style otherwise. Both are library-proven.
_STYLE_BY_OPERATION = {
    "image2video": "K05-slide-preserving-motion-card-std-silent",
    "text2video": "K07-clinical-hallway-atmosphere-std-silent",
}

_MOTION_TYPES_EMITTED = frozenset({"video", "animation"})

_engine_module: ModuleType | None = None


class MotionPlannerActError(SpecialistDispatchError):
    """Raised when the motion-plan producer cannot project a valid plan.

    Dispatch-family so a mid-walk failure error-pauses recoverably (mirrors the
    kira/texas/gary fail-loud seams) instead of killing the trial.
    """


def _engine() -> ModuleType:
    """Load the Epic-14 motion-plan engine (REUSE the stockpile, not a re-impl).

    Imported from its file path because ``skills/production-coordination/scripts``
    is not an importable dotted package (hyphenated dir). The module inserts the
    repo root on ``sys.path`` for its ``scripts.utilities.motion_budgeting``
    import at load time.
    """
    global _engine_module
    if _engine_module is None:
        spec = importlib.util.spec_from_file_location(
            "production_coordination_motion_plan", _MOTION_PLAN_ENGINE_PATH
        )
        if spec is None or spec.loader is None:  # pragma: no cover - defensive
            raise MotionPlannerActError(
                f"could not load motion-plan engine from {_MOTION_PLAN_ENGINE_PATH}",
                tag="motion-planner.engine.missing",
            )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _engine_module = module
    return _engine_module


def _trail_entry(last_entry: ModelResolutionEntry, *, tag: str) -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level=last_entry.level,
        requested=last_entry.requested,
        resolved=last_entry.resolved,
        reason=tag,
        timestamp=last_entry.timestamp,
        cache_prefix_hash=last_entry.cache_prefix_hash,
    )


def decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise MotionPlannerActError(
            "motion_planner envelope cache_prefix is not JSON",
            tag="motion-planner.malformed",
        ) from exc
    if not isinstance(decoded, dict):
        raise MotionPlannerActError(
            "motion_planner envelope cache_prefix must decode to an object",
            tag="motion-planner.wrong-type",
        )
    return decoded


def _load_config() -> dict[str, Any]:
    if not CONFIG_PATH.is_file():
        return {}
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _resolve_authorized_storyboard(payload: dict[str, Any]) -> dict[str, Any]:
    """Find the authorized winner deck in the dispatched payload, FAILING LOUD.

    The 07D.5 edge delivers the quinn_r winner deck whole under ``upstream_output``
    (amendment B); a dev/replay path may pass ``authorized_storyboard`` directly.
    """
    candidates: list[dict[str, Any]] = []
    upstream = payload.get("upstream_output")
    if isinstance(upstream, dict):
        candidates.append(upstream)
    explicit = payload.get("authorized_storyboard")
    if isinstance(explicit, dict):
        candidates.append(explicit)
    candidates.append(payload)

    def _normalize(doc: Any) -> dict[str, Any] | None:
        """Accept either the Epic-14 ``authorized_slides`` shape OR quinn_r's G2C
        authorized-doc shape (key ``slides`` — ``_authorized_doc`` emits
        ``{schema_version, slides:[...]}``). Normalize ``slides`` -> the
        ``authorized_slides`` key the Epic-14 engine reads."""
        if not isinstance(doc, dict):
            return None
        if isinstance(doc.get("authorized_slides"), list) and doc["authorized_slides"]:
            return doc
        if isinstance(doc.get("slides"), list) and doc["slides"]:
            return {**doc, "authorized_slides": doc["slides"]}
        # quinn_r review/variant-selection shape: selections carry slide_ids (the
        # live G2B dependency). Build a minimal authorized deck (slide_id only) —
        # the explicit Gate-2M designation supplies the motion details; the
        # Epic-14 engine only strictly requires slide_id.
        review = doc.get("quinn_r_review")
        selections = (
            review.get("selections") if isinstance(review, dict) else doc.get("selections")
        )
        if isinstance(selections, list) and selections:
            slides = [
                {"slide_id": str(sel.get("slide_id"))}
                for sel in selections
                if isinstance(sel, dict) and sel.get("slide_id")
            ]
            if slides:
                return {"authorized_slides": slides}
        return None

    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        normalized = _normalize(candidate.get("authorized_storyboard"))
        if normalized is not None:
            return normalized
        normalized = _normalize(candidate)
        if normalized is not None:
            return normalized
    raise MotionPlannerActError(
        "motion_planner received no authorized storyboard (no authorized_slides/slides under "
        "upstream_output / authorized_storyboard); the producer cannot fabricate a deck",
        tag="motion-planner.storyboard.missing",
    )


def _env_designations() -> dict[str, dict[str, Any]] | None:
    """Dev/replay seam: a partial Gate-2M designation map from a JSON file named by
    ``MOTION_DESIGNATIONS_PATH``. Overlaid on the auto map (so only override slides
    need listing). Env-gated — the real path is the live G2M HIL gate; production
    never sets this. Mirrors kira's ``motion_plan_path`` replay affordance."""
    path = os.environ.get("MOTION_DESIGNATIONS_PATH")
    if not path or not Path(path).is_file():
        return None
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data if isinstance(data, dict) and data else None


def _max_credits(payload: dict[str, Any], config: dict[str, Any]) -> float:
    budget = payload.get("motion_budget")
    if isinstance(budget, dict) and isinstance(budget.get("max_credits"), (int, float)):
        return float(budget["max_credits"])
    return float(config.get("default_motion_budget_max_credits", 10000.0))


def _model_preference(payload: dict[str, Any], config: dict[str, Any]) -> str:
    budget = payload.get("motion_budget")
    if isinstance(budget, dict) and budget.get("model_preference"):
        return str(budget["model_preference"])
    return str(config.get("default_motion_budget_model_preference", "std"))


def _auto_designations(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Designate every slide as its Epic-14 recommendation (no override needed).

    Using each slide's own recommendation means ``apply_motion_designations``
    sees no operator-vs-recommendation divergence, so no ``override_reason`` is
    required (deterministic, no HIL).
    """
    designations: dict[str, dict[str, Any]] = {}
    for row in plan.get("slides", []):
        if not isinstance(row, dict):
            continue
        slide_id = str(row.get("slide_id") or "").strip()
        if not slide_id:
            continue
        raw_recommendation = row.get("recommendation")
        recommendation = raw_recommendation if isinstance(raw_recommendation, dict) else {}
        motion_type = str(recommendation.get("motion_type") or "static").strip().lower()
        designations[slide_id] = {
            "motion_type": motion_type,
            "motion_brief": recommendation.get("motion_brief"),
            "guidance_notes": recommendation.get("guidance_notes"),
        }
    return designations


def _slide_images(storyboard: dict[str, Any], payload: dict[str, Any]) -> dict[str, str]:
    """Map slide_id -> public image url / path for image2video, when available."""
    images: dict[str, str] = {}
    slides = storyboard.get("authorized_slides")
    if isinstance(slides, list):
        for slide in slides:
            if not isinstance(slide, dict):
                continue
            slide_id = str(slide.get("slide_id") or "").strip()
            if not slide_id:
                continue
            image = (
                slide.get("image_url")
                or slide.get("png_url")
                or slide.get("visual_file")
                or slide.get("png_path")
                or slide.get("file_path")
            )
            if image:
                images[slide_id] = str(image)
    overrides = payload.get("slide_images")
    if isinstance(overrides, dict):
        for slide_id, image in overrides.items():
            if image:
                images[str(slide_id)] = str(image)
    return images


def _load_style_catalog() -> dict[str, dict[str, Any]]:
    if not VIDEO_STYLE_CATALOG_PATH.is_file():
        return {}
    data = yaml.safe_load(VIDEO_STYLE_CATALOG_PATH.read_text(encoding="utf-8")) or {}
    catalog: dict[str, dict[str, Any]] = {}
    for style in data.get("styles", []) if isinstance(data, dict) else []:
        if isinstance(style, dict) and style.get("style_id"):
            catalog[str(style["style_id"])] = style
    return catalog


def _select_style(catalog: dict[str, dict[str, Any]], operation: str) -> dict[str, Any]:
    """Deterministically pick a catalog style for the operation (stable default)."""
    preferred = _STYLE_BY_OPERATION.get(operation)
    if preferred and preferred in catalog:
        return catalog[preferred]
    # Fallback: first catalog style matching the operation, by sorted style_id.
    for style_id in sorted(catalog):
        if str(catalog[style_id].get("operation") or "") == operation:
            return catalog[style_id]
    return {"style_id": preferred or operation, "prompt_template": ""}


def _fuse_prompt(brief: str | None, prompt_template: str | None) -> str:
    """Fuse the Epic-14 brief with a proven library prompt_template (deterministic)."""
    brief_text = (brief or "").strip()
    template_text = " ".join((prompt_template or "").split()).strip()
    if brief_text and template_text:
        return f"{brief_text} {template_text}"
    return (
        brief_text
        or template_text
        or "Create concise instructional motion from the approved still image."
    )


def _valid_model_id() -> str:
    """Resolve a CURRENTLY-VALID kling model id from the library SSOT.

    Reads ``production_valid_model_ids`` / ``deprecated_model_ids`` from
    ``model-capabilities.yaml`` (refreshed at this story); prefers the proven
    kling-v1-6 and never returns a deprecated id (e.g. the stale kling-v2-6).
    """
    data: dict[str, Any] = {}
    if MODEL_CAPABILITIES_PATH.is_file():
        loaded = yaml.safe_load(MODEL_CAPABILITIES_PATH.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            data = loaded
    valid = [str(m) for m in data.get("production_valid_model_ids", []) if m]
    deprecated = {str(m) for m in data.get("deprecated_model_ids", [])}
    if PREFERRED_MODEL_ID in valid and PREFERRED_MODEL_ID not in deprecated:
        return PREFERRED_MODEL_ID
    for model_id in valid:
        if model_id not in deprecated:
            return model_id
    raise MotionPlannerActError(
        "model-capabilities.yaml lists no currently-valid kling model id "
        "(production_valid_model_ids empty or all deprecated)",
        tag="motion-planner.model.invalid",
    )


def _project_slides(
    applied_plan: dict[str, Any],
    storyboard: dict[str, Any],
    payload: dict[str, Any],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    """Project video/animation-designated rows into kira's motion_plan slide shape."""
    images = _slide_images(storyboard, payload)
    catalog = _load_style_catalog()
    model_name = _valid_model_id()
    model_preference = _model_preference(payload, config)
    usd_per_credit = float(config.get("usd_per_credit", USD_PER_CREDIT))
    credits = estimate_motion_credits(_DEFAULT_DURATION_SECONDS, model_preference)
    estimated_cost_usd = round(credits * usd_per_credit, 2)

    projected: list[dict[str, Any]] = []
    for row in applied_plan.get("slides", []):
        if not isinstance(row, dict):
            continue
        motion_type = str(row.get("motion_type") or "static").strip().lower()
        if motion_type not in _MOTION_TYPES_EMITTED:
            continue
        slide_id = str(row.get("slide_id") or "").strip()
        if not slide_id:
            continue
        image_url = images.get(slide_id)
        operation = "image2video" if image_url else "text2video"
        style = _select_style(catalog, operation)
        brief = row.get("motion_brief") or row.get("guidance_notes")
        motion_prompt = _fuse_prompt(brief, style.get("prompt_template"))
        slide: dict[str, Any] = {
            "slide_id": slide_id,
            "model_name": model_name,
            "duration": _DEFAULT_DURATION,
            "aspect_ratio": _DEFAULT_ASPECT_RATIO,
            "mode": _DEFAULT_MODE,
            "motion_prompt": motion_prompt,
            "estimated_cost_usd": estimated_cost_usd,
            "style_id": str(style.get("style_id") or ""),
        }
        # image2video carries the approved slide PNG; text2video omits image_url.
        if image_url:
            slide["image_url"] = image_url
        projected.append(slide)
    projected.sort(key=lambda item: item["slide_id"])
    return projected


def build_motion_plan(payload: dict[str, Any]) -> dict[str, Any]:
    """Deterministically build kira's motion_plan from the dispatched payload."""
    config = _load_config()
    if os.environ.get("MOTION_PLANNER_DEBUG"):
        try:
            up = payload.get("upstream_output")
            dbg = {
                "payload_keys": sorted(payload.keys()),
                "upstream_type": type(up).__name__,
                "upstream_keys": sorted(up.keys()) if isinstance(up, dict) else None,
                "sample": {k: str(v)[:240] for k, v in payload.items()},
            }
            Path(".tmp/producer_payload_debug.json").write_text(
                json.dumps(dbg, indent=2, default=str), encoding="utf-8"
            )
        except Exception:  # pragma: no cover - debug only
            pass
    storyboard = _resolve_authorized_storyboard(payload)
    engine = _engine()
    budget = {
        "max_credits": _max_credits(payload, config),
        "model_preference": _model_preference(payload, config),
    }
    try:
        plan = engine.build_motion_plan_from_authorized_storyboard(
            storyboard, motion_enabled=True, motion_budget=budget
        )
        # Auto map (each slide -> its Epic-14 recommendation) is the COMPLETE base;
        # an explicit partial designation (payload or replay-env) overlays it, so a
        # caller only lists the slides they override (apply_motion_designations
        # requires a complete map).
        explicit = (
            payload.get("motion_designations")
            or payload.get("designations")
            or _env_designations()
        )
        designations = _auto_designations(plan)
        if isinstance(explicit, dict):
            designations = {**designations, **explicit}
        applied = engine.apply_motion_designations(plan, designations)
    except engine.MotionPlanError as exc:
        raise MotionPlannerActError(
            f"Epic-14 engine rejected the storyboard/designation: {exc}",
            tag="motion-planner.engine.invalid",
        ) from exc
    slides = _project_slides(applied, storyboard, payload, config)
    return {"slides": slides}


def act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError(
            "motion_planner act invoked before plan; resolution trail is empty"
        )
    last_entry = state.model_resolution_trail[-1]
    payload = decode_envelope_payload(state)
    try:
        motion_plan = build_motion_plan(payload)
    except MotionPlannerActError as exc:
        state.model_resolution_trail.append(_trail_entry(last_entry, tag=exc.tag))
        raise
    output = {
        "motion_plan": motion_plan,
        "motion_planner": {
            "specialist_id": "motion_planner",
            "slide_count": len(motion_plan["slides"]),
        },
    }
    entries_count = state.cache_state.entries_count if state.cache_state is not None else 0
    return {
        "model_resolution_trail": [
            *state.model_resolution_trail,
            _trail_entry(last_entry, tag="motion-planner.projected.ok"),
        ],
        "cache_state": CacheState(
            cache_prefix=json.dumps(
                output, sort_keys=True, ensure_ascii=True, separators=(",", ":"), default=str
            ),
            entries_count=entries_count + 1,
        ).model_dump(mode="json"),
    }


__all__ = [
    "CONFIG_PATH",
    "CONSUMED_PAYLOAD_KEYS",
    "MotionPlannerActError",
    "SANCTUM_DIR",
    "act",
    "build_motion_plan",
    "decode_envelope_payload",
]
