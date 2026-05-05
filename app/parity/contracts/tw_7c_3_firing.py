"""Single-source TW-7c-3 four-file-lockstep firing rule."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

FOUR_FILE_GLOBS = {
    "model": "app/models/decision_cards/{gate_id_lower}.py",
    "schema": "app/models/decision_cards/schema/{gate_id_lower}.v1.schema.json",
    "shape_pin": "tests/parity/test_decision_card_{gate_id_lower}_shape.py",
    "golden_fixture": "tests/fixtures/decision_cards/{gate_id_lower}_golden.json",
}


class LockstepResult(BaseModel):
    """Result of applying TW-7c-3's four-file-lockstep rule to one gate."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    gate_id: str = Field(..., min_length=1)
    files_present: dict[str, bool]
    all_four_present: bool
    failure_reason: str | None = None


def _gate_id_lower(gate_id: str) -> str:
    return gate_id.lower().replace(".", "_")


def _paths_for(gate_id: str, repo_root: Path) -> dict[str, Path]:
    gate_id_lower = _gate_id_lower(gate_id)
    return {
        key: repo_root / template.format(gate_id_lower=gate_id_lower)
        for key, template in FOUR_FILE_GLOBS.items()
    }


def LOCKSTEP_CHECK(  # noqa: N802 - contract-locked exported callable name.
    gate_id: str,
    repo_root: Path | None = None,
) -> LockstepResult:
    """Evaluate the single-source four-file-lockstep rule for ``gate_id``."""

    root = repo_root or Path(__file__).resolve().parents[3]
    paths = _paths_for(gate_id, root)
    files_present = {key: path.is_file() for key, path in paths.items()}
    all_four_present = all(files_present.values())
    missing = sorted(key for key, present in files_present.items() if not present)
    return LockstepResult(
        gate_id=gate_id,
        files_present=files_present,
        all_four_present=all_four_present,
        failure_reason=None
        if all_four_present
        else "missing four-file-lockstep artifact(s): " + ", ".join(missing),
    )


__all__ = ["FOUR_FILE_GLOBS", "LOCKSTEP_CHECK", "LockstepResult"]
