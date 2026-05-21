"""Shared fixtures for the transport-parity test lane (Slab 1 Story 1.1d).

These tests run on a nightly / on-merge cadence — NOT per-PR — per the
2026-04-22 middle-path consensus on MCP-in-Slab-1. Select the lane via
``pytest -m transport_parity``; deselect via ``-m 'not transport_parity'``.

The `minimal_node_fixture` returns a direct module reference to
`app.runtime.minimal_node`. It exists so the parity tests rely on the
import-boundary contract (any future drift between transports is caught
by the fact that all three transports import the SAME module) rather than
a re-implementation at the test site.
"""

from __future__ import annotations

import types

import pytest

from app.runtime import minimal_node as _minimal_node_module


@pytest.fixture(scope="session")
def minimal_node_fixture() -> types.ModuleType:
    """Return the literal `app.runtime.minimal_node` module.

    Test bodies access ``minimal_node_fixture.minimal_node`` and
    ``minimal_node_fixture.MINIMAL_NODE_NAME`` through this single import
    boundary. Re-implementing the no-op behavior in a test fixture would
    silently break the parity contract; do NOT do that.
    """
    return _minimal_node_module
