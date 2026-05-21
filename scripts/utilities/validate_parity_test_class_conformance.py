"""Validate Slab 7b per-specialist parity test class shape.

Story 7b.1 introduced Class-A activation contracts. Story 7b.4 adds Class-B
persona-continuity + sidecar-write parity assertions for Irene Pass-1.
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.models.tripwire_ledger import (  # noqa: E402
    TripwireId,
    TripwireLedgerEntry,
    TripwireSeverity,
)
from app.parity.contracts.tw_7c_3_firing import (  # noqa: E402
    LOCKSTEP_CHECK,
    LockstepResult,
)

DEFAULT_TARGET = REPO_ROOT / "tests" / "parity"
GATE_FAMILY_IDS = frozenset({"G0", "G1", "G2A", "G2C", "G3", "G4", "G5", "G6"})
RUNTIME_GATE_IDS = frozenset(
    {
        "G0",
        "G0A",
        "G0B",
        "G1",
        "G1A",
        "G1.5",
        "G2",
        "G2B",
        "G2C",
        "G2M",
        "G2.5",
        "G2F",
        "G3",
        "G3B",
        "G4",
        "G4A",
        "G4B",
        "G5",
    }
)
CLASS_B_REQUIRED_METHODS = frozenset(
    {
        "cold_activation_smoke",
        "test_class_b_scaffold_conformance",
        "test_lesson_plan_artifact_write_contract",
        "test_scope_lock_learning_events",
        "test_mode_singularity",
        "test_shared_sanctum_fingerprint",
    }
)
CLASS_C_PLUS_IDS = frozenset({"C+", "CPLUS"})
CLASS_C_PLUS_REQUIRED_METHODS = frozenset(
    {
        "cold_activation_smoke",
        "test_class_c_plus_scaffold_conformance",
        "test_four_file_sidecar_pattern",
        "test_live_llm_only_binding",
        "test_cache_hit_rate_harness_wired",
        "test_retrieval_intent_shape",
        "test_skill_md_activation_order",
    }
)
CLASS_C_REQUIRED_METHODS = frozenset(
    {
        "cold_activation_smoke",
        "test_class_c_scaffold_conformance",
        "test_six_file_bmb_sanctum_pattern",
        "test_gamma_api_client_binding",
        "test_vcr_cassettes_present",
        "test_credential_rotation_register_entry",
        "test_rate_limit_budget_declared",
        "test_cache_hit_rate_not_applicable",
        "test_operator_gated_canary_documented",
        "test_cold_activation_smoke",
    }
)
CLASS_D1_REQUIRED_METHODS = frozenset(
    {
        "cold_activation_smoke",
        "test_class_d1_scaffold_conformance",
        "test_six_file_bmb_sanctum_pattern",
        "test_single_skill_md_pattern",
        "test_llm_only_shared_facade",
        "test_aux_contribution_shape",
        "test_advisory_only_partition",
        "test_golden_fixture_replay",
        "test_cold_activation_smoke",
    }
)
CLASS_D2_REQUIRED_METHODS = frozenset(
    {
        "cold_activation_smoke",
        "test_class_d2_scaffold_conformance",
        "test_four_file_operational_sidecar_pattern",
        "test_single_compositor_skill_md_pattern",
        "test_no_llm_or_third_party_api",
        "test_pipeline_determinism_harness_wired",
        "test_field_mask_yaml_consumed",
        "test_four_input_chain_test_present",
        "test_operator_control_and_decision_log_landed",
    }
)
DECISION_CARD_SHAPE_REQUIRED_TOKENS = frozenset(
    {
        "LOCKSTEP_CHECK",
        "model_json_schema",
        "model_validate",
        "model_dump",
        "ValidationError",
        "_golden.json",
        ".v1.schema.json",
    }
)


def is_valid_runtime_gate_id(gate_id: str) -> bool:
    """Return whether ``gate_id`` is in 7c.4a's canonical runtime set."""

    return gate_id in RUNTIME_GATE_IDS


def gate_lockstep_result(gate_id: str, repo_root: Path | None = None) -> LockstepResult:
    """Evaluate TW-7c-3's single-source lockstep rule for one gate."""

    if not is_valid_runtime_gate_id(gate_id) and gate_id not in GATE_FAMILY_IDS:
        raise ValueError(f"unknown Slab 7c runtime gate id: {gate_id}")
    return LOCKSTEP_CHECK(gate_id, repo_root=repo_root)


