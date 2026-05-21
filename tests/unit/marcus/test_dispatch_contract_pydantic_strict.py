from __future__ import annotations

import pytest

from app.marcus.dispatch.contract import DispatchEnvelope, DispatchReceipt


@pytest.mark.parametrize("model_cls", [DispatchEnvelope, DispatchReceipt])
def test_dispatch_contract_models_are_strict(model_cls: type[object]) -> None:
    config = model_cls.model_config
    assert config.get("extra") == "forbid"
    assert config.get("validate_assignment") is True
