from __future__ import annotations

import ast
import hashlib
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPRINT_STATUS_PATH = REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
VALIDATOR_PATH = REPO_ROOT / "scripts" / "utilities" / "validate_parity_test_class_conformance.py"

EXPECTED_SHAPE_PIN_FLOOR = 20
EXPECTED_CLASS_CONFORMANCE_FLOOR = 11
TW_7C_1_FIRE_GAP_FLOOR = 4

DIMENSION_TOKENS = {
    "field-presence": ("model_fields", "properties", "Field("),
    "closed-enum-red-reject": ("ValidationError", "TypeAdapter", "field_validator"),
    "JSON-Schema-emission": ("model_json_schema", ".v1.schema.json"),
    "golden-fixture-round-trip": (
        "_golden.json",
        "model_validate",
        "model_dump",
        "accepts_valid_meta",
        "_override_event",
    ),
}

FAMILY_EVIDENCE_FILES = {
    "G1": (
        "tests/parity/test_decision_card_g1_shape.py",
        "tests/schemas/operator_verdict/test_section_04a_shape.py",
        "tests/schemas/operator_verdict/test_section_04_5_shape.py",
        "tests/schemas/operator_verdict/test_section_04_55_shape.py",
    ),
    "G2C": (
        "tests/parity/test_decision_card_g2c_shape.py",
        "tests/schemas/operator_verdict/test_section_05_5_shape.py",
        "tests/schemas/operator_verdict/test_section_07b_shape.py",
        "tests/schemas/operator_verdict/test_section_07d_shape.py",
        "tests/schemas/operator_verdict/test_section_07f_shape.py",
    ),
    "G3": (
        "tests/parity/test_decision_card_g3_shape.py",
        "tests/schemas/operator_verdict/test_section_08b_shape.py",
    ),
    "G4": (
        "tests/parity/test_decision_card_g4_shape.py",
        "tests/schemas/operator_verdict/test_section_11_shape.py",
        "tests/schemas/operator_verdict/test_section_11b_shape.py",
    ),
    "Override": (
        "app/models/decision_cards/override_event.py",
        "tests/parity/test_decision_card_base_shape.py",
    ),
}


@dataclass(frozen=True)
class ShapeAuditSnapshot:
    shape_pin_assertion_count: int
    class_conformance_count: int
    gap_descriptors: tuple[str, ...]
    validator_stdout: str

    @property
    def gap_count(self) -> int:
        return len(self.gap_descriptors)


def _test_function_count(path: Path) -> int:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    )


def _shape_pin_assertion_count() -> int:
    parity_paths = [
        path
        for path in (REPO_ROOT / "tests" / "parity").glob("test_decision_card_*_shape.py")
        if path.name != "test_decision_card_base_shape.py"
    ]
    operator_paths = sorted(
        (REPO_ROOT / "tests" / "schemas" / "operator_verdict").glob("test_*_shape.py")
    )
    return sum(_test_function_count(path) for path in [*parity_paths, *operator_paths])


def _validator_counts() -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), "tests/parity"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    match = re.search(
        r"\((?P<activation>\d+) activation \+ (?P<shape>\d+) decision-card shape-pin\)",
        result.stdout,
    )
    assert match is not None, result.stdout
    return int(match.group("activation")), result.stdout.strip()


def _coverage_gaps() -> tuple[str, ...]:
    gaps: list[str] = []
    for family, rel_paths in FAMILY_EVIDENCE_FILES.items():
        text = "\n".join(
            (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            for rel_path in rel_paths
        )
        for dimension, tokens in DIMENSION_TOKENS.items():
            if not any(token in text for token in tokens):
                gaps.append(f"{family}:{dimension}")
    return tuple(sorted(gaps))


def _audit_snapshot() -> ShapeAuditSnapshot:
    class_conformance_count, validator_stdout = _validator_counts()
    return ShapeAuditSnapshot(
        shape_pin_assertion_count=_shape_pin_assertion_count(),
        class_conformance_count=class_conformance_count,
        gap_descriptors=_coverage_gaps(),
        validator_stdout=validator_stdout,
    )


def test_shape_pin_and_class_conformance_floors_are_met() -> None:
    snapshot = _audit_snapshot()

    assert snapshot.shape_pin_assertion_count >= EXPECTED_SHAPE_PIN_FLOOR
    assert snapshot.class_conformance_count >= EXPECTED_CLASS_CONFORMANCE_FLOOR
    assert snapshot.gap_count < TW_7C_1_FIRE_GAP_FLOOR, snapshot.gap_descriptors


def test_expected_family_dimension_pairs_have_shape_evidence() -> None:
    snapshot = _audit_snapshot()

    assert snapshot.gap_descriptors == ()


def test_audit_is_deterministic_and_read_only_for_sprint_status() -> None:
    before_digest = hashlib.sha256(SPRINT_STATUS_PATH.read_bytes()).hexdigest()
    first = _audit_snapshot()
    second = _audit_snapshot()
    after_digest = hashlib.sha256(SPRINT_STATUS_PATH.read_bytes()).hexdigest()

    assert first == second
    assert before_digest == after_digest
