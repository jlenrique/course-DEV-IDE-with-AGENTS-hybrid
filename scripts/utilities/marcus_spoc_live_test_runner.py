"""Delegated, test-only HIL driver for Marcus-SPOC workbook verification.

This utility does not remove or bypass HIL.  It exercises the production G0
confirmation callback and the production ``resume_production_trial`` seam with
real, card-bound :class:`OperatorVerdict` values.  Its authority is a narrow,
versioned policy approved for Epics 36--40 workbook live tests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from uuid import UUID, uuid4

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.composers.section_02a.directive_model import Directive  # noqa: E402
from app.gates.resume_api import compute_decision_card_digest  # noqa: E402
from app.marcus.cli.trial import start_trial  # noqa: E402
from app.marcus.lesson_plan.prework_artifact import (  # noqa: E402
    WORKBOOK_RUNTIME_CONTEXT_FILENAME,
    WorkbookBriefRuntimeContext,
)
from app.marcus.orchestrator.production_runner import (  # noqa: E402
    resume_production_trial,
)
from app.models.decision_cards import AnyDecisionCardAdapter  # noqa: E402
from app.models.runtime.production_trial_envelope import (  # noqa: E402
    ProductionTrialEnvelope,
)
from app.models.state.component_selection import ComponentSelection  # noqa: E402
from app.models.state.operator_verdict import OperatorVerdict  # noqa: E402

DELEGATE_ID = "codex_hil_runner"
POLICY_SCHEMA = "marcus-spoc-live-test-delegation.v1"
JOURNAL_SCHEMA = "marcus-spoc-live-test-hil-journal.v1"
SUMMARY_SCHEMA = "marcus-spoc-live-test-hil-summary.v1"
_SELECTION_FIELDS = {
    "G2B": "slide_variant_selections",
    "G4A": "selected_voice_id",
}
_TERMINAL_STATES = frozenset({"completed", "failed"})
_STOP_STATES = frozenset(
    {"paused-at-error", "waiting_for_provider_batch", "failed", "registered", "in-flight"}
)
_SECRET_KEY_FRAGMENTS = ("api_key", "password", "secret", "authorization", "credential")


class RunnerRefusal(RuntimeError):  # noqa: N818 - refusal is the domain term
    """Stable fail-closed refusal from the delegated runner."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class GateRule(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    action: Literal["approve", "select"]
    selection_field: Literal["slide_variant_selections", "selected_voice_id"] | None = None
    strategy: Literal["first_offered"] | None = None

    @model_validator(mode="after")
    def _validate_action(self) -> GateRule:
        if self.action == "approve" and (self.selection_field or self.strategy):
            raise ValueError("approve rules cannot carry selection configuration")
        if self.action == "select" and (
            self.selection_field is None or self.strategy != "first_offered"
        ):
            raise ValueError("select rules require a selection_field and first_offered strategy")
        return self


