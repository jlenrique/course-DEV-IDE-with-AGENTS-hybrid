from __future__ import annotations

import ast
import importlib
import re
import subprocess
import sys
from pathlib import Path

from app.parity.contracts import iter_sanctum_alignments
from app.parity.contracts._sanctum import _clear_sanctum_alignments_for_tests

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_sg1_class_conformance_validator_reports_expected_floor() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts/utilities/validate_parity_test_class_conformance.py"),
            "tests/parity/",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    match = re.search(r"PASS: (\d+) parity contract file", result.stdout)
    assert match, result.stdout
    assert int(match.group(1)) >= 19
    assert "11 activation" in result.stdout


def test_sg2_mapping_checklist_floor_is_enforced() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/parity/test_mapping_checklist_status.py",
            "-p",
            "no:randomly",
            "-q",
            "--tb=short",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_sg3_composition_spec_sha256_append_only_shape_is_present() -> None:
    spec_text = (REPO_ROOT / "docs/dev-guide/composition-specification.md").read_text(
        encoding="utf-8"
    )
    assert "SHA256 of canonical JSON" in spec_text
    assert "append-only" in spec_text.lower()

    writer_path = REPO_ROOT / "app/marcus/orchestrator/writers/outbound_envelope.py"
    tree = ast.parse(writer_path.read_text(encoding="utf-8"))
    class_names = {node.name for node in tree.body if isinstance(node, ast.ClassDef)}
    assert "GaryOutboundEnvelope" in class_names
    source = writer_path.read_text(encoding="utf-8")
    for token in ("schema_version", "yaml.safe_dump", "sort_keys=True", "write_text"):
        assert token in source


def test_sg4_sanctum_alignment_registry_has_six_writer_ids() -> None:
    _clear_sanctum_alignments_for_tests()
    for module_name in (
        "app.marcus.orchestrator.writers.slide_content",
        "app.marcus.orchestrator.writers.fidelity_slides",
        "app.marcus.orchestrator.writers.diagram_cards",
        "app.marcus.orchestrator.writers.theme_resolution",
        "app.marcus.orchestrator.writers.outbound_envelope",
        "app.marcus.orchestrator.writers.section_15_bundle",
    ):
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)

    writer_ids = [alignment.writer_id for alignment in iter_sanctum_alignments()]
    assert writer_ids == [
        "gary-diagram-cards",
        "gary-fidelity-slides",
        "gary-outbound-envelope",
        "gary-slide-content",
        "gary-theme-resolution",
        "section-15-bundle",
    ]
