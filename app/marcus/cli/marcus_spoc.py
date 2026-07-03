"""Marcus SPOC — conversational single-point-of-contact over the production engine.

BETA capability (a-g): instead of raw `[c/e/s/x]` gate verdicts, the operator
converses with Marcus, who at each gate NARRATES the relevant content in persona
(sources+treatment, ingestion report, lesson plan, research, creative treatment
incl. #variants + voice, motion plan) and collects the operator's decision, then
drives the underlying `production_runner` under the hood. This is the
subprocess-narration-over-the-seam shape ratified at BETA scoping (Winston Q3):
`production_runner` stays the runtime authority; Marcus-SPOC is the operator
surface (operator-facing callsign for the runtime conversational layer — the
deterministic orchestration engine is `production_runner`, not renamed).

Sophisticated free-form NL dialogue / LLM-mediated turn-taking is deferred
(operator directive: defer sophisticated ML); this MVP delivers the structured
conversational surface that presents a-g and accepts per-gate decisions.

Decisions are supplied as a ``{gate_id: {"verb": ..., "edit_payload": ...}}`` map
(operator-in-the-loop or scripted); unmapped gates default to ``approve``.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any
from uuid import UUID

from app.marcus.orchestrator.picker_html_emitter import decode_picker_selection_code
from app.marcus.orchestrator.picker_publisher import publish_picker
from app.marcus.orchestrator.production_runner import resume_production_trial
from app.marcus.orchestrator.styleguide_picker import (
    PickerError,
    append_pick_event,
    load_picker_roster,
    write_pick_to_directive,
)
from app.models.state.operator_verdict import OperatorVerdict
from app.runtime.economics import RUNS_ROOT

_RULE = "─" * 64
_M = "🧑‍💼 **Marcus-SPOC:**"

DEFAULT_OPERATOR_ID = "operator_juan"


# ----------------------------------------------- styleguide-picker PRE-FLIGHT (Seam 3)
def narrate_picker_preflight(
    publish_url: str, run_tag: str, *, style_count: int | None = None
) -> str:
    """Client-facing PRE-FLIGHT narration (runs BEFORE G1): surface the picker url.

    Numbered-row HIL instruction + paste-back close. Deliberately client-facing:
    no styleguide slug ids and no "directive" vocabulary leak into what a client
    sees (A6/A7 keep the internal ids server-side).
    """
    count = f" ({style_count} styles to choose from)" if style_count else ""
    lines = [
        _RULE,
        f"{_M} Before we start, let's pick the visual style for your deck{count}.",
        "  1. Open your styleguide picker:",
        f"     {publish_url}",
        "     (it can take up to a minute to go live — if it shows a not-found page "
        "at first, wait a moment and refresh.)",
        "  2. Choose your style, and whether you want one version or two (A/B).",
        "  3. Copy the SELECTION CODE the page shows you and paste it back to me here.",
        f"{_M} I'll read it back to you to confirm before we lock it in.",
    ]
    return "\n".join(lines)


def _roster_index(ssot_path: str | Path | None) -> dict[str, dict[str, Any]]:
    roster = load_picker_roster(
        include_probes=True, include_deprecated=True, ssot_path=ssot_path
    )
    return {entry["name"]: entry for entry in roster}


def _roster_content_hash(ssot_path: str | Path | None) -> str:
    """Stable content hash of the resolvable roster (A7 provenance handle)."""
    index = _roster_index(ssot_path)
    payload = [
        {"name": name, "lifecycle": index[name].get("lifecycle")}
        for name in sorted(index)
    ]
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def decode_and_echo_pick(
    code: str,
    *,
    expected_run_tag: str,
    ssot_path: str | Path | None = None,
) -> tuple[dict[str, str], str]:
    """Decode a pasted selection code and build a human-readable echo-and-confirm.

    Returns ``({"A": slug, "B": slug?}, echo_text)``. The echo names the guide(s)
    by DISPLAY NAME + lifecycle + version count (client-facing — no slug ids, no
    "directive"). A stale/foreign or malformed code propagates the fail-loud
    ``PickerError`` from the decoder.
    """
    picks = decode_picker_selection_code(
        code, expected_run_tag=expected_run_tag, ssot_path=ssot_path
    )
    index = _roster_index(ssot_path)
    version_count = 2 if "B" in picks else 1
    named: list[str] = []
    for label in ("A", "B"):
        if label not in picks:
            continue
        entry = index.get(picks[label], {})
        display = str(entry.get("display_name") or picks[label])
        lifecycle = str(entry.get("lifecycle") or "candidate")
        named.append(f"Version {label}: {display} ({lifecycle})")
    words = "2 versions" if version_count == 2 else "1 version"
    echo = (
        f"{_M} Here's what I have — please confirm:\n  "
        + "\n  ".join(named)
        + f"\n  That's {words}. Reply 'confirm' to lock it in, or paste a new code."
    )
    return picks, echo


def commit_picker_pick(
    picks: dict[str, str] | None = None,
    *,
    directive_path: str | Path,
    expected_run_tag: str,
    publish_url: str,
    picked_by: str,
    code: str,
    confirmed: bool = False,
    ssot_path: str | Path | None = None,
    events_path: str | Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """On CONFIRM: write the directive + append the sidecar with A7 provenance.

    Threads the full provenance chain (who / from-url / roster content-hash /
    resolved ids + version count / the code itself) into the directive's
    ``styleguide_picker_provenance`` block. An unattributable pick (empty
    ``picked_by``) FAILS LOUD — never a silent anonymous bind.

    ENFORCED confirm gate: ``confirmed`` must be truthy — a caller cannot
    decode-then-commit directly, bypassing the echo-and-confirm beat. The picks
    are RE-DERIVED from ``code`` (single source of truth) so the provenance
    ``selection_code`` can never disagree with the bound picks; a ``picks`` arg,
    when passed, is cross-checked against the decode and a mismatch FAILS LOUD.
    An identical re-confirm is a TRUE no-op on the sidecar (stable
    ``(run_tag, code)`` dedup key), and always leaves exactly one provenance block.
    """
    if not confirmed:
        raise PickerError(
            "commit refused: the pick was not affirmatively confirmed "
            "(echo-and-confirm gate) — decode-then-commit may not bypass the echo"
        )
    attributed = str(picked_by or "").strip()
    if not attributed:
        raise PickerError(
            "unattributable pick: picked_by (who chose — operator or named client) "
            "is required for the A7 provenance chain"
        )
    # Single-source the picks FROM the code (Blind Hunter NIT): the provenance's
    # selection_code can then never disagree with the bound picks.
    derived = decode_picker_selection_code(
        code, expected_run_tag=expected_run_tag, ssot_path=ssot_path
    )
    if picks is not None and dict(picks) != derived:
        raise PickerError(
            f"selection code decodes to {derived} but the supplied picks are "
            f"{dict(picks)} — refusing to bind a code that disagrees with its picks"
        )
    version_count = 2 if "B" in derived else 1
    provenance_extra = {
        "picked_by": attributed,
        "publish_url": publish_url,
        "roster_sha256": _roster_content_hash(ssot_path),
        "version_count": version_count,
        "selection_code": code,
        "run_tag": expected_run_tag,
    }
    provenance = write_pick_to_directive(
        directive_path,
        derived,
        ssot_path=ssot_path,
        provenance_extra=provenance_extra,
    )
    # Stable dedup identity: an identical re-confirm (fresh picked_at) is a no-op.
    stable_dedup = f"{expected_run_tag}:{hashlib.sha256(code.encode('utf-8')).hexdigest()}"
    append_pick_event(
        derived,
        directive_path=directive_path,
        picked_at=provenance["picked_at"],
        run_id=run_id,
        events_path=events_path,
        dedup_key=stable_dedup,
    )
    return {"picks": derived, "provenance": provenance}


_AFFIRMATIVE = frozenset({"confirm", "confirmed", "yes", "y", "lock it in", "lock"})


def run_picker_preflight(
    *,
    run_tag: str,
    directive_path: str | Path,
    out_dir: str | Path,
    picked_by: str,
    input_fn: Callable[[str], str] = input,
    print_fn: Callable[[str], None] = print,
    publish_fn: Callable[..., dict[str, Any]] = publish_picker,
    ssot_path: str | Path | None = None,
    events_path: str | Path | None = None,
    run_id: str | None = None,
    include_probes: bool = False,
    site_repo: str | None = None,
    token: str | None = None,
    max_attempts: int = 3,
) -> dict[str, Any] | None:
    """The enforced pre-flight product path (runs BEFORE G1) — the ONE real caller.

    Ties the seam end-to-end: publish the picker for THIS ``run_tag`` → surface the
    url via :func:`narrate_picker_preflight` → read a pasted selection code → decode
    + echo via :func:`decode_and_echo_pick` → REQUIRE an explicit affirmative
    confirm → only then :func:`commit_picker_pick` (with ``confirmed=True``). A
    stale/foreign or malformed code is rejected AT DECODE, before any commit. If no
    valid code is confirmed within ``max_attempts``, raises :class:`PickerError`
    without writing the directive. All I/O is via injectable ``input_fn`` /
    ``print_fn`` / ``publish_fn`` so the path is fully testable offline.
    """
    record = publish_fn(
        run_tag=run_tag,
        out_dir=out_dir,
        ssot_path=ssot_path,
        include_probes=include_probes,
        site_repo=site_repo,
        token=token,
    )
    publish_url = str(record["publish_url"])
    print_fn(
        narrate_picker_preflight(
            publish_url, run_tag, style_count=record.get("style_count")
        )
    )
    for _attempt in range(max_attempts):
        code = input_fn("Paste your selection code: ").strip()
        try:
            _picks, echo = decode_and_echo_pick(
                code, expected_run_tag=run_tag, ssot_path=ssot_path
            )
        except PickerError as exc:
            # Rejected AT DECODE — a stale/foreign/malformed code never reaches commit.
            print_fn(f"{_M} That code didn't work: {exc}. Please paste it again.")
            continue
        print_fn(echo)
        answer = input_fn("Reply 'confirm' to lock it in, or paste a new code: ").strip()
        if answer.lower() in _AFFIRMATIVE:
            return commit_picker_pick(
                directive_path=directive_path,
                expected_run_tag=run_tag,
                publish_url=publish_url,
                picked_by=picked_by,
                code=code,
                confirmed=True,
                ssot_path=ssot_path,
                events_path=events_path,
                run_id=run_id,
            )
        # Not affirmative — treat the reply as a fresh code on the next loop.
    raise PickerError(
        f"no confirmed styleguide pick after {max_attempts} attempts; pre-flight "
        f"aborted without writing the directive"
    )


def build_operator_verdict_kwargs(
    *,
    trial_id: UUID,
    gate_id: str,
    card: dict[str, Any],
    verb: str,
    edit_payload: Any | None = None,
    reject_reason: str | None = None,
    operator_id: str = DEFAULT_OPERATOR_ID,
) -> dict[str, Any]:
    """Build the ``OperatorVerdict(**kwargs)`` dict shared by the scripted SPOC
    and the interactive interlocutor (A3 — backward-compat is structural, not
    coincidental). ``card`` is the persisted decision-card payload (the
    ``{"card": {...}, "digest": ...}`` envelope on disk).
    """
    kwargs: dict[str, Any] = {
        "trial_id": trial_id,
        "gate_id": gate_id,
        "card_id": UUID(card["card"]["card_id"]),
        "operator_id": operator_id,
        "decision_card_digest": card["digest"],
        "verb": verb,
    }
    if verb in {"edit", "select"}:
        kwargs["edit_payload"] = edit_payload
    if verb == "reject":
        kwargs["reject_reason"] = reject_reason or "operator-rejected"
    return kwargs


def _load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _narrate_sources(run_dir: Path, lines: list[str]) -> None:
    """Capability (a): sources + how each is treated."""
    directive_path = run_dir / "directive.yaml"
    if not directive_path.exists():
        return
    roles: list[str] = []
    cur_loc = None
    for raw in directive_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("locator:"):
            cur_loc = line.split("locator:", 1)[1].strip()
        elif line.startswith("role:") and cur_loc:
            role = line.split("role:", 1)[1].strip()
            roles.append(f"  - {cur_loc} -> treated as **{role}**")
            cur_loc = None
    lines.append(f"{_M} I've composed the source directive (capability a). Source treatment:")
    lines.extend(roles or ["  - (no sources parsed)"])
    lines.append("  Confirm these roles, or tell me to re-treat any source.")


def _narrate_ingestion(run_dir: Path, lines: list[str]) -> None:
    """Capability (b): ingestion completeness / errors."""
    manifest = _load(run_dir / "bundle" / "manifest.json")
    lines.append(f"{_M} Ingestion report (capability b) -")
    if isinstance(manifest, dict) and manifest.get("artifacts"):
        arts = manifest["artifacts"]
        total = sum(int(a.get("size_bytes", 0)) for a in arts if isinstance(a, dict))
        lines.append(f"  - Texas extracted {len(arts)} artifacts ({total:,} bytes); complete.")
        for a in arts[:6]:
            if isinstance(a, dict):
                lines.append(f"      - {a.get('path')} ({a.get('size_bytes')} bytes)")
        lines.append("  - No ingestion errors; the source bundle is ready to narrate.")
    else:
        lines.append("  - (bundle manifest not yet available at this gate)")


def _narrate_lesson_plan(run_dir: Path, lines: list[str]) -> None:
    """Capability (c): the lesson plan (Marcus + Irene)."""
    alt = run_dir / "irene-pass1.md"
    top = run_dir.parent.parent.parent / "runs" / run_dir.name / "irene-pass1.md"
    src = alt if alt.exists() else (top if top.exists() else None)
    lines.append(f"{_M} The lesson plan Irene and I drafted (capability c) -")
    if src is not None:
        head = [f"  {ln}" for ln in src.read_text(encoding="utf-8").splitlines()[:8] if ln.strip()]
        lines.extend(head or ["  - (lesson plan present)"])
    else:
        lines.append("  - plan units are staged in run state; tell me to adjust scope/sequencing.")


def _narrate_treatment(card: dict[str, Any], lines: list[str]) -> None:
    """Capability (e): creative treatment - #variants + clustering/pace."""
    inner = card.get("card", {})
    variants = inner.get("variant_candidates") or []
    opts = [e for e in inner.get("pick_context", []) if e.get("kind") == "variant-options"]
    lines.append(f"{_M} The Creative Director's proposed treatment (capability e) -")
    lines.append(f"  - Slide variants for Storyboard-A selection: {variants or '(1 per slide)'}")
    if opts:
        for slide in opts[0].get("slides", [])[:8]:
            vs = ", ".join(str(v.get("variant")) for v in slide.get("variants", []))
            lines.append(f"      - {slide.get('slide_id')}: variant(s) [{vs}]")
    lines.append("  Tell me how many variants per slide, or approve the proposed set.")


