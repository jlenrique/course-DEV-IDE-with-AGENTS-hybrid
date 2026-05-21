from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "tests" / "_smoke_suite_manifest.json"
META = REPO_ROOT / "tests" / "_smoke_suite_manifest.json.meta"


def _manifest_nodeids() -> list[str]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert all(isinstance(item, str) for item in data)
    return data


def test_smoke_suite_manifest_shape_and_cardinality() -> None:
    nodeids = _manifest_nodeids()
    assert 150 <= len(nodeids) <= 250
    assert len(nodeids) == len(set(nodeids))
    assert all("::" in nodeid for nodeid in nodeids)
    assert META.is_file()


def test_smoke_suite_manifest_paths_exist() -> None:
    for nodeid in _manifest_nodeids():
        path_part = nodeid.split("::", 1)[0]
        assert (REPO_ROOT / path_part).is_file(), nodeid


def test_smoke_suite_manifest_load_bearing_coverage_spot_check() -> None:
    joined = "\n".join(_manifest_nodeids())
    required_fragments = [
        "test_tripwire_ledger_entry_shape.py",
        "test_override_event_chain_integrity.py",
        "test_acceptance_criteria_schema_stable.py",
        "test_tracy_to_texas_chain.py",
        "test_pre_gate_marcus_precedence_unaltered.py",
        "test_shim_basic_invocation.py",
        "activation_contract.py",
    ]
    for fragment in required_fragments:
        assert fragment in joined


def test_smoke_suite_manifest_invokable_via_smoke_option() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--smoke",
            "-n0",
            "-p",
            "no:randomly",
            "-q",
            "--tb=short",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr
