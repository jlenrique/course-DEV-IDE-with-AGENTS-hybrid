"""Story Q1.2 — per-criterion signal readers + the signal→level derivation.

These readers surface honest FACTS for the DID criteria so a human cannot hand-score
what the code can observe. The load-bearing lesson from the post-review honesty
rework: **a signal is named for what it measures, and a level is NEVER mechanically
awarded a clean/strong value from a proxy, unverified, unknown, or malformed signal.**

Which criteria are actually mechanical:
  * **C3 fence-enforcement** IS purely mechanical — the three gates are env-toggle
    default-OFF and the production preset sets none of their env keys, so the
    production-preset posture is all-OFF *independent of the caller's shell*
    (:func:`fences_enabled_signal` clears the ambient fence env before reading the
    gate functions). Derives to ``weak`` today.
  * **C2 bone-determinism** is NOT purely mechanical: ``model_config_ref``-nullness is
    a *determinism proxy*, not proof (Irene Pass-2 id ``08`` is an LLM with a null
    ref; Pass-1 gate nodes are LLM with null refs). The signal is therefore named for
    the config-ref fact it truly measures, and :func:`level_from_signal` can only
    *downgrade* on a detected boundary breach — it never awards ``strong``. The
    ``strong`` in the machine block is a documented human JUDGMENT (§1.6 basis).
  * **C4 lock+contract** is NOT purely mechanical: runtime bypass detection is
    honestly ``"undetected"`` today, and ``digest_module_present_on_disk`` is only a
    file-existence fact (NOT proof the digest is runtime-wired). ``"undetected"`` /
    unknown / malformed can never award a clean level; only a real detector-observed
    ``int == 0`` may reach the capped ``strong``. The machine-block ``strong`` is a
    documented human JUDGMENT (§1.6 basis).

Design contract — **fail-soft and read-only, per field**: every reader NEVER raises;
on any failure it degrades *that field* to an honest marker, never a false-clean value.

GL-3 clean-leaf invariant: this module imports **zero** ``app.*`` at MODULE scope.
Manifest / deferred-inventory reads are plain ``yaml``/stdlib file reads; the three
fence gate functions are reached ONLY via deferred local imports inside the reader.
"""

from __future__ import annotations

import io
import json
import os
import re
import threading
from collections.abc import Mapping
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path
from types import MappingProxyType
from typing import Any

import yaml

_MANIFEST_REL = "state/config/pipeline-manifest.yaml"
_DEFERRED_INVENTORY_REL = "_bmad-output/planning-artifacts/deferred-inventory.md"
#: Compile-time content-addressed digest substrate (Composition-catalog S2). Its
#: presence on disk is a NECESSARY-not-sufficient fact for C4 — file-existence only,
#: NOT proof the digest is runtime-wired. Read without importing ``app``.
_DIGEST_MODULE_REL = "app/runtime/compiled_graph_digest.py"

#: The three fence env toggles. The production preset sets NONE of these, so the
#: production-preset posture is read by clearing them (env-independence, REWORK-3).
_FENCE_ENV_KEYS: tuple[str, ...] = (
    "MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE",
    "MARCUS_COVERAGE_GATE_ACTIVE",
    "MARCUS_UDAC_ACTIVE",
)

#: ``did_leak:`` tag, anchored to line start (optional list/quote/whitespace prefix)
#: so a mid-line prose mention does not inflate the count (REWORK-4.6). 5 tags today,
#: all in the fixed ``## DID Scorecard Leak Registry`` section (Q1.5).
_DID_LEAK_LINE_RE = re.compile(r"(?m)^[\s>]*(?:[-*+]\s+)?did_leak:")
_FENCE_LINE_RE = re.compile(r"^\s*```")
#: ``<!-- ... -->`` HTML-comment span (non-greedy, DOTALL for multi-line). Stripped
#: before counting so a tag commented-out to temporarily disable it (a whole
#: ``<!-- did_leak: x -->`` line) does NOT count, while a harmless inline trailing
#: comment on a real tag line is removed leaving the tag (FIX-7).
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

_MISSING = object()


def _repo_root() -> Path:
    # app/quality/signals.py -> app/quality -> app -> <repo root>
    return Path(__file__).resolve().parents[2]


# ============================ C3 — fence enforcement ============================


@contextmanager
def _production_preset_env():
    """Temporarily clear the fence env toggles so a gate read reflects the
    **production-preset posture** (the preset sets none of them), independent of the
    caller's ambient shell. Restores the prior environment unconditionally.
    """
    saved = {k: os.environ.get(k) for k in _FENCE_ENV_KEYS}
    try:
        for k in _FENCE_ENV_KEYS:
            os.environ.pop(k, None)
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def fences_enabled_signal() -> dict[str, Any]:
    """C3 — is each fence wired ON under ``--preset production``?

    Env-INDEPENDENT (REWORK-3): the gate functions are read inside
    :func:`_production_preset_env`, so a polluted ambient shell (a dev with
    ``MARCUS_UDAC_ACTIVE=1`` exported) cannot change the reported posture. Because the
    gates are default-OFF env-toggles and the preset sets none of their keys, the
    honest posture today is all-``False``. Each gate is reached by a deferred local
    import (GL-3) and read independently; a raising gate or a non-``bool`` return
    degrades exactly that field to ``"unavailable"`` (never silently ``bool()``-coerced
    — a ``None``→``False`` would report a fence definitely-OFF when it is unknown).
    """
    with _production_preset_env():
        fidelity: bool | str
        try:
            from app.specialists.irene.graph import narration_figure_fidelity_active

            _v = narration_figure_fidelity_active()
            fidelity = _v if isinstance(_v, bool) else "unavailable"
        except Exception:  # noqa: BLE001 — a fence read must never raise into a caller
            fidelity = "unavailable"

        coverage: bool | str
        try:
            from app.marcus.orchestrator.coverage_gate_wiring import (
                coverage_gate_active,
            )

            _v = coverage_gate_active()
            coverage = _v if isinstance(_v, bool) else "unavailable"
        except Exception:  # noqa: BLE001
            coverage = "unavailable"

        udac: bool | str
        try:
            from app.marcus.orchestrator.udac_wiring import udac_active

            _v = udac_active()
            udac = _v if isinstance(_v, bool) else "unavailable"
        except Exception:  # noqa: BLE001
            udac = "unavailable"

    return {"fidelity": fidelity, "coverage": coverage, "udac": udac}


# ============================ C2 — bone determinism (proxy) ============================


def bone_inventory_signal(manifest_path: Path | None = None) -> dict[str, Any]:
    """C2 — the ``model_config_ref`` roster read from ``pipeline-manifest.yaml``.

    Plain YAML read (no ``app`` import). Fields are named for what they MEASURE —
    ``model_config_ref`` nullness — NOT determinism, because nullness is a *proxy*, not
    proof (Irene Pass-2 id ``08`` is an LLM with a null ref; Pass-1 gate nodes are LLM
    with null refs). Reports:

      * ``model_config_ref_null_count`` / ``model_config_ref_null_nodes`` — explicit
        ``null`` refs only (a MISSING key is ``model_config_ref_absent_nodes``, never
        counted as null — REWORK-4.1);
      * ``model_config_ref_set_nodes`` — nodes carrying a non-null ref (id/label/
        specialist_id/ref);
      * ``gates_all_model_config_ref_null`` — ``True`` iff every ``gate``-truthy node
        (REWORK-4.2: truthy, not ``is True``) carries an explicit null ref.

    Fail-soft: missing file / bad YAML / non-mapping / missing ``nodes`` list →
    ``{"status": "unavailable", ...}``.
    """
    p = manifest_path or (_repo_root() / _MANIFEST_REL)
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except (OSError, ValueError, yaml.YAMLError):
        return {"status": "unavailable", "source": _MANIFEST_REL}
    if not isinstance(data, dict) or not isinstance(data.get("nodes"), list):
        return {"status": "unavailable", "source": _MANIFEST_REL}

    nodes = [n for n in data["nodes"] if isinstance(n, dict)]
    null_nodes: list[Any] = []
    set_nodes: list[dict[str, Any]] = []
    absent_nodes: list[Any] = []
    gates_all_null = True
    for n in nodes:
        is_gate = bool(n.get("gate"))  # truthy, not `is True` (REWORK-4.2)
        ref = n.get("model_config_ref", _MISSING)
        if ref is _MISSING:
            absent_nodes.append(n.get("id"))
            if is_gate:  # an unknown ref on a gate cannot be claimed null
                gates_all_null = False
        elif ref is None:
            null_nodes.append(n.get("id"))
        else:
            set_nodes.append(
                {
                    "id": n.get("id"),
                    "label": n.get("label"),
                    "specialist_id": n.get("specialist_id"),
                    "model_config_ref": ref,
                }
            )
            if is_gate:
                gates_all_null = False

    return {
        "status": "ok",
        "source": _MANIFEST_REL,
        "total_nodes": len(nodes),
        "model_config_ref_null_count": len(null_nodes),
        "model_config_ref_null_nodes": null_nodes,
        "model_config_ref_set_nodes": set_nodes,
        "model_config_ref_absent_nodes": absent_nodes,
        "gates_all_model_config_ref_null": gates_all_null,
        "caveat": (
            "model_config_ref nullness is a determinism PROXY, not proof: Irene Pass-2 "
            "(id 08) is an LLM with a null ref, and Irene Pass-1 gate nodes are LLM "
            "with null refs; the workbook writer seams 07W.1/07W.3 carry a writer ref "
            "while deterministic stubs today. This signal cannot mechanically certify "
            "'strong' — that is a §1.6 human judgment; it can only downgrade on a "
            "detected boundary breach (an LLM ref on a gate node)."
        ),
    }


# ============================ C4 — lock + contract (unverified) ============================


def _load_run_summary(run_summary: dict | str | Path | None) -> dict | None:
    """Coerce the optional run-summary argument into a mapping (or ``None``).

    A ``str`` is treated as a filesystem path (REWORK-4.8 — a real path passed as a
    string must be read, not silently ignored → 'no run').
    """
    if isinstance(run_summary, dict):
        return run_summary
    if isinstance(run_summary, (str, Path)):
        try:
            data = yaml.safe_load(Path(run_summary).read_text(encoding="utf-8"))
        except (OSError, ValueError, yaml.YAMLError):
            return None
        return data if isinstance(data, dict) else None
    return None


def _normalize_bypass(raw: Any) -> int | str:
    """Normalize a raw ``silent_bypass_events`` value to a non-negative int, or the
    sentinels ``"undetected"`` / ``"unavailable"`` — never a false clean.

    Honest coercions (REWORK-4.3/4.4): a numeric string (``"3"``) and an
    integer-valued non-negative float (``2.0``) are real counts; a ``bool``, a
    negative number, a non-integer float, or unparseable text is malformed →
    ``"unavailable"``. ``None`` / absent → ``"undetected"``.
    """
    if raw is None:
        return "undetected"
    if isinstance(raw, bool):  # bool is an int subclass — never a count
        return "unavailable"
    if isinstance(raw, int):
        return raw if raw >= 0 else "unavailable"
    if isinstance(raw, float):
        return int(raw) if (raw.is_integer() and raw >= 0) else "unavailable"
    if isinstance(raw, str):
        low = raw.strip().lower()
        if low in {"undetected", "unavailable"}:
            return low
        try:
            iv = int(raw.strip())
        except ValueError:
            return "unavailable"
        return iv if iv >= 0 else "unavailable"
    return "unavailable"


def lock_contract_signal(run_summary: dict | str | Path | None = None) -> dict[str, Any]:
    """C4 — digest-module presence (file-existence FACT) + honest runtime bypass state.

    ``digest_module_present_on_disk`` is the mechanical file-existence of
    ``app/runtime/compiled_graph_digest.py`` — honestly labelled: it is NOT proof the
    digest is runtime-wired, only that the substrate module exists.

    ``silent_bypass_events`` consumes Q1.4a's honest run-summary
    ``fence_state.silent_bypass_events`` when a run-summary (dict / ``str`` path /
    ``Path``) is supplied; with no run observed it is the first-class sentinel
    ``"undetected"`` — never coerced to ``0``. See :func:`_normalize_bypass`.
    """
    digest_present = (_repo_root() / _DIGEST_MODULE_REL).is_file()

    silent_bypass: int | str = "undetected"
    summary = _load_run_summary(run_summary)
    if isinstance(summary, dict):
        fence_state = summary.get("fence_state")
        if isinstance(fence_state, dict):
            silent_bypass = _normalize_bypass(
                fence_state.get("silent_bypass_events", None)
            )

    return {
        "status": "ok",
        "source": _DIGEST_MODULE_REL,
        "digest_module_present_on_disk": digest_present,
        "silent_bypass_events": silent_bypass,
        "note": (
            "digest_module_present_on_disk is file-existence only (NOT proof of runtime "
            "wiring); silent_bypass_events is honestly 'undetected' with no run observed. "
            "Neither can certify a clean level — C4 'strong' is a §1.6 human judgment."
        ),
    }


# ============================ leak-count ============================


def _strip_fenced_code(text: str) -> str:
    """Drop fenced ``` code blocks so an EXAMPLE ``did_leak:`` inside one is not counted
    (REWORK-4.6). Toggles on any line whose stripped form starts with a code fence."""
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if _FENCE_LINE_RE.match(line):
            in_fence = not in_fence
            continue  # drop the fence line itself
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def _strip_html_comments(text: str) -> str:
    """Drop ``<!-- ... -->`` comment spans so a tag commented-out to temporarily
    disable it is NOT counted — a commented ``<!-- did_leak: x -->`` must read as
    absent (FIX-7). Mirrors :func:`_strip_fenced_code`. Non-greedy + DOTALL so
    multi-line comments are removed; an unclosed ``<!--`` is left intact (fail-soft),
    and an inline trailing comment on a real tag line is removed leaving the tag."""
    return _HTML_COMMENT_RE.sub("", text)


def _strip_archived_section(text: str) -> str:
    """Drop the archived section so only OPEN entries remain. Only the EXACT
    ``## Closed Entries …`` header opens the archive (REWORK-4.7) — a ``## `` heading
    that merely mentions "closed entries" mid-text is still open. The archive runs to
    the next top-level ``## `` header (or EOF).
    """
    out: list[str] = []
    in_archived = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            heading = stripped[3:].lstrip()
            in_archived = heading.lower().startswith("closed entries")
        if not in_archived:
            out.append(line)
    return "\n".join(out)


