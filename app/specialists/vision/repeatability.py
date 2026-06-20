"""Offline repeatability comparator for P2-2 golden perception artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

REPEATABILITY_THRESHOLDS: dict[str, float] = {
    "bbox_iou_min": 0.90,
    "text_edit_distance_max": 8.0,
    "element_jaccard_min": 1.0,
}


@dataclass(frozen=True)
class RepeatabilityVerdict:
    stable: bool
    reasons: list[str]
    thresholds: dict[str, float]


def compare_artifacts(left: dict[str, Any], right: dict[str, Any]) -> RepeatabilityVerdict:
    """Compare two serialized provider responses against calibrated thresholds."""

    reasons: list[str] = []
    left_elements = _element_set(left)
    right_elements = _element_set(right)
    element_jaccard = _jaccard(left_elements, right_elements)
    if element_jaccard < REPEATABILITY_THRESHOLDS["element_jaccard_min"]:
        reasons.append(f"element_jaccard={element_jaccard:.3f}")
    edit_distance = _levenshtein(
        str(left.get("extracted_text") or ""),
        str(right.get("extracted_text") or ""),
    )
    if edit_distance > REPEATABILITY_THRESHOLDS["text_edit_distance_max"]:
        reasons.append(f"text_edit_distance={edit_distance}")
    for index, (left_box, right_box) in enumerate(zip(_bboxes(left), _bboxes(right), strict=False)):
        iou = _iou(left_box, right_box)
        if iou < REPEATABILITY_THRESHOLDS["bbox_iou_min"]:
            reasons.append(f"bbox_iou[{index}]={iou:.3f}")
    return RepeatabilityVerdict(
        stable=not reasons,
        reasons=reasons,
        thresholds=dict(REPEATABILITY_THRESHOLDS),
    )


def _element_set(payload: dict[str, Any]) -> set[tuple[str, str]]:
    values = set()
    for row in payload.get("visual_elements") or []:
        if isinstance(row, dict):
            values.add((str(row.get("kind") or ""), str(row.get("text") or "")))
    return values


def _jaccard(left: set[tuple[str, str]], right: set[tuple[str, str]]) -> float:
    if not left and not right:
        return 1.0
    return len(left & right) / len(left | right)


def _bboxes(payload: dict[str, Any]) -> list[tuple[float, float, float, float]]:
    boxes = []
    for row in payload.get("visual_elements") or []:
        if isinstance(row, dict) and isinstance(row.get("bbox"), list) and len(row["bbox"]) == 4:
            boxes.append(tuple(float(v) for v in row["bbox"]))
    return boxes


def _iou(
    left: tuple[float, float, float, float],
    right: tuple[float, float, float, float],
) -> float:
    lx1, ly1, lx2, ly2 = left
    rx1, ry1, rx2, ry2 = right
    ix1, iy1 = max(lx1, rx1), max(ly1, ry1)
    ix2, iy2 = min(lx2, rx2), min(ly2, ry2)
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    left_area = max(0.0, lx2 - lx1) * max(0.0, ly2 - ly1)
    right_area = max(0.0, rx2 - rx1) * max(0.0, ry2 - ry1)
    union = left_area + right_area - inter
    return 1.0 if union == 0 else inter / union


def _levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for i, l_char in enumerate(left, start=1):
        current = [i]
        for j, r_char in enumerate(right, start=1):
            current.append(
                min(
                    previous[j] + 1,
                    current[j - 1] + 1,
                    previous[j - 1] + (0 if l_char == r_char else 1),
                )
            )
        previous = current
    return previous[-1]


__all__ = ["REPEATABILITY_THRESHOLDS", "RepeatabilityVerdict", "compare_artifacts"]
