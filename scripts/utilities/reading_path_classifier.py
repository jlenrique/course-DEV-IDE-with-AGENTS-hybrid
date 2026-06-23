"""Deterministic reading-path classification over rich perception artifacts."""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.models.adapter import make_chat_model
from app.models.perception.perception_artifact import (
    CalloutIntent,
    ImageRoleFlag,
    ImageRoleTier,
    MacroLayout,
    NarrationCadence,
    PerceptionArtifact,
    ReadingPath,
    ReadingPathFlag,
    ReadingPathSource,
    TextSubstructure,
)
from scripts.utilities.reading_path_derivation import derive_primary_name

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = (
    REPO_ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "reading-path-patterns-catalog.md"
)
LLM_PRIMARY_MODEL_ID = "gpt-5.5"
LLM_PRIMARY_SPECIALIST_ID = "vision"
LLM_PRIMARY_TIMEOUT_SECONDS = 60.0
LLM_PRIMARY_ATTEMPTS = 2

READING_PATH_PATTERNS: tuple[str, ...] = (
    "z_pattern",
    "f_pattern",
    "center_out",
    "top_down",
    "multi_column",
    "grid_quadrant",
    "sequence_numbered",
    "split_image_text",
    "two_up_comparison",
    "text_hero_divider",
    "enumerated_process",
    "diagram_driven",
)

REQUIRED_PERCEPTION_FIELDS: frozenset[str] = frozenset(
    {
        "confidence",
        "coverage",
        "extracted_text",
        "layout_description",
        "slide_title",
        "text_blocks",
        "visual_elements",
    }
)

CADENCE_TOKENS: dict[str, tuple[str, ...]] = {
    "z_pattern": ("headline", "body", "visual", "CTA", "top-left", "bottom-right"),
    "f_pattern": ("evidence", "drill into", "as shown", "note the", "data shows", "callout"),
    "center_out": (
        "returning to the center",
        "back to the hero",
        "circling back",
        "center again",
        "back to the main",
        "returning to the heart",
    ),
    "top_down": (
        "next item",
        "continuing down",
        "further down",
        "proceeding through",
        "step by step",
        "in order",
    ),
    "multi_column": (
        "in the next column",
        "moving to the right",
        "the adjacent column",
        "the column beside",
        "moving rightward",
        "in the column to the right",
        "across the columns",
    ),
    "grid_quadrant": (
        "compared to",
        "contrast",
        "whereas",
        "whilst",
        "on the other hand",
        "vs",
        "versus",
        "by contrast",
        "different from",
        "in comparison",
    ),
    "sequence_numbered": (
        "first",
        "second",
        "third",
        "fourth",
        "next",
        "then",
        "finally",
        "step 1",
        "step 2",
        "step 3",
        "step a",
        "step b",
        "step c",
    ),
    "split_image_text": (
        "text side",
        "image side",
        "the main message",
        "visual context",
    ),
    "two_up_comparison": (
        "compared with",
        "by contrast",
        "on one side",
        "on the other side",
    ),
    "text_hero_divider": (
        "pause on",
        "single message",
        "transition",
        "section opener",
    ),
    "enumerated_process": (
        "first",
        "then",
        "produces",
        "feeds",
        "launch",
        "iterate",
    ),
    "diagram_driven": (
        "framework",
        "diagram",
        "flow",
        "structure",
        "canvas",
    ),
}

_ORDINAL_RE = re.compile(
    r"(?<![\w$])(?:step\s*)?([1-9]|[a-d])[\).:-]|\b(first|second|third|fourth)\b",
    re.I,
)


class ReadingPathClassificationError(ValueError):
    """Raised when a perceived artifact cannot be deterministically classified."""


class ReadingPathLLMPrimaryError(ValueError):
    """Raised when the live LLM-primary tuple cannot be parsed."""


class _LLMPrimaryTuple(BaseModel):
    """Strict response shape for the live LLM-primary reading-path classifier."""

    model_config = ConfigDict(extra="forbid")

    macro_layout: MacroLayout
    image_role: ImageRoleTier | None = None
    text_substructure: TextSubstructure
    narration_cadence: NarrationCadence
    callout_intent: CalloutIntent | None = None
    rationale: dict[str, str] = Field(default_factory=dict)

    @field_validator("callout_intent", mode="before")
    @classmethod
    def _default_callout_to_none(cls, value: object) -> object:
        if value in ("inform", "none", "null", ""):
            return None
        return value


@dataclass(frozen=True)
class ReadingPathBatchSummary:
    """Observable summary for a deterministic reading-path classify batch."""

    total: int
    counts: dict[str, int]
    default_count: int
    default_ratio: float


