"""Shared fixtures for marcus integration suites."""

from __future__ import annotations

import pytest

from app.marcus.orchestrator import storyboard_publisher


@pytest.fixture(autouse=True)
def storyboard_publish_calls(request, monkeypatch):
    """Stub the online storyboard publisher for runner-walk tests.

    S5 criterion 7 wired the publisher into the live G2C pause path; these
    suites exercise walk/gate mechanics with fake adapters and must not hit
    the real generate+publish (GitHub Pages) machinery. The stub records
    calls so wiring tests can assert the runner invoked it.

    The publisher's OWN suite (test_storyboard_publisher.py) is exempt —
    it tests the real module surface directly.
    """
    if "test_storyboard_publisher" in request.node.nodeid:
        yield None
        return
    calls: list[dict] = []

    def _record(**kwargs):
        calls.append(kwargs)
        return None

    monkeypatch.setattr(
        storyboard_publisher, "publish_storyboard_for_gate", _record
    )
    yield calls
