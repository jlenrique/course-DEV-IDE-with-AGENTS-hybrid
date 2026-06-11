"""Trial-3 finding #10 defect pins — Quinn-R G2B/G2F gate coverage.

Attempt-4 first resume (2026-06-11) crashed at the first-ever live Quinn-R
dispatch (§07B variant selection, open throttle): production dispatch
supplied no gate context AND GATE_MODES lacked G2B/G2F entirely. Two-layer
fix: the runner threads the manifest node's gate_code via the A-R3 Option-A
runner_supplied_payload seam, and Quinn-R gains dedicated minimal bodies for
G2B (variant-selection) and G2F (motion-gate).

Fourth A23/P5 instance in the trial-launch arc ("tested module, untested
integration"); the manifest-coverage test below pins against a fifth.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from app.marcus.orchestrator.production_runner import _runner_payload_for_specialist
from app.specialists.quinn_r._act import GATE_MODES
from app.specialists.quinn_r.graph import ModeMismatchError, _act
from tests.specialists.quinn_r.conftest import make_state

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"


def test_empty_gate_context_still_fails_loud() -> None:
    """Pins the finding-#10 crash signature: trial-level cache_prefix carries
    no gate keys; Quinn-R must keep refusing rather than guess a body."""
    state = make_state(
        json.dumps(
            {"corpus_path": "x", "preset": "production", "trial_id": "t"}
        )
    )
    with pytest.raises(ModeMismatchError):
        _act(state)


def test_g2b_variant_selection_body_approves_without_storyboard_write(
    tmp_path: Path,
) -> None:
    payload = json.dumps(
        {
            "gate_id": "G2B",
            "runs_root": str(tmp_path),
            "slides": [{"slide_id": "s1", "selected_variant": "variant-2"}],
        }
    )
    update = _act(make_state(payload))
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["quinn_r_review"]["mode"] == "variant-selection"
    assert output["quinn_r_review"]["status"] == "approved"
    assert output["quinn_r_review"]["selections"] == [
        {"slide_id": "s1", "selected_variant": "variant-2"}
    ]
    # G2B must NOT emit the G2C artifact — a premature authorized-storyboard
    # at §07B would pollute artifact provenance before G2C approval.
    assert not list(tmp_path.rglob("authorized-storyboard.json"))


def test_g2f_motion_gate_body_reviews_zero_assets(tmp_path: Path) -> None:
    update = _act(
        make_state(json.dumps({"gate_id": "G2F", "runs_root": str(tmp_path)}))
    )
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["quinn_r_review"] == {
        "mode": "motion-gate",
        "status": "reviewed",
        "motion_assets_reviewed": 0,
    }


def test_gate_modes_cover_every_quinn_r_manifest_gate() -> None:
    """Lockstep pin: every manifest node dispatching quinn-r with a gate_code
    must have a GATE_MODES entry — prevents the next first-live-dispatch
    crash when the manifest grows a Quinn-R gate."""
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    quinn_gates = {
        node.get("gate_code")
        for node in manifest["nodes"]
        if node.get("specialist_id") == "quinn-r" and node.get("gate_code")
    }
    missing = sorted(quinn_gates - set(GATE_MODES))
    assert missing == [], (
        f"Quinn-R manifest gates without GATE_MODES coverage: {missing}"
    )


def test_runner_payload_supplies_gate_id_for_quinn_r_only() -> None:
    assert _runner_payload_for_specialist(
        specialist_id="quinn-r",
        directive_path=None,
        bundle_dir=None,
        gate_code="G2B",
    ) == {"gate_id": "G2B"}
    # No gate_code (ungated node) -> no runner payload.
    assert (
        _runner_payload_for_specialist(
            specialist_id="quinn-r",
            directive_path=None,
            bundle_dir=None,
            gate_code=None,
        )
        is None
    )
    # Non-Quinn-R specialists keep their existing contract.
    assert (
        _runner_payload_for_specialist(
            specialist_id="gary",
            directive_path=None,
            bundle_dir=None,
            gate_code="G2M",
        )
        is None
    )
