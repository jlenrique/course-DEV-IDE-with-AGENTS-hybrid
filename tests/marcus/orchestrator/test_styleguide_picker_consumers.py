"""Leg-D — cite-the-consumer tests (Murat AC-2/AC-3/AC-7, M-1).

M-1: every consumer symbol is imported from its REAL production module path —
no shadow copies. The picker-written directive is resolved by:

- AC-2: the REAL ``_gamma_settings_from_directive`` (production_runner) — the
  exact function the runner uses to build Gary's dispatch payload — and then by
  Gary's REAL ``_normalized_gamma_settings`` (the styleguide base-layer seam).
- AC-3: the REAL ``_min_cluster_floor_from_directive`` via the REAL
  ``_runner_payload_for_specialist`` irene_pass1 branch — binding the Leg-C
  floor-probe guide must thread ``{"min_cluster_floor": 8}`` from the REAL SSOT.
- AC-7: the ``styleguide_picker_provenance`` block survives a yaml round-trip
  read of the directive (the run's own input artifact carries the audit trail).

RED-first: authored before the picker module existed (ModuleNotFoundError RED).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from app.marcus.orchestrator.production_runner import (
    _gamma_settings_from_directive,
    _runner_payload_for_specialist,
)
from app.marcus.orchestrator.styleguide_picker import (
    PICKER_VERSION,
    write_pick_to_directive,
)


# --------------------------------------------------------------------------- AC-2
def test_picker_directive_resolved_by_real_gamma_settings_consumer(tmp_path: Path) -> None:
    directive = tmp_path / "directive.yaml"
    write_pick_to_directive(
        directive,
        {"A": "classic-freeform-x-cards", "B": "hil-2026-apc-studio-image-card"},
    )
    settings = _gamma_settings_from_directive(directive)
    assert settings == [
        {"variant_id": "A", "styleguide": "classic-freeform-x-cards"},
        {"variant_id": "B", "styleguide": "hil-2026-apc-studio-image-card"},
    ]


def test_picker_directive_resolves_through_gary_base_layer_seam(tmp_path: Path) -> None:
    """The picked guide seeds Gary's REAL styleguide base layer (J-3 verbatim)."""
    from app.specialists.gary._act import _normalized_gamma_settings

    directive = tmp_path / "directive.yaml"
    write_pick_to_directive(directive, {"A": "classic-freeform-x-cards"})
    settings = _gamma_settings_from_directive(directive)
    normalized = _normalized_gamma_settings({"gamma_settings": settings})
    assert len(normalized) == 1  # single bind -> exactly one variant (retire-variant)
    assert normalized[0]["variant_id"] == "A"
    assert normalized[0]["theme"] == "njim9kuhfnljvaa"  # the SSOT record IS the base
    assert normalized[0]["dimensions"] == "fluid"


def test_patch_preserves_existing_directive_keys_and_other_variant(tmp_path: Path) -> None:
    """J-3: existing gamma_settings semantics VERBATIM — patch, don't clobber."""
    directive = tmp_path / "directive.yaml"
    directive.write_text(
        yaml.safe_dump(
            {
                "course": "c1m1",
                "gamma_settings": [
                    {"variant_id": "A", "styleguide": "old-name", "tone": "warm"},
                    {"variant_id": "B", "styleguide": "hil-2026-apc-blueprint-classic"},
                ],
            }
        ),
        encoding="utf-8",
    )
    write_pick_to_directive(directive, {"A": "classic-freeform-x-cards"})
    loaded = yaml.safe_load(directive.read_text(encoding="utf-8"))
    assert loaded["course"] == "c1m1"  # non-picker keys untouched
    entry_a = next(e for e in loaded["gamma_settings"] if e["variant_id"] == "A")
    entry_b = next(e for e in loaded["gamma_settings"] if e["variant_id"] == "B")
    assert entry_a["styleguide"] == "classic-freeform-x-cards"
    assert entry_a["tone"] == "warm"  # per-variant explicit keys survive the patch
    assert entry_b["styleguide"] == "hil-2026-apc-blueprint-classic"  # unpicked variant kept


# --------------------------------------------------------------------------- AC-3
def test_floor_probe_pick_threads_min_cluster_floor_8(tmp_path: Path) -> None:
    """Shape parity with the Leg-C floor consumer, against the REAL repo SSOT."""
    directive = tmp_path / "directive.yaml"
    write_pick_to_directive(directive, {"A": "leg-c-part3-floor-probe"})
    payload = _runner_payload_for_specialist(
        specialist_id="irene_pass1", directive_path=directive, bundle_dir=None
    )
    assert payload == {"min_cluster_floor": 8}


def test_floorless_seed_pick_threads_no_floor(tmp_path: Path) -> None:
    directive = tmp_path / "directive.yaml"
    write_pick_to_directive(directive, {"A": "classic-freeform-x-cards"})
    payload = _runner_payload_for_specialist(
        specialist_id="irene_pass1", directive_path=directive, bundle_dir=None
    )
    assert payload is None


# --------------------------------------------------------------------------- AC-7
def test_provenance_block_survives_yaml_round_trip(tmp_path: Path) -> None:
    directive = tmp_path / "directive.yaml"
    provenance = write_pick_to_directive(
        directive,
        {"A": "classic-freeform-x-cards", "B": "leg-c-part3-floor-probe"},
    )
    loaded = yaml.safe_load(directive.read_text(encoding="utf-8"))
    block = loaded["styleguide_picker_provenance"]
    assert block == provenance  # byte-faithful through the round trip
    assert block["written_by"] == "styleguide_picker"
    assert block["picker_version"] == PICKER_VERSION
    assert len(block["ssot_sha256"]) == 64
    assert block["picks"] == [
        {"variant_id": "A", "styleguide": "classic-freeform-x-cards"},
        {"variant_id": "B", "styleguide": "leg-c-part3-floor-probe"},
    ]
    assert "T" in block["picked_at"]  # ISO-8601 timestamp


def test_repeat_pick_overwrites_provenance_not_duplicates(tmp_path: Path) -> None:
    directive = tmp_path / "directive.yaml"
    write_pick_to_directive(directive, {"A": "classic-freeform-x-cards"})
    write_pick_to_directive(directive, {"A": "hil-2026-apc-blueprint-classic"})
    loaded = yaml.safe_load(directive.read_text(encoding="utf-8"))
    entries_a = [e for e in loaded["gamma_settings"] if e["variant_id"] == "A"]
    assert len(entries_a) == 1  # never a duplicate variant row (Gary RED-gates those)
    assert entries_a[0]["styleguide"] == "hil-2026-apc-blueprint-classic"
    assert (
        loaded["styleguide_picker_provenance"]["picks"][0]["styleguide"]
        == "hil-2026-apc-blueprint-classic"
    )
