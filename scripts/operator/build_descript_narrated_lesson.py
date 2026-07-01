"""Build a narrated-slide video in Descript from an APP assembly bundle.

Proven recipe (matches the April 2026 "Inflection Point" project):
  1. Direct-upload the slide PNGs + per-segment narration MP3s into a new project.
  2. Poll the import job to completion.
  3. Invoke Underlord (POST /jobs/agent) to assemble the narrated slideshow
     (each slide held for its segment's narration, in order, captions on).
  4. Poll the agent job and report the project URL.

Auth: requires ``DESCRIPT_API_KEY`` in the environment (Drive-scoped Bearer token).

Examples:
  python scripts/operator/build_descript_narrated_lesson.py --dry-run
  python scripts/operator/build_descript_narrated_lesson.py            # import + agent
  python scripts/operator/build_descript_narrated_lesson.py --skip-agent  # import only
"""

from __future__ import annotations

import argparse
import contextlib
import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.api_clients.descript_client import (  # noqa: E402
    DescriptClient,
    content_type_for,
)
from scripts.operator.descript_publication_receipt import (  # noqa: E402
    DescriptPublicationError,
    build_publication_receipt,
)

logger = logging.getLogger("build_descript_narrated_lesson")

# -- Default package: most recent completed trial run (6cb8eafd) --
DEFAULT_RUN_ID = "6cb8eafd-4f66-4d8e-9b5f-848bd3b08b49"
DEFAULT_SLIDES_DIR = REPO_ROOT / "runs" / "compositor" / "assembly-bundle" / "visuals"
DEFAULT_AUDIO_DIR = (
    REPO_ROOT
    / "state" / "config" / "runs" / DEFAULT_RUN_ID
    / "enrique-narration" / "assembly-bundle" / "audio"
)
DEFAULT_PROJECT_NAME = "APP Narrated Lesson - 6cb8eafd (2026-06-24)"

def build_assembly_prompt(n_segments: int) -> str:
    """Count-aware Underlord assembly prompt (generalizes the original hardcoded-6).

    A clustered deck expands to N sub-slides/segments (e.g. 13), so the prompt must
    name the real count and last index, not a fixed 6.
    """
    last = f"{n_segments:02d}"
    return (
        "Assemble a polished narrated slide lesson video from the media in this project. "
        f"There are {n_segments} narration audio clips named narration-01.mp3 through "
        f"narration-{last}.mp3 and {n_segments} slide images named slide-01.png through "
        f"slide-{last}.png. "
        "Build a single composition that plays the narration clips in order "
        f"(narration-01, then -02, ... through -{last}) as the soundtrack. While each "
        "narration clip plays, display its matching slide full-screen for the entire "
        "duration of that clip (slide-01 with narration-01, slide-02 with narration-02, "
        "and so on, 1:1 in order). Scale each slide to fill the 1920x1080 frame. Add "
        "accurate captions generated from the narration. Do not invent or add any new "
        "script, slides, or B-roll — use only the provided media."
    )


def collect_media(slides_dir: Path, audio_dir: Path) -> dict[str, Path]:
    """Map Descript media display names to local file paths (slides + narration)."""
    media: dict[str, Path] = {}
    slides = sorted(slides_dir.glob("slide-*.png"))
    audio = sorted(audio_dir.glob("seg-*.mp3"))
    if not slides:
        raise FileNotFoundError(f"No slide PNGs found in {slides_dir}")
    if not audio:
        raise FileNotFoundError(f"No narration MP3s found in {audio_dir}")
    for idx, png in enumerate(slides, start=1):
        media[f"slide-{idx:02d}.png"] = png
    for idx, mp3 in enumerate(audio, start=1):
        media[f"narration-{idx:02d}.mp3"] = mp3
    return media


def build_add_media(media: dict[str, Path]) -> dict[str, dict[str, object]]:
    """Build the ``add_media`` payload using direct-upload entries."""
    add_media: dict[str, dict[str, object]] = {}
    for name, path in media.items():
        add_media[name] = {
            "content_type": content_type_for(path),
            "file_size": path.stat().st_size,
        }
    return add_media


def resolve_expected_audio_total_s(audio_dir: Path) -> float | None:
    """Find the synthesized-audio total (seconds) for the assembly bundle.

    Locates ``enrique-synthesis-receipt.json`` in ``audio_dir`` or any ancestor
    directory and returns its declared total. Prefers
    ``attestation.total_audio_duration_seconds`` (the authoritative measured
    total); falls back to a top-level ``total_audio_duration_seconds`` and then
    to summing the per-segment ``duration_seconds``. Returns None if no receipt
    is found — the verify gate decides how to treat a missing expected total.
    """
    receipt_path: Path | None = None
    for d in (audio_dir, *audio_dir.parents):
        candidate = d / "enrique-synthesis-receipt.json"
        if candidate.is_file():
            receipt_path = candidate
            break
    if receipt_path is None:
        return None
    try:
        data = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    attestation = data.get("attestation") or {}
    total = attestation.get("total_audio_duration_seconds")
    if total is None:
        total = data.get("total_audio_duration_seconds")
    if total is None:
        segs = data.get("segments") or []
        per = [s.get("duration_seconds") for s in segs if s.get("duration_seconds") is not None]
        total = sum(per) if per else None
    if total is None:
        return None
    print(f"  expected_audio_total_s={total} (from {receipt_path})")
    return float(total)


