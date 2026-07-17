"""Story 39.1b — D2 MERGE exercise composition: the five ratified floors.

I/O matrix (every row a pinned deterministic test; wave party record §D2):

  a)  collision identity — overlay id == collateral id pre-prefix: the ``g0-``
      prefix disambiguates; a residual cross-source collision fails LOUD via
      ``assert_unique_collateral_ids`` (never silent-dropped).
  b)  total ordering — unit -> provenance class (collateral before enrichment)
      -> stable id; byte-deterministic across runs.
  c)  cap — >12 total / >2 collateral in a unit: collateral trimmed per the
      J-3 round-robin rule (by unit then stable id; every unit keeps >=1
      Practice before any keeps 2), recorded in ``exercise_overlay_loss``;
      overlay NEVER trimmed. Includes the ratified 18->12 arithmetic
      (6 overlay + 12 collateral -> 6 + 6 kept, 6 trimmed).
  c') the REAL 8b275e5b shape — committed live-shape fixture (6 overlay + 8
      collateral = 14 -> 12; trim ``ex-u03-2``/``ex-u05-2``) + a full replay
      pin against ``runs/8b275e5b…`` when the run dir is present (M-D2-2).
      NOTE: the story spec's "18-exercise (6 overlay + 12 collateral)" figure
      was an authoring estimate; the frozen run's actual attachable shape is
      6 overlay + 8 collateral — the pin follows the real substrate per the
      live-shape rule (discrepancy recorded in the story Dev Agent Record).
  d)  provenance labels — "Practice" / "Course Check — drawn from this
      course's own assessments" groups render per unit; the Answer Key
      carries the SAME labels; grouping keys on the ``origin`` FIELD.
  e)  answer-key mapping, mixed keyed/unkeyed — keyed exercises map to their
      ``answer_keys`` entry (re-keyed to the ``g0-`` rendered id) under the
      correct label; unkeyed render the pending note; no prompt carries
      ``Correct Answer:`` (the 47-pin answer-leak floor).
  f)  zero overlay — pure-collateral render, no "Course Check" group, no loss
      record.
  g)  zero collateral — pure-overlay render under "Course Check", no phantom
      "Practice" group.

OFFLINE ONLY: no live LLM / network. Deterministic throughout.
"""

from __future__ import annotations

import json
import shutil
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import yaml

from app.marcus.lesson_plan.collateral_spec import (
    DepthDeltaContract,
    Exercise,
    WorkbookSection,
)
from app.marcus.lesson_plan.workbook_producer import (
    COURSE_CHECK_GROUP_LABEL,
    EXERCISE_OVERLAY_LOSS_CALLOUT,
    PRACTICE_GROUP_LABEL,
    DuplicateCollateralIdError,
    WorkbookProducer,
)
from app.specialists.workbook_producer import _act as wb_act
from app.specialists.workbook_producer._act import (
    _EXERCISE_TOTAL_CAP,
    _OVERLAY_EXERCISE_ID_PREFIX,
    _UNIT_COLLATERAL_CAP,
    _apply_exercise_composition_cap,
)

from ._run_fixture import collateral_present, section, write_run_json

REPO_ROOT = Path(__file__).resolve().parents[3]
COMPOSITION_FIXTURE = (
    REPO_ROOT / "tests" / "fixtures" / "exercise_merge_39_1b" / "composition-8b275e5b.json"
)
COMPOSITION_FIXTURE_SCHEMA_VERSION = "exercise-merge-composition-fixture.v1"
RUN_8B275E5B = REPO_ROOT / "runs" / "8b275e5b-ed8a-4720-8217-8ddaca4c6627"


# ---------------------------------------------------------------------------
# Model builders (cap-function unit surface)
# ---------------------------------------------------------------------------


def _ex(exercise_id: str, origin: str = "collateral") -> Exercise:
    return Exercise(
        exercise_id=exercise_id,
        bloom_level="understand",
        prompt_intent=f"prompt intent for {exercise_id}",
        answer_key_source_ref=f"src-ref-{exercise_id}",
        origin=origin,  # type: ignore[arg-type]
    )


def _model_section(
    section_id: str, objective_id: str, exercises: list[Exercise]
) -> WorkbookSection:
    return WorkbookSection(
        section_id=section_id,
        learning_objective_id=objective_id,
        title=f"Section {section_id}",
        depth_delta=DepthDeltaContract(
            deferred_from_slide="slide-01",
            deferred_depth=f"deferred depth for {section_id}",
        ),
        exercises=exercises,
    )


# ---------------------------------------------------------------------------
# Row b — total ordering: unit -> provenance class -> stable id; deterministic
# ---------------------------------------------------------------------------


def test_row_b_total_ordering_class_then_stable_id() -> None:
    sections = [
        _model_section(
            "sec-a",
            "lo-a",
            [
                _ex("g0-z-check", origin="enrichment"),
                _ex("b-practice"),
                _ex("g0-a-check", origin="enrichment"),
                _ex("a-practice"),
            ],
        )
    ]
    rebuilt, loss = _apply_exercise_composition_cap(sections)
    assert loss is None
    assert [ex.exercise_id for ex in rebuilt[0].exercises] == [
        "a-practice",
        "b-practice",
        "g0-a-check",
        "g0-z-check",
    ]


def test_row_b_byte_deterministic_across_runs() -> None:
    def build() -> list[WorkbookSection]:
        return [
            _model_section(
                "sec-a",
                "lo-a",
                [_ex("p2"), _ex("g0-c1", origin="enrichment"), _ex("p1")],
            ),
            _model_section("sec-b", "lo-b", [_ex("p9"), _ex("p3")]),
        ]

    first, first_loss = _apply_exercise_composition_cap(build())
    second, second_loss = _apply_exercise_composition_cap(build())
    assert [
        [ex.exercise_id for ex in sec.exercises] for sec in first
    ] == [[ex.exercise_id for ex in sec.exercises] for sec in second]
    assert first_loss == second_loss


# ---------------------------------------------------------------------------
# Row c — cap + visible loss (incl. the ratified 18->12 arithmetic)
# ---------------------------------------------------------------------------


def test_row_c_per_unit_collateral_cap_trims_beyond_two() -> None:
    # 4 collateral in ONE unit, plenty of total budget: per-unit cap 2 still
    # trims the 3rd/4th (stable-id retention), recorded — never silent.
    sections = [
        _model_section("sec-a", "lo-a", [_ex("p4"), _ex("p1"), _ex("p3"), _ex("p2")])
    ]
    rebuilt, loss = _apply_exercise_composition_cap(sections)
    assert [ex.exercise_id for ex in rebuilt[0].exercises] == ["p1", "p2"]
    assert loss is not None
    assert loss["trimmed_count"] == 2
    assert loss["trimmed_exercise_ids"] == ["p3", "p4"]


def test_row_c_ratified_18_to_12_round_robin() -> None:
    # The ratified D2/J-3 arithmetic: 6 overlay + 12 collateral (2 per unit x 6
    # units) = 18 -> 6 overlay kept untrimmed + 6 collateral kept round-robin
    # (every unit keeps exactly its stable-id-first Practice item), 6 trimmed.
    sections = [
        _model_section(
            f"sec-u{i}",
            f"lo-u{i}",
            [
                _ex(f"ex-u{i}-1"),
                _ex(f"ex-u{i}-2"),
                _ex(f"g0-check-u{i}", origin="enrichment"),
            ],
        )
        for i in range(1, 7)
    ]
    rebuilt, loss = _apply_exercise_composition_cap(sections)
    total = sum(len(sec.exercises) for sec in rebuilt)
    assert total == _EXERCISE_TOTAL_CAP == 12
    for i, sec in enumerate(rebuilt, start=1):
        assert [ex.exercise_id for ex in sec.exercises] == [
            f"ex-u{i}-1",
            f"g0-check-u{i}",
        ]
    assert loss is not None
    assert loss["trimmed_count"] == 6
    assert loss["overlay_count"] == 6
    assert loss["kept_collateral_count"] == 6
    assert loss["trimmed_exercise_ids"] == [f"ex-u{i}-2" for i in range(1, 7)]


