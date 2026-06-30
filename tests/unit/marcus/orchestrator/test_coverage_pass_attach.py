"""Step 1 — coverage PASS attach onto G0EnrichmentResult (offline; mirrors P3).

``_attach_coverage_annotations`` builds the coverage front matter (component_id /
type / locator / excerpt / pedagogical_role / lo_refs) and delegates to
``build_coverage_annotations`` (offline default). Gated by the coverage-pass flag so a
flag-OFF run attaches NOTHING -> the card firewall prunes the empty layer ->
byte-identical. Only note-bearing (narration) components are segmented.
"""

from __future__ import annotations

from pathlib import Path

from app.marcus.lesson_plan.pedagogy_annotation import PedagogyAnnotation
from app.marcus.lesson_plan.source_type import TypedComponent
from app.marcus.orchestrator import coverage_gate_wiring as cgw
from app.marcus.orchestrator import g0_enrichment_wiring as gw

# Reuse the corpus the existing brick tests point at.
GW_CORPUS = (
    Path(__file__).resolve().parents[4] / "course-content" / "courses" / "studio-smoke-min"
)


def _typed() -> list[TypedComponent]:
    return [
        TypedComponent(
            component_id="src-001-c001", parent_source_id="src-001", source_type="narration",
            label="notes", locator="Course 1 > Slide 1",
            excerpt="Dose is 5 mg daily. Do not exceed 10 mg. Titrate slowly.",
        ),
        TypedComponent(
            component_id="src-001-c002", parent_source_id="src-001", source_type="slide",
            label="title", locator="Course 1 > Slide 1", excerpt="Trends in dosing",
        ),
    ]


def _ped() -> tuple[PedagogyAnnotation, ...]:
    return (
        PedagogyAnnotation(
            component_id="src-001-c001", lo_refs=("lo-g0-001",), bloom="understand",
            pedagogical_role="synthesis", teachable=True, rationale="x",
        ),
    )


def test_attach_populates_when_flag_on(monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_PASS_ACTIVE_ENV, "1")
    annotations = gw._attach_coverage_annotations(
        _typed(), _ped(), [], dispatch_live=False, chat_model_factory=None
    )
    assert len(annotations) == 1  # only the narration component is note-bearing
    ann = annotations[0]
    assert ann.component_id == "src-001-c001"
    assert ann.slide_key == "Slide 1"
    assert len(ann.source_points) >= 2  # the note block re-segmented into assertions
    # the deterministic risk floor survives (numeric/negation -> verbatim_required)
    assert any(sp.verbatim_required for sp in ann.source_points)


def test_attach_empty_when_flag_off(monkeypatch) -> None:
    monkeypatch.delenv(cgw.COVERAGE_PASS_ACTIVE_ENV, raising=False)
    annotations = gw._attach_coverage_annotations(
        _typed(), _ped(), [], dispatch_live=False, chat_model_factory=None
    )
    assert annotations == ()


def test_offline_build_result_flag_off_has_no_coverage_layer(monkeypatch) -> None:
    # The whole offline pre-pass: flag OFF -> no coverage_annotations on the result,
    # and the card payload omits the key entirely (byte-identical firewall).
    monkeypatch.delenv(cgw.COVERAGE_PASS_ACTIVE_ENV, raising=False)
    result = gw.build_enrichment_result(corpus_dir=GW_CORPUS, dispatch_live=False)
    assert result.coverage_annotations == ()
    assert "coverage_annotations" not in result.to_card_payload()
