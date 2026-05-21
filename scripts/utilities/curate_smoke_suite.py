"""Curate the Slab 7c R2 smoke-suite manifest.

Canonical methodology from Story 7c.0c / AMEND-V2:

1. Run `pytest --durations=0 --co --cov=app --cov-report=json` against the
   full suite.
2. Score each test as `(covered_lines * not_already_covered) / wall_clock`.
3. Rank descending and take the top 200 tests.
4. Manually spot-check that load-bearing modules are represented:
   substrate-shape, retrieval contract, party-mode / gate-loop, schema
   validators, and activation-contract class conformance.
5. Re-run this script at each Slab 7c wave close so the R2 tier tracks added
   coverage.

The current project does not emit per-test coverage in a machine-readable form
without adding dependencies. This helper keeps the canonical target documented
and applies a deterministic zero-dependency approximation over collected node
ids: exclude known red/live/serial nodes, seed the required load-bearing areas,
then fill by path-weighted buckets that favor fast structural, parity, contract,
composition, retrieval, and runtime smoke tests.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
NODEIDS_CACHE = REPO_ROOT / ".pytest_cache" / "v" / "cache" / "nodeids"
LASTFAILED_CACHE = REPO_ROOT / ".pytest_cache" / "v" / "cache" / "lastfailed"
MANIFEST_PATH = REPO_ROOT / "tests" / "_smoke_suite_manifest.json"
META_PATH = REPO_ROOT / "tests" / "_smoke_suite_manifest.json.meta"
CURATION_VERSION = "7c.0c-v1"
TARGET_COUNT = 200

LOAD_BEARING_SEEDS = [
    "tests/parity/test_tripwire_ledger_entry_shape.py::test_schema_required_fields_are_exactly_pinned",
    "tests/parity/test_tripwire_ledger_entry_shape.py::test_validate_assignment_true_rejects_invalid_mutation",
    "tests/audit/test_override_event_chain_integrity.py::test_append_only_three_entry_ledger_succeeds",
    "tests/contracts/test_acceptance_criteria_schema_stable.py::test_retrieval_intent_fields_match_snapshot",
    "tests/contracts/test_retrieval_adapter_base.py::test_adapter_protocol_accepts_fake_provider",
    "tests/contracts/test_provider_directory_roster_placeholders.py::test_roster_placeholder_present_with_expected_status[scite-retrieval-ratified]",
    "tests/composition/test_tracy_to_texas_chain.py::TestTracyToTexasChain::test_retrieval_intent_shape_is_texas_compatible",
    "tests/composition/test_tracy_to_texas_chain.py::TestTracyToTexasChain::test_texas_dispatch_signature_accepts_directive_and_bundle_paths",
    "tests/composition/test_pre_gate_marcus_precedence_unaltered.py::test_pre_gate_marcus_does_not_promote_per_specialist_gates",
    "tests/cli/test_shim_basic_invocation.py::test_shim_main_success_invokes_resume_and_returns_zero[app.marcus.cli.gate_shims.g1_shim-G1]",
    "tests/parity/test_texas_activation_contract.py::TestTexasActivationContract::test_cold_activation_smoke",
    "tests/parity/test_quinn_r_activation_contract.py::TestQuinnRActivationContract::test_cold_activation_smoke",
    "tests/parity/test_vera_activation_contract.py::TestVeraActivationContract::test_cold_activation_smoke",
    "tests/parity/test_irene_pass1_activation_contract.py::TestIrenePass1ActivationContract::test_cold_activation_smoke",
    "tests/parity/test_tracy_activation_contract.py::TestTracyActivationContract::test_cold_activation_smoke",
    "tests/parity/test_gary_activation_contract.py::TestGaryActivationContract::test_cold_activation_smoke",
    "tests/parity/test_kira_activation_contract.py::TestKiraActivationContract::test_cold_activation_smoke",
    "tests/parity/test_enrique_activation_contract.py::TestEnriqueActivationContract::test_cold_activation_smoke",
    "tests/parity/test_wanda_activation_contract.py::TestWandaActivationContract::test_cold_activation_smoke",
    "tests/parity/test_dan_activation_contract.py::TestDanActivationContract::test_cold_activation_smoke",
    "tests/parity/test_compositor_activation_contract.py::TestCompositorActivationContract::test_cold_activation_smoke",
]

EXCLUDED_PREFIXES = (
    "tests/live/",
    "tests/end_to_end/",
    "tests/integration/replay/",
    "tests/integration/postgres/",
    "tests/integration/transport_parity/",
)

BUCKET_WEIGHTS = (
    ("tests/parity/test_", 0),
    ("tests/structural/test_", 1),
    ("tests/contracts/test_", 2),
    ("tests/composition/test_", 3),
    ("tests/audit/test_", 4),
    ("tests/cli/test_", 5),
    ("tests/unit/", 6),
    ("tests/specialists/texas/", 7),
    ("tests/agents/bmad-agent-texas/", 8),
    ("tests/integration/manifest/", 9),
    ("tests/integration/runtime/", 10),
)


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _collect_nodeids() -> list[str]:
    if NODEIDS_CACHE.is_file():
        return list(_load_json(NODEIDS_CACHE, []))
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-n0", "-p", "no:randomly", "--collect-only", "-q"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode not in {0, 5}:
        raise RuntimeError(result.stderr)
    return [line.strip() for line in result.stdout.splitlines() if "::" in line]


def _lastfailed_nodeids() -> set[str]:
    data = _load_json(LASTFAILED_CACHE, {})
    return {nodeid for nodeid, failed in data.items() if failed}


def _bucket(nodeid: str) -> int:
    for prefix, weight in BUCKET_WEIGHTS:
        if nodeid.startswith(prefix):
            return weight
    return 50


def _eligible(nodeid: str, lastfailed: set[str]) -> bool:
    if nodeid in lastfailed:
        return False
    if any(nodeid.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return False
    return not ("/live/" in nodeid or "\\live\\" in nodeid)


def curate_manifest(target_count: int = TARGET_COUNT) -> list[str]:
    nodeids = _collect_nodeids()
    nodeid_set = set(nodeids)
    lastfailed = _lastfailed_nodeids()
    eligible = [nodeid for nodeid in nodeids if _eligible(nodeid, lastfailed)]

    selected: list[str] = []
    for nodeid in LOAD_BEARING_SEEDS:
        if nodeid in nodeid_set and _eligible(nodeid, lastfailed):
            selected.append(nodeid)

    selected_set = set(selected)
    ranked = sorted(
        (nodeid for nodeid in eligible if nodeid not in selected_set),
        key=lambda value: (_bucket(value), value),
    )
    selected.extend(ranked[: max(0, target_count - len(selected))])
    return selected[:target_count]


def write_manifest(nodeids: list[str]) -> None:
    MANIFEST_PATH.write_text(
        json.dumps(nodeids, indent=2) + "\n",
        encoding="utf-8",
    )
    meta = {
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "curation_version": CURATION_VERSION,
        "manifest_path": MANIFEST_PATH.relative_to(REPO_ROOT).as_posix(),
        "count": len(nodeids),
        "python": sys.version.split()[0],
        "source": {
            "nodeids_cache": NODEIDS_CACHE.relative_to(REPO_ROOT).as_posix(),
            "lastfailed_cache": LASTFAILED_CACHE.relative_to(REPO_ROOT).as_posix(),
        },
        "methodology": "deterministic zero-dependency approximation of coverage-per-second ranking",
    }
    META_PATH.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-count", type=int, default=TARGET_COUNT)
    parser.add_argument("--check", action="store_true", help="Validate without writing.")
    args = parser.parse_args()

    nodeids = curate_manifest(target_count=args.target_count)
    if not 150 <= len(nodeids) <= 250:
        raise SystemExit(f"smoke manifest cardinality out of bounds: {len(nodeids)}")
    if args.check:
        print(f"manifest candidates: {len(nodeids)}")
        return 0
    write_manifest(nodeids)
    print(f"wrote {MANIFEST_PATH.relative_to(REPO_ROOT).as_posix()} ({len(nodeids)} nodeids)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