def test_row_c_overlay_never_trimmed_even_beyond_total_cap() -> None:
    # 14 overlay items alone exceed the total cap: every one is kept (overlay
    # is never trimmed); ALL collateral is trimmed and recorded.
    sections = [
        _model_section(
            "sec-a",
            "lo-a",
            [_ex(f"g0-c{i:02d}", origin="enrichment") for i in range(14)]
            + [_ex("p1")],
        )
    ]
    rebuilt, loss = _apply_exercise_composition_cap(sections)
    kept = [ex.exercise_id for ex in rebuilt[0].exercises]
    assert len(kept) == 14
    assert all(ex_id.startswith(_OVERLAY_EXERCISE_ID_PREFIX) for ex_id in kept)
    assert loss is not None
    assert loss["trimmed_exercise_ids"] == ["p1"]


def test_row_c_round_robin_every_unit_keeps_one_before_any_keeps_two() -> None:
    # Budget forces a partial second round: units are granted their second
    # Practice item in section order only AFTER every unit holds one.
    # 11 overlay -> budget 1... use pure-collateral shape instead: 0 overlay,
    # budget 12; 8 units x 2 collateral = 16 -> first round grants 8 (one
    # each), second round grants 4 more (sections 1-4), 4 trimmed (5-8).
    sections = [
        _model_section(
            f"sec-{i:02d}", f"lo-{i:02d}", [_ex(f"ex-{i:02d}-a"), _ex(f"ex-{i:02d}-b")]
        )
        for i in range(1, 9)
    ]
    rebuilt, loss = _apply_exercise_composition_cap(sections)
    keep_counts = [len(sec.exercises) for sec in rebuilt]
    assert keep_counts == [2, 2, 2, 2, 1, 1, 1, 1]
    assert loss is not None
    assert loss["trimmed_exercise_ids"] == [
        "ex-05-b",
        "ex-06-b",
        "ex-07-b",
        "ex-08-b",
    ]
    assert _UNIT_COLLATERAL_CAP == 2


# ---------------------------------------------------------------------------
# Row c' — the REAL 8b275e5b shape (committed live-shape fixture + replay pin)
# ---------------------------------------------------------------------------


def _load_composition_fixture() -> dict[str, Any]:
    fixture = json.loads(COMPOSITION_FIXTURE.read_text(encoding="utf-8"))
    # Digest-bound bump tripwire (live-shape rule): a schema_version drift
    # means the fixture shape changed — re-derive from the frozen run.
    assert fixture["schema_version"] == COMPOSITION_FIXTURE_SCHEMA_VERSION
    return fixture


def test_row_c_prime_fixture_pins_real_8b275e5b_composition() -> None:
    fixture = _load_composition_fixture()
    sections = [
        _model_section(
            row["section_id"],
            row["learning_objective_id"],
            [_ex(ex_id) for ex_id in row["collateral"]]
            + [
                _ex(_OVERLAY_EXERCISE_ID_PREFIX + cid, origin="enrichment")
                for cid in row["overlay_component_ids"]
            ],
        )
        for row in fixture["sections"]
    ]
    rebuilt, loss = _apply_exercise_composition_cap(sections)
    kept_by_section = {
        sec.section_id: [ex.exercise_id for ex in sec.exercises] for sec in rebuilt
    }
    assert kept_by_section == fixture["expected"]["kept_by_section"]
    assert loss is not None
    assert loss["trimmed_exercise_ids"] == fixture["expected"]["trimmed_exercise_ids"]
    for key, value in fixture["expected"]["loss"].items():
        assert loss[key] == value, key
    # Byte-deterministic across runs (J-3).
    rebuilt_again, loss_again = _apply_exercise_composition_cap(
        [
            _model_section(
                row["section_id"],
                row["learning_objective_id"],
                [_ex(ex_id) for ex_id in row["collateral"]]
                + [
                    _ex(_OVERLAY_EXERCISE_ID_PREFIX + cid, origin="enrichment")
                    for cid in row["overlay_component_ids"]
                ],
            )
            for row in fixture["sections"]
        ]
    )
    assert kept_by_section == {
        sec.section_id: [ex.exercise_id for ex in sec.exercises]
        for sec in rebuilt_again
    }
    assert loss == loss_again