@dataclass(frozen=True)
class _TupleClassification:
    reading_path: ReadingPath
    macro_layout: MacroLayout
    text_substructure: TextSubstructure
    narration_cadence: NarrationCadence
    reading_path_flags: list[ReadingPathFlag] | None


@dataclass(frozen=True)
class _Element:
    source_index: int
    key: str
    text: str
    kind: str
    x1: float
    y1: float
    x2: float
    y2: float
    role_tier: ImageRoleTier | None = None
    invalid_role_tier: bool = False

    @property
    def cx(self) -> float:
        return (self.x1 + self.x2) / 2

    @property
    def cy(self) -> float:
        return (self.y1 + self.y2) / 2

    @property
    def area(self) -> float:
        return max(0.0, self.x2 - self.x1) * max(0.0, self.y2 - self.y1)


def cadence_tokens_for_pattern(pattern: str) -> tuple[str, ...]:
    if pattern not in CADENCE_TOKENS:
        raise ReadingPathClassificationError(f"out-of-vocab reading_path: {pattern}")
    return CADENCE_TOKENS[pattern]


def classify_reading_path(artifact: PerceptionArtifact) -> ReadingPath:
    return _classify_tuple(artifact).reading_path


def classify_reading_path_batch(
    artifacts: list[PerceptionArtifact],
) -> ReadingPathBatchSummary:
    patterns = [classify_reading_path(artifact) for artifact in artifacts]
    counts = dict(Counter(patterns))
    total = len(patterns)
    default_count = counts.get("top_down", 0)
    return ReadingPathBatchSummary(
        total=total,
        counts=counts,
        default_count=default_count,
        default_ratio=(default_count / total) if total else 0.0,
    )


def assert_default_ceiling(
    summary: ReadingPathBatchSummary,
    *,
    ceiling: float = 0.25,
) -> None:
    if summary.total and summary.default_ratio > ceiling:
        raise ReadingPathClassificationError(
            f"DEFAULT top_down emissions {summary.default_count}/{summary.total} "
            f"({summary.default_ratio:.2f}) exceed ceiling {ceiling:.2f}"
        )


def _classify_tuple(artifact: PerceptionArtifact) -> _TupleClassification:
    if artifact.coverage != "perceived" or artifact.confidence != "HIGH":
        raise ReadingPathClassificationError(
            "reading_path requires perceived HIGH-confidence artifact"
        )
    elements = _elements(artifact)
    if not elements:
        if not artifact.visual_elements:
            text = _artifact_text(artifact)
            text_substructure = _text_substructure(text, [], "single_text_block")
            return _TupleClassification(
                reading_path=derive_primary_name("single_text_block", text_substructure),
                macro_layout="single_text_block",
                text_substructure=text_substructure,
                narration_cadence=_narration_cadence(text, [], "single_text_block"),
                reading_path_flags=None,
            )
        raise ReadingPathClassificationError(
            f"slide {artifact.slide_id} has no positioned visual_elements for reading_path"
        )
    text = _artifact_text(artifact)
    kinds_text = " ".join(element.kind + " " + element.text for element in elements).lower()

    macro_layout: MacroLayout = "single_text_block"
    if _looks_center_out(elements, kinds_text):
        macro_layout = "center_out"
    elif _looks_instructional_diagram(kinds_text):
        macro_layout = "diagram_driven"
    elif _looks_split_image_text(elements):
        macro_layout = "split_image_text"
    elif _looks_like_grid(kinds_text, elements):
        macro_layout = "card_grid"
    elif _looks_multi_column(elements):
        macro_layout = "multi_column"
    elif _looks_text_hero_divider(elements, kinds_text):
        macro_layout = "text_hero_divider"

    text_substructure = _text_substructure(text, elements, macro_layout)
    narration_cadence = _narration_cadence(text, elements, macro_layout)
    reading_path_flags = _reading_path_flags(elements)
    reading_path = derive_primary_name(macro_layout, text_substructure)
    return _TupleClassification(
        reading_path=reading_path,
        macro_layout=macro_layout,
        text_substructure=text_substructure,
        narration_cadence=narration_cadence,
        reading_path_flags=reading_path_flags,
    )


def ordered_element_keys_for_reading_path(artifact: PerceptionArtifact) -> list[str]:
    elements = _elements(artifact)
    pattern = artifact.reading_path or classify_reading_path(artifact)
    if pattern == "sequence_numbered":
        return [element.key for element in sorted(elements, key=_ordinal_sort_key)]
    if pattern == "enumerated_process":
        return [
            element.key
            for element in sorted(elements, key=lambda item: (_bucket(item.cy), item.x1, item.y1))
        ]
    if pattern == "multi_column":
        return [
            element.key
            for element in sorted(
                elements,
                key=lambda item: (_bucket(item.cx), item.cy, item.cx),
            )
        ]
    if pattern == "center_out":
        return [element.key for element in sorted(elements, key=_center_out_sort_key)]
    if pattern in {"z_pattern", "grid_quadrant"}:
        return [
            element.key
            for element in sorted(
                elements,
                key=lambda item: (_bucket(item.cy), item.cx, item.y1),
            )
        ]
    return [element.key for element in sorted(elements, key=lambda item: (item.y1, item.x1))]


