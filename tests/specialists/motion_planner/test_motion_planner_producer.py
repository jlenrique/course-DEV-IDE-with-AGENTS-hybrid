"""RED-first floors for the 07D.5 motion-plan producer (spec-07d5 §8).

Eight floors, all exercised with REAL deterministic fixture inputs (no mocks for
the producer logic — a small authorized_storyboard fixture drives the Epic-14
engine for real):

1. producer determinism + NO model client touched (amendment A invariant)
2. contract satisfaction — emitted motion_plan passes kira's payload contract
3. composer prune symmetry — motion deselected => 07D/07D.5/07E/07F absent AND
   deck-default byte-identical to the B1 baseline (amendment D)
4. kira ingestion equivalence — dict-fed == path-fed internal plan (amendment I)
5. 07E edge rewire — single motion_plan projection source; quinn_r tolerance gone
6. sound omitted from the Kling request unless explicitly enabled (absorbed fix 1)
7. pack_version uniformity — half-flip is detectable (amendment E)
8. L1 lockstep checks 9 + 10 green; 07D.5 traversed by BOTH walks (amendment H)
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import yaml

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.kira import _act as kira_act
from app.specialists.kira.payload_contract import CONSUMED_PAYLOAD_KEYS as KIRA_KEYS
from app.specialists.motion_planner import _act as mp_act

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"
MOTION_NODE_IDS = {"07D", "07D.5", "07E", "07F"}


# --- shared fixture (a small REAL authorized_storyboard) -------------------

AUTHORIZED_STORYBOARD: dict[str, Any] = {
    "run_id": "trial-fixture",
    "authorized_slides": [
        # creative scene cues -> video; carries an approved PNG -> image2video
        {
            "slide_id": "slide-00",
            "card_number": 4,
            "fidelity": "creative",
            "source_ref": "patient footage b-roll",
            "image_url": "https://cdn.example/img0.png",
        },
        # clinician/scene cues -> video; no image -> text2video
        {
            "slide_id": "slide-01",
            "card_number": 1,
            "fidelity": "creative",
            "source_ref": "clinician at the hospital crossroads scene",
        },
        # roadmap/journey + literal-visual -> animation
        {
            "slide_id": "slide-02",
            "card_number": 2,
            "fidelity": "literal-visual",
            "source_ref": "roadmap journey toward the future",
        },
        # literal-text -> static (NOT emitted)
        {
            "slide_id": "slide-03",
            "card_number": 3,
            "fidelity": "literal-text",
            "source_ref": "definition text block",
        },
    ],
}


def _payload() -> dict[str, Any]:
    return {"upstream_output": json.loads(json.dumps(AUTHORIZED_STORYBOARD))}


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


# --- Floor 1: producer determinism + NO model client touched ---------------


def test_producer_is_deterministic() -> None:
    out_a = mp_act.build_motion_plan(_payload())
    out_b = mp_act.build_motion_plan(_payload())
    assert out_a == out_b
    slide_ids = [s["slide_id"] for s in out_a["slides"]]
    # Only the three non-static slides, in sorted order.
    assert slide_ids == ["slide-00", "slide-01", "slide-02"]
    # One row per designated slide; library-sourced prompt + valid model id.
    for slide in out_a["slides"]:
        assert slide["model_name"] == "kling-v1-6"
        assert slide["model_name"] != "kling-v2-6"  # the stale/deprecated id
        assert slide["motion_prompt"].strip()
        assert slide["style_id"]
        assert slide["estimated_cost_usd"] <= 0.40  # under kira's per-invocation cap
    # image2video carries the PNG; text2video omits image_url.
    by_id = {s["slide_id"]: s for s in out_a["slides"]}
    assert by_id["slide-00"]["image_url"] == "https://cdn.example/img0.png"
    assert "image_url" not in by_id["slide-01"]


def test_act_touches_no_model_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """Amendment A pinned as a test INVARIANT: act() never constructs a model.

    Patch the model adapter to explode; act() must still succeed because the
    deterministic producer never resolves or invokes a model client.
    """

    def _boom(*args: Any, **kwargs: Any) -> Any:  # pragma: no cover - must not fire
        raise AssertionError("motion_planner act must not touch a model client")

    monkeypatch.setattr("app.models.adapter.make_chat_model", _boom)
    state = _seed_state(_payload())
    update = mp_act.act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["motion_plan"]["slides"]
    assert output["motion_planner"]["slide_count"] == 3
    assert update["model_resolution_trail"][-1].reason == "motion-planner.projected.ok"


def test_no_model_client_imports_in_act_module() -> None:
    source = (REPO_ROOT / "app" / "specialists" / "motion_planner" / "_act.py").read_text(
        encoding="utf-8"
    )
    assert "make_chat_model" not in source
    assert "ChatOpenAI" not in source


# --- Floor 2: contract satisfaction (kira ingests the emitted plan) ---------


def test_emitted_plan_satisfies_kira_payload_contract() -> None:
    assert "motion_plan" in KIRA_KEYS
    motion_plan = mp_act.build_motion_plan(_payload())
    # kira's loader + slide reader accept the produced plan without raising.
    loaded = kira_act._load_motion_plan({"motion_plan": motion_plan})
    slides = kira_act._slides_from_plan(loaded)
    assert len(slides) == 3
    for index, slide in enumerate(slides, start=1):
        assert kira_act._slide_id(slide, index)
        assert kira_act._prompt_for(slide)  # motion_prompt is read by kira
        assert kira_act._estimate_cost(slide) <= 0.40


# --- Floor 4: kira ingestion equivalence (dict-fed == path-fed) ------------


def test_kira_dict_fed_equals_path_fed(tmp_path: Path) -> None:
    motion_plan = mp_act.build_motion_plan(_payload())
    plan_path = tmp_path / "motion_plan.yaml"
    plan_path.write_text(yaml.safe_dump(motion_plan, sort_keys=False), encoding="utf-8")

    dict_fed = kira_act._load_motion_plan({"motion_plan": motion_plan})
    path_fed = kira_act._load_motion_plan({"motion_plan_path": str(plan_path)})
    assert dict_fed == path_fed
    assert kira_act._slides_from_plan(dict_fed) == kira_act._slides_from_plan(path_fed)


# --- Floor 5: 07E edge rewire (single source; quinn_r tolerance gone) -------


def _manifest_nodes() -> list[dict[str, Any]]:
    return yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))["nodes"]


def test_07e_consumes_single_motion_plan_projection() -> None:
    nodes = {n["id"]: n for n in _manifest_nodes()}
    node_07e = nodes["07E"]
    # No legacy quinn_r dependency edge survives (amendment C, fail-closed).
    assert not node_07e.get("dependencies")
    projections = node_07e.get("dependency_projections") or {}
    assert set(projections) == {"motion_plan"}
    assert projections["motion_plan"]["from"] == "motion_planner"
    assert projections["motion_plan"]["key"] == "motion_plan"


def test_07d5_producer_reads_the_winner_deck() -> None:
    nodes = {n["id"]: n for n in _manifest_nodes()}
    node = nodes["07D.5"]
    assert node["specialist_id"] == "motion_planner"
    assert node["dependencies"] == {"upstream_output": "quinn_r"}
    assert node["gate"] is False
    assert node["model_config_ref"] is None


# --- Floor 6: sound omitted from the Kling request unless enabled ----------


class _CapturingKling(kira_act.KlingClient):  # type: ignore[misc]
    def __init__(self) -> None:  # noqa: D401 - test double, skip real auth init
        self.bodies: list[dict[str, Any]] = []

    def post(self, path: str, json: dict[str, Any] | None = None, **_: Any) -> dict[str, Any]:  # type: ignore[override]
        self.bodies.append(dict(json or {}))
        return {"data": {"task_result": {"videos": [{"url": "https://cdn/x.mp4"}]}}}


def test_sound_absent_from_request_unless_enabled() -> None:
    client = _CapturingKling()
    # text2video with no native audio -> request body omits `sound` entirely.
    client.text_to_video(prompt="p", model_name="kling-v1-6", sound=None)
    assert "sound" not in client.bodies[-1]
    # explicitly enabled -> present.
    client.text_to_video(prompt="p", model_name="kling-v1-6", sound=True)
    assert client.bodies[-1]["sound"] is True
    # image2video parity.
    client.image_to_video("https://cdn/img.png", prompt="p", model_name="kling-v1-6", sound=None)
    assert "sound" not in client.bodies[-1]


def test_kira_default_model_is_not_the_stale_id() -> None:
    """Absorbed fix 2: the _call_generate_motion default model is a valid id."""
    captured: dict[str, Any] = {}

    class _Recorder:
        def generate_motion(self, **kwargs: Any) -> dict[str, Any]:
            captured.update(kwargs)
            return {"data": {"task_result": {"videos": [{"url": "https://cdn/x.mp4"}]}}}

    kira_act._call_generate_motion(_Recorder(), {"slide_id": "s1"}, prompt="p")  # type: ignore[arg-type]
    assert captured["model_name"] == "kling-v1-6"
    assert captured["model_name"] != "kling-v2-6"


# --- Floor 3: composer prune symmetry (amendment D) ------------------------


def test_motion_deselected_prunes_all_four_and_keeps_deck_byte_identical() -> None:
    from app.manifest import load
    from app.manifest.lanes import DEFAULT_RUN_MANIFEST_PATH
    from app.marcus.lesson_plan.composition import compose_manifest
    from app.models.state.component_selection import ComponentSelection

    manifest = load(DEFAULT_RUN_MANIFEST_PATH)

    # Full/default selection is a byte-identical no-op (deck-default baseline).
    default_composed = compose_manifest(manifest, ComponentSelection.production_default())
    assert default_composed is manifest or default_composed == manifest

    deck_only = compose_manifest(manifest, ComponentSelection(deck=True, motion=False))
    deck_ids = {n.id for n in deck_only.nodes}
    # All four motion nodes are absent as a unit.
    assert MOTION_NODE_IDS.isdisjoint(deck_ids)
    # Deck-default is byte-identical to the B1 baseline (every non-motion node
    # survives unchanged; deck-only composition is deterministic on repeat).
    expected_ids = {n.id for n in manifest.nodes} - MOTION_NODE_IDS
    assert deck_ids == expected_ids
    deck_only_again = compose_manifest(manifest, ComponentSelection(deck=True, motion=False))
    assert [n.model_dump() for n in deck_only.nodes] == [
        n.model_dump() for n in deck_only_again.nodes
    ]
    assert [e.model_dump() for e in deck_only.edges] == [
        e.model_dump() for e in deck_only_again.edges
    ]


# --- Floor 7: pack_version uniformity (half-flip detectable) ----------------


def test_pack_version_is_uniform_across_all_nodes() -> None:
    versions = {n.get("pack_version") for n in _manifest_nodes()}
    assert versions == {"v4.2"}, f"non-uniform pack_version: {sorted(versions)}"


def test_half_flipped_pack_version_is_detectable() -> None:
    nodes = _manifest_nodes()
    half_flipped = [dict(n) for n in nodes]
    # Flip exactly the new producer node to a different pack version.
    for node in half_flipped:
        if node["id"] == "07D.5":
            node["pack_version"] = "v4.3"
    versions = {n.get("pack_version") for n in half_flipped}
    assert len(versions) > 1  # the half-flip is RED to the uniformity invariant


# --- Floor 8: L1 lockstep + continuation-walk traversal --------------------


def test_l1_lockstep_checks_9_and_10_green() -> None:
    from scripts.utilities.check_pipeline_manifest_lockstep import DEFAULT_PACK_PATH, run_check

    exit_code, trace = run_check(MANIFEST_PATH, DEFAULT_PACK_PATH, None)
    assert exit_code == 0, trace
    passed = {c["check"]: c["pass"] for c in trace["l1_checks_run"]}
    assert passed.get(9) is True
    assert passed.get(10) is True


def test_07d5_is_traversed_by_both_walks() -> None:
    """Both the start and continuation walkers enumerate manifest.nodes in order
    (production_runner lines ~1924 and ~2471), so a node present in the manifest
    node list with its in/out edges is traversed by BOTH walks (amendment H)."""
    raw = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    node_ids = [n["id"] for n in raw["nodes"]]
    assert "07D.5" in node_ids
    assert node_ids.index("07D") < node_ids.index("07D.5") < node_ids.index("07E")
    edges = {(e["from"], e["to"]) for e in raw["edges"]}
    assert ("07D", "07D.5") in edges
    assert ("07D.5", "07E") in edges
    assert ("07D", "07E") not in edges  # the old direct edge is gone


# --- Party DONE-gate conditions (Murat C2/C3 + Winston fail-closed) ---------


def test_auto_designation_recommends_motion_without_an_explicit_designation() -> None:
    """Murat C2: the AUTO path (no operator designation) CAN recommend motion.

    Proves the producer is not dependent on an explicit Gate-2M override — fed a
    deck with motion-worthy slides and NO ``motion_designations``, the Epic-14
    recommendation engine designates >=1 video/animation slide on its own. (A
    conservative deck that scores all-static is intended behavior, not a bug: the
    engine errs toward static and the operator's 07D designation is the override.)
    """
    payload = _payload()
    assert "motion_designations" not in payload and "designations" not in payload
    out = mp_act.build_motion_plan(payload)
    assert len(out["slides"]) >= 1  # AUTO fired without any explicit designation
    assert out["slides"] == mp_act.build_motion_plan(_payload())["slides"]  # deterministic


def test_multi_entry_plan_projects_multiple_kira_receipts(tmp_path: Path) -> None:
    """Murat C3: a >1-designation plan projects multiple entries through kira.

    Closes the 'segment of one' coverage gap — the producer emits N>=2 slides and
    kira renders one receipt per slide (offline, fake client materializing files).
    """
    motion_plan = mp_act.build_motion_plan(_payload())
    assert len(motion_plan["slides"]) >= 2  # the fixture deck designates 3

    class _FakeKling:
        def __init__(self) -> None:
            self.calls = 0

        def generate_motion(self, **kwargs: Any) -> dict[str, Any]:
            self.calls += 1
            return {"data": {"task_status": "succeed",
                             "task_result": {"videos": [{"url": f"https://cdn/{self.calls}.mp4"}]}}}

        def download_video(self, video_url: object, output_path: object) -> Path:
            p = Path(str(output_path))
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"\x00\x00\x00\x18ftypmp42moovmdat")
            return p

    client = _FakeKling()
    verdict = kira_act.generate_motion_from_plan(
        {"motion_plan": motion_plan, "bundle_path": str(tmp_path)}, client=client
    )
    receipts = verdict["motion_receipts"]
    assert len(receipts) == len(motion_plan["slides"]) >= 2
    assert all(r["status"] == "success" for r in receipts)
    assert client.calls == len(receipts)


def test_fail_closed_on_missing_winner_deck() -> None:
    """Winston condition: no authorized winner deck => HARD fail, never a silent
    empty plan that 07E would consume. The producer cannot fabricate a deck."""
    with pytest.raises(mp_act.MotionPlannerActError) as exc_info:
        mp_act.build_motion_plan({"upstream_output": {"not_a_storyboard": True}})
    assert exc_info.value.tag == "motion-planner.storyboard.missing"
    # An entirely empty payload fails closed identically (no default emission).
    with pytest.raises(mp_act.MotionPlannerActError) as exc_info2:
        mp_act.build_motion_plan({})
    assert exc_info2.value.tag == "motion-planner.storyboard.missing"
