"""YAML → `PipelineManifest` loader (AC-1.4-B).

Single entrypoint `load(path)` that:
1. Reads the file as YAML (`yaml.safe_load`).
2. Validates the parsed payload against `PipelineManifest` (Pydantic v2).
3. Re-raises Pydantic `ValidationError` as `ManifestValidationError` so callers
   catch one stable named type and get a clean grep surface for named
   violations.

Callers are expected to provide an absolute or repo-relative path. Missing
files raise `ManifestValidationError` (not bare `FileNotFoundError`) so every
manifest-load error routes through one handler at runtime.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from app.manifest.exceptions import ManifestValidationError
from app.manifest.schema import PipelineManifest


def load(path: Path | str) -> PipelineManifest:
    """Load a `PipelineManifest` from a YAML file.

    Args:
        path: Filesystem path to the manifest YAML (absolute or repo-relative).

    Returns:
        The validated `PipelineManifest` instance.

    Raises:
        ManifestValidationError: If the file does not exist, is not valid YAML,
            or the parsed payload does not conform to `PipelineManifest`.
    """
    manifest_path = Path(path)
    if not manifest_path.is_file():
        raise ManifestValidationError(
            f"manifest file not found: {manifest_path} "
            f"(cwd-resolved: {manifest_path.resolve()})"
        )
    try:
        raw_text = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover — filesystem race; kept for grep clarity
        raise ManifestValidationError(
            f"manifest read failed: {manifest_path} ({exc})"
        ) from exc

    try:
        parsed = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise ManifestValidationError(
            f"manifest YAML parse failed at {manifest_path}: {exc}"
        ) from exc

    if not isinstance(parsed, dict):
        raise ManifestValidationError(
            f"manifest root must be a mapping (got {type(parsed).__name__}) at {manifest_path}"
        )

    try:
        return PipelineManifest.model_validate(parsed)
    except ValidationError as exc:
        raise ManifestValidationError(
            f"manifest validation failed at {manifest_path}:\n{exc}"
        ) from exc


__all__ = ["load"]
