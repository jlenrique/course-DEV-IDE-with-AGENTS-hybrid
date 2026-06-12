"""S0 fail-loud policy ratchet — SCP 2026-06-11 segment-data-plane.

Party-mode unanimous ruling (Murat #3, Winston C-1, operator-ratified):
absence of inputs is a contract violation, never a mode switch. Every
dispatch seam must RAISE on missing inputs; fixture mode is reachable only
via explicit ``allow_fixture=True`` opt-in that production code never sets.

Trial-3 attempt-4 evidence: gary's silent fixture fallback put placeholder
slides into a production envelope; vera PROCEED'd over them and quinn_r
approved them — three of six contributions were quality theater. Prior
strikes in the same arc: texas cwd fallback (finding #2), exit-10 invented
semantics (finding #3).
"""

from __future__ import annotations

import pytest

from app.specialists.gary.gamma_dispatch import GammaDispatchError, dispatch_to_gamma
from app.specialists.kira.kling_dispatch import KlingDispatchError, dispatch_to_kling
from app.specialists.quinn_r.sensory_bridges_dispatch import (
    SensoryBridgeDispatchError as QuinnSensoryError,
)
from app.specialists.quinn_r.sensory_bridges_dispatch import (
    dispatch_to_sensory_bridges as quinn_sensory_dispatch,
)
from app.specialists.texas._act import BundleDispatchError
from app.specialists.texas.retrieval_dispatch import dispatch_retrieval
from app.specialists.vera.sensory_bridges_dispatch import (
    SensoryBridgeDispatchError as VeraSensoryError,
)
from app.specialists.vera.sensory_bridges_dispatch import (
    dispatch_to_sensory_bridges as vera_sensory_dispatch,
)


class TestMissingInputRaises:
    """The seam must refuse, not invent. One case per dispatch seam."""

    def test_gary_gamma_raises_not_fixture(self) -> None:
        with pytest.raises(GammaDispatchError) as excinfo:
            dispatch_to_gamma(directive_path=None, export_dir=None)
        assert excinfo.value.tag == "gamma.input.missing"

    def test_texas_retrieval_raises_not_fixture(self) -> None:
        with pytest.raises(BundleDispatchError) as excinfo:
            dispatch_retrieval(directive_path=None, bundle_dir=None)
        assert excinfo.value.tag == "bundle.dispatch.input-missing"

    def test_kira_kling_raises_not_fixture(self) -> None:
        with pytest.raises(KlingDispatchError) as excinfo:
            dispatch_to_kling(
                kling_prompt="pan", model_name="kling-v1", mode="std", duration=5.0
            )
        assert excinfo.value.tag == "kling.input.missing"

    def test_vera_sensory_raises_not_fixture(self) -> None:
        with pytest.raises(VeraSensoryError) as excinfo:
            vera_sensory_dispatch(
                artifact_path=None,
                source_of_truth_path=None,
                modality="image",
                gate="fidelity",
            )
        assert excinfo.value.tag == "sensory.input.missing"

    def test_quinn_r_sensory_raises_not_fixture(self) -> None:
        with pytest.raises(QuinnSensoryError) as excinfo:
            quinn_sensory_dispatch(artifact_path=None, modality="image", gate="qrr")
        assert excinfo.value.tag == "sensory.input.missing"


class TestFixtureRequiresExplicitOptIn:
    """allow_fixture=True (test-harness only) preserves deterministic paths."""

    def test_gary_fixture_optin(self) -> None:
        receipt = dispatch_to_gamma(
            directive_path=None, export_dir=None, allow_fixture=True
        )
        assert receipt["generation_id"] == "gen-fixture-001"

    def test_texas_fixture_optin(self) -> None:
        receipt = dispatch_retrieval(
            directive_path=None, bundle_dir=None, allow_fixture=True
        )
        assert receipt["status"] == "mocked"

    def test_kira_fixture_optin(self) -> None:
        receipt = dispatch_to_kling(
            kling_prompt="pan",
            model_name="kling-v1",
            mode="std",
            duration=5.0,
            allow_fixture=True,
        )
        assert receipt["status"] == "mocked"

    def test_vera_sensory_fixture_optin(self) -> None:
        out = vera_sensory_dispatch(
            artifact_path=None,
            source_of_truth_path=None,
            modality="image",
            gate="fidelity",
            allow_fixture=True,
        )
        assert out["confidence"] == "LOW"

    def test_quinn_r_sensory_fixture_optin(self) -> None:
        out = quinn_sensory_dispatch(
            artifact_path=None, modality="image", gate="qrr", allow_fixture=True
        )
        assert out["confidence"] == "LOW"


def test_production_runner_never_sets_allow_fixture() -> None:
    """Static pin: the production dispatch path must not opt into fixtures."""
    import inspect

    import app.marcus.orchestrator.dispatch_adapter as adapter_module
    import app.marcus.orchestrator.production_runner as runner_module

    for module in (runner_module, adapter_module):
        assert "allow_fixture" not in inspect.getsource(module), (
            f"{module.__name__} must never set allow_fixture"
        )
