"""CI parity test — capability-overlay generated honesty map (Braid S4, DP1).

Mirrors ``tests/parity/test_skill_md_sanctum_alignment.py`` /
``_sanctum_parity_base.py``: filesystem-fact assertions, no mocks, no LLM. The
test re-derives the overlay from the *live* substrate and content-hash compares
against the committed ``state/config/capability-overlay.yaml`` — it goes RED the
instant a narratable claim diverges from what the manifest routes (the Tracy
drift class).

AC coverage: AC-1 (closed enum), AC-2 (known classification), AC-5 (staleness
gate), AC-6 (injected-drift RED proof).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from scripts.utilities.generate_capability_overlay import (
    CAPABILITY_STATES,
    DEFAULT_OVERLAY_PATH,
    compute_content_hash,
    derive_overlay,
    is_stale,
    main,
    render_overlay_text,
    write_overlay,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _committed_doc() -> dict:
    return yaml.safe_load(DEFAULT_OVERLAY_PATH.read_text(encoding="utf-8"))


# --- AC-5: staleness / divergence (the core gate) --------------------------


def test_committed_overlay_exists() -> None:
    assert DEFAULT_OVERLAY_PATH.is_file(), (
        f"missing generated artifact: {DEFAULT_OVERLAY_PATH} — run "
        "`python -m scripts.utilities.generate_capability_overlay`"
    )


def test_committed_overlay_matches_live_derivation_text() -> None:
    """Re-derive from live substrate; the committed file must be byte-identical."""
    fresh = render_overlay_text(derive_overlay(REPO_ROOT))
    committed = DEFAULT_OVERLAY_PATH.read_text(encoding="utf-8")
    assert committed == fresh, (
        "committed capability-overlay.yaml is stale vs a live re-derivation; "
        "regenerate via `python -m scripts.utilities.generate_capability_overlay`"
    )


def test_committed_content_hash_matches_live_derivation() -> None:
    """The committed content_hash equals the live-derived hash (AC-5)."""
    fresh_hash = compute_content_hash(derive_overlay(REPO_ROOT))
    committed = _committed_doc()
    assert committed["content_hash"] == fresh_hash


# --- AC-1: closed-enum integrity -------------------------------------------


def test_closed_enum_integrity() -> None:
    overlay = derive_overlay(REPO_ROOT)
    for sid, entry in overlay.specialists.items():
        assert entry.capability_state in CAPABILITY_STATES, (
            f"{sid} has out-of-set state {entry.capability_state!r}"
        )
    assert overlay.marcus.role == "orchestrator"


def test_marcus_is_orchestrator_not_a_specialist_defect() -> None:
    committed = _committed_doc()
    assert committed["marcus"]["role"] == "orchestrator"
    assert committed["marcus"]["in_manifest"] is True
    assert committed["marcus"]["in_dispatch"] is False
    # marcus must NOT appear as a (present-but-unrouted) specialist defect.
    assert "marcus" not in committed["specialists"]


# --- AC-2: known-classification pins (acceptance witnesses) -----------------


def test_known_classification_pins() -> None:
    overlay = derive_overlay(REPO_ROOT)
    specialists = overlay.specialists
    assert specialists["gary"].capability_state == "wired"
    assert specialists["texas"].capability_state == "wired"
    assert specialists["tracy"].capability_state == "present-but-unrouted"
    # Canonical-arc S1 (2026-07-06): cd's `partial` ground was STALE doc drift
    # (monitor SOP-001: CD is dispatched at 4.75 in both walks + load-bearing
    # at §06). Registry staleness fixed -> the honest classification is wired.
    assert specialists["cd"].capability_state == "wired"
    assert specialists["midjourney"].capability_state == "shelf"


def test_partial_ordering_beats_wired(tmp_path: Path) -> None:
    """`partial` is evaluated BEFORE `wired` (first-match-wins decision table).

    Canonical-arc S1: cd — the former live example — was reclassified wired
    when its stale partial-status ground was corrected, so the ordering rule
    is now pinned via an injected partial-status flag in a substrate mirror
    (assertion PRESERVED at full strength, witness relocated)."""
    mirror = _copy_substrate(tmp_path)
    registry_path = (
        mirror / "skills" / "bmad-agent-marcus" / "references" / "specialist-registry.yaml"
    )
    raw = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    raw["partial-status"] = {
        "gary": {
            "persona_skill": "skills/bmad-agent-gamma/SKILL.md",
            "role": "injected ordering witness",
        }
    }
    registry_path.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")

    drifted = derive_overlay(mirror)
    gary = drifted.specialists["gary"]
    assert gary.in_manifest is True
    assert gary.in_dispatch is True
    assert gary.real_module is True
    assert gary.capability_state == "partial"  # NOT wired — partial wins


def test_canonicalization_aliases_not_misclassified() -> None:
    """quinn-r / irene-pass1 / enrique(elevenlabs alias) must join correctly."""
    overlay = derive_overlay(REPO_ROOT)
    # All three are manifest-routed + dispatchable + real → wired (not unrouted).
    assert overlay.specialists["quinn_r"].capability_state == "wired"
    assert overlay.specialists["irene_pass1"].capability_state == "wired"
    assert overlay.specialists["enrique"].capability_state == "wired"


def test_present_but_unrouted_set() -> None:
    overlay = derive_overlay(REPO_ROOT)
    unrouted = {
        sid
        for sid, entry in overlay.specialists.items()
        if entry.capability_state == "present-but-unrouted"
    }
    # The Tracy bug class: dispatchable + real module but no manifest node routes.
    assert {"tracy", "wanda", "kim", "vyx", "aria", "mira", "tamara"} <= unrouted


# --- AC-6: injected-drift RED proof ----------------------------------------


def _copy_substrate(tmp_path: Path) -> Path:
    """Copy the substrate the generator reads into a tmp repo-root mirror."""
    for rel in (
        "state/config/pipeline-manifest.yaml",
        "state/config/dispatch-registry.yaml",
        "skills/bmad-agent-marcus/references/specialist-registry.yaml",
    ):
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / rel, dst)
    # Mirror app/specialists/*/graph.py existence (touch empty files is enough for
    # the on-disk check, but the not-stub check needs the builder ref from the
    # dispatch registry, which we copy above). We symlink-copy the real tree.
    src_spec = REPO_ROOT / "app" / "specialists"
    dst_spec = tmp_path / "app" / "specialists"
    for graph in src_spec.glob("*/graph.py"):
        rel_graph = graph.relative_to(REPO_ROOT)
        target = tmp_path / rel_graph
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# mirror\n", encoding="utf-8")
    assert dst_spec.is_dir()
    return tmp_path


def test_injected_drift_flips_state_and_fails_parity(tmp_path: Path) -> None:
    """Removing Tracy's dispatch entry must flip its state AND break the hash."""
    mirror = _copy_substrate(tmp_path)

    # Baseline derivation in the mirror equals the live derivation (sanity).
    baseline = derive_overlay(mirror)
    assert baseline.specialists["tracy"].capability_state == "present-but-unrouted"
    baseline_hash = compute_content_hash(baseline)

    # Inject drift: remove Tracy's dispatch entry.
    dispatch_path = mirror / "state" / "config" / "dispatch-registry.yaml"
    raw = yaml.safe_load(dispatch_path.read_text(encoding="utf-8"))
    del raw["specialists"]["tracy"]
    dispatch_path.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")

    drifted = derive_overlay(mirror)
    # Tracy is no longer dispatchable → it drops out of the dispatchable universe.
    assert "tracy" not in drifted.specialists or (
        drifted.specialists["tracy"].capability_state != "present-but-unrouted"
    )
    # The derived facts changed → the hash diverges → parity would go RED.
    assert compute_content_hash(drifted) != baseline_hash


