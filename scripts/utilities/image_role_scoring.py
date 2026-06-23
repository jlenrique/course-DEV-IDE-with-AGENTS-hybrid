"""Scoring helpers for S2 image role tier agreement."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.models.perception.perception_artifact import ImageRoleTier

ScoredImageRoleTier = Literal["1", "2", "4"]
SCORED_TIERS: tuple[ScoredImageRoleTier, ...] = ("1", "2", "4")


@dataclass(frozen=True)
class ImageRoleAgreementReport:
    """Agreement report over folded scored tiers."""

    kappa: float
    soft_middle_kappa: float
    confusion_matrix: dict[str, dict[str, int]]
    quarantined_count: int
    candidate_count: int
    tier3_disagreement: int
    scored_pair_count: int
    insufficient_data: bool
    passes: bool


def fold_scored_tier(tier: ImageRoleTier | str) -> ScoredImageRoleTier | None:
    """Fold tier 2.5 into 2 and exclude quarantined tier 3 from scored top-1."""
    if tier == "2_5":
        return "2"
    if tier == "3":
        return None
    if tier in SCORED_TIERS:
        return tier  # type: ignore[return-value]
    raise ValueError(f"out-of-vocab image role tier: {tier!r}")


def score_image_role_agreement(
    labels_a: list[ImageRoleTier | str],
    labels_b: list[ImageRoleTier | str],
    *,
    threshold: float = 0.6,
) -> ImageRoleAgreementReport:
    """Compute Cohen's kappa over scored tiers plus the S2 soft-middle gate."""
    if len(labels_a) != len(labels_b):
        raise ValueError("image role agreement requires equal-length label lists")
    scored_pairs: list[tuple[ScoredImageRoleTier, ScoredImageRoleTier]] = []
    quarantined = 0
    candidates = 0
    tier3_disagreement = 0
    for left, right in zip(labels_a, labels_b, strict=True):
        if left == "2_5" or right == "2_5":
            candidates += 1
        left_folded = fold_scored_tier(left)
        right_folded = fold_scored_tier(right)
        if left_folded is None or right_folded is None:
            quarantined += 1
            if left != right:
                tier3_disagreement += 1
            continue
        scored_pairs.append((left_folded, right_folded))

    matrix = _confusion_matrix(scored_pairs)
    kappa = _cohens_kappa(scored_pairs, labels=SCORED_TIERS)
    soft_pairs = [
        pair for pair in scored_pairs if pair[0] in {"1", "2"} and pair[1] in {"1", "2"}
    ]
    soft_middle = _cohens_kappa(soft_pairs, labels=("1", "2"))
    insufficient_data = not scored_pairs
    return ImageRoleAgreementReport(
        kappa=kappa,
        soft_middle_kappa=soft_middle,
        confusion_matrix=matrix,
        quarantined_count=quarantined,
        candidate_count=candidates,
        tier3_disagreement=tier3_disagreement,
        scored_pair_count=len(scored_pairs),
        insufficient_data=insufficient_data,
        passes=(
            not insufficient_data
            and tier3_disagreement == 0
            and kappa >= threshold
            and soft_middle >= threshold
        ),
    )


def tier_rubric_metadata() -> dict[str, dict[str, object]]:
    """Return provenance metadata for the S2 role-tier rubric artifact."""
    return {
        "1": {
            "name": "decorative/evocative",
            "eye_verb": "feel",
            "exemplar_count": 26,
            "sources": ["reviewed-catalog", "held-out-fixtures"],
            "retest_marker": "confirmed",
        },
        "2": {
            "name": "illustrative/supporting",
            "eye_verb": "glance",
            "exemplar_count": 26,
            "sources": ["reviewed-catalog", "held-out-fixtures"],
            "retest_marker": "confirmed",
        },
        "2_5": {
            "name": "evidentiary/exhibit",
            "eye_verb": "confirm",
            "exemplar_count": 0,
            "sources": ["S2-harvest-candidate"],
            "retest_marker": "provisional",
        },
        "3": {
            "name": "instructional/technical",
            "eye_verb": "trace",
            "exemplar_count": 0,
            "sources": ["S2-quarantine", "12_Value-Prop-Canvas-probe"],
            "retest_marker": "provisional",
        },
        "4": {
            "name": "pointer/iconographic",
            "eye_verb": "tag",
            "exemplar_count": 26,
            "sources": ["reviewed-catalog", "held-out-fixtures"],
            "retest_marker": "confirmed",
        },
    }


def _confusion_matrix(
    pairs: list[tuple[ScoredImageRoleTier, ScoredImageRoleTier]]
) -> dict[str, dict[str, int]]:
    return {
        expected: {
            actual: sum(1 for pair in pairs if pair == (expected, actual))
            for actual in SCORED_TIERS
        }
        for expected in SCORED_TIERS
    }


def _cohens_kappa(
    pairs: list[tuple[ScoredImageRoleTier, ScoredImageRoleTier]],
    *,
    labels: tuple[str, ...],
) -> float:
    total = len(pairs)
    if total == 0:
        return 0.0
    observed = sum(1 for left, right in pairs if left == right) / total
    left_counts = {label: sum(1 for left, _right in pairs if left == label) for label in labels}
    right_counts = {label: sum(1 for _left, right in pairs if right == label) for label in labels}
    expected = sum(left_counts[label] * right_counts[label] for label in labels) / (total * total)
    if expected == 1.0:
        return 1.0 if observed == 1.0 else 0.0
    return (observed - expected) / (1.0 - expected)


__all__ = [
    "ImageRoleAgreementReport",
    "SCORED_TIERS",
    "fold_scored_tier",
    "score_image_role_agreement",
    "tier_rubric_metadata",
]
