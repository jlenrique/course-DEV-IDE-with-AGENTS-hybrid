"""Thin dispatch seam for Gary gamma generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from skills.gamma_api_mastery.scripts.gamma_operations import execute_generation

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FIXTURE_RECEIPT = (
    REPO_ROOT / "tests" / "fixtures" / "specialists" / "gary" / "fixture_receipt.json"
)


class GammaDispatchError(RuntimeError):  # noqa: N818
    """Raised when gamma dispatch fails before receipt parsing."""

    def __init__(self, message: str, *, tag: str) -> None:
        super().__init__(message)
        self.tag = tag


def _load_fixture_receipt(path: Path = DEFAULT_FIXTURE_RECEIPT) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dispatch_to_gamma(
    *,
    directive_path: str | Path | None = None,
    export_dir: str | Path | None = None,
    allow_fixture: bool = False,
) -> dict[str, Any]:
    """Run Gary gamma generation.

    S0 fail-loud policy (SCP 2026-06-11 segment-data-plane): missing inputs
    RAISE; the fixture receipt is reachable only via explicit ``allow_fixture``
    opt-in, which production dispatch never sets. The prior silent fallback
    emitted placeholder slides into Trial-3 attempt-4's production envelope
    and downstream gates blessed them.
    """
    if not directive_path or not export_dir:
        if allow_fixture:
            return _load_fixture_receipt()
        missing = "directive_path" if not directive_path else "export_dir"
        raise GammaDispatchError(
            f"dispatch_to_gamma missing required input: {missing}",
            tag="gamma.input.missing",
        )

    directive = Path(str(directive_path))
    if not directive.is_absolute():
        directive = (REPO_ROOT / directive).resolve()
    if not directive.is_file():
        raise GammaDispatchError(
            f"directive_path does not exist: {directive.as_posix()}",
            tag="receipt.parsed.missing-key",
        )

    export = Path(str(export_dir))
    if not export.is_absolute():
        export = (REPO_ROOT / export).resolve()
    export.mkdir(parents=True, exist_ok=True)

    params = {
        "input_text": directive.read_text(encoding="utf-8"),
        "export_dir": str(export),
        "export_as": "png",
    }
    try:
        result = execute_generation(params, module_lesson_part="gary-dispatch")
    except TimeoutError as exc:
        raise GammaDispatchError(
            f"gamma dispatch timed out: {exc}",
            tag="receipt.parsed.timeout",
        ) from exc
    except Exception as exc:  # pragma: no cover - live API path
        # Gamma client surfaces heterogeneous exception types; normalize under
        # one tag for deterministic parse-branch handling.
        raise GammaDispatchError(
            f"gamma dispatch API error: {exc}",
            tag="receipt.parsed.api-error",
        ) from exc

    if not isinstance(result, dict):
        raise GammaDispatchError(
            "gamma dispatch returned non-mapping receipt",
            tag="receipt.parsed.api-error",
        )
    return result


__all__ = ["DEFAULT_FIXTURE_RECEIPT", "GammaDispatchError", "dispatch_to_gamma"]