def build_tw_7c_3_entry(
    *,
    gate_id: str,
    result: LockstepResult,
) -> TripwireLedgerEntry:
    """Build the TripwireLedgerEntry emitted when TW-7c-3 fires."""

    return TripwireLedgerEntry(
        tripwire_id=TripwireId.TW_7C_3,
        story_owner="7c-4b",
        fired_at=datetime.now(tz=UTC),
        fired_verdict="fired" if not result.all_four_present else "not_fired",
        measured_value={
            "gate_id": gate_id,
            "files_present": result.files_present,
            "all_four_present": result.all_four_present,
        },
        escalation_action_taken="halt-and-remediate-four-file-lockstep"
        if not result.all_four_present
        else None,
        decision_record_link="app/parity/contracts/tw_7c_3_firing.py",
        severity=TripwireSeverity.CRITICAL,
        trace_id=uuid4(),
    )


def write_tripwire_entry(
    sprint_status_path: Path,
    entry: TripwireLedgerEntry,
) -> Path:
    """Append a TripwireLedgerEntry-shaped row to sprint-status tripwire_events."""

    payload = yaml.safe_load(sprint_status_path.read_text(encoding="utf-8")) or {}
    events = payload.setdefault("tripwire_events", [])
    if not isinstance(events, list):
        raise ValueError("sprint-status.yaml::tripwire_events must be a list")
    events.append(entry.model_dump(mode="json"))
    sprint_status_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return sprint_status_path


@dataclass(frozen=True)
class Violation:
    path: Path
    line: int
    message: str

    def render(self) -> str:
        rel = self.path.relative_to(REPO_ROOT).as_posix()
        return f"{rel}:{self.line}: {self.message}"


def _iter_activation_contract_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target] if target.name.endswith("_activation_contract.py") else []
    return sorted(target.rglob("test_*_activation_contract.py"))


def _iter_decision_card_shape_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target] if _is_decision_card_shape_pin(target) else []
    return sorted(
        path for path in target.glob("test_decision_card_*_shape.py")
        if _is_decision_card_shape_pin(path)
    )


def _is_decision_card_shape_pin(path: Path) -> bool:
    return (
        path.name.startswith("test_decision_card_")
        and path.name.endswith("_shape.py")
        and path.name != "test_decision_card_base_shape.py"
    )


def _gate_id_from_shape_pin(path: Path) -> str:
    gate_slug = path.name.removeprefix("test_decision_card_").removesuffix("_shape.py")
    return gate_slug.upper().replace("_", ".")


def _name_of_expr(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Subscript):
        return _name_of_expr(node.value)
    return ""


def _literal_class_attr(class_node: ast.ClassDef, attr: str) -> object:
    for stmt in class_node.body:
        value: ast.expr | None = None
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == attr:
                    value = stmt.value
                    break
        elif (
            isinstance(stmt, ast.AnnAssign)
            and isinstance(stmt.target, ast.Name)
            and stmt.target.id == attr
        ):
            value = stmt.value
        if value is not None:
            try:
                return ast.literal_eval(value)
            except ValueError:
                return None
    return None


