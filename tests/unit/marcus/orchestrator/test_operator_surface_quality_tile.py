"""Story Q4.1 — assembler-populated operator-surface ``quality`` tile.

RED-first pins for the wiring that folds the COMMITTED project-quality scorecard
into the per-run operator surface at the terminal-completion choke-point:

  * AC2  — reads the COMMITTED doc (``read_scorecard_block`` / ranked-leaks /
           coverage-gaps / history trend), NEVER ``app.quality.signals.*``;
           deferred ``app.quality`` import (not module scope).
  * AC3  — fires at the SAME verb-conditional completion choke-point ``deliverables``
           uses → rides ``emit()`` in BOTH walks, NEVER at a pause / registered.
  * AC4  — zero-lie / fail-soft: absent/corrupt block → ``available=False`` + null
           posture, STILL emitted, walk never perturbed.
  * AC6  — no-Band-better-than-committed: the worst band across present dimensions
           wins; a clean sibling can never paint over a redder one.
  * AC7  — calibration honesty: the OWED/uncalibrated posture surfaces honestly,
           never a fresh-naive number (the tile carries no ``/100`` field at all).
"""

from __future__ import annotations

import ast
import inspect
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

import app.quality as appq
from app.marcus.orchestrator import operator_surface_assembler as osa
from app.marcus.orchestrator.operator_surface_assembler import OperatorSurfaceAssembler
from app.models.runtime.operator_surface import (
    OperatorSurfaceProjection,
    read_operator_surface_lenient,
)


class _StubEnvelope:
    """Minimal envelope stand-in (mirrors the assembler test harness)."""

    def __init__(
        self,
        trial_id: UUID,
        status: str,
        *,
        paused_gate: str | None = None,
        completed_at: datetime | None = None,
        corpus_path: str = "lesson-alpha",
        preset: str = "production",
        operator_id: str = "operator_cli",
    ) -> None:
        self.trial_id = trial_id
        self.status = status
        self.paused_gate = paused_gate
        self.paused_error_tag = None
        self.waiting_batch_id = None
        self.completed_at = completed_at
        self.corpus_path = corpus_path
        self.preset = preset
        self.operator_id = operator_id

    def model_dump_json(self, indent: int = 2) -> str:
        return json.dumps(
            {
                "trial_id": str(self.trial_id),
                "status": self.status,
                "paused_gate": self.paused_gate,
                "completed_at": self.completed_at.isoformat()
                if self.completed_at
                else None,
            },
            indent=indent,
            sort_keys=True,
        )


def _assembler(tmp_path: Path, trial_id: UUID) -> OperatorSurfaceAssembler:
    return OperatorSurfaceAssembler(
        trial_id, tmp_path, hud_config_path=tmp_path / "no-such-hud-config.yaml"
    )


def _read(assembler: OperatorSurfaceAssembler) -> OperatorSurfaceProjection:
    parsed = read_operator_surface_lenient(assembler.projection_path.read_bytes())
    assert isinstance(parsed, OperatorSurfaceProjection), parsed
    return parsed


def _completed(tid: UUID) -> _StubEnvelope:
    return _StubEnvelope(tid, "completed", completed_at=datetime.now(UTC))


# A synthetic committed machine block: a CLEAN dim ("A") and a RED dim ("D") with
# open leaks — so worst-across-dimensions must render "D", never "A".
_SYNTH_BLOCK = {
    "as_of": "2026-07-19",
    "dimensions": {
        "dim_clean": {"label": "Clean Dim", "band": "A", "open_leaks": 0},
        "dim_red": {
            "label": "Red Dim",
            "band": "D",
            "open_leaks": 2,
            "leaks": [
                {"rank": 1, "criterion": "C1", "slug": "red-leak-1", "lane": "paid-walk"},
                {"rank": 2, "criterion": "C2", "slug": "red-leak-2", "lane": "governance"},
            ],
        },
    },
}


# --------------------------------------------------------------------------
# AC3 — completion choke-point, both walks, not-at-pause
# --------------------------------------------------------------------------


