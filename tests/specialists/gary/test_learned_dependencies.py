"""Leg-B2 — hermetic learned-dependencies store scaffold (RED-first).

Pins the declarative learned-rule interpreter, the append-only digest-idempotent
observations ledger (a FILE store, NOT the Postgres ``app/ledger``), the identity-
manifest pin (superset + predicate_hash + fixture existence), the anti-vacuous-green
guard, and the honesty disclaimer. Asserts DIAGNOSTIC IDS, not just exit codes.

SCAFFOLD: ships ZERO active learned rules. The manifest is EMPTY by design; the 3
candidates live in the ledger as ``status: candidate`` OBSERVATIONS and do NOT
enforce. NO network, NO DB in any test.
"""

from __future__ import annotations

import copy

import pytest

pytestmark = pytest.mark.filterwarnings("ignore")


# --------------------------------------------------------------------------- #
# Fixtures / helpers
# --------------------------------------------------------------------------- #
def _synthetic_rule(*, severity: str = "fail", status: str = "active") -> dict:
    """A declarative learned rule: image_model present ⇒ image_source == aiGenerated."""
    return {
        "rule_id": "synthetic-image-model-requires-aigen",
        "antecedent": {"field": "image_model", "predicate": {"op": "present"}},
        "consequent": {
            "field": "image_source",
            "expected": {"op": "equals", "value": "aiGenerated"},
        },
        "severity": severity,
        "status": status,
        "provenance": {
            "observation_ids": ["obs-synthetic-1"],
            "birthing_run_ref": "fixture://synthetic",
            "fixture_path": "tests/specialists/gary/fixtures/synthetic.json",
            "promoted_at": "2026-07-01T00:00:00Z",
            "cd_commit": "deadbeef",
        },
    }


def _violating_resolved() -> dict:
    return {"image_model": "recraft-v3-svg", "image_source": "pexels"}


def _good_resolved() -> dict:
    return {"image_model": "recraft-v3-svg", "image_source": "aiGenerated"}


# --------------------------------------------------------------------------- #
# AC#1 — schema + interpreter
# --------------------------------------------------------------------------- #
def test_ac1_active_rule_fires_error_on_violation_silent_on_good() -> None:
    from app.specialists.gary.learned_dependencies import apply_learned_rules

    rule = _synthetic_rule(severity="fail")
    errors, warnings = apply_learned_rules({}, _violating_resolved(), [rule])
    assert any("gamma.learned.synthetic-image-model-requires-aigen" in e for e in errors), errors
    assert warnings == []

    errors2, warnings2 = apply_learned_rules({}, _good_resolved(), [rule])
    assert errors2 == [], errors2
    assert warnings2 == []


def test_ac1_warn_severity_routes_to_warnings_channel() -> None:
    from app.specialists.gary.learned_dependencies import apply_learned_rules

    rule = _synthetic_rule(severity="warn")
    errors, warnings = apply_learned_rules({}, _violating_resolved(), [rule])
    assert errors == [], errors
    tag = "gamma.learned.synthetic-image-model-requires-aigen"
    assert any(tag in w for w in warnings), warnings


def test_ac1_antecedent_false_is_silent() -> None:
    from app.specialists.gary.learned_dependencies import apply_learned_rules

    rule = _synthetic_rule()
    # image_model absent -> antecedent 'present' is false -> rule not triggered.
    errors, warnings = apply_learned_rules({}, {"image_source": "pexels"}, [rule])
    assert errors == [] and warnings == []


def test_ac1_candidate_status_rule_never_evaluates() -> None:
    from app.specialists.gary.learned_dependencies import apply_learned_rules

    rule = _synthetic_rule(status="candidate")
    errors, warnings = apply_learned_rules({}, _violating_resolved(), [rule])
    assert errors == [] and warnings == [], (errors, warnings)


