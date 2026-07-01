"""Leg-3 per-sub-slide VO<->on-screen invariant driver (cluster c-u03).

WHAT THIS PROVES
----------------
The non-waivable 07G VO<->on-screen alignment invariant holds PER SUB-SLIDE on
the live *clustered* slide c-u03 (head "The Knowledge Explosion & New
Technologies" = slide-05, plus 2 interstitials slide-06/07). It drives the three
sub-slides through Gary render -> 07G vision perception -> Irene Pass-2 and
asserts, per sub-slide:

  (a) DISTINCT perception    -- 3 distinct source_png_path + 3 distinct slide_id,
                                each artifact reading_path_source == "llm_primary".
  (b) TRACEABLE references   -- every Pass-2 narration segment / delta visual
                                reference keys to ITS OWN slide_id (roster-join,
                                _assert_narration_joins_roster passes).
  (c) 0 figure-contradiction -- _assert_figure_citations_within_perceived passes:
                                no narrated figure absent from that slide's
                                perceived authority.
  (d) TRIP-WIRE (must RAISE) -- inject into ONE interstitial's narration `text`
                                a figure token present on the HEAD's perceived
                                figures but NOT on that interstitial's -> the
                                figure gate MUST raise Pass2GroundingError
                                (tag "irene.pass2.figure-contradiction").

MECHANISM MAP (verified against source 2026-07-01)
--------------------------------------------------
* Gary is bundle-driven: scripts/utilities/run_gary_dispatch.py::build_slides
  (:161) + build_base_params (:198). A bundle dir carries 5 files:
  gary-slide-content.json / gary-fidelity-slides.json / gary-theme-resolution.json
  / gary-outbound-envelope.yaml / gary-diagram-cards.json. Theme
  hil-2026-apc-nejal-A (theme_id njim9kuhfnljvaa) carries cardOptions.dimensions
  "16x9" + formatVariant classic. double_dispatch is NEVER set (avoids the
  all-illustrated crash at gamma_operations.py:746). ONE generate call -> 3 PNGs
  in <bundle>/gamma-export/.
* 07G vision: app/specialists/vision/_act.py::act(state) (:127) reads
  state.cache_state.cache_prefix JSON {"gary_slide_output":[{slide_id,file_path,
  card_number},...]} + a non-empty model_resolution_trail; each artifact's
  source_png_path is CODE-SET from the real PNG (provider.py:191) and slide_id is
  fail-loud verified (provider.py:182). reading_path_source is stamped
  "llm_primary" by with_llm_primary_reading_path on the LLM path.
* Pass-2: app/specialists/irene/graph.py::_act_pass_2 (:1862). envelope_payload
  needs bundle_reference (dir w/ extracted.md), gary_slide_output (3 rows),
  lesson_plan (probe plan), perception_artifacts (3 RICH
  app.models.perception.PerceptionArtifact). The roster (_slide_roster :163)
  derives perceived_figures per slide from the rich artifacts. Post-parse gates
  (:1918-1923): _assert_narration_joins_roster / _assert_reading_path_conformance
  / _assert_figure_citations_within_perceived (:673) / assert_pass2_surfaces_validatable.
* Figure gate (:673): perceived_by_slide[slide_id] = set(roster_entry
  ["perceived_figures"]); for each narration_script segment it tokenizes
  segment["text"] (fallback "narration_text") via figure_tokens._figures and
  raises when figures - perceived is non-empty. THE TRIP-WIRE MUTATES
  narration_script[*].text.

USAGE
-----
Offline plumbing validation (NO live API -- default):
    .venv/Scripts/python.exe scratchpad/leg3_perception_persubslide_driver.py --all
    # (equivalent: --build without --live runs every offline check)

Live sequence (run by the separate first-run-stands agent):
    .venv/Scripts/python.exe scratchpad/leg3_perception_persubslide_driver.py --build
    .venv/Scripts/python.exe scratchpad/leg3_perception_persubslide_driver.py --render   --live
    .venv/Scripts/python.exe scratchpad/leg3_perception_persubslide_driver.py --perceive --live
    .venv/Scripts/python.exe scratchpad/leg3_perception_persubslide_driver.py --author   --live
    .venv/Scripts/python.exe scratchpad/leg3_perception_persubslide_driver.py --tripwire --live
"""

# ruff: noqa: E501  (throwaway scratch driver; long source strings + dict literals kept inline for readability)
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

REPO = Path(r"C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS-hybrid")
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

SCRATCH = REPO / "scratchpad"
BUNDLE = SCRATCH / "leg3-c-u03-persubslide-bundle"
PROBE_PLAN = (
    REPO
    / "_bmad-output/implementation-artifacts/evidence"
    / "leg3-clustering-probe-20260701T014354Z/full-lesson-plan.json"
)