def test_completion_populates_quality_tile(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(appq, "read_scorecard_block", lambda *a, **k: dict(_SYNTH_BLOCK))
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    assert asm.emit(_completed(tid)) is True
    proj = _read(asm)
    assert proj.envelope.status == "completed"
    assert proj.quality is not None
    assert proj.quality.available is True
    assert proj.quality.band == "D"
    assert proj.quality.ranked_leak_count == 2
    assert proj.quality.coverage_gaps == 0
    assert len(proj.quality.top_leaks) == 2


def test_tile_carries_committed_scorecard_as_of_distinct_from_read_stamp(
    tmp_path: Path, monkeypatch
) -> None:
    """FIX 2: the tile surfaces the COMMITTED scorecard doc's ``as_of`` (a staleness
    signal) as ``scorecard_as_of`` — distinct from the section's own emit-time
    ``as_of`` read-stamp (which uses ``now()``)."""
    monkeypatch.setattr(appq, "read_scorecard_block", lambda *a, **k: dict(_SYNTH_BLOCK))
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(_completed(tid))
    q = _read(asm).quality
    assert q.available is True
    assert q.scorecard_as_of == "2026-07-19"  # the COMMITTED doc date, verbatim
    # the read-stamp is emit-time now(), NOT the committed doc date
    assert q.as_of.isoformat() != "2026-07-19"


def test_unavailable_tile_has_null_scorecard_as_of(
    tmp_path: Path, monkeypatch
) -> None:
    """FIX 2: an unavailable tile carries ``scorecard_as_of=None`` (no lie)."""
    monkeypatch.setattr(appq, "read_scorecard_block", lambda *a, **k: None)
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(_completed(tid))
    q = _read(asm).quality
    assert q.available is False
    assert q.scorecard_as_of is None


def test_quality_absent_at_pause_and_registered(tmp_path: Path, monkeypatch) -> None:
    """AC3: NEVER a 'completed' posture at a non-terminal pause / registered."""
    monkeypatch.setattr(appq, "read_scorecard_block", lambda *a, **k: dict(_SYNTH_BLOCK))
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    assert _read(asm).quality is None  # in-flight
    asm.emit(_StubEnvelope(tid, "paused-at-gate", paused_gate="G1"))
    assert _read(asm).quality is None  # paused


def test_quality_written_by_any_stateless_sole_writer_assembler(
    tmp_path: Path, monkeypatch
) -> None:
    """FIX 7b — proves SOLE-WRITER STATELESSNESS: a DIFFERENT assembler instance
    (a second sole-writer for the same trial_id / runs_root) writing completion
    produces the tile too, with no per-walk state carried in the assembler. (What
    actually proves "never rendered at the G1 pause" is the completion-only gate +
    ``test_quality_absent_at_pause_and_registered`` — NOT this test.)"""
    monkeypatch.setattr(appq, "read_scorecard_block", lambda *a, **k: dict(_SYNTH_BLOCK))
    tid = uuid4()
    _assembler(tmp_path, tid).emit(_StubEnvelope(tid, "in-flight"))
    other_walk = _assembler(tmp_path, tid)
    assert other_walk.emit(_completed(tid)) is True
    assert _read(other_walk).quality.band == "D"


# --------------------------------------------------------------------------
# AC4 — zero-lie / fail-soft
# --------------------------------------------------------------------------


def test_absent_block_emits_available_false_never_fabricated(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(appq, "read_scorecard_block", lambda *a, **k: None)
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    assert asm.emit(_completed(tid)) is True  # walk unperturbed
    q = _read(asm).quality
    assert q is not None  # STILL emitted (never silent-absence at completion)
    assert q.available is False
    assert q.band is None  # never a fabricated band
    assert q.ranked_leak_count is None
    assert q.top_leaks == []
    assert q.coverage_gaps is None
    assert q.trend is None


def test_corrupt_block_read_is_swallowed_available_false(
    tmp_path: Path, monkeypatch
) -> None:
    def _boom(*a, **k):
        raise RuntimeError("corrupt scorecard read")

    monkeypatch.setattr(appq, "read_scorecard_block", _boom)
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    assert asm.emit(_completed(tid)) is True  # exception swallowed, walk unperturbed
    q = _read(asm).quality
    assert q is not None
    assert q.available is False
    assert q.band is None


def test_fallback_construction_failure_never_aborts_the_emit(
    tmp_path: Path, monkeypatch
) -> None:
    """FIX 6: even if the unavailable-fallback construction ITSELF raises, the
    quality tile path must NOT propagate into ``_build`` and abort the terminal
    emit (which would lose deliverables / envelope / identity). The tile is
    omitted (None) or unavailable, but ``emit()`` still succeeds."""
    monkeypatch.setattr(appq, "read_scorecard_block", lambda *a, **k: None)
    tid = uuid4()
    asm = _assembler(tmp_path, tid)

    def _boom(_now):
        raise RuntimeError("fallback construction blew up")

    monkeypatch.setattr(asm, "_quality_unavailable", _boom)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    # the completion emit is NOT aborted by the double-failure on the tile path
    assert asm.emit(_completed(tid)) is True
    proj = _read(asm)
    assert proj.envelope.status == "completed"  # the terminal emit landed intact
    # the tile is omitted or unavailable — never a fabricated posture
    assert proj.quality is None or proj.quality.available is False


def test_block_missing_dimensions_is_unavailable(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(appq, "read_scorecard_block", lambda *a, **k: {"as_of": "2026-07-19"})
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(_completed(tid))
    assert _read(asm).quality.available is False


def test_present_dims_but_no_parseable_band_is_unavailable(
    tmp_path: Path, monkeypatch
) -> None:
    """FIX 1: a non-empty ``dimensions`` where NO dimension carries a parseable
    band (band omitted/null) — even with open leaks — must render the honest
    UNAVAILABLE posture (``available=False``, ``band=None``), never an
    ``available=True`` tile whose ``band`` is ``None`` (a self-contradiction that
    would surface a leak count with no band to interpret it against)."""
    block = {
        "as_of": "2026-07-19",
        "dimensions": {
            "dim_no_band": {
                "label": "No Band",
                "open_leaks": 2,
                "leaks": [
                    {"rank": 1, "criterion": "C1", "slug": "leak-1", "lane": "paid-walk"},
                    {"rank": 2, "criterion": "C2", "slug": "leak-2", "lane": "governance"},
                ],
            },
            "dim_null_band": {"label": "Null Band", "band": None, "open_leaks": 0},
        },
    }
    monkeypatch.setattr(appq, "read_scorecard_block", lambda *a, **k: block)
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(_completed(tid))
    q = _read(asm).quality
    assert q.available is False, "present dims but no parseable band must be UNAVAILABLE"
    assert q.band is None
    assert q.ranked_leak_count is None  # unavailable posture is fully null
    assert q.top_leaks == []


# --------------------------------------------------------------------------
# AC6 — no Band better than the committed block's worst dimension
# --------------------------------------------------------------------------


def test_band_is_worst_across_dimensions_never_the_cleaner_sibling(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(appq, "read_scorecard_block", lambda *a, **k: dict(_SYNTH_BLOCK))
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(_completed(tid))
    band = _read(asm).quality.band
    assert band == "D"
    assert band != "A", "tile painted the cleanest dimension over a redder sibling"


def test_unknown_band_never_renders_cleaner_than_a_known_red(
    tmp_path: Path, monkeypatch
) -> None:
    """FIX 4: an unrecognized band token must NEVER be surfaced verbatim on the
    operator tile (a garbage string is not an actionable ladder value). It is
    mapped to the conservative ladder floor ``"D"`` for BOTH ranking and display,
    so it can never render cleaner than a known red sibling (QLW-9) yet the tile
    always shows an actionable band, never ``"Z??"``."""
    block = {
        "as_of": "2026-07-19",
        "dimensions": {
            "dim_known_red": {"label": "Known Red", "band": "D", "open_leaks": 0},
            "dim_weird": {"label": "Weird", "band": "Z??", "open_leaks": 0},
        },
    }
    monkeypatch.setattr(appq, "read_scorecard_block", lambda *a, **k: block)
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(_completed(tid))
    band = _read(asm).quality.band
    # the garbage token is mapped to the actionable floor "D" (never surfaced raw),
    # and never renders cleaner than the known "D" sibling.
    assert band == "D"
    assert band != "Z??"


def test_lone_unknown_band_maps_to_actionable_floor_not_garbage(
    tmp_path: Path, monkeypatch
) -> None:
    """FIX 4: a lone unparseable band renders the ladder floor ``"D"`` — an
    actionable display value — never the raw garbage token."""
    block = {
        "as_of": "2026-07-19",
        "dimensions": {"dim_weird": {"label": "Weird", "band": "Z??", "open_leaks": 0}},
    }
    monkeypatch.setattr(appq, "read_scorecard_block", lambda *a, **k: block)
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(_completed(tid))
    q = _read(asm).quality
    assert q.available is True
    assert q.band == "D"


def test_band_value_is_whitespace_stripped(tmp_path: Path, monkeypatch) -> None:
    """FIX 4 NIT: a padded committed band (``" D "``) is stored stripped."""
    block = {
        "as_of": "2026-07-19",
        "dimensions": {"dim_pad": {"label": "Padded", "band": " D ", "open_leaks": 0}},
    }
    monkeypatch.setattr(appq, "read_scorecard_block", lambda *a, **k: block)
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(_completed(tid))
    assert _read(asm).quality.band == "D"


# --------------------------------------------------------------------------
# AC7 — calibration honesty
# --------------------------------------------------------------------------


def test_calibration_owed_posture_surfaces_honestly_no_fresh_number(
    tmp_path: Path, monkeypatch
) -> None:
    block = {
        "as_of": "2026-07-19",
        "dimensions": {
            "calibration": {
                "label": "Calibration",
                "band": "D",
                "band_note": "UNCALIBRATED — fresh-naive holdout OWED",
                "open_leaks": 1,
                "leaks": [
                    {
                        "rank": 1,
                        "criterion": "C1",
                        "slug": "reading-path-fresh-naive-holdout-pre-trial",
                        "lane": "learner-trust",
                    }
                ],
            }
        },
    }
    monkeypatch.setattr(appq, "read_scorecard_block", lambda *a, **k: block)
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(_completed(tid))
    q = _read(asm).quality
    assert q.available is True
    assert q.band == "D"  # the weak/owed posture surfaces, never inflated
    # the tile structurally carries NO numeric /100 score to fabricate.
    assert not hasattr(q, "score")
    assert any("holdout" in leak for leak in q.top_leaks)


# --------------------------------------------------------------------------
# AC2 — reads the COMMITTED doc; NEVER app.quality.signals.*; deferred import
# --------------------------------------------------------------------------


#: FIX 5 — the ENTIRE tile path, not just ``_quality_dict``. The no-signals guard
#: must scan every helper the tile calls (the Q3.1 subset-not-cover lesson): a
#: ``signals`` reference smuggled into ``_worst_band`` / ``_leak_label`` /
#: ``_quality_unavailable`` would slip past a ``_quality_dict``-only scan.
_TILE_PATH_METHODS = (
    "_quality_dict",
    "_worst_band",
    "_leak_label",
    "_quality_unavailable",
)


def _docstring_stripped_source(method_name: str) -> str:
    import textwrap

    source = textwrap.dedent(
        inspect.getsource(getattr(OperatorSurfaceAssembler, method_name))
    )
    fn = ast.parse(source).body[0]
    if fn.body and isinstance(fn.body[0], ast.Expr) and isinstance(fn.body[0].value, ast.Constant):
        fn.body = fn.body[1:]  # drop the docstring (which may name signals as a NEGATIVE)
    return ast.unparse(fn)


def test_tile_path_never_references_signals() -> None:
    """AC2 / FIX 5: NO method on the tile path (docstring-stripped) references
    ``app.quality.signals.*`` — scans EVERY tile-path helper, not just
    ``_quality_dict`` (subset-not-cover)."""
    for method_name in _TILE_PATH_METHODS:
        code = _docstring_stripped_source(method_name)
        assert "signals" not in code, (
            f"the quality tile path must never touch app.quality.signals.* "
            f"(offending helper: {method_name})"
        )
    # the entry point still reaches the COMMITTED doc via app.quality.
    assert "app.quality" in _docstring_stripped_source("_quality_dict"), (
        "the tile must read the COMMITTED doc via app.quality"
    )


def test_assembler_module_defers_app_quality_import() -> None:
    """AC2/AC3: ``app.quality`` is imported LAZILY (function scope), never at module
    scope — mirrors the assembler's next_action / TrialEconomicsReport deferrals."""
    tree = ast.parse(Path(osa.__file__).read_text(encoding="utf-8"))
    for node in tree.body:  # module-scope statements only
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("app.quality"):
            raise AssertionError(
                f"app.quality imported at module scope (line {node.lineno}); "
                "it must be a deferred local import"
            )
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith("app.quality")


def test_real_committed_scorecard_smoke(tmp_path: Path) -> None:
    """AC2 integration: with NO monkeypatch, the tile reads the REAL committed
    scorecard doc and renders a live posture (available + a real worst band)."""
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(_completed(tid))
    q = _read(asm).quality
    assert q is not None
    assert q.available is True
    assert isinstance(q.band, str) and q.band.strip()
    assert isinstance(q.ranked_leak_count, int) and q.ranked_leak_count >= 1
    assert isinstance(q.coverage_gaps, int)
    assert q.trend in {"baseline", "rising", "falling", "flat", None}
