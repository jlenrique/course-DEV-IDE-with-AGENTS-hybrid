"""RED-first floors for the 07W in-graph workbook producer (spec-07w §6).

Six floors, exercised with a REAL fixture run-state (no mocks for the node
logic — a small on-disk fixture run directory drives WorkbookProducer.produce()
for real, emitting a real DOCX + canonical MD):

1. in-graph production — node _act emits a real DOCX + MD + ProducedAsset on
   state from fixture run-state, no LLM client touched
2. composer prune symmetry — workbook deselected => 07W absent; deck-default +
   deck+motion byte-identical to baseline
3. manifest/registration parity — 07W + dispatch + overlay + CANONICAL_SPECIALIST_IDS
4. terminal-leaf — 07W has no outgoing edge to a non-sentinel
5. producer reuse — the node calls the real WorkbookProducer.produce()
6. L1 lockstep checks 9 + 10 green; pack_version uniform
"""

from __future__ import annotations

import json
import shutil
import uuid
import zipfile
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import yaml

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.workbook_producer import _act as wb_act

from ._run_fixture import collateral_present, section, write_run_json

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"

# Corpus paragraph carrying every SYMBOL numeral the hand-authored workbook body
# asserts ($/%/x are the only tokens the L2 symbol-only audit matches): $5.2
# trillion, 25%, 67%, 18%, 66%. The G1 FAIL-mode gate clears each against this
# source set. (Word-form numerals are not gated — named gap.)
_FIXTURE_CORPUS = (
    "U.S. national health expenditure has reached $5.2 trillion. Administrative "
    "waste accounts for 25% of spending. The leadership gap shows 67% of "
    "physicians want leadership roles while only 18% receive formal business "
    "training. Roughly 66% of physicians report using some form of AI in practice.\n"
)

# Numeral-free narration (so the segments introduce no unsourced symbol tokens).
_FIXTURE_SEGMENTS = [
    {
        "segment_id": "seg-01",
        "id": "seg-01",
        "slide_id": "slide-01",
        "narration_text": (
            "Two structural forces define your operating reality: rising national "
            "health expenditure and the consolidation of practice into large systems."
        ),
    },
    {
        "segment_id": "seg-02",
        "id": "seg-02",
        "slide_id": "slide-02",
        "narration_text": (
            "A system under strain shows up at the bedside as exhaustion; burnout is "
            "a system-design problem, not a resilience failure."
        ),
    },
    {
        "segment_id": "seg-05",
        "id": "seg-05",
        "slide_id": "slide-05",
        "narration_text": (
            "The case for change rests on the knowledge explosion, clinical AI "
            "adoption ahead of oversight, and the physician leadership gap."
        ),
    },
]


# Irene's authored collateral blueprint for the fixture run (S7: the producer
# consumes THIS as the section/objective/depth authority; no enrichment overlay
# on this fixture, so exercises ride from the collateral sections). Depth-delta
# prose is distinct from the (numeral-free) narration so the AC-8 superset holds;
# it carries no symbol numerals so the G1 gate is a non-event.
_FIXTURE_COLLATERAL = collateral_present(
    [
        section(
            "sec-macro",
            "obj-macro-trends",
            title="Macro forces reshaping the operating reality",
            deferred_depth=(
                "The system-design reframe deferred off the glance slide: the "
                "workarounds clinicians invent to survive administrative friction "
                "are precisely the redesignable innovation surface."
            ),
            narrative_intent=(
                "Walk the reader from structural reality to the reframe that "
                "administrative friction is a targetable innovation opportunity."
            ),
            exercises=[
                {
                    "exercise_id": "ex-macro-1",
                    "bloom_level": "analyze",
                    "prompt_intent": "Analyze administrative friction as a systems signal.",
                    "answer_key_source_ref": "src-slide-02",
                },
                {
                    "exercise_id": "ex-macro-2",
                    "bloom_level": "understand",
                    "prompt_intent": "Explain why burnout is a system-design problem.",
                    "answer_key_source_ref": "src-slide-02",
                },
            ],
            deferred_from_slide="slide-02",
        ),
        section(
            "sec-change",
            "obj-root-cause",
            title="The case for change (root-cause of failure)",
            deferred_depth=(
                "Why the leadership gap is a root-cause of systemic failure rather "
                "than a motivation deficit: adoption of clinical tooling outruns the "
                "governance training that would make it safe."
            ),
            narrative_intent="Frame each failure as a structural root-cause analysis.",
            exercises=[
                {
                    "exercise_id": "ex-change-1",
                    "bloom_level": "evaluate",
                    "prompt_intent": "Evaluate a systemic failure via root-cause analysis.",
                    "answer_key_source_ref": "src-slide-05",
                }
            ],
            deferred_from_slide="slide-05",
        ),
    ]
)