def test_row_c_prime_replay_full_8b275e5b_run_composition(tmp_path: Path) -> None:
    """M-D2-2: the real-run replay probe pins the CHOSEN composition (merged,
    labeled ids, capped) against the frozen inputs. Skips when the gitignored
    run dir is absent (the committed fixture pin above is the CI floor).

    39.2 rig note: the frozen pre-38-2 run carries the legacy Ask-B STUB
    contribution (``stub_status: not_yet_wired``) at ``07W.4`` — under the
    39.2 re-point the strict Ask-B reader fail-louds on it BY DESIGN (W-1).
    On a live run the band's reconcile-upgrade replaces the stub before the
    terminal producer consumes, so the honest replay posture is empty class
    (a): replay off a tmp COPY with the stub dropped (the frozen run dir is
    never mutated); the exercise-composition pins are Ask-B-independent.
    """
    if not (RUN_8B275E5B / "g0-enrichment.json").is_file():
        pytest.skip("run 8b275e5b artifacts unavailable")
    fixture = _load_composition_fixture()
    replay_dir = tmp_path / "8b275e5b-replay"
    shutil.copytree(RUN_8B275E5B, replay_dir)
    trial = json.loads((replay_dir / "run.json").read_text(encoding="utf-8"))
    envelope = trial.get("production_envelope", trial)
    envelope["contributions"] = [
        contribution
        for contribution in envelope["contributions"]
        if not (
            contribution["specialist_id"] == "ask_b_hot_topics"
            and contribution.get("node_id") == "07W.4"
            and isinstance(contribution.get("output"), dict)
            and contribution["output"].get("stub_status") == "not_yet_wired"
        )
    ]
    (replay_dir / "run.json").write_text(
        json.dumps(trial, ensure_ascii=False), encoding="utf-8"
    )
    inputs = wb_act.build_workbook_inputs(replay_dir, run_id="8b275e5b")
    assert inputs is not None
    kept_by_section = {
        sec.section_id: [ex.exercise_id for ex in sec.exercises]
        for sec in inputs.spec.sections
    }
    assert kept_by_section == fixture["expected"]["kept_by_section"]
    assert inputs.exercise_overlay_loss is not None
    assert (
        inputs.exercise_overlay_loss["trimmed_exercise_ids"]
        == fixture["expected"]["trimmed_exercise_ids"]
    )
    # Origin rides the FIELD on every composed exercise.
    for sec in inputs.spec.sections:
        for ex in sec.exercises:
            expected_origin = (
                "enrichment"
                if ex.exercise_id.startswith(_OVERLAY_EXERCISE_ID_PREFIX)
                else "collateral"
            )
            assert ex.origin == expected_origin, ex.exercise_id
    # Row e substrate: every attached overlay exercise's worked answer was
    # re-keyed to the rendered (prefixed) id.
    for row in fixture["sections"]:
        for cid in row["overlay_component_ids"]:
            assert _OVERLAY_EXERCISE_ID_PREFIX + cid in inputs.answer_keys


# ---------------------------------------------------------------------------
# Rows a/d/e/f/g — end-to-end through the REAL attach seam + renderer
# ---------------------------------------------------------------------------

_SEGMENTS = [
    {
        "segment_id": "seg-01",
        "id": "seg-01",
        "slide_id": "slide-01",
        "narration_text": (
            "Healthcare delivery is shifting toward proactive, population-focused "
            "models and clinician leadership."
        ),
    },
]
_CORPUS = (
    "Healthcare delivery shifts toward proactive, population-focused models and "
    "clinician leadership; administrative friction is a redesignable surface.\n"
)


