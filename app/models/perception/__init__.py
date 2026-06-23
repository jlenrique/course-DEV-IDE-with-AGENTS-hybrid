"""Perception artifact contracts consumed by downstream QA gates."""

from app.models.perception.perception_artifact import (
    CalloutIntent,
    Confidence,
    CoverageState,
    ImageRoleFlag,
    ImageRoleTier,
    MacroLayout,
    NarrationCadence,
    PerceptionArtifact,
    PerceptionProvenance,
    ReadingPath,
    ReadingPathFlag,
    ReadingPathSource,
    RoleTier,
    TextSubstructure,
)

__all__ = [
    "CalloutIntent",
    "Confidence",
    "CoverageState",
    "ImageRoleFlag",
    "ImageRoleTier",
    "MacroLayout",
    "NarrationCadence",
    "PerceptionArtifact",
    "PerceptionProvenance",
    "ReadingPath",
    "ReadingPathFlag",
    "ReadingPathSource",
    "RoleTier",
    "TextSubstructure",
]
