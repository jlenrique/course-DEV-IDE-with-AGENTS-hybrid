from __future__ import annotations

import json
from importlib import util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "utilities" / "run_gary_dispatch.py"


def _load_module():
    spec = util.spec_from_file_location("run_gary_dispatch_module", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mod = _load_module()


def _write_bundle(tmp_path: Path) -> Path:
    bundle = tmp_path / "bundle"
    bundle.mkdir()

    (bundle / "gary-slide-content.json").write_text(
        json.dumps(
            {
                "run_id": "RUN-001",
                "lesson_slug": "lesson-alpha",
                "slides": [
                    {
                        "slide_number": 1,
                        "content": "Head slide",
                        "source_ref": "brief#1",
                        "cluster_id": "c1",
                        "cluster_role": "head",
                        "parent_slide_id": None,
                        "narrative_arc": "Introduce the concept, complicate it, then land the takeaway.",
                        "cluster_interstitial_count": 1,
                    },
                    {
                        "slide_number": 2,
                        "content": "Interstitial slide",
                        "source_ref": "brief#2",
                        "cluster_id": "c1",
                        "cluster_role": "interstitial",
                        "parent_slide_id": "slide-01",
                    },
                    {
                        "slide_number": 3,
                        "content": "Flat slide",
                        "source_ref": "brief#3",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    (bundle / "gary-fidelity-slides.json").write_text(
        json.dumps(
            {
                "run_id": "RUN-001",
                "lesson_slug": "lesson-alpha",
                "slides": [
                    {
                        "slide_number": 1,
                        "fidelity": "creative",
                        "cluster_role": "head",
                        "queue": "creative",
                    },
                    {
                        "slide_number": 2,
                        "fidelity": "literal-text",
                        "cluster_role": "interstitial",
                        "queue": "literal",
                    },
                    {
                        "slide_number": 3,
                        "fidelity": "literal-visual",
                        "queue": "literal",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    (bundle / "gary-theme-resolution.json").write_text(
        json.dumps({"resolved_parameter_set": "preset-a", "resolved_theme_key": "theme-a"}),
        encoding="utf-8",
    )

    (bundle / "gary-outbound-envelope.yaml").write_text(
        yaml.safe_dump(
            {
                "dispatch_metadata": {"site_repo_url": "https://example.com/repo"},
                "clusters": [
                    {
                        "cluster_id": "c1",
                        "interstitial_count": 1,
                        "narrative_arc": "Introduce the concept, complicate it, then land the takeaway.",
                    }
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    return bundle


def test_build_slides_inherits_head_fidelity_for_interstitials(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path)

    slides = mod.build_slides(bundle)

    assert slides[0]["fidelity"] == "creative"
    assert slides[1]["fidelity"] == "creative"
    assert slides[1]["cluster_id"] == "c1"
    assert slides[1]["cluster_role"] == "interstitial"
    assert slides[1]["parent_slide_id"] == "slide-01"


def test_filter_interstitial_diagram_cards_skips_cluster_interstitials() -> None:
    slides = [
        {"slide_number": 1, "cluster_role": "head"},
        {"slide_number": 2, "cluster_role": "interstitial"},
        {"slide_number": 3, "cluster_role": None},
    ]

    filtered = mod._filter_interstitial_diagram_cards(
        [  # noqa: SLF001 - intentional unit test of helper
            {"card_number": 1},
            {"card_number": 2},
            {"card_number": 3},
        ],
        slides,
    )

    assert [card["card_number"] for card in filtered] == [1, 3]


def test_assemble_outbound_contract_carries_cluster_metadata(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path)
    slides = mod.build_slides(bundle)
    envelope = yaml.safe_load((bundle / "gary-outbound-envelope.yaml").read_text(encoding="utf-8"))

    payload = mod.assemble_outbound_contract(
        {
            "gary_slide_output": [
                {"slide_id": "slide-01", "card_number": 1, "file_path": "slide-01.png"},
                {"slide_id": "slide-02", "card_number": 2, "file_path": "slide-02.png"},
                {"slide_id": "slide-03", "card_number": 3, "file_path": "slide-03.png"},
            ],
            "calls_made": 2,
            "generation_mode": "mixed_fidelity",
        },
        base_params={"themeId": "njim9kuhfnljvaa", "site_repo_url": "https://example.com/repo"},
        tr={"resolved_theme_key": "theme-a"},
        slides=slides,
        envelope=envelope,
        run_id="RUN-001",
        lesson_slug="lesson-alpha",
        bundle=bundle,
        generated_at="2026-04-11T00:00:00Z",
    )

    assert payload["gary_slide_output"][0]["cluster_id"] == "c1"
    assert payload["gary_slide_output"][0]["cluster_role"] == "head"
    assert payload["gary_slide_output"][0]["parent_slide_id"] is None
    assert payload["gary_slide_output"][1]["cluster_id"] == "c1"
    assert payload["gary_slide_output"][1]["cluster_role"] == "interstitial"
    assert payload["gary_slide_output"][1]["parent_slide_id"] == "slide-01"
    assert "cluster_id" not in payload["gary_slide_output"][2]
    assert payload["clusters"] == [
        {
            "cluster_id": "c1",
            "interstitial_count": 1,
            "narrative_arc": "Introduce the concept, complicate it, then land the takeaway.",
        }
    ]