THEME_ID = "njim9kuhfnljvaa"
PARAM_SET = "hil-2026-apc-nejal-A"  # carries theme_id njim9kuhfnljvaa + 16x9 + classic
LESSON_SLUG = "apc-c1m1-tejal"
PLANNED_URL_BASE = "https://jlenrique.github.io/assets/gamma/c-u03-persubslide-probe"
RUN_ID = "C-U03-PERSUBSLIDE-PROBE"

# ---------------------------------------------------------------------------
# c-u03 sub-slide content (synthesized from plan_units title +
# master_behavioral_intent + narrative_arc; source-grounded to extracted Slide 3).
# Head narration carries "66%" (percent:66) -> head perceived authority holds it.
# Interstitial i2 (SMART/VR) carries NO percentage -> trip-wire target.
# ---------------------------------------------------------------------------
SUBSLIDES = [
    {
        "slide_number": 1,
        "slide_id": "S05",  # internal content id; real gary slide_id is derived
        "title": "The Knowledge Explosion & New Technologies",
        "mode": "creative",
        "cluster_role": "head",
        "cluster_id": "c-u03",
        "parent_slide_id": None,
        "cluster_interstitial_count": 2,
        "narrative_arc": "From technology overwhelm to innovation stewardship through staged evidence about knowledge acceleration, AI adoption, and care-delivery tools",
        "content": (
            "Conceptual timeline diagram, dark navy. Left: a steep exponential "
            "curve labeled 'Medical knowledge doubling: 50 years (1950) -> 73 "
            "days (today)'. Center callout: '66% of physicians now use AI in "
            "practice'. Right: three technology icons (AI oversight, remote "
            "monitoring, virtual reality). Clean sans-serif, high-contrast, modern.\n\n"
            "Narration anchor: 'Medical knowledge that once took 50 years to "
            "double now doubles in 73 days. 66% of physicians are now using some "
            "form of AI in practice, yet formal oversight training remains "
            "limited. Technology will reshape care -- it needs clinical "
            "innovators to steward it safely.'"
        ),
        "source_ref": "extracted.md - Slide 3 (Knowledge Explosion) narration",
        "extracted_text": (
            "The Knowledge Explosion & New Technologies. In 1950 it took 50 years "
            "for medical knowledge to double; today the doubling time is projected "
            "at just 73 days. 66% of physicians are now using some form of AI in "
            "practice, yet formal training on safe oversight remains severely limited."
        ),
    },
    {
        "slide_number": 2,
        "slide_id": "S06",
        "title": "Technology Tension: Adoption Is Outpacing Oversight",
        "mode": "creative",
        "cluster_role": "interstitial",
        "cluster_id": "c-u03",
        "parent_slide_id": "S05",
        "narrative_arc": "From technology overwhelm to innovation stewardship through staged evidence about knowledge acceleration, AI adoption, and care-delivery tools",
        "content": (
            "Single bold typographic tension slide, dark background. 'Adoption' in "
            "teal on the left, large upward arrow. 'Oversight' in muted amber on "
            "the right, a small flat line. A widening gap motif between them. No "
            "charts, no numerals -- a pure conceptual risk signal.\n\n"
            "Narration anchor: 'Here is the tension: adoption is racing ahead while "
            "formal oversight training lags behind. The risk signal is the gap "
            "itself -- capability outrunning our ability to supervise it safely.'"
        ),
        "source_ref": "extracted.md - Slide 3 risk beat (AI adoption vs. limited oversight training)",
        "extracted_text": (
            "Technology Tension: adoption is outpacing oversight. Clinical AI "
            "capability is being adopted faster than formal training for safe "
            "clinical supervision. The main risk signal is the widening gap between "
            "adoption and oversight."
        ),
    },
    {
        "slide_number": 3,
        "slide_id": "S07",
        "title": "Technology in Practice: From Reactive Care to Safer Learning",
        "mode": "creative",
        "cluster_role": "interstitial",
        "cluster_id": "c-u03",
        "parent_slide_id": "S05",
        "narrative_arc": "From technology overwhelm to innovation stewardship through staged evidence about knowledge acceleration, AI adoption, and care-delivery tools",
        "content": (
            "Split illustration, dark navy. Left panel: SMART remote-monitoring "
            "dashboard shifting care from reactive to proactive for COPD and heart "
            "failure. Right panel: a clinician in a VR headset rehearsing a "
            "procedure. Flat vector, teal/white palette. Upside-of-technology framing.\n\n"
            "Narration anchor: 'Used thoughtfully, technology delivers real upside. "
            "SMART remote monitoring shifts care from reactive to proactive, "
            "reducing avoidable emergencies. Virtual reality lets learners rehearse "
            "complex procedures without patient risk.'"
        ),
        "source_ref": "extracted.md - Slide 3 exemplar beat (SMART remote monitoring + VR training)",
        "extracted_text": (
            "Technology in Practice: from reactive care to safer learning. SMART "
            "remote monitoring shifts care from reactive to proactive for COPD and "
            "heart failure. Virtual reality transforms procedural training by "
            "letting learners rehearse complex scenarios without patient risk."
        ),
    },
]