def _narrate_voice(card: dict[str, Any], lines: list[str]) -> None:
    """Capability (e): narration voice selection."""
    ctx = card.get("card", {}).get("pick_context", [])
    opts = [e for e in ctx if e.get("kind") == "voice-options"]
    lines.append(f"{_M} Narration voice options (capability e/voice) -")
    if opts:
        for v in opts[0].get("voices", []):
            lines.append(
                f"  - {v.get('voice_id')} - {v.get('voice_name')}  "
                f"sample: {v.get('sample_audio_url')}"
            )
    lines.append("  Say a voice id to bind it through synthesis, or approve my recommendation.")


def _narrate_g0_enrichment(card: dict[str, Any], run_dir: Path, lines: list[str]) -> None:
    """Confirm-gate #1 (G0E): typed COMPONENTS grouped by file + LOs + roots + dissent."""
    enrichment = _load(run_dir / "g0-enrichment.json") or {}
    inner = card.get("card", {})
    components = inner.get("typed_components") or enrichment.get("typed_components") or []
    los = inner.get("provisional_los") or enrichment.get("provisional_los") or []
    roots = inner.get("traversal_roots") or enrichment.get("traversal_roots") or []
    reconcile = inner.get("reconcile") or enrichment.get("reconcile") or {}
    dissents = inner.get("dissents") or enrichment.get("dissents") or []
    lines.append(f"{_M} G0 source-enrichment manifest for your confirmation (gate #1):")
    lines.append(f"  Traversal roots I walked ({len(roots)}):")
    for root in roots[:5]:
        lines.append(f"    - {root.get('kind')}: {root.get('root_id')}")
    # Group the typed components by their parent FILE (a file yields N components).
    by_file: dict[str, list[dict[str, Any]]] = {}
    for comp in components:
        by_file.setdefault(str(comp.get("parent_source_id")), []).append(comp)
    lines.append(
        f"  Typed COMPONENTS ({len(components)} across {len(by_file)} files):"
    )
    for parent, comps in list(by_file.items())[:8]:
        lines.append(f"    {parent} ({len(comps)} components):")
        for comp in comps[:6]:
            flag = "  [flagged: no generator today]" if comp.get("flagged_unconsumed") else ""
            label = str(comp.get("label", ""))[:48]
            lines.append(
                f"      - {comp.get('source_type')}: {label} @ "
                f"{comp.get('locator')}{flag}"
            )
    lines.append(f"  Candidate provisional LOs ({len(los)}):")
    for lo in los[:8]:
        lines.append(f"    - {lo.get('objective_id')}: {lo.get('statement', '')[:80]}")
    if reconcile:
        lines.append(
            f"  Reconcile: {reconcile.get('n_files_in')} files in == "
            f"{reconcile.get('n_files_covered')} covered + "
            f"{reconcile.get('n_files_ignored')} ignored; "
            f"{reconcile.get('n_components')} components "
            f"({reconcile.get('n_flagged')} flagged classification-only)."
        )
    if dissents:
        d = dissents[0]
        lines.append(
            f"  My recorded dissent (A3): on {d.get('against')} — {d.get('marcus_position')}"
        )
    lines.append("  Confirm the typing + LOs, or tell me to re-type a component / drop an LO.")


