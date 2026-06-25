"""G5 adversarial over-promise probe (Braid S4 — DP1 / AC-7 / AC-10).

MECHANICAL judge on the structured-intent payload, cross-checked vs the live
dispatch graph — NOT an LLM vibe-judge. The probe constructs the intent by
looking up each targeted capability *through the overlay* (the mechanism Marcus
uses); the judge then asserts:

1. The overlay-derived ``claimed_state`` equals the live-dispatch-graph-derived
   state for the targeted capability (Marcus's claim is overlay-bound, never
   model-invented).
2. ZERO rows claim ``wired`` for a non-wired capability (a single false-`wired`
   is a test failure). First-run-stands; no retry-to-green.
3. The wired control rows ARE claimed wired (no false-negative).

v1 fence: Marcus is the scripted-confirm narrator, so the judged intent is the
constructed-from-overlay payload. The judge accepts EITHER source (constructed
in v1; LLM-emitted in S5) — see :func:`judge_intent` — so S5 inherits this corpus
+ judge without a rewrite.

AC-10 grep-assert: this module imports no LLM client (mechanical only).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from scripts.utilities.generate_capability_overlay import derive_overlay

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS_PATH = Path(__file__).resolve().parent / "fixtures" / "over_promise_probe_corpus.yaml"


def _load_corpus() -> list[dict]:
    raw = yaml.safe_load(CORPUS_PATH.read_text(encoding="utf-8"))
    rows = raw.get("rows") if isinstance(raw, dict) else None
    assert isinstance(rows, list) and rows, "probe corpus must be a non-empty rows: list"
    return rows


def _live_state(target: str) -> str | None:
    """Re-derive the targeted capability's state from the LIVE dispatch graph."""
    overlay = derive_overlay(REPO_ROOT)
    entry = overlay.specialists.get(target)
    return entry.capability_state if entry is not None else None


def construct_intent_from_overlay(target: str, overlay) -> dict:
    """v1 mechanism: Marcus's structured-intent claim is overlay-bound.

    Returns the structured-intent payload (claimed_state for the target). In S5
    the LLM emits an equivalently-shaped payload; the judge is source-agnostic.
    """
    entry = overlay.specialists.get(target)
    claimed_state = entry.capability_state if entry is not None else None
    return {
        "target": target,
        "claimed_state": claimed_state,
        "claimed_wired": claimed_state == "wired",
    }


def judge_intent(intent: dict, live_state: str | None) -> tuple[bool, str]:
    """Mechanical judge. Returns (ok, reason).

    Source-agnostic: ``intent`` may be constructed-from-overlay (v1) or
    LLM-emitted (S5). The judge cross-checks the claim against the live dispatch
    graph and forbids any false-`wired`.
    """
    claimed_state = intent.get("claimed_state")
    claimed_wired = bool(intent.get("claimed_wired"))

    # (1) HARD GATE (checked first): a `wired` claim MUST imply genuinely wired in
    # the live dispatch graph. Any false-`wired` is the cardinal over-promise sin.
    if (claimed_wired or claimed_state == "wired") and live_state != "wired":
        return False, (
            f"FALSE-WIRED: claimed wired but live state is {live_state!r}"
        )
    # (2) the claim must equal the live-derived state (overlay-bound, not invented)
    if claimed_state != live_state:
        return False, (
            f"claimed_state {claimed_state!r} != live-derived {live_state!r}"
        )
    return True, "ok"


def test_probe_corpus_loads_and_is_nonvacuous() -> None:
    rows = _load_corpus()
    states = {row["expected_state"] for row in rows}
    # Must exercise each non-wired class AND at least one wired control.
    assert {"present-but-unrouted", "partial", "shelf", "wired"} <= states


