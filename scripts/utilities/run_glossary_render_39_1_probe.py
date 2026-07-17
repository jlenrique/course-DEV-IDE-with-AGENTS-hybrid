#!/usr/bin/env python3
"""One-shot, first-run-stands component probe for Story 39.1.

Probe id: ``probe-39-1-glossary-render-001`` (registered in the story spec
BEFORE it runs — probe honesty contract, wave-3940 party record D3).

Exact claim licensed: "the term-keyed glossary render, fed the frozen REAL
Ask-A pool (a940c5eb, 1 row) and the landed 37-2b bolded-term set for that
lesson, produces a workbook whose encyclopedia section carries exactly the
bolded terms as headwords — 'AI' association-covered with verbatim T4 tier +
resolving citation, every other term honest-uncovered — with the MD and DOCX
association invariants green." It licenses NOTHING else (not "the pipeline
works", not exercises, not run A).

Vehicle: DETERMINISTIC REPLAY-RENDER probe — this story adds NO new LLM
surface (the glossary writer is the deterministic default; the injectable
``GlossaryTermWriter`` seam is preserved for a future SME-prose writer). The
07W.3 contribution replays ZERO-CALL from the frozen 838524b8 completed
journal (probe-37-2b-deep-dive-enrichment-001's PASSING attempt — the path's
enrolled witness) through the production reconcile
(``run_workbook_review``), with a poison writer identity that FAILS LOUD if
any dispatch is attempted. provider_calls == 0 by construction.

Deterministic machine judge (named gates — no human vibes):
  1. headword-identity association: glossary ``###`` headwords == the frozen
     bolded-term set, in order, byte-exact (matrix rows f/h);
  2. covered-entry honesty: 'AI' carries ``ask-a-cite-001`` with
     ``tier=T4_peer_other`` VERBATIM (rows a/g);
  3. lean uncovered honesty: every other term carries the J-1 one-line note,
     zero citations/tiers (row c) + the section-lead coverage line;
  4. MD association: Deep-Dive bold set == glossary headword set (row h);
  5. DOCX association: bold runs in the Deep Dive region == Heading-3
     paragraphs in the glossary region, via python-docx (row i);
  6. citation resolvability + dedupe: ``ask-a-cite-001`` resolves ONCE into
     the cited-entries block (rows j + AC-A9);
  7. the deliverable-bar deep-dive + glossary clauses accept the artifact
     (the harness-side machine bar).

Evidence pack: immutable attempt dir under
``_bmad-output/implementation-artifacts/evidence/glossary-render-39-1-<id>/``
with input digests (pool packet digest, bolded-term-set digest, renderer
config identity), the rendered MD+DOCX, and the machine verdict JSON.
First-run-stands: a failed attempt is preserved immutably and remediated
under governance. On PASS the output freezes as this path's witness fixture
and enrolls in ``tests/live_witness_replay/witnesses.yaml`` (registry founded
by 37-2b).

``--dry-run``: preflight only — verify the frozen inputs, strict-revalidate
the frozen enriched result, and print the input-identity digests
(drift-flags amendment). NOTHING is written and no contribution is replayed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.marcus.lesson_plan.deep_dive_enrichment import (  # noqa: E402
    DeepDiveEnrichedResultV1,
)

PROBE_ID = "probe-39-1-glossary-render-001"
SCHEMA_VERSION = "glossary-render-39-1-probe-evidence.v1"
STORY = "39.1"

# Frozen REAL inputs: the PASSING 37-2b probe attempt (838524b8) carries the
# re-minted a940c5eb run.json + brief + Ask-A pool + the COMPLETED enrichment
# journal (the enrolled witness for the 07W.3 family). The trial id inside
# that run.json is part of the journal's idempotency identity — it is staged
# VERBATIM (never re-minted) so the zero-call replay reconciles.
FROZEN_RUN = (
    ROOT
    / "_bmad-output/implementation-artifacts/evidence"
    / "deep-dive-enrichment-37-2b-838524b8/run"
)
FROZEN_ARTIFACTS = (
    "run.json",
    "workbook-brief.v1.json",
    "ask-a-research-call.v1.json",
    "g0-enrichment.json",
    "workbook-deep-dive-enrichment-call.v1.json",
)
# The render additionally needs the run's segment manifest + corpus, which the
# 37-2b probe did not freeze (it exercised only the review node). They come
# from the SAME source run the frozen run.json was staged from.
SOURCE_RUN = ROOT / "runs/a940c5eb-1043-42c1-a2a4-8a6301b6bcf4"
SOURCE_EXTRAS = (
    "exports/segment-manifest-storyboard-b.yaml",
    "bundle/extracted.md",
)
COURSE_ROOT = ROOT / "course-content/courses/tejal-apc-c1-m1-p2-trends"
EVIDENCE_ROOT = ROOT / "_bmad-output/implementation-artifacts/evidence"
# P8a (probe honesty): the renderer-config identity covers EVERY module whose
# behavior the probe's claim rides on — the projection, the producer, the
# _act intake (authority selection + supplements), and the harness-side
# deliverable bar the machine judge invokes.
RENDERER_MODULES = (
    ROOT / "app/marcus/lesson_plan/glossary_projection.py",
    ROOT / "app/marcus/lesson_plan/workbook_producer.py",
    ROOT / "app/specialists/workbook_producer/_act.py",
    ROOT / "scripts/utilities/marcus_spoc_live_test_runner.py",
)

# P8d (probe honesty): the EXPECTED digests of every frozen input, pinned as
# constants. ``_input_digests()`` is COMPARED against this map — drift FAILS
# the probe (dry-run and full run alike), never merely recorded.
EXPECTED_INPUT_DIGESTS = {
    "run.json": (
        "sha256:99c3f21d85753ba65dbb982c4b29698a83f9ffbdb4b73c6aa2ec16fd79e4a135"
    ),
    "workbook-brief.v1.json": (
        "sha256:a72aa8028fec3c2e7cd64f3d7e1d0cb62a4153a652e8e888c33bd00e7a696636"
    ),
    "ask-a-research-call.v1.json": (
        "sha256:4f4d7849cdfc53154430c7c8120cde3ea71eab8dc6fc873ed976f47de7b7155e"
    ),
    "g0-enrichment.json": (
        "sha256:a6ff6f29b559ec9b1b2902b8879048cdef78efb5bbefa4d6aa4e264b8d7b71a5"
    ),
    "workbook-deep-dive-enrichment-call.v1.json": (
        "sha256:8d32ce0fbbe262beee8faa7645bd947c9eebb513ec49768669692c55f330a6ee"
    ),
    "exports/segment-manifest-storyboard-b.yaml": (
        "sha256:ac27203dfa5ab871d0947d82e1a32859e11a4a855a193f3b47c52c7ed9bf4847"
    ),
    "bundle/extracted.md": (
        "sha256:07875ae66344e7ae9b7e06b2fe8d9cc0b1295eb16d50976a3a8ec46d10262f46"
    ),
}


class _PoisonDispatchError(AssertionError):
    pass


class InputDriftError(ValueError):
    """A frozen probe input's digest drifted from its pinned constant (P8d)."""


