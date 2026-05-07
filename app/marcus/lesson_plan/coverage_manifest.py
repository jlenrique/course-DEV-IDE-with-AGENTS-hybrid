"""Coverage-manifest verifier for Lesson Planner downstream plan-ref surfaces.

Story 32-2 audits the downstream contract claim carried forward by 31-2:
every lesson-plan envelope surface in the 05→13 path must preserve
``lesson_plan_revision`` + ``lesson_plan_digest`` and, when required, gate the
live consumer entry path with ``marcus.lesson_plan.log.assert_plan_fresh``.

This module intentionally stays narrow:

* it does not create downstream emitters;
* it carries an explicit, story-owned inventory instead of grepping the repo
  for guessed envelope names;
* it emits one canonical engineering artifact consumed by 32-3:
  ``_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json``.
"""

from __future__ import annotations

import ast
import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.marcus.lesson_plan.produced_asset import ProducedAsset
from app.marcus.lesson_plan.quinn_r_gate import QuinnRTwoBranchResult, QuinnRUnitVerdict
from app.marcus.lesson_plan.schema import PlanRef
from app.marcus.lesson_plan.step_05_pre_packet_handoff import Step05PrePacketEnvelope
from app.marcus.lesson_plan.step_06_plan_lock_fanout import Step06PlanLockFanoutEnvelope
from app.marcus.lesson_plan.step_07_gap_dispatch import Step07GapDispatchEnvelope

SCHEMA_VERSION = "1.0"
"""Coverage-manifest schema version pinned by Story 32-2."""


def _find_project_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "pyproject.toml").exists() or (candidate / ".git").exists():
            return candidate
    return Path(__file__).resolve().parent.parent.parent


PROJECT_ROOT = _find_project_root()
COVERAGE_MANIFEST_PATH = (
    PROJECT_ROOT
    / "_bmad-output"
    / "maps"
    / "coverage-manifest"
    / "lesson-plan-envelope-coverage-manifest.json"
)
SPRINT_STATUS_PATH = (
    PROJECT_ROOT / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
)

StepId = Literal["05", "06", "07", "08", "09", "10", "11", "12", "13"]
ArtifactKind = Literal[
    "envelope",
    "produced-asset",
    "fit-report",
    "gate-payload",
    "manifest-entry",
]
PlanRefMode = Literal["top-level-fields", "nested-plan-ref"]
CoverageStatus = Literal["implemented", "pending", "deferred"]


class CoverageManifestError(RuntimeError):
    """Raised when the inventory and current repo state contradict each other."""


class CoverageSurface(BaseModel):
    """One audited producer/consumer boundary in the 05→13 lesson-plan path."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )

    step_id: StepId
    surface_name: str = Field(..., min_length=1)
    owner_story_key: str = Field(..., min_length=1)
    module_path: str = Field(..., min_length=1)
    artifact_kind: ArtifactKind
    plan_ref_mode: PlanRefMode
    has_lesson_plan_revision: bool
    has_lesson_plan_digest: bool
    assert_plan_fresh_required: bool
    assert_plan_fresh_verified: bool
    status: CoverageStatus
    notes: str = Field(..., min_length=1)


class CoverageSummary(BaseModel):
    """Machine-readable rollup consumed by the 32-3 smoke harness."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )

    total_surfaces: int = Field(..., ge=0)
    implemented_surfaces: int = Field(..., ge=0)
    pending_surfaces: int = Field(..., ge=0)
    deferred_surfaces: int = Field(..., ge=0)
    surfaces_with_full_plan_ref_coverage: int = Field(..., ge=0)
    surfaces_missing_one_or_both_fields: int = Field(..., ge=0)
    surfaces_missing_freshness_gate_verification: int = Field(..., ge=0)
    trial_ready: bool


