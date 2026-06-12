"""PIN-G1 — manifest-wide grounding audit (dp-v1.1, party consensus 2026-06-12).

The generalized form of the ungrounded-prompt family (4 instances to date:
attempt-4 quinn_r/gary placeholders, cycle-2 irene_pass1 + cd confabulation,
cycle-4 irene Pass-2 sepsis narration): a specialist node dispatched with NO
data-plane delivery (no ``dependencies``, no ``dependency_projections``)
prompts its LLM from reference exemplars and invents content with
``provenance: real``.

Every specialist node must either declare a delivery or sit in the explicit
GROUNDLESS_ALLOWLIST below. The allowlist is shrink-only (Murat: same
discipline as the live-dispatch allowlist): adding a NEW groundless node
fails this test; grounding an allowlisted node retires its row. Rows for
currently-unexercised downstream seams (§11-§15) carry follow-ons in
deferred-inventory rather than in-batch hardening (John scope ruling —
don't harden seams the trial cannot reach yet).
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"

# (node_id, declared specialist_id) — every specialist node with no
# data-plane delivery as of dp-v1.1. Each row is either (a) an orchestration
# or gate-ceremony node whose act is not content-generating, (b) a seam-fed
# node (texas 02/03 receive directive/bundle paths via the runner-supplied
# payload seam), or (c) a downstream seam past the current trial frontier.
GROUNDLESS_ALLOWLIST: frozenset[tuple[str, str]] = frozenset(
    {
        ("01", "marcus"),
        ("02", "texas"),
        ("02A", "marcus"),
        ("03", "texas"),
        ("04", "vera"),
        ("04.5", "marcus"),
        ("04.55", "marcus"),
        ("06", "marcus"),
        ("6.2", "marcus"),
        ("6.3", "marcus"),
        ("06B", "marcus"),
        ("07C", "quinn-r"),
        ("07D", "marcus"),
        ("07F", "quinn-r"),
        ("09", "marcus"),
        ("10", "vera"),
        # dp-v1.2 (audio-arc 2026-06-12): rows (12, elevenlabs),
        # (13, quinn-r), (14, compositor) RETIRED — grounded via
        # projections. (11, elevenlabs) ADDED: its dead quarantined
        # upstream_output edge was removed; the voice-selection leg is
        # config/HIL-only (no content inputs; G4A folds into G4 — voice
        # HIL rider filed). (11B, elevenlabs) stays: all three elevenlabs
        # nodes share one act body — projecting narration into 11B would
        # synthesize audio twice.
        ("11", "elevenlabs"),
        ("11B", "elevenlabs"),
        ("15", "marcus"),
    }
)


def _groundless_nodes() -> set[tuple[str, str]]:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    groundless: set[tuple[str, str]] = set()
    for node in manifest["nodes"]:
        specialist = node.get("specialist_id")
        if not specialist:
            continue
        if node.get("dependencies") or node.get("dependency_projections"):
            continue
        groundless.add((str(node["id"]), str(specialist)))
    return groundless


def test_no_new_groundless_specialist_nodes() -> None:
    groundless = _groundless_nodes()
    new_nodes = groundless - GROUNDLESS_ALLOWLIST
    assert new_nodes == set(), (
        f"NEW specialist node(s) with no data-plane delivery: {sorted(new_nodes)} "
        "— declare dependencies/dependency_projections (the ungrounded-prompt "
        "family is 4-for-4 on producing confabulated content) or add a "
        "deliberate allowlist row with rationale."
    )


def test_allowlist_is_shrink_only() -> None:
    groundless = _groundless_nodes()
    retired = GROUNDLESS_ALLOWLIST - groundless
    assert retired == set(), (
        f"Allowlist row(s) no longer groundless: {sorted(retired)} — remove "
        "them from GROUNDLESS_ALLOWLIST (shrink-only discipline)."
    )


def test_grounded_frontier_nodes_stay_grounded() -> None:
    """The four seams the family already burned must never re-enter the
    allowlist: 04A/05/05B (irene_pass1), 4.75 (cd), 07 (gary), 08 (irene),
    08B (quinn-r)."""
    groundless = {node_id for node_id, _ in _groundless_nodes()}
    for node_id in ("04A", "05", "05B", "4.75", "07", "08", "08B"):
        assert node_id not in groundless, (
            f"node {node_id} lost its data-plane delivery — this re-opens a "
            "confirmed confabulation seam"
        )
