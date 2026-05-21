#!/usr/bin/env python3
"""Build and publish the Video Style Picker to GitHub Pages.

Reads video-style-catalog.yaml, copies sample videos, generates an
interactive HTML picker, and publishes to the site repo.

Usage:
    python build_style_picker.py [--publish] [--output-dir <dir>]
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "skills" / "gamma-api-mastery" / "scripts"))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

CATALOG_PATH = PROJECT_ROOT / "skills" / "kling-video" / "references" / "video-style-catalog.yaml"
SITE_REPO_URL = "https://github.com/jlenrique/jlenrique.github.io"
TARGET_SUBDIR = "assets/video-style-picker"


def load_catalog() -> dict:
    return yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))


def build_picker_html(styles: list[dict]) -> str:
    styles_json = json.dumps(styles, default=str)
    count = len(styles)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Video Style Picker - Kling Production Library</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f5f5f5;color:#333;padding:20px}}
h1{{font-size:22px;margin-bottom:4px}}
.subtitle{{color:#666;font-size:13px;margin-bottom:16px}}
.toolbar{{display:flex;gap:12px;align-items:center;margin-bottom:16px;flex-wrap:wrap}}
.toolbar input{{padding:6px 12px;border:1px solid #ccc;border-radius:4px;font-size:13px;width:240px}}
.toolbar select{{padding:6px 8px;border:1px solid #ccc;border-radius:4px;font-size:13px}}
.tag-filters{{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:16px}}
.tag-btn{{padding:3px 10px;border:1px solid #aaa;border-radius:12px;font-size:11px;cursor:pointer;background:#fff}}
.tag-btn.active{{background:#2a7;color:#fff;border-color:#2a7}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}}
.card{{background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.1);transition:box-shadow .2s}}
.card:hover{{box-shadow:0 4px 12px rgba(0,0,0,.15)}}
.card video{{width:100%;height:auto;display:block;background:#000}}
.card-body{{padding:12px}}
.card-title{{font-size:15px;font-weight:600;margin-bottom:4px}}
.card-meta{{font-size:11px;color:#888;margin-bottom:6px}}
.card-tags{{display:flex;gap:4px;flex-wrap:wrap;margin-bottom:8px}}
.card-tag{{font-size:10px;padding:2px 6px;background:#e8e8e8;border-radius:8px}}
.card-prompt{{font-size:11px;color:#555;max-height:60px;overflow:hidden;margin-bottom:8px;line-height:1.4}}
.card-prompt.expanded{{max-height:none}}
.expand-link{{font-size:11px;color:#2a7;cursor:pointer}}
.select-btn{{width:100%;padding:8px;border:2px solid #2a7;border-radius:4px;background:#fff;color:#2a7;font-weight:600;cursor:pointer;font-size:13px;transition:all .15s}}
.select-btn:hover{{background:#2a7;color:#fff}}
.card.selected{{outline:3px solid #2a7}}
.card.selected .select-btn{{background:#2a7;color:#fff}}
.export-bar{{position:sticky;bottom:0;background:#fff;border-top:2px solid #2a7;padding:12px 20px;display:flex;justify-content:space-between;align-items:center;margin:16px -20px -20px;box-shadow:0 -2px 8px rgba(0,0,0,.1)}}
.export-bar .status{{font-weight:600}}
.export-bar button{{padding:8px 20px;background:#2a7;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:14px}}
.export-bar button:disabled{{opacity:.4;cursor:not-allowed}}
</style>
</head>
<body>
<h1>Video Style Picker</h1>
<p class="subtitle">Kling Production Library &mdash; {count} styles. Hover to preview. Click to select. Export dispatch-ready JSON.</p>

<div class="toolbar">
<input type="text" id="search" placeholder="Search styles..." />
<select id="mode-filter"><option value="">All modes</option><option value="std">std</option><option value="pro">pro</option></select>
<select id="op-filter"><option value="">All operations</option><option value="image2video">image2video</option><option value="text2video">text2video</option></select>
</div>
<div class="tag-filters" id="tag-filters"></div>
<div class="grid" id="grid"></div>

<div class="export-bar">
<span class="status" id="status">No style selected</span>
<button id="export-btn" disabled>Export dispatch JSON</button>
</div>

<script>
const STYLES={styles_json};
let selected=null;
let activeTag=null;

const allTags=new Set();
STYLES.forEach(s=>(s.tags||[]).forEach(t=>allTags.add(t)));
const tagBar=document.getElementById("tag-filters");
["all",...[...allTags].sort()].forEach(t=>{{
  const btn=document.createElement("span");
  btn.className="tag-btn"+(t==="all"?" active":"");
  btn.textContent=t;
  btn.onclick=()=>{{
    document.querySelectorAll(".tag-btn").forEach(b=>b.classList.remove("active"));
    btn.classList.add("active");
    activeTag=t==="all"?null:t;
    render();
  }};
  tagBar.appendChild(btn);
}});

function esc(s){{return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;")}}

function render(){{
  const q=document.getElementById("search").value.toLowerCase();
  const mf=document.getElementById("mode-filter").value;
  const of_=document.getElementById("op-filter").value;
  const grid=document.getElementById("grid");
  grid.innerHTML="";
  STYLES.filter(s=>{{
    if(q&&!s.display_name.toLowerCase().includes(q)&&!s.prompt_template.toLowerCase().includes(q)&&!(s.tags||[]).some(t=>t.includes(q)))return false;
    if(mf&&s.mode!==mf)return false;
    if(of_&&s.operation!==of_)return false;
    if(activeTag&&!(s.tags||[]).includes(activeTag))return false;
    return true;
  }}).forEach(s=>{{
    const card=document.createElement("div");
    card.className="card"+(selected===s.style_id?" selected":"");
    const videoUrl=s.hosted_video_url||"";
    const tags=(s.tags||[]).map(t=>"<span class=\\"card-tag\\">"+esc(t)+"</span>").join("");
    card.innerHTML=
      "<video src=\\""+esc(videoUrl)+"\\" muted loop preload=\\"metadata\\" onmouseenter=\\"this.play()\\" onmouseleave=\\"this.pause();this.currentTime=0\\"></video>"+
      "<div class=\\"card-body\\">"+
      "<div class=\\"card-title\\">"+esc(s.display_name)+"</div>"+
      "<div class=\\"card-meta\\">"+esc(s.operation)+" | "+esc(s.model)+" | "+esc(s.mode)+" | "+s.duration+"s</div>"+
      "<div class=\\"card-tags\\">"+tags+"</div>"+
      "<div class=\\"card-prompt\\" id=\\"prompt-"+s.style_id+"\\">"+esc(s.prompt_template)+"</div>"+
      "<span class=\\"expand-link\\" data-sid=\\""+s.style_id+"\\">show more</span>"+
      "<button class=\\"select-btn\\" data-sid=\\""+s.style_id+"\\">Select this style</button>"+
      "</div>";
    grid.appendChild(card);
  }});
  grid.querySelectorAll(".expand-link").forEach(el=>{{
    el.onclick=()=>{{
      const p=document.getElementById("prompt-"+el.dataset.sid);
      if(p)p.classList.toggle("expanded");
      el.textContent=el.textContent==="show more"?"show less":"show more";
    }};
  }});
  grid.querySelectorAll(".select-btn").forEach(el=>{{
    el.onclick=()=>pick(el.dataset.sid);
  }});
}}

function pick(id){{
  selected=id;
  document.getElementById("status").textContent="Selected: "+id;
  document.getElementById("export-btn").disabled=false;
  render();
}}

document.getElementById("search").oninput=render;
document.getElementById("mode-filter").onchange=render;
document.getElementById("op-filter").onchange=render;

document.getElementById("export-btn").onclick=()=>{{
  const s=STYLES.find(x=>x.style_id===selected);
  if(!s)return;
  const dispatch={{
    style_id:s.style_id,
    selected_at:new Date().toISOString(),
    operation:s.operation,
    model:s.model,
    mode:s.mode,
    duration:s.duration,
    prompt_template:s.prompt_template,
    negative_prompt:s.negative_prompt||"",
    tags:s.tags,
    source_receipt:s.receipt_path,
    image_url:"REPLACE_WITH_SOURCE_IMAGE_URL"
  }};
  const blob=new Blob([JSON.stringify(dispatch,null,2)],{{type:"application/json"}});
  const a=document.createElement("a");
  a.href=URL.createObjectURL(blob);
  a.download="style-dispatch-"+s.style_id+".json";
  a.click();
}};

render();
</script>
</body>
</html>"""