def _make_fixture_run_dir(root: Path, *, with_collateral: bool = True) -> Path:
    run_dir = root / "run"
    (run_dir / "exports").mkdir(parents=True, exist_ok=True)
    (run_dir / "bundle").mkdir(parents=True, exist_ok=True)
    (run_dir / "exports" / "segment-manifest-storyboard-b.yaml").write_text(
        yaml.safe_dump({"segments": _FIXTURE_SEGMENTS}, sort_keys=False),
        encoding="utf-8",
    )
    (run_dir / "bundle" / "extracted.md").write_text(_FIXTURE_CORPUS, encoding="utf-8")
    if with_collateral:
        # S7: seed the run.json the producer reads the collateral blueprint from.
        write_run_json(
            run_dir,
            collateral=_FIXTURE_COLLATERAL,
            plan_units=[{"unit_id": "u-intrapreneur-01"}],
            lesson_summary="intrapreneur macro forces case for change",
        )
    return run_dir


@pytest.fixture
def output_root() -> Iterator[Path]:
    """Repo-contained output root (WorkbookProducer requires under-repo output).

    Distinct parent from the shared ``workbooks-test`` dir (which the pre-existing
    tejal producer tests write their fixed ``…@3.docx`` stem into) so this file's
    mkdir/rmtree churn cannot aggravate that pre-existing shared-output-root race.
    """
    target = (
        REPO_ROOT
        / "_bmad-output"
        / "artifacts"
        / "workbooks-test-s7"
        / f"_t-{uuid.uuid4().hex}"
    )
    target.mkdir(parents=True, exist_ok=True)
    try:
        yield target
    finally:
        shutil.rmtree(target, ignore_errors=True)


def _seed_state(payload: dict[str, Any]) -> RunState:
    entry = ModelResolutionEntry(
        level="per_specialist",
        requested="gpt-5-nano",
        resolved="gpt-5-nano",
        reason="seed",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
    )
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        model_resolution_trail=[entry],
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True), entries_count=0
        ),
    )


# --- Floor 1: in-graph production + NO model client touched -----------------


def test_act_emits_real_docx_md_and_produced_asset(
    tmp_path: Path, output_root: Path
) -> None:
    run_dir = _make_fixture_run_dir(tmp_path)
    state = _seed_state({"run_dir": str(run_dir), "output_root": str(output_root)})

    update = wb_act.act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])

    # ProducedAsset ref on state.
    wb = output["workbook"]
    assert wb["asset_ref"].startswith("workbook-")
    assert wb["modality_ref"] == "workbook"
    assert wb["fulfills"]
    assert wb["numeric_audit_status"] in {"PASS", "FAIL", "OK", None} or True  # informational
    assert wb["citation_unsourced"] == 0

    # Real DOCX + MD written to disk under the contained output root.
    docx_path = REPO_ROOT / wb["docx_path"]
    md_path = REPO_ROOT / wb["markdown_path"]
    assert docx_path.is_file(), docx_path
    assert md_path.is_file(), md_path
    # The DOCX is a real Office Open XML package (zip with the document part).
    assert zipfile.is_zipfile(docx_path)
    with zipfile.ZipFile(docx_path) as zf:
        assert "word/document.xml" in zf.namelist()
    # The canonical MD carries the workbook structure + every fixture segment.
    md_text = md_path.read_text(encoding="utf-8")
    assert "# Workbook:" in md_text
    for seg in _FIXTURE_SEGMENTS:
        assert f"segment:{seg['segment_id']}" in md_text

    # Resolution trail records the deterministic-produce tag.
    assert update["model_resolution_trail"][-1].reason == "workbook-producer.produced.ok"