def test_ac1_predicate_ops_are_a_closed_set() -> None:
    from app.specialists.gary.learned_dependencies import (
        SUPPORTED_PREDICATE_OPS,
        apply_learned_rules,
    )

    assert set(SUPPORTED_PREDICATE_OPS) == {
        "present",
        "absent",
        "equals",
        "not_equals",
        "in",
    }
    # An unknown op is a fail-loud validation error, never silently-true.
    bad = _synthetic_rule()
    bad["antecedent"]["predicate"] = {"op": "regex_eval", "value": ".*"}
    with pytest.raises(ValueError):
        apply_learned_rules({}, _violating_resolved(), [bad])


# --------------------------------------------------------------------------- #
# AC#2 — append-only, digest-idempotent ledger
# --------------------------------------------------------------------------- #
def _obs(digest: str, *, status: str = "candidate") -> dict:
    return {
        "observation_id": f"obs-{digest}",
        "observed_at": "2026-07-01T00:00:00Z",
        "output_digest": digest,
        "source_component": "test",
        "behavior": "synthetic observation",
        "status": status,
    }


def test_ac2_append_new_then_idempotent_noop(tmp_path) -> None:
    from app.specialists.gary.learned_dependencies import (
        append_observation,
        read_observations,
    )

    ledger = tmp_path / "obs.jsonl"
    assert append_observation(ledger, _obs("d1")) is True
    assert append_observation(ledger, _obs("d2")) is True
    assert len(read_observations(ledger)) == 2

    before = ledger.read_text(encoding="utf-8")
    # Re-append same digest -> no-op, returns False, file byte-identical.
    assert append_observation(ledger, _obs("d1")) is False
    after = ledger.read_text(encoding="utf-8")
    assert before == after
    assert len(read_observations(ledger)) == 2


def test_ac2_append_only_line_count_only_grows(tmp_path) -> None:
    from app.specialists.gary.learned_dependencies import (
        append_observation,
        read_observations,
    )

    ledger = tmp_path / "obs.jsonl"
    counts = []
    for i in range(4):
        append_observation(ledger, _obs(f"d{i}"))
        counts.append(len(read_observations(ledger)))
    # monotonically non-decreasing, never shrinks
    assert counts == sorted(counts)
    assert counts[-1] == 4


def test_ac2_read_missing_ledger_returns_empty(tmp_path) -> None:
    from app.specialists.gary.learned_dependencies import read_observations

    assert read_observations(tmp_path / "nope.jsonl") == []


# --------------------------------------------------------------------------- #
# AC#3 — 3 shipped candidates are OBSERVATIONS only (not rules, not manifest)
# --------------------------------------------------------------------------- #
def test_ac3_three_shipped_candidates_are_observations_only() -> None:
    from app.specialists.gary.learned_dependencies import (
        GAMMA_LEARNED_OBSERVATIONS_PATH,
        GAMMA_LEARNED_RULES_LOCK_PATH,
        load_manifest,
        read_observations,
    )

    obs = read_observations(GAMMA_LEARNED_OBSERVATIONS_PATH)
    candidates = [o for o in obs if o.get("status") == "candidate"]
    # Leg-E (2026-07-02) legitimately appended run-born observations to the real
    # ledger, so the exact-3 seed count no longer holds. The AC#3 invariants that
    # DO hold forever: the 3 shipped seeds are present, EVERY ledger row is a
    # candidate observation (append-only; nothing self-promotes), and each row
    # carries the provenance trio.
    assert len(candidates) == len(obs), "every ledger row must be status:candidate"
    seed_ids = {
        "obs-gamma-model-ui-name-vs-api-string-2026-06-25",
        "obs-gamma-burst-throttle-401-not-429-2026-06-25",
        "obs-account-parallel-task-cap-2026-06-26",
    }
    present = {o.get("observation_id") for o in candidates}
    assert seed_ids <= present, (seed_ids - present, present)
    for o in candidates:
        assert o.get("output_digest")
        assert o.get("birthing_run_ref")
        assert o.get("behavior")

    # None are promoted rules; the shipped manifest is EMPTY.
    manifest = load_manifest(GAMMA_LEARNED_RULES_LOCK_PATH)
    assert manifest == []
    manifest_ids = {m.get("rule_id") for m in manifest}
    for o in candidates:
        assert o["observation_id"] not in manifest_ids