def _quiz_card(
    quizzes: list[dict[str, Any]], objective_ids: list[str]
) -> dict[str, Any]:
    """A minimal flat enrichment-card payload: quiz components + annotations.

    ``lo_refs`` home each quiz; provisional LOs bind the collateral's
    ``lo-g0-*`` objective ids DIRECTLY (no authority-map bridge needed).
    """
    return {
        "typed_components": [
            {
                "component_id": quiz["cid"],
                "source_type": "quiz",
                "excerpt": quiz["excerpt"],
                "label": quiz.get("label", quiz["cid"]),
            }
            for quiz in quizzes
        ],
        "provisional_los": [
            {
                "objective_id": oid,
                "statement": f"Objective statement for {oid} without figures.",
            }
            for oid in objective_ids
        ],
        "citation_resolutions": [],
        "pedagogy_annotations": [
            {
                "component_id": quiz["cid"],
                "lo_refs": quiz["lo_refs"],
                "bloom": "understand",
                "pedagogical_role": "assessment",
                "teaches_after": [],
                "prerequisite_concepts": [],
                "assessment_link": None,
                "teachable": True,
                "rationale": "fixture quiz",
                "transform_model": "marcus",
                "transform_version": "ped-v1",
                "generated_at": "2026-07-16T00:00:00Z",
            }
            for quiz in quizzes
        ],
    }


def _collateral(sections_spec: list[dict[str, Any]]) -> dict[str, Any]:
    return collateral_present(
        [
            section(
                row["section_id"],
                row["objective_id"],
                title=f"Section {row['section_id']}",
                deferred_depth=(
                    f"The deferred read-channel depth for {row['section_id']}: a "
                    "fuller derivation the glance deck cannot carry."
                ),
                exercises=[
                    {
                        "exercise_id": ex_id,
                        "bloom_level": "analyze",
                        "prompt_intent": f"Practice intent for {ex_id} without figures.",
                        "answer_key_source_ref": f"src-ref-{ex_id}",
                    }
                    for ex_id in row.get("exercises", [])
                ],
                narrative_intent=f"The fuller narrative for {row['section_id']}.",
            )
            for row in sections_spec
        ]
    )


def _make_run_dir(
    root: Path, card: dict[str, Any] | None, collateral: dict[str, Any]
) -> Path:
    run_dir = root / "run"
    (run_dir / "exports").mkdir(parents=True, exist_ok=True)
    (run_dir / "bundle").mkdir(parents=True, exist_ok=True)
    (run_dir / "exports" / "segment-manifest-storyboard-b.yaml").write_text(
        yaml.safe_dump({"segments": _SEGMENTS}, sort_keys=False), encoding="utf-8"
    )
    (run_dir / "bundle" / "extracted.md").write_text(_CORPUS, encoding="utf-8")
    if card is not None:
        (run_dir / "g0-enrichment.json").write_text(json.dumps(card), encoding="utf-8")
    write_run_json(
        run_dir,
        collateral=collateral,
        plan_units=[{"unit_id": "u-merge-fixture"}],
        lesson_summary="exercise merge composition fixture lesson",
    )
    return run_dir


@pytest.fixture
def output_root() -> Iterator[Path]:
    target = (
        REPO_ROOT
        / "_bmad-output"
        / "artifacts"
        / "workbooks-test-s7"
        / f"_391b-{uuid.uuid4().hex}"
    )
    target.mkdir(parents=True, exist_ok=True)
    try:
        yield target
    finally:
        shutil.rmtree(target, ignore_errors=True)


def _produce(run_dir: Path, output_root: Path):
    inputs = wb_act.build_workbook_inputs(run_dir, run_id="merge391btest")
    assert inputs is not None
    producer = WorkbookProducer(output_root=str(output_root))
    sidecar = producer.produce(
        inputs.plan_unit,
        inputs.context,
        spec=inputs.spec,
        segments=inputs.segments,
        source_text=inputs.source_text,
        citations=inputs.citations,
        source_ref_manifest=inputs.source_ref_manifest,
        vo_script_text=inputs.vo_script_text,
        learning_objectives=inputs.learning_objectives,
        answer_keys=inputs.answer_keys,
        further_reading=inputs.further_reading,
        research_entries=inputs.research_entries,
        research_supplements=inputs.research_supplements,
        lo_overlay_loss=inputs.lo_overlay_loss,
        exercise_overlay_loss=inputs.exercise_overlay_loss,
        diff_files=["app/marcus/lesson_plan/workbook_producer.py"],
        reuse_sha="merge391b",
    )
    markdown = (REPO_ROOT / sidecar.markdown_path).read_text(encoding="utf-8")
    return inputs, sidecar, markdown