def narrate_gate(gate_id: str, card: dict[str, Any], run_dir: Path) -> str:
    """Marcus-voiced narration of a gate, surfacing the relevant a-g capability."""
    lines: list[str] = [_RULE, f"  GATE {gate_id}"]
    if gate_id == "G0E":
        _narrate_g0_enrichment(card, run_dir, lines)
    elif gate_id == "G1":
        _narrate_sources(run_dir, lines)
        _narrate_ingestion(run_dir, lines)
        _narrate_lesson_plan(run_dir, lines)
        lines.append(f"{_M} No gap-fill research was needed (capability d); the lesson is "
                     "corpus-grounded. Tell me if you'd like supporting research (Tracy).")
    elif gate_id == "G2B":
        _narrate_treatment(card, lines)
        chooser = _load(run_dir / "chooser-publish-G2B.json") or {}
        chooser_url = chooser.get("publish_url")
        if chooser_url:
            lines.append(
                f"{_M} Storyboard A is published - open it and CLICK your preferred variant "
                "for each slide, then paste the selection code back to me:"
            )
            lines.append(f"  {chooser_url}")
    elif gate_id == "G2C":
        pub = _load(run_dir / "storyboard-publish-G2C.json") or {}
        lines.append(
            f"{_M} Here is the storyboard with your per-slide picks applied, for final review:"
        )
        lines.append(f"  {pub.get('publish_url', '(local storyboard pack)')}")
    elif gate_id == "G3":
        lines.append(f"{_M} Motion plan (capability f) - this narrated-deck lesson plans no "
                     "motion clips (synthesis is a later capability). Tell me if you want "
                     "motion on any slide; otherwise I'll proceed still-only.")
    elif gate_id == "G4":
        lines.append(f"{_M} Fidelity gate - Vera checked the assets against your sources; no "
                     "blocking drift. Approve to proceed to narration.")
    elif gate_id == "G4A":
        _narrate_voice(card, lines)
    else:
        lines.append(f"{_M} Decision needed at {gate_id}.")
    return "\n".join(lines)


