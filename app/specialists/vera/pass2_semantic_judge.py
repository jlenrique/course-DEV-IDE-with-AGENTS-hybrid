"""Vera-agentic Pass 2 judgments: G4-18 teaching-scope and spoken-bridge quality.

The handoff validator stays a structural oracle. This module is the live
juncture for the two semantic questions word lists cannot answer.
"""

from __future__ import annotations

import json
from typing import Any

from app.models.adapter import make_chat_model

RUBRIC = """You are Vera judging two Pass 2 questions. Return JSON only.

Q1 G4-18 teaching-scope: For each clustered interstitial, does the spoken
narration open a NEW teaching idea outside (a) the head narration, (b) that
cluster's Pass 1 title / learning_objective / source_refs / narrative_arc,
and (c) this interstitial's own source_ref plus perceived/on-card detail?
Function words and ordinary connective English are NOT new concepts.
Walking the head's idea on this card is allowed.

Q2 Spoken-bridge quality (G4-12): For each segment with bridge_type
cluster_boundary, is the narration a two-part seam — one beat synthesizing
the prior cluster, then one beat pulling the learner forward? Do NOT require
the substring "in this section". For intro/outro/both, is connective language
actually hearable? Metadata alone is not enough.

Return:
{
  "g4_18_verdict": "pass" | "fail",
  "bridge_quality_verdict": "pass" | "fail",
  "severity": "low" | "medium" | "high" | "critical",
  "summary": "one short paragraph",
  "findings": [
    {
      "criterion_id": "G4-18" | "G4-12",
      "seg_id": "seg-...",
      "severity": "low" | "medium" | "high" | "critical",
      "category": "O" | "I" | "A",
      "description": "what failed and why"
    }
  ]
}
If both questions pass, findings may contain a single advisory pass note.
g4_18_verdict is fail only on a high-confidence new teaching idea.
"""


def _segments_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw = payload.get("pass2_segments") or payload.get("segments")
    if isinstance(raw, list):
        return [row for row in raw if isinstance(row, dict)]
    return []


def judge_pass2_semantics(payload: dict[str, Any]) -> dict[str, Any]:
    """Call Vera's chat model on the frozen Pass 2 semantic rubric."""
    segments = _segments_from_payload(payload)
    if not segments:
        raise ValueError("pass2_semantic_judge requires pass2_segments")
    compact = []
    for row in segments:
        compact.append(
            {
                "id": row.get("id") or row.get("seg_id"),
                "cluster_id": row.get("cluster_id"),
                "cluster_role": row.get("cluster_role"),
                "cluster_position": row.get("cluster_position"),
                "bridge_type": row.get("bridge_type"),
                "source_ref": row.get("source_ref"),
                "isolation_target": row.get("isolation_target"),
                "narration_text": row.get("narration_text"),
            }
        )
    user = (
        f"{RUBRIC}\n\n"
        "## Pass 1 lesson plan (teaching terms)\n\n"
        f"```json\n{json.dumps(payload.get('lesson_plan') or {}, ensure_ascii=True)}\n```\n\n"
        "## Pass 2 segments\n\n"
        f"```json\n{json.dumps(compact, ensure_ascii=True)}\n```\n"
    )
    handle = make_chat_model(
        specialist_id="vera",
        temperature=0.2,
        tier_request="reasoning",
        request_timeout=180.0,
        max_retries=1,
        max_completion_tokens=8000,
    )
    response = handle.chat.invoke(
        [
            {
                "role": "system",
                "content": "You are Vera. Return only the JSON object specified.",
            },
            {"role": "user", "content": user},
        ]
    )
    raw = response.content if hasattr(response, "content") else str(response)
    text = raw if isinstance(raw, str) else str(raw)
    if "```json" in text:
        start = text.find("```json") + len("```json")
        end = text.find("```", start)
        if end > start:
            text = text[start:end].strip()
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("Vera semantic judge returned a non-object")
    g4_18 = str(parsed.get("g4_18_verdict") or "fail").strip().lower()
    if g4_18 not in {"pass", "fail"}:
        g4_18 = "fail"
    findings = parsed.get("findings")
    if not isinstance(findings, list) or not findings:
        findings = [
            {
                "criterion_id": "G4-18",
                "severity": "low",
                "category": "O",
                "description": parsed.get("summary") or "semantic judge returned no findings",
            }
        ]
    return {
        "g4_18_verdict": g4_18,
        "bridge_quality_verdict": str(parsed.get("bridge_quality_verdict") or "").strip().lower(),
        "severity": parsed.get("severity") or "medium",
        "summary": parsed.get("summary") or "",
        "findings": findings,
        "model_id": getattr(getattr(handle, "chat", None), "model_name", None),
    }