def test_row_a_pre_prefix_identity_collision_disambiguated(
    tmp_path: Path, output_root: Path
) -> None:
    """Row a: overlay component id == collateral exercise id — the ``g0-``
    prefix disambiguates and BOTH render (never a silent drop)."""
    card = _quiz_card(
        [
            {
                "cid": "shared-id",
                "excerpt": "Which delivery model is population-focused?",
                "lo_refs": ["lo-g0-001"],
            }
        ],
        ["lo-g0-001"],
    )
    run_dir = _make_run_dir(
        tmp_path,
        card,
        _collateral(
            [
                {
                    "section_id": "sec-lo-g0-001",
                    "objective_id": "lo-g0-001",
                    "exercises": ["shared-id"],
                }
            ]
        ),
    )
    inputs, _, markdown = _produce(run_dir, output_root)
    composed = [
        ex.exercise_id for sec in inputs.spec.sections for ex in sec.exercises
    ]
    assert composed == ["shared-id", "g0-shared-id"]
    assert "#### Exercise `shared-id`" in markdown
    assert "#### Exercise `g0-shared-id`" in markdown


def test_row_a_residual_collision_fails_loud(tmp_path: Path, output_root: Path) -> None:
    """Row a (residual): collateral authored BOTH ``x`` and ``g0-x`` while the
    overlay carries ``x`` -> the prefixed overlay id collides with the
    collateral ``g0-x`` and ``assert_unique_collateral_ids`` fails LOUD."""
    card = _quiz_card(
        [
            {
                "cid": "colliding",
                "excerpt": "Which friction is a system-design problem?",
                "lo_refs": ["lo-g0-001"],
            }
        ],
        ["lo-g0-001"],
    )
    run_dir = _make_run_dir(
        tmp_path,
        card,
        _collateral(
            [
                {
                    "section_id": "sec-lo-g0-001",
                    "objective_id": "lo-g0-001",
                    "exercises": ["colliding", "g0-colliding"],
                }
            ]
        ),
    )
    inputs = wb_act.build_workbook_inputs(run_dir, run_id="merge391btest")
    assert inputs is not None
    producer = WorkbookProducer(output_root=str(output_root))
    with pytest.raises(DuplicateCollateralIdError):
        producer.produce(
            inputs.plan_unit,
            inputs.context,
            spec=inputs.spec,
            segments=inputs.segments,
            source_text=inputs.source_text,
            citations=inputs.citations,
            source_ref_manifest=inputs.source_ref_manifest,
            learning_objectives=inputs.learning_objectives,
            answer_keys=inputs.answer_keys,
            research_supplements=inputs.research_supplements,
            lo_overlay_loss=inputs.lo_overlay_loss,
            exercise_overlay_loss=inputs.exercise_overlay_loss,
            diff_files=["app/marcus/lesson_plan/workbook_producer.py"],
            reuse_sha="merge391b",
        )


def test_row_d_labels_render_per_unit_and_answer_key_mirrors(
    tmp_path: Path, output_root: Path
) -> None:
    card = _quiz_card(
        [
            {
                "cid": "check-one",
                "excerpt": "Which model is proactive rather than reactive?",
                "lo_refs": ["lo-g0-001"],
            }
        ],
        ["lo-g0-001", "lo-g0-002"],
    )
    run_dir = _make_run_dir(
        tmp_path,
        card,
        _collateral(
            [
                {
                    "section_id": "sec-lo-g0-001",
                    "objective_id": "lo-g0-001",
                    "exercises": ["ex-practice-a"],
                },
                {
                    "section_id": "sec-lo-g0-002",
                    "objective_id": "lo-g0-002",
                    "exercises": ["ex-practice-b"],
                },
            ]
        ),
    )
    _, sidecar, markdown = _produce(run_dir, output_root)
    # Exercises block: per-unit labels, keyed on the origin FIELD.
    assert f"### {PRACTICE_GROUP_LABEL} — section `sec-lo-g0-001`" in markdown
    assert f"### {COURSE_CHECK_GROUP_LABEL} — section `sec-lo-g0-001`" in markdown
    assert f"### {PRACTICE_GROUP_LABEL} — section `sec-lo-g0-002`" in markdown
    # Section 2 has no overlay item: no phantom Course Check group for it.
    assert f"### {COURSE_CHECK_GROUP_LABEL} — section `sec-lo-g0-002`" not in markdown
    # The Answer Key mirrors the SAME labels (once per block => twice total).
    assert markdown.count(f"### {PRACTICE_GROUP_LABEL} — section `sec-lo-g0-001`") == 2
    assert (
        markdown.count(f"### {COURSE_CHECK_GROUP_LABEL} — section `sec-lo-g0-001`")
        == 2
    )
    # The composition receipt records the same grouping (structured side).
    receipt = sidecar.exercise_composition
    assert receipt is not None
    assert receipt["sections"][0] == {
        "section_id": "sec-lo-g0-001",
        "practice": ["ex-practice-a"],
        "course_check": ["g0-check-one"],
    }
    assert receipt["collateral_trimmed_count"] == 0
    assert sidecar.exercise_overlay_loss is None
    assert EXERCISE_OVERLAY_LOSS_CALLOUT not in markdown


