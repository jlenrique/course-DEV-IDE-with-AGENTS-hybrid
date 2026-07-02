"""Hermetic learned-dependencies store SCAFFOLD for the CD-owned Gamma styleguide.

Leg-B2 (arc ``dev/gamma-styleguide-library-2026-07-01``). Stands up the WRITE-TARGET
and enforcement machinery for *learned* Gamma-dependency rules so that, once Leg-E's
live audit produces real observations, a promoted rule can be validated OFFLINE and
cannot silently vanish or mutate.

Two-store split (ratified Leg-B green-light §Decision 3/6):

* Raw OBSERVATIONS -> an append-only, digest-idempotent JSONL ledger
  (``state/config/gamma-learned-observations.jsonl``). This is the SOLE SSOT and is
  a plain FILE store. It is deliberately NOT the Postgres event ledger under
  ``app/`` (that one is DB-coupled and non-hermetic); this scaffold never touches a
  database or a network socket.
* Promoted RULES -> a CD-authored ``learned_dependencies`` YAML block, provenance-
  cited and validator-gated by the identity-manifest pin
  (``state/config/gamma-learned-rules.lock``).

⚠️ HONESTY DISCLAIMER (Dan, BINDING; surgically updated at Leg-E close per D-9):
the **WRITE PATH is now exercised LIVE** — the Leg-E ``gamma_docs`` live-doc audit
(``scripts/utilities/audit_gamma_docs.py``) produced the ledger's first real
run-born observations via ``append_observation`` (evidence:
``_bmad-output/implementation-artifacts/evidence/leg-e-gamma-docs-audit-20260702T043139Z/``;
idempotent re-run witnessed byte-identical). The live CD envelope-authoring
**ceremony** and the automation-proposes / CD-ratifies **promotion path** REMAIN
validated-by-fixture, NOT exercised live — DEFERRED to
``styleguide-cd-envelope-authoring-ceremony`` (its reactivation trigger, "Leg-E
produces real observations", has now FIRED — noted, not acted on). This module
still ships ZERO active learned rules — the manifest stays EMPTY by design and
every ledger row remains a ``status: candidate`` OBSERVATION that does NOT enforce.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

try:  # TypedDict is documentation-only here (declarative schema, not runtime-enforced)
    from typing import TypedDict
except ImportError:  # pragma: no cover
    TypedDict = None  # type: ignore[assignment]

from app.specialists.gary.styleguide_library import (
    PROJECT_ROOT,
    _is_present,
)

# --- Ship paths (file stores; hermetic) --------------------------------------- #
GAMMA_LEARNED_RULES_LOCK_PATH = (
    PROJECT_ROOT / "state" / "config" / "gamma-learned-rules.lock"
)
GAMMA_LEARNED_OBSERVATIONS_PATH = (
    PROJECT_ROOT / "state" / "config" / "gamma-learned-observations.jsonl"
)

# --- Closed predicate op set (NO free-form / eval logic) ---------------------- #
# ``present``/``absent`` take no value; ``equals``/``not_equals``/``in`` take a value.
SUPPORTED_PREDICATE_OPS = frozenset({"present", "absent", "equals", "not_equals", "in"})

PIN_VIOLATION_TAG = "gamma.learned.pin-violation"


# --- Declarative schema (documentation-only TypedDicts) ----------------------- #
if TypedDict is not None:  # pragma: no branch

    class Predicate(TypedDict, total=False):
        op: str
        value: Any

    class Antecedent(TypedDict):
        field: str
        predicate: Predicate

    class Consequent(TypedDict):
        field: str
        expected: Predicate

    class Provenance(TypedDict, total=False):
        observation_ids: list[str]
        birthing_run_ref: str
        fixture_path: str
        promoted_at: str
        cd_commit: str

    class LearnedRule(TypedDict, total=False):
        rule_id: str
        antecedent: Antecedent
        consequent: Consequent
        severity: str  # 'fail' | 'warn'
        provenance: Provenance
        status: str  # 'active' | 'candidate'


def _norm(value: Any) -> Any:
    """Normalize a scalar for comparison (strings are stripped)."""
    if isinstance(value, str):
        return value.strip()
    return value


def _eval_predicate(predicate: dict[str, Any] | None, actual: Any) -> bool:
    """Evaluate one closed-set predicate op against ``actual``. Fail-loud on unknown op."""
    if not isinstance(predicate, dict):
        raise ValueError(f"learned-rule predicate must be a mapping; got {predicate!r}")
    op = predicate.get("op")
    if op not in SUPPORTED_PREDICATE_OPS:
        raise ValueError(
            f"learned-rule predicate op {op!r} is not in the closed set "
            f"{sorted(SUPPORTED_PREDICATE_OPS)} (no free-form/eval logic allowed)"
        )
    if op == "present":
        return _is_present(actual)
    if op == "absent":
        return not _is_present(actual)
    value = predicate.get("value")
    if op == "equals":
        return _norm(actual) == _norm(value)
    if op == "not_equals":
        return _norm(actual) != _norm(value)
    if op == "in":
        choices = value if isinstance(value, (list, tuple, set)) else [value]
        return _norm(actual) in {_norm(v) for v in choices}
    raise ValueError(f"unreachable predicate op {op!r}")  # pragma: no cover


def _lookup(field: str | None, record: dict[str, Any], resolved: dict[str, Any]) -> Any:
    """Resolve ``field`` against the resolved surface first, then a dotted record path."""
    if field is None:
        return None
    if field in resolved:
        return resolved[field]
    cur: Any = record
    for part in field.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


def apply_learned_rules(
    record: dict[str, Any],
    resolved: dict[str, Any],
    rules: list[dict[str, Any]],
    *,
    name: str = "",
) -> tuple[list[str], list[str]]:
    """Pure declarative interpreter: evaluate ACTIVE learned rules against a record.

    For each ACTIVE rule, if the ``antecedent`` predicate holds and the
    ``consequent`` predicate does NOT, emit a diagnostic tagged
    ``gamma.learned.<rule_id>`` routed to ``errors`` (severity ``fail``) or
    ``warnings`` (severity ``warn``). Candidate rules are never evaluated. No
    free-form logic — only the closed predicate op set.
    """
    errors: list[str] = []
    warnings: list[str] = []
    prefix = f"{name}: " if name else ""
    for rule in rules or []:
        if not isinstance(rule, dict) or rule.get("status") != "active":
            continue
        rule_id = rule.get("rule_id", "<unnamed>")
        antecedent = rule.get("antecedent") or {}
        consequent = rule.get("consequent") or {}
        ant_actual = _lookup(antecedent.get("field"), record, resolved)
        if not _eval_predicate(antecedent.get("predicate"), ant_actual):
            continue  # antecedent does not hold -> rule not triggered
        con_actual = _lookup(consequent.get("field"), record, resolved)
        if _eval_predicate(consequent.get("expected"), con_actual):
            continue  # consequent satisfied -> silent
        msg = (
            f"{prefix}learned rule {rule_id!r} violated: when "
            f"{antecedent.get('field')!r} {antecedent.get('predicate')} then "
            f"{consequent.get('field')!r} must satisfy {consequent.get('expected')} "
            f"(got {con_actual!r}) [gamma.learned.{rule_id}]"
        )
        if str(rule.get("severity") or "fail").strip().lower() == "warn":
            warnings.append(msg)
        else:
            errors.append(msg)
    return (errors, warnings)


def predicate_hash(rule: dict[str, Any]) -> str:
    """Stable SHA-256 over the normalized antecedent + consequent + severity.

    The in-place-mutation guard: any silent edit to a pinned rule's semantics
    changes this hash and trips the manifest pin.
    """
    core = {
        "antecedent": rule.get("antecedent"),
        "consequent": rule.get("consequent"),
        "severity": rule.get("severity"),
    }
    normalized = json.dumps(core, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


# --- Observations ledger (append-only, digest-idempotent FILE store) ---------- #
def read_observations(ledger_path: str | Path) -> list[dict[str, Any]]:
    """Read all observations from the JSONL ledger; a missing ledger reads empty."""
    path = Path(ledger_path)
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        out.append(json.loads(stripped))
    return out


def append_observation(ledger_path: str | Path, observation: dict[str, Any]) -> bool:
    """Digest-keyed idempotent append. Returns True if written, False if a no-op.

    An observation whose ``output_digest`` already exists in the ledger is a NO-OP
    (returns False; the file is never rewritten or shrunk) — structurally append-
    only, so replaying observations is safe without a live fetch.
    """
    path = Path(ledger_path)
    digest = observation.get("output_digest")
    if not digest:
        raise ValueError("observation must carry a non-empty output_digest")
    existing = read_observations(path)
    if any(o.get("output_digest") == digest for o in existing):
        return False
    line = json.dumps(observation, sort_keys=True, separators=(",", ":"))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return True


# --- Identity-manifest pin ---------------------------------------------------- #
def load_manifest(lock_path: str | Path) -> list[dict[str, Any]]:
    """Load the sorted rule manifest (``rules`` list) from the lock file.

    A missing lock file reads as an empty manifest.
    """
    path = Path(lock_path)
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    rules = payload.get("rules") if isinstance(payload, dict) else None
    return list(rules) if isinstance(rules, list) else []


def check_manifest_pin(
    active_rules: list[dict[str, Any]],
    manifest: list[dict[str, Any]],
    *,
    repo_root: str | Path | None = None,
) -> list[str]:
    """Assert the active learned-rule set is pinned by the manifest. Returns errors.

    Enforces:
    * append-only SUPERSET — every manifested id must appear in the active set (a
      drop/rename of a manifested rule is RED);
    * every active rule MUST have a manifest row (an unpinned active rule is RED);
    * per-entry ``predicate_hash`` match (silent in-place mutation is RED);
    * every active rule's manifest ``fixture_path`` must exist on disk (anti-vacuous
      guard: an active rule must resolve to a committed RED-proven birthing fixture).

    All diagnostics are tagged ``gamma.learned.pin-violation``.
    """
    errors: list[str] = []
    active_by_id = {r.get("rule_id"): r for r in active_rules if isinstance(r, dict)}
    manifest_by_id = {m.get("rule_id"): m for m in manifest if isinstance(m, dict)}
    active_ids = set(active_by_id)
    manifest_ids = set(manifest_by_id)
    root = Path(repo_root) if repo_root is not None else PROJECT_ROOT

    for mid in sorted(manifest_ids - active_ids):
        errors.append(
            f"learned-rule manifest pin: manifested rule {mid!r} is missing from the "
            f"active learned_dependencies set (append-only superset violated; a drop "
            f"or rename) [{PIN_VIOLATION_TAG}]"
        )
    for aid in sorted(active_ids - manifest_ids):
        errors.append(
            f"learned-rule manifest pin: active learned rule {aid!r} has no manifest "
            f"row in gamma-learned-rules.lock (unpinned active rule) [{PIN_VIOLATION_TAG}]"
        )
    for rid in sorted(active_ids & manifest_ids):
        rule = active_by_id[rid]
        row = manifest_by_id[rid]
        actual_hash = predicate_hash(rule)
        pinned_hash = row.get("predicate_hash")
        if pinned_hash != actual_hash:
            errors.append(
                f"learned-rule manifest pin: rule {rid!r} predicate_hash {actual_hash!r} "
                f"!= pinned {pinned_hash!r} (in-place mutation of a pinned rule) "
                f"[{PIN_VIOLATION_TAG}]"
            )
        fixture_path = row.get("fixture_path")
        if not fixture_path:
            errors.append(
                f"learned-rule manifest pin: rule {rid!r} has no fixture_path (anti-"
                f"vacuous guard) [{PIN_VIOLATION_TAG}]"
            )
            continue
        fp = Path(fixture_path)
        if not fp.is_absolute():
            fp = root / fixture_path
        if not fp.exists():
            errors.append(
                f"learned-rule manifest pin: rule {rid!r} birthing fixture "
                f"{fixture_path!r} does not exist (anti-vacuous guard: an active rule "
                f"must resolve to a committed RED-proven fixture) [{PIN_VIOLATION_TAG}]"
            )
    return errors


def active_learned_rules(learned_dependencies: Any) -> list[dict[str, Any]]:
    """Normalize the top-level ``learned_dependencies`` block to a list of ACTIVE rules.

    Accepts a list of rule mappings or a mapping with a ``rules`` list; absent/empty
    resolves to ``[]``. Only ``status: active`` entries are returned.
    """
    if not learned_dependencies:
        return []
    if isinstance(learned_dependencies, dict):
        rules = learned_dependencies.get("rules") or []
    elif isinstance(learned_dependencies, list):
        rules = learned_dependencies
    else:
        return []
    return [
        r for r in rules if isinstance(r, dict) and r.get("status") == "active"
    ]
