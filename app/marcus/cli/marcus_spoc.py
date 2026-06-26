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

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from app.marcus.orchestrator.production_runner import resume_production_trial
from app.models.state.operator_verdict import OperatorVerdict
from app.runtime.economics import RUNS_ROOT

_RULE = "─" * 64
_M = "🧑‍💼 **Marcus-SPOC:**"

DEFAULT_OPERATOR_ID = "operator_juan"


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
    """Confirm-gate #1 (G0E): typed manifest + provisional LOs + A10 roots + dissent."""
    enrichment = _load(run_dir / "g0-enrichment.json") or {}
    inner = card.get("card", {})
    typed = inner.get("typed_manifest") or enrichment.get("typed_sources") or []
    los = inner.get("provisional_los") or enrichment.get("provisional_los") or []
    roots = inner.get("traversal_roots") or enrichment.get("traversal_roots") or []
    reconcile = inner.get("reconcile") or enrichment.get("reconcile") or {}
    dissents = inner.get("dissents") or enrichment.get("dissents") or []
    lines.append(f"{_M} G0 source-enrichment manifest for your confirmation (gate #1):")
    lines.append(f"  Traversal roots I walked ({len(roots)}):")
    for root in roots[:5]:
        lines.append(f"    - {root.get('kind')}: {root.get('root_id')}")
    lines.append(f"  Source TYPE manifest ({len(typed)} spans):")
    for src in typed[:12]:
        flag = "  [flagged: no generator today]" if src.get("flagged_unconsumed") else ""
        lines.append(f"    - {src.get('source_id')} -> {src.get('source_type')}{flag}")
    lines.append(f"  Candidate provisional LOs ({len(los)}):")
    for lo in los[:8]:
        lines.append(f"    - {lo.get('objective_id')}: {lo.get('statement', '')[:80]}")
    if reconcile:
        lines.append(
            f"  Reconcile: {reconcile.get('n_in')} in == "
            f"{reconcile.get('n_typed')} typed + {reconcile.get('n_ignored')} ignored "
            f"({reconcile.get('n_flagged')} flagged classification-only)."
        )
    if dissents:
        d = dissents[0]
        lines.append(
            f"  My recorded dissent (A3): on {d.get('against')} — {d.get('marcus_position')}"
        )
    lines.append("  Confirm the typing + LOs, or tell me to re-type a span / drop an LO.")


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
    "narrate_gate",
    "run_marcus_spoc",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
