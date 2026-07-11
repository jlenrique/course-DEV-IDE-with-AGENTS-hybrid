"""Tagged errors for LiteLLM Batch transport (B1/B3)."""

from __future__ import annotations

from pathlib import Path

from app.runtime.llm_batch.receipts import BatchReceipt


class LlmBatchError(Exception):
    """Fail-loud Batch transport error with a stable tag for runners/tests."""

    def __init__(self, message: str, *, tag: str) -> None:
        super().__init__(message)
        self.tag = tag


class WaitingForProviderBatchError(RuntimeError):
    """Non-terminal provider Batch — pause the trial (B3).

    Must **not** subclass SpecialistDispatchError (that routes to paused-at-error).
    """

    def __init__(
        self,
        message: str,
        *,
        batch_id: str,
        receipt_path: Path,
        receipt: BatchReceipt,
        tag: str = "vision.batch.waiting-for-provider",
    ) -> None:
        super().__init__(message)
        self.tag = tag
        self.batch_id = batch_id
        self.receipt_path = receipt_path
        self.receipt = receipt


__all__ = ["LlmBatchError", "WaitingForProviderBatchError"]
