"""Deterministic narration-to-perception fidelity checks for Quinn-R G5."""

from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import ValidationError

from app.models.perception import PerceptionArtifact
from app.specialists.quinn_r.quality_control_dispatch import FidelityError

ReferenceClass = Literal["fidelity-bearing", "non-visual"]

ORPHAN_TAG = "quinn_r.g5.fidelity-orphan-reference"
FIGURE_TAG = "quinn_r.g5.fidelity-figure-contradiction"

_FIGURE_RE = re.compile(
    r"\$\s*\d+(?:\.\d+)?\s*(?:t|trillion|b|billion)?|\b\d+(?:\.\d+)?\s*%|\b\d+(?:\.\d+)?x\b",
    re.IGNORECASE,
)
# Blind-Hunter MEDIUM (T11): bare single words ("bar", "line", "building", "stat",
# "image") trip a BLOCKING check on idioms ("raise the bar", "bottom line"). For a
# Class-A gate, false positives are poison (Murat: stuck-alarm). Triggers are
# restricted to specific multi-word visual phrases + low-idiom-risk single words.
_VISUAL_GROUPS: dict[str, tuple[str, ...]] = {
    "bar": ("bar chart", "bar graph", "paired bars"),
    "callout": ("stat callout", "stat callouts", "callouts", "callout"),
    "diagram": ("diagram", "process diagram"),
    "image": ("clinic image", "building photo", "photo"),
    "line": ("line chart", "line graph", "trend line", "upward line"),
    # "table" dropped: no reliable multi-word form and bare "table" is idiomatic
    # ("table the discussion"); a blocking gate must not fire on idioms.
}
_TERM_RE = {
    group: tuple(
        re.compile(rf"(?<![A-Za-z0-9]){re.escape(term)}(?![A-Za-z0-9])", re.IGNORECASE)
        for term in terms
    )
    for group, terms in _VISUAL_GROUPS.items()
}


def classify_fidelity_reference(text: str) -> ReferenceClass:
    """Classify whether narration makes a visual/figure claim."""

    candidate = str(text or "")
    if _FIGURE_RE.search(candidate):
        return "fidelity-bearing"
    return "fidelity-bearing" if _referenced_visual_groups(candidate) else "non-visual"


def detect_fidelity(
    narration_segments: list[dict[str, Any]], perception_artifacts: Any
) -> dict[str, Any]:
    """Raise FidelityError on narration claims unsupported by perception."""

    artifacts = _artifact_map(perception_artifacts)
    evaluated = 0
    for segment in narration_segments or []:
        if not isinstance(segment, dict):
            continue
        text = str(segment.get("text") or segment.get("narration_text") or "").strip()
        if not text:
            continue
        slide_id = str(segment.get("slide_id") or "").strip()
        artifact = artifacts.get(slide_id)
        if artifact is None:
            raise FidelityError(
                f"missing perception artifact for slide {slide_id or '<unknown>'}",
                tag=ORPHAN_TAG,
            )
        _assert_perceived(artifact)
        evaluated += 1
        perceived = _artifact_text(artifact)
        missing_groups = sorted(
            group
            for group in _referenced_visual_groups(text)
            if not _group_present(group, perceived)
        )
        if missing_groups:
            raise FidelityError(
                "slide "
                f"{slide_id} narration references unsupported visual elements: {missing_groups}",
                tag=ORPHAN_TAG,
            )
        missing_figures = sorted(_figures(text) - _figures(perceived))
        if missing_figures:
            raise FidelityError(
                f"slide {slide_id} narration figures not present in perception: {missing_figures}",
                tag=FIGURE_TAG,
            )
    return {"blocking": [], "evaluated_segments": evaluated}


def _artifact_map(perception_artifacts: Any) -> dict[str, PerceptionArtifact]:
    raw = perception_artifacts
    if isinstance(raw, dict):
        if "perception_artifacts" in raw:
            raw = raw["perception_artifacts"]
        elif "slide_id" in raw:  # a single artifact dict, not a wrapper/map
            raw = [raw]
        else:  # slide_id -> artifact map
            raw = list(raw.values())
    if not isinstance(raw, list) or not raw:
        raise FidelityError("G5 fidelity check requires perception_artifacts", tag=ORPHAN_TAG)
    try:
        artifacts = [PerceptionArtifact.model_validate(item) for item in raw]
    except ValidationError as exc:  # schema drift surfaces as a tagged, error-pause-able fail
        raise FidelityError(
            f"perception artifact failed validation: {exc}", tag=ORPHAN_TAG
        ) from exc
    mapping: dict[str, PerceptionArtifact] = {}
    for artifact in artifacts:
        if artifact.slide_id in mapping:  # silent last-wins would mask a real conflict
            raise FidelityError(
                f"duplicate perception artifact for slide {artifact.slide_id}", tag=ORPHAN_TAG
            )
        mapping[artifact.slide_id] = artifact
    return mapping


def _assert_perceived(artifact: PerceptionArtifact) -> None:
    if artifact.coverage != "perceived" or artifact.confidence != "HIGH":
        raise FidelityError(
            f"slide {artifact.slide_id} perception is not high-confidence perceived evidence",
            tag=ORPHAN_TAG,
        )


def _artifact_text(artifact: PerceptionArtifact) -> str:
    values: list[str] = [
        artifact.extracted_text,
        artifact.layout_description,
        artifact.slide_title,
        artifact.artifact_path,
    ]
    for block in artifact.text_blocks:
        values.append(_stringify(block))
    for element in artifact.visual_elements:
        values.append(_stringify(element))
    return " ".join(value for value in values if value)


def _stringify(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(_stringify(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_stringify(item) for item in value)
    return str(value or "")


def _referenced_visual_groups(text: str) -> set[str]:
    return {
        group
        for group, patterns in _TERM_RE.items()
        if any(pattern.search(text) for pattern in patterns)
    }


def _group_present(group: str, perceived_text: str) -> bool:
    return any(pattern.search(perceived_text) for pattern in _TERM_RE[group])


def _figures(text: str) -> set[str]:
    return {_normalize_figure(match.group(0)) for match in _FIGURE_RE.finditer(text)}


def _normalize_figure(value: str) -> str:
    token = value.lower().replace(" ", "")
    if token.startswith("$"):
        number = float(re.search(r"\d+(?:\.\d+)?", token).group(0))  # type: ignore[union-attr]
        # Blind-Hunter CRITICAL (T11): only normalize to trillions when a unit is
        # PRESENT. A bare "$5" must NOT collapse onto "$5 trillion" — they are
        # different magnitudes; conflating them is a silent wrong-answer.
        if "trillion" in token or token.endswith("t"):
            return f"money-trillion:{number:g}"
        if "billion" in token or token.endswith("b"):
            return f"money-trillion:{number / 1000.0:g}"
        return f"money-bare:{number:g}"
    if token.endswith("%"):
        return f"percent:{float(token[:-1]):g}"
    if token.endswith("x"):
        return f"multiple:{float(token[:-1]):g}"
    return token


__all__ = ["classify_fidelity_reference", "detect_fidelity"]
