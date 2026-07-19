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

import os
import re
from contextlib import contextmanager
from pathlib import Path
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


def level_from_signal(criterion_key: str, signal: Any) -> str | None:
    """Derive a criterion's level from its signal (the anti-believed-green rule).

    Total over each mechanical criterion's signal domain (never raises); for a
    proxy/unverified/unknown/malformed signal it returns a NON-clean level (never
    ``strong``/``uniform``) — the sole exception being C4 on a real detector-observed
    ``int == 0``, and C3 on genuinely all-ON fences. Judgment criteria (C1/C5) and
    unknown keys return ``None`` (no derivation; the human authors those).
    """
    if criterion_key == "fence_enforcement_default_on":
        return _level_c3(signal)
    if criterion_key == "bone_determinism":
        return _level_c2(signal)
    if criterion_key == "lock_and_contract_discipline":
        return _level_c4(signal)
    return None
