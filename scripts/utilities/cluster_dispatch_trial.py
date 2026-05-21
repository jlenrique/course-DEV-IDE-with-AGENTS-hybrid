"""One-shot trial: dispatch a Gamma generation from cluster-structured data.

Validates that a call built from the cluster prompt + visual constraints
produces a valid Gamma API call and returns generated assets.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "skills" / "gamma-api-mastery" / "scripts"))

import io
import zipfile

import requests
from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from scripts.api_clients.gamma_client import GammaClient


def main() -> None:
    bundle = PROJECT_ROOT / "course-content" / "staging" / "storyboard-a-trial"
    cluster = json.loads((bundle / "clusters.json").read_text(encoding="utf-8"))

    vc = cluster["constraints"]["visual_constraints"]

    # Reconstruct the rendered prompt (matches cluster_prompt_engineering.py output)
    prompt_text = (
        f"Cluster {cluster['cluster_id']} (small) — "
        f"intents: {'; '.join(cluster['intents'])}. "
        f"Goal: {cluster['goal']}.\n"
        f"Apply constraints: accent: {vc['accent']}; "
        f"layout: {vc['layout']}; palette: {vc['palette']}\n"
        f"Safety: Stay within this cluster only; do not reference other clusters. "
        f"| Avoid PII; keep content professional and factual."
    )

    print("=== CLUSTER DISPATCH CALL ===")
    print(f"Cluster ID: {cluster['cluster_id']}")
    print(f"Slides requested: {len(cluster['slides'])}")
    print(f"Prompt text ({len(prompt_text)} chars):")
    print(prompt_text)
    print()

    additional = (
        f"Visual palette: {vc['palette']}. "
        f"Accent color: {vc['accent']}. "
        f"Layout: {vc['layout']}. "
        f"This is a health sciences educational presentation."
    )

    client = GammaClient()
    print("Gamma client initialized. Dispatching generation...")
    print()

    # Resolve theme from run-constants (trial uses same as canonical)
    theme_id = "njim9kuhfnljvaa"  # 2026 HIL APC Nejal theme

    result = client.generate(
        input_text=prompt_text,
        text_mode="generate",
        format="presentation",
        num_cards=len(cluster["slides"]),
        theme_id=theme_id,
        additional_instructions=additional,
        export_as="png",
    )

    gen_id = result.get("id") or result.get("generationId", "")
    print(f"Generation started: id={gen_id}")
    print(f"Initial status: {result.get('status', 'unknown')}")
    print()

    print("Polling for completion...")
    completed = client.wait_for_generation(gen_id)
    print()

    print("=== RESULT ===")
    print(f"Status: {completed.get('status')}")
    print(f"Gamma URL: {completed.get('gammaUrl', 'N/A')}")
    print(f"Export URL: {completed.get('exportUrl', 'N/A')}")
    print(f"Cards generated: {completed.get('numCards', 'N/A')}")

    # Print full response minus bulky content field
    safe = {k: v for k, v in completed.items() if k != "content"}
    print(json.dumps(safe, indent=2, default=str))

    # Download and extract PNGs
    export_url = completed.get('exportUrl')
    if export_url:
        print()
        print("Downloading PNG export...")
        export_dir = bundle / "gamma-export"
        export_dir.mkdir(exist_ok=True)

        response = requests.get(export_url)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            zf.extractall(export_dir)
            print(f"Extracted {len(zf.namelist())} PNG files to {export_dir}")
            for name in zf.namelist():
                print(f"  - {name}")
    else:
        print("No export URL available for download")


if __name__ == "__main__":
    main()