def with_classified_reading_path(artifact: PerceptionArtifact) -> PerceptionArtifact:
    if artifact.coverage != "perceived" or artifact.confidence != "HIGH":
        return artifact
    classified = _classify_tuple(artifact)
    image_roles, image_role_flags = _image_roles(artifact)
    return artifact.model_copy(
        update={
            "reading_path": classified.reading_path,
            "macro_layout": classified.macro_layout,
            "text_substructure": classified.text_substructure,
            "narration_cadence": classified.narration_cadence,
            "image_roles": image_roles,
            "image_role_flags": image_role_flags,
            "callout_intent": None,
            "reading_path_flags": classified.reading_path_flags,
        }
    )


def with_llm_primary_reading_path(artifact: PerceptionArtifact) -> PerceptionArtifact:
    """Populate the authoritative reading-path tuple from one live frontier LLM call.

    Deterministic geometry is retained only as cross-check telemetry. Transport
    and parse failures safe-degrade to the plain top_down tuple instead of
    blocking a production run.
    """
    if artifact.coverage != "perceived" or artifact.confidence != "HIGH":
        return artifact

    geometry_artifact, geometry = _geometry_cross_check(artifact)
    for attempt in range(1, LLM_PRIMARY_ATTEMPTS + 1):
        try:
            result = request_live_reading_path_tuple(geometry_artifact)
            return _apply_llm_primary_tuple(
                geometry_artifact,
                result,
                source="llm_primary",
                degraded=False,
                geometry=geometry,
            )
        except Exception as exc:  # noqa: BLE001 - safe-degrade is intentional.
            if attempt >= LLM_PRIMARY_ATTEMPTS:
                return _safe_default_reading_path(
                    geometry_artifact,
                    geometry=geometry,
                    reason=str(exc),
                )
    return _safe_default_reading_path(
        geometry_artifact,
        geometry=geometry,
        reason="reading-path LLM-primary retry loop exhausted",
    )


def request_live_reading_path_tuple(
    artifact: PerceptionArtifact,
    *,
    model_id: str = LLM_PRIMARY_MODEL_ID,
    timeout_seconds: float = LLM_PRIMARY_TIMEOUT_SECONDS,
) -> _LLMPrimaryTuple:
    """Make the single live gpt-5.5 reading-path tuple classification call."""
    messages = [
        SystemMessage(
            content=(
                "You are the authoritative reading-path classifier for narrated "
                "slide production. Use the catalog definitions exactly. Return "
                "only JSON matching the requested schema."
            )
        ),
        HumanMessage(content=_llm_primary_prompt(artifact)),
    ]
    handle = make_chat_model(
        LLM_PRIMARY_SPECIALIST_ID,
        per_call_override=model_id,
        temperature=0.0,
    )
    response = handle.chat.bind(timeout=timeout_seconds).invoke(messages)
    return parse_live_reading_path_tuple(_decode_content(response))


def parse_live_reading_path_tuple(raw: str) -> _LLMPrimaryTuple:
    """Parse the strict LLM-primary JSON tuple response."""
    try:
        payload = json.loads(_strip_json(raw))
    except ValueError as exc:
        raise ReadingPathLLMPrimaryError(f"reading-path LLM returned non-JSON: {exc}") from exc
    try:
        return _LLMPrimaryTuple.model_validate(payload)
    except ValidationError as exc:
        raise ReadingPathLLMPrimaryError(
            f"reading-path LLM tuple failed validation: {exc}"
        ) from exc


def _geometry_cross_check(
    artifact: PerceptionArtifact,
) -> tuple[PerceptionArtifact, dict[str, Any]]:
    try:
        geometry_artifact = with_classified_reading_path(artifact)
    except ReadingPathClassificationError as exc:
        return artifact, {"error": str(exc)}
    return geometry_artifact, {
        "reading_path": geometry_artifact.reading_path,
        "macro_layout": geometry_artifact.macro_layout,
        "image_roles": geometry_artifact.image_roles,
        "image_role_flags": geometry_artifact.image_role_flags,
        "text_substructure": geometry_artifact.text_substructure,
        "narration_cadence": geometry_artifact.narration_cadence,
        "callout_intent": geometry_artifact.callout_intent,
        "reading_path_flags": geometry_artifact.reading_path_flags,
    }