EXTRACTED_MD = """# Source bundle: APC C1-M1 Part 2 -- c-u03 cluster (Knowledge Explosion)

# **Slide 3: The Knowledge Explosion & New Technologies**

- **Visual Format:** Conceptual Animation or Timeline Diagram.
- **Narration (Speaker Notes):** "At the same time, the tools we use are evolving
  faster than our ability to adapt. In 1950, it took 50 years for medical
  knowledge to double; today, that doubling time is projected at just 73 days.
  We can no longer rely on static training. Furthermore, 66% of physicians are
  now using some form of AI in practice, yet formal training on how to oversee
  these tools safely remains severely limited. But the upside is tremendous. We
  see digital health innovations, like the SMART remote monitoring program,
  significantly reducing ER visits for COPD and heart failure by shifting care
  from reactive to proactive. We also see virtual reality transforming procedural
  training by allowing learners to rehearse complex scenarios without patient
  risk. Technology will reshape care, but it requires clinical innovators to
  ensure it does so safely and effectively."

**References:** Densen P. (2011); Isaranuwatchai W et al., JMIR (2018); AMA AI Report.
"""


# ---------------------------------------------------------------------------
# Live env
# ---------------------------------------------------------------------------
def load_env_override(require_live: bool) -> dict[str, str]:
    """Load .env with override (defeats the sk-subst sentinel gotcha)."""
    report: dict[str, str] = {}
    try:
        os.environ.pop("OPENAI_API_KEY", None)
        from dotenv import load_dotenv

        load_dotenv(REPO / ".env", override=True)
        report["dotenv_loaded"] = "yes"
    except Exception as exc:  # noqa: BLE001
        report["dotenv_loaded"] = f"no ({type(exc).__name__}: {exc})"
    if require_live:
        key = os.environ.get("OPENAI_API_KEY", "")
        assert key.startswith("sk-"), "live OPENAI_API_KEY not loaded (starts with sk-)"
    return report


def _mask(val: str | None) -> str:
    if not val:
        return "ABSENT"
    v = val.strip().strip('"').strip("'")
    return f"present(len={len(v)}, {v[:6]}...{v[-4:]})" if len(v) > 10 else f"present(len={len(v)})"


def read_dotenv_keys() -> dict[str, str]:
    env_path = REPO / ".env"
    kv: dict[str, str] = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()
    return {k: _mask(kv.get(k)) for k in ("OPENAI_API_KEY", "GAMMA_API_KEY", "GAMMA_API_TOKEN")}