def test_row_e_answer_key_mapping_mixed_keyed_unkeyed(
    tmp_path: Path, output_root: Path
) -> None:
    card = _quiz_card(
        [
            {
                "cid": "keyed-check",
                # Word-form answer keeps the G1 symbol gate a non-event; the
                # leak is stripped from the prompt and routed to answer_keys.
                "excerpt": (
                    "What is the primary driver of clinician burnout?\n"
                    "Correct Answer: administrative friction"
                ),
                "lo_refs": ["lo-g0-001"],
            }
        ],
        ["lo-g0-001"],
    )
    run_dir = _make_run_dir(
        tmp_path,
        card,
        _collateral(
            [
                {
                    "section_id": "sec-lo-g0-001",
                    "objective_id": "lo-g0-001",
                    "exercises": ["ex-unkeyed"],
                }
            ]
        ),
    )
    inputs, _, markdown = _produce(run_dir, output_root)
    # The keyed overlay exercise's worked answer was re-keyed to the rendered id.
    assert "g0-keyed-check" in inputs.answer_keys
    assert inputs.answer_keys["g0-keyed-check"].startswith("administrative friction")
    # Rendered under the Course Check label in the Answer Key block.
    answer_key_block = markdown[markdown.index("## Answer Key") :]
    answer_key_block = answer_key_block[: answer_key_block.index("\n## ", 1)]
    assert f"### {COURSE_CHECK_GROUP_LABEL} — section `sec-lo-g0-001`" in answer_key_block
    assert "#### Answer — `g0-keyed-check`" in answer_key_block
    assert "administrative friction (source-provided correct answer" in answer_key_block
    # The unkeyed collateral exercise renders the honest pending note.
    assert "#### Answer — `ex-unkeyed`" in answer_key_block
    assert "worked answer pending writer" in answer_key_block
    # The 47-pin floor holds on the rendered surface: no prompt leaks an answer.
    exercises_block = markdown[markdown.index("## Exercises") :]
    exercises_block = exercises_block[: exercises_block.index("## Answer Key")]
    assert "Correct Answer:" not in exercises_block


def test_row_f_zero_overlay_pure_practice(tmp_path: Path, output_root: Path) -> None:
    card = _quiz_card([], ["lo-g0-001"])  # LOs resolve; no quiz components
    run_dir = _make_run_dir(
        tmp_path,
        card,
        _collateral(
            [
                {
                    "section_id": "sec-lo-g0-001",
                    "objective_id": "lo-g0-001",
                    "exercises": ["ex-practice-a"],
                }
            ]
        ),
    )
    _, sidecar, markdown = _produce(run_dir, output_root)
    assert f"### {PRACTICE_GROUP_LABEL} — section `sec-lo-g0-001`" in markdown
    assert COURSE_CHECK_GROUP_LABEL not in markdown
    assert sidecar.exercise_overlay_loss is None
    assert EXERCISE_OVERLAY_LOSS_CALLOUT not in markdown


