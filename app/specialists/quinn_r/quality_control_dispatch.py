"""Importlib dispatch wrapper for Quinn-R quality-control checks."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
QC_SCRIPTS = REPO_ROOT / "skills" / "quality-control" / "scripts"


def _ensure_module_stub(name: str) -> None:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)


def _ensure_package_stubs() -> None:
    _ensure_module_stub("skills")
    _ensure_module_stub("skills.quality_control")
    _ensure_module_stub("skills.quality_control.scripts")


def _load_module(module_name: str, file_name: str) -> Any:
    _ensure_package_stubs()
    path = QC_SCRIPTS / file_name
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load quality-control module at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def run_precomposition_validators(*, artifact_paths: list[str]) -> dict[str, Any]:
    if not artifact_paths:
        return {
            "status": "skipped",
            "findings": [],
            "dimension_scores": {"composition": "SKIPPED"},
        }
    precomp = _load_module(
        "skills.quality_control.scripts.precomposition_validator",
        "precomposition_validator.py",
    )
    accessibility = _load_module(
        "skills.quality_control.scripts.accessibility_checker",
        "accessibility_checker.py",
    )
    target = artifact_paths[0]
    if not Path(target).is_file():
        return {
            "status": "degraded",
            "findings": [{"dimension": "composition", "reason": "artifact missing"}],
            "dimension_scores": {"composition": "LOW"},
        }
    result = precomp.validate_precomposition(target)
    if not isinstance(result, dict):
        raise RuntimeError("validate_precomposition must return a mapping")
    content = []
    for path in artifact_paths:
        candidate = Path(path)
        if candidate.is_file():
            content.append(candidate.read_text(encoding="utf-8", errors="ignore"))
    accessibility_result = accessibility.run_accessibility_check("\n\n".join(content))
    findings = result.get("findings", [])
    if isinstance(accessibility_result, dict):
        findings = [
            *findings,
            *accessibility_result.get("findings", []),
        ]
    result["findings"] = findings
    dimension_scores = result.get("dimension_scores", {})
    if isinstance(dimension_scores, dict):
        accessibility_status = str(accessibility_result.get("status", "pass")).lower()
        dimension_scores["accessibility"] = (
            "PASS" if accessibility_status == "pass" else "FAIL"
        )
    result["dimension_scores"] = dimension_scores
    return result


def run_postcomposition_validators(*, artifact_path: str | None) -> dict[str, Any]:
    if not artifact_path:
        return {
            "status": "skipped",
            "findings": [],
            "dimension_scores": {"accessibility": "SKIPPED", "brand": "SKIPPED"},
        }
    artifact = Path(artifact_path)
    if not artifact.is_file():
        return {
            "status": "degraded",
            "findings": [{"dimension": "content", "reason": "artifact missing"}],
            "dimension_scores": {
                "accessibility": "SKIPPED",
                "brand": "SKIPPED",
                "composition": "SKIPPED",
            },
        }
    artifact_text = artifact.read_text(encoding="utf-8", errors="ignore")
    accessibility = _load_module(
        "skills.quality_control.scripts.accessibility_checker",
        "accessibility_checker.py",
    )
    brand = _load_module(
        "skills.quality_control.scripts.brand_validator",
        "brand_validator.py",
    )
    visual = _load_module(
        "skills.quality_control.scripts.visual_fill_validator",
        "visual_fill_validator.py",
    )
    accessibility_result = accessibility.run_accessibility_check(artifact_text)
    brand_result = brand.run_brand_validation(artifact_text)
    visual_result = visual.validate_visual_fill(str(artifact))
    accessibility_status = str(accessibility_result.get("status", "pass")).lower()
    brand_status = str(brand_result.get("status", "pass")).lower()
    return {
        "status": "ok",
        "accessibility": accessibility_result,
        "brand": brand_result,
        "visual_fill": visual_result,
        "dimension_scores": {
            "accessibility": "PASS" if accessibility_status == "pass" else "FAIL",
            "brand": "PASS" if brand_status == "pass" else "FAIL",
            "composition": "PASS" if visual_result.get("passed", True) else "WARN",
        },
    }


__all__ = ["run_postcomposition_validators", "run_precomposition_validators"]
