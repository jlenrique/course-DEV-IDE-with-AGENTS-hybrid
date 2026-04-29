"""Composition Smoke gate at A2 boundary (Story 7a.7, AC-7.7-C).

Wires each terminal-gate shim → resume_production_trial stub → asserts no
raise. Mirrors 7a.1's `migration-7-1-directive-composer-composition-smoke.py`
pattern. Exit 0 = PASS.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.marcus.cli.gate_shims import g1_shim, g2c_shim, g3_shim, g4_shim  # noqa: E402

SHIMS = [
    (g1_shim, "G1"),
    (g2c_shim, "G2C"),
    (g3_shim, "G3"),
    (g4_shim, "G4"),
]


def _stub_envelope() -> MagicMock:
    env = MagicMock()
    env.status = "completed"
    env.paused_gate = None
    env.cost_report_path = None
    env.production_clone_launch_evidence = False
    return env


def _smoke_one(shim_module, gate_id: str) -> bool:
    trial_id = uuid4()
    with tempfile.TemporaryDirectory() as scratch:
        scratch_root = Path(scratch)
        verdict_path = scratch_root / "verdict.json"
        verdict_path.write_text(
            json.dumps(
                {
                    "verdict_id": "11111111-1111-4111-8111-111111111111",
                    "trial_id": str(trial_id),
                    "card_id": "22222222-2222-4222-8222-222222222222",
                    "verb": "approve",
                    "gate_id": gate_id,
                    "decision_card_digest": "a" * 64,
                    "operator_id": "smoke",
                    "edit_payload": None,
                    "reject_reason": None,
                    "revise_count": 0,
                    "timestamp": "2026-04-29T12:00:00Z",
                }
            ),
            encoding="utf-8",
        )

        original = shim_module.resume_production_trial
        shim_module.resume_production_trial = lambda **_: _stub_envelope()
        try:
            rc = shim_module.main(
                [
                    "--trial-id",
                    str(trial_id),
                    "--verdict-file",
                    str(verdict_path),
                    "--operator-id",
                    "smoke",
                    "--runs-root",
                    str(scratch_root / "runs"),
                ]
            )
        finally:
            shim_module.resume_production_trial = original
    return rc == 0


def main() -> int:
    results = [_smoke_one(mod, gid) for mod, gid in SHIMS]
    if all(results):
        print("PASS slab-7a A2-shims composition smoke")
        for _, gate_id in SHIMS:
            print(f"  shim {gate_id}: exit 0")
        return 0
    print("FAIL slab-7a A2-shims composition smoke")
    for (_, gid), ok in zip(SHIMS, results):
        print(f"  shim {gid}: {'PASS' if ok else 'FAIL'}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