class _FrozenIdentityWriter:
    """Writer identity for journal replay; FAILS LOUD on any dispatch.

    P8b: ``calls`` is a real invocation counter — the verdict's
    ``provider_calls`` is MEASURED off it, never asserted as a constant.
    """

    def __init__(self, model_config_digest: str, default_model: str | None) -> None:
        self.model_config_digest = model_config_digest
        self.model_config = SimpleNamespace(default_model=default_model)
        self.calls = 0

    def __call__(self, request: object) -> object:
        self.calls += 1
        raise _PoisonDispatchError(
            "deterministic replay probe must never dispatch a provider call"
        )


def _sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _frozen_journal() -> dict:
    return json.loads(
        (FROZEN_RUN / "workbook-deep-dive-enrichment-call.v1.json").read_text("utf-8")
    )


def _frozen_result(journal: dict) -> DeepDiveEnrichedResultV1:
    return DeepDiveEnrichedResultV1.model_validate_json(
        json.dumps(journal["result"], separators=(",", ":"), ensure_ascii=False),
        strict=True,
    )


def _bold_term_set_digest(terms: list[str]) -> str:
    canonical = json.dumps(terms, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _renderer_config_identity() -> str:
    digest = hashlib.sha256()
    for module in RENDERER_MODULES:
        digest.update(module.read_bytes())
    return "sha256:" + digest.hexdigest()


def _input_digests() -> dict[str, str]:
    digests = {name: _sha256_file(FROZEN_RUN / name) for name in FROZEN_ARTIFACTS}
    for rel in SOURCE_EXTRAS:
        digests[rel] = _sha256_file(SOURCE_RUN / rel)
    return digests


def _allocate_attempt_root() -> tuple[str, Path]:
    while True:
        attempt_id = str(uuid4())
        attempt_root = EVIDENCE_ROOT / f"glossary-render-39-1-{attempt_id[:8]}"
        try:
            attempt_root.mkdir(parents=True)
        except FileExistsError:
            continue
        return attempt_id, attempt_root


def _stage_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True)
    for name in FROZEN_ARTIFACTS:
        shutil.copy2(FROZEN_RUN / name, run_dir / name)
    for rel in SOURCE_EXTRAS:
        target = run_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE_RUN / rel, target)


