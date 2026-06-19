"""Node 07B Quinn-R variant-mode gate_id resolution (Trial-4 finding T4-F4).

Arc-1a (2026-06-18) split the woken G2B gate_code off the Quinn-R evaluation
node (07B) onto the content-free ``07B-gate`` node to keep the wake pack-neutral.
That left node 07B with no gate_id, crashing Quinn-R live with
``ModeMismatchError('')`` (the offline suites never dispatched it). These tests
pin the recovery: the variant-eval node resolves its mode-selecting gate_code
from the content-free woken gate that follows it.
"""

from __future__ import annotations

from app.manifest.loader import load as load_manifest
from app.marcus.orchestrator.production_runner import (
    DEFAULT_MANIFEST_PATH,
    _effective_quinn_r_gate_code,
)


def _node(manifest, node_id: str):
    return next(node for node in manifest.nodes if node.id == node_id)


def test_node_07b_resolves_g2b_from_following_content_free_gate() -> None:
    manifest = load_manifest(DEFAULT_MANIFEST_PATH)
    node_07b = _node(manifest, "07B")
    # Precondition: 07B itself carries no gate_code (Arc-1a moved it away).
    assert not node_07b.gate_code
    # It must still resolve G2B (variant mode) from the content-free 07B-gate.
    assert _effective_quinn_r_gate_code(node_07b, manifest) == "G2B"


def test_node_07c_keeps_its_own_gate_code_g2c() -> None:
    manifest = load_manifest(DEFAULT_MANIFEST_PATH)
    node_07c = _node(manifest, "07C")
    # 07C still owns its gate_code; the helper returns it unchanged and does
    # NOT mis-borrow a sibling gate (07B-gate also follows 07B).
    assert node_07c.gate_code == "G2C"
    assert _effective_quinn_r_gate_code(node_07c, manifest) == "G2C"


def test_07b_does_not_borrow_the_sibling_content_gate_07c() -> None:
    """07C (a CONTENT gate, specialist_id=quinn-r) also has insertion_after=07B;
    the helper must pick the content-free 07B-gate (G2B), never 07C (G2C)."""
    manifest = load_manifest(DEFAULT_MANIFEST_PATH)
    assert _effective_quinn_r_gate_code(_node(manifest, "07B"), manifest) != "G2C"