def _method_names(class_node: ast.ClassDef) -> set[str]:
    return {
        stmt.name
        for stmt in class_node.body
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _inherits_from_sanctum_base(
    class_node: ast.ClassDef,
    class_index: dict[str, ast.ClassDef],
    seen: set[str] | None = None,
) -> bool:
    seen = seen or set()
    for base in class_node.bases:
        base_name = _name_of_expr(base)
        if base_name == "SanctumParityTestBase":
            return True
        if base_name in seen:
            continue
        seen.add(base_name)
        parent = class_index.get(base_name)
        if parent is not None and _inherits_from_sanctum_base(
            parent, class_index, seen
        ):
            return True
    return False


def _validate_file(path: Path) -> list[Violation]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [Violation(path, exc.lineno or 1, f"syntax error: {exc.msg}")]
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    class_index = {node.name: node for node in classes}
    test_classes = [node for node in classes if node.name.startswith("Test")]
    if not test_classes:
        return [Violation(path, 1, "no pytest test class found")]

    violations: list[Violation] = []
    for class_node in test_classes:
        if not _inherits_from_sanctum_base(class_node, class_index):
            violations.append(
                Violation(
                    path,
                    class_node.lineno,
                    f"{class_node.name} must derive from SanctumParityTestBase",
                )
            )
        specialist_name = _literal_class_attr(class_node, "specialist_name")
        class_template_id = _literal_class_attr(class_node, "class_template_id")
        if not isinstance(specialist_name, str) or not specialist_name:
            violations.append(
                Violation(
                    path,
                    class_node.lineno,
                    f"{class_node.name} must set specialist_name",
                )
            )
        if not isinstance(class_template_id, str) or not class_template_id:
            violations.append(
                Violation(
                    path,
                    class_node.lineno,
                    f"{class_node.name} must set class_template_id",
                )
            )
            continue
        normalized_template = class_template_id.upper()
        if normalized_template == "B":
            missing_methods = sorted(CLASS_B_REQUIRED_METHODS - _method_names(class_node))
            if missing_methods:
                violations.append(
                    Violation(
                        path,
                        class_node.lineno,
                        "Class-B parity test missing required method(s): "
                        + ", ".join(missing_methods),
                    )
                )
            continue
        if normalized_template in CLASS_C_PLUS_IDS:
            missing_methods = sorted(
                CLASS_C_PLUS_REQUIRED_METHODS - _method_names(class_node)
            )
            if missing_methods:
                violations.append(
                    Violation(
                        path,
                        class_node.lineno,
                        "Class-C+ parity test missing required method(s): "
                        + ", ".join(missing_methods),
                    )
                )
            continue
        if normalized_template == "C":
            missing_methods = sorted(CLASS_C_REQUIRED_METHODS - _method_names(class_node))
            if missing_methods:
                violations.append(
                    Violation(
                        path,
                        class_node.lineno,
                        "Class-C parity test missing required method(s): "
                        + ", ".join(missing_methods),
                    )
                )
            continue
        if normalized_template == "D1":
            missing_methods = sorted(CLASS_D1_REQUIRED_METHODS - _method_names(class_node))
            if missing_methods:
                violations.append(
                    Violation(
                        path,
                        class_node.lineno,
                        "Class-D1 parity test missing required method(s): "
                        + ", ".join(missing_methods),
                    )
                )
            continue
        if normalized_template == "D2":
            missing_methods = sorted(CLASS_D2_REQUIRED_METHODS - _method_names(class_node))
            if missing_methods:
                violations.append(
                    Violation(
                        path,
                        class_node.lineno,
                        "Class-D2 parity test missing required method(s): "
                        + ", ".join(missing_methods),
                    )
                )
            continue
        if normalized_template != "A":
            violations.append(
                Violation(
                    path,
                    class_node.lineno,
                    "validator scaffold enforces only Class-A, Class-B, "
                    "Class-C, Class-C+, Class-D1, and Class-D2 tests",
                )
            )
            continue
        if "cold_activation_smoke" not in _method_names(class_node):
            violations.append(
                Violation(
                    path,
                    class_node.lineno,
                    "Class-A parity test must override cold_activation_smoke",
                )
            )
    return violations


def _validate_decision_card_shape_pin(path: Path) -> list[Violation]:
    text = path.read_text(encoding="utf-8")
    gate_id = _gate_id_from_shape_pin(path)
    violations: list[Violation] = []
    if not is_valid_runtime_gate_id(gate_id) and gate_id not in GATE_FAMILY_IDS:
        violations.append(
            Violation(path, 1, f"unknown DecisionCard shape-pin gate id: {gate_id}")
        )
    missing_tokens = sorted(
        token for token in DECISION_CARD_SHAPE_REQUIRED_TOKENS if token not in text
    )
    if missing_tokens:
        violations.append(
            Violation(
                path,
                1,
                "DecisionCard shape-pin missing required token(s): "
                + ", ".join(missing_tokens),
            )
        )
    if f"decision_cards.{gate_id.lower().replace('.', '_')}" not in text:
        violations.append(
            Violation(
                path,
                1,
                "DecisionCard shape-pin must import its per-gate model module",
            )
        )
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "target",
        nargs="?",
        default=str(DEFAULT_TARGET),
        help="Parity test file or directory; defaults to tests/parity/",
    )
    args = parser.parse_args(argv)

    target = Path(args.target)
    if not target.is_absolute():
        target = REPO_ROOT / target
    files = _iter_activation_contract_files(target)
    shape_files = _iter_decision_card_shape_files(target)
    violations: list[Violation] = []
    for path in files:
        violations.extend(_validate_file(path))
    for path in shape_files:
        violations.extend(_validate_decision_card_shape_pin(path))

    if violations:
        for violation in violations:
            print(violation.render())
        return 1
    total = len(files) + len(shape_files)
    print(
        f"PASS: {total} parity contract file(s) conform "
        f"({len(files)} activation + {len(shape_files)} decision-card shape-pin)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