# ---------------------------------------------------------------------------
# 1. Bundle builder
# ---------------------------------------------------------------------------
def build_bundle() -> Path:
    BUNDLE.mkdir(parents=True, exist_ok=True)
    (BUNDLE / "gamma-export").mkdir(exist_ok=True)

    (BUNDLE / "extracted.md").write_text(EXTRACTED_MD, encoding="utf-8")

    slide_content = {
        "run_id": RUN_ID,
        "lesson_slug": LESSON_SLUG,
        "slides": [
            {
                "slide_number": s["slide_number"],
                "slide_id": s["slide_id"],
                "title": s["title"],
                "mode": s["mode"],
                "cluster_role": s["cluster_role"],
                "cluster_id": s["cluster_id"],
                "parent_slide_id": s["parent_slide_id"],
                "narrative_arc": s["narrative_arc"],
                **({"cluster_interstitial_count": s["cluster_interstitial_count"]}
                   if s.get("cluster_interstitial_count") is not None else {}),
                "content": s["content"],
                "source_ref": s["source_ref"],
            }
            for s in SUBSLIDES
        ],
    }
    (BUNDLE / "gary-slide-content.json").write_text(
        json.dumps(slide_content, indent=2), encoding="utf-8"
    )

    fidelity = {
        "run_id": RUN_ID,
        "lesson_slug": LESSON_SLUG,
        "slides": [
            {
                "slide_number": s["slide_number"],
                "slide_id": s["slide_id"],
                "fidelity": "creative",
                "cluster_role": s["cluster_role"],
                "cluster_id": s["cluster_id"],
                "fidelity_rationale": f"{s['cluster_role']} of c-u03 -- creative treatment, brief-driven.",
            }
            for s in SUBSLIDES
        ],
    }
    (BUNDLE / "gary-fidelity-slides.json").write_text(
        json.dumps(fidelity, indent=2), encoding="utf-8"
    )

    theme_resolution = {
        "run_id": RUN_ID,
        "requested_theme_key": PARAM_SET,
        "resolved_theme_key": PARAM_SET,
        "resolved_parameter_set": PARAM_SET,  # -> preset carries theme_id njim9kuhfnljvaa + 16x9 + classic
        "mapping_source": "state/config/gamma-style-presets.yaml",
        "mapping_version": "1",
        "user_confirmation": True,
        "theme_selection_required": False,
        "notes": "c-u03 per-sub-slide probe -- theme carried from hil-2026-apc-nejal-A preset.",
    }
    (BUNDLE / "gary-theme-resolution.json").write_text(
        json.dumps(theme_resolution, indent=2), encoding="utf-8"
    )

    envelope = {
        "schema_version": "1.0",
        "run_id": RUN_ID,
        "lesson_slug": LESSON_SLUG,
        "requested_content_type": "narrated-lesson",
        "motion_enabled": False,
        "double_dispatch": False,  # NEVER true -- avoids all-illustrated crash
        "dispatch_count": 1,
        "experience_profile": "visual-led",
        "theme_resolution": theme_resolution,
        "deck_mode": True,
        "num_cards": len(SUBSLIDES),
        "card_split": "inputTextBreaks",
        "export_format": "png",
        "clusters": [
            {
                "cluster_id": "c-u03",
                "interstitial_count": 2,
                "narrative_arc": SUBSLIDES[0]["narrative_arc"],
            }
        ],
        "dispatch_metadata": {
            "slides_content_json_path": "gary-slide-content.json",
            "diagram_cards_json_path": "gary-diagram-cards.json",
            "site_repo_url": "https://github.com/jlenrique/jlenrique.github.io",
            "planned_asset_url_base": PLANNED_URL_BASE,
            "invocation_mode": "tracked",
            "bundle_path": str(BUNDLE),
        },
    }
    import yaml

    (BUNDLE / "gary-outbound-envelope.yaml").write_text(
        yaml.safe_dump(envelope, sort_keys=False), encoding="utf-8"
    )

    (BUNDLE / "gary-diagram-cards.json").write_text(
        json.dumps({"run_id": RUN_ID, "cards": [], "notes": "no diagram cards for c-u03 probe"}, indent=2),
        encoding="utf-8",
    )

    run_constants = {
        "bundle_path": str(BUNDLE),
        "lesson_slug": LESSON_SLUG,
        "run_id": RUN_ID,
        "double_dispatch": False,
        "execution_mode": "tracked/default",
        "theme_paramset_key": PARAM_SET,
    }
    (BUNDLE / "run-constants.yaml").write_text(
        yaml.safe_dump(run_constants, sort_keys=False), encoding="utf-8"
    )
    return BUNDLE


# ---------------------------------------------------------------------------
# 1b. Offline bundle validation via Gary's own loaders
# ---------------------------------------------------------------------------
def offline_validate_bundle() -> dict[str, object]:
    sys.path.insert(0, str(REPO / "scripts" / "utilities"))
    import importlib

    rgd = importlib.import_module("run_gary_dispatch")

    slides = rgd.build_slides(BUNDLE)
    base_params, tr, envelope = rgd.build_base_params(BUNDLE)

    assert len(slides) == 3, f"expected 3 slides, got {len(slides)}"
    titles = [s["slide_id"] for s in SUBSLIDES]
    roles = [s.get("cluster_role") for s in slides]
    assert roles.count("head") == 1 and roles.count("interstitial") == 2, f"cluster roles wrong: {roles}"

    card_options = base_params.get("cardOptions", {})
    dims = card_options.get("dimensions") if isinstance(card_options, dict) else None
    assert dims == "16x9", f"cardOptions.dimensions expected 16x9, got {dims!r} (base_params keys={list(base_params)})"

    assert base_params.get("themeId") == THEME_ID, f"themeId expected {THEME_ID}, got {base_params.get('themeId')!r}"
    assert base_params.get("formatVariant") == "classic", f"formatVariant expected classic, got {base_params.get('formatVariant')!r}"

    # double_dispatch must NOT be present in base_params (would trip gamma_operations:746)
    assert not (base_params.get("double_dispatch") or base_params.get("doubleDispatch")), (
        "double_dispatch/doubleDispatch present in base_params -- would trip all-illustrated crash"
    )

    fidelities = {s["fidelity"] for s in slides}
    assert fidelities == {"creative"}, f"expected all creative, got {fidelities}"

    return {
        "slides_loaded": len(slides),
        "titles": titles,
        "cluster_roles": roles,
        "cardOptions.dimensions": dims,
        "themeId": base_params.get("themeId"),
        "formatVariant": base_params.get("formatVariant"),
        "double_dispatch_in_base_params": bool(
            base_params.get("double_dispatch") or base_params.get("doubleDispatch")
        ),
        "export_dir": base_params.get("export_dir"),
    }