def _inject_contribution(run_dir: Path, output_payload: dict, model_used: str) -> None:
    """Persist the replayed 07W.3 contribution into run.json (the production
    runner's dispatch normally does this; the probe replays that persistence
    so the producer's disk read sees the activated contribution)."""
    from app.models.runtime.production_envelope import (  # noqa: PLC0415
        SpecialistContribution,
    )
    from app.models.runtime.production_trial_envelope import (  # noqa: PLC0415
        ProductionTrialEnvelope,
    )

    trial = ProductionTrialEnvelope.model_validate_json(
        (run_dir / "run.json").read_text("utf-8")
    )
    envelope = trial.production_envelope
    kept = tuple(c for c in envelope.contributions if c.node_id != "07W.3")
    activated = SpecialistContribution.from_output(
        specialist_id="workbook_review",
        node_id="07W.3",
        output=output_payload,
        model_used=model_used,
    )
    envelope = envelope.model_copy(update={"contributions": (*kept, activated)})
    trial = trial.model_copy(update={"production_envelope": envelope})
    (run_dir / "run.json").write_text(trial.model_dump_json(indent=2) + "\n", "utf-8")


def _machine_judge(
    run_dir: Path, markdown_path: Path, docx_path: Path, terms: list[str]
) -> dict[str, object]:
    """Deterministic judge over the Package-A I/O-matrix gates + the bar."""
    import re  # noqa: PLC0415

    from docx import Document  # noqa: PLC0415

    from scripts.utilities import marcus_spoc_live_test_runner as runner  # noqa: PLC0415

    text = markdown_path.read_text(encoding="utf-8").replace("\r\n", "\n")

    def section(heading: str) -> str:
        marker = f"\n## {heading}\n"
        start = text.index(marker) + len(marker)
        rest = text[start:]
        nxt = rest.find("\n## ")
        return rest if nxt == -1 else rest[:nxt]

    glossary = section("Research Glossary")
    deep_dive = section("Deep Dive")
    references = section("References")
    headwords = re.findall(r"^### (.+?)\s*$", glossary, flags=re.MULTILINE)
    gate_headwords = headwords == terms
    coverage_line = f"Research coverage this run: 1 of {len(terms)} terms." in glossary

    chunks = re.split(r"^### .+$", glossary, flags=re.MULTILINE)
    bodies = dict(zip(headwords, chunks[1:], strict=True))
    ai_body = bodies.get("AI", "")
    gate_covered = (
        "**Provenance:** `ask-a-cite-001`" in ai_body
        and "tier=T4_peer_other" in ai_body
    )
    uncovered_line = (
        "Key term from the Deep Dive. No research row in this run's pool "
        "covers it; no definition is invented."
    )
    gate_uncovered = all(
        uncovered_line in body and "ask-a-cite-" not in body and "tier=" not in body
        for term, body in bodies.items()
        if term != "AI"
    )
    bold_terms = set(re.findall(r"\*\*([^*]+)\*\*", deep_dive))
    gate_md_association = bold_terms == set(headwords) == set(terms)

    document = Document(str(docx_path))
    region: str | None = None
    docx_bolds: set[str] = set()
    docx_h3: set[str] = set()
    for paragraph in document.paragraphs:
        style = paragraph.style.name if paragraph.style is not None else ""
        if style == "Heading 2":
            region = paragraph.text
            continue
        if region == "Deep Dive":
            for run in paragraph.runs:
                if run.bold and run.text.strip():
                    docx_bolds.add(run.text)
        elif region == "Research Glossary" and style == "Heading 3":
            docx_h3.add(paragraph.text)
    gate_docx_association = docx_bolds == docx_h3 == set(terms)

    gate_resolvability = references.count("citation_id: `ask-a-cite-001`") == 1

    try:
        runner._assert_deep_dive_conformant_markdown(run_dir, [markdown_path])
        runner._assert_glossary_conformant_markdown(run_dir, [markdown_path])
        gate_deliverable_bar = True
        bar_error = None
    except Exception as exc:  # first-run-stands: record, never retry
        gate_deliverable_bar = False
        bar_error = f"{type(exc).__name__}: {exc}"

    gates = {
        "headword_identity_association": gate_headwords,
        "covered_entry_verbatim_tier_and_citation": gate_covered,
        "lean_uncovered_honesty_plus_coverage_line": gate_uncovered and coverage_line,
        "md_bold_set_equals_headword_set": gate_md_association,
        "docx_association_python_docx": gate_docx_association,
        "citation_resolvability_deduped_once": gate_resolvability,
        "deliverable_bar_clauses": gate_deliverable_bar,
    }
    verdict = {
        "judge": gates,
        "pass": all(gates.values()),
        "headwords": headwords,
        "claim_licensed": (
            "term-keyed glossary render over the frozen a940c5eb pool + the "
            "landed 37-2b bolded-term set — headword-identity, covered/"
            "uncovered honesty, MD+DOCX association, citation resolvability"
            if all(gates.values())
            else "none"
        ),
    }
    if bar_error:
        verdict["deliverable_bar_error"] = bar_error
    return verdict


