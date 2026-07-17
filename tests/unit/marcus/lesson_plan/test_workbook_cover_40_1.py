"""Story 40.1 — cover producer: placeholder hero + art-brief, journey-TOC,
provenance colophon. Deterministic I/O matrix rows a–k (row h's render diff is
FLIP-2 in ``test_workbook_s0_s7.py``; rows i/j land in the deliverable-bar
module ``test_workbook_deliverable_bar_40_1.py``).

Fixtures follow the live-shape rule (M-6): row g's absent/corrupt/symlink
``run.json`` shapes are MUTATED COPIES of the frozen live run
``runs/8b275e5b-ed8a-4720-8217-8ddaca4c6627`` (via the committed digest-bound
trimmed copy under ``tests/fixtures/cover_40_1/``) — never synthetic.

OFFLINE ONLY: no live LLM / network / Gamma calls. Deterministic throughout.
"""

from __future__ import annotations

import json
import shutil
import uuid
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

import pytest

from app.marcus.lesson_plan.prework_projection import (
    FRICTION_SCALE,
    PreWorkBrief,
    PreWorkProvenance,
    PromiseProjection,
    PromiseVow,
    SceneBrief,
)
from app.marcus.lesson_plan.produced_asset import ProductionContext
from app.marcus.lesson_plan.schema import PlanUnit
from app.marcus.lesson_plan.workbook_enrichment import run_identity_from_run
from app.marcus.lesson_plan.workbook_producer import (
    ABOUT_HEADING,
    CONTENTS_HEADING,
    COVER_ART_BRIEF_SCHEMA_VERSION,
    COVER_HEADING,
    COVER_HEADINGS,
    COVER_HERO_PLACEHOLDER_MARKER,
    CoverInputs,
    WorkbookProducer,
    compose_cover_sections,
    compose_workbook,
    cover_art_brief_digest,
    default_prose_revoicer,
    load_transcript_segments,
    render_markdown,
)
from app.specialists._shared.figure_tokens import _figures
from app.specialists.workbook_producer._act import _derive_display_title
from tests.marcus.lesson_plan.test_workbook_s0_s7 import (
    TEJAL_BUNDLE,
    TEJAL_MANIFEST,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "cover_40_1"
TRIMMED_RUN_JSON = FIXTURE_DIR / "run-8b275e5b.trimmed.run.json"
FIXTURE_MANIFEST = FIXTURE_DIR / "fixture-manifest.json"
COVER_FIXTURE_SCHEMA_VERSION = "cover-render-fixture.v1"


# --------------------------------------------------------------------------- #
# Builders (mirror test_workbook_s0_s7's real frozen-bundle fixtures)          #
# --------------------------------------------------------------------------- #


def _plan_unit() -> PlanUnit:
    return PlanUnit(
        unit_id="apc-c1m1-tejal-20260419b-motion-card-01",
        event_type="present-trends",
        source_fitness_diagnosis="frozen tejal deck — read-only inputs",
        weather_band="green",
        modality_ref="workbook",
    )


def _context() -> ProductionContext:
    return ProductionContext(lesson_plan_revision=3, lesson_plan_digest="abc123")


def _spec():
    from app.marcus.lesson_plan.collateral_spec import (
        DepthDeltaContract,
        Exercise,
        WorkbookSection,
        WorkbookSpec,
    )

    return WorkbookSpec(
        sections=[
            WorkbookSection(
                section_id="sec-a",
                learning_objective_id="obj-lo2",
                title="Chapter 2",
                depth_delta=DepthDeltaContract(
                    deferred_from_slide="slide-02",
                    deferred_depth="why administrative waste is an innovation target",
                ),
                narrative_intent="The fuller systems-design argument for chapter 2.",
                exercises=[
                    Exercise(
                        exercise_id="ex-a1",
                        bloom_level="analyze",
                        prompt_intent="Analyze the burnout driver.",
                        answer_key_source_ref="src-slide-02",
                    )
                ],
            ),
            WorkbookSection(
                section_id="sec-b",
                learning_objective_id="obj-lo4",
                title="Chapter 3",
                depth_delta=DepthDeltaContract(
                    deferred_from_slide="slide-05",
                    deferred_depth="the root-cause of the leadership gap",
                ),
                narrative_intent="The root-cause analysis for chapter 3.",
            ),
        ]
    )


def _prework(*, scene_text: str = "A patient transport delay blocks the work.") -> PreWorkBrief:
    scene = SceneBrief(
        status="authored",
        text=scene_text,
        source_refs=("assessment#Q5",),
        known_losses=(),
        marker=None,
        lesson_type="fresh_pain",
        archetype="external_friction",
    )
    promise = PromiseProjection(
        status="authored",
        vows=(PromiseVow(objective_id="obj-lo2", text="I can identify a first move."),),
        known_losses=(),
        marker=None,
    )
    return PreWorkBrief(
        scene=scene,
        friction_scale=FRICTION_SCALE,
        promise=promise,
        provenance=PreWorkProvenance(source_refs=scene.source_refs, known_losses=()),
    )


@pytest.fixture(scope="module")
def segments():
    return load_transcript_segments(TEJAL_MANIFEST)


def _compose(
    segments,
    *,
    pre_work: PreWorkBrief | None = "default",  # type: ignore[assignment]
    encounter_mode: str = "recorded",
    render_profile: str = "presentation_support",
    cover_inputs: CoverInputs | None = None,
    workbook_title: str | None = None,
):
    return compose_workbook(
        _plan_unit(),
        _context(),
        _spec(),
        segments,
        prose_revoicer=default_prose_revoicer,
        workbook_title=workbook_title,
        pre_work=_prework() if pre_work == "default" else pre_work,
        encounter_mode=encounter_mode,  # type: ignore[arg-type]
        render_profile=render_profile,  # type: ignore[arg-type]
        cover_inputs=cover_inputs,
    )


def _section_body(md: str, heading: str) -> str:
    marker = f"## {heading}\n"
    start = md.index(marker) + len(marker)
    rest = md[start:]
    nxt = rest.find("\n## ")
    return rest if nxt == -1 else rest[:nxt]


def _toc_targets(md: str) -> list[str]:
    import re

    return re.findall(r"^- .+ — `([^`]+)`$", _section_body(md, CONTENTS_HEADING), re.M)


def _fixture_manifest() -> dict:
    manifest = json.loads(FIXTURE_MANIFEST.read_text(encoding="utf-8"))
    # Digest-bound bump tripwire (live-shape rule M-6): a schema drift means
    # the fixture shape changed — re-derive from the frozen run.
    assert manifest["schema_version"] == COVER_FIXTURE_SCHEMA_VERSION
    return manifest


def _install_trimmed_run_json(run_dir: Path) -> dict:
    """MUTATED COPY of the frozen live run.json (committed trimmed slice)."""
    import hashlib

    manifest = _fixture_manifest()
    raw = TRIMMED_RUN_JSON.read_text(encoding="utf-8")
    assert (
        hashlib.sha256(raw.encode("utf-8")).hexdigest()
        == manifest["files"]["run-8b275e5b.trimmed.run.json"]
    )
    (run_dir / "run.json").write_text(raw, encoding="utf-8")
    return json.loads(raw)


# --------------------------------------------------------------------------- #
# Row a — cover renders FIRST; honest TEXT hero; no collision; no ###          #
# --------------------------------------------------------------------------- #


def test_row_a_cover_renders_first_with_honest_text_hero(segments) -> None:
    doc = _compose(segments)
    md = render_markdown(doc)
    headings = [heading for _level, heading, _body in doc.blocks]
    assert headings[:4] == [COVER_HEADING, CONTENTS_HEADING, ABOUT_HEADING, "Pre-work"]
    # H1-first MD floor untouched: the document H1 stays the first line.
    first_nonblank = next(line for line in md.splitlines() if line.strip())
    assert first_nonblank.startswith("# Workbook: ")
    # Heading-collision check: the three cover headings collide with NO other
    # composed heading (every _md_section_body-scoped bar check keeps scope).
    assert not set(COVER_HEADINGS) & set(headings[3:])
    cover_body = _section_body(md, COVER_HEADING)
    # Honest placeholder: the exported marker, visible alt-text, and the
    # art-brief pointer (path + digest); NEVER image syntax.
    assert COVER_HERO_PLACEHOLDER_MARKER in cover_body
    assert "![" not in cover_body
    assert "Alt-text: " in cover_body
    assert doc.cover_art_brief is not None
    digest = doc.cover_art_brief["self_digest"]
    stem = doc.cover_art_brief["workbook_stem"]
    assert (
        f"Art-brief: `{stem}.cover-art-brief.json` (sha256: {digest})" in cover_body
    )
    # Cover sub-content uses list items / paragraphs only — no ### headings
    # (the glossary entry-heading regex is section-scoped; keep it that way).
    for heading in COVER_HEADINGS:
        assert "\n### " not in "\n" + _section_body(md, heading)
    # Identity lines (AC 1): display title + unit id + fulfills target.
    assert (
        "Unit: `apc-c1m1-tejal-20260419b-motion-card-01` · fulfills "
        "`apc-c1m1-tejal-20260419b-motion-card-01@3`" in cover_body
    )


def test_row_a_hero_and_receipt_claim_placeholder_never_final_art(segments) -> None:
    doc = _compose(segments)
    assert doc.cover_receipt is not None
    assert doc.cover_receipt["hero"] == "placeholder"
    assert doc.cover_receipt["hero_marker"] == COVER_HERO_PLACEHOLDER_MARKER
    assert doc.cover_art_brief["hero_slot"] == "placeholder"


# --------------------------------------------------------------------------- #
# Row b — TOC bidirectional coverage, journey grouping, friendly labels        #
# --------------------------------------------------------------------------- #


def test_row_b_toc_bidirectional_coverage_and_journey_grouping(segments) -> None:
    doc = _compose(segments)
    md = render_markdown(doc)
    headings = [heading for _level, heading, _body in doc.blocks]
    section_headings = [h for h in headings if h not in COVER_HEADINGS] + [
        "Human Review Checkpoint"
    ]
    entries = doc.cover_receipt["toc"]
    # Exactly one entry per rendered H2 (+ the renderer-appended footer), and
    # every entry's target names a composed heading verbatim (bidirectional).
    assert [entry["target"] for entry in entries] == section_headings
    rendered_targets = _toc_targets(md)
    assert sorted(rendered_targets) == sorted(section_headings)
    assert len(set(rendered_targets)) == len(rendered_targets)
    # Every rendered ## heading matches a TOC target verbatim and vice versa.
    import re

    rendered_h2 = re.findall(r"(?m)^## (.*?)\s*$", md)
    assert set(rendered_targets) == {
        h for h in rendered_h2 if h not in COVER_HEADINGS
    }
    # Journey grouping (W-2 enumerated Before-you-watch keys).
    by_phase = {entry["target"]: entry["phase"] for entry in entries}
    for before in ("Pre-work", "Scene", "Friction Scale", "Promise"):
        assert by_phase[before] == "before"
    for after in (
        "Overview",
        "Learning Objectives",
        "Deep Dive",
        "Depth-delta narrative",
        "Exercises",
        "Answer Key",
        "Research Glossary",
        "References",
        "Research Trends",
        "Human Review Checkpoint",
    ):
        assert by_phase[after] == "after"
    # Friendly-label map applied ("Test yourself", not the raw heading).
    labels = {entry["target"]: entry["label"] for entry in entries}
    assert labels["Exercises"] == "Test yourself"
    assert labels["Research Trends"] == "What's next in the field"
    contents = _section_body(md, CONTENTS_HEADING)
    assert "- Test yourself — `Exercises`" in contents
    # Rhythm order: Before group -> [presentation] divider -> After group.
    assert (
        contents.index("**Before you watch**")
        < contents.index("*[The presentation")
        < contents.index("**After you watch**")
    )
    # TOC entries are list items only — never lines beginning "## ".
    assert not any(line.startswith("## ") for line in contents.splitlines())


def test_row_b_encounter_mode_receipt_and_brief_parity(segments) -> None:
    """Row h (receipt half; the render-diff half is FLIP-2 in
    test_workbook_s0_s7): the mode rides the receipt; the art-brief is
    byte-identical across modes (no mode content leaks into the brief)."""
    briefs = {}
    for mode in ("recorded", "live"):
        doc = _compose(segments, encounter_mode=mode)
        assert doc.cover_receipt["encounter_mode"] == mode
        briefs[mode] = json.dumps(doc.cover_art_brief, sort_keys=True)
    assert briefs["recorded"] == briefs["live"]


# --------------------------------------------------------------------------- #
# Row c — section-set variance flows into the TOC; legacy renders NO cover     #
# --------------------------------------------------------------------------- #


def test_row_c_legacy_profile_renders_no_cover_and_no_receipt(segments) -> None:
    doc = _compose(segments, pre_work=None, render_profile="legacy")
    headings = [heading for _level, heading, _body in doc.blocks]
    assert not set(COVER_HEADINGS) & set(headings)
    assert doc.cover_receipt is None
    assert doc.cover_art_brief is None
    md = render_markdown(doc)
    assert f"## {COVER_HEADING}" not in md


def test_row_c_toc_updates_when_section_set_changes(segments) -> None:
    with_prework = _compose(segments)
    without_prework = _compose(segments, pre_work=None)
    targets_with = {e["target"] for e in with_prework.cover_receipt["toc"]}
    targets_without = {e["target"] for e in without_prework.cover_receipt["toc"]}
    # Set-difference assertion: pre-work headings appear IFF the brief does.
    assert targets_with - targets_without == {
        "Pre-work",
        "Scene",
        "Friction Scale",
        "Promise",
    }
    # And the TOC follows the composed blocks exactly in both shapes.
    for doc in (with_prework, without_prework):
        composed = [
            h for _l, h, _b in doc.blocks if h not in COVER_HEADINGS
        ] + ["Human Review Checkpoint"]
        assert [e["target"] for e in doc.cover_receipt["toc"]] == composed


# --------------------------------------------------------------------------- #
# Row d — empty-honest sections keep their TOC entries                         #
# --------------------------------------------------------------------------- #


def test_row_d_empty_honest_sections_keep_toc_entries(segments) -> None:
    doc = _compose(segments)  # no glossary / trends supplied => empty-honest
    md = render_markdown(doc)
    targets = _toc_targets(md)
    assert "Research Glossary" in targets
    assert "Research Trends" in targets
    # The headings render unconditionally with empty-honest bodies.
    assert "recorded explicitly-empty" in _section_body(md, "Research Trends")


# --------------------------------------------------------------------------- #
# Row e — long display title (>120-char summary truncation) + unicode          #
# --------------------------------------------------------------------------- #


def test_row_e_long_unicode_title_h1_cover_brief_agree(segments, tmp_path) -> None:
    summary = (
        "Ce cours démontre pourquoi la transformation des systèmes de santé — "
        "économie, épuisement professionnel, données massives — exige des "
        "cliniciens-leaders façonnant l'innovation dès maintenant"
    )
    display = _derive_display_title({"lesson_summary": summary}, tmp_path)
    assert len(display) <= 121 and display.endswith("…")
    doc = _compose(segments, workbook_title=display)
    md = render_markdown(doc)
    assert md.splitlines()[0] == f"# Workbook: {display}"
    assert f"**{display}**" in _section_body(md, COVER_HEADING)
    assert doc.cover_art_brief["display_title"] == display
    # Byte-deterministic: same inputs, identical render.
    assert render_markdown(_compose(segments, workbook_title=display)) == md


# --------------------------------------------------------------------------- #
# Row f — byte-determinism double-produce (MD, DOCX, art-brief JSON + digest)  #
# --------------------------------------------------------------------------- #


@pytest.fixture
def output_root() -> Iterator[Path]:
    target = (
        REPO_ROOT
        / "_bmad-output"
        / "artifacts"
        / "workbooks-test"
        / f"_401f-{uuid.uuid4().hex}"
    )
    target.mkdir(parents=True, exist_ok=True)
    try:
        yield target
    finally:
        shutil.rmtree(target, ignore_errors=True)


def test_row_f_double_produce_is_byte_identical(segments, tmp_path, output_root) -> None:
    identity_dir = tmp_path / "identity"
    identity_dir.mkdir()
    _install_trimmed_run_json(identity_dir)
    cover_inputs = CoverInputs(
        run_identity=run_identity_from_run(identity_dir),
        sme_name="Fixture SME",
        deck_reference="exports/segment-manifest-storyboard-b.yaml",
    )
    source_text = (TEJAL_BUNDLE / "extracted.md").read_text(encoding="utf-8")
    producer = WorkbookProducer(output_root=str(output_root))

    def _produce():
        return producer.produce(
            _plan_unit(),
            _context(),
            spec=_spec(),
            segments=segments,
            source_text=source_text,
            pre_work=_prework(),
            encounter_mode="recorded",
            render_profile="presentation_support",
            cover_inputs=cover_inputs,
        )

    first = _produce()
    md_1 = (REPO_ROOT / first.markdown_path).read_bytes()
    docx_1 = (REPO_ROOT / first.docx_path).read_bytes()
    brief_1 = (REPO_ROOT / first.art_brief_path).read_bytes()
    second = _produce()
    assert (REPO_ROOT / second.markdown_path).read_bytes() == md_1
    assert (REPO_ROOT / second.docx_path).read_bytes() == docx_1  # B8 holds
    assert (REPO_ROOT / second.art_brief_path).read_bytes() == brief_1
    assert first.cover["art_brief"]["digest"] == second.cover["art_brief"]["digest"]
    # The written brief's self-digest recomputes from the canonical bytes.
    brief = json.loads(brief_1.decode("utf-8"))
    assert brief["schema_version"] == COVER_ART_BRIEF_SCHEMA_VERSION
    assert cover_art_brief_digest(brief) == brief["self_digest"]
    # Provenance rode the run artifacts, never wall-clock: the rendered date
    # equals the fixture envelope's started_at VALUE.
    raw = json.loads(TRIMMED_RUN_JSON.read_text(encoding="utf-8"))
    md_text = md_1.decode("utf-8")
    rendered_date = next(
        line.split("Generated: ", 1)[1]
        for line in md_text.splitlines()
        if line.startswith("Generated: ")
    )
    assert datetime.fromisoformat(rendered_date) == datetime.fromisoformat(
        raw["started_at"].replace("Z", "+00:00")
    )
    assert f"Production run: {raw['trial_id']}" in md_text


# --------------------------------------------------------------------------- #
# Row g — run.json absent vs corrupt vs symlink: DISTINCT honest reasons       #
# (fixtures = mutated copies of the frozen live run.json — M-6)               #
# --------------------------------------------------------------------------- #


def test_row_g_reader_ok_on_frozen_live_shape(tmp_path) -> None:
    raw = _install_trimmed_run_json(tmp_path)
    identity = run_identity_from_run(tmp_path)
    assert identity["status"] == "ok"
    assert identity["trial_id"] == raw["trial_id"]
    assert datetime.fromisoformat(identity["started_at"]) == datetime.fromisoformat(
        raw["started_at"].replace("Z", "+00:00")
    )
    assert identity["corpus_path"] == raw["corpus_path"]
    pairs = {
        (row["specialist_id"], row["node_id"], row["model_used"])
        for row in identity["models_used"]
    }
    expected = {
        (c["specialist_id"], c.get("node_id"), c["model_used"])
        for c in raw["production_envelope"]["contributions"]
    }
    assert pairs == expected  # J-2: collected for the RECEIPT only


def test_row_g_reader_distinguishes_absent_corrupt_symlink(tmp_path) -> None:
    absent_dir = tmp_path / "absent"
    absent_dir.mkdir()
    absent = run_identity_from_run(absent_dir)
    assert absent["status"] == "absent"

    corrupt_dir = tmp_path / "corrupt"
    corrupt_dir.mkdir()
    raw_bytes = TRIMMED_RUN_JSON.read_bytes()
    # Mutated COPY of the frozen live bytes (never synthetic): break the JSON.
    (corrupt_dir / "run.json").write_bytes(b"[" + raw_bytes[1:])
    corrupt = run_identity_from_run(corrupt_dir)
    assert corrupt["status"] == "corrupt"

    symlink_dir = tmp_path / "symlink"
    symlink_dir.mkdir()
    real_copy = tmp_path / "real-run.json"
    real_copy.write_bytes(raw_bytes)
    try:
        (symlink_dir / "run.json").symlink_to(real_copy)
    except OSError:
        pytest.skip("symlink creation not permitted in this environment")
    symlinked = run_identity_from_run(symlink_dir)
    assert symlinked["status"] == "symlink"

    reasons = {absent["reason"], corrupt["reason"], symlinked["reason"]}
    assert len(reasons) == 3  # three DISTINCT reason lines (W-1)


@pytest.mark.parametrize(
    ("status", "expected_reason"),
    [
        ("absent", "run.json is absent for this render"),
        ("corrupt", "run.json is corrupt or unparseable"),
        ("symlink", "run.json coordinate is a symlink (untrusted)"),
    ],
)
def test_row_g_provenance_renders_distinct_absent_reason_lines(
    segments, status: str, expected_reason: str
) -> None:
    doc = _compose(
        segments,
        cover_inputs=CoverInputs(
            run_identity={"status": status, "reason": f"probe {status}"},
        ),
    )
    md = render_markdown(doc)
    about = _section_body(md, ABOUT_HEADING)
    # The DISTINGUISHING reason line renders for run-id AND date AND corpus.
    assert f"Production run: not recorded — {expected_reason}" in about
    assert f"Generated: not recorded — {expected_reason}" in about
    assert f"Course corpus: not recorded — {expected_reason}" in _section_body(
        md, COVER_HEADING
    )
    # Never wall-clock backfilled: no dated Generated value line anywhere.
    assert not any(
        line.startswith("Generated: 2") for line in about.splitlines()
    )
    # The art-brief still emits (its inputs are compose-side) and the receipt
    # records the degrade.
    assert doc.cover_art_brief is not None
    degrade = doc.cover_receipt["provenance"]["identity_degrade"]
    assert degrade == {"status": status, "reason": f"probe {status}"}
    # Models-used stays receipt-only and honestly empty on a degraded read.
    assert doc.cover_receipt["provenance"]["models_used"] == []


def test_row_g_no_identity_supplied_degrades_honestly(segments) -> None:
    doc = _compose(segments, cover_inputs=None)
    about = _section_body(render_markdown(doc), ABOUT_HEADING)
    assert (
        "Production run: not recorded — no run identity was supplied to this render"
        in about
    )
    assert "Subject-matter expert: not recorded in this run's artifacts" in about
    assert "Source deck: not recorded in this run's artifacts" in about


# --------------------------------------------------------------------------- #
# Row k — unmapped H2 injected at compose level: never dropped (M-4)           #
# --------------------------------------------------------------------------- #


def test_row_k_unmapped_h2_falls_to_after_you_watch_verbatim(segments) -> None:
    # Compose-level injection: a scene text carrying its own "## " line lands
    # as a REAL unknown level-2 block via the pre-work splitter.
    doc = _compose(
        segments,
        pre_work=_prework(
            scene_text="A patient transport delay blocks the work.\n## Field Notes\nKeep a note."
        ),
    )
    headings = [heading for _level, heading, _body in doc.blocks]
    assert "Field Notes" in headings
    entries = [
        entry for entry in doc.cover_receipt["toc"] if entry["target"] == "Field Notes"
    ]
    # Exactly one TOC entry; falls to "After you watch"; verbatim-fallback label.
    assert len(entries) == 1
    assert entries[0]["phase"] == "after"
    assert entries[0]["label"] == "Field Notes"
    md = render_markdown(doc)
    contents = _section_body(md, CONTENTS_HEADING)
    assert "- Field Notes — `Field Notes`" in contents
    assert contents.index("**After you watch**") < contents.index(
        "- Field Notes — `Field Notes`"
    )


def test_row_k_pure_function_unknown_heading_never_dropped() -> None:
    blocks, receipt, art_brief = compose_cover_sections(
        ["Overview", "Utterly Unknown Section"],
        title_label="T",
        unit_id="u01",
        event_type="present",
        fulfills="u01@1",
        stem="u01@1",
        encounter_mode="recorded",
        themes=("theme-one",),
        palette_hints=("slate blue", "warm neutral accent"),
        bound_objective_ids=("obj-1",),
        cover_inputs=None,
    )
    targets = [entry["target"] for entry in receipt["toc"]]
    assert targets == ["Overview", "Utterly Unknown Section", "Human Review Checkpoint"]
    unknown = receipt["toc"][1]
    assert unknown["phase"] == "after" and unknown["label"] == "Utterly Unknown Section"
    assert art_brief["self_digest"] == cover_art_brief_digest(art_brief)
    assert [heading for _l, heading, _b in blocks] == list(COVER_HEADINGS)


# --------------------------------------------------------------------------- #
# G1 quiet-by-construction + B5 supplement idiom (AC 8)                        #
# --------------------------------------------------------------------------- #


def test_g1_cover_provenance_lines_carry_no_figure_tokens(segments, tmp_path) -> None:
    identity_dir = tmp_path / "identity"
    identity_dir.mkdir()
    _install_trimmed_run_json(identity_dir)
    doc = _compose(
        segments,
        cover_inputs=CoverInputs(run_identity=run_identity_from_run(identity_dir)),
    )
    md = render_markdown(doc)
    # The provenance date / run-id / digest / count numerals are invisible to
    # the symbol-only figure tokenizer — the cover adds ZERO figure tokens
    # beyond what the body already carries.
    for heading in (COVER_HEADING, ABOUT_HEADING, CONTENTS_HEADING):
        assert _figures(_section_body(md, heading)) == set()


def test_g1_symbol_bearing_theme_rides_b5_supplement(segments, output_root) -> None:
    """A theme string that DOES carry a symbol figure (an LO statement with a
    percent) clears G1 via the existing ``_authored_prose_figure_supplements``
    declaration idiom (B5) — the alt-text repeats a declared token, it never
    mints an undeclared one."""
    from app.marcus.lesson_plan.workbook_producer import LearningObjectiveBrief

    # The frozen tejal extract carries no symbol figures; give the source ONE
    # real figure token so the zero-denominator honesty gate does not fire and
    # the B5 supplement path is actually exercised (42% clears via the
    # declaration, not via the source).
    source_text = (
        (TEJAL_BUNDLE / "extracted.md").read_text(encoding="utf-8")
        + "\nAdministrative activity consumes 25% of spending.\n"
    )
    objectives = (
        LearningObjectiveBrief("obj-lo2", "analyze", "Cut administrative waste by 42%."),
        LearningObjectiveBrief("obj-lo4", "evaluate", "Evaluate the leadership gap."),
    )
    producer = WorkbookProducer(output_root=str(output_root))
    sidecar = producer.produce(
        _plan_unit(),
        _context(),
        spec=_spec(),
        segments=load_transcript_segments(TEJAL_MANIFEST),
        source_text=source_text,
        learning_objectives=objectives,
        research_supplements=_figures("Cut administrative waste by 42%."),
        # No pre-work: the LO statement is then among the first three themes,
        # so the rendered alt-text visibly repeats the declared 42% token.
        pre_work=None,
        encounter_mode="recorded",
        render_profile="presentation_support",
        cover_inputs=None,
    )
    md = (REPO_ROOT / sidecar.markdown_path).read_text(encoding="utf-8")
    assert "42%" in _section_body(md, COVER_HEADING)  # the alt-text carries it
    assert sidecar.numeric_audit["buckets"]["unsourced_numeric"]["count"] == 0


# T4 40-1 finding-1 remediation pin: the palette-hint map keys EVERY real
# SceneBrief.archetype Literal member (no dead keys, no silent default fall).
def test_palette_hint_map_keys_every_real_archetype() -> None:
    from typing import get_args

    from app.marcus.lesson_plan.prework_projection import SceneBrief
    from app.marcus.lesson_plan.workbook_producer import _COVER_PALETTE_HINTS

    literal = SceneBrief.model_fields["archetype"].annotation
    real = {a for arg in get_args(literal) for a in get_args(arg) if isinstance(a, str)}
    assert real, "archetype Literal members must be extractable"
    assert set(_COVER_PALETTE_HINTS) == real, (
        f"palette hints must key exactly the real archetype vocabulary; "
        f"map={sorted(_COVER_PALETTE_HINTS)} real={sorted(real)}"
    )
