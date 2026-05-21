"""L1 lockstep check for learning-event schema, wiring, and manifest declarations."""

from __future__ import annotations

import argparse
import ast
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from scripts.utilities.file_helpers import project_root
from scripts.utilities.pipeline_manifest import load_manifest

ROOT = project_root()
REPORTS_ROOT = ROOT / "reports" / "dev-coherence"
DEFAULT_SCHEMA = ROOT / "state" / "config" / "learning-event-schema.yaml"
DEFAULT_CAPTURE = ROOT / "scripts" / "utilities" / "learning_event_capture.py"
DEFAULT_WIRING = ROOT / "app" / "marcus" / "orchestrator" / "learning_event_wiring.py"
DEFAULT_MANIFEST = ROOT / "state" / "config" / "pipeline-manifest.yaml"


def _trace_payload(
    checks: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    closure_gate: str,
) -> dict[str, Any]:
    return {
        "lane": "L1",
        "scope": "learning-event-lockstep",
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "closure_gate": closure_gate,
        "l1_checks_run": checks,
        "findings": findings,
    }


def _capture_event_type_literals(capture_path: Path) -> set[str]:
    tree = ast.parse(capture_path.read_text(encoding="utf-8"))
    literals: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.AnnAssign):
            continue
        if not isinstance(node.target, ast.Name) or node.target.id != "event_type":
            continue
        ann = node.annotation
        if not isinstance(ann, ast.Subscript):
            continue
        if not isinstance(ann.value, ast.Name) or ann.value.id != "Literal":
            continue
        slice_value = ann.slice
        values = slice_value.elts if isinstance(slice_value, ast.Tuple) else [slice_value]
        for value in values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                literals.add(value.value)
    return literals


def _parse_callsites(wiring_path: Path) -> list[dict[str, str | None]]:
    tree = ast.parse(wiring_path.read_text(encoding="utf-8"))
    callsites: list[dict[str, str | None]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name) or node.func.id != "create_event":
            continue
        gate = None
        event_type = None
        for kw in node.keywords:
            if (
                kw.arg == "gate"
                and isinstance(kw.value, ast.Constant)
                and isinstance(kw.value.value, str)
            ):
                gate = kw.value.value
            if (
                kw.arg == "event_type"
                and isinstance(kw.value, ast.Constant)
                and isinstance(kw.value.value, str)
            ):
                event_type = kw.value.value
        callsites.append({"gate": gate, "event_type": event_type})
    return callsites


def run_check(
    schema_path: Path,
    capture_path: Path,
    wiring_path: Path,
    manifest_path: Path,
) -> tuple[int, dict[str, Any]]:
    if not schema_path.exists():
        return (
            2,
            _trace_payload(
                [],
                [{"check": "structural", "message": f"Missing schema file: {schema_path}"}],
                "STRUCTURAL",
            ),
        )
    if not capture_path.exists():
        return (
            2,
            _trace_payload(
                [],
                [{"check": "structural", "message": f"Missing capture module: {capture_path}"}],
                "STRUCTURAL",
            ),
        )
    if not wiring_path.exists():
        return (
            2,
            _trace_payload(
                [],
                [
                    {
                        "check": "structural",
                        "message": f"Missing Marcus wiring module: {wiring_path}",
                    }
                ],
                "STRUCTURAL",
            ),
        )

    manifest = load_manifest(manifest_path)
    schema_data = yaml.safe_load(schema_path.read_text(encoding="utf-8")) or {}
    schema_types = set(schema_data.get("event_type_enum", []))
    capture_types = _capture_event_type_literals(capture_path)
    callsites = _parse_callsites(wiring_path)

    emitters = {
        step.gate_code
        for step in manifest.steps
        if step.learning_events.emits and step.gate_code
    }
    event_types_by_gate = {
        step.gate_code: set(step.learning_events.event_types)
        for step in manifest.steps
        if step.learning_events.emits and step.gate_code
    }
    callsite_gates = {item["gate"] for item in callsites if item["gate"]}

    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []

    check_a = schema_types == capture_types
    checks.append({"check": "A", "name": "schema-capture-enum-equality", "pass": check_a})
    if not check_a:
        findings.append(
            {
                "check": "A",
                "type": "alteration",
                "message": "Schema event_type_enum diverges from capture Literal union",
                "schema_only": sorted(schema_types - capture_types),
                "capture_only": sorted(capture_types - schema_types),
            }
        )

    check_b = callsite_gates.issubset(emitters)
    checks.append({"check": "B", "name": "callsite-gates-subset-emitters", "pass": check_b})
    if not check_b:
        findings.append(
            {
                "check": "B",
                "type": "invention",
                "message": "Marcus call-site uses gate not declared as emitter",
                "unexpected_callsite_gates": sorted(callsite_gates - emitters),
            }
        )

    check_c = emitters.issubset(callsite_gates)
    checks.append({"check": "C", "name": "emitters-subset-callsite-gates", "pass": check_c})
    if not check_c:
        findings.append(
            {
                "check": "C",
                "type": "omission",
                "message": "Manifest emitter gate has no Marcus call-site",
                "missing_callsite_gates": sorted(emitters - callsite_gates),
            }
        )

    invalid_event_types: list[dict[str, str]] = []
    for item in callsites:
        gate = item["gate"]
        event_type = item["event_type"]
        if not gate or not event_type:
            continue
        if event_type not in event_types_by_gate.get(gate, set()):
            invalid_event_types.append({"gate": gate, "event_type": event_type})
    check_d = not invalid_event_types
    checks.append({"check": "D", "name": "callsite-event-type-subset-gate-types", "pass": check_d})
    if not check_d:
        findings.append(
            {
                "check": "D",
                "type": "alteration",
                "message": "Marcus call-site event_type is not declared for that gate",
                "mismatches": invalid_event_types,
            }
        )

    if findings:
        return 1, _trace_payload(checks, findings, "FAIL")
    return 0, _trace_payload(checks, [], "PASS")


def _write_trace(payload: dict[str, Any], exit_code: int) -> Path:
    ts = datetime.now(tz=UTC).strftime("%Y-%m-%d-%H%M")
    trace_dir = REPORTS_ROOT / ts
    trace_dir.mkdir(parents=True, exist_ok=True)
    suffix = "PASS" if exit_code == 0 else "STRUCTURAL" if exit_code == 2 else "FAIL"
    trace_path = trace_dir / f"check-learning-event-lockstep.{suffix}.yaml"
    trace_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return trace_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check learning-event lockstep integrity.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--capture", type=Path, default=DEFAULT_CAPTURE)
    parser.add_argument("--wiring", type=Path, default=DEFAULT_WIRING)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args(argv)

    exit_code, payload = run_check(args.schema, args.capture, args.wiring, args.manifest)
    trace_path = _write_trace(payload, exit_code)
    print(f"learning-lockstep exit={exit_code} trace={trace_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