class DelegationScope(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    purpose: Literal["epics-36-40-workbook-live-verification"]
    epics: tuple[int, ...]
    customer_facing_approval: Literal[False] = False

    @field_validator("epics")
    @classmethod
    def _exact_workbook_epics(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        if value != (36, 37, 38, 39, 40):
            raise ValueError("delegation must be bound exactly to Epics 36-40")
        return value


class RunnerBudgets(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    max_gate_actions: int = Field(ge=1, le=32)
    max_wall_seconds: int = Field(ge=1, le=86_400)
    max_specialist_calls_per_segment: int = Field(ge=1, le=100)


class DelegationPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[POLICY_SCHEMA]
    delegate_id: Literal[DELEGATE_ID]
    approved_by: Literal["Juanl"]
    authority_spec: str = Field(min_length=1)
    scope: DelegationScope
    allowed_runs_roots: tuple[str, ...]
    allowed_input_roots: tuple[str, ...]
    allowed_evidence_root: str
    gate_rules: dict[str, GateRule]
    stop_states: tuple[str, ...]
    terminal_success_state: Literal["completed"]
    budgets: RunnerBudgets

    @model_validator(mode="after")
    def _closed_policy(self) -> DelegationPolicy:
        expected = {"G0E", "G0R", "G1", "G2B", "G2C", "G3", "G4", "G4A"}
        if set(self.gate_rules) != expected:
            raise ValueError("gate_rules must enumerate the exact production gate inventory")
        for gate, field in _SELECTION_FIELDS.items():
            rule = self.gate_rules[gate]
            if rule.action != "select" or rule.selection_field != field:
                raise ValueError(f"{gate} must use select with {field}")
        if any(self.gate_rules[g].action != "approve" for g in expected - set(_SELECTION_FIELDS)):
            raise ValueError("non-selection gates must be approve-only")
        if set(self.stop_states) != _STOP_STATES:
            raise ValueError("stop_states must enumerate every non-success stop class")
        if not self.allowed_runs_roots or not self.allowed_input_roots:
            raise ValueError("policy roots cannot be empty")
        return self


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _is_reparse_point(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return bool(getattr(info, "st_file_attributes", 0) & 0x400)


def _absolute_without_resolving(path: Path) -> Path:
    return Path(os.path.abspath(os.path.normpath(os.fspath(path))))


def _assert_safe_path(
    path: Path,
    *,
    root: Path,
    kind: Literal["file", "dir", "missing-ok"],
) -> Path:
    """Refuse escapes, symlinks/junctions, and unexpected file kinds."""
    if ".." in path.parts or ".." in root.parts:
        raise RunnerRefusal("parent-traversal-refused")
    absolute_root = _absolute_without_resolving(root)
    absolute = _absolute_without_resolving(path)
    try:
        relative = absolute.relative_to(absolute_root)
    except ValueError as exc:
        raise RunnerRefusal("path-outside-allowed-root") from exc
    current = absolute_root
    if absolute_root.exists() and (absolute_root.is_symlink() or _is_reparse_point(absolute_root)):
        raise RunnerRefusal("symlink-or-reparse-root-refused")
    for part in relative.parts:
        current /= part
        if current.exists() and (current.is_symlink() or _is_reparse_point(current)):
            raise RunnerRefusal("symlink-or-reparse-path-refused")
    if kind == "file":
        try:
            mode = absolute.lstat().st_mode
        except FileNotFoundError as exc:
            raise RunnerRefusal("required-file-missing") from exc
        if not stat.S_ISREG(mode):
            raise RunnerRefusal("non-regular-file-refused")
    elif kind == "dir":
        try:
            mode = absolute.lstat().st_mode
        except FileNotFoundError as exc:
            raise RunnerRefusal("required-directory-missing") from exc
        if not stat.S_ISDIR(mode):
            raise RunnerRefusal("non-directory-refused")
    elif absolute.exists():
        mode = absolute.lstat().st_mode
        if not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            raise RunnerRefusal("special-file-refused")
    return absolute


def _assert_safe_tree(root: Path) -> Path:
    """Recursively refuse links, reparse points, and special filesystem entries."""
    safe_root = _assert_safe_path(root, root=root, kind="dir")
    pending = [safe_root]
    while pending:
        directory = pending.pop()
        try:
            entries = list(os.scandir(directory))
        except OSError as exc:
            raise RunnerRefusal("source-tree-unreadable") from exc
        for entry in entries:
            path = Path(entry.path)
            if entry.is_symlink() or _is_reparse_point(path):
                raise RunnerRefusal("source-tree-link-refused")
            try:
                mode = path.lstat().st_mode
            except OSError as exc:
                raise RunnerRefusal("source-tree-entry-unreadable") from exc
            if stat.S_ISDIR(mode):
                pending.append(path)
            elif not stat.S_ISREG(mode):
                raise RunnerRefusal("source-tree-special-entry-refused")
    return safe_root


def _policy_path(raw: str) -> Path:
    return PROJECT_ROOT / raw


def _match_allowed_root(path: Path, roots: tuple[str, ...], *, kind: str) -> Path:
    for raw in roots:
        root = _policy_path(raw)
        try:
            return _assert_safe_path(path, root=root, kind=kind)  # type: ignore[arg-type]
        except RunnerRefusal as exc:
            if exc.code != "path-outside-allowed-root":
                raise
    raise RunnerRefusal("path-outside-policy-roots")


def _read_json(path: Path, *, root: Path) -> dict[str, Any]:
    safe = _assert_safe_path(path, root=root, kind="file")
    try:
        value = json.loads(safe.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RunnerRefusal("malformed-json") from exc
    if not isinstance(value, dict):
        raise RunnerRefusal("json-root-not-object")
    return value


def load_policy(path: Path) -> tuple[DelegationPolicy, str]:
    payload = _read_json(path, root=PROJECT_ROOT)
    try:
        policy = DelegationPolicy.model_validate(payload)
    except Exception as exc:  # pydantic errors must not leak untrusted content
        raise RunnerRefusal("invalid-delegation-policy") from exc
    expected_spec = PROJECT_ROOT / policy.authority_spec
    _assert_safe_path(expected_spec, root=PROJECT_ROOT, kind="file")
    if expected_spec.name != "spec-delegated-live-test-hil-runner.md":
        raise RunnerRefusal("wrong-delegation-authority")
    return policy, _digest(policy.model_dump(mode="json"))


def _reject_secret_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in _SECRET_KEY_FRAGMENTS):
                raise RunnerRefusal("secret-shaped-evidence-refused")
            _reject_secret_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            _reject_secret_keys(nested)


def _atomic_write_json(path: Path, payload: dict[str, Any], *, root: Path) -> None:
    _reject_secret_keys(payload)
    absolute = _assert_safe_path(path, root=root, kind="missing-ok")
    parent = absolute.parent
    parent.mkdir(parents=True, exist_ok=True)
    _assert_safe_path(parent, root=root, kind="dir")
    if absolute.exists():
        _assert_safe_path(absolute, root=root, kind="file")
    temp = parent / f".{absolute.name}.{uuid4().hex}.tmp"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(temp, flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, absolute)
    finally:
        if temp.exists():
            temp.unlink()


def _write_once_json(path: Path, payload: dict[str, Any], *, root: Path) -> None:
    if path.exists():
        existing = _read_json(path, root=root)
        if existing != payload:
            raise RunnerRefusal("immutable-summary-already-exists")
        return
    _atomic_write_json(path, payload, root=root)


class EvidenceJournal:
    def __init__(
        self,
        *,
        trial_id: UUID,
        policy_digest: str,
        evidence_root: Path,
    ) -> None:
        self.trial_id = trial_id
        self.policy_digest = policy_digest
        self.root = evidence_root
        self.directory = evidence_root / str(trial_id)
        self.path = self.directory / "journal.json"
        self.summary_path = self.directory / "summary.json"
        if self.path.exists():
            self.payload = _read_json(self.path, root=evidence_root)
            if (
                self.payload.get("schema_version") != JOURNAL_SCHEMA
                or self.payload.get("trial_id") != str(trial_id)
                or self.payload.get("delegate_id") != DELEGATE_ID
                or self.payload.get("policy_digest") != policy_digest
                or not isinstance(self.payload.get("events"), list)
            ):
                raise RunnerRefusal("journal-binding-mismatch")
        else:
            self.payload = {
                "schema_version": JOURNAL_SCHEMA,
                "trial_id": str(trial_id),
                "delegate_id": DELEGATE_ID,
                "policy_digest": policy_digest,
                "created_at": _utc_now(),
                "events": [],
            }
            self._persist()

    @property
    def events(self) -> list[dict[str, Any]]:
        return self.payload["events"]

    def append(self, kind: str, **fields: Any) -> None:
        self.events.append(
            {
                "sequence": len(self.events) + 1,
                "at": _utc_now(),
                "kind": kind,
                **fields,
            }
        )
        self._persist()

    def _persist(self) -> None:
        _atomic_write_json(self.path, self.payload, root=self.root)

    def submitted_digests(self) -> set[str]:
        return {
            str(event["decision_card_digest"])
            for event in self.events
            if event.get("kind") == "submission-started" and event.get("decision_card_digest")
        }

    def pending_submission(self) -> dict[str, Any] | None:
        completed = {
            event.get("decision_card_digest")
            for event in self.events
            if event.get("kind") in {"transition-recorded", "submission-reconciled"}
        }
        for event in reversed(self.events):
            if (
                event.get("kind") == "submission-started"
                and event.get("decision_card_digest") not in completed
            ):
                return event
        return None

    def finalize(self, *, status: str, success: bool, reason: str, actions: int) -> dict[str, Any]:
        base = {
            "schema_version": SUMMARY_SCHEMA,
            "trial_id": str(self.trial_id),
            "delegate_id": DELEGATE_ID,
            "policy_digest": self.policy_digest,
            "status": status,
            "success": success,
            "reason": reason,
            "gate_actions": actions,
            "journal_path": self.path.as_posix(),
            "finished_at": _utc_now(),
        }
        summary_path = self.summary_path
        if summary_path.exists():
            existing = _read_json(summary_path, root=self.root)
            stable_keys = ("trial_id", "policy_digest", "status", "success", "reason")
            if all(existing.get(key) == base.get(key) for key in stable_keys):
                return existing
            index = 2
            while (self.directory / f"summary-{index:03d}.json").exists():
                index += 1
            summary_path = self.directory / f"summary-{index:03d}.json"
        summary = {**base, "summary_path": summary_path.as_posix()}
        _write_once_json(summary_path, summary, root=self.root)
        return summary


@contextmanager
def exclusive_trial_lock(run_dir: Path, *, trial_id: UUID, policy_digest: str) -> Iterator[None]:
    lock = run_dir / ".codex-hil-runner.lock"
    _assert_safe_path(run_dir, root=run_dir.parent, kind="dir")
    if lock.exists() and (lock.is_symlink() or _is_reparse_point(lock)):
        raise RunnerRefusal("unsafe-trial-lock")
    try:
        descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise RunnerRefusal("trial-lock-held") from exc
    try:
        body = {
            "trial_id": str(trial_id),
            "delegate_id": DELEGATE_ID,
            "policy_digest": policy_digest,
            "pid": os.getpid(),
            "acquired_at": _utc_now(),
        }
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(body, handle, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        yield
    finally:
        try:
            current = _read_json(lock, root=run_dir)
            if (
                current.get("trial_id") != str(trial_id)
                or current.get("policy_digest") != policy_digest
            ):
                raise RunnerRefusal("trial-lock-mutated")
            lock.unlink()
        except FileNotFoundError as exc:
            raise RunnerRefusal("trial-lock-disappeared") from exc


def _load_envelope(trial_id: UUID, run_dir: Path) -> ProductionTrialEnvelope:
    payload = _read_json(run_dir / "run.json", root=run_dir)
    try:
        envelope = ProductionTrialEnvelope.model_validate_json(
            json.dumps(payload), context={"invariant_mode": "strict"}
        )
    except Exception as exc:
        raise RunnerRefusal("invalid-run-envelope") from exc
    if envelope.trial_id != trial_id:
        raise RunnerRefusal("trial-envelope-id-mismatch")
    return envelope


def _assert_workbook_checkpoint(trial_id: UUID, run_dir: Path) -> None:
    checkpoint = _read_json(run_dir / "checkpoint.json", root=run_dir)
    if checkpoint.get("trial_id") != str(trial_id):
        raise RunnerRefusal("checkpoint-trial-mismatch")
    run_state = checkpoint.get("run_state")
    selection = run_state.get("component_selection") if isinstance(run_state, dict) else None
    if not isinstance(selection, dict) or selection.get("workbook") is not True:
        raise RunnerRefusal("trial-not-workbook-scoped")


def _load_canonical_runtime_context(run_dir: Path) -> WorkbookBriefRuntimeContext:
    raw = _read_json(run_dir / WORKBOOK_RUNTIME_CONTEXT_FILENAME, root=run_dir)
    if raw.pop("schema_version", None) != "workbook-runtime-context.v1":
        raise RunnerRefusal("workbook-runtime-context-invalid")
    raw["run_dir"] = run_dir
    if raw.get("course_source_root") is not None:
        raw["course_source_root"] = Path(raw["course_source_root"])
    try:
        return WorkbookBriefRuntimeContext.model_validate(raw, strict=True)
    except (TypeError, ValueError) as exc:
        raise RunnerRefusal("workbook-runtime-context-invalid") from exc


def _assert_delegated_trial_scope(
    *,
    trial_id: UUID,
    envelope: ProductionTrialEnvelope,
    run_dir: Path,
    policy: DelegationPolicy,
) -> None:
    """Bind an attachment to a delegated production workbook test trial."""
    if envelope.preset != "production":
        raise RunnerRefusal("trial-preset-out-of-scope")
    if envelope.operator_id != DELEGATE_ID:
        raise RunnerRefusal("trial-operator-not-delegate")
    corpus = _match_allowed_root(
        Path(envelope.corpus_path), policy.allowed_input_roots, kind="dir"
    )
    _assert_safe_tree(corpus)
    _assert_workbook_checkpoint(trial_id, run_dir)
    context = _load_canonical_runtime_context(run_dir)
    if context.course_source_root is None:
        raise RunnerRefusal("course-source-root-missing")
    course_root = _match_allowed_root(
        context.course_source_root, policy.allowed_input_roots, kind="dir"
    )
    _assert_safe_tree(course_root)


def _load_bound_card(trial_id: UUID, gate_id: str, run_dir: Path) -> tuple[Any, str, str]:
    path = run_dir / f"decision-card-{gate_id}.json"
    raw = _assert_safe_path(path, root=run_dir, kind="file").read_bytes()
    file_digest = hashlib.sha256(raw).hexdigest()
    try:
        payload = json.loads(raw.decode("utf-8"))
        card = AnyDecisionCardAdapter.validate_python(payload["card"])
        issued_at = datetime.fromisoformat(str(payload["issued_at"]).replace("Z", "+00:00"))
        nonce = str(payload["server_nonce"])
        persisted_digest = str(payload["digest"])
    except Exception as exc:
        raise RunnerRefusal("malformed-decision-card") from exc
    if card.trial_id != trial_id or card.gate_id != gate_id:
        raise RunnerRefusal("decision-card-identity-mismatch")
    if not nonce or len(persisted_digest) != 64:
        raise RunnerRefusal("decision-card-metadata-missing")
    expected = compute_decision_card_digest(
        card=card,
        trial_id=trial_id,
        issuance_timestamp=issued_at,
        server_nonce=nonce,
    )
    if expected != persisted_digest:
        raise RunnerRefusal("decision-card-digest-mismatch")
    checkpoint = _read_json(run_dir / "checkpoint.json", root=run_dir)
    if checkpoint.get("trial_id") != str(trial_id) or checkpoint.get("gate_id") != gate_id:
        raise RunnerRefusal("checkpoint-card-mismatch")
    checkpoint_path = Path(str(payload.get("checkpoint_path") or ""))
    if ".." in checkpoint_path.parts:
        raise RunnerRefusal("parent-traversal-refused")
    if _absolute_without_resolving(checkpoint_path) != _absolute_without_resolving(
        run_dir / "checkpoint.json"
    ):
        raise RunnerRefusal("decision-card-checkpoint-path-mismatch")
    return card, persisted_digest, file_digest


def _make_verdict(
    *,
    policy: DelegationPolicy,
    trial_id: UUID,
    gate_id: str,
    card: Any,
    card_digest: str,
) -> tuple[OperatorVerdict, Any | None]:
    rule = policy.gate_rules.get(gate_id)
    if rule is None:
        raise RunnerRefusal("unknown-gate")
    kwargs: dict[str, Any] = {
        "trial_id": trial_id,
        "gate_id": gate_id,
        "card_id": card.card_id,
        "operator_id": DELEGATE_ID,
        "decision_card_digest": card_digest,
    }
    selection_receipt: Any | None = None
    if rule.action == "approve":
        kwargs["verb"] = "approve"
    else:
        expected_field = _SELECTION_FIELDS.get(gate_id)
        if rule.selection_field != expected_field or expected_field is None:
            raise RunnerRefusal("selection-policy-gate-mismatch")
        if gate_id == "G2B":
            offered = getattr(card, "variant_candidates", None)
            if (
                not isinstance(offered, list)
                or not offered
                or any(not isinstance(item, str) or not item.strip() for item in offered)
                or len(set(offered)) != len(offered)
            ):
                raise RunnerRefusal("missing-or-ambiguous-selection-choices")
            offered_set = set(offered)
            contexts = [
                row
                for row in getattr(card, "pick_context", [])
                if isinstance(row, dict) and row.get("kind") == "variant-options"
            ]
            if len(contexts) != 1 or not isinstance(contexts[0].get("slides"), list):
                raise RunnerRefusal("missing-or-ambiguous-selection-choices")
            selections: dict[str, str] = {}
            for slide in contexts[0]["slides"]:
                if not isinstance(slide, dict):
                    raise RunnerRefusal("missing-or-ambiguous-selection-choices")
                slide_id = slide.get("slide_id")
                variants = slide.get("variants")
                if (
                    not isinstance(slide_id, str)
                    or not slide_id.strip()
                    or slide_id in selections
                    or not isinstance(variants, list)
                    or not variants
                ):
                    raise RunnerRefusal("missing-or-ambiguous-selection-choices")
                variant_ids = [
                    row.get("variant") if isinstance(row, dict) else None
                    for row in variants
                ]
                if (
                    any(not isinstance(item, str) or not item.strip() for item in variant_ids)
                    or len(set(variant_ids)) != len(variant_ids)
                    or any(item not in offered_set for item in variant_ids)
                ):
                    raise RunnerRefusal("missing-or-ambiguous-selection-choices")
                selections[slide_id] = variant_ids[0]
            if not selections:
                raise RunnerRefusal("missing-or-ambiguous-selection-choices")
            selection_receipt = selections
        else:
            candidates = getattr(card, "voice_candidates", None)
            if (
                not isinstance(candidates, list)
                or not candidates
                or any(not isinstance(item, str) or not item.strip() for item in candidates)
                or len(set(candidates)) != len(candidates)
            ):
                raise RunnerRefusal("missing-or-ambiguous-selection-choices")
            selection_receipt = candidates[0]
        kwargs.update(
            verb="select", edit_payload={expected_field: selection_receipt}
        )
    try:
        return OperatorVerdict(**kwargs), selection_receipt
    except Exception as exc:
        raise RunnerRefusal("delegated-verdict-invalid") from exc


def _reconcile_pending(
    journal: EvidenceJournal,
    envelope: ProductionTrialEnvelope,
    run_dir: Path,
) -> None:
    pending = journal.pending_submission()
    if pending is None:
        return
    if envelope.status == "paused-at-gate" and envelope.paused_gate == pending.get("gate_id"):
        _, current_digest, _ = _load_bound_card(
            envelope.trial_id, str(envelope.paused_gate), run_dir
        )
        if current_digest == pending.get("decision_card_digest"):
            raise RunnerRefusal("split-brain-consumed-card-still-current")
    journal.append(
        "submission-reconciled",
        decision_card_digest=pending["decision_card_digest"],
        observed_status=envelope.status,
        observed_gate=envelope.paused_gate,
    )


def _check_deadline(started_at: float, policy: DelegationPolicy) -> None:
    if time.monotonic() - started_at >= policy.budgets.max_wall_seconds:
        raise RunnerRefusal("wall-clock-budget-exhausted")


def _authoritative_resume_result(
    *,
    trial_id: UUID,
    run_dir: Path,
    returned: ProductionTrialEnvelope,
) -> ProductionTrialEnvelope:
    if not isinstance(returned, ProductionTrialEnvelope):
        raise RunnerRefusal("resume-return-envelope-invalid")
    persisted = _load_envelope(trial_id, run_dir)
    if returned.trial_id != trial_id:
        raise RunnerRefusal("resume-return-trial-mismatch")
    if returned.model_dump(mode="json") != persisted.model_dump(mode="json"):
        raise RunnerRefusal("resume-return-disk-mismatch")
    return persisted


def _drive_paused_trial_impl(
    *,
    trial_id: UUID,
    runs_root: Path,
    policy: DelegationPolicy,
    policy_digest: str,
    evidence_root: Path,
    resume_fn: Callable[..., ProductionTrialEnvelope] = resume_production_trial,
    started_at: float,
) -> dict[str, Any]:
    run_dir = runs_root / str(trial_id)
    journal = EvidenceJournal(
        trial_id=trial_id, policy_digest=policy_digest, evidence_root=evidence_root
    )
    actions = sum(event.get("kind") == "submission-started" for event in journal.events)
    envelope = _load_envelope(trial_id, run_dir)
    _assert_delegated_trial_scope(
        trial_id=trial_id,
        envelope=envelope,
        run_dir=run_dir,
        policy=policy,
    )
    _reconcile_pending(journal, envelope, run_dir)
    while True:
        _check_deadline(started_at, policy)
        if envelope.status == policy.terminal_success_state:
            envelope = _load_envelope(trial_id, run_dir)
            _assert_delegated_trial_scope(
                trial_id=trial_id,
                envelope=envelope,
                run_dir=run_dir,
                policy=policy,
            )
            _check_deadline(started_at, policy)
            if envelope.status != policy.terminal_success_state:
                raise RunnerRefusal("terminal-state-changed-before-success")
            return journal.finalize(
                status=envelope.status, success=True, reason="completed", actions=actions
            )
        if envelope.status in policy.stop_states:
            return journal.finalize(
                status=envelope.status,
                success=False,
                reason=f"stopped-{envelope.status}",
                actions=actions,
            )
        if envelope.status != "paused-at-gate" or envelope.paused_gate is None:
            raise RunnerRefusal("unknown-run-state")
        if actions >= policy.budgets.max_gate_actions:
            raise RunnerRefusal("gate-action-budget-exhausted")
        gate_id = str(envelope.paused_gate)
        card, card_digest, card_file_digest = _load_bound_card(trial_id, gate_id, run_dir)
        if card_digest in journal.submitted_digests():
            raise RunnerRefusal("decision-card-replay-refused")
        verdict, selection_id = _make_verdict(
            policy=policy,
            trial_id=trial_id,
            gate_id=gate_id,
            card=card,
            card_digest=card_digest,
        )
        # Re-read both authority surfaces immediately before the one engine call.
        current = _load_envelope(trial_id, run_dir)
        _assert_delegated_trial_scope(
            trial_id=trial_id,
            envelope=current,
            run_dir=run_dir,
            policy=policy,
        )
        if current.status != "paused-at-gate" or current.paused_gate != gate_id:
            raise RunnerRefusal("stale-run-state-before-submit")
        _, rebound_digest, rebound_file_digest = _load_bound_card(trial_id, gate_id, run_dir)
        if rebound_digest != card_digest or rebound_file_digest != card_file_digest:
            raise RunnerRefusal("decision-card-mutated-before-submit")
        final_current = _load_envelope(trial_id, run_dir)
        _assert_delegated_trial_scope(
            trial_id=trial_id,
            envelope=final_current,
            run_dir=run_dir,
            policy=policy,
        )
        if (
            final_current.status != "paused-at-gate"
            or final_current.paused_gate != gate_id
        ):
            raise RunnerRefusal("stale-run-state-before-submit")
        _check_deadline(started_at, policy)
        journal.append(
            "submission-started",
            gate_id=gate_id,
            card_id=str(card.card_id),
            decision_card_digest=card_digest,
            verdict_id=str(verdict.verdict_id),
            verb=verdict.verb,
            selection_id=selection_id,
        )
        actions += 1
        returned = resume_fn(
            trial_id=trial_id,
            verdict=verdict,
            runs_root=runs_root,
            max_specialist_calls=policy.budgets.max_specialist_calls_per_segment,
        )
        _check_deadline(started_at, policy)
        envelope = _authoritative_resume_result(
            trial_id=trial_id,
            run_dir=run_dir,
            returned=returned,
        )
        _assert_delegated_trial_scope(
            trial_id=trial_id,
            envelope=envelope,
            run_dir=run_dir,
            policy=policy,
        )
        journal.append(
            "transition-recorded",
            decision_card_digest=card_digest,
            resulting_status=envelope.status,
            resulting_gate=envelope.paused_gate,
        )


def _drive_with_evidence_handling(
    *,
    trial_id: UUID,
    runs_root: Path,
    policy: DelegationPolicy,
    policy_digest: str,
    evidence_root: Path,
    resume_fn: Callable[..., ProductionTrialEnvelope] = resume_production_trial,
    started_at: float,
) -> dict[str, Any]:
    """Drive one attached trial and persist a summary for every refusal."""
    try:
        return _drive_paused_trial_impl(
            trial_id=trial_id,
            runs_root=runs_root,
            policy=policy,
            policy_digest=policy_digest,
            evidence_root=evidence_root,
            resume_fn=resume_fn,
            started_at=started_at,
        )
    except RunnerRefusal as exc:
        journal = EvidenceJournal(
            trial_id=trial_id,
            policy_digest=policy_digest,
            evidence_root=evidence_root,
        )
        actions = sum(
            event.get("kind") == "submission-started" for event in journal.events
        )
        journal.append("runner-refused", reason=exc.code)
        journal.finalize(
            status="refused",
            success=False,
            reason=exc.code,
            actions=actions,
        )
        raise
    except Exception as exc:
        journal = EvidenceJournal(
            trial_id=trial_id,
            policy_digest=policy_digest,
            evidence_root=evidence_root,
        )
        actions = sum(
            event.get("kind") == "submission-started" for event in journal.events
        )
        journal.append(
            "runner-refused",
            reason="engine-call-failed",
            error_type=type(exc).__name__,
        )
        journal.finalize(
            status="refused",
            success=False,
            reason="engine-call-failed",
            actions=actions,
        )
        raise RunnerRefusal("engine-call-failed") from exc


def _validate_public_roots(
    *,
    policy: DelegationPolicy,
    runs_root: Path,
    evidence_root: Path,
) -> tuple[Path, Path]:
    if ".." in evidence_root.parts:
        raise RunnerRefusal("parent-traversal-refused")
    if ".." in Path(policy.allowed_evidence_root).parts:
        raise RunnerRefusal("parent-traversal-refused")
    safe_runs_root = _match_allowed_root(
        runs_root, policy.allowed_runs_roots, kind="dir"
    )
    expected_evidence = _absolute_without_resolving(
        _policy_path(policy.allowed_evidence_root)
    )
    candidate_evidence = _absolute_without_resolving(evidence_root)
    if candidate_evidence != expected_evidence:
        raise RunnerRefusal("evidence-root-policy-mismatch")
    # Validate containment and every existing component before creating anything.
    safe_evidence = _assert_safe_path(
        candidate_evidence, root=PROJECT_ROOT, kind="missing-ok"
    )
    safe_evidence.mkdir(parents=True, exist_ok=True)
    _assert_safe_path(safe_evidence, root=PROJECT_ROOT, kind="dir")
    return safe_runs_root, safe_evidence


def _validate_policy_digest(policy: DelegationPolicy, policy_digest: str) -> None:
    expected = _digest(policy.model_dump(mode="json"))
    if policy_digest != expected:
        raise RunnerRefusal("policy-digest-mismatch")


def drive_paused_trial(
    *,
    trial_id: UUID,
    runs_root: Path,
    policy: DelegationPolicy,
    policy_digest: str,
    evidence_root: Path,
    resume_fn: Callable[..., ProductionTrialEnvelope] = resume_production_trial,
    started_at: float | None = None,
) -> dict[str, Any]:
    """Public attach entry: validate policy roots, lock, scope, then drive."""
    clock_start = time.monotonic() if started_at is None else started_at
    _validate_policy_digest(policy, policy_digest)
    safe_runs_root, safe_evidence = _validate_public_roots(
        policy=policy, runs_root=runs_root, evidence_root=evidence_root
    )
    _check_deadline(clock_start, policy)
    run_dir = _assert_safe_path(
        safe_runs_root / str(trial_id), root=safe_runs_root, kind="dir"
    )
    with exclusive_trial_lock(
        run_dir, trial_id=trial_id, policy_digest=policy_digest
    ):
        return _drive_with_evidence_handling(
            trial_id=trial_id,
            runs_root=safe_runs_root,
            policy=policy,
            policy_digest=policy_digest,
            evidence_root=safe_evidence,
            resume_fn=resume_fn,
            started_at=clock_start,
        )


def _directive_confirmation(
    *,
    trial_id: UUID,
    input_path: Path,
    run_dir: Path,
    journal: EvidenceJournal,
) -> Callable[..., Literal["confirmed"]]:
    def confirm(
        *, directive_path: Path, auto_confirm_directive: bool
    ) -> Literal["confirmed"]:
        if auto_confirm_directive:
            raise RunnerRefusal("g0-auto-confirm-bypass-refused")
        safe = _assert_safe_path(directive_path, root=run_dir, kind="file")
        try:
            before = safe.lstat()
            raw = safe.read_bytes()
            after = safe.lstat()
            stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
            if any(getattr(before, name) != getattr(after, name) for name in stable_fields):
                raise RunnerRefusal("g0-directive-mutated-during-review")
            payload = yaml.safe_load(raw.decode("utf-8"))
            directive = Directive.model_validate(payload)
        except RunnerRefusal:
            raise
        except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
            raise RunnerRefusal("g0-directive-malformed") from exc
        if directive.run_id != trial_id:
            raise RunnerRefusal("g0-directive-trial-mismatch")
        corpus = Path(directive.corpus_dir)
        if ".." in corpus.parts:
            raise RunnerRefusal("parent-traversal-refused")
        if _absolute_without_resolving(corpus) != _absolute_without_resolving(input_path):
            raise RunnerRefusal("g0-directive-corpus-mismatch")
        journal.append(
            "g0-directive-confirmed",
            directive_path=safe.relative_to(_absolute_without_resolving(run_dir)).as_posix(),
            directive_digest=hashlib.sha256(raw).hexdigest(),
        )
        return "confirmed"

    return confirm


def _start_and_drive_core(
    *,
    trial_id: UUID,
    input_path: Path,
    runs_root: Path,
    policy: DelegationPolicy,
    policy_digest: str,
    evidence_root: Path,
    course_source_root: Path,
    encounter_mode: Literal["recorded", "live"],
    started_at: float,
) -> dict[str, Any]:
    run_dir = runs_root / str(trial_id)
    journal = EvidenceJournal(
        trial_id=trial_id, policy_digest=policy_digest, evidence_root=evidence_root
    )
    try:
        _check_deadline(started_at, policy)
        start_result = start_trial(
            preset="production",
            input_path=input_path,
            operator_id=DELEGATE_ID,
            trial_id=trial_id,
            runs_root=runs_root,
            auto_confirm_directive=False,
            confirm_fn=_directive_confirmation(
                trial_id=trial_id,
                input_path=input_path,
                run_dir=run_dir,
                journal=journal,
            ),
            max_specialist_calls=policy.budgets.max_specialist_calls_per_segment,
            component_selection=ComponentSelection(deck=True, motion=False, workbook=True),
            hud="off",
            course_source_root=course_source_root,
            encounter_mode=encounter_mode,
        )
        _check_deadline(started_at, policy)
    except Exception as exc:
        reason = exc.code if isinstance(exc, RunnerRefusal) else "start-failed"
        journal.append(
            "start-refused",
            reason=reason,
            error_type=type(exc).__name__,
        )
        journal.finalize(status="refused", success=False, reason=reason, actions=0)
        if isinstance(exc, RunnerRefusal):
            raise
        raise RunnerRefusal("start-failed") from exc
    journal.append("start-returned", status=str(start_result.get("status")))
    return _drive_with_evidence_handling(
        trial_id=trial_id,
        runs_root=runs_root,
        policy=policy,
        policy_digest=policy_digest,
        evidence_root=evidence_root,
        started_at=started_at,
    )


def start_and_drive_trial(
    *,
    trial_id: UUID,
    input_path: Path,
    course_source_root: Path,
    encounter_mode: Literal["recorded", "live"],
    runs_root: Path,
    policy: DelegationPolicy,
    policy_digest: str,
    evidence_root: Path,
    started_at: float | None = None,
) -> dict[str, Any]:
    """Public start entry: validate all roots, reserve trial, lock, then start."""
    clock_start = time.monotonic() if started_at is None else started_at
    _validate_policy_digest(policy, policy_digest)
    if encounter_mode not in {"recorded", "live"}:
        raise RunnerRefusal("encounter-mode-invalid")
    safe_runs_root, safe_evidence = _validate_public_roots(
        policy=policy, runs_root=runs_root, evidence_root=evidence_root
    )
    safe_input = _match_allowed_root(
        input_path, policy.allowed_input_roots, kind="dir"
    )
    safe_course_root = _match_allowed_root(
        course_source_root, policy.allowed_input_roots, kind="dir"
    )
    _assert_safe_tree(safe_input)
    _assert_safe_tree(safe_course_root)
    _check_deadline(clock_start, policy)
    run_dir = safe_runs_root / str(trial_id)
    try:
        run_dir.mkdir()
    except FileExistsError as exc:
        raise RunnerRefusal("trial-already-exists") from exc
    with exclusive_trial_lock(
        run_dir, trial_id=trial_id, policy_digest=policy_digest
    ):
        return _start_and_drive_core(
            trial_id=trial_id,
            input_path=safe_input,
            runs_root=safe_runs_root,
            policy=policy,
            policy_digest=policy_digest,
            evidence_root=safe_evidence,
            course_source_root=safe_course_root,
            encounter_mode=encounter_mode,
            started_at=clock_start,
        )


def run(
    *,
    mode: Literal["attach", "start"],
    trial_id: UUID,
    policy_path: Path,
    runs_root: Path,
    evidence_root: Path,
    input_path: Path | None = None,
    course_source_root: Path | None = None,
    encounter_mode: Literal["recorded", "live"] | None = None,
) -> dict[str, Any]:
    if mode not in {"attach", "start"}:
        raise RunnerRefusal("unknown-runner-mode")
    started_at = time.monotonic()
    policy, policy_digest = load_policy(policy_path)
    if mode == "start":
        if input_path is None or course_source_root is None or encounter_mode is None:
            raise RunnerRefusal("start-workbook-context-required")
        return start_and_drive_trial(
            trial_id=trial_id,
            input_path=input_path,
            course_source_root=course_source_root,
            encounter_mode=encounter_mode,
            runs_root=runs_root,
            policy=policy,
            policy_digest=policy_digest,
            evidence_root=evidence_root,
            started_at=started_at,
        )
    return drive_paused_trial(
        trial_id=trial_id,
        runs_root=runs_root,
        policy=policy,
        policy_digest=policy_digest,
        evidence_root=evidence_root,
        started_at=started_at,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("attach", "start"))
    parser.add_argument("--trial-id", type=UUID, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--course-source-root", type=Path)
    parser.add_argument("--encounter-mode", choices=("recorded", "live"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        summary = run(
            mode=args.mode,
            trial_id=args.trial_id,
            policy_path=args.policy,
            runs_root=args.runs_root,
            evidence_root=args.evidence_root,
            input_path=args.input,
            course_source_root=args.course_source_root,
            encounter_mode=args.encounter_mode,
        )
    except RunnerRefusal as exc:
        print(json.dumps({"status": "refused", "reason": exc.code}, sort_keys=True))
        return 2
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
