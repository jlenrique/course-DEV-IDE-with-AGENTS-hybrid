"""BETA S0.4 flake-budget (T5a-F2): bounded auto-retry for LLM-variance tags.

Irene pass-2 perception_source join failed first-roll across Trial-4 + both T5a
runs (the rerun needed 3 re-rolls). A retryable-tagged variance must be absorbed
automatically (no operator-manual recover) within a bounded budget; a
non-retryable / deterministic tag must still fail loud immediately.
"""

from __future__ import annotations

import pytest

from app.marcus.orchestrator import production_runner as pr
from app.specialists.dispatch_errors import SpecialistDispatchError


class _FlakyAdapter:
    """Raises a given tag `fail_times`, then returns a sentinel envelope."""

    def __init__(self, tag: str, fail_times: int) -> None:
        self.tag = tag
        self.fail_times = fail_times
        self.calls = 0

    def invoke_specialist(self, **_kwargs):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise SpecialistDispatchError("variance", tag=self.tag)
        return "ENVELOPE_OK"


def test_retryable_tag_absorbed_within_budget() -> None:
    # irene needed 3 re-rolls in the T5a rerun — within the budget (1 + 3).
    adapter = _FlakyAdapter("irene.pass2.slide-join-failed", fail_times=3)
    result = pr._invoke_specialist_with_retry(adapter, {}, "08")
    assert result == "ENVELOPE_OK"
    assert adapter.calls == 4  # 3 failures + 1 success


def test_retryable_tag_exceeding_budget_fails_loud() -> None:
    adapter = _FlakyAdapter("irene.pass2.slide-join-failed", fail_times=99)
    with pytest.raises(SpecialistDispatchError) as exc:
        pr._invoke_specialist_with_retry(adapter, {}, "08")
    assert exc.value.tag == "irene.pass2.slide-join-failed"
    assert adapter.calls == 1 + pr._MAX_DISPATCH_RETRIES  # bounded


def test_non_retryable_tag_fails_immediately() -> None:
    # a deterministic substrate defect must NOT be retried (fail-loud preserved).
    # Note: gamma.export.brief-unmatched is intentionally RETRYABLE (LLM variance);
    # use a deterministic tag outside _RETRYABLE_DISPATCH_TAGS.
    adapter = _FlakyAdapter("cd.directive.malformed", fail_times=1)
    with pytest.raises(SpecialistDispatchError):
        pr._invoke_specialist_with_retry(adapter, {}, "07")
    assert adapter.calls == 1  # no retry


def test_gamma_brief_unmatched_is_retryable() -> None:
    """gamma.export.brief-unmatched is LLM-variance class — absorbed in budget."""
    adapter = _FlakyAdapter("gamma.export.brief-unmatched", fail_times=1)
    assert pr._invoke_specialist_with_retry(adapter, {}, "07") == "ENVELOPE_OK"
    assert adapter.calls == 2


def test_desmond_advisory_missing_is_retryable() -> None:
    """handoff.parsed.advisory-missing is LLM heading variance — absorbed in budget."""
    adapter = _FlakyAdapter("handoff.parsed.advisory-missing", fail_times=1)
    assert pr._invoke_specialist_with_retry(adapter, {}, "14.5") == "ENVELOPE_OK"
    assert adapter.calls == 2


def test_happy_path_no_retry() -> None:
    adapter = _FlakyAdapter("irene.pass2.slide-join-failed", fail_times=0)
    assert pr._invoke_specialist_with_retry(adapter, {}, "08") == "ENVELOPE_OK"
    assert adapter.calls == 1