# ---------------------------------------------------------------------------
# 2. Render (LIVE only)
# ---------------------------------------------------------------------------
def render_live() -> dict[str, object]:
    import importlib

    sys.path.insert(0, str(REPO / "scripts" / "utilities"))
    old_argv = sys.argv[:]
    sys.argv = ["run_gary_dispatch.py", "--bundle", str(BUNDLE), "--run-id", RUN_ID]
    try:
        rgd = importlib.import_module("run_gary_dispatch")
        rc = rgd.main()
    finally:
        sys.argv = old_argv
    assert rc == 0, f"gary dispatch returned {rc}"
    result = json.loads((BUNDLE / "gary-dispatch-result.json").read_text(encoding="utf-8"))
    rows = result["gary_slide_output"]
    pngs = [r.get("file_path") for r in rows]
    assert len(rows) == 3, f"expected 3 rendered rows, got {len(rows)}"
    for p in pngs:
        assert p and Path(p).is_file(), f"missing rendered PNG: {p}"
    return {"rendered_rows": len(rows), "slide_ids": [r["slide_id"] for r in rows], "pngs": pngs}


# ---------------------------------------------------------------------------
# state helpers
# ---------------------------------------------------------------------------
def _model_entry():
    from app.models.state.model_resolution_entry import ModelResolutionEntry

    return ModelResolutionEntry(
        level="per_call",
        requested="gpt-5.5",
        resolved="gpt-5.5",
        reason="leg3-driver-synthetic",
        timestamp=datetime.now(UTC),
        cache_prefix_hash=sha256(b"leg3").hexdigest(),
    )


def _run_state(cache_prefix: str):
    from uuid import uuid4

    from app.models.state.cache_state import CacheState
    from app.models.state.run_state import RunState

    return RunState(
        run_id=uuid4(),
        graph_version="v42",
        temperature=0.0,
        model_resolution_trail=[_model_entry()],
        cache_state=CacheState(cache_prefix=cache_prefix, entries_count=1),
    )


def _gary_rows_for_vision() -> list[dict]:
    """Read real gary_slide_output (slide_id, file_path, card_number) when a
    live render exists; otherwise synthesize offline rows (paths won't exist ->
    vision _not_covered path -- shape-only)."""
    result_path = BUNDLE / "gary-dispatch-result.json"
    if result_path.is_file():
        result = json.loads(result_path.read_text(encoding="utf-8"))
        return [
            {"slide_id": r["slide_id"], "file_path": r["file_path"], "card_number": r["card_number"]}
            for r in result["gary_slide_output"]
        ]
    return [
        {
            "slide_id": f"c-u03-persubslide-probe-card-{s['slide_number']:02d}",
            "file_path": str(BUNDLE / "gamma-export" / f"c-u03_slide_{s['slide_number']:02d}.png"),
            "card_number": s["slide_number"],
        }
        for s in SUBSLIDES
    ]


# ---------------------------------------------------------------------------
# 3. Perceive (07G) -- LIVE runs the real vision act; offline validates plumbing
# ---------------------------------------------------------------------------
def perceive(live: bool) -> dict[str, object]:
    from app.specialists.vision import _act as vision_act

    rows = _gary_rows_for_vision()
    cache_prefix = json.dumps({"gary_slide_output": rows}, sort_keys=True)
    state = _run_state(cache_prefix)

    if not live:
        # Offline: confirm the vision act CONTRACT is satisfiable (payload decodes,
        # _slide_rows accepts the shape). We do NOT assert llm_primary offline.
        payload = vision_act._payload(state)
        parsed_rows = vision_act._slide_rows(payload)
        assert len(parsed_rows) == 3, f"vision _slide_rows saw {len(parsed_rows)} rows"
        for i, r in enumerate(parsed_rows, start=1):
            assert vision_act._slide_id(r, i), "empty slide_id"
        return {
            "mode": "offline-plumbing",
            "gary_rows": len(parsed_rows),
            "slide_ids": [vision_act._slide_id(r, i) for i, r in enumerate(parsed_rows, 1)],
            "note": "reading_path_source==llm_primary is a LIVE-only assertion",
        }

    out = vision_act.act(state)  # LIVE gpt-5.5 perception (3 PNGs)
    cache = out["cache_state"]
    prefix = cache["cache_prefix"] if isinstance(cache, dict) else cache.cache_prefix
    artifacts = json.loads(prefix)["perception_artifacts"]
    (BUNDLE / "perception-artifacts.json").write_text(
        json.dumps(artifacts, indent=2), encoding="utf-8"
    )

    # ---- Assertion (a): distinct perception per sub-slide ----
    assert len(artifacts) == 3, f"expected 3 artifacts, got {len(artifacts)}"
    slide_ids = [a["slide_id"] for a in artifacts]
    png_paths = [a.get("source_png_path") for a in artifacts]
    assert len(set(slide_ids)) == 3, f"slide_ids not distinct: {slide_ids}"
    assert len(set(png_paths)) == 3, f"source_png_path not distinct: {png_paths}"
    for a in artifacts:
        assert a.get("reading_path_source") == "llm_primary", (
            f"slide {a['slide_id']} reading_path_source={a.get('reading_path_source')!r} != llm_primary"
        )
        assert a.get("coverage") == "perceived" and a.get("confidence") == "HIGH", (
            f"slide {a['slide_id']} not perceived/HIGH: coverage={a.get('coverage')} confidence={a.get('confidence')}"
        )
    return {
        "mode": "live",
        "artifacts": 3,
        "slide_ids": slide_ids,
        "distinct_png_paths": len(set(png_paths)),
        "reading_path_source": [a.get("reading_path_source") for a in artifacts],
    }


