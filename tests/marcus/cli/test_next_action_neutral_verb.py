"""Story 42.1 (finding G) — the ``paused-at-gate`` next-action must be NEUTRAL.

The bc747b51 trial exposed that ``build_next_action`` hardcoded ``--verb approve``
for every gate pause, so ``operator-surface.next_action.command`` pre-framed the
operator's verdict. These tests pin the fix: all allowed verbs present, none
preselected as THE sole option, card-id + digest retained for whichever verb, no
verdict implied. Replayed against the REAL frozen ``decision-card-G0R.json`` verb
contract (skip-if-absent) plus a synthetic multi-verb gate.
"""

from __future__ import annotations

import json
import shlex
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.marcus.cli.next_action import build_next_action

REPO_ROOT = Path(__file__).resolve().parents[3]
LIVE_TRIAL = "bc747b51-7009-4742-9f65-8de6abc29ca4"
LIVE_G0R_CARD = (
    REPO_ROOT / "state" / "config" / "runs" / LIVE_TRIAL / "decision-card-G0R.json"
)


def _env(**kw):
    base = dict(
        trial_id=uuid4(),
        status="paused-at-gate",
        paused_gate="G0R",
        operator_id="juanl",
    )
    base.update(kw)
    return SimpleNamespace(**base)


def _resume_lines(surface: str) -> list[str]:
    return [ln.strip() for ln in surface.splitlines() if ln.strip().startswith("trial resume")]


def _verbs_in(surface: str) -> set[str]:
    verbs = set()
    for line in _resume_lines(surface):
        toks = shlex.split(line)
        if "--verb" in toks:
            verbs.add(toks[toks.index("--verb") + 1])
    return verbs


def _write_card(tmp_path: Path, gate: str, *, card_id: str, digest: str, allowed=None) -> Path:
    card: dict = {"card_id": card_id}
    if allowed is not None:
        card["allowed_verbs"] = allowed
    path = tmp_path / f"decision-card-{gate}.json"
    path.write_text(json.dumps({"card": card, "digest": digest}), encoding="utf-8")
    return path


def test_no_single_preselected_verb_for_multi_verb_gate(tmp_path: Path) -> None:
    """AC-5 core pin: no operator-facing next-action string presents a single
    ``--verb <x>`` as the SOLE option for a multi-verb gate."""
    card = _write_card(tmp_path, "G0R", card_id=str(uuid4()), digest="a" * 64)
    surface = build_next_action(_env(), card_path=card)

    # All three closed-set verbs are present, each on its own paste line.
    assert _verbs_in(surface) == {"approve", "edit", "reject"}
    # More than one resume line => approve is NOT the sole option.
    assert len(_resume_lines(surface)) >= 3
    # The old defect: the whole surface being exactly one approve command.
    assert surface.strip() != _resume_lines(surface)[0]


def test_no_bare_approve_only_command() -> None:
    """The surface is never a single approve-prefilled command (the bc747b51
    defect). It must contain edit and reject paths too."""
    surface = build_next_action(_env(), card_path=None)
    assert "--verb approve" in surface
    assert "--verb edit" in surface
    assert "--verb reject" in surface


def test_card_id_and_digest_retained_for_every_verb(tmp_path: Path) -> None:
    card_id = str(uuid4())
    digest = "b" * 64
    card = _write_card(tmp_path, "G0R", card_id=card_id, digest=digest)
    surface = build_next_action(_env(), card_path=card)

    for line in _resume_lines(surface):
        assert f"--card-id {card_id}" in line
        assert f"--decision-card-digest {digest}" in line
        assert "--operator-id juanl" in line


def test_no_verdict_implied_copy(tmp_path: Path) -> None:
    """AC-5: copy honors 'Marcus proposes; you decide' — never implies a decision."""
    card = _write_card(tmp_path, "G0R", card_id=str(uuid4()), digest="c" * 64)
    surface = build_next_action(_env(), card_path=card)
    assert "you decide" in surface.lower()
    assert "choose" in surface.lower()


def test_allowed_verbs_threaded_from_card_not_assumed(tmp_path: Path) -> None:
    """AC-4: the allowed-verb set is threaded from the card when it declares one
    (gates may differ) rather than universally assuming approve|edit|reject."""
    card = _write_card(
        tmp_path, "G0", card_id=str(uuid4()), digest="d" * 64, allowed=["approve", "reject"]
    )
    surface = build_next_action(_env(paused_gate="G0"), card_path=card)
    assert _verbs_in(surface) == {"approve", "reject"}
    assert "--verb edit" not in surface


def test_each_verb_line_carries_gate_and_trial(tmp_path: Path) -> None:
    card = _write_card(tmp_path, "G0R", card_id=str(uuid4()), digest="e" * 64)
    env = _env()
    surface = build_next_action(env, card_path=card)
    for line in _resume_lines(surface):
        assert "--gate-id G0R" in line
        assert f"--trial-id {env.trial_id}" in line


@pytest.mark.skipif(
    not LIVE_G0R_CARD.exists(),
    reason="live bc747b51 decision-card-G0R.json absent on this machine",
)
def test_real_g0r_card_contract_is_multi_verb() -> None:
    """The real frozen G0R card's contract is approve|edit|reject — proving the
    neutral surface must present three verbs for this gate (P-5 real-artifact)."""
    card = json.loads(LIVE_G0R_CARD.read_text(encoding="utf-8"))
    # the card carries a single default `verb` (the old preselect source)
    assert card["card"]["verb"] == "approve"
    card_id = card["card"]["card_id"]
    env = _env(paused_gate="G0R")
    surface = build_next_action(env, card_path=LIVE_G0R_CARD)
    # neutral surface presents all three closed-set verbs, not just the card's default
    assert _verbs_in(surface) == {"approve", "edit", "reject"}
    for line in _resume_lines(surface):
        assert f"--card-id {card_id}" in line
