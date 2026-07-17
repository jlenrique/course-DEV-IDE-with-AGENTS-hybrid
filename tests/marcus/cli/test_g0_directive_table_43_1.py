"""Story 43-1 — G0 directive source-inventory table (kill the raw dump).

Replay-only against ``tests/fixtures/hil_projector/directive-*.yaml`` (zero live
spend). Proves the bespoke ``directive`` renderer produces the operator-approved
source-inventory table and that ``trial.py::_confirm_or_edit_directive`` now makes
that TABLE the default G0 review surface (the raw ``read_text`` YAML dump is gone;
raw is one keystroke away via ``[e]dit``), with the ``c/e/s/x`` contract and the
pure-IO seam preserved.

Names the surface — **G0 directive composition** — so a G0E-only replay corpus can
never re-close the requirement on a subset (pin 3 / Story 43-10).
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
import yaml

import app.marcus.cli.trial as trial
from app.marcus.cli.hil_tabular_projector import (
    KNOWN_UNRENDERED_ALLOWLIST,
    get_renderer,
    registered_content_types,
    render_directive_sources,
    render_gate_content,
)

FIXTURES = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "hil_projector"
DIRECTIVE_5169 = FIXTURES / "directive-5169a872.yaml"
DIRECTIVE_BC74 = FIXTURES / "directive-bc747b51.yaml"


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# AC-1 / AC-4 — bespoke directive renderer, registered (allowlist→registry move).
# ---------------------------------------------------------------------------


def test_directive_renderer_is_registered_and_off_the_allowlist() -> None:
    """AC-1 + AC-4: ``directive`` dispatches to the bespoke renderer and has LEFT
    the shrink-only allowlist (the first allowlist→registry move; 43-10's disjoint
    invariant requires the deletion)."""
    assert "directive" in registered_content_types()
    assert "directive" not in KNOWN_UNRENDERED_ALLOWLIST
    assert get_renderer("directive") is render_directive_sources


# ---------------------------------------------------------------------------
# AC-6 — replay: the operator-approved table shape on directive-5169a872.
# ---------------------------------------------------------------------------


def test_g0_directive_composition_table_shape_5169a872() -> None:
    """AC-6 (pin 3 — names **G0 directive composition**): the rendered table for
    the 5169a872 directive carries the header (run_id + corpus basename + A/B
    styleguide variants), primary-first ordering, ALL 14 ref_ids, a truncated
    description column, and the exact counts footer."""
    directive = _load(DIRECTIVE_5169)
    out = render_directive_sources(directive, title="Gate content")

    # Header line: run_id + corpus BASENAME (not the full path).
    assert "G0 — Directive review" in out
    assert "run 5169a872-6421-4e75-b07e-6a3bda42a4cc" in out
    assert "corpus tejal-apc-c1m1-p1-call" in out
    # …and the full path is reduced to its basename.
    assert "C:/Users" not in out

    # Variants line: A/B styleguide slugs from gamma_settings.
    assert "Variants:" in out
    assert "A hil-2026-apc-crossroads-blueprint" in out
    assert "B hil-2026-apc-videographic-glance" in out

    # All 14 ref_ids present.
    for n in range(1, 15):
        assert f"src-{n:03d}" in out

    # Primary-first ordering: src-003 (primary) precedes the supporting rows
    # (src-001, src-002), even though src-001 sorts first lexically.
    assert out.index("src-003") < out.index("src-001")
    assert out.index("src-003") < out.index("src-002")

    # Description column is truncated (rider R5): the long src-013 brief is capped
    # with an ellipsis and its tail text never reaches the table.
    assert "…" in out
    assert "wise risk-taking" not in out  # tail of the src-013 description

    # Counts footer, verbatim.
    assert "14 sources · 12 primary · 2 supporting · 0 excluded" in out


def test_g0_directive_table_header_and_footer_bc747b51() -> None:
    """AC-6: repeat the header/footer assertions on the second fixture."""
    directive = _load(DIRECTIVE_BC74)
    out = render_directive_sources(directive, title="Gate content")

    assert "run bc747b51-7009-4742-9f65-8de6abc29ca4" in out
    assert "corpus tejal-apc-c1m1-p1-call" in out
    # bc747b51 picked different variants than 5169a872.
    assert "A hil-2026-apc-videographic-glance" in out
    assert "B hil-2026-apc-crossroads-magazine" in out
    assert "14 sources · 12 primary · 2 supporting · 0 excluded" in out


def test_directive_dispatch_through_render_gate_content() -> None:
    """AC-1: dispatch via the registry (``content_type='directive'``) yields the
    bespoke table, not the generic Field|Value fallback."""
    directive = _load(DIRECTIVE_5169)
    out = render_gate_content(directive, content_type="directive")
    assert "G0 — Directive review" in out
    assert "| ref | role | locator | min-words | excl | description |" in out
    # generic fallback header would be "**Gate content**" / "| Field | Value |".
    assert "| Field | Value |" not in out


# ---------------------------------------------------------------------------
# AC-2 / AC-3 / AC-6 — confirm path: table is default, raw dump gone, c/e/s/x kept.
# ---------------------------------------------------------------------------


def _drive_confirm(
    directive_path: Path, choices: list[str]
) -> tuple[str, list[str], list[Path]]:
    """Drive ``_confirm_or_edit_directive`` with an injected pure-IO seam.

    Returns ``(verdict, printed_chunks, edit_calls)``.
    """
    printed: list[str] = []
    edit_calls: list[Path] = []
    it = iter(choices)

    def input_fn(_prompt: str) -> str:
        return next(it)

    def edit_fn(path: Path) -> None:
        edit_calls.append(path)

    def print_fn(msg: str) -> None:
        printed.append(str(msg))

    verdict = trial._confirm_or_edit_directive(
        directive_path=directive_path,
        auto_confirm_directive=False,
        input_fn=input_fn,
        edit_fn=edit_fn,
        isatty_fn=lambda: True,
        print_fn=print_fn,
    )
    return verdict, printed, edit_calls


@pytest.fixture
def directive_file(tmp_path: Path) -> Path:
    path = tmp_path / "directive.yaml"
    path.write_text(DIRECTIVE_5169.read_text(encoding="utf-8"), encoding="utf-8")
    return path


def test_confirm_shows_table_and_no_raw_yaml_dump(directive_file: Path) -> None:
    """AC-2 + AC-6: at the G0 confirm the operator sees the source-inventory TABLE
    by default, and the old raw ``directive_path.read_text()`` YAML dump is GONE
    (raw-only tokens like ``styleguide_picker_provenance`` / ``schema_version`` no
    longer appear on the confirm surface)."""
    verdict, printed, edit_calls = _drive_confirm(directive_file, ["c"])
    assert verdict == "confirmed"
    assert edit_calls == []
    surface = "\n".join(printed)

    # Table is the default view.
    assert "G0 — Directive review" in surface
    assert "14 sources · 12 primary · 2 supporting · 0 excluded" in surface
    # Raw YAML dump is gone: these keys exist ONLY in the raw directive file.
    assert "styleguide_picker_provenance" not in surface
    assert "schema_version" not in surface
    assert "ssot_sha256" not in surface


def test_confirm_route_returns_confirmed(directive_file: Path) -> None:
    """AC-3: ``[c]`` confirms."""
    verdict, _printed, edit_calls = _drive_confirm(directive_file, ["c"])
    assert verdict == "confirmed"
    assert edit_calls == []


def test_edit_route_opens_raw_directive_then_confirms(directive_file: Path) -> None:
    """AC-3: ``[e]`` opens the RAW directive.yaml in the editor (raw one keystroke
    away), re-renders, and the loop continues; a following ``[c]`` confirms."""
    verdict, _printed, edit_calls = _drive_confirm(directive_file, ["e", "c"])
    assert verdict == "confirmed"
    assert edit_calls == [directive_file]  # [e] opened the raw directive path


def test_save_route_returns_saved_only(directive_file: Path) -> None:
    """AC-3: ``[s]`` saves and exits without dispatch."""
    verdict, _printed, edit_calls = _drive_confirm(directive_file, ["s"])
    assert verdict == "saved-only"
    assert edit_calls == []


def test_cancel_route_raises(directive_file: Path) -> None:
    """AC-3: ``[x]`` cancels — raises ``DirectiveDeclinedError``, no dispatch."""
    with pytest.raises(trial.DirectiveDeclinedError):
        _drive_confirm(directive_file, ["x"])


def test_invalid_choice_reprompts_then_confirms(directive_file: Path) -> None:
    """AC-3: an unrecognized choice re-prompts (loop preserved) rather than
    crashing; a following ``[c]`` confirms."""
    verdict, printed, _edit_calls = _drive_confirm(directive_file, ["q", "c"])
    assert verdict == "confirmed"
    assert any("invalid choice" in chunk for chunk in printed)


def test_pure_io_seam_signature_unchanged() -> None:
    """AC-3: the injectable pure-IO seam (input_fn/edit_fn/isatty_fn/print_fn) is
    preserved exactly on ``_confirm_or_edit_directive``."""
    import inspect

    params = inspect.signature(trial._confirm_or_edit_directive).parameters
    for name in ("input_fn", "edit_fn", "isatty_fn", "print_fn"):
        assert name in params
        assert params[name].default is None
    # The seam is keyword-only and callable-typed.
    seam: Callable[..., object] = trial._confirm_or_edit_directive
    assert callable(seam)