# ---------------------------------------------------------------------------
# envelope_payload assembly for Pass-2
# ---------------------------------------------------------------------------
def _rich_perception_artifacts(rows: list[dict]) -> list[dict]:
    """Rich app.models.perception.PerceptionArtifact dicts, one per sub-slide.

    Used OFFLINE (synthetic authoritative perception) and as the fallback when
    no live perception-artifacts.json exists. Head carries '66%' in
    extracted_text so its perceived authority holds percent:66; the SMART/VR
    interstitial carries none."""
    arts = []
    for row, sub in zip(rows, SUBSLIDES, strict=True):
        arts.append(
            {
                "slide_id": row["slide_id"],
                "confidence": "HIGH",
                "coverage": "perceived",
                "reading_path_source": "llm_primary",
                "slide_title": sub["title"],
                "extracted_text": sub["extracted_text"],
                "layout_description": sub["content"].split("\n\n")[0],
                "text_blocks": [sub["title"]],
                "visual_elements": [{"description": sub["title"]}],
                "source_png_path": row["file_path"],
                "artifact_path": row["file_path"],
                "card_number": row["card_number"],
            }
        )
    return arts


def _load_perception_artifacts(rows: list[dict]) -> list[dict]:
    live_path = BUNDLE / "perception-artifacts.json"
    if live_path.is_file():
        return json.loads(live_path.read_text(encoding="utf-8"))
    return _rich_perception_artifacts(rows)


def _envelope_payload(rows: list[dict], perception: list[dict]) -> dict:
    lesson_plan = json.loads(PROBE_PLAN.read_text(encoding="utf-8"))
    return {
        "bundle_reference": str(BUNDLE),
        "gary_slide_output": [
            {
                "slide_id": r["slide_id"],
                "card_number": r["card_number"],
                "file_path": r["file_path"],
                "source_ref": SUBSLIDES[i]["source_ref"],
                "visual_description": SUBSLIDES[i]["title"],
                "cluster_id": "c-u03",
                "cluster_role": SUBSLIDES[i]["cluster_role"],
                "parent_slide_id": SUBSLIDES[i]["parent_slide_id"],
            }
            for i, r in enumerate(rows)
        ],
        "perception_artifacts": perception,
        "lesson_plan": lesson_plan,
        "pass_phase": "pass_2",
    }


# ---------------------------------------------------------------------------
# 4. Author (Pass-2) -- LIVE runs _act_pass_2; offline validates assembly
# ---------------------------------------------------------------------------
def author(live: bool) -> dict[str, object]:
    from app.specialists.irene import graph as irene_graph

    rows = _gary_rows_for_vision()
    perception = _load_perception_artifacts(rows)
    payload = _envelope_payload(rows, perception)

    # ---- Offline plumbing: readers + roster + rich-model validation + cross-shape ----
    from app.specialists.source_bundle import read_extracted_source

    extracted = read_extracted_source(payload)
    assert "Knowledge Explosion" in extracted, "extracted.md not read via bundle_reference"
    assert payload.get("lesson_plan"), "lesson_plan missing/empty"

    roster = irene_graph._slide_roster(payload)  # validates rich perception + builds perceived_figures
    assert len(roster) == 3, f"roster should have 3 entries, got {len(roster)}"
    perceived_by_slide = {e["slide_id"]: set(e["perceived_figures"]) for e in roster}
    head_id = roster[0]["slide_id"]

    # cross-artifact contract: perception.source_image_path == gary.file_path per slide
    from app.specialists.irene.authoring.pass_2_template import (
        GarySlideOutput,
        _normalized_path,
        project_rich_perception_for_authoring,
    )

    for r, art in zip(payload["gary_slide_output"], perception, strict=True):
        gary = GarySlideOutput(
            slide_id=r["slide_id"], card_number=r["card_number"],
            file_path=r["file_path"], source_ref=r["source_ref"],
        )
        proj = project_rich_perception_for_authoring(art)
        assert _normalized_path(proj.source_image_path) == _normalized_path(gary.file_path), (
            f"cross-artifact path mismatch for {r['slide_id']}"
        )

    offline = {
        "mode": "offline-plumbing",
        "extracted_source_ok": True,
        "lesson_plan_present": True,
        "roster_entries": len(roster),
        "head_slide_id": head_id,
        "perceived_figures_by_slide": {k: sorted(v) for k, v in perceived_by_slide.items()},
        "cross_artifact_path_match": True,
    }

    if not live:
        return offline

    # ---- LIVE Pass-2 authoring ----
    from app.models.adapter import make_chat_model

    handle = make_chat_model(specialist_id="irene", temperature=0.0, tier_request="reasoning")
    state = _run_state(json.dumps({"gary_slide_output": payload["gary_slide_output"]}, sort_keys=True))
    result = irene_graph._act_pass_2(
        state, handle=handle, envelope_payload=payload, model_id="gpt-5.5"
    )
    prefix = result["cache_state"]["cache_prefix"]
    parsed = json.loads(prefix)
    (BUNDLE / "pass2-output.json").write_text(json.dumps(parsed, indent=2), encoding="utf-8")

    # If _act_pass_2 returned, all four post-parse gates (join / reading-path /
    # figure-citation / surfaces-validatable) ALREADY PASSED. Re-affirm (b)+(c)
    # explicitly for the record.
    irene_graph._assert_narration_joins_roster(parsed, roster)        # (b) traceable refs
    irene_graph._assert_figure_citations_within_perceived(parsed, roster)  # (c) 0 contradiction

    # (b) each visual reference keys to a real roster slide_id
    roster_ids = {e["slide_id"] for e in roster}
    referenced = set()
    for delta in parsed.get("segment_manifest_deltas") or []:
        for ref in (delta.get("visual_references") or []):
            src = str((ref or {}).get("perception_source") or "").strip()
            if src:
                referenced.add(src)
    orphans = referenced - roster_ids
    assert not orphans, f"orphan perception_source refs: {orphans}"
    assert referenced, "no visual references keyed to roster slides"

    return {
        **offline,
        "mode": "live",
        "narration_segments": len(parsed.get("narration_script") or []),
        "referenced_slide_ids": sorted(referenced),
        "gate_b_join": "PASS",
        "gate_c_figure_citation": "PASS",
    }


