"""Validate Slab 7b per-specialist parity test class shape.

Story 7b.1 introduced Class-A activation contracts. Story 7b.4 adds Class-B
persona-continuity + sidecar-write parity assertions for Irene Pass-1.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TARGET = REPO_ROOT / "tests" / "parity"
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
    violations: list[Violation] = []
    for path in files:
        violations.extend(_validate_file(path))

    if violations:
        for violation in violations:
            print(violation.render())
        return 1
    print(f"PASS: {len(files)} activation contract file(s) conform")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