def open_leak_count_signal(inventory_path: Path | None = None) -> dict[str, Any]:
    """leak-count — count ``did_leak:``-tagged OPEN entries in the deferred inventory.

    Plain ``.md`` read. **5 today** (Q1.5 tagged the 5 DID leaks in the fixed
    ``## DID Scorecard Leak Registry`` section). Fenced code blocks are stripped
    (examples, not tags), ``<!-- ... -->`` HTML comments are stripped (a commented-out
    tag must not count — FIX-7), the archived section is excluded (open entries only),
    and the tag is anchored to line start (a mid-line prose mention does not count).
    Fail-soft: unreadable file → ``{"status": "unavailable", "open_leak_count": None}``.
    """
    p = inventory_path or (_repo_root() / _DEFERRED_INVENTORY_REL)
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return {
            "status": "unavailable",
            "source": _DEFERRED_INVENTORY_REL,
            "open_leak_count": None,
        }
    open_text = _strip_archived_section(_strip_html_comments(_strip_fenced_code(text)))
    count = len(_DID_LEAK_LINE_RE.findall(open_text))
    return {
        "status": "ok",
        "source": _DEFERRED_INVENTORY_REL,
        "open_leak_count": count,
    }


# ============================ cost-efficiency (Q2.1) ============================
#
# Signal readers over the EXISTING economics emitters (GL-15 — reuse, NO parallel
# plumbing): the budget-stop DEFAULT posture, ``cost_posture``, per-agent drift, and
# cost transparency. Economics types are reached ONLY via deferred LOCAL imports
# (GL-3 clean-leaf), and a run's cost report is otherwise read as PLAIN JSON. Every
# reader is fail-soft per field — it never raises and never invents a clean value.

#: ``cost_leak:`` tag, anchored to line start (mirrors ``_DID_LEAK_LINE_RE`` but a
#: SEPARATE per-dimension namespace so the cost count/identity reconciliation never
#: collides with the DID ``did_leak:`` count). 1 today (the budget-opt-in leak).
_COST_LEAK_LINE_RE = re.compile(r"(?m)^[\s>]*(?:[-*+]\s+)?cost_leak:")

#: The env var that wires the Epic-41 dollar brake. Today this is the runtime's ONLY
#: budget source (``production_runner._resolve_trial_budget_usd`` / the economics
#: ``resolved_budget`` both read it), and the production preset sets NO default for it.
_BUDGET_ENV_KEY = "MARCUS_TRIAL_BUDGET_USD"

_UNSET = object()
#: 64-hex digest, case-insensitive (a JSON cost-report may carry upper- or lower-case
#: hex; the model persists lower-case but a hand/JSON report must not false-"absent").
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)