# --- AC-3: not-stub check is live (stub passthrough is NOT wired) ----------


def test_stub_passthrough_builder_is_not_wired(tmp_path: Path) -> None:
    """A dispatch entry pointing at the _stub passthrough is NOT classified wired."""
    mirror = _copy_substrate(tmp_path)

    # Point gary's dispatch builder at the _stub passthrough module. Its graph.py
    # still exists on disk, but the not-stub check must demote it from wired.
    dispatch_path = mirror / "state" / "config" / "dispatch-registry.yaml"
    raw = yaml.safe_load(dispatch_path.read_text(encoding="utf-8"))
    raw["specialists"]["gary"] = (
        "app.specialists._stub.passthrough_specialist:passthrough_node"
    )
    dispatch_path.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")

    drifted = derive_overlay(mirror)
    gary = drifted.specialists["gary"]
    assert gary.in_manifest is True
    assert gary.in_dispatch is True
    assert gary.real_module is False  # stub builder → not a real module
    assert gary.capability_state != "wired"


def test_stub_package_reexport_builder_is_not_wired(tmp_path: Path) -> None:
    """The _stub PACKAGE re-export form must also demote from wired (FIX-2).

    ``app.specialists._stub:passthrough_node`` resolves the module name to the
    package ``app.specialists._stub`` (NOT the ``.passthrough_specialist``
    submodule). A prefix match on the submodule would miss this → a false
    ``wired`` bypass (the residual over-promise path the honesty map exists to
    close). The not-stub guard must reject any reference into the ``_stub``
    package, exact or dotted.
    """
    mirror = _copy_substrate(tmp_path)
    dispatch_path = mirror / "state" / "config" / "dispatch-registry.yaml"
    raw = yaml.safe_load(dispatch_path.read_text(encoding="utf-8"))
    raw["specialists"]["gary"] = "app.specialists._stub:passthrough_node"
    dispatch_path.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")

    drifted = derive_overlay(mirror)
    gary = drifted.specialists["gary"]
    assert gary.real_module is False  # package re-export of the stub → not real
    assert gary.capability_state != "wired"