def publish_project(
    client: DescriptClient,
    project_id: str,
    *,
    resolution: str,
    composition_id: str | None = None,
) -> dict[str, object]:
    """Render + publish a composition; return {share_url, download_url, status}.

    Post-composition only — wraps the existing DescriptClient.publish(). Honors the
    capability-doc contract: a correct publish returns a share_url and a time-limited
    download_url. Errors 402 (out of credits) / 429 (rate limit) surface from the client.
    """
    print(f"\nPublishing project {project_id} (resolution={resolution})...")
    job = client.publish(
        project_id, composition_id=composition_id, resolution=resolution
    )
    job_id = job.get("job_id")
    print(f"  publish job_id={job_id}")
    done = client.wait_for_job(
        job_id,
        on_progress=lambda i, d: print(f"  [{i:>3}] publish job_state={d.get('job_state')}")
        if i % 6 == 0 else None,
    )
    result = done.get("result") or {}
    share_url = result.get("share_url") or result.get("published_url") or done.get("share_url")
    download_url = (
        result.get("download_url") or result.get("export_url") or done.get("download_url")
    )
    print(f"  publish result.status={result.get('status')}")
    print(f"  share_url={share_url}")
    print(f"  download_url={download_url}")
    if not (share_url or download_url):
        print(f"  WARNING: no share/download url returned. Full result keys: {sorted(result)}")
    return {"status": result.get("status"), "share_url": share_url, "download_url": download_url}


def _load_env_if_available() -> None:
    """Load .env so DESCRIPT_API_KEY is present even when not exported in the shell.

    DescriptClient reads DESCRIPT_API_KEY from os.environ; without this, a shell that
    hasn't exported the key fails the first auth call with a misleading 401 (looks
    like an expired token, is actually an unset var). Mirrors trial.py.
    """
    try:
        from scripts.utilities.env_loader import load_env

        load_env()
    except (OSError, UnicodeDecodeError, ImportError):
        # Best-effort: a missing/unreadable/non-UTF-8 .env must not abort the
        # build. OSError covers FileNotFoundError + PermissionError; load_env's
        # read_text(encoding="utf-8") can raise UnicodeDecodeError (not an OSError).
        pass


