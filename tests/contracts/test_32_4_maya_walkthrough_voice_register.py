"""Story 32-4 AC-C.1 — no Intake/Orchestrator leaks in operator-visible strings.

Walks every operator-visible string field of a :class:`MayaWalkthroughResult`
instance (via ``model_dump()``) + the operator walkthrough markdown file;
asserts zero word-boundary occurrences of ``"intake"`` or ``"orchestrator"``
(case-insensitive). Tracks the 30-1 pattern pinned in
``test_no_intake_orchestrator_leak_marcus_duality.py`` — the two programming
tokens R1 amendment 17 names explicitly.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

from app.marcus.lesson_plan.log import LessonPlanLog
from app.marcus.orchestrator.maya_walkthrough import run_maya_walkthrough

_FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "maya_walkthrough" / "sme_corpus"
_OPERATOR_MARKDOWN = (
    Path(__file__).resolve().parents[2]
    / "_bmad-output"
    / "maps"
    / "maya-journey"
    / "maya-walkthrough.md"
)

_FORBIDDEN_PATTERN = re.compile(r"\b(intake|orchestrator)\b", re.IGNORECASE)


@pytest.fixture(autouse=True)
def _patch_pre_packet_repo_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from app.marcus.intake import pre_packet

    monkeypatch.setattr(pre_packet, "_REPO_ROOT", tmp_path)


def _walk_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        collected: list[str] = []
        for key, inner in value.items():
            if isinstance(key, str):
                collected.append(key)
            collected.extend(_walk_strings(inner))
        return collected
    if isinstance(value, list | tuple):
        collected = []
        for inner in value:
            collected.extend(_walk_strings(inner))
        return collected
    return []


def test_no_intake_or_orchestrator_tokens_in_operator_surface(tmp_path: Path) -> None:
    log = LessonPlanLog(path=tmp_path / "log.jsonl")
    result = run_maya_walkthrough(
        _FIXTURE_DIR,
        log=log,
        run_id="voice-register",
        output_path=tmp_path / "irene-packet.md",
    )

    # Walk every string on the operator-visible result, excluding internal
    # identifiers (unit_id values are not Maya-visible — they are programming
    # tokens exposed only for debug surfaces).
    payload = result.model_dump(mode="json")
    operator_visible_fields = {
        "marcus_delegation_proposal.sentence",
        "click_gray_card.source_fitness_diagnosis",
        "operator_rationale_sentence.stored",
        "card_turned_gold.stored_rationale",
    }
    leaks: list[str] = []
    for dotted in operator_visible_fields:
        current: Any = payload
        for part in dotted.split("."):
            current = current[part]
        if not isinstance(current, str):
            continue
        match = _FORBIDDEN_PATTERN.search(current)
        if match:
            leaks.append(f"{dotted}: leaked {match.group()!r} in {current!r}")

    for idx, rationale in enumerate(result.declined_articulations):
        match = _FORBIDDEN_PATTERN.search(rationale)
        if match:
            leaks.append(
                f"declined_articulations[{idx}]: leaked {match.group()!r} in {rationale!r}"
            )

    markdown = _OPERATOR_MARKDOWN.read_text(encoding="utf-8")
    for line_no, line in enumerate(markdown.splitlines(), start=1):
        match = _FORBIDDEN_PATTERN.search(line)
        if match:
            leaks.append(f"maya-walkthrough.md:{line_no}: leaked {match.group()!r} in {line!r}")

    assert not leaks, "operator-visible surface leaked Marcus-duality tokens:\n" + "\n".join(leaks)