# --- AC-4: deterministic no-op regen + --check staleness exit code ---------


def test_main_regen_is_byte_identical_noop(tmp_path: Path) -> None:
    out = tmp_path / "capability-overlay.yaml"
    main(["--path", str(out)])
    first = out.read_text(encoding="utf-8")
    main(["--path", str(out)])
    second = out.read_text(encoding="utf-8")
    assert first == second


def test_check_flag_exit_codes(tmp_path: Path) -> None:
    out = tmp_path / "capability-overlay.yaml"
    write_overlay(derive_overlay(REPO_ROOT), out)
    # Fresh artifact at REPO_ROOT derivation → not stale.
    assert is_stale(REPO_ROOT, out) is False
    # Mutate the on-disk artifact → stale.
    out.write_text(out.read_text(encoding="utf-8") + "\n# tampered\n", encoding="utf-8")
    assert is_stale(REPO_ROOT, out) is True
    assert main(["--check", "--path", str(out)]) == 1


def test_injected_fake_manifest_node_flips_shelf_to_wired(tmp_path: Path) -> None:
    """Adding a fake manifest+dispatch wiring for a shelf specialist flips it."""
    mirror = _copy_substrate(tmp_path)
    baseline = derive_overlay(mirror)
    assert baseline.specialists["midjourney"].capability_state == "shelf"
    baseline_hash = compute_content_hash(baseline)

    # Inject: make midjourney dispatchable + add a real on-disk module + route it.
    dispatch_path = mirror / "state" / "config" / "dispatch-registry.yaml"
    raw = yaml.safe_load(dispatch_path.read_text(encoding="utf-8"))
    raw["specialists"]["midjourney"] = (
        "app.specialists.midjourney.graph:build_midjourney_graph"
    )
    dispatch_path.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    (mirror / "app" / "specialists" / "midjourney").mkdir(parents=True, exist_ok=True)
    (mirror / "app" / "specialists" / "midjourney" / "graph.py").write_text(
        "# mirror\n", encoding="utf-8"
    )
    manifest_path = mirror / "state" / "config" / "pipeline-manifest.yaml"
    manifest_raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_raw["nodes"].append(
        {"id": "99-fake", "label": "fake", "specialist_id": "midjourney"}
    )
    manifest_path.write_text(
        yaml.safe_dump(manifest_raw, sort_keys=False), encoding="utf-8"
    )

    drifted = derive_overlay(mirror)
    assert drifted.specialists["midjourney"].capability_state == "wired"
    assert compute_content_hash(drifted) != baseline_hash


# --- FIX-1: local lockstep freshness guard (the "caught locally" half) ------


def test_local_lockstep_guard_flags_stale_overlay(monkeypatch: pytest.MonkeyPatch) -> None:
    """A capability-overlay INPUT changing with a stale overlay fails locally.

    Closes the gap where the local block-mode hook gave zero overlay-staleness
    protection (only CI parity caught drift). Uses content comparison (is_stale)
    so a routing-neutral edit that regenerates to byte-identical does NOT
    false-fail.
    """
    from scripts.utilities import check_manifest_lockstep as cml

    # Stale overlay + a relevant input in the diff → raises locally.
    monkeypatch.setattr(
        "scripts.utilities.generate_capability_overlay.is_stale",
        lambda *a, **k: True,
    )
    for trigger in (
        "state/config/pipeline-manifest.yaml",
        "state/config/dispatch-registry.yaml",
        "scripts/utilities/generate_capability_overlay.py",
        "skills/bmad-agent-marcus/references/specialist-registry.yaml",
    ):
        with pytest.raises(cml.CapabilityOverlayStaleError):
            cml._assert_capability_overlay_fresh([trigger])

    # No capability-overlay input in the diff → no raise even if stale.
    cml._assert_capability_overlay_fresh(["docs/whatever.md", "README.md"])

    # Input changed but overlay fresh (routing-neutral regen) → no false-fail.
    monkeypatch.setattr(
        "scripts.utilities.generate_capability_overlay.is_stale",
        lambda *a, **k: False,
    )
    cml._assert_capability_overlay_fresh(["state/config/pipeline-manifest.yaml"])
