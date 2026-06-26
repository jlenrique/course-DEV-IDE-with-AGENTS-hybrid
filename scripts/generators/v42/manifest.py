"""Manifest adapters for v4.2 generator rendering."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scripts.utilities.pipeline_manifest import PipelineManifest, StepEntry, load_manifest


class MissingSectionTemplateError(RuntimeError):
    """A renderable (non-orchestration) step has no section template.

    Renderer/L1 story (drift-audit fold, 2026-06-12): the previous behavior
    FABRICATED a plausible template name and let Jinja crash later with
    TemplateNotFound deep in the include stack — the silent-lie pattern.
    Raising here names the step and the expected template path up front.
    """


@dataclass(frozen=True)
class GeneratorStep:
    """Generator-friendly step projection."""

    id: str
    label: str
    pack_section_anchor: str
    template_name: str
    hud_id: str
    module_path: str
    audience: str
    rationale: str | None
    sub_phase_of: str | None
    insertion_after: str | None


@dataclass(frozen=True)
class GeneratorManifest:
    """Generator input model."""

    schema_version: str
    pack_version: str
    generator_ref: str
    steps: tuple[GeneratorStep, ...]


def _slugify(label: str) -> str:
    import re

    lowered = label.lower().replace("&", " and ").replace("+", " ")
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    return re.sub(r"-+", "-", lowered).strip("-")


def _template_name(step: StepEntry, template_root: Path | None = None) -> str:
    root = template_root or (Path(__file__).parent / "templates")
    matches = sorted((root / "sections").glob(f"{step.id}-*.md.j2"))
    if not matches:
        raise MissingSectionTemplateError(
            f"renderable step {step.id!r} ({step.label}) has no section "
            f"template; expected something like "
            f"sections/{step.id}-{_slugify(step.label)}.md.j2"
        )
    return f"sections/{matches[0].name}"


def _module_path(step: StepEntry) -> str:
    if step.id == "07G":
        return "app/specialists/vision"
    if step.id == "07D.5":
        return "app/specialists/motion_planner"
    if step.id == "07W":
        return "app/specialists/workbook_producer"
    if step.id.startswith("11") or step.id == "12":
        # PP-1 (S1 P0-5 cleanup 2026-05-07): ElevenLabs lane is Enrique;
        # the Audra value predated the Slab-7b roster and was hand-fixed in
        # the committed pack without folding back here (A12 counter-pattern).
        return "skills/bmad-agent-enrique"
    if step.id.startswith("07"):
        return "skills/bmad-agent-gary"
    if step.id.startswith("04"):
        return "marcus/orchestrator/loop.py"
    if step.id in {"14", "14.5", "15"}:
        return "skills/bmad-agent-desmond"
    return "scripts/utilities/run_hud.py"


def _audience(step: StepEntry) -> str:
    if step.gate:
        return "M→O"
    if step.sub_phase_of:
        return "M→self"
    return "O→M"


def _orchestration_only_ids(path: Path) -> frozenset[str]:
    """Node ids that are runtime-only orchestration, never pack prose.

    Mirrors the L1 lockstep check's exclusion via the SHARED predicate
    (app.manifest.schema.is_orchestration_only): the classification ruling
    existed in L1 since Story 7a.2 but the renderer never learned it, so
    `pack.md.j2` demanded a section template per node unconditionally and
    crashed on the four Slab-7a orchestration nodes (renderer/L1 story,
    drift-audit fold 2026-06-12; classification fix, NOT placeholder
    templates — orchestration nodes are runtime-only by ratified design).
    Legacy steps-shaped manifests carry no graph nodes; treat as none.
    """
    from app.manifest.loader import load as load_graph_manifest
    from app.manifest.schema import is_pack_excluded

    try:
        graph_manifest = load_graph_manifest(path)
    except Exception:  # noqa: BLE001 - legacy steps-shaped manifests
        return frozenset()
    # is_pack_excluded = orchestration-only nodes PLUS folded HIL gate nodes
    # (Arc 1a) — both are runtime-only / pack-invisible.
    return frozenset(
        node.id for node in graph_manifest.nodes if is_pack_excluded(node)
    )


def load_generator_manifest(
    path: Path, template_root: Path | None = None
) -> GeneratorManifest:
    """Load the canonical manifest and shape RENDERABLE steps for renderer loops."""
    manifest: PipelineManifest = load_manifest(path)
    skip_ids = _orchestration_only_ids(path)
    ordered = [step for step in manifest.steps if step.id not in skip_ids]
    generator_steps = tuple(
        GeneratorStep(
            id=step.id,
            label=step.label,
            pack_section_anchor=step.pack_section_anchor,
            template_name=_template_name(step, template_root),
            hud_id=step.id,
            module_path=_module_path(step),
            audience=_audience(step),
            rationale=getattr(step, "rationale", None),
            sub_phase_of=step.sub_phase_of,
            insertion_after=step.insertion_after,
        )
        for step in ordered
    )
    return GeneratorManifest(
        schema_version=manifest.schema_version,
        pack_version=manifest.pack_version,
        generator_ref=manifest.generator_ref,
        steps=generator_steps,
    )
