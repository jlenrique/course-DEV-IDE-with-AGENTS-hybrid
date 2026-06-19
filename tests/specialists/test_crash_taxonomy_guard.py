"""Crash-taxonomy guard (BETA S0.1; charter D6 / Murat G-Q3).

Trial-4 crashed at node 07B because `ModeMismatchError` was a bare ValueError —
outside the `SpecialistDispatchError` family the runner catches to error-pause.
A crash is unrecoverable + non-resumable; it converts a survivable event into a
dead run. This guard pins that the known mid-walk failure families route to
error-pause (i.e. derive from `SpecialistDispatchError`), so a future regression
that reintroduces a bare-crash family fails CI here rather than at a live trial.
"""

from __future__ import annotations

import pytest

from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.irene_pass1._act import ModeMismatchError as IreneModeMismatchError
from app.specialists.quinn_r._act import ModeMismatchError as QuinnModeMismatchError

# Mode-resolution families that MUST error-pause (were/would-be bare crashes).
_MODE_FAMILIES = [
    QuinnModeMismatchError,
    IreneModeMismatchError,
]


@pytest.mark.parametrize("err_cls", _MODE_FAMILIES)
def test_mode_family_is_dispatch_error(err_cls: type[Exception]) -> None:
    """Each mode-mismatch family derives from SpecialistDispatchError so the
    production runner's `except SpecialistDispatchError -> _pause_at_error`
    catches it (recoverable via `trial recover`) instead of crashing the walk."""
    assert issubclass(err_cls, SpecialistDispatchError)


@pytest.mark.parametrize("err_cls", _MODE_FAMILIES)
def test_mode_family_carries_tag(err_cls: type[Exception]) -> None:
    """A raised instance carries a non-empty `tag` (the error-pause records it)."""
    exc = err_cls("boom")
    assert getattr(exc, "tag", "")  # truthy tag
    assert isinstance(exc.tag, str) and exc.tag


def test_quinn_mode_mismatch_keeps_valueerror_semantics() -> None:
    """Dual-base preserves the historic `except ValueError` / pytest.raises(ValueError)
    callers (Quinn-R only — it was the ValueError-typed one)."""
    assert issubclass(QuinnModeMismatchError, ValueError)
    with pytest.raises(ValueError):
        raise QuinnModeMismatchError("still a ValueError")


def test_irene_mode_mismatch_keeps_runtimeerror_semantics() -> None:
    """Irene Pass-1's family was RuntimeError-typed; SpecialistDispatchError is
    RuntimeError-derived, so that contract is preserved."""
    assert issubclass(IreneModeMismatchError, RuntimeError)


def test_dispatch_error_base_requires_tag() -> None:
    """The base contract: SpecialistDispatchError takes a keyword-only tag."""
    exc = SpecialistDispatchError("msg", tag="some.tag")
    assert exc.tag == "some.tag"