def test_row_g_zero_collateral_pure_course_check(
    tmp_path: Path, output_root: Path
) -> None:
    card = _quiz_card(
        [
            {
                "cid": "check-solo",
                "excerpt": "Which surface is redesignable?",
                "lo_refs": ["lo-g0-001"],
            }
        ],
        ["lo-g0-001"],
    )
    run_dir = _make_run_dir(
        tmp_path,
        card,
        _collateral(
            [
                {
                    "section_id": "sec-lo-g0-001",
                    "objective_id": "lo-g0-001",
                    "exercises": [],
                }
            ]
        ),
    )
    _, sidecar, markdown = _produce(run_dir, output_root)
    assert f"### {COURSE_CHECK_GROUP_LABEL} — section `sec-lo-g0-001`" in markdown
    # No phantom Practice group heading anywhere (matrix row g).
    assert f"### {PRACTICE_GROUP_LABEL} — section" not in markdown
    assert sidecar.exercise_overlay_loss is None


def test_visible_loss_callout_renders_when_cap_trims(
    tmp_path: Path, output_root: Path
) -> None:
    """AC 4: a trim is a visible callout in the Exercises block + the
    structured record on the sidecar — degrade-with-record, never silent."""
    card = _quiz_card([], ["lo-g0-001"])
    run_dir = _make_run_dir(
        tmp_path,
        card,
        _collateral(
            [
                {
                    "section_id": "sec-lo-g0-001",
                    "objective_id": "lo-g0-001",
                    # 3 collateral in one unit: per-unit cap 2 trims the third.
                    "exercises": ["ex-a", "ex-b", "ex-c"],
                }
            ]
        ),
    )
    _, sidecar, markdown = _produce(run_dir, output_root)
    assert sidecar.exercise_overlay_loss is not None
    assert sidecar.exercise_overlay_loss["trimmed_exercise_ids"] == ["ex-c"]
    assert sidecar.exercise_composition is not None
    assert sidecar.exercise_composition["collateral_trimmed_count"] == 1
    assert f"> _{EXERCISE_OVERLAY_LOSS_CALLOUT}" in markdown
    assert "ex-c" in markdown  # named in the callout
    assert "#### Exercise `ex-c`" not in markdown  # but not rendered as an item


def test_noteless_loss_record_renders_fallback_callout_never_none(
    tmp_path: Path, output_root: Path
) -> None:
    """T4 F8: a loss record with a missing/empty ``note`` (untyped dict from a
    harness caller) still renders an honest callout — never a literal "None",
    never a suppressed callout desyncing from the persisted record."""
    card = _quiz_card([], ["lo-g0-001"])
    run_dir = _make_run_dir(
        tmp_path,
        card,
        _collateral(
            [
                {
                    "section_id": "sec-lo-g0-001",
                    "objective_id": "lo-g0-001",
                    "exercises": ["ex-a"],
                }
            ]
        ),
    )
    inputs = wb_act.build_workbook_inputs(run_dir, run_id="merge391btest")
    assert inputs is not None
    producer = WorkbookProducer(output_root=str(output_root))
    sidecar = producer.produce(
        inputs.plan_unit,
        inputs.context,
        spec=inputs.spec,
        segments=inputs.segments,
        source_text=inputs.source_text,
        citations=inputs.citations,
        source_ref_manifest=inputs.source_ref_manifest,
        learning_objectives=inputs.learning_objectives,
        answer_keys=inputs.answer_keys,
        research_supplements=inputs.research_supplements,
        lo_overlay_loss=inputs.lo_overlay_loss,
        # Note-less loss record (harness-authored shape).
        exercise_overlay_loss={"trimmed_count": 1, "trimmed_exercise_ids": ["ex-x"]},
        diff_files=["app/marcus/lesson_plan/workbook_producer.py"],
        reuse_sha="merge391b",
    )
    markdown = (REPO_ROOT / sidecar.markdown_path).read_text(encoding="utf-8")
    assert f"> _{EXERCISE_OVERLAY_LOSS_CALLOUT}" in markdown  # callout ⇔ record
    assert f"{EXERCISE_OVERLAY_LOSS_CALLOUT} None_" not in markdown
    # F11: the receipt echoes the record verbatim (no laundering).
    assert sidecar.exercise_composition is not None
    assert sidecar.exercise_composition["collateral_trimmed_count"] == 1
