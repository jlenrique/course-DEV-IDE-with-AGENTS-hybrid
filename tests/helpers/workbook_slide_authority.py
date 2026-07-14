from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path

import yaml

from app.marcus.lesson_plan.pass1_authority import finalize_plan_authority
from app.marcus.lesson_plan.slide_authority import canonical_source_content_digest
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from tests._helpers.pass1_bundle import (
    write_authenticated_slide_bundle_from_course,
)

_SOURCE_SLIDE = re.compile(r"slide-(?P<ordinal>[1-9][0-9]*)-.*\.md")


def _authority_plan(
    envelope: ProductionEnvelope, plan_units: list[dict[str, object]]
) -> dict[str, object]:
    """Preserve authored plan fields while replacing fixture authority units."""
    for contribution in reversed(envelope.contributions):
        if contribution.specialist_id != "irene_pass1":
            continue
        candidate = contribution.output.get("lesson_plan")
        if isinstance(candidate, dict):
            return {**deepcopy(candidate), "plan_units": plan_units}
    return {"plan_units": plan_units}


def _plan_authority_receipt(
    lesson_plan: dict[str, object], course_source_root: Path
) -> dict[str, object]:
    root = Path(course_source_root)
    source_sections = tuple(
        (
            f"{path.relative_to(root).as_posix()}|"
            f"{canonical_source_content_digest(path.read_text(encoding='utf-8'))}",
            path.read_text(encoding="utf-8"),
        )
        for path in sorted((root / "slides").iterdir())
        if path.is_file() and not path.is_symlink()
    )
    return finalize_plan_authority(
        lesson_plan, source_sections=source_sections
    )


def single_slide_authority_payloads(
    course_source_root: Path,
) -> tuple[dict[str, object], dict[str, object]]:
    """Return an exact one-final-slide authority pair for integration fixtures."""
    slides = Path(course_source_root) / "slides"
    candidates = sorted(
        path
        for path in slides.iterdir()
        if path.is_file()
        and not path.is_symlink()
        and (match := _SOURCE_SLIDE.fullmatch(path.name)) is not None
        and int(match.group("ordinal")) == 1
    )
    if len(candidates) != 1:
        raise AssertionError("fixture requires exactly one source slide with ordinal 1")
    first_line = next(
        (line for line in candidates[0].read_text(encoding="utf-8").splitlines() if line),
        None,
    )
    if first_line is None:
        raise AssertionError("fixture source slide must contain a literal anchor")
    lesson_plan: dict[str, object] = {
        "plan_units": [
            {
                "unit_id": "u1",
                "scope_decision": "in-scope",
                "cluster_id": "c-u1",
                "cluster_role": "head",
                "parent_slide_id": None,
                "source_refs": [first_line],
            }
        ]
    }
    package: dict[str, object] = {
        "slides": [{"slide_id": "slide-01", "source_ref": "u1"}]
    }
    return lesson_plan, package


def write_single_slide_plan_sidecar(
    run_dir: Path, course_source_root: Path
) -> tuple[dict[str, object], dict[str, object]]:
    lesson_plan, package = single_slide_authority_payloads(course_source_root)
    Path(run_dir).mkdir(parents=True, exist_ok=True)
    (Path(run_dir) / "irene-pass1.lesson-plan.json").write_text(
        json.dumps(lesson_plan, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="",
    )
    receipt = _plan_authority_receipt(lesson_plan, course_source_root)
    (Path(run_dir) / "irene-pass1.plan-authority.json").write_text(
        json.dumps(receipt, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="",
    )
    write_authenticated_slide_bundle_from_course(run_dir, course_source_root)
    return lesson_plan, package


def install_single_slide_authority(
    envelope: ProductionEnvelope,
    *,
    run_dir: Path,
    course_source_root: Path,
) -> ProductionEnvelope:
    lesson_plan, package = write_single_slide_plan_sidecar(
        run_dir, course_source_root
    )
    plan = envelope.get_contribution("irene_pass1", node_id="05B")
    packaged = envelope.get_contribution("package_builder", node_id="06")
    if plan is not None or packaged is not None:
        if plan is None or packaged is None:
            raise AssertionError("fixture authority contributions are only partially present")
        return envelope
    updated = envelope.model_copy(deep=True)
    receipt = _plan_authority_receipt(lesson_plan, course_source_root)
    updated.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="irene_pass1",
            node_id="05B",
            output={"lesson_plan": lesson_plan, "plan_authority_receipt": receipt},
            model_used="fixture",
        )
    )
    updated.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="package_builder",
            node_id="06",
            output=package,
            model_used="fixture",
        )
    )
    return updated


def install_manifest_slide_authority(
    envelope: ProductionEnvelope,
    *,
    run_dir: Path,
    course_source_root: Path,
) -> ProductionEnvelope:
    """Install exact test authority matching an existing serialized manifest."""
    manifest = yaml.safe_load(
        (Path(run_dir) / "exports" / "segment-manifest-storyboard-b.yaml").read_text(
            encoding="utf-8"
        )
    )
    segments = manifest.get("segments") if isinstance(manifest, dict) else None
    if not isinstance(segments, list) or not segments:
        raise AssertionError("fixture manifest must carry nonempty segments")
    slides = sorted(
        path
        for path in (Path(course_source_root) / "slides").iterdir()
        if path.is_file() and not path.is_symlink() and _SOURCE_SLIDE.fullmatch(path.name)
    )
    if len(segments) > len(slides):
        raise AssertionError("fixture needs at least one source slide per manifest segment")
    plan_units: list[dict[str, object]] = []
    package_slides: list[dict[str, str]] = []
    for index, (segment, source) in enumerate(zip(segments, slides, strict=False), start=1):
        slide_id = segment.get("slide_id") if isinstance(segment, dict) else None
        if not isinstance(slide_id, str) or not slide_id:
            raise AssertionError("fixture manifest slide_id must be a nonblank string")
        anchor = next(
            (line for line in source.read_text(encoding="utf-8").splitlines() if line),
            None,
        )
        if anchor is None:
            raise AssertionError("fixture source slide must contain a literal anchor")
        unit_id = f"u{index}"
        plan_units.append(
            {
                "unit_id": unit_id,
                "scope_decision": "in-scope",
                "cluster_id": f"c-{unit_id}",
                "cluster_role": "head",
                "parent_slide_id": None,
                "source_refs": [anchor],
            }
        )
        package_slides.append({"slide_id": slide_id, "source_ref": unit_id})
    lesson_plan = _authority_plan(envelope, plan_units)
    package: dict[str, object] = {"slides": package_slides}
    (Path(run_dir) / "irene-pass1.lesson-plan.json").write_text(
        json.dumps(lesson_plan, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="",
    )
    receipt = _plan_authority_receipt(lesson_plan, course_source_root)
    (Path(run_dir) / "irene-pass1.plan-authority.json").write_text(
        json.dumps(receipt, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="",
    )
    write_authenticated_slide_bundle_from_course(run_dir, course_source_root)
    updated = envelope.model_copy(deep=True)
    updated.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="irene_pass1",
            node_id="05B",
            output={"lesson_plan": lesson_plan, "plan_authority_receipt": receipt},
            model_used="fixture",
        )
    )
    updated.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="package_builder",
            node_id="06",
            output=package,
            model_used="fixture",
        )
    )
    return updated


__all__ = [
    "install_manifest_slide_authority",
    "install_single_slide_authority",
    "single_slide_authority_payloads",
    "write_single_slide_plan_sidecar",
]
