"""Leg-1a LIVE gate (T6 / AC2-AC3-AC4-AC5) — REAL ElevenLabs, no mocks.

Drives the SHIPPED enrique build_assembly_bundle with the REAL ElevenLabsClient
(default) on a tiny 2-segment v3 slice, both carrying rhetorical_role=contrast_emphasis
(the deterministic value Irene's producer now emits for pedagogical_role=synthesis).

Asserts (first-run-stands, deterministic):
  AC2  receipt render_mode == "v3_provider_text" AND effective model (receipt.model_id) == eleven_v3
  AC3  receipt provider_text_tags == ["[slow]"]  (exact)
  AC4  distinct REAL request_ids across the two segments
  AC5  captions .vtt == canonical (contains canonical text, no "[slow]" leak)

Run FOREGROUND with hard timeout + flushed logging. Writes evidence JSON.
"""
from __future__ import annotations

import functools
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

print = functools.partial(print, flush=True)  # noqa: A001 - flushed logging

REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
EVID = REPO / "_bmad-output" / "implementation-artifacts" / "evidence"


def _load_live_key() -> str:
    from dotenv import load_dotenv

    # Live-key recipe: real .env wins over any placeholder sentinel already in env.
    sentinel = os.environ.get("ELEVENLABS_API_KEY", "")
    load_dotenv(REPO / ".env", override=True)
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key or key == sentinel and ("subst" in key or "placeholder" in key.lower()):
        pass
    if not key or len(key) < 40 or "placeholder" in key.lower() or "subst" in key.lower():
        raise SystemExit(f"ELEVENLABS_API_KEY not a real key (len={len(key)}); refusing live run")
    return key


def main() -> int:
    _load_live_key()
    os.environ["MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE"] = "1"
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

    from app.specialists._shared import voice_provider_text as vpt
    from app.specialists.enrique import _act as enrique_act

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle = EVID / f"concierge-leg1a-live-{ts}"
    bundle.mkdir(parents=True, exist_ok=True)

    SARAH = "EXAVITQu4vr4xnSDxMaL"
    selection = {"selected_voice_id": SARAH}
    # Short, tag-free canonical (keeps cost ~$0.04 and avoids the canonical-contains-tag guard).
    seg_texts = {
        "seg-01": "Bring the threads together now. This single decision reshapes the entire pathway.",
        "seg-02": "Step back and see the whole. The pattern only becomes clear from this height.",
    }
    segments = [
        {
            "segment_id": sid,
            "slide_id": f"slide-{i:02d}",
            "text": text,
            "voice_direction": {
                "elevenlabs": {"model_id": "eleven_v3"},
                "rhetorical_role": "contrast_emphasis",
            },
        }
        for i, (sid, text) in enumerate(seg_texts.items(), start=1)
    ]
    payload = {"bundle_path": str(bundle), "segments": segments}

    print(f"[leg1a-live] dispatching {len(segments)} v3 segments (contrast_emphasis) to REAL ElevenLabs ...")
    result = enrique_act.build_assembly_bundle(payload, selection=selection)  # real client default
    receipts = result.get("narration_receipts", [])
    print(f"[leg1a-live] got {len(receipts)} receipts")

    checks: dict[str, object] = {}
    request_ids: list[str] = []
    per_seg = []
    for sid, text in seg_texts.items():
        rcpt = next((r for r in receipts if r.get("segment_id") == sid), None)
        assert rcpt is not None, f"no receipt for {sid}"
        expected_provider = vpt.compile_provider_text(text, rhetorical_role="contrast_emphasis")
        vtt_path = bundle / "assembly-bundle" / "captions" / f"{sid}.vtt"
        vtt = vtt_path.read_text(encoding="utf-8") if vtt_path.exists() else ""
        rid = rcpt.get("request_id")
        if rid:
            request_ids.append(rid)
        seg_rec = {
            "segment_id": sid,
            "render_mode": rcpt.get("render_mode"),
            "effective_model_id": rcpt.get("model_id"),
            "provider_text_tags": rcpt.get("provider_text_tags"),
            "request_id": rid,
            "provider_text_sha256": rcpt.get("provider_text_sha256"),
            "expected_provider_sha256": vpt.sha256_text(expected_provider),
            "captions_eq_canonical": (text in vtt) and ("[slow]" not in vtt),
        }
        per_seg.append(seg_rec)
        # AC2
        assert rcpt.get("render_mode") == "v3_provider_text", f"{sid} render_mode={rcpt.get('render_mode')}"
        assert rcpt.get("model_id") == "eleven_v3", f"{sid} effective model={rcpt.get('model_id')}"
        # AC3
        assert rcpt.get("provider_text_tags") == ["[slow]"], f"{sid} tags={rcpt.get('provider_text_tags')}"
        assert rcpt.get("provider_text_sha256") == vpt.sha256_text(expected_provider), f"{sid} provider sha mismatch"
        # AC5
        assert text in vtt, f"{sid} captions missing canonical"
        assert "[slow]" not in vtt, f"{sid} TAG LEAK in captions"
        print(f"[leg1a-live] {sid}: render={rcpt.get('render_mode')} model={rcpt.get('model_id')} "
              f"tags={rcpt.get('provider_text_tags')} req={rid} captions_clean=True")

    # AC4
    assert len(request_ids) == len(seg_texts), f"missing request_ids: {request_ids}"
    assert len(set(request_ids)) == len(request_ids), f"request_ids NOT distinct: {request_ids}"

    checks = {
        "AC2_render_mode_and_effective_model_v3": True,
        "AC3_provider_tags_exact_slow": True,
        "AC4_distinct_real_request_ids": True,
        "AC5_captions_canonical_no_leak": True,
    }
    evidence = {
        "story": "concierge-leg1a-rhetorical-role-emission",
        "leg": "Leg-1a live gate (T6)",
        "timestamp_utc": ts,
        "model": "eleven_v3",
        "voice_id": SARAH,
        "rhetorical_role": "contrast_emphasis",
        "tag": "[slow]",
        "real_api": True,
        "segments": per_seg,
        "distinct_request_ids": request_ids,
        "checks": checks,
        "verdict": "PASS",
    }
    out = EVID / f"concierge-leg1a-live-gate-{ts}.json"
    out.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(f"[leg1a-live] ALL ACs PASS. evidence -> {out}")
    print(f"[leg1a-live] request_ids: {request_ids}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