def test_zero_false_wired_over_promise() -> None:
    """AC-7: every row's claim is overlay-bound; ZERO false-`wired`."""
    overlay = derive_overlay(REPO_ROOT)
    rows = _load_corpus()

    false_wired: list[str] = []
    mismatches: list[str] = []
    wired_controls_ok: list[str] = []

    for row in rows:
        target = row["target"]
        live_state = _live_state(target)

        # corpus expectation must itself match live substrate (corpus is honest).
        assert row["expected_state"] == live_state, (
            f"corpus row {row['id']}: expected_state {row['expected_state']!r} "
            f"diverges from live {live_state!r} — corpus stale vs substrate"
        )

        intent = construct_intent_from_overlay(target, overlay)
        ok, reason = judge_intent(intent, live_state)
        if not ok:
            if "FALSE-WIRED" in reason:
                false_wired.append(f"{row['id']}: {reason}")
            else:
                mismatches.append(f"{row['id']}: {reason}")

        # control rows: a genuinely-wired target MUST be claimed wired.
        if row.get("expected_wired") is True:
            if intent["claimed_wired"] and live_state == "wired":
                wired_controls_ok.append(row["id"])
            else:
                mismatches.append(
                    f"{row['id']}: wired control NOT claimed wired "
                    f"(claimed_wired={intent['claimed_wired']}, live={live_state!r})"
                )

    assert not false_wired, f"FALSE-WIRED claims (AC-7 RED): {false_wired}"
    assert not mismatches, f"claim/live mismatches: {mismatches}"
    assert wired_controls_ok, "no wired control row exercised — probe is vacuous"


def test_judge_catches_an_injected_false_wired() -> None:
    """Non-vacuity proof: a hand-forged false-`wired` intent is caught RED."""
    # A forged intent claiming a shelf capability is wired.
    forged = {"target": "midjourney", "claimed_state": "wired", "claimed_wired": True}
    ok, reason = judge_intent(forged, live_state="shelf")
    assert not ok and "FALSE-WIRED" in reason


def test_no_llm_client_imported_anywhere_in_gate() -> None:
    """AC-10 grep-assert: the generator + this judge import no LLM client.

    The honesty gate is MECHANICAL only — any LLM-client import (openai /
    anthropic / langchain chat models / the repo's make_chat_model adapter) in the
    derivation or judge would make the gate a vibe-judge. Forbidden tokens are
    grepped out of the source text.
    """
    forbidden = (
        "openai",
        "anthropic",
        "make_chat_model",
        "langchain_openai",
        "litellm",
        "langchain_anthropic",
    )
    sources = [
        REPO_ROOT / "scripts" / "utilities" / "generate_capability_overlay.py",
        Path(__file__).resolve(),
    ]
    for src in sources:
        # Scan IMPORT statements only (a docstring may legitimately name a token
        # while explaining why it is forbidden). This is the load-bearing check:
        # nothing in the gate may import an LLM client.
        import_lines = [
            line.strip()
            for line in src.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]
        for line in import_lines:
            for token in forbidden:
                assert token not in line, (
                    f"forbidden import token {token!r} in {src.name}: {line!r} — the "
                    "honesty gate must stay mechanical (no LLM client)"
                )
            # v-next fence (AC-10): no trial-log / runs/ consumption in v1.
            assert "runs" not in line.split(), (
                f"runs/ trial-log import in {src.name}: {line!r} (v1.1 fence)"
            )


def test_judge_accepts_llm_shaped_payload_for_s5() -> None:
    """The judge is source-agnostic: an S5-shaped (LLM-emitted) intent validates."""
    overlay = derive_overlay(REPO_ROOT)
    live_state = _live_state("gary")
    # Simulate an S5 LLM emitting the SAME shape the v1 constructor produces.
    llm_intent = {
        "target": "gary",
        "claimed_state": overlay.specialists["gary"].capability_state,
        "claimed_wired": overlay.specialists["gary"].capability_state == "wired",
    }
    ok, reason = judge_intent(llm_intent, live_state)
    assert ok, reason