def test_ac3_candidates_do_not_enforce() -> None:
    # Observations carry no antecedent/consequent surface; feeding them to the
    # interpreter as if they were rules yields nothing (they are not 'active' rules).
    from app.specialists.gary.learned_dependencies import (
        GAMMA_LEARNED_OBSERVATIONS_PATH,
        apply_learned_rules,
        read_observations,
    )

    obs = read_observations(GAMMA_LEARNED_OBSERVATIONS_PATH)
    errors, warnings = apply_learned_rules({}, _violating_resolved(), obs)
    assert errors == [] and warnings == [], (errors, warnings)


# --------------------------------------------------------------------------- #
# AC#4 — identity-manifest pin (superset + predicate_hash + fixture)
# --------------------------------------------------------------------------- #
def _manifest_row(rule: dict, fixture_path: str) -> dict:
    from app.specialists.gary.learned_dependencies import predicate_hash

    return {
        "rule_id": rule["rule_id"],
        "provenance_run_ref": rule["provenance"]["birthing_run_ref"],
        "fixture_path": fixture_path,
        "predicate_hash": predicate_hash(rule),
    }


def test_ac4_empty_manifest_empty_rules_passes() -> None:
    from app.specialists.gary.learned_dependencies import check_manifest_pin

    assert check_manifest_pin([], []) == []


def test_ac4_active_rule_not_in_manifest_is_pin_violation(tmp_path) -> None:
    from app.specialists.gary.learned_dependencies import check_manifest_pin

    rule = _synthetic_rule()
    errors = check_manifest_pin([rule], [])  # no manifest row for the active rule
    assert any("gamma.learned.pin-violation" in e for e in errors), errors
    assert any(rule["rule_id"] in e for e in errors), errors


def test_ac4_predicate_hash_mismatch_is_red(tmp_path) -> None:
    from app.specialists.gary.learned_dependencies import check_manifest_pin

    fixture = tmp_path / "fx.json"
    fixture.write_text("{}", encoding="utf-8")
    rule = _synthetic_rule()
    row = _manifest_row(rule, str(fixture))
    row["predicate_hash"] = "0" * 64  # tampered / stale hash
    errors = check_manifest_pin([rule], [row])
    assert any("gamma.learned.pin-violation" in e and "predicate_hash" in e for e in errors), errors


def test_ac4_removing_manifested_id_is_red_superset(tmp_path) -> None:
    from app.specialists.gary.learned_dependencies import check_manifest_pin

    fixture = tmp_path / "fx.json"
    fixture.write_text("{}", encoding="utf-8")
    rule = _synthetic_rule()
    row = _manifest_row(rule, str(fixture))
    # Manifest still pins the rule, but it was dropped from the active set.
    errors = check_manifest_pin([], [row])
    assert any("gamma.learned.pin-violation" in e and rule["rule_id"] in e for e in errors), errors


def test_ac4_matching_manifest_row_with_fixture_passes(tmp_path) -> None:
    from app.specialists.gary.learned_dependencies import check_manifest_pin

    fixture = tmp_path / "fx.json"
    fixture.write_text("{}", encoding="utf-8")
    rule = _synthetic_rule()
    row = _manifest_row(rule, str(fixture))
    assert check_manifest_pin([rule], [row]) == []


# --------------------------------------------------------------------------- #
# AC#5 — anti-vacuous guard (BLOCKING)
# --------------------------------------------------------------------------- #
def test_ac5_active_rule_without_existing_fixture_is_red(tmp_path) -> None:
    from app.specialists.gary.learned_dependencies import check_manifest_pin

    rule = _synthetic_rule()
    row = _manifest_row(rule, str(tmp_path / "does-not-exist.json"))
    errors = check_manifest_pin([rule], [row])
    assert any("gamma.learned.pin-violation" in e for e in errors), errors
    assert any("fixture" in e.lower() for e in errors), errors