def _missing_inputs() -> list[str]:
    return [
        str(p)
        for p in [
            *(FROZEN_RUN / n for n in FROZEN_ARTIFACTS),
            *(SOURCE_RUN / r for r in SOURCE_EXTRAS),
        ]
        if not p.is_file()
    ]


def _digest_drift(digests: dict[str, str]) -> dict[str, dict[str, str | None]]:
    """P8d: compare measured digests against the pinned EXPECTED constants."""
    drift: dict[str, dict[str, str | None]] = {}
    for name, expected in EXPECTED_INPUT_DIGESTS.items():
        actual = digests.get(name)
        if actual != expected:
            drift[name] = {"expected": expected, "actual": actual}
    return drift


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="preflight only: verify frozen inputs + print identity digests; "
        "nothing is written",
    )
    args = parser.parse_args()

    if args.dry_run:
        # P8c-parallel: missing frozen inputs preflight-FAIL as a structured
        # verdict (never a bare traceback). Nothing is written in dry-run.
        preflight: dict[str, object] = {
            "schema_version": SCHEMA_VERSION,
            "probe_id": PROBE_ID,
            "mode": "dry-run-preflight",
            "deterministic_replay": True,
            "pass": False,
        }
        missing = _missing_inputs()
        if missing:
            preflight["missing_inputs"] = missing
            print(json.dumps(preflight, indent=2, sort_keys=True))
            return 1
        journal = _frozen_journal()
        result = _frozen_result(journal)
        terms = [marker.term for marker in result.bold_terms]
        digests = _input_digests()
        drift = _digest_drift(digests)
        preflight.update(
            {
                "input_digests": digests,
                "expected_input_digests": EXPECTED_INPUT_DIGESTS,
                "pool_packet_digest": journal["pool_packet_digest"],
                "bold_term_set_digest": _bold_term_set_digest(terms),
                "bold_term_count": len(terms),
                "renderer_config_identity": _renderer_config_identity(),
                "frozen_journal_state": journal.get("state"),
                "frozen_model_config_digest": journal.get("model_config_digest"),
                "frozen_witness": "deep-dive-enrichment-37-2b-838524b8",
                "result_status": result.status,
                # P8d: drift COMPARED, not just recorded — any drift fails.
                "input_digest_drift": drift,
                "pass": not drift and result.status == "enriched",
            }
        )
        print(json.dumps(preflight, indent=2, sort_keys=True))
        return 0 if preflight["pass"] else 1

    # P8c: the immutable attempt dir + verdict.json exist for EVERY attempt —
    # including one whose frozen inputs are missing or drifted (first-run-
    # stands: a failed attempt is preserved as evidence, never a traceback).
    attempt_id, attempt_root = _allocate_attempt_root()
    run_dir = attempt_root / "run"
    verdict_path = attempt_root / "verdict.json"
    verdict: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "probe_id": PROBE_ID,
        "story": STORY,
        "attempt_id": attempt_id,
        "started_at": datetime.now(UTC).isoformat(),
        "first_run_stands": True,
        "deterministic_replay": True,
        # P8b: MEASURED off the poison writer's invocation counter below;
        # ``None`` until the replay leg runs (never a hardcoded 0 claim).
        "provider_calls": None,
        "run_dir": run_dir.relative_to(ROOT).as_posix(),
        "pass": False,
    }
    writer: _FrozenIdentityWriter | None = None
    try:
        missing = _missing_inputs()
        if missing:
            verdict["missing_inputs"] = missing
            raise FileNotFoundError(
                f"frozen probe inputs missing: {', '.join(missing)}"
            )
        journal = _frozen_journal()
        result = _frozen_result(journal)
        terms = [marker.term for marker in result.bold_terms]
        digests = _input_digests()
        drift = _digest_drift(digests)
        verdict.update(
            {
                "input_digests": digests,
                "expected_input_digests": EXPECTED_INPUT_DIGESTS,
                "input_digest_drift": drift,
                "pool_packet_digest": journal["pool_packet_digest"],
                "bold_term_set_digest": _bold_term_set_digest(terms),
                "bold_term_count": len(terms),
                "renderer_config_identity": _renderer_config_identity(),
                "frozen_journal_state": journal.get("state"),
                "frozen_model_config_digest": journal.get("model_config_digest"),
                "frozen_witness": "deep-dive-enrichment-37-2b-838524b8",
            }
        )
        if drift:
            # P8d: drift FAILS the attempt — the claim is licensed only over
            # the pinned frozen inputs.
            raise InputDriftError(
                f"frozen input digest drift on: {', '.join(sorted(drift))}"
            )

        from app.marcus.lesson_plan.prework_artifact import (  # noqa: PLC0415
            WorkbookBriefRuntimeContext,
            read_workbook_brief,
        )
        from app.marcus.orchestrator.deep_dive_enrichment_wiring import (  # noqa: PLC0415
            run_workbook_review,
        )
        from app.models.runtime.production_trial_envelope import (  # noqa: PLC0415
            ProductionTrialEnvelope,
        )

        _stage_run(run_dir)
        trial = ProductionTrialEnvelope.model_validate_json(
            (run_dir / "run.json").read_text("utf-8")
        )
        receipt = journal.get("provider_receipt") or {}
        writer = _FrozenIdentityWriter(
            model_config_digest=str(journal["model_config_digest"]),
            default_model=receipt.get("model"),
        )
        context = WorkbookBriefRuntimeContext(
            run_dir=run_dir,
            course_source_root=COURSE_ROOT,
            encounter_mode="recorded",
            context_origin="operator_migrated",
            writer_execution_mode="live",
            deep_dive_enrichment_writer=writer,
        )
        # Zero-call replay through the production reconcile (journal-verified).
        output = run_workbook_review(
            run_dir=run_dir, trial_id=trial.trial_id, runtime_context=context
        )
        verdict["replay_reconciled"] = True
        # P8b: MEASURED provider-call count off the poison writer's counter
        # (any dispatch would ALSO have raised _PoisonDispatchError above).
        verdict["provider_calls"] = writer.calls
        _inject_contribution(run_dir, output, str(receipt.get("model") or "replay"))

        from app.marcus.lesson_plan.workbook_producer import (  # noqa: PLC0415
            WorkbookProducer,
        )
        from app.specialists.workbook_producer._act import (  # noqa: PLC0415
            build_workbook_inputs,
        )

        brief = read_workbook_brief(run_dir)
        inputs = build_workbook_inputs(
            run_dir, run_id=attempt_id[:8], validated_brief=brief
        )
        if inputs is None:
            raise ValueError("staged run declares no workbook")
        producer = WorkbookProducer(output_root=str(run_dir / "exports" / "workbooks"))
        sidecar = producer.produce(
            inputs.plan_unit,
            inputs.context,
            workbook_title=inputs.workbook_title,
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
            research_empty_reason=inputs.research_empty_reason,
            research_omitted_note=inputs.research_omitted_note,
            glossary_articles=inputs.glossary_articles,
            glossary_empty_reason=inputs.glossary_empty_reason,
            glossary=inputs.glossary,
            research_trends=inputs.research_trends,
            research_supplements=inputs.research_supplements,
            lo_overlay_loss=inputs.lo_overlay_loss,
            pre_work=inputs.pre_work,
            encounter_mode=inputs.encounter_mode,
            render_profile=inputs.render_profile,
            workbook_brief_receipt=inputs.workbook_brief_receipt,
            deep_dive_review=inputs.deep_dive_review,
        )
        markdown_path = ROOT / sidecar.markdown_path
        docx_path = ROOT / sidecar.docx_path
        judge = _machine_judge(run_dir, markdown_path, docx_path, terms)
        verdict.update(
            {
                "completed_at": datetime.now(UTC).isoformat(),
                "markdown_path": sidecar.markdown_path,
                "docx_path": sidecar.docx_path,
                "machine_judge": judge,
                "pass": bool(judge["pass"]),
                "claim_licensed": judge["claim_licensed"],
            }
        )
        if verdict["pass"]:
            verdict["enrollment_note"] = (
                "PASS: freeze this attempt dir as the glossary-render witness "
                "and enroll it in tests/live_witness_replay/witnesses.yaml "
                "(family workbook-glossary-render.v1, node 07W)"
            )
    except Exception as exc:  # first-run-stands: record; never retry
        verdict.update(
            {
                "completed_at": datetime.now(UTC).isoformat(),
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )
        if writer is not None:
            # P8b: still a measurement, even on a failed attempt.
            verdict["provider_calls"] = writer.calls
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True) + "\n", "utf-8")
    print(verdict_path.relative_to(ROOT).as_posix())
    print(json.dumps(verdict, sort_keys=True, default=str))
    return 0 if verdict.get("pass") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