def _resolve_runtime_default_budget(env: Mapping[str, str] | None = None) -> float | None:
    """Resolve the run's default dollar cap the SAME source + algorithm the runtime
    budget resolver uses (``production_runner._resolve_trial_budget_usd`` and the
    economics ``resolved_budget`` in ``measure_trial_cost``): read
    ``MARCUS_TRIAL_BUDGET_USD`` LIVE — an unset / blank / unparseable value means **no
    cap**. **Read-only — no ``os.environ`` mutation** (FIX-6). ``env`` defaults to the
    live ``os.environ`` and exists so a caller (a pin) can pass a clean mapping to read
    the preset-default posture WITHOUT a global env-clear window.

    **Honest today:** the production preset defines NO default-budget source, so a fresh
    production run resolves ``None`` → the brake is OPT-IN. **The close-path is reachable
    but needs runtime substrate:** when the preset gains a default-budget source that
    this resolver returns (the preset sets the env by default, or the resolver grows a
    preset-config cap), this returns a real cap and CE1 earns ``strong`` — the reader is
    NOT a hardcoded constant, it delegates to the real source.
    """
    source = os.environ if env is None else env
    raw = (source.get(_BUDGET_ENV_KEY) or "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _read_cost_report(source: Any) -> dict[str, Any] | None:
    """Coerce a cost-report source into a plain mapping, or ``None`` (fail-soft).

    A ``dict`` is returned as-is; a ``str``/``Path`` is read as a run's
    ``cost-report.json`` (plain JSON — no ``app`` import); a ``TrialEconomicsReport``-
    like object is dumped via ``.model_dump(mode="json")`` when available. Any failure
    (missing file, bad JSON, non-mapping) degrades to ``None``.
    """
    if source is None:
        return None
    if isinstance(source, dict):
        return source
    if isinstance(source, (str, Path)):
        try:
            data = json.loads(Path(source).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        return data if isinstance(data, dict) else None
    dump = getattr(source, "model_dump", None)
    if callable(dump):
        try:
            data = dump(mode="json")
        except Exception:  # noqa: BLE001 — a reader must never raise into a caller
            return None
        return data if isinstance(data, dict) else None
    return None


def budget_stop_default_signal(
    default_budget_usd: Any = _UNSET, env: Mapping[str, str] | None = None
) -> dict[str, Any]:
    """CE1 — is a budget cap ENFORCED BY DEFAULT on the production preset?

    The Epic-41 dollar brake (``MARCUS_TRIAL_BUDGET_USD`` → the ``check_trial_budget``
    SSOT, enforced at both walks' dispatch chokepoint — Story 41-4) is a REAL economic
    stop **when set**, but the production preset defines NO default-budget source, so the
    runtime resolver returns ``None`` and ``check_trial_budget(total, None)`` returns
    ``no-cap`` — the default posture is OPT-IN (default = no cap). This is the DID-C3
    pattern (mechanism exists, default OFF) → a cost-efficiency LEAK on the paid walk.

    **Not a hardcoded constant (FIX-1):** the default budget is resolved by
    :func:`_resolve_runtime_default_budget`, which reads the runtime's OWN budget source
    (the same ``MARCUS_TRIAL_BUDGET_USD`` the runtime resolver uses) — so IF the preset
    gains a default-budget source that resolver returns, this reader detects it and CE1
    can earn ``strong``. **Read-only (FIX-6):** no ``os.environ`` mutation. A pin reads
    the preset-default posture (ignoring an ambient operator opt-in) by passing a clean
    ``env`` mapping; ``check_trial_budget`` is reached by a DEFERRED local import (GL-3).
    ``default_budget_usd`` is a SEEDED-TEST override proving the level logic reaches
    ``strong`` on a real resolved cap (the substrate to feed a real preset-default is
    deferred — see deferred-work.md ``q2-1-r2-cost-posture-witness`` / the §2.6 close-path).
    """
    if default_budget_usd is _UNSET:
        budget = _resolve_runtime_default_budget(env)
    else:
        budget = default_budget_usd
    try:
        from app.runtime.economics import check_trial_budget

        status = check_trial_budget(1.0, budget)
        state = getattr(status, "state", None)
    except Exception:  # noqa: BLE001 — a signal read must never raise into a caller
        return {
            "status": "unavailable",
            "source": "app.runtime.economics.check_trial_budget",
        }
    if not isinstance(state, str):
        return {
            "status": "unavailable",
            "source": "app.runtime.economics.check_trial_budget",
        }
    enforced = budget is not None and state != "no-cap"
    return {
        "status": "ok",
        "source": "MARCUS_TRIAL_BUDGET_USD / app.runtime.economics.check_trial_budget",
        "default_budget_usd": budget,
        "budget_status_state": state,
        "default_budget_enforced": enforced,
        "note": (
            "the production preset defines no default-budget source, so the runtime "
            "resolver returns None and check_trial_budget(total, None)=='no-cap' → the "
            "Epic-41 dollar brake is a REAL enforced stop WHEN SET but OPT-IN by default. "
            "Closing the leak needs runtime substrate (a preset-default budget source the "
            "resolver returns); when present this reader detects it and CE1 earns strong."
        ),
    }


def cost_posture_signal(report: Any = None) -> dict[str, Any]:
    """CE2 — the run's ``cost_posture`` (``exact`` vs
    ``known-lower-bound-with-explicit-unavailable-attempts``) + ``unavailable_attempt_count``.

    A lower-bound posture means the reported cost is a FLOOR, not exact — an honest
    honesty-gap WHEN it occurs (the model validator forbids claiming ``exact`` with
    unavailable attempts, so the posture cannot lie). Reads a report dict / JSON path /
    model object; no report → an honest ``"no-report"`` marker (never a clean value).
    """
    data = _read_cost_report(report)
    if data is None:
        return {
            "status": "no-report",
            "source": "trial_economics_report.cost_posture",
            "cost_posture": None,
            "unavailable_attempt_count": None,
        }
    posture = data.get("cost_posture")
    return {
        "status": "ok",
        "source": "trial_economics_report.cost_posture",
        "cost_posture": posture,
        "unavailable_attempt_count": data.get("unavailable_attempt_count"),
        "is_exact": posture == "exact",
        "is_lower_bound": (
            posture == "known-lower-bound-with-explicit-unavailable-attempts"
        ),
        "note": (
            "a lower-bound posture = the reported cost is a FLOOR, not exact; the model "
            "validator forbids 'exact' when unavailable_attempt_count>0 (posture cannot lie)."
        ),
    }


def cost_drift_signal(report: Any = None) -> dict[str, Any]:
    """CE3 — is per-agent drift monitoring wired, and what does a report's
    ``drift_alerts`` carry?

    ``compute_per_agent_drift`` (rolling 5-trial median; a ≥50% per-call deviation →
    a ``DriftAlert``) is the wired monitor — its importability is the ``drift_monitoring_wired``
    fact (deferred import, GL-3). A supplied report's ``drift_alerts`` list length is the
    observed alert count. Honest caveat: drift needs ≥5 history to fire and is ADVISORY
    (informational, not a spend gate).
    """
    monitoring_wired = False
    try:
        from app.runtime.economics import compute_per_agent_drift  # noqa: F401

        monitoring_wired = True
    except Exception:  # noqa: BLE001
        monitoring_wired = False
    data = _read_cost_report(report)
    alerts = data.get("drift_alerts") if isinstance(data, dict) else None
    # FIX-4: the monitor being UNIMPORTABLE is not "healthy" — a consumer keying on
    # status=="ok" must not read wiring-absent as fine. Mirror the budget reader's
    # import-failure handling: status "unavailable" when the monitor cannot be imported.
    return {
        "status": "ok" if monitoring_wired else "unavailable",
        "source": "app.runtime.economics.compute_per_agent_drift / drift_alerts",
        "drift_monitoring_wired": monitoring_wired,
        "drift_alert_count": len(alerts) if isinstance(alerts, list) else None,
        "note": (
            "drift is a rolling 5-trial median monitor (>=50% per-call deviation → alert); "
            "needs >=5 history to fire and is ADVISORY (informational, not a spend gate)."
        ),
    }


def cost_transparency_signal(report: Any = None) -> dict[str, Any]:
    """CE4 — does a report carry the reproducible cost-attestation fields?

    ``per_agent_breakdown`` + ``per_model_breakdown`` + a 64-hex ``cascade_config_digest``
    + a 64-hex ``pricing_table_digest`` together let a run's cost be re-derived and
    audited. Reports per-field presence + ``all_present``; no report → ``"no-report"``.
    """
    data = _read_cost_report(report)
    if data is None:
        return {
            "status": "no-report",
            "source": "trial_economics_report cost-attestation fields",
            "fields_present": None,
            "all_present": None,
        }

    def _sha256(value: Any) -> bool:
        return isinstance(value, str) and bool(_SHA256_RE.match(value))

    def _nonempty_dict(value: Any) -> bool:
        # FIX-3: an EMPTY breakdown ({}) is not a reproducible attestation — a report
        # with no cost data must NOT claim "fully reproducible". Require non-empty.
        return isinstance(value, dict) and len(value) > 0

    fields_present = {
        "per_agent_breakdown": _nonempty_dict(data.get("per_agent_breakdown")),
        "per_model_breakdown": _nonempty_dict(data.get("per_model_breakdown")),
        "cascade_config_digest": _sha256(data.get("cascade_config_digest")),
        "pricing_table_digest": _sha256(data.get("pricing_table_digest")),
    }
    return {
        "status": "ok",
        "source": "trial_economics_report cost-attestation fields",
        "fields_present": fields_present,
        "all_present": all(fields_present.values()),
        "note": (
            "per_agent + per_model breakdown + cascade/pricing digests = a reproducible "
            "cost attestation (report-time transparency, not a live spend fence)."
        ),
    }


def cost_leak_count_signal(inventory_path: Path | None = None) -> dict[str, Any]:
    """cost leak-count — count ``cost_leak:``-tagged OPEN entries in the deferred
    inventory (a SEPARATE per-dimension namespace from ``did_leak:``).

    Same scoping as :func:`open_leak_count_signal` (fenced code / HTML comments /
    archived section stripped; line-anchored tag). **1 today** (the budget-opt-in leak
    in the ``## Cost-Efficiency Scorecard Leak Registry``). Fail-soft: unreadable file →
    ``{"status": "unavailable", "cost_leak_count": None}``.
    """
    p = inventory_path or (_repo_root() / _DEFERRED_INVENTORY_REL)
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return {
            "status": "unavailable",
            "source": _DEFERRED_INVENTORY_REL,
            "cost_leak_count": None,
        }
    open_text = _strip_archived_section(_strip_html_comments(_strip_fenced_code(text)))
    count = len(_COST_LEAK_LINE_RE.findall(open_text))
    return {
        "status": "ok",
        "source": _DEFERRED_INVENTORY_REL,
        "cost_leak_count": count,
    }


# ============================ coverage-honesty (Q2.2) ============================
#
# Signal readers over the EXISTING coverage emitters (GL-15 — reuse, NO parallel
# plumbing): the coverage-gate DEFAULT posture (``coverage_gate_active`` — the fence),
# the receipt-honesty / vacuous distinction (``evaluate_vacuous_receipt`` +
# ``COVERAGE_VACUOUS_TAG`` + the ``CoverageReceipt`` model), and the narration-obligation
# BLOCK term (``evaluate_coverage_gate`` + ``narration_obligation_unmet``). Coverage types
# and gate functions are reached ONLY via deferred LOCAL imports (GL-3 clean-leaf), and a
# run's coverage receipt is otherwise read as PLAIN JSON. Every reader is fail-soft per
# field — it never raises and never invents a clean value.

#: ``cov_leak:`` tag, anchored to line start — a THIRD per-dimension namespace disjoint
#: from ``did_leak:`` / ``cost_leak:`` so the coverage count/identity reconciliation never
#: collides with the other two. 1 today (the default-OFF coverage-gate leak).
_COVERAGE_LEAK_LINE_RE = re.compile(r"(?m)^[\s>]*(?:[-*+]\s+)?cov_leak:")

#: The env var that wakes the coverage fail-loud gate (``coverage_gate_active`` reads it,
#: default OFF). The production preset sets NO default for it → source-coverage is not
#: enforced by default. This is the runtime's OWN gate source (no parallel plumbing).
_COVERAGE_GATE_ENV_KEY = "MARCUS_COVERAGE_GATE_ACTIVE"
#: The truthy vocabulary ``coverage_gate_wiring._env_true`` uses (mirrored here so the
#: injectable-env resolution matches the real gate's rule exactly — anti-drift).
_ENV_TRUTHY: frozenset[str] = frozenset({"1", "true", "yes", "on"})


def coverage_fence_default_signal(env: Mapping[str, str] | None = None) -> dict[str, Any]:
    """CV1 — is source-coverage ENFORCED BY DEFAULT on the production preset?

    The coverage fail-loud gate (``coverage_gate_active`` → the both-walks
    ``enforce_coverage_gate_before_audio`` seam, BEFORE audio spend) is a REAL fence
    **when woken**, but ``MARCUS_COVERAGE_GATE_ACTIVE`` is default-OFF and the production
    preset sets no default for it → the default posture is OPT-IN (default = un-enforced).
    This is the DID-C3 / cost-CE1 pattern (mechanism exists, default OFF) → a
    coverage-honesty LEAK: the default-OFF gap IS the leak, NOT a pass.

    **Built RIGHT per the Q2.1 CE1 remediation:**
      * **reachable close-path** — when ``env is None`` (live) the reader delegates to the
        REAL ``coverage_gate_active()`` (deferred import); so IF the preset genuinely wires
        the gate ON by default, this reports ``default_coverage_enforced=True`` and CV1 can
        earn ``strong`` — the pin must NOT block that honest upgrade;
      * **read-only + env-independent (FIX-1/FIX-6)** — NO ``os.environ`` mutation and NO
        self-clearing constant. A caller (a pin) reads the PRESET-DEFAULT posture (ignoring
        an ambient operator opt-in) by passing a clean ``env`` mapping; the flag is then
        resolved from that mapping with the SAME truthy rule the real gate uses.

    FIX-4: an unimportable gate seam degrades to ``status="unavailable"`` (never a clean or
    silently-``False`` posture — a missing seam is NOT "definitely un-enforced").
    """
    try:
        from app.marcus.orchestrator.coverage_gate_wiring import coverage_gate_active
    except Exception:  # noqa: BLE001 — a signal read must never raise into a caller
        return {
            "status": "unavailable",
            "source": "app.marcus.orchestrator.coverage_gate_wiring.coverage_gate_active",
        }
    if env is None:
        # Live path: consult the REAL source (reads os.environ, read-only, no mutation).
        try:
            enforced = coverage_gate_active()
        except Exception:  # noqa: BLE001
            return {
                "status": "unavailable",
                "source": "app.marcus.orchestrator.coverage_gate_wiring.coverage_gate_active",
            }
    else:
        # Preset-default posture from an injectable env, using the gate's own truthy rule.
        # Fail-soft (FIX-2): the reader NEVER raises into a caller. A non-Mapping env (a
        # list) or a non-str env value (a malformed env mapping) degrades to
        # "unavailable" — never a false-clean posture and never an escaping AttributeError.
        _unavailable = {
            "status": "unavailable",
            "source": "app.marcus.orchestrator.coverage_gate_wiring.coverage_gate_active",
        }
        try:
            val = env.get(_COVERAGE_GATE_ENV_KEY)
        except Exception:  # noqa: BLE001 — a non-Mapping env (e.g. a list)
            return _unavailable
        if val is None:
            enforced = False
        elif isinstance(val, str):
            enforced = val.strip().lower() in _ENV_TRUTHY
        else:  # a non-str env value is malformed — never coerced to a clean posture
            return _unavailable
    if not isinstance(enforced, bool):
        return {
            "status": "unavailable",
            "source": "app.marcus.orchestrator.coverage_gate_wiring.coverage_gate_active",
        }
    return {
        "status": "ok",
        "source": f"{_COVERAGE_GATE_ENV_KEY} / coverage_gate_wiring.coverage_gate_active",
        "default_coverage_enforced": enforced,
        "note": (
            "the production preset sets no default for MARCUS_COVERAGE_GATE_ACTIVE, so "
            "coverage_gate_active()==False by default → the coverage fail-loud gate (a REAL "
            "fence when woken, at the both-walks pre-audio-spend seam) is OPT-IN. The "
            "default-OFF gap IS the leak (a leak, NOT a pass). Close-path is reachable: if "
            "the preset wires the gate ON by default this reader reports enforced=True and "
            "CV1 earns strong."
        ),
    }


def _load_coverage_receipt_obj(source: Any) -> Any | None:
    """Coerce a coverage-receipt source into a ``CoverageReceipt`` object, or ``None``.

    A ``CoverageReceipt``-like object (duck-typed: has ``is_vacuous`` + ``rows``) passes
    through; a ``dict`` / JSON ``str``/``Path`` is rehydrated via a DEFERRED import of
    ``load_coverage_receipt`` (GL-3 — no module-scope ``app.*``). Any failure (missing
    file / bad JSON / non-mapping / validation error) degrades to ``None`` (fail-soft).
    """
    if source is None:
        return None
    if hasattr(source, "is_vacuous") and hasattr(source, "rows"):
        return source
    data: Any = None
    if isinstance(source, dict):
        data = source
    elif isinstance(source, str):
        # FIX-4: a ``str`` may be JSON CONTENT or a filesystem PATH. Try JSON-content
        # first (so a supplied receipt-as-text is not silently misread as "no receipt"
        # via an OSError), then fall back to reading it as a path.
        try:
            parsed = json.loads(source)
        except ValueError:
            parsed = None
        if isinstance(parsed, dict):
            data = parsed
        else:
            try:
                data = json.loads(Path(source).read_text(encoding="utf-8"))
            except (OSError, ValueError):
                return None
    elif isinstance(source, Path):
        try:
            data = json.loads(Path(source).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
    if not isinstance(data, dict):
        return None
    try:
        from app.marcus.lesson_plan.coverage_receipt import load_coverage_receipt

        return load_coverage_receipt(data)
    except Exception:  # noqa: BLE001 — a reader must never raise into a caller
        return None


def coverage_receipt_honesty_signal(
    receipt: Any = None, *, note_bearing_content_exists: bool = False
) -> dict[str, Any]:
    """CV2 — does the machinery honestly distinguish PASS / FAIL / PASS-vacuous?

    ``evaluate_vacuous_receipt`` + ``COVERAGE_VACUOUS_TAG`` flag a receipt that "passed"
    only because it asserted nothing (rows-but-zero-joined, or empty-when-note-bearing-
    content-existed) — a vacuous PASS is honestly NOT a real pass. ``all_deliberately_
    excluded`` is the legitimate nothing-to-cover case (NOT vacuous). This reader reports
    the FACT that the guard is wired + honest; the LEVEL is a §3 judgment-with-evidence
    (``level_from_signal`` returns ``None``).

    FIX-4: an unimportable guard degrades to ``status="unavailable"`` +
    ``vacuous_guard_wired=False`` (never read wiring-absent as healthy). FIX-3: a
    present-but-EMPTY receipt against note-bearing content is honestly NOT a clean pass
    (the guard returns a block reason) — a non-empty structure is never assumed "covered".
    """
    try:
        from app.marcus.lesson_plan.coverage_gate import (
            COVERAGE_VACUOUS_TAG,
            evaluate_coverage_gate,
            evaluate_vacuous_receipt,
        )
    except Exception:  # noqa: BLE001
        return {
            "status": "unavailable",
            "source": "app.marcus.lesson_plan.coverage_gate",
            "vacuous_guard_wired": False,
        }
    rec = _load_coverage_receipt_obj(receipt)
    if rec is None:
        return {
            "status": "ok",
            "source": "app.marcus.lesson_plan.coverage_gate.evaluate_vacuous_receipt",
            "vacuous_guard_wired": True,
            "vacuous_tag": COVERAGE_VACUOUS_TAG,
            "receipt_present": False,
            "note": (
                "the vacuous-distinction guard (evaluate_vacuous_receipt + "
                "COVERAGE_VACUOUS_TAG) is wired; no receipt supplied so only the wiring "
                "FACT is reported. A vacuous PASS is honestly NOT a real pass."
            ),
        }
    try:
        reason = evaluate_vacuous_receipt(
            rec, note_bearing_content_exists=note_bearing_content_exists
        )
        # A must-cover BLOCK (evaluate_coverage_gate returns ≥1 blocking row) is a real
        # FAIL — a coverage hole the vacuous guard alone is BLIND to (review FIX-1). A
        # receipt the gate BLOCKS is never a clean pass; is_clean_pass must consult it.
        gate_blocks = bool(evaluate_coverage_gate(rec))
        is_vacuous = bool(rec.is_vacuous())
        all_excluded = bool(rec.all_deliberately_excluded())
        joined = int(rec.joined_row_count())
        row_count = len(rec.rows)
    except Exception:  # noqa: BLE001
        return {
            "status": "unavailable",
            "source": "app.marcus.lesson_plan.coverage_gate.evaluate_vacuous_receipt",
            "vacuous_guard_wired": True,
        }
    return {
        "status": "ok",
        "source": "app.marcus.lesson_plan.coverage_gate.evaluate_vacuous_receipt",
        "vacuous_guard_wired": True,
        "vacuous_tag": COVERAGE_VACUOUS_TAG,
        "receipt_present": True,
        "row_count": row_count,
        "joined_row_count": joined,
        "is_vacuous": is_vacuous,
        "all_deliberately_excluded": all_excluded,
        "gate_blocks": gate_blocks,
        "vacuous_block_reason": reason,
        # A clean pass = the must-cover gate does NOT block (FIX-1: a genuine FAIL is
        # never a clean pass) AND the vacuous guard raised NO reason (FIX-3: a
        # present-but-empty / rows-but-zero-joined receipt is not covered) AND real
        # coverage was joined (or it is the legitimate all-excluded nothing-to-cover case).
        "is_clean_pass": (
            reason is None and not gate_blocks and (joined > 0 or all_excluded)
        ),
        "note": (
            "PASS / FAIL / PASS-vacuous are honestly distinguished: gate_blocks flags a "
            "must-cover FAIL (evaluate_coverage_gate); is_vacuous flags rows-but-zero- "
            "joined; an empty receipt against note-bearing content blocks; "
            "all_deliberately_excluded is the legitimate nothing-to-cover PASS. Neither a "
            "FAIL nor a vacuous receipt is a real pass (R5-A5)."
        ),
    }


def coverage_narration_obligation_signal(receipt: Any = None) -> dict[str, Any]:
    """CV3 — is the narration-obligation BLOCK term wired (FIX-2 in coverage_gate)?

    A ``detail_in_narration`` point carried ONLY on the slide does NOT satisfy its
    narration obligation; ``narration_obligation_unmet`` is an INDEPENDENT block term in
    the gate predicate. This reader reports the wiring FACT by EXERCISING the real
    ``_is_blocking`` predicate (FIX-3 — not mere model-field presence: a probe row whose
    only blocking reason is the narration obligation must actually block) + a supplied
    receipt's unmet/blocking counts. The LEVEL is a §3 judgment-with-evidence
    (``level_from_signal`` returns ``None``).

    FIX-4: an unimportable gate/model degrades to ``status="unavailable"`` +
    ``narration_obligation_gate_wired=False``.
    """
    try:
        from app.marcus.lesson_plan.coverage_gate import (
            _is_blocking,
            evaluate_coverage_gate,
        )
    except Exception:  # noqa: BLE001
        return {
            "status": "unavailable",
            "source": "app.marcus.lesson_plan.coverage_gate.evaluate_coverage_gate",
            "narration_obligation_gate_wired": False,
        }
    # FIX-3: verify the REAL block-predicate wiring, NOT mere model-field presence. A
    # synthetic must-cover row whose ONLY blocking reason is narration_obligation_unmet
    # must be BLOCKED by _is_blocking, while its narration-met control must NOT — so a
    # future edit that drops the term from the predicate (while keeping the model field)
    # flips gate_wired to False (a false wiring claim in an honesty dimension is caught).
    from types import SimpleNamespace

    def _probe(unmet: bool) -> SimpleNamespace:
        return SimpleNamespace(
            must_cover=True,
            planned_on_slide=True,
            planned_in_narration=False,
            coverage_status="covered_on_slide",
            verbatim_absent=False,
            narration_obligation_unmet=unmet,
        )

    try:
        gate_wired = bool(_is_blocking(_probe(True))) and not _is_blocking(_probe(False))
    except Exception:  # noqa: BLE001
        gate_wired = False
    rec = _load_coverage_receipt_obj(receipt)
    if rec is None:
        return {
            "status": "ok",
            "source": "app.marcus.lesson_plan.coverage_gate.evaluate_coverage_gate",
            "narration_obligation_gate_wired": gate_wired,
            "receipt_present": False,
            "note": (
                "narration_obligation_unmet is an independent BLOCK term (FIX-2): a "
                "slide-only carriage does NOT satisfy a must-cover detail_in_narration "
                "obligation. No receipt supplied so only the wiring FACT is reported."
            ),
        }
    try:
        blocking = evaluate_coverage_gate(rec)
        unmet_rows = sum(
            1 for r in rec.rows if getattr(r, "narration_obligation_unmet", False)
        )
        blocking_unmet = sum(
            1 for r in blocking if getattr(r, "narration_obligation_unmet", False)
        )
    except Exception:  # noqa: BLE001
        return {
            "status": "unavailable",
            "source": "app.marcus.lesson_plan.coverage_gate.evaluate_coverage_gate",
            "narration_obligation_gate_wired": gate_wired,
        }
    return {
        "status": "ok",
        "source": "app.marcus.lesson_plan.coverage_gate.evaluate_coverage_gate",
        "narration_obligation_gate_wired": gate_wired,
        "receipt_present": True,
        "narration_obligation_unmet_rows": unmet_rows,
        "blocking_rows": len(blocking),
        "blocking_narration_obligation_rows": blocking_unmet,
        "note": (
            "a must-cover detail_in_narration point whose span reaches only the slide is "
            "an UNMET narration obligation → an independent BLOCK term the gate blocks on "
            "(FIX-2). Wired end-to-end, but fires only when the gate is woken (default-OFF)."
        ),
    }


def coverage_leak_count_signal(inventory_path: Path | None = None) -> dict[str, Any]:
    """coverage leak-count — count ``cov_leak:``-tagged OPEN entries in the deferred
    inventory (a THIRD per-dimension namespace, disjoint from ``did_leak:`` /
    ``cost_leak:``).

    Same scoping as :func:`open_leak_count_signal` / :func:`cost_leak_count_signal`
    (fenced code / HTML comments / archived section stripped; line-anchored tag). **1
    today** (the default-OFF coverage-gate leak in the ``## Coverage-Honesty Scorecard
    Leak Registry``). Fail-soft: unreadable file → ``{"status": "unavailable",
    "coverage_leak_count": None}``.
    """
    p = inventory_path or (_repo_root() / _DEFERRED_INVENTORY_REL)
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return {
            "status": "unavailable",
            "source": _DEFERRED_INVENTORY_REL,
            "coverage_leak_count": None,
        }
    open_text = _strip_archived_section(_strip_html_comments(_strip_fenced_code(text)))
    count = len(_COVERAGE_LEAK_LINE_RE.findall(open_text))
    return {
        "status": "ok",
        "source": _DEFERRED_INVENTORY_REL,
        "coverage_leak_count": count,
    }


# ============================ fidelity-trust (Q2.3) ============================
#
# Signal readers over the EXISTING fidelity emitters (GL-15 — reuse, NO parallel
# plumbing): the semantic-fidelity audit's DEFAULT gating posture (the
# ``SEMANTIC_TRIPWIRE["gates_production"]`` module constant — the fence), the Vera
# fidelity trace's real Omissions/Inventions/Alterations FAIL condition
# (``vera._act._hard_fail`` over a trace's findings + the verdict status), and the
# audit's WARN-transparency posture (``mode == "warn_only"`` + the claim fence). The
# fidelity types are reached ONLY via deferred LOCAL imports (GL-3 clean-leaf), and a
# run's fidelity trace is otherwise read as PLAIN JSON. Every reader is fail-soft per
# field — it never raises and never invents a clean value.

#: ``fid_leak:`` tag, anchored to line start — a FOURTH per-dimension namespace disjoint
#: from ``did_leak:`` / ``cost_leak:`` / ``cov_leak:`` so the fidelity count/identity
#: reconciliation never collides with the other three. 1 today (the WARN-only-that-never-
#: gates semantic-fence leak).
_FIDELITY_LEAK_LINE_RE = re.compile(r"(?m)^[\s>]*(?:[-*+]\s+)?fid_leak:")

#: The Vera fidelity-trace hard-fail category set (Omissions / Inventions / Alterations),
#: mirrored here for the O/I/A COUNT only; the REAL predicate ``vera._act._hard_fail`` is
#: what the honesty reader consults for the fail decision (never re-implemented). An
#: anti-drift pin (test_fidelity_mirrored_vera_constants_match_source) ties this to Vera's
#: real ``OIA`` so a future Vera rename reds the test rather than silently mis-counting.
_OIA_CATEGORIES: frozenset[str] = frozenset({"O", "I", "A"})
#: Vera verdict status that marks a real fidelity FAIL (a hard O/I/A finding halts). Hand-
#: mirrored from ``vera._act`` and anti-drift-pinned (same test) so a Vera rename cannot
#: silently make ``verdict_halts`` permanently False.
_FIDELITY_HALT_STATUS = "HALT-AND-REMEDIATE"
#: The schema tag a genuine Vera fidelity trace carries (``vera._act`` emits it). A dict
#: lacking this tag is a foreign artifact / wrong file and can NEVER certify clean (FIX-3).
_FIDELITY_TRACE_SCHEMA = "fidelity-trace.v1"


def _read_semantic_tripwire(tripwire: Any = None) -> Mapping[str, Any] | None:
    """Coerce the semantic-tripwire source into a mapping, or ``None`` (fail-soft).

    ``tripwire is None`` → consult the REAL ``SEMANTIC_TRIPWIRE`` module constant via a
    DEFERRED import (GL-3 — no module-scope ``app.*``). An injectable ``Mapping`` is
    returned as-is so a pin/test can read a SEEDED posture (the reachable close-path:
    ``gates_production=True`` → gating) WITHOUT mutating the real constant — read-only.
    A non-mapping injected value / an unimportable constant degrades to ``None``.
    """
    if tripwire is not None:
        return tripwire if isinstance(tripwire, Mapping) else None
    try:
        from app.specialists._shared.source_fidelity_audit import SEMANTIC_TRIPWIRE
    except Exception:  # noqa: BLE001 — a signal read must never raise into a caller
        return None
    return SEMANTIC_TRIPWIRE if isinstance(SEMANTIC_TRIPWIRE, Mapping) else None


def semantic_fence_gating_signal(tripwire: Any = None) -> dict[str, Any]:
    """FT1 — does the semantic-fidelity audit GATE production BY DEFAULT?

    The semantic-fidelity audit (``audit_semantic_framing`` — a REAL heuristic that
    reports candidate unsourced-framing) is honest machinery, but its disposition
    constant ``SEMANTIC_TRIPWIRE["gates_production"]`` is ``False``: it WARNs and never
    FAILS a production run. A WARN that never gates = the measured gap → a fidelity-trust
    LEAK (the DID-C3 / cost-CE1 / coverage-CV1 pattern: mechanism exists, never gates).

    **SIGNAL-DERIVED + reachable close-path (Q2.1 CE1 / Q2.2 CV1 discipline):** the reader
    reads the REAL ``gates_production`` constant (not a hardcoded ``False``); IF it is
    genuinely flipped ``True`` the reader reports ``semantic_fence_gates=True`` and FT1 can
    earn ``strong`` — the pin must NOT block that honest upgrade. **Read-only** — it only
    READS the constant (simpler than CE1/CV1 since the source is a constant, not an env
    toggle; no mutation, no self-clearing). An injectable ``tripwire`` mapping reads a
    seeded posture independent of the committed constant. ``gates_production`` is read
    STRICTLY as ``bool`` — a non-``bool`` value (unknown posture) degrades to
    ``"unavailable"`` (never coerced to a clean/false posture).

    FIX-4: an unimportable / non-mapping tripwire degrades to ``status="unavailable"``
    (never a clean or silently-``False`` posture — a missing constant is NOT "definitely
    non-gating").
    """
    trip = _read_semantic_tripwire(tripwire)
    if trip is None:
        return {
            "status": "unavailable",
            "source": "app.specialists._shared.source_fidelity_audit.SEMANTIC_TRIPWIRE",
        }
    try:
        gates = trip.get("gates_production")
    except Exception:  # noqa: BLE001 — a non-Mapping-ish injected value
        return {
            "status": "unavailable",
            "source": "app.specialists._shared.source_fidelity_audit.SEMANTIC_TRIPWIRE",
        }
    if not isinstance(gates, bool):
        # unknown / malformed posture — never coerced to a clean or false gating claim.
        return {
            "status": "unavailable",
            "source": "SEMANTIC_TRIPWIRE.gates_production",
        }
    return {
        "status": "ok",
        "source": "SEMANTIC_TRIPWIRE.gates_production",
        "gates_production": gates,
        "semantic_fence_gates": gates,
        "note": (
            "the semantic-fidelity audit (audit_semantic_framing) is REAL but "
            "SEMANTIC_TRIPWIRE['gates_production'] is False → it WARNs and never FAILS a "
            "production run. A WARN that never gates IS the measured gap (the DID-C3 / "
            "cost-CE1 / coverage-CV1 pattern) → the fidelity-trust leak. Close-path is "
            "reachable: flip gates_production True (the real audit becomes gating) and this "
            "reader reports semantic_fence_gates=True → FT1 earns strong. Cross-links DID "
            "Leak-2 (braid-workbook-semantic-claim-citation-audit) — counted once, under "
            "fid_leak:, not double-counted."
        ),
    }


def _read_fidelity_trace(source: Any) -> dict[str, Any] | None:
    """Coerce a Vera fidelity-trace source into a plain mapping, or ``None`` (fail-soft).

    A ``dict`` passes through; a ``str`` is tried as JSON CONTENT first then as a
    filesystem PATH (Q2.2 FIX-4 — a supplied trace-as-text is not silently misread as
    "no trace" via an OSError); a ``Path`` is read as JSON. Any failure (missing file /
    bad JSON / non-mapping) degrades to ``None``. No ``app`` import — a trace is plain
    ``fidelity-trace.v1`` JSON.
    """
    if source is None:
        return None
    if isinstance(source, dict):
        return source
    if isinstance(source, str):
        try:
            parsed = json.loads(source)
        except ValueError:
            parsed = None
        if isinstance(parsed, dict):
            return parsed
        try:
            data = json.loads(Path(source).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        return data if isinstance(data, dict) else None
    if isinstance(source, Path):
        try:
            data = json.loads(Path(source).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        return data if isinstance(data, dict) else None
    return None


def fidelity_trace_honesty_signal(trace: Any = None) -> dict[str, Any]:
    """FT2 — does the fidelity trace honestly report a real Omission/Invention/Alteration
    FAIL, rather than reading "clean" on a real fidelity fail? (The Q2.2 CV2 lesson.)

    The Vera fidelity trace (``fidelity-trace.v1``) carries ``findings`` (each
    ``{category, severity, ...}`` with ``category`` ∈ O/I/A) and a ``verdict``. A REAL
    fidelity FAIL is a hard O/I/A finding — decided by the REAL predicate
    ``vera._act._hard_fail`` (category ∈ O/I/A ∧ severity ``critical`` → the trace's
    verdict becomes ``HALT-AND-REMEDIATE``). This reader CONSULTS that real predicate (a
    DEFERRED import, GL-3) — it does NOT re-implement the fail rule and does NOT report a
    "clean" fidelity on a real O/I/A fail (``is_clean_fidelity`` is False whenever
    ``_hard_fail`` fires OR the verdict halts). The LEVEL is a §4 judgment-with-evidence
    (``level_from_signal`` returns ``None``).

    A trace with ZERO findings cannot certify clean (non-empty guard — a real trace emits
    at least the advisory O/I/A trio); no trace supplied → only the wiring FACT.

    FIX-4: an unimportable predicate degrades to ``status="unavailable"`` +
    ``fidelity_fail_predicate_wired=False`` (never read wiring-absent as clean).
    """
    try:
        from app.specialists.vera._act import _hard_fail
    except Exception:  # noqa: BLE001
        return {
            "status": "unavailable",
            "source": "app.specialists.vera._act._hard_fail",
            "fidelity_fail_predicate_wired": False,
        }
    data = _read_fidelity_trace(trace)
    if data is None:
        return {
            "status": "ok",
            "source": "app.specialists.vera._act._hard_fail",
            "fidelity_fail_predicate_wired": True,
            "trace_present": False,
            "note": (
                "the real O/I/A hard-fail predicate (vera._act._hard_fail: category in "
                "{O,I,A} and severity=='critical' → HALT-AND-REMEDIATE) is wired; no trace "
                "supplied so only the wiring FACT is reported. A real O/I/A fail is NEVER a "
                "clean fidelity (the Q2.2 CV2 is_clean_pass lesson applied to fidelity)."
            ),
        }
    # FIX-3: only a genuine ``fidelity-trace.v1`` Vera trace may certify clean. An arbitrary
    # dict with findings/verdict keys (a foreign artifact / wrong file) degrades to
    # "unavailable" — never a false-clean. (schema_version is what vera._act emits.)
    if data.get("schema_version") != _FIDELITY_TRACE_SCHEMA:
        return {
            "status": "unavailable",
            "source": "app.specialists.vera._act._hard_fail",
            "fidelity_fail_predicate_wired": True,
            "note": (
                f"trace schema_version {data.get('schema_version')!r} != "
                f"{_FIDELITY_TRACE_SCHEMA!r} — a foreign / wrong-schema artifact cannot "
                "certify a clean fidelity."
            ),
        }
    findings = data.get("findings")
    findings_list = findings if isinstance(findings, list) else []
    # FIX-2: pass the DICT-FILTERED findings to the real predicate (consistent with
    # oia_finding_count). _hard_fail does finding.get(...), so a non-dict entry would raise
    # AttributeError → caught → "unavailable", MASKING a genuine critical O/I/A positioned
    # after the non-dict. Filtering first means a real fail after a junk entry is still
    # detected, not suppressed.
    dict_findings = [f for f in findings_list if isinstance(f, dict)]
    verdict = data.get("verdict")
    verdict_status = verdict.get("status") if isinstance(verdict, dict) else None
    try:
        hard_fail = _hard_fail(dict_findings)
    except Exception:  # noqa: BLE001 — the predicate must never raise into a caller
        return {
            "status": "unavailable",
            "source": "app.specialists.vera._act._hard_fail",
            "fidelity_fail_predicate_wired": True,
        }
    oia_finding_count = sum(
        1 for f in dict_findings if f.get("category") in _OIA_CATEGORIES
    )
    verdict_halts = verdict_status == _FIDELITY_HALT_STATUS
    return {
        "status": "ok",
        "source": "app.specialists.vera._act._hard_fail",
        "fidelity_fail_predicate_wired": True,
        "trace_present": True,
        "findings_count": len(findings_list),
        "oia_finding_count": oia_finding_count,
        "hard_fail_finding": hard_fail,
        "verdict_status": verdict_status,
        "verdict_halts": verdict_halts,
        # A clean fidelity = the trace carries REAL O/I/A findings AND the REAL hard-fail
        # predicate does NOT fire AND the verdict does not halt. FIX-1: require
        # oia_finding_count > 0 (not merely len(findings) > 0) — a degenerate trace with
        # findings but ZERO O/I/A entries cannot certify clean fidelity (the CV2 over-claim-
        # clean failure this reader exists to prevent). The `_hard_fail` term (not the
        # verdict status) is what drives NOT-clean on a real critical O/I/A — the verdict_halts
        # term is defensive/redundant, so a regressed impl trusting only verdict.status would
        # be caught by the isolating test (critical O/I/A + PROCEED → still not-clean).
        "is_clean_fidelity": (
            hard_fail is None and not verdict_halts and oia_finding_count > 0
        ),
        "note": (
            "PASS / FAIL are honestly distinguished by the REAL predicate: a critical O/I/A "
            "finding (vera._act._hard_fail) → NOT a clean fidelity (independent of verdict "
            "status); a trace with no O/I/A findings cannot certify clean (oia_finding_count "
            "guard). The reader consults the real fail condition, never mere trace presence "
            "(Q2.2 CV2)."
        ),
    }


def fidelity_audit_honesty_signal(tripwire: Any = None) -> dict[str, Any]:
    """FT3 — does the semantic-fidelity audit honestly LABEL itself advisory (``warn_only``
    + a claim fence) rather than silently passing unsourced framing?

    ``SEMANTIC_TRIPWIRE`` declares ``mode == "warn_only"``, a ``disposition``, and a
    ``claim_fence`` prose that scopes exactly what the heuristic does and does NOT assert
    (it does NOT claim comprehensive semantic claim↔source faithfulness). That honest
    self-labelling — a WARN transparently declared, not a silent pass — is the FACT this
    reader reports; the LEVEL is a §4 judgment-with-evidence (``level_from_signal`` returns
    ``None``). Read-only. FIX-4: an unimportable / non-mapping tripwire → ``status=
    "unavailable"`` (never read the label-absent as honest).
    """
    trip = _read_semantic_tripwire(tripwire)
    if trip is None:
        return {
            "status": "unavailable",
            "source": "app.specialists._shared.source_fidelity_audit.SEMANTIC_TRIPWIRE",
        }
    try:
        mode = trip.get("mode")
        claim_fence = trip.get("claim_fence")
        disposition = trip.get("disposition")
        gates_production = trip.get("gates_production")
    except Exception:  # noqa: BLE001
        return {
            "status": "unavailable",
            "source": "app.specialists._shared.source_fidelity_audit.SEMANTIC_TRIPWIRE",
        }
    labels_warn_only = mode == "warn_only"
    has_claim_fence = isinstance(claim_fence, str) and bool(claim_fence.strip())
    return {
        "status": "ok",
        "source": "SEMANTIC_TRIPWIRE.{mode,claim_fence,disposition}",
        "mode": mode,
        "labels_warn_only": labels_warn_only,
        "has_claim_fence": has_claim_fence,
        "disposition": disposition,
        "gates_production": gates_production,
        # honest advisory transparency = it labels itself warn_only AND scopes its claim
        # fence — a WARN transparently declared, NOT a silent pass of unsourced framing.
        "advisory_transparency": labels_warn_only and has_claim_fence,
        "note": (
            "the audit transparently labels itself warn_only with an explicit claim_fence "
            "(it does NOT assert comprehensive semantic claim↔source faithfulness) — an "
            "honestly-declared advisory, not a silent pass. This is report-time honesty, "
            "NOT a gate (gates_production stays False — see FT1)."
        ),
    }


def fidelity_leak_count_signal(inventory_path: Path | None = None) -> dict[str, Any]:
    """fidelity leak-count — count ``fid_leak:``-tagged OPEN entries in the deferred
    inventory (a FOURTH per-dimension namespace, disjoint from ``did_leak:`` /
    ``cost_leak:`` / ``cov_leak:``).

    Same scoping as the sibling leak-count readers (fenced code / HTML comments / archived
    section stripped; line-anchored tag). **1 today** (the WARN-only-semantic-fence leak in
    the ``## Fidelity-Trust Scorecard Leak Registry``). Fail-soft: unreadable file →
    ``{"status": "unavailable", "fidelity_leak_count": None}``.
    """
    p = inventory_path or (_repo_root() / _DEFERRED_INVENTORY_REL)
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return {
            "status": "unavailable",
            "source": _DEFERRED_INVENTORY_REL,
            "fidelity_leak_count": None,
        }
    open_text = _strip_archived_section(_strip_html_comments(_strip_fenced_code(text)))
    count = len(_FIDELITY_LEAK_LINE_RE.findall(open_text))
    return {
        "status": "ok",
        "source": _DEFERRED_INVENTORY_REL,
        "fidelity_leak_count": count,
    }


# ============================ capability-honesty (Q3.1) ============================
#
# Signal readers over the EXISTING front-door capability ledger (GL-15 — reuse, NO
# parallel plumbing): the per-component ``CapabilityTier`` in
# ``app/marcus/lesson_plan/bundle_catalog.py`` (``CAPABILITY_TIERS``), reconciled
# READ-ONLY against a small, BOUNDED, curated produced-evidence signal (the recorded
# DID-Leak-5 evidence). ⛔ This module NEVER edits a tier — tier bumps are party-gated
# governance (CLAUDE.md pack-versioning + the DID-Leak-5 entry). It SCORES the honesty of
# the tiers; it consumes ``bundle_catalog`` read-only via a DEFERRED local import (GL-3
# clean-leaf). Every reader is fail-soft per field — it never raises and never invents a
# clean value.
#
# PHASING FLAG (Q2-retro AI-Q2d, binding): the produced-evidence signal is the small
# curated DID-Leak-5 set, NOT a full trial-artifact scanner. The deep "scan every trial run
# for produced artifacts" reconciliation is a split TODO (deferred-work.md).

#: ``cap_leak:`` tag, anchored to line start — a FIFTH per-dimension namespace disjoint
#: from ``did_leak:`` / ``cost_leak:`` / ``cov_leak:`` / ``fid_leak:`` so the capability
#: count/identity reconciliation never collides with the other four. 1 today (the workbook
#: tier-lags-produced-reality leak — a CONSERVATIVE/understating coherence gap).
_CAPABILITY_LEAK_LINE_RE = re.compile(r"(?m)^[\s>]*(?:[-*+]\s+)?cap_leak:")

#: The ``CapabilityTier`` values that assert a component has NEVER produced a real artifact.
#: ``CapabilityTier`` is a FOUR-value enum: BOTH ``mechanism_only_never_produced`` ("design/
#: mechanism landed, never produced") AND ``shelf`` ("named but not built (placeholder)" —
#: strictly further from produced reality) assert never-produced. A component carrying EITHER
#: while a produced artifact demonstrably exists is the DID-Leak-5 LAG (a CONSERVATIVE/
#: understating coherence gap — fail-safe, NOT an overclaim). Hand-mirrored from
#: ``bundle_catalog.CapabilityTier``; anti-drift-pinned
#: (test_capability_mirrored_tier_constants_match_source) so a future rename OR a NEW
#: unclassified tier reds the test rather than silently mis-reconciling / false-cleaning.
_NEVER_PRODUCED_TIERS: frozenset[str] = frozenset(
    {"mechanism_only_never_produced", "shelf"}
)
#: The tiers that ASSERT a component was produced at some point (proven now, or once-proven-
#: now-regressed-repairable). A component carrying one of these while curated evidence says
#: it was NEVER produced would be the OVERSTATING direction (the worse believed-green gap) —
#: none exist today. Hand-mirrored + anti-drift-pinned (same test). Together with
#: ``_NEVER_PRODUCED_TIERS`` this COVERS every ``CapabilityTier`` member (enum-coverage pin).
_PROVEN_TIERS: frozenset[str] = frozenset(
    {"proven_wired", "proven_regressed_repairable"}
)

#: BOUNDED, curated produced-evidence signal (PHASING FLAG — NOT a trial-artifact scanner).
#: The recorded DID-Leak-5 evidence: the workbook companion produced real MD+DOCX on the
#: FROZEN Tejal P2 lesson (trial ``a940c5eb``; LO-verified ``8b275e5b``). ``produced=True``
#: means "a real artifact demonstrably exists"; the honest tier is ``proven-on-frozen-lesson``
#: (off-frozen-lesson stays an open claim — NOT blanket ``proven_wired``).
_CURATED_PRODUCED_EVIDENCE: Mapping[str, Mapping[str, Any]] = MappingProxyType(
    {
        "workbook": MappingProxyType(
            {
                "produced": True,
                "honest_tier": "proven-on-frozen-lesson",
                "lesson_scope": "frozen Tejal P2 (off-frozen-lesson stays an open claim)",
                "evidence_refs": (
                    "trial a940c5eb (first complete workbook MD+DOCX)",
                    "LO-verified 8b275e5b (6/6 LOs, frozen Tejal P2)",
                ),
            }
        ),
    }
)


def _read_capability_tiers(tiers: Any = None) -> dict[str, Any] | None:
    """Coerce the capability-tier source into a ``{component: tier_str}`` mapping, or
    ``None`` (fail-soft).

    ``tiers is None`` → consult the REAL ``CAPABILITY_TIERS`` registry via a DEFERRED
    import (GL-3 — no module-scope ``app.*``), READ-ONLY. An injectable ``Mapping`` reads a
    SEEDED tier posture (the reachable close-path / the isolating pin) WITHOUT touching the
    real registry — values may be plain ``str`` tiers OR ``ComponentCapability``-like objects
    carrying a ``.tier``. A non-mapping / unimportable source degrades to ``None``.
    """
    if tiers is not None:
        if not isinstance(tiers, Mapping):
            return None
        out: dict[str, Any] = {}
        for name, value in tiers.items():
            if isinstance(value, str):
                out[name] = value
            else:  # a ComponentCapability-like object carrying a .tier
                tier = getattr(value, "tier", None)
                out[name] = tier if isinstance(tier, str) else None
        return out
    try:
        from app.marcus.lesson_plan.bundle_catalog import CAPABILITY_TIERS
    except Exception:  # noqa: BLE001 — a signal read must never raise into a caller
        return None
    try:
        return {
            name: (cap.tier if isinstance(getattr(cap, "tier", None), str) else None)
            for name, cap in CAPABILITY_TIERS.items()
        }
    except Exception:  # noqa: BLE001
        return None


def capability_tier_reconciliation_signal(
    tiers: Any = None, produced_evidence: Any = None
) -> dict[str, Any]:
    """CH1/CH2 — reconcile the front-door capability TIERS against produced reality.

    Reads the REAL ``bundle_catalog`` ``CAPABILITY_TIERS`` (read-only, deferred import) +
    the BOUNDED curated produced-evidence set, and flags the DID-Leak-5 pattern —
    **a component tiered ``mechanism_only_never_produced`` for which a produced artifact
    demonstrably exists** (workbook, per the recorded evidence). That is a LAG: the declared
    tier UNDERSTATES produced reality (a CONSERVATIVE/fail-safe coherence gap, NOT an
    overclaim). The opposite — a component tiered proven while curated evidence says it was
    NEVER produced — is the worse OVERSTATING direction (none today).

    **Consults the REAL mismatch condition (CV2/FT2 lesson):** a lag is flagged only when
    ``produced is True`` AND ``tier == mechanism_only_never_produced`` — NOT on mere tier
    presence. A component tiered ``mechanism_only_never_produced`` with NO produced-evidence
    is HONEST (not a mismatch). The isolating pin varies the produced-evidence axis while
    holding the tier to prove a raw-tier-only regression can't ship green.

    ``tiers_match_produced_reality`` is ``True`` iff there is NO lag AND NO overstatement —
    the SIGNAL-DERIVED CH1 level keys off it (True → strong; the reachable close-path: a
    party-ratified tier that matches reality → no mismatch → strong, and the pin never blocks
    that honest upgrade). ``no_overstatement`` (the worse direction absent) is the fact CH2
    (judgment-with-evidence) rests its §5.6 ``strong`` on.

    ⛔ READ-ONLY: this NEVER edits a tier (party-gated governance). Fail-soft: an unimportable
    / non-mapping / empty tier source degrades to ``status="unavailable"`` (never a clean or
    silently-``False`` coherence claim).
    """
    tier_map = _read_capability_tiers(tiers)
    if not isinstance(tier_map, dict) or not tier_map:
        return {
            "status": "unavailable",
            "source": "app.marcus.lesson_plan.bundle_catalog.CAPABILITY_TIERS",
        }
    evidence = (
        produced_evidence
        if isinstance(produced_evidence, Mapping)
        else _CURATED_PRODUCED_EVIDENCE
    )
    lag_mismatches: list[dict[str, Any]] = []
    overstatement_mismatches: list[dict[str, Any]] = []
    unreconciled: list[dict[str, Any]] = []
    reconciled_count = 0
    for component, ev in evidence.items():
        if not isinstance(ev, Mapping):
            continue
        produced = ev.get("produced")
        tier = tier_map.get(component)
        # A component is RECONCILED only when its tier is a readable ``str`` AND ``produced``
        # is a real ``bool``. Anything else — an absent/typo'd component (tier None), an
        # unreadable/None tier, or a non-bool ``produced`` — is UNKNOWN, never certified clean
        # (the CV2/FT2 principle: never read clean on an unchecked/unreadable input). It is
        # SURFACED in ``unreconciled`` (not silently dropped), and does NOT count toward
        # coherence.
        if not isinstance(tier, str) or not isinstance(produced, bool):
            unreconciled.append(
                {
                    "component": component,
                    "declared_tier": tier if isinstance(tier, str) else None,
                    "produced": produced if isinstance(produced, bool) else None,
                    "reason": (
                        "tier not readable"
                        if not isinstance(tier, str)
                        else "produced is not a bool"
                    ),
                }
            )
            continue
        reconciled_count += 1
        if produced and tier in _NEVER_PRODUCED_TIERS:
            # LAG: the tier asserts "never produced" (mechanism_only_never_produced OR shelf)
            # but a produced artifact demonstrably exists → declared reality LAGS produced
            # reality (conservative/understating).
            lag_mismatches.append(
                {
                    "component": component,
                    "declared_tier": tier,
                    "honest_tier": ev.get("honest_tier"),
                    "lesson_scope": ev.get("lesson_scope"),
                    "evidence_refs": list(ev.get("evidence_refs") or ()),
                }
            )
        elif not produced and tier in _PROVEN_TIERS:
            # OVERSTATEMENT: the tier claims produced while curated evidence says NEVER
            # produced → the worse believed-green direction (none today).
            overstatement_mismatches.append(
                {
                    "component": component,
                    "declared_tier": tier,
                    "evidence_refs": list(ev.get("evidence_refs") or ()),
                }
            )
    if reconciled_count == 0:
        # Nothing was ACTUALLY reconciled (empty evidence, all-unreadable tiers, absent/typo'd
        # components, non-bool produced). "Nothing reconcilable" is UNKNOWN, NOT coherent — a
        # clean/strong verdict here would be an over-claim on an unchecked input (CV2/FT2).
        return {
            "status": "unavailable",
            "source": (
                "app.marcus.lesson_plan.bundle_catalog.CAPABILITY_TIERS + curated "
                "produced-evidence (DID-Leak-5)"
            ),
            "reconciled_count": 0,
            "unreconciled": unreconciled,
            "note": (
                "no component was actually reconciled (tier readable AND produced a real "
                "bool) — an unchecked/unreadable input is UNKNOWN, never certified coherent."
            ),
        }
    coherent = not lag_mismatches and not overstatement_mismatches
    if lag_mismatches and not overstatement_mismatches:
        direction = "conservative-understatement"
    elif overstatement_mismatches:
        direction = "overstatement"
    else:
        direction = "none"
    return {
        "status": "ok",
        "source": (
            "app.marcus.lesson_plan.bundle_catalog.CAPABILITY_TIERS + curated "
            "produced-evidence (DID-Leak-5)"
        ),
        "tiers": tier_map,
        "reconciled_count": reconciled_count,
        "unreconciled": unreconciled,
        "lag_mismatches": lag_mismatches,
        "overstatement_mismatches": overstatement_mismatches,
        "tiers_match_produced_reality": coherent,
        "no_overstatement": not overstatement_mismatches,
        "mismatch_direction": direction,
        "note": (
            "the reconciliation reads bundle_catalog tiers READ-ONLY against a bounded "
            "curated produced-evidence set and flags the DID-Leak-5 pattern (a component "
            "tiered mechanism_only_never_produced for which a produced artifact exists — "
            "workbook). The workbook lag UNDERSTATES produced reality (conservative/fail-safe, "
            "greys the bundle), it does NOT overstate; no tier claims proven while never "
            "produced. The real mismatch condition is declared-tier-vs-produced-evidence, "
            "NOT mere tier presence (CV2/FT2). Close-path reachable + read-only: a "
            "party-ratified tier that matches reality → no mismatch → strong. ⛔ NEVER edits a "
            "tier (party-gated). Cross-links DID Leak-5 (workbook-capability-tier-honesty-lag), "
            "counted once under cap_leak:, not double-counted. BOUNDED reconciliation — the "
            "full trial-artifact scan is a split TODO (PHASING FLAG)."
        ),
    }


def capability_leak_count_signal(inventory_path: Path | None = None) -> dict[str, Any]:
    """capability leak-count — count ``cap_leak:``-tagged OPEN entries in the deferred
    inventory (a FIFTH per-dimension namespace, disjoint from ``did_leak:`` / ``cost_leak:``
    / ``cov_leak:`` / ``fid_leak:``).

    Same scoping as the sibling leak-count readers (fenced code / HTML comments / archived
    section stripped; line-anchored tag). **1 today** (the workbook tier-lags-produced-reality
    leak in the ``## Capability-Honesty Scorecard Leak Registry``). Fail-soft: unreadable file
    → ``{"status": "unavailable", "capability_leak_count": None}``.
    """
    p = inventory_path or (_repo_root() / _DEFERRED_INVENTORY_REL)
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return {
            "status": "unavailable",
            "source": _DEFERRED_INVENTORY_REL,
            "capability_leak_count": None,
        }
    open_text = _strip_archived_section(_strip_html_comments(_strip_fenced_code(text)))
    count = len(_CAPABILITY_LEAK_LINE_RE.findall(open_text))
    return {
        "status": "ok",
        "source": _DEFERRED_INVENTORY_REL,
        "capability_leak_count": count,
    }


# ============================ tracker-coherence (Q3.2) ============================
#
# Signal readers over the EXISTING status-tracker qualifiers (GL-15 — reuse, NO parallel
# plumbing): progress_map.qualify_sources() (the divergence signal across the status
# trackers — sprint-status.yaml + SESSION-HANDOFF.md + next-session-start-here.md, incl.
# the cross-tracker next_step_conflict check) and doc_drift_monitor.get_changed_files()
# (the code↔doc drift signal). ⛔ READ-ONLY: this module NEVER edits a tracker or its
# tooling — it CONSUMES the qualifier output and SCORES the coherence. This is the ONLY
# FULLY-COMPUTED dimension (GL-7): BOTH criteria are signal-derived — there is NO
# hand-authored judgment level (a hand-judged coherence score would be believed-green in
# the very dimension that scores believed-green). The tracker tooling is reached ONLY via
# deferred LOCAL imports (GL-3 clean-leaf; ``scripts.*`` is not ``app.*``, but a deferred
# import keeps the import graph unchanged and matches the sibling pattern). Every reader is
# fail-soft per field — it never raises and never invents a clean value.
#
# ⚠️ Measures the EXTERNAL status trackers ONLY. The scorecard's OWN internal coherence
# (machine block ↔ history ↔ registry) is already pinned by Q1.3 (mirror + leak-identity);
# reconciling that here would be the self-referential recursion the scope fence forbids.

#: ``trk_leak:`` tag, anchored to line start — a SIXTH per-dimension namespace disjoint
#: from ``did_leak:`` / ``cost_leak:`` / ``cov_leak:`` / ``fid_leak:`` / ``cap_leak:`` so the
#: tracker-coherence count/identity reconciliation never collides with the other five. May be
#: 0 (the FIRST dimension that can carry zero leaks): today 2 (TC1 the qualify_sources STRUCTURAL
#: divergence — orphan-stories; TC2 the code↔doc drift monitoring is advisory / never-gates).
_TRACKER_LEAK_LINE_RE = re.compile(r"(?m)^[\s>]*(?:[-*+]\s+)?trk_leak:")

#: qualify_sources finding checks that are TIME-BASED (wall-clock staleness of ``last_updated``)
#: rather than STRUCTURAL tracker divergence. EXCLUDED from TC1's coherence verdict (FIX-B) so
#: the level is DETERMINISTIC: a structurally-coherent tracker set must NEVER flip CLEAN→DEGRADED
#: purely because time elapsed (that would mislabel "stale" as "divergent" and flap the golden/
#: mirror on a different day). Staleness is the CLI ``--check`` nag's concern, not coherence.
_TIME_BASED_QUALIFY_CHECKS: frozenset[str] = frozenset({"staleness", "last_updated"})
#: The qualify_sources finding levels (mirrored). A finding carrying any other ``level`` is a
#: malformed shape → ``unavailable`` (never a clean coherence claim).
_QUALIFY_FINDING_LEVELS: frozenset[str] = frozenset({"ok", "warn", "error"})

_TRACKER_SRC = "scripts.utilities.progress_map.qualify_sources"
_DOC_DRIFT_SRC = "scripts.utilities.doc_drift_monitor"


def _qualify_verdict(errors: int, warnings: int) -> str:
    """The qualify_sources verdict rule (errors→FAIL, warnings→DEGRADED, else CLEAN), applied to
    a chosen finding subset. TC1 applies it to the STRUCTURAL findings only."""
    if errors:
        return "FAIL"
    if warnings:
        return "DEGRADED"
    return "CLEAN"


def tracker_coherence_signal(qualify_result: Any = None) -> dict[str, Any]:
    """TC1 — the tracker-DIVERGENCE coherence signal over the EXISTING status-tracker
    qualifier (``progress_map.qualify_sources``).

    ``qualify_sources`` reconciles the status trackers (sprint-status.yaml + SESSION-HANDOFF.md
    + next-session-start-here.md — existence / YAML / expected-headings / status-vocab /
    orphan-stories / staleness AND the cross-tracker ``next_step_conflict`` check). This reader
    CONSUMES its ``findings`` READ-ONLY and derives a **STRUCTURAL** coherence verdict — a CLEAN
    structural verdict means the trackers are mutually coherent; DEGRADED means soft structural
    divergences (warnings); FAIL means hard ones (errors).

    **FIX-B (deterministic):** the verdict is recomputed from the STRUCTURAL findings only —
    TIME-BASED staleness findings (:data:`_TIME_BASED_QUALIFY_CHECKS`) are EXCLUDED, so a
    structurally-coherent tracker set does not flip CLEAN→DEGRADED purely because time elapsed.
    **FIX-C (verdict↔count reconcile):** if the input carries its own ``verdict`` / count fields
    they MUST be internally consistent with the ``findings`` tally (qualify_sources' own
    all-findings verdict) — a contradictory shape (e.g. ``{verdict: CLEAN, warning_count: 3}``)
    is UNEXPECTED → ``unavailable``, never coerced to coherent.

    **SIGNAL-DERIVED + reachable close-path:** the level keys off the recomputed structural
    verdict (not a hardcoded value) — reconcile the trackers to a CLEAN structural verdict and
    TC1 earns ``strong``. **Consult-real-signal, nothing-checked→unavailable (Q3.1 FIX-3):** a
    missing/non-list ``findings``, a malformed finding, or an unimportable/raising qualifier
    degrades to ``unavailable`` — "we could not actually qualify the trackers" is UNKNOWN, NEVER
    silently ``coherent``.

    ``qualify_result is None`` → consult the REAL ``qualify_sources()`` via a DEFERRED import
    (GL-3 — no module-scope ``app.*``/``scripts.*``); an injectable ``Mapping`` reads a SEEDED
    posture (a coherent or seeded-divergent fixture result) WITHOUT running the live qualifier.
    """
    result = qualify_result
    if result is None:
        try:
            from scripts.utilities.progress_map import qualify_sources

            result = qualify_sources()
        except Exception:  # noqa: BLE001 — a signal read must never raise into a caller
            return {"status": "unavailable", "source": _TRACKER_SRC}
    if not isinstance(result, Mapping):
        return {"status": "unavailable", "source": _TRACKER_SRC}
    findings = result.get("findings")
    # The findings list is the SSOT for divergence. A missing/non-list findings list means we
    # cannot actually assess structural coherence → UNKNOWN, never coherent (Q3.1 FIX-3).
    if not isinstance(findings, list):
        return {"status": "unavailable", "source": _TRACKER_SRC}
    all_err = all_warn = struct_err = struct_warn = 0
    for f in findings:
        if not isinstance(f, Mapping):
            return {"status": "unavailable", "source": _TRACKER_SRC}  # malformed finding shape
        level = f.get("level")
        if level not in _QUALIFY_FINDING_LEVELS:
            return {"status": "unavailable", "source": _TRACKER_SRC}  # malformed level
        chk = f.get("check")
        time_based = isinstance(chk, str) and chk in _TIME_BASED_QUALIFY_CHECKS
        if level == "error":
            all_err += 1
            if not time_based:
                struct_err += 1
        elif level == "warn":
            all_warn += 1
            if not time_based:
                struct_warn += 1
    # FIX-C: a supplied verdict / count must reconcile with the ALL-findings tally (what
    # qualify_sources itself computes). A contradiction is an unexpected/malformed shape.
    in_verdict = result.get("verdict")
    if in_verdict is not None and in_verdict != _qualify_verdict(all_err, all_warn):
        return {"status": "unavailable", "source": _TRACKER_SRC}
    in_err = result.get("error_count")
    if in_err is not None and (
        not isinstance(in_err, int) or isinstance(in_err, bool) or in_err != all_err
    ):
        return {"status": "unavailable", "source": _TRACKER_SRC}
    in_warn = result.get("warning_count")
    if in_warn is not None and (
        not isinstance(in_warn, int) or isinstance(in_warn, bool) or in_warn != all_warn
    ):
        return {"status": "unavailable", "source": _TRACKER_SRC}
    structural_verdict = _qualify_verdict(struct_err, struct_warn)
    return {
        "status": "ok",
        "source": _TRACKER_SRC,
        # STRUCTURAL verdict (time-based staleness excluded — FIX-B). ``raw_verdict`` keeps the
        # all-findings verdict as evidence (so a staleness-only DEGRADED is visible but unscored).
        "verdict": structural_verdict,
        "raw_verdict": _qualify_verdict(all_err, all_warn),
        "error_count": struct_err,
        "warning_count": struct_warn,
        "divergence_count": struct_err + struct_warn,
        "trackers_coherent": structural_verdict == "CLEAN",
        "note": (
            "the coherence verdict is recomputed from qualify_sources' STRUCTURAL findings only "
            "(orphan_stories / next_step_conflict / heading & structure drift / status-vocab / "
            "epic-presence) — TIME-BASED staleness findings are EXCLUDED (FIX-B: deterministic; a "
            "structurally-coherent set never flips CLEAN→DEGRADED because time passed). CLEAN→"
            "strong, DEGRADED→partial, FAIL→weak — no human judgment (GL-7 fully-computed). "
            "DEGRADED→partial is COARSE by design (FIX-E: divergence_count is surfaced as "
            "evidence, not scaled into the level). A supplied verdict/count that contradicts the "
            "findings tally → unavailable (FIX-C). Close-path reachable: reconcile the trackers to "
            "a CLEAN structural verdict → trackers_coherent=True → TC1 earns strong. Nothing-"
            "checked (unimportable qualifier, missing/malformed findings) → unavailable, NEVER "
            "silently coherent."
        ),
    }


def tracker_doc_drift_signal(monitor: Any = None) -> dict[str, Any]:
    """TC2 — the code↔doc drift-MONITORING POSTURE signal over the EXISTING drift monitor
    (``scripts/utilities/doc_drift_monitor.py``).

    **FIX-A (the design fix): measures the STABLE monitoring/gating POSTURE, NOT the volatile
    per-commit drift.** The prior design ran ``git HEAD~1..HEAD`` at scorecard-read time and
    mapped the *current commit's* drift into a PERSISTED machine-block level — a latent
    time-bomb (the level flipped on every commit that touched only code, red-ing the
    fully-computed + arithmetic pins), and it could false-clean on git-unavailable and hang on a
    stuck git subprocess. This reader instead asks the STABLE question every other scorecard
    fence asks: **is code↔doc drift monitoring WIRED, and does it GATE a production run or is it
    ADVISORY?** — mirroring coverage-gate default-OFF (CV1) / semantic-fence WARN-only (FT1).
    It does NOT call git / run the drift diff.

    Honest today: ``doc_drift_monitor`` EXISTS (monitoring wired) but is an ADVISORY pre-push/CI
    heuristic — ``check_documentation_drift`` prints ✅/⚠ and at most ``sys.exit``s as a
    non-blocking hook; it exposes NO production-gate affordance (no ``gates_production`` flag,
    not wired into ``production_runner``) → the fence-not-gating pattern → ``weak`` (mechanism
    exists, never gates), DETERMINISTIC. **Reachable close-path (grounded in the real module):**
    if the monitor gains a truthy ``gates_production`` affordance (a real production gate) this
    reader detects it → ``strong``. Monitoring UNIMPORTABLE / substrate absent → ``unavailable``
    (never a clean or silently-``False`` gating claim).

    ``monitor is None`` → consult the REAL ``doc_drift_monitor`` module via a DEFERRED import
    (GL-3; importing the module runs NO git — the git calls live inside functions this reader
    never invokes). An injectable module-like object reads a SEEDED posture (wired / gating /
    absent) WITHOUT touching the real module.
    """
    mod = monitor
    if mod is None:
        try:
            import scripts.utilities.doc_drift_monitor as mod  # noqa: PLC0415 — deferred (GL-3)
        except Exception:  # noqa: BLE001 — a signal read must never raise into a caller
            return {"status": "unavailable", "source": _DOC_DRIFT_SRC}
    # monitoring WIRED == the real drift-check functions exist (importing runs no git).
    monitoring_wired = callable(
        getattr(mod, "check_documentation_drift", None)
    ) and callable(getattr(mod, "get_changed_files", None))
    if not monitoring_wired:
        return {
            "status": "unavailable",
            "source": _DOC_DRIFT_SRC,
            "monitoring_wired": False,
        }
    # gates_production: derived from the REAL module (not a hardcoded verdict). Today the monitor
    # exposes no such affordance → False → advisory (weak). If wired to gate → True → strong.
    gates_production = bool(getattr(mod, "gates_production", False))
    return {
        "status": "ok",
        "source": _DOC_DRIFT_SRC,
        "monitoring_wired": True,
        "gates_production": gates_production,
        "note": (
            "doc_drift_monitor is a code↔doc drift heuristic that EXISTS (monitoring wired) but is "
            "an ADVISORY pre-push/CI hook (check_documentation_drift prints ✅/⚠ and at most "
            "sys.exits non-blocking; no gates_production affordance, not wired into "
            "production_runner) — it does NOT gate a production run → the fence-not-gating pattern "
            "(like coverage default-OFF / fidelity WARN-only) → weak. NO git is run at read time "
            "(the posture is STABLE, not per-commit — FIX-A). Close-path reachable + grounded in "
            "the real module: wire the monitor to gate production (a truthy gates_production) → "
            "this reports gates_production=True → strong. Substrate absent/unimportable → "
            "unavailable, never a clean gating claim."
        ),
    }


def tracker_leak_count_signal(inventory_path: Path | None = None) -> dict[str, Any]:
    """tracker leak-count — count ``trk_leak:``-tagged OPEN entries in the deferred inventory
    (a SIXTH per-dimension namespace, disjoint from ``did_leak:`` / ``cost_leak:`` /
    ``cov_leak:`` / ``fid_leak:`` / ``cap_leak:``).

    Same scoping as the sibling leak-count readers (fenced code / HTML comments / archived
    section stripped; line-anchored tag). **2 today** (TC1 the qualify_sources STRUCTURAL
    divergence + TC2 the advisory-not-gating drift-monitoring leak, in the
    ``## Governance/Tracker-Coherence Scorecard Leak Registry``) — but this is the FIRST
    dimension whose count may legitimately be **0** (if the trackers reconcile to CLEAN),
    which the leak-count identity pin (``_reconcile(0, 0)``) and ``leak_coverage_gaps``
    (``open_leaks <= 0`` is not a gap) both handle cleanly. Fail-soft: unreadable file →
    ``{"status": "unavailable", "tracker_leak_count": None}``.
    """
    p = inventory_path or (_repo_root() / _DEFERRED_INVENTORY_REL)
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return {
            "status": "unavailable",
            "source": _DEFERRED_INVENTORY_REL,
            "tracker_leak_count": None,
        }
    open_text = _strip_archived_section(_strip_html_comments(_strip_fenced_code(text)))
    count = len(_TRACKER_LEAK_LINE_RE.findall(open_text))
    return {
        "status": "ok",
        "source": _DEFERRED_INVENTORY_REL,
        "tracker_leak_count": count,
    }


# ============================ lane-discipline / scope-fidelity (Q3.3) ============================
#
# Signal reader over the LIVE import-linter result via the SHIPPED ``importlinter.api`` (GL-16 —
# NOT the ``lint-imports`` CLI on PATH): ``pyproject.toml [tool.importlinter]`` declares the
# lane/scope contracts (Marcus M1/M2, Cora C1, lane-isolation D3/D4, etc.); the reader runs them
# programmatically and reads the REAL kept/broken RESULT. ⛔ READ-ONLY: this SCORES the
# already-CI-enforced lane isolation; it adds NO enforcement and NEVER edits a contract (GL-15).
# The ``importlinter`` dep is THIRD-PARTY (not ``app.*``, so the clean-leaf guard does not require
# it deferred) but is reached ONLY via a DEFERRED local import (GL-3-consistent — keeps the app/
# import graph unchanged + matches the sibling deferred pattern). The read is DETERMINISTIC
# (import-linter breaks ONLY on a real import-graph regression — a forbidden import — which SHOULD
# red the scorecard; unlike Q3.2's volatile git-drift this is a legitimate persisted-level signal)
# and BOUNDED (building the app/ import graph is ~seconds; guarded by try/except → ``unavailable``
# on ANY error). Fail-soft: importlinter unavailable / config missing / the run errors / nothing
# actually checked → ``unavailable``, NEVER clean (never report clean lane discipline from a linter
# that did not actually run — the Q3.1/Q3.2 nothing-checked→unavailable rule). Consults the REAL
# broken-count, NOT the DECLARED contract count (the isolating pin proves it).

#: ``lane_leak:`` tag, anchored to line start — a SEVENTH per-dimension namespace disjoint from
#: ``did_leak:`` / ``cost_leak:`` / ``cov_leak:`` / ``fid_leak:`` / ``cap_leak:`` / ``trk_leak:`` so
#: the lane count/identity reconciliation never collides with the other six. **0 today** (the
#: import-linter is 18/0 clean → the ZERO-LEAK path; a real broken contract or a documented
#: lane-matrix hole would register one).
_LANE_LEAK_LINE_RE = re.compile(r"(?m)^[\s>]*(?:[-*+]\s+)?lane_leak:")

#: The import-linter config the shipped dep reads (GL-16). ``pyproject.toml [tool.importlinter]``
#: declares 18 contracts today (root_packages=["app"]); the reader consults the REAL kept/broken
#: RESULT of running them, NOT this declared count.
_IMPORTLINTER_CONFIG_REL = "pyproject.toml"
_IMPORTLINTER_SRC = "importlinter.api / pyproject.toml [tool.importlinter]"
#: Watchdog bound for the LIVE import-linter build (FIX-E). The real ``app/`` graph build is ~0.4s;
#: a generous cap turns a pathological stuck build into an ``unavailable`` return instead of an
#: indefinite block. Read at call time so a test can shrink it to prove the timeout path.
_IMPORTLINTER_TIMEOUT_S: float = 60.0


def _coerce_count(value: Any) -> int | None:
    """A real non-negative ``int`` count, or ``None`` — a ``bool`` (int subclass), a negative, or a
    non-int is malformed and can never certify a clean level."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    return None


def _run_import_linter_live() -> Any:
    """Run the LIVE import-linter contracts via the SHIPPED ``importlinter.api`` (GL-16 — NOT the
    ``lint-imports`` CLI), returning a real importlinter ``Report`` — or ``None`` on ANY failure or
    a watchdog TIMEOUT. Never raises, never blocks indefinitely, never flashes a console spinner.

      * **BOUNDED (FIX-E):** the build runs in a daemon worker thread joined with
        :data:`_IMPORTLINTER_TIMEOUT_S`; a stuck/unbounded build → ``None`` (``unavailable``) within
        the bound rather than an indefinite block (a plain ``try/except`` catches raises but NOT a
        hang). ``signal.alarm`` is POSIX-only, so a worker-thread watchdog keeps this portable on
        Windows.
      * **NO console side-effects (FIX-A):** ``create_report`` renders a rich ``console.status`` +
        a transient ``Live`` progress bar during the multi-second build; a session-ramp / retro
        scorecard read must not flash a spinner. The build window is wrapped in
        ``redirect_stdout``/``redirect_stderr`` sinks AND the importlinter console is set
        ``quiet=True`` — so NOTHING reaches the real terminal. The redirect spans the join in the
        MAIN thread (not the worker), so a completed build restores the streams cleanly.
      * **GL-16 (shipped dep, NOT the CLI):** reads via ``read_user_options`` + ``create_report``
        (in-process; no subprocess, no ``lint_imports`` CLI wrapper).
    """
    holder: dict[str, Any] = {}

    def _worker() -> None:
        try:
            # DEFERRED local import (GL-3-consistent): importlinter is third-party; keeping it
            # function-local leaves the app/ import graph — the very thing being scored — unchanged.
            from importlinter.api import use_cases
            from importlinter.application.use_cases import _register_contract_types

            config = str(_repo_root() / _IMPORTLINTER_CONFIG_REL)
            user_options = use_cases.read_user_options(config_filename=config)
            # Built-in + plugin contract types must be registered before the report runs (the
            # `lint-imports` CLI does this internally). ``_register_contract_types`` is an internal
            # of ``importlinter`` — an anti-drift test (test_importlinter_register_seam_available)
            # fails LOUD if this seam moves in a future 2.x, so a dep upgrade reds a test rather
            # than silently degrading LD1 to ``unavailable`` while the doc/history claim ``strong``.
            _register_contract_types(user_options)
            holder["report"] = use_cases.create_report(user_options, cache_dir=None)
        except Exception as exc:  # noqa: BLE001 — a signal read must never raise into a caller
            holder["error"] = exc

    try:
        from importlinter.api import use_cases as _uc

        prev_quiet = _uc.console.quiet
    except Exception:  # noqa: BLE001 — importlinter unimportable → unavailable
        return None
    sink_out, sink_err = io.StringIO(), io.StringIO()
    try:
        _uc.console.quiet = True
        with redirect_stdout(sink_out), redirect_stderr(sink_err):
            worker = threading.Thread(
                target=_worker, name="lane-discipline-import-linter", daemon=True
            )
            worker.start()
            worker.join(_IMPORTLINTER_TIMEOUT_S)
    finally:
        _uc.console.quiet = prev_quiet
    if worker.is_alive():
        return None  # TIMEOUT — the build is stuck; return unavailable, never block, never clean
    if "error" in holder or "report" not in holder:
        return None
    return holder["report"]


def _read_import_linter_report(report: Any) -> dict[str, Any] | None:
    """Coerce an import-linter report source into a ``{kept, broken, could_not_run}`` mapping, or
    ``None`` (fail-soft).

    ``report is None`` → run the LIVE contracts via :func:`_run_import_linter_live` (GL-16 shipped
    dep, bounded, console-suppressed). An injectable ``Mapping`` (``{kept, broken}`` /
    ``{kept_count, broken_count}``) OR an object carrying ``.kept_count``/``.broken_count`` (a real
    ``Report`` or a hermetic fake) reads a SEEDED posture WITHOUT running the live linter — the
    fixture / isolating path. Any failure — including a HOSTILE report whose attribute access RAISES
    (FIX-F: a raising ``.kept_count`` property must not propagate) — degrades to ``None``, a
    fail-soft read that NEVER raises into a caller.
    """
    if report is None:
        report = _run_import_linter_live()
        if report is None:
            return None
    try:
        if isinstance(report, Mapping):  # a seeded fixture (prefer `kept`, else `kept_count`)
            kept = report["kept"] if "kept" in report else report.get("kept_count")
            broken = report["broken"] if "broken" in report else report.get("broken_count")
            return {
                "kept": kept,
                "broken": broken,
                "could_not_run": bool(report.get("could_not_run", False)),
            }
        # A real importlinter Report (or a hermetic fake) carrying the count attributes. A raising
        # property (a hostile report) is caught here → None (FIX-F), matching the live guarantee.
        kept = getattr(report, "kept_count", None)
        broken = getattr(report, "broken_count", None)
        if kept is None and broken is None:
            return None
        return {
            "kept": kept,
            "broken": broken,
            "could_not_run": bool(getattr(report, "could_not_run", False)),
        }
    except Exception:  # noqa: BLE001 — a hostile report must never raise into a caller
        return None


def import_linter_lane_signal(report: Any = None) -> dict[str, Any]:
    """LD1 — the LIVE import-linter lane-discipline signal via the SHIPPED ``importlinter.api``
    (GL-16 — NOT the ``lint-imports`` CLI).

    Runs the ``pyproject.toml [tool.importlinter]`` contracts programmatically and reports the REAL
    ``kept_count`` / ``broken_count``. ``lane_discipline_clean`` is ``broken_count == 0``. The
    level (see :func:`_level_ld_import_linter`) is a function of the REAL broken-count — 0 broken →
    ``strong`` (lane discipline clean, ALREADY the case today at 18/0); broken > 0 → ``weak`` (a
    real import-graph regression, a forbidden import that SHOULD red the scorecard) — NOT a function
    of the DECLARED contract count.

    ⛔ READ-ONLY (GL-15): SCORES the already-CI-enforced lanes; adds NO enforcement, edits NO
    contract. DETERMINISTIC + BOUNDED (the graph build is ~seconds, guarded). Fail-soft: an
    unimportable dep / missing config / a run error / ``could_not_run`` / nothing-actually-checked
    (``kept + broken == 0``) / malformed counts → ``unavailable`` — NEVER clean (never report clean
    lane discipline from a linter that did not actually run). This is an assessment-cadence read,
    not a hot loop (see §7 Cadence).
    """
    data = _read_import_linter_report(report)
    if data is None:
        return {"status": "unavailable", "source": _IMPORTLINTER_SRC}
    if data.get("could_not_run"):
        # invalid contract options → the linter could not actually run → UNKNOWN, never clean.
        return {
            "status": "unavailable",
            "source": _IMPORTLINTER_SRC,
            "note": "import-linter could_not_run (invalid contract options) — never clean.",
        }
    kept = _coerce_count(data.get("kept"))
    broken = _coerce_count(data.get("broken"))
    if kept is None or broken is None:
        return {"status": "unavailable", "source": _IMPORTLINTER_SRC}
    total = kept + broken
    if total <= 0:
        # NOTHING was actually evaluated (no contract ran) — UNKNOWN, never clean (the Q3.1/Q3.2
        # nothing-checked→unavailable rule). A clean lane-discipline claim requires a real run.
        return {
            "status": "unavailable",
            "source": _IMPORTLINTER_SRC,
            "note": "no contract was actually evaluated (kept+broken==0) — never clean.",
        }
    return {
        "status": "ok",
        "source": _IMPORTLINTER_SRC,
        "kept_count": kept,
        "broken_count": broken,
        "contracts_total": total,
        "lane_discipline_clean": broken == 0,
        "note": (
            "the LIVE import-linter result via the SHIPPED importlinter.api (GL-16 — NOT the "
            "lint-imports CLI on PATH): kept_count kept / broken_count broken; broken==0 → lane "
            "discipline clean → strong; broken>0 → weak (a REAL import-graph regression — a "
            "forbidden import — that SHOULD red the scorecard). The level keys off the REAL "
            "broken-count, NOT the DECLARED contract count (consult-real-result — the isolating "
            "pin proves it). DETERMINISTIC (a break is a real lane-discipline regression, not "
            "per-commit noise) + BOUNDED (the app/ graph build is ~seconds, guarded; any error → "
            "unavailable). READ-ONLY — SCORES the already-CI-enforced lanes, adds no enforcement."
        ),
    }


def lane_leak_count_signal(inventory_path: Path | None = None) -> dict[str, Any]:
    """lane leak-count — count ``lane_leak:``-tagged OPEN entries in the deferred inventory (a
    SEVENTH per-dimension namespace, disjoint from the other six).

    Same scoping as the sibling leak-count readers (fenced code / HTML comments / archived section
    stripped; line-anchored tag). **0 today** — the import-linter is 18/0 clean → the ZERO-LEAK
    path (a real broken contract or a documented lane-matrix hole would register a ``lane_leak:``).
    This is the SECOND dimension whose count may legitimately be **0**; ``_reconcile(0, 0)`` and
    ``leak_coverage_gaps`` (``open_leaks <= 0`` is not a gap) both handle it cleanly. Fail-soft:
    unreadable file → ``{"status": "unavailable", "lane_leak_count": None}``.
    """
    p = inventory_path or (_repo_root() / _DEFERRED_INVENTORY_REL)
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return {
            "status": "unavailable",
            "source": _DEFERRED_INVENTORY_REL,
            "lane_leak_count": None,
        }
    open_text = _strip_archived_section(_strip_html_comments(_strip_fenced_code(text)))
    count = len(_LANE_LEAK_LINE_RE.findall(open_text))
    return {
        "status": "ok",
        "source": _DEFERRED_INVENTORY_REL,
        "lane_leak_count": count,
    }


# ============================ signal → level derivation ============================
#
# THE anti-believed-green rule: a level is NEVER mechanically awarded a clean/uniform
# value from a proxy / unverified / unknown / malformed signal. Only C3 is purely
# mechanical. C2 (config-ref proxy) and C4 (unverified runtime bypass) can only
# DOWNGRADE mechanically; their machine-block 'strong' is a documented human JUDGMENT
# (derivation: judgment-with-evidence). Judgment criteria (C1/C5) return None.

_CLEAN_LEVELS = frozenset({"strong", "uniform"})


def _level_c3(signal: Any) -> str:
    """C3 (purely mechanical): 0/3 fences ON → weak; 1–2 → partial; 3 → strong; any
    non-``bool`` fence value (unknown posture) → ``"unavailable"``."""
    if not isinstance(signal, dict):
        return "unavailable"
    vals = [signal.get("fidelity"), signal.get("coverage"), signal.get("udac")]
    if any(not isinstance(v, bool) for v in vals):
        return "unavailable"
    enabled = sum(1 for v in vals if v)
    if enabled == 0:
        return "weak"  # fences EXIST but default OFF (not "absent")
    if enabled == len(vals):
        return "strong"
    return "partial"


def _level_c2(signal: Any) -> str:
    """C2 (proxy — NEVER clean mechanically): a detected boundary breach (an LLM ref on
    a gate → ``gates_all_model_config_ref_null`` False) → ``"partial"``; otherwise
    ``"unavailable"`` (the config-ref proxy cannot certify ``strong`` — that is the
    §1.6 judgment). Malformed / non-ok → ``"unavailable"``."""
    if not isinstance(signal, dict) or signal.get("status") != "ok":
        return "unavailable"
    if signal.get("gates_all_model_config_ref_null") is not True:
        return "partial"
    return "unavailable"


def _level_c4(signal: Any) -> str:
    """C4 (unverified — clean only on a real detector-0): digest absent → ``"weak"``;
    present + a detector-observed ``int == 0`` → capped ``"strong"``; present +
    ``int > 0`` → ``"partial"``; present + ``"undetected"`` → ``"partial"`` (cannot
    confirm clean); anything else unknown/malformed → ``"unavailable"``."""
    if not isinstance(signal, dict) or signal.get("status") != "ok":
        return "unavailable"
    present = signal.get("digest_module_present_on_disk")
    if not isinstance(present, bool):
        return "unavailable"
    if not present:
        return "weak"
    bypass = signal.get("silent_bypass_events")
    if isinstance(bypass, int) and not isinstance(bypass, bool):
        if bypass < 0:
            return "unavailable"
        return "strong" if bypass == 0 else "partial"
    if bypass == "undetected":
        return "partial"  # cannot confirm clean discipline — NON-clean, below strong
    return "unavailable"  # "unavailable" / unknown / malformed → NON-clean


def _level_ce_budget(signal: Any) -> str:
    """CE1 (purely mechanical, mirrors C3): a default budget wired + enforced →
    ``strong``; the brake EXISTS but is OPT-IN by default (``default_budget_enforced``
    False — ``check_trial_budget`` honours a cap but the preset sets none) → ``weak``
    (mechanism present, default OFF — NOT ``absent``); malformed / non-ok / unknown
    ``default_budget_enforced`` → ``unavailable``."""
    if not isinstance(signal, dict) or signal.get("status") != "ok":
        return "unavailable"
    enforced = signal.get("default_budget_enforced")
    if enforced is True:
        return "strong"
    if enforced is False:
        return "weak"
    return "unavailable"


def _level_cv_coverage_fence(signal: Any) -> str:
    """CV1 (purely mechanical, mirrors DID C3 / cost CE1): the coverage gate wired +
    enforced by default → ``strong``; the gate EXISTS but is OPT-IN by default
    (``default_coverage_enforced`` False — ``coverage_gate_active`` reads a default-OFF
    env the preset never sets) → ``weak`` (mechanism present, default OFF — NOT
    ``absent``); malformed / non-ok / unknown ``default_coverage_enforced`` →
    ``unavailable``."""
    if not isinstance(signal, dict) or signal.get("status") != "ok":
        return "unavailable"
    enforced = signal.get("default_coverage_enforced")
    if enforced is True:
        return "strong"
    if enforced is False:
        return "weak"
    return "unavailable"


def _level_ft_semantic_fence(signal: Any) -> str:
    """FT1 (purely mechanical, mirrors DID C3 / cost CE1 / coverage CV1): the semantic-
    fidelity audit gates production by default → ``strong``; the audit EXISTS but WARNs and
    never gates (``semantic_fence_gates`` False — ``SEMANTIC_TRIPWIRE['gates_production']``
    is False) → ``weak`` (mechanism present, never gates — NOT ``absent``); malformed /
    non-ok / unknown ``semantic_fence_gates`` → ``unavailable``."""
    if not isinstance(signal, dict) or signal.get("status") != "ok":
        return "unavailable"
    gates = signal.get("semantic_fence_gates")
    if gates is True:
        return "strong"
    if gates is False:
        return "weak"
    return "unavailable"


def _level_ch_reconciliation(signal: Any) -> str:
    """CH1 (purely mechanical, mirrors DID C3 / cost CE1 / coverage CV1 / fidelity FT1):
    the capability tiers match produced reality (no lag, no overstatement) → ``strong``;
    a mismatch exists (``tiers_match_produced_reality`` False — today the CONSERVATIVE
    workbook LAG) → ``weak`` (a coherence gap, fail-safe but still a gap — NOT ``absent``);
    malformed / non-ok / unknown ``tiers_match_produced_reality`` → ``unavailable``.

    Reachable close-path + read-only: a party-ratified tier that matches produced reality
    flips ``tiers_match_produced_reality`` True → ``strong`` (the pin never blocks the honest
    upgrade). The reader reads the REAL ``CAPABILITY_TIERS``, not a hardcoded verdict."""
    if not isinstance(signal, dict) or signal.get("status") != "ok":
        return "unavailable"
    coherent = signal.get("tiers_match_produced_reality")
    if coherent is True:
        return "strong"
    if coherent is False:
        return "weak"
    return "unavailable"


def _level_tc_divergence(signal: Any) -> str:
    """TC1 (purely mechanical, FULLY-COMPUTED — GL-7): the qualify_sources verdict across the
    status trackers → CLEAN (no divergences) → ``strong``; DEGRADED (warnings — soft
    divergences) → ``partial``; FAIL (errors — hard divergences) → ``weak``; non-ok / unknown
    verdict / malformed counts → ``unavailable`` (nothing-checked, never a clean coherence
    claim). NO human judgment — the level derives ENTIRELY from the real divergence signal.

    Reachable close-path: reconcile the trackers to CLEAN → ``trackers_coherent`` True → the
    derived level is ``strong`` (the reader reads the REAL verdict, not a hardcoded value)."""
    if not isinstance(signal, dict) or signal.get("status") != "ok":
        return "unavailable"
    verdict = signal.get("verdict")
    if verdict == "CLEAN":
        return "strong"
    if verdict == "DEGRADED":
        return "partial"
    if verdict == "FAIL":
        return "weak"
    return "unavailable"


def _level_tc_doc_drift(signal: Any) -> str:
    """TC2 (mechanical, FULLY-COMPUTED — GL-7; the fence-not-gating pattern, mirrors CV1/FT1):
    the code↔doc drift-monitoring POSTURE (FIX-A — STABLE, not per-commit). monitoring wired +
    gates production (``gates_production`` True) → ``strong`` (the reachable close-path); wired
    but ADVISORY (``gates_production`` False — the monitor exists but never gates) → ``weak``
    (mechanism exists, never gates); monitoring not wired / substrate absent / non-ok →
    ``unavailable`` (never a clean or silently-``False`` gating claim). NO human judgment."""
    if not isinstance(signal, dict) or signal.get("status") != "ok":
        return "unavailable"
    if signal.get("monitoring_wired") is not True:
        return "unavailable"
    gates = signal.get("gates_production")
    if gates is True:
        return "strong"
    if gates is False:
        return "weak"
    return "unavailable"


def _level_ld_import_linter(signal: Any) -> str:
    """LD1 (purely mechanical, SIGNAL-DERIVED): the LIVE import-linter kept/broken result.

    ``broken_count == 0`` → ``strong`` (lane discipline clean — the reachable close-path is ALREADY
    reached today, 18/0); ``broken_count > 0`` → ``weak`` (a REAL import-graph / lane regression —
    a forbidden import that SHOULD red the scorecard); non-ok / nothing-checked (``kept + broken
    <= 0``) / malformed counts → ``unavailable`` (never a clean claim from a linter that did not
    actually run). Keys off the REAL broken-count, NOT the DECLARED contract count — the isolating
    pin (a seeded ``broken > 0`` result) proves a raw declared-count reader can't ship green."""
    if not isinstance(signal, dict) or signal.get("status") != "ok":
        return "unavailable"
    broken = signal.get("broken_count")
    kept = signal.get("kept_count")
    if not isinstance(broken, int) or isinstance(broken, bool) or broken < 0:
        return "unavailable"
    if not isinstance(kept, int) or isinstance(kept, bool) or kept < 0:
        return "unavailable"
    if kept + broken <= 0:
        return "unavailable"  # nothing actually checked — NON-clean, never strong
    return "strong" if broken == 0 else "weak"


def level_from_signal(criterion_key: str, signal: Any) -> str | None:
    """Derive a criterion's level from its signal (the anti-believed-green rule).

    Total over each mechanical criterion's signal domain (never raises); for a
    proxy/unverified/unknown/malformed signal it returns a NON-clean level (never
    ``strong``/``uniform``) — the sole exception being C4 on a real detector-observed
    ``int == 0``, C3 on genuinely all-ON fences, CE1 on a real default budget wired, CV1
    on the coverage gate genuinely wired ON by default, FT1 on the semantic-fidelity
    audit genuinely gating production, and CH1 on the capability tiers genuinely matching
    produced reality. Q3.2 tracker_coherence is FULLY-COMPUTED (GL-7): BOTH TC1
    (``tracker_divergence_coherence``, on the qualify_sources verdict) and TC2
    (``tracker_doc_drift``, on the code↔doc drift heuristic — capped at partial) derive real
    levels here. Q3.3 lane_discipline LD1 (``lane_discipline_import_linter``) derives from the LIVE
    import-linter kept/broken result (0 broken → ``strong``; broken > 0 → ``weak``). Judgment /
    judgment-with-evidence-only criteria (C1/C5, cost CE2/CE3/CE4, coverage CV2/CV3, fidelity
    FT2/FT3, capability CH2) and unknown keys return ``None`` (no mechanical derivation; the human
    authors those).
    """
    if criterion_key == "fence_enforcement_default_on":
        return _level_c3(signal)
    if criterion_key == "bone_determinism":
        return _level_c2(signal)
    if criterion_key == "lock_and_contract_discipline":
        return _level_c4(signal)
    if criterion_key == "budget_stop_default_on":
        return _level_ce_budget(signal)
    if criterion_key == "coverage_fence_default_on":
        return _level_cv_coverage_fence(signal)
    if criterion_key == "semantic_fence_gating_on":
        return _level_ft_semantic_fence(signal)
    if criterion_key == "capability_tier_reconciliation_on":
        return _level_ch_reconciliation(signal)
    # Q3.2 — tracker_coherence is the ONLY FULLY-COMPUTED dimension (GL-7): BOTH criteria are
    # signal-derived (no judgment level). TC1 keys off the qualify_sources verdict; TC2 keys
    # off the code↔doc drift heuristic (capped at partial — a HEAD-only git proxy).
    if criterion_key == "tracker_divergence_coherence":
        return _level_tc_divergence(signal)
    if criterion_key == "tracker_doc_drift":
        return _level_tc_doc_drift(signal)
    # Q3.3 — lane_discipline LD1 is purely mechanical (SIGNAL-DERIVED): the LIVE import-linter
    # kept/broken result via the shipped importlinter.api (GL-16). 0 broken → strong (18/0 today);
    # broken>0 → weak (a real forbidden-import regression); nothing-checked/malformed → unavailable.
    if criterion_key == "lane_discipline_import_linter":
        return _level_ld_import_linter(signal)
    return None