def test_ac5_empty_ship_state_is_honest() -> None:
    from app.specialists.gary.learned_dependencies import (
        GAMMA_LEARNED_RULES_LOCK_PATH,
        check_manifest_pin,
        load_manifest,
    )

    manifest = load_manifest(GAMMA_LEARNED_RULES_LOCK_PATH)
    assert manifest == []
    assert check_manifest_pin([], manifest) == []


# --------------------------------------------------------------------------- #
# AC#6 — hermetic (no network, no psycopg / app.ledger)
# --------------------------------------------------------------------------- #
def test_ac6_default_full_path_makes_no_network_call(monkeypatch) -> None:
    import socket

    from scripts.utilities.validate_gamma_style_guides import (
        GAMMA_STYLE_GUIDES_PATH,
        load_style_guides,
        validate_style_guides_full,
    )

    data = load_style_guides(GAMMA_STYLE_GUIDES_PATH)

    def _boom(*_a, **_k):
        raise AssertionError("validate_style_guides_full opened a network socket")

    monkeypatch.setattr(socket, "socket", _boom)
    assert validate_style_guides_full(data) == ([], [])


def test_ac6_module_imports_no_psycopg_or_app_ledger() -> None:
    from pathlib import Path

    import app.specialists.gary.learned_dependencies as mod

    source = Path(mod.__file__).read_text(encoding="utf-8")
    assert "psycopg" not in source, "learned_dependencies must not couple to the Postgres ledger"
    assert "app.ledger" not in source and "app/ledger" not in source, source[:200]


# --------------------------------------------------------------------------- #
# AC#7 — back-compat + seeds clean
# --------------------------------------------------------------------------- #
def test_ac7_three_seeds_zero_errors_zero_warnings() -> None:
    from scripts.utilities.validate_gamma_style_guides import (
        GAMMA_STYLE_GUIDES_PATH,
        load_style_guides,
        validate_style_guides,
        validate_style_guides_full,
    )

    data = load_style_guides(GAMMA_STYLE_GUIDES_PATH)
    errors, warnings = validate_style_guides_full(data)
    assert errors == [], errors
    assert warnings == [], warnings
    assert validate_style_guides(data) == []


# --------------------------------------------------------------------------- #
# AC#8 — honesty disclaimer (Dan, BINDING)
# --------------------------------------------------------------------------- #
def test_ac8_module_docstring_disclaims_live_ceremony() -> None:
    import app.specialists.gary.learned_dependencies as mod

    doc = (mod.__doc__ or "").lower()
    assert "validated-by-fixture" in doc or "validated by fixture" in doc, doc
    assert "not" in doc and "exercised" in doc, doc
    assert "envelope" in doc and "ceremony" in doc, doc


# --------------------------------------------------------------------------- #
# Validator wiring — active rule flows through per-record into the channels
# --------------------------------------------------------------------------- #
def test_validator_applies_active_learned_rule_per_record(tmp_path) -> None:
    from scripts.utilities.validate_gamma_style_guides import (
        GAMMA_STYLE_GUIDES_PATH,
        load_style_guides,
        validate_style_guides_full,
    )

    fixture = tmp_path / "fx.json"
    fixture.write_text("{}", encoding="utf-8")
    rule = _synthetic_rule(severity="fail")
    row = _manifest_row(rule, str(fixture))
    lock = tmp_path / "rules.lock"
    lock.write_text(
        f'{{"schema_version": "1.0", "rules": [{_row_json(row)}]}}',
        encoding="utf-8",
    )

    data = load_style_guides(GAMMA_STYLE_GUIDES_PATH)
    broken = copy.deepcopy(data)
    # crossroads-classic carries image_model=gpt-image-2-mini; flip its source off aiGenerated
    broken["style_guides"]["hil-2026-apc-crossroads-classic"]["prompt_configuration"][
        "visuals"
    ]["image_source"] = "pexels"
    broken["learned_dependencies"] = [rule]

    errors, _warnings = validate_style_guides_full(broken, lock_path=lock)
    assert any("gamma.learned.synthetic-image-model-requires-aigen" in e for e in errors), errors


def _row_json(row: dict) -> str:
    import json

    return json.dumps(row)