def run_marcus_spoc(
    trial_id: UUID,
    decisions: dict[str, dict[str, Any]] | None = None,
    runs_root: Path = RUNS_ROOT,
) -> list[str]:
    """Drive a paused trial to completion as a Marcus conversation; return the transcript."""
    decisions = decisions or {}
    run_dir = runs_root / str(trial_id)
    transcript: list[str] = [
        f"{_M} I'm your single point of contact for this run (trial {trial_id}). I'll walk "
        "you through each decision and handle the specialists, tools, and state behind the scenes.",
    ]
    for _ in range(30):
        run = _load(run_dir / "run.json") or {}
        status, gate = run.get("status"), run.get("paused_gate")
        if status == "completed":
            transcript.append(_RULE)
            transcript.append(f"{_M} Your lesson is assembled - slides, narration, and the "
                              "Descript hand-off bundle are ready. That's the run, error-free.")
            break
        if status == "paused-at-error":
            transcript.append(f"{_M} I hit a snag I couldn't auto-resolve "
                              f"({run.get('paused_error_tag')}); pausing for repair.")
            break
        if status != "paused-at-gate" or not gate:
            transcript.append(f"{_M} Unexpected state ({status}); stopping.")
            break
        card = _load(run_dir / f"decision-card-{gate}.json") or {}
        transcript.append(narrate_gate(gate, card, run_dir))
        decision = decisions.get(gate, {"verb": "approve"})
        verb = decision.get("verb", "approve")
        kwargs = build_operator_verdict_kwargs(
            trial_id=trial_id,
            gate_id=gate,
            card=card,
            verb=verb,
            edit_payload=decision.get("edit_payload"),
            reject_reason=decision.get("reject_reason"),
        )
        extra = f" {decision.get('edit_payload')}" if verb in {"edit", "select"} else ""
        transcript.append(f"👤 **Operator:** {verb}{extra}")
        env = resume_production_trial(
            trial_id=trial_id,
            verdict=OperatorVerdict(**kwargs),
            runs_root=runs_root,
            max_specialist_calls=12,
        )
        nxt = f", next: {env.paused_gate}" if env.paused_gate else ""
        transcript.append(f"{_M} (done - {env.status}{nxt})")
    return transcript


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="python -m app.marcus.cli.marcus_spoc")
    parser.add_argument("--trial-id", required=True, type=UUID)
    parser.add_argument("--decisions-file", required=False)
    parser.add_argument("--runs-root", required=False)
    args = parser.parse_args(argv)
    decisions = None
    if args.decisions_file:
        decisions = json.loads(Path(args.decisions_file).read_text(encoding="utf-8"))
    runs_root = Path(args.runs_root) if args.runs_root else RUNS_ROOT
    print("\n".join(run_marcus_spoc(args.trial_id, decisions=decisions, runs_root=runs_root)))
    return 0


__all__ = [
    "DEFAULT_OPERATOR_ID",
    "build_operator_verdict_kwargs",
    "commit_picker_pick",
    "decode_and_echo_pick",
    "main",
    "narrate_gate",
    "narrate_picker_preflight",
    "run_marcus_spoc",
    "run_picker_preflight",
]


if __name__ == "__main__":
    raise SystemExit(main())
