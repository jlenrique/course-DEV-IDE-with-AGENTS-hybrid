"""Story Q1.2 — component tests for the per-criterion signal readers + derivation.

Post-review honesty rework (believed-green kill):
  * Only **C3** is purely mechanical (env-independent production-preset posture →
    weak today). **C2** (``model_config_ref``-nullness is a determinism *proxy*, not
    proof) and **C4** (runtime bypass honestly ``"undetected"``) are NOT mechanically
    certifiable, so they are **judgment-with-evidence**: the machine-block level stays
    strong (from the §1.6 durable basis) but is NOT signal-derived, and
    ``level_from_signal`` must NEVER award a clean/uniform level from a
    proxy/unverified/unknown/malformed signal.

Covers AC1/AC2/AC4 + the review's REWORK-1..4 + the anti-believed-green invariant.
Hermetic where a fixture is used; real-repo reads for the manifest, deferred
inventory, and the production-preset gate posture. No live calls; no ``--run-live``.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

from app.quality.scorecard import _DID_KEY, read_scorecard_block
from app.quality.signals import (
    bone_inventory_signal,
    fences_enabled_signal,
    level_from_signal,
    lock_contract_signal,
    open_leak_count_signal,
)

_FENCE_ENVS = {
    "fidelity": "MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE",
    "coverage": "MARCUS_COVERAGE_GATE_ACTIVE",
    "udac": "MARCUS_UDAC_ACTIVE",
}
_GATE_FNS = {
    "fidelity": ("app.specialists.irene.graph", "narration_figure_fidelity_active"),
    "coverage": ("app.marcus.orchestrator.coverage_gate_wiring", "coverage_gate_active"),
    "udac": ("app.marcus.orchestrator.udac_wiring", "udac_active"),
}
_CLEAN = {"strong", "uniform"}


def _write(tmp_path: Path, name: str, text: str) -> Path:
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def _clear_fence_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for env in _FENCE_ENVS.values():
        monkeypatch.delenv(env, raising=False)


def _patch_gate(monkeypatch: pytest.MonkeyPatch, fence: str, value: object) -> None:
    import importlib

    mod_name, attr = _GATE_FNS[fence]
    mod = importlib.import_module(mod_name)
    monkeypatch.setattr(mod, attr, lambda: value)


# ===================== C3 — fences_enabled_signal (env-independent) =====================


def test_fences_production_posture_all_false(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_fence_env(monkeypatch)
    assert fences_enabled_signal() == {
        "fidelity": False,
        "coverage": False,
        "udac": False,
    }


def test_fence_env_pollution_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    """REWORK-3: a polluted ambient shell (a dev with the toggle exported) must NOT
    change the reported production-preset posture — the signal is env-INDEPENDENT."""
    for env in _FENCE_ENVS.values():
        monkeypatch.setenv(env, "1")
    # Despite all three toggles set ON in the environment, the production-preset
    # posture (the preset sets NONE of them) is still all-OFF.
    assert fences_enabled_signal() == {
        "fidelity": False,
        "coverage": False,
        "udac": False,
    }


@pytest.mark.parametrize("fence", ["fidelity", "coverage", "udac"])
def test_fence_anti_drift_via_function(
    monkeypatch: pytest.MonkeyPatch, fence: str
) -> None:
    """C3 anti-drift: the gate FUNCTION is the source of truth. Flipping exactly one
    gate fn flips exactly that key (env-independent — env stays polluted ON)."""
    for env in _FENCE_ENVS.values():
        monkeypatch.setenv(env, "1")  # pollution must not matter
    _patch_gate(monkeypatch, fence, True)
    sig = fences_enabled_signal()
    assert sig[fence] is True
    for other in _FENCE_ENVS:
        if other != fence:
            assert sig[other] is False, f"{other} drifted when {fence} toggled"


def test_fences_per_field_fail_soft(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom() -> bool:
        raise RuntimeError("gate read exploded")

    import app.specialists.irene.graph as g

    _clear_fence_env(monkeypatch)
    monkeypatch.setattr(g, "narration_figure_fidelity_active", _boom)
    sig = fences_enabled_signal()
    assert sig["fidelity"] == "unavailable"
    assert sig["coverage"] is False
    assert sig["udac"] is False


def test_fences_nonbool_gate_degrades(monkeypatch: pytest.MonkeyPatch) -> None:
    """A gate returning a non-bool (e.g. None) degrades to 'unavailable', never
    silently bool()-coerced to False (Q1.4a FIX-B)."""
    _clear_fence_env(monkeypatch)
    _patch_gate(monkeypatch, "udac", None)
    assert fences_enabled_signal()["udac"] == "unavailable"


@pytest.mark.parametrize(
    ("sig", "expected"),
    [
        ({"fidelity": False, "coverage": False, "udac": False}, "weak"),
        ({"fidelity": True, "coverage": False, "udac": False}, "partial"),
        ({"fidelity": True, "coverage": True, "udac": True}, "strong"),
        ({"fidelity": "unavailable", "coverage": False, "udac": False}, "unavailable"),
        ("garbage", "unavailable"),
        ({}, "unavailable"),
    ],
)
def test_level_c3_total(sig: object, expected: str) -> None:
    assert level_from_signal("fence_enforcement_default_on", sig) == expected


# ===================== C2 — bone_inventory_signal (honestly named proxy) =====================

_FIXTURE_MANIFEST = textwrap.dedent(
    """\
    schema_version: test
    nodes:
      - id: "A-render"
        label: "Deterministic render"
        specialist_id: null
        model_config_ref: null
        gate: false
      - id: "B-gate"
        label: "Deterministic gate"
        specialist_id: null
        model_config_ref: null
        gate: true
      - id: "C-neck"
        label: "LLM neck"
        specialist_id: "irene"
        model_config_ref: "app/x/model_config.yaml"
        gate: false
    """
)


def test_bone_inventory_fixture_clean(tmp_path: Path) -> None:
    p = _write(tmp_path, "m.yaml", _FIXTURE_MANIFEST)
    sig = bone_inventory_signal(p)
    assert sig["status"] == "ok"
    assert sig["total_nodes"] == 3
    # Honestly-named fields: what the signal MEASURES is model_config_ref nullness,
    # NOT determinism.
    assert sig["model_config_ref_null_count"] == 2
    assert sig["model_config_ref_null_nodes"] == ["A-render", "B-gate"]
    assert [n["id"] for n in sig["model_config_ref_set_nodes"]] == ["C-neck"]
    assert sig["gates_all_model_config_ref_null"] is True
    assert sig["model_config_ref_absent_nodes"] == []
    # A config-ref proxy cannot mechanically certify 'strong' — never clean here.
    assert level_from_signal("bone_determinism", sig) not in _CLEAN


def test_bone_inventory_key_absent_not_counted_null(tmp_path: Path) -> None:
    """REWORK-4.1: a node MISSING the model_config_ref key is unknown, NOT counted as
    null — it must not inflate the null roster."""
    absent = textwrap.dedent(
        """\
        nodes:
          - id: "no-key"
            label: "missing the field entirely"
            gate: false
          - id: "explicit-null"
            model_config_ref: null
            gate: false
        """
    )
    p = _write(tmp_path, "absent.yaml", absent)
    sig = bone_inventory_signal(p)
    assert sig["model_config_ref_null_count"] == 1  # only explicit-null
    assert sig["model_config_ref_null_nodes"] == ["explicit-null"]
    assert sig["model_config_ref_absent_nodes"] == ["no-key"]


def test_bone_inventory_truthy_gate_breach_caught(tmp_path: Path) -> None:
    """REWORK-4.2: a gate that is truthy-but-not-True (gate: 1) carrying an LLM ref is
    still a boundary breach → gates_all_model_config_ref_null False → non-clean."""
    breach = textwrap.dedent(
        """\
        nodes:
          - id: "truthy-gate-llm"
            model_config_ref: "app/x/model_config.yaml"
            gate: 1
        """
    )
    p = _write(tmp_path, "breach.yaml", breach)
    sig = bone_inventory_signal(p)
    assert sig["gates_all_model_config_ref_null"] is False
    assert level_from_signal("bone_determinism", sig) == "partial"


def test_bone_inventory_seeded_llm_grows_roster(tmp_path: Path) -> None:
    seeded = _FIXTURE_MANIFEST.replace(
        "    model_config_ref: null\n    gate: false",
        '    model_config_ref: "app/seed/model_config.yaml"\n    gate: false',
        1,
    )
    p = _write(tmp_path, "seed.yaml", seeded)
    sig = bone_inventory_signal(p)
    assert sig["model_config_ref_null_count"] == 1  # was 2
    assert {n["id"] for n in sig["model_config_ref_set_nodes"]} == {"A-render", "C-neck"}


def test_bone_inventory_real_manifest() -> None:
    sig = bone_inventory_signal()
    assert sig["status"] == "ok"
    assert sig["total_nodes"] == 52
    assert sig["model_config_ref_null_count"] == 49
    assert {n["id"] for n in sig["model_config_ref_set_nodes"]} == {
        "07G",
        "07W.1",
        "07W.3",
    }
    assert sig["gates_all_model_config_ref_null"] is True
    # Proxy → the mechanical derivation cannot award 'strong' (that is a §1.6 judgment).
    assert level_from_signal("bone_determinism", sig) not in _CLEAN


def test_bone_inventory_missing_file_unavailable(tmp_path: Path) -> None:
    sig = bone_inventory_signal(tmp_path / "nope.yaml")
    assert sig["status"] == "unavailable"
    assert level_from_signal("bone_determinism", sig) == "unavailable"


def test_bone_inventory_malformed_is_unavailable(tmp_path: Path) -> None:
    p = _write(tmp_path, "bad.yaml", "nodes: not-a-list\n")
    assert bone_inventory_signal(p)["status"] == "unavailable"


@pytest.mark.parametrize(
    ("sig", "expected"),
    [
        ({"status": "ok", "gates_all_model_config_ref_null": True}, "unavailable"),
        ({"status": "ok", "gates_all_model_config_ref_null": False}, "partial"),
        ({"status": "unavailable"}, "unavailable"),
        ("garbage", "unavailable"),
        ({}, "unavailable"),
    ],
)
def test_level_c2_total_never_clean(sig: object, expected: str) -> None:
    got = level_from_signal("bone_determinism", sig)
    assert got == expected
    assert got not in _CLEAN


# ===================== C4 — lock_contract_signal (unverified → never clean) =====================


def _c4sig(present: object, bypass: object) -> dict[str, object]:
    return {
        "status": "ok",
        "digest_module_present_on_disk": present,
        "silent_bypass_events": bypass,
    }


def test_lock_contract_real_undetected() -> None:
    sig = lock_contract_signal()
    assert sig["status"] == "ok"
    assert sig["digest_module_present_on_disk"] is True
    assert sig["silent_bypass_events"] == "undetected"
    # BLOCKER fix: undetected can NEVER award a clean level.
    assert level_from_signal("lock_and_contract_discipline", sig) == "partial"


def test_lock_contract_run_summary_str_path(tmp_path: Path) -> None:
    """REWORK-4.8: a real run-summary passed as a STR path must be read, not silently
    treated as 'no run' → undetected."""
    p = tmp_path / "run_summary.yaml"
    p.write_text(
        yaml.safe_dump({"fence_state": {"silent_bypass_events": 0}}),
        encoding="utf-8",
    )
    sig = lock_contract_signal(str(p))  # STR, not Path
    assert sig["silent_bypass_events"] == 0


def test_lock_contract_stringified_bypass() -> None:
    """REWORK-4.3: '3' coerces to int 3 (a real count), never passes through as clean."""
    sig = lock_contract_signal({"fence_state": {"silent_bypass_events": "3"}})
    assert sig["silent_bypass_events"] == 3
    assert level_from_signal("lock_and_contract_discipline", sig) == "partial"


def test_lock_contract_float_bypass() -> None:
    """REWORK-4.4: 2.0 is a real count → partial; never floored to undetected/clean."""
    sig = lock_contract_signal({"fence_state": {"silent_bypass_events": 2.0}})
    assert sig["silent_bypass_events"] == 2
    assert level_from_signal("lock_and_contract_discipline", sig) == "partial"


def test_lock_contract_zero_int_may_be_strong() -> None:
    sig = lock_contract_signal({"fence_state": {"silent_bypass_events": 0}})
    assert sig["silent_bypass_events"] == 0
    assert level_from_signal("lock_and_contract_discipline", sig) == "strong"


def test_lock_contract_detected_bypasses_partial() -> None:
    sig = lock_contract_signal({"fence_state": {"silent_bypass_events": 3}})
    assert level_from_signal("lock_and_contract_discipline", sig) == "partial"


def test_lock_contract_missing_run_summary_path_falls_back(tmp_path: Path) -> None:
    sig = lock_contract_signal(tmp_path / "absent.yaml")
    assert sig["status"] == "ok"
    assert sig["silent_bypass_events"] == "undetected"
    assert level_from_signal("lock_and_contract_discipline", sig) == "partial"


@pytest.mark.parametrize(
    ("sig", "expected"),
    [
        (_c4sig(True, "undetected"), "partial"),
        (_c4sig(True, 0), "strong"),
        (_c4sig(True, 5), "partial"),
        (_c4sig(True, "unavailable"), "unavailable"),  # REWORK-1: was wrongly 'strong'
        (_c4sig(True, -1), "unavailable"),
        (_c4sig(True, True), "unavailable"),  # bool is not a count
        (_c4sig(False, "undetected"), "weak"),
        (_c4sig("maybe", "undetected"), "unavailable"),
        ({"status": "unavailable"}, "unavailable"),
        ("garbage", "unavailable"),
    ],
)
def test_level_c4_total(sig: object, expected: str) -> None:
    assert level_from_signal("lock_and_contract_discipline", sig) == expected


# ===================== leak-count — open_leak_count_signal =====================

_FIXTURE_INVENTORY = textwrap.dedent(
    """\
    # Deferred Inventory

    ## Named-But-Not-Filed Follow-Ons

    ### open-entry-one
    did_leak: true — this is an OPEN leak, counted.

    ### open-entry-two
    Some prose. A parenthetical mention of did_leak: is NOT at line start → skip.
    did_leak: yes — this OPEN tag IS at line start, counted.

    ## Closed Entries — Archived (preserved for audit trail)

    ### archived-entry
    did_leak: true — but ARCHIVED, must NOT count.

    ## Some Later Open Section

    ### later-open-entry
    did_leak: true — OPEN again (after the archived block), counted.
    """
)


def test_open_leak_count_fixture_counts_open_only(tmp_path: Path) -> None:
    p = _write(tmp_path, "inv.md", _FIXTURE_INVENTORY)
    sig = open_leak_count_signal(p)
    assert sig["status"] == "ok"
    # three OPEN line-start tags; the mid-line prose mention and the archived tag excluded
    assert sig["open_leak_count"] == 3


def test_open_leak_count_skips_fenced_code(tmp_path: Path) -> None:
    """REWORK-4.6: a did_leak: inside a fenced code block is an EXAMPLE, not a tag."""
    doc = textwrap.dedent(
        """\
        # Deferred Inventory

        ### real-open
        did_leak: true — counted.

        ### example
        Here is how to tag it:

        ```yaml
        did_leak: true   # example inside a code fence — must NOT count
        ```
        """
    )
    p = _write(tmp_path, "fence.md", doc)
    assert open_leak_count_signal(p)["open_leak_count"] == 1


def test_open_leak_count_exact_archive_header(tmp_path: Path) -> None:
    """REWORK-4.7: only the EXACT '## Closed Entries …' header starts the archive
    block — a heading merely MENTIONING closed entries mid-text is still OPEN."""
    doc = textwrap.dedent(
        """\
        # Deferred Inventory

        ## Why we keep closed entries around (a discussion, NOT the archive)
        did_leak: true — still OPEN, counted.

        ## Closed Entries — Archived (preserved for audit trail)
        did_leak: true — ARCHIVED, excluded.
        """
    )
    p = _write(tmp_path, "hdr.md", doc)
    assert open_leak_count_signal(p)["open_leak_count"] == 1


def test_open_leak_count_real_is_zero_today() -> None:
    sig = open_leak_count_signal()
    assert sig["status"] == "ok"
    assert sig["open_leak_count"] == 0


def test_open_leak_count_missing_file_unavailable(tmp_path: Path) -> None:
    sig = open_leak_count_signal(tmp_path / "nope.md")
    assert sig["status"] == "unavailable"
    assert sig["open_leak_count"] is None


# ===================== level_from_signal — totality + anti-believed-green =====================


def test_level_from_signal_judgment_criteria_return_none() -> None:
    assert level_from_signal("neck_placement", None) is None
    assert level_from_signal("honesty_and_calibration", {"anything": 1}) is None
    assert level_from_signal("some_unknown_key", None) is None


@pytest.mark.parametrize(
    "key",
    ["bone_determinism", "fence_enforcement_default_on", "lock_and_contract_discipline"],
)
@pytest.mark.parametrize(
    "degenerate",
    [
        None,
        "unavailable",
        "undetected",
        "garbage",
        {},
        {"status": "unavailable"},
        {"fidelity": "unavailable", "coverage": "unavailable", "udac": "unavailable"},
        {"status": "ok"},  # missing the criterion's fields
    ],
)
def test_no_clean_level_from_degenerate_signal(key: str, degenerate: object) -> None:
    """THE anti-believed-green invariant: for EVERY mechanical criterion, an
    unavailable/undetected/unknown/malformed signal maps to a NON-clean level —
    never strong/uniform. ``level_from_signal`` is total (never raises)."""
    got = level_from_signal(key, degenerate)
    assert got not in _CLEAN, f"{key} awarded clean level {got!r} from {degenerate!r}"


# ===================== machine-block reclassification (AC3 / no hand-score) =====================


def test_c3_is_signal_derived_and_agrees(monkeypatch: pytest.MonkeyPatch) -> None:
    """C3 is the ONLY purely-mechanical criterion: machine-block level == derived."""
    _clear_fence_env(monkeypatch)
    block = read_scorecard_block()
    assert isinstance(block, dict)
    crit = block["dimensions"][_DID_KEY]["criteria"]["fence_enforcement_default_on"]
    assert crit["derivation"] == "signal-derived"
    derived = level_from_signal("fence_enforcement_default_on", fences_enabled_signal())
    assert derived == "weak"
    assert crit["level"] == derived


def test_c2_c4_are_judgment_with_evidence() -> None:
    """C2/C4 are NOT purely signal-derived: level stays strong (from §1.6 basis), the
    machine block LABELS them judgment-with-evidence + evidence_ref, and the mechanical
    derivation from today's proxy/unverified signal is NON-clean (proving the strong is
    a documented human judgment, not a false mechanical claim)."""
    block = read_scorecard_block()
    assert isinstance(block, dict)
    crit = block["dimensions"][_DID_KEY]["criteria"]
    for key, reader in (
        ("bone_determinism", bone_inventory_signal),
        ("lock_and_contract_discipline", lock_contract_signal),
    ):
        c = crit[key]
        assert c["derivation"] == "judgment-with-evidence"
        assert c["level"] == "strong"  # DID number unchanged
        assert isinstance(c["signal"], dict)
        assert c["signal"]["reader"].startswith("app.quality.signals.")
        assert isinstance(c["evidence_ref"], str) and c["evidence_ref"]
        # The mechanical signal today does NOT award the clean level:
        assert level_from_signal(key, reader()) not in _CLEAN


def test_c1_c5_stay_judgment_signal_null() -> None:
    block = read_scorecard_block()
    assert isinstance(block, dict)
    crit = block["dimensions"][_DID_KEY]["criteria"]
    assert crit["neck_placement"]["signal"] is None
    assert crit["honesty_and_calibration"]["signal"] is None


def test_did_headline_numbers_unchanged() -> None:
    """The DID numbers STAY (65/B-; C1/C2 strong, C3 weak, C4 strong, C5 partial;
    open_leaks 5) — the rework relabels HOW levels are justified, not the score."""
    block = read_scorecard_block()
    assert isinstance(block, dict)
    dim = block["dimensions"][_DID_KEY]
    assert dim["score"] == 65
    assert dim["band"] == "B-"
    assert dim["open_leaks"] == 5
    levels = {k: v["level"] for k, v in dim["criteria"].items()}
    assert levels == {
        "neck_placement": "strong",
        "bone_determinism": "strong",
        "fence_enforcement_default_on": "weak",
        "lock_and_contract_discipline": "strong",
        "honesty_and_calibration": "partial",
    }
