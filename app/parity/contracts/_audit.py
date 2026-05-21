"""Self-registration audit harness for parity-contract declarations."""

from __future__ import annotations

import argparse
import importlib
import json
import pkgutil
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.parity.contracts._registry import iter_registered_surfaces
from app.parity.contracts._sanctum import iter_sanctum_alignments

AuditStatus = Literal["PASS", "FAIL", "NOT_YET_EVALUATED"]
DEFAULT_MANIFEST_PATH = Path(
    "_bmad-output/implementation-artifacts/parity-registration-manifest.json"
)


class AuditResult(BaseModel):
    """Result of the parity self-registration audit."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    surface_cardinality: int = Field(..., ge=0)
    sanctum_cardinality: int = Field(..., ge=0)
    cardinality_floor: int = Field(..., ge=0)
    audit_status: AuditStatus
    failure_reason: str | None = None


def _import_walk_roots(
    discovery_roots: Sequence[str],
    *,
    include_reference_surface: bool = True,
) -> None:
    for root_name in discovery_roots:
        spec = importlib.util.find_spec(root_name)
        if spec is None:
            continue
        module = importlib.import_module(root_name)
        module_path = getattr(module, "__path__", None)
        if module_path is None:
            continue
        for module_info in pkgutil.walk_packages(
            module_path,
            prefix=f"{root_name}.",
        ):
            importlib.import_module(module_info.name)
    if include_reference_surface:
        importlib.import_module("app.parity.contracts._reference_surface")


def emit_registration_manifest(manifest_path: Path) -> Path:
    """Write registered surface declarations as stable UTF-8 JSON evidence."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    surfaces = [
        surface.model_dump(mode="json")
        for surface in iter_registered_surfaces()
    ]
    payload = {
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "schema_version": 1,
        "surfaces": surfaces,
    }
    manifest_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def run_self_registration_audit(
    *,
    declared_floor: int = 0,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    discovery_roots: Sequence[str] = ("app.gates", "app.composers"),
    include_reference_surface: bool = True,
) -> AuditResult:
    """Import registration roots, emit evidence, and compare to a floor."""
    if declared_floor < 0:
        raise ValueError("declared_floor must be non-negative")
    _import_walk_roots(
        discovery_roots,
        include_reference_surface=include_reference_surface,
    )
    surface_cardinality = len(list(iter_registered_surfaces()))
    sanctum_cardinality = len(list(iter_sanctum_alignments()))
    emit_registration_manifest(manifest_path)
    total = surface_cardinality + sanctum_cardinality
    if total >= declared_floor:
        return AuditResult(
            surface_cardinality=surface_cardinality,
            sanctum_cardinality=sanctum_cardinality,
            cardinality_floor=declared_floor,
            audit_status="PASS",
            failure_reason=None,
        )
    return AuditResult(
        surface_cardinality=surface_cardinality,
        sanctum_cardinality=sanctum_cardinality,
        cardinality_floor=declared_floor,
        audit_status="FAIL",
        failure_reason=(
            f"registered cardinality {total} is below declared floor "
            f"{declared_floor}"
        ),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the parity-contract self-registration audit."
    )
    parser.add_argument("--declared-floor", type=int, default=0)
    parser.add_argument("--manifest-path", type=Path, default=DEFAULT_MANIFEST_PATH)
    args = parser.parse_args(argv)
    result = run_self_registration_audit(
        declared_floor=args.declared_floor,
        manifest_path=args.manifest_path,
    )
    print(result.model_dump_json())
    return 0 if result.audit_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "AuditResult",
    "emit_registration_manifest",
    "main",
    "run_self_registration_audit",
]
