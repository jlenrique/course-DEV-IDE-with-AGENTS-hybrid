"""Gate-layer error types."""

from __future__ import annotations


class GateError(RuntimeError):
    """Raised when verdict resume invariants are violated."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


class SchedulerImportError(GateError):
    """Raised when gate guardrails detect scheduler-style bypass code."""

    def __init__(self, message: str) -> None:
        super().__init__("scheduler_import_forbidden", message)


class UnauthorizedResumeBypassError(GateError):
    """Raised when direct `Command(resume=...)` usage bypasses resume_api."""

    def __init__(self, message: str) -> None:
        super().__init__("unauthorized_resume_bypass", message)


__all__ = ["GateError", "SchedulerImportError", "UnauthorizedResumeBypassError"]
