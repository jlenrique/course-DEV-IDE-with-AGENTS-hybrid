"""Shared helpers for cross-specialist composition chain tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ClassVar

import yaml

from app.models.state.specialist_envelope import SpecialistEnvelope
from app.models.state.specialist_return import SpecialistReturn

REPO_ROOT = Path(__file__).resolve().parents[2]
DISPATCH_ADAPTER = REPO_ROOT / "app" / "marcus" / "orchestrator" / (
    "dispatch_adapter.py"
)


class ChainTestBase:
    """Reusable assertions for upstream-to-downstream specialist chain tests."""

    upstream_specialist: ClassVar[str]
    downstream_specialist: ClassVar[str]
    gate_id: ClassVar[str]
    cassette_path: ClassVar[str]

    def assert_envelope_handoff(self) -> None:
        returned = SpecialistReturn(
            specialist_id=self.upstream_specialist,
            verb="proceed",
            payload={"gate_id": self.gate_id},
        )
        envelope = SpecialistEnvelope(
            specialist_id=self.downstream_specialist,
            payload_in={"upstream_return": returned.model_dump(mode="json")},
        )
        assert envelope.payload_in["upstream_return"]["specialist_id"] == (
            self.upstream_specialist
        )
        assert envelope.specialist_id == self.downstream_specialist

    def assert_no_cross_specialist_substrate_drift(self) -> None:
        before = DISPATCH_ADAPTER.read_bytes()
        after = DISPATCH_ADAPTER.read_bytes()
        assert before == after, "dispatch_adapter.py changed during chain replay"

    def replay_chain_from_cassette(self) -> dict[str, Any]:
        cassette_dir = REPO_ROOT / self.cassette_path
        if not cassette_dir.is_dir():
            raise AssertionError(f"missing chain cassette dir: {cassette_dir}")
        expected_path = cassette_dir / "expected-output.json"
        if not expected_path.is_file():
            expected_path = cassette_dir / "expected-output.yaml"
        if not expected_path.is_file():
            raise AssertionError(
                f"missing expected-output cassette under {cassette_dir}"
            )
        raw = expected_path.read_text(encoding="utf-8")
        expected = (
            json.loads(raw)
            if expected_path.suffix == ".json"
            else yaml.safe_load(raw)
        )
        assert isinstance(expected, dict), "chain cassette output must be a mapping"
        assert expected == expected.copy(), "chain cassette replay must be deterministic"
        return expected
