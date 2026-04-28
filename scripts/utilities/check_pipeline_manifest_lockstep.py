"""Deterministic lockstep check for pipeline-manifest projections."""

from __future__ import annotations

import argparse
import ast
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

if __package__ in {None, ""}:  # direct script invocation
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.utilities.file_helpers import project_root
from scripts.utilities.pipeline_manifest import DEFAULT_MANIFEST_PATH, load_manifest
from scripts.utilities.run_hud import PIPELINE_STEPS

DEFAULT_PACK_PATH = (
    project_root()
    / "docs"
    / "workflow"
    / "production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md"
)
REPORTS_ROOT = project_root() / "reports" / "dev-coherence"


def _parse_pack_sections(pack_path: Path) -> list[dict[str, str]]:
    text = pack_path.read_text(encoding="utf-8")
    sections: list[dict[str, str]] = []
    for line in text.splitlines():
        if not line.startswith("## "):
            continue
        after = line[3:].strip()
        if ")" not in after:
            continue
        head, rest = after.split(")", 1)
        step_id = head.strip().upper().replace(" ", "")
        if not step_id:
            continue
        sections.append({"id": step_id, "name": rest.strip()})
    return sections


def _parse_insert_between_calls() -> list[tuple[str | None, str | None]]:
    workflow_runner = (project_root() / "marcus" / "orchestrator" / "workflow_runner.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(workflow_runner)
    pairs: list[tuple[str | None, str | None]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id != "insert_between" or len(node.args) < 2:
                continue
            before = node.args[0].value if isinstance(node.args[0], ast.Constant) else None
            after = node.args[1].value if isinstance(node.args[1], ast.Constant) else None
            pairs.append(
                (
                    before if isinstance(before, str) else None,
                    after if isinstance(after, str) else None,
                )
            )
    return pairs


def _trace_payload(
    checks: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    closure_gate: str,
) -> dict[str, Any]:
    return {
        "lane": "L1",
        "scope": "pipeline-lockstep",
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "closure_gate": closure_gate,
        "l1_checks_run": checks,
        "findings": findings,
    }


def run_check(
    manifest_path: Path,
    pack_path: Path,
    pack_version: str | None,
) -> tuple[int, dict[str, Any]]:
    if not manifest_path.exists():
        return 2, _trace_payload(
            [],
            [{"check": "structural", "message": f"Missing manifest: {manifest_path}"}],
            "STRUCTURAL",
        )
    if not pack_path.exists():
        return 2, _trace_payload(
            [],
            [{"check": "structural", "message": f"Missing pack file: {pack_path}"}],
            "STRUCTURAL",
        )

    try:
        manifest = load_manifest(manifest_path)
    except Exception as exc:  # noqa: BLE001
        return 2, _trace_payload([], [{"check": "structural", "message": str(exc)}], "STRUCTURAL")

    active_pack_version = pack_version or manifest.pack_version
    manifest_steps = [
        step for step in manifest.steps if (step.pack_version in (None, active_pack_version))
    ]
    manifest_ids = [step.id.upper() for step in manifest_steps]
    hud_ids = [step["id"].upper() for step in PIPELINE_STEPS]
    pack_steps = _parse_pack_sections(pack_path)
    pack_ids = [step["id"] for step in pack_steps if step["id"] in set(manifest_ids)]

    findings: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []

    # Check 1: set equality
    set_ok = set(manifest_ids) == set(hud_ids) == set(pack_ids)
    checks.append({"check": 1, "name": "set-equality", "pass": set_ok})
    if not set_ok:
        findings.append(
            {
                "check": 1,
                "message": "Manifest/HUD/pack step-id sets diverge",
                "manifest_only": sorted(set(manifest_ids) - set(hud_ids)),
                "hud_only": sorted(set(hud_ids) - set(manifest_ids)),
                "pack_only": sorted(set(pack_ids) - set(manifest_ids)),
            }
        )

    # Check 2: order equality
    order_ok = manifest_ids == hud_ids == pack_ids
    checks.append({"check": 2, "name": "order-equality", "pass": order_ok})
    if not order_ok:
        findings.append({"check": 2, "message": "Order differs across projections"})

    # Check 3: name equality
    manifest_names = {step.id.upper(): step.label for step in manifest_steps}
    hud_names = {step["id"].upper(): step["name"] for step in PIPELINE_STEPS}
    pack_names = {step["id"]: step["name"] for step in pack_steps}
    mismatched_names = [
        sid
        for sid in manifest_names
        if sid in hud_names
        and sid in pack_names
        and not (manifest_names[sid] == hud_names[sid] == pack_names[sid])
    ]
    names_ok = not mismatched_names
    checks.append({"check": 3, "name": "name-equality", "pass": names_ok})
    if not names_ok:
        findings.append({"check": 3, "message": f"Name mismatch for IDs: {mismatched_names}"})

    # Check 4: gate bitmap equality (manifest <-> HUD only)
    manifest_gate = {step.id.upper(): step.gate for step in manifest_steps}
    hud_gate = {step["id"].upper(): step["gate"] == "yes" for step in PIPELINE_STEPS}
    gate_mismatches = [
        sid for sid in manifest_gate if sid in hud_gate and manifest_gate[sid] != hud_gate[sid]
    ]
    gate_ok = not gate_mismatches
    checks.append({"check": 4, "name": "gate-bitmap-equality", "pass": gate_ok})
    if not gate_ok:
        findings.append({"check": 4, "message": f"Gate mismatch for IDs: {gate_mismatches}"})

    # Check 5: insertion consistency
    manifest_id_set = set(manifest_ids)
    insertion_ok = True
    for step in manifest_steps:
        if step.insertion_after and step.insertion_after.upper() not in manifest_id_set:
            insertion_ok = False
    for before_id, after_id in _parse_insert_between_calls():
        if before_id and before_id.upper() not in manifest_id_set:
            insertion_ok = False
        if after_id and after_id.upper() not in manifest_id_set:
            insertion_ok = False
    checks.append({"check": 5, "name": "insertion-consistency", "pass": insertion_ok})
    if not insertion_ok:
        findings.append({"check": 5, "message": "Insertion references missing manifest IDs"})

    # Check 6: emission declaration integrity
    emission_ok = True
    for step in manifest_steps:
        emits = step.learning_events.emits
        event_types = list(step.learning_events.event_types)
        if emits and not event_types:
            emission_ok = False
        if not emits and event_types:
            emission_ok = False
    checks.append({"check": 6, "name": "emission-declaration", "pass": emission_ok})
    if not emission_ok:
        findings.append({"check": 6, "message": "Invalid emits/event_types combinations"})

    # Check 7: schema_ref resolves
    schema_ref = manifest.learning_events.schema_ref
    schema_obj: dict[str, Any] | None = None
    if schema_ref:
        schema_path = project_root() / schema_ref
        if not schema_path.exists():
            return 2, _trace_payload(
                checks,
                [{"check": 7, "message": f"schema_ref path does not exist: {schema_ref}"}],
                "STRUCTURAL",
            )
        try:
            loaded = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
            schema_obj = loaded if isinstance(loaded, dict) else {}
        except Exception as exc:  # noqa: BLE001
            findings.append({"check": 7, "message": f"schema_ref parse failed: {exc}"})
    checks.append(
        {
            "check": 7,
            "name": "schema-ref-resolves",
            "pass": not any(f["check"] == 7 for f in findings),
        }
    )

    # Check 8: event_types subset schema enum
    event_subset_ok = True
    if schema_ref and schema_obj is not None:
        schema_types = set(schema_obj.get("event_type_enum", []))
        declared_types = {
            event_type
            for step in manifest_steps
            if step.learning_events.schema_ref == schema_ref
            for event_type in step.learning_events.event_types
        }
        if schema_types and not declared_types.issubset(schema_types):
            event_subset_ok = False
    checks.append({"check": 8, "name": "event-types-subset", "pass": event_subset_ok})
    if not event_subset_ok:
        findings.append({"check": 8, "message": "Manifest event_types not subset of schema enum"})

    if findings:
        return 1, _trace_payload(checks, findings, "FAIL")
    return 0, _trace_payload(checks, [], "PASS")


def _write_trace(payload: dict[str, Any], exit_code: int) -> Path:
    ts = datetime.now(tz=UTC).strftime("%Y-%m-%d-%H%M")
    trace_dir = REPORTS_ROOT / ts
    trace_dir.mkdir(parents=True, exist_ok=True)
    if exit_code == 0:
        suffix = "PASS"
    elif exit_code == 2:
        suffix = "STRUCTURAL"
    else:
        suffix = "FAIL"
    trace_path = trace_dir / f"check-pipeline-manifest-lockstep.{suffix}.yaml"
    trace_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return trace_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check pipeline manifest lockstep integrity.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--pack-path", type=Path, default=DEFAULT_PACK_PATH)
    parser.add_argument("--pack-version", type=str, default=None)
    args = parser.parse_args(argv)

    exit_code, trace = run_check(args.manifest, args.pack_path, args.pack_version)
    trace_path = _write_trace(trace, exit_code)
    print(f"lockstep-check exit={exit_code} trace={trace_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
