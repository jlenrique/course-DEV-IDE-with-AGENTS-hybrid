"""Deterministic reading-path classification over rich perception artifacts."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

from app.models.perception.perception_artifact import (
    MacroLayout,
    NarrationCadence,
    PerceptionArtifact,
    ReadingPath,
    ReadingPathFlag,
    TextSubstructure,
)
from scripts.utilities.reading_path_derivation import derive_primary_name

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
    return artifact.model_copy(
        update={
            "reading_path": classified.reading_path,
            "macro_layout": classified.macro_layout,
            "text_substructure": classified.text_substructure,
            "narration_cadence": classified.narration_cadence,
            "image_roles": None,
            "callout_intent": None,
            "reading_path_flags": classified.reading_path_flags,
        }
    )


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


def _is_text(element: _Element) -> bool:
    return any(
        token in (element.kind + " " + element.text).lower()
        for token in ("text", "headline", "title", "copy", "callout", "step", "box")
    )


def _text_word_count(text: str, elements: list[_Element]) -> int:
    joined = " ".join([text, *(element.text for element in elements)])
    return len(re.findall(r"\b\w+\b", joined))
