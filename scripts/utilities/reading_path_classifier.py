"""Deterministic reading-path classification over rich perception artifacts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.models.perception.perception_artifact import PerceptionArtifact, ReadingPath

READING_PATH_PATTERNS: tuple[str, ...] = (
    "z_pattern",
    "f_pattern",
    "center_out",
    "top_down",
    "multi_column",
    "grid_quadrant",
    "sequence_numbered",
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
}

_SCORERS: dict[str, str] = {pattern: pattern for pattern in READING_PATH_PATTERNS}
_ORDINAL_RE = re.compile(
    r"(?<![\w$])(?:step\s*)?([1-9]|[a-d])[\).:-]|\b(first|second|third|fourth)\b",
    re.I,
)


class ReadingPathClassificationError(ValueError):
    """Raised when a perceived artifact cannot be deterministically classified."""


@dataclass(frozen=True)
class _Element:
    key: str
    text: str
    kind: str
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def cx(self) -> float:
        return (self.x1 + self.x2) / 2

    @property
    def cy(self) -> float:
        return (self.y1 + self.y2) / 2


def cadence_tokens_for_pattern(pattern: str) -> tuple[str, ...]:
    if pattern not in CADENCE_TOKENS:
        raise ReadingPathClassificationError(f"out-of-vocab reading_path: {pattern}")
    return CADENCE_TOKENS[pattern]


def classify_reading_path(artifact: PerceptionArtifact) -> ReadingPath:
    if artifact.coverage != "perceived" or artifact.confidence != "HIGH":
        raise ReadingPathClassificationError(
            "reading_path requires perceived HIGH-confidence artifact"
        )
    elements = _elements(artifact)
    text = _artifact_text(artifact)
    if _has_ordinal(text, elements):
        return "sequence_numbered"
    if not elements:
        raise ReadingPathClassificationError(
            f"slide {artifact.slide_id} has no positioned visual_elements for reading_path"
        )
    kinds_text = " ".join(element.kind + " " + element.text for element in elements).lower()
    if _looks_like_grid(kinds_text, elements):
        return "grid_quadrant"
    if _looks_center_out(elements, kinds_text):
        return "center_out"
    if _looks_z(elements, kinds_text):
        return "z_pattern"
    if _looks_multi_column(elements):
        return "multi_column"
    if _looks_f_pattern(elements, kinds_text):
        return "f_pattern"
    return "top_down"


def ordered_element_keys_for_reading_path(artifact: PerceptionArtifact) -> list[str]:
    elements = _elements(artifact)
    pattern = artifact.reading_path or classify_reading_path(artifact)
    if pattern == "sequence_numbered":
        return [element.key for element in sorted(elements, key=_ordinal_sort_key)]
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
    return artifact.model_copy(update={"reading_path": classify_reading_path(artifact)})


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
                key=key,
                text=text.strip(),
                kind=str(raw.get("kind") or raw.get("type") or "").strip(),
                x1=bbox[0],
                y1=bbox[1],
                x2=bbox[2],
                y2=bbox[3],
            )
        )
    return parsed


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
                return (x, y, x + float(source["width"]), y + float(source["height"]))
            keys = ("x1", "y1", "x2", "y2")
            if set(keys) <= set(source):
                return tuple(float(source[key]) for key in keys)  # type: ignore[return-value]
        if isinstance(source, (list, tuple)) and len(source) == 4:
            return tuple(float(item) for item in source)  # type: ignore[return-value]
    except (ValueError, TypeError):
        return None
    return None


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


def _has_ordinal(text: str, elements: list[_Element]) -> bool:
    return bool(_ORDINAL_RE.search(text)) or any(_ORDINAL_RE.search(item.text) for item in elements)


def _looks_like_grid(kinds_text: str, elements: list[_Element]) -> bool:
    return any(
        token in kinds_text for token in ("grid", "matrix", "quadrant", "axis")
    ) and _two_by_two(elements)


def _looks_center_out(elements: list[_Element], kinds_text: str) -> bool:
    if any(token in kinds_text for token in ("center", "hero", "radial", "orbit")):
        return any(0.35 <= item.cx <= 0.65 and 0.35 <= item.cy <= 0.65 for item in elements)
    return False


def _looks_z(elements: list[_Element], kinds_text: str) -> bool:
    if not _two_by_two(elements):
        return False
    return any(token in kinds_text for token in ("headline", "hero", "cta", "callout", "body"))


def _looks_multi_column(elements: list[_Element]) -> bool:
    if len(elements) < 4:
        return False
    buckets: dict[int, int] = {}
    for element in elements:
        buckets[_bucket(element.cx)] = buckets.get(_bucket(element.cx), 0) + 1
    return len(buckets) >= 2 and max(buckets.values()) >= 2


def _looks_f_pattern(elements: list[_Element], kinds_text: str) -> bool:
    if any(token in kinds_text for token in ("callout", "evidence", "note", "margin")):
        left = [item for item in elements if item.cx < 0.55]
        right = [item for item in elements if item.cx >= 0.55]
        return len(left) >= 2 and bool(right)
    return False


def _two_by_two(elements: list[_Element]) -> bool:
    if len(elements) < 4:
        return False
    xs = {_bucket(item.cx) for item in elements}
    ys = {_bucket(item.cy) for item in elements}
    return len(xs) >= 2 and len(ys) >= 2


def _bucket(value: float) -> int:
    return int(value * 3)


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