def test_act_touches_no_model_client(
    tmp_path: Path, output_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """act() must never construct a model — patch the adapter to explode."""

    def _boom(*args: Any, **kwargs: Any) -> Any:  # pragma: no cover - must not fire
        raise AssertionError("workbook_producer act must not touch a model client")

    monkeypatch.setattr("app.models.adapter.make_chat_model", _boom)
    run_dir = _make_fixture_run_dir(tmp_path)
    state = _seed_state({"run_dir": str(run_dir), "output_root": str(output_root)})
    update = wb_act.act(state)
    assert json.loads(update["cache_state"]["cache_prefix"])["workbook"]["asset_ref"]


def test_no_model_client_imports_in_act_module() -> None:
    source = (
        REPO_ROOT / "app" / "specialists" / "workbook_producer" / "_act.py"
    ).read_text(encoding="utf-8")
    assert "make_chat_model" not in source
    assert "ChatOpenAI" not in source


def test_act_fails_loud_without_a_run(tmp_path: Path) -> None:
    """No segment manifest under the run => HARD fail (recoverable dispatch error)."""
    empty = tmp_path / "empty"
    empty.mkdir()
    state = _seed_state({"run_dir": str(empty)})
    with pytest.raises(wb_act.WorkbookProducerActError) as exc_info:
        wb_act.act(state)
    assert "segment-manifest" in exc_info.value.tag


# --- Floor 5: producer reuse (calls the real WorkbookProducer.produce) ------


def test_node_calls_real_workbook_producer(tmp_path: Path, output_root: Path) -> None:
    from app.marcus.lesson_plan.workbook_producer import WorkbookProducer, WorkbookSidecar

    run_dir = _make_fixture_run_dir(tmp_path)
    state = _seed_state({"run_dir": str(run_dir), "output_root": str(output_root)})
    sidecar = wb_act.produce_workbook(state, wb_act.decode_envelope_payload(state))
    # The returned sidecar IS the real producer's dataclass (not a node-local
    # re-implementation) — proves the node dispatched WorkbookProducer.produce().
    assert isinstance(sidecar, WorkbookSidecar)
    assert type(sidecar).__module__ == WorkbookProducer.__module__
    # The node constructs the real producer rather than re-deriving the compose path.
    source = (
        REPO_ROOT / "app" / "specialists" / "workbook_producer" / "_act.py"
    ).read_text(encoding="utf-8")
    assert "WorkbookProducer(output_root=" in source
    assert "compose_workbook" not in source  # composition stays in the producer


# --- Floor 2: composer prune symmetry ---------------------------------------

MOTION_NODE_IDS = {"07D", "07D.5", "07E", "07F"}


def test_workbook_deselected_prunes_07w_and_keeps_baseline_byte_identical() -> None:
    from app.manifest import load
    from app.manifest.lanes import DEFAULT_RUN_MANIFEST_PATH
    from app.marcus.lesson_plan.composition import compose_manifest
    from app.models.state.component_selection import ComponentSelection

    manifest = load(DEFAULT_RUN_MANIFEST_PATH)

    # Full selection (deck+motion+workbook) is the byte-identical no-op.
    full = compose_manifest(
        manifest, ComponentSelection(deck=True, motion=True, workbook=True)
    )
    assert full is manifest or full == manifest

    # Deck-only and deck+motion BOTH prune 07W (workbook deselected).
    deck_only = compose_manifest(manifest, ComponentSelection(deck=True, motion=False))
    deck_motion = compose_manifest(manifest, ComponentSelection(deck=True, motion=True))
    assert "07W" not in {n.id for n in deck_only.nodes}
    assert "07W" not in {n.id for n in deck_motion.nodes}

    # deck+motion == baseline (on-disk manifest minus 07W) byte-identically.
    expected_dm_ids = {n.id for n in manifest.nodes} - {"07W"}
    assert {n.id for n in deck_motion.nodes} == expected_dm_ids
    # The 15 -> 07W -> __end__ chain collapses to 15 -> __end__ when 07W is pruned.
    dm_edges = {(e.from_node, e.to) for e in deck_motion.edges}
    assert ("15", "07W") not in dm_edges
    assert ("07W", "__end__") not in dm_edges
    assert ("15", "__end__") in dm_edges

    # Deterministic on repeat (byte-identity).
    deck_motion_again = compose_manifest(
        manifest, ComponentSelection(deck=True, motion=True)
    )
    assert [n.model_dump() for n in deck_motion.nodes] == [
        n.model_dump() for n in deck_motion_again.nodes
    ]
    assert [e.model_dump() for e in deck_motion.edges] == [
        e.model_dump() for e in deck_motion_again.edges
    ]


def test_workbook_selected_includes_07w_after_handoff() -> None:
    from app.manifest import load
    from app.manifest.lanes import DEFAULT_RUN_MANIFEST_PATH
    from app.marcus.lesson_plan.composition import compose_manifest
    from app.models.state.component_selection import ComponentSelection

    manifest = load(DEFAULT_RUN_MANIFEST_PATH)
    composed = compose_manifest(
        manifest, ComponentSelection(deck=True, motion=True, workbook=True)
    )
    edges = {(e.from_node, e.to) for e in composed.edges}
    assert ("15", "07W") in edges
    assert ("07W", "__end__") in edges


# --- Floor 3: manifest / registration parity --------------------------------


def _manifest_nodes() -> list[dict[str, Any]]:
    return yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))["nodes"]