def run(args: argparse.Namespace) -> int:
    _load_env_if_available()
    # Publish-only mode: publish an existing project (skip build).
    if args.project_id:
        if not args.publish:
            print("--project-id requires --publish (publish-only mode).")
            return 2
        if args.dry_run:
            print(f"[dry-run] Would publish existing project {args.project_id} "
                  f"at {args.resolution}.")
            return 0
        client = DescriptClient()
        status = client.status()
        print(f"Auth OK — drive_id={status.get('drive_id')} "
              f"api_version={status.get('api_version')}")
        publish_project(client, args.project_id, resolution=args.resolution)
        return 0

    slides_dir = Path(args.slides_dir)
    audio_dir = Path(args.audio_dir)
    media = collect_media(slides_dir, audio_dir)
    add_media = build_add_media(media)

    print(f"Package: {len(media)} assets "
          f"({sum(1 for k in media if k.startswith('slide'))} slides + "
          f"{sum(1 for k in media if k.startswith('narration'))} narration)")
    for name, path in media.items():
        print(f"  {name:<18} {add_media[name]['content_type']:<12} "
              f"{add_media[name]['file_size']:>10} bytes  <- {path}")

    if args.dry_run:
        print("\n[dry-run] No API calls made. Project name would be: "
              f"{args.project_name!r}")
        return 0

    client = DescriptClient()
    status = client.status()
    print(f"\nAuth OK — drive_id={status.get('drive_id')} "
          f"api_version={status.get('api_version')}")

    # 1) Import (create project + signed upload URLs)
    print(f"\nCreating project {args.project_name!r} and requesting upload URLs...")
    imp = client.import_media(add_media=add_media, project_name=args.project_name)
    project_id = imp.get("project_id")
    project_url = imp.get("project_url")
    job_id = imp.get("job_id")
    upload_urls = imp.get("upload_urls") or {}
    print(f"  project_id={project_id}")
    print(f"  project_url={project_url}")
    print(f"  import job_id={job_id}  upload_urls={len(upload_urls)}")

    # 2) PUT each file to its signed URL
    for name, info in upload_urls.items():
        path = media[name]
        code = client.upload_to_signed_url(
            info["upload_url"], path, content_type=content_type_for(path)
        )
        print(f"  uploaded {name:<18} -> HTTP {code}")

    # 3) Poll import job
    print("\nWaiting for import job to finish processing/transcription...")
    done = client.wait_for_job(
        job_id,
        on_progress=lambda i, d: print(f"  [{i:>3}] import job_state={d.get('job_state')}")
        if i % 6 == 0 else None,
    )
    print(f"  import result.status={(done.get('result') or {}).get('status')}")

    if args.skip_agent:
        print(f"\n[skip-agent] Import complete. Open: {project_url}")
        return 0

    # 4) Underlord assembly
    n_narration = sum(1 for k in media if k.startswith("narration"))
    assembly_prompt = build_assembly_prompt(n_narration)
    print("\nInvoking Underlord to assemble the narrated slide video...")
    agent = client.agent_edit(prompt=assembly_prompt, project_id=project_id)
    agent_job = agent.get("job_id")
    print(f"  agent job_id={agent_job}")
    a_done = client.wait_for_job(
        agent_job,
        on_progress=lambda i, d: print(
            f"  [{i:>3}] agent job_state={d.get('job_state')} "
            f"{(d.get('progress') or {}).get('label', '')}"
        ) if i % 6 == 0 else None,
    )
    result = a_done.get("result") or {}
    print(f"  agent result.status={result.get('status')}")
    if result.get("agent_response"):
        print(f"  Underlord: {result['agent_response']}")

    # 5) Verify — fail loud on the duration-0-mid-assembly detachment case.
    project = client.get_project(project_id)
    comps = project.get("compositions") or []
    print(f"\nCompositions ({len(comps)}):")
    for c in comps:
        print(f"  - {c.get('name')!r} dur={c.get('duration')} "
              f"media_type={c.get('media_type')} id={c.get('id')}")

    if not comps:
        raise DescriptPublicationError(
            f"No compositions on project {project_id} after assembly — "
            "Underlord did not produce a timeline. NOT declaring published."
        )

    comp0 = comps[0]
    actual_duration = comp0.get("duration")
    expected_audio_total_s = resolve_expected_audio_total_s(audio_dir)
    if expected_audio_total_s is None:
        raise DescriptPublicationError(
            f"Could not resolve expected_audio_total_s (no synthesis receipt "
            f"found at/above {audio_dir}). Cannot attest publication; NOT "
            "declaring published."
        )

    receipt = build_publication_receipt(
        project_id=project_id,
        composition_id=comp0.get("id"),
        composition_duration_s=actual_duration,
        expected_audio_total_s=expected_audio_total_s,
        attested_at_utc=datetime.now(UTC).isoformat(),
    )
    receipt["project_url"] = project_url
    receipt["composition_name"] = comp0.get("name")
    receipt["composition_media_type"] = comp0.get("media_type")

    receipt_path = Path(args.audio_dir).parent / "descript-publication-receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"\nPUBLISHED (attested). Receipt written: {receipt_path}")
    print(f"  composition_duration_s={receipt['composition_duration_s']} "
          f"expected={receipt['expected_audio_total_s']} "
          f"delta={receipt['duration_delta_s']:+.3f}s")
    print(f"\nDone. Open your narrated lesson: {project_url}")

    # 6) Publish (optional) — render a shareable MP4 + link.
    #    Gated behind the passed assertion above: we only reach here if the
    #    composition was durably assembled (no detachment / drift).
    if args.publish:
        comp_id = comp0.get("id")
        publish_project(client, project_id, resolution=args.resolution, composition_id=comp_id)
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--slides-dir", default=str(DEFAULT_SLIDES_DIR))
    p.add_argument("--audio-dir", default=str(DEFAULT_AUDIO_DIR))
    p.add_argument("--project-name", default=DEFAULT_PROJECT_NAME)
    p.add_argument("--skip-agent", action="store_true",
                   help="Import + upload only; do not run the Underlord assembly.")
    p.add_argument("--publish", action="store_true",
                   help="After assembly, render + publish the composition (MP4 + share link).")
    p.add_argument("--project-id", default=None,
                   help="Publish an EXISTING project (skip build); requires --publish.")
    p.add_argument("--resolution", default="1080p",
                   help="Publish resolution (default 1080p). Used only with --publish.")
    p.add_argument("--dry-run", action="store_true",
                   help="Print the planned payload without calling the API.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    # Windows consoles default to cp1252; Underlord responses contain Unicode
    # (e.g. U+2192). Force UTF-8 so prints never crash the run.
    for stream in (sys.stdout, sys.stderr):
        with contextlib.suppress(AttributeError, ValueError):
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    return run(parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