def _apply_llm_primary_tuple(
    artifact: PerceptionArtifact,
    result: _LLMPrimaryTuple,
    *,
    source: ReadingPathSource,
    degraded: bool,
    geometry: dict[str, Any],
) -> PerceptionArtifact:
    dominant_image_role = result.image_role or _dominant_image_role_from_largest_image(artifact)
    dominant_image_role = _apply_decorative_image_boundary(
        artifact,
        dominant_image_role,
    )
    return artifact.model_copy(
        update={
            "reading_path": derive_primary_name(
                result.macro_layout,
                result.text_substructure,
            ),
            "macro_layout": result.macro_layout,
            "dominant_image_role": dominant_image_role,
            "text_substructure": result.text_substructure,
            "narration_cadence": result.narration_cadence,
            "callout_intent": result.callout_intent,
            "reading_path_source": source,
            "reading_path_degraded": degraded,
            "reading_path_rationale": result.rationale or None,
            "reading_path_geometry": geometry,
        }
    )


def _dominant_image_role_from_largest_image(
    artifact: PerceptionArtifact,
) -> ImageRoleTier | None:
    elements = _elements(artifact)
    image_elements = _image_like_elements(elements)
    if not image_elements:
        return None
    largest = max(image_elements, key=lambda element: element.area)
    return _image_role(largest, elements)


def _apply_decorative_image_boundary(
    artifact: PerceptionArtifact,
    dominant_image_role: ImageRoleTier | None,
) -> ImageRoleTier | None:
    if dominant_image_role not in {"2", "2_5"}:
        return dominant_image_role
    elements = _elements(artifact)
    image_elements = _image_like_elements(elements)
    if not image_elements:
        return dominant_image_role
    largest = max(image_elements, key=lambda element: element.area)
    if _is_plain_unreferenced_mood_image(largest, elements):
        return "1"
    return dominant_image_role


def _image_like_elements(elements: list[_Element]) -> list[_Element]:
    return [element for element in elements if _is_image_like(element)]


def _is_plain_unreferenced_mood_image(
    element: _Element,
    elements: list[_Element],
) -> bool:
    if _is_chart_or_table(element) or _is_diagram(element) or _is_small_icon_or_logo(element):
        return False
    if not _is_photo_or_illustration(element):
        return False
    if _internal_label_count(element, elements) > 0:
        return False
    return not _has_caption(element, elements)


def _safe_default_reading_path(
    artifact: PerceptionArtifact,
    *,
    geometry: dict[str, Any],
    reason: str,
) -> PerceptionArtifact:
    result = _LLMPrimaryTuple(
        macro_layout="single_text_block",
        image_role=None,
        text_substructure="dense_exposition",
        narration_cadence="moderate",
        callout_intent=None,
        rationale={"degraded": reason},
    )
    return _apply_llm_primary_tuple(
        artifact,
        result,
        source="safe_default",
        degraded=True,
        geometry=geometry,
    )


def _llm_primary_prompt(artifact: PerceptionArtifact) -> str:
    return (
        "Classify this perceived slide into the reading-path catalog v1.1 tuple.\n\n"
        "Return EXACTLY this JSON object, with no markdown fences and no prose:\n"
        "{\n"
        '  "macro_layout": "split_image_text|text_hero_divider|multi_column|two_pane|'
        'card_grid|center_out|diagram_driven|single_text_block",\n'
        '  "image_role": "1|2|2_5|3|4" or null,\n'
        '  "text_substructure": "enumerated_process|peer_boxes|comparison_pair|'
        'dense_exposition|hero_message",\n'
        '  "narration_cadence": "sparse_slow|moderate|dense",\n'
        '  "callout_intent": "invite_response|challenge_quiz|directive_cta" or null,\n'
        '  "rationale": {\n'
        '    "macro_layout": "short reason",\n'
        '    "image_role": "short reason",\n'
        '    "text_substructure": "short reason",\n'
        '    "narration_cadence": "short reason",\n'
        '    "callout_intent": "short reason"\n'
        "  }\n"
        "}\n\n"
        "Rules:\n"
        "- Use null for ordinary inform/no-op callout intent.\n"
        "- Do not emit takeaway_imperative or contact; map real CTAs to directive_cta.\n"
        "- image_role is the slide-level dominant role, not a per-element list.\n"
        "- Tier 1 image_role means DECORATIVE or evocative: the image sets tone, "
        "mood, or theme. A rich, prominent, full-bleed photo or illustration is "
        "still tier 1 when it has no internal labels/text, is not a technical or "
        "instructional graphic, and the slide text does not reference it as "
        "content. The narrator should give a tier 1 image no comment.\n"
        "- Tier 2 image_role means ILLUSTRATIVE: the image carries content the "
        "narration may reference because it depicts a specific thing the slide "
        "text or claim points at, but it is not a technical/instructional "
        "diagram needing a walk-through. Do not promote a mood/subject photo to "
        "tier 2 just because it is large. Return tier 2 only when the slide text "
        "explicitly depends on what the image depicts, names it, compares against "
        "it, or the image contains visible content that substantiates the claim. "
        "If uncertain between tier 1 and tier 2, choose tier 1.\n"
        "- Tier 3 image_role means INSTRUCTIONAL: a diagram, canvas, chart, or "
        "framework with internal structure the narrator must walk through.\n"
        "- Tier 4 image_role means POINTER/iconographic: small icons that type "
        "or label a message unit; do not narrate them as images.\n"
        "- When at least one image element exists, do not return null for "
        "image_role; choose the dominant image tier.\n"
        "- Do not use slide_id memorization; reason from the visible artifact and catalog.\n\n"
        f"Catalog context:\n{_catalog_context()}\n\n"
        f"PerceptionArtifact JSON:\n{artifact.model_dump_json()}\n"
    )


