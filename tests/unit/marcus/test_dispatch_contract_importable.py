from __future__ import annotations


def test_dispatch_contract_import_paths_share_identity() -> None:
    from app.marcus.dispatch import contract as app_contract
    from app.marcus.dispatch import contract as root_contract

    assert root_contract.DispatchKind is app_contract.DispatchKind
    assert root_contract.DispatchOutcome is app_contract.DispatchOutcome
    assert root_contract.DispatchEnvelope is app_contract.DispatchEnvelope
    assert root_contract.DispatchReceipt is app_contract.DispatchReceipt
    assert root_contract.DispatchKind.TEXAS_RETRIEVAL.value == "texas_retrieval"
    assert root_contract.DispatchOutcome.COMPLETE.value == "complete"
    assert root_contract.DispatchOutcome.PARTIAL.value == "partial"
    assert root_contract.DispatchOutcome.FAILED.value == "failed"