# ---------------------------------------------------------------------------
# trip-wire helpers
# ---------------------------------------------------------------------------
def _surface_from_token(token: str) -> str | None:
    """Reverse a normalized figure token to a narration surface form."""
    if token.startswith("percent:"):
        return f"{token.split(':', 1)[1]}%"
    if token.startswith("money-trillion:"):
        return f"${token.split(':', 1)[1]} trillion"
    if token.startswith("money-bare:"):
        return f"${token.split(':', 1)[1]}"
    if token.startswith("multiple:"):
        return f"{token.split(':', 1)[1]}x"
    return None


# ---------------------------------------------------------------------------
# 5. Trip-wire (d) -- MUST RAISE
# ---------------------------------------------------------------------------
def tripwire(live: bool) -> dict[str, object]:
    from app.specialists._shared.figure_tokens import _figures
    from app.specialists.irene import graph as irene_graph
    from app.specialists.irene.graph import Pass2GroundingError

    # --- Offline: prove the mutation targets the field the gate reads ---
    # Construct a synthetic roster (head holds percent:66; interstitial holds none)
    # + a synthetic parsed narration; confirm clean=no-raise, mutated=raise, and
    # that the gate reads segment["text"] + roster["perceived_figures"].
    head, inter = "S05", "S07"
    roster = [
        {"slide_id": head, "perceived_figures": ["percent:66"]},
        {"slide_id": inter, "perceived_figures": []},
    ]
    clean = {
        "narration_script": [
            {"slide_id": head, "text": "Medical knowledge doubles fast; 66% of physicians use AI."},
            {"slide_id": inter, "text": "SMART monitoring shifts care from reactive to proactive."},
        ]
    }
    # clean must NOT raise
    irene_graph._assert_figure_citations_within_perceived(clean, roster)

    injected_surface = _surface_from_token("percent:66")  # "66%"
    assert "percent:66" in _figures(f"about {injected_surface} of ..."), "surface->token reverse broke"
    mutated = json.loads(json.dumps(clean))
    # MUTATE THE EXACT FIELD THE GATE READS: narration_script[interstitial].text
    mutated["narration_script"][1]["text"] = (
        f"SMART monitoring reaches roughly {injected_surface} of eligible patients."
    )
    offline_raised = False
    try:
        irene_graph._assert_figure_citations_within_perceived(mutated, roster)
    except Pass2GroundingError as exc:
        offline_raised = exc.tag == "irene.pass2.figure-contradiction"
    assert offline_raised, "OFFLINE trip-wire did not raise the figure-contradiction tag"

    # confirm the gate is field-sensitive: mutating a NON-read field must NOT raise
    non_read = json.loads(json.dumps(clean))
    non_read["narration_script"][1]["visual_description"] = f"contains {injected_surface}"
    irene_graph._assert_figure_citations_within_perceived(non_read, roster)  # no raise

    offline = {
        "mode": "offline-plumbing",
        "field_read_by_gate": "narration_script[*].text (fallback narration_text)",
        "perceived_source": "roster[*].perceived_figures",
        "injected_token": "percent:66",
        "injected_surface": injected_surface,
        "clean_no_raise": True,
        "mutated_raised_correct_tag": offline_raised,
        "non_read_field_no_raise": True,
    }

    if not live:
        return offline

    # --- LIVE: re-run real Pass-2 authoring, then inject a head-only figure into
    # ONE interstitial's real narration text and assert the gate raises. ---
    rows = _gary_rows_for_vision()
    perception = _load_perception_artifacts(rows)
    payload = _envelope_payload(rows, perception)
    live_roster = irene_graph._slide_roster(payload)
    perceived = {e["slide_id"]: set(e["perceived_figures"]) for e in live_roster}
    head_id = live_roster[0]["slide_id"]
    head_figs = perceived[head_id]

    # pick (interstitial, token) where token is on the head but NOT the interstitial
    choice = None
    for e in live_roster[1:]:
        diff = head_figs - perceived[e["slide_id"]]
        surfaced = [(t, _surface_from_token(t)) for t in sorted(diff)]
        surfaced = [(t, s) for t, s in surfaced if s]
        if surfaced:
            choice = (e["slide_id"], *surfaced[0])
            break
    if choice is None:
        raise AssertionError(
            "cannot construct authentic trip-wire: head has no surfaceable figure "
            f"absent from an interstitial (head_figs={sorted(head_figs)}, "
            f"perceived={ {k: sorted(v) for k, v in perceived.items()} })"
        )
    target_slide, token, surface = choice

    # obtain real narration (reuse the authored output if present, else author now)
    out_path = BUNDLE / "pass2-output.json"
    if out_path.is_file():
        parsed = json.loads(out_path.read_text(encoding="utf-8"))
    else:
        from app.models.adapter import make_chat_model

        handle = make_chat_model(specialist_id="irene", temperature=0.0, tier_request="reasoning")
        state = _run_state(json.dumps({"gary_slide_output": payload["gary_slide_output"]}, sort_keys=True))
        res = irene_graph._act_pass_2(state, handle=handle, envelope_payload=payload, model_id="gpt-5.5")
        parsed = json.loads(res["cache_state"]["cache_prefix"])

    mutated = json.loads(json.dumps(parsed))
    injected = False
    for seg in mutated.get("narration_script") or []:
        sid = str(seg.get("slide_id") or seg.get("perception_source") or "")
        if sid == target_slide:
            seg["text"] = (seg.get("text") or seg.get("narration_text") or "") + f" It reaches {surface} of patients."
            injected = True
    assert injected, f"could not inject into target slide {target_slide} narration text"

    raised = False
    try:
        irene_graph._assert_figure_citations_within_perceived(mutated, live_roster)
    except Pass2GroundingError as exc:
        raised = exc.tag == "irene.pass2.figure-contradiction"
    assert raised, "LIVE trip-wire did not raise irene.pass2.figure-contradiction"

    return {
        **offline,
        "mode": "live",
        "target_interstitial": target_slide,
        "head_slide": head_id,
        "injected_token": token,
        "injected_surface": surface,
        "live_raised_correct_tag": raised,
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Leg-3 per-sub-slide invariant driver (c-u03)")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--perceive", action="store_true")
    ap.add_argument("--author", action="store_true")
    ap.add_argument("--tripwire", action="store_true")
    ap.add_argument("--all", action="store_true", help="offline: all offline checks; with --live: full live chain")
    ap.add_argument("--live", action="store_true", help="run real APIs (Gamma render / gpt-5.5 perception / Pass-2)")
    args = ap.parse_args()

    any_step = args.build or args.render or args.perceive or args.author or args.tripwire or args.all
    if not any_step:
        args.all = True

    env_report = load_env_override(require_live=args.live)
    results: dict[str, object] = {"env": env_report, "dotenv_keys": read_dotenv_keys(), "live": args.live}

    try:
        if args.build or args.all:
            build_bundle()
            results["build"] = {"bundle": str(BUNDLE)}
            results["offline_validate_bundle"] = offline_validate_bundle()

        if args.render or (args.all and args.live):
            if args.live:
                results["render"] = render_live()
            else:
                results["render"] = {"skipped": "live-only step (needs --live)"}

        if args.perceive or args.all:
            results["perceive"] = perceive(live=args.live)

        if args.author or args.all:
            results["author"] = author(live=args.live)

        if args.tripwire or args.all:
            results["tripwire"] = tripwire(live=args.live)

        results["status"] = "PASS"
    except Exception as exc:  # noqa: BLE001
        results["status"] = "FAIL"
        results["error"] = f"{type(exc).__name__}: {exc}"
        results["traceback"] = traceback.format_exc()

    print(json.dumps(results, indent=2, default=str))
    return 0 if results.get("status") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
