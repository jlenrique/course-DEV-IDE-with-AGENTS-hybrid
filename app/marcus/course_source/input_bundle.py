"""Lesson-planning input bundle prototype for course-source material."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Self

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.marcus.course_source.asset_records import (
    AssetSourceRef,
    CanonicalAssetRecord,
    emit_requirement_gap_records,
)
from app.marcus.course_source.manifest_scan import scan_course
from app.marcus.course_source.models import GapEntry, SourceManifest, SourcePurpose
from app.marcus.course_source.registry import load_course
from app.marcus.course_source.syllabus_metadata import (
    CourseMetadataProposal,
    ModuleMetadataProposal,
)
from app.models.state.component_selection import ComponentSelection

SCHEMA_VERSION = "0.1"


class CoursePlanningProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    course_id: str
    code: str
    title: str
    sme_name: str
    source_purpose: SourcePurpose
    source_availability: tuple[dict[str, object], ...] = Field(default_factory=tuple)


class ModulePlanningProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    module_id: str
    container_title: str
    proposal_status: str
    proposed_slug: str | None = None
    proposed_title: str | None = None
    topics: tuple[str, ...] = Field(default_factory=tuple)
    source_bucket_suggestions: tuple[str, ...] = Field(default_factory=tuple)


class StyleguideResolution(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    sme_name: str
    sme_key: str | None = None
    styleguide_id: str | None = None
    attribution: str = ""
    approval_route: str = ""
    voice_profile_ref: str = ""
    fallback: bool = False
    reason: str = ""


class LessonPlanningInputBundle(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    schema_version: Literal["0.1"] = SCHEMA_VERSION
    course: CoursePlanningProfile
    module: ModulePlanningProfile
    learner_profile: str | None = None
    course_learning_objectives: tuple[dict[str, object], ...] = Field(default_factory=tuple)
    module_learning_objectives: tuple[dict[str, object], ...] = Field(default_factory=tuple)
    scoped_source_manifest: SourceManifest
    asset_records: tuple[CanonicalAssetRecord, ...] = Field(default_factory=tuple)
    gap_ledger: tuple[GapEntry, ...] = Field(default_factory=tuple)
    operator_focus: str
    workflow_capabilities: tuple[str, ...] = Field(default=("deck", "motion", "workbook"))
    component_selection: ComponentSelection = Field(
        default_factory=ComponentSelection.production_default
    )
    styleguide_resolution: StyleguideResolution

    def model_copy(
        self,
        *,
        update: dict[str, Any] | None = None,
        deep: bool = False,
    ) -> Self:
        data = self.model_dump(mode="python")
        if update:
            data.update(update)
        return type(self).model_validate(data)

    @model_validator(mode="after")
    def _scope_and_gap_contract(self) -> LessonPlanningInputBundle:
        if not self.gap_ledger:
            raise ValueError("lesson-planning input bundle requires gap_ledger")
        if not self.asset_records:
            raise ValueError("lesson-planning input bundle requires asset_records")
        if "deck" not in self.workflow_capabilities:
            raise ValueError("workflow_capabilities must include deck")
        unknown = set(self.workflow_capabilities) - set(ComponentSelection.COMPONENTS)
        if unknown:
            raise ValueError(f"unknown workflow capabilities: {sorted(unknown)}")
        return self


def load_module_metadata_proposal(path: Path) -> CourseMetadataProposal:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return CourseMetadataProposal.model_validate(data)


def render_input_bundle_yaml(bundle: LessonPlanningInputBundle) -> str:
    return yaml.safe_dump(bundle.model_dump(mode="json"), sort_keys=False, allow_unicode=True)


def load_input_bundle(path: Path) -> LessonPlanningInputBundle:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return LessonPlanningInputBundle.model_validate(data)


def write_input_bundle(bundle: LessonPlanningInputBundle, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_input_bundle_yaml(bundle), encoding="utf-8")
    return path


def _module_yaml_title(course_root: Path, module_id: str) -> str:
    module_yaml = course_root / "modules" / module_id / "module.yaml"
    data = yaml.safe_load(module_yaml.read_text(encoding="utf-8"))
    return str(data.get("title") or "")


def _proposal_module(
    proposal: CourseMetadataProposal,
    module_id: str,
) -> ModuleMetadataProposal:
    for module in proposal.modules:
        if module.module_id == module_id:
            return module
    raise ValueError(f"module proposal not found: {module_id}")


def _module_profile(
    course_root: Path,
    proposal: CourseMetadataProposal,
    module_id: str,
) -> ModulePlanningProfile:
    module = _proposal_module(proposal, module_id)
    return ModulePlanningProfile(
        module_id=module_id,
        container_title=_module_yaml_title(course_root, module_id),
        proposal_status=module.status,
        proposed_slug=module.proposed_slug.value if module.proposed_slug else None,
        proposed_title=module.title.value if module.title else None,
        topics=tuple(topic.value for topic in module.topics),
        source_bucket_suggestions=tuple(
            suggestion.value for suggestion in module.source_bucket_suggestions
        ),
    )


def _scoped_manifest(
    course_root: Path,
    module_id: str,
) -> tuple[SourceManifest, tuple[GapEntry, ...]]:
    scan = scan_course(course_root)
    scoped_entries = [
        entry
        for entry in scan.manifest.entries
        if entry.scope in {"course", "shared"} or entry.module_id == module_id
    ]
    scoped_gaps = tuple(
        gap
        for gap in scan.gap_ledger.gaps
        if gap.path is None
        or gap.path == "course.yaml"
        or gap.path == "sources"
        or gap.path.startswith(f"modules/{module_id}/")
    )
    detected = dict(scan.manifest.detected)
    detected["source_file_count"] = sum(
        entry.source_role == "source" for entry in scoped_entries
    )
    detected["reference_file_count"] = sum(
        entry.source_role == "reference" for entry in scoped_entries
    )
    detected["scaffold_file_count"] = sum(
        entry.source_role == "scaffold" for entry in scoped_entries
    )
    gap_summary: dict[str, int] = {}
    for gap in scoped_gaps:
        gap_summary[gap.kind] = gap_summary.get(gap.kind, 0) + 1
    scoped_manifest = scan.manifest.model_copy(
        update={
            "entries": scoped_entries,
            "detected": detected,
            "gap_summary": dict(sorted(gap_summary.items())),
        }
    )
    return scoped_manifest, scoped_gaps


def _styleguide_resolution(sme_name: str) -> StyleguideResolution:
    """Resolve SME-keyed styleguide/attribution/approval/voice (Mine 3).

    Unknown SME names hard-fail via the registry (never silent Tejal).
    """
    from app.marcus.course_source.sme_registry import (
        SmeRegistryError,
        resolve_sme_profile,
    )

    try:
        profile = resolve_sme_profile(sme_name)
    except SmeRegistryError as exc:
        raise ValueError(str(exc)) from exc
    return StyleguideResolution(
        sme_name=sme_name,
        sme_key=profile.sme_key,
        styleguide_id=profile.styleguide_id,
        attribution=profile.attribution,
        approval_route=profile.approval_route,
        voice_profile_ref=profile.voice_profile_ref,
        fallback=profile.fallback,
        reason=profile.reason
        or (
            "No SME-specific styleguide is available; downstream planning must "
            "treat style as unresolved."
            if profile.fallback
            else ""
        ),
    )


def _asset_records_from_module_proposal(
    proposal: CourseMetadataProposal,
    module_id: str,
) -> tuple[CanonicalAssetRecord, ...]:
    module = _proposal_module(proposal, module_id)
    if module.status == "missing":
        raise ValueError("module metadata proposal is missing")
    source_refs = [
        AssetSourceRef(
            ref_id=f"{module_id}-requirement-{index:03d}",
            path=source_ref.path,
            locator=source_ref.locator,
            role="requirement",
        )
        for index, source_ref in enumerate(module.source_refs, start=1)
    ]
    if not source_refs:
        source_refs = [
            AssetSourceRef(
                ref_id=f"{module_id}-requirement-001",
                path=proposal.source_path,
                locator=f"module {module_id}",
                role="requirement",
            )
        ]
    return emit_requirement_gap_records(
        course_id=proposal.course_id,
        module_id=module_id,
        asset_kind="lecture",
        source_refs=source_refs,
    )


def build_lesson_planning_input_bundle(
    *,
    course_root: Path,
    proposal_path: Path,
    module_id: str,
    operator_focus: str,
) -> LessonPlanningInputBundle:
    course = load_course(course_root)
    proposal = load_module_metadata_proposal(proposal_path)
    if proposal.course_id != course.course_id:
        raise ValueError("proposal course_id does not match course root")
    if proposal.extraction_status != "verified":
        raise ValueError("proposal extraction_status must be verified")
    source_path = Path(proposal.source_path)
    if not source_path.is_absolute():
        source_path = (Path.cwd() / source_path).resolve()
    if course_root.resolve() not in source_path.parents:
        raise ValueError("proposal source_path must be under course root")
    scoped_manifest, scoped_gaps = _scoped_manifest(course_root, module_id)
    module_profile = _module_profile(course_root, proposal, module_id)
    return LessonPlanningInputBundle(
        course=CoursePlanningProfile(
            course_id=course.course_id,
            code=course.course.code,
            title=course.course.title,
            sme_name=course.sme.name,
            source_purpose=course.source_purpose,
            source_availability=tuple(
                availability.model_dump(mode="json")
                for availability in course.source_availability
            ),
        ),
        module=module_profile,
        learner_profile=proposal.learner_profile.value if proposal.learner_profile else None,
        course_learning_objectives=tuple(
            objective.model_dump(mode="json")
            for objective in proposal.course_learning_objectives
        ),
        scoped_source_manifest=scoped_manifest,
        asset_records=_asset_records_from_module_proposal(proposal, module_id),
        gap_ledger=scoped_gaps,
        operator_focus=operator_focus,
        styleguide_resolution=_styleguide_resolution(course.sme.name),
    )


__all__ = [
    "CoursePlanningProfile",
    "LessonPlanningInputBundle",
    "ModulePlanningProfile",
    "SCHEMA_VERSION",
    "StyleguideResolution",
    "build_lesson_planning_input_bundle",
    "load_input_bundle",
    "load_module_metadata_proposal",
    "render_input_bundle_yaml",
    "write_input_bundle",
]