def build_local(output_dir: Path, catalog: dict) -> Path:
    """Build the picker locally without publishing."""
    videos_dir = output_dir / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)

    for style in catalog["styles"]:
        vp = Path(style["video_path"])
        if not vp.is_absolute():
            vp = PROJECT_ROOT / vp
        if not vp.exists():
            print(f"  SKIP {style['style_id']}: video not found")
            style["hosted_video_url"] = ""
            continue
        dest = videos_dir / f"{style['style_id']}.mp4"
        shutil.copy2(vp, dest)
        style["hosted_video_url"] = f"videos/{style['style_id']}.mp4"

    (output_dir / "catalog.json").write_text(
        json.dumps(catalog, indent=2, default=str), encoding="utf-8"
    )
    html = build_picker_html(catalog["styles"])
    (output_dir / "index.html").write_text(html, encoding="utf-8")
    return output_dir


def publish(local_dir: Path, catalog: dict) -> str:
    """Push the picker to GitHub Pages. Returns the published URL."""
    from gamma_operations import _git_auth_env, _github_pages_base_url, _run_git_command

    token = os.environ.get("GITHUB_PAGES_TOKEN", "").strip()
    if not token:
        raise RuntimeError("GITHUB_PAGES_TOKEN not set")

    git_env = _git_auth_env(token)
    pages_base = _github_pages_base_url(SITE_REPO_URL)

    temp_repo = Path(tempfile.mkdtemp(prefix="video-picker-"))
    try:
        _run_git_command(
            ["git", "clone", "--depth", "1", "--branch", "main", SITE_REPO_URL, str(temp_repo)],
            env=git_env,
        )
        _run_git_command(["git", "config", "user.name", "app-marcus-bot"], cwd=temp_repo)
        _run_git_command(
            ["git", "config", "user.email", "app-marcus-bot@users.noreply.github.com"],
            cwd=temp_repo,
        )

        target = temp_repo / TARGET_SUBDIR
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(local_dir, target)

        _run_git_command(["git", "add", TARGET_SUBDIR], cwd=temp_repo, env=git_env)
        status = _run_git_command(
            ["git", "status", "--short", TARGET_SUBDIR], cwd=temp_repo, env=git_env
        )
        if status.strip():
            _run_git_command(
                ["git", "commit", "-m", f"Publish video style picker ({len(catalog['styles'])} styles)"],
                cwd=temp_repo,
                env=git_env,
            )
            _run_git_command(
                ["git", "push", SITE_REPO_URL, "HEAD:main"],
                cwd=temp_repo,
                env=git_env,
                display_args=["git", "push", SITE_REPO_URL, "HEAD:main"],
            )
        return f"{pages_base}/{TARGET_SUBDIR}/index.html"
    finally:
        shutil.rmtree(temp_repo, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and publish Video Style Picker")
    parser.add_argument("--publish", action="store_true", help="Publish to GitHub Pages")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "exports" / "video-style-picker",
        help="Local output directory",
    )
    args = parser.parse_args()

    catalog = load_catalog()
    print(f"Loaded {len(catalog['styles'])} styles from catalog")

    local_dir = build_local(args.output_dir, catalog)
    videos_ok = sum(1 for s in catalog["styles"] if s.get("hosted_video_url"))
    print(f"Built picker: {videos_ok} videos, {len(catalog['styles'])} entries -> {local_dir}")

    if args.publish:
        url = publish(local_dir, catalog)
        print(f"Published: {url}")
        receipt = {
            "status": "published",
            "url": url,
            "styles": len(catalog["styles"]),
            "videos": videos_ok,
        }
        print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