def _catalog_context() -> str:
    text = CATALOG_PATH.read_text(encoding="utf-8")
    start = text.find("## 2. THE COMPOSITIONAL TUPLE")
    end = text.find("## 8. BUILD DIRECTIVE")
    if start == -1 or end == -1 or end <= start:
        return text[:12000]
    decision_start = text.find("## 11. HELD-OUT CONFIRM/DENY")
    decision_text = text[decision_start:] if decision_start != -1 else ""
    return f"{text[start:end].strip()}\n\n{decision_text[:6000].strip()}"


def _decode_content(response: object) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                value = block.get("text") or block.get("content")
                if isinstance(value, str):
                    parts.append(value)
        return "".join(parts)
    return str(content)


def _strip_json(raw: str) -> str:
    stripped = raw.strip()
    if "```" in stripped:
        fence = "```json" if "```json" in stripped else "```"
        start = stripped.find(fence) + len(fence)
        end = stripped.find("```", start)
        if end > start:
            stripped = stripped[start:end].strip()
    if not stripped.startswith("{"):
        first = stripped.find("{")
        last = stripped.rfind("}")
        if first != -1 and last > first:
            stripped = stripped[first : last + 1]
    return stripped


def _elements(artifact: PerceptionArtifact) -> list[_Element]:
    parsed: list[_Element] = []
    for index, raw in enumerate(artifact.visual_elements):
        bbox = _bbox(raw)
        if bbox is None:
            continue
        key = _element_key(raw, index)
        text = " ".join(
            str(raw.get(field) or "")
            for field in ("label", "text", "title", "name", "description")
        )
        parsed.append(
            _Element(
                source_index=index,
                key=key,
                text=text.strip(),
                kind=str(raw.get("kind") or raw.get("type") or "").strip(),
                x1=bbox[0],
                y1=bbox[1],
                x2=bbox[2],
                y2=bbox[3],
                role_tier=_role_tier(raw),
                invalid_role_tier=_invalid_role_tier(raw),
            )
        )
    return parsed


def _role_tier(raw: dict[str, Any]) -> ImageRoleTier | None:
    value = raw.get("role_tier")
    if value in {"1", "2", "2_5", "3", "4"}:
        return value  # type: ignore[return-value]
    return None


def _invalid_role_tier(raw: dict[str, Any]) -> bool:
    return (
        "role_tier" in raw
        and raw.get("role_tier") is not None
        and raw.get("role_tier") not in {"1", "2", "2_5", "3", "4"}
    )


def _bbox(raw: dict[str, Any]) -> tuple[float, float, float, float] | None:
    source = raw.get("bbox") or raw.get("bounds") or raw.get("position")
    # P2-4a T11 (party-mode 5/5): non-numeric coordinate entries SKIP (return
    # None) uniformly — matching the structural-mismatch path — rather than
    # raising an uncaught ValueError out of the classifier/vision node.
    try:
        if isinstance(source, dict):
            if {"x", "y", "width", "height"} <= set(source):
                x = float(source["x"])
                y = float(source["y"])
                return _normalize_bbox(
                    (x, y, x + float(source["width"]), y + float(source["height"]))
                )
            keys = ("x1", "y1", "x2", "y2")
            if set(keys) <= set(source):
                return _normalize_bbox(tuple(float(source[key]) for key in keys))  # type: ignore[arg-type]
        if isinstance(source, (list, tuple)) and len(source) == 4:
            return _normalize_bbox(tuple(float(item) for item in source))  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return None
    return None


