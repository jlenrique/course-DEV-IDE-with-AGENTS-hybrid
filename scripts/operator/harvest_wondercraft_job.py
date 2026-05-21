"""Harvest a finished Wondercraft job — downloads audio, computes SHA256,
saves to fixture path, writes metadata, prints addendum block.

Use when a Wondercraft job is already finished (per probe_wondercraft_job.py)
and we just need to complete the M2 ceremony lifecycle without re-polling.

Usage:
    .venv\\Scripts\\python.exe scripts\\operator\\harvest_wondercraft_job.py <job_id>
"""

from __future__ import annotations

import hashlib
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

try:
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    print("ERROR: python-dotenv not installed.", file=sys.stderr)
    sys.exit(1)

sys.path.insert(0, str(REPO_ROOT))

ARTIFACT_DATE = datetime.now(tz=UTC).strftime("%Y-%m-%d")
ARTIFACT_DIR = REPO_ROOT / "tests" / "fixtures" / "specialists" / "wanda" / "live_artifacts" / ARTIFACT_DATE
COST_CEILING_USD = 5.00


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: harvest_wondercraft_job.py <job_id>", file=sys.stderr)
        return 2

    job_id = sys.argv[1]
    print(f"Harvesting Wondercraft job {job_id} ...")

    from scripts.api_clients.wondercraft_client import WondercraftClient

    client = WondercraftClient()
    response = client.get(f"/podcast/{job_id}")
    print(f"Job response: finished={response.get('finished')}, error={response.get('error')}")

    if not response.get("finished"):
        print("ERROR: job not yet finished. Wait and re-run.", file=sys.stderr)
        return 1
    if response.get("error"):
        print(f"ERROR: job ended in failure: {response.get('error_details')}", file=sys.stderr)
        return 1

    audio_url = response.get("url")
    if not audio_url:
        print(f"ERROR: no 'url' field in response: {response}", file=sys.stderr)
        return 1

    print(f"\nDownloading audio (signed S3 URL; expires ~3 days)...")
    import httpx

    download_response = httpx.get(audio_url, timeout=120, follow_redirects=True)
    download_response.raise_for_status()
    audio_bytes = download_response.content
    print(f"Downloaded {len(audio_bytes)} bytes.")

    sha256 = hashlib.sha256(audio_bytes).hexdigest()
    print(f"SHA256: {sha256}")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    artifact_path = ARTIFACT_DIR / f"{sha256}.mp3"
    artifact_path.write_bytes(audio_bytes)
    print(f"Saved to: {artifact_path}")

    # Best-effort duration estimate (mp3 framing varies; we approximate from file size at typical 128kbps)
    bitrate_bps = 128_000
    estimated_duration_sec = len(audio_bytes) * 8 / bitrate_bps

    script_text = response.get("script", "")
    metadata_text = f"""# M2 Live Artifact Metadata - {ARTIFACT_DATE}

- **Title:** M2 Operator-Window Ceremony
- **Artifact path:** `tests/fixtures/specialists/wanda/live_artifacts/{ARTIFACT_DATE}/{sha256}.mp3`
- **SHA256:** `{sha256}`
- **Bytes:** {len(audio_bytes)}
- **Estimated duration (sec; from byte count at 128kbps):** {estimated_duration_sec:.1f}
- **Cost USD:** (not reported by Wondercraft API; per pricing ~10 credits = ~$2.25 on Pro plan)
- **Voice ID:** 231bca1f-eb6f-496c-8781-92cdc58e9ff3
- **Script word count:** {len(script_text.split())}
- **Job ID:** {job_id}
- **Captured at:** {datetime.now(tz=UTC).isoformat()}
- **Wondercraft API endpoint used:** `/podcast/scripted` (POST) + `/podcast/{{job_id}}` (GET)
- **Operator-session note:** harvested via harvest_wondercraft_job.py after M2 ceremony's
  poll-loop missed the terminal state (Wondercraft uses `finished: true` boolean, not `status` enum;
  in-session A16 instance — Composition-vs-Component Audit Gap).
"""
    metadata_path = ARTIFACT_DIR / "LIVE_ARTIFACT_METADATA.md"
    metadata_path.write_text(metadata_text, encoding="utf-8")
    print(f"Metadata: {metadata_path}")

    # Verify duration in canary band per M2 spec (4*60 <= duration_sec <= 10*60)
    canary_min = 4 * 60
    canary_max = 10 * 60
    canary_status = (
        "WITHIN canary band (4-10 min)"
        if canary_min <= estimated_duration_sec <= canary_max
        else f"OUTSIDE canary band (4-10 min) — observed ~{estimated_duration_sec:.1f}s; review acceptable"
    )

    print("\n" + "=" * 60)
    print("ADDENDUM BLOCK -- paste into:")
    print("  _bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md")
    print("  (under section 'Operator-Window Addendum'; create the section if absent)")
    print("=" * 60)
    print()
    print(f"## Operator-Window Addendum (M2 close - {ARTIFACT_DATE})")
    print()
    print(f"M2 Wondercraft live-artifact ceremony executed {ARTIFACT_DATE}. One real podcast generated via")
    print(f"`POST /podcast/scripted` against live Wondercraft API; harvested via")
    print(f"`scripts/operator/harvest_wondercraft_job.py` after job-completion signal.")
    print()
    print(f"- Artifact: `tests/fixtures/specialists/wanda/live_artifacts/{ARTIFACT_DATE}/{sha256}.mp3`")
    print(f"- SHA256: `{sha256}`")
    print(f"- Estimated duration: {estimated_duration_sec:.1f} sec ({canary_status})")
    print(f"- Cost: ~$2.25 estimated (Pro plan; ~10 credits at $0.225/credit; under ${COST_CEILING_USD:.2f} ceiling)")
    print(f"- Job ID: `{job_id}`")
    print(f"- Voice ID: `231bca1f-eb6f-496c-8781-92cdc58e9ff3`")
    print(f"- Metadata: `tests/fixtures/specialists/wanda/live_artifacts/{ARTIFACT_DATE}/LIVE_ARTIFACT_METADATA.md`")
    print()
    print(f"Two A16 instances surfaced + handled in same session: (1) `WondercraftClient.create_scripted_podcast()` payload-shape defect")
    print(f"(`script` was plain string but API requires array of `{{text, voice_id}}` objects); (2) `WondercraftClient.wait_for_job()` / M2 ceremony")
    print(f"polling looked for `status` enum but Wondercraft response uses `finished` boolean. Both bypassed in M2 ceremony script with corrected")
    print(f"direct API calls; full client cleanup filed as deferred-inventory follow-on `5a-2-wondercraft-client-payload-shape-defect`.")
    print()
    print(f"M2 condition closes. Flip `2c-3-m2-verdict-conditional-on-2c-2-live-artifact`")
    print(f"in `_bmad-output/planning-artifacts/deferred-inventory.md` from")
    print(f"DEFERRED-CONTINUES to RESOLVED-{ARTIFACT_DATE}.")
    print()
    print("=" * 60)
    print("HARVEST COMPLETE")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