class CoverageManifest(BaseModel):
    """Top-level emitted coverage-manifest artifact."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )

    schema_version: str = Field(default=SCHEMA_VERSION, min_length=1)
    generated_at: datetime
    source_story_key: str = Field(default="32-2-plan-ref-envelope-coverage-manifest")
    surfaces: list[CoverageSurface]
    summary: CoverageSummary

    @field_validator("generated_at")
    @classmethod
    def _generated_at_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("CoverageManifest.generated_at must be timezone-aware")
        return value


@dataclass(frozen=True)
class CoverageInventoryEntry:
    """Story-owned inventory row used to build the emitted manifest."""

    step_id: StepId
    surface_name: str
    owner_story_key: str
    module_path: str
    artifact_kind: ArtifactKind
    plan_ref_mode: PlanRefMode
    assert_plan_fresh_required: bool
    notes: str
    consumer_entrypoint: str | None = None
    sample_factory: Callable[[], Any] | None = None
    deferred: bool = False


_SAMPLE_DIGEST: Final[str] = "sha256:" + "0" * 64


def _sample_step_05_pre_packet_envelope() -> Step05PrePacketEnvelope:
    return Step05PrePacketEnvelope(
        lesson_plan_revision=1,
        lesson_plan_digest=_SAMPLE_DIGEST,
    )


def _sample_step_06_plan_lock_fanout_envelope() -> Step06PlanLockFanoutEnvelope:
    return Step06PlanLockFanoutEnvelope(
        lesson_plan_revision=1,
        lesson_plan_digest=_SAMPLE_DIGEST,
    )


def _sample_step_07_gap_dispatch_envelope() -> Step07GapDispatchEnvelope:
    return Step07GapDispatchEnvelope(
        lesson_plan_revision=1,
        lesson_plan_digest=_SAMPLE_DIGEST,
        unit_id="u1",
        gap_type="corroborate",
    )


def _sample_blueprint_producer_output() -> ProducedAsset:
    return ProducedAsset(
        asset_ref="blueprint-u1@1",
        modality_ref="blueprint",
        source_plan_unit_id="u1",
        asset_path="_bmad-output/artifacts/blueprints/u1@1.md",
        fulfills="u1@1",
    )


def _sample_quinn_r_unit_verdict() -> QuinnRUnitVerdict:
    return QuinnRUnitVerdict(
        unit_id="u1",
        branch="produced-asset",
        passed=True,
        reason="produced asset passed quality",
        asset_ref="blueprint-u1@1",
    )


def _sample_quinn_r_two_branch_result() -> QuinnRTwoBranchResult:
    return QuinnRTwoBranchResult(
        plan_ref=PlanRef(
            lesson_plan_revision=1,
            lesson_plan_digest="sha256:" + "0" * 64,
        ),
        evaluated_at=datetime.now(tz=UTC),
        passed=True,
        unit_verdicts=[],
        prior_declined_rationales=[],
    )


DEFAULT_COVERAGE_INVENTORY: tuple[CoverageInventoryEntry, ...] = (
    CoverageInventoryEntry(
        step_id="05",
        surface_name="Pre-packet handoff consumer boundary",
        owner_story_key="30-4-plan-lock-fanout",
        module_path="marcus/lesson_plan/step_05_pre_packet_handoff.py",
        artifact_kind="envelope",
        plan_ref_mode="top-level-fields",
        assert_plan_fresh_required=True,
        notes=(
            "Consumer-side verification boundary for the pre-packet handoff, "
            "landed by Story 30-4 as Step05PrePacketEnvelope + consume()."
        ),
        consumer_entrypoint="consume",
        sample_factory=_sample_step_05_pre_packet_envelope,
    ),
    CoverageInventoryEntry(
        step_id="06",
        surface_name="30-4 plan-lock fanout envelope",
        owner_story_key="30-4-plan-lock-fanout",
        module_path="marcus/lesson_plan/step_06_plan_lock_fanout.py",
        artifact_kind="envelope",
        plan_ref_mode="top-level-fields",
        assert_plan_fresh_required=True,
        notes="First plan-lock fanout boundary in the 05+ branch.",
        consumer_entrypoint="consume",
        sample_factory=_sample_step_06_plan_lock_fanout_envelope,
    ),
    CoverageInventoryEntry(
        step_id="07",
        surface_name="30-4 gap-dispatch envelope",
        owner_story_key="30-4-plan-lock-fanout",
        module_path="marcus/lesson_plan/step_07_gap_dispatch.py",
        artifact_kind="envelope",
        plan_ref_mode="top-level-fields",
        assert_plan_fresh_required=True,
        notes="Downstream gap-dispatch boundary emitted from the plan-lock fanout lane.",
        consumer_entrypoint="consume",
        sample_factory=_sample_step_07_gap_dispatch_envelope,
    ),
    CoverageInventoryEntry(
        step_id="08",
        surface_name="30-4 produced-asset consumer boundary",
        owner_story_key="30-4-plan-lock-fanout",
        module_path="marcus/lesson_plan/step_08_produced_asset_consumer.py",
        artifact_kind="produced-asset",
        plan_ref_mode="nested-plan-ref",
        assert_plan_fresh_required=True,
        notes=(
            "Deferred by Story 32-2a: Story 30-4 closed with scope limited to "
            "05/06/07 consumer boundaries; step-08 surface has no known owner "
            "until a future story (32-3 smoke harness or targeted follow-on) "
            "claims it. Row kept as an explicit audit-incomplete reminder."
        ),
        consumer_entrypoint="consume",
        deferred=True,
    ),
    CoverageInventoryEntry(
        step_id="09",
        surface_name="30-4 fit-report bridge payload",
        owner_story_key="30-4-plan-lock-fanout",
        module_path="marcus/lesson_plan/step_09_fit_report_bridge.py",
        artifact_kind="fit-report",
        plan_ref_mode="nested-plan-ref",
        assert_plan_fresh_required=True,
        notes=(
            "Deferred by Story 32-2a: step-09 surface has no known owner after "
            "Story 30-4 closed with scope limited to 05/06/07. Future claim "
            "likely lands with 32-3 or a targeted follow-on."
        ),
        consumer_entrypoint="consume",
        deferred=True,
    ),
    CoverageInventoryEntry(
        step_id="10",
        surface_name="30-4 manifest-bound handoff payload",
        owner_story_key="30-4-plan-lock-fanout",
        module_path="marcus/lesson_plan/step_10_manifest_bound_handoff.py",
        artifact_kind="manifest-entry",
        plan_ref_mode="nested-plan-ref",
        assert_plan_fresh_required=True,
        notes=(
            "Deferred by Story 32-2a: step-10 surface has no known owner after "
            "Story 30-4 closed with scope limited to 05/06/07. Future claim "
            "likely lands with 32-3 or a targeted follow-on."
        ),
        consumer_entrypoint="consume",
        deferred=True,
    ),
    CoverageInventoryEntry(
        step_id="11",
        surface_name="31-4 blueprint-producer output",
        owner_story_key="31-4-blueprint-producer",
        module_path="marcus/lesson_plan/blueprint_producer.py",
        artifact_kind="produced-asset",
        plan_ref_mode="nested-plan-ref",
        assert_plan_fresh_required=True,
        notes=(
            "Blueprint producer output surface emitted by Story 31-4. "
            "ProducedAsset does not carry a nested plan_ref field today; the "
            "audit honestly flags plan_ref fields as absent until 30-4's "
            "plan-lock fanout envelope wraps the asset with PlanRef."
        ),
        consumer_entrypoint="produce",
        sample_factory=_sample_blueprint_producer_output,
    ),
    CoverageInventoryEntry(
        step_id="12",
        surface_name="31-5 branch-result payload",
        owner_story_key="31-5-quinn-r-two-branch",
        module_path="marcus/lesson_plan/quinn_r_gate.py",
        artifact_kind="gate-payload",
        plan_ref_mode="nested-plan-ref",
        assert_plan_fresh_required=True,
        notes=(
            "Step-12 per-unit branch-result payload (QuinnRUnitVerdict). "
            "31-5 consolidated step-12 + step-13 payloads into a single "
            "module; step-13 below audits the aggregate QuinnRTwoBranchResult. "
            "QuinnRUnitVerdict does not carry a plan_ref today; honest audit."
        ),
        consumer_entrypoint="evaluate_quinn_r_two_branch_gate",
        sample_factory=_sample_quinn_r_unit_verdict,
    ),
    CoverageInventoryEntry(
        step_id="13",
        surface_name="31-5 quinn-r gate payload",
        owner_story_key="31-5-quinn-r-two-branch",
        module_path="marcus/lesson_plan/quinn_r_gate.py",
        artifact_kind="gate-payload",
        plan_ref_mode="nested-plan-ref",
        assert_plan_fresh_required=True,
        notes="Final step-13 gate payload audited before 32-3 trial smoke.",
        consumer_entrypoint="evaluate_quinn_r_two_branch_gate",
        sample_factory=_sample_quinn_r_two_branch_result,
    ),
)

_STORY_STATUS_PATTERN = re.compile(r"^\s*([0-9]+-[0-9]+[a-z]?(?:-[^:]+)+):\s*([a-z-]+)")


def _load_story_statuses(project_root: Path) -> dict[str, str]:
    path = project_root / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
    if not path.exists():
        return {}
    statuses: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _STORY_STATUS_PATTERN.match(line)
        if match:
            statuses[match.group(1)] = match.group(2)
    return statuses


def _has_field(value: Any, field_name: str) -> bool:
    if value is None:
        return False
    if isinstance(value, Mapping):
        return field_name in value
    return hasattr(value, field_name)


def _get_field(value: Any, field_name: str) -> Any | None:
    if value is None:
        return None
    if isinstance(value, Mapping):
        return value.get(field_name)
    return getattr(value, field_name, None)


def verify_plan_ref_fields(surface: Any, plan_ref_mode: PlanRefMode) -> tuple[bool, bool]:
    """Check whether a surface exposes the expected plan-ref fields."""
    if plan_ref_mode == "top-level-fields":
        return (
            _has_field(surface, "lesson_plan_revision"),
            _has_field(surface, "lesson_plan_digest"),
        )
    nested = _get_field(surface, "plan_ref")
    return (
        _has_field(nested, "lesson_plan_revision"),
        _has_field(nested, "lesson_plan_digest"),
    )


def _canonical_import_bindings(tree: ast.Module) -> tuple[set[str], set[str]]:
    direct_names: set[str] = set()
    module_aliases: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "marcus.lesson_plan.log":
            for alias in node.names:
                if alias.name == "assert_plan_fresh":
                    direct_names.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "marcus.lesson_plan.log" and alias.asname:
                    module_aliases.add(alias.asname)
    return direct_names, module_aliases


def _is_canonical_call(func: ast.expr, direct_names: set[str], module_aliases: set[str]) -> bool:
    if isinstance(func, ast.Name):
        return func.id in direct_names
    if (
        isinstance(func, ast.Attribute)
        and func.attr == "assert_plan_fresh"
        and isinstance(func.value, ast.Name)
    ):
        return func.value.id in module_aliases
    return False


def _first_call_arg_name(call: ast.Call) -> str | None:
    if not call.args:
        return None
    first = call.args[0]
    if isinstance(first, ast.Name):
        return first.id
    return None


def _statement_calls_anything(stmt: ast.stmt) -> bool:
    return any(isinstance(node, ast.Call) for node in ast.walk(stmt))


def _statement_calls_canonical(
    stmt: ast.stmt,
    *,
    direct_names: set[str],
    module_aliases: set[str],
    expected_arg_name: str | None,
) -> bool:
    for node in ast.walk(stmt):
        if isinstance(node, ast.Call) and _is_canonical_call(
            node.func,
            direct_names,
            module_aliases,
        ):
            return _first_call_arg_name(node) == expected_arg_name
    return False


def _wrapper_is_live_and_canonical(
    wrapper: ast.FunctionDef,
    *,
    direct_names: set[str],
    module_aliases: set[str],
    entry_arg_name: str | None,
) -> bool:
    if not wrapper.args.args or entry_arg_name is None:
        return False
    wrapper_param = wrapper.args.args[0].arg
    for stmt in wrapper.body:
        if _statement_calls_canonical(
            stmt,
            direct_names=direct_names,
            module_aliases=module_aliases,
            expected_arg_name=wrapper_param,
        ):
            return True
        if _statement_calls_anything(stmt):
            return False
    return False


def verify_assert_plan_fresh_usage(module_path: Path | str, *, entrypoint_name: str) -> bool:
    """Verify canonical `assert_plan_fresh` use at a live entry path.

    Accepted proofs:
    - direct invocation of the canonical imported symbol from
      ``marcus.lesson_plan.log``;
    - a same-module local wrapper that calls the canonical symbol and is
      itself invoked on the entry path before downstream processing.
    """
    path = Path(module_path)
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    direct_names, module_aliases = _canonical_import_bindings(tree)
    if not direct_names and not module_aliases:
        return False

    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    entrypoint = functions.get(entrypoint_name)
    if entrypoint is None or not entrypoint.args.args:
        return False
    expected_arg_name = entrypoint.args.args[0].arg

    approved_wrappers = {
        name
        for name, fn in functions.items()
        if name != entrypoint_name
        and _wrapper_is_live_and_canonical(
            fn,
            direct_names=direct_names,
            module_aliases=module_aliases,
            entry_arg_name=expected_arg_name,
        )
    }

    saw_downstream_processing = False
    for stmt in entrypoint.body:
        if _statement_calls_canonical(
            stmt,
            direct_names=direct_names,
            module_aliases=module_aliases,
            expected_arg_name=expected_arg_name,
        ):
            return not saw_downstream_processing

        for node in ast.walk(stmt):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in approved_wrappers
                and _first_call_arg_name(node) == expected_arg_name
            ):
                return not saw_downstream_processing

        if _statement_calls_anything(stmt):
            saw_downstream_processing = True

    return False


def summarize_surfaces(surfaces: Sequence[CoverageSurface]) -> CoverageSummary:
    implemented = [surface for surface in surfaces if surface.status == "implemented"]
    pending_count = sum(surface.status == "pending" for surface in surfaces)
    deferred_count = sum(surface.status == "deferred" for surface in surfaces)
    full_plan_ref = sum(
        surface.has_lesson_plan_revision and surface.has_lesson_plan_digest
        for surface in implemented
    )
    missing_fields = sum(
        not (surface.has_lesson_plan_revision and surface.has_lesson_plan_digest)
        for surface in implemented
    )
    missing_freshness = sum(
        surface.assert_plan_fresh_required and not surface.assert_plan_fresh_verified
        for surface in implemented
    )
    trial_ready = (
        len(surfaces) > 0
        and pending_count == 0
        and deferred_count == 0
        and missing_fields == 0
        and missing_freshness == 0
    )
    return CoverageSummary(
        total_surfaces=len(surfaces),
        implemented_surfaces=len(implemented),
        pending_surfaces=pending_count,
        deferred_surfaces=deferred_count,
        surfaces_with_full_plan_ref_coverage=full_plan_ref,
        surfaces_missing_one_or_both_fields=missing_fields,
        surfaces_missing_freshness_gate_verification=missing_freshness,
        trial_ready=trial_ready,
    )


def _sorted_surfaces(surfaces: Sequence[CoverageSurface]) -> list[CoverageSurface]:
    return sorted(
        surfaces,
        key=lambda surface: (surface.step_id, surface.owner_story_key, surface.surface_name),
    )


_IMPLEMENTED_OWNER_STATUSES: frozenset[str] = frozenset({"done", "review"})


def _resolve_status(
    entry: CoverageInventoryEntry,
    *,
    project_root: Path,
    story_statuses: Mapping[str, str],
) -> CoverageStatus:
    if entry.deferred:
        return "deferred"
    story_status = story_statuses.get(entry.owner_story_key)
    if story_status is None:
        raise CoverageManifestError(
            f"Inventory drift: {entry.owner_story_key} is not present in sprint-status.yaml."
        )
    module_exists = (project_root / entry.module_path).exists()
    if story_status == "done" and not module_exists:
        raise CoverageManifestError(
            f"Inventory drift: {entry.owner_story_key} is done but {entry.module_path} "
            "does not exist."
        )
    if module_exists and story_status == "backlog":
        raise CoverageManifestError(
            f"Inventory drift: {entry.module_path} exists while {entry.owner_story_key} "
            "is still in 'backlog'."
        )
    if module_exists and story_status in _IMPLEMENTED_OWNER_STATUSES:
        return "implemented"
    return "pending"


def build_coverage_manifest(
    inventory: Sequence[CoverageInventoryEntry] | None = None,
    *,
    project_root: Path | None = None,
    story_statuses: Mapping[str, str] | None = None,
    generated_at: datetime | None = None,
) -> CoverageManifest:
    """Build the current coverage-manifest from the explicit inventory."""
    root = project_root or PROJECT_ROOT
    statuses = dict(story_statuses or _load_story_statuses(root))
    seeds = inventory or DEFAULT_COVERAGE_INVENTORY
    resolved_surfaces: list[CoverageSurface] = []
    now = generated_at or datetime.now(tz=UTC)

    for entry in seeds:
        status = _resolve_status(entry, project_root=root, story_statuses=statuses)
        has_revision = False
        has_digest = False
        freshness_verified = False

        if status == "implemented":
            if entry.sample_factory is None:
                raise CoverageManifestError(
                    f"Implemented surface {entry.surface_name!r} requires a sample_factory."
                )
            sample = entry.sample_factory()
            has_revision, has_digest = verify_plan_ref_fields(sample, entry.plan_ref_mode)
            if entry.assert_plan_fresh_required:
                if entry.consumer_entrypoint is None:
                    raise CoverageManifestError(
                        "Implemented surface "
                        f"{entry.surface_name!r} requires a consumer_entrypoint."
                    )
                freshness_verified = verify_assert_plan_fresh_usage(
                    root / entry.module_path,
                    entrypoint_name=entry.consumer_entrypoint,
                )

        resolved_surfaces.append(
            CoverageSurface(
                step_id=entry.step_id,
                surface_name=entry.surface_name,
                owner_story_key=entry.owner_story_key,
                module_path=entry.module_path,
                artifact_kind=entry.artifact_kind,
                plan_ref_mode=entry.plan_ref_mode,
                has_lesson_plan_revision=has_revision,
                has_lesson_plan_digest=has_digest,
                assert_plan_fresh_required=entry.assert_plan_fresh_required,
                assert_plan_fresh_verified=freshness_verified,
                status=status,
                notes=entry.notes,
            )
        )

    sorted_surfaces = _sorted_surfaces(resolved_surfaces)
    summary = summarize_surfaces(sorted_surfaces)
    return CoverageManifest(
        generated_at=now,
        surfaces=sorted_surfaces,
        summary=summary,
    )


def render_coverage_manifest_json(manifest: CoverageManifest) -> str:
    """Render diff-friendly deterministic JSON for the emitted artifact."""
    payload = manifest.model_dump(mode="json")
    return json.dumps(payload, indent=2, ensure_ascii=True) + "\n"


def emit_coverage_manifest(
    inventory: Sequence[CoverageInventoryEntry] | None = None,
    *,
    project_root: Path | None = None,
    story_statuses: Mapping[str, str] | None = None,
    generated_at: datetime | None = None,
    output_path: Path | None = None,
) -> CoverageManifest:
    """Build and write the canonical coverage-manifest JSON artifact."""
    root = project_root or PROJECT_ROOT
    manifest = build_coverage_manifest(
        inventory=inventory,
        project_root=root,
        story_statuses=story_statuses,
        generated_at=generated_at,
    )
    target = output_path or (
        root
        / "_bmad-output"
        / "maps"
        / "coverage-manifest"
        / "lesson-plan-envelope-coverage-manifest.json"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_coverage_manifest_json(manifest), encoding="utf-8")
    return manifest


__all__ = [
    "COVERAGE_MANIFEST_PATH",
    "CoverageInventoryEntry",
    "CoverageManifest",
    "CoverageManifestError",
    "CoverageSummary",
    "CoverageSurface",
    "DEFAULT_COVERAGE_INVENTORY",
    "SCHEMA_VERSION",
    "build_coverage_manifest",
    "emit_coverage_manifest",
    "render_coverage_manifest_json",
    "summarize_surfaces",
    "verify_assert_plan_fresh_usage",
    "verify_plan_ref_fields",
]