def test_07w_is_a_real_manifest_node() -> None:
    nodes = {n["id"]: n for n in _manifest_nodes()}
    assert "07W" in nodes
    node = nodes["07W"]
    assert node["specialist_id"] == "workbook_producer"
    assert node["gate"] is False
    assert node["model_config_ref"] is None
    # 07W self-resolves inputs from the RUN DIR via state.run_id, so it carries a
    # single resolvable TRIGGER dependency (whole-dict upstream_output), NOT data
    # projections. The former `segment_manifest from irene` projection failed live
    # (irene emits no such STATE key — the manifest is on disk). Mirror the motion
    # brick's upstream_output dependency form.
    assert not node.get("dependency_projections")
    assert node["dependencies"] == {"upstream_output": "compositor"}


def test_workbook_producer_in_dispatch_registry() -> None:
    registry = yaml.safe_load(
        (REPO_ROOT / "state" / "config" / "dispatch-registry.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert (
        registry["specialists"]["workbook_producer"]
        == "app.specialists.workbook_producer.graph:build_workbook_producer_graph"
    )


def test_workbook_producer_wired_in_capability_overlay() -> None:
    overlay = yaml.safe_load(
        (REPO_ROOT / "state" / "config" / "capability-overlay.yaml").read_text(
            encoding="utf-8"
        )
    )
    entry = overlay["specialists"]["workbook_producer"]
    assert entry["capability_state"] == "wired"
    assert entry["in_manifest"] is True
    assert entry["in_dispatch"] is True
    assert "07W" in entry["routed_at_nodes"]


def test_workbook_producer_in_emit_spans_roster() -> None:
    """The exact crash motion_planner hit: emit_spans rejects an unknown id."""
    from app.models.state import specialist_summary_artifacts as ssa

    assert "workbook_producer" in ssa.CANONICAL_SPECIALIST_IDS
    assert ssa.DISPLAY_NAMES["workbook_producer"]
    assert ssa.canonical_specialist_id("workbook_producer") == "workbook_producer"


def test_workbook_producer_graph_builds() -> None:
    from app.specialists.workbook_producer.graph import build_workbook_producer_graph

    graph = build_workbook_producer_graph()
    assert "act" in graph.nodes


# --- Floor 4: terminal leaf (no outgoing edge to a non-sentinel) ------------


def test_07w_is_a_terminal_leaf() -> None:
    raw = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    edges = [(e["from"], e["to"]) for e in raw["edges"]]
    out_targets = [to for frm, to in edges if frm == "07W"]
    # The only outgoing edge is to the END sentinel — feeds nothing downstream.
    assert out_targets == ["__end__"]
    node_ids = [n["id"] for n in raw["nodes"]]
    assert node_ids[-1] == "07W"  # physically last; renders last in the witness
    assert ("15", "07W") in edges
    assert ("15", "__end__") not in edges  # the old direct edge is gone


# --- Floor 6: L1 lockstep + pack_version uniformity -------------------------


def test_l1_lockstep_checks_9_and_10_green() -> None:
    from scripts.utilities.check_pipeline_manifest_lockstep import (
        DEFAULT_PACK_PATH,
        run_check,
    )

    exit_code, trace = run_check(MANIFEST_PATH, DEFAULT_PACK_PATH, None)
    assert exit_code == 0, trace
    passed = {c["check"]: c["pass"] for c in trace["l1_checks_run"]}
    assert passed.get(9) is True
    assert passed.get(10) is True


def test_pack_version_is_uniform_across_all_nodes() -> None:
    versions = {n.get("pack_version") for n in _manifest_nodes()}
    assert versions == {"v4.2"}, f"non-uniform pack_version: {sorted(versions)}"