def _normalize_bbox(source: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = source
    left, right = sorted((x1, x2))
    top, bottom = sorted((y1, y2))
    return (
        _clamp(left),
        _clamp(top),
        _clamp(right),
        _clamp(bottom),
    )


def _clamp(value: float) -> float:
    return min(1.0, max(0.0, value))


def _element_key(raw: dict[str, Any], index: int) -> str:
    for field in ("id", "element_id", "label", "text", "kind"):
        value = str(raw.get(field) or "").strip()
        if value:
            return value
    return f"element-{index + 1}"


def _artifact_text(artifact: PerceptionArtifact) -> str:
    blocks = " ".join(
        item if isinstance(item, str) else " ".join(str(value) for value in item.values())
        for item in artifact.text_blocks
    )
    return " ".join(
        item
        for item in (
            artifact.slide_title,
            artifact.layout_description,
            artifact.extracted_text,
            blocks,
        )
        if item
    )


def _has_element_ordinal(elements: list[_Element]) -> bool:
    return any(_ORDINAL_RE.search(item.text) for item in elements)


def _has_transform_sequence(elements: list[_Element]) -> bool:
    content_elements = [element for element in elements if not _is_connector(element)]
    return len(content_elements) >= 2 and any(_is_connector(element) for element in elements)


def _has_opposition_cue(text: str) -> bool:
    return False
    return bool(
        re.search(
            r"\b(vs|versus|before|after|pro|con|option\s+a|option\s+b)\b|[✓✗]",
            text,
            re.I,
        )
    )


def _reading_path_flags(elements: list[_Element]) -> list[ReadingPathFlag] | None:
    if _has_structural_opposition_cue(elements):
        return ["oppositional_cue"]
    return None


def _image_roles(
    artifact: PerceptionArtifact,
) -> tuple[list[ImageRoleTier | None], list[ImageRoleFlag] | None]:
    elements = _elements(artifact)
    elements_by_index = {element.source_index: element for element in elements}
    roles: list[ImageRoleTier | None] = []
    flags: list[ImageRoleFlag] = []
    for index, raw in enumerate(artifact.visual_elements):
        element = elements_by_index.get(index)
        if element is None:
            roles.append(None)
            if _invalid_role_tier(raw):
                _append_unique(flags, "dropped_invalid_tier")
            continue
        roles.append(_image_role(element, elements))
        if element.invalid_role_tier:
            _append_unique(flags, "dropped_invalid_tier")
    if "2_5" in roles:
        _append_unique(flags, "tier_2_5_candidate")
    if "3" in roles:
        _append_unique(flags, "tier_3_quarantined")
    return roles, flags or None


def _append_unique(flags: list[ImageRoleFlag], flag: ImageRoleFlag) -> None:
    if flag not in flags:
        flags.append(flag)


def _image_role(element: _Element, elements: list[_Element]) -> ImageRoleTier:
    internal_label_count = _internal_label_count(element, elements)
    if _is_small_icon_or_logo(element):
        return "4"
    if element.role_tier == "3" and internal_label_count == 0:
        return _backfill_image_role(element, elements, allow_tier_3=False)
    if element.role_tier in {"1", "2", "2_5", "3", "4"}:
        return element.role_tier
    return _backfill_image_role(
        element,
        elements,
        allow_tier_3=internal_label_count > 0,
    )


def _backfill_image_role(
    element: _Element,
    elements: list[_Element],
    *,
    allow_tier_3: bool,
) -> ImageRoleTier:
    if _is_text(element):
        return "1"
    if _is_decorative(element):
        return "1"
    if (
        _edge_bleed(element)
        and _text_overlaps_image(element, elements)
        and _internal_label_count(element, elements) == 0
    ):
        return "1"
    if element.area < 0.05 and not _has_caption(element, elements):
        return "1"
    if _is_chart_or_table(element) and _has_caption(element, elements):
        return "2_5"
    if (
        allow_tier_3
        and _is_diagram(element)
        and element.area >= 0.25
        and _centrality(element) >= 0.60
    ):
        return "3"
    if _is_photo(element):
        return "2"
    return "2"


def _is_small_icon_or_logo(element: _Element) -> bool:
    return any(token in element.kind.lower() for token in ("icon", "logo")) and element.area < 0.05


def _is_decorative(element: _Element) -> bool:
    content = f"{element.kind} {element.text}".lower()
    return any(token in content for token in ("decorative", "background", "evocative"))


def _is_chart_or_table(element: _Element) -> bool:
    return any(token in element.kind.lower() for token in ("chart", "table"))


def _is_diagram(element: _Element) -> bool:
    return "diagram" in element.kind.lower()


def _is_photo(element: _Element) -> bool:
    return any(token in element.kind.lower() for token in ("photo", "image", "visual"))


def _is_photo_or_illustration(element: _Element) -> bool:
    content = f"{element.kind} {element.text}".lower()
    return any(
        token in content
        for token in ("photo", "photograph", "image", "illustration", "picture")
    )


def _edge_bleed(element: _Element) -> bool:
    return (
        element.x1 <= 0.02
        or element.y1 <= 0.02
        or element.x2 >= 0.98
        or element.y2 >= 0.98
    )


def _text_overlaps_image(element: _Element, elements: list[_Element]) -> bool:
    return any(
        other is not element and _is_text(other) and _overlaps(element, other)
        for other in elements
    )


def _has_caption(element: _Element, elements: list[_Element]) -> bool:
    return any(
        other is not element
        and _is_text(other)
        and _horizontal_overlap(element, other) >= 0.20
        and 0.0 <= other.y1 - element.y2 <= 0.10
        for other in elements
    )


def _internal_label_count(element: _Element, elements: list[_Element]) -> int:
    if not (_is_diagram(element) or _is_chart_or_table(element)):
        return 0
    return sum(
        1
        for other in elements
        if other is not element
        and _is_text(other)
        and _contains(element, other)
        and not _looks_like_caption_for(element, other)
    )


def _looks_like_caption_for(element: _Element, text_element: _Element) -> bool:
    return _horizontal_overlap(element, text_element) >= 0.20 and text_element.y1 >= element.y2


def _contains(outer: _Element, inner: _Element) -> bool:
    return (
        outer.x1 <= inner.x1
        and outer.y1 <= inner.y1
        and outer.x2 >= inner.x2
        and outer.y2 >= inner.y2
    )


def _overlaps(left: _Element, right: _Element) -> bool:
    return not (
        left.x2 <= right.x1
        or right.x2 <= left.x1
        or left.y2 <= right.y1
        or right.y2 <= left.y1
    )


def _horizontal_overlap(left: _Element, right: _Element) -> float:
    width = max(0.001, min(left.x2 - left.x1, right.x2 - right.x1))
    overlap = max(0.0, min(left.x2, right.x2) - max(left.x1, right.x1))
    return overlap / width


def _centrality(element: _Element) -> float:
    distance = ((element.cx - 0.5) ** 2 + (element.cy - 0.5) ** 2) ** 0.5
    return max(0.0, 1.0 - (distance / 0.7072))


def _has_structural_opposition_cue(elements: list[_Element]) -> bool:
    if len(elements) < 2:
        return False
    tokens_by_element = [_opposition_tokens(element) for element in elements]
    return (
        _paired_token(tokens_by_element, "before", "after")
        or _paired_token(tokens_by_element, "pro", "con")
        or _paired_token(tokens_by_element, "option_a", "option_b")
        or _paired_token(tokens_by_element, "check", "cross")
        or _has_between_element_versus(elements)
    )


def _paired_token(token_sets: list[set[str]], first: str, second: str) -> bool:
    first_indexes = {index for index, tokens in enumerate(token_sets) if first in tokens}
    second_indexes = {index for index, tokens in enumerate(token_sets) if second in tokens}
    return any(left != right for left in first_indexes for right in second_indexes)


def _has_between_element_versus(elements: list[_Element]) -> bool:
    cue_elements = [
        element
        for element in elements
        if re.search(r"\b(?:vs|versus)\b", element.text, re.I)
        and len(re.findall(r"\b\w+\b", element.text)) <= 2
    ]
    return bool(cue_elements) and len(elements) >= 3


def _opposition_tokens(element: _Element) -> set[str]:
    text = element.text
    tokens: set[str] = set()
    if re.search(r"\bbefore\b", text, re.I):
        tokens.add("before")
    if re.search(r"\bafter\b", text, re.I):
        tokens.add("after")
    if re.search(r"\bpro\b", text, re.I):
        tokens.add("pro")
    if re.search(r"\bcon\b", text, re.I):
        tokens.add("con")
    if re.search(r"\boption\s*a\b", text, re.I):
        tokens.add("option_a")
    if re.search(r"\boption\s*b\b", text, re.I):
        tokens.add("option_b")
    if any(mark in text for mark in ("✓", "✔")):
        tokens.add("check")
    if any(mark in text for mark in ("✕", "✗", "✘")):
        tokens.add("cross")
    return tokens


def _text_substructure(
    text: str,
    elements: list[_Element],
    macro_layout: MacroLayout,
) -> TextSubstructure:
    if _has_transform_sequence(elements):
        return "enumerated_process"
    if macro_layout in {"multi_column", "card_grid"} or _has_element_ordinal(elements):
        return "peer_boxes"
    if _text_word_count(text, elements) <= 12:
        return "hero_message"
    return "dense_exposition"


def _narration_cadence(
    text: str,
    elements: list[_Element],
    macro_layout: MacroLayout,
) -> NarrationCadence:
    if macro_layout == "text_hero_divider":
        return "sparse_slow"
    if _text_word_count(text, elements) >= 45 or len(elements) >= 6:
        return "dense"
    return "moderate"


def _looks_like_grid(kinds_text: str, elements: list[_Element]) -> bool:
    return any(
        token in kinds_text for token in ("grid", "matrix", "quadrant", "axis")
    ) and _two_by_two(elements)


def _looks_center_out(elements: list[_Element], kinds_text: str) -> bool:
    if any(token in kinds_text for token in ("center", "hero", "radial", "orbit")):
        return any(0.35 <= item.cx <= 0.65 and 0.35 <= item.cy <= 0.65 for item in elements)
    return False


def _looks_multi_column(elements: list[_Element]) -> bool:
    if len(elements) < 2 or _has_large_visual(elements):
        return False
    if _has_element_ordinal(elements) and not _has_transform_sequence(elements):
        return False
    buckets: dict[int, int] = {}
    for element in elements:
        buckets[_bucket(element.cx)] = buckets.get(_bucket(element.cx), 0) + 1
    return len(buckets) >= 2


def _is_connector(element: _Element) -> bool:
    text = f"{element.kind} {element.text}".lower()
    return any(token in text for token in ("arrow", "connector", "flowline"))


def _two_by_two(elements: list[_Element]) -> bool:
    if len(elements) < 4:
        return False
    xs = {_bucket(item.cx) for item in elements}
    ys = {_bucket(item.cy) for item in elements}
    return len(xs) >= 2 and len(ys) >= 2


def _bucket(value: float) -> int:
    return min(2, max(0, int(_clamp(value) * 3)))


def _ordinal_sort_key(element: _Element) -> tuple[int, float, float]:
    match = _ORDINAL_RE.search(element.text)
    if match:
        token = (match.group(1) or match.group(2) or "").lower()
        ordinal = {
            "1": 1,
            "a": 1,
            "first": 1,
            "2": 2,
            "b": 2,
            "second": 2,
            "3": 3,
            "c": 3,
            "third": 3,
            "4": 4,
            "d": 4,
            "fourth": 4,
        }.get(token, 99)
        return (ordinal, element.y1, element.x1)
    return (99, element.y1, element.x1)


def _center_out_sort_key(element: _Element) -> tuple[float, float]:
    distance = ((element.cx - 0.5) ** 2 + (element.cy - 0.5) ** 2) ** 0.5
    return (distance, element.cy)


def _looks_split_image_text(elements: list[_Element]) -> bool:
    visuals = [element for element in elements if _is_visual(element) and element.area >= 0.10]
    texts = [element for element in elements if _is_text(element)]
    if not visuals or not texts:
        return False
    largest_visual = max(visuals, key=lambda item: item.area)
    text_center = sum(item.cx for item in texts) / len(texts)
    return abs(largest_visual.cx - text_center) >= 0.25


def _looks_text_hero_divider(elements: list[_Element], kinds_text: str) -> bool:
    if any(token in kinds_text for token in ("section opener", "divider", "poster", "cta")):
        return len(elements) <= 3
    text_elements = [element for element in elements if _is_text(element)]
    return (
        len(elements) == 1
        and bool(text_elements)
        and ("headline" in text_elements[0].kind.lower() or text_elements[0].area >= 0.35)
    )


def _looks_instructional_diagram(kinds_text: str) -> bool:
    if "diagram" not in kinds_text:
        return False
    blocked = ("decorative", "background", "illustrative", "semi-transparent")
    if any(token in kinds_text for token in blocked):
        return False
    return any(token in kinds_text for token in ("framework", "flow", "canvas", "load-bearing"))


def _has_large_visual(elements: list[_Element]) -> bool:
    return any(_is_visual(element) and element.area >= 0.16 for element in elements)


def _is_visual(element: _Element) -> bool:
    return any(
        token in element.kind.lower()
        for token in ("image", "visual", "photo", "diagram", "chart", "graphic")
    )


def _is_image_like(element: _Element) -> bool:
    return any(
        token in (element.kind + " " + element.text).lower()
        for token in (
            "image",
            "visual",
            "photo",
            "illustration",
            "picture",
            "graphic",
            "diagram",
            "chart",
            "figure",
        )
    )


def _is_text(element: _Element) -> bool:
    return any(
        token in (element.kind + " " + element.text).lower()
        for token in ("text", "headline", "title", "copy", "callout", "step", "box", "caption")
    )


def _text_word_count(text: str, elements: list[_Element]) -> int:
    joined = " ".join([text, *(element.text for element in elements)])
    return len(re.findall(r"\b\w+\b", joined))
